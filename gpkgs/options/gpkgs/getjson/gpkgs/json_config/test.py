#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.0.0
# name: json_config
# license: MIT

import importlib
import os
from pprint import pprint
import sys

direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, direpa_script_parent)
pkg = importlib.import_module(module_name)
del sys.path[0]

pprint(pkg.Json_config(
    os.path.join(
        "config",
        "config.json"    
)).data)
print()
pprint(pkg.Json_config(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "config",
        "config.json"    
)).data)
