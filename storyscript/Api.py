# -*- coding: utf-8 -*-
from .Bundle import Bundle
from .Features import Features
from .Story import Story
from .exceptions import StoryError


class StoryscriptCompilationResult:
    """
    Result of a Storyscript compilation.
    Contains the compiled story or a list of compilation errors.
    """

    def __init__(self, result, errors, deprecations):
        self._result = result
        self._errors = errors
        self._deprecations = deprecations
        self._warnings = []

    @classmethod
    def from_result(cls, story, deprecations):
        """
        Creates a CompilationResult from a result.
        """
        return cls(story, errors=[], deprecations=deprecations)

    @classmethod
    def from_error(cls, error):
        """
        Creates a CompilationResult from a single error.
        """
        return cls(None, errors=[error], deprecations=[])

    def result(self):
        """
        Returns the compiled story.
        """
        return self._result

    def errors(self):
        """
        Returns a list of all errorsemitted by the Storyscript compiler.
        """
        return self._errors

    def warnings(self):
        """
        Returns a list of all warnings emitted by the Storyscript compiler.
        """
        return self._warnings

    def deprecations(self):
        """
        Returns a list of all deprecations emitted by the Storyscript compiler.
        """
        return self._deprecations

    def success(self):
        """
        Returns `True` if the compilation succeeded.
        """
        return self._result is not None

    def check_success(self):
        """
        Throws the first error encountered if the compilation did not succeed.
        """
        if len(self._errors) > 0:
            raise self._errors[0]


class Api:
    """
    Exposes functionalities for external use
    """

    @staticmethod
    def loads(string, features=None, backend="json", scope=None, hub=None):
        """
        Load story from a string.
        """
        features = Features(features)
        try:
            story = Story(
                string, features, backend=backend, scope=scope, hub=hub
            )
            s = story.process()
            deprecations = story.deprecations()
            return StoryscriptCompilationResult.from_result(s, deprecations)
        except StoryError as e:
            return StoryscriptCompilationResult.from_error(e)
        except Exception as e:
            if features.debug:
                raise e
            else:
                e = StoryError.internal_error(e)
                return StoryscriptCompilationResult.from_error(e)

    @staticmethod
    def load(stream, features=None):
        """
        Load story from a file stream.
        """
        features = Features(features)
        try:
            story = Story.from_stream(stream, features).process()
            s = {stream.name: story, "services": story["services"]}
            deprecations = {stream.name: story.deprecations()}
            return StoryscriptCompilationResult.from_result(s, deprecations)
        except StoryError as e:
            return StoryscriptCompilationResult.from_error(e)
        except Exception as e:
            if features.debug:
                raise e
            else:
                e = StoryError.internal_error(e)
                return StoryscriptCompilationResult.from_error(e)

    @staticmethod
    def load_map(files, features=None):
        """
        Load multiple stories from a file mapping
        """
        features = Features(features)
        try:
            compiledbundle = Bundle(
                story_files=files, features=features
            ).bundle()
            return StoryscriptCompilationResult.from_result(
                compiledbundle.results, compiledbundle.deprecations
            )
        except StoryError as e:
            return StoryscriptCompilationResult.from_error(e)
        except Exception as e:
            if features.debug:
                raise e
            else:
                e = StoryError.internal_error(e)
                return StoryscriptCompilationResult.from_error(e)
