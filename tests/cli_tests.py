import pdb
import unittest
import sys
sys.path.insert(0, "/home/juber/repositories/inv-tool")
from invdns.dispatch import registrar
from invdns.dispatch import DNSDispatch

EXEC_PATH = "./bin/invdns"

def run_tests():
    def test_method_to_params(test_case):
        if not test_case:
            return ''
        elif not test_case[0]:
            return test_case[1]
        else:
            return "--{0} {1}".format(*test_case)

    def build_testcases(dispatch):
        test_cases = []
        command = [EXEC_PATH]
        for add_arg, extract_arg, test_method in dispatch.create_args:
            command.append(test_method_to_params(test_method()))
        print ' '.join(command)
        class _TestCase(unittest.TestCase):
            def test_foo(self):
                print "Ran test"
        return _TestCase('test_foo')

    ts = unittest.TestSuite()
    # Build DNS test cases
    for dispatch in registrar.dns_dispatches:
        tcs = build_testcases(dispatch)
        ts.addTests(tcs)

    result = unittest.TestResult()
    ts.run(result)

if __name__ == "__main__":
    run_tests()
