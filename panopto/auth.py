import hashlib

from zeep import Client
from zeep.exceptions import Fault


class PanoptoAuth(object):
    '''
        Integration with Panopto's SOAP API service for authentication.
        Authentication can take place via
        * LogOnWithPassword - username & password
        * LogOnWithExternalProvider -
            username
            instance_name - The instance name as set in
                Panopto > System > Identity Providers
            application key - The key produced through
                Panopto > System > Identity Providers
                returns a dict of hashed auth code and user key

        https://support.panopto.com/articles/Documentation/api-0
    '''

    def __init__(self, server):
        self.server = server
        self.client = self._client('Auth')

    def _client(self, name):
        url = 'https://{}/Panopto/PublicAPI/4.6/{}.svc?wsdl'.format(
            self.server, name)
        return Client(url)

    @classmethod
    def _auth_code(cls, server, user_key, application_key):
        payload = user_key + '@' + server + '|' + application_key
        return hashlib.sha1(payload.encode('utf-8')).hexdigest().upper()

    @classmethod
    def user_key(cls, username, instance_name):
        return '%s\\%s' % (instance_name, username)

    @classmethod
    def auth_info(cls, server, username,
                  instance_name=None, application_key=None,
                  password=None):
        '''
            Utility function to retrieve the authenticationInfo for a
            SOAP call. The authInfo allows a short-circuit path to
            authenticate a user and perform the call in one go

            * server
            * username
            * instance name
            * application_key

            returns AuthenticationInfo object with hashed auth_code
        '''
        user_key = cls.user_key(username, instance_name)
        if password:
            return {'UserKey': user_key, 'Password': password}
        elif application_key:
            code = cls._auth_code(server, user_key, application_key)
            return {'UserKey': user_key, 'AuthCode': code}
        else:
            return None

    def authenticate_with_password(self, username, password):
        try:
            self.client.service.LogOnWithPassword(
                userKey=username, password=password)

            # return the underlying request object
            # @todo - does it make more sense to return the auth cookie?
            return self.client.transport.session
        except (Fault, AttributeError):
            pass

        return None

    def authenticate_with_application_key(
            self, username, instance_name, application_key):

        try:
            user_key = self.user_key(username, instance_name)
            auth_code = self._auth_code(
                self.server, user_key, application_key)
            self.client.service.LogOnWithExternalProvider(
                userKey=user_key, authCode=auth_code)

            # return the underlying request object
            # @todo - does it make more sense to return the auth cookie?
            return self.client.transport.session
        except (Fault, AttributeError):
            pass

        return None
