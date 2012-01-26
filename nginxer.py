import os
import subprocess

def load():
	if not os.access('/etc/shogoki/domains', 0):
	    return {}

	bind_f = open('/etc/shogoki/domains', 'r')
	raw = bind_f.read()
	bind_f.close()

	import yaml
	try:
	    return yaml.load(raw)
	except Exception, e:
	    return {}


def format_back(up):
    print up
    ret = ""
    for srv in up:
        ret += "server %s;\n" % srv

    return ret

def reconfig(backends):
    tpl_f = open('/etc/shogoki/server.conf')
    tpl = tpl_f.read()
    tpl_f.close()

    doms = load()
    print doms
    for serv, ver, up in backends:
        if not backends:
            os.unlink('/var/run/shogoki/%s.conf' % serv)
            continue

        print serv, 'v', ver, 'u', up
        dom = doms.get(serv, serv)

        if isinstance(dom, list):
	    dom = str.join(' ', dom)

        conf = tpl % {
                "serv": serv,
                "domain": dom,
                "up": format_back(up),
                "ver": ver,
        }

        conf_f = open('/var/run/shogoki/%s.conf' % serv, 'w')
        # TRUNCATE!!!
        conf_f.write(conf)
        conf_f.close()


    subprocess.call(["sudo", "service", "nginx", "reload"])
