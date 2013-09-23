import subprocess
import shlex

try:
    import simplejson as json
except ImportError:
    import json

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
    print command_str
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


class TestKVSetupMixin(object):
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
