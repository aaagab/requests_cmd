#!/usr/bin/env python3
from pprint import pprint
import ast
import json
import os
import re
import sys
import traceback

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt

def parse_dy(dy, keys=[], root=True):
    for key in sorted(dy):
        value=dy[key]
        if isinstance(value, dict):
            parse_dy(dy[key], keys=keys, root=False)
        else:
            if value == "__hidden__":
                dy[key]=prompt(key, hidden=True)
            elif value == "__input__":
                res=prompt(key, default="")
                if res == "null":
                    res=None
                dy[key]=res
            elif key in keys:
                dy[key]=keys[key]
    if root is True:
        return dy

def getjson(value, 
    error_msg=None,
    error_exit=True,
    keys=dict(),
    parse=True,
):
    dy=dict()
    failed=False
    errors=[]
    if isinstance(value, dict):
        dy=value
    elif re.match(r"^.*\.json$", value):
        try:
            if not os.path.isabs(value):
                value=os.path.abspath(value)
            value=os.path.normpath(value)
            dy=Json_config(value).data
        except BaseException as e:
            failed=True
            errors.append(e)
    else:
        try:
            dy=json.loads(value)
            if type(dy) is not dict:
                raise Exception("{} is not a dict".format(dy))
        except BaseException as e:
            errors.append(e)
            try:
                ### for json string with single quotes
                syntax=dict(true=True, false=False, null=None)
                for old, new in syntax.items():
                    value = re.sub(r"(:)(\s?){}".format(old), r"\1\2{}".format(new), value)
                dy=ast.literal_eval(value)
                if type(dy) is not dict:
                    raise Exception("{} is not a dict".format(dy))
            except BaseException as e:
                failed=True
                errors.append(e)

    if failed is True:
        if error_msg is not None:
            msg.error(error_msg)

        if error_exit is True:
            msg.error("Error when trying to load json from '{}'.".format(value), trace=True)
            print(traceback.format_exc())
            for error in errors:
                print(error)
            sys.exit(1)
        else:
            return None
    else:
        if parse is True:
            parse_dy(dy, keys=keys)
        return dy