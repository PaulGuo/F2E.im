#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import re

def find_mentions(content):
    regex = re.compile(r"@(?P<username>\w+)(\s|$)", re.I)
    return [m.group("username") for m in regex.finditer(content)]

