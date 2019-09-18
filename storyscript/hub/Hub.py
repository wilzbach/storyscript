# -*- coding: utf-8 -*-
from functools import lru_cache

from storyhub.sdk.StoryscriptHub import StoryscriptHub


@lru_cache(maxsize=1)
def _story_hub():
    """
    Cached instance of the hub sdk
    """
    return StoryscriptHub()


def story_hub():
    """
    Returns an instance of StoryscriptHub() from the hub sdk
    """
    return _story_hub()
