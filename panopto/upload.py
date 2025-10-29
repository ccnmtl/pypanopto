from _io import BytesIO
from datetime import timezone
from datetime import datetime
from json import loads
import math
import os
import re
import unicodedata
import uuid

import boto3
from lxml import etree

from botocore import UNSIGNED
from botocore.client import Config
from panopto.auth import PanoptoAuth


class PanoptoUploadTarget(object):

    '''
        Encapsulate an upload target from the Panopto upload REST API

        Given uploadTarget =
            http[s]://{hostname}/Panopto/Upload/{guid}
    '''
    def __init__(self, upload_id: str, upload_target: str):
        self.upload_id = upload_id
        self.upload_target = upload_target

        m = re.match(
            r'https:\/\/(.*)\/Panopto\/(.*)\/(.*)', upload_target)

        self.hostname = 'https://{}'.format(m.group(1))
        self.bucket_name = 'Panopto'
        self.key_base = '{}/{}'.format(m.group(2), m.group(3))

    def file_key(self, filename):
        return '{}/{}'.format(self.key_base, filename)

    def host(self):
        return self.hostname


class PanoptoUpload(object):

    '''
        Implementation of the Panopto Upload API.

        Overview of Basic Workflow
        0. Authenticate to server via the Panopto SOAP api. This class
           currently supports authentication via application_key.
        1. Create a blank session via Panopto's REST api.
        2. Using the S3 multipart upload protocol, upload the session
            manifest file to Panopto's server
        3. Using the S3 multipart upload protocol, upload the media file
           to Panopto's server
        4. Complete session via Panopto's REST api with a manifest of all
           all uploaded files

        More details here:
        https://support.panopto.com/articles/Documentation/Upload-API
    '''

    def __init__(self):
        self.files = []
        self.server = None
        self.folder = None
        self.username = None
        self.password = None
        self.input_file = None
        self.dest_filename = None
        self.title = None
        self.description = None
        self.uuid = str(uuid.uuid4())

    def set_destination_attributes(self):
        path, filename = os.path.split(self.input_file)

        fname, ext = os.path.splitext(filename)
        self.dest_filename = '{}{}'.format(self.uuid, ext)

        if not self.title:
            self.title = fname

    def create_session(self) -> bool:
        # authenticate
        auth = PanoptoAuth(self.server)

        self.session = auth.authenticate_with_password(
            self.username, self.password)

        if not self.session:
            return False

        self.set_destination_attributes()

        url = 'https://{}/Panopto/PublicAPI/REST/sessionUpload'.format(
            self.server)
        payload = {'FolderId': self.folder}

        response = self.session.post(url, json=payload)

        if response.status_code != 201:
            return False

        content = loads(response.content)
        self.target = PanoptoUploadTarget(
            content['ID'], content['UploadTarget'])
        return True

    def create_bucket(self):
        self.s3 = boto3.client('s3', aws_access_key_id=None,
                               aws_secret_access_key=None,
                               endpoint_url=self.target.host(),
                               config=Config(
                                   signature_version=UNSIGNED,
                                   s3={
                                       'payload_signing_enabled': False
                                   }))

    def upload_media(self):
        source_file = open(self.input_file, 'rb')
        key_name = self.target.file_key(self.dest_filename)
        upload_id = self.s3.create_multipart_upload(
            Bucket=self.target.bucket_name, Key=key_name)['UploadId']

        parts = []
        chunk_size = 13107200
        source_size = os.stat(self.input_file).st_size
        chunk_count = int(math.ceil(source_size / float(chunk_size)))

        for i in range(chunk_count):
            offset = chunk_size * i
            byte_count = min(chunk_size, source_size - offset)

            data = source_file.read(byte_count)
            part = self.s3.upload_part(
                Bucket=self.target.bucket_name, Body=data, Key=key_name,
                UploadId=upload_id, PartNumber=i)
            parts.append({'PartNumber': i, 'ETag': part['ETag']})

        self.s3.complete_multipart_upload(
            Bucket=self.target.bucket_name,
            Key=key_name,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts})

        source_file.close()

    def _panopto_manifest(
            self, dest_filename: str, title: str, descript: str) -> bytes:
        namespace_map = {
            None: 'http://tempuri.org/UniversalCaptureSpecification/v1',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
        }

        # create XML
        root = etree.Element('Session', nsmap=namespace_map)

        elt = etree.Element('Title')
        elt.text = title
        root.append(elt)

        elt = etree.Element('Description')
        elt.text = unicodedata.normalize('NFKD', descript or '')
        root.append(elt)

        elt = etree.Element('Date')
        elt.text = datetime.now(timezone.utc).isoformat()
        root.append(elt)

        video = etree.Element('Video')
        elt = etree.Element('Start')
        elt.text = 'PT0S'
        video.append(elt)

        elt = etree.Element('File')
        elt.text = dest_filename
        video.append(elt)

        elt = etree.Element('Type')
        elt.text = 'Primary'
        video.append(elt)

        videos = etree.Element('Videos')
        videos.append(video)
        root.append(videos)

        return etree.tostring(root, xml_declaration=True, encoding='UTF-8')

    def upload_manifest(self):
        # create and upload a manifest file for panopto
        manifest = self._panopto_manifest(
            self.dest_filename, self.title, self.description)
        source_file = BytesIO(manifest)
        key_name = self.target.file_key('{}.xml'.format(self.uuid))

        self.s3.upload_fileobj(
            source_file, self.target.bucket_name, key_name,
            ExtraArgs={'ContentType': 'text/xml'})

    def complete_session(self) -> bool:
        url = 'https://{}/Panopto/PublicAPI/REST/sessionUpload/{}'.format(
            self.server, self.target.upload_id)

        payload = {
            'ID': self.target.upload_id,
            'FolderId': self.folder,
            'SessionId': None,
            'UploadTarget': self.target.upload_target,
            'State': 1,
            'MessageID': 0,
            'Message': None
        }

        response = self.session.put(url, json=payload)
        return response.status_code == 200

    def get_upload_id(self) -> str:
        return self.target.upload_id


class PanoptoUploadStatus(object):
    """
    This class encapsulates Panopto's upload status types:

    0: Uploading - An upload was created, and has not been cancelled
      or completed
    1: UploadComplete - The upload has been completed, but has yet to
      be transferred to storage
    2: UploadCancelled - The upload was cancelled by the user and
      hasn’t been deleted yet
    3: Processing - The upload is being processed
    4: Complete - The upload has been processed and can now be used by
      the Panopto system
    5: ProcessingError - There was an error during transfer
    6: DeletingFiles - The upload was cancelled or timed out, and is
      being deleted
    7: Delete - The upload was cancelled or timed out and was deleted
    8: DeletingError - There was an error while deleting the upload

    https://support.panopto.com/resource/uploadapi/index.html
    """

    UPLOAD_CREATED = 0
    UPLOAD_COMPLETE = 1
    UPLOAD_CANCELLED = 2
    UPLOAD_PROCESSING = 3
    UPLOAD_READY = 4
    UPLOAD_ERROR = 5
    UPLOAD_DELETING_FILE = 6
    UPLOAD_DELETED = 7
    UPLOAD_DELETION_ERROR = 8

    UPLOAD_STATES = {
        UPLOAD_CREATED: 'Upload Created',
        UPLOAD_COMPLETE: 'Upload Complete',
        UPLOAD_CANCELLED: 'Upload Cancelled',
        UPLOAD_PROCESSING: 'Upload Processing',
        UPLOAD_READY: 'Upload Ready',
        UPLOAD_ERROR: 'Upload Processing Error',
        UPLOAD_DELETING_FILE: 'Upload Deleting Files',
        UPLOAD_DELETED: 'Upload Deleted',
        UPLOAD_DELETION_ERROR: 'Upload Deletion Error'
    }

    def __init__(self):
        self.server = None
        self.username = None
        self.password = None
        self.upload_id = None

    def check(self) -> tuple[int, str]:
        auth = PanoptoAuth(self.server)

        self.session = auth.authenticate_with_password(
            self.username, self.password)

        url = 'https://{}/Panopto/PublicAPI/REST/sessionUpload/{}'.format(
            self.server, self.upload_id)

        response = self.session.get(url)
        if response.status_code == 200:
            content = loads(response.content)
            return (content['State'], content['SessionId'])

        return (0, None)
