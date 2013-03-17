def add_itype_argument(parser, required=False):
    parser.add_argument(
        '--iname', metavar="inteface name", type=str, dest='iname',
        default='None', required=required, help="eth<primary>.<alias> or "
        "eth<primary>. Example eth0 or eth1.0. If blank it will be decided "
        "for you."
    )


def add_dns_enable(parser, required=False):
    parser.add_argument(
        '--no-dns', action='store_true', dest='disable_dns', default=False,
        required=False, help="Disable dns. Defaults to false."
    )


def add_dhcp_enable(parser, required=False):
    parser.add_argument(
        '--no-dhcp', action='store_true', dest='disable_dhcp', default=False,
        required=False, help="Disable dns. Defaults to false."
    )


def add_system_argument(parser, required=False):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--system-hostname', type=str, dest='system_hostname', default=False,
        required=required, help="The hostname of the interface's system"
    )
    group.add_argument(
        '--system-pk', type=str, dest='system_pk', default=False,
        required=required, help="The pk of the interface's system"
    )
    group.add_argument(
        '--system-url', type=str, dest='system_url', default=False,
        required=required, help="The RESTful url of the interface's system"
    )
