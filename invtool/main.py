import argparse
import simplejson as json
import sys

enabled_dispatches = [
    'invtool.dns_dispatch',
    'invtool.search_dispatch',
    'invtool.status_dispatch',
    'invtool.core_dispatch',
    'invtool.kv.kv_dispatch',
    'invtool.kv.kv_core_dispatch',
    'invtool.kv.kv_system_dispatch',
    'invtool.kv.kv_sreg_dispatch',
    'invtool.system_dispatch',
    'invtool.csv_dispatch',
    'invtool.ba_dispatch',
    'invtool.sreg_dispatch',
    'invtool.decommission_dispatch',
    'invtool.service_dispatch'
]

for d in enabled_dispatches:
    __import__(d)

from invtool.lib.registrar import registrar
from invtool.dispatch import dispatch


def do_dispatch(args, IN=sys.stdin):
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
    format_group.add_argument(
        '--pk-only', default=False, dest='p_pk_only', action='store_true',
        help="If an object was just update/created print the primary key"
        "of that object otherwise print nothing. No new line is printed."
    )
    base_parser = inv_parser.add_subparsers(dest='dtype')

    # Build parsers. Parses should register arguments.
    for d in registrar.dispatches:
        d.build_parser(base_parser)

    nas = inv_parser.parse_args(args)
    nas.IN = IN  # Where invtool reads its input from
    if nas.p_pk_only:
        nas.p_json = True
    return nas, dispatch(nas)


def main(args):
    nas, (resp_code, resp_list) = do_dispatch(args[1:])
    if not nas.p_silent and resp_list:
        if nas.p_pk_only:
            ret_json = json.loads('\n'.join(resp_list))
            if 'pk' in ret_json:
                print(ret_json['pk']),
        else:
            print('\n'.join(resp_list).strip())
    return resp_code
