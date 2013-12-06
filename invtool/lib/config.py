import os
import ConfigParser
import getpass

API_MAJOR_VERSION = 1
GLOBAL_CONFIG_FILE = "/etc/invtool.conf"
HOME_CONFIG_FILE = os.path.expanduser("~/.invtool.conf")
LOCAL_CONFIG_FILE = "./etc/invtool.conf"
CONFIG_FILES = [GLOBAL_CONFIG_FILE, HOME_CONFIG_FILE, LOCAL_CONFIG_FILE]

if not any(os.path.exists(f) for f in CONFIG_FILES):
    raise Exception(
        "No configuration files (%s) found." % ', '.join(
            map(repr, CONFIG_FILES)
        )
    )

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILES)

if not config.has_section('authorization'):
    config.add_section('authorization')

host = config.get('remote', 'host')
port = config.get('remote', 'port')
dev = config.get('dev', 'dev')

REMOTE = "http{0}://{1}{2}".format(
    's' if dev != 'True' else '',
    host,
    '' if port == '80' else ':' + port
)

try:
    import keyring
    KEYRING_PRESENT = True
except ImportError:
    KEYRING_PRESENT = False


def _keyring():
    # If there's an existing keyring, let's use it!
    if (config.has_option('authorization', 'ldap_username') and
            config.get('authorization', 'ldap_username') != '' and
            config.has_option('authorization', 'keyring') and
            config.get('authorization', 'keyring') != '' and KEYRING_PRESENT):

        # use keyring
        auth = [
            config.get('authorization', 'ldap_username'),
            keyring.get_password(
                config.get('authorization', 'keyring'),
                config.get('authorization', 'ldap_username')
            )
        ]
        if auth[1] is None:
            keyring.get_keyring()
            print("Can't retrieve ldap password from keyring '{0}'"
                  .format(config.get('authorization', 'keyring')))
            auth[1] = getpass.getpass(
                'ldap username: {0}\npassword: '
                .format(config.get('authorization', 'ldap_username'))
            )
            keyring.set_password(
                config.get('authorization', 'keyring'),
                config.get('authorization', 'ldap_username'),
                auth[1]
            )
            print("Saved password to keyring")
        return tuple(auth)
    # If there's no existing keyring and we have keyring support
    #  let's try to be nice and create a keyring.
    else:
        # configure credentials
        auth = (
            raw_input('ldap username: '),
            getpass.getpass('password: ')
        )

        # store the username and service name
        config.set('authorization', 'ldap_username', auth[0])
        if (not config.has_option('authorization', 'keyring') or
                config.get('authorization', 'keyring') == ''):
            config.set('authorization', 'keyring', 'invtool-ldap')
        try:
            config.write(open(HOME_CONFIG_FILE, 'w'))
            print("Wrote new configuration to {0}".format(HOME_CONFIG_FILE))
        except OSError:
            print("could not write keyring configuration to {0}".format(
                HOME_CONFIG_FILE
            ))

        # store the password
        keyring.set_password(config.get('authorization', 'keyring'), *auth)
        print("Saved password to keyring")
        return auth


def _plaintext():
    if config.has_option('authorization', 'ldap_username'):
        username = config.get('authorization', 'ldap_username')
    else:
        username = raw_input('ldap username: ')
    if config.has_option('authorization', 'ldap_password'):
        password = config.get('authorization', 'ldap_password')
    else:
        password = getpass.getpass('ldap password: ')
    # use plaintext
    return (username, password)


def ldap_username_and_password_configured():
    return (
        config.has_option('authorization', 'ldap_password') and
        config.has_option('authorization', 'ldap_username')
    )


def keyring_configured():
    return (
        config.has_option('authorization', 'keyring') and
        config.has_option('authorization', 'ldap_username') and
        KEYRING_PRESENT
    )

# No auth required for dev
if dev == 'True':
    AUTH_TYPE = None
    _realauth = lambda: None

# Can't use keyring and a password in the config at the same time.
elif (config.has_option('authorization', 'ldap_password') and
      config.has_option('authorization', 'keyring')):
    raise Exception(
        "ldap_password and keyring cannot both be set in the configuration"
    )

# Always take keyring first
elif keyring_configured():
    AUTH_TYPE = 'keyring'
    _realauth = _keyring

# If keyring isn't configured, see if ldap username and password are configured
elif ldap_username_and_password_configured():
    AUTH_TYPE = 'plaintext'
    _realauth = _plaintext

# Nothing is configured
# If keyring is present and there is a keyring name, use keyring. invtool will
# configure it.
elif KEYRING_PRESENT and config.has_option('authorization', 'keyring'):
    AUTH_TYPE = 'keyring'
    _realauth = _keyring

# The user wants to specify everything via stdin
else:
    AUTH_TYPE = 'plaintext'
    _realauth = _plaintext


authcache = False


def auth():
    global authcache
    if authcache is False:
        authcache = _realauth()

    return authcache
