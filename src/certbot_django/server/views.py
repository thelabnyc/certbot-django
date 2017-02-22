from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, permissions
from .models import AcmeChallenge
from .serializers import AcmeChallengeSerializer


class AcmeChallengeViewSet(viewsets.ModelViewSet):
    queryset = AcmeChallenge.objects.all()
    serializer_class = AcmeChallengeSerializer
    lookup_field = 'challenge'
    permission_classes = (permissions.IsAdminUser, permissions.DjangoModelPermissions)


def detail(request, acme_data):
    acme_challenge = get_object_or_404(AcmeChallenge, challenge=acme_data)
    context = {
        'response': acme_challenge.response
    }
    return render(request, 'certbot_django/detail.html', context)
