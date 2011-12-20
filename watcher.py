import socket
from simplejson import dumps, loads
import struct
from collections import namedtuple
from threading import Thread
from time import time, sleep

UDP_IP="0.0.0.0"
UDP_PORT=2626

CONTROL = ("0.0.0.0", 2626,)

sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
sock.bind( (UDP_IP,UDP_PORT) )

BIND = {}
SUBS = {}

UPLINK = [
   ('localhost', 12626),
]

class Up:
  touch = 0

def split(data):
    limit = len(data)
    pos = 0

    mod1,sz,mod2 = struct.unpack_from('=BHB', data, pos)
    assert mod1 == 224
    assert mod2 == 0

    pos += 4

    while pos < limit:
      [sz] = struct.unpack_from('H', data, pos)
      pos += 2
      key = data[pos:pos+sz]
      pos += sz

      [sz] = struct.unpack_from('H', data, pos)
      pos += 2
      val = data[pos:pos+sz]
      pos += sz

      yield key
      yield val

def pack(data):
    pack = ""
    for key in data:
      pack += struct.pack('h', len(key))
      pack += key

    head = struct.pack('=bhb', 111, len(pack), 1)
    return head+pack

Serv = namedtuple('Serv', ['k', 'key', 'a', 'address'])

class TTLList(object):
    def __init__(self,):
        self.data = []
        self.ttl = 12

    def append(self, item):
        for x,(_item,_touch) in enumerate(self.data):
            if _item == item:
                self.data[x] = (_item, time())
                return
 
        Up.touch = time()
        self.data.append((item, Up.touch))

    def __repr__(self):
        return repr(self.data)

    def refresh(self):
        now = time()
        _len = len(self.data)
        self.data = [
                (item,touch)
                for item,touch in self.data
                if touch+self.ttl > now
        ]

        if len(self.data) != _len:
            Up.touch = now

    def export(self):
        return [
                item
                for item,touch in self.data
        ]

def drop_old():
    for servers in BIND.values():
        servers.refresh()

def recv():
    try:
        raw, addr = sock.recvfrom( 100 ) # buffer size is 1024 bytes
    except socket.timeout:
        return

    server = Serv._make(split(raw))

    servers = SUBS.get(server.key) or TTLList()
    servers.append(server.address)

    SUBS[server.key] = servers
    rev, app = server.key.split('.')

    if app not in SUBS:
        SUBS[app] = servers

def control_loop():
    control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control.bind(CONTROL)
    control.listen(1)
    for conn, addr in iter(control.accept, None):
        conn.send(dumps([
            (key,servers.export())
            for key,servers in SUBS.items()
        ]))
        try:
            raw = conn.recv(4096)
        except socket.error:
            continue

        if raw:
            setver = loads(raw)
            for key, ver in setver.items():
                if ver in SUBS:
                    SUBS[key] = SUBS[ver]
                    Up.touch = time()
                    send_up(Up.touch)


        conn.close()


def uplink_loop():
    while True:
        for servers in SUBS.values():
            servers.refresh()

            try:
                send_up(Up.touch)
            except Exception, e:
                print 'fail', e
                pass

        sleep(9)

def send_up(touched):
    data = dict([
        (host, servers.export())
        for host, servers in SUBS.items()
    ])
    for up in UPLINK:
        send(up, data, touched)

def send(host, binds, touched):
    import pickle
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(host)
    s.send(pack(['binds', dumps(binds)]))
    s.close()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(host)
    s.send(pack(['binds_update', str(int(touched))]))
    s.close()


def recv_loop():
    sock.settimeout(5)
    while True:
        recv()

if __name__ == '__main__':
    udp = Thread(target=recv_loop)
    udp.daemon = True
    udp.start()

    uplink = Thread(target=uplink_loop)
    uplink.daemon = True
    uplink.start()

    control_loop()
