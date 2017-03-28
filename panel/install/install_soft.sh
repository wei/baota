#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
serverUrl='http://download.bt.cn/install'
mtype=$1
actionType=$2
name=$3
version=$4

if [ ! -f 'lib.sh' ];then
	wget -O lib.sh $serverUrl/$mtype/lib.sh
fi
wget -O $name.sh $serverUrl/$mtype/$name.sh
if [ "$actionType" == 'install' ];then
	sh lib.sh
fi
sh $name.sh $actionType $version
