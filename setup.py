from setuptools import find_packages, setup
from setuptools.command.install import install


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
    'ply==3.4'
]

extras = [
    'sphinx',
    'guzzle-sphinx-theme'
]


class CustomInstallCommand(install):
    def run(self):
        print('building lexer and parser')
        from storyscript import parser
        parser.Parser(optimize=True)
        install.run(self)


setup(name='storyscript',
      version='0.0.4',
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
      cmdclass={
          'install': CustomInstallCommand,
      },
      entry_points={
          'console_scripts': ['storyscript=storyscript.cli:Cli.main']
      })
