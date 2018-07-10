# -*- coding: utf-8 -*-
import json
import os

from .compiler import Compiler
from .parser import Grammar, Parser
from .story import Story


class App:

    @staticmethod
    def read_story(storypath):
        """
        Reads a story
        """
        try:
            with open(storypath, 'r') as file:
                return file.read()
        except FileNotFoundError:
            abspath = os.path.abspath(storypath)
            print('File "{}" not found at {}'.format(storypath, abspath))
            exit()

    @staticmethod
    def get_stories(storypath):
        """
        Gets stories from a path
        """
        stories = []
        if os.path.isdir(storypath):
            for root, subdirs, files in os.walk(storypath):
                for file in files:
                    if file.endswith('.story'):
                        stories.append(os.path.join(root, file))
            return stories
        return [storypath]

    @staticmethod
    def services(stories):
        """
        Builds a global list of services from each story's services
        """
        services = []
        for storypath, story in stories.items():
            services += story['services']
        services = list(set(services))
        services.sort()
        return services

    @classmethod
    def compile(cls, path, ebnf_file=None, debug=False):
        """
        Parse and compile stories in path to JSON
        """
        compiled_stories = {}
        kwargs = {'ebnf_file': ebnf_file, 'debug': debug}
        for file in cls.get_stories(path):
            story = Story.from_file(file)
            compiled_stories[file] = story.process(**kwargs)
        services = cls.services(compiled_stories)
        dictionary = {'stories': compiled_stories, 'services': services}
        return json.dumps(dictionary, indent=2)

    @classmethod
    def lex(cls, path):
        """
        Lex stories, producing the list of used tokens
        """
        stories = cls.get_stories(path)
        results = {}
        for story in stories:
            results[story] = Story.from_file(story).lex()
        return results

    @staticmethod
    def grammar():
        """
        Returns the current grammar
        """
        return Grammar().build()

    @staticmethod
    def loads(string):
        return Story(string).process()

    @classmethod
    def load(cls, stream):
        dictionary = {stream.name: cls.loads(stream.read())}
        services = cls.services(dictionary)
        dictionary['services'] = services
        return dictionary
