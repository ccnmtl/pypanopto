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
        except (Fault, TypeError):
            return ''

    def get_folder_access_details(self, folder_id):
        try:
            response = self.client['access'].service.GetFolderAccessDetails(
                auth=self.auth_info, folderId=folder_id)

            if response is None or len(response) < 1:
                return ''

            obj = serialize_object(response)
            return obj['GroupsWithCreatorAccess']
        except (Fault, TypeError):
            return ''

    def grant_group_access_to_folder(self, folder_id, group_id):
        try:
            # Grant creator access to specified group
            self.client['access'].service.GrantGroupAccessToFolder(
                auth=self.auth_info, folderId=folder_id, groupId=group_id)

            return True
        except Fault:
            return False

    def inherit_folder_access(self, from_folder_id, to_folder_id):
        groups = self.get_folder_access_details(from_folder_id)
        for group in groups['guid']:
            self.grant_group_access_to_folder(to_folder_id, group)

    def get_session_url(self, session_id):
        try:
            response = self.client['session'].service.GetSessionsById(
                auth=self.auth_info, sessionIds=[session_id])
        except Fault:
            return ''

        if response is None or len(response) < 1:
            return ''

        obj = serialize_object(response)
        return obj[0]['MP4Url']

    def get_thumb_url(self, session_id):
        try:
            response = self.client['session'].service.GetSessionsById(
                auth=self.auth_info, sessionIds=[session_id])
        except Fault:
            return None

        if response is None or len(response) < 1:
            return None

        obj = serialize_object(response)
        return obj[0]['ThumbUrl']

    def get_session_list(self, folder):
        request = {
            'FolderId': folder,
            'Pagination': {'MaxNumberResults': 100, 'PageNumber': 0}
        }

        try:
            response = self.client['session'].service.GetSessionsList(
                auth=self.auth_info, request=request, searchQuery=None)
        except Fault:
            return []

        if (
                response is None or len(response) < 1 or
                response['TotalNumberResults'] == 0
        ):
            return []

        obj = serialize_object(response)
        return obj['Results']['Session']

    def move_sessions(self, session_ids, folder):
        try:
            self.client['session'].service.MoveSessions(
                auth=self.auth_info, sessionIds=session_ids, folderId=folder)
        except Fault:
            return False

        # This api does not return a response. If no exception is thrown
        # assuming everything was completed successfully
        return True
