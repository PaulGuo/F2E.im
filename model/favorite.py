#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import time
from lib.query import Query

class FavoriteModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "favorite"
        super(FavoriteModel, self).__init__()

    def add_new_favorite(self, favorite_info):
        return self.data(favorite_info).add()

    def get_favorite_by_topic_id_and_owner_user_id(self, topic_id, owner_user_id):
        where = "involved_topic_id = %s AND owner_user_id = %s" % (topic_id, owner_user_id)
        return self.where(where).find()

    def get_user_favorite_count(self, owner_user_id):
        where = "owner_user_id = %s" % owner_user_id
        return self.where(where).count()

    def get_user_all_favorites(self, uid, num = 16, current_page = 1):
        where = "favorite.owner_user_id = %s" % uid
        join = "LEFT JOIN topic ON favorite.involved_topic_id = topic.id \
                LEFT JOIN user AS author_user ON topic.author_id = author_user.uid \
                LEFT JOIN node ON topic.node_id = node.id \
                LEFT JOIN user AS last_replied_user ON topic.last_replied_by = last_replied_user.uid"
        order = "favorite.id DESC"
        field = "topic.*, \
                author_user.username as author_username, \
                author_user.nickname as author_nickname, \
                author_user.avatar as author_avatar, \
                author_user.uid as author_uid, \
                author_user.reputation as author_reputation, \
                node.name as node_name, \
                node.slug as node_slug, \
                last_replied_user.username as last_replied_username, \
                last_replied_user.nickname as last_replied_nickname"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def cancel_exist_favorite_by_id(self, favorite_id):
        where = "id = %s" %  favorite_id
        return self.where(where).delete()

