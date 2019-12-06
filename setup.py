#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
from os import path
from shutil import rmtree
from glob import glob

from pkg_resources import DistributionNotFound, get_distribution

from setuptools import Command, find_packages, setup

root_dir = path.dirname(__file__)


# Read a file and return its as a string
def read(file_name):
    with open(path.join(root_dir, file_name), encoding="utf-8") as f:
        return f.read()


name = "storyscript"
description = read("README.md")
short_description = (
    "StoryScript is an high-level language that can be used "
    "to orchestrate microservices in an algorithmic way."
)

classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Environment :: Plugins",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Programming Language :: Other Scripting Engines",
    "Topic :: Office/Business",
    "Topic :: Software Development :: Build Tools",
    "Topic :: Software Development :: Compilers",
]

requirements = [
    "bom-open~=0.4.0",
    "click~=7.0",
    "click-aliases~=1.0",
    "lark-parser==0.7.2",
    "story-hub~=0.3.1",
]

extras = ["sphinx", "guzzle-sphinx-theme"]

###############################################################################
# Custom build steps
###############################################################################


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(path.join(root_dir, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        subprocess.run(
            [
                sys.executable,
                "setup.py",
                "sdist",
                "bdist_egg",
                "bdist_wheel",
                "--universal",
            ],
            check=True,
        )

        self.status("Uploading the package to PyPI via Twine…")
        subprocess.run(["twine", "upload", *glob("dist/*")], check=True)
        sys.exit()


try:
    __version__ = get_distribution(name).version
except DistributionNotFound:
    __version__ = "0.0.0"

setup(
    name=name,
    description=short_description,
    long_description=description,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    download_url=(
        "https://github.com/storyscript/storyscript/archive/"
        f"{__version__}.zip"
    ),
    keywords="",
    author="Storyscript",
    author_email="support@storyscript.io",
    url="http://storyscript.org",
    license="MIT",
    packages=find_packages(exclude=("build.*", "tests", "tests.*")),
    include_package_data=True,
    install_requires=requirements,
    extras_require={"docs": extras, "stylecheck": ["black==19.10b0"],},
    python_requires=">=3.7",
    entry_points={"console_scripts": ["storyscript=storyscript.Cli:Cli.main"]},
    use_scm_version=True,
    setup_requires=["setuptools_scm~=3.3",],
    cmdclass={"upload": UploadCommand,},
)
