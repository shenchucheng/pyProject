#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


class Api:
    def __init__(self, conf_path="", conf_dir=""):
        """
        :param conf_path: config file path
               default: .pyproject/tencentapi/api.conf at config_dir
        :param conf_dir: files produced saved at this dir
               default: ~/.pyproject/tencentapi/
        """
        if not conf_dir:
            conf_dir = os.path.join(os.path.expanduser("~"), ".pyconfig", "tencentapi")
            if not os.path.exists(conf_dir):
                os.makedirs(conf_dir)
        if not conf_path:
            conf_path = os.path.join(conf_dir, "tencentapi.conf")
        self.conf_dir = conf_dir
        self.conf_path = conf_path
        self.__conf_doc = ''
        self.config = self.parser()
        self.secretId = self.config["secretId"]
        self.secretKey = self.config["secretKey"]

    @property
    def conf_doc(self):
        if not self.__conf_doc:
            with open(self.conf_path, "a+") as f:
                if f.tell() > 0:
                    f.seek(0)
                    self.__conf_doc = f.read()
                else:
                    self.__conf_doc = _conf_doc_pre
        return self.__conf_doc

    @conf_doc.setter
    def conf_doc(self, doc: str):
        # lines = self.conf_doc.splitlines(True)
        # doc_pre = "".join(lines[:5])
        lines = doc.splitlines(True)
        _ = ""
        for line in lines:
            if not line.startswith("#"):
                line = "# " + line
            _ += line
        # doc = _ if doc.startswith(doc_pre) else doc_pre+_
        if doc not in self.conf_doc:
            doc = "\n\n" + doc
            self.__conf_doc += doc

    def create_conf(self, conf=""):
        with open(conf or self.conf_path, "w") as f:
            f.write(self.conf_doc)

    # def create_conf(self):
    #     conf_path = self.conf_path
    #     self.__create_conf(conf_path)
        # if os.path.exists(conf_path):
        #     with open(conf_path) as f:
        #         _ = ""
        #         for line in f:
        #             if line.startswith("#"):
        #                 continue
        #             if line == "\n":
        #                 continue
        #             _ += line
        #     with open(conf_path, "w") as f:
        #         f.write(self.conf_doc+"\n"+_)
        # else:
        #     self.__create_conf(conf_path)

    def parser(self):
        """
        parser the args for configure file
        :return: config dict
        """
        if not os.path.exists(self.conf_path):
            self.create_conf(self.conf_path)
        with open(self.conf_path) as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
        if conf is None:
            raise NotImplementedError(
                "Fatal Error: TencentApi conf file without setting. " +
                "File has initialised in {}".format(self.conf_path)
            )
        return conf

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
    def __init__(self, *domains, **kwargs):
        """
        :param domain: such as "baidu.com", "bing.cn"
        :param kwargs:
        """
        super().__init__(**kwargs)
        try:
            self.domains = domains or self.config["domains"]
        except KeyError:
            self.conf_doc = "# domain\n# Example\n# domains: !!set\n#   ab.com: \n#   cd.cn: \n"
            self.create_conf()
            raise Exception("domain not set,please check the config file at {}".format(self.conf_path))
        with open(os.path.join(self.conf_dir, "record.list"), "a+") as f:
            f.seek(0)
            self.records = yaml.load(f, yaml.SafeLoader) or {}

    def __record_list(self, domain, **kwargs):
        ret = self.get(action='RecordList', domain=domain, **kwargs)["data"]
        with open(os.path.join(self.conf_dir, "record.list"), "a+") as f:
            yaml.dump({domain: ret}, f)
        self.records[domain] = ret

    def record_list(self, update=False, *domains, **kwargs):
        """
        :param update: bool if update will update self.records
        :param domains: str 要操作的域名（主域名，不包括 www，例如：qcloud.com）
        :param kwargs:
            offset int 偏移量，默认为0。关于offset的更进一步介绍参考 接口请求参数
            length int 返回数量，默认20，最大值100
            subDomain str （过滤条件）根据子域名进行过滤
            recordType str （过滤条件）根据记录类型进行过滤
            qProjectId int （过滤条件）项目 ID
        :return:
        """
        ret = {}
        domains = domains or self.domains
        if update:
            for i in domains:
                self.__record_list(i, **kwargs)
        for i in domains:
            if i not in self.records.keys():
                self.__record_list(i, **kwargs)
            ret[i] = self.records[i]
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


def get_conf_doc_pre():
    doc = ''
    doc += "# App: TencentAPI\n"
    doc += "# Description: Tencent api need SecretId and secretKey\n"
    doc += "# Id-Key\n"
    doc += "# How to get Id&Key see https://cloud.tencent.com/developer/article/1385239\n"
    doc += "# Example: \n"
    doc += "# secretId: idAafkSyAJohQSnRidZShsDLsDuMqYUgWecQ\n"
    doc += "# secretKey: zAuhBlapaarSHJMrKfYtheLyMgLUvqrL\n"
    return doc


_conf_doc_pre = get_conf_doc_pre()


if __name__ == "__main__":
    api = CnsApi()
    records = api.record_list(update=True)
    print(records)
