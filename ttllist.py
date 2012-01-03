from time import time

class TTLList(object):
    def __init__(self,taint=None):
        self.data = []
        self.ttl = 12
        self.parent = taint

    def append(self, item):
        for x,(_item,_touch) in enumerate(self.data):
            if _item == item:
                self.data[x] = (_item, time())
                return
 
        self.data.append((item, time()))
        self.parent.taint()

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

        if _len != len(self.data):
            self.parent.taint()

    def export(self):
        return [
                item
                for item,touch in self.data
        ]

