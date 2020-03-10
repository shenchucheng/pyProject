#!/usr/bin/env python3
import os, sys
import subprocess
import platform
import socket
import pyqrcode


def print_file(fileDir):
    OS = platform.system()
    if OS == 'Darwin':
        subprocess.call(['open', fileDir])
    elif OS == 'Linux':
        subprocess.call(['xdg-open', fileDir])
    else:
        os.startfile(fileDir)


def get_qr(data, img_file=''):
    img_file = img_file or 'QR.png'
    qr = pyqrcode.create(data)
    qr.png(img_file, 10)
    print_file(img_file)


def print_cmd_qr(qrText, white='', black='  ', enableCmdQR=True):
    if not white:
        try:
            b = u'\u2588'
            sys.stdout.write(b + '\r')
            sys.stdout.flush()
        except UnicodeEncodeError:
            BLOCK = 'MM'
        else:
            BLOCK = b
        white = BLOCK
    blockCount = int(enableCmdQR)
    if abs(blockCount) == 0:
        blockCount = 1
    white *= abs(blockCount)
    if blockCount < 0:
        white, black = black, white
    sys.stdout.write(' '*50 + '\r')
    sys.stdout.flush()
    qr = qrText.replace('0', white).replace('1', black)
    sys.stdout.write(qr)
    sys.stdout.flush()


def get_ipv4(dns=None):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((dns or "8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = None
    finally:
        s.close()
    return ip


def get_ipv6(dns=None):
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect((dns or "2001:4860:4860::8888", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = None
    finally:
        s.close()
    return ip


if __name__ == '__main__':
    import argparse
    from functools import partial
    from http import server

    parser = argparse.ArgumentParser()
    parser.add_argument('--cgi', action='store_true',
                       help='Run as CGI Server')
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('--directory', '-d', default=os.getcwd(),
                        help='Specify alternative directory '
                        '[default:current directory]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    parser.add_argument('--enableCmdQR', '-s', type=int, default=0)
    args = parser.parse_args()
    if args.cgi:
        handler_class = server.CGIHTTPRequestHandler
    else:
        if sys.version.startswith("3.6"):
            handler_class = server.SimpleHTTPRequestHandler
        else:
            handler_class = partial(server.SimpleHTTPRequestHandler,
                                directory=args.directory)
    try:
        ServerClass = server.ThreadingHTTPServer
    except AttributeError:
        ServerClass = server.HTTPServer
    if args.bind == "::":
        ServerClass.address_family = socket.AF_INET6
        ipaddr = "http://[{}]:{}".format(get_ipv6(), args.port)
    else:
        ip = get_ipv4()
        ipaddr = "http://{}:{}".format(ip, args.port)
    img_file = ".QR.png"
    if args.enableCmdQR:
        qr = pyqrcode.create(ipaddr)
        print_cmd_qr(qr.text(1), enableCmdQR=args.enableCmdQR)
        print(qr.terminal())
    else:
        get_qr(data=ipaddr, img_file=img_file)
    print(ipaddr)
    server.test(
        HandlerClass=handler_class,
        ServerClass=ServerClass,
        port=args.port, bind=args.bind
    )
    # os.remove(img_file)

