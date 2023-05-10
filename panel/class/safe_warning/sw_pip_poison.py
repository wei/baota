#!/usr/bin/python
#coding: utf-8

import os, re, public

_title = 'pypi供应链投毒检测'
_version = 1.0  # 版本
_ps = "pypi供应链投毒检测"  # 描述
_level = 2  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2023-03-14'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_pip_poison.pl")
_tips = [
    "执行命令btpip uninstall 【检测出来的恶意库名】",
]
_help = ''


def check_run():
    pip = public.ExecShell("btpip freeze | grep -E \"istrib|djanga|easyinstall|junkeldat|libpeshka|mumpy|mybiubiubiu|nmap"
                               "-python|openvc|python-ftp|pythonkafka|python-mongo|python-mysql|python-mysqldb|python"
                               "-openssl|python-sqlite|virtualnv|mateplotlib|request=\"")[0].strip()
    if 'command not found' in pip or '未找到命令' in pip:
        return True, '无风险，未安装pip'
    if pip:
        pip = pip.split('\n')
        return False, '【{}】python库存在安全风险，请尽快处理'.format('、'.join(pip))
    else:
        return True, '无风险'

