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
import math
import datetime

from base import *
from lib.variables import *
from form.topic import *
from lib.variables import gen_random
from lib.xss import XssCleaner
from lib.utils import find_mentions

class IndexHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "notifications": self.notification_model.get_user_unread_notification_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

        template_variables["status_counter"] = {
            "users": self.user_model.get_all_users_count(),
            "nodes": self.node_model.get_all_nodes_count(),
            "topics": self.topic_model.get_all_topics_count(),
            "replies": self.reply_model.get_all_replies_count(),
        }
        template_variables["topics"] = self.topic_model.get_all_topics(current_page = page)
        template_variables["planes"] = self.plane_model.get_all_planes_with_nodes()
        template_variables["hot_nodes"] = self.node_model.get_all_hot_nodes()
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/topics.html", **template_variables)

class NodeTopicsHandler(BaseHandler):
    def get(self, node_slug, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }
        template_variables["topics"] = self.topic_model.get_all_topics_by_node_slug(current_page = page, node_slug = node_slug)
        template_variables["node"] = self.node_model.get_node_by_node_slug(node_slug)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/node_topics.html", **template_variables)

class ViewHandler(BaseHandler):
    def get(self, topic_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }
        template_variables["gen_random"] = gen_random
        template_variables["topic"] = self.topic_model.get_topic_by_topic_id(topic_id)
        template_variables["replies"] = self.reply_model.get_all_replies_by_topic_id(topic_id, current_page = page)
        template_variables["active_page"] = "topic"

        # update topic reply_count and hits

        self.topic_model.update_topic_by_topic_id(topic_id, {
            "reply_count": template_variables["replies"]["page"]["total"],
            "hits": (template_variables["topic"]["hits"] or 0) + 1,
        })

        self.render("topic/view.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = ReplyForm(self)

        if not form.validate():
            self.get(form.tid.data, {"errors": form.errors})
            return

        # continue while validate succeed

        topic_info = self.topic_model.get_topic_by_topic_id(form.tid.data)
        replied_info = self.reply_model.get_user_reply_by_topic_id(self.current_user["uid"], form.tid.data)

        if(not topic_info):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_topic_info"] = [u"要回复的帖子不存在"]
            self.get(template_variables)
            return
        
        reply_info = {
            "author_id": self.current_user["uid"],
            "topic_id": form.tid.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.reply_model.add_new_reply(reply_info)

        # update topic last_replied_by and last_replied_time

        self.topic_model.update_topic_by_topic_id(form.tid.data, {
            "last_replied_by": self.current_user["uid"],
            "last_replied_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        # create reply notification

        if not self.current_user["uid"] == topic_info["author_id"]:
            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 1, # 0: mention, 1: reply
                "involved_user_id": topic_info["author_id"],
                "involved_topic_id": form.tid.data,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # create @username notification

        for username in set(find_mentions(form.content.data)):
            mentioned_user = self.user_model.get_user_by_username(username)

            if not mentioned_user:
                continue

            if mentioned_user["uid"] == self.current_user["uid"]:
                continue

            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 0, # 0: mention, 1: reply
                "involved_user_id": mentioned_user["uid"],
                "involved_topic_id": form.tid.data,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # update reputation of topic author
        if not self.current_user["uid"] == topic_info["author_id"] and not replied_info:
            topic_time_diff = datetime.datetime.now() - topic_info["created"]
            reputation = topic_info["author_reputation"] or 0
            reputation = reputation + 2 * math.log(self.current_user["reputation"] or 0 + topic_time_diff.days + 10, 10)
            self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})

        self.get(form.tid.data)

class CreateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, node_slug = None, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["user_info"]["counter"] = {
            "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
            "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
            "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
        }
        template_variables["gen_random"] = gen_random
        template_variables["node_slug"] = node_slug
        template_variables["active_page"] = "topic"
        self.render("topic/create.html", **template_variables)

    @tornado.web.authenticated
    def post(self, node_slug = None, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = CreateForm(self)

        if not form.validate():
            self.get(node_slug, {"errors": form.errors})
            return

        # continue while validate succeed

        node = self.node_model.get_node_by_node_slug(node_slug)
        
        topic_info = {
            "author_id": self.current_user["uid"],
            "title": form.title.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "node_id": node["id"],
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            "reply_count": 0
        }

        reply_id = self.topic_model.add_new_topic(topic_info)

        # update reputation of topic author
        reputation = self.current_user["reputation"] or 0
        reputation = reputation - 5
        reputation = 0 if reputation < 0 else reputation
        self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})
        self.redirect("/")

class EditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, topic_id, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["user_info"]["counter"] = {
            "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
            "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
            "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
        }
        template_variables["topic"] = self.topic_model.get_topic_by_topic_id(topic_id)
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "topic"
        self.render("topic/edit.html", **template_variables)

    @tornado.web.authenticated
    def post(self, topic_id, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = CreateForm(self)

        if not form.validate():
            self.get(topic_id, {"errors": form.errors})
            return

        # continue while validate succeed

        topic_info = self.topic_model.get_topic_by_topic_id(topic_id)

        if(not topic_info["author_id"] == self.current_user["uid"]):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_permission"] = [u"没有权限修改该主题"]
            self.get(topic_id, template_variables)
            return

        update_topic_info = {
            "title": form.title.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "updated": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.topic_model.update_topic_by_topic_id(topic_id, update_topic_info)

        # update reputation of topic author
        reputation = topic_info["author_reputation"] or 0
        reputation = reputation - 2
        reputation = 0 if reputation < 0 else reputation
        self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})
        self.redirect("/t/%s" % topic_id)

class ProfileHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        if(re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

        '''
        if user_info["github"]:
            github_repos = self.mc.get(str("%s_github_repos" % user_info["github"])) or json.JSONDecoder().decode(urllib2.urlopen('https://api.github.com/users/%s/repos' % user_info["github"]).read())
            self.mc.set(str("%s_github_repos" % user_info["github"]), github_repos)
            template_variables["github_repos"] = github_repos
        '''

        template_variables["topics"] = self.topic_model.get_user_all_topics(user_info["uid"], current_page = page)
        template_variables["replies"] = self.reply_model.get_user_all_replies(user_info["uid"], current_page = page)
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "_blank"
        self.render("topic/profile.html", **template_variables)

class VoteHandler(BaseHandler):
    def get(self, template_variables = {}):
        topic_id = int(self.get_argument("topic_id"))
        topic_info = self.topic_model.get_topic_by_topic_id(topic_id)

        if not topic_info:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "topic_not_exist",
            }))
            return

        if self.current_user["uid"] == topic_info["author_id"]:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "can_not_vote_your_topic",
            }))
            return

        if self.vote_model.get_vote_by_topic_id_and_trigger_user_id(topic_id, self.current_user["uid"]):
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "already_voted",
            }))
            return

        self.vote_model.add_new_vote({
            "trigger_user_id": self.current_user["uid"],
            "involved_type": 0, # 0: topic, 1: reply
            "involved_user_id": topic_info["author_id"],
            "involved_topic_id": topic_id,
            "status": 0,
            "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        self.write(lib.jsonp.print_JSON({
            "success": 1,
            "message": "thanks_for_your_vote",
        }))

        # update reputation of topic author
        topic_time_diff = datetime.datetime.now() - topic_info["created"]
        reputation = topic_info["author_reputation"] or 0
        reputation = reputation + 2 * math.log(self.current_user["reputation"] or 0 + topic_time_diff.days + 10, 10)
        self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})

class UserTopicsHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        if(re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }
        template_variables["topics"] = self.topic_model.get_user_all_topics(user_info["uid"], current_page = page)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/user_topics.html", **template_variables)

class UserRepliesHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        if(re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }
        template_variables["replies"] = self.reply_model.get_user_all_replies(user_info["uid"], current_page = page)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/user_replies.html", **template_variables)

class UserFavoritesHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        if(re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }
        template_variables["favorites"] = self.favorite_model.get_user_all_favorites(user_info["uid"], current_page = page)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/user_favorites.html", **template_variables)

class ReplyEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, reply_id, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["user_info"]["counter"] = {
            "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
            "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
            "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
        }
        template_variables["reply"] = self.reply_model.get_reply_by_reply_id(reply_id)
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "topic"
        self.render("topic/reply_edit.html", **template_variables)

    @tornado.web.authenticated
    def post(self, reply_id, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = ReplyEditForm(self)

        if not form.validate():
            self.get(reply_id, {"errors": form.errors})
            return

        # continue while validate succeed

        reply_info = self.reply_model.get_reply_by_reply_id(reply_id)

        if(not reply_info["author_id"] == self.current_user["uid"]):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_permission"] = [u"没有权限修改该回复"]
            self.get(reply_id, template_variables)
            return

        update_reply_info = {
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "updated": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.reply_model.update_reply_by_reply_id(reply_id, update_reply_info)

        # update reputation of topic author
        reputation = self.current_user["reputation"] or 0
        reputation = reputation - 2
        reputation = 0 if reputation < 0 else reputation
        self.user_model.set_user_base_info_by_uid(reply_info["author_id"], {"reputation": reputation})
        self.redirect("/t/%s" % reply_info["topic_id"])

class FavoriteHandler(BaseHandler):
    def get(self, template_variables = {}):
        topic_id = int(self.get_argument("topic_id"))
        topic_info = self.topic_model.get_topic_by_topic_id(topic_id)

        if not topic_info:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "topic_not_exist",
            }))
            return

        if self.current_user["uid"] == topic_info["author_id"]:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "can_not_favorite_your_topic",
            }))
            return

        if self.favorite_model.get_favorite_by_topic_id_and_owner_user_id(topic_id, self.current_user["uid"]):
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "already_favorited",
            }))
            return

        self.favorite_model.add_new_favorite({
            "owner_user_id": self.current_user["uid"],
            "involved_type": 0, # 0: topic, 1: reply
            "involved_topic_id": topic_id,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        self.write(lib.jsonp.print_JSON({
            "success": 1,
            "message": "favorite_success",
        }))

        # update reputation of topic author
        topic_time_diff = datetime.datetime.now() - topic_info["created"]
        reputation = topic_info["author_reputation"] or 0
        reputation = reputation + 2 * math.log(self.current_user["reputation"] or 0 + topic_time_diff.days + 10, 10)
        self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})

