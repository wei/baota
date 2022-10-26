#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

check_gevent_version(){
    is_gevent140=$(/www/server/panel/pyenv/bin/python3 -c "import gevent;print(gevent.__version__)"|grep  -E '^1.')
}

check_gevent_version
if [ "${is_gevent140}" = "" ];then
    exit;
fi

/www/server/panel/pyenv/bin/pip3 install gevent -U

check_gevent_version
if [ "${is_gevent140}" = "" ];then
    rm -f /www/server/panel/script/upgrade_gevent.sh
    bash /www/server/panel/init.sh reload
fi
