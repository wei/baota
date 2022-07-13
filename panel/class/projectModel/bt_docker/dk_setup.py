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
    def get_config (OOO000OOOO00OOOO0 ,OOO0O0O000O0OOO0O ):#line:21
        import projectModel .bt_docker .dk_public as dp #line:22
        O0O0O00000OO0O0O0 =OOO000OOOO00OOOO0 .get_registry_mirrors (OOO0O0O000O0OOO0O )#line:24
        if not O0O0O00000OO0O0O0 ["status"]:#line:25
            return O0O0O00000OO0O0O0 #line:26
        else :#line:27
            O0O0O00000OO0O0O0 =O0O0O00000OO0O0O0 ['msg']#line:28
        O0O000O0O0000O0OO =OOO000OOOO00OOOO0 .get_service_status ()#line:29
        return public .returnMsg (True ,{"registry_mirrors":O0O0O00000OO0O0O0 ,"service_status":O0O000O0O0000O0OO ,"installed":OOO000OOOO00OOOO0 .check_docker_program (),"monitor_status":OOO000OOOO00OOOO0 .get_monitor_status (),"monitor_save_date":dp .docker_conf ()['SAVE']})#line:36
    def set_monitor_save_date (OO0OOO000O00OO0OO ,O0O0OOOO00O0O00O0 ):#line:38
        ""#line:43
        import re #line:44
        O00OOOOOO00000O00 ="{}/data/docker.conf".format (public .get_panel_path ())#line:45
        OO0OO00O000OOO0O0 =public .readFile (O00OOOOOO00000O00 )#line:46
        try :#line:47
            O0OOO0OO0OO0OOOO0 =int (O0O0OOOO00O0O00O0 .save_date )#line:48
        except :#line:49
            return public .returnMsg (False ,"监控保存时间需要是正整数！")#line:50
        if O0OOO0OO0OO0OOOO0 >999 :#line:51
            return public .returnMsg (False ,"监控数据不能保留超过999天！")#line:52
        if not OO0OO00O000OOO0O0 :#line:53
            OO0OO00O000OOO0O0 ="SAVE={}".format (O0OOO0OO0OO0OOOO0 )#line:54
            public .writeFile (O00OOOOOO00000O00 ,OO0OO00O000OOO0O0 )#line:55
            return public .returnMsg (True ,"设置成功！")#line:56
        OO0OO00O000OOO0O0 =re .sub ("SAVE\s*=\s*\d+","SAVE={}".format (O0OOO0OO0OO0OOOO0 ),OO0OO00O000OOO0O0 )#line:57
        public .writeFile (O00OOOOOO00000O00 ,OO0OO00O000OOO0O0 )#line:58
        dp .write_log ("设置监控时间为【】天！".format (O0OOO0OO0OO0OOOO0 ))#line:59
        return public .returnMsg (True ,"设置成功！")#line:60
    def get_service_status (O0OO00000OOOOOO0O ):#line:62
        import projectModel .bt_docker .dk_public as dp #line:63
        OO0OOO000000OO0OO ='/var/run/docker.pid'#line:64
        if os .path .exists (OO0OOO000000OO0OO ):#line:65
            try :#line:66
                O0O0O0O0O00000O00 =dp .docker_client ()#line:67
                if O0O0O0O0O00000O00 :#line:68
                    return True #line:69
                else :#line:70
                    return False #line:71
            except :#line:72
                return False #line:73
        else :#line:74
            return False #line:75
    def docker_service (O0OO0O00O0O0000OO ,O00O0OOO0OO0OOOO0 ):#line:78
        ""#line:83
        import public #line:84
        O0000O0OOO0000O00 ={'start':'启动','stop':'停止','restart':'重启'}#line:85
        if O00O0OOO0OO0OOOO0 .act not in O0000O0OOO0000O00 :#line:86
            return public .returnMsg (False ,'没有这个操作方法！')#line:87
        O0O000O00OO0OOO0O ='systemctl {} docker'.format (O00O0OOO0OO0OOOO0 .act )#line:88
        if O00O0OOO0OO0OOOO0 .act =="stop":#line:89
            O0O000O00OO0OOO0O +="&& systemctl {} docker.socket".format (O00O0OOO0OO0OOOO0 .act )#line:90
        public .ExecShell (O0O000O00OO0OOO0O )#line:91
        dp .write_log ("设置Docker服务状态为【{}】成功".format (O0000O0OOO0000O00 [O00O0OOO0OO0OOOO0 .act ]))#line:92
        return public .returnMsg (True ,"设置状态为【{}】成功".format (O0000O0OOO0000O00 [O00O0OOO0OO0OOOO0 .act ]))#line:93
    def get_registry_mirrors (OOOO0OO000OO0OO00 ,O0O0O0OOOO0O000OO ):#line:96
        try :#line:97
            if not os .path .exists ('/etc/docker/daemon.json'):#line:98
                return public .returnMsg (True ,[])#line:99
            OOO0OO00O0000OOOO =json .loads (public .readFile ('/etc/docker/daemon.json'))#line:100
            if "registry-mirrors"not in OOO0OO00O0000OOOO :#line:101
                return public .returnMsg (True ,[])#line:102
            return public .returnMsg (True ,OOO0OO00O0000OOOO ['registry-mirrors'])#line:103
        except :#line:104
            return public .returnMsg (False ,'获取失败！失败原因：{}'.format (public .get_error_info ()))#line:105
    def set_registry_mirrors (OO00OO00000O00OO0 ,O0OO000OOO0000O00 ):#line:108
        ""#line:113
        import re #line:114
        try :#line:115
            O00O0OOOO0O0OO00O ={}#line:116
            if os .path .exists ('/etc/docker/daemon.json'):#line:117
                O00O0OOOO0O0OO00O =json .loads (public .readFile ('/etc/docker/daemon.json'))#line:118
            if not O0OO000OOO0000O00 .registry_mirrors_address .strip ():#line:119
                if 'registry-mirrors'not in O00O0OOOO0O0OO00O :#line:121
                    return public .returnMsg (True ,'设置成功')#line:122
                del (O00O0OOOO0O0OO00O ['registry-mirrors'])#line:123
            else :#line:124
                O0O0000O0OO0OOOOO =O0OO000OOO0000O00 .registry_mirrors_address .strip ().split ('\n')#line:125
                for OOO00O0O0O000OO00 in O0O0000O0OO0OOOOO :#line:126
                    if not re .search ('https?://',OOO00O0O0O000OO00 ):#line:127
                        return public .returnMsg (False ,'加速地址【{}】格式错误<br>参考：https://mirror.ccs.tencentyun.com'.format (OOO00O0O0O000OO00 ))#line:128
                O00O0OOOO0O0OO00O ['registry-mirrors']=O0O0000O0OO0OOOOO #line:130
            public .writeFile ('/etc/docker/daemon.json',json .dumps (O00O0OOOO0O0OO00O ,indent =2 ))#line:133
            dp .write_log ("设置Docker加速成功！")#line:134
            return public .returnMsg (True ,'设置成功')#line:135
        except :#line:136
            return public .returnMsg (False ,'设置失败！失败原因：{}'.format (public .get_error_info ()))#line:137
    def get_monitor_status (O0OO0O000OO00OOO0 ):#line:139
        ""#line:142
        O0OOOO0O00O0OOOOO =public .process_exists ("python",cmdline ="/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:144
        if O0OOOO0O00O0OOOOO :#line:145
            return O0OOOO0O00O0OOOOO #line:146
        O0OOOO0O00O0OOOOO =public .process_exists ("python3",cmdline ="/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:147
        if O0OOOO0O00O0OOOOO :#line:148
            return O0OOOO0O00O0OOOOO #line:149
        return O0OOOO0O00O0OOOOO #line:150
    def set_docker_monitor (O00O0OO0O0OOOOOO0 ,OO00O00OOOOO0OO0O ):#line:152
        ""#line:157
        import time #line:158
        import projectModel .bt_docker .dk_public as dp #line:159
        O0O0OOO00OOOO000O ="/www/server/panel/pyenv/bin/python"#line:160
        if not os .path .exists (O0O0OOO00OOOO000O ):#line:161
            O0O0OOO00OOOO000O ="/www/server/panel/pyenv/bin/python3"#line:162
        OOO0OOO0OOOOO0O00 ="/www/server/panel/class/projectModel/bt_docker/dk_monitor.py"#line:163
        if OO00O00OOOOO0OO0O .act =="start":#line:164
            O0OO00OOO0O0OOOOO ="nohup {} {} &".format (O0O0OOO00OOOO000O ,OOO0OOO0OOOOO0O00 )#line:165
            public .ExecShell (O0OO00OOO0O0OOOOO )#line:166
            time .sleep (1 )#line:167
            if O00O0OO0O0OOOOOO0 .get_monitor_status ():#line:168
                dp .write_log ("Docker监控启动成功！")#line:169
                return public .returnMsg (True ,"启动监控成功！")#line:170
            return public .returnMsg (False ,"启动监控失败！")#line:171
        else :#line:172
            O000OO0000OO000OO =dp .get_process_id ("python","/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:173
            if not O000OO0000OO000OO :#line:174
                O000OO0000OO000OO =dp .get_process_id ("python3","/www/server/panel/class/projectModel/bt_docker/dk_monitor.py")#line:175
            public .ExecShell ("kill -9 {}".format (O000OO0000OO000OO ))#line:176
            dp .write_log ("Docker监控停止成功！")#line:177
            return public .returnMsg (True ,"停止监控成功！")#line:178
    def check_docker_program (OOO0O00OOO00O00OO ):#line:180
        ""#line:184
        OOO0O0000000OOOO0 ="/usr/bin/docker"#line:185
        OOO00OOOO0O0OOOOO ="/usr/bin/docker-compose"#line:186
        if not os .path .exists (OOO0O0000000OOOO0 )or not os .path .exists (OOO00OOOO0O0OOOOO ):#line:187
            return False #line:188
        return True #line:189
    def install_docker_program (O0000O000000O0OOO ,O000O0OOO00000O0O ):#line:191
        ""#line:196
        import time #line:197
        OOOO00OOO00O00O00 ="安装Docker服务"#line:198
        O0O0O0O00OO0OO000 ="/bin/bash /www/server/panel/install/install_soft.sh 0 install docker_install"#line:201
        public .M ('tasks').add ('id,name,type,status,addtime,execstr',(None ,OOOO00OOO00O00O00 ,'execshell','0',time .strftime ('%Y-%m-%d %H:%M:%S'),O0O0O0O00OO0OO000 ))#line:202
        public .httpPost (public .GetConfigValue ('home')+'/api/panel/plugin_total',{"pid":"1111111",'p_name':"Docker商用模块"},3 )#line:203
        return public .returnMsg (True ,"已将安装任务添加到队列!")#line:204
