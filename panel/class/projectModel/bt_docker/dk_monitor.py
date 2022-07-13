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
import sys #line:13
import threading #line:14
sys .path .insert (0 ,"/www/server/panel/class/")#line:15
sys .path .insert (1 ,"/www/server/panel/")#line:16
import projectModel .bt_docker .dk_public as dp #line:17
import projectModel .bt_docker .dk_container as dc #line:18
import projectModel .bt_docker .dk_status as ds #line:19
import projectModel .bt_docker .dk_image as di #line:20
import public #line:21
import time #line:23
class main :#line:24
    __O000O00000OO00OOO =None #line:26
    __OOO0O00OO0OOO000O =86400 #line:27
    def __init__ (O0O000OO00OOO0000 ,OO00O00OOOOOOOO0O ):#line:29
        if not OO00O00OOOOOOOO0O :#line:30
            O0O000OO00OOO0000 .__O000O00000OO00OOO =30 #line:31
        else :#line:32
            O0O000OO00OOO0000 .__O000O00000OO00OOO =OO00O00OOOOOOOO0O #line:33
    def docker_client (OO0OO0OO000OO0OO0 ,O00000OO0O0000000 ):#line:35
        return dp .docker_client (O00000OO0O0000000 )#line:36
    def get_all_host_stats (OO0O0OO00O0O0O00O ,OOO0OOOO0O0OOOO00 ):#line:38
        ""#line:43
        O00O00OOO000OOO0O =dp .sql ('hosts').select ()#line:44
        for O000O0OO00OO00O00 in O00O00OOO000OOO0O :#line:45
            OO000O00O0OOO0OOO =threading .Thread (target =OOO0OOOO0O0OOOO00 ,args =(O000O0OO00OO00O00 ,))#line:46
            OO000O00O0OOO0OOO .setDaemon (True )#line:47
            OO000O00O0OOO0OOO .start ()#line:48
    def container_status_for_all_hosts (O0O0OOO00OOOO0000 ,OO0O00O0OOOOOO0O0 ):#line:51
        ""#line:56
        OO000OO0OOOO00O0O =public .to_dict_obj ({})#line:58
        OO000OO0OOOO00O0O .url =OO0O00O0OOOOOO0O0 ['url']#line:59
        O0000O0000000OO00 =dc .main ().get_list (OO000OO0OOOO00O0O )['msg']#line:60
        for OOO00O0OOO0OO0000 in O0000O0000000OO00 ['container_list']:#line:61
            OO000OO0OOOO00O0O .id =OOO00O0OOO0OO0000 ['id']#line:62
            OO000OO0OOOO00O0O .write =1 #line:63
            OO000OO0OOOO00O0O .save_date =O0O0OOO00OOOO0000 .__O000O00000OO00OOO #line:64
            ds .main ().stats (OO000OO0OOOO00O0O )#line:65
    def container_count (O0OO00O0OO0O0OO00 ):#line:69
        O0OO00OO0000OOO00 =dp .sql ('hosts').select ()#line:71
        O00O00OO0O0000OOO =0 #line:72
        for OOOOOO0OOOO000O0O in O0OO00OO0000OOO00 :#line:73
            O0OO0O0O0O0OO0O00 =public .to_dict_obj ({})#line:74
            O0OO0O0O0O0OO0O00 .url =OOOOOO0OOOO000O0O ['url']#line:75
            O0O0O00O0OOOOOO0O =dc .main ().get_list (O0OO0O0O0O0OO0O00 )['msg']#line:76
            O00O00OO0O0000OOO +=len (O0O0O00O0OOOOOO0O )#line:77
        O00OO0OOO00O00OO0 ={"time":int (time .time ()),"container_count":O00O00OO0O0000OOO }#line:81
        OOO0000O000OOO0OO =time .time ()-(O0OO00O0OO0O0OO00 .__O000O00000OO00OOO *O0OO00O0OO0O0OO00 .__OOO0O00OO0OOO000O )#line:82
        dp .sql ("container_count").where ("time<?",(OOO0000O000OOO0OO ,)).delete ()#line:83
        dp .sql ("container_count").insert (O00OO0OOO00O00OO0 )#line:84
    def image_for_all_host (O00O0000O000OOO0O ):#line:87
        OO000O0O00OO0OOOO =dp .sql ('hosts').select ()#line:89
        OO00O0OO0OOOOOOOO =0 #line:90
        O00O0000O00O0O00O =0 #line:91
        for O0OO0O0O00OOOO0O0 in OO000O0O00OO0OOOO :#line:92
            OO00OOO0OOOO0O0O0 =public .to_dict_obj ({})#line:93
            OO00OOO0OOOO0O0O0 .url =O0OO0O0O00OOOO0O0 ['url']#line:94
            OOO00OOOOOOOOO0O0 =di .main ().image_for_host (OO00OOO0OOOO0O0O0 )#line:95
            if not OOO00OOOOOOOOO0O0 ['status']:#line:96
                continue #line:97
            print (OOO00OOOOOOOOO0O0 )#line:98
            OO00O0OO0OOOOOOOO +=OOO00OOOOOOOOO0O0 ['msg']['num']#line:99
            O00O0000O00O0O00O +=OOO00OOOOOOOOO0O0 ['msg']['size']#line:100
        O0O0000OO00O0O0OO ={"time":int (time .time ()),"num":OO00O0OO0OOOOOOOO ,"size":int (O00O0000O00O0O00O )}#line:105
        OOO0000000O00O0O0 =time .time ()-(O00O0000O000OOO0O .__O000O00000OO00OOO *O00O0000O000OOO0O .__OOO0O00OO0OOO000O )#line:106
        dp .sql ("image_infos").where ("time<?",(OOO0000000O00O0O0 ,)).delete ()#line:107
        dp .sql ("image_infos").insert (O0O0000OO00O0O0OO )#line:108
def monitor ():#line:111
    while True :#line:114
        O000OOOO0000O0OOO =dp .docker_conf ()['SAVE']#line:115
        OOOOOO0000O0OO00O =main (O000OOOO0000O0OOO )#line:116
        OOOOOO0000O0OO00O .get_all_host_stats (OOOOOO0000O0OO00O .container_status_for_all_hosts )#line:117
        OOO0O0OOO00O0O000 =threading .Thread (target =OOOOOO0000O0OO00O .container_count )#line:119
        OOO0O0OOO00O0O000 .setDaemon (True )#line:120
        OOO0O0OOO00O0O000 .start ()#line:121
        OOO0O0OOO00O0O000 =threading .Thread (target =OOOOOO0000O0OO00O .image_for_all_host )#line:123
        OOO0O0OOO00O0O000 .setDaemon (True )#line:124
        OOO0O0OOO00O0O000 .start ()#line:125
        time .sleep (60 )#line:126
if __name__ =="__main__":#line:131
    monitor ()