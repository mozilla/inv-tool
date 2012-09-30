import sys
import argparse
from options import *
from intr_options import *
from dispatch import dispatch_dns

inv_parser = argparse.ArgumentParser(prog='invdns')
inv_parser.add_argument('--format', default='text', type=str,
            choices=['json', 'text', 'bind'],
            help="The format the output")
record_base_parser = inv_parser.add_subparsers(dest='rtype')

def dns_command_template(rtype):
    base_parser = record_base_parser.add_parser(rtype, help="The interface for {0} "
                "records".format(rtype), add_help=True)
    action_parser = base_parser.add_subparsers(help="{0} record "
                "actions".format(rtype), dest='action')
    create_parser = action_parser.add_parser('create', help="Create "
                        "an {0} record".format(rtype))
    update_parser = action_parser.add_parser('update', help="Update "
                        "an {0} record".format(rtype))
    delete_parser = action_parser.add_parser('delete', help="Delete "
                        "an {0} record".format(rtype))
    return action_parser, create_parser, update_parser, delete_parser

# A, AAAA, PTR, CNAME, MX, NS, SRV, TXT, SSHFP and SOA

# A Record
(a_action_parser, a_create_parser, a_update_parser,
        a_delete_parser) = dns_command_template('A')
# Create A Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_ip_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(a_create_parser), args)

# Update A Record options
add_update_id_argument(a_update_parser, 'A')
map(lambda apply_arg: apply_arg(a_update_parser, required=False), args)

# Delete A Record options
add_delete_id_argument(a_delete_parser, 'A')

# AAAA Record
(aaaa_action_parser, aaaa_create_parser, aaaa_update_parser,
        aaaa_delete_parser) = dns_command_template('AAAA')

# Create AAAA Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_ip_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(aaaa_create_parser), args)

# Update AAAA Record options
add_update_id_argument(aaaa_update_parser, 'AAAA')
map(lambda apply_arg: apply_arg(aaaa_update_parser, required=False), args)

# Delete AAAA Record options
add_delete_id_argument(aaaa_delete_parser, 'AAAA')

# PTR Record
(ptr_action_parser, ptr_create_parser, ptr_update_parser,
        ptr_delete_parser) = dns_command_template('PTR')

# Create PTR Record options
args = [add_ip_argument,
        add_ttl_argument,
        add_target_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(ptr_create_parser), args)

# Update PTR Record options
add_update_id_argument(ptr_update_parser, 'PTR')
map(lambda apply_arg: apply_arg(ptr_update_parser, required=False), args)

# Delete PTR Record options
add_delete_id_argument(ptr_delete_parser, 'PTR')

# CNAME Record
(cname_action_parser, cname_create_parser, cname_update_parser,
        cname_delete_parser) = dns_command_template('CNAME')

# Create CNAME Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_target_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(cname_create_parser), args)

# Update CNAME Record options
add_update_id_argument(cname_update_parser, 'CNAME')
map(lambda apply_arg: apply_arg(cname_update_parser, required=False), args)

# Delete CNAME Record options
add_delete_id_argument(cname_delete_parser, 'CNAME')

# NS Record
(ns_action_parser, ns_create_parser, ns_update_parser,
        ns_delete_parser) = dns_command_template('NS')

# Create NS Record options
args = [add_domain_argument,
        add_ttl_argument,
        add_target_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(ns_create_parser), args)

# Update NS Record options
add_update_id_argument(ns_update_parser, 'NS')
map(lambda apply_arg: apply_arg(ns_update_parser, required=False), args)

# Delete NS Record options
add_delete_id_argument(ns_delete_parser, 'NS')

# MX Record
(mx_action_parser, mx_create_parser, mx_update_parser,
        mx_delete_parser) = dns_command_template('MX')

# Create MX Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_priority_argument,
        add_target_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(mx_create_parser), args)

# Update MX Record options
add_update_id_argument(mx_update_parser, 'MX')
map(lambda apply_arg: apply_arg(mx_update_parser, required=False), args)

# Delete MX Record options
add_delete_id_argument(mx_delete_parser, 'MX')

# SRV Record
(srv_action_parser, srv_create_parser, srv_update_parser,
        srv_delete_parser) = dns_command_template('SRV')

# Create SRV Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_priority_argument,
        add_port_argument,
        add_weight_argument,
        add_target_argument,
        add_view_arguments,
        add_comment_argument]

map(lambda apply_arg: apply_arg(srv_create_parser), args)

# Update SRV Record options
add_update_id_argument(srv_update_parser, 'SRV')
map(lambda apply_arg: apply_arg(srv_update_parser, required=False), args)

# Delete SRV Record options
add_delete_id_argument(srv_delete_parser, 'SRV')

# TXT Record
(txt_action_parser, txt_create_parser, txt_update_parser,
        txt_delete_parser) = dns_command_template('TXT')

# Create TXT Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_text_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(txt_create_parser), args)

# Update TXT Record options
add_update_id_argument(txt_update_parser, 'TXT')
map(lambda apply_arg: apply_arg(txt_update_parser, required=False), args)

# Delete TXT Record options
add_delete_id_argument(txt_delete_parser, 'TXT')

# SSHFP Record
(sshfp_action_parser, sshfp_create_parser, sshfp_update_parser,
        sshfp_delete_parser) = dns_command_template('SSHFP')

# Create SSHFP Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_algorithm_argument,
        add_fingerprint_argument,
        add_key_argument,
        add_view_arguments,
        add_comment_argument]
map(lambda apply_arg: apply_arg(sshfp_create_parser), args)

# Update SSHFP Record options
add_update_id_argument(sshfp_update_parser, 'SSHFP')
map(lambda apply_arg: apply_arg(sshfp_update_parser, required=False), args)

# Delete SSHFP Record options
add_delete_id_argument(sshfp_delete_parser, 'SSHFP')

# INTR Record
(intr_action_parser, intr_create_parser, intr_update_parser,
        intr_delete_parser) = dns_command_template('INTR')

# Create INTR Record options
args = [add_label_argument,
        add_domain_argument,
        add_fqdn_argument,
        add_ttl_argument,
        add_ip_argument,
        add_itype_argument,
        add_view_arguments,
        add_dns_enable,
        add_dhcp_enable,
        add_system_argument,
        add_comment_argument]
map(lambda apply_arg: apply_arg(intr_create_parser), args)

# Update INTR Record options
add_update_id_argument(intr_update_parser, 'INTR')
map(lambda apply_arg: apply_arg(intr_update_parser, required=False), args)

# Delete INTR Record options
add_delete_id_argument(intr_delete_parser, 'INTR')

if __name__ == "__main__":
    dispatch_dns(inv_parser.parse_args(sys.argv[1:]))
