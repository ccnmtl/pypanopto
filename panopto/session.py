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

    def _client(self, server, name):
        url = 'https://{}/Panopto/PublicAPI/4.6/{}.svc?wsdl'.format(
            server, name)
        return Client(url)

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

    def update_session_owner(self, new_owner, instance_name, session_id):
        '''
            Update a session's owner, can only be called by an admin
        '''
        try:
            user_key = PanoptoAuth.user_key(instance_name, new_owner)

            response = self.client['session'].service.UpdateSessionOwner(
                auth=self.auth_info, sessionIds=[session_id],
                newOwnerUserKey=user_key)

            if response is None or len(response) < 1:
                return False

            return True
        except Fault:
            return False

    def grant_view_access(self, viewer, instance_name, session_id):
        '''
            Update a session's owner, can only be called by an admin
            or the creator. Not yet working in my dev environment
        '''
        try:
            user_key = PanoptoAuth.user_key(viewer, instance_name)
            response = self.client['user'].service.GetUserByKey(
                auth=self.auth_info, userKey=user_key)

            obj = serialize_object(response)
            user_id = obj[0]['ID']

            api = self.client['access']
            response = api.service.GrantUsersViewerAccessToSession(
                auth=self.auth_info, sessionId=session_id,
                userIds=[user_id])

            if response is None or len(response) < 1:
                return False

            return True
        except Fault:
            return False
