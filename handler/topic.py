#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.
from __future__ import print_function
import hashlib
import math
import datetime

import tornado.web

import lib.jsonp
from base import *
from lib.variables import *
from form.topic import *
from lib.variables import gen_random
from lib.utils import find_mentions


class IndexHandler(BaseHandler):
    def get(self, template_variables={}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                user_info["uid"]);

        template_variables["status_counter"] = {
            "users": self.user_model.get_all_users_count(),
            "nodes": self.node_model.get_all_nodes_count(),
            "topics": self.topic_model.get_all_topics_count(),
            "replies": self.reply_model.get_all_replies_count(),
        }
        template_variables["topics"] = self.topic_model.get_all_topics(current_page=page)
        template_variables["planes"] = self.plane_model.get_all_planes_with_nodes()
        template_variables["hot_nodes"] = self.node_model.get_all_hot_nodes()
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/topics.html", **template_variables)


class NodeTopicsHandler(BaseHandler):
    def get(self, node_slug, template_variables={}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                user_info["uid"]);

        template_variables["topics"] = self.topic_model.get_all_topics_by_node_slug(current_page=page,
                                                                                    node_slug=node_slug)
        template_variables["node"] = self.node_model.get_node_by_node_slug(node_slug)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/node_topics.html", **template_variables)


class ViewHandler(BaseHandler):
    def get(self, topic_id, template_variables={}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                user_info["uid"]);
            template_variables["topic_favorited"] = self.favorite_model.get_favorite_by_topic_id_and_owner_user_id(
                topic_id, user_info["uid"]);

        template_variables["gen_random"] = gen_random
        template_variables["topic"] = self.topic_model.get_topic_by_topic_id(topic_id)

        # check reply count and cal current_page if `p` not given
        reply_num = 106
        reply_count = template_variables["topic"]["reply_count"]
        reply_last_page = (reply_count / reply_num + (reply_count % reply_num and 1)) or 1
        page = int(self.get_argument("p", reply_last_page))
        template_variables["reply_num"] = reply_num
        template_variables["current_page"] = page

        template_variables["replies"] = self.reply_model.get_all_replies_by_topic_id(topic_id, current_page=page,
                                                                                     num=reply_num)
        template_variables["active_page"] = "topic"

        # update topic reply_count and hits

        self.topic_model.update_topic_by_topic_id(topic_id, {
            "reply_count": template_variables["replies"]["page"]["total"],
            "hits": (template_variables["topic"]["hits"] or 0) + 1,
        })

        self.render("topic/view.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables={}):
        template_variables = {}

        # validate the fields

        form = ReplyForm(self)

        if not form.validate():
            self.get(form.tid.data, {"errors": form.errors})
            return

        # continue while validate succeed

        topic_info = self.topic_model.get_topic_by_topic_id(form.tid.data)
        replied_info = self.reply_model.get_user_last_reply_by_topic_id(self.current_user["uid"], form.tid.data)

        if (not topic_info):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_topic_info"] = [u"要回复的帖子不存在"]
            self.get(form.tid.data, template_variables)
            return

        if (replied_info):
            last_replied_fingerprint = hashlib.sha1(
                str(replied_info.topic_id) + str(replied_info.author_id) + replied_info.content).hexdigest()
            new_replied_fingerprint = hashlib.sha1(
                str(form.tid.data) + str(self.current_user["uid"]) + form.content.data).hexdigest()

            if last_replied_fingerprint == new_replied_fingerprint:
                template_variables["errors"] = {}
                template_variables["errors"]["duplicated_reply"] = [u"回复重复提交"]
                self.get(form.tid.data, template_variables)
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
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        # create reply notification

        if not self.current_user["uid"] == topic_info["author_id"]:
            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 1,  # 0: mention, 1: reply
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

            if mentioned_user["uid"] == topic_info["author_id"]:
                continue

            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 0,  # 0: mention, 1: reply
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

        # self.get(form.tid.data)
        self.redirect("/t/%s#reply%s" % (form.tid.data, topic_info["reply_count"] + 1))


class CreateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, node_slug=None, template_variables={}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["user_info"]["counter"] = {
            "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
            "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
            "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
        }

        template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
            user_info["uid"]);
        template_variables["gen_random"] = gen_random
        template_variables["node_slug"] = node_slug
        template_variables["active_page"] = "topic"
        self.render("topic/create.html", **template_variables)

    @tornado.web.authenticated
    def post(self, node_slug=None, template_variables={}):
        template_variables = {}

        # validate the fields

        form = CreateForm(self)

        if not form.validate():
            self.get(node_slug, {"errors": form.errors})
            return

        # continue while validate succeed

        node = self.node_model.get_node_by_node_slug(node_slug)
        last_created = self.topic_model.get_user_last_created_topic(self.current_user["uid"])

        if last_created:
            last_created_fingerprint = hashlib.sha1(
                last_created.title + last_created.content + str(last_created.node_id)).hexdigest()
            new_created_fingerprint = hashlib.sha1(form.title.data + form.content.data + str(node["id"])).hexdigest()

            if last_created_fingerprint == new_created_fingerprint:
                template_variables["errors"] = {}
                template_variables["errors"]["duplicated_topic"] = [u"帖子重复提交"]
                self.get(node_slug, template_variables)
                return

        topic_info = {
            "author_id": self.current_user["uid"],
            "title": form.title.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "node_id": node["id"],
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            "reply_count": 0,
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
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
    def get(self, topic_id, template_variables={}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["user_info"]["counter"] = {
            "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
            "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
            "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
        }

        template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
            user_info["uid"]);
        template_variables["topic"] = self.topic_model.get_topic_by_topic_id(topic_id)
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "topic"
        self.render("topic/edit.html", **template_variables)

    @tornado.web.authenticated
    def post(self, topic_id, template_variables={}):
        template_variables = {}

        # validate the fields

        form = CreateForm(self)

        if not form.validate():
            self.get(topic_id, {"errors": form.errors})
            return

        # continue while validate succeed

        topic_info = self.topic_model.get_topic_by_topic_id(topic_id)

        if (not topic_info["author_id"] == self.current_user["uid"]):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_permission"] = [u"没有权限修改该主题"]
            self.get(topic_id, template_variables)
            return

        update_topic_info = {
            "title": form.title.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "updated": time.strftime('%Y-%m-%d %H:%M:%S'),
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.topic_model.update_topic_by_topic_id(topic_id, update_topic_info)

        # update reputation of topic author
        reputation = topic_info["author_reputation"] or 0
        reputation = reputation - 2
        reputation = 0 if reputation < 0 else reputation
        self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})
        self.redirect("/t/%s" % topic_id)


class ProfileHandler(BaseHandler):
    def get(self, user, template_variables={}):
        if (re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        if not user_info:
            self.write_error(404)
            return

        current_user = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

        if (current_user):
            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                current_user["uid"]);

        '''
        if user_info["github"]:
            github_repos = self.mc.get(str("%s_github_repos" % user_info["github"])) or json.JSONDecoder().decode(urllib2.urlopen('https://api.github.com/users/%s/repos' % user_info["github"]).read())
            self.mc.set(str("%s_github_repos" % user_info["github"]), github_repos)
            template_variables["github_repos"] = github_repos
        '''

        template_variables["topics"] = self.topic_model.get_user_all_topics(user_info["uid"], current_page=page)
        template_variables["replies"] = self.reply_model.get_user_all_replies(user_info["uid"], current_page=page)
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "_blank"
        self.render("topic/profile.html", **template_variables)


class VoteHandler(BaseHandler):
    def get(self, template_variables={}):
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
            "involved_type": 0,  # 0: topic, 1: reply
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
    def get(self, user, template_variables={}):
        if (re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        current_user = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

        if (current_user):
            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                current_user["uid"]);

        template_variables["topics"] = self.topic_model.get_user_all_topics(user_info["uid"], current_page=page)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/user_topics.html", **template_variables)


class UserRepliesHandler(BaseHandler):
    def get(self, user, template_variables={}):
        if (re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        current_user = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

        if (current_user):
            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                current_user["uid"]);

        template_variables["replies"] = self.reply_model.get_user_all_replies(user_info["uid"], current_page=page)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/user_replies.html", **template_variables)


class UserFavoritesHandler(BaseHandler):
    def get(self, user, template_variables={}):
        if (re.match(r'^\d+$', user)):
            user_info = self.user_model.get_user_by_uid(user)
        else:
            user_info = self.user_model.get_user_by_username(user)

        current_user = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

        if (current_user):
            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                current_user["uid"]);

        template_variables["favorites"] = self.favorite_model.get_user_all_favorites(user_info["uid"],
                                                                                     current_page=page)
        template_variables["active_page"] = "topic"
        template_variables["gen_random"] = gen_random
        self.render("topic/user_favorites.html", **template_variables)


class ReplyEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, reply_id, template_variables={}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["user_info"]["counter"] = {
            "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
            "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
            "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
        }

        template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
            user_info["uid"]);
        template_variables["reply"] = self.reply_model.get_reply_by_reply_id(reply_id)
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "topic"
        self.render("topic/reply_edit.html", **template_variables)

    @tornado.web.authenticated
    def post(self, reply_id, template_variables={}):
        template_variables = {}

        # validate the fields

        form = ReplyEditForm(self)

        if not form.validate():
            self.get(reply_id, {"errors": form.errors})
            return

        # continue while validate succeed

        reply_info = self.reply_model.get_reply_by_reply_id(reply_id)

        if (not reply_info["author_id"] == self.current_user["uid"]):
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
    def get(self, template_variables={}):
        topic_id = int(self.get_argument("topic_id"))
        topic_info = self.topic_model.get_topic_by_topic_id(topic_id)

        if not self.current_user:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "user_not_login",
            }))
            return

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
            "involved_type": 0,  # 0: topic, 1: reply
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


class CancelFavoriteHandler(BaseHandler):
    def get(self, template_variables={}):
        topic_id = int(self.get_argument("topic_id"))
        topic_info = self.topic_model.get_topic_by_topic_id(topic_id)
        favorite_info = None

        if not self.current_user:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "user_not_login",
            }))
            return

        if not topic_info:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "topic_not_exist",
            }))
            return

        favorite_info = self.favorite_model.get_favorite_by_topic_id_and_owner_user_id(topic_id,
                                                                                       self.current_user["uid"])

        if not favorite_info:
            self.write(lib.jsonp.print_JSON({
                "success": 0,
                "message": "not_been_favorited",
            }))
            return

        self.favorite_model.cancel_exist_favorite_by_id(favorite_info["id"])

        self.write(lib.jsonp.print_JSON({
            "success": 1,
            "message": "cancel_favorite_success",
        }))

        # update reputation of topic author
        topic_time_diff = datetime.datetime.now() - topic_info["created"]
        reputation = topic_info["author_reputation"] or 0
        reputation = reputation + 2 * math.log(self.current_user["reputation"] or 0 + topic_time_diff.days + 10, 10)
        self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})


class MembersHandler(BaseHandler):
    def get(self, template_variables={}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        if (user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }

            template_variables["notifications_count"] = self.notification_model.get_user_unread_notification_count(
                user_info["uid"])

        template_variables["members"] = self.user_model.get_users_by_latest(num=49)
        template_variables["active_members"] = self.user_model.get_users_by_last_login(num=49)
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "members"
        self.render("topic/members.html", **template_variables)


class PlaneAdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        if user['role'] != self.user_model.admin_role:
            return self.redirect('/')
        paginator = self.paginator()
        planes = self.query_by_paginator(self.plane_model, paginator)
        data = {
            'paginator': paginator,
            'planes': planes,
            'user_info': user,
            'gen_random': gen_random,
        }
        self.render('admin/plane_list.html', **data)


class NodeAdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        if user['role'] != self.user_model.admin_role:
            return self.redirect('/')
        paginator = self.paginator()
        nodes = self.query_by_paginator(self.node_model, paginator)
        for node in nodes:
            node['plane'] = self.plane_model.get_plane_by_id(node['plane_id'])
        data = {
            'paginator': paginator,
            'nodes': nodes,
            'user_info': user,
            'gen_random': gen_random,
        }
        self.render('admin/node_list.html', **data)


class PlaneEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id=-1):
        user = self.current_user
        if user['role'] != self.user_model.admin_role:
            return self.redirect('/')
        plane = self.plane_model.get_plane_by_id(id)
        is_new = plane is None
        if is_new:
            plane = {'id': 0}
        data = {
            'user_info': user,
            'plane': plane,
            'is_new': is_new,
            'gen_random': gen_random,
        }
        self.render('admin/plane_edit.html', **data)

    @tornado.web.authenticated
    def post(self, id=-1):
        """TODO: use form and validator"""
        user = self.current_user
        if user['role'] != self.user_model.admin_role:
            return self.redirect('/')
        plane = self.plane_model.get_plane_by_id(id)
        is_new = plane is None
        if is_new:
            plane = {}
        name = self.get_body_argument('name')
        # TODO: check the existence of name
        plane['name'] = name
        if is_new:
            self.plane_model.add_new_plane(plane)
        else:
            self.plane_model.update_plane(id, plane)
        self.redirect('/admin/plane')


class NodeEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id=-1):
        user = self.current_user
        if user['role'] != self.user_model.admin_role:
            return self.redirect('/')
        node = self.node_model.get_node_by_id(id)
        is_new = node is None
        if is_new:
            node = {'id': 0}
        data = {
            'user_info': user,
            'node': node,
            'is_new': is_new,
            'gen_random': gen_random,
            'planes': self.plane_model.get_all_planes(),
        }
        self.render('admin/node_edit.html', **data)

    @tornado.web.authenticated
    def post(self, id=-1):
        """
        TODO: use form to replace, and check the existence of same name/slug node
        """
        user = self.current_user
        if user['role'] != self.user_model.admin_role:
            return self.redirect('/')
        node = self.node_model.get_node_by_id(id)
        name = self.get_body_argument('name')
        slug = self.get_body_argument('slug')
        thumb = self.get_body_argument('thumb')
        plane_id = int(self.get_body_argument('plane_id'))
        topic_count = int(self.get_body_argument('topic_count'))
        introduction = self.get_body_argument('introduction')
        custom_style = self.get_body_argument('custom_style')
        limit_reputation = int(self.get_body_argument('limit_reputation', '0'))
        is_new = node is None
        if node is None:
            node = {}
        node['name'] = name
        node['slug'] = slug
        node['thumb'] = thumb
        node['introduction'] = introduction
        node['custom_style'] = custom_style
        node['limit_reputation'] = limit_reputation
        node['plane_id'] = plane_id
        node['topic_count'] = topic_count
        if is_new:
            self.node_model.add_new_node(node)
        else:
            self.node_model.update_node(node['id'], node)
        self.redirect('/admin/node')
