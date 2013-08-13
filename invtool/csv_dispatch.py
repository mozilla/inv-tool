import requests
import sys

try:
    import simplejson as json
except ImportError:
    import json

from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib.config import REMOTE, auth


class CSVDispatch(Dispatch):
    dgroup = dtype = 'csv'

    def build_parser(self, base_parser):
        # Search is a top level command.
        mcsv = base_parser.add_parser(
            'csv', add_help=True, help='System CSV exporter'
        )
        mcsv_options = mcsv.add_mutually_exclusive_group(required=True)
        mcsv_options.add_argument(
            '--query', '-q', type=str, dest='query',
            help='A searcy query'
        )

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def csv(self, nas):
        if nas.query:
            return self.query(nas)
        else:
            return (0, ['What do you want?'])

    def query(self, nas):
        tmp_url = "/en-US/csv/ajax_csv_exporter/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'content-type': 'application/json'}
        search = {'search': nas.query}
        resp = requests.get(url, params=search, headers=headers, auth=auth())
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, search
            ))
        was_json = nas.p_json
        nas.p_json = True  # Do this so we can play with the response
        ret_code, raw_results = self.handle_resp(nas, search, resp)
        if ret_code:
            return (ret_code, raw_results)  # repack and go home
        results = json.loads(raw_results[0])
        if 'csv_content' not in results:
            return 1, []
        else:
            if was_json:
                return 0, raw_results
            return 0, [''.join(results['csv_content'])]


registrar.register(CSVDispatch())
