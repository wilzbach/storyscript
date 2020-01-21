# -*- coding: utf-8 -*-
import pkg_resources


def get_version():
    try:
        return pkg_resources.get_distribution("storyscript").version
    except pkg_resources.DistributionNotFound:
        return "0.0.0"


version = get_version()
