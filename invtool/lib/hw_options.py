from invtool.lib.options import build_extractor
from invtool.tests.test_data import TEST_MAC


def group_argument(field_name):
    def add_group_argument(parser, required=False):
        parser.add_argument(
            '--dhcp-group', type=str, dest='group',
            default='', required=required, help="The name of an existing dhcp "
            "group"
        )
    test_data = lambda: ''

    extractor = build_extractor(field_name, field_name)
    return add_group_argument, extractor, test_data


def mac_argument(field_name):
    def add_com_arg(parser, required=True, **kwargs):
        parser.add_argument(
            '--{0}'.format(field_name), default="", type=str,
            dest='mac', help="Mac Address",
            required=required
        )

    def test_data():
        return field_name, TEST_MAC()

    return add_com_arg, build_extractor(field_name, field_name), test_data


def enable_dhcp_argument(field_name):
    def add_enable_dhcp_argument(parser, required=False):
        dhcp_group = parser.add_mutually_exclusive_group()

        dhcp_group.add_argument(
            '--no-dhcp', default=False, action='store_false',
            dest='enable_dhcp', help="Disable dhcp.", required=required
        )

        dhcp_group.add_argument(
            '--dhcp', default=True, action='store_true', dest='enable_dhcp',
            help="Enabled dhcp (True by default).", required=required
        )

    def test_data():
        return '', '--no-dhcp'

    extractor = build_extractor(field_name, 'enable_dhcp')

    return add_enable_dhcp_argument, extractor, test_data


def sreg_argument(field_name):
    def add_sreg_argument(parser, required=False):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--sreg-pk', type=str, dest='sreg_pk', default=False,
            required=required, help="The pk of a registration"
        )
        group.add_argument(
            '--sreg-url', type=str, dest='sreg_url', default=False,
            required=required, help="The RESTful url of a registration"
        )

    def extract_sreg(nas):
        if nas.sreg_pk:
            sreg = nas.sreg_pk
        elif nas.sreg_url:
            sreg = nas.sreg_pk
        else:
            raise Exception('sreg is required')
        data = {field_name: sreg}
        return data

    def test_data():
        # sreg_pk will need to be evaluated in at test time
        return 'sreg-pk', '{{ sreg_pk }}'

    return add_sreg_argument, extract_sreg, test_data
