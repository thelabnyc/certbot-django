from django.db import models


class AcmeChallenge(models.Model):
    """
    Store Let's Encrypt .well-known/acme-challenge data
    """
    challenge = models.CharField(unique=True, max_length=255, help_text='The identifier for this challenge')
    response = models.CharField(max_length=255, help_text='The response expected for this challenge')


    class Meta:
        verbose_name = 'ACME Challenge'
        verbose_name_plural = 'ACME Challenges'

    def __str__(self):
        return self.challenge
