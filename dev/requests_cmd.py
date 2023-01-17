#!/usr/bin/env python3
from pprint import pprint
import logging
import json
import os
import re
import requests
import shutil
import sys
import tempfile
import textwrap

yaml_enabled=True
try:
    import yaml
except ModuleNotFoundError:
    yaml_enabled=False

from ..gpkgs import message as msg
from ..gpkgs.geturl import geturl
from ..gpkgs.getjson import getjson

def get_path(file_path):
    if not os.path.isabs(file_path):
        file_path=os.path.abspath(file_path)
    return os.path.normpath(file_path)

def get_data_value(value):
    if (isinstance(value, dict) or isinstance(value, list)):
        return value
    else:
        if value[-5:] == ".yaml":
            filenpa_yaml=get_path(value)
            if yaml_enabled is False:
                msg.error("Can't process '{}'. pyyaml not found please install it with pip install pyyaml".format(filenpa_yaml), exit=1)
            with open(filenpa_yaml, "r") as f:
                value=yaml.safe_load(f)
        else:
            value=getjson(value)
        return value

def requests_cmd(
    auth_pull=False,
    auth_push=False,
    download=False,
    direpa_download=None,
    direpa_project=None,
    error_exit=False,
    filen_download=None,
    filenpa_token=None,
    hostname_path=None,
    input_data=None,
    input_data_not_json=False,
    input_files=None,
    input_form_data=None,
    input_json=None,
    input_params=None,
    method=None,
    show_http_code=False,
    show_http_code_info=False,
    show_http_code_pretty=False,
    show_output=False,
    show_raw=False,
    show_raw_before=False,
    show_raw_before_exit=False,
    url=None,
    url_alias=None,
):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    requests.packages.urllib3.disable_warnings()

    if url_alias is None:
        url_alias="hostname_url"

    dy_mimetypes=dict()
    if input_files is not None:
        if not isinstance(input_files, list):
            msg.error("files must be of type {}".format(list), exit=1)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "mimetypes.json"), "r")as f:
            dy_mimetypes=json.load(f)

    _input=dict()
    has_data=input_data is not None
    has_json=input_json is not None
    has_form_data=None
    if input_files is None or len(input_files) == 0:
        has_form_data=input_form_data is not None
    else:
        has_form_data=input_form_data is not None

    if has_data:
        if has_json:
            msg.error("input_data can't be set when input_json is set.", exit=1)
        if has_form_data:
            msg.error("input_data can't be set when input_files is set or input_form_data is set.", exit=1)
        if input_data_not_json is True:
            _input["data"]=input_data
        else:
            _input["data"]=get_data_value(input_data)
    elif has_json:
        if has_form_data:
            msg.error("input_json can't be set when input_files is set or input_form_data is set.", exit=1)

        _input["json"]=get_data_value(input_json)

    if input_params is not None:
        _input["params"]=get_data_value(input_params)

    if url is None:
        msg.error("url not set")
        sys.exit(1)

    methods=[ "DELETE", "GET", "POST", "PUT"]

    if method is None:
        method="GET"
    else:
        method=method.upper()

    if method not in methods:
        msg.error("Method not Found '{}' in {}".format(method, methods), exit=1)

    url=geturl(
        url,
        alias=url_alias, 
        direpa_project=direpa_project,
        hostname_path=hostname_path,
        params=dict(),
    )

    if filenpa_token is None:
        filenpa_token=os.path.join(tempfile.gettempdir(), "_requests_cmd", "data")
    os.makedirs(os.path.dirname(filenpa_token), exist_ok=True)

    cookie=None
    if auth_push is True:
        if not os.path.exists(filenpa_token):
            open(filenpa_token, "w").close()
        with open(filenpa_token, "r") as f:
            cookie=f.read()


    if input_form_data is None:
        if input_files is None or len(input_files) == 0:
            pass
        else:
            if len(input_files) > 0:
                _input["files"]=get_files(input_files, dy_mimetypes)
    else:
        tmp_data=get_data_value(input_form_data)
        _input["data"]=dict()
        for key, value in tmp_data.items():
            _input["data"][key]=json.dumps(value)

        if not isinstance(_input["data"], dict):
            msg.error("input_form_data must be of type {}".format(dict), exit=1)

        if input_files is None or len(input_files)  == 0:
            if len(_input["data"]) == 0:
                msg.error("For form-data either input_form_data must be set or input_files.", exit=1)

            # send an empty file to be able to send data with content-type application/x-www-form-urlencoded
            _input["files"]=[("", None)]
        else:                
            _input["files"]=get_files(input_files, dy_mimetypes)

    request_options = dict(
        headers=get_headers(cookie=cookie),
        verify=False,
        **_input,
    )

    if has_data:
        request_options["headers"].update({"Content-Type": "application/x-www-form-urlencoded"})

    if download is True:
        request_options["stream"]=True

    if show_raw_before is True:
        del request_options["verify"]
        before_request=requests.Request(method,url,**request_options).prepare()
        pretty_print_request(before_request)
        if show_raw_before_exit is True:
            sys.exit(0)
        else:
            request_options["verify"]=False

    response=getattr( requests, method.lower())(url, **request_options)

    if show_raw is True:
        pretty_print_request(response.request)   
    
    if response.ok is True:
        if download is True:
            if response.status_code == 200:
                value=response.headers.get("Content-Disposition")
                if value is None:
                    msg.error("Filename can't be found for download")
                    sys.exit(1)

                if direpa_download is None:
                    direpa_download=os.getcwd()
                else:
                    direpa_download=get_path(direpa_download)

                if filen_download is None:
                    reg_str=r"^.*filename=(?:\"?|\')(.+?)(?:\"|\')?$"
                    reg=re.match(reg_str, value)
                    if reg:
                        filen_download=reg.group(1)
                    else:
                        msg.error("value '{}' does not match regex '{}'".format(value, reg_str), exit=1)

                filenpa_download=os.path.join(direpa_download, filen_download)

                with open(filenpa_download, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                    msg.success("Saved '<cyan>{}</cyan>'".format(filenpa_download))

        if auth_pull is True:
            with open(filenpa_token, "w") as f:
                f.write(response.json())

    if show_http_code is True:
        if show_http_code_pretty is True:
            print("\n--> '{}' <--".format(response.status_code))
        elif show_http_code_info is True:
            filenpa_status_code=os.path.join(os.path.dirname(os.path.realpath(__file__)), "status-codes.json")
            with open(filenpa_status_code, "r") as f:
                dy_status_codes=json.load(f)

                for search_code in [
                    str(response.status_code)[0]+"xx",
                    str(response.status_code),
                ]:
                    if search_code in dy_status_codes:
                        dy=dy_status_codes[search_code]
                        print_status_code(search_code, dy)
                    else:       
                        msg.warning("status code not documented '{}'".format(response.status_code))
        else:
            print(response.status_code)


    if show_output is True:
        print_html_if(response.text)

    if error_exit is True and response.ok is False:
        print("Error Status Code '{}'".format(response.status_code))
        sys.exit(1)

    return response

def get_files(files, dy_mimetypes):
    tmp_files=[]
    authorized_keys=[
        "content_type",
        "headers",
        "name",
        "path",
    ]

    for dy in files:
        tmp_list=[]
        if not isinstance(dy, dict):
            msg.error("File value '{}' must be of type {}.".format(dy, dict), exit=1)

        for key in sorted(dy):
            if key not in authorized_keys:
                msg.error("For file dictionary key '{}' not found in {}.".format(key, authorized_keys), exit=1)

        # The tuples may be 
        #     2-tuples (filename, fileobj), 
        #     3-tuples (filename, fileobj, contentype)
        #     4-tuples (filename, fileobj, contentype, custom_headers).
        
        if "path" in dy and dy["path"] is not None:
            tmp_file=get_path(dy["path"])
            if not os.path.exists(tmp_file):
                msg.error("File not found '{}'.".format(tmp_file), exit=1)

            if "name" in dy and dy["name"] is not None:
                tmp_list.append(dy["name"])
            else:
                tmp_list.append(os.path.basename(tmp_file))
            tmp_list.append(open(tmp_file, "rb"))
            
            if "headers" in dy and dy["headers"] is not None:
                dy["headers"]=getjson(dy["headers"])
                if "content_type" in dy and dy["content_type"] is not None:
                    tmp_list.append(dy["content_type"])
                else:
                    filer, ext=os.path.splitext(dy["path"])
                    if ext in dy_mimetypes:
                        tmp_list.append(dy_mimetypes[ext])
                    else:
                        msg.error("Unknown mimetypes for file '{}'. Please provide mimetype with key 'content_type'.".format(dy["path"]), exit=1)

                tmp_list.append(dy["headers"])
            else:
                if "content_type" in dy and dy["content_type"] is not None:
                    tmp_list.append(dy["content_type"])
                else:
                    filer, ext=os.path.splitext(dy["path"])
                    if ext in dy_mimetypes:
                        tmp_list.append(dy_mimetypes[ext])

            tmp_files.append((
                tmp_list[0],
                tuple(tmp_list),
            ))
        else:
            msg.error("In File dictionary '{}' key not found 'path'.".format(dy), exit=1)

    return tmp_files

def print_status_code(code, dy_code):
    print("--> '{}' <--> '{}' <--\n{}".format(
        code,
        dy_code["phrase"],
        textwrap.indent(dy_code["description"], "  ", lambda line: True),
    ))

def get_headers(method="GET", host="localhost", referer="http://localhost/", user_agent="firefox", cookie=None):
    user_agents=dict(
        chrome="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        edge="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763",
        firefox="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
    )

    headers={
        "Host": "{}".format(host),
        "User-Agent": user_agents[user_agent],
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "{}".format(referer),
        "DNT": "1",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    if cookie is not None:
        headers.update({
            "Authorization": "Bearer {}".format(cookie),
            "Cookie": "token={}".format(cookie),
        })

    return headers

def pretty_print_request(req):
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

def print_html_if(text):
    if "<html>" in text:
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        previous_blank=False
        print()
        for line in h.handle(text).splitlines():
            if previous_blank is True:
                if line.strip() == "":
                    print_line=False
                else:
                    print_line=True
                    previous_blank=False
            else:
                print_line=True
                if line.strip() == "":
                    previous_blank=True

            if print_line is True:
                print(line)
    else:
        try:
            dy=json.loads(text)
            if "message" in dy:
                print()
                content= dy["message"]
                print("message:")
                for line in content.splitlines():
                    print("    {}".format(line))
                print()
            else:
                pprint(dy)
        except:
            if text:
                print("\n{}\n".format(text))
