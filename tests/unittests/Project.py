# -*- coding: utf-8 -*-
import io
import os

from storyscript.Project import Project


def test_project_readme(patch):
    patch.object(io, "open")
    Project.readme("app")
    io.open.assert_called_with("app/README.md", "w")
    assert io.open().__enter__().write.call_count == 1


def test_project_app(patch):
    patch.object(io, "open")
    Project.app("app")
    io.open.assert_called_with("app/src/app.story", "w")
    assert io.open().__enter__().write.call_count == 1


def test_project_new(patch):
    patch.object(os.path, "exists")
    patch.many(Project, ["readme", "app"])
    Project.new("app")
    Project.readme.assert_called_with("app")
    Project.app.assert_called_with("app")


def test_project_new_makedir(patch):
    patch.object(os.path, "exists", return_value=False)
    patch.object(os, "makedirs")
    patch.many(Project, ["readme", "app"])
    Project.new("app")
    os.makedirs.assert_called_with("app/src")
