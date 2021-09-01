# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/26 22:00
"""
import pymongo

from ftrack_events_helper.config import DB_CONFIG


class Mongo(object):
    UP = pymongo.ASCENDING
    DOWN = pymongo.DESCENDING

    def __init__(self, database_name, collection_name):
        self.connect = pymongo.MongoClient(**DB_CONFIG)
        self.database = self.connect[database_name]
        self.collection = self.database[collection_name]
        self._query_data = None

    def collection_names(self):
        return self.database.list_collection_names()

    def add(self, data):
        if isinstance(data, dict):
            data = [data]
        return self.collection.insert_many(data)

    def update(self, data, query_filter, upsert=False, multi=True):
        return self.collection.update(query_filter, {'$set': data}, upsert,
                                      multi=multi)

    def delete(self, query_filter):
        if not query_filter:
            raise ValueError(
                'Query_filter is empty, please user drop_collection delete collection.')
        self.collection.delete_many(query_filter)

    def drop_collection(self):
        return self.collection.drop()

    def query_one(self, query_filter, *args, **kwargs):
        return self.collection.find_one(query_filter, *args, **kwargs) or {}

    def query(self, *args, **kwargs):
        self._query_data = self.collection.find(*args, **kwargs)
        return self

    def all(self, to_list=False):
        if to_list:
            return list(self._query_data)
        return self._query_data

    def sort(self, key_or_list):
        if self._query_data is None:
            raise ValueError('Please try the query function first')
        self._query_data = self._query_data.sort(key_or_list)
        return self

    def limit(self, limit):
        if self._query_data is None:
            raise ValueError('Please try the query function first')
        self._query_data = self._query_data.limit(limit)
        return self._query_data

    def close(self):
        return self.connect.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connect.close()


if __name__ == '__main__':
    with Mongo('FtrackEventsManager', 'EventsInfos') as db:
        print(db.collection_names())
