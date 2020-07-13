#!/usr/bin/env python3
import json
import platform
from pprint import pprint
import os
import shutil
import sys

from .arg import Arg
from .parse_cli import parse_cli
from .set_args import set_args
from .set_dfn import set_dfn

from ..gpkgs import message as msg

class Options():
    def __init__(self, 
        allow_empty=False,
        cli_expand=False,
        dy_app=None, 
        dy_args=None,
        filenpa_app=None,
        filenpa_args=None, 
    ):
        self.allow_empty=allow_empty
        self.appname=None
        self.argsns=None
        self.argsdy=None
        self.args_nodes=None
        self.authors=None
        self.cli_expand=cli_expand
        self.dy={}
        self.dy_app=dy_app
        self.dy_args=dy_args
        self.description="edit description"
        self.exe_name=sys.argv[0].split(os.sep)[-1]
        self.filenpa_app=filenpa_app
        self.filenpa_args=filenpa_args
        self.licenses=None
        self.help_pointer=None
        self.help_pointer_verbose=None
        self.version=None
        self.aliases={}

        if self.dy_app is None:
            self.set_dy_app_from_path()

        self.set_dy_app()
        self.this_usage="usage: "+self.exe_name

        if self.dy_args is None:
            self.set_dy_arg_from_path()

        self.root_arg_name="__app__"
        self.root_arg=None
        self.current_arg=None
        self.args_lst=[]
        
        set_dfn(self)
        parse_cli(self)
        set_args(self)
        
    def get_argsns_dy_app(self):
        return self.argsns, self.dy_app

    def set_dy_app_from_path(self):
        if self.filenpa_app is not None:
            if not os.path.isabs(self.filenpa_app):
                self.filenpa_app=os.path.join(sys.path[0], self.filenpa_app)
            
            if os.path.exists(self.filenpa_app):
                if os.path.isfile(self.filenpa_app):
                    self.dy_app=self.get_json(self.filenpa_app)
                else:
                    msg.error("Path '{}' is a directory not a json file".format(self.filenpa_app), trace=True)
                    sys.exit(1)
            else:
                msg.error("Path '{}' not found".format(self.filenpa_app), trace=True)
                sys.exit(1)

    def set_dy_arg_from_path(self):
        if self.filenpa_args is not None:
            if not os.path.isabs(self.filenpa_args):
                self.filenpa_args=os.path.join(sys.path[0], self.filenpa_args)
            
            if os.path.exists(self.filenpa_args):
                if os.path.isfile(self.filenpa_args):
                    self.dy_args=self.get_json(self.filenpa_args)
                else:
                    msg.error("Path '{}' is a directory not a json file".format(self.filenpa_args), trace=True)
                    sys.exit(1)
            else:
                msg.error("Path '{}' not found".format(self.filenpa_args), trace=True)
                sys.exit(1)

    def set_dy_app(self):
        if self.dy_app is not None:
            if "description" in self.dy_app:
                self.description=self.dy_app["description"]
            if "version" in self.dy_app:
                self.version=self.dy_app["version"]
            if "exe_name" in self.dy_app:
                self.exe_name=self.dy_app["exe_name"]
                if not "name" in self.dy_app:
                    self.appname=self.dy_app["exe_name"]
            if "name" in self.dy_app:
                if not "exe_name" in self.dy_app:
                    self.exe_name=self.dy_app["name"]
                self.appname=self.dy_app["name"]
            if "authors" in self.dy_app:
                self.authors=", ".join(self.dy_app["authors"])
            if "licenses" in self.dy_app:
                self.licenses=", ".join(self.dy_app["licenses"])
            if not "platform" in self.dy_app:
                self.dy_app["platform"]=platform.system()

            self.dy_app["tty"]={}
            tty=shutil.get_terminal_size((80, 20))
            self.dy_app["tty"]["columns"]=tty.columns
            self.dy_app["tty"]["lines"]=tty.lines
                
    def get_json(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except BaseException as e:
            msg.error(
                "Error '{}' when trying to load json from file '{}'.".format(e, path), trace=True)
            sys.exit(1)
