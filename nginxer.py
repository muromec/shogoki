import subprocess

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

    for serv, ver, up in backends:
        print serv, 'v', ver, 'u', up
        dom = str.join('',reversed(serv.split('-')))
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
