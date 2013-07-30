from invtool.lib.options import build_extractor, write_num_argument
from invtool.tests.test_data import TEST_NAME, TEST_PORT, TEST_NETWORK


def name_argument(field_name, required=False):
    def add_name_arg(parser, required=required, **kwargs):
        parser.add_argument(
            '--{0}'.format(field_name), type=str,
            dest=field_name, help="A name.",
            required=required
        )

    def test_data():
        return field_name, TEST_NAME()  # Reuse this test data

    return add_name_arg, build_extractor(field_name, field_name), test_data


def number_argument(field_name, required=False):
    def add_number_argument(parser, required=required):
        write_num_argument(
            parser, field_name, field_name, "A number number.",
            required=required
        )

    def test_data():
        return field_name, TEST_PORT

    return (
        add_number_argument,
        build_extractor(field_name, field_name),
        test_data
    )


def network_str_argument(field_name, required=False):
    def add_network_argument(parser, required=required):
        parser.add_argument(
            '--{0}'.format(field_name), type=str, dest='network_str',
            required=required, help="Complete CIDR Notation"
        )

    def test_data():
        return 'network-str', TEST_NETWORK

    def build_extractor(field_name, nas_name):
        def extractor(nas):
            if not getattr(nas, nas_name):
                return {}
            data = {field_name: getattr(nas, nas_name)}
            return data
        return extractor

    return (
        add_network_argument,
        build_extractor('network_str', 'network_str'),
        test_data
    )


def vlan_argument(field_name):
    def add_argument(parser, required=False):
        parser.add_argument(
            '--vlan-pk', type=str, dest='vlan',
            required=required, help="The pk of a vlan"
        )

    def extract_arg(nas):
        data = {}
        if nas.vlan:
            data = {field_name: nas.vlan}
        return data

    def test_data():
        # vlan will need to be evaluated in at test time
        return 'vlan-pk', '{{ vlan }}'

    return add_argument, extract_arg, test_data


def site_argument(field_name):
    def add_argument(parser, required=False):
        parser.add_argument(
            '--site-pk', type=str, dest='site',
            required=required, help="The pk of a site"
        )

    def extract_arg(nas):
        data = {}
        if nas.site:
            data = {field_name: nas.site}
        return data

    def test_data():
        # site need to be evaluated in at test time
        return 'site-pk', '{{ site }}'

    return add_argument, extract_arg, test_data
