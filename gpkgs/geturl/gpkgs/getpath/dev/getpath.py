#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from ..gpkgs import message as msg

def getpath(path_elem, path_type, error_exit=True, warn=False):
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
            err_msg="Path not found '{}'".format(path_elem)
            if error_exit is True:
                msg.error(err_msg, exit=1)
            else:
                if warn is True:
                    msg.warning(err_msg)
                return None
        if path_type == "directory":
            if not os.path.isdir(path_elem):
                err_msg="Path is not a directory '{}'".format(path_elem)
                if error_exit is True:
                    msg.error(err_msg, exit=1)
                else:
                    if warn is True:
                        msg.warning(err_msg)
                    return None
        elif path_type == "file":
            if not os.path.isfile(path_elem):
                err_msg="Path is not a file '{}'".format(path_elem)
                if error_exit is True:
                    msg.error(err_msg, exit=1)
                else:
                    if warn is True:
                        msg.warning(err_msg)
                    return None

    return path_elem
