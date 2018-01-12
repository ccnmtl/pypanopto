class MockPanoptoSoapClient(object):

    class MockAuthService(object):
        @staticmethod
        def LogOnWithPassword(userKey, password):
            if userKey != 'test':
                raise AttributeError()

        @staticmethod
        def LogOnWithExternalProvider(userKey, password):
            if userKey != 'test':
                raise AttributeError()

    class MockTransport(object):
        def __init__(self):
            self.session = 'valid session'

    def __init__(self):
        self.service = self.MockAuthService()
        self.transport = self.MockTransport()


def mock_soap_client(instance, name):
    return MockPanoptoSoapClient()
