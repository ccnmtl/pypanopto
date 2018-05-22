from datetime import datetime
from json import loads
import math
import os
import re

from boto.compat import BytesIO
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from filechunkio import FileChunkIO

from panopto.auth import PanoptoAuth


class PanoptoUploadTarget(object):

    '''
        Encapsulate an upload target from the Panopto upload REST API

        Given uploadTarget =
            http[s]://{hostname}/Panopto/Upload/{guid}
    '''
    def __init__(self, upload_id, upload_target):
        self.upload_id = upload_id
        self.upload_target = upload_target

        m = re.match(
            r'https:\/\/(.*)\/Panopto\/(.*)\/(.*)', upload_target)

        self.hostname = '{}'.format(m.group(1))
        self.bucket_name = 'Panopto/{}'.format(m.group(2))
        self.guid = m.group(3)

    def file_key(self, filename):
        return '{}/{}'.format(self.guid, filename)

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

    def set_destination_attributes(self):
        if not self.dest_filename:
            self.dest_filename = os.path.basename(self.input_file)
        if not self.title:
            self.title = self.dest_filename

    def create_session(self):
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

    def _multipart_manifest(self, parts):
        s = '<CompleteMultipartUpload>\n'
        for part in parts:
            s += '  <Part>\n'
            s += '    <PartNumber>%d</PartNumber>\n' % part['part_number']
            s += '    <ETag>%s</ETag>\n' % part['etag']
            s += '  </Part>\n'
        s += '</CompleteMultipartUpload>'

        return s

    def create_bucket(self):
        conn = S3Connection(host=self.target.host(),
                            calling_format=OrdinaryCallingFormat(),
                            anon=True)
        self.bucket = conn.get_bucket(
            bucket_name=self.target.bucket_name, validate=False)

    def upload_media(self):
        source_file = open(self.input_file, 'rb')

        # Cribbed from http://boto.cloudhackers.com/en/latest/s3_tut.html
        # #storing-large-data
        # Create a multipart upload request
        key_name = self.target.file_key(self.dest_filename)
        mp = self.bucket.initiate_multipart_upload(key_name)
        mp.key_name = key_name

        parts = []
        chunk_size = 52428800
        source_size = os.stat(self.input_file).st_size
        chunk_count = int(math.ceil(source_size / float(chunk_size)))

        # Send the file parts, using FileChunkIO to create a file-like object
        # that points to a certain byte range within the original file. We
        # set bytes to never exceed the original file size.
        for i in range(chunk_count):
            offset = chunk_size * i
            byte_count = min(chunk_size, source_size - offset)
            with FileChunkIO(source_file.name, 'r',
                             offset=offset, bytes=byte_count) as fp:
                key = mp.upload_part_from_file(
                    fp, part_num=i + 1, size=byte_count)
                parts.append({
                    'part_number': i + 1, 'etag': key.etag})

        # Finish the upload by sending a manifest file with the parts listed
        self.bucket.complete_multipart_upload(
            mp.key_name, mp.id, self._multipart_manifest(parts))

        source_file.close()

    def _panopto_manifest(self, dest_filename, title, descript):
        dt = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000-00:00')
        return '''<PanoptoSession
            xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
            xmlns="http://panopto.com/PanoptoSession/v1">
            <Title>{}</Title>
            <Description>{}</Description>
            <Date>{}</Date>
            <Videos>
                <Video>
                    <Start>PT0S</Start>
                    <Filename>{}</Filename>
                    <Cuts />
                    <TableOfContents />
                    <Type>Primary</Type>
                    <Transcripts />
                </Video>
            </Videos>
            <Presentations />
            <Images />
            <Cuts />
            <Tags />
            <Extensions />
            <Attachments />
        </PanoptoSession>'''.format(title, descript, dt, dest_filename)

    def upload_manifest(self):
        # create and upload a manifest file for panopto
        manifest = self._panopto_manifest(
            self.dest_filename, self.title, self.description)

        source_file = BytesIO(manifest.encode('utf-8'))

        key_name = self.target.file_key('manifest.xml')
        mp = self.bucket.initiate_multipart_upload(key_name)
        mp.key_name = key_name

        key = mp.upload_part_from_file(
            source_file, part_num=1, size=len(manifest))
        parts = [{'part_number': 1, 'etag': key.etag}]

        self.bucket.complete_multipart_upload(
            mp.key_name, mp.id, self._multipart_manifest(parts))

        source_file.close()

    def complete_session(self):
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

    def get_upload_id(self):
        return self.target.upload_id


class PanoptoUploadStatus(object):

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

    def check(self):
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
