from setuptools import find_packages, setup
from setuptools.command.install import install


version = '0.5.3'

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
    'click==6.7',
    'lark-parser>=0.6.2'
]

extras = [
    'sphinx',
    'guzzle-sphinx-theme'
]


setup(name='storyscript',
      version=version,
      description='',
      long_description='',
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
          'console_scripts': ['storyscript=storyscript.cli:Cli.main']
      })
