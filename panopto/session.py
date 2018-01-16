from zeep.client import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

from panopto.auth import PanoptoAuth


class PanoptoSessionManager(object):

    def __init__(self, server, username, instance_name, application_key):
        self.client = self._client(server, 'SessionManagement')
        self.auth_info = PanoptoAuth(server).auth_info(
                username, instance_name, application_key)

    def _client(self, server, name):
        url = 'https://{}/Panopto/PublicAPI/4.6/{}.svc?wsdl'.format(
            server, name)
        return Client(url)

    def get_session_url(self, session_id):
        try:
            response = self.client.service.GetSessionsById(
                auth=self.auth_info, sessionIds=[session_id])

            if response is None or len(response) < 1:
                return ''

            obj = serialize_object(response)
            return obj[0]['MP4Url']
        except Fault:
            return ''
