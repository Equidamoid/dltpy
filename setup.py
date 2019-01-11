#! /usr/bin/env python3
from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='dltpy',
    version='0.2.2',
    description='Pyre-python reader for DLT log files',
    long_description=Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    author='Vladimir Shapranov',
    author_email='equidamoid@gmail.com',
    url='https://github.com/Equidamoid/dltpy',
    packages=find_packages(),
    scripts=['bin/dltpy-dump', 'bin/dltpy-filter'],
    install_requires=['kaitaistruct>=0.7'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

    ]
)
