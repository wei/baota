#!/usr/bin/python
#coding: utf-8

import os, re, public

_title = 'strace获取登录凭证后门检测'
_version = 1.0  # 版本
_ps = "检测进程中是否有通过strace命令获取其他用户账号信息"  # 描述
_level = 3  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2023-03-09'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_strace_backdoor.pl")
_tips = [
    "ps aux命令查看是否存在通过strace读取sshd登录凭证",
    "ps aux | grep strace",
    "若筛选出进程，则使用kill -9 【pid】命令停止进程"
]
_help = ''


def check_run():
    '''
        @name 开始检测
        @return tuple (status<bool>,msg<string>)
    '''
    sshd_pid = public.ExecShell('ps aux|grep "sshd -D"|grep -v grep|awk {\'print$2\'}')[0].strip()
    result = public.ExecShell('ps aux')[0].strip()
    rep = 'strace.*' + sshd_pid + '.*trace=read,write'
    tmp = re.search(rep, result)
    if tmp:
        return False, '存在通过strace窃取sshd登录信息的恶意进程'
    else:
        return True, '无风险'
