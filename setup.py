#! /usr/bin/env python3
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import os
import pathlib
import shutil

class CMakeExtension(Extension):

    def __init__(self, name):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[])


class build_ext_cmake(build_ext):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)

    def build_cmake(self, extension):

        build_dir = pathlib.Path(self.build_temp)

        extension_path = pathlib.Path(self.get_ext_fullpath(extension.name))

        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(extension_path.parent.absolute(), exist_ok=True)

        # Now that the necessary directories are created, build

        self.announce("Configuring cmake project", level=3)

        # Change your cmake arguments below as necessary
        # Below is just an example set of arguments for building Blender as a Python module

        config = 'Debug' if self.debug else 'Release'
        self.spawn(['cmake', '-H'+str(pathlib.Path().absolute()), '-B'+self.build_temp,
                    '-DCMAKE_BUILD_TYPE=' + config,
                    '-DPYBIND11_PYTHON_VERSION=%s.%s' % (sys.version_info.major, sys.version_info.minor)])

        self.announce("Building binaries", level=3)

        self.spawn(['cmake', '--build', self.build_temp,
                    '--config', config])

        # Build finished, now copy the files into the copy directory
        # The copy directory is the parent directory of the extension (.pyd)

        self.announce("Moving built python module", level=3)

        bin_dir = os.path.join(build_dir, 'dltpy', 'native')
        self.distribution.bin_dir = bin_dir

        pyd_path = [os.path.join(bin_dir, _pyd) for _pyd in
                    os.listdir(bin_dir) if
                    os.path.isfile(os.path.join(bin_dir, _pyd)) and
                    os.path.splitext(_pyd)[0].startswith('dltreader_native') and
                    os.path.splitext(_pyd)[1] in [".pyd", ".so"]][0]

        shutil.move(pyd_path, extension_path)

setup(
    name='dltpy',
    version='0.3.6.6',
    description='DLT log reader',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    author='Vladimir Shapranov',
    author_email='equidamoid@gmail.com',
    url='https://github.com/Equidamoid/dltpy',
    packages=find_packages(),
    ext_modules=[CMakeExtension('dltpy/native/dltreader_native')],
    cmdclass={'build_ext': build_ext_cmake,},
    entry_points={
        'console_scripts': [
            'dltpy-filter=dltpy.dltpy_filter:main',
            'dltpy-print=dltpy.dltpy_print:main',
            'dltpy-receive=dltpy.dltpy_receive:main',
        ],
    },
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
