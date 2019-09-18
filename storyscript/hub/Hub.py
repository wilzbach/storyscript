# -*- coding: utf-8 -*-
from functools import lru_cache

from storyhub.sdk.StoryscriptHub import StoryscriptHub


@lru_cache(maxsize=1)
def story_hub():
    """
    Returns a cached instance of StoryscriptHub() from the hub sdk.
    """
    return StoryscriptHub()
