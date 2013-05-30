from invtool.lib.options import build_extractor, extract_pk


def update_pk_argument(field_name, dtype):
    display_name = field_name.replace('_', '-')

    def add_update_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(display_name), required=True,
            default=None, type=int, dest=field_name, help="The database id of "
            "the {0} KV being updated.".format(dtype)
        )
        return parser

    def _extract_pk(nas):
        return extract_pk(nas, field_name)

    def test_data():
        # kv_pk will need to be evaluated in at test time
        return display_name, '{{ kv_pk }}'

    return add_update_pk_argument, _extract_pk, test_data


def create_pk_argument(field_name, dtype):
    display_name = field_name.replace('_', '-')

    def add_update_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(display_name), required=True,
            default=None, type=int, dest=field_name, help="The Database id of "
            "the object that the new Key Value pair is for.".format(dtype)
        )
        return parser

    def _extract_pk(nas):
        return extract_pk(nas, field_name)

    def test_data():
        # kv_pk will need to be evaluated in at test time
        return display_name, '{{ obj_pk }}'

    return add_update_pk_argument, _extract_pk, test_data


def detail_pk_argument(field_name, dtype):
    display_name = field_name.replace('_', '-')

    def add_detail_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(display_name), required=True,
            default=None, type=int, dest=field_name, help="database id of the "
            "Key Value.".format(dtype)
        )
        return parser

    def _extract_pk(nas):
        return extract_pk(nas, field_name)

    def test_data():
        # kv_pk will need to be evaluated in at test time
        return display_name, '{{ kv_pk }}'

    return add_detail_pk_argument, _extract_pk, test_data


def kvlist_pk_argument(field_name, dtype):
    display_name = field_name.replace('_', '-')

    def add_detail_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(display_name), required=True,
            default=None, type=int, dest=field_name, help="database id of the "
            "object who's Key Value " "store will be returned.".format(dtype)
        )
        return parser

    def _extract_pk(nas):
        return extract_pk(nas, field_name)

    def test_data():
        # obj_pk will need to be evaluated in at test time
        return display_name, '{{ obj_pk }}'

    return add_detail_pk_argument, _extract_pk, test_data


def delete_pk_argument(field_name, dtype):
    display_name = field_name.replace('_', '-')

    # Required has no affect.
    def add_delete_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(display_name), default=None,
            type=int, dest=field_name, help="Delete the Key Value pair with "
            "the corresponding database primary key.".format(dtype),
            required=True
        )
        return parser

    def _extract_pk(nas):
        return extract_pk(nas, field_name)

    def test_data():
        # kv_pk will need to be evaluated in at test time
        return display_name, '{{ kv_pk }}'

    return add_delete_pk_argument, _extract_pk, test_data


def key_argument(field_name):
    def add_key_argument(parser, required=True):
        parser.add_argument(
            '--key/-k', default=None, type=str, dest='key',
            help="The key.", required=required
        )

    def test_data():
        return 'key', 'testkey'

    return add_key_argument, build_extractor(field_name, 'key'), test_data


def value_argument(field_name):
    def add_value_argument(parser, required=True):
        parser.add_argument(
            '--value/-v', default=None, type=str, dest='value',
            help="The value.", required=required
        )

    def test_data():
        return 'value', 'testvalue'

    return add_value_argument, build_extractor(field_name, 'value'), test_data
