#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import time
from lib.query import Query

class VoteModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "vote"
        super(VoteModel, self).__init__()

    def add_new_vote(self, vote_info):
        return self.data(vote_info).add()

    def get_vote_by_topic_id_and_trigger_user_id(self, topic_id, trigger_user_id):
        where = "involved_topic_id = %s AND trigger_user_id = %s" % (topic_id, trigger_user_id)
        return self.where(where).find()

