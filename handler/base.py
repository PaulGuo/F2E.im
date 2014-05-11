#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import json

import tornado.web

import lib.session
import helper
import settings
from lib import utils


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.session = lib.session.Session(self.application.session_manager, self)
        self.jinja2 = self.settings.get("jinja2")
        self.jinja2 = helper.Filters(self.jinja2).register()

    @property
    def db(self):
        return self.application.db

    @property
    def picture_model(self):
        return self.application.picture_model

    @property
    def user_model(self):
        return self.application.user_model

    @property
    def topic_model(self):
        return self.application.topic_model

    @property
    def reply_model(self):
        return self.application.reply_model

    @property
    def plane_model(self):
        return self.application.plane_model

    @property
    def node_model(self):
        return self.application.node_model

    @property
    def notification_model(self):
        return self.application.notification_model

    @property
    def vote_model(self):
        return self.application.vote_model

    @property
    def favorite_model(self):
        return self.application.favorite_model

    @property
    def loader(self):
        return self.application.loader

    @property
    def mc(self):
        return self.application.mc

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return self.user_model.get_user_by_uid(int(user_id))

    def render(self, template_name, **template_vars):
        html = self.render_string(template_name, **template_vars)
        self.write(html)

    def render_string(self, template_name, **template_vars):
        template_vars["xsrf_form_html"] = self.xsrf_form_html
        template_vars["current_user"] = self.current_user
        template_vars["request"] = self.request
        template_vars["request_handler"] = self
        template_vars['settings'] = settings.app_settings
        template_vars['site_settings'] = settings.site
        template = self.jinja2.get_template(template_name)
        return template.render(**template_vars)

    def render_from_string(self, template_string, **template_vars):
        template = self.jinja2.from_string(template_string)
        return template.render(**template_vars)

    def paginator(self):
        """
        create paginator from request
        """
        data = {
            'page': self.get_argument('page', None),
            'page_size': self.get_argument('page_size', None),
            'extra_url_params': self.get_argument('extra_url_params', None),
            'pagination_display_count': self.get_argument('pagination_display_count', None),
        }
        p_data = dict()
        for k in data.keys():
            if data[k] is not None:
                p_data[k] = data[k]
        pg = utils.Paginator(**p_data)
        return pg

    def query_by_paginator(self, model, paginator):
        q = model.where('1=1').limit(paginator.skipped_count, paginator.page_size)
        records = q.select()
        paginator.total_count = q.count()
        return records

    def ajax_response(self, success, data=None, code=0):
        """
        send ajax response with format {success: true/false, data: content, code: error code of type int
        code:
        0: success:
        1: common error code which might be any kind of error
        2: login required or permission denied
        3: login required
        4: permission denied
        [5, ...): other fail error code
        """
        res = {
            'success': success,
            'data': data,  # JSON.to_json(data)
            'code': code,
        }
        self.write(json.dumps(res))

    def ajax_success(self, data=None, code=0):
        self.ajax_response(True, data, code)

    def ajax_fail(self, data=None, code=1):
        self.ajax_response(False, data, code)