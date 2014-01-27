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
            '--comment', type=str, default='',
            help="A bug number would be nice"
        )
        p.add_argument(
            '--no-decommission-sreg', action='store_false', default=True,
            help="Don't decommission SREG objects (True by default)"
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


registrar.register(DecommissionDispatch())
