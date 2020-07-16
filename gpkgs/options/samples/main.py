#!/usr/bin/env python3
# author: Gabriel Auger
# version: 8.2.0
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

    args, dy_app=pkg.Options(filenpa_app="gpm.json", dy_args=dict( myjson=dict(values="json_VALUE", type="json"))).get_argsns_dy_app()
    # samples/main.py --myjson "{'key': '__hidden__'}"
    if args.myjson.here:
        print(args.myjson.value)
    sys.exit(0)

    opts=pkg.Options()
    print(opts.args, opts.dy_app)

    sys.exit()

    args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/release.json").get_argsns_dy_app()
    print(args.__app__.values)
    sys.exit(0)

    # testing path types
    args, dy_app=pkg.Options(filenpa_app="gpm.json", dy_args=dict(
        mydirectory=dict(values="directory_VALUE", type="directory"),
        myfile=dict(values="file_VALUE", type="file"),
        myvirtualpath=dict(values="virtualpath_VALUE", type="virtualpath"),
        myrealpath=dict(values="realpath_VALUE", type="realpath"),
    )).get_argsns_dy_app()
    # pprint(dy_)

    # samples/main.py --mydirectory /sys --myfile gpm.json --myvirtualpath moon/lander --myrealpath /etc/grub.d/README"
    print("mydirectory: ", args.mydirectory.value) 
    print("myfile: ", args.myfile.value) 
    print("myvirtualpath: ", args.myvirtualpath.value) 
    print("myrealpath: ", args.myrealpath.value) 

    sys.exit(0)

    args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/pbuilder.json").get_argsns_dy_app()
    print(args.__app__.values)
    sys.exit(0)

    # testing value types
    args, dy_app=pkg.Options(filenpa_app="gpm.json", dy_args=dict(
        mybool=dict(values="bool_VALUE", type="bool"),
        myint=dict(values="int_VALUE", type="int"),
        myfloat=dict(values="float_VALUE", type="float"),
        mystring=dict(values="string_VALUE", type="string"),
        myjson=dict(values="json_VALUE", type="json"),
    )).get_argsns_dy_app()
    # pprint(dy_)

    # samples/main.py --mystring sdf --mybool true --myint -234 --myfloat 2.343 --myjson "{'mykey':'value'}"
    print("mybool: ", args.mybool.value) 
    print("myint: ", args.myint.value) 
    print("myfloat: ", args.myfloat.value) 
    print("mystring: ", args.mystring.value) 
    print("myjson: ", args.myjson.value) 

    # samples/main.py --myjson gpm.json
    # pprint(args.myjson.value)

    # samples/main.py --myjson "{'username': '__input__', 'password':'__hidden__' }"
    # pprint(args.myjson.value)
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
