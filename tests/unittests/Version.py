# -*- coding: utf-8 -*-
import io
import subprocess
from unittest import mock

from storyscript import Version


def test_git_version(patch):
    patch.object(subprocess, 'run')
    r = Version.git_version()
    subprocess.run.assert_called_with(
        ['git', 'describe', '--abbrev=0', '--tags'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
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
        text=True,
        check=True,
        cwd=mock.ANY,
    )
    assert r == subprocess.run().stdout.strip()


def test_read_version(patch):
    patch.object(io, 'open')
    Version.read_version.cache_clear()
    r = Version.read_version()
    io.open.assert_called_with(
        mock.ANY,
        'r',
        encoding='utf8'
    )
    assert io.open.call_args[0][0].endswith('VERSION')
    assert r == io.open().read().strip()


def test_get_version(patch):
    patch.object(Version, 'git_describe')
    assert Version.get_version() == Version.git_describe()

    patch.object(Version, 'read_version')
    Version.git_describe.side_effect = Exception('.no.file.found.')
    assert Version.get_version() == Version.read_version()

    Version.read_version.side_effect = Exception('.no.file.found.')
    assert Version.get_version() == '0.0.0'


def test_get_release_version(patch):
    patch.object(Version, 'git_version')
    assert Version.get_release_version() == Version.git_version()

    patch.object(Version, 'read_version')
    Version.git_version.side_effect = Exception('.no.file.found.')
    assert Version.get_release_version() == Version.read_version()

    Version.read_version.side_effect = Exception('.no.file.found.')
    assert Version.get_release_version() == '0.0.0'
