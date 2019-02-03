#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import subprocess
from os import path

root_dir = path.abspath(path.dirname(path.dirname(__file__)))


def git_version():
    return subprocess.run(
        ['git', 'describe', '--abbrev=0', '--tags'],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
        cwd=root_dir,
    ).stdout.strip()


def git_describe():
    return subprocess.run(
        ['git', 'describe', '--dirty'],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
        cwd=root_dir,
    ).stdout.strip()


def read_version():
    return io.open(path.join(root_dir, 'storyscript', 'VERSION'), 'r',
                   encoding='utf8').read().strip()


def get_version():
    # try detecting the git version first
    try:
        return git_describe()
    except Exception:
        pass

    # fallback to a VERSION file (e.g. for a released storyscript)
    try:
        return read_version()
    except Exception:
        pass

    # soft fallback in case everything fails
    return '0.0.0'


def get_release_version():
    # try detecting the git version first
    try:
        return git_version()
    except Exception:
        pass

    # fallback to a VERSION file (e.g. for a released storyscript)
    try:
        return read_version()
    except Exception:
        pass

    # soft fallback in case everything fails
    return '0.0.0'


version = get_version()
release_version = get_release_version()
