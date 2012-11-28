from distutils.core import setup

setup(
    name='Mozilla Inventory Tool',
    version='0.1.0',
    author='Jacques Uber',
    author_email='juber@mozilla.com',
    packages=['invtool', 'invtool.tests'],
    scripts=['bin/invtool'],
    url='https://github.com/uberj/inv-tool',
    license='LICENSE.txt',
    description='An interface to inventory',
    long_description=open('README.rst').read(),
    install_requires=[
        open('requirements.txt').read().strip('\n').replace('\n',',')
    ],
    data_files=[('/etc', ['etc/invtool.conf'])],
)
