=========
 invtool
=========

-------------------------------------------------------------------
A Command Line Interface for poking at Mozilla's Inventory project.
-------------------------------------------------------------------

Notes On Updating
=================
Here is how you update your invtool.

The git method (recommended)
----------------------------
See which ``INVTOOL_VERSION`` you are running::

    invtool status | grep INVTOOL_VERSION

Change directory to where you cloned this repository::

    cd invtool

Update the code to the latest version::

    git pull

Install the code you just pulled in (You don't need to do this if you are running a non-root install)::

    sudo python setup.py install

Confirm you are running a newer version::

    invtool status | grep INVTOOL_VERSION


The non-git method (not recommended)
------------------------------------

Go to https://github.com/uberj/inv-tool/releases and download the latest version.

Notes On Installing
===================

``invtool`` requires ``requests`` and ``simplejson`` (and ``argparse`` if you are running python2.6)::

    sudo pip install -r requirements.txt
    sudo python setup.py install

An optional package (though highly recommend and included in
``requirements.txt``) is ``keychain``. If you need to use ``invtool`` without
it, remove it from ``requirements.txt`` and store your ldap password in
plaintext.

``invtool`` supports a few different ways of setting your credentials. Your
username can either be stored in the configuration file or passed at the
command line. Your password may be stored in the configuration file (in
plain text), stored in a `python-keyring <https://pypi.python.org/pypi/keyring>`_,
or passed on the command line. If you do not want to store your credentials
on disk at all, you must remove the ldap_username AND ldap_password entries
from the configuration file.

``invtool`` will read its configuration from

 * ``/etc/invtool.conf``
 * ``~/.invtool.conf`` and
 * ``./etc/invtool.conf``

Quick Install
-------------
Here is a quick tip for a non-root install::

    git clone https://github.com/uberj/inv-tool.git invtool
    cd invtool
    cp etc/invtool.conf-dist etc/invtool.conf
    # Set host and port
    $EDITOR etc/invtool.conf
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
