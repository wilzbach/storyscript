# -*- coding: utf-8 -*-
import os

import delegator

from .Story import Story


class Bundle:
    """
    Bundles all stories that must be compiled together.
    """

    def __init__(self, path, ignored_path=None):
        self.path = path
        self.stories = {}
        self.ignored_path = ignored_path

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

        return self.filter_paths(paths)

    def compare_paths(self, path, ignored_path):
         """
          Compare path and ignored_path
         """
         return path[:len(ignored_path)] == ignored_path

    def filter_paths(self, paths):
        """
         Filter paths from ignored_path
        """
        if self.ignored_path is None:
            return paths
        paths = [path for path in paths if not self.compare_paths(path, self.ignored_path)]
        return paths

    def find_stories(self):
        """
        Finds bundle stories.
        """
        if os.path.isdir(self.path):
            return self.parse_directory(self.path)
        return [self.path]

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
            story = Story.from_file(storypath)
            story.parse(ebnf=ebnf, debug=debug)
            self.parse_modules(story.modules(), ebnf, debug)
            self.stories[storypath] = story.tree

    def compile(self, stories, ebnf, debug):
        """
        Reads and parses a story, then compiles its modules and finally
        compiles the story itself.
        """
        for storypath in stories:
            story = Story.from_file(storypath)
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
