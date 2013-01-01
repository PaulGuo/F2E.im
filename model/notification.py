#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import time
from lib.query import Query

class NotificationModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "notification"
        super(NotificationModel, self).__init__()

    def add_new_notification(self, notification_info):
        return self.data(notification_info).add()

    def get_user_unread_notification_count(self, uid):
        where = "status = 0 AND involved_user_id = %s" % uid
        return self.where(where).count()

    def get_user_all_notifications(self, uid, num = 16, current_page = 1):
        where = "involved_user_id = %s" % uid
        join = "LEFT JOIN user AS trigger_user ON notification.trigger_user_id = trigger_user.uid \
                LEFT JOIN topic AS involved_topic ON notification.involved_topic_id = involved_topic.id \
                LEFT JOIN user AS involved_user ON notification.involved_user_id = involved_user.uid"
        order = "id DESC"
        field = "notification.*, \
                trigger_user.username as trigger_username, \
                trigger_user.nickname as trigger_nickname, \
                trigger_user.avatar as trigger_avatar, \
                trigger_user.uid as trigger_uid, \
                involved_topic.title as involved_topic_title, \
                involved_user.username as involved_username, \
                involved_user.nickname as involved_nickname, \
                involved_user.avatar as involved_avatar"
        return self.where(where).join(join).field(field).order(order).pages(current_page = current_page, list_rows = num)

    def mark_user_unread_notification_as_read(self, uid):
        where = "status = 0 AND involved_user_id = %s" % uid
        return self.where(where).data({"status": 1}).save()

