#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from ..gpkgs import message as msg

def getpath(path_elem, path_type):
    exit_not_found=None
    if path_type in ["realpath", "file", "directory"]:
        exit_not_found=True
    elif path_type == "virtualpath":
        exit_not_found=False

    if not os.path.isabs(path_elem):
        path_elem=os.path.abspath(path_elem)
    path_elem=os.path.normpath(path_elem)
    if exit_not_found is True:
        if not os.path.exists(path_elem):
            msg.error("Path not found '{}'".format(path_elem), exit=1)
        if path_type == "directory":
            if not os.path.isdir(path_elem):
                msg.error("Path is not a directory '{}'".format(path_elem), exit=1)
        elif path_type == "file":
            if not os.path.isfile(path_elem):
                msg.error("Path is not a file '{}'".format(path_elem), exit=1)

    return path_elem