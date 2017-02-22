from django.test import TestCase
from ..models import AcmeChallenge


class TestAcmeChallenge(TestCase):
    def test_challenge(self):
        """
        Test the challenge data in the model
        """
        challenge = 'challenge'
        response = ''
        acme_object = AcmeChallenge(challenge=challenge, response=response)
        self.assertEqual(acme_object.challenge, challenge)


    def test_response(self):
        """
        Test the response data in the model
        """
        challenge = ''
        response = 'challenge.response'
        acme_object = AcmeChallenge(challenge=challenge, response=response)
        self.assertEqual(acme_object.response, response)


    def test_str(self):
        """
        Test the __str__ representation
        """
        challenge = 'challenge'
        response = 'challenge.response'
        acme_object = AcmeChallenge(challenge=challenge, response=response)
        self.assertEqual(str(acme_object), challenge)
