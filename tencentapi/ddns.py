import socket
import sqlite3
import time
from random import randint
from cns import QcloudApi


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

def recordmodify(value=None):
    qcloud = QcloudApi()
    ret = qcloud.get(action="RecordModify",
                     domain="phichem.xyz", 
                     subDomain="ipv6", 
                     value=value or get_host_ip(), 
                     recordType="AAAA", 
                     recordId="541603110", 
                     recordLine="默认")
    return ret

def main():
    try:
        ipv6 = get_host_ip()
        print("ipv6 current: ", ipv6)
        con = sqlite3.connect("ipv6.db")
        con.execute("insert into records values (?, ?)",
                    (time.strftime("%Y-%M-%d %H:%m:%S"),ipv6))
        with open("ipv6.txt") as f:
            ipv6_ = f.read()
        if ipv6_ != ipv6:
            ret = recordmodify(ipv6)
            print(ret, "\n", "ipv6 record change from {} to {}".format(ipv6_, ipv6))
            with open("ipv6.txt","w") as f:
                f.write(ipv6)         
        else:
            print("ipv6 does not change")

    finally:
        con.commit()
        con.close()
if __name__ == "__main__":
    while 1:
        main()
        time.sleep(randint(300,900))


