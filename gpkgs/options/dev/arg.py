#!/usr/bin/env python3
class Arg():
    def __init__(self, name, dy):
        self.alias=None
        self.default_short_alias=None
        self.default_long_alias=None
        self.default_alias=None
        self.name=name
        self.dy=dy
        self.here=False
        self.value=None
        self.values=[]
