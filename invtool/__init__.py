import os

# Originally authored by the Buildbot Team Members

__version__ = "latest"

try:
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')
    with open(fn) as f:
        __version__ = f.read().strip()

except IOError:
    from subprocess import Popen, PIPE
    import re

    VERSION_MATCH = re.compile(r'(\d+(\.\d+){0,})*')

    try:
        dir = os.path.dirname(os.path.abspath(__file__))
        p = Popen(['git', 'describe', '--tags', '--always'], cwd=dir,
                  stdout=PIPE, stderr=PIPE)
        out = p.communicate()[0]

        if (not p.returncode) and out:
            v = VERSION_MATCH.search(out)
            if v:
                __version__ = v.group()
    except OSError:
        pass
