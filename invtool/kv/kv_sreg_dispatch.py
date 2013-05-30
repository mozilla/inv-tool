from invtool.lib.registrar import registrar
from invtool.sreg_dispatch import DispatchSREG, DispatchHW
from invtool.tests.utils import call_to_json, test_method_to_params, EXEC

from invtool.kv.kv_dispatch import DispatchKV
from invtool.lib.dns_options import detail_pk_argument
from invtool.lib.kv_options import (
    key_argument, value_argument, update_pk_argument,
    delete_pk_argument, detail_pk_argument, kvlist_pk_argument,
    create_pk_argument
)


class TestSetupMixin(object):
    def do_setup(self, DispatchType, test_case):
        """Create an object and return it's pk so the KV api can test itself"""
        command = [EXEC, DispatchType.dtype, 'create']
        for add_arg, extract_arg, tm in DispatchType.create_args:
            command.append(test_method_to_params(tm()))
        command_str = ' '.join(command)
        ret, errors, rc = call_to_json(command_str)
        if errors:
            test_case.fail(errors)
        return ret['pk']


class StaticRegKV(DispatchKV, TestSetupMixin):
    kv_class = 'staticregkeyvalue'
    dtype = 'SREG_kv'
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
        return self.do_setup(DispatchSREG, test_case)


class HWAdapterKV(DispatchKV, TestSetupMixin):
    kv_class = 'hwadapterkeyvalue'
    dtype = 'HW_kv'
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
        sreg_pk = self.do_setup(DispatchSREG, test_case)

        # Create a HW
        command = [EXEC, DispatchHW.dtype, 'create']
        for add_arg, extract_arg, test_method in DispatchHW.create_args:
            command.append(test_method_to_params(test_method()))
        command_str = ' '.join(command)
        # lol, we are jinja2. evaluate our placeholder
        command_str = command_str.replace('{{ sreg_pk }}', str(sreg_pk))
        hw_ret, hw_errors, hw_rc = call_to_json(command_str)

        if hw_errors:
            test_case.fail(hw_errors)
        return hw_ret['pk']


# Uncomment when dhcp is rolled out
#registrar.register(StaticRegKV())
#registrar.register(HWAdapterKV())
