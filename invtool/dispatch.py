try:
    import simplejson as json
except ImportError:
    import json
import requests

from gettext import gettext as _
from invtool.lib.registrar import registrar
from invtool.lib.config import REMOTE, auth


class Dispatch(object):
    def format_response(self, nas, resp_msg, user_msg):
        resp_list = []
        if nas.p_json:
            resp_list.append(json.dumps(resp_msg, indent=2))
        else:
            resp_list.append(user_msg)
            for k, v in resp_msg.iteritems():
                resp_list.append("{0}: {1}".format(k, v))
        return resp_list

    def handle_resp(self, nas, data, resp):
        resp_msg = self.get_resp_dict(resp)

        if resp.status_code == 404:
            return 1, self.format_response(
                nas, resp_msg, "http_status: 404 (not found)"
            )
        elif resp.status_code == 204:
            if nas.p_json:
                return 0, [json.dumps(resp_msg, indent=2)]
            else:
                return 0, ["http_status: 204 (request fulfilled)"]
        elif resp.status_code == 500:
            resp_list = [_("SERVER ERROR! (Please email this output to a "
                         "code monkey)")]
            return self.error_out(nas, data, resp, resp_list=resp_list)
        elif resp.status_code == 400:
            # Bad Request
            if nas.p_json:
                return 1, [json.dumps(resp_msg, indent=2)]
            else:
                if 'error_messages' in resp_msg:
                    return self.get_errors(resp_msg['error_messages'])
                elif 'message' in resp_msg:
                    return 1, [resp_msg['message']]
                else:
                    return 1, ["http_status: 400 (bad request)"]
        elif resp.status_code == 201:
            return 0, self.format_response(
                nas, resp_msg, "http_status: 201 (created)"
            )
        elif resp.status_code == 202:
            return 0, self.format_response(
                nas, resp_msg, "http_status: 202 (Accepted)"
            )
        elif resp.status_code == 200:
            return 0, self.format_response(
                nas, resp_msg, "http_status: 200 (Success)"
            )
        else:
            resp_list = []
            resp_list.append("Client didn't understand the response.")
            resp_list.append(
                "CLIENT ERROR! (Please email this output to a code monkey)"
            )
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
        resp_list.append(resp.content)
        resp_list.append(str(nas))
        resp_list.append(str(data))
        return 1, resp_list

    def delete(self, nas):
        url = "{0}{1}?format=json".format(REMOTE, self.delete_url(nas))
        headers = {'content-type': 'application/json'}
        resp = requests.delete(url, headers=headers, auth=auth)
        return self.handle_resp(nas, {}, resp)

    def detail(self, nas):
        url = "{0}{1}?format=json".format(REMOTE, self.detail_url(nas))
        headers = {'content-type': 'application/json'}
        resp = requests.get(url, headers=headers, auth=auth)
        return self.handle_resp(nas, {}, resp)

    def update(self, nas):
        data = self.get_update_data(nas)  # Dispatch defined Hook
        url = "{0}{1}".format(REMOTE, self.update_url(nas))
        return self.action(nas, url, requests.patch, data)

    def create(self, nas):
        data = self.get_create_data(nas)  # Dispatch defined Hook
        url = "{0}{1}".format(REMOTE, self.create_url(nas))
        return self.action(nas, url, requests.post, data)

    def action(self, nas, url, method, data):
        headers = {'content-type': 'application/json'}
        data = json.dumps(data, indent=2)
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


def dispatch(nas):
    for dispatch in registrar.dispatches:
        if dispatch.dtype.lower() == nas.dtype.lower():
            return dispatch.route(nas)
