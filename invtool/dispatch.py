import simplejson as json
from gettext import gettext as _
from invtool.lib.registrar import registrar


class Dispatch(object):
    object_url = "/en-US/mozdns/api/v{0}_dns/{1}/{2}/"
    object_list_url = "/en-US/mozdns/api/v{0}_dns/{1}/"

    def handle_resp(self, nas, data, resp):
        def format_response(resp_msg, user_msg):
            resp_list = []
            if nas.p_json:
                resp_list.append(json.dumps(resp_msg, indent=2))
            else:
                resp_list.append(user_msg)
                for k, v in resp_msg.iteritems():
                    resp_list.append("{0}: {1}".format(k, v))
            return resp_list

        resp_msg = self.get_resp_dict(resp)

        if resp.status_code == 404:
            return 1, format_response(resp_msg, "http_status: 404 (file not "
                                      "found)")
        elif resp.status_code == 204:
            if nas.p_json:
                return 0, [json.dumps(resp_msg, indent=2)]
            else:
                return 0, ["http_status: 204 (request fulfilled)"]
        elif resp.status_code == 500:
            resp_list = [_("SERVER ERROR! (Please email this output to a "
                         "code monkey)")]
            return self.error_out(data, resp, resp_list=resp_list)
        elif resp.status_code == 400:
            # Bad Request
            if nas.p_json:
                return 1, [json.dumps(resp_msg, indent=2)]
            else:
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
        resp_list.append(str(nas))
        resp_list.append(str(data))
        return 1, resp_list


def dispatch(nas):
    for dispatch in registrar.dispatches:
        if dispatch.dtype.lower() == nas.dtype.lower():
            return dispatch.route(nas)
