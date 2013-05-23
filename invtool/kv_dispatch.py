try:
    import simplejson as json
except ImportError:
    import json
import requests

from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib.config import REMOTE, auth

from invtool.lib.kv_options import (
    key_argument, value_argument, update_pk_argument,
    delete_pk_argument, detail_pk_argument, kvlist_pk_argument
)

from invtool.lib.parser import (
    build_create_parser, build_update_parser, build_delete_parser,
    build_detail_parser
)


def build_kvlist_parser(dispatch, action_parser):
    kvlist_parser = action_parser.add_parser(
        'kvlist', help="List a object's KV pairs"
    )
    for add_arg, extract_arg, test_method in dispatch.kvlist_args:
        add_arg(kvlist_parser)


class DispatchKV(Dispatch):
    def route(self, nas):
        if self.dtype.lower() == nas.dtype.lower():
            return getattr(self, nas.action.lower())(nas)

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
        build_create_parser(
            self, action_parser, help="Create a {0} KV pair".format(self.dtype)
        )
        build_update_parser(
            self, action_parser, help="Update a {0} KV pair".format(self.dtype)
        )
        build_delete_parser(
            self, action_parser, help="Delete a {0} KV pair".format(self.dtype)
        )
        build_detail_parser(
            self, action_parser, help="Detail a {0} KV pair".format(self.dtype)
        )
        build_kvlist_parser(self, action_parser)

    def action(self, nas, url, method, data):
        headers = {'content-type': 'application/json'}
        resp = method(url, headers=headers, data=data, auth=auth)
        return self.handle_resp(nas, data, resp)

    def format_response(self, nas, resp_msg, user_msg):
        resp_list = []
        if nas.p_json:
            resp_list.append(json.dumps(resp_msg, indent=2))
        else:
            resp_list.append(user_msg)
            for k, v in resp_msg.iteritems():
                if k == 'kvs':
                    self.format_kvs(v, resp_list)
                    continue
                resp_list.append("{0}: {1}".format(k, v))
        return resp_list

    def format_kvs(self, bundles, resp_list):
        for i, bundle in enumerate(bundles):
            for ikey, ivalue in bundle.iteritems():
                resp_list.append(
                    "{0} {1}: {2}".format(
                        (i % 2 + 1) * '|', ikey, ivalue
                    )
                )

    def kvlist(self, nas):
        url = "{0}{1}?format=json".format(REMOTE, self.kvlist_url(nas))
        headers = {'content-type': 'application/json'}
        resp = requests.get(url, headers=headers, auth=auth)
        return self.handle_resp(nas, {}, resp)

    def create_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{obj_pk}/create/'.format(
            **{'kv_class': self.kv_class + 'keyvalue', 'obj_pk': nas.obj_pk}
        )

    def detail_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{kv_pk}/detail/'.format(
            **{'kv_class': self.kv_class + 'keyvalue', 'kv_pk': nas.kv_pk}
        )

    def kvlist_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{obj_pk}/list/'.format(
            **{'kv_class': self.kv_class + 'keyvalue', 'obj_pk': nas.obj_pk}
        )

    def update_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{kv_pk}/update/'.format(
            **{'kv_class': self.kv_class + 'keyvalue', 'kv_pk': nas.kv_pk}
        )

    def delete_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{kv_pk}/delete/'.format(
            **{'kv_class': self.kv_class + 'keyvalue', 'kv_pk': nas.kv_pk}
        )


class StaticRegistrationKV(DispatchKV):
    kv_class = 'sreg'
    dtype = kv_class + 'kv'
    dgroup = 'kv'
    create_args = [
        key_argument('key'),
        value_argument('value'),
        update_pk_argument('obj_pk', dtype)
    ]

    update_args = [
        key_argument('key'),
        value_argument('value'),
        update_pk_argument('kv_pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('kv_pk', dtype)
    ]

    detail_args = [detail_pk_argument('kv_pk', dtype)]

    kvlist_args = [kvlist_pk_argument('obj_pk', dtype)]


class HWAdapterKV(DispatchKV):
    kv_class = 'hwadapter'
    dtype = kv_class + 'kv'
    dgroup = 'kv'
    create_args = [
        key_argument('key'),
        value_argument('value'),
        update_pk_argument('obj_pk', dtype)
    ]
    update_args = [
        key_argument('key'),
        value_argument('value'),
        update_pk_argument('kv_pk', dtype)
    ]

    delete_args = [
        delete_pk_argument('kv_pk', dtype)
    ]

    detail_args = [detail_pk_argument('kv_pk', dtype)]

    kvlist_args = [kvlist_pk_argument('obj_pk', dtype)]


registrar.register(StaticRegistrationKV())
registrar.register(HWAdapterKV())
