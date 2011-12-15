import socket
import struct
from collections import namedtuple

UDP_IP="0.0.0.0"
UDP_PORT=2626

sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
sock.bind( (UDP_IP,UDP_PORT) )

up = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP

BIND = {
  'rev_bde5690.quiz-fb': 'quiz-fb',
}
UPLINK = [
   ('192.168.122.200', 26262),
]

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
    head = struct.pack('=BHB', 224, 0, 3)
    for key in data:
      head += struct.pack('H', len(key))
      head += key

    return head

Serv = namedtuple('Serv', ['k', 'key', 'a', 'address'])

while True:
    raw, addr = sock.recvfrom( 1024 ) # buffer size is 1024 bytes
    data = Serv._make(split(raw))
    print data
    send = [raw]

    if data.key in BIND:
      bind_data = Serv(data.k, BIND[data.key], data.a, data.address)
      send.append(pack(bind_data))

    for uplink in UPLINK:
      for d in send:
        up.sendto(d, uplink)
