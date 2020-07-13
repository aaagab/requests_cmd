#!/usr/bin/env python3
import sys

from ..gpkgs import message as msg

class Node():
    def __init__(self, arg, parent=None):
        self.arg=arg
        self.parent=parent
        self.parents={}
        self.is_leaf=True
        self.nodes=[]
        self.name=self.arg.name

        if self.parent is None:
            self.root=self
            self.is_root=True
            self.level=1
        else:
            self.root=self.parent.root
            self.is_root=False
            self.parent.is_leaf=False
            self.level=self.parent.level+1
            self.parent.nodes.append(self)
            for p, value in self.parent.parents.items():
                self.parents.update({p:value})
            self.parents[self.parent.name]=self.parent
            if self.name in self.parents:
                msg.error(
                    "Error halting problem during nested arg recursion",
                    "{}".format(get_parents(self)),
                    "You can either:",
                    "- Remove '{}' from '{}'".format(self.name, self.parents[self.name].parent.name),
                    "- Remove '{}' from '{}'".format(self.name, self.parent.name))
                if self.arg.dy["args"] is not None:
                    msg.error("- Remove nested arg(s) '{}' from '{}'".format(self.arg.dy["args"], self.name,))
                sys.exit(1)

def get_parents(arg):
    text=arg.name
    args=[arg.name]
    while arg.parent is not None:
        arg=arg.parent
        args.insert(0, arg.name)

    return " > ".join(args)