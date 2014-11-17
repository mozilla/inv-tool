#!/usr/bin/env python

import getpass
import ConfigParser
import os
import sys

try:
    import keyring
    KEYRING_PRESENT = True
except ImportError:
    print "No keyring. No point to this script running."
    sys.exit(1)

if len(sys.argv) != 2:
    CONFIG_FILE = '/etc/invtool.conf'
else:
    CONFIG_FILE = sys.argv[1]

print "Using config file at {0}".format(CONFIG_FILE)

if not os.path.exists(CONFIG_FILE):
    print "The config file {0} doesn't seem to exist".format(CONFIG_FILE)
    sys.exit(1)

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

if not config.has_option('authorization', 'keyring'):
    print "You need to set the keyring value in your config."
    sys.exit(1)


keyring.get_keyring()
try:
    ldap_pass = getpass.getpass(
        'ldap username: {0}\npassword: '
        .format(config.get('authorization', 'ldap_username'))
    )
except ConfigParser.NoOptionError, e:
    print e
    sys.exit(1)

keyring.set_password(
    config.get('authorization', 'keyring'),
    config.get('authorization', 'ldap_username'),
    ldap_pass
)
print("Saved password to keyring")
