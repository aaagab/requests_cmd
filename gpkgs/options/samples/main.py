#!/usr/bin/env python3
# author: Gabriel Auger
# version: 8.1.3
# name: options
# license: MIT

# test/main.py --version --required
if __name__ == "__main__":
    import importlib
    import json
    import os
    from pprint import pprint
    import sys
    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(os.path.dirname(direpa_script))
    module_name=os.path.basename(os.path.dirname(direpa_script))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/pbuilder.json").get_argsns_dy_app()
    print(args.__app__.values)
    sys.exit(0)
   
    # cli_expand test
    # cmd:
    #     export value1="apple_"
    #     export value2="pear_"
    #     samples/main.py --update __value1____value2__
    # result arg_value:
    #     apple_pear_
    # cli_expand is useful for windows mainly so that you can expand environment variable within you command
    # on windows do set var=123 or set var="other value"

    args, dy_app=pkg.Options(filenpa_app="gpm.json", dy_args=dict(
        update=dict(values="MYVALUE")
    ), allow_empty=True, cli_expand=True).get_argsns_dy_app()

    sys.exit(0)
   
    # minimal config
    opts=pkg.Options()
    print(opts.args, opts.dy_app)

    # other config
    args, dy_app=pkg.Options(allow_empty=True).get_argsns_dy_app()
    print(opts.args, opts.dy_app)

    with open(os.path.join(direpa_script, "gpm.json"), 'r') as f:
        dy_app=json.load(f)
        args, dy_app=pkg.Options(dy_app=dy_app, filenpa_args="config/min.json", allow_empty=True).get_argsns_dy_app()
        print(args, dy_app["platform"])

    args, dy_app=pkg.Options(filenpa_app="gpm.json").get_argsns_dy_app()
    print(args, dy_app["platform"])

    args, dy_app=pkg.Options(dy_app=dict(version="1.0.1")).get_argsns_dy_app()
    print(args, dy_app["version"])    

    args, dy_app=pkg.Options(filenpa_app="gpm.json", dy_args=dict(
        update=dict(values="marc,john")
    )).get_argsns_dy_app()
    print(args, dy_app["args"])
    if args.update:
        print(args.update[0], args.update[1])
        sys.exit(0)
 
    args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/options.json").get_argsns_dy_app()
    
    if args.debug.here is True:
        print("debug mode")
        dy_app["debug"]=True

    if args.required_arg.here is True:
        print("Required argument added")

    argsdy=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/options.json").argsdy

    pprint(argsdy)
    print(argsdy["info"].here)
    print(argsdy["info"].value)
    print(argsdy["info"].values)
    print(argsdy["__app__"].values)
