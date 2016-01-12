#!/bin/sh

. /etc/rc.subr

name=p4d
rcvar=p4d_enable
dbroot="{{ p4_root }}"
dbjournal="{{ p4_root }}/journal"
pidfile="/var/run/$name/$name.pid"
p4d_user=perforce

command="/usr/local/sbin/$name"
command_args="-r $dbroot -J $dbjournal --pid-file=$pidfile -d"

load_rc_config $name
run_rc_command "$1"
