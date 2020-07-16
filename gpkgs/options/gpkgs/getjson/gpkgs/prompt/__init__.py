#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.0.2
# name: prompt
# license: MIT
__version__ = "3.0.2"

from .dev.prompt import prompt, prompt_multiple, prompt_boolean, get_path, pause
__all__ = [
    "prompt",
    "prompt_multiple",
    "prompt_boolean",
    "get_path",
    "pause",
]

from .gpkgs import message as msg
