#!/usr/bin/env python3
from pprint import pprint
import os 
import sys

from .set_help_usage import set_help_usage

from ..gpkgs import message as msg

def set_args(Options):
    if Options.help_pointer is not None:
        set_help_usage(Options, "usage")
        arg=Options.help_pointer
        print(arg.dy["usage"])
        sys.exit(0)
    elif Options.help_pointer_verbose is not None:
        set_help_usage(Options, "help")
        arg=Options.help_pointer_verbose
        print(arg.dy["help"])
        sys.exit(0)
    elif not sys.argv[1:]:
        if Options.allow_empty == False:
            print_usage(Options)
            sys.exit(1)
    elif Options.argsns.help.here:
        print_full_help(Options)
        sys.exit(0)
    elif Options.argsns.usage.here:
        print_usage(Options)
        sys.exit(0)
    elif Options.argsns.version.here is True:
        if Options.version is None:
            print("0.0.0")
        else:
            print(Options.version)
        sys.exit(0)

    cli_args=[arg for arg in Options.args_lst if arg.here is True]

    for arg in cli_args:
        if arg.here is True:
            check_values(Options, arg)
            check_required(Options, arg)

    for narg in [arg for arg in cli_args if arg.dy["nested"] is True]:
        parent_found=False
        for rarg in [arg for arg in cli_args if arg.dy["args"] is not None]:
            if narg in rarg.dy["args"]:
                parent_found=True
                break

        if parent_found is False:
            msg.error("'{}' should be used as a nested arg but it does not belong to any other arg".format(narg.alias), exit=1)
            
    for name, arg in sorted(Options.argsdy.items()):
        Options.dy.update({
            name: arg.__dict__
        })

    if "args" not in Options.dy_app:
        Options.dy_app["args"]=Options.argsdy

def check_required(Options, arg):
    if arg.dy["required"] is not None:
        for narg in arg.dy["required"]:
            if narg.here is False:
                msg.error("For arg '{}' required nested arg '{}' is not present.".format(arg.alias, narg.default_alias), exit=1)

def check_values(Options, arg):
    num_min=arg.dy["num_min"]
    num_max=arg.dy["num_max"]
    len_values=len(arg.values)
    error=False
    if len_values == 0:
        if num_min > 0:
            msg.error("For arg '{}' expected '{}' value(s) got 'None'".format(arg.alias, num_min))
            error=True
    else:
        if len_values < num_min:
            msg.error("For arg '{}' expected '{}' value(s) minimum got '{}'".format(arg.alias, num_min, len_values))
            error=True

        if num_max is not None:
            if len_values > num_max:
                msg.error("For arg '{}' expected '{}' value(s) maximum got '{}'".format(arg.alias, num_max, len_values))
                error=True

    if error is True:
        set_help_usage(Options, "usage")
        print(arg.dy["usage"])
        sys.exit(1)

def print_usage(Options):
    set_help_usage(Options, "usage")
    print("Usage: \n  {}".format(Options.root_arg.dy["usage"]))

def print_help(Options):
    set_help_usage(Options, "help")
    print("Documentation: \n  {}".format(Options.root_arg.dy["help"]))

def print_full_help(Options):

    print("Name: {}".format(Options.appname))
    if Options.authors is not None:
        print("Author(s): {}".format(Options.authors))
    if Options.licenses is not None:
        print("License(s): {}".format(Options.licenses))
    if Options.description is not None:
        print("Description: {}".format(Options.description))
    if Options.version is not None:
        print("Version: {}".format(Options.version))
    print()
    print_usage(Options)
    print()
    print_help(Options)            