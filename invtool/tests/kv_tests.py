import unittest

from gettext import gettext as _

import sys
sys.path.insert(0, '')

__import__('invtool.main')
from invtool.main import registrar
from invtool.tests.utils import call_to_json, test_method_to_params, EXEC


def run_tests():
    def build_testcase(dispatch, commands):
        """
        The first command is used to create an object. Using the pk returned
        from the object's creation we look up the object and use the second
        command to update the object. The object is then deleted and finally
        the object is looked up again to ensure a 404.
        """
        class _TestCase(unittest.TestCase):
            pass

        def place_holder(self):
            # This should create an object that we can use to associate KV's to
            print "testing {0} ...".format(dispatch.dtype)
            obj_pk = dispatch.do_test_setup(self)

            # List the object's KV store and remember the count
            def list_kv():
                list_command = _("{0} {1} list --obj-pk {2}".format(
                    EXEC, dispatch.dtype, obj_pk)
                )
                ret, errors, rc = call_to_json(list_command)

                if errors:
                    self.fail(errors)

                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 200)
                self.assertTrue('kvs' in ret)
                return len(ret['kvs'])

            num_kvs_before = list_kv()

            expected_status, command = commands[0]
            # Create a Keyvalue

            def create_kv():
                command_str = command.replace('{{ obj_pk }}', str(obj_pk))
                ret, errors, rc = call_to_json(command_str)

                if errors:
                    self.fail(errors)

                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], expected_status)
                self.assertTrue('kv_pk' in ret)
                return ret['kv_pk']

            kv_pk = create_kv()

            num_kvs_after = list_kv()

            self.assertEqual(num_kvs_before + 1, num_kvs_after)

            detail_command = _("{0} {1} detail --kv-pk {2}".format(
                EXEC, dispatch.dtype, kv_pk)
            )

            # Look up the object
            def lookup_kv():
                ret, errors, rc = call_to_json(detail_command)
                if errors:
                    self.fail(errors)
                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 200)
                self.assertTrue('kv_pk' in ret)
                self.assertEqual(ret['kv_pk'], kv_pk)

            lookup_kv()

            # The Update call
            def update_kv():
                expected_status, command = commands[1]
                update_command_str = command.replace('{{ kv_pk }}', str(kv_pk))
                ret, errors, rc = call_to_json(update_command_str)

                if errors:
                    self.fail(errors)

                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], 200)

            update_kv()

            # Delete the object
            def delete_kv():
                delete_command = _("{0} {1} delete --kv-pk {2}".format(
                    EXEC, dispatch.dtype, kv_pk)
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
                self.assertFalse('kv_pk' in ret)

            delete_kv()

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
    # Build KV test cases
    for dispatch in registrar.dispatches:
        if dispatch.dgroup == 'kv':
            tc = build_testcases(dispatch)
            test_cases.append(tc)

    return test_cases

if __name__ == "__main__":
    tcs = run_tests()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test_class in tcs:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    unittest.TextTestRunner(verbosity=2).run(suite)
