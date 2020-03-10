from os import makedirs
from os.path import dirname, exists
from queue import Queue
from requests import Session


def tofile(p):
    return "..\\"+p.replace("://", "\\").replace("-", "_").replace("/", "\\")


def save():
    s = Session()
    while q.qsize():
        p = q.get()
        r = s.get(p)
        if r.status_code == 200:
            print("ok, {}".format(p))
            r.encoding = r.apparent_encoding
            p = tofile(p)
            _p = dirname(p)
            if not exists(_p):
                makedirs(_p)
            with open(p, "w") as f:
                f.write(r.text)
        else:
            print("error {}, {}".format(r.text, p))


if __name__ == '__main__':
    q = Queue()
