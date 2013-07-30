try:
    import simplejson as json
except ImportError:
    import json

from invtool.dispatch import ObjectDispatch
from invtool.tests.utils import call_to_json, test_method_to_params, EXEC

from invtool.lib.registrar import registrar
from invtool.lib.parser import build_detail_parser
from invtool.lib.dns_options import (
    description_argument, comment_argument, update_pk_argument,
    delete_pk_argument, detail_pk_argument
)
from invtool.lib.core_options import (
    name_argument, number_argument, site_argument, vlan_argument,
    network_str_argument
)


# TODO, make a core_dispatch.py with CoreDispatch base class

class CoreDispatch(ObjectDispatch):
    object_url = "/en-US/core/api/v1_core/{1}/{2}/"
    object_list_url = "/en-US/core/api/v1_core/{1}/"


class ROCoreDispatch(ObjectDispatch):
    object_url = "/en-US/core/api/v1_core/{1}/{2}/"
    object_list_url = "/en-US/core/api/v1_core/{1}/"

    def build_parser(self, base_parser):
        record_base_parser = base_parser.add_parser(
            self.dtype,
            help="Interface for {0} records".format(self.dtype),
            add_help=True
        )
        action_parser = record_base_parser.add_subparsers(
            help="{0} record actions".format(self.dtype),
            dest='action'
        )
        build_detail_parser(self, action_parser)


class DispatchNetwork(CoreDispatch):
    resource_name = 'network'
    dtype = 'NET'
    dgroup = 'core'
    ip_type = None

    def test_setup(self):
        def setUp(self):
            def create_site():
                command = [EXEC, DispatchSite.dtype, 'create']
                for add_arg, extract_arg, test_f in DispatchSite.create_args:
                    command.append(test_method_to_params(test_f()))

                site_ret, site_errors, site_rc = call_to_json(
                    ' '.join(command)
                )

                if site_errors:
                    self.fail(site_errors)

                self.assertEqual(0, site_rc)

                # Make sure the SREG was created correctly
                self.assertTrue('http_status' in site_ret)
                self.assertEqual(site_ret['http_status'], 201)
                self.assertTrue('pk' in site_ret)
                return site_ret['pk']

            def create_vlan():
                command = [EXEC, DispatchVlan.dtype, 'create']
                for add_arg, extract_arg, test_f in DispatchVlan.create_args:
                    command.append(test_method_to_params(test_f()))

                vlan_ret, vlan_errors, vlan_rc = call_to_json(
                    ' '.join(command)
                )

                if vlan_errors:
                    self.fail(vlan_errors)

                self.assertEqual(0, vlan_rc)

                # Make sure the SREG was created correctly
                self.assertTrue('http_status' in vlan_ret)
                self.assertEqual(vlan_ret['http_status'], 201)
                self.assertTrue('pk' in vlan_ret)
                return vlan_ret['pk']

            self.site_pk = create_site()
            self.vlan_pk = create_site()

            def modify_command(command_str):
                command_str = command_str.replace(
                    '{{ site }}', str(self.site_pk)
                )
                command_str = command_str.replace(
                    '{{ vlan }}', str(self.vlan_pk)
                )
                return command_str

            self.modify_command = modify_command
        return setUp

    def test_teardown(self):
        def tearDown(self):
            # Delete the object
            def delete_vlan():
                delete_command = "{0} {1} delete --pk {2}".format(
                    EXEC, 'VLAN', self.vlan_pk)
                ret, errors, rc = call_to_json(delete_command)
                if errors:
                    self.fail(errors)
                self.assertEqual(0, rc)
                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 204)

            def delete_site():
                delete_command = "{0} {1} delete --pk {2}".format(
                    EXEC, 'SITE', self.vlan_pk)
                ret, errors, rc = call_to_json(delete_command)
                if errors:
                    self.fail(errors)
                self.assertEqual(0, rc)
                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 204)
            delete_vlan()
            delete_site()
        return tearDown

    update_args = [
        site_argument('site'),
        vlan_argument('vlan'),
        network_str_argument('network-str'),
        comment_argument('comment'),
        description_argument('description'),
        update_pk_argument('pk', dtype)
    ]

    create_args = [
        site_argument('site'),
        vlan_argument('vlan'),
        network_str_argument('network-str'),
        comment_argument('comment'),
        description_argument('description'),
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]

    def get_create_data(self, nas):
        data = super(DispatchNetwork, self).get_create_data(nas)
        return set_ip_type('network_str', data)

    def get_update_data(self, nas):
        data = super(DispatchNetwork, self).get_update_data(nas)
        return set_ip_type('network_str', data)


registrar.register(DispatchNetwork())


class DispatchSite(CoreDispatch):
    resource_name = 'site'
    dtype = 'SITE'
    dgroup = 'core'

    update_args = [
        name_argument('full_name'),
        comment_argument('comment'),
        description_argument('description'),
        update_pk_argument('pk', dtype)
    ]

    create_args = [
        name_argument('full_name', required=True),
        comment_argument('comment'),
        description_argument('description')
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]


registrar.register(DispatchSite())


class DispatchVlan(CoreDispatch):
    resource_name = 'vlan'
    dtype = 'VLAN'
    dgroup = 'core'

    update_args = [
        name_argument('name'),
        number_argument('number'),
        comment_argument('comment'),
        description_argument('description'),
        update_pk_argument('pk', dtype)
    ]

    create_args = [
        name_argument('name', required=True),
        number_argument('number', required=True),
        comment_argument('comment'),
        description_argument('description')
    ]

    delete_args = [
        delete_pk_argument('pk', dtype)
    ]

    detail_args = [detail_pk_argument('pk', dtype)]


registrar.register(DispatchVlan())


def set_ip_type(nas_name, data):
    if nas_name in data:
        if data[nas_name].find(':') < 0:
            data['ip_type'] = '4'
        else:
            data['ip_type'] = '6'
    return data
