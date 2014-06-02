import requests
import sys
import yaml

try:
    import simplejson as json
except ImportError:
    import json

from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib.config import REMOTE, auth


class ServiceDispatch(Dispatch):
    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def handle_service_resp(self, nas, query, resp):
        ret_code, raw_results = self.handle_resp(nas, query, resp)
        if ret_code:
            return (ret_code, raw_results)  # repack and go home

        results = json.loads(raw_results[0])
        dump = self.get_encoder(nas)

        if 'errors' in results:
            ret_code = 1
        else:
            ret_code = 0

        return ret_code, [dump(results)]


class ServiceImportDispatch(ServiceDispatch):
    dgroup = dtype = 'service_import'

    def get_encoder(self, nas):
        return lambda d: json.dumps(d, indent=4, sort_keys=True)

    def build_parser(self, base_parser):
        service_import = base_parser.add_parser(
            'service_import', help="Import a JSON or YAML file", add_help=True
        )
        service_import.add_argument(
            '--file-path', help="A path to a file containing "
            "a JSON or YAML representation that can be used for import. "
            "Piping the file into this command's STDIN also works."
        )

    def service_import(self, nas):
        # naively read in from stdin
        if nas.file_path:
            try:
                with open(nas.file_path, 'r') as fd:
                    raw_data = fd.read().strip()
            except IOError, e:
                return 1, [str(e)]

        else:
            raw_data = nas.IN.read().strip()

        try:
            data = json.loads(raw_data)
        except ValueError:
            try:
                data = yaml.load(raw_data)
            except ValueError:
                return 1, [
                    "Coulnd't parse import data as valid JSON or valid YAML"
                ]
        return self.do_import(nas, json.dumps(data))

    def do_import(self, nas, json_data):
        tmp_url = "/en-US/core/service/import/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        resp = requests.post(url, data=json_data, headers=headers, auth=auth())
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, json_data
            ))
        nas.p_json = True  # Do this so we can play with the response
        return self.handle_service_resp(nas, json_data, resp)


class ServiceExportDispatch(ServiceDispatch):
    dgroup = dtype = 'service_export'

    def get_encoder(self, nas):
        if nas.p_yaml:
            dump = lambda d: yaml.dump(d, default_flow_style=False)
        else:
            dump = lambda d: json.dumps(d, indent=4, sort_keys=True)
        return dump

    def build_parser(self, base_parser):
        service_export = base_parser.add_parser(
            'service_export', help="Export services.", add_help=True
        )
        service_export.add_argument(
            'query', type=str,
            help="A search string describing the services to export"
        )
        service_export.add_argument(
            '--yaml', action='store_true', default=False, dest='p_yaml',
            help="Export in YAML format",
        )

    def service_export(self, nas):
        tmp_url = "/core/service/export/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'content-type': 'application/json'}
        query = {'search': nas.query}
        resp = requests.get(url, params=query, headers=headers, auth=auth())
        if nas.DEBUG:
            sys.stderr.write('method: {0}\nurl: {1}\nparams:{2}\n'.format(
                'get', url, query
            ))
        nas.p_json = True  # Do this so we can play with the response
        return self.handle_service_resp(nas, query, resp)


registrar.register(ServiceImportDispatch())
registrar.register(ServiceExportDispatch())
