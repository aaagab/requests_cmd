#!/usr/bin/env python3
import ast
from copy import deepcopy
import json
from getpass import getpass
import os
from pprint import pprint
import re
import shutil
import sys
import tempfile
import textwrap

# from .args import get_arg_values

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt
from ..gpkgs.geturl import geturl
from ..gpkgs.getjson import getjson


def get_path(file_path):
    if not os.path.isabs(file_path):
        file_path=os.path.abspath(file_path)
    return os.path.normpath(file_path)

def requests_cmd(
    auth_pull=False,
    auth_push=False,
    download=False,
    direpa_download=None,
    direpa_project=None,
    dy_input=dict(), # ["data", "params"] provide a dict value to any of these keys if needed
    exit_after=False,
    files=[],
    geturl_alias=None,
    hostname_path=None,
    method=None,
    show_http_code=False,
    show_http_code_info=False,
    show_output=False,
    show_raw=False,
    show_raw_before=False,
    return_content=False,
    url=None,
):
    import requests
    import tempfile

    if url is None:
        msg.error("--url not set")
        sys.exit(1)

    requests.packages.urllib3.disable_warnings()
    methods=[ "DELETE", "GET", "POST", "PUT"]

    if method is None:
        method="GET"
    else:
        method=method.upper()

    if method not in methods:
        msg.error("Method not Found '{}' in {}".format(method, methods), exit=1)

    if len(files) > 0:
        if method != "POST":
            msg.error("--files can only be sent with a POST method", exit=1)
        for key in dy_input:
            if key != "data":
                msg.error("Not authorized '{}'".format(key),"If you send data when posting files only 'data' argument is authorized", exit=1)

    dy_files=dict()
    for i in range(len(files)):
        files[i]=get_path(files[i])
        if not os.path.exists(files[i]):
            msg.error("For --files file not found '{}'".format(files[i]), exit=1)
        temp_name = next(tempfile._get_candidate_names())
        dy_files["upload_"+temp_name]=open(files[i], "rb")

    url=geturl(
        url,
        alias=geturl_alias, 
        direpa_project=direpa_project,
        hostname_path=hostname_path,
        params=dict(),
    )


    direpa_data=os.path.join(tempfile.gettempdir(), "_requests_cmd")
    os.makedirs(direpa_data, exist_ok=True)
    filenpa_data=os.path.join(direpa_data, "data")

    cookie=None
    if auth_push is True:
        if not os.path.exists(filenpa_data):
            msg.error("Authentication File not found '{}'".format(filenpa_data))
            sys.exit(1)
        with open(filenpa_data, "r") as f:
            cookie=f.read()


    # I am not taking care of that case anymore but at some point I should
    # for [FromBody]
    # =john
    # if ":" not in values:
    #     return "={}".format(values)
    data={}
    for key, value in dy_input.items():
        if not (isinstance(value, dict) and isinstance(value, list)):
            value=getjson(value)
        data[key]=value

    if dy_files:
        data["files"]=dy_files
        if "data" in data:
            if len(data["data"]) != 1:
                msg.error(
                    "For data for formData the dict must have a main root key",
                    "The main root key is going to be the name of the part",
                    "Here you have multiple keys {}".format(sorted(data["data"])),
                    exit=1    
                )
            key=next(iter(data["data"]))
            value=json.dumps(data["data"][key])
            data["data"]={ key: value }

    request_options = dict(
        headers=get_headers(cookie=cookie),
        verify=False,
        **data,
    )

    # if using keyword data or json then the format of the data is set to urlencoded for data and application/json for json. It happens even if you modifiy the headers content-type
    if "data" in request_options and not dy_files:
        request_options["headers"].update({"Content-Type": "application/x-www-form-urlencoded"})
    elif "json" in request_options and not dy_files:
        request_options["headers"].update({"Content-Type": "application/json"})

    # if method in ["GET", "P:
    if download is True:
        request_options["stream"]=True

    if show_raw_before is True:
        del request_options["verify"]
        before_request=requests.Request(method,url,**request_options).prepare()
        pretty_print_request(before_request)
        if exit_after is True:
            sys.exit(0)
        else:
            request_options["verify"]=False

    response=getattr( requests, method.lower())(url, **request_options)

    # from urllib3.filepost import encode_multipart_formdata, choose_boundary

    # def encode_multipart_related(fields, boundary=None):
    #     if boundary is None:
    #         boundary = choose_boundary()

    #     body, _ = encode_multipart_formdata(fields, boundary)
    #     content_type = str('multipart/related; boundary=%s' % boundary)

    #     return body, content_type

    if show_raw is True:
        pretty_print_request(response.request)   
    
    response=get_reponse_content(show_http_code_info, show_http_code, response, show_output)

    r"""
set id=44 && A:\wrk\r\requests_cmd\src\main.py --url api/attachments/download/__id__ --method get --auth-push --download --path C:\Users\user\AppData\Local\Temp
set data="{ 'ids':['dd77a72b-c8f1-e911-b75a-00e04c680e1a']}" &&  A:\wrk\r\requests_cmd\src\main.py --url api/events/report --method post --auth-push --json __data__ --download --path C:\Users\user\AppData\Local\Temp
    """
    if download is True:
        if response.status_code == 200:
            value=response.headers.get("Content-Disposition")
            if value is None:
                msg.error("Filename can't be found for download")
                sys.exit(1)

            filen_download = re.findall("filename=(.+)", value)[0]
            if direpa_download is None:
                direpa_download=os.getcwd()
            else:
                direpa_download=get_path(direpa_download)
            filenpa_download=os.path.join(direpa_download, filen_download)

            with open(filenpa_download, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
                msg.success("Saved '<cyan>{}</cyan>'".format(filenpa_download))

    if auth_pull is True:
        with open(filenpa_data, "w") as f:
            f.write(response.json())
            print("Cookie Saved!")

    if show_output is True:
        print_html_if(response.text)

    return response

def get_headers(method="GET", host="localhost", referer="http://localhost/", user_agent="firefox", cookie=None):
    # referer="http://lclwapps.edu/t/timeclock/1/login"
    # host="lclwapps.edu"
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

def get_reponse_content(show_http_code_info, show_http_code, response, show_output=False):
    status_code=response.status_code
    get_status_code_info(show_http_code_info, show_http_code, status_code)
    if response.status_code == 200:
        try:
            return response
        except:
            print("Not Json Output")
            print(response.headers)
            print(response.text)
    else:
        if show_output is True:
            print_html_if(response.content.decode("utf-8"))
        print("Error Status Code '{}'".format(status_code))
        sys.exit(1)

def print_html_if(text):
    if "<html>" in text:
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        # print(h.handle(text))
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

def get_status_code_info(show_http_code_info, show_http_code, code):
    filenpa_status_code=os.path.join(os.path.dirname(os.path.realpath(__file__)), "status-codes.json")
    with open(filenpa_status_code, "r") as f:
        dy_status_codes=json.load(f)
        for search_code in [
            str(code)[0]+"xx",
            str(code),
        ]:
            if search_code in dy_status_codes:
                dy=dy_status_codes[search_code]
                if show_http_code_info is True:
                    print_status_code(search_code, dy)
                else:
                    if search_code == str(code):
                        if show_http_code is True:
                            print("\n--> '{}' <--".format(code))

def print_status_code(code, dy_code):
    print("--> '{}' <--> '{}' <--\n{}".format(
        code,
        dy_code["phrase"],
        textwrap.indent(dy_code["description"], "  ", lambda line: True),
    ))

# Host: lclwapps.edu
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0
# Accept: application/json, text/plain, */*
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate
# Referer: http://lclwapps.edu/t/timeclock/1/login
# Content-Type: application/json;charset=utf-8
# Content-Length: 59
# DNT: 1
# Connection: keep-alive
# Pragma: no-cache
# Cache-Control: no-cache
