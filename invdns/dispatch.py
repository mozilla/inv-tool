import pprint
import sys
import ConfigParser
import pdb
import requests
import simplejson as json

pp = pprint.PrettyPrinter(indent=4)
auth=None
API_MAJOR_VERSION = 1
CONFIG_FILE = "./config.cfg"

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

host = config.get('remote','host')
port = config.get('remote','port')
remote = "http://{0}:{1}".format(host, port)

def do_action(nas, data):
    print "Using remote: {0}".format(remote)

    object_url = "/mozdns/api/v{0}_dns/{1}/{2}/"
    object_list_url = "/mozdns/api/v{0}_dns/{1}/"
    if nas.rtype == 'NS':
        resource_name = 'nameserver'
    elif nas.rtype == 'INTR':
        resource_name = 'staticinterface'
    elif nas.rtype == 'A' or nas.rtype == 'AAAA':
        resource_name = 'addressrecord'
    else:
        resource_name = nas.rtype.lower()
    if nas.action == 'create':
        tmp_url = object_list_url.format(API_MAJOR_VERSION, resource_name)
        url = "{0}{1}".format(remote, tmp_url)
        method = requests.post
    elif nas.action == 'update':
        tmp_url = object_url.format(API_MAJOR_VERSION, resource_name, nas.pk)
        url = "{0}{1}".format(remote, tmp_url)
        method = requests.patch
    headers = {'content-type': 'application/json'}
    data = json.dumps(data)
    resp = method(url, headers=headers, data=data, auth=auth)
    handle_resp(nas, data, resp)
    return

def handle_resp(nas, data, resp):
    # This function *will* call sys.exit!
    resp_msg = get_resp_text(resp)
    if resp.status_code == 500:
        print "SERVER ERROR! (Please email this output to a code monkey)"
        error_out(nas, data, resp)

    if resp.status_code == 400:
        # Bad Request
        if nas.format == 'json':
            print resp_msg
        elif nas.format in ('text', 'bind'):
            if 'error_messages' in resp_msg:
                print get_errors(resp_msg['error_messages'])
        sys.exit(1)
    if resp.status_code == 201:
        # Created
        if nas.format == 'text':
            print "Created!"
            for k, v in resp_msg.iteritems():
                print "{0}: {1}".format(k, v)
        if nas.format == 'json':
            print resp_msg
        sys.exit(0)
    if resp.status_code == 202:
        # Accepted
        if nas.format == 'text':
            print "Accepted!"
            for k, v in resp_msg.iteritems():
                print "{0}: {1}".format(k, v)
        if nas.format == 'json':
            print resp_msg
        sys.exit(0)
    else:
        print "Client didn't understand the response."
        print "CLIENT ERROR! (Please email this output to a code monkey)"
        error_out(nas, data, resp)

def error_out(nas, data, resp):
        print nas
        print data
        pprint.pprint(vars(resp))
        sys.exit(1)

def get_errors(resp_msg):
    messages = json.loads(resp_msg)
    errors = ''
    for error, msg in messages.iteritems():
        if error == '__all__':
            error = "Object Error"
        errors += "Error: {0}  {1}".format(error, ', '.join(msg))
    return errors


def get_resp_text(resp):
    if resp.text:
        # Tasty pie returns json that is unicode. Thats ok.
        msg = json.loads(resp.text, 'unicode')
        return msg
    return 'No message from server'

def print_resp(resp):
    if resp.text:
        text = json.loads(resp.text)
        print text

class InvalidCommand(Exception):
    pass

def dispatch_search(nas):
    tmp_url = "/core/search/search_dns_text/"
    url = "{0}{1}".format(remote, tmp_url)
    headers = {'content-type': 'application/json'}
    search = {'search': nas.query}
    resp = requests.get(url, params=search, headers=headers, auth=auth)
    if resp.status_code == 500:
        print "CLIENT ERROR! (Please email this output to a code monkey)"
        error_out(nas, search, resp)
        return
    print resp.text

def dispatch(nas):
    if nas.rtype == 'search':
        return dispatch_search(nas)
    if nas.rtype == 'NS':
        return dispatch_NS(nas)
    if nas.rtype == 'A':
        return dispatch_A(nas)
    if nas.rtype == 'AAAA':
        return dispatch_AAAA(nas)

def dispatch_NS(nas):
    pass

def dispatch_MX(nas):
    pass

def dispatch_AAAA(nas):
    data = {}
    if nas.action == 'create':
        data['ip_type'] = '6'
    return _dispatch_addr_record(nas, data)

def dispatch_A(nas):
    data = {}
    if nas.action == 'create':
        data['ip_type'] = '4'
    return _dispatch_addr_record(nas, data)

def _dispatch_addr_record(nas, data):
    if nas.action == 'delete':
        return
    try:
        data.update(extract_label_domain_or_fqdn(nas))
        data.update(extract_ip_str(nas))
        data.update(extract_comment_ttl(nas))
        data.update(extract_views(nas))
    except InvalidCommand, e:
        print e.message
        return None
    do_action(nas, data)
    #pprint.pprint(data)
    return data

def extract_views(nas):
    views = []
    if nas.no_private:
        views.append('no-private')
    elif nas.private:
        views.append('private')

    if nas.no_public:
        views.append('no-public')
    elif nas.public:
        views.append('public')

    data = {
        'views': views
        }
    return data

def extract_ip_str(nas):
    if nas.action == 'update':
        if not nas.ip:
            return {}
    data = {
        'ip_str': nas.ip
        }
    return data

def extract_label_domain_or_fqdn(nas):
    if (nas.label or nas.domain) and nas.fqdn:
        raise InvalidCommand("Use either domain (and label) OR use fqdn.")
    if nas.action == 'create':
        if not (nas.domain or nas.fqdn):
            raise InvalidCommand("Use either domain (and label) OR use fqdn.")
        if nas.label and not nas.domain:
            raise InvalidCommand("If you specify a label you need to also specify "
                "a domain name")
    data = {}
    if nas.fqdn:
        data.update({
                'fqdn': nas.fqdn
                })
        return data
    else:
        if nas.action == 'update':
            if nas.label:
                data['label'] = nas.label
            if nas.domain:
                data['domain'] = nas.domain
        elif nas.action == 'create':
            data['label'] = nas.label
            data['domain'] = nas.domain
        return data
    raise Exception("Shouldn't have got here")

def extract_comment_ttl(nas):
    data = {}
    if nas.ttl:
        data['ttl'] = nas.ttl
    if nas.comment:
        data['comment'] = nas.comment
    return data
