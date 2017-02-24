from asymmetric_jwt_auth.models import PublicKey
from asymmetric_jwt_auth import generate_key_pair, create_auth_header
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from ..models import AcmeChallenge


class TestAcmeChallengeViews(TestCase):
    def setUp(self):
        self.expected_challenge = 'challenge_view_test'
        self.expected_response = 'challenge_view_test_response'
        self.expected_response_bytes = b'challenge_view_test_response\n'
        self.expected_response_decode = 'challenge_view_test_response\n'
        self.test_challenge = AcmeChallenge.objects.create(challenge=self.expected_challenge, response=self.expected_response)


    def test_detail(self):
        """
        When given a valid request challenge, make sure the response is returned
        """
        url = reverse('acmechallenge-response', args=(self.expected_challenge, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, self.expected_response_bytes)
        self.assertEqual(response.content.decode(response.charset), self.expected_response_decode)


    def test_detail_404(self):
        """
        When given a bad request challenge, make sure a 404 is returned
        """
        url = reverse('acmechallenge-response', args=('fake', ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class TestAcmeChallengeAPI(TestCase):
    def setUp(self):
        self.perm_add = Permission.objects.get(codename='add_acmechallenge')
        self.perm_change = Permission.objects.get(codename='change_acmechallenge')
        self.perm_delete = Permission.objects.get(codename='delete_acmechallenge')

        self.user_joe = User.objects.create_user(username='joe')
        self.user_joe.is_staff = False
        self.user_joe.save()

        self.user_certbot = User.objects.create_user(username='certbot')
        self.user_certbot.is_staff = True
        self.user_certbot.user_permissions = [
            self.perm_add,
            self.perm_change,
            self.perm_delete,
        ]
        self.user_certbot.save()

        _priv, _pub = generate_key_pair()
        self.priv_key_joe = _priv
        PublicKey.objects.create(key=_pub, comment='Test Key', user=self.user_joe)

        _priv, _pub = generate_key_pair()
        self.priv_key_certbot = _priv
        PublicKey.objects.create(key=_pub, comment='Test Key', user=self.user_certbot)


    def test_add_challenge(self):
        matrix = (
            ('', '', status.HTTP_403_FORBIDDEN),
            ('joe', self.priv_key_joe, status.HTTP_403_FORBIDDEN),
            ('certbot', self.priv_key_joe, status.HTTP_403_FORBIDDEN),
            ('certbot', self.priv_key_certbot, status.HTTP_201_CREATED),
        )

        url = reverse('acmechallenge-list')

        data = {
            'challenge': 'foo',
            'response': 'bar',
        }

        for username, private_key, expected_status in matrix:
            headers = {}
            if username:
                headers['HTTP_AUTHORIZATION'] = create_auth_header(username=username, key=private_key)
            response = self.client.post(url, data=data, **headers)
            self.assertEquals(response.status_code, expected_status)


    def test_remove_challenge(self):
        matrix = (
            ('', '', status.HTTP_403_FORBIDDEN),
            ('joe', self.priv_key_joe, status.HTTP_403_FORBIDDEN),
            ('certbot', self.priv_key_joe, status.HTTP_403_FORBIDDEN),
            ('certbot', self.priv_key_certbot, status.HTTP_204_NO_CONTENT),
        )

        for username, private_key, expected_status in matrix:
            AcmeChallenge.objects.get_or_create(challenge='foo', response='bar')
            url = reverse('acmechallenge-detail', args=('foo', ))
            headers = {}
            if username:
                headers['HTTP_AUTHORIZATION'] = create_auth_header(username=username, key=private_key)
            response = self.client.delete(url, **headers)
            self.assertEquals(response.status_code, expected_status)


    def test_view_challenge(self):
        matrix = (
            ('', '', status.HTTP_403_FORBIDDEN),
            ('joe', self.priv_key_joe, status.HTTP_403_FORBIDDEN),
            ('certbot', self.priv_key_joe, status.HTTP_403_FORBIDDEN),
            ('certbot', self.priv_key_certbot, status.HTTP_200_OK),
        )

        for username, private_key, expected_status in matrix:
            AcmeChallenge.objects.get_or_create(challenge='foo', response='bar')
            url = reverse('acmechallenge-detail', args=('foo', ))
            headers = {}
            if username:
                headers['HTTP_AUTHORIZATION'] = create_auth_header(username=username, key=private_key)
            response = self.client.get(url, **headers)
            self.assertEquals(response.status_code, expected_status)
            if expected_status == status.HTTP_200_OK:
                self.assertEquals(response.data['challenge'], 'foo')
                self.assertEquals(response.data['response'], 'bar')
