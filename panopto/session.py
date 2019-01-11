from zeep.client import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

from panopto.auth import PanoptoAuth


class PanoptoSessionManager(object):

    def __init__(self, server, username,
                 instance_name=None, application_key=None,
                 password=None):
        self.client = {
            'session': self._client(server, 'SessionManagement'),
            'access': self._client(server, 'AccessManagement'),
            'user': self._client(server, 'UserManagement')
        }
        self.auth_info = PanoptoAuth.auth_info(
                server, username, instance_name, application_key, password)

        self.server = server
        self.username = username
        self.instance_name = instance_name
        self.application_key = application_key
        self.password = password

    def _client(self, server, name):
        url = 'https://{}/Panopto/PublicAPI/4.6/{}.svc?wsdl'.format(
            server, name)
        return Client(url)

    def add_folder(self, name, parent_guid):
        try:
            response = self.client['session'].service.AddFolder(
                auth=self.auth_info, name=name, parentFolder=parent_guid,
                isPublic=False)

            if response is None or len(response) < 1:
                return ''

            obj = serialize_object(response)
            return obj['Id']
        except Fault:
            return ''

    def get_folder(self, parent_guid, name):
        try:
            response = self.client['session'].service.GetCreatorFoldersList(
                auth=self.auth_info, request={'ParentFolderId': parent_guid})

            if response is None or len(response) < 1:
                return ''

            obj = serialize_object(response)
            for folder in obj['Results']['Folder']:
                if folder['Name'] == name:
                    return folder['Id']
            return ''
        except Fault:
            return ''

    def get_session_url(self, session_id):
        try:
            response = self.client['session'].service.GetSessionsById(
                auth=self.auth_info, sessionIds=[session_id])

            if response is None or len(response) < 1:
                return ''

            obj = serialize_object(response)
            return obj[0]['MP4Url']
        except Fault:
            return ''

    def get_thumb_url(self, session_id):
        try:
            response = self.client['session'].service.GetSessionsById(
                auth=self.auth_info, sessionIds=[session_id])

            if response is None or len(response) < 1:
                return None

            obj = serialize_object(response)
            return obj[0]['ThumbUrl']
        except Fault:
            return None
