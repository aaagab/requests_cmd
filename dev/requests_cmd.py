#!/usr/bin/env python3
from enum import Enum
from pprint import pprint
from typing import Any
from io import BufferedReader
import logging
import json
import os
import re
import requests
from requests import Response, PreparedRequest
from requests.adapters import HTTPAdapter, Retry
import urllib3
import shutil
import sys
import tempfile
import textwrap
from urllib.parse import urlparse

yaml_enabled=True
try:
    import yaml
except ModuleNotFoundError:
    yaml_enabled=False

from ..gpkgs import message as msg
from ..gpkgs.geturl import geturl
from ..gpkgs.getjson import getjson

class HttpMethod(str, Enum):
    __order__ = "DELETE GET POST PUT"
    DELETE="delete"
    GET="get"
    POST="post"
    PUT="put"

class InputFile():
    def __init__(self,
        path:str,
        content_type: str|None=None,
        headers:dict[str, Any]|str|None=None,
        name: str|None=None,
        field: str|None=None,
    ):
        """
            :param str path: required filepath absolute or relative
            :param str|None content_type: provides file mimetype
            :param dict[str, Any]|str|None headers: provides headers for file upload request
            :param str|None name: provides alternative file name
            :param str|None field: provides a field name for FormData default is files
        """
        self.path=path
        self.content_type=content_type
        self.headers=headers
        self.name=name
        self.field=field
    
def get_path(file_path:str):
    if not os.path.isabs(file_path):
        file_path=os.path.abspath(file_path)
    return os.path.normpath(file_path)

def get_data_value(value:bool|dict|float|int|list|str):
    if (isinstance(value, dict) or isinstance(value, list)):
        return value
    elif isinstance(value, str):
        if value[-5:] == ".yaml":
            filenpa_yaml=get_path(value)
            if yaml_enabled is False:
                msg.error("Can't process '{}'. pyyaml not found please install it with pip install pyyaml".format(filenpa_yaml))
                sys.exit(1)
            with open(filenpa_yaml, "r") as f:
                return yaml.safe_load(f)
        else:
            return getjson(value)
    else:
        return getjson(value)

def requests_cmd(
    url:str,
    auth_pull:bool=False,
    auth_push:bool=False,
    download:bool=False,
    direpa_download:str|None=None,
    direpa_project:str|None=None,
    error_exit:bool=False,
    filen_download:str|None=None,
    filenpa_token:str|None=None,
    hostname_path:str|None=None,
    input_data:str|dict|None=None,
    input_data_not_json:bool=False,
    input_files:list[InputFile]|None=None,
    input_form_data:list[str|dict]|None=None,
    input_json:str|dict|list|None=None,
    input_params:str|dict|list|None=None,
    method:HttpMethod|None=HttpMethod.GET,
    retries:int=0,
    show_http_code:bool=False,
    show_http_code_info:bool=False,
    show_http_code_pretty:bool=False,
    show_output:bool=False,
    show_raw:bool=False,
    show_raw_before:bool=False,
    show_raw_before_exit:bool=False,
    url_alias:str|None="hostname_url",
) -> Response:
    """ Python Requests Wrapper
    :param str    url: full url or relative url
    :param bool=False    auth_pull: save response token into filenpa_token
    :param bool=False    auth_push: get token from filenpa_token and add it to request header "Authorization: Bearer {token}"
    :param bool=False    download: download response, if direpa_download is not provided then it is downloaded to current directory. if filen_download is not provided then filename is read from response header Content-Disposition
    :param str|None=None    direpa_download: provide selected download directory
    :param str|None=None    direpa_project: provide direpa_project when using relative url see url_alias. If set to None direpa_project is current directory
    :param bool=False    error_exit: If Response.ok is false then an error is printed and the program exits with code 1.
    :param str|None=None    filen_download: provide an alternative filename for a download
    :param str|None=None    filenpa_token: provide a path to save a bearer token. Default path is os.path.join(tempfile.gettempdir(), "_requests_cmd", "data")
    :param str|None=None    hostname_path: When url is relative a hostname_path can be provided to complete the url .i.e https://wwww.myserver.com
    :param str|None=None    input_data: send data inside a request. data is parsed to json, a JSON string single or double quotes will be parsed.
    :param bool=False    input_data_not_json: send data that is not JSON inside a request
    :param list[InputFile]|None=None    input_files: send file to server only path is required see InputFile object
    :param str|dict|None=None    input_form_data: send form_data inside a request
    :param str|dict|list|None=None    input_json: send JSON inside a request
    :param str|dict|list|None=None    input_params: allow to provide query parameters as a dict
    :param HttpMethod|None=HttpMethod.GET    method: HTTP methods supported by requests_cmd see object HttpMethod
    :param int=0         retries: allows to increase value for error Max retries exceeded with url 
    :param bool=False    show_http_code: print the response http status code
    :param bool=False    show_http_code_info: print the response http status code description
    :param bool=False    show_http_code_pretty: print the response http status code in a "pretty" way
    :param bool=False    show_output: print response output print response text in formatted HTML if HTML or if JSON and has a message key, print the message key or print JSON or if not JSON print the text
    :param bool=False    show_raw: print raw request after sending it
    :param bool=False    show_raw_before: print raw request before sending it
    :param bool=False    show_raw_before_exit: print raw request and exit before sending it
    :param str|None=None    url_alias: If url is relative and hostname_path is None then program is looking into url_alias value os.environ variable to complete the url path. If url_alias value environ variable does not exists then program searches in direpa_project directory for a file "{url_alias}.txt" to get the hostname path from there.
    """
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    urllib3.disable_warnings()

    if method is None:
        method=HttpMethod.GET

    if method not in list(HttpMethod):
        msg.error(f"Method not Found '{method}' in {list(HttpMethod)}")
        sys.exit(1)

    if url_alias is None:
        url_alias="hostname_url"

    dy_mimetypes=dict()
    if input_files is not None:
        if not isinstance(input_files, list):
            msg.error(f"files must be of type {list}")
            sys.exit(1)
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
            msg.error("input_data can't be set when input_json is set.")
            sys.exit(1)
        if has_form_data:
            msg.error("input_data can't be set when input_files is set or input_form_data is set.")
            sys.exit(1)
        if input_data_not_json is True:
            _input["data"]=input_data
        else:
            _input["data"]=get_data_value(input_data)
    elif has_json:
        if has_form_data:
            msg.error("input_json can't be set when input_files is set or input_form_data is set.")
            sys.exit(1)

        _input["json"]=get_data_value(input_json)

    if input_params is not None:
        _input["params"]=get_data_value(input_params)

    if url is None:
        msg.error("url not set")
        sys.exit(1)

    url=geturl(
        url,
        alias=url_alias, 
        direpa_project=direpa_project,
        hostname_path=hostname_path,
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


    if input_form_data is None or (isinstance(input_form_data, list) and len(input_form_data) == 0):
        if input_files is None or len(input_files) == 0:
            pass
        else:
            if len(input_files) > 0:
                _input["files"]=get_files(input_files, dy_mimetypes)
    else:
        _input["data"]=dict()
        for fdata in input_form_data:
            tmp_data=get_data_value(fdata)
            if isinstance(tmp_data, dict):
                for key, value in tmp_data.items():
                    _input["data"][key]=json.dumps(value)
            else:
                msg.error(f"input_form_data must be of type {dict}")
                sys.exit(1)

        if input_files is None or len(input_files)  == 0:
            if len(_input["data"]) == 0:
                msg.error("When using form-data please set either input_form_data and/or input_files.")
                sys.exit(1)
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
        if isinstance(request_options["headers"], dict):
            request_options["headers"].update({"Content-Type": "application/x-www-form-urlencoded"})

    if download is True:
        request_options["stream"]=True

    if show_raw_before is True:
        del request_options["verify"]
        before_request=requests.Request(method.value, url,**request_options).prepare()
        pretty_print_request(before_request)
        if show_raw_before_exit is True:
            sys.exit(0)
        else:
            request_options["verify"]=False

    session=requests.Session()
    param_retries = Retry(total=retries,
                backoff_factor=0.1,
            )
    session.mount(f"{urlparse(url).scheme}://", HTTPAdapter(max_retries=param_retries))
    response:Response=getattr( session, method.value.lower())(url, **request_options)

    if show_raw is True:
        pretty_print_request(response.request)   
    
    if response.ok is True:
        if download is True:
            if response.status_code == 200:
                value=response.headers.get("Content-Disposition")
                pprint(response.headers)
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
                        filen_download=reg.group(1).split(";")[0]
                    else:
                        msg.error("value '{}' does not match regex '{}'".format(value, reg_str))
                        sys.exit(1)

                if filen_download is not None:
                    filenpa_download=os.path.join(direpa_download, filen_download)

                    with open(filenpa_download, 'wb') as f:
                        shutil.copyfileobj(response.raw, f)
                        msg.success("Saved '{}'".format(filenpa_download))
                else:
                    raise NotImplementedError("At this point filen_download shouldn't be None")

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

def get_files(files:list[InputFile], dy_mimetypes:dict[str,str]):
    tmp_files:list[
        tuple[str, tuple[str, BufferedReader]]|
        tuple[str, tuple[str, BufferedReader, str]]|
        tuple[str, tuple[str, BufferedReader, str, dict]]
    ]=[]
    
    for input_file in files:
        tmp_list:list[str|BufferedReader|dict]=[]
        # The tuples may be 
        #     2-tuples (filename, fileobj), 
        #     3-tuples (filename, fileobj, contentype)
        #     4-tuples (filename, fileobj, contentype, custom_headers).
        
        tmp_file=get_path(input_file.path)
        if not os.path.exists(tmp_file):
            msg.error("File not found '{}'.".format(tmp_file))
            sys.exit(1)

        if input_file.field is None:
            input_file.field="files"

        if input_file.name is None:
            tmp_list.append(os.path.basename(tmp_file))
        else:
            tmp_list.append(input_file.name)
        tmp_list.append(open(tmp_file, "rb"))
        
        if input_file.headers is None:
            if input_file.content_type is None:
                filer, ext=os.path.splitext(tmp_file)
                if ext in dy_mimetypes:
                    tmp_list.append(dy_mimetypes[ext])
                else:
                    tmp_list.append("application/octet-stream")
            else:
                tmp_list.append(input_file.content_type)
        else:
            headers=getjson(input_file.headers)
                
            if input_file.content_type is None:
                filer, ext=os.path.splitext(input_file.path)
                if ext in dy_mimetypes:
                    tmp_list.append(dy_mimetypes[ext])
                else:
                    tmp_list.append("application/octet-stream")
            else:
                tmp_list.append(input_file.content_type)

            if isinstance(headers, dict):
                tmp_list.append(headers)
            else:
                msg.error(f"In InputFile '{input_file.path}' headers must be a str parsable as a dict or a dict.")
                sys.exit(1)

        if len(tmp_list) == 2:
            if isinstance(tmp_list[0], str) and isinstance(tmp_list[1], BufferedReader):
                tmp_files.append(
                    (input_file.field, (tmp_list[0], tmp_list[1]))
                )
        elif len(tmp_list) == 3:
            if isinstance(tmp_list[0], str) and isinstance(tmp_list[1], BufferedReader) and isinstance(tmp_list[2], str):
                tmp_files.append(
                    (input_file.field, (tmp_list[0], tmp_list[1], tmp_list[2]))
                )
        elif len(tmp_list) == 4:
            if isinstance(tmp_list[0], str) and isinstance(tmp_list[1], BufferedReader) and isinstance(tmp_list[2], str) and isinstance(tmp_list[3], dict):
                tmp_files.append(
                    (input_file.field, (tmp_list[0], tmp_list[1], tmp_list[2], tmp_list[3]))
                )
        else:
            raise TypeError()

    return tmp_files

def print_status_code(code:str, dy_code:dict):
    print("--> '{}' <--> '{}' <--\n{}".format(
        code,
        dy_code["phrase"],
        textwrap.indent(dy_code["description"], "  ", lambda line: True),
    ))

def get_headers(host="localhost", referer="http://localhost/", user_agent="firefox", cookie=None):
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

def pretty_print_request(req:PreparedRequest):
    if req.method is None or req.url is None:
        raise Exception("For PreparedRequest method and url must be not None")
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

def print_html_if(text:str):
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
