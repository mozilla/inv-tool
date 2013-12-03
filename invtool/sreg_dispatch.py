try:
    import simplejson as json
except ImportError:
    import json

from invtool.lib.registrar import registrar
from invtool.dispatch import ObjectDispatch
from invtool.dns_dispatch import DNSDispatch
from invtool.core_dispatch import set_ip_type

from invtool.lib.options import (
    description_argument, comment_argument, update_pk_argument,
    delete_pk_argument, detail_pk_argument
)

from invtool.lib.dns_options import (
    fqdn_argument, ttl_argument, ip_argument, view_arguments,
    system_argument, name_argument
)

from invtool.lib.hw_options import (
    group_argument, mac_argument, enable_dhcp_argument, sreg_argument
)


# TODO, make a core_dispatch.py with CoreDispatch base class


class DispatchHW(ObjectDispatch):
    object_url = "/en-US/core/api/v1_core/{1}/{2}/"
    object_list_url = "/en-US/core/api/v1_core/{1}/"
    resource_name = 'hwadapter'
    dtype = 'HW'
    dgroup = 'dhcp'

    common_args = [
        mac_argument('mac'),
        group_argument('group'),
        enable_dhcp_argument('enable_dhcp'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = common_args + [
        name_argument('name', prefix='hw'),
        update_pk_argument('pk', dtype)
    ]

    create_args = common_args + [
        sreg_argument('sreg'),
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


class DispatchSREG(DNSDispatch):
    object_url = "/en-US/core/api/v1_core/{1}/{2}/"
    object_list_url = "/en-US/core/api/v1_core/{1}/"
    resource_name = 'staticreg'
    dtype = 'SREG'
    dgroup = 'dns'
    ip_type = '4'  # Used for testing

    common_args = [
        fqdn_argument('fqdn', dtype),
        ttl_argument('ttl'),
        ip_argument('ip_str', ip_type),
        view_arguments('views'),
        description_argument('description'),
        comment_argument('comment')
    ]

    update_args = common_args + [
        name_argument('name', prefix='nic'),
        update_pk_argument('pk', dtype)
    ]

    create_args = common_args + [
        system_argument('system_hostname'),
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]

    def get_create_data(self, nas):
        data = super(DispatchSREG, self).get_create_data(nas)
        return set_ip_type('ip_str', data)

    def get_update_data(self, nas):
        data = super(DispatchSREG, self).get_update_data(nas)
        return set_ip_type('ip_str', data)

    def format_hwadapters(self, hws):
        # This is never called if p_json is true
        resp_list = []
        for i, hw in enumerate(hws):
            for k, v in hw.iteritems():
                resp_list.append("\t{0} | {1}: {2}".format(i, k, v))
        return resp_list

    def format_response(self, nas, resp_msg, user_msg):
        # Override this so we can display hwadapters better
        resp_list = []
        if nas.p_json:
            resp_list.append(json.dumps(resp_msg, indent=2))
        else:
            resp_list.append(user_msg)
            for k, v in resp_msg.iteritems():
                if k == 'hwadapter_set':
                    continue  # handle these last
                    # indent these
                else:
                    resp_list.append("{0}: {1}".format(k, v))
            if resp_msg.get('hwadapter_set', None):
                resp_list.append("Hardware Adapters: {0}".format('-' * 20))
                resp_list += self.format_hwadapters(resp_msg['hwadapter_set'])
        return resp_list


# Uncomment when dhcp is rolled out
registrar.register(DispatchSREG())
registrar.register(DispatchHW())
