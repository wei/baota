#!/usr/bin/python
# coding: utf-8

import os, re, public


_title = '检查是否禁用whell组外的用户su为root'
_version = 1.0  # 版本
_ps = "检查是否使用PAM认证模块禁止wheel组之外的用户su为root"  # 描述
_level = 1  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2023-03-10'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_su_root.pl")
_tips = [
    "在文件【/etc/pam.d/su】中添加auth sufficient pam_rootok.so以及auth required pam_wheel.so group=wheel",
    "如需配置用户可以切换为root，则将用户加入wheel组，使用命令gpasswd -a username wheel",
]
_help = ''


def check_run():
    '''
        @name 开始检测
        @return tuple (status<bool>,msg<string>)
    '''
    cfile = '/etc/pam.d/su'
    if not os.path.exists(cfile):
        return True, '无风险'
    conf = public.readFile(cfile)
    rep1 = '[^#](\s*)auth(\s*)sufficient(\s*)pam_rootok.so'
    tmp1 = re.search(rep1, conf)
    if not tmp1:
        return False, '未禁止普通用户su为root用户'
    rep2 = '[^#](\s*)auth(\s*)required(\s*)pam_wheel.so(\s*)group(\s*)=(\s*)wheel'
    tmp2 = re.search(rep2, conf)
    if not tmp2:
        return True, '无风险，但未配置whell组用户可su'
    else:
        return True, '无风险'
