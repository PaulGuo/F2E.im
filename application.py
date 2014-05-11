#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

# cat /etc/mime.types
# application/octet-stream    crx
from __future__ import print_function
import sys

reload(sys)
sys.setdefaultencoding("utf8")

import os.path
import memcache
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import handler.base
import handler.user
import handler.topic
import handler.page
import handler.notification

from tornado.options import options
from lib.loader import Loader
from lib.session import SessionManager
from jinja2 import Environment, FileSystemLoader
import tcelery

import settings

db_default = settings.DATABASE['default']
# define("port", default=settings.http['port'], help="run on the given port", type=int)
# define("mysql_host", default=db_default['host'], help="community database host")
# define("mysql_database", default=db_default['db_name'], help="community database name")
# define("mysql_user", default=db_default['user'], help="community database user")
# define("mysql_password", default=db_default['password'], help="community database password")


tcelery.setup_nonblocking_producer()


class Application(tornado.web.Application):
    def __init__(self):
        app_settings = dict(
            blog_title=settings.site['title'],
            login_url="/login",
            jinja2=Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
                               trim_blocks=True),
            reserved=["user", "topic", "home", "setting", "forgot", "login", "logout", "register", "admin"],
        )
        app_settings.update(settings.app_settings)

        handlers = [
            (r"/", handler.topic.IndexHandler),
            (r"/t/(\d+)", handler.topic.ViewHandler),
            (r"/t/create/(.*)", handler.topic.CreateHandler),
            (r"/t/edit/(.*)", handler.topic.EditHandler),
            (r"/reply/edit/(.*)", handler.topic.ReplyEditHandler),
            (r"/node/(.*)", handler.topic.NodeTopicsHandler),
            (r"/u/(.*)/topics", handler.topic.UserTopicsHandler),
            (r"/u/(.*)/replies", handler.topic.UserRepliesHandler),
            (r"/u/(.*)/favorites", handler.topic.UserFavoritesHandler),
            (r"/u/(.*)", handler.topic.ProfileHandler),
            (r"/vote", handler.topic.VoteHandler),
            (r"/favorite", handler.topic.FavoriteHandler),
            (r"/unfavorite", handler.topic.CancelFavoriteHandler),
            (r"/notifications", handler.notification.ListHandler),
            (r"/members", handler.topic.MembersHandler),
            (r"/setting", handler.user.SettingHandler),
            (r"/setting/avatar", handler.user.SettingAvatarHandler),
            (r"/setting/avatar/gravatar", handler.user.SettingAvatarFromGravatarHandler),
            (r"/setting/password", handler.user.SettingPasswordHandler),
            (r"/forgot", handler.user.ForgotPasswordHandler),
            (r"/login", handler.user.LoginHandler),
            (r"/logout", handler.user.LogoutHandler),
            (r"/register", handler.user.RegisterHandler),

            (r'/admin/user$', handler.user.UserAdminHandler),
            (r'/admin/node$', handler.topic.NodeAdminHandler),
            (r'/admin/node/new$', handler.topic.NodeEditHandler),
            (r'/admin/node/(\d+)$', handler.topic.NodeEditHandler),
            (r'/admin/plane$', handler.topic.PlaneAdminHandler),
            (r'/admin/plane/new$', handler.topic.PlaneEditHandler),
            (r'/admin/plane/(\d+)$', handler.topic.PlaneEditHandler),

            (r'/resource/picture/upload_async', handler.page.PictureIframeUploadHandler),

            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path=app_settings["static_path"])),
            (r"/(sitemap.*$)", tornado.web.StaticFileHandler, dict(path=app_settings["static_path"])),
            (r"/(bdsitemap\.txt)", tornado.web.StaticFileHandler, dict(path=app_settings["static_path"])),
            (r"/(.*)", handler.topic.ProfileHandler),
        ]

        tornado.web.Application.__init__(self, handlers, **app_settings)

        # Have one global connection to the blog DB across all handlers
        self.db = torndb.Connection(
            host=db_default['host'], database=db_default['db_name'],
            user=db_default['user'], password=db_default['password']
        )

        # Have one global loader for loading models and handles
        self.loader = Loader(self.db)

        # Have one global model for db query
        self.user_model = self.loader.use("user.model")
        self.topic_model = self.loader.use("topic.model")
        self.reply_model = self.loader.use("reply.model")
        self.plane_model = self.loader.use("plane.model")
        self.node_model = self.loader.use("node.model")
        self.notification_model = self.loader.use("notification.model")
        self.vote_model = self.loader.use("vote.model")
        self.favorite_model = self.loader.use("favorite.model")
        self.picture_model = self.loader.use('picture.model')

        # Have one global session controller
        self.session_manager = SessionManager(app_settings["cookie_secret"], settings.memcached, 0)

        # Have one global memcache controller
        self.mc = memcache.Client(settings.memcached)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    port = settings.http['port']
    http_server.listen(port)
    print("http listen at http://localhost:%d" % port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

