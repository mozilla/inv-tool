try:
    import simplejson as json
except ImportError:
    import json

from invtool.dispatch import Dispatch
from invtool.lib.registrar import registrar
from invtool.lib import config


def build_status_parsers(base_parser):
    # Search is a top level command.
    base_parser.add_parser(
        'status', help="Print config vars.", add_help=True
    )


class StatusDispatch(Dispatch):
    dgroup = dtype = 'status'

    def route(self, nas):
        return getattr(self, nas.dtype)(nas)

    def status(self, nas):
        """
        Look at the config module and print out interesting things.
        """
        # Items of interest
        items = (
            'API_MAJOR_VERSION',
            'CONFIG_FILE',
            'GLOBAL_CONFIG_FILE',
            'LOCAL_CONFIG_FILE',
            'REMOTE',
            'dev',
            'host',
            'port',
        )
        ret = {}
        for item in items:
            ret[item] = getattr(config, item)
        return 0, self.format_response(nas, ret, 'Status Vars')


registrar.register(StatusDispatch())
