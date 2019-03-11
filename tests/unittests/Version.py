# -*- coding: utf-8 -*-
import io
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
        ['git', 'describe', '--dirty', '--tags'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        check=True,
        cwd=mock.ANY,
    )
    assert r == subprocess.run().stdout.strip()


def test_read_version_file(patch):
    patch.object(io, 'open')
    r = Version.read_version()
    io.open.assert_called_with(
        mock.ANY,
        'r',
        encoding='utf8'
    )
    assert io.open.call_args[0][0].endswith('VERSION')
    assert r == io.open().read().strip()


def test_read_version_package(patch):
    patch.object(pkg_resources, 'resource_string')
    r = Version.read_version()
    pkg_resources.resource_string.assert_called_with(
        'storyscript', 'VERSION'
    )
    assert r == pkg_resources.resource_string().decode('utf8').strip()


def test_read_version(patch):
    patch.object(Version, 'read_version_file')
    patch.object(Version, 'read_version_package')
    assert Version.read_version() == Version.read_version_file()

    Version.read_version_file.side_effect = Exception('.no.file.found.')
    assert Version.read_version() == Version.read_version_package()

    Version.read_version_package.side_effect = Exception('.no.file.found.')
    assert Version.read_version() is None


def test_get_version(patch):
    patch.object(Version, '_version')
    assert Version.get_version() == Version._version

    patch.object(Version, 'git_describe')
    Version._version = None
    assert Version.get_version() == Version.git_describe()

    Version.git_describe.side_effect = Exception('.no.file.found.')
    assert Version.get_version() == '0.0.0'


def test_get_release_version(patch):
    patch.object(Version, '_version')
    assert Version.get_release_version() == Version._version

    patch.object(Version, 'git_version')
    Version._version = None
    assert Version.get_release_version() == Version.git_version()

    Version.git_version.side_effect = Exception('.no.file.found.')
    assert Version.get_release_version() == '0.0.0'
