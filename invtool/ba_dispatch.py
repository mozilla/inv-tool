import requests
import sys

try:
    import simplejson as json
except ImportError:
    import json

from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib.config import REMOTE, auth


class BA(Dispatch):
    def handle_ba_resp(self, nas, query, resp):
        ret_code, raw_results = self.handle_resp(nas, query, resp)
        if ret_code:
            return (ret_code, raw_results)  # repack and go home
        results = json.loads(raw_results[0])
        if 'errors' in results:
            return 1, [json.dumps(results, indent=4, sort_keys=True)]
        else:
            return 0, [json.dumps(results, indent=4, sort_keys=True)]


class BAImportDispatch(BA):
    dgroup = dtype = 'ba_import'

    def build_parser(self, base_parser):
        # BA is a top level command.
        p = base_parser.add_parser(
            'ba_import', help="Bulk Action Import. To use, send a JSON blob "
            "into STDIN.", add_help=True
        )
        p.add_argument(
            '--commit', action='store_true', default=False,
            help="Commit changes to the db."
        )

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def ba_import(self, nas):
        # naively read in from stdin
        raw_json = nas.IN.read().strip('\n')
        return self.do_import(nas, raw_json)

    def do_import(self, nas, main_json):
        tmp_url = "/en-US/bulk_action/import/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        resp = requests.post(url, data=main_json, headers=headers, auth=auth())
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, main_json
            ))
        nas.p_json = True  # Do this so we can play with the response
        return self.handle_ba_resp(nas, main_json, resp)


class BAExportDispatch(BA):
    dgroup = dtype = 'ba_export'

    def build_parser(self, base_parser):
        # BA is a top level command.
        ba = base_parser.add_parser(
            'ba_export', help="Bulk Action Export.", add_help=True
        )
        ba.add_argument(
            '--query', '-q', dest='query', type=str, help="A query string "
            "surrounded by quotes. I.E `search -q 'foo.bar.mozilla.com'`",
            default=None, required=False
        )

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def ba_export(self, nas):
        if nas.query:
            return self.query(nas)
        else:
            return (0, ['What do you want?'])

    def query(self, nas):
        tmp_url = "/bulk_action/export/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'content-type': 'application/json'}
        query = {'q': nas.query}
        resp = requests.get(url, params=query, headers=headers, auth=auth())
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, query
            ))
        nas.p_json = True  # Do this so we can play with the response
        return self.handle_ba_resp(nas, query, resp)


class BAShowDispatch(BA):
    dgroup = dtype = 'ba_show'

    def build_parser(self, base_parser):
        # BA is a top level command.
        ba = base_parser.add_parser(
            'ba_show', help="Show fields on a bulk action json blob.",
            add_help=True
        )
        ba.add_argument(
            '--query', '-q', dest='query', type=str, help="A query string "
            "surrounded by quotes. I.E `search -q 'foo.bar.mozilla.com'`",
            default=None, required=False
        )

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def ba_show(self, nas):
        if nas.query:
            return self.query(nas)
        else:
            return (0, ['What do you want?'])

    def query(self, nas):
        tmp_url = "/bulk_action/export/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'content-type': 'application/json'}
        query = {'q': nas.query}
        resp = requests.get(url, params=query, headers=headers, auth=auth())
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, query
            ))

        nas.p_json = True  # Do this so we can play with the response

        ret_code, raw_results = self.handle_resp(nas, query, resp)
        if ret_code:
            return (ret_code, raw_results)  # repack and go home
        results = json.loads(raw_results[0])
        return ret_code, self.show_lookup_paths(results)

    def show_lookup_paths(self, blob):
        prefix = ''
        try:
            blobs = blob['systems']
        except KeyError:
            raise KeyError(
                "'systems' wasn't in the exported blob. The API changed"
            )
        result = []
        for hostname, blob in blobs.iteritems():
            result.append("--- Lookup values for {0}".format(hostname))
            result += self._show_lookup_paths(prefix, blob)
        return result

    def _show_lookup_paths(self, prefix, blob):
        result = []
        more = []
        for key, value in blob.iteritems():
            if isinstance(value, dict):
                more += self._show_lookup_paths(
                    prefix + key + '.', value)
            elif isinstance(value, list):  # CNAME exception
                for cn in value:
                    more += self._show_lookup_paths(
                        prefix, {key: cn}
                    )
            else:
                result.append("{0}{1} = {2}".format(prefix, key, value))
        return result + more


registrar.register(BAImportDispatch())
registrar.register(BAExportDispatch())
registrar.register(BAShowDispatch())
