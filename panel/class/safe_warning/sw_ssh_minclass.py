#!/usr/bin/python
# coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: hwliang <hwl@bt.cn>
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# SSH密码复杂度检查
# -------------------------------------------------------------------
# import sys, os
# os.chdir('/www/server/panel')
# sys.path.append("class/")
import os, sys, re, public

_title = 'SSH密码复杂度检查'
_version = 1.0  # 版本
_ps = "SSH密码复杂度检查"  # 描述
_level = 2  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2022-08-10'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_ssh_minclass.pl")
_tips = [
    "【/etc/security/pwquality.conf】 把minclass（至少包含小写字母、大写字母、数字、特殊字符等4类字符中等3类或4类）设置为3或4。如：",
    "minclass=3",
]
_help = ''


def check_run():
    try:
        p_file = '/etc/security/pwquality.conf'
        p_body = public.readFile(p_file)
        if not p_body: return True, '无风险'
        tmp = re.findall("\s*minclass\s+=\s+(.+)", p_body, re.M)
        if not tmp: return True, '无风险'
        minlen = tmp[0].strip()
        if int(minlen) <3:
            return False, '【%s】文件中把minclass设置置为3或者4' % p_file
        return True, '无风险'
    except:
        return True, '无风险'
