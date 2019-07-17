# -*- coding: utf-8 -*-
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from .Api import Api
from .Version import version


__version__ = version = version


loads = Api.loads
load = Api.load
load_map = Api.load_map
