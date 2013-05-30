try:
    import simplejson as json
except ImportError:
    import json

from invtool.lib.registrar import registrar
from invtool.dispatch import ObjectDispatch

from invtool.lib.dns_options import detail_pk_argument
from invtool.lib.parser import build_detail_parser


# TODO, make a core_dispatch.py with CoreDispatch base class

class CoreDispatch(ObjectDispatch):
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

    detail_args = [detail_pk_argument('pk', dtype)]


registrar.register(DispatchNetwork())


class DispatchSite(CoreDispatch):
    resource_name = 'site'
    dtype = 'SITE'
    dgroup = 'core'

    detail_args = [detail_pk_argument('pk', dtype)]


registrar.register(DispatchSite())


class DispatchVlan(CoreDispatch):
    resource_name = 'vlan'
    dtype = 'VLAN'
    dgroup = 'core'

    detail_args = [detail_pk_argument('pk', dtype)]


registrar.register(DispatchVlan())
