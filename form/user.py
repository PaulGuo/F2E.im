#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from wtforms import TextField, validators
from lib.forms import Form

class RegisterForm(Form):
    username = TextField('Username', [
        validators.Required(message = "必须填写用户名"),
        validators.Length(min = 3, message = "用户名长度过短（3-12个字符）"),
        validators.Length(max = 12, message = "用户名长度过长（3-12个字符）"),
        validators.Regexp("^[a-zA-Z][a-zA-Z0-9_]*$", message = "用户名格式错误（英文字母开头，数字，下划线构成）"),
    ])

    email = TextField('Email', [
        validators.Required(message = "必须填写Email"),
        validators.Length(min = 4, message = "Email长度有误"),
        validators.Email(message = "Email地址无效"),
    ])

    password = TextField('Password', [
        validators.Required(message = "必须填写密码"),
        validators.Length(min = 6, message = "密码长度过短（6-64个字符）"),
        validators.Length(max = 64, message = "密码长度过长（6-64个字符）"),
        validators.EqualTo('password_confirm', message='两次输入密码不一致'),
    ])

    password_confirm = TextField('Password_confirm')

class LoginForm(Form):
    email = TextField('Email', [
        validators.Required(message = "必须填写Email"),
        validators.Length(min = 4, message = "Email长度有误"),
        validators.Email(message = "Email地址无效"),
    ])

    password = TextField('Password', [
        validators.Required(message = "必须填写密码"),
        validators.Length(min = 6, message = "密码长度过短（6-64个字符）"),
        validators.Length(max = 64, message = "密码长度过长（6-64个字符）"),
    ])

class ForgotPasswordForm(Form):
    username = TextField('Username', [
        validators.Required(message = "必须填写用户名"),
        validators.Length(min = 3, message = "用户名长度过短（3-12个字符）"),
        validators.Length(max = 12, message = "用户名长度过长（3-12个字符）"),
        validators.Regexp("^[a-zA-Z][a-zA-Z0-9_]*$", message = "用户名格式错误（英文字母开头，数字，下划线构成）"),
    ])

    email = TextField('Email', [
        validators.Required(message = "必须填写Email"),
        validators.Length(min = 4, message = "Email长度有误"),
        validators.Email(message = "Email地址无效"),
    ])

class SettingPasswordForm(Form):
    password_old = TextField('Password_old', [
        validators.Required(message = "必须填写当前密码"),
        validators.Length(min = 6, message = "密码长度过短（6-64个字符）"),
        validators.Length(max = 64, message = "密码长度过长（6-64个字符）"),
    ])

    password = TextField('Password', [
        validators.Required(message = "必须填写新密码"),
        validators.Length(min = 6, message = "密码长度过短（6-64个字符）"),
        validators.Length(max = 64, message = "密码长度过长（6-64个字符）"),
        validators.EqualTo('password_confirm', message='两次输入密码不一致'),
    ])

    password_confirm = TextField('Password_confirm')

class SettingForm(Form):
    username = TextField('Username') # readonly
    email = TextField('Email') # readonly
    nickname = TextField('Nickname', [
        validators.Optional(),
        validators.Length(min = 2, message = "昵称长度过短（2-12个字符）"),
        validators.Length(max = 12, message = "昵称长度过长（3-12个字符）"),
    ])
    signature = TextField('Signature', [
        validators.Optional(),
    ])
    location = TextField('Location', [
        validators.Optional(),
    ])
    website = TextField('Website', [
        validators.Optional(),
        validators.URL(message = "请填写合法的URL地址（如：http://f2e.im）")
    ])
    company = TextField('Company', [
        validators.Optional(),
    ])
    github = TextField('Github', [
        validators.Optional(),
    ])
    twitter = TextField('Twitter', [
        validators.Optional(),
    ])
    douban = TextField('Douban', [
        validators.Optional(),
    ])
    self_intro = TextField('Self_intro', [
        validators.Optional(),
    ])
