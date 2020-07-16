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

    print(pkg.getpath("/sys", "directory"))
    print(pkg.getpath("gpkgs", "directory"))
    print(pkg.getpath("gpm.json", "file"))
    print(pkg.getpath("gpm.json", "realpath"))
    print(pkg.getpath("apple/pine/flavor.txt", "virtualpath"))
    print(pkg.getpath("../../apple/pine/flavor.txt", "virtualpath"))

    try:
        print(pkg.getpath("gpm.json", "directory"))
    except:
        pass
