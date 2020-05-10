#/usr/bin/env python3
# -*- coding:UTF-8 -*-
# File Name: test.py
# Author: Shechucheng
# Created Time: 2020年05月09日 星期六 20时31分35秒


import re
import time
import pickle

from os.path import join
from random import randint
from spider.taobao import get_taobao_session, logger


__shop_url = 'https://shopsearch.taobao.com/search'
__filename = '.taobao.session.pickle'
__s = get_taobao_session(filename=__filename)
__initiative_id = 'staobaoz_{}'.format(time.strftime('%Y%m%d', time.localtime()))
__params = {
        'initiative_id' : __initiative_id,
        'ie'            : 'utf-8',
        'js'            : '1'
        }
__p = re.compile("g_page_config = (.*);\n")
true  = 1
false = 0


def search_shops(q, session = __s, items=20, storage='', **kwargs):
    if storage:
        def __save(r):
            r = r.text
            fn = join(storage, 'search?t={}&q={}'.format(time.time(), q))
            with open(fn, 'w') as f:
                f.write(r)
            return r
    else:
        __save = lambda x: x.text

    try:
        params = __params.copy()
        params['q']     = q
        params.update(kwargs)
        shops = []
        i = 20
        while 1:
            params['items'] = i
            r = session.get(__shop_url, params=params)
            if r.status_code == 200:
                r.encoding = r.apparent_encoding
                r = __save(r)       
                pr = __p.search(r)
                pr = pr[1]
                g_page_config = eval(pr)
                shoplist = g_page_config['mods']['shoplist']['data']['shopItems']
                for shop in shoplist:
                   print(shop)
                shops.extend(shoplist)
            else:
                raise Exception(r)
            if i < items:
                i += 20
            else:
                break
            time.sleep(randint(5,30)/10)
    except NameError as e:
        r  = '"g_page_config" in pr: {}'
        rs =  "g_page_config" in pr
        logger.warn(r.format(rs))
        return pr
    except Exception as e:
        logger.warn(e)
    finally:
        with open(__filename, 'wb') as f:
            pickle.dump(session, f)
        return shops

if __name__ == '__main__':
    r = search_shops('零食')
    print(r)
