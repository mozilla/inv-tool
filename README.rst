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

``invtool`` requires you to store your ldap username/password in a clear text
configuration file. ``invtool`` tries to find a configuration file by first
looking at ``./etc/invtool.conf`` and if it can't find anything there,
``/etc/invtool.conf``. Here is a quick tip for a non-root install::

    git clone git@github.com:uberj/inv-tool.git invtool
    cd invtool
    export PYTHONPATH=.:$PYTHONPATH
    ln -s ./bin/invtool ./devinvtool
    ./devinvtool status

RTFM
====

``man invtool`` OR checkout the repo and run ``make man``.
