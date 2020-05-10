#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
# File Name: session.py
# Author: Shechucheng
# Created Time: 2020年05月07日 星期四 07时59分02秒


import os
import sys
import pickle

from logging import getLogger
from requests import session
from requests.utils import cookiejar_from_dict


logger = getLogger('spider')
__headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}


def parse_cookies(cookies=''):
    if not cookies:
        cookies = input('把cookies复制进来：')
    if cookies[0] in ['\'', '"']:
        cookies = cookies.strip('\'"')
    if cookies.startswith('cookie'):
        cookies = cookies[8:]
    return dict(map(lambda x: x.split('=', 1), map(lambda x: x.strip(), cookies.split(';'))))



def get_session(cookies='', filename='.session'):
    """
    """
    if not cookies and os.path.exists(filename):
        with open(filename, 'rb') as f:
            s = pickle.load(f)
    else:
        c = parse_cookies(cookies)
        s = session()
        s.headers = __headers
        s.cookies = cookiejar_from_dict(c)
        with open(filename, 'wb') as f:
            pickle.dump(s, f)
    return s
