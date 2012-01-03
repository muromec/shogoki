import uwsgi
from simplejson import loads


class Bind:
    routes = {}
    update = -1
    idx = 0

    @classmethod
    def fetch(cls, time):
        routes = uwsgi.cache_get('binds')
        if routes:
            cls.routes = loads(routes)
            cls.update = time

    @classmethod
    def clear(cls):
        uwsgi.cache_del('binds')

def get(key):
    Bind.fetch(0)
    Bind.clear()

    Bind.idx += 1
    servers = Bind.routes.get(key)
    if not servers:
        return "/tmp/sock"

    print key, Bind.idx, servers
    return servers[Bind.idx % len(servers)]