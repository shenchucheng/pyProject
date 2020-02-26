#!/usr/bin/env python3
import os
import yaml
from bypy import ByPy


pan = ByPy()
__home = os.path.expanduser("~")
__default = ".TransferStation/"
__conffile = os.path.join(__home, ".bypy", "sync.conf")


def sync_file(conf, default):
    if not os.path.exists(conf):
        with open(conf, "w") as f:
            f.write("# This is used for bypy to syncup file\n")
            f.write("# Setting the local and remote path \n")
            f.write("# Example:\n# C:\\User\\cheng\\Downloads: test/downloads")
            f.write("# /home/cheng/.bypy: test/.bypy")

    with open(conf) as f:
        __conf = yaml.load(f, Loader=yaml.FullLoader)
        if conf is None:
            raise NotImplementedError(
                "Fatal Error: syncup conf file without setting. " +
                "File has initialised in {}".format(__conffile)
            )

    for l, r in __conf.items():
        pan.syncup(l, r or __default+l.replace(os.sep, '.').replace(":", ''))


if __name__ == '__main__':
    import argparse
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
    sync_file(args.config, args.remote)

