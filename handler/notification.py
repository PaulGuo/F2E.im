#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import uuid
import hashlib
import Image
import StringIO
import time
import json
import re
import urllib2
import tornado.web
import lib.jsonp
import pprint

from base import *
from lib.variables import *
from form.topic import *
from lib.variables import gen_random
from lib.xss import XssCleaner
from lib.utils import find_mentions

class ListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["user_info"]["counter"] = {
            "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
            "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
            "notifications": self.notification_model.get_user_unread_notification_count(user_info["uid"]),
            "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
        }
        template_variables["notifications"] = self.notification_model.get_user_all_notifications(user_info["uid"], current_page = page)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random

        # mark user unread notifications as read
        self.notification_model.mark_user_unread_notification_as_read(user_info["uid"])

        self.render("notification/notifications.html", **template_variables)

