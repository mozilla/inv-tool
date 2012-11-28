import pdb
import subprocess, shlex
import unittest
import sys
sys.path.insert(0, "/home/juber/repositories/inv-tool")
import simplejson as json
from gettext import gettext as _

from invtool.dispatch import registrar
from invtool.dispatch import DNSDispatch

EXEC = "./bin/invtool --json"

def test_method_to_params(test_case):
    if not test_case:
        return ''
    elif not test_case[0]:
        return test_case[1]
    else:
        return "--{0} {1}".format(*test_case)

def call_to_json(command_str):
    """Given a string, this function will shell out, execute the command
    and parse the json returned by that command"""
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
            expected_status, command = commands[0]
            ret, errors, rc = call_to_json(command)

            if errors:
                self.fail(errors)

            self.assertEqual(0, rc)

            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], expected_status)

            # Range
            expected_status, command = commands[1]
            ret, errors, rc = call_to_json(command)

            if errors:
                self.fail(errors)

            self.assertEqual(0, rc)

            self.assertTrue('http_status' in ret)
            self.assertEqual(ret['http_status'], expected_status)


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

        return build_testcase(commands)

    ts = unittest.TestSuite()
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

