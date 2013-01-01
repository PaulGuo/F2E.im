#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import json

def print_JSONP(callback = "callback", data = {}):
    if(not callback): callback = "callback"
    json_data = json.JSONEncoder().encode(data)
    return "%s(%s);" % (callback, json_data)

def print_JSON(data = {}):
    json_data = json.JSONEncoder().encode(data)
    return "%s" % json_data

def dump(data = {}, callback = None):
    if(callback):
        return print_JSONP(callback, data)
    else:
        return print_JSON(data)

