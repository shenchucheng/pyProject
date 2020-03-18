import os


__home = os.path.expanduser("~")
__ssr = "sslocal -s {} -p {} -k {} -m {}" 


def get_conf(p=os.path.join(__home, ".pyconfig", "breakFGW", "ssr.txt")):
    with open(p) as f:
        for i in f:
            yield i.split()


if __name__ == "__main__":
    from requests import get
    proxies={
            'http':'127.0.0.1:1080',
            'https':'127.0.0.1:1080'
            }
    for i in '1':#get_conf():
        r = get("http://httpbin.org/ip", proxies=proxies)
        print(r.text())

