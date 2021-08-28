# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/27 22:30 
"""
import sys
import ctypes
import traceback
from functools import wraps
from datetime import datetime

from utils.mongo import Mongo
from config import DB_LOG_CONFIG
from handler import LogFormatter, get_group_name


def subscribe(topic='ftrack.update', subscriber=None, priority=100):
    """
    注册订阅装饰器
    eg:
        @subscribe()
        def my_event(event):
            pass
    Args:
        topic: 订阅的项，eg: 'my_event_topic'
        subscriber: 订阅的信息
        priority: 优先级 (这个值为初始优先级，会被网站上的事件优先级值覆盖)

    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                if hasattr(func, 'run'):
                    file_path = func.run.__globals__['__file__']
                else:
                    file_path = func.__globals__['__file__']
                group = get_group_name(file_path, func.__name__)
                Log.exception(traceback.format_exc(), group, func.__name__,
                              variables=str(args[-1].items()),
                              pathname=file_path)

        inner.topic = topic
        inner.subscriber = subscriber
        inner.priority = priority
        inner.is_class = hasattr(func, 'run')
        return inner

    return wrapper


class Log(object):
    """用于记录event事件的log"""
    _log_color_by_type = {
        'info': ('green', 0x0a),
        'warning': ('orange', 0x0e),
        'error': ('pink', 0x0d),
        'exception': ('red', 0x0c)
    }
    _log_formatter = LogFormatter()

    log_format = '{local_time} group:{group} event:{event} {type!u}:{msg}'

    @classmethod
    def error(cls, msg, **kwargs):
        return cls._record(msg, 'error', **kwargs)

    @classmethod
    def exception(cls, msg, group=None, event=None, **kwargs):
        return cls._record(msg, 'exception', group, event, **kwargs)

    @classmethod
    def info(cls, msg, **kwargs):
        return cls._record(msg, 'info', **kwargs)

    @classmethod
    def warning(cls, msg, **kwargs):
        return cls._record(msg, 'warning', **kwargs)

    @classmethod
    def _make_msg(cls, data):
        return (cls._log_formatter.format(cls.log_format, **data) or
                data['msg']) + u'\n'

    @classmethod
    def _record(cls, msg, log_type, group=None, event=None, info=None, **kwargs):
        if not info:
            info = traceback.extract_stack()[-3]

        time = datetime.now()
        with Mongo(*DB_LOG_CONFIG) as db:
            event = event or info[-2]
            data = {
                'msg': msg.strip(),
                'type': log_type,
                'group': (group or get_group_name(info[0].replace('\\\\', '/'), event)),
                'time': time,
                'local_time': time.strftime('%Y/%m/%d %H:%M:%S'),
                'event': event,
            }
            data.update(kwargs)
            db.add(data)

        msg = cls._make_msg(data)
        cls._set_cmd_text_color(log_type)
        sys.stdout.write(msg)
        cls._reset_cmd_color()

        return msg

    @classmethod
    def log_color(cls, color_type):
        return cls._log_color_by_type.get(color_type, ('black', 0x0f))[0]

    @classmethod
    def _set_cmd_text_color(cls, color_type):
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        if not isinstance(color_type, int):
            color = cls._log_color_by_type.get(color_type, ('black', 0x0f))[1]
        else:
            color = color_type
        return ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)

    @classmethod
    def _reset_cmd_color(cls):
        cls._set_cmd_text_color(0x0c | 0x0a | 0x09)
