#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from lib.query import Query

class UserModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "user"
        super(UserModel, self).__init__()

    def get_user_by_uid(self, uid):
        where = "uid = %s" % uid
        return self.where(where).find()

    def get_user_by_email(self, email):
        where = "email = '%s'" % email
        return self.where(where).find()

    def get_user_by_username(self, username):
        where = "username = '%s'" % username
        return self.where(where).find()

    def get_user_by_nickname(self, nickname):
        where = "nickname = '%s'" % nickname
        return self.where(where).find()

    def get_users_by_email_except_uid(self, email, uid):
        where = "email = '%s' AND uid <> %s" % (email, uid)
        return self.where(where).select()

    def get_users_by_nickname_except_uid(self, nickname, uid):
        where = "nickname = '%s' AND uid <> %s" % (nickname, uid)
        return self.where(where).select()

    def get_user_by_email_and_uid(self, email, uid):
        where = "email = '%s' AND uid = '%s'" % (email, uid)
        return self.where(where).find()

    def get_user_by_email_and_password(self, email, secure_password):
        where = "email = '%s' AND password = '%s'" % (email, secure_password)
        return self.where(where).find()

    def get_user_by_email_and_username(self, email, username):
        where = "email = '%s' AND username = '%s'" % (email, username)
        return self.where(where).find()

    def get_user_by_email_and_nickname(self, email, nickname):
        where = "email = '%s' AND nickname = '%s'" % (email, nickname)
        return self.where(where).find()

    def set_user_base_info_by_uid(self, uid, info):
        where = "uid = %s" % uid
        return self.data(info).where(where).save()

    def set_user_avatar_by_uid(self, uid, avatar_name):
        where = "uid = %s" % uid
        return self.data({
            "avatar": avatar_name
        }).where(where).save()

    def set_user_password_by_uid(self, uid, secure_password):
        where = "uid = %s" % uid
        return self.data({
            "password": secure_password
        }).where(where).save()

    def add_new_user(self, info):
        return self.data(info).add()

    def get_user_info_by_open_id(self, openId, source = 0):
        where = "openid='%s' AND source=%s" % (openId, source)
        return self.where(where).find()

    def get_users_by_latest(self, num = 16):
        order = "uid DESC"
        return self.order(order).limit(num).pages(list_rows = num)

    def get_all_users_count(self):
        return self.count()

    def get_users_by_last_login(self, num = 16):
        order = "last_login DESC"
        return self.order(order).limit(num).pages(list_rows = num)

