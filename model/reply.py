#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import time
from lib.query import Query

class ReplyModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "reply"
        super(ReplyModel, self).__init__()

    def get_all_replies_by_topic_id(self, topic_id, num = 16, current_page = 1):
        where = "topic_id = %s" % topic_id
        join = "LEFT JOIN user ON reply.author_id = user.uid"
        order = "id ASC"
        field = "reply.*, \
                user.username as author_username, \
                user.nickname as author_nickname, \
                user.avatar as author_avatar"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def add_new_reply(self, reply_info):
        return self.data(reply_info).add()

    def get_user_all_replies_count(self, uid):
        where = "author_id = %s" % uid
        return self.where(where).count()

    def get_all_replies_count(self):
        return self.count()

    def get_user_all_replies(self, uid, num = 16, current_page = 1):
        where = "reply.author_id = %s" % uid
        join = "LEFT JOIN topic ON reply.topic_id = topic.id \
                LEFT JOIN user AS topic_author_user ON topic.author_id = topic_author_user.uid"
        order = "reply.id DESC"
        field = "reply.*, \
                topic.title as topic_title, \
                topic_author_user.username as topic_author_username, \
                topic_author_user.nickname as topic_author_nickname, \
                topic_author_user.avatar as topic_author_avatar"
        group = "reply.topic_id"
        return self.where(where).field(field).join(join).group(group).order(order).pages(current_page = current_page, list_rows = num)

    def get_user_reply_by_topic_id(self, uid, topic_id):
        where = "author_id = %s AND topic_id = %s" % (uid, topic_id)
        return self.where(where).find()

    def get_reply_by_reply_id(self, reply_id):
        where = "id = %s" % reply_id
        return self.where(where).find()

    def update_reply_by_reply_id(self, reply_id, reply_info):
        where = "id = %s" % reply_id
        return self.where(where).data(reply_info).save()

