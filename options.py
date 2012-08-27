import argparse

###############
# DNS OPTIONS #
###############

def add_label_argument(parser, required=True):
    parser.add_argument('--label', default="", type=str, dest='label',
            help="The first label in the fqdn. If label is ommited then '' is "
            "used and is analigouse to using '@' in a zone file (the record "
            "will get it's domain's name as it's fqdn).", required=required)

def add_domain_argument(parser, required=True):
    parser.add_argument('--domain', default=None, type=str, dest='domain',
            help="The domain a record is in.", required=required)

def add_ip_argument(parser, required=True):
    parser.add_argument('--ip', default=None, type=str, dest='ip', help="A "
            "string representation of an IP address.", required=required)

def add_target_argument(parser, required=True):
    parser.add_argument('--target', default=None, type=str, dest='target',
            help="The target name of a record", required=required)

def add_comment_argument(parser, required=False):
    parser.add_argument('--comment', default="", type=str, dest='comment',
            help="Tell us a little about this record", required=False)

def add_text_argument(parser, required=True):
    parser.add_argument('--text', default=None, type=str, dest='text',
            help="The text data.", required=False)

def write_num_argument(parser, name, dest, help_text, required=False):
    parser.add_argument('--{0}'.format(name), default=None, type=int,
            dest=dest, help=help_text, required=required)
    return parser

def add_ttl_argument(parser, required=True):
    write_num_argument(parser, 'ttl', 'ttl', "The ttl "
                        "of a record.", required=False)

def add_key_argument(parser, required=True):
    parser.add_argument('--key', default=None, type=str, dest='sshfp_key',
            help="The key data.", required=False)

def add_algorithm_argument(parser, required=True):
    parser.add_argument('--algo', metavar="algorithm type",
            type=str, dest='algorith_type',
            choices = ['RSA', 'DSS'],
            help="The Algorithm type. See RFC 4255.", required=required)
    return parser

def add_fingerprint_argument(parser, required=False):
    parser.add_argument('--finger-type', metavar="fingerprint number",
            type=str, dest='fingerprint_type',
            choices = ['SHA1'], default='SHA1',
            help="The fingerprint type. See RFC 4255",
            required=required)
    return parser

def add_priority_argument(parser, required=True):
    write_num_argument(parser, 'priority', 'priority',
                        "The priority number of a record", required=required)

def add_port_argument(parser, required=True):
    write_num_argument(parser, 'port', 'port', "The "
                        "target port of an SRV " "record", required=required)

def add_weight_argument(parser, required=True):
    write_num_argument(parser, 'weight', 'weight', "The "
                        "weight number of an SRV record", required=required)

def add_update_id_argument(parser, rtype):
    parser.add_argument('--{0}'.format("pk"), required=True, default=None,
            type=int, dest='pk', help="The database integer primary key (id) "
            "of the {0} you are updating.".format(rtype))
    return parser

def add_delete_id_argument(parser, rtype):
    parser.add_argument('--{0}'.format("pk"), default=None, type=int,
            dest='pk', help="Delete the {0} record with the database primary "
            "key of 'pk'".format(rtype), required=True)
    return parser
