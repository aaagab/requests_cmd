#!/usr/bin/env python3

if __name__ == "__main__":
    from pprint import pprint
    import importlib
    import json
    import os
    import sys
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    dy=pkg.getjson('{"key":"value"}')
    print(dy, dy["key"])

    dy=pkg.getjson("{'key':'value'}")
    print(dy, dy["key"])

    dy=pkg.getjson("{'nested':{'id':'', 'other': {'id':''}}}", keys=dict(id="12345"))
    pprint(dy)

    dy=pkg.getjson(dict(name="id"), keys=dict(id="12345"))
    pprint(dy)    
    
    dy=pkg.parse_dy(dict(name="id"), keys=dict(id="12345"))
    pprint(dy)

    dy=pkg.parse_dy(dict(name="id", other_name="__input__"), keys=dict(id="12345"))
    pprint(dy)

    dy=pkg.getjson("{'nested':{'user':'__input__', 'pass': '__hidden__'}}")
    pprint(dy)

    dy=pkg.getjson( os.path.join(os.path.dirname(os.path.realpath(__file__)), "gpm.json"))
    print(dy)

    dy=pkg.getjson("notfound.json", error_exit=False)
    print(dy)