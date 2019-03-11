#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import subprocess
from os import path

import pkg_resources

root_dir = path.abspath(path.dirname(path.dirname(__file__)))


def git_version():
    return subprocess.run(
        ['git', 'describe', '--abbrev=0', '--tags'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        check=True,
        cwd=root_dir,
    ).stdout.strip()


def git_describe():
    return subprocess.run(
        ['git', 'describe', '--dirty', '--tags'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        check=True,
        cwd=root_dir,
    ).stdout.strip()


def read_version_file():
    return io.open(path.join(root_dir, 'storyscript', 'VERSION'), 'r',
                   encoding='utf8').read().strip()


def read_version_package():
    resource_package = 'storyscript'
    ver = pkg_resources.resource_string(resource_package, 'VERSION')
    return ver.decode('utf8').strip()


def read_version():
    try:
        return read_version_file()
    except Exception:
        try:
            return read_version_package()
        except Exception:
            return None


# The version is a constant which isn't going to change over the program
# lifetime
_version = read_version()


def get_version():
    # try to read a VERSION file (e.g. for a released storyscript)
    if _version is not None:
        return _version

    # detect a git version (for development builds)
    try:
        return git_describe()
    except Exception:
        pass

    # soft fallback in case everything fails
    return '0.0.0'


def get_release_version():
    # try to read a VERSION file (e.g. for a released storyscript)
    if _version is not None:
        return _version

    # detect a git version (for development builds)
    try:
        return git_version()
    except Exception:
        pass

    # soft fallback in case everything fails
    return '0.0.0'


version = get_version()
release_version = get_release_version()
