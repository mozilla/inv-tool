=========
 invtool
=========

-------------------------------------------------------------------
A Command Line Interface for poking at Mozilla's Inventory project.
-------------------------------------------------------------------

Notes On Installing
===================

``invtool`` requires ``requests`` and ``simplejson`` (and ``argparse`` if you are running python2.6)::

    sudo pip install -r requirements.txt
    sudo python setup.py install

``invtool`` requires you to store your ldap username in a clear text
configuration file. Your ldap password can be stored either in plaintext in the
same file or else in the system keyring. In order to use the keyring you need
`python-keyring <https://pypi.python.org/pypi/keyring>`_.  ``invtool`` tries to
find a configuration file by first looking at ``./etc/invtool.conf`` and if it
can't find anything there, ``/etc/invtool.conf``. Here is a quick tip for a
non-root install::

    git clone git@github.com:uberj/inv-tool.git invtool
    cd invtool
    export PYTHONPATH=.:$PYTHONPATH
    ln -s ./bin/invtool ./devinvtool
    ./devinvtool status

On this first invocation, if no credentials have been previously set, invtool
will prompt you for them. If the keyring module is present, your password will
be stored in the system keyring for later use under the service
"invtool-ldap". The keyring service name can be changed in the configuration
file.

RTFM
====

``man invtool`` OR checkout the repo and run ``make man``.
