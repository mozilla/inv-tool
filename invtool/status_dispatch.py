try:
    import simplejson as json
except ImportError:
    import json  # noqa

import invtool
from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib import config


class StatusDispatch(Dispatch):
    dgroup = dtype = 'status'

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def build_parser(self, base_parser):
        base_parser.add_parser(
            'status', help="Print config vars.", add_help=True
        )

    def status(self, nas):
        """
        Look at the config module and print out interesting things.
        """
        # Items of interest
        items = (
            'API_MAJOR_VERSION',
            'GLOBAL_CONFIG_FILE',
            'HOME_CONFIG_FILE',
            'LOCAL_CONFIG_FILE',
            'AUTH_TYPE',
            'REMOTE',
            'dev',
            'host',
            'port',
        )
        ret = {}
        for item in items:
            ret[item] = getattr(config, item)
        ret['INVTOOL_VERSION'] = invtool.__version__
        return 0, self.format_response(nas, ret, 'Status Vars')


registrar.register(StatusDispatch())
