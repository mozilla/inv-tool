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

Formating Output
================

There are a few ways to format output:

    ::

        ~/ » invtool -h
        usage: invtool [-h] [--json | --silent] ...

Formating flags (like ``--json``) come directly after ``invtool``.
The ``--silent`` flag will silence all output and ``--json`` will display any
output in JSON format.

Return codes
============
Every execution of a command returns either ``0`` or ``1``.

Things that return ``1``:

    * HTTP 500
    * HTTP 200
    * Empty search results
    * Client errors

Everything else returns ``0``.

Searching
=========

The search command combined with the ``-q|--query`` flag is useful for
searching and filtering different types of objects.

    ::

        invtool search -q "<query string>"

The following sections are an overview of how to build a ``query string``.

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

    !
        The character ``!`` can be used to negate any search pattern. It can
        also negate the ``type`` directive and parameters in parenthesis.

        ``Example``::

            [ hostname !hostname1 ]

    OR
        The binary ``OR`` operator will return the results of two separate
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
        query containing the type directive with no other filter will return all
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

        You can specify a vlan number *and* a vlan name at the same time using
        a ',' to delimit the two values.

        ``Example``::

            [ vlan=:db,3 ]

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

    ip
        The ``ip`` directive can be used to gather site, vlan, network, range,
        and DNS information about a specific ip address.

        ``Example``::

            [ ip=:192.168.3.11 ]

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

Deleting an object
------------------

To delete an object use a record class's ``delete`` command.

    ::

        ~/ » invtool A delete --pk 13033
        http_status: 204 (request fulfilled)

Decommissioning Systems
=======================
Invtool provides a few tools to help you decommission systems in Inventory. The
decommission command is one of these tools:

By default the decommission command will do the following to a system:

- Set the system status to 'decommissioned' (override with ``--decommission-system-status``)
- Cleared values for operating_system, allocation, oob_ip, switch_ports, and oob_switch_port
- Attempt to convert the system to use SREG objects (override with ``--no-convert-to-sreg``)
- Decommission any SREG by removing it from DNS and setting its IP/FQDN to decommissioned values (override with ``--no-decommission-sreg``)
- Disables any HWAdapter objects attached to decommissioned SREG objects.
- Remove related DNS records

*invtool will report what changes it's going to make (or has made if
``--commit`` is used). Inspect the output to verify you are seeing the behavior
you are expecting*

A decommissioned SREG *IS NOT DELETED*. It merely has its fqdn and IP
set to disabled values, which are excluded from DNS, DHCP, etc. If ever the system
becomes recommissioned, setting the SREG FQDN/IP values to valid ones will
re-enable the SREG -- you'll also need to re-enable the HWAdapters if you want
DHCP to be re-enabled.

An example of a decommission command follows::

    ~/ » invtool decommission --comment "BUG 12345" --commit host1.mozilla.com
    http_status: 200 (Success)
    comment: BUG 12345
    commit: True
    systems: host1.mozilla.com
    http_status: 200
    Decommission options used:
        decommission_system_status: decommissioned
        convert_to_sreg: True
        decommission_sreg: True
    Decommission actions for host1.mozilla.com
        Cleared values for operating_system, allocation, oob_ip, switch_ports, and oob_switch_port
        Set system status to decommissioned
        ...


You can also specify multiple hostnames in one decommission command::

    ~/ » invtool decommission --comment "BUG 12345" --commit host2.mozilla.com host1.mozilla.com
    http_status: 200 (Success)
    comment: BUG 12345
    commit: True
    systems: host1.mozilla.com, host2.mozilla.com
    http_status: 200
    Decommission options used:
        decommission_system_status: decommissioned
        convert_to_sreg: True
        decommission_sreg: True
    Decommission actions for host1.mozilla.com
        Cleared values for operating_system, allocation, oob_ip, switch_ports, and oob_switch_port
        Set system status to decommissioned
        ...
    Decommission actions for host2.mozilla.com
        Cleared values for operating_system, allocation, oob_ip, switch_ports, and oob_switch_port
        Set system status to decommissioned
        ...

Without the ``--commit`` flag the decommission operation is a no-op. For
example, if you leave off the ``--commit`` flag for the first example, the
output would look like this::

    ~/ » invtool decommission --comment "BUG 12345" host1.mozilla.com
    http_status: 200 (Success)
    comment: BUG 12345
    commit: False
    systems: host1.mozilla.com
    http_status: 200
    Decommission options used:
        decommission_system_status: decommissioned
        convert_to_sreg: True
        decommission_sreg: True
    Decommission actions for host1.mozilla.com
        Cleared values for operating_system, allocation, oob_ip, switch_ports, and oob_switch_port
        Set system status to decommissioned
        ...

Note ``commit: False`` in the output -- no changes in Inventory were made.

See ``invtool decommission --help`` for more options.


Manipulating SYS (System) objects
=================================

The work flow for manipulating SYS objects is very similar to how one creates,
updates, and deletes DNS records.

Search results
--------------

The search results for systems are in the following format::

    <hostname> <oob_ip_str> INV SYS <asset_tag_str> <serial_str>

Looking up a system
-------------------

System objects can be specified using the ``--pk`` flag *or* the ``--hostname``
flag. For example, say we have a system with the hostname
``foobar.mozilla.com`` that has the primary key ``1992``. The following two
commands are equivalent.

    ::

        ~/ » invtool SYS update --pk 1992 --switch-ports 'core1:2/10, core2:2/10'
        ...
        ...
        ...

        ~/ » invtool SYS update --hostname foobar.mozilla.com --switch-ports 'core1:2/10, core2:2/10'
        ...
        ...
        ...

System --(.*)-pk flags
----------------------

Certain fields on a system need to be assigned via their relational integer
primary key. These objects include: OperatingSystem, ServerModel, Allocation,
SystemRack, SystemType, and SystemStatus. These objects require that you know
the integer ``pk`` value of the object you are assigning  *before* you update
a SYS. Invtool doesn't expose these related objects via it's search so you
will need to gather that info from another source, like Inventory's web UI.

For example, if you know you want to assign a SystemRack to a system that has
the ``pk`` value of ``77`` you can assign it via the ``--system-rack-pk``
flag.

    ::

        ~/ » invtool SYS --hostname foo.baz.mozilla.com --system-rack-pk 77
        ...
        ...
        ...

Changing a system's hostname
----------------------------

It is common for an existing system to have it's hostname changed. To do this
you can use the ``--new-hostname`` option along with the ``--hostname`` option.

    ::

        ~/ » invtool SYS update --hostname old-hostname.mozilla.com --new-hostname updated-hostname.mozilla.com
        ...
        ...
        ...

In the example above the system is looked up with the ``--hostname`` value
(``old-hostname.mozilla.com``) and has its hostname attribute updated to
the ``--new-hostname`` value (``updated-hostname.mozilla.com``). Note that this
sort of update is not idempotent.

Exporting System CSVs
---------------------

You can export csv records for system objects using the ``csv`` command. As of
right now only exportation is supported. You can narrow which system objects
you want to export by using the same search language supported by the
``search --query`` command. For example, to export all systems that match the
pattern ``node[0-9].mozilla.com``, you could run

    ::

        ~/ » invtool csv --query "/node[0-9].mozilla.com"
        ...
        ...
        ...

The first row of csv query results is always the CSV headers.

The Bulk Action API (An annotated walk through)
===============================================

The bulk action API allows you to export multiple JSON blobs from Inventory,
update the blobs, and send the blobs back to Inventory. These blobs represent
Inventory objects (i.e. system objects).

The ``ba_export`` command takes a ``--query`` parameter that is used to find
system objects to export. Try this now on a sample host (i.e. ``invtool
ba_export --query 'some.host.that.exists.mozilla.com'``). Notice that the blob
is made up of dictionaries that map to other dictionaries. This will come in
handy later.

Once you have exported a JSON blob you can make changes to it and send it back
to Inventory. Inventory will then update the object to reflect your changes.

For example, an extremely nieve way of renaming a host could be::

    invtool ba_export --query 'oldhost.mozilla.com' |
        sed 's/oldhost/newhost/' |
        invtool ba_import --commit

The first part of this command exports a JSON blob for all hosts matching
'oldhost.mozilla.com'. Next, the sed command looks for any occurrence of the
string 'oldhost' in the JSON blob and renames it to 'newhost'. The ``ba_import``
command then reads in the modified JSON blob and sends it back to Inventory,
which will process the blob and update the originally exported system.

Using scripts/ba_import_csv
---------------------------
The process of exporting a host, updating its JSON blob, and sending back to
Inventory can be done via a CSV import script: ``scripts/ba_import_csv``.

In the previous section we renamed a host on the command line. Using the
``ba_import_csv`` script we can achieve the same result with the following csv::

    hostname,            new-hostname
    oldhost.mozilla.com, newhost.mozilla.com

To read in a CSV ``mycsvfile.csv``, you would do::

    ``python scripts/ba_import_csv --csv-file mycsvfile.csv``


Using lookup paths with scripts/ba_import_csv
---------------------------------------------
Certain attributes of a system, like a key value pair, are within nested
dictionaries in system's JSON blob. For example, a key 'somekey'
would be accessed by::

    ``main_blob['systems']['hostname.mozilla.com']['keyvalue_set']['somekey']``

These nested attributes can be accessed in a CSV by using the ``.`` operator to
signify dictionary lookup. For example::

    hostname,             keyvalue_set.somekey
    hostname.mozilla.com, somevalue

This would lookup be equivalent to doing::

    main_blob['systems']['hostname.mozilla.com']['keyvalue_set']['somekey'] = 'somevalue'


Service Import/Export API
=========================
Invtool exposes the state of a specific services via the ``invtool
service_export`` command. For easy human consumption the export can be done via
``YAML`` format. To specify a service to export, use the standard IQL syntax.
For example, to export a service with the name "dns" you would do::

    ~/ » invtool service_export --yaml service.name=dns
    - alias: "Domain Name Resolution"
      business_owner: Wesley
      pk: 55
      category: Infrastructure Management
      description: Serves name resolution to IP addresses
      impact: high
      name: dns
      notes: !!python/unicode ''
      parent_service: None
      site: None
      systems: []
      tech_owner: Infra
      usage_frequency: constantly
      used_by: Anyone on the internet trying to resolve a Mozilla DNS name

Once a service's stanza has been exported it can be updated and then imported
via the ``invtool service_import`` command. For example, say you wanted to add
the hosts ``ns1.mozilla.com`` and ``ns2.mozilla.com`` to the dns service
previously exported. You would export into a local file for editing::

    ~/ » invtool service_export --yaml service.name=dns > dns.service

And then add the two hosts to the 'systems' array in the locally-stored
definition::

    ~/ » invtool service_export --yaml service.name=dns
    - alias: "Domain Name Resolution"
      business_owner: Wesley
      pk: 55
      category: Infrastructure Management
      description: Serves name resolution to IP addresses
      impact: high
      name: dns
      notes: !!python/unicode ''
      parent_service: None
      site: None
      systems:
        - ns1.mozilla.com
        - ns2.mozilla.com
      tech_owner: Infra
      usage_frequency: constantly
      used_by: Anyone on the internet trying to resolve a Mozilla DNS name

And then import the updated ``dns.service`` by either piping the contents of the
file into ``invtool`` or specifying the file to ``invtool``::

    ~/ » invtool service_import --file-path dns.service
    OR
    ~/ » cat dns.service | invtool service_import

If any errors occur during an import process in Inventory the entire import is
rolled back and the user must resolve the errors and rerun the entire import.

Systems specified under the ``systems`` key must correspond to a system in
Inventory with a matching hostname.

Creating vs. Updating
---------------------
A service is looked up in two ways: first by pk, and then if nothing is found,
by its name and site. When you include the ``pk`` attribute in a JSON/YAML blob
you are indicating to Inventory which service object to update.  This is useful
for when you are updating either the site or the name of a service.

Excluding the ``pk`` attribute will signal to Inventory that it should first try
to find a service with the name/site pair in the JSON blob, and if nothing is
found, to create a new service with the information contained in the blob.

Specifiying the parent service and dependancies
-----------------------------------------------
There are two special keys that can be used to specify when a service related to
another service: the ``parent_service`` and ``depends_on``. Both use an IQL
statement to specify which service is being listed. The IQL is always in the
following syntax::

    service.name='<service-name>' service.site__full_name='<service-site>'

Services may have one ``parent_service`` relationship and many ``depends_on``
relationships.

Taken together, the values of ``service-name`` and ``service-site`` can always
be used to uniquely identify a service.

An example of specifying a ``parent_service`` relationship for our ``dns``
example would be::

    - alias: "Domain Name Resolution"
      name: dns
      ...
      ... (removed lines)
      ...
      parent_service: service.name='dns' service.site=null
      ...
      ... (removed lines)
      ...
      site: scl3

.. note::
    When specifying a service that has no site, you must use ``service.site=null``.
    If you want to specify a service that does have a site you must specify the
    site's full name, for example ``service.site__full_name=corp.phx1``.

An example of specifying many ``depends_on`` relationships for our ``dns``
example would be::

    - alias: "Domain Name Resolution"
      name: dns
      ...
      ... (removed lines)
      ...
      depends_on:
        - service.name='ldap' service.site__full_name=scl3
        - service.name='dhcp' service.site__full_name=scl3
      ...
      ... (removed lines)
      ...
      site: scl3




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

        ~/ » invtool search -q "testfqdn view=:private" | awk '{ print "invtool " $5  " update --pk " $1 " --private --no-public"}'

        invtool SRV update --pk 134 --private --no-public
        invtool A update --pk 13052 --private --no-public
        invtool AAAA update --pk 13053 --private --no-public
        invtool PTR update --pk 13483 --private --no-public


Fetching details
----------------

You can look up the details of objects return by search results by using
something like this...

    ::

        ~/ » invtool search -q "host-name-pattern" | awk '{ print "invtool "  $5 " detail --pk " $1}' | bash)
        ...
        ...
