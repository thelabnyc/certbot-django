from django.conf.urls import include, url
from django.contrib import admin

import certbot_django.server.urls


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^\.well-known/', include(certbot_django.server.urls))
]
