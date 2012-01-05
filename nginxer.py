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

    for serv, up in backends:
        dom = str.join('',reversed(serv.split('-')))
        conf = tpl % {
                "serv": serv,
                "domain": dom,
                "up": format_back(up),
        }

        conf_f = open('/var/run/shogoki/%s.conf' % serv, 'w')
        # TRUNCATE!!!
        conf_f.write(conf)
        conf_f.close()


    subprocess.call(["sudo", "service", "nginx", "reload"])
