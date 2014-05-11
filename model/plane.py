#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

from lib.query import Query


class PlaneModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "plane"
        super(PlaneModel, self).__init__()

    def get_all_planes(self):
        return self.select()

    def get_all_planes_with_nodes(self):
        planes = self.get_all_planes()

        for plane in planes:
            where = "plane_id = %s" % plane["id"]
            plane["nodes"] = self.table("node").where(where).select()

        return planes

    def get_plane_by_plane_id(self):
        where = ""
        planes = self.get_all_planes()

        for plane in planes:
            where = "plane_id = %s" % plane["id"]
            plane["nodes"] = self.table("node").where(where).select()

        return planes

    def get_plane_by_id(self, id):
        where = "id = %s" % str(id)
        return self.where(where).find()

    def add_new_plane(self, info):
        return self.data(info).add()

    def update_plane(self, id, info):
        where = "id=%s" % str(id)
        return self.data(info).where(where).save()

