from mock import patch
import unittest

from panopto.auth import PanoptoAuth
from panopto.tests.patches import mock_soap_client


class TestPanoptoAuth(unittest.TestCase):

    def setUp(self):
        with patch.object(PanoptoAuth, '_client', mock_soap_client):
            self.auth = PanoptoAuth('test.hosted.panopto.com')

    def test_user_key(self):
        self.assertEqual(PanoptoAuth.user_key('foo', 'BAR'), 'BAR\\foo')

    def test_auth_code(self):
        user_key = 'BAR\\foo'
        application_key = 'd0dbe76a-40af-4de8-93c6-4df6f413f0e1'
        self.assertIsNotNone(
            PanoptoAuth._auth_code(
                'test.hosted.panopto.com', user_key, application_key))

    def test_authenticate_with_password(self):
        self.assertIsNone(
            self.auth.authenticate_with_password('foo', 'bar'))

        self.assertEqual(
            self.auth.authenticate_with_password('test', 'bar'),
            'valid session')

    def authenticate_with_application_key(self):
        self.assertIsNone(
            self.auth.authenticate_with_application_key('foo', 'bar'))

        self.assertEqual(
            self.auth.authenticate_with_application_key('test', 'bar'),
            'valid session')
