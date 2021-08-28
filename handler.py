# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/28 20:42 
"""
import string

import ftrack_api

from mongo import Mongo
from config import DB_INFO_CONFIG, FTRACK_USER_CONFIG, FTRACK_DEBUG_USER_CONFIG


def get_group_name(current_file, event_name):
    with Mongo(*DB_INFO_CONFIG) as db:
        db_data = db.query({'type': 'group'}).all()

    for data in db_data:
        for event in data['events']:
            if event['path'] == current_file and event['name'] == event_name:
                return data['name']
    return ''


class LogFormatter(string.Formatter):
    def convert_field(self, value, conversion):
        if conversion == 'u':
            return str(value).upper()
        elif conversion == 'l':
            return str(value).lower()
        elif conversion == 'c':
            return str(value).capitalize()
        elif conversion == 't':
            return str(value).title()

        return super(LogFormatter, self).convert_field(value, conversion)


def load_session(debug=False):
    if debug:
        return ftrack_api.Session(**FTRACK_DEBUG_USER_CONFIG)

    return ftrack_api.Session(**FTRACK_USER_CONFIG)


def load_events(session, file_path_or_module, debug):
    # todo 实现这个
    pass
