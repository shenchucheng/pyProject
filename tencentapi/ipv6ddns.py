import socket
from logging import getLogger
from socket import getaddrinfo
from tencentapi.tencentApi import CnsApi

logger = getLogger("ddns")


def get_host_ip(dns='240e:4c:4008::1'):
    """
    查询本机ip地址
    :return: ip
    """
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect((dns, 80))
        ip = s.getsockname()[0]
        return ip
    except Exception as e:
        logger.warning("Fail to get local ip for {}".format(e))
    finally:
        s.close()


def get_addr_ip(addr, p=80, **kwargs):
    try:
        r = getaddrinfo(addr, p, **kwargs)
        if r:
            return list(i[4][0] for i in r)
        else:
            logger.warning("Can not resolve {}:{} {}".format(addr, p, kwargs or ""))
    except Exception as e:
        logger.warning("Fail to get ip of address {}:{} {} for {} ".format(addr, p, kwargs or "", e))


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
        logger.debug("DDNS initialization successfully, information {}".format(self.ddnsinfo))

    def update_record_list(self):
        self.record_list(self.domain, update=True)
        logger.debug("Update domain {} successfully".format(self.domain))

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
            recordLine=info["line"]
        )
        self.record_delete(domain=self.domain, id=self.id)
        logger.info("Create record which id {} with ip {} and delete {} with {} for {}.{}".format(
            ret["id"], ip_local, self.id, info["value"], self.sub_domain, self.domain,
        ))
        self.id = ret["id"]

    def __ddns_modify(self, ip_local):
        info = self.get_record_info(domain=self.domain, id=self.id)
        if ip_local == info["value"]:
            logger.warning("Record which id {} and host {} has modified: information {}".format(
                self.id, self.addr, {"ttl": info["ttl"], "interval": self.interval}
            ))
        else:
            ret = self.record_modify(domain=self.domain, subDomain=self.sub_domain, recordId=self.id, value=ip_local)

            logger.info("Update record which id {} and host {} change ip from {} to {} ".format(
            self.id, self.addr, info["value"], ip_local
            ))

    def ddns(self, modify=True, **kwargs):
        ip_local = get_host_ip()
        ip_remote = self.get_rm_ip()
        if ip_local not in ip_remote:
            logger.info("remote: {}, local: {}".format(ip_remote, ip_local))
            if kwargs.get("mode") == "prod":
                self.update_record_list()
            if modify:
                self.__ddns_modify(ip_local)
            else:
                self.__ddns_delete(ip_local)
        else:
            logger.info("Ip {} has not changed".format(ip_local))

    def run(self, **kwargs):
        def __main():
            from time import sleep
            while 1:
                try:
                    self.ddns(**kwargs)
                    sleep(self.interval)
                except KeyboardInterrupt:
                    logger.info("Exit for user interrupt")
                    import sys
                    sys.exit()
                except Exception as e:
                    logger.warning("ipv6 ddns error {}".format(e))

        if kwargs.get("unblock"):
            from threading import Thread
            Thread(target=__main).start()
        else:
            __main()


if __name__ == '__main__':
    api = DDns()
    api.ddns()
    api.run()
