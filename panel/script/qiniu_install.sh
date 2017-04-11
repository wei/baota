#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'
download_Url=http://download.bt.cn
Install_Qiniu()
{
	echo '正在安装前置组件...' > $install_tmp
	country=`curl -sS --connect-timeout 10 -m 60 http://ip.vpser.net/country`
	if [ "${country}" = "CN" ]; then
		mkdir ~/.pip
		cat > ~/.pip/pip.conf <<EOF
[global]
index-url = https://pypi.doubanio.com/simple/

[install]
trusted-host=pypi.doubanio.com
EOF
    fi
	
	tmp=`python -V 2>&1|awk '{print $2}'`
	pVersion=${tmp:0:3}
	
	if [ ! -f "/usr/lib/python${pVersion}/site-packages/setuptools-33.1.1-py${pVersion}.egg" ];then
		wget $download_Url/install/src/setuptools-33.1.1.zip -T 10
		unzip setuptools-33.1.1.zip
		rm -f setuptools-33.1.1.zip
		cd setuptools-33.1.1
		python setup.py install
		cd ..
		rm -rf setuptools-33.1.1
	fi
	if [ ! -f "/usr/bin/pip" ];then
		wget $download_Url/install/src/pip-9.0.1.tar.gz -T 10
		tar xvf pip-9.0.1.tar.gz
		rm -f pip-9.0.1.tar.gz
		cd pip-9.0.1
		python setup.py install
		cd ..
		rm -rf pip-9.0.1
	fi
	
	pip install qiniu
	
	echo '正在安装脚本文件...' > $install_tmp
	wget -O /www/server/panel/script/backup_qiniu.py $download_Url/install/lib/script/backup_qiniu.py -T 5
	
	echo '安装完成' > $install_tmp
}

Uninstall_Qiniu()
{
	pip uninstall qiniu -y
	echo '卸载完成' > $install_tmp
}


action=$1
if [ "${1}" == 'install' ];then
	Install_Qiniu
else
	Uninstall_Qiniu
fi
