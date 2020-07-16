#!/usr/bin/env python3
import inspect
import logging
import os
import platform
from pprint import pprint
import re
import sys
import traceback

from ..gpkgs.format_text import ft

if platform.system() == "Windows":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

opts=dict(
    bullet=None, # to disable bullet, use bullet=""
    debug=False,
    exit=None,
    format=True,
    heredoc=False,
    indent="  ",
    keys=[],
    style=True,
    trace=False,
    width="auto",  # auto, int, None
)

def error(*msgs, **options ):
    print_message("error", *msgs, **options)
        
def success(*msgs, **options):
    print_message("success", *msgs, **options)

def warning(*msgs, **options):
    print_message("warning", *msgs, **options)

def info(*msgs, **options):
    print_message("info", *msgs, **options)

def print_message(log_type, *msgs, **options):
    display_msg=False
    if "debug" in options:
        if options["debug"] is True:
            display_msg=True
    else:
        display_msg=True

    if display_msg is True:
        if platform.system() == "Windows":
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        for key in opts:
            if key not in options:
                options.update({key:opts[key]})

        tmp_msgs=[]
        for msg in msgs:
            if isinstance(msg, list):
                for m in msg:
                    tmp_msgs.append(m)
            else:
                tmp_msgs.append(msg)

        if not tmp_msgs:
            tmp_msgs.append("")

        indent=None 
        if options["indent"] is None:
            indent="  "
            indent=""
        else:
            indent=options["indent"]

        bullet=None
        if options["bullet"] is None:
            bullet=log_type
        else:
            bullet=options["bullet"]

        all_msgs=[]
        if options["heredoc"] is True:
            heredoc_indent=None
            if tmp_msgs:
                lines=tmp_msgs[0].splitlines()
                firstLineText=False

                after_bullet=None
                if bullet in ft.get_bullets():
                    after_bullet=" "
                else:
                    words_info=ft.get_style_formatted_words([bullet])
                    after_bullet=" "*len(words_info[0]["word"])

                for l, line in enumerate(lines[1:-1]):
                    if l == 0:
                        heredoc_indent=get_heredoc_indent(line)
                    else:
                        bullet=after_bullet

                    tmp_text=None
                    if not line.strip():
                        tmp_text=""
                    else:
                        tmp_text=get_text_without_indent(line, heredoc_indent)

                    if log_type == "error":
                        tmp_text=re.sub(r"^(\s+)?(.*)$", r"\1<red>\2</red>", tmp_text)

                    all_msgs.append(ft.log(
                        text=tmp_text,
                        bullet=bullet,
                        format=options["format"], 
                        indent=indent, 
                        style=options["style"],
                        width=options["width"], 
                    ))
        else:
            for msg in tmp_msgs:
                if log_type == "error":
                    msg="<red>{}</red>".format(msg)
                all_msgs.append(ft.log(
                    text=msg,
                    bullet=bullet,
                    format=options["format"], 
                    indent=indent, 
                    style=options["style"],
                    width=options["width"], 
                ))

        text="\n".join(all_msgs)

                
        if options["keys"]:
            if isinstance(options["keys"], list):
                text=text.format(*options["keys"])
            elif isinstance(options["keys"], dict):
                text=text.format(**options["keys"])

        logging.getLogger().setLevel(logging.DEBUG)
        logging.basicConfig(format="")

        if log_type == "error":
            logging.error(text)
        elif log_type == "info":
            if options["debug"] is True:
                print(text)
            else:
                logging.info(text)
        elif log_type == "success":
            print(text)
        elif log_type == "warning":
            logging.warning(text)

        if options["trace"] is True:
            printed_trace=False
            if hasattr(traceback, 'print_stack'):
                printed_trace=True
                traceback.print_stack()

            if printed_trace is False:
                if hasattr(traceback, 'format_exc'):
                    text=traceback.format_exc()
                    if text is not None:
                        if text.strip() != "NoneType: None":
                            printed_trace=True
                            print(text)

            if printed_trace is False:
                print("No stack to print")

        if options["exit"] is not None:
            sys.exit(options["exit"])

def get_text_without_indent(text, indent):
    if indent is None:
        indent=""

    tmp_text=re.sub(r"^({})(.*)".format(indent), r"\2", text.rstrip())

    return tmp_text
    # return "{}{}".format(indent, tmp_text)

def get_heredoc_indent(txt):
    return re.match(r"(\s*).*", txt).group(1)