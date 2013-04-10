try:
    import simplejson as json
except ImportError:
    import json

from invtool.lib.registrar import registrar
from invtool.dns_dispatch import DNSDispatch

from invtool.lib.dns_options import (
    fqdn_argument, ttl_argument, ip_argument, view_arguments,
    description_argument, comment_argument, update_pk_argument,
    delete_pk_argument, detail_pk_argument, system_argument, mac_argument,
    interface_name_argument
)

from invtool.lib.options import group_argument


class DispatchBondedINTR(DNSDispatch):
    resource_name = 'bondedinterface'
    dtype = 'BONDI'
    dgroup = 'dhcp'

    update_args = [
        mac_argument('mac'),
        interface_name_argument('interface_name'),
        group_argument('group'),
        description_argument('description'),
        comment_argument('comment')
    ]

    create_args = update_args

    update_args = update_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]

    def format_response(self, nas, resp_msg, user_msg):
        resp_list = []
        if nas.p_json:
            resp_list.append(json.dumps(resp_msg, indent=2))
        else:
            resp_list.append(user_msg)
            for k, v in resp_msg.iteritems():
                resp_list.append("{0}: {1}".format(k, v))
        return resp_list


registrar.register(DispatchBondedINTR())


class DispatchINTR(DNSDispatch):
    resource_name = 'staticinterface'
    dtype = 'INTR'
    dgroup = 'dns'
    ip_type = '4'  # Used for testing

    update_args = [
        fqdn_argument('fqdn', dtype),
        mac_argument('mac'),
        interface_name_argument('interface_name'),
        ttl_argument('ttl'),
        ip_argument('ip_str', ip_type),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    create_args = update_args + [
        system_argument('system_hostname'),
    ]

    update_args = update_args + [
        update_pk_argument('pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]

    def get_create_data(self, nas):
        data = super(DispatchINTR, self).get_create_data(nas)
        if 'ip_str' in data:
            if data['ip_str'].find(':') < 0:
                data['ip_type'] = '4'
            else:
                data['ip_type'] = '4'
        return data

    def get_update_data(self, nas):
        data = super(DispatchINTR, self).get_update_data(nas)
        if 'ip_str' in data:
            if data['ip_str'].find(':') < 0:
                data['ip_type'] = '4'
            else:
                data['ip_type'] = '4'
        return data


registrar.register(DispatchINTR())
