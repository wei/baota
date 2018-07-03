#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
setup_path=/www
CN='125.88.182.172'
HK='download.bt.cn'
HK2='103.224.251.67'
US='128.1.164.196'
sleep 0.5;
CN_PING=`ping -c 1 -w 1 $CN|grep time=|awk '{print $7}'|sed "s/time=//"`
HK_PING=`ping -c 1 -w 1 $HK|grep time=|awk '{print $7}'|sed "s/time=//"`
HK2_PING=`ping -c 1 -w 1 $HK2|grep time=|awk '{print $7}'|sed "s/time=//"`
US_PING=`ping -c 1 -w 1 $US|grep time=|awk '{print $7}'|sed "s/time=//"`

echo "$HK_PING $HK" > ping.pl
echo "$HK2_PING $HK2" >> ping.pl
echo "$US_PING $US" >> ping.pl
echo "$CN_PING $CN" >> ping.pl
nodeAddr=`sort -V ping.pl|sed -n '1p'|awk '{print $2}'`
if [ "$nodeAddr" == "" ];then
	nodeAddr=$HK2
fi

download_Url=http://$nodeAddr:5880

version=$1

if [ "$version" = '' ];then
	updateApi=https://www.bt.cn/Api/updateLinux
	if [ -f /www/server/panel/plugin/beta/beta_main.py ];then
		updateApi=https://www.bt.cn/Api/updateLinuxBeta
	fi
	version=`/usr/local/curl/bin/curl $updateApi 2>/dev/null|grep -Po '"version":".*?"'|grep -Po '[0-9\.]+'`
fi

if [ "$version" = '' ];then
	echo '版本号获取失败,请手动在第一个参数传入!';
	exit;
fi

wget -T 5 -O panel.zip $download_Url/install/update/LinuxPanel-$version.zip

unzip -o panel.zip -d $setup_path/server/ > /dev/null
rm -f panel.zip
cd $setup_path/server/panel/
rm -f $setup_path/server/panel/class/*.pyc
python -m compileall $setup_path/server/panel/
python -m compileall $setup_path/server/panel/main.py
python -m compileall $setup_path/server/panel/task.py
python -m compileall $setup_path/server/panel/tools.py
if [ -f "main.py" ];then
	python -m py_compile main.py
fi
if [ -f "task.py" ];then
	python -m py_compile task.py
fi
if [ -f "tools.py" ];then
	python -m py_compile tools.py
fi

rm -f $setup_path/server/panel/data/templates.pl
check_bt=`cat /etc/init.d/bt`
if [ "${check_bt}" = "" ];then
	rm -f /etc/init.d/bt
	wget -O /etc/init.d/bt $download_Url/install/src/bt.init -T 10
	chmod +x /etc/init.d/bt
fi
if [ ! -f "/etc/init.d/bt" ]; then
	wget -O /etc/init.d/bt $download_Url/install/src/bt.init -T 10
	chmod +x /etc/init.d/bt
fi
sleep 1 && service bt restart > /dev/null 2>&1 &
echo "====================================="
echo "已成功升级到[$version]";

