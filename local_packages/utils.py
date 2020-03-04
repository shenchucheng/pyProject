import os
from os.path import join


def get_all_files(path="."):
    paths = []
    for i in os.walk(path):
        d = i[0]
        for p in i[2]:
            paths.append(join(d, p))
    return paths


def generate_files(path="."):
    for i in os.walk(path):
        d = i[0]
        for p in i[2]:
            yield join(d, p)
