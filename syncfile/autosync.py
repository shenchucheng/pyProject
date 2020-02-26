import os
import yaml
from bypy import ByPy


pan = ByPy()
__home = os.path.expanduser("~")
__default = ".TransferStation/"
__conffile = os.path.join(__home, ".bypy", "sync.conf")
if not os.path.exists(__conffile):
    with open(__conffile, "w") as f:
        f.write("# This is used for bypy to syncup file\n")
        f.write("# Setting the local and remote path \n")
        f.write("# Example:\n# C:\\User\\cheng\\Downloads: test/downloads")
        f.write("# C:\\User\\cheng\\.bypy: /bypy/app/test/.bypy")


def sync_file():
    with open(__conffile) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
        if conf is None:
            raise NotImplementedError(
                "Fatal Error: syncup conf file without setting. " +
                "File has initialised in {}".format(__conffile)
            )
    for l, r in conf.items():
        pan.syncup(l, r or __default+l.replace(os.sep, '.').replace(":", ''))


if __name__ == '__main__':
    sync_file()
