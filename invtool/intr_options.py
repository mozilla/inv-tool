def add_itype_argument(parser, required=False):
    parser.add_argument('--iname', metavar="inteface name",
            type=str, dest='iname', default='None',
            help="eth<primary>.<alias> or eth<primary>. Example eth0 or "
                "eth1.0. If blank it will be decided for you.",
            required=required)

def add_dns_enable(parser, required=False):
    parser.add_argument('--no-dns', action='store_true', dest='disable_dns',
            help="Disable dns. Defaults to false.", default=False, required=False)

def add_dhcp_enable(parser, required=False):
    parser.add_argument('--no-dhcp', action='store_true', dest='disable_dhcp',
            help="Disable dns. Defaults to false.", default=False, required=False)

def add_system_argument(parser, required=False):
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--system-hostname', type=str, dest='system_hostname',
            help="The hostname of the interface's system", default=False,
            required=required)
    group.add_argument('--system-pk', type=str, dest='system_pk',
            help="The pk of the interface's system", default=False,
            required=required)
    group.add_argument('--system-url', type=str, dest='system_url',
            help="The RESTful url of the interface's system", default=False,
            required=required)
