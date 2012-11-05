import pprint
import sys
import ConfigParser
import pdb
import requests
import simplejson as json
from invdns.options import *

pp = pprint.PrettyPrinter(indent=4)
auth=None
API_MAJOR_VERSION = 1
CONFIG_FILE = "./config.cfg"

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

host = config.get('remote','host')
port = config.get('remote','port')
REMOTE = "http://{0}:{1}".format(host, port)


class InvalidCommand(Exception):
    pass

class Dispatch(object):
    object_url = "/mozdns/api/v{0}_dns/{1}/{2}/"
    object_list_url = "/mozdns/api/v{0}_dns/{1}/"

    def handle_resp(self, nas, data, resp):
        def format_response(resp_msg, user_msg):
            resp_list = []
            if nas.format == 'text':
                resp_list.append(user_msg)
                for k, v in resp_msg.iteritems():
                    resp_list.append("{0}: {1}".format(k, v))
            if nas.format == 'json':
                resp_list.append(json.dumps(resp_msg))
            return resp_list

        resp_msg = self.get_resp_dict(resp)

        if resp.status_code == 404:
            return 1, format_response(resp_msg,
                                    "http_status: 404 (file not found)")
        elif resp.status_code == 204:
            if nas.format == 'text':
                return 0, ["http_status: 204 (request fulfilled)"]
            else:
                return 0, [json.dumps(resp_msg)]
        elif resp.status_code == 500:
            resp_list = [_("SERVER ERROR! (Please email this output to a "
                            "code monkey)")]
            return self.error_out(data, resp, resp_list=resp_list)
        elif resp.status_code == 400:
            # Bad Request
            if nas.format == 'json':
                return 1, [json.dumps(resp_msg)]
            elif nas.format == 'text':
                if 'error_messages' in resp_msg:
                    return self.get_errors(resp_msg['error_messages'])
                else:
                    return 1, ["http_status: 400 (bad request)"]
        elif resp.status_code == 201:
            return 0, format_response(resp_msg, "http_status: 201 (created)")
        elif resp.status_code == 202:
            return 0, format_response(resp_msg, "http_status: 202 (Accepted)")
        elif resp.status_code == 200:
            return 0, format_response(resp_msg, "http_status: 200 (Success)")
        else:
            resp_list = []
            resp_list.append("Client didn't understand the response.")
            resp_list.append("CLIENT ERROR! (Please email this output to a "
                             "code monkey)")
            return self.error_out(nas, data, resp, resp_list=resp_list)

    def get_errors(self, resp_msg):
        messages = json.loads(resp_msg, 'unicode')
        errors = []
        for error, msg in messages.iteritems():
            if error == '__all__':
                error = "Object Error"
            errors.append("Error: {0}  {1}".format(error, ', '.join(msg)))
        return 1, errors

    def get_resp_dict(self, resp):
        if resp.text:
            # Tasty pie returns json that is unicode. Thats ok.
            msg = json.loads(resp.text, 'unicode')
        else:
            msg = {'message': 'No message from server'}
        msg['http_status'] = resp.status_code
        return msg

    def error_out(self, nas, data, resp, resp_list=[]):
        resp_list.append(str(nas))
        resp_list.append(str(data))
        resp_list.append(pprint(vars(resp)))
        return 1, resp_list


class DNSDispatch(Dispatch):
    def delete(self, nas):
        url = self.object_url.format(API_MAJOR_VERSION,
                                          self.resource_name, nas.pk)
        url = "{0}{1}?format=json".format(REMOTE, url)
        headers = {'content-type': 'application/json'}
        resp = requests.delete(url, headers=headers, auth=auth)
        return self.handle_resp(nas, {}, resp)

    def detail(self, nas):
        url = self.object_url.format(API_MAJOR_VERSION,
                                          self.resource_name, nas.pk)
        url = "{0}{1}?format=json".format(REMOTE, url)
        headers = {'content-type': 'application/json'}
        resp = requests.get(url, headers=headers, auth=auth)
        return self.handle_resp(nas, {}, resp)

    def update(self, nas):
        data = self.get_update_data(nas)  # Dispatch defined Hook
        tmp_url = self.object_url.format(API_MAJOR_VERSION, self.resource_name,
                                    nas.pk)
        url = "{0}{1}".format(REMOTE, tmp_url)
        return self.action(nas, url, requests.patch, data)

    def create(self, nas):
        data = self.get_create_data(nas)  # Dispatch defined Hook
        tmp_url = self.object_list_url.format(API_MAJOR_VERSION,
                                              self.resource_name)
        url = "{0}{1}".format(REMOTE, tmp_url)
        return self.action(nas, url, requests.post, data)

    def action(self,nas, url, method, data):
        headers = {'content-type': 'application/json'}
        data = json.dumps(data)
        resp = method(url, headers=headers, data=data, auth=auth)
        return self.handle_resp(nas, data, resp)

    def get_create_data(self, nas):
        data = {}
        for add_arg, extract_arg, test_method in self.create_args:
            data.update(extract_arg(nas))
        return data

    def get_update_data(self, nas):
        data = {}
        for add_arg, extract_arg, test_method in self.update_args:
            data.update(extract_arg(nas))
        return data


class Registrar():
    dns_dispatches = []
    dispatches = []
    def register(self, dispatch):
        if isinstance(dispatch, DNSDispatch):
            self.dns_dispatches.append(dispatch)
        else:
            self.dispatches.append(dispatch)

registrar = Registrar()


def build_dns_parsers(base_parser):
    # Search is a top level command.
    search = base_parser.add_parser('search', help="Search for stuff.",
                                    add_help=True)
    search.add_argument('-q', dest='query', type=str, help="A query string "
                        "surrounded by quotes. I.E `search -q "
                        "'foo.bar.mozilla.com'`", required=True)

    # Build all the records

    for dispatch in registrar.dns_dispatches:
        record_base_parser = base_parser.add_parser(dispatch.rdtype, help="The"
                " interface for {0} records".format(dispatch.rdtype),
                add_help=True)
        action_parser = record_base_parser.add_subparsers(help="{0} record "
                    "actions".format(dispatch.rdtype), dest='action')
        build_create_parser(dispatch, action_parser)
        build_update_parser(dispatch, action_parser)
        build_delete_parser(dispatch, action_parser)
        build_detail_parser(dispatch, action_parser)


class SearchDispatch(Dispatch):
    dtype = 'search'

    def search(self, nas):
        """This is the fast display minimal information search. Use the
        object_search to get a more detailed view of a specific type of object.
        """
        tmp_url = "/core/search/search_dns_text/"
        url = "{0}{1}".format(REMOTE, tmp_url)
        headers = {'content-type': 'application/json'}
        search = {'search': nas.query}
        resp = requests.get(url, params=search, headers=headers, auth=auth)
        if resp.status_code == 500:
            resp_list = [_("CLIENT ERROR! (Please email this output to "
                         "a code monkey)")]
            self.error_out(nas, search, resp, resp_list=resp_list)
            return
        results = resp.text.strip()
        if not results:
            return 0, ['']
        else:
            return 0, [results]


registrar.register(SearchDispatch())


def build_create_parser(dispatch, action_parser):
    create_parser = action_parser.add_parser('create', help="Create "
                        "a(n) {0} record".format(dispatch.rdtype))
    for add_arg, extract_arg, test_method in dispatch.create_args:
        add_arg(create_parser)


def build_update_parser(dispatch, action_parser):
    update_parser = action_parser.add_parser('update', help="Update "
                        "a(n) {0} record".format(dispatch.rdtype))
    for add_arg, extract_arg, test_method in dispatch.update_args:
        add_arg(update_parser, required=False)


def build_delete_parser(dispatch, action_parser):
    delete_parser = action_parser.add_parser('delete', help="Delete "
                        "a(n) {0} record".format(dispatch.rdtype))
    for add_arg, extract_arg, test_method  in dispatch.delete_args:
        add_arg(delete_parser)


def build_detail_parser(dispatch, action_parser):
    detail_parser = action_parser.add_parser('detail', help="Detail "
                        "a(n) {0} record".format(dispatch.rdtype))
    for add_arg, extract_arg, test_method in dispatch.detail_args:
        add_arg(detail_parser)


class DispatchA(DNSDispatch):
    resource_name = 'addressrecord'
    rdtype = 'A'
    ip_type = '4'

    create_args = [
        fqdn_argument('fqdn', rdtype), # ~> (labmda, lambda)
        ttl_argument('ttl'),
        ip_argument('ip_str', ip_type),
        view_arguments('views'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', rdtype)
    ]

    delete_args = [
        delete_pk_argument('pk', rdtype)
    ]

    detail_args = [detail_pk_argument('pk', rdtype)]

    def get_create_data(self, nas):
        data = super(DispatchA, self).get_create_data(nas)
        data['ip_type'] = self.ip_type
        return data

    def get_update_data(self, nas):
        data = super(DispatchA, self).get_update_data(nas)
        data['ip_type'] = self.ip_type
        return data

class DispatchPTR(DNSDispatch):
    resource_name = 'ptr'
    rdtype = 'PTR'

    create_args = [
        ttl_argument('ttl'),
        ip_argument('ip_str', '4'),
        view_arguments('views'),
        target_argument('name'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', rdtype)
    ]

    delete_args = [
        delete_pk_argument('pk', rdtype)
    ]

    detail_args = [detail_pk_argument('pk', rdtype)]

    def determine_ip_type(self, ip_str):
        if ip_str.find(':') > -1:
            ip_type = '6'
        else:
            ip_type = '4' # Default to 4
        return ip_type

    def get_create_data(self, nas):
        data = super(DispatchPTR, self).get_create_data(nas)
        data['ip_type'] = self.determine_ip_type(data.get('ip_str', ''))
        return data

    def get_update_data(self, nas):
        data = super(DispatchPTR, self).get_update_data(nas)
        data['ip_type'] = self.determine_ip_type(data.get('ip_str', ''))
        return data

class DispatchAAAA(DispatchA):
    rdtype = 'AAAA'
    ip_type = '6'
    create_args = [
        fqdn_argument('fqdn', rdtype), # ~> (labmda, lambda)
        ttl_argument('ttl'),
        ip_argument('ip_str', ip_type),
        view_arguments('views'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', rdtype)
    ]

    delete_args = [
        delete_pk_argument('pk', rdtype)
    ]

    detail_args = [detail_pk_argument('pk', rdtype)]


class DispatchCNAME(DNSDispatch):
    resource_name = 'cname'
    rdtype = 'CNAME'

    create_args = [
        fqdn_argument('fqdn', rdtype), # ~> (labmda, lambda)
        ttl_argument('ttl'),
        target_argument('target'),
        view_arguments('views'),
        comment_argument('comment')]

    update_args = create_args + [
        update_pk_argument('pk', rdtype)
    ]

    delete_args = [
        delete_pk_argument('pk', rdtype)
    ]

    detail_args = [detail_pk_argument('pk', rdtype)]

class DispatchSRV(DNSDispatch):
    resource_name = 'srv'
    rdtype = 'SRV'

    create_args = [
        fqdn_argument('fqdn', rdtype), # ~> (labmda, lambda)
        ttl_argument('ttl'),
        port_argument('port'),
        weight_argument('weight'),
        priority_argument('priority'),
        target_argument('target'),
        view_arguments('views'),
        comment_argument('comment')]

    update_args = create_args + [
        update_pk_argument('pk', rdtype)
    ]

    delete_args = [
        delete_pk_argument('pk', rdtype)
    ]

    detail_args = [detail_pk_argument('pk', rdtype)]


registrar.register(DispatchA())
registrar.register(DispatchAAAA())
registrar.register(DispatchCNAME())
registrar.register(DispatchPTR())
registrar.register(DispatchSRV())


def dispatch(nas):
    if hasattr(nas, 'dtype'):
        for dispatch in registrar.dispatches:
            if dispatch.dtype == nas.dtype:
                return getattr(dispatch, nas.dtype)(nas)
    for dispatch in registrar.dns_dispatches:
        if dispatch.rdtype == nas.dtype:
            return getattr(dispatch, nas.action)(nas)
