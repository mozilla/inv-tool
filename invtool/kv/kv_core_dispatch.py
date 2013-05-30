from invtool.lib.registrar import registrar

from invtool.lib.kv_options import kvlist_pk_argument
from invtool.kv.kv_dispatch import DispatchKV, build_kvlist_parser
from invtool.lib.dns_options import detail_pk_argument
from invtool.lib.parser import build_detail_parser


class CoreDispatchKV(DispatchKV):
    NO_TEST = True

    def build_parser(self, base_parser):
        record_base_parser = base_parser.add_parser(
            self.dtype,
            help="The interface for CRUDing {0} Key Value "
            "pairs".format(self.dtype),
            add_help=True
        )
        action_parser = record_base_parser.add_subparsers(
            help="{0} record actions".format(self.dtype),
            dest='action'
        )
        build_detail_parser(
            self, action_parser, help="Detail a {0} KV pair".format(self.dtype)
        )
        build_kvlist_parser(self, action_parser)

    def do_test_setup(self, test_case):
        return False


class NetworkKV(CoreDispatchKV):
    kv_class = 'networkkeyvalue'
    dtype = 'NET_kv'
    dgroup = 'kv'

    detail_args = [detail_pk_argument('kv_pk', dtype)]

    kvlist_args = [kvlist_pk_argument('obj_pk', dtype)]


registrar.register(NetworkKV())


class SiteKV(CoreDispatchKV):
    kv_class = 'sitekeyvalue'
    dtype = 'SITE_kv'
    dgroup = 'kv'

    detail_args = [detail_pk_argument('kv_pk', dtype)]

    kvlist_args = [kvlist_pk_argument('obj_pk', dtype)]


registrar.register(SiteKV())


class VlanKV(CoreDispatchKV):
    kv_class = 'vlankeyvalue'
    dtype = 'VLAN_kv'
    dgroup = 'kv'

    detail_args = [detail_pk_argument('kv_pk', dtype)]

    kvlist_args = [kvlist_pk_argument('obj_pk', dtype)]


registrar.register(VlanKV())
