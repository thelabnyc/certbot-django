from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'challenges', views.AcmeChallengeViewSet)


urlpatterns = [
    url(r'^acme-challenge/(?P<acme_data>.+)$', views.detail, name='acmechallenge-response'),
    url(r'^', include(router.urls)),
]
