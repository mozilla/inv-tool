from distutils.core import setup
import invtool
from os import getuid

if getuid() == 0:
    # Require root privileges
    data_files = [('/etc', ['etc/invtool.conf-dist']),
                  ('/usr/local/share/man/man1/', ['docs/man1/invtool.1.gz'])]
else:
    data_files = None

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='invtool',
    version=invtool.__version__,
    author='Jacques Uber',
    author_email='juber@mozilla.com',
    install_requires=required,
    packages=['invtool', 'invtool.tests', 'invtool.lib', 'invtool.kv'],
    package_dir={'invtool': 'invtool'},
    package_data={
        'invtool': ['invtool/*', 'invtool/*/*/*.py', 'invtool/*/*.py']
    },
    scripts=['bin/invtool'],
    url='https://github.com/uberj/inv-tool',
    license='LICENSE.txt',
    description='An interface to inventory',
    data_files=data_files
)
