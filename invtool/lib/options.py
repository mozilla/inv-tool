from invtool.tests.test_data import TEST_DESCRIPTION, TEST_STR

import argparse
from datetime import datetime


def build_extractor(field_name, nas_name):
    def extractor(nas):
        if not getattr(nas, nas_name):
            return {}
        data = {field_name: getattr(nas, nas_name)}
        return data
    return extractor


def extract_pk(nas, field_name):
    return {field_name: getattr(nas, field_name)}


def write_num_argument(parser, name, dest, help_text, required=False):
    parser.add_argument(
        '--{0}'.format(name), default=None, type=int,
        dest=dest, help=help_text, required=required
    )
    return parser


def _extract_pk(nas, field_name):
    return {field_name: nas.pk}


def update_pk_argument(field_name, rdtype):
    def add_update_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--pk', required=True, default=None, type=int,
            dest='pk', help="The database integer primary key (id) of the "
            "{0} you are updating.".format(rdtype)
        )
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_update_pk_argument, extract_pk, lambda: None


def detail_pk_argument(field_name, rdtype):
    def add_detail_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--pk', required=True, default=None, type=int,
            dest='pk', help="The database integer primary key (id) of the "
            "{0} you are getting detail about.".format(rdtype)
        )
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_detail_pk_argument, extract_pk, lambda: None


def delete_pk_argument(field_name, rdtype):
    # Required has no affect.
    def add_delete_pk_argument(parser, **kwargs):
        parser.add_argument(
            '--pk', default=None, type=int, dest='pk',
            help="Delete the {0} record with the database primary key of "
            "'pk'".format(rdtype), required=True
        )
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_delete_pk_argument, extract_pk, lambda: None


def description_argument(field_name):
    def add_desc_arg(parser, **kwargs):
        parser.add_argument(
            '--description', default="", type=str, dest='description',
            help="Tell us a little about this record", required=False
        )

    def test_data():
        return 'description', TEST_DESCRIPTION

    return add_desc_arg, build_extractor(field_name, 'description'), test_data


def comment_argument(field_name):
    def add_com_arg(parser, **kwargs):
        parser.add_argument(
            '--comment', default="", type=str,
            dest='comment', help="Use this to record why a change is "
            "being made", required=False
        )

    def test_data():
        return 'comment', TEST_DESCRIPTION  # Reuse this test data

    return add_com_arg, build_extractor(field_name, 'comment'), test_data


def general_argument(field_name, help, type=lambda x: x, test_data=None):
    real_fname = field_name.replace('-', '_')

    def add_srt_arg(parser, **kwargs):
        parser.add_argument(
            '--{0}'.format(field_name), default="", type=str,
            dest=real_fname, required=False, help=help
        )

    if test_data is None:
        def test_data_fun():
            return field_name, TEST_STR()  # Reuse this test data
    else:
        test_data_fun = test_data

    return add_srt_arg, build_extractor(real_fname, real_fname), test_data_fun


def datetime_argument(field_name, help):
    def parse_datetime(date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%dT%M:%H')
        except ValueError:
            raise argparse.ArgumentTypeError(
                '{0} is not in the format yyyy-mm-ddThh-mm (iso-8601)'.format(
                    date_str)
            )

    def test_data_fun():
        return field_name, '2013-02-02T11:11'

    return general_argument(
        field_name, help, type=parse_datetime, test_data=test_data_fun
    )


def date_argument(field_name, help):
    def parse_date(date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise argparse.ArgumentTypeError(
                '{0} is not in the format yyyy-mm-dd'.format(
                    date_str)
            )

    def test_data_fun():
        return field_name, '2013-02-02'

    return general_argument(
        field_name, help, type=parse_date, test_data=test_data_fun
    )
