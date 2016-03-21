#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup

root = os.path.abspath(os.path.dirname(__file__))

version = __import__('swf').__version__

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(root, 'requirements-test.txt')) as f:
    test_requirements = [line for line in f]

with open(os.path.join(root, 'requirements.txt')) as f:
    install_requirements = [line for line in f]

setup(
    name='simple-workflow',
    version=version,
    license='MIT',

    description='Amazon simple workflow service wrapper for python',
    long_description=README + '\n\n',

    author='Oleiade',
    author_email='tcrevon@gmail.com',
    url='http://github.com/botify-labs/python-simple-workflow',
    keywords='amazon simple wokflow swf python',
    zip_safe=True,

    install_requires=install_requirements,
    tests_requires=test_requirements,

    package_dir={'': '.'},
    include_package_data=False,

    packages=[
        'swf',
        'swf.actors',
        'swf.querysets',
        'swf.responses',
        'swf.models',
        'swf.models.event',
        'swf.models.decision',
        'swf.models.history',
    ],
)
