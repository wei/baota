#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
setup_path=/www
wget -T 5 -O panel.zip $1
unzip -o panel.zip -d $setup_path/server/ > /dev/null
rm -f panel.zip
cd $setup_path/server/panel/
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

service bt restart