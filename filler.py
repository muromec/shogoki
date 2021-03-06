#!/usr/bin/env python

import socket
from simplejson import loads, dumps

def dump(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(host)
    data = s.recv(4096)
    print data
    for host, servers in loads(data):
        print host
        print servers
        print '----'

def setver(host, key, ver):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(host)
    s.send(dumps({key:ver}))


if __name__ == '__main__':
    import sys
    uplink = ('localhost',2626)
    if sys.argv[1:]:
        setver(uplink, *sys.argv[1:])
    else:
        dump(uplink)
