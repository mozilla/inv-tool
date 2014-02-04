import requests
import sys

try:
    import simplejson as json
except ImportError:
    import json

from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib.config import REMOTE, auth


class DecommissionDispatch(Dispatch):
    dgroup = dtype = 'decommission'

    def build_parser(self, base_parser):
        # BA is a top level command.
        p = base_parser.add_parser(
            'decommission', add_help=True,
            help="Decommision a host. This command only changes System, SREG, "
            "and HWAdapter objects",
        )

        p.add_argument(
            'hostnames', metavar='HOSTNAME', type=str, nargs='+',
            help='A list of hostnames of systems that should be decommissioned'
        )

        p.add_argument(
            '--commit', action='store_true', default=False,
            help="Commit changes to the db."
        )

        p.add_argument(
            '--comment', type=str, default='', required=True,
            help="A bug number would be nice"
        )

        p.add_argument(
            '--no-decommission-sreg', action='store_false', default=True,
            help="Don't decommission SREG objects (True by default)"
        )

        p.add_argument(
            '--no-convert-to-sreg', action='store_false', default=True,
            help="Don't try to convert a system to use SREG objects"
        )

        p.add_argument(
            '--no-remove-dns', action='store_false', default=True,
            help="Don't remove CNAME and SRV records associated to this "
            "system.  A/PTR records from SREG will still be removed"
        )

        p.add_argument(
            '--decommission-system-status', type=str, default='decommissioned',
            help="The *name* of the status to set the systems to "
            "(i.e. 'spare'). By default " "the status is set to "
            "'decommissioned'"
        )

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def decommission(self, nas):
        # naively read in from stdin
        tmp_url = "/en-US/decommission/hosts/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        main_json = json.dumps({
            'systems': nas.hostnames,
            'options': {
                'decommission_sreg': nas.no_decommission_sreg,
                'decommission_system_status': nas.decommission_system_status,
                'convert_to_sreg': nas.no_convert_to_sreg,
                'remove_dns': nas.no_remove_dns
            },
            'commit': nas.commit,
            'comment': nas.comment
        })

        resp = requests.post(url, data=main_json, headers=headers, auth=auth())
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, main_json
            ))

        return self.handle_resp(nas, main_json, resp)

    def format_response(self, nas, resp_msg, user_msg):
        resp_list = []
        if nas.p_json:
            resp_list.append(json.dumps(resp_msg, indent=2))
        else:
            resp_list.append(user_msg)
            messages = None
            for k, v in resp_msg.iteritems():
                if k == 'options':
                    resp_list.append("Decommission options used:")
                    for k_i, v_i in v.iteritems():
                        resp_list.append("\t{0}: {1}".format(k_i, v_i))
                elif k == 'systems':
                    resp_list.append("systems: {0}".format(', '.join(v)))
                elif k == 'messages':
                    messages = v
                else:
                    resp_list.append("{0}: {1}".format(k, v))
            if messages:
                resp_list.append(
                    "Additional information returned by Inventory:"
                )
                resp_list += messages

        return resp_list

registrar.register(DecommissionDispatch())
