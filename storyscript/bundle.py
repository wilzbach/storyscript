# -*- coding: utf-8 -*-
import os

from .story import Story


class Bundle:
    """
    Bundles all stories that must be compiled together.
    """

    def __init__(self, path):
        self.path = path

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

    def bundle(self, ebnf_file=None, debug=False):
        """
        Makes the bundle
        """
        self.stories = {}
        for storypath in self.find_stories():
            story = Story.from_file(storypath)
            self.stories[storypath] = story.process(ebnf_file=ebnf_file,
                                                    debug=debug)
        return {'stories': self.stories, 'services': self.services()}
