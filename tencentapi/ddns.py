import socket
import sqlite3
import time
from random import randint
from tencentApi import CnsApi

api = CnsApi()


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


def modify_record_ipv6(ip=""):
    return api.record_modify(
        domain="phichem.xyz",
        subDomain="ipv6",
        value=ip or get_host_ip(),
        recordType="AAAA",
        recordId="541603110",
        recordLine="默认"
    )


def main():
    try:
        ipv6 = get_host_ip()
        print("ipv6 current: ", ipv6)
        con = sqlite3.connect("ipv6.db")
        con.execute("insert into records values (?, ?)",
                    (time.strftime("%Y-%M-%d %H:%m:%S"), ipv6))
        with open("ipv6.txt") as f:
            ipv6_ = f.read()
        if ipv6_ != ipv6:
            ret = modify_record_ipv6(ipv6)
            print(ret, "\n", "ipv6 record change from {} to {}".format(ipv6_, ipv6))
            with open("ipv6.txt", "w") as f:
                f.write(ipv6)
        else:
            print("ipv6 does not change")

    finally:
        con.commit()
        con.close()


if __name__ == "__main__":
    while 1:
        main()
        time.sleep(randint(300, 900))
