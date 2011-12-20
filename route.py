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
            cls.routes  = loads(routes)
            cls.update = time

    @classmethod
    def clear(cls):
        uwsgi.cache_del('binds_update')
        uwsgi.cache_del('binds')

def get(key):
    binds_update = uwsgi.cache_get('binds_update') or 0
    print binds_update, Bind.update
    if int(binds_update) > Bind.update:
        Bind.fetch(binds_update)
	Bind.clear()

    Bind.idx += 1
    servers = Bind.routes.get(key)
    print servers, key
    if not servers:
        return "/tmp/sock"

    return servers[Bind.idx % len(servers)]
