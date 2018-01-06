from setuptools import setup

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


setup(name='storyscript',
      version='0.0.2',
      description='',
      long_description='',
      classifiers=classifiers,
      download_url='https://github.com/asyncy/storyscript/archive/master.zip',
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
