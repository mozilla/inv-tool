try:
    import simplejson as json
except ImportError:
    import json  # noqa

from invtool.dispatch import ObjectDispatch
from invtool.lib.registrar import registrar
from invtool.lib.dns_options import (
    fqdn_argument, ttl_argument, ip_argument, view_arguments,
    target_argument, priority_argument,
    port_argument, weight_argument,
)
from invtool.lib.options import (
    description_argument, comment_argument, update_pk_argument,
    delete_pk_argument, detail_pk_argument
)
from invtool.lib.parser import (
    build_create_parser, build_update_parser, build_delete_parser,
    build_detail_parser
)


class DNSDispatch(ObjectDispatch):
    object_url = "/en-US/mozdns/api/v{0}_dns/{1}/{2}/"
    object_list_url = "/en-US/mozdns/api/v{0}_dns/{1}/"


class DispatchA(DNSDispatch):
    resource_name = 'addressrecord'
    dtype = 'A'
    dgroup = 'dns'

    create_args = [
        fqdn_argument('fqdn', dtype),  # ~> (labmda, lambda)
        ttl_argument('ttl'),
        ip_argument('ip_str', '4'),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]

    def determine_ip_type(self, ip_str):
        if ip_str.find(':') > -1:
            ip_type = '6'
        else:
            ip_type = '4'  # Default to 4
        return ip_type

    def get_create_data(self, nas):
        data = super(DispatchA, self).get_create_data(nas)
        if 'ip_str' in data:
            data['ip_type'] = self.determine_ip_type(data.get('ip_str', ''))
        return data

    def get_update_data(self, nas):
        data = super(DispatchA, self).get_update_data(nas)
        if 'ip_str' in data:
            data['ip_type'] = self.determine_ip_type(data.get('ip_str', ''))
        return data


class DispatchPTR(DNSDispatch):
    resource_name = 'ptr'
    dtype = 'PTR'
    dgroup = 'dns'

    create_args = [
        ttl_argument('ttl'),
        ip_argument('ip_str', '4'),
        view_arguments('views'),
        target_argument('name'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]

    def determine_ip_type(self, ip_str):
        if ip_str.find(':') > -1:
            ip_type = '6'
        else:
            ip_type = '4'  # Default to 4
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
    dtype = 'AAAA'
    dgroup = 'dns'

    create_args = [
        fqdn_argument('fqdn', dtype),  # ~> (labmda, lambda)
        ttl_argument('ttl'),
        ip_argument('ip_str', '6'),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]


class DispatchCNAME(DNSDispatch):
    resource_name = 'cname'
    dtype = 'CNAME'
    dgroup = 'dns'

    create_args = [
        fqdn_argument('fqdn', dtype),  # ~> (labmda, lambda)
        ttl_argument('ttl'),
        target_argument('target'),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]


class DispatchSRV(DNSDispatch):
    resource_name = 'srv'
    dtype = 'SRV'
    dgroup = 'dns'

    create_args = [
        fqdn_argument('fqdn', dtype),  # ~> (labmda, lambda)
        ttl_argument('ttl'),
        port_argument('port'),
        weight_argument('weight'),
        priority_argument('priority'),
        target_argument('target'),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]


class DispatchMX(DNSDispatch):
    resource_name = 'mx'
    dtype = 'MX'
    dgroup = 'dns'

    create_args = [
        fqdn_argument('fqdn', dtype),  # ~> (labmda, lambda)
        ttl_argument('ttl'),
        priority_argument('priority'),
        target_argument('server'),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]


class DispatchTXT(DNSDispatch):
    resource_name = 'txt'
    dtype = 'TXT'
    dgroup = 'dns'

    create_args = [
        fqdn_argument('fqdn', dtype),  # ~> (labmda, lambda)
        ttl_argument('ttl'),
        target_argument('txt_data'),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = create_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]


registrar.register(DispatchA())
registrar.register(DispatchAAAA())
registrar.register(DispatchCNAME())
registrar.register(DispatchMX())
registrar.register(DispatchPTR())
registrar.register(DispatchSRV())
registrar.register(DispatchTXT())


def build_dns_parsers(base_parser):
    # Build all the records
    for dispatch in [d for d in registrar.dispatches if d.dgroup == 'dns']:
        record_base_parser = base_parser.add_parser(
            dispatch.dtype,
            help="Interface for {0} records".format(dispatch.dtype),
            add_help=True
        )
        action_parser = record_base_parser.add_subparsers(
            help="{0} record actions".format(dispatch.dtype),
            dest='action'
        )
        build_create_parser(dispatch, action_parser)
        build_update_parser(dispatch, action_parser)
        build_delete_parser(dispatch, action_parser)
        build_detail_parser(dispatch, action_parser)
