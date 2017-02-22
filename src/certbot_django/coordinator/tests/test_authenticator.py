from acme import challenges
from asymmetric_jwt_auth import generate_key_pair
from certbot import errors
from certbot.tests import acme_util
from certbot.tests import util as test_util
import tempfile
import unittest
import six
import mock
import requests_mock
import shutil
import os.path
import re


class AuthenticatorTest(unittest.TestCase):
    def setUp(self):
        self.http_achall = acme_util.HTTP01_A
        self.achalls = [self.http_achall]
        self.config = mock.MagicMock(
            http01_port=0, django_username=None, django_key_directory=None,
            django_public_ip_logging_ok=False, noninteractive_mode=False)

        self.temp_dir = tempfile.mkdtemp()

        from certbot_django.coordinator.authenticator import Authenticator
        self.auth = Authenticator(self.config, name='django')


    def tearDown(self):
        shutil.rmtree(self.temp_dir)


    def test_bad_key_dir(self):
        self.config.django_key_directory = '/this/dir/doest/exist/'
        self.assertRaises(errors.PluginError, self.auth.prepare)


    def test_more_info(self):
        self.assertTrue(isinstance(self.auth.more_info(), six.string_types))


    def test_get_chall_pref(self):
        self.assertEqual(self.auth.get_chall_pref('example.org'), [challenges.HTTP01])


    @test_util.patch_get_utility()
    def test_ip_logging_not_ok(self, mock_get_utility):
        mock_get_utility().yesno.return_value = False
        self.assertRaises(errors.PluginError, self.auth.perform, [])


    @test_util.patch_get_utility()
    def test_ip_logging_ok(self, mock_get_utility):
        mock_get_utility().yesno.return_value = True
        self.auth.perform([])
        self.assertTrue(self.config.django_public_ip_logging_ok)


    @test_util.patch_get_utility()
    def test_perform_generate_key(self, mock_get_utility):
        self.config.django_public_ip_logging_ok = True
        self.config.django_username = 'certbot'
        self.config.django_key_directory = self.temp_dir

        with requests_mock.mock() as m:
            m.post('http://example.com/.well-known/challenges/', json={}, status_code=201)
            actual = self.auth.perform(self.achalls)
            expected = [achall.response(achall.account_key) for achall in self.achalls]
            self.assertEqual(actual, expected)
            self.assertEqual(m.call_count, 1)

        for i, (args, kwargs) in enumerate(mock_get_utility().notification.call_args_list):
            self.assertTrue("new key has been generated and saved" in args[0])
            self.assertTrue("user 'certbot'" in args[0])
            self.assertFalse(kwargs['wrap'])


    @test_util.patch_get_utility()
    def test_perform_existing_key(self, mock_get_utility):
        self.config.django_public_ip_logging_ok = True
        self.config.django_username = 'certbot'
        self.config.django_key_directory = self.temp_dir

        priv, pub = generate_key_pair()
        keypath = os.path.join(self.temp_dir, 'certbot_django_id_rsa_examplecom')
        with open(keypath, 'w') as keyfile:
            keyfile.write(priv)

        with requests_mock.mock() as m:
            m.post('http://example.com/.well-known/challenges/', json={}, status_code=201)
            actual = self.auth.perform(self.achalls)
            expected = [achall.response(achall.account_key) for achall in self.achalls]
            self.assertEqual(actual, expected)
            self.assertEqual(m.call_count, 1)

        for i, (args, kwargs) in enumerate(mock_get_utility().notification.call_args_list):
            self.assertEqual("" in args[0])
            self.assertFalse(kwargs['wrap'])


    @test_util.patch_get_utility()
    def test_perform_bad_auth(self, mock_get_utility):
        self.config.django_public_ip_logging_ok = True
        self.config.django_username = 'certbot'
        self.config.django_key_directory = self.temp_dir

        priv, pub = generate_key_pair()
        keypath = os.path.join(self.temp_dir, 'certbot_django_id_rsa_examplecom')
        with open(keypath, 'w') as keyfile:
            keyfile.write(priv)

        with requests_mock.mock() as m:
            m.post('http://example.com/.well-known/challenges/', json={}, status_code=403)
            self.assertRaises(errors.PluginError, self.auth.perform, self.achalls)


    def test_cleanup(self):
        self.config.django_public_ip_logging_ok = True
        self.config.django_username = 'certbot'
        self.config.django_key_directory = self.temp_dir

        priv, pub = generate_key_pair()
        keypath = os.path.join(self.temp_dir, 'certbot_django_id_rsa_examplecom')
        with open(keypath, 'w') as keyfile:
            keyfile.write(priv)

        with requests_mock.mock() as m:
            m.post('http://example.com/.well-known/challenges/', json={}, status_code=201)
            m.delete(re.compile('example\.com/\.well-known/challenges/[A-Za-z0-9]+/$'), json={}, status_code=204)
            self.auth.perform(self.achalls)
            self.auth.cleanup(self.achalls)
            self.assertEqual(m.call_count, 2)
