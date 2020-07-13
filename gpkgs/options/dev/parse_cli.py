#!/usr/bin/env python3
from pprint import pprint
import re
import os
import sys

from ..gpkgs import message as msg

def parse_cli(Options):
    Options.current_arg=Options.aliases[Options.exe_name]
    Options.current_arg.here=True
    Options.current_arg.alias=Options.exe_name
    
    for elem in sys.argv[1:]:
        if elem == "?":
            Options.help_pointer=Options.current_arg
        elif elem == "??":
            Options.help_pointer_verbose=Options.current_arg
        elif re.match(r"-.+", elem) or re.match(r"--.+", elem):
            if not elem in Options.aliases:
                msg.error("Unknown alias '{}'".format(elem), exit=1)
            Options.current_arg=Options.aliases[elem]
            Options.current_arg.here=True
            Options.current_arg.alias=elem
        else:
            if Options.cli_expand is True:
                elem=re.sub(r"__([a-zA-Z][a-zA-Z0-9]*)__", lambda m: get_env_var(m), elem)
            Options.current_arg.values.append(elem)
            if Options.current_arg.value is None:
                Options.current_arg.value=Options.current_arg.values[0]

def get_env_var(reg):
    key=next(iter(reg.groups()))
    if key in os.environ:
        value=os.environ[key].strip()
        return re.sub(r"^\"?(.*?)\"?$", r"\1", value)
    else:
        return reg.group()

