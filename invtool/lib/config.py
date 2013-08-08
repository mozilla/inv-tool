import os
import ConfigParser
import getpass

API_MAJOR_VERSION = 1
INVTOOL_VESION = 2.0
GLOBAL_CONFIG_FILE = "/etc/invtool.conf"
LOCAL_CONFIG_FILE = "./etc/invtool.conf"

if os.path.isfile(LOCAL_CONFIG_FILE):
    CONFIG_FILE = LOCAL_CONFIG_FILE
else:
    if os.path.isfile(GLOBAL_CONFIG_FILE):
        CONFIG_FILE = GLOBAL_CONFIG_FILE
    else:
        raise Exception(
            "Can't find global config file '{0}'"
            .format(GLOBAL_CONFIG_FILE)
        )

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

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
        config.write(open(CONFIG_FILE, 'w'))

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


# No auth required for dev
if dev == 'True':
    AUTH_TYPE = None
    _realauth = lambda: None
# Can't use keyring and a password in the config at the same time.
elif (config.has_option('authorization', 'ldap_password') and
      config.has_option('authorization', 'keyring')):
    raise Exception(
        "ldap_password and keyring are mutually exclusive "
        "in config file '{0}'".format(CONFIG_FILE)
    )
elif KEYRING_PRESENT:
    AUTH_TYPE = 'keyring'
    _realauth = _keyring
# If there's no keyring support, let's try to get the username and password
# from the config or command line
else:
    AUTH_TYPE = 'plaintext'
    _realauth = _plaintext


authcache = False


def auth():
    global authcache
    if authcache is False:
        authcache = _realauth()

    return authcache
