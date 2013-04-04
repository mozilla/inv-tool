import argparse

from invtool.dispatch import dispatch
from invtool.dns_dispatch import build_dns_parsers
from invtool.search_dispatch import build_search_parsers
from invtool.status_dispatch import build_status_parsers
from invtool.kv_dispatch import build_kv_parsers


def main(args):
    inv_parser = argparse.ArgumentParser(prog='invtool')
    format_group = inv_parser.add_mutually_exclusive_group()
    format_group.add_argument(
        '--json', default=False, dest='p_json',  action='store_true',
        help="Format the output as JSON"
    )
    format_group.add_argument(
        '--silent', default=False, dest='p_silent', action='store_true',
        help="Silence all stdout and stderr"
    )
    format_group.add_argument(
        '--debug', default=False, dest='DEBUG', action='store_true',
        help="Print stuff"
    )
    base_parser = inv_parser.add_subparsers(dest='dtype')

    # Build parsers. Parses should register arguments.
    build_dns_parsers(base_parser)
    build_search_parsers(base_parser)
    build_status_parsers(base_parser)
    build_kv_parsers(base_parser)

    nas = inv_parser.parse_args(args[1:])
    resp_code, resp_list = dispatch(nas)
    if not nas.p_silent and resp_list:
        print '\n'.join(resp_list),
    return resp_code
