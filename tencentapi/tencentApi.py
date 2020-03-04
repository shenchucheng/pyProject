#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
# 引入云API入口模块
 

import os
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
conf_dir = os.path.join(os.path.expanduser("~"), ".pyconfig")
if not os.path.exists(conf_dir):
    os.mkdir(conf_dir)


def parser(conf):
    """
    parse the args from the config file
    :param conf:  config file path;
    default at ~/.pyconfig/tencentapi.conf
    :return:  dict
    """
    if not os.path.exists(conf):
        with open(conf, "w") as f:
            f.write("# App: TencentAPI\n")
            f.write("# Description: Tencent api need SecretId and secretKey\n")
            f.write("# Example: \n")
            f.write("#secretId: gsh67*^*&&%GSuhosgaj\n#secretKey: y9habgcschgvajnlKHg")
    with open(conf) as f:
        __conf = yaml.load(f, Loader=yaml.FullLoader)
        if __conf is None:
            raise NotImplementedError(
                "Fatal Error: TencentApi conf file without setting. " +
                "File has initialised in {}".format(conf)
            )
        return __conf


class Api:
    def __init__(self, conf_path=os.path.join(conf_dir, "tencentapi.conf")):
        info = parser(conf_path)
        self.secretId = info["secretId"]
        self.secretKey = info["secretKey"]
 
    def get(self, action, module='cns', **params):
        config = {
            'Action': action,
            'Nonce': random.randint(10000, 99999),
            'SecretId': self.secretId,
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


class CnsApi(Api):
    """
    腾讯云解析记录相关接口:
    https://cloud.tencent.com/document/product/302/3875
    接口请求域名：cns.api.qcloud.com
    """
    def record_list(self, domain, **kwargs):
        """
        :param domain: str 要操作的域名（主域名，不包括 www，例如：qcloud.com）
        :param kwargs:
            offset int 偏移量，默认为0。关于offset的更进一步介绍参考 接口请求参数
            length int 返回数量，默认20，最大值100
            subDomain str （过滤条件）根据子域名进行过滤
            recordType str （过滤条件）根据记录类型进行过滤
            qProjectId int （过滤条件）项目 ID
        :return:
        """
        ret = self.get(action='RecordList', domain=domain, **kwargs)["data"]
        return ret

    def record_modify(self, domain, subDomain, value, recordId,
                      recordType, recordLine="默认", **kwargs):
        """
        :param domain: str 要操作的域名（主域名，不包括 www，例如：qcloud.com）
        :param subDomain: str 子域名，例如：www
        :param value: str 记录值，例如 IP：192.168.10.2，CNAME：cname.dnspod.com.，MX：mail.dnspod.com.
        :param recordId: int 解析记录的 ID，可通过 RecordList 接口返回值中的 ID 获取
        :param recordType: str 记录类型，可选的记录类型为："A"，"CNAME"，"MX"，"TXT"，"NS"，"AAAA"，"SRV"
        :param recordLine: str 记录的线路名称，例如："默认"
        :param kwargs:
        ttl int TTL 值，范围1 - 604800，不同等级域名最小值不同，默认为 600
        mx	int	MX 优先级，范围为0 ~ 50，当 recordType 选择 MX 时，mx 参数必选
        :return:
        """
        return self.get(action='RecordModify', domain=domain, subDomain=subDomain,
                        value=value, recordId=recordId, recordType=recordType,
                        recordLine="默认", **kwargs)

    def record_create(self, **kwargs):
        return self.get(action='RecordCreate', **kwargs)

    def record_delete(self, **kwargs):
        return self.get(action='RecordDelete', **kwargs)


if __name__ == "__main__":
    api = CnsApi()
    __domain = 'phichem.xyz'
    data = api.record_list(domain=__domain)
    with open(os.path.join(conf_dir, "record.list"), "w") as f:
        yaml.dump({__domain: data}, f)

