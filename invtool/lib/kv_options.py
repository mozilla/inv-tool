from invtool.lib.options import build_extractor


def _extract_pk(nas, field_name):
    return {field_name: getattr(nas, field_name)}


def update_pk_argument(field_name, dtype):
    def add_update_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(field_name), required=True, default=None, type=int,
            dest=field_name, help="The database id of the {0} KV being "
            "updated/created.".format(dtype)
        )
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_update_pk_argument, extract_pk, lambda: None


def detail_pk_argument(field_name, dtype):
    def add_detail_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(field_name), required=True, default=None, type=int,
            dest=field_name, help="database id of the Key Value.".format(dtype)
        )
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_detail_pk_argument, extract_pk, lambda: None


def kvlist_pk_argument(field_name, dtype):
    def add_detail_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(field_name), required=True, default=None, type=int,
            dest=field_name, help="database id of the object who's Key Value "
            "store will be returned.".format(dtype)
        )
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_detail_pk_argument, extract_pk, lambda: None


def delete_pk_argument(field_name, dtype):
    # Required has no affect.
    def add_delete_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(field_name), default=None, type=int,
            dest=field_name, help="Delete the Key Value pair with the "
            "corresponding database primary key.".format(dtype),
            required=True
        )
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_delete_pk_argument, extract_pk, lambda: None


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
