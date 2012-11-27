=========
 invtool
=========

-------------------------------------------------------------------
A Command Line Interface for poking at Mozilla's Inventory project.
-------------------------------------------------------------------

:Author: juber@mozilla.com
:organization: Mozilla IT
:Copyright: Mozilla Public Licence
:Version: 0.0.1
:Manual section: 1
:Manual group: User Tools


SYNOPSIS
========

``invtool`` ``-h``

``invtool`` [ RDCOMMAND | COMMAND ]

``COMMAND`` search [ STYPE ] *query-string*

``RDCOMMAND`` [ RDTYPE ] [ ACTION ] [ ARGS ]

``RDTYPE``` [ A | AAAA | CNAME | MX | PTR | SRV | TXT ]

``ACTION``  [create | update | delete | detail ]


Manipulating DNS Record: An Example
====================================
Before using a command it can be useful to look at the help text of the command

    ::

        invdns A create --help

To create the `A` record `host1.scl3.mozilla.com A 10.2.3.4`, run the command

    ::

        ~/ » invdns A create --fqdn host1.scl3.mozilla.com --ip 10.2.3.4
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

The `A` record we just created does not belong to any dns view. To add the object to
the private view you can run this command:

    ::

        ~/ » invdns A update --pk 13033 --private
        http_status: 202 (Accepted)
        ...
        ...

The '...' represents omitted output, which in this case was details about the
updated object.

The `--pk` flag tells the api which object you want to update. The `pk` value
is returned to you when you first created the object and can be used to update,
delete, or show details about an object.

An object's primary key (`pk`) is only unique within it's own type. (The
exception to this rule is `A` and `AAAA` records which are internally
stored as the same type of object).

If you forget an object's primary key, you can look the object up by using the
`search` command where printed before every object is the object's primary key.
To look up the `A` record `host1.scl3.mozilla.com A 10.2.3.4` you could run a
command similar to the following.

    ::

        ~/ » invdns search -q "host1.scl"
        13033 host1.scl3.mozilla.com.                  3600 IN  A    10.2.3.4

The `A` record's primary key is 13033.

An example of updating a record could be changing the description to a record.

    ::

        ~/ » invdns A update --pk 13033 --description "This record is fubar"
        http_status: 202 (Accepted)
        ...
        ...

Every call to update is translated into an HTTP `PATCH` request that is sent to
Inventory. The request contains the fields and values that should be used to
patch the object.

If we wanted to change the `ip` address of an `A` record we would use the `--ip`
flag and specify a new ip.

    ::

        ~/ » invdns A update --pk 13033 --ip 33.33.33.33
        http_status: 202 (Accepted)
        ...
        ...

You can get a detailed description of an object by using the `detail` command.

    ::

        ~/ » invdns A detail --pk 13033
        http_status: 200 (Success)
        ...
        ...

To delete an object use the `delete` command.

    ::

        ~/ » invdns A delete --pk 13033
        http_status: 204 (request fulfilled)

Formating Output
================
There are a few ways to format the output of the tool.

    ::

        ~/ » invdns -h
        usage: invdns [-h] [--json | --silent] ...

Formating flags (like `--json`) come directly after the name of the binary. The
`--silent` flag will silence all output and `--json` will display any output in
JSON format.

Searching with -q
=================
The search command combined with the `-q|--query` flag is usefull for searching
and filtering different types of objects.

    ::

        invdns search -q "<query string>"

Currently, only DNS objects are displayed; to see Systems use the web
interface's search page.

The following sections are an overview of how to build a `query string`.

Search Patterns
---------------

    a-zA-Z0-9
        Filter objects with *plain text* words. Objects that match all of the words
        are returned.

        `Example`::

            [ foopy scl3 ]
            [ puppet phx1 ]

    '/' (forward slash)
        A work starting with with */* is assumed to be regex pattern.  The
        regular language is that of MySQL.

        `Example`::

              [ /^puppet\d+ ]

Operators
---------

    \-
        The character *-* can be used to negate any search pattern. It
        can also negate the *type* directive and parameters in parenthesis.

        `Example`::
            [ hostname -hostname1 ]

    OR
        Use of the binary *OR* operator will return the results of two seperate
        queries.

        `Example`::

            [ host1 OR host2 ]

    AND
        Use of the binary *AND* operator will return the results a query that
        matches both of it's operands.

        `Example`::

            [ host1 AND domain1 ]

Directives
----------

    All directives are in the format *<directive-name>*\=:*<directive-value>*.
    You use directives in your query string.

        `Example`::

            invdns search --query "type=:SOA"

    type
        The *type* directive can be used to target a type of object.  Type is
        case insensitive. A search query contaning the type directive with no
        other filter will return all objects of that type and might take a
        while to complete depending on how many objects of that type exist.

        `Example`::

            [ type=:CNAME web ]

    zone
        The *zone* directive filters DNS records by DNS zone.

        `Example`::

            [ zone=:phx1.mozilla.com ]

    site
        The *site* directive can be used to search for objects that have IP
        addresses that fall into one of the networks associated with a
        site (datacenter or business unit).

        `Example`::

            [ site=:phx1 ]

    vlan
        The 'vlan' directive can be used to search for objects that have IP
        addresses within one of the networks associated with a specific
        vlan.

        `Example`::

            [ vlan=:db ]

    network
        The 'network' directive can be used to search for objects that have IP
        addresses within a network.

        `Example`::

            [ network=:192.168.3.0/23 ]

    range
        The *range* directive can be used to search for objects that have IP
        addresses within a specific IP range.

        `Example`::

            [ range=:192.168.3.10,192.168.3.100 ]


Free IP space
=============
Inventory is a source of truth so it can tell you which IP ranges are vacant
(and used). To see free IP space between a `start` and `end` ip use the
`--range` option of the `search` command.

For example, to see all free IP ranges between 10.0.0.0 and 10.0.0.255

    ::

        invdns search --rang "10.0.0.0,10.0.0.255"

To see the objects using IP addresses in this range, use the `range` directive
along with the `--query` option

    ::

        invdns search --query "range=:10.0.0.0,10.0.0.255"


Cook Book
=========
When being displayed by the `search` command a DNS object is always in the format:

    ::

        <pk>    <lhs (left hand side)> <rdclass> <ttl> <rdtpe> <rhs (right hand side)>

We can exploit this pattern and use a tool like `awk` to do mass updates/deletes.


For example, one could add all objects that have the string `testfqdn` in their
name to the private view and remove them from the public view:

    ::

        ~/ » invdns search -q "testfqdn" | awk '{ print "invdns " $5  " update --pk " $1 " --private --no-public"}'
        invdns SRV update --pk 134 --private --no-public
        invdns A update --pk 13052 --private --no-public
        invdns AAAA update --pk 13053 --private --no-public
        invdns PTR update --pk 13483 --private --no-public

Notes on installing:
--------------------

    ::

        pip install -r requirements.txt
        cp config.cfg-dist config.cfg


Make sure to fill in the correct options in the config file
