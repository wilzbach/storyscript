# -*- coding: utf-8 -*-
import subprocess
from unittest import mock

import pkg_resources

from storyscript import Version


def test_git_version(patch):
    patch.object(subprocess, 'run')
    r = Version.git_version()
    subprocess.run.assert_called_with(
        ['git', 'describe', '--abbrev=0', '--tags'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        check=True,
        cwd=mock.ANY,
    )
    assert r == subprocess.run().stdout.strip()


def test_git_describe(patch):
    patch.object(subprocess, 'run')
    r = Version.git_describe()
    subprocess.run.assert_called_with(
        ['git', 'describe', '--dirty'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        check=True,
        cwd=mock.ANY,
    )
    assert r == subprocess.run().stdout.strip()


def test_read_version(patch):
    patch.object(pkg_resources, 'resource_string')
    Version.read_version.cache_clear()
    r = Version.read_version()
    pkg_resources.resource_string.assert_called_with(
        'storyscript.Version', 'VERSION'
    )
    assert r == pkg_resources.resource_string().decode('utf8').strip()


def test_get_version(patch):
    patch.object(Version, 'read_version')
    assert Version.get_version() == Version.read_version()

    patch.object(Version, 'git_describe')
    Version.read_version.side_effect = Exception('.no.file.found.')
    assert Version.get_version() == Version.git_describe()

    Version.git_describe.side_effect = Exception('.no.file.found.')
    assert Version.get_version() == '0.0.0'


def test_get_release_version(patch):
    patch.object(Version, 'read_version')
    assert Version.get_release_version() == Version.read_version()

    patch.object(Version, 'git_version')
    Version.read_version.side_effect = Exception('.no.file.found.')
    assert Version.get_release_version() == Version.git_version()

    Version.git_version.side_effect = Exception('.no.file.found.')
    assert Version.get_release_version() == '0.0.0'
