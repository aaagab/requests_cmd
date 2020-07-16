#!/usr/bin/env python3
import ast
from pprint import pprint
import re
import os
import sys

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.getjson import getjson
from ..gpkgs.prompt import prompt
from ..gpkgs.getpath import getpath

def parse_cli(Options):
    Options.current_arg=Options.aliases[Options.exe_name]
    Options.current_arg.here=True
    Options.current_arg.alias=Options.exe_name
    
    for elem in sys.argv[1:]:
        if elem == "?":
            Options.help_pointer=Options.current_arg
        elif elem == "??":
            Options.help_pointer_verbose=Options.current_arg
        elif re.match(r"-[a-zA-Z].*", elem) or re.match(r"--[a-zA-Z].*", elem):
            if not elem in Options.aliases:
                msg.error("Unknown alias '{}'".format(elem), exit=1)
            Options.current_arg=Options.aliases[elem]
            Options.current_arg.here=True
            Options.current_arg.alias=elem
        else:
            if Options.cli_expand is True:
                elem=re.sub(r"__([a-zA-Z][a-zA-Z0-9]*)__", lambda m: get_env_var(m), elem)

            arg_type=Options.current_arg.dy["type"]
            error_msg="For arg '{}' value '{}' is not of type '{}'".format(Options.current_arg.name, elem, arg_type)
            if arg_type in ["int", "float", "bool"]:
                try:
                    if arg_type == "int":
                        elem=int(elem)
                    elif arg_type == "float":
                        elem=float(elem)
                    elif arg_type == "bool":
                        try:
                            tmp_value=float(elem)
                            if tmp_value == 0:
                                elem=True
                            else:
                                elem=False
                        except:
                            if elem.lower() == "true":
                                elem=True
                            elif elem.lower() == "false":
                                elem=False
                            else:
                                raise Exception()
                except BaseException as e:
                    msg.error(error_msg)
                    sys.exit(1)
            elif arg_type == "json":
                elem=getjson(elem, error_msg)
            elif arg_type in  [ "realpath", "virtualpath", "file", "directory"]:
                elem=getpath(elem, arg_type)

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
