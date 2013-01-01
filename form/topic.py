#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from wtforms import TextField, HiddenField, validators
from lib.forms import Form

class ReplyForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写回复内容"),
    ])

    tid = TextField('Tid', [
        validators.Required(message = "要回复的帖子不明确"),
    ])

class CreateForm(Form):
    title = TextField('Title', [
        validators.Required(message = "请填写帖子标题"),
        validators.Length(min = 3, message = "帖子标题长度过短（3-56个字符）"),
        validators.Length(max = 56, message = "帖子标题长度过长（3-56个字符）"),
    ])

    content = TextField('Content', [
        validators.Required(message = "请填写帖子内容"),
    ])

class ReplyEditForm(Form):
    content = TextField('Content', [
        validators.Required(message = "请填写回复内容"),
    ])
