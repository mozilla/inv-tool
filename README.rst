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

``invtool`` also to have a configuration file with your ldap username/password
in it. Currently this file is a clear text file. ``invtool`` tries find a
configuration file by first look at ``./etc/invtool.conf`` and if
it can't find anything there, ``/etc/invtool.conf``. This allows you to run
invtool without installing it from the project root. To ease debugging and
development, you can do::

    git clone git@github.com:uberj/inv-tool.git invtool
    cd invtool
    export PYTHONPATH=.:$PYTHONPATH
    ln -s ./bin/invtool ./devinvtool
    ./devinvtool status

RTFM
====

``man invtool`` OR checkout the repo and run ``make man``.
