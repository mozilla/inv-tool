import argparse

from invtool.dispatch import dispatch

import invtool.dns_dispatch
import invtool.search_dispatch
import invtool.status_dispatch
import invtool.kv_dispatch
from  invtool.lib.registrar import registrar


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
    for d in registrar.dispatches:
        d.build_parser(base_parser)

    nas = inv_parser.parse_args(args[1:])
    resp_code, resp_list = dispatch(nas)
    if not nas.p_silent and resp_list:
        print '\n'.join(resp_list),
    return resp_code
