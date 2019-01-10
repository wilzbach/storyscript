# -*- coding: utf-8 -*-
import io

from setuptools import find_packages, setup


version = '0.9.0'

description = io.open('README.md', 'r', encoding='utf-8').read()
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
    'delegator.py>=0.1.1',
    'lark-parser>=0.6.5',
    'click-alias==0.1.1a2'
]

extras = [
    'sphinx',
    'guzzle-sphinx-theme'
]


setup(name='storyscript',
      version=version,
      description=short_description,
      long_description=description,
      long_description_content_type='text/markdown',
      classifiers=classifiers,
      download_url='https://github.com/asyncy/storyscript/archive/master.zip',
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
      })
