#coding: utf-8
#-------------------------------------------------------------------
# 宝塔Linux面板
#-------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
#-------------------------------------------------------------------
# Author: hwliang <hwl@bt.cn>
#-------------------------------------------------------------------

#------------------------------
# 任务编排调用脚本
#------------------------------
import sys,os
os.chdir('/www/server/panel')
sys.path.insert(0,'class/')
import PluginLoader
import public
args = public.dict_obj()

if len(sys.argv) < 2:
    print('ERROR: Task ID not found.')
    sys.exit()
args.trigger_id = int(sys.argv[1])
args.model_index = 'crontab'
res = PluginLoader.module_run('trigger','test_trigger',args)

if not res['status']:
    print(res['msg'])
    sys.exit()