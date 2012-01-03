import os
import signal

def format_back(up):
    print up
    ret = ""
    for srv in up:
        ret += 'server %s;' % srv

    return ret

def reconfig(backends):
    tpl_f = open('/etc/shogoki/server.conf')
    tpl = tpl_f.read()
    tpl_f.close()

    for serv, up in backends:
        conf = tpl % {
                "serv": serv,
                "domain": serv,
                "up": format_back(up),
        }

        conf_f = open('/var/run/shogoki/%s.conf' % serv, 'w')
        # TRUNCATE!!!
        conf_f.write(conf)
        conf_f.close()


    pid_f = open('/var/run/nginx.pid')
    pid_s = pid_f.read()
    pid_f.close()

    os.kill(int(pid_s), signal.SIGHUP)
