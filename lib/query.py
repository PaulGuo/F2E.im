#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 Guokai (benben.cc)
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import re

do_dict = {
    "where": "__condition",
    "table": "__table_name",
    "limit": "__limit",
    "order": "__order",
    "field": "__field",
    "data": "__data",
    "group": "__group",
    "having": "__having",
    "join": "__join",
}

class Query(object):
    def __init__(self, table_name = None, db = None):
        if not table_name == None:
            self.table_name = table_name

        if not db == None:
            self.db = db

        self.__reset()
        
    def __reset(self):
        self.__cluster = []
        self.__protected = {}
        self.__protected["__field"] = "*"
        self.__protected["__table_name"] = self.table_name

    def __close(self):
        self.__reset()

    def __tracker(self, name):
        if(not name in self.__cluster): self.__cluster.append(name)

    def __check(self, name):
        return True if(name in self.__cluster) else False

    def __do(self, name, value):
        value = value.strip() if type(value) == type('string') else value
        self.__protected[do_dict[name]] = value
        self.__tracker(name)

    def __sqlfix(self, sql):
        sql = re.sub(r"(?<!%)%(?!%)", "%%", sql)
        sql = re.sub(r"(?<!\\)\\(?!\\)", r"\\\\", sql)
        return sql

    def __valuefix(self, value):
        value = re.sub(r"\'", "''", value) if type(value) == type("string") or type(value) == type(u"unicode") else value
        return value

    def __sqlbuild(self, sql = '', queue = []):
        for statement in queue:
            if(self.__check("join") and statement == "join"):
                sql = sql + " %s" % self.__protected["__join"]

            if(self.__check("where") and statement == "where"):
                sql = sql + " WHERE %s" % self.__protected["__condition"]

            if(self.__check("order") and statement == "order"):
                sql = sql + " ORDER BY %s" % self.__protected["__order"]

            if(self.__check("limit") and statement == "limit"):
                sql = sql + " LIMIT %s" % self.__protected["__limit"]

            if(self.__check("group") and statement == "group"):
                sql = sql + " GROUP BY %s" % self.__protected["__group"]

            if(self.__check("having") and statement == "having"):
                sql = sql + " HAVING %s" % self.__protected["__having"]

            if(self.__check("data") and statement == "data:save"):
                sets = ""
                for data in self.__protected["__data"]:
                    sets = sets + "%s = '%s', " % (data, self.__valuefix(self.__protected["__data"][data]))
                
                sets = sets.strip().rstrip(",")
                sql = sql + " SET %s" % sets

            if(self.__check("data") and statement == "data:add"):
                sets = ""
                values = ""
                for data in self.__protected["__data"]:
                    sets = sets + "%s, " % data
                    values = values + "'%s', " % self.__valuefix(self.__protected["__data"][data])
                
                sets = sets.strip().rstrip(",")
                values = values.strip().rstrip(",")
                sql = sql + " (%s)" % sets
                sql = sql + " VALUES (%s)" % values

        return sql

    def prepend(self, name, value):
        self.__protected[do_dict[name]] = "%s AND %s" % (value, self.__protected[do_dict[name]])
        return self

    def table(self, table_name):
        self.__do("table", table_name)
        return self

    def where(self, condition):
        self.__do("where", condition)
        return self

    def limit(self, start, end = None):
        limit = start if not end else "%s, %s" % (start, end)
        self.__do("limit", limit)
        return self

    def order(self, type):
        self.__do("order", type)
        return self

    def field(self, field):
        self.__do("field", field)
        return self

    def data(self, data):
        self.__do("data", data)
        return self

    def group(self, type):
        self.__do("group", type)
        return self

    def having(self, condition):
        self.__do("having", condition)
        return self

    def join(self, condition):
        self.__do("join", condition)
        return self

    def query(self, sql):
        self.__close()
        sql = self.__sqlfix(sql)
        return self.db.query(sql)

    def grasp(self, sql):
        select_regx = re.compile("SELECT (COUNT\()?(?P<field>[\w\*\s\.,]+)\)? FROM (?P<table_name>.*?)(LIMIT|ORDER|GROUP|HAVING|WHERE|LEFT|RIGHT|INNER|$)", re.I)
        where_complex_regx = re.compile("WHERE (?P<condition>.*?)(LIMIT|ORDER|GROUP|HAVING|LEFT|RIGHT|INNER)", re.I)
        where_regx = re.compile("WHERE (?P<condition>.*)", re.I)
        limit_regx = re.compile("LIMIT (?P<start>\d+),?\s*(?P<end>\d+)?", re.I)
        group_regx = re.compile("GROUP BY (?P<group_by>[\w\.]+)", re.I)
        having_regx = re.compile("HAVING (?P<having>\w+)", re.I)
        order_regx = re.compile("ORDER BY (?P<order_by>[\w\.\,\s]+\s+(ASC|DESC|\(\)|\s))\s*(LIMIT|GROUP|HAVING|WHERE|LEFT|RIGHT|INNER|$)", re.I)
        insert_regx = re.compile("INSERT INTO (?P<table_name>\w+) \(((\w+,?\s?)+)\) VALUES \((([\"']?\w+[\"']?,?\s?)+)\)", re.I)
        update_complex_regx = re.compile("UPDATE (?P<table_name>\w+) SET (.*?)(LIMIT|ORDER|GROUP|HAVING|WHERE|LEFT|RIGHT|INNER)", re.I)
        update_regx = re.compile("UPDATE (?P<table_name>\w+) SET (.*)", re.I)
        table_regx = re.compile("FROM (?P<table_name>.*?)(LIMIT|ORDER|GROUP|HAVING|WHERE|LEFT|RIGHT|INNER|$)", re.I)
        join_regx = re.compile("(?P<join_condition>(?P<join_dir>LEFT|RIGHT)?\s*(?P<join_type>INNER|OUTER)? JOIN (?P<table_name>\w+) (AS \w+\s+)?ON (.*?))(LIMIT|ORDER|GROUP|HAVING|WHERE)", re.I)

        select = select_regx.search(sql)
        where_complex = where_complex_regx.search(sql)
        where = where_regx.search(sql)
        limit = limit_regx.search(sql)
        group = group_regx.search(sql)
        having = having_regx.search(sql)
        order = order_regx.search(sql)
        insert = insert_regx.search(sql)
        update_complex = update_complex_regx.search(sql)
        update = update_regx.search(sql)
        table = table_regx.search(sql)
        join = join_regx.search(sql)

        if select:
            _field = select.groupdict()["field"]
            _table_name = select.groupdict()["table_name"]
            self.__do("field", _field)
            self.__do("table", _table_name)

        if where_complex:
            _condition = where_complex.groupdict()["condition"]
            self.__do("where", _condition)

        elif where:
            _condition = where.groupdict()["condition"]
            self.__do("where", _condition)

        if limit:
            start = limit.groupdict()["start"]
            end = limit.groupdict()["end"]
            _limit = start if not end else "%s, %s" % (start, end)
            self.__do("limit", _limit)

        if group:
            _group_by = group.groupdict()["group_by"]
            self.__do("group", _group_by)

        if having:
            _having = group.groupdict()["having"]
            self.__do("having", _having)

        if order:
            _order_by = order.groupdict()["order_by"]
            self.__do("order", _order_by)

        if table:
            _table_name = table.groupdict()["table_name"]
            self.__do("table", _table_name)

        if join:
            _join = join.groupdict()["join_condition"]
            self.__do("join", _join)

        if insert:
            _table_name = insert.groupdict()["table_name"]
            fields = insert.groups()[1].split(",")
            values = insert.groups()[3].split(",")
            _data = {}

            for index, field in enumerate(fields):
                field = field.strip()
                value = values[index].strip()
                _data[field] = value

            self.__do("data", _data)
            self.__do("table", _table_name)

        if update_complex:
            _table_name = update_complex.groupdict()["table_name"]
            pairs = update_complex.groups()[1].split(",")
            _data = {}
            
            for index, pair in enumerate(pairs):
                pair = pair.split("=")
                field = pair[0].strip()
                value = pair[1].strip()
                _data[field] = value

            self.__do("data", _data)
            self.__do("table", _table_name)

        elif update:
            _table_name = update.groupdict()["table_name"]
            pairs = update.groups()[1].split(",")
            _data = {}
            
            for index, pair in enumerate(pairs):
                pair = pair.split("=")
                field = pair[0].strip()
                value = pair[1].strip()
                _data[field] = value

            self.__do("data", _data)
            self.__do("table", _table_name)

        return self

    def count(self, cheat = False):
        sql = "SELECT COUNT(*) FROM %s" % self.__protected["__table_name"]
        sql = self.__sqlbuild(sql, ["join", "where", "group", "having"])
        sql = self.__sqlfix(sql)
        self.__close()

        group_having_regx = re.compile("(GROUP|HAVING)", re.I)

        if(not group_having_regx.search(sql)):
            return self.db.get(sql)["COUNT(*)"] if not cheat else sql
        else:
            return len(self.db.query(sql)) if not cheat else sql

    def sum(self, field, cheat = False):
        sql = "SELECT SUM(%s) FROM %s" % (field, self.__protected["__table_name"])
        sql = self.__sqlbuild(sql, ["where"])
        sql = self.__sqlfix(sql)
        self.__close()
        return self.db.get(sql)["SUM(%s)" % field] if not cheat else sql

    def find(self, cheat = False):
        try:
            return self.select()[0] if not cheat else self.select(cheat)
        except:
            return None

    def select(self, cheat = False):
        sql = "SELECT %s FROM %s" % (self.__protected["__field"], self.__protected["__table_name"])
        sql = self.__sqlbuild(sql, ["join", "where", "group", "having", "order", "limit"])
        sql = self.__sqlfix(sql)
        self.__close()
        return self.db.query(sql) if not cheat else sql

    def delete(self, cheat = False):
        sql = "DELETE FROM %s" % self.__protected["__table_name"]
        sql = self.__sqlbuild(sql, ["where", "order", "limit"])
        sql = self.__sqlfix(sql)
        self.__close()
        return self.db.execute(sql) if not cheat else sql

    def save(self, cheat = False):
        sql = "UPDATE %s" % self.__protected["__table_name"]
        sql = self.__sqlbuild(sql, ["data:save", "where"])
        sql = self.__sqlfix(sql)
        self.__close()
        return self.db.execute(sql) if not cheat else sql

    def add(self, cheat = False):
        sql = "INSERT INTO %s" % self.__protected["__table_name"]
        sql = self.__sqlbuild(sql, ["data:add"])
        sql = self.__sqlfix(sql)
        self.__close()
        return self.db.execute(sql) if not cheat else sql

    def pages(self, current_page = 1, list_rows = 40, cheat = False):
        sql = self.select(cheat = True)
        self.__close()
        count = self.grasp(sql).count()
        pages = count / list_rows
        pages = pages + 1 if not count % list_rows == 0 else pages
        if(pages == 0): pages = 1
        if(current_page < 1): current_page = 1
        if(current_page > pages): current_page = current_page
        start = (current_page - 1) * list_rows
        end = list_rows
        previous_page = current_page - 1 if current_page > 1 else 1
        next_page = current_page + 1 if current_page < pages else pages

        result = {}
        result["list"] = self.grasp(sql).limit(start, end).select()
        result["page"] = {
            "prev": previous_page,
            "next": next_page,
            "current": current_page,
            "pages": pages,
            "total": count,
        }

        return result if not cheat else self.grasp(sql).limit(start, end).select(cheat)
