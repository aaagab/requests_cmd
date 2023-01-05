#!/usr/bin/env python3

if __name__ == "__main__":
    import sys, os
    import importlib
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg=importlib.import_module(module_name)
    del sys.path[0]

    args=pkg.Nargs(
        options_file="config/options.yaml",
        metadata=dict(executable="requests_cmd"),
        substitute=True,
    ).get_args()

    input_files=[]
    for farg in args.input.file._branches:
        if farg._here:
            input_files.append(dict(
                content_type=farg.content_type._value,
                headers=farg.headers._value,
                name=farg.name._value,
                path=farg._value,
            ))

    pkg.requests_cmd(
        auth_pull=args.auth.pull._here,
        auth_push=args.auth.push._here,
        download=args.download._here,
        direpa_download=args.download._value,
        direpa_project=args.project_path._value,
        error_exit=args.ignore_error._here == False,
        filen_download=args.download.filen._value,
        filenpa_token=args.auth.push.token._value,
        hostname_path=args.hostname._value,
        input_data=args.input.data._value,
        input_data_not_json=args.input.data.not_json._here,
        input_files=input_files,
        input_form_data=args.input.form_data._value,
        input_json=args.input.json._value,
        input_params=args.input.params._value,
        method=args.method._value,
        show_http_code=args.http_code._here,
        show_http_code_info=args.http_code.info._here,
        show_http_code_pretty=args.http_code.pretty._here,
        show_output=args.output._here,
        show_raw=args.raw._here,
        show_raw_before=args.raw.before._here,
        show_raw_before_exit=args.raw.before.exit._here,
        url=args.url._value,
        url_alias=args.url.alias._value,
    )
