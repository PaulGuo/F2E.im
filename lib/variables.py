#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import time
import re
import random

from htmlentity import unescape
from HTMLParser import HTMLParser

def date(timestamp, formatter):
    return time.strftime(formatter, time.gmtime(float(timestamp)))

def build_uri(uri, param, value):
    regx = re.compile("[\?&](%s=[^\?&]*)" % param)
    find = regx.search(uri)
    split = "&" if re.search(r"\?", uri) else "?"
    if not find: return "%s%s%s=%s" % (uri, split, param, value)
    return re.sub(find.group(1), "%s=%s" % (param, value), uri)

def strip_tags(html):
    html = html.strip()
    html = html.strip("\n")
    result = []
    parse = HTMLParser()
    parse.handle_data = result.append
    parse.feed(html)
    parse.close()
    return "".join(result)

def gen_random():
    return random.random()

template_variables = {}
template_variables["build_uri"] = build_uri
template_variables["date"] = date
template_variables["strip_tags"] = strip_tags

