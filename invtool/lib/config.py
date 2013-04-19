import os
import ConfigParser

API_MAJOR_VERSION = 1
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

host = config.get('remote', 'host')
port = config.get('remote', 'port')
dev = config.get('dev', 'dev')

REMOTE = "http{0}://{1}{2}".format(
    's' if dev != 'True' else '',
    host,
    '' if port == '80' else ':' + port
)

if dev == 'True':
    auth = None
elif config.has_option('authorization', 'keyring'):
    try:
        import keyring
    except ImportError:
        raise Exception(
            "The keyring module could not be imported. "
            "For keyring support, install the keyring "
            "module.")
    auth = (
        config.get('authorization', 'ldap_username'),
        keyring.get_password(
            config.get('authorization', 'keyring'),
            config.get('authorization', 'ldap_username')),
    )
    if auth[1] is None:
        raise Exception(
            "Can't find ldap password in keyring '{0}'"
            .format(config.get('authorization', 'keyring'))
        )
else:
    auth = (
        config.get('authorization', 'ldap_username'),
        config.get('authorization', 'ldap_password')
    )
