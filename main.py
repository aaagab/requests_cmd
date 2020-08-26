#!/usr/bin/env python3
import json
from pprint import pprint
import re
import os
import sys
import subprocess
import shlex

if __name__ == "__main__":
    import sys, os

    import importlib
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg=importlib.import_module(module_name)
    del sys.path[0]

    args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="options.json", allow_empty=True, cli_expand=True).get_argsns_dy_app()

    if args.examples.here:
        print(r"""
    requests_cmd --url api/users/me --hostname A:\wrk\e\example\1\src\url_hostname.txt --output
    requests_cmd --url api/users/me --hostname --output
    requests_cmd --url https://www.example.com/e/example/api/account/login --method post --data A:\wrk\e\example\1\src\_requests\post.json --auth-pull
    requests_cmd --url https://www.example.com/e/example/api/users/me --method get --auth-push --output
    requests_cmd --url https://www.example.com/e/example/api/attachements/upload --method post --data  A:\wrk\e\example\1\src\_requests\uploadFile.json --auth-push --output --files "A:\wrk\e\example\1\src\_tests\browser\files\file6.txt"
        
    requests_cmd --url api/attachments/download --params "{\"id\":4}" --auth-push --download --path C:\Users\user\AppData\Local\Temp
    requests_cmd --url api/session --path-project A:\wrk\e\example\1\src --output

    # script example
    response=pkg.requests_cmd(url="https://www.example.com/e/example/api/users/me")
    pprint(dir(response))
    print(response.status_code)
    pprint(response.json())
        """) 
        sys.exit(0)

    dy_input=dict()
    for arg_str in ["data", "json", "params"]:
        arg=dy_app["args"][arg_str]
        if arg.here:
            dy_input[arg_str]=arg.value

    url_alias=args.url_alias.value
    if url_alias is None:
        url_alias="hostname_url"

    pkg.requests_cmd(
        auth_pull=args.auth_pull.here,
        auth_push=args.auth_push.here,
        download=args.download.here,
        direpa_download=args.path.value,
        direpa_project=args.path_project.value,
        dy_input=dy_input,
        error_exit=args.error_exit.here,
        exit_after=args.exit.here,
        files=args.files.values,
        geturl_alias=url_alias,
        hostname_path=args.hostname.value,
        method=args.method.value,
        show_http_code=args.code.here,
        show_http_code_info=args.code_info.here,
        show_http_code_pretty=args.code_pretty.here,
        show_output=args.get_output.here,
        show_raw=args.raw.here,
        show_raw_before=args.raw_before.here,
        url=args.url.value,
    )


    ## script example
    # response=pkg.requests_cmd(url="https://www.example.com/e/example/api/users/me")
    # pprint(dir(response))
    # print(response.status_code)
    # pprint(response.json())