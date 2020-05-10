#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
# File Name: __init__.py
# Author: Shechucheng
# Created Time: 2020年05月09日 星期六 20时28分56秒


from spider.session import logger, get_session


def get_taobao_session(cookies='', filename='.taobao.session'):
    """
    """
    s = get_session(cookies, filename=filename)
    return s
