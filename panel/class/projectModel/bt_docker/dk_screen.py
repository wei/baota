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
import projectModel .bt_docker .dk_public as dp #line:13
import time #line:14
class main :#line:16
    def get_status (O0OOO000OOOOOOOO0 ,OOO0O0OO0O00000OO ):#line:18
        ""#line:24
        O0OO00000OOO00O0O =dict ()#line:25
        O0OO00000OOO00O0O ['container_count']=O0OOO000OOOOOOOO0 .__OO0OOO0O0OOOOO000 (OOO0O0OO0O00000OO )#line:27
        O0OO00000OOO00O0O ['image_info']=dp .sql ("image_infos").where ("time>=? and time<=?",(OOO0O0OO0O00000OO .start_time ,OOO0O0OO0O00000OO .stop_time )).select ()#line:29
        O0OO00000OOO00O0O ['host']=len (dp .sql ('hosts').select ())#line:31
        O0OO00000OOO00O0O ['container_top']={"cpu":O0OOO000OOOOOOOO0 .__OOOOO00O0OOO0OO0O (),"mem":O0OOO000OOOOOOOO0 .__O0O0OO000OO0OO00O ()}#line:33
        return O0OO00000OOO00O0O #line:34
    def __OO0OOO0O0OOOOO000 (O0O00O00OO00O0O00 ,OO00OOO00OO00O00O ):#line:36
        OO00OOO0OO000O000 =dp .sql ('container_count').where ("time>=? and time<=?",(OO00OOO00OO00O00O .start_time ,OO00OOO00OO00O00O .stop_time )).select ()#line:37
        if not OO00OOO0OO000O000 :#line:38
            return 0 #line:39
        return OO00OOO0OO000O000 [-1 ]#line:40
    def __O0O0OO000OO0OO00O (OO00O0O00000OOO0O ):#line:42
        O0OO00OO00000OO00 =int (time .time ())#line:43
        O00O0O0000OOO00OO =O0OO00OO00000OO00 -3600 #line:44
        O000OOOO0000000OO =dp .sql ("mem_stats").where ("time>=? and time<=?",(O00O0O0000OOO00OO ,O0OO00OO00000OO00 )).select ()#line:45
        O00O0OO00O0OOO000 =list ()#line:46
        OOO000OO0O0O0OOO0 =dict ()#line:47
        for O0O0O0O00OOOO00O0 in O000OOOO0000000OO :#line:49
            O00O0OO00O0OOO000 .append (O0O0O0O00OOOO00O0 ['container_id'])#line:50
        O00O0OO00O0OOO000 =set (O00O0OO00O0OOO000 )#line:52
        for O0O00OO0000OOO0O0 in O00O0OO00O0OOO000 :#line:53
            O0O000000000O0O0O =0 #line:54
            O00OOOO0OOO000O0O =0 #line:55
            for O0O0O0O00OOOO00O0 in O000OOOO0000000OO :#line:56
                if O0O0O0O00OOOO00O0 ['container_id']==O0O00OO0000OOO0O0 :#line:57
                    O0O000000000O0O0O +=1 #line:58
                    O00OOOO0OOO000O0O +=float (O0O0O0O00OOOO00O0 ['usage'])#line:59
            if O0O000000000O0O0O !=0 :#line:60
                OOO000OO0O0O0OOO0 [O0O00OO0000OOO0O0 ]=O00OOOO0OOO000O0O /O0O000000000O0O0O #line:61
        return OOO000OO0O0O0OOO0 #line:62
    def __OOOOO00O0OOO0OO0O (OO0O0O0000O00OO0O ):#line:64
        O0OO0O0OO00O00000 =int (time .time ())#line:65
        O0OO00O0O00O0O0O0 =O0OO0O0OO00O00000 -3600 #line:66
        OOO0O0O00OOO0O00O =dp .sql ("cpu_stats").where ("time>=? and time<=?",(O0OO00O0O00O0O0O0 ,O0OO0O0OO00O00000 )).select ()#line:67
        O0OO0OO0O00OO0O00 =list ()#line:68
        O0OOOO00O00O0O00O =dict ()#line:69
        for OO0O0000OO0O00000 in OOO0O0O00OOO0O00O :#line:71
            O0OO0OO0O00OO0O00 .append (OO0O0000OO0O00000 ['container_id'])#line:72
        O0OO0OO0O00OO0O00 =set (O0OO0OO0O00OO0O00 )#line:74
        for O0O0OO00OOOOOO0OO in O0OO0OO0O00OO0O00 :#line:75
            OOOOO00O000OOO0O0 =0 #line:76
            OOO00O00O0OO00OOO =0 #line:77
            for OO0O0000OO0O00000 in OOO0O0O00OOO0O00O :#line:78
                if OO0O0000OO0O00000 ['container_id']==O0O0OO00OOOOOO0OO :#line:79
                    OOOOO00O000OOO0O0 +=1 #line:80
                    OOO00O00O0OO00OOO +=float (0 if OO0O0000OO0O00000 ['cpu_usage']=='0.0'else OO0O0000OO0O00000 ['cpu_usage'])#line:81
            if OOOOO00O000OOO0O0 !=0 :#line:82
                O0OOOO00O00O0O00O [O0O0OO00OOOOOO0OO ]=OOO00O00O0OO00OOO /OOOOO00O000OOO0O0 #line:83
        return O0OOOO00O00O0O00O