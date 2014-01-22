try:
    import simplejson as json
except ImportError:
    import json  # noqa

from invtool.lib.registrar import registrar
from invtool.core_dispatch import CoreDispatch
from invtool.lib.config import API_MAJOR_VERSION

from invtool.lib.options import (
    comment_argument, general_argument,
    datetime_argument, date_argument
)

from invtool.lib.system_options import (
    foreign_key_argument, hostname_argument, notes_argument,
    system_pk_argument, new_hostname_argument
)


class DispatchSystem(CoreDispatch):
    object_url = "/en-US/core/api/v1_core/{1}/{2}/"
    object_list_url = "/en-US/core/api/v1_core/{1}/"
    resource_name = 'system'
    dtype = 'SYS'
    dgroup = 'core'

    create_args = [
        foreign_key_argument(
            'operating-system', 'The primary key of an OperatingSystem'
        ),
        foreign_key_argument(
            'server-model', 'The primary key of a ServerModel'
        ),
        foreign_key_argument(
            'allocation', 'The primary key of an Allocation'
        ),
        foreign_key_argument(
            'system-rack', 'The primary key of a SystemRack'
        ),
        foreign_key_argument(
            'system-type', 'The primary key of a SystemType'
        ),
        foreign_key_argument(
            'system-status', 'The primary key of a SystemStatus'
        ),
        general_argument('serial', 'Serial number'),
        general_argument('oob-ip', 'Out of bands ip address'),
        general_argument('asset-tag', 'Asset Tag'),
        general_argument('notes', 'Notes about a system'),
        general_argument(
            'rack-order',
            'Rack order (e.x.: 1.2, 33, 4.0)',
            type=float,
            test_data=lambda: ('rack-order', '1.1')
        ),
        general_argument('switch-ports', 'Switch Port'),
        general_argument('patch-panel-port', 'Patch Panel Port'),
        general_argument('oob-switch-port', 'OOB switch port'),
        date_argument('purchase-date', 'Date purchased'),
        general_argument('purchase-price', 'Purchase Price'),
        datetime_argument(
            'change-password', 'When the last password change was. Format is '
            'yyyy-mm-ddThh-mm (iso-8601)'
        ),
        date_argument(
            'warranty-start', 'Warrenty start date. Format is '
            'yyyy-mm-dd'
        ),
        date_argument('warranty-end', 'Warrenty end date yyyy-mm-dd'),
        notes_argument('description', 'Notes about this system'),
        comment_argument('comment'),
    ]

    # When a system is updated, there may be a new hostname. A user can use
    # 'new-hostname' to specify a new hostname and use --pk <hostname> to
    # specify which host is getting the new hostname.
    update_args = [
        system_pk_argument(),
        new_hostname_argument()
    ] + create_args

    # When a system is created, there must be a hostname
    create_args = create_args + [
        hostname_argument('hostname', 'A valid hostname'),
    ]

    delete_args = [
        system_pk_argument(action='deleting'),
        comment_argument('comment')
    ]

    detail_args = [system_pk_argument(action='detailing')]

    def update_url(self, nas):
        pk = nas.pk or nas.hostname
        return self.object_url.format(
            API_MAJOR_VERSION, self.resource_name, pk
        )


registrar.register(DispatchSystem())
