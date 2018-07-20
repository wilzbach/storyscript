# -*- coding: utf-8 -*-
import os

from .story import Story


class Bundle:
    """
    Bundles all stories that must be compiled together.
    """

    def __init__(self, path):
        self.path = path
        self.stories = {}

    def find_stories(self):
        """
        Finds bundle stories.
        """
        stories = []
        if os.path.isdir(self.path):
            for root, subdirs, files in os.walk(self.path):
                for file in files:
                    if file.endswith('.story'):
                        stories.append(os.path.join(root, file))
            return stories
        return [self.path]

    def services(self):
        services = []
        for storypath, story in self.stories.items():
            services += story['services']
        services = list(set(services))
        services.sort()
        return services

    def compile_modules(self, stories, ebnf_file, debug):
        self.compile(stories, ebnf_file, debug)

    def compile(self, stories, ebnf_file, debug):
        """
        Reads and parses a story, then compiles its modules and finally
        compiles the story itself.
        """
        for storypath in stories:
            story = Story.from_file(storypath)
            story.parse(ebnf_file=ebnf_file, debug=debug)
            self.compile_modules(story.modules(), ebnf_file, debug)
            story.compile(debug=debug)
            self.stories[storypath] = story.compiled

    def bundle(self, ebnf_file=None, debug=False):
        """
        Makes the bundle
        """
        self.compile(self.find_stories(), ebnf_file, debug)
        return {'stories': self.stories, 'services': self.services()}
