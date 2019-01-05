#! /usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='dltpy',
    version='0.1',
    packages=find_packages(),
    scripts=['bin/dltpy-dump'],
    install_requires=['kaitaistruct>=0.7'],
)