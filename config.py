# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/28 20:27 
"""
import os

# DB
DB_CONFIG = {
    'host': '127.0.0.1',
    'post': 27017
}
DB_INFO_CONFIG = ('FtrackEventsManager', 'EventsInfos')
DB_LOG_CONFIG = ('FtrackEventsManager', 'EventsLogs')

# EVENTS
EVENTS_ROOT = ''

# USER
DEBUG_USER = 'debug01'  # 用于开启debug模式后，判断当前events账号是不是debug账号
FTRACK_USER_CONFIG = {
    'api_key': os.environ.get('FTRACK_API_KEY'),
    'api_user': os.environ.get('FTRACK_API_USER'),
    'server_url': os.environ.get('FTRACK_SERVER')
}

FTRACK_DEBUG_USER_CONFIG = {
    'api_key': os.environ.get('FTRACK_DEBUG_API_KEY'),
    'api_user': os.environ.get('FTRACK_DEBUG_API_USER'),
    'server_url': os.environ.get('FTRACK_SERVER')
}
