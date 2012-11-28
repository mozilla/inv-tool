=========
 invtool
=========

-------------------------------------------------------------------
A Command Line Interface for poking at Mozilla's Inventory project.
-------------------------------------------------------------------

:Author: juber@mozilla.com
:organization: Mozilla IT
:Bugs: Report any bugs to juber@mozilla.com
:Copyright: Mozilla Public Licence
:Version: 0.0.1
:Manual section: 1
:Manual group: User Tools


SYNOPSIS
========

``invtool`` ``--help``

``invtool`` [ --json | --silent ] search [ ``--query`` | ``--range`` ] *query-string*

``invtool`` [ --json | --silent ] ``rdtype`` ``action`` [ args | --help ]

    ``rdtype`` [ A | AAAA | CNAME | MX | PTR | SRV | TXT ]

    ``action``  [ create | update | delete | detail ]


Formating Output
================

There are a few ways to format output:

    ::

        ~/ » invtool -h
        usage: invtool [-h] [--json | --silent] ...

Formating flags (like ``--json``) come directly after the name of the binary.
The ``--silent`` flag will silence all output and ``--json`` will display any
output in JSON format.

Searching
=========

The search command combined with the ``-q|--query`` flag is usefull for
searching and filtering different types of objects.

    ::

        invtool search -q "<query string>"

Currently, only DNS objects are displayed; to see Systems use the web
interface's search page.

The following sections are an overview of how to build a ``query string``.

Return codes
============
Every execution of a command returns either ``0`` or ``1``.

Things that return ``1``:

    * HTTP 500
    * HTTP 200
    * Empty search results
    * Client errors

Everything else returns ``0``.

Search Patterns
---------------

    a-zA-Z0-9
        Filter objects with *plain text* words. Objects that match all of the
        words are returned.

        ``Example``::

            [ foopy scl3 ]
            [ puppet phx1 ]

    '/' (forward slash)
        A word starting with with ``/`` is assumed to be regex pattern.  The
        regular language is that of MySQL.

        ``Example``::

              [ /^puppet\d+ ]

Operators
---------

    \-
        The character ``-`` can be used to negate any search pattern. It can
        also negate the ``type`` directive and parameters in parenthesis.

        ``Example``::

            [ hostname -hostname1 ]

    OR
        The binary ``OR`` operator will return the results of two seperate
        queries.

        ``Example``::

            [ host1 OR host2 ]

    AND
        The binary ``AND`` operator will return the results of a query that
        matches both of it's operands.

        ``Example``::

            [ host1 AND domain1 ]

Directives
----------

    All directives are in the format ``<directive>``\=:``<directive-value>``.
    Directives are used in query strings.

        ``Example``::

            invtool search --query "type=:SOA mozilla.com"
                # This will return all SOA records that contain 'mozilla.com'
                # in their name.

    type
        The ``type`` directive can be used to target a type of object.
        Values used in the ``type`` directive are case insensitive. A search
        query contaning the type directive with no other filter will return all
        objects of that type and might take a while to complete depending on
        how many objects of that type exist.

        ``Example``::

            [ type=:CNAME web ]
                # This returns all CNAMEs that contain the substring 'web'

    view
        Filter DNS records by view.

        ``Example``::

            [ puppet view=:private ]
                # This returns all records that contain the substring 'puppet'
                # and are in the public view

    zone
        The ``zone`` directive filters DNS records by DNS zone.

        ``Example``::

            [ zone=:phx1.mozilla.com ]
                # This returns all records the 'phx1.mozilla.com' zone

    site
        The ``site`` directive can be used to search for objects that have IP
        addresses that fall into one of the networks associated with a
        site (datacenter or business unit).

        ``Example``::

            [ site=:phx1 ]

    vlan
        The ``vlan`` directive can be used to search for objects that have IP
        addresses within one of the networks associated with a specific
        vlan.

        ``Example``::

            [ vlan=:db ]

    network
        The ``network`` directive can be used to search for objects that have IP
        addresses within a network.

        ``Example``::

            [ network=:192.168.3.0/23 ]

    range
        The ``range`` directive can be used to search for objects that have IP
        addresses within a specific IP range.

        ``Example``::

            [ range=:192.168.3.10,192.168.3.100 ]

A search that returns no objects has an exit code of ``1``. A search
returning objects has an exit code of ``0``.

Auditing IP space
=================

Inventory is a source of truth so it can tell you which IP ranges are vacant
and which IPs are used. To see free IP space between a ``start`` and ``end`` ip
use the ``search`` command combined with the ``--range`` option.

For example, to see all free IP ranges between ``10.0.0.0`` and ``10.0.0.255``

    ::

        invtool search --range "10.0.0.0,10.0.0.255"

To see the objects using IP addresses in this range, use the ``range`` directive
along with the ``--query`` option

    ::

        invtool search --query "range=:10.0.0.0,10.0.0.255"

Manipulating DNS Records
========================

Before using a command it can be useful to look at the help text of the command

    ::

        invtool A create --help

Interfacing with records is done per ``record class``. Each record class
(``A``, ``PTR``, ``CNAME``, etc.) has the commands ``create``, ``update``,
``detail``, and ``delete``.

Creating an object
------------------

To create the ``A`` record ``host1.scl3.mozilla.com A 10.2.3.4``, run the command

    ::

        ~/ » invtool A create --fqdn host1.scl3.mozilla.com --ip 10.2.3.4
        http_status: 201 (created)
        description:
        domain: scl3.mozilla.com
        views: []
        ttl: 3600
        fqdn: host1.scl3.mozilla.com
        label: host1
        meta: {u'soa': u'SOA for scl3.mozilla.com', u'fqdn': u'host1.scl3.mozilla.com'}
        http_status: 201
        ip_type: 4
        ip_str: 10.2.3.4
        pk: 13033
        resource_uri: /mozdns/api/v1_dns/addressrecord/13033/

Whenever you create an object the tool will display information about that
object.

Updating an object
------------------

The ``A`` record just created does not belong to any dns view. To add the
object to the private view run this command:

    ::

        ~/ » invtool A update --pk 13033 --private
        http_status: 202 (Accepted)
        ...
        ...

(The ``...`` represents omitted output, which in this case was details about the
updated object.)

The ``--pk`` flag tells the api which object you want to update. The ``pk`` value
is returned to you when you first created the object and can be used to update,
delete, or show details about an object.

An object's ``pk`` (primary key) is only unique within it's own type. (There is
an exception to this with  ``A`` and ``AAAA`` records, which are internally
stored as the same type of object).

If you forget an object's primary key, you can look the object up using the
``search`` command. Printed before every object returned by a search is the
object's primary key.  To look up the ``A`` record ``host1.scl3.mozilla.com A
10.2.3.4`` you could run a command similar to the following.

    ::

        ~/ » invtool search -q "host1.scl"
        13033 host1.scl3.mozilla.com.                  3600 IN  A    10.2.3.4

The ``A`` record's primary key is ``13033``.

    ::

        # Changing the description of an A record

        ~/ » invtool A update --pk 13033 --description "This record is fubar"
        http_status: 202 (Accepted)
        ...
        ...

Every call to update is translated into an HTTP ``PATCH`` request that is sent
to Inventory. The request contains the fields and values that should be used to
patch the object.

If we wanted to change the ``ip`` address of an ``A`` record we would use the
``--ip`` flag and specify a new ip.

    ::

        ~/ » invtool A update --pk 13033 --ip 33.33.33.33
        http_status: 202 (Accepted)
        ...
        ...


Details about an object
-----------------------

You can get a detailed description of an object by using a record class's
``detail`` command.

    ::

        ~/ » invtool A detail --pk 13033
        http_status: 200 (Success)
        ...
        ...

Deleteing an object
-------------------

To delete an object use a record class's ``delete`` command.

    ::

        ~/ » invtool A delete --pk 13033
        http_status: 204 (request fulfilled)


Cook Book
=========

Mass update or delete
---------------------
When being displayed by the ``search`` command a DNS object is always in the
format:

    ::

        <pk>   <lhs> <rdclass> <ttl> <rdtpe> <rhs>

We can exploit this pattern and use a tool like ``awk`` to do mass
updates/deletes.


For example, one could add all objects that have the string ``testfqdn`` in
their name to the private view and remove them from the public view:

    ::

        ~/ » invtool search -q "testfqdn" | awk '{ print "invtool " $5  " \
                    update --pk " $1 " --private --no-public"}'

        invtool SRV update --pk 134 --private --no-public
        invtool A update --pk 13052 --private --no-public
        invtool AAAA update --pk 13053 --private --no-public
        invtool PTR update --pk 13483 --private --no-public


Fetching details
----------------

You can look up the details of objects return by search results by using
something like this...

    ::

        ~/ » invtool search -q "host-name-pattern" | awk '{ print "invtool " \
                            $5 " detail --pk " $1}' | bash)
        ...
        ...
