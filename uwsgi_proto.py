import struct

def split(data, _mod1=224, _mod2 =0):
    limit = len(data)
    pos = 0

    mod1,sz,mod2 = struct.unpack_from('=BHB', data, pos)
    assert mod1 == _mod1, "Invalid mod1 %d" % mod1
    assert mod2 == _mod2, "Invalid mod2 %d" % mod2

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

def pack(data, ):
    pack = ""
    for key in data:
      pack += struct.pack('h', len(key))
      pack += key

    head = struct.pack('=bhb',111, len(pack), 1)
    return head+pack

