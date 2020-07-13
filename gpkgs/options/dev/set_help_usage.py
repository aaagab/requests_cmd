#!/usr/bin/env python3
from pprint import pprint
import os 
import sys
import textwrap

from .node import Node

from ..gpkgs import message as msg

def set_help_usage(Options, mode=None): # mode usage|help
    for name, arg in sorted(Options.argsdy.items()):
        set_arg_basic(Options, mode, arg)

    for name, arg in sorted(Options.argsdy.items()):
        set_arg(mode, Options, arg)

def set_arg(mode, Options, arg, increment=None, pnode=None, root_arg=None, nargs_text=[], levels=[]):
    node=None
    if pnode == None:
        node=Node(arg)
    else:
        node=Node(arg, parent=pnode)

    if root_arg is None:
        levels=[]
        root_arg=arg
        nargs_text=[]

    space=""
    space_info=""
    indent=""
    if increment is None:
        increment=1
    else:
        space=" "*2*increment
        space_info=" "*2*(increment+1)

    if arg.dy["show"] is True:
        if arg != root_arg:
            arg_text=arg.dy["basic_"+mode]
            tmp_text=""
            tmp_text="["+arg_text+"]"
            if mode == "help":
                all_text=arg_text.splitlines()
                if len(all_text) > 1:
                    tmp_text="["+all_text[0]+"]"
                    tmp_infos=[]
                    for text in all_text[1:]:
                        tmp_infos.append(text.strip())
                    if tmp_infos:
                        tmp_text+="\n{}".format(get_wrap_text(Options, " ".join(tmp_infos), space_info))

            if pnode.arg.dy["required"] is not None:
                if arg in pnode.arg.dy["required"]:
                    tmp_text=arg_text
                    if mode == "help":
                        all_text=arg_text.splitlines()
                        if len(all_text) > 1:
                            tmp_text=all_text[0]
                            tmp_infos=[]
                            for text in all_text[1:]:
                                tmp_infos.append(text.strip())
                            if tmp_infos:
                                tmp_text+="\n{}".format(get_wrap_text(Options, " ".join(tmp_infos), space_info))

            nargs_text.append("{}{}".format(space, tmp_text))

    if arg.dy["args"] is not None:
        for narg in arg.dy["args"]:
            levels.append(increment)
           
            set_arg(mode, Options, narg, 
                nargs_text=nargs_text,
                increment=increment+1,
                levels=levels,
                pnode=node,
                root_arg=root_arg, 
            )

    if arg == root_arg:
        arg.dy["levels"]=levels
        arg.dy[mode]=arg.dy["basic_"+mode]
        tmp_args_text=""

        if nargs_text:
            tmp_args_text="{}{}".format("\n","\n".join(nargs_text))

        suffix=""
        if arg == Options.root_arg:
            arg.dy[mode]=arg.dy["basic_"+mode]
        else:
            if arg.dy["basic_"+mode][-1] == "]":
                arg.dy[mode]=arg.dy["basic_"+mode][:-1]
                suffix="]"
            else:
                arg.dy[mode]=arg.dy["basic_"+mode]

        arg.dy[mode]+="{}{}".format(tmp_args_text, suffix)
        # print(arg.dy[mode])

def get_wrap_text(Options, text, indent):
    screen_width=Options.dy_app["tty"]["columns"]
    max_width=screen_width-len(indent)

    data=""
    start_index=0
    lines=[]
    for c, char in enumerate(text):
        data+=char
        if len(indent) > (screen_width/2):
            indent=" "*int(screen_width/3)
            max_width=screen_width-len(indent)
            if len(data) == max_width:
                lines.append(get_formatted_text(indent, data))
                data=""
        else:    
            if len(data) == max_width:
                if c < len(text):
                    if text[c+1] == " ":
                        lines.append(get_formatted_text(indent, data))
                        data=""
                    else:
                        if " " in data:
                            index=data.rfind(" ")
                            remain=data[index+1:c+1]
                            data=data[:index]
                            lines.append(get_formatted_text(indent, data))
                            data=remain
                        else:
                            lines.append(get_formatted_text(indent, data))
                            data=""

    if data:
        lines.append(get_formatted_text(indent, data))

    return "\n".join(lines)

def get_formatted_text(indent, text):
    return "{}{}".format(indent, text.strip())

def set_arg_basic(Options, mode, arg):
    aliases=[]
    tmp_text=""
    if mode == "usage":
        for default in [arg.default_short_alias, arg.default_long_alias]:
            if default is not None:
                aliases.append(default)
    elif mode == "help":
        sorted_aliases=sorted(arg.dy["aliases"])
        tmp_long=[]
        for alias in sorted_aliases:
            if alias[:2] == "--":
                tmp_long.append(alias)
            else:
                aliases.append(alias)
        aliases.extend(tmp_long)

    tmp_text=",".join(aliases)
    values=get_values_syntax(arg.dy)
    tmp_text+=values

    if mode == "help":
        if arg.dy["info"] is not None:
            indent=" "*6
            get_wrap_text(Options, arg.dy["info"], indent)
            tmp_text+="\n"+(get_wrap_text(Options, arg.dy["info"], indent))

    arg.dy["basic_"+mode]=tmp_text

def get_values_syntax(opts):
    tmp_txt=""
    if opts["num_max"] != 0:
        if opts["values"] is not None:
            is_required=False
            reached_total=0
            reached_min=0
            for p, param_opt in enumerate(get_array(opts, "values")):
                if p+1 <= opts["num_min"]:
                    tmp_txt+=get_required_syntax(param_opt)
                    reached_min=p+1
                else:
                    tmp_txt+=get_optional_syntax(param_opt)

                reached_total=p+1
                if p+1 == opts["num_max"]:
                    break

            tmp_txt+=complete_values(opts, reached_min, reached_total)
        else:
            tmp_txt+=complete_values(opts)

    return tmp_txt

def complete_values(opts, reached_min=0, reached_total=0):
    tmp_txt=""
    opt_min=opts["num_min"]-reached_min
    if opt_min > 0:
        if opt_min == 1:
            tmp_txt+=get_required_syntax("value")
        else:
            tmp_txt+=get_required_syntax("value({})".format(opt_min))
    
    if opts["num_max"] is None:
        tmp_txt+=get_optional_syntax("...")
    else:
        if opts["num_max"] > 0:
            if opts["num_max"] != opts["num_min"]:
                elems_left=opts["num_max"]-opts["num_min"]
                if reached_total > opts["num_min"]:
                    elems_left=opts["num_max"]-reached_total

                if elems_left > 0:
                    if elems_left == 1:
                        tmp_txt+=get_optional_syntax("value")
                    else:
                        tmp_txt+=get_optional_syntax("value({})".format(elems_left))
    return tmp_txt

def get_optional_syntax(value):
    return " [<{}>]".format(value)

def get_required_syntax(value):
    return " <{}>".format(value)

def get_array(opts, attr):
    if isinstance(opts[attr], str):
        return opts[attr].split(",")
    else:
        return opts[attr]