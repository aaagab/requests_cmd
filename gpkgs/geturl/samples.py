#!/usr/bin/env python3

if __name__ == "__main__":
    import importlib
    import os
    import sys
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    os.environ["NEW_HOSTNAME"]="https://webgui.com/"
    url=pkg.geturl(
        "departments",
        alias="new_hostname",
    )
    print(url)

    url=pkg.geturl(
        "departments",
        hostname_path="https://librocket.com",
    )
    print(url)

    url=pkg.geturl(
        "departments",
        hostname_path="https://librocket.com",
        params=dict(fruit="apple",meal="dessert",region="greenland",code=33)
    )
    print(url)

    try:
        print()
        print("showing error message")
        url=pkg.geturl(
            "departments",
            alias="hostname_url",
            direpa_project=r"A:\wrk\e\example"
        )
        print(url)
    except:
        print()

    try:
        print()
        print("error message params")
        url=pkg.geturl(
            "departments",
            hostname_path="https://librocket.com",
            params=[],
        )
        print(url)
    except:
        print()
        
    try:
        url=pkg.geturl(
            "departments",
            alias="hostname_url",
            direpa_project=r"A:\wrk\e\example\1\src"
        )
        print(url)
    except:
        print("This example does not apply in you context")