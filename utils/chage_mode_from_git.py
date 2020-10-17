#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
# @Date    : 2020-10-17 11:15:44
# @Author  : Shenchucheng (shenchucheng@126.com)
# @Desc    : 同步文件夹权限


import logging
import os


logger = logging.getLogger(__name__)


def chmodr(target, follow):
    times = 0
    for root, dirs, files in os.walk(target):
        tempdir = root.replace(target, follow, 1)
        for file in dirs + files:
            tempfile = os.path.join(tempdir, file)
            file = os.path.join(root, file)
            if os.path.exists(tempfile):
                k = os.path.join(root, file)
                m1 = os.stat(tempfile).st_mode
                m2 = os.stat(file).st_mode
                if m1 != m2:
                    os.chmod(file, m1)
                    logger.debug('chage %s mode from %s to %s', k, m2, m1)
                    times += 1
    logger.info('change records total %s', times)


def main():
    import sys
    logging.basicConfig(level = logging.DEBUG)
    _, target, follow = sys.argv
    chmodr(target, follow)


if __name__ == "__main__":
    main()
     
