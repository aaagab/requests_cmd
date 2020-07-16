#!/usr/bin/env python3
from getpass import getpass
import platform
import os
import shlex
import sys
import subprocess

from ..gpkgs import message as msg

pfm=platform.system()


if pfm == "Linux":
    import readline

def prompt(txt,
    clear_error=False,
    default=None,
    exclude=[],
    indent=" "*2,
    hidden=False,
):
    if not isinstance(exclude, list):
        msg.error("exclude must be a list", exit=1, trace=True)

    tmp_var=""
    input_text=""
    if exclude:
        input_text="{}Input Excluded: '{}'.\n".format(indent, ", ".join(exclude))
    input_text+="{}{} [q to quit]".format(indent, txt )
    if default is not None:
        if default == "":
            input_text+="(\"\")".format(default)
        else:
            input_text+="({})".format(default)

    input_text+=": "
    while not tmp_var:
        if hidden is True:
            tmp_var = getpass(input_text)
        else:
            tmp_var = input(input_text)
        if tmp_var.lower() == "q":
            sys.exit(1)

        if not tmp_var:
            if default is not None:
                return default
            
        tmp_var=tmp_var.strip()
        if exclude:
            if tmp_var in exclude:
                msg.warning("'{}' belongs to exclude list '{}'".format(tmp_var, exclude))
                tmp_var=""
                pause(clear_error, indent)

    return tmp_var.strip()

def prompt_multiple(
    names,
    add_none=False,
    allow_duplicates=False,
    bullet=" - ",
    clear_error=False,
    clear_start=False,
    default=None, 
    indent=" "*4, 
    index_only=False,
    return_list=False, 
    show_item_info=True,
    show_numbers=True, 
    sort=True, 
    title=None,
    values=[],
):
    if not isinstance(names, list):
        msg.error("names is not a list", exit=1, trace=True)

    if not isinstance(values, list):
        msg.error("values is not a list", exit=1, trace=True)

    if not values:
        values=names
    else:
        if len(values) != len(names):
            msg.error("len values '{}' must be equals to len names '{}'".format(len(values), len(names)),exit=1, trace=True)

    if clear_start is True:
         msg.ft.clear_screen()

    tmp_names=[]
    for name in names:
        if name.lower() == "q":
            msg.error("'{}' is a reserved char for quit".format(name), exit=1, trace=True)
        
        if add_none is True:
            if name.lower() == "none":
                msg.error("'{}' is a reserved keyword to return None".format(name), exit=1, trace=True)

        if name not in tmp_names:
            tmp_names.append(name)
        else:
            msg.error("item '{}' has already been selected".format(name),exit=1, trace=True)

    number=""
    items_text=""
    if index_only is True:
        show_numbers=True

    for i ,name in enumerate(names):
        if show_numbers is True:
            number=i+1
        items_text+="{}{}{}{}\n".format(indent, number, bullet, name)

    if clear_error is False:
        items_text="\n"+items_text
        print(items_text)

    user_input=None
    choices=[]

    item_info="{}{}".format(indent, "Choose item with its")

    if index_only is True:
        item_info+=" index."
    else:
        if show_numbers is True:
            item_info+=" name or index."
        else:
            item_info+=" name."

    if return_list is True or return_list is None:
        text="{}{}".format(indent, "Split choices with a comma.")
        if sort is False:
            text+=" Order matters."
        
        if allow_duplicates is True:
            text+=" Duplicates allowed."

        item_info+="\n{}".format(text)
 
    input_text=""
    if title is not None:
        input_text="{}{}".format(indent, title)
    else:
        input_text="{}select entry".format(indent)
 
    if add_none is True:
        input_text+=" or type 'None'"

    input_text+=" [q to quit]."

    if default is not None:
        input_text+="\n{}Default({}).".format(indent, default)

    input_text+="\n{}input: ".format(indent)

    if show_item_info is True:
        input_text="{}\n{}".format(item_info,input_text)

    while not user_input:
        if clear_error is True:
            print(items_text)

        user_input = input(input_text)

        if user_input.lower() == "q":
            sys.exit(1)

        if not user_input:
            if default is not None:
                user_input=default

        if user_input.lower() == "none":
            return None

        user_input=user_input.split(",")
        if isinstance(user_input, list):
            tmp_input=[]
            for inp in user_input:
                inp=inp.strip()
                if inp:
                    if allow_duplicates is False:
                        if inp in tmp_input:
                            continue
                    tmp_input.append(inp)
            user_input=tmp_input
        else:
            user_input=[user_input.strip()]

        if not user_input:
            continue

        for inp in user_input:
            is_digit=False
            if inp.isdigit():
                is_digit=True

            found=False
            if index_only is True:
                if is_digit is False:
                    msg.warning("Input '{}' must be an index from 1 to '{}'.".format(inp, len(names)))
                    user_input=[]
                    pause(clear_error, indent)
                    continue
                else:
                    inp=int(inp)
                    if inp in range(1, len(names)+1):
                        choices.append(values[inp-1])
                        found=True
            else:
                if inp in names:
                    choices.append(values[names.index(inp)])
                    found=True
                elif is_digit is True:
                    inp=int(inp)
                    if inp in range(1, len(names)+1):
                        choices.append(values[inp-1])
                        found=True

            if found is False:
                msg.warning("'{}' choice is not a valid choice.".format(inp))
                user_input=[]
                pause(clear_error, indent)

    if return_list is None:
        if len(choices) == 1:
            return choices[0]
        elif len(choices) > 1:
            if sort is True:
                return sorted(choices)
            else:
                return choices
    elif return_list is False:
        return choices[0]
    elif return_list is True:
        if sort is True:
            return sorted(choices)
        else:
            return choices

def pause(clear_error=False, indent=" "*2):
    if pfm == "Linux":
        os.system("bash -c 'read -sn 1 -p \"Press any key to continue...\"'")
        print()
    elif pfm == "Windows":
        os.system("pause")
    if clear_error is True:
        msg.ft.clear_screen()

def prompt_boolean(txt, Y_N="y"):
    tmp_var=""
    while not tmp_var:
        if Y_N.lower() == "y":
            tmp_var = input("  "+txt +" [Ynq]? ")
            if tmp_var.lower() == "":
                return True
        elif Y_N.lower() == "n":
            tmp_var = input("  "+txt +" [yNq]? ")
            if tmp_var.lower() == "":
                return False
        else:
            msg.error("Wrong Value for prompt_boolean: "+Y_N )
            sys.exit(1)

        if tmp_var.lower() == "q":
            sys.exit(1)
        elif tmp_var.lower() == "y":
            return True
        elif tmp_var.lower() == "n":
            return False

def get_path(txt, allow_empty=False):
    if pfm == "Linux":
        txt="  "+txt +" [q]: "
        path=""
        while not path:
            path=subprocess.check_output(shlex.split("bash -c 'read -e -p \"{}\" text; echo \"$text\"'".format(txt))).decode("utf-8").rstrip()

            if path.lower() == "q":
                sys.exit(1)
            if allow_empty:
                if not path:
                    return ""

        return path
    else:
        msg.error("prompt get_path not supported on platform '{}'".format(pfm), exit=1, trace=True)
    