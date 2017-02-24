.. _installation:

Installation
============


Server Installation
-------------------

To use certbot-django, you must first install it in the Django application for which you'd like to obtain an SSL token.

1. Follow the instructions for installing `asymmetric_jwt_auth <https://asymmetric-jwt-auth.readthedocs.io/en/latest/install.html>`_. This is necessary for certbot to authentication with your application.

2. Install the ``certbot-django`` package.

.. code-block:: bash

    $ pip install certbot-django

3. Add ``certbot_django.server`` to your application's ``INSTALLED_APPS`` list.

.. code-block:: python
    :emphasize-lines: 12

    # myproject/settings.py
    …
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.postgres',
        …
        'asymmetric_jwt_auth',
        'certbot_django.server',
        …
    ]
    …

4. Deploy your application so that it's accessible to the Internet over HTTP on port 80.

5. Run migrations to create the necessary models.

.. code-block:: bash

    $ python manage.py migrate


Client Installation
-------------------

Next, you must install certbot-django on the system where you plan run the certbot client.

*Note: Unfortunately, you must install certbot-django globally on the system. Certbot will not be able to find the package if you install it in a virtual environment, even if certbot is installed and run from the same virtual environment.*

.. code-block:: bash

    $ pip install certbot
    $ pip install certbot-django
