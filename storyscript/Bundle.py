# -*- coding: utf-8 -*-
import os
import subprocess

from .Story import Story
from .compiler import Preprocessor
from .parser import Parser


class Bundle:
    """
    Bundles all stories that must be compiled together.
    """

    def __init__(self, story_files={}):
        self.stories = {}
        self.story_files = story_files

    @staticmethod
    def gitignores():
        """
        Get the list of files ignored by git
        """
        command = ['git', 'ls-files', '--others', '--ignored',
                   '--exclude-standard']
        p = subprocess.run(command, stdout=subprocess.PIPE, encoding='utf8')
        if p.returncode != 0:
            return []
        return p.stdout.split('\n')

    @staticmethod
    def ignores(path):
        ignores = []
        if os.path.isdir(path):
            for root, subdirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.story'):
                        story = os.path.relpath(os.path.join(root, file))
                        ignores.append(story)
            return ignores
        return [os.path.relpath(path)]

    @staticmethod
    def filter_path(root, filename, ignores):
        if filename.endswith('.story'):
            path = os.path.relpath(os.path.join(root, filename))
            if path not in ignores:
                return path
        return None

    @classmethod
    def parse_directory(cls, directory, ignored_path=None):
        """
        Parse a directory to find stories.
        """
        paths = []
        ignores = cls.gitignores()
        if ignored_path:
            ignores = ignores + cls.ignores(ignored_path)
        for root, subdirs, files in os.walk(directory):
            for file in files:
                path = cls.filter_path(root, file, ignores)
                if path:
                    paths.append(path)
        return paths

    @classmethod
    def from_path(cls, path, ignored_path=None):
        """
        Load a bundle of stories from the filesystem.
        If a directory is given. all `.story` files in the directory will be
        loaded.
        """
        bundle = Bundle()
        if os.path.isdir(path):
            for story in cls.parse_directory(path, ignored_path=ignored_path):
                bundle.load_story(story)
            return bundle
        bundle.load_story(path)
        return bundle

    def load_story(self, path):
        """
        Reads a story file and adds it to the loaded stories
        """
        if path not in self.story_files:
            self.story_files[path] = Story.read(path)
        return Story(self.story_files[path])

    def find_stories(self):
        """
        Finds bundle stories.
        """
        return list(self.story_files.keys())

    def services(self):
        services = []
        for storypath, story in self.stories.items():
            services += story['services']
        services = list(set(services))
        services.sort()
        return services

    def parser(self, ebnf):
        return Parser(ebnf=ebnf)

    def parse(self, stories, parser):
        """
        Parse stories.
        """
        for storypath in stories:
            story = self.load_story(storypath)
            story.parse(parser=parser)
            self.parse(story.modules(), parser=parser)
            self.stories[storypath] = story.tree

    def compile(self, stories, parser):
        """
        Reads and parses a story, then compiles its modules and finally
        compiles the story itself.
        """
        for storypath in stories:
            story = self.load_story(storypath)
            story.parse(parser=parser)
            self.compile(story.modules(), parser=parser)
            story.compile()
            self.stories[storypath] = story.compiled

    def bundle(self, ebnf=None):
        """
        Makes the bundle
        """
        entrypoint = self.find_stories()
        parser = self.parser(ebnf)
        self.compile(entrypoint, parser=parser)
        return {'stories': self.stories, 'services': self.services(),
                'entrypoint': entrypoint}

    def bundle_trees(self, ebnf=None, preprocess=False):
        """
        Makes a bundle of syntax trees
        """
        parser = self.parser(ebnf)
        self.parse(self.find_stories(), parser=parser)
        if preprocess:
            proc = Preprocessor(parser)
            for story, tree in self.stories.items():
                self.stories[story] = proc.process(tree)
        return self.stories

    def lex(self, ebnf=None):
        """
        Lexes the bundle
        """
        stories = self.find_stories()
        results = {}
        for story in stories:
            results[story] = Story.from_file(story).lex(ebnf=ebnf)
        return results
