try:
    import simplejson as json
except ImportError:
    import json
import requests

from invtool.dispatch import Dispatch
from invtool.lib.config import REMOTE

from invtool.lib.parser import (
    build_create_parser, build_update_parser, build_delete_parser,
    build_detail_parser
)


def build_kvlist_parser(dispatch, action_parser):
    kvlist_parser = action_parser.add_parser(
        'list', help="List a object's KV pairs"
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

    def action(self, nas, url, method, data, **kwargs):
        kwargs.update(**{'form_encode': False})
        return super(DispatchKV, self).action(nas, url, method, data, **kwargs)

    def update(self, nas):
        # We have to override this because the default update uses PATCH, we
        # need to use POST because this dispatch isn't for a tastypie endpoint
        # and doesn't support PATCH yet.
        data = self.get_update_data(nas)  # Dispatch defined Hook
        url = "{0}{1}".format(REMOTE, self.update_url(nas))
        return self.action(nas, url, requests.post, data)

    def format_response(self, nas, resp_msg, user_msg):
        resp_list = []
        if nas.p_json:
            resp_list.append(json.dumps(resp_msg, indent=2))
        else:
            resp_list.append(user_msg)
            for k, v in resp_msg.iteritems():
                if k == 'kvs':  # process these last
                    continue
                resp_list.append("{0}: {1}".format(k, v))

            if 'kvs' in resp_msg:
                resp_list += self.format_kvs(resp_msg['kvs'], resp_list)

        return resp_list

    def format_kvs(self, bundles, resp_list):
        resp_list = []
        for i, bundle in enumerate(bundles):
            for ikey, ivalue in bundle.iteritems():
                resp_list.append("{0} {1}: {2}".format(
                    '-' if i % 2 else '=', ikey, ivalue
                ))
        return resp_list

    def list(self, nas):
        url = "{0}{1}?format=json".format(REMOTE, self.kvlist_url(nas))
        return self.action(nas, url, requests.get, {})

    def create_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{obj_pk}/create/'.format(
            **{'kv_class': self.kv_class, 'obj_pk': nas.obj_pk}
        )

    def detail_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{kv_pk}/detail/'.format(
            **{'kv_class': self.kv_class, 'kv_pk': nas.kv_pk}
        )

    def kvlist_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{obj_pk}/list/'.format(
            **{'kv_class': self.kv_class, 'obj_pk': nas.obj_pk}
        )

    def update_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{kv_pk}/update/'.format(
            **{'kv_class': self.kv_class, 'kv_pk': nas.kv_pk}
        )

    def delete_url(self, nas):
        return '/en-US/core/keyvalue/api/{kv_class}/{kv_pk}/delete/'.format(
            **{'kv_class': self.kv_class, 'kv_pk': nas.kv_pk}
        )
