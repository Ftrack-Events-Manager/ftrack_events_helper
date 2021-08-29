# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/29 17:42 
"""
from ftrack_events_helper.handler import (load_session, load_events,
                                          import_module, get_event_paths)

DEBUG = False


def register_events():
    print('Ftrack Events测试服务器已启动...')
    session = load_session(DEBUG)

    if DEBUG:
        print('当前为Debug模式，只会处理DEBUG_USERS中的账号触发的事件...')

    tmp_models = []
    for event_path in get_event_paths():
        model_obj = import_module(event_path)

        if hasattr(model_obj, 'DEBUG') and getattr(model_obj, 'DEBUG'):
            tmp_models.append((True, model_obj))
        else:
            tmp_models.append((False, model_obj))

    # 如果有DEBUG=true的event就只加载这些event，如果没有就加载所有的
    models = [m[1] for m in tmp_models if m[0]]
    if not models:
        models = [m[1] for m in tmp_models]

    for model_obj in models:
        load_events(session, model_obj, DEBUG)

    print('Ftrack事件已加载完成...')
    session.event_hub.wait()


if __name__ == '__main__':
    register_events()
