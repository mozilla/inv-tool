import argparse
from tests.test_data import *

###############
# DNS OPTIONS #
###############
def view_arguments(field_name):
    def add_view_arguments(parser, required=False):
        pri_group = parser.add_mutually_exclusive_group()
        pri_group.add_argument('--no-private', default=False, action='store_true',
                dest='no_private', help="Disable private view.", required=required)
        pri_group.add_argument('--private', default=False, action='store_true',
                dest='private', help="Enabled private view.", required=False)

        pub_group = parser.add_mutually_exclusive_group()
        pub_group.add_argument('--no-public', default=False, action='store_true',
                dest='no_public', help="Disable public view.", required=required)
        pub_group.add_argument('--public', default=False, action='store_true',
                dest='public', help="Enabled public view.", required=False)

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
            field_name: views
            }
        return data

    def test_data():
        return '', '--nopublic --private'

    return add_view_arguments, extract_views, test_data


def _add_domain_argument(parser, required=True):
    parser.add_argument('--domain', default=None, type=str, dest='domain',
            help="The domain a record is in.", required=False)

def domain_argument(field_name):
    def extract_domain(nas):
        data = {}
        if nas.domain:
            data.update({
                    field_name: nas.domain
                    })
            return data

    def test_data():
        return 'domain', TEST_DOMAIN

    return _add_domain_argument, extract_domain, test_data

def _add_label_argument(parser, required=True):
    parser.add_argument('--label', default="", type=str, dest='label',
            help="The first label in the fqdn. If label is ommited then '' is "
            "used and is analigouse to using '@' in a zone file (the record "
            "will get it's domain's name as it's fqdn).", required=False)

def fqdn_argument(field_name):
    def add_fqdn_argument(parser, required=True):
        _add_label_argument(parser, required)
        _add_domain_argument(parser, required)
        parser.add_argument('--fqdn', default="", type=str, dest='fqdn',
                help="The FQDN of the record being created. If you use this "
                "option you cannot use label or domain", required=False)

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
                    field_name: nas.fqdn
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

    def test_data():
        return 'fqdn', TEST_FQDN

    return add_fqdn_argument, extract_label_domain_or_fqdn, test_data

def ip_argument(field_name):
    def add_ip_argument(parser, required=True):
        parser.add_argument('--ip', default=None, type=str, dest='ip', help="A "
                "string representation of an IP address.", required=required)

    def extract_ip_str(nas):
        if nas.action == 'update':
            if not nas.ip:
                return {}
        data = {
            field_name: nas.ip
            }
        return data

    def test_data():
        return 'ip', TEST_IP

    return add_ip_argument, extract_ip_str, test_data

def target_argument(field_name):
    def add_target_argument(parser, required=True):
        parser.add_argument('--target', default=None, type=str, dest='target',
                help="The target name of a record", required=required)

def comment_argument(field_name):
    def add_comment_argument(parser, required=False):
        parser.add_argument('--comment', default="", type=str, dest='comment',
                help="Tell us a little about this record", required=False)
    def extract_comment(nas):
        data = {}
        if nas.comment:
            data[field_name] = nas.comment
        return data

    def test_data():
        return 'comment', TEST_COMMENT

    return add_comment_argument, extract_comment, test_data

def text_argument(field_name):
    def add_text_argument(parser, required=True):
        parser.add_argument('--text', default=None, type=str, dest='text',
                help="The text data.", required=False)

def write_num_argument(parser, name, dest, help_text, required=False):
    parser.add_argument('--{0}'.format(name), default=None, type=int,
            dest=dest, help=help_text, required=required)
    return parser

def ttl_argument(field_name):
    def add_ttl_argument(parser, required=True):
        write_num_argument(parser, 'ttl', 'ttl', "The ttl "
                            "of a record.", required=False)
    def extract_ttl(nas):
        data = {}
        if nas.ttl:
            data['ttl'] = nas.ttl
        return data

    def test_data():
        return 'ttl', TEST_TTL

    return add_ttl_argument, extract_ttl, test_data

def key_argument(field_name):
    def add_key_argument(parser, required=True):
        parser.add_argument('--key', default=None, type=str, dest='sshfp_key',
                help="The key data.", required=True)

def algorithm_argument(field_name):
    def add_algorithm_argument(parser, required=True):
        parser.add_argument('--algo', metavar="algorithm type",
                type=str, dest='algorith_type',
                choices = ['RSA', 'DSS'],
                help="The Algorithm type. See RFC 4255.", required=required)
        return parser

def fingerprint_argument(field_name):
    def add_fingerprint_argument(parser, required=False):
        parser.add_argument('--finger-type', metavar="fingerprint number",
                type=str, dest='fingerprint_type',
                choices = ['SHA1'], default='SHA1',
                help="The fingerprint type. See RFC 4255",
                required=required)
        return parser

def priority_argument(field_name):
    def add_priority_argument(parser, required=True):
        write_num_argument(parser, 'priority', 'priority',
                            "The priority number of a record", required=required)

def port_argument(field_name):
    def add_port_argument(parser, required=True):
        write_num_argument(parser, 'port', 'port', "The "
                            "target port of an SRV " "record", required=required)

def weight_argument(field_name):
    def add_weight_argument(parser, required=True):
        write_num_argument(parser, 'weight', 'weight', "The "
                            "weight number of an SRV record", required=required)

def _extract_pk(nas, field_name):
    return {field_name: nas.pk}

def update_pk_argument(field_name, rdtype):
    def add_update_pk_argument(parser):
        parser.add_argument('--{0}'.format("pk"), required=True, default=None,
                type=int, dest='pk', help="The database integer primary key (id) "
                "of the {0} you are updating.".format(rdtype))
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_update_pk_argument, extract_pk, lambda: None


def detail_pk_argument(field_name, rdtype):
    def add_detail_pk_argument(parser):
        parser.add_argument('--{0}'.format("pk"), required=True, default=None,
                type=int, dest='pk', help="The database integer primary key (id) "
                "of the {0} you are updating.".format(rdtype))
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_detail_pk_argument, extract_pk, lambda: None

def delete_pk_argument(field_name, rdtype):
    def add_delete_pk_argument(parser):
        parser.add_argument('--{0}'.format("pk"), default=None, type=int,
                dest='pk', help="Delete the {0} record with the database primary "
                "key of 'pk'".format(rdtype), required=True)
        return parser

    def extract_pk(nas):
        return _extract_pk(nas, field_name)

    return add_delete_pk_argument, extract_pk, lambda: None
