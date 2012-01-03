import socket
from simplejson import dumps, loads
from collections import namedtuple
from threading import Thread
import uwsgi_proto
from backends import Backends

UDP_IP="0.0.0.0"
UDP_PORT=2626

CONTROL = ("0.0.0.0", 2626,)

sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
sock.bind( (UDP_IP,UDP_PORT) )

back = Backends()

UPLINK = [
   ('localhost', 12626),
]

Serv = namedtuple('Serv', ['k', 'key', 'a', 'address'])


def recv():
    try:
        raw, addr = sock.recvfrom( 100 ) # buffer size is 1024 bytes
    except socket.timeout:
        return

    server = Serv._make(uwsgi_proto.split(raw))
    back.add(server)


def control_loop():
    control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control.bind(CONTROL)
    control.listen(1)
    for conn, addr in iter(control.accept, None):
        conn.send(dumps(list(back.export())))

        try:
            raw = conn.recv(4096)
            if not raw:
                conn.close()
                continue

        except socket.error:
            continue

        setver = loads(raw)
        for key, ver in setver.items():
            back.bind(key, ver)

        conn.close()

def recv_loop():
    sock.settimeout(5)
    while True:
        try:
            back.refresh()
        except:
            pass

        try:
            recv()
        except:
            pass

if __name__ == '__main__':
    udp = Thread(target=recv_loop)
    udp.daemon = True
    udp.start()

    control_loop()
