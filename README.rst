A Command Line Interface for poking at Mozilla's Inventory project.

An Example
----------
Let's create an A record. Before using a command it can be useful to look at
the help text of the command.

```
invdns A create --help
```

Now that you know what the options are, let's create the A record
`host1.scl3.mozilla.com A 10.2.3.4`.

The command will look something like this:
```
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
```

Whenever you create an object the tool will display information about that
object.

The A record we just created does not belong to any view. To add the object to
the private view you can run this command:

```
~/ » invdns A update --pk 13033 --private
http_status: 202 (Accepted)
...
...
```

The `--pk` flag tells the api which object you want to update. The `pk` value
is returned to you when you first created the object and can be used to update,
delete, or show details about an object.

_An object's primary key (pk) is only unique within it's own type. (The
exception to this rule is A and AAAA records which are considered be the same type
of object)._

If you forget an object's primary key, you can look the object up by using the
`search` command where printed before every object is the object's primary key.
Let's look up our A record.

```
~/ » invdns search -q "host1.scl"
13033 host1.scl3.mozilla.com.                  3600 IN  A    10.2.3.4
```

It's primary key is indeed 13033.

Let's add a description to our record.

```
~/ » invdns A update --pk 13033 --description "foobar description"
http_status: 202 (Accepted)
...
...
```

Every call to update is translated into a PATCH request that is sent to the
server. The request contains the fields and values that should be used to patch
the object.

If we wanted to change the `ip` address of our A record we would use the `--ip`
flag and specify a new ip.

```
~/ » invdns A update --pk 13033 --ip 33.33.33.33
http_status: 202 (Accepted)
...
...
```

You can get a detailed description of an object by using the `detail` command.

```
~/ » invdns A detail --pk 13033
http_status: 200 (Success)
...
...
```

To delete an object use the `delete` command.

```
~/ » invdns A delete --pk 13033
http_status: 204 (request fulfilled)
```

Formating Output
----------------
There are a few ways to format the output of the tool.

```
~/ » invdns -h
usage: invdns [-h] [--json | --silent] ...
```

Formating flags (like `--json`) come directly after the name of the binary. The
`--silent` flag will silence all output and `--json` will display any output in
JSON format.

Search
------
The search tool described earlier is usefull for searching and filtering
different types of objects. The `-r` (range) option can be used to query
inventory for it's knowledge of IP ranges.

Cook Book
---------
When being displayed by the `search` command an object is always in the format:

```
<pk>    <lhs (left hand side)> <rdclass> <ttl> <rdtpe> <rhs (right hand side)>
```

We can exploit this pattern and use a tool like `awk` to do mass updates/deletes.


For example, we can add all objects that have the string `testfqdn` in their
name to the private view and remove them from the public view:

```
~/ » invdns search -q "testfqdn" | awk '{ print "invdns " $5  " update --pk " $1 " --private --no-public"}'
invdns SRV update --pk 134 --private --no-public
invdns A update --pk 13052 --private --no-public
invdns AAAA update --pk 13053 --private --no-public
invdns PTR update --pk 13483 --private --no-public
```



Notes on installing:
--------------------

```
pip install -r requirements.txt
cp config.cfg-dist config.cfg
```

Make sure to fill in the correct options in the config file
