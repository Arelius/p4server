from fabric.api import *
from fabric.contrib import *
from fabric.contrib.files import *
from os.path import basename
import json

binprefix = "bin/FreeBSD10-x64/"

settings = json.load(open('settings.cfg'))

#env.sudo_prefix = "su -m root -c "
env.shell = "/bin/sh -c "

emulateSudo = settings["install_sudo"]

def sudu(cmd):
    if emulateSudo:
        run("su -m root -c'" + cmd + "'")
    else:
        sudo(cmd)

def ports_install():
    sudu("portsnap fetch")
    sudu("portsnap extract")

def install_from_ports(pkg, cat):
    with cd("/usr/ports/" + cat + "/" + pkg):
        sudu("make install clean BATCH=yes")

def install_from_pkg(pkg, cat):
    sudu("pkg install -y " + pkg)

def install(pkg, cat):
    install_from_pkg(pkg, cat)

def sudo_install():
    install('sudo', 'security')
    put("sudoers", "/tmp/sudoers", mode=0640)
    sudu("chown root /tmp/sudoers")
    sudu("mv /tmp/sudoers /usr/local/etc/sudoers")

def create_user():
    sudo("pw useradd perforce -m");

def mvown(src, dest, user):
    sudo("mv %s %s" % (src, dest))
    sudo("chown %s %s" % (user, dest))

def putown(src, dest, user, mode):
    tmp = basename(src)
    tmppath = "/tmp/%s" % tmp
    destpath = dest
    if basename(dest) == "":
        destpath += tmp
    put(src, tmppath, mode=mode)
    mvown(tmppath, destpath, user)

def s3cmd_install():
    install('py27-s3cmd', 'net')
    upload_template("s3cfg.cfg", "/tmp/.s3cfg", mode=0600, use_jinja=True, context=settings)
    mvown("/tmp/.s3cfg", "/home/perforce/.s3cfg", "perforce")

def upload_bin():
    putown(binprefix + "p4d", "/usr/local/sbin/", "root", 0755)
    putown(binprefix + "p4", "/usr/local/sbin/", "root", 0755)

def setup_init():
    upload_template("p4d.sh", "/tmp/p4d.sh", mode=0755, use_jinja=True, context=settings)
    mvown("/tmp/p4d.sh", "/etc/rc.d/p4d", "root")
    #append("/etc/rc.conf", "p4d_enable=YES", use_sudo=True, shell=True, escape=False)
    sudo("echo 'p4d_enable=YES' >> /etc/rc.conf")
    sudo("mkdir /var/run/p4d/")
    sudo("chown perforce:perforce /var/run/p4d")

def config_p4():
    sudo("mkdir %s" % settings["p4_root"])
    sudo("chown perforce %s" % settings["p4_root"])

def setup_backup():
    upload_template("backup_to_s3.sh", "/tmp/backup_to_s3", mode=0755, use_jinja=True, context=settings)
    mvown("/tmp/backup_to_s3", "/usr/local/bin/backup_to_s3", "root")

def p4_server():
    if settings["install_sudo"]:
        sudo_install()
    create_user()
    s3cmd_install()
    upload_bin()
    setup_init()
    config_p4()
    setup_backup()

def restore_backup():
    sudo("s3cmd get s3://%s/%s /tmp/backup.tar.gz" % (settings["s3_bucket"], settings["s3_restore_file"]), user="perforce")
    sudo("tar xzf /tmp/backup.tar.gz -C %s" % settings["p4_root"])
    sudo("rm /tmp/backup.tar.gz", user="perforce")

def start_p4d():
    sudo("/etc/rc.d/p4d start");

def stop_p4d():
    sudo("/etc/rc.d/p4d stop");

def test():
    run("echo test")
