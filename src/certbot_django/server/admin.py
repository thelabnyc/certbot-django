from django.contrib import admin
from django.utils.html import format_html
from django.core.urlresolvers import reverse, NoReverseMatch
from .models import AcmeChallenge


class AcmeChallengeAdmin(admin.ModelAdmin):
    def format_acme_url(self, acme_object):
        try:
            object_url = reverse(viewname='acmechallenge-response', args=(acme_object.challenge, ))
            return format_html("<a href='{}'>ACME Challenge Link</a>", object_url)
        except NoReverseMatch:
            return '-'
    format_acme_url.short_description = 'Link'

    fieldsets = [
        ('ACME Request', {
            'fields': [
                'challenge',
                'response',
            ],
        }),
        ('Metadata', {
            'fields': [
                'id',
                'format_acme_url',
            ],
        }),
    ]

    list_display = ['challenge', 'format_acme_url']
    ordering = ['challenge']
    readonly_fields = ['id', 'format_acme_url']
    search_fields = ['challenge', 'response']


admin.site.register(AcmeChallenge, AcmeChallengeAdmin)
