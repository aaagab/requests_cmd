#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import re

from ..gpkgs.getpath import getpath
from ..gpkgs import message as msg

def geturl(url, 
    alias=None, 
    direpa_project=None,
    hostname_path=None,
    params=dict(),
):
    http_regstr=r"^http.*$"
    if re.match(http_regstr, url):
        return url
    else:
        if hostname_path is None:
            if alias is None:
                msg.error("url is not absolute ''".format(url),
                "please give an absolute url or add an alias", exit=1)
            else:
                alias_var=alias.upper()
                if alias_var in os.environ:
                    if os.environ[alias_var]:
                        hostname_path=os.environ[alias_var]

                if hostname_path is None:
                    if direpa_project is None:
                        direpa_project=os.getcwd()
                    filenpa_hostname=os.path.join(direpa_project, "{}.txt".format(alias.lower()))
                    hostname_path=get_hostname_from_file(filenpa_hostname)
                
                if hostname_path is None or not re.match(http_regstr, hostname_path):
                    msg.error(
                        "url is not a valid url, you need hostname for '{}'".format(url),
                        "Possible reasons:",
                        " - Environ variable '{}' not set".format(alias_var),
                        " - '{}'.txt does not exists or is not a file.".format(alias_var, filenpa_hostname),
                        " - '{}'.txt is empty".format(alias_var, filenpa_hostname),
                        " - Value provided by the file or the env var does not match '{}'".format(http_regstr),
                        exit=1
                    )
                    sys.exit(1)
        else:
            if not re.match(http_regstr, hostname_path):
                msg.error("hostname path '{}' does not match '{}'".format(hostname_path, http_regstr), exit=1)

        if len(url) > 0:
            if url[0] == "/":
                url=url[1:]
            if hostname_path[-1] == "/":
                hostname_path=hostname_path[:-1]
        url="{}/{}".format(
            hostname_path,
            url
        )
        params_str=""
        for key, value in params.items():
            prefix="&"
            if params_str == "":
                prefix=""
            params_str+="{}{}={}".format(prefix, key, value)
            pass

        if params_str != "":
            url+="?"+params_str
        return url

def get_hostname_from_file(file_path):
    filenpa_hostname=getpath(file_path, "file", error_exit=False)
    if filenpa_hostname is None:
        return filenpa_hostname

    with open(filenpa_hostname, "r") as f:
        url_hostname_direl=f.read().strip()
        if not url_hostname_direl:
            return None
    return url_hostname_direl
