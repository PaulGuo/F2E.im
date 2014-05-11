#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.
from __future__ import print_function
import logging

from lib.query import Query
from lib import qiniu_util
from lib import utils


class PictureModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "picture"
        super(PictureModel, self).__init__()

    def create_from_files(self, files, user=None):
        for file in files:
            content_type = file.get('content_type')
            filename = file.get('filename')
            body = file.get('body')
            key = utils.random_str(30)
            ret, err = qiniu_util.upload_binary_stream(key, body, content_type)
            if err:
                logging.log(logging.ERROR, err)
                print(err)
                continue
            pic = {
                'creator_id': int(user['uid']) if user else None,
                'service': 'qiniu',
                'store_key': key,
            }
            if pic.get('id', None) is not None:
                pic['id'] = int(pic['id'])
            self.data(pic).add()
            yield pic

    def gen_picture_url(self, info):
        return qiniu_util.get_public_url_by_key(info['store_key'])