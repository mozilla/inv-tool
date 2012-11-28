=========
 invtool
=========

-------------------------------------------------------------------
A Command Line Interface for poking at Mozilla's Inventory project.
-------------------------------------------------------------------


SYNOPSIS
========

``invtool`` ``--help``

``invtool`` [ --json | --silent ] search [ ``--query`` | ``--range`` ] *query-string*

``invtool`` [ --json | --silent ] ``rdtype`` ``action`` [ args | --help ]

    ``rdtype`` [ A | AAAA | CNAME | MX | PTR | SRV | TXT ]

    ``action``  [ create | update | delete | detail ]


RTFM
====

`man invtool` OR checkout the repo, install `docutils`, run `make view-docs`.
