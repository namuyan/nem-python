#!/user/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

try:
    with open('README.md') as f:
        readme = f.read()
except IOError:
    readme = ''


def _requires_from_file(filename):
    return open(filename).read().splitlines()

# version
here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(os.path.join(here,
                                              'nem_python',
                                              '__init__.py'))
                if line.startswith('__version__ = ')),
               '0.0.dev0')

setup(
    name="nem_python",
    version=version,
    url='https://github.com/namuyan/nem-python',
    author='namuyan',
    description='Package Dependency: Validates package requirements',
    long_description=readme,
    packages=find_packages(),
    license="MIT",
    install_requires=['requests', 'fasteners', 'pycrypto'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)