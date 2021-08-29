# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/28 22:01 
"""
import sys
import ctypes
import traceback
from functools import wraps
from datetime import datetime

from .mongo import Mongo
from .config import DB_LOG_CONFIG
from .handler import LogFormatter, get_group_name, load_session, load_events


def subscribe(topic='ftrack.update', subscriber=None, priority=100):
    """
    注册订阅装饰器
    eg:
        @subscribe()
        def my_event(event):
            pass
    Args:
        topic: 订阅的项
        subscriber: 订阅的信息
        priority: 优先级 (这个值为初始优先级，会被网站上的事件优先级值覆盖，这里加这个参数是为了方便几个事件间的调试)
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

    def error(self, msg, **kwargs):
        return self._record(msg, 'error', **kwargs)

    def exception(self, msg, group=None, event=None, **kwargs):
        return self._record(msg, 'exception', group, event, **kwargs)

    def info(self, msg, **kwargs):
        return self._record(msg, 'info', **kwargs)

    def warning(self, msg, **kwargs):
        return self._record(msg, 'warning', **kwargs)

    def _make_msg(self, data):
        return self._log_formatter.format(self.log_format, **data) or data[
            "msg"]

    def _record(self, msg, log_type, group=None, event=None, info=None,
                **kwargs):
        if not info:
            info = traceback.extract_stack()[-3]

        time = datetime.now()
        with Mongo(*DB_LOG_CONFIG) as db:
            event = event or info[-2]
            data = {
                'msg': msg.strip(),
                'type': log_type,
                'group': (group or
                          get_group_name(info[0].replace('\\\\', '/'), event)),
                'time': time,
                'local_time': time.strftime('%Y/%m/%d %H:%M:%S'),
                'event': event,
            }
            data.update(kwargs)
            db.add(data)

        msg = self._make_msg(data)
        self._set_cmd_text_color(log_type)
        sys.stdout.write(f'{msg}\n')
        self._reset_cmd_color()

        return msg

    def log_color(self, color_type):
        return self._log_color_by_type.get(color_type, ('black', 0x0f))[0]

    def _set_cmd_text_color(self, color_type):
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        if not isinstance(color_type, int):
            color = self._log_color_by_type.get(color_type, ('black', 0x0f))[1]
        else:
            color = color_type
        return ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)

    def _reset_cmd_color(self):
        self._set_cmd_text_color(0x0c | 0x0a | 0x09)


logger = Log()


class EventBase(object):
    """
        如果事件想写成类，可以继承这个类
        run函数为event的入口函数，需要在run函数处理事件
        在类里面可以直接调用self.logger 拿到logger对象
    """
    event_name = None  # 自定义事件名，如果不设置，就用类名

    def __init__(self, session):
        self.session = session
        self.logger = Log()
        self.logger._record = self._logger_record

    def run(self, event):
        raise NotImplementedError

    def _logger_record(self, msg, log_type, group=None, event=None, **kwargs):
        event = self.event_name or self.__class__.__name__

        return Log()._record(
            msg, log_type, group, event, traceback.extract_stack()[-3], **kwargs
        )


def run_test_server(debug=False):
    """
    用于直接测试当前文件中的事件
    Args:
        debug: 是否只接受debug账号发送过来的消息
    """
    session = load_session(debug)
    file_path = traceback.extract_stack()[0][0].replace('\\', '/')
    load_events(session, file_path, debug)

    session.event_hub.wait()
