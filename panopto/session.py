from zeep.cache import SqliteCache
from zeep.client import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
from zeep.transports import Transport

from panopto.auth import PanoptoAuth


class PanoptoSessionManager(object):

    def __init__(self, server, username,
                 instance_name=None, application_key=None,
                 password=None, cache_dir=None):
        self.client = {
            'session': self._client(server, 'SessionManagement', cache_dir),
            'access': self._client(server, 'AccessManagement', cache_dir),
            'user': self._client(server, 'UserManagement', cache_dir)
        }
        self.auth_info = PanoptoAuth.auth_info(
            server, username, instance_name, application_key, password)

        self.server = server
        self.username = username
        self.instance_name = instance_name
        self.application_key = application_key
        self.password = password

    def _client(self, server, name, cache_dir):
        url = 'https://{}/Panopto/PublicAPI/4.6/{}.svc?wsdl'.format(
            server, name)
        if cache_dir:
            cache = SqliteCache(path=cache_dir)
            transport = Transport(cache=cache, timeout=1440)
        else:
            transport = Transport()
        return Client(url, transport=transport)

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

    def get_session_list(self, folder):
        try:
            request = {
                'FolderId': folder,
                'Pagination': {'MaxNumberResults': 100, 'PageNumber': 0}
            }
            response = self.client['session'].service.GetSessionsList(
                auth=self.auth_info, request=request, searchQuery=None)

            if response is None or len(response) < 1:
                return None

            obj = serialize_object(response)
            return obj['Results']['Session']
        except Fault:
            return None

    def move_sessions(self, session_ids, folder):
        try:
            self.client['session'].service.MoveSessions(
                auth=self.auth_info, sessionIds=session_ids, folderId=folder)

            # This api does not return a response. If no exception is thrown
            # assuming everything was completed successfully
            return True
        except Fault:
            return False
