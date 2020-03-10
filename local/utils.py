import os
import re
from os.path import join


def generate_files(path=".", absolute=False):
    if absolute:
        path = os.path.abspath(path)
    for i in os.walk(path):
        d = i[0]
        for p in i[2]:
            yield join(d, p)


def get_all_files(**kwargs):
    return list(generate_files(**kwargs))


def search_file(content: str, path=".", encoding="utf-8", ):
    content = content.encode(encoding)
    for i in generate_files(path):
        with open(i, "rb") as f:
            for line in f:
                if content in line:
                    yield i
                    break


def replace(old, new, *ignore, encoding="utf-8", path=".", suffix=".backup"):
    old, new = old.encode(encoding), new.encode(encoding)
    ignore = list(re.compile(i) for i in ignore)
    for i in os.walk("."):
        for p in i[2]:
            if p.endswith(suffix):
                break
            if not all(_.match(p) for _ in ignore):
                break
            temp = "." + p
            temp = join(i[0], temp)
            p = join(i[0], p)
            os.replace(p, temp)
            change = False
            with open(temp, "rb") as _f:
                with open(p, "wb") as f:
                    for line in _f:
                        if old in line:
                            line.replace(old, new)
                            change = True
                            print("file: ", p, "\nposition: ", f.tell())
                        f.write(line)
            if change:
                os.replace(temp, p+suffix)


