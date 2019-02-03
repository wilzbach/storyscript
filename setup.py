#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
from os import path

from setuptools import find_packages, setup
from setuptools.command.install import install as _install
from setuptools.command.sdist import sdist as _sdist

root_dir = path.dirname(__file__)


# Read a file and return its as a string
def read(file_name):
    return io.open(path.join(root_dir, file_name)).read()


name = 'storyscript'
version = None
release_version = None
# try loading the current version
try:
    result = {'__file__': path.join(root_dir, name, 'Version.py')}
    exec(read(path.join(name, 'Version.py')), result)
    version = result['version']
    release_version = result['release_version']
except FileNotFoundError:
    pass

description = read('README.md')
short_description = ('StoryScript is an high-level language that can be used '
                     'to orchestrate microservices in an algorithmic way.')

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Plugins',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.6',
    'Topic :: Office/Business',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Software Development :: Compilers'
]

requirements = [
    'click==7.0',
    'lark-parser==0.6.5',
    'click-alias==0.1.1a2'
]

extras = [
    'sphinx',
    'guzzle-sphinx-theme'
]

###############################################################################
# Custom build steps
###############################################################################


def prepare_release(cwd, use_release):
    version_file = path.join(cwd, name, 'VERSION')
    if use_release:
        version_text = release_version
    else:
        version_text = version
    print(f'writing version({version_text}) -> {version_file}')
    with open(version_file, 'w') as f:
        f.write(version_text)


class Install(_install):
    def run(self):
        _install.run(self)
        self.execute(prepare_release, (self.install_lib, False),
                     msg='Preparing the installation')


class Sdist(_sdist):
    def make_release_tree(self, basedir, files):
        _sdist.make_release_tree(self, basedir, files)
        self.execute(prepare_release, (basedir, True),
                     msg='Building the release')


setup(name=name,
      version=release_version,
      description=short_description,
      long_description=description,
      long_description_content_type='text/markdown',
      classifiers=classifiers,
      download_url=('https://github.com/asyncy/storyscript/archive/'
                    f'{version}.zip'),
      keywords='',
      author='Asyncy',
      author_email='noreply@storyscript.org',
      url='http://storyscript.org',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=requirements,
      extras_require={
          'docs': extras
      },
      entry_points={
          'console_scripts': ['storyscript=storyscript.Cli:Cli.main']
      },
      cmdclass={
        'install': Install,
        'sdist': Sdist,
      })
