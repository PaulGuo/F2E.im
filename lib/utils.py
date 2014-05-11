#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from __future__ import print_function, unicode_literals
import re


def find_mentions(content):
    regex = re.compile(r"@(?P<username>\w+)(\s|$)", re.I)
    return [m.group("username") for m in regex.finditer(content)]


import random
import string
import hashlib
import os
from easy_json import JSON


def encrypt_password(password, salt):
    salt = salt.strip().encode('UTF-8')
    password = password.strip().encode('UTF-8')
    p1 = hashlib.sha256(password).hexdigest()
    p2 = p1.encode('UTF-8') + salt
    return hashlib.sha256(p2).hexdigest()


def random_str(length=20):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:length])


def split_path(path):
    """
    split path to list of items
    eg. /Users/abc/test.txt would be splited to ['Users', 'abc', 'test.txt']
    """
    items = []
    while True:
        path, folder = os.path.split(path)
        if folder != '':
            items.append(folder)
        else:
            if path != '':
                items.append(path)
            break
    items.reverse()
    return items


def get_server_address(request):
    from .. import settings

    if settings.SERVER_HOST is not None:
        return settings.SERVER_HOST
    host = request.host
    if host.find(':') > 0:
        host = host[:host.find(':')]
    return host


def list_strip(lst):
    return filter(lambda x: len(x) > 0, map(lambda x: x.strip(), lst))


def safeunicode(obj, encoding='utf-8'):
    r"""
    Converts any given object to unicode string.

        >>> safeunicode('hello')
        u'hello'
        >>> safeunicode(2)
        u'2'
        >>> safeunicode('\xe1\x88\xb4')
        u'\u1234'
    """
    t = type(obj)
    if t is unicode:
        return obj
    elif t is str:
        return obj.decode(encoding, 'ignore')
    elif t in [int, float, bool]:
        return unicode(obj)
    elif hasattr(obj, '__unicode__') or isinstance(obj, unicode):
        try:
            return unicode(obj)
        except Exception as e:
            return u""
    else:
        return str(obj).decode(encoding, 'ignore')


def safe_utf8(s):
    return safeunicode(s).encode('UTF-8')


def make_sure_between(val, start=None, end=None):
    """
    make sure start <= val <= end, if start/end is not None
    """
    if start is not None:
        if val < start:
            return start
    if end is not None:
        if val > end:
            return end
    return val


class Paginator(object):
    def __init__(self, **kwargs):
        self.page = make_sure_between(int(kwargs.get('page', 1)), start=1)
        self.page_size = make_sure_between(int(kwargs.get('page_size', 10)), start=1)
        self.pagination_display_count = make_sure_between(int(kwargs.get('pagination_display_count', 5)), start=1)
        self.extra_url_params = kwargs.get('extra_url_params', None)
        self.total_count = 0

    @property
    def to_json(self):
        return JSON.to_json(self)

    @property
    def skipped_count(self):
        return (self.page - 1) * self.page_size

    @property
    def page_counts(self):
        """
        total counts of pages
        """
        return 1 + (self.total_count - 1) / self.page_size

    @property
    def pagination_html(self):
        result = "<ul class=\"pagination\">"
        total_pages = self.page_counts
        self.page = make_sure_between(self.page, start=1, end=total_pages)
        start_page = make_sure_between(self.page - self.pagination_display_count / 2, start=1)
        end_page = make_sure_between(start_page + self.pagination_display_count - 1, end=total_pages)
        tmp_url = None
        for i in range(start_page, end_page + 1):
            if i == start_page:
                tmp_url = "?page=1&page_size=%d" % self.page_size
                if self.extra_url_params:
                    tmp_url += self.extra_url_params
                result += "<li><a href='%s'>&laquo;</a></li>" % tmp_url
                if start_page <= 1:
                    result += "<li class=\"disabled\"><a href=\"#\">&laquo;</a></li>"
                else:
                    tmp_url = "?page=%d&page_size=%d" % (start_page - self.pagination_display_count, self.page_size)
                    if self.extra_url_params:
                        tmp_url += self.extra_url_params
                    result += "<li class=\"\"><a href='%s'>&laquo;</a></li>" % tmp_url
            if i == self.page:
                tmp_url = "?page=%d&page_size=%d"
                if self.extra_url_params:
                    tmp_url += self.extra_url_params
                result += "<li class=\"active\"><a href='%s'>%d<span class=\"sr-only\">(current)</span></a></li>" \
                          % (tmp_url, i)
            else:
                tmp_url = "?page=%d&page_size=%d" % (i, self.page_size)
                if self.extra_url_params:
                    tmp_url += self.extra_url_params
                result += "<li><a href='%s'>%d</a></li>" % (tmp_url, i)
            if i == end_page:
                if end_page >= total_pages:
                    result += "<li class=\"disabled\"><a href=\"#\">&raquo;</a></li>"
                else:
                    tmp_url = "?page=%d&page_size=%d" % (end_page + self.pagination_display_count, self.page_size)
                    if self.extra_url_params:
                        tmp_url += self.extra_url_params
                    result += "<li class=\"\"><a href='%s'>&raquo;</a></li>" % tmp_url
                tmp_url = "?page=%d&page_size=%d" % (total_pages, self.page_size)
                if self.extra_url_params:
                    tmp_url += self.extra_url_params
                result += "<li><a href='%s'>&raquo;</a></li>" % tmp_url
        result += "<li>Total %d Page</li>" % total_pages
        result += "</ul>"
        return result