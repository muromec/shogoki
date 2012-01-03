from ttllist import TTLList
import nginxer

class Backends(object):
    def __init__(self):
        self.subs = {}
        self.binds = {}
        self.tainted = False

    def refresh(self):
        for key,servers in list(self.subs.items()):
            print 'refresh', key, servers.data
            servers.refresh()
            if not servers.data:
               del self.subs[key]

    def add(self, server):
        servers = self.subs.get(server.key) or TTLList(taint=self)
        self.subs[server.key] = servers
        servers.append(server.address)

    def export(self):
        for key, servers in list(self.subs.items()):
            yield key, servers.export()

        for key in list(self.binds.keys()):
            yield key, self.serving(key)


    @property
    def conf(self):
        apps = set([
            key.rsplit('.',1)[-1]
            for key in self.subs.keys()
        ])

        for key in apps:
            yield key, self.serving(key)

    def bind(self, key, ver):
        self.binds[key] = ver
        self.taint()

        return True

    def serving(self, key):
        pin = self.binds.get(key)

        servers = self.subs.get(pin)
        if servers:
            return servers.export()

        versions = sorted([
                ver
                for ver in self.subs
                if ver.rsplit('.', 1)[-1] == key
        ])

        if not versions:
            return []

        servers = self.subs.get(versions[-1])
        if servers:
            return servers.export()

        return []


    def taint(self):
        print 'tainted!'
        self.tainted = True
        nginxer.reconfig(self.conf)
