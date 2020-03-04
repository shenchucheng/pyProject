import socket
from socket import getaddrinfo

from tencentapi.tencentApi import CnsApi


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect(('240e:4c:4008::1', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_addr_ip(addr, p=80, **kwargs):
    try:
        r = getaddrinfo(addr, p, **kwargs)
        return list(i[4][0] for i in r)
    except Exception:
        return ""


class DDns(CnsApi):
    def __init__(self, *domains, domain='', subDomain='',
                 id='', interval='', create=False, **kwargs):
        super().__init__(*domains, **kwargs)
        try:
            self.ddnsinfo = self.config.get("ddns") or {}
            self.domain = domain or self.ddnsinfo["domain"]
            self.sub_domain = subDomain or self.ddnsinfo.get("name")
            self.id = id or self.ddnsinfo.get("id")
            self.interval = interval or self.ddnsinfo.get("interval") or 300
            if self.id:
                self.ddnsinfo = self.get_record_info(self.domain, id=self.id)
                self.sub_domain = self.ddnsinfo["name"]
            elif self.sub_domain:
                self.ddnsinfo = self.get_record_info(self.domain, name=self.sub_domain, fetchone=False)
                if len(self.ddnsinfo) != 1:
                    raise Exception("match result error for {} in {}\n{}".format(
                        self.sub_domain, self.domain,
                        self.ddnsinfo if self.ddnsinfo else "record does not exist"
                    ))
                else:
                    self.ddnsinfo = self.ddnsinfo[0]
                    self.id = self.ddnsinfo["id"]
        except KeyError as e:
            self.conf_doc = '\n# ddns:\n# Example\n# ddns: \n#   domain: ' \
                            'baidu.com\n#   name: ipv6\n#   interval: 300 \n' \
                            '#    port: 8000'
            self.create_conf(self.conf_path)
            raise Exception("{}\n please check the config file at {}".format(e, self.conf_path))
        self.addr = ".".join((self.sub_domain, self.domain))
        self.port = self.ddnsinfo.get("port") or 80

    def update_record_list(self):
        self.record_list(self.domain, update=True)

    def get_rm_ip(self):
        return get_addr_ip(self.addr, self.port)
        # try:
        #     r = get(self.ipurl)
        #     if r.status_code == 200:
        #         return r.text
        # finally:
        #     return ""

    def __ddns_delete(self, ip_local):
        info = self.get_record_info(domain=self.domain, id=self.id)
        ret = self.record_create(
            domain=self.domain, subDomain=info["name"],
            recordType=info["type"], value=ip_local,
        )
        self.record_delete(domain=self.domain, id=self.id)
        self.id = ret["id"]

    def __ddns_modify(self, ip_local):
        ret = self.record_modify(domain=self.domain, subDomain=self.sub_domain, recordId=self.id, value=ip_local)

    def ddns(self, modify=True):
        ip_local = get_host_ip()
        ip_remote = self.get_rm_ip()
        if ip_local not in ip_remote:
            if modify:
                self.__ddns_modify(ip_local)
            else:
                self.__ddns_delete(ip_local)

    def run(self, **kwargs):
        def __main():
            from time import sleep
            while 1:
                self.ddns(**kwargs)
                sleep(self.interval)

        if kwargs.get("unblock"):
            from threading import Thread
            Thread(target=__main).start()
        else:
            __main()


if __name__ == '__main__':
    api = DDns()
    api.ddns()
