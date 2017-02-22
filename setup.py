#!/usr/bin/env python
from setuptools import setup, find_packages, Distribution
import codecs
import os.path

# Make sure versiontag exists before going any further
Distribution().fetch_build_eggs('versiontag>=1.2.0')

from versiontag import get_version, cache_git_tag  # NOQA


packages = find_packages('src')

install_requires = [
    'asymmetric_jwt_auth>=0.3.0',
    'Django>=1.8.17',
    'djangorestframework>=3.4.7',
    'requests>=2.13.0'
]

extras_require = {
    'coordinator': [
        'acme>=0.1.1',
        'certbot>=0.9.3',
        'zope.interface',
    ],
    'development': [
        'flake8>=3.2.1',
        'requests-mock>=1.3.0',
        'sphinx>=1.5.2',
        'versiontag>=1.2.0',
    ],
}

entry_points = {
    'certbot.plugins': [
        'auth = certbot_django.coordinator.authenticator:Authenticator',
    ],
}


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return codecs.open(fpath(fname), encoding='utf-8').read()


cache_git_tag()

setup(
    name='certbot-django',
    description="Full-stack Django / LetsEncrypt / Certbot Integration",
    version=get_version(pypi=True),
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    author="Craig Weber",
    author_email='crgwbr@gmail.com',
    url='https://github.com/crgwbr/certbot-django',
    license='ISC',
    package_dir={'': 'src'},
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points=entry_points,
)
