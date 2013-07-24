import requests
import sys

try:
    import simplejson as json
except ImportError:
    import json

from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib.config import REMOTE, auth


class SearchDispatch(Dispatch):
    dgroup = dtype = 'search'

    def build_parser(self, base_parser):
        # Search is a top level command.
        search = base_parser.add_parser(
            'search', help="Search for stuff.", add_help=True
        )
        search.add_argument(
            '--query', '-q', dest='query', type=str, help="A query string "
            "surrounded by quotes. I.E `search -q 'foo.bar.mozilla.com'`",
            default=None, required=False
        )

        search.add_argument(
            '--range', '-r', dest='irange', type=str, help="Get information "
            "and statistics about an IP range. Specify the range using: "
            "<ip-start>,<ip-end> format (no spaces)", default=None,
            required=False
        )

        search.add_argument(
            '--display-integers', dest='d_integers', help="Return integers "
            "when showing free ip ranges.", action='store_true', default=False,
            required=False
        )

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def search(self, nas):
        """
        This is the fast display minimal information search. Use the
        object_search to get a more detailed view of a specific type of object.
        """
        if nas.query:
            return self.query(nas)
        elif nas.irange:
            return self.irange(nas)

    def irange(self, nas):
        tmp_url = "/core/range/usage_text/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'content-type': 'application/json'}
        start, end = nas.irange.split(',')
        search = {'start': start, 'end': end}
        if nas.d_integers:
            search['format'] = 'integers'
        resp = requests.get(url, params=search, headers=headers, auth=auth)
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, search
            ))
        was_json = nas.p_json
        nas.p_json = True  # Do this so we can play with the response
        ret_code, raw_results = self.handle_resp(nas, search, resp)
        if ret_code:
            return (ret_code, raw_results)  # repack and go home

        def display_ranges(free_ranges):
            ret_list = []
            for fstart, fend in free_ranges:
                ret_list.append("{0} to {1}".format(fstart, fend))
            return ret_list

        results = json.loads(raw_results[0], 'unicode')
        if not results:
            return 1, []
        else:
            if was_json:
                return 0, raw_results
            resp_list = ["# of Used IPs: {0}".format(results['used']),
                         "# of Unused IPs: {0}".format(results['unused']),
                         "------ Vacant IP ranges ------"]
            resp_list += display_ranges(results['free_ranges'])
            return 0, resp_list

    def query(self, nas):
        tmp_url = "/core/search/search_dns_text/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'content-type': 'application/json'}
        search = {'search': nas.query}
        resp = requests.get(url, params=search, headers=headers, auth=auth)
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, search
            ))
        was_json = nas.p_json
        nas.p_json = True  # Do this so we can play with the response
        ret_code, raw_results = self.handle_resp(nas, search, resp)
        if ret_code:
            return (ret_code, raw_results)  # repack and go home
        results = json.loads(raw_results[0], 'unicode')
        if 'text_response' not in results:
            return 1, []
        else:
            if was_json:
                return 0, raw_results
            return 0, [results['text_response']]


registrar.register(SearchDispatch())
