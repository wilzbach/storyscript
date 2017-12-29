from setuptools import setup

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: Other/Proprietary License',
    'Natural Language :: English',
    'Topic :: Office/Business',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Software Development :: Compilers'
]

requirements = ['ply==3.4']


setup(name='storyscript',
      version='0.0.1',
      description='',
      long_description='',
      classifiers=classifiers,
      keywords='',
      author='Asyncy',
      author_email='noreply@storyscript.org',
      url='http://storyscript.org',
      license='MIT',
      packages=['storyscript'],
      include_package_data=True,
      zip_safe=True,
      install_requires=requirements,
      entry_points={
          'console_scripts': ['storyscript=storyscript.cli:Cli.main']
      })
