# -*- coding: utf-8 -*-
import os

import delegator

from .Story import Story


class Bundle:
    """
    Bundles all stories that must be compiled together.
    """

    def __init__(self, story_files={}):
        self.stories = {}
        self.story_files = story_files

    def gitignores(self):
        """
        Get the list of files ignored by git
        """
        command = 'git ls-files --others --ignored --exclude-standard'
        return delegator.run(command).out.split('\n')

    def parse_directory(self, directory):
        """
        Parse a directory to find stories.
        """
        paths = []
        ignores = self.gitignores()
        for root, subdirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.story'):
                    path = os.path.join(root, file)
                    if path[2:] not in ignores:
                        paths.append(path)
        return paths

    @classmethod
    def from_path(cls, path):
        """
        Load a bundle of stories from the filesystem.
        If a directory is given. all `.story` files in the directory will be
        loaded.

        Arguments:
            path -- path to file or directory to load stories from
        """
        bundle = Bundle()
        for e in cls._from_path(path):
            bundle.load_story(e)
        return bundle

    @classmethod
    def _from_path(cls, path):
        if os.path.isdir(path):
            return cls.parse_directory(path)
        return [path]

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

    def compile_modules(self, stories, ebnf, debug):
        self.compile(stories, ebnf, debug)

    def parse_modules(self, stories, ebnf, debug):
        self.parse(stories, ebnf, debug)

    def parse(self, stories, ebnf, debug):
        """
        Parse stories.
        """
        for storypath in stories:
            story = self.load_story(storypath)
            story.parse(ebnf=ebnf, debug=debug)
            self.parse_modules(story.modules(), ebnf, debug)
            self.stories[storypath] = story.tree

    def compile(self, stories, ebnf, debug):
        """
        Reads and parses a story, then compiles its modules and finally
        compiles the story itself.
        """
        for storypath in stories:
            story = self.load_story(storypath)
            story.parse(ebnf=ebnf, debug=debug)
            self.compile_modules(story.modules(), ebnf, debug)
            story.compile(debug=debug)
            self.stories[storypath] = story.compiled

    def bundle(self, ebnf=None, debug=False):
        """
        Makes the bundle
        """
        entrypoint = self.find_stories()
        self.compile(entrypoint, ebnf, debug)
        return {'stories': self.stories, 'services': self.services(),
                'entrypoint': entrypoint}

    def bundle_trees(self, ebnf=None, debug=None):
        """
        Makes a bundle of syntax trees
        """
        self.parse(self.find_stories(), ebnf, debug)
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
