# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/28 20:42 
"""
import os
import string
import importlib.util
from functools import partial

import ftrack_api

from ftrack_events_helper.mongo import Mongo
from ftrack_events_helper.config import (DB_INFO_CONFIG, FTRACK_USER_CONFIG,
                                         FTRACK_DEBUG_USER_CONFIG, DEBUG_USERS,
                                         EVENTS_ROOTS)


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
        return ftrack_api.Session(**FTRACK_DEBUG_USER_CONFIG,
                                  auto_connect_event_hub=True)

    return ftrack_api.Session(**FTRACK_USER_CONFIG, auto_connect_event_hub=True)


def import_module(model_path):
    name = os.path.basename(model_path).rsplit('.', 1)[0]
    spec = importlib.util.spec_from_file_location(name, model_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_event_func(file_path_or_module):
    if isinstance(file_path_or_module, str):
        module_obj = import_module(file_path_or_module)
    else:
        module_obj = file_path_or_module

    funcs = []
    for func in [x for x in dir(module_obj) if not x.startswith('_')]:
        func_obj = getattr(module_obj, func)
        if hasattr(func_obj, 'topic'):
            funcs.append(func_obj)

    return funcs


def func_obj_proxy(func_obj, session, is_class, debug, event):
    is_debug_user = (event.get('data', {}).get('user', {}).get('name', '')
                     in DEBUG_USERS)

    if debug:
        if not is_debug_user:
            return
    else:
        if is_debug_user:
            return

    if is_class:
        return func_obj(event)
    else:
        return func_obj(session, event)


def subscribe_event(func_obj, session, debug):
    if func_obj.is_class:
        class_obj = func_obj(session)
        run_func_obj = class_obj.run
    else:
        run_func_obj = func_obj

    event_func = partial(func_obj_proxy, run_func_obj, session,
                         func_obj.is_class, debug)

    return session.event_hub.subscribe(
        'topic=' + func_obj.topic,
        event_func,
        func_obj.subscriber,
        func_obj.priority
    )


def load_events(session, file_path_or_module, debug):
    for func in get_event_func(file_path_or_module):
        subscribe_event(func, session, debug)
        print('已成功添加事件：{}'.format(func.__name__))


def get_event_paths():
    return [os.path.join(f, n).replace('\\', '/')
            for f in EVENTS_ROOTS for n in os.listdir(f)
            if n.endswith('.py') and not n.startswith('_')]
