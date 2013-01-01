#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

class Loader(object):
    def __init__(self, db):
        self.db = db
        self.loaded = {
            "model": {},
            "handler": {},
        }

    def use(self, name):
        name = name.split(".")
        _name = name[0]
        _type = name[1]

        if(_type == "model"):
            return self.load_model(_name)

        if(_type == "handler"):
            return self.load_handler(_name)

    def load_model(self, name):
        if(name in self.loaded["model"]):
            return self.loaded["model"][name]
        instance_name = "%s%s" % (name.capitalize(), "Model")
        self.loaded["model"][name] = __import__("model.%s" % name)
        self.loaded["model"][name] = eval('self.loaded["model"][name].%s.%s' % (name, instance_name))
        self.loaded["model"][name] = self.loaded["model"][name](self.db)
        return self.loaded["model"][name]

    def load_handler(self, name):
        if(name in self.loaded["handler"]):
            return self.loaded["handler"][name]
        instance_name = "%s%s" % (name.capitalize(), "Handle")
        self.loaded["handler"][name] = __import__("handler.%s" % name)
        self.loaded["handler"][name] = eval('self.loaded["handler"][name].%s.%s' % (name, instance_name))
        self.loaded["handler"][name] = self.loaded["handler"][name](self.loader)
        return self.loaded["handler"][name]
