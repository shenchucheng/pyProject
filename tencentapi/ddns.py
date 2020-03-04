#!/usr/bin/env python3
import sys
import socket
import sqlite3
import time
from random import randint
sys.path.append("/home/cheng/pyProject/tencentapi/")
from tencentApi import CnsApi as QcloudApi


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
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info("current: {}, ipv6: {}".format(now, ipv6))
        con = sqlite3.connect("ipv6.db")
        cur = con.execute("select max(time), ipv6 from records")
        result = cur.fetchone()
        last_time, ipv6_ = result
        logger.info("last time: {}, ipv6 is {}".format(last_time, ipv6))
        cur.execute("insert into records values (?, ?)",
                    (now,ipv6))
        if ipv6_ != ipv6:
            ret = recordmodify(ipv6)
            logger.info(str(ret))
            logger.info("ipv6 record change from {} to {}".format(ipv6_, ipv6))
            with open("ipv6.txt","a") as f:
                f.write(ipv6)         
        else:
            logger.info("ipv6 does not change")

    finally:
        con.commit()
        con.close()
if __name__ == "__main__":
    import os
    os.chdir("/home/cheng/pyProject/tencentapi/")
    import logging
    logger = logging.getLogger("ddns")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("log.txt")
    fh.setLevel(logging.INFO)
    fmt = '%(asctime)s [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    while 1:
        main()
        time.sleep(randint(300,900))

