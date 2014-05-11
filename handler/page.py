#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.
from __future__ import print_function

import tornado.web
from tornado import gen

from base import *
import tasks


class AboutHandler(BaseHandler):
    def get(self, template_variables={}):
        self.render("page/about.html", **template_variables)


class PictureIframeUploadHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        # TODO: avoid upload too frequently and limit total and max size of pictures the current user can upload
        user = self.current_user
        callback = self.get_body_argument('callback', 'callback')
        files = self.request.files['files[]']
        response = yield gen.Task(tasks.upload_pictures.apply_async, args=[files, user])
        pictures = response.result
        # pictures = self.picture_model.create_from_files(files, user)
        for pic in pictures:
            self.picture_model.data(pic).add()
        pics_data = map(lambda pic: {'store_key': pic['store_key'], 'url': self.picture_model.gen_picture_url(pic)},
                        pictures)
        result = '<script>parent.%s(%s)</script>' % (callback, json.dumps(pics_data))
        self.write(result)
        self.finish()
