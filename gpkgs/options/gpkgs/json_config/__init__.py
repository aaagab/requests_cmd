#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.0.0
# name: json_config
# license: MIT
__version__ = "2.0.0"

from .dev.json_config import Json_config
__all__ = [
    "Json_config"
]

from .gpkgs import message as msg
