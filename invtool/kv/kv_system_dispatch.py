from invtool.lib.registrar import registrar

from invtool.tests.utils import (
    call_to_json, test_method_to_params, EXEC, TestKVSetupMixin
)
from invtool.kv.kv_dispatch import DispatchKV
from invtool.lib.kv_options import (
    key_argument, value_argument, update_pk_argument,
    delete_pk_argument, detail_pk_argument, kvlist_pk_argument,
    create_pk_argument
)
from invtool.system_dispatch import DispatchSystem


class SystemKV(DispatchKV, TestKVSetupMixin):
    kv_class = 'keyvalue'
    dtype = 'SYS_kv'
    dgroup = 'kv'
    create_args = [
        key_argument('key'),
        value_argument('value'),
        create_pk_argument('obj_pk', dtype)
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

    def do_test_setup(self, test_case):
        command = [EXEC, DispatchSystem.dtype, 'create']
        for add_arg, extract_arg, tm in DispatchSystem.create_args:
            command.append(test_method_to_params(tm()))
        command_str = ' '.join(command)
        ret, errors, rc = call_to_json(command_str)
        if errors:
            test_case.fail(errors)
        return ret['pk']


registrar.register(SystemKV())
