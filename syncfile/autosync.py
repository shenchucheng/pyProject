#!/usr/bin/env python3
import os
import yaml
from os.path import join, abspath, exists, dirname
from bypy import __file__ as __bypy_path

__bypy_path = join(dirname(__bypy_path), "bypy_dev.py")
if not exists(__bypy_path):
    with open(join(dirname(__bypy_path), "bypy.py")) as f:
        lines = f.read()
    # lines = lines.replace("from .", "from bypy.").replace("from bypy. ", "from bypy ")
    lines = lines.replace("md5 = f['md5']", "md5 = f['block_list'][0]")
    with open(__bypy_path, "w") as f:
        f.write(lines)
from bypy.bypy_dev import ByPy


def __get_file(top=".", **kwargs):
    ws = os.walk(abspath(top), **kwargs)
    files = []
    dirs = []
    for i in ws:
        path = i[0]
        for i1 in i[1]:
            dirs.append(join(path, i1))
        for i2 in i[2]:
            files.append(join(path, i2))
    return dirs, files


def sync_file(conf, default):
    if not os.path.exists(conf):
        with open(conf, "w") as f:
            f.write("# This is used for bypy to syncup file\n")
            f.write("# Setting the local and remote path \n")
            f.write("# Example:\n# C:\\User\\cheng\\Downloads: test/downloads")
            f.write("# /home/cheng/.bypy: test/.bypy")

    with open(conf) as f:
        __conf = yaml.load(f, Loader=yaml.FullLoader)
        if __conf is None:
            raise NotImplementedError(
                "Fatal Error: syncup conf file without setting. " +
                "File has initialised in {}".format(conf)
            )

    for l, r in __conf.items():
        pan.syncup(l, r or default+l.replace(os.sep, '.').replace(":", ''))


pan = ByPy()


if __name__ == '__main__':
    import argparse
    __default = ".TransferStation/"
    __home = os.path.expanduser("~")
    __conffile = os.path.join(__home, ".bypy", "sync.conf")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--remote', '-r', default=__default,
        help='syncup file to remote dir if not set, default: {}'.format(__default)
    )
    parser.add_argument(
        '--config', '-c', default=__conffile, 
        help='config file path, default: {}'.format(__conffile)
    )
    args = parser.parse_args()
    pan.compare("test", r"C:\Users\cheng\test")
    # sync_file(args.config, args.remote)

