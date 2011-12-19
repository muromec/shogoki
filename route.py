import pickle
import uwsgi


class Bind:
    routes = {}
    update = -1
    idx = 0

    @classmethod
    def fetch(cls, time):
        routes = uwsgi.cache_get('binds')
        if routes:
            cls.routes  = pickle.loads(routes)
            cls.update = time

def get(key):
    binds_update = uwsgi.cache_get('binds_update') or 0
    if int(binds_update) > Bind.update:
        Bind.fetch(binds_update)

    Bind.idx += 1
    servers = Bind.routes.get(key)
    if not servers:
        return "/tmp/sock"

    return servers[Bind.idx % len(servers)]
