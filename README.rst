==============
Certbot Django
==============

This is a combined plugin for the certbot ACME client and also a Django-app for proving ACME challenges. It works basically like this:


Server Setup:

1. Install ``asymmetric_jwt_auth`` and ``certbot_django.server`` in your Django application.
2. Deploy your Django application somewhere and make your domain point to it.
3. Using Django Admin, create a user (maybe called ``certbot``). Make it a staff user and give it permission to add and delete ACMEChallenge objects.


First run:

1. Install ``certbot`` and ``certbot_django``.
2. Run certbot and using the ``certbot_django:auth`` authenticator plugin.::

    mkdir -p ~/.ssh/certbot/
    certbot certonly -d example.com -a certbot-django:auth --certbot-django:auth-key-directory=~/.ssh/certbot/ --certbot-django:auth-username=certbot


3. Certbot will print a public key in PEM format and ask you to add it to the ``certbot`` user (which you created a moment ago) in Django. You can do that using the Django Admin at ``http://my.domain/admin/asymmetric_jwt_auth/publickey/add/``
4. After doing this, press enter in your terminal to continue.
5. Certbot will now add ACME challenge objects to your Django installation, tell LetsEncrypt to verify them, then cleanup by removing the challenge objects.


Subsequent runs:

1. As long as you leave the certbot user and it's public key in Django and leave the private key in the same place on your computer (``~/.ssh/certbot/`` in the above example), authentication for a cert renew will be automatic.::

    certbot renew -d example.com -a certbot-django:auth --certbot-django:auth-key-directory=~/.ssh/certbot/ --certbot-django:auth-username=certbot

2. Since the private key still exists locally, it will use it instead of generating a new one.
