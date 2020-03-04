import os
import socket
import sqlite3
import time

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


def ddns(get_func_only=False, times=0, **kwargs):
    """
    :param get_func_only:
    :param times:
    :param kwargs:
    wd: word dir
    :return:
    """

    def __modify_record_ipv6(ip=""):
        api = CnsApi()
        return api.record_modify(
            domain="phichem.xyz",
            subDomain="file",
            value=ip or get_host_ip(),
            recordType="AAAA",
            recordId="540163804",  # ""541603110",
            recordLine="默认"
        )

    def __main(**kwargs):
        wd = kwargs.get("wd") or os.path.join(os.path.expanduser("~"), ".pyconfig", "tencentapi")
        try:
            ipv6 = get_host_ip()
            print("ipv6 current: ", ipv6)
            db_path = os.path.join(wd, "ipv6.db")
            txt_path = os.path.join(wd, "ipv6.txt")
            con = sqlite3.connect(db_path)
            con.execute("insert into records values (?, ?)",
                        (time.strftime("%Y-%M-%d %H:%m:%S"), ipv6))
            with open(txt_path) as f:
                ipv6_ = f.read()
            if ipv6_ != ipv6:
                ret = __modify_record_ipv6(ipv6)
                print(ret, "\n", "ipv6 record change from {} to {}".format(ipv6_, ipv6))
                with open(txt_path, "w") as f:
                    f.write(ipv6)
            else:
                print("ipv6 does not change")
        except FileNotFoundError :
            with open(txt_path, "w") as f:
                f.write("initialization")
            raise
        except sqlite3.OperationalError as e:
            if "no such table:" in e:
                con.execute("CREATE TABLE records (time CHAR(19), ip VARCHAR)")
                con.commit()
                con.close()
                raise
        finally:
            con.commit()
            con.close()
    if get_func_only:
        return __main
    elif times:
        for i in range(times):
            __main(**kwargs)
    else:
        while 1:
            __main(**kwargs)
            time.sleep(300)


if __name__ == "__main__":
    ddns()

