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
# Mysql 弱口令检测
# -------------------------------------------------------------------

import  public, os
_title = '面板未开启监控'
_version = 1.0  # 版本
_ps = "面板未开启监控"  # 描述
_level = 1  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2022-8-10'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_panel_control.pl")
_tips = [
    "在【设置】-【监控】中开启"
]
_help = ''

def check_run():
    '''
        @name 面板未开启监控
        @time 2022-08-12
        @author lkq@bt.cn
    '''
    send_type = ""
    if os.path.exists("/www/server/panel/data/control.conf"):
        return True, '无风险'
    return False, '请在【设置】-【监控】中开启'



