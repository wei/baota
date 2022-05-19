#coding: utf-8
#-------------------------------------------------------------------
# 宝塔Linux面板
#-------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
#-------------------------------------------------------------------
# Author: zouhw <zhw@bt.cn>
#-------------------------------------------------------------------

#------------------------------
# Docker模型
#------------------------------

import os #line:14
import json #line:15
import public #line:16
import projectModel .bt_docker .dk_public as dp #line:17
class main :#line:19
    def get_config (O000OOOOO00O0O000 ,O00000OO00O0O0OO0 ):#line:21
        import projectModel .bt_docker .dk_public as dp #line:22
        OOOO00000O0O0OO0O =O000OOOOO00O0O000 .get_registry_mirrors (O00000OO00O0O0OO0 )#line:24
        if not OOOO00000O0O0OO0O ["status"]:#line:25
            return OOOO00000O0O0OO0O #line:26
        else :#line:27
            OOOO00000O0O0OO0O =OOOO00000O0O0OO0O ['msg']#line:28
        O0O0000OOO0O0O00O =O000OOOOO00O0O000 .get_service_status ()#line:29
        return public .returnMsg (True ,{"registry_mirrors":OOOO00000O0O0OO0O ,"service_status":O0O0000OOO0O0O00O ,"installed":O000OOOOO00O0O000 .check_docker_program (),"monitor_status":O000OOOOO00O0O000 .get_monitor_status (),"monitor_save_date":dp .docker_conf ()['SAVE']})#line:36
    def set_monitor_save_date (OO0O0O0OOO0OO0000 ,OOO00O00000OO0O00 ):#line:38
        ""#line:43
        import re #line:44
        O0O0000OO0O000O00 ="{}/data/docker.conf".format (public .get_panel_path ())#line:45
        O000O0OO00OO00000 =public .readFile (O0O0000OO0O000O00 )#line:46
        try :#line:47
            OOOOO00OOOOO0O000 =int (OOO00O00000OO0O00 .save_date )#line:48
        except :#line:49
            return public .returnMsg (False ,"监控保存时间需要是正整数！")#line:50
        if OOOOO00OOOOO0O000 >999 :#line:51
            return public .returnMsg (False ,"监控数据不能保留超过999天！")#line:52
        if not O000O0OO00OO00000 :#line:53
            O000O0OO00OO00000 ="SAVE={}".format (OOOOO00OOOOO0O000 )#line:54
            public .writeFile (O0O0000OO0O000O00 ,O000O0OO00OO00000 )#line:55
            return public .returnMsg (True ,"设置成功！")#line:56
        O000O0OO00OO00000 =re .sub ("SAVE\s*=\s*\d+","SAVE={}".format (OOOOO00OOOOO0O000 ),O000O0OO00OO00000 )#line:57
        public .writeFile (O0O0000OO0O000O00 ,O000O0OO00OO00000 )#line:58
        dp .write_log ("设置监控时间为【】天！".format (OOOOO00OOOOO0O000 ))#line:59
        return public .returnMsg (True ,"设置成功！")#line:60
    def get_service_status (O0OOO00O0O0O00O00 ):#line:62
        import projectModel .bt_docker .dk_public as dp #line:63
        OO00OO000OO00O0O0 ='/var/run/docker.pid'#line:64
        if os .path .exists (OO00OO000OO00O0O0 ):#line:65
            try :#line:66
                O0OOOOO00OOOOO0OO =dp .docker_client ()#line:67
                if O0OOOOO00OOOOO0OO :#line:68
                    return True #line:69
                else :#line:70
                    return False #line:71
            except :#line:72
                return False #line:73
        else :#line:74
            return False #line:75
    def docker_service (O0000O0OOOOOOOOOO ,OO00O000O000O0000 ):#line:78
        ""#line:83
        import public #line:84
        O0O0O00O0O0O00OOO ={'start':'启动','stop':'停止','restart':'重启'}#line:85
        if OO00O000O000O0000 .act not in O0O0O00O0O0O00OOO :#line:86
            return public .returnMsg (False ,'没有这个操作方法！')#line:87
        O0000O0O0OOO00OO0 ='systemctl {} docker'.format (OO00O000O000O0000 .act )#line:88
        if OO00O000O000O0000 .act =="stop":#line:89
            O0000O0O0OOO00OO0 +="&& systemctl {} docker.socket".format (OO00O000O000O0000 .act )#line:90
        public .ExecShell (O0000O0O0OOO00OO0 )#line:91
        dp .write_log ("设置Docker服务状态为【{}】成功".format (O0O0O00O0O0O00OOO [OO00O000O000O0000 .act ]))#line:92
        return public .returnMsg (True ,"设置状态为【{}】成功".format (O0O0O00O0O0O00OOO [OO00O000O000O0000 .act ]))#line:93
    def get_registry_mirrors (OOO0OOO00O0O0OOOO ,O00O0O0O0OO0OOOO0 ):#line:96
        try :#line:97
            if not os .path .exists ('/etc/docker/daemon.json'):#line:98
                return public .returnMsg (True ,[])#line:99
            OO000O0OO0OOOO000 =json .loads (public .readFile ('/etc/docker/daemon.json'))#line:100
            if "registry-mirrors"not in OO000O0OO0OOOO000 :#line:101
                return public .returnMsg (True ,[])#line:102
            return public .returnMsg (True ,OO000O0OO0OOOO000 ['registry-mirrors'])#line:103
        except :#line:104
            return public .returnMsg (False ,'获取失败！失败原因：{}'.format (public .get_error_info ()))#line:105
    def set_registry_mirrors (O000O0OO000O0OO00 ,OO0OOO00O0OO00OO0 ):#line:108
        ""#line:113
        try :#line:114
            OOO0000OOOOOOO000 =OO0OOO00O0OO00OO0 .registry_mirrors_address .strip ().split ('\n')#line:115
            OOOO0OOOO0O000O0O ={}#line:116
            if os .path .exists ('/etc/docker/daemon.json'):#line:117
                OOOO0OOOO0O000O0O =json .loads (public .readFile ('/etc/docker/daemon.json'))#line:118
            OOOO0OOOO0O000O0O ['registry-mirrors']=OOO0000OOOOOOO000 #line:119
            if not OOOO0OOOO0O000O0O ['registry-mirrors']:#line:120
                del (OOOO0OOOO0O000O0O ['registry-mirrors'])#line:121
            public .writeFile ('/etc/docker/daemon.json',json .dumps (OOOO0OOOO0O000O0O ,indent =2 ))#line:122
            dp .write_log ("设置Docker加速成功！")#line:123
            return public .returnMsg (True ,'设置成功')#line:124
        except :#line:125
            return public .returnMsg (False ,'设置失败！失败原因：{}'.format (public .get_error_info ()))#line:126
    def get_monitor_status (O0000OOOOO0OO00OO ):#line:128
        ""#line:131
        O0O00OO00O0OO000O =public .process_exists ("python",cmdline ="/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:133
        if O0O00OO00O0OO000O :#line:134
            return O0O00OO00O0OO000O #line:135
        O0O00OO00O0OO000O =public .process_exists ("python3",cmdline ="/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:136
        if O0O00OO00O0OO000O :#line:137
            return O0O00OO00O0OO000O #line:138
        return O0O00OO00O0OO000O #line:139
    def set_docker_monitor (O0O000O0O00O0OOOO ,OOOOO0O0OO000000O ):#line:141
        ""#line:146
        import time #line:147
        import projectModel .bt_docker .dk_public as dp #line:148
        O0OOO00OOOOOO000O ="/www/server/panel/pyenv/bin/python"#line:149
        if not os .path .exists (O0OOO00OOOOOO000O ):#line:150
            O0OOO00OOOOOO000O ="/www/server/panel/pyenv/bin/python3"#line:151
        OOOO00000OOO0O0O0 ="/www/server/panel/class/projectModel/bt_docker/dk_monitor.py"#line:152
        if OOOOO0O0OO000000O .act =="start":#line:153
            OO0OOOO00OOO0OO0O ="nohup {} {} &".format (O0OOO00OOOOOO000O ,OOOO00000OOO0O0O0 )#line:154
            public .ExecShell (OO0OOOO00OOO0OO0O )#line:155
            time .sleep (1 )#line:156
            if O0O000O0O00O0OOOO .get_monitor_status ():#line:157
                dp .write_log ("Docker监控启动成功！")#line:158
                return public .returnMsg (True ,"启动监控成功！")#line:159
            return public .returnMsg (False ,"启动监控失败！")#line:160
        else :#line:161
            O000OO00O0O000OO0 =dp .get_process_id ("python","/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:162
            if not O000OO00O0O000OO0 :#line:163
                O000OO00O0O000OO0 =dp .get_process_id ("python3","/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:164
            public .ExecShell ("kill -9 {}".format (O000OO00O0O000OO0 ))#line:165
            dp .write_log ("Docker监控停止成功！")#line:166
            return public .returnMsg (True ,"停止监控成功！")#line:167
    def check_docker_program (O00OO0O00O0O0OOO0 ):#line:169
        ""#line:173
        O0OO00O0OO0OO0O0O ="/usr/bin/docker"#line:174
        O00OO00000OO00OOO ="/usr/bin/docker-compose"#line:175
        if not os .path .exists (O0OO00O0OO0OO0O0O )or not os .path .exists (O00OO00000OO00OOO ):#line:176
            return False #line:177
        return True #line:178
    def install_docker_program (OO000OOO00000OOO0 ,OOOOO0OOO00O0O0O0 ):#line:180
        ""#line:185
        import time #line:186
        O00000OO000OOOO00 ="安装Docker服务"#line:187
        O00OOO000OOOOO0OO ="/bin/bash /www/server/panel/install/install_soft.sh 0 install docker_install"#line:190
        public .M ('tasks').add ('id,name,type,status,addtime,execstr',(None ,O00000OO000OOOO00 ,'execshell','0',time .strftime ('%Y-%m-%d %H:%M:%S'),O00OOO000OOOOO0OO ))#line:191
        public .httpPost (public .GetConfigValue ('home')+'/api/panel/plugin_total',{"pid":"1111111",'p_name':"Docker商用模块"},3 )#line:192
        return public .returnMsg (True ,"已将安装任务添加到队列!")#line:193
