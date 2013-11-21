import unittest

try:
    import simplejson as json
except ImportError:
    import json

from invtool.tests.utils import call_to_json, EXEC


def run_tests():
    def build_testcase(commands):
        """The first command is used to create an object. Using the pk returned
        from the object's creation we look up the object and use the second
        command to update the object. The object is then deleted and finally
        the object is looked up again to ensure a 404."""
        class _TestCase(unittest.TestCase):
            pass

        def place_holder(self):
            # Search
            def test_search():
                expected_status, command = commands[0]
                ret, errors, rc = call_to_json(command)

                if errors:
                    self.fail(errors)

                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], expected_status)

            test_search()

            # Range
            def test_range():
                expected_status, command = commands[1]
                ret, errors, rc = call_to_json(command)

                if errors:
                    self.fail(errors)

                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], expected_status)

            test_range()

            # CSV export
            def test_csv_export():
                expected_status, command = commands[2]
                ret, errors, rc = call_to_json(command)

                if errors:
                    self.fail(errors)

                self.assertEqual(0, rc)

                self.assertTrue('http_status' in ret)
                self.assertEqual(ret['http_status'], expected_status)

            test_csv_export()

        test_name = "test_{0}".format('search')
        place_holder.__name__ = test_name
        setattr(_TestCase, test_name, place_holder)
        return _TestCase

    def build_testcases():
        commands = []
        command = [EXEC, 'search', ' -q "foopy32"']
        commands.append((200, ' '.join(command)))

        command = [EXEC, 'search', ' -r 10.0.0.0,10.0.20.3']
        commands.append((200, ' '.join(command)))

        command = [EXEC, 'csv', ' -q foopy32']
        commands.append((200, ' '.join(command)))

        return build_testcase(commands)

    unittest.TestSuite()
    test_cases = [build_testcases()]
    return test_cases

if __name__ == "__main__":
    tcs = run_tests()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test_class in tcs:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    unittest.TextTestRunner(verbosity=2).run(suite)
