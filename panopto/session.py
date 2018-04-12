from zeep.client import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

from panopto.auth import PanoptoAuth


class PanoptoSessionManager(object):

    def __init__(self, server, username, instance_name, application_key):
        self.client = {
            'session': self._client(server, 'SessionManagement'),
            'access': self._client(server, 'AccessManagement'),
            'user': self._client(server, 'UserManagement')
        }
        self.auth_info = PanoptoAuth.auth_info(
                server, username, instance_name, application_key)

        self.server = server
        self.username = username
        self.instance_name = instance_name
        self.application_key = application_key

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

    def get_group_guid(self, group_name):
        try:
            response = self.client['user'].service.GetGroupsByName(
                auth=self.auth_info, groupName=group_name)

            if not response or len(response) < 1:
                return None

            obj = serialize_object(response)
            return obj[0]['Id']
        except Fault:
            return None

    def get_user_guids(self, usernames):
        guids = []
        for user in usernames:
            try:
                auth_info = PanoptoAuth.auth_info(
                    self.server, user, self.instance_name,
                    self.application_key)
                user_key = PanoptoAuth.user_key(user, self.instance_name)
                response = self.client['user'].service.GetUserByKey(
                    auth_info, user_key)

                if response is None or len(response) < 1:
                    continue

                obj = serialize_object(response)
                guids.append(obj['UserId'])
            except Fault:
                return ''
        return guids

    def grant_users_viewer_access(self, session_id, usernames):
        '''
            Update a session's owner, can only be called by an admin
            or the creator.
        '''
        try:
            guids = self.get_user_guids(usernames)
            api = self.client['access']
            response = api.service.GrantUsersViewerAccessToSession(
                auth=self.auth_info, sessionId=session_id, userIds=guids)

            if response is None or len(response) < 1:
                return False

            return True
        except Fault:
            return False

    def grant_group_viewer_access(self, session_id, group_name):
        '''
            Update a session's owner, can only be called by an admin
            or the creator.
        '''
        try:
            guids = self.get_group_guid(group_name)
            api = self.client['access']
            response = api.service.GrantGroupViewerAccessToSession(
                auth=self.auth_info, sessionId=session_id, userIds=guids)

            if response is None or len(response) < 1:
                return False

            return True
        except Fault:
            return False
