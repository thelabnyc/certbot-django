from acme import challenges
from asymmetric_jwt_auth import create_auth_header, generate_key_pair
from certbot import interfaces, errors
from certbot.plugins import common
from certbot.display import util as display_util
import requests
import os.path
import os
import zope.component
import zope.interface
import logging

logger = logging.getLogger(__name__)


def _test_key_dir_read_write(key_dir):
    test_file_path = os.path.join(key_dir, 'certbot-test-file.txt')

    try:
        with open(test_file_path, 'w') as testfile:
            testfile.write('test')
    except (IOError, OSError):
        raise errors.PluginError('Could not write file to %s' % key_dir)

    try:
        with open(test_file_path, 'r') as testfile:
            testfile.readlines()
    except (IOError, OSError):
        raise errors.PluginError('Could not read file from %s' % key_dir)

    try:
        os.unlink(test_file_path)
    except (IOError, OSError):
        raise errors.PluginError('Could not remove file from %s' % key_dir)


def _validate_key_dir(key_dir):
    key_dir = os.path.expanduser(key_dir)
    if not os.path.isdir(key_dir):
        raise errors.PluginError(key_dir + " does not exist or is not a directory")
    key_dir = os.path.abspath(key_dir)
    _test_key_dir_read_write(key_dir)
    return key_dir


def _validate_username(username):
    if len(username) <= 0:
        raise errors.PluginError("Username can not be blank")
    return username


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(common.Plugin):
    """Django authenticator

    This plugin allows the user to perform the domain validation by
    using a remote-Django application that has certbot_django.server
    installed.
    """

    description = 'Django Server Authenticator'
    long_description = (
        'Authenticate by connecting to a Django application that has'
        'certbot_django.server installed.'
    )


    @classmethod
    def add_parser_arguments(cls, add):
        add('username',
            help='Username for authenticating with Django server.')
        add('key-directory',
            help='Directory to store generated public / private keys or to read previously generated keys from.')
        add('public-ip-logging-ok', action='store_true',
            help='Automatically allows public IP logging (default: Ask)')


    def prepare(self):
        pass


    def more_info(self):
        return (
            'Authenticate by connecting to a Django application that has'
            'certbot_django.server installed.'
        )


    def get_chall_pref(self, domain):
        """
        Only HTTP challenges are supported currently.
        """
        return [challenges.HTTP01]


    def perform(self, achalls):
        self._verify_ip_logging_ok()
        responses = []
        for achall in achalls:
            self._perform_achall(achall)
            responses.append(achall.response(achall.account_key))
        return responses


    def cleanup(self, achalls):
        for achall in achalls:
            domain = achall.domain
            challenge = achall.chall.encode('token')
            self._remove_challenge_from_server(domain, challenge)


    def _verify_ip_logging_ok(self):
        if not self.conf('public-ip-logging-ok'):
            cli_flag = '--{0}'.format(self.option_name('public-ip-logging-ok'))
            msg = ('NOTE: The IP of this machine will be publicly logged as '
                   "having requested this certificate. If you're running "
                   'certbot in manual mode on a machine that is not your '
                   "server, please ensure you're okay with that.\n\n"
                   'Are you OK with your IP being logged?')
            display = zope.component.getUtility(interfaces.IDisplay)
            if display.yesno(msg, cli_flag=cli_flag, force_interactive=True):
                setattr(self.config, self.dest('public-ip-logging-ok'), True)
            else:
                raise errors.PluginError('Must agree to IP logging to proceed')


    def _perform_achall(self, achall):
        domain = achall.domain
        challenge = achall.chall.encode('token')
        response = achall.validation(achall.account_key)
        self._add_challenge_to_server(domain, challenge, response)


    def _add_challenge_to_server(self, domain, challenge, response):
        url = 'http://{}/.well-known/challenges/'.format(domain)
        headers = self._get_headers(domain)
        data = {
            'challenge': challenge,
            'response': response,
        }
        try:
            logger.info("Attempting to add ACMEChallenge to server: %s" % challenge)
            resp = requests.post(url, headers=headers, data=data)
            resp.raise_for_status()
            logger.info("Successfully added ACMEChallenge to server: %s" % challenge)
        except requests.RequestException as e:
            raise errors.PluginError('Encountered error when adding challenge to Django server: {}'.format(e))


    def _remove_challenge_from_server(self, domain, challenge):
        url = 'http://{}/.well-known/challenges/{}/'.format(domain, challenge)
        headers = self._get_headers(domain)
        try:
            logger.info("Attempting to remove ACMEChallenge from server: %s" % challenge)
            requests.delete(url, headers=headers)
            logger.info("Successfully removed ACMEChallenge from server: %s" % challenge)
        except requests.RequestException as e:
            logger.warning("Encountered error while removing ACMEChallenge from server: %s" % challenge)


    def _get_headers(self, domain):
        private_key = self._get_private_key(domain)
        headers = {
            'Authorization': create_auth_header(username=self._get_username(), key=private_key)
        }
        return headers


    def _get_private_key(self, domain):
        filename = 'certbot_django_id_rsa_{}'.format(domain).replace('.', '')
        private_key_file = os.path.join(self._get_key_dir(), filename)
        private_key = None

        try:
            with open(private_key_file, 'r') as keyfile:
                private_key = keyfile.read()
        except (IOError, OSError):
            if self.config.noninteractive_mode:
                raise errors.PluginError('Could not read file from %s' % self._get_key_dir())

        if not private_key:
            private_key, public_key = generate_key_pair()
            try:
                logger.info('Trying to load private key: %s' % private_key_file)
                with open(private_key_file, 'w') as keyfile:
                    keyfile.write(private_key)
            except (IOError, OSError):
                raise errors.PluginError('Could not write private key to %s' % self._get_key_dir())
            msg = (
                "Couldn't read private key from {private_key_file}, so a new key has been generated and saved. "
                "Please go your website ({url}) and add the following public key to the user '{username}'. "
                "Please also make sure that '{username}' is a staff user and has permission to add and "
                "delete AcmeChallenge objects."
                "\n\n"
                "{public_key}"
            )
            msg = msg.format(
                private_key_file=private_key_file,
                url="http://{}/admin/asymmetric_jwt_auth/publickey/add/".format(domain),
                username=self._get_username(),
                public_key=public_key)
            display = zope.component.getUtility(interfaces.IDisplay)
            display.notification(msg, wrap=False, force_interactive=True)

        return private_key


    def _get_username(self):
        return self._get_config('username', 'Django username', _validate_username)


    def _get_key_dir(self):
        return self._get_config('key-directory', 'key storage directory', _validate_key_dir)


    def _get_config(self, option, name, validation_fn):
        value = self.conf(option)
        if not value:
            value = self._prompt_for_config("Input the {}".format(name), validation_fn)
            setattr(self.config, self.dest(option), value)
        if not value:
            cli_flag = '--{0}'.format(self.option_name(option))
            raise errors.PluginError('Must provide {} with flag {}'.format(name, cli_flag))
        return validation_fn(value)


    def _prompt_for_config(self, prompt, validation_fn=lambda value: value):
        display = zope.component.getUtility(interfaces.IDisplay)
        while True:
            code, value = display.directory_select(prompt, force_interactive=True)
            if code == display_util.HELP:
                return None
            elif code == display_util.CANCEL:
                return None
            else:
                try:
                    return validation_fn(value)
                except errors.PluginError as error:
                    display.notification(str(error), pause=False)
