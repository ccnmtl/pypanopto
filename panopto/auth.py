import hashlib

from zeep import Client
from zeep.exceptions import Fault


class PanoptoAuth(object):
    '''
        Integration with Panopto's SOAP API service for authentication.
        Authentication can take place via
        * username & password
        * username, instance_name and application key

        https://support.panopto.com/articles/Documentation/api-0
    '''

    def __init__(self, server):
        self.server = server
        self.client = {
            'auth': self._client('Auth')
        }

    def _client(self, name):
        url = 'https://{}/Panopto/PublicAPI/4.6/{}.svc?wsdl'.format(
            self.server, name)
        return Client(url)

    def _user_key(self, username, instance_name):
        return '%s\\%s' % (instance_name, username)

    def _auth_code(self, user_key, application_key):
        payload = user_key + '@' + self.server + '|' + application_key
        return hashlib.sha1(payload).hexdigest().upper()

    def authenticate_with_password(self, username, password):
        try:
            self.client['auth'].service.LogOnWithPassword(
                userKey=username, password=password)

            # return the underlying request object
            return self.client['auth'].transport.session
        except (Fault, AttributeError):
            pass

        return None

    def authenticate_with_application_key(
            self, username, instance_name, application_key):

        try:
            user_key = self._user_key(username, instance_name)
            auth_code = self._auth_code(user_key, application_key)
            self.client['auth'].service.LogOnWithExternalProvider(
                userKey=user_key, authCode=auth_code)

            # return the underlying request object
            return self.client['auth'].transport.session
        except (Fault, AttributeError):
            pass

        return None
