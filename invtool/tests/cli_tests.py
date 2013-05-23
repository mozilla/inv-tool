import subprocess
import shlex
import unittest
from itertools import chain

try:
    import simplejson as json
except ImportError:
    import json

from gettext import gettext as _

import sys
sys.path.insert(0, '')

from invtool.dns_dispatch import registrar
from invtool.sreg_dispatch import DispatchHW, DispatchSREG

EXEC = "./inv --json"


def test_method_to_params(test_case):
    if not test_case:
        return ''
    elif not test_case[0]:
        return test_case[1]
    else:
        return "--{0} {1}".format(*test_case)


def call_to_json(command_str):
    """
    Given a string, this function will shell out, execute the command
    and parse the json returned by that command
    """
    p = subprocess.Popen(shlex.split(command_str),
                         stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stderr:
        return None, stderr, p.returncode

    stdout = stdout.replace('u\'', '"').replace('\'', '"').strip('\n')
    try:
        return json.loads(stdout, 'unicode'), None, p.returncode
    except json.decoder.JSONDecodeError, e:
        return (None,
                "Ret was: {0}. Got error: {1}".format(stdout, str(e)),
                p.returncode)


def run_dns_tests():
    def build_testcase(dispatch, commands):
        """The first command is used to create an object. Using the pk returned
        from the object's creation we look up the object and use the second
        command to update the object. The object is then deleted and finally
        the object is looked up again to ensure a 404."""
        class _TestCase(unittest.TestCase):
            pass

        def place_holder(self):
            # Create the object
            expected_status, command = commands[0]
            ret, errors, rc = call_to_json(command)

            if errors:
                self.fail(errors)

            self.assertEqual(0, rc)

            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], expected_status)
            self.assertTrue('pk' in ret)
            obj_pk = ret['pk']

            # Look up the object
            detail_command = _("{0} {1} detail --pk {2}".format(
                EXEC, dispatch.dtype, obj_pk)
            )
            ret, errors, rc = call_to_json(detail_command)
            if errors:
                self.fail(errors)
            self.assertEqual(0, rc)

            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], 200)
            self.assertTrue('pk' in ret)
            self.assertEqual(ret['pk'], obj_pk)

            # The Update call
            expected_status, command = commands[1]
            command = "{0} --pk {1}".format(command, obj_pk)
            ret, errors, rc = call_to_json(command)
            self.assertEqual(0, rc)

            if errors:
                self.fail(errors)

            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], expected_status)

            # Look up the object using the calculated detail command
            ret, errors, rc = call_to_json(detail_command)
            if errors:
                self.fail(errors)
            self.assertEqual(0, rc)

            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], 200)
            self.assertTrue('pk' in ret)
            self.assertEqual(ret['pk'], obj_pk)

            # Make sure an update doesn't require all the fields to be
            # specified
            blank_update_command = _("{0} {1} update --pk {2}".format(
                EXEC, dispatch.dtype, obj_pk)
            )
            ret, errors, rc = call_to_json(blank_update_command)
            if errors:
                self.fail(errors)
            self.assertEqual(0, rc)
            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], 202)

            # Delete the object
            delete_command = _("{0} {1} delete --pk {2}".format(
                EXEC, dispatch.dtype, obj_pk)
            )
            ret, errors, rc = call_to_json(delete_command)
            if errors:
                self.fail(errors)
            self.assertEqual(0, rc)
            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], 204)

            # Detail the object (expect a 404)
            ret, errors, rc = call_to_json(detail_command)
            if errors:
                self.fail(errors)
            self.assertEqual(1, rc)

            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], 404)
            self.assertFalse('pk' in ret)

        test_name = "test_{0}".format(dispatch.dtype)
        place_holder.__name__ = test_name
        setattr(_TestCase, test_name, place_holder)
        return _TestCase

    def build_testcases(dispatch):
        commands = []
        command = [EXEC, dispatch.dtype, 'create']
        for add_arg, extract_arg, test_method in dispatch.create_args:
            command.append(test_method_to_params(test_method()))
        commands.append((201, ' '.join(command)))

        command = [EXEC, dispatch.dtype, 'update']
        for add_arg, extract_arg, test_method in dispatch.update_args:
            command.append(test_method_to_params(test_method()))
        commands.append((202, ' '.join(command)))

        return build_testcase(dispatch, commands)

    unittest.TestSuite()
    test_cases = []
    # Build DNS test cases
    for dispatch in registrar.dispatches:
        if dispatch.dgroup == 'dns':
            tc = build_testcases(dispatch)
            test_cases.append(tc)

    return test_cases


def run_dhcp_tests():
    class SREGHWTestCase(unittest.TestCase):
        def test_HW_and_SREG(self):
            # Create the SREG
            command = [EXEC, DispatchSREG.dtype, 'create']
            for add_arg, extract_arg, test_method in DispatchSREG.create_args:
                command.append(test_method_to_params(test_method()))

            sreg_ret, sreg_errors, sreg_rc = call_to_json(' '.join(command))

            if sreg_errors:
                self.fail(sreg_errors)

            self.assertEqual(0, sreg_rc)

            # Make sure the SREG was created correctly
            self.assertTrue('http_status' in sreg_ret)
            self.assertEqual(sreg_ret['http_status'], 201)
            self.assertTrue('pk' in sreg_ret)
            sreg_pk = sreg_ret['pk']

            # Create a HW
            command = [EXEC, DispatchHW.dtype, 'create']
            for add_arg, extract_arg, test_method in DispatchHW.create_args:
                command.append(test_method_to_params(test_method()))
            command_str = ' '.join(command)
            # lol, we are jinja2. evaluate our placeholder
            command_str = command_str.replace('{{ sreg_pk }}', str(sreg_pk))
            hw_ret, hw_errors, hw_rc = call_to_json(command_str)

            if hw_errors:
                self.fail(sreg_errors)

            self.assertEqual(0, hw_rc)
            self.assertTrue('http_status' in hw_ret)
            self.assertEqual(hw_ret['http_status'], 201)
            self.assertTrue('pk' in hw_ret)
            hw_pk = hw_ret['pk']

            # Detail the hw and make sure we get the correct results
            def hw_detail():
                # Use a closure to keep outer context more clean
                detail_command = _("{0} {1} detail --pk {2}".format(
                    EXEC, DispatchHW.dtype, hw_pk)
                )
                ret, errors, rc = call_to_json(detail_command)
                if errors:
                    self.fail(errors)
                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 200)
                self.assertTrue('pk' in ret)
                self.assertEqual(ret['pk'], hw_pk)

            # Detail the sreg and make sure we see the hw we created
            def detail_sreg_1():
                detail_command = _("{0} {1} detail --pk {2}".format(
                    EXEC, DispatchSREG.dtype, sreg_pk)
                )
                ret, errors, rc = call_to_json(detail_command)
                if errors:
                    self.fail(errors)
                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 200)
                self.assertTrue('pk' in ret)
                self.assertEqual(ret['pk'], sreg_pk)

                self.assertTrue('hwadapter_set' in ret)
                self.assertEqual(1, len(ret['hwadapter_set']))
                self.assertEqual(hw_pk, ret['hwadapter_set'][0]['pk'])

            detail_sreg_1()

            def delete_hw():
                # Create a HW
                command = [EXEC, DispatchHW.dtype, 'create']
                for add_arg, extract_arg, tm in DispatchHW.create_args:
                    command.append(test_method_to_params(tm()))
                command_str = ' '.join(command)
                # lol, we are jinja2. evaluate our placeholder
                command_str = command_str.replace(
                    '{{ sreg_pk }}', str(sreg_pk))
                local_ret, local_errors, local_rc = call_to_json(command_str)

                if local_errors:
                    self.fail(sreg_errors)

                self.assertTrue('http_status' in local_ret)
                self.assertEqual(local_ret['http_status'], 201)
                self.assertTrue('pk' in local_ret)
                local_pk = local_ret['pk']

                delete_command = _("{0} {1} delete --pk {2}".format(
                    EXEC, DispatchHW.dtype, local_pk)
                )
                ret, errors, rc = call_to_json(delete_command)

                if errors:
                    self.fail(errors)
                self.assertEqual(0, rc)

                detail_command = _("{0} {1} detail --pk {2}".format(
                    EXEC, DispatchHW.dtype, local_pk)
                )
                ret, errors, rc = call_to_json(detail_command)

                if errors:
                    self.fail(errors)

                self.assertEqual(1, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 404)
                self.assertTrue('pk' not in ret)

            delete_hw()

            def delete_sreg_causing_hw_delete():
                delete_command = _("{0} {1} delete --pk {2}".format(
                    EXEC, DispatchSREG.dtype, sreg_pk)
                )
                ret, errors, rc = call_to_json(delete_command)
                if errors:
                    self.fail(errors)
                self.assertEqual(0, rc)

                # Make sure the SREG getting deleted caused a cascade delete
                detail_command = _("{0} {1} detail --pk {2}".format(
                    EXEC, DispatchHW.dtype, hw_pk)
                )
                local_ret, local_errors, local_rc = call_to_json(
                    detail_command)

                if local_errors:
                    self.fail(local_errors)

                self.assertEqual(1, local_rc)

                self.assertTrue('http_status' in local_ret)
                self.assertEqual(local_ret['http_status'], 404)
                self.assertTrue('pk' not in local_ret)

            delete_sreg_causing_hw_delete()

    return [SREGHWTestCase]

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    dns_tcs = run_dns_tests()
    dhcp_tcs = run_dhcp_tests()
    for test_class in chain(dns_tcs, dhcp_tcs):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    unittest.TextTestRunner(verbosity=2).run(suite)
