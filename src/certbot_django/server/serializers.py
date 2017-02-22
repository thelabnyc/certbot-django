from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import AcmeChallenge


class AcmeChallengeSerializer(serializers.ModelSerializer):
    acme_url = serializers.SerializerMethodField()

    class Meta:
        model = AcmeChallenge
        fields = ('challenge', 'response', 'acme_url')

    def get_acme_url(self, obj):
        return reverse(viewname='acmechallenge-response', args=(obj.challenge, ), request=self.context['request'])
