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
import public #line:13
import projectModel .bt_docker .dk_public as dp #line:14
import docker .errors #line:15
class main :#line:17
    __OO0000O00O0000OOO =None #line:19
    def docker_client (OO000O00O00000O0O ,O0OO0O000000OO000 ):#line:21
        import projectModel .bt_docker .dk_public as dp #line:22
        return dp .docker_client (O0OO0O000000OO000 )#line:23
    def get_volume_container_name (OO0OO0O0O00O00OOO ,OOO0O0O0O00OOOO00 ):#line:26
        OOOOO0OOOOOO00O00 =OO0OO0O0O00O00OOO .docker_client (OO0OO0O0O00O00OOO .__OO0000O00O0000OOO ).containers #line:27
        O000O00OOOOO0OOOO =OOOOO0OOOOOO00O00 .list (all =True )#line:28
        OO00OO0OOO0O00O0O =[OOOOO000OOOO0OO00 .attrs for OOOOO000OOOO0OO00 in O000O00OOOOO0OOOO ]#line:30
        for O0OOOO00OO0O00OO0 in OO00OO0OOO0O00O0O :#line:31
            if not O0OOOO00OO0O00OO0 ['Mounts']:#line:32
                continue #line:33
            for O00O00OOOO00000O0 in O0OOOO00OO0O00OO0 ['Mounts']:#line:34
                if "Name"not in O00O00OOOO00000O0 :#line:35
                    continue #line:36
                if OOO0O0O0O00OOOO00 ['Name']==O00O00OOOO00000O0 ['Name']:#line:37
                    OOO0O0O0O00OOOO00 ['container']=O0OOOO00OO0O00OO0 ['Name'].replace ("/","")#line:38
        if 'container'not in OOO0O0O0O00OOOO00 :#line:39
            OOO0O0O0O00OOOO00 ['container']=''#line:40
        return OOO0O0O0O00OOOO00 #line:41
    def get_volume_list (O0OO00000O0O00OO0 ,OO000O0O0OO00O000 ):#line:43
        ""#line:47
        import projectModel .bt_docker .dk_setup as ds #line:48
        O0OO00000O0O00OO0 .__OO0000O00O0000OOO =OO000O0O0OO00O000 .url #line:49
        OO0OOO0O00O00OOO0 =O0OO00000O0O00OO0 .docker_client (OO000O0O0OO00O000 .url )#line:50
        O000O00OO0OO0000O =ds .main ()#line:51
        O0O0000OOO0O0O0OO =O000O00OO0OO0000O .check_docker_program ()#line:52
        OO0OOOOOO0000OO00 =O000O00OO0OO0000O .get_service_status ()#line:53
        if not OO0OOO0O00O00OOO0 :#line:54
            O000O0OOO00OO000O ={"volume":[],"installed":O0O0000OOO0O0O0OO ,"service_status":OO0OOOOOO0000OO00 }#line:59
            return public .returnMsg (True ,O000O0OOO00OO000O )#line:60
        OO0O00O0OOOO00O0O =OO0OOO0O00O00OOO0 .volumes #line:61
        O000O0OOO00OO000O ={"volume":O0OO00000O0O00OO0 .get_volume_attr (OO0O00O0OOOO00O0O ),"installed":O0O0000OOO0O0O0OO ,"service_status":OO0OOOOOO0000OO00 }#line:67
        return public .returnMsg (True ,O000O0OOO00OO000O )#line:68
    def get_volume_attr (O00000O000O0000O0 ,O00OOOO000OO0O00O ):#line:70
        OO0OOO0OO0000O000 =O00OOOO000OO0O00O .list ()#line:71
        OO0000O0000O00OOO =list ()#line:72
        for OOOO0O000O0O0OO0O in OO0OOO0OO0000O000 :#line:73
            OOOO0O000O0O0OO0O =O00000O000O0000O0 .get_volume_container_name (OOOO0O000O0O0OO0O .attrs )#line:74
            OO0000O0000O00OOO .append (OOOO0O000O0O0OO0O )#line:75
        return OO0000O0000O00OOO #line:76
    def add (O000O0O00O0O0O0O0 ,O000OO0000OOOOO00 ):#line:78
        ""#line:86
        O000O0O00O0O0O0O0 .docker_client (O000OO0000OOOOO00 .url ).volumes .create (name =O000OO0000OOOOO00 .name ,driver =O000OO0000OOOOO00 .driver ,driver_opts =O000OO0000OOOOO00 .driver_opts if O000OO0000OOOOO00 .driver_opts else None ,labels =dp .set_kv (O000OO0000OOOOO00 .labels ))#line:92
        dp .write_log ("添加存储卷【[]】成功！".format (O000OO0000OOOOO00 .name ))#line:93
        return public .returnMsg (True ,"添加成功！")#line:94
    def remove (O0O00OO000OO0OOO0 ,O000OOO00OOO00OO0 ):#line:96
        ""#line:102
        try :#line:103
            OO0O0O0O0O00O0000 =O0O00OO000OO0OOO0 .docker_client (O000OOO00OOO00OO0 .url ).volumes .get (O000OOO00OOO00OO0 .name )#line:104
            OO0O0O0O0O00O0000 .remove ()#line:105
            dp .write_log ("删除存储卷【[]】成功！".format (O000OOO00OOO00OO0 .name ))#line:106
            return public .returnMsg (True ,"删除成功")#line:107
        except docker .errors .APIError as O00OO00OO0OOOOOOO :#line:108
            if "volume is in use"in str (O00OO00OO0OOOOOOO ):#line:109
                return public .returnMsg (False ,"存储卷正在使用，无法删除！")#line:110
            return public .returnMsg (False ,"删除失败！{}".format (O00OO00OO0OOOOOOO ))#line:111
