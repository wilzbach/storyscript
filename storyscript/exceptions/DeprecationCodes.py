# -*- coding: utf-8 -*-


class DeprecationCodes:

    unidentified_deprecation = ('D0001', '')
    no_range = ('D0002', 'Ranges are deprecated.')

    @staticmethod
    def is_deprecation(deprecation_name):
        """
        Checks whether a given deprecation name is a valid deprecation.
        """
        if isinstance(deprecation_name, str):
            if hasattr(DeprecationCodes, deprecation_name):
                return True
            return False
        assert 0, 'Deprecation name should be a string.'

    @staticmethod
    def get_deprecation(deprecation_name):
        """
        Retrieve the deprecation object for a valid deprecation name.
        """
        return getattr(DeprecationCodes, deprecation_name)
