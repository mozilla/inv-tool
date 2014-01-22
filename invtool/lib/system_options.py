from invtool.lib.options import build_extractor, general_argument
from invtool.tests.test_data import TEST_STR


def foreign_key_argument(field_name, help):
    real_fname = field_name.replace('-', '_')

    def add_srt_arg(parser, **kwargs):
        parser.add_argument(
            '--{0}-pk'.format(field_name), default="", type=str,
            dest=real_fname, required=False, help=help
        )

    def test_data():
        return '', ''

    return add_srt_arg, build_extractor(real_fname, real_fname), test_data


def hostname_argument(field_name, help):
    return general_argument(field_name, help)


def new_hostname_argument():
    def add_srt_arg(parser, **kwargs):
        parser.add_argument(
            '--new-hostname', default="", type=str,
            dest='hostname', required=False, help='If you are changing the '
            'hostname of an existing system specify it with --hostname and '
            'use this option to assign a new hostname'
        )

    def test_data():
        return 'new-hostname', TEST_STR()

    return add_srt_arg, build_extractor('hostname', 'hostname'), test_data


def notes_argument(field_name, help):
    """
    Work around for systems calling it 'Notes' and everything else calling it
    'Description'.
    """
    def add_srt_arg(parser, **kwargs):
        parser.add_argument(
            '--description', default="", type=str, dest='notes',
            required=False, help=help
        )

    def test_data():
        return 'description', 'asdfasdf'

    return add_srt_arg, build_extractor('notes', 'notes'), test_data


def str_argument(field_name, help):
    display_name = field_name.replace('_', '-')

    def add_srt_arg(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(display_name), default="", type=str,
            dest=field_name, required=False, help=help
        )

    def test_data():
        return field_name, TEST_STR()  # Reuse this test data

    return add_srt_arg, build_extractor(field_name, field_name), test_data


def system_pk_argument(action='updating'):
    def add_pk_arg(parser, **kwargs):
        arg_g = parser.add_mutually_exclusive_group(required=True)
        arg_g.add_argument(
            '--hostname', type=str, dest='pk',
            help='The hostname of a system you are {0}'.format(action)
        )
        arg_g.add_argument(
            '--pk', type=str, dest='pk',
            help='The integer primary key of a system you are '
            '{0}'.format(action)
        )

    def extract_pk(nas):
        if nas.hostname:
            return {'pk': nas.hostname}
        else:
            return {'pk': nas.pk}

    return add_pk_arg, build_extractor('hostname', 'hostname'), lambda: None
