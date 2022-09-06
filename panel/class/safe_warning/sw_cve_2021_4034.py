#!/usr/bin/python
# coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: lkq <lkq@bt.cn>
# -------------------------------------------------------------------
# Time: 2022-08-10
# -------------------------------------------------------------------
# CVE-2021-4034 polkit pkexec 本地提权漏洞检测
# -------------------------------------------------------------------
# import sys, os
# os.chdir('/www/server/panel')
# sys.path.append("class/")
import  public, os
_title = 'CVE-2021-4034 polkit pkexec 本地提权漏洞检测'
_version = 1.0  # 版本
_ps = "CVE-2021-4034 polkit pkexec 本地提权漏洞检测"  # 描述
_level = 3  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2022-8-10'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_cve_2021_4034.pl")
_tips = [
    "更新polkit 组件"
]
_help = ''



def check_run():
    '''
        @name CVE-2021-4034 polkit pkexec 本地提权漏洞检测
        @time 2022-08-12
        @author lkq@bt.cn
    '''

    redhat_file = '/etc/redhat-release'
    if os.path.exists(redhat_file):
        data=public.ReadFile(redhat_file)
        if not data:return True, '无风险1'
        if data.find('CentOS Linux release 7.') != -1:
            polkit=public.ExecShell("rpm -q polkit-0.*")
            if not polkit[0]:return True, '无风险'
            polkit_list = polkit[0].strip()
            if polkit_list.find('polkit-0') != -1:return True, '无风险'
            p = polkit_list.strip().split(".")
            if len(p)<2:return True, '无风险'
            if p[1] == '112-26':return True,'无风险'
            p2=p[1].split("-")
            if p2[1] <26:
                return False, '请更新polkit'
            return True,'无风险'
        #CentOS 8.0
        elif data.find('CentOS Linux release 8.0') == 0:
            polkit = public.ExecShell("rpm -q polkit-0.*")
            if not polkit[0]: return True, '无风险'
            polkit_list = polkit[0].strip()
            if polkit_list.find('polkit-0') != -1: return True, '无风险'
            # Centos 7
            p = polkit_list.strip().split(".")
            if len(p) < 2: return True, '无风险'
            if p[1] == '115-13': return True, '无风险'
            p2 = p[1].split("-")
            if p2[1] < 13:
                return False, '请更新polkit'
            return True, '无风险'
        elif data.find("CentOS Linux release 8.2") == 0:
            polkit = public.ExecShell("rpm -q polkit-0.*")
            if not polkit[0]: return True, '无风险'
            polkit_list = polkit[0].strip()
            if polkit_list.find('polkit-0') != -1: return True, '无风险'
            # Centos 7
            p = polkit_list.strip().split(".")
            if len(p) < 2: return True, '无风险'
            if p[1] == '115-11': return True, '无风险'
            p2 = p[1].split("-")
            if p2[1] < 11:
                return False, '请更新polkit'
            return True, '无风险'
        elif data.find("CentOS Linux release 8.5") == 0:
            polkit = public.ExecShell("rpm -q polkit-0.*")
            if not polkit[0]: return True, '无风险2'
            polkit_list = polkit[0].strip()
            if polkit_list.find('polkit-0.115-12') ==0:
                return False, '请更新polkit'
            return True, '无风险'
    return True, '无风险'