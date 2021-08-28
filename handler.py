# -*- coding: utf-8 -*-
"""
@author: LiaoKong
@time: 2021/08/28 20:42 
"""
import string

from utils.mongo import Mongo
from config import DB_INFO_CONFIG


def get_group_name(current_file, event):
    pass


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
