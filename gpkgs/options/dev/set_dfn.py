#!/usr/bin/env python3
from copy import deepcopy
from pprint import pprint
import os 
import re
import sys
from types import SimpleNamespace

from .arg import Arg
from .node import Node

from ..gpkgs import message as msg

def set_dfn(Options):
    set_defaults(Options)
    filter_options(Options)

    dy_names={}
    for name, opts in sorted(Options.dy_args.items()):
        arg=Arg(name, opts)
        Options.args_lst.append(arg)
        if name == Options.root_arg_name:
            Options.root_arg=arg
        set_min_max(Options, name)
        set_aliases(Options, name, arg)
        dy_names.update({ name: arg})
        set_args(Options, arg)

    Options.argsns=SimpleNamespace(**dy_names)
    Options.argsdy=dy_names

    for name, arg in sorted(Options.argsdy.items()):
        if arg == Options.root_arg:
            args=sorted([n for n, a  in Options.argsdy.items() if a.dy["nested"] is False])
            args.remove(Options.root_arg.name)
            if arg.dy["args"] is not None:
                arg.dy["args"].extend(args)
                arg.dy["args"].sort()
            else:
                arg.dy["args"]=args

        if arg.dy["required"] is not None:
            if arg.dy["args"] is None:
                msg.error("For arg '{}' 'required' '{}' is not None but 'args' is None .".format(name, arg.dy["required"]), exit=1)

            tmp_required=[]
            for nargname in arg.dy["required"].split(","):
                if nargname not in arg.dy["args"]:
                    msg.error("For arg '{}' required arg '{}' is not in 'args' '{}'.".format(name, nargname, arg.dy["args"]), exit=1)

                if nargname not in Options.argsdy:
                    msg.error("For arg '{}' required arg '{}' not found.".format(name, nargname), exit=1)
                else:
                    tmp_required.append(Options.argsdy[nargname])

            arg.dy["required"]=tmp_required


        check_recursion(Options, arg)
        
    for name, arg in sorted(Options.argsdy.items()):
        set_args_name(Options, arg)

def set_args_name(Options, arg):
    if arg.dy["args"] is not None:
        tmp_args=[]
        for name in arg.dy["args"]:
            narg=Options.argsdy[name]
            tmp_args.append(narg)

        arg.dy["args"]=tmp_args

def check_recursion(Options, arg=None, pnode=None):
    if pnode == None:
        node=Node(arg)
        if Options.args_nodes is None:
            Options.args_nodes={}
        
        Options.args_nodes.update({arg: node})
    else:
        node=Node(arg, parent=pnode)

    if arg.dy["args"] is not None:
        for name in arg.dy["args"]:
            narg=Options.argsdy[name]
            check_recursion(Options, arg=narg, pnode=node)


def set_args(Options, arg):
    if arg.dy["args"] is not None:
        argnames=arg.dy["args"].split(",")
        tmp_args=[]
        for argname in argnames:
            if argname not in Options.dy_args:
                msg.error("For arg '{}' in args option '{}' does not exist.".format(arg.name, argname), exit=1)
            else:
                if Options.dy_args[argname]["nested"] is False:
                    msg.error("For arg '{}' in args option '{}' is not a nested arg.".format(arg.name, argname), exit=1)
            tmp_args.append(argname)

        arg.dy["args"]=tmp_args


def set_defaults(Options):
    if Options.dy_args is None:
        Options.dy_args={}
    
    Options.dy_args.update({
        "help": {
            "aliases": "-h,--help",
            "info": "Show Help and exit."
        },
        "usage": {
            "aliases": "--usage",
            "info": "Show usage."
        },
        "version": {
            "aliases": "-v,--version",
            "info": "Show version."
        }
    })

    if Options.root_arg_name in Options.dy_args:
        if not "info" in Options.dy_args[Options.root_arg_name]:
            Options.dy_args[Options.root_arg_name]["info"]=Options.description
    else:
        Options.dy_args.update({
            Options.root_arg_name:{
                "info": Options.description
        }})

def filter_options(Options):
    Options.defaults=None
    filenpa_defaults=os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "gpm.json")
    dy_app=Options.get_json(filenpa_defaults)
    Options.defaults=dy_app["conf"]
    for name, opts in sorted(Options.dy_args.items()):
        for opt, value in Options.defaults.items():
            if opt not in opts:
                Options.dy_args[name][opt]=value
            else:
                if isinstance(opts[opt], str):
                    if opts[opt].strip() == "":
                        opts[opt]=value

def set_aliases(Options, name, arg):
    opts=Options.dy_args[name]
    if arg == Options.root_arg:
        opts["aliases"]= [Options.exe_name]
    else:
        if opts["aliases"] is None:    
            opts["aliases"]=["--{}".format(name.replace("_", "-"))]
        else:
            if isinstance(opts["aliases"], str):
                opts["aliases"]=opts["aliases"].split(",")
            else:
                msg.error("For arg '{}' alias '{}' syntax error.".format(name, opts["aliases"]), exit=1)

    if arg == Options.root_arg:
        arg.default_long_alias=Options.exe_name
    else:
        has_short=False
        has_long=False
        shortest_alias=opts["aliases"][0]
        for alias in opts["aliases"]:
            if len(alias)< len(shortest_alias):
                shortest_alias=alias
            if alias[:2] == "--":
                if has_long is False:
                    arg.default_long_alias=alias
                    arg.default_alias=alias
                    has_long=True
            else:
                if has_short is False:
                    arg.default_short_alias=alias
                    has_short=True

            if has_short is True and has_long is True:
                break

        if has_short is False:
            if shortest_alias != arg.default_long_alias:
                arg.default_short_alias=shortest_alias

        if has_long is False:
            arg.default_alias=arg.default_short_alias

    for alias in opts["aliases"]:
        if alias in Options.aliases:
            msg.error("for arg '{}' alias '{}' has already been selected for arg '{}'".format(name, alias, Options.aliases[alias].name), exit=1)
        else:
            Options.aliases.update({alias: arg})


def test_int_symbols(symbols, name, opts, value):
    try:
        opts["num_min"]=int(value)
        opts["num_max"]=int(value)
    except:
        if value in ["+", "?", "*"]:
            if value == "+":
                opts["num_min"]=1
                opts["num_max"]=None
            elif value == "?":
                opts["num_min"]=0
                opts["num_max"]=1
            elif value == "*":
                opts["num_min"]=0
                opts["num_max"]=None
        else:
            msg.error("For arg '{}' In nvalues '{}' expected an int or a symbol from '[{}]'".format(name, value, "','".join(symbols)), exit=1)

def test_list(name, opts, values):
    if len(values) == 2:
        tmp_arr_values=[]
        for v, value in enumerate(values):
            try:
                tmp_arr_values.append(int(value))
                if v == 0:
                        opts["num_min"]=int(value)
                elif v == 1:
                    opts["num_max"]=int(value)
                    if opts["num_max"] < opts["num_min"]:
                        msg.error("For arg '{}' In nvalues '{}' num_max '{}' is lesser than num_min '{}'".format(name, opts["nvalues"], opts["num_max"], opts["num_min"]), exit=1)
            except:
                if v == 0:
                    msg.error("For arg '{}' In nvalues '{}' expected an int for first list value got '{}'".format(name, opts["nvalues"], value), exit=1)
                elif v == 1:
                    if value == "*":
                        opts["num_max"]=None                    
                    else:
                        msg.error("For arg '{}' In nvalues '{}' when two values are used the second must be an integer or '*'".format(name, opts["nvalues"]), exit=1)
                tmp_arr_values.append(value)

    else:
        msg.error("For arg '{}' In nvalues '{}' expected max '2' values, got '{}'".format(name, opts["nvalues"], len(values)), exit=1)

def set_min_max(Options, name):
    opts=Options.dy_args[name]
    symbols=["+", "?", "*"]
    if opts["nvalues"] is None:
        if opts["values"] == "":
            opts["values"]=None

        if opts["values"] is not None:
            len_values=len(opts["values"].split(","))
            opts["num_min"]=len_values
            opts["num_max"]=len_values
        else:
            opts["num_min"]=0
            opts["num_max"]=0
    else:
        if isinstance(opts["nvalues"], str):
            if len(opts["nvalues"]) == 0:
                opts["num_min"]=0
                opts["num_max"]=0
                opts["nvalues"]=None                    
            elif len(opts["nvalues"]) == 1:
                test_int_symbols(symbols, name, opts, opts["nvalues"])
            else:
                tmp_nvalues=opts["nvalues"].split(",")
                test_list(name, opts, tmp_nvalues)
        elif isinstance(opts["nvalues"], int):
            opts["num_min"]=opts["nvalues"]
            opts["num_max"]=opts["nvalues"]
        else:
            msg.error("For arg '{}' In nvalues '{}' syntax expected is a 'str' or an 'int'".format(name, opts["nvalues"]), exit=1)

    for attr in ["num_min", "num_max"]:
        if attr not in opts:
            msg.error("Developer miss something '{}' '{}'".format(name, opts["nvalues"]), exit=1, trace=True)
