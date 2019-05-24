# -*- coding: utf-8 -*-


class Features:
    """
    Configuration for compiler settings or features.
    """

    defaults = {
        'globals': False,  # makes global variables writable
        'debug': False,    # enable debug output
    }

    def __init__(self, features):
        self.features = self.defaults.copy()
        if features is not None:
            for k, v in features.items():
                assert k in self.defaults, f'{k} is in invalid feature option'
                self.features[k] = v

    def __str__(self):
        features = ','.join([f'{k}={v}' for k, v in self.features.items()])
        return f'Features({features})'

    def __getattr__(self, attribute):
        return self.features[attribute]

    @classmethod
    def all_feature_names(cls):
        return cls.defaults.keys()
