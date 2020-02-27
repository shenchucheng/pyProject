#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
# 引入云API入口模块
 

import base64
import hashlib
import hmac
import random
import time
import operator
import json
import urllib.parse
import yaml 
import urllib3
 
 
class QcloudApi():
    def __init__(self):
        info = yaml.load("")
        self.SecretId = 'SecretId'
        self.secretKey = info["secretkey"] 
 
    def get(self, action, module='cns', **params):
        config = {
            'Action': action,
            'Nonce': random.randint(10000, 99999),
            'SecretId': self.SecretId,
            'SignatureMethod': 'HmacSHA256',
            'Timestamp': int(time.time()),
        }
        url_base = '{0}.api.qcloud.com/v2/index.php?'.format(module)
 
        params_all = dict(config, **params)
 
        params_sorted = sorted(params_all.items(), key=operator.itemgetter(0))
 
        srcStr = 'GET{0}'.format(url_base) + ''.join("%s=%s&" % (k, v) for k, v in dict(params_sorted).items())[:-1]
        signStr = base64.b64encode(hmac.new(bytes(self.secretKey, encoding='utf-8'), bytes(srcStr, encoding='utf-8'), digestmod=hashlib.sha256).digest()).decode('utf-8')
 
        config['Signature'] = signStr
 
        params_last = dict(config, **params)
 
        params_url = urllib.parse.urlencode(params_last)
 
        url = 'https://{0}&'.format(url_base) + params_url
        http = urllib3.PoolManager()
        r = http.request('GET', url=url, retries=False)
        ret = json.loads(r.data.decode('utf-8'))
        if ret.get('code', {}) == 0:
            return ret
        else:
            raise Exception(ret)


if __name__ == "__main__":
    qcloud = QcloudApi()
    ret = qcloud.get(action='RecordList', domain='phichem.xyz')
    domainInfo = ret["data"]["domain"]
    records = ret["data"]["records"]
    for i in records:
        print(i["name"], " - ", i["id"], " - ", i["type"])

#调用例子：
# ret = qcloud.get(module='cns', action='DomainCreate', domain='abc.com')
# ret = qcloud.get(module='cns', action='SetDomainStatus', domain='abc.com', status='enable')  # 'enable' or 'disable'
# ret = qcloud.get(module='cns', action='DomainList')
# ret = qcloud.get(module='cns', action='DomainDelete', domain='abc.com')
 
# ret = qcloud.get(module='cns', action='RecordList', domain='abc.com', length=100)
# ret = qcloud.get(module='cns', action='RecordCreate', domain='abc.com', subDomain='www', value='192.168.100.11', recordType='A', recordLine='联通')
# ret = qcloud.get(module='cns', action='RecordModify', domain='abc.com', recordId=388853153, subDomain='www', value='192.168.101.11', recordType='A', recordLine='电信', remark='主站搜索引擎线路')
# ret = qcloud.get(module='cns', action='RecordStatus', domain='abc.com', recordId=388745814, status='enable')
# ret = qcloud.get(module='cns', action='RecordDelete', domain='abc.com', recordId=388745814)
 
# print(ret['data']['domains'][0].get('name'))
# if 'coinlab.club' in [item['name'] for item in ret['data']['domains']]:
#    print('yes')

