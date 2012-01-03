from ttllist import TTLList

class Backends(object):
    def __init__(self):
        self.subs = {}
        self.tainted = False

    def refresh(self):
        for key,servers in list(self.subs.items()):
            print 'refresh', key, servers.data
            servers.refresh()
            if not servers.data:
               del self.subs[key]

    def add(self, server):
        servers = self.subs.get(server.key) or TTLList(taint=self)
        servers.append(server.address)

        self.subs[server.key] = servers
        rev, app = server.key.split('.', 1)

        if app not in self.subs:
            self.subs[app] = servers

    def export(self):
        for key, servers in list(self.subs.items()):
            yield key, servers.export()


    def bind(self, key, ver):
        if ver not in self.subs:
            return

        self.subs[key] = self.subs[ver]

        return True

    def taint(self):
        print 'tainted!'
        self.tainted = True
