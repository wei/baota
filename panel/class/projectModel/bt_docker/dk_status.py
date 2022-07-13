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
import time #line:14
import projectModel .bt_docker .dk_public as dp #line:15
class main :#line:18
    __O0OOOOOOOO0O0OO00 =dict ()#line:20
    __O0OO0OOOO0000OOO0 =None #line:21
    def docker_client (O00000000O00OOO0O ,O0OO0OOO0O0O000OO ):#line:23
        if not O00000000O00OOO0O .__O0OO0OOOO0000OOO0 :#line:24
            O00000000O00OOO0O .__O0OO0OOOO0000OOO0 =dp .docker_client (O0OO0OOO0O0O000OO )#line:25
        return O00000000O00OOO0O .__O0OO0OOOO0000OOO0 #line:26
    def io_stats (O000OO00O00OOO0OO ,OOO0O0OO0OO0OOOOO ,write =None ):#line:28
        O00OOO0OO0OOOO0O0 =OOO0O0OO0OO0OOOOO ['blkio_stats']['io_service_bytes_recursive']#line:29
        try :#line:31
            OOO0O000OOO0OO0OO =O00OOO0OO0OOOO0O0 [0 ]['value']+O00OOO0OO0OOOO0O0 [2 ]['value']#line:32
            O000OO00O00OOO0OO .__O0OOOOOOOO0O0OO00 ['read_total']=OOO0O000OOO0OO0OO #line:34
        except :#line:36
            O000OO00O00OOO0OO .__O0OOOOOOOO0O0OO00 ['read_total']=0 #line:37
        try :#line:39
            OOO0O000OOO0OO0OO =O00OOO0OO0OOOO0O0 [1 ]['value']+O00OOO0OO0OOOO0O0 [3 ]['value']#line:40
            O000OO00O00OOO0OO .__O0OOOOOOOO0O0OO00 ['write_total']=OOO0O000OOO0OO0OO #line:42
        except :#line:44
            O000OO00O00OOO0OO .__O0OOOOOOOO0O0OO00 ['write_total']=0 #line:45
        if write :#line:47
            O000OO00O00OOO0OO .__O0OOOOOOOO0O0OO00 ['container_id']=OOO0O0OO0OO0OOOOO ['id']#line:48
            O000OO00O00OOO0OO .write_io (O000OO00O00OOO0OO .__O0OOOOOOOO0O0OO00 )#line:49
    def net_stats (OO00O0OO0OO00O00O ,O00O0OOO00O0O00OO ,OOOO00OOO00OO0OOO ,write =None ):#line:52
        try :#line:53
            OO0000OOO00O0000O =O00O0OOO00O0O00OO ['networks']['eth0']#line:54
            O0O0OO0O0O0000OOO =OOOO00OOO00OO0OOO ['networks']['eth0']#line:55
        except :#line:56
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['rx_total']=0 #line:57
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['rx']=0 #line:58
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['tx_total']=0 #line:59
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['tx']=0 #line:60
            if write :#line:61
                OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['container_id']=O00O0OOO00O0O00OO ['id']#line:62
                OO00O0OO0OO00O00O .write_net (OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 )#line:63
            return #line:64
        O0O0OO0O000000OO0 =O00O0OOO00O0O00OO ["time"]#line:65
        O00O0O0OOO000OOOO =OOOO00OOO00OO0OOO ["time"]#line:66
        try :#line:67
            OOO0O0O00OO0OO000 =OO0000OOO00O0000O ["rx_bytes"]#line:68
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['rx_total']=OOO0O0O00OO0OO000 #line:69
            OOO0O00O00OOO0OO0 =O0O0OO0O0O0000OOO ["rx_bytes"]#line:70
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['rx']=int ((OOO0O0O00OO0OO000 -OOO0O00O00OOO0OO0 )/(O0O0OO0O000000OO0 -O00O0O0OOO000OOOO ))#line:71
        except :#line:72
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['rx_total']=0 #line:73
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['rx']=0 #line:74
        try :#line:75
            OOO0O0O00OO0OO000 =OO0000OOO00O0000O ["tx_bytes"]#line:76
            OOO0O00O00OOO0OO0 =O0O0OO0O0O0000OOO ["tx_bytes"]#line:77
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['tx_total']=OOO0O0O00OO0OO000 #line:78
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['tx']=int ((OOO0O0O00OO0OO000 -OOO0O00O00OOO0OO0 )/(O0O0OO0O000000OO0 -O00O0O0OOO000OOOO ))#line:79
        except :#line:80
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['tx_total']=0 #line:81
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['tx']=0 #line:82
        if write :#line:83
            OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 ['container_id']=O00O0OOO00O0O00OO ['id']#line:84
            OO00O0OO0OO00O00O .write_net (OO00O0OO0OO00O00O .__O0OOOOOOOO0O0OO00 )#line:85
    def mem_stats (OOO0OO00O00OO0O0O ,O000O0OOOOOOOO000 ,write =None ):#line:88
        OO0000O00O00000OO =O000O0OOOOOOOO000 ['memory_stats']#line:89
        try :#line:90
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['limit']=OO0000O00O00000OO ['limit']#line:91
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['usage_total']=OO0000O00O00000OO ['usage']#line:92
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['usage']=OO0000O00O00000OO ['usage']-OO0000O00O00000OO ['stats']['cache']#line:93
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['cache']=OO0000O00O00000OO ['stats']['cache']#line:94
        except :#line:96
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['limit']=0 #line:98
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['usage']=0 #line:99
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['cache']=0 #line:100
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['usage_total']=0 #line:101
        if write :#line:103
            OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 ['container_id']=O000O0OOOOOOOO000 ['id']#line:104
            OOO0OO00O00OO0O0O .write_mem (OOO0OO00O00OO0O0O .__O0OOOOOOOO0O0OO00 )#line:105
    def cpu_stats (O0000O0O000O000O0 ,O000000O000O00000 ,write =None ):#line:108
        try :#line:114
            O00O0O0O000000O00 =O000000O000O00000 ['cpu_stats']['cpu_usage']['total_usage']-O000000O000O00000 ['precpu_stats']['cpu_usage']['total_usage']#line:115
        except :#line:116
            O00O0O0O000000O00 =0 #line:117
        try :#line:118
            O00O0O000OO000OO0 =O000000O000O00000 ['cpu_stats']['system_cpu_usage']-O000000O000O00000 ['precpu_stats']['system_cpu_usage']#line:119
        except :#line:120
            O00O0O000OO000OO0 =0 #line:121
        try :#line:122
            O0000O0O000O000O0 .__O0OOOOOOOO0O0OO00 ['online_cpus']=O000000O000O00000 ['cpu_stats']['online_cpus']#line:123
        except :#line:124
            O0000O0O000O000O0 .__O0OOOOOOOO0O0OO00 ['online_cpus']=0 #line:125
        if O00O0O0O000000O00 >0 and O00O0O000OO000OO0 >0 :#line:126
            O0000O0O000O000O0 .__O0OOOOOOOO0O0OO00 ['cpu_usage']=round ((O00O0O0O000000O00 /O00O0O000OO000OO0 )*100 *O0000O0O000O000O0 .__O0OOOOOOOO0O0OO00 ['online_cpus'],2 )#line:127
        else :#line:128
            O0000O0O000O000O0 .__O0OOOOOOOO0O0OO00 ['cpu_usage']=0.0 #line:129
        if write :#line:130
            O0000O0O000O000O0 .__O0OOOOOOOO0O0OO00 ['container_id']=O000000O000O00000 ['id']#line:131
            O0000O0O000O000O0 .write_cpu (O0000O0O000O000O0 .__O0OOOOOOOO0O0OO00 )#line:132
    def stats (OO0000000O00OO000 ,O00OOO0OO00O0OOOO ):#line:135
        ""#line:142
        OO0000O0O000000O0 =OO0000000O00OO000 .docker_client (O00OOO0OO00O0OOOO .url ).containers .get (O00OOO0OO00O0OOOO .id )#line:143
        OOOO00000000O000O =OO0000O0O000000O0 .stats (decode =None ,stream =False )#line:144
        OOOO00000000O000O ['time']=time .time ()#line:145
        OO000OO0O00O00000 =public .cache_get ('stats')#line:146
        if not OO000OO0O00O00000 :#line:147
            OO000OO0O00O00000 =OOOO00000000O000O #line:148
            public .cache_set ('stats',OOOO00000000O000O )#line:149
        O0O0O0O0O000000OO =None #line:150
        if hasattr (O00OOO0OO00O0OOOO ,"write"):#line:151
            O0O0O0O0O000000OO =O00OOO0OO00O0OOOO .write #line:152
            OO0000000O00OO000 .__O0OOOOOOOO0O0OO00 ['expired']=time .time ()-(O00OOO0OO00O0OOOO .save_date *86400 )#line:153
        OOOO00000000O000O ['id']=O00OOO0OO00O0OOOO .id #line:154
        OO0000000O00OO000 .io_stats (OOOO00000000O000O ,O0O0O0O0O000000OO )#line:155
        OO0000000O00OO000 .net_stats (OOOO00000000O000O ,OO000OO0O00O00000 ,O0O0O0O0O000000OO )#line:156
        OO0000000O00OO000 .cpu_stats (OOOO00000000O000O ,O0O0O0O0O000000OO )#line:157
        OO0000000O00OO000 .mem_stats (OOOO00000000O000O ,O0O0O0O0O000000OO )#line:158
        public .cache_set ('stats',OOOO00000000O000O )#line:159
        OO0000000O00OO000 .__O0OOOOOOOO0O0OO00 ['detail']=OOOO00000000O000O #line:160
        return public .returnMsg (True ,OO0000000O00OO000 .__O0OOOOOOOO0O0OO00 )#line:161
    def write_cpu (OOO0OO0000O0000O0 ,O0O0OO00O0OOO0O0O ):#line:163
        OOO000O00OO0OO000 ={"time":time .time (),"cpu_usage":O0O0OO00O0OOO0O0O ['cpu_usage'],"online_cpus":O0O0OO00O0OOO0O0O ['online_cpus'],"container_id":O0O0OO00O0OOO0O0O ['container_id']}#line:169
        dp .sql ("cpu_stats").where ("time<?",(OOO0OO0000O0000O0 .__O0OOOOOOOO0O0OO00 ['expired'],)).delete ()#line:170
        dp .sql ("cpu_stats").insert (OOO000O00OO0OO000 )#line:171
    def write_io (O00OO0000O0O0OOOO ,OOOO00OO0O0OO0O00 ):#line:173
        O000OOOOO000O0OOO ={"time":time .time (),"write_total":OOOO00OO0O0OO0O00 ['write_total'],"read_total":OOOO00OO0O0OO0O00 ['read_total'],"container_id":OOOO00OO0O0OO0O00 ['container_id']}#line:179
        dp .sql ("io_stats").where ("time<?",(O00OO0000O0O0OOOO .__O0OOOOOOOO0O0OO00 ['expired'],)).delete ()#line:180
        dp .sql ("io_stats").insert (O000OOOOO000O0OOO )#line:181
    def write_net (OO0000000O00O000O ,OOO0OOOO00O00OO00 ):#line:183
        O0OO0OOO00O000000 ={"time":time .time (),"tx_total":OOO0OOOO00O00OO00 ['tx_total'],"rx_total":OOO0OOOO00O00OO00 ['rx_total'],"tx":OOO0OOOO00O00OO00 ['tx'],"rx":OOO0OOOO00O00OO00 ['rx'],"container_id":OOO0OOOO00O00OO00 ['container_id']}#line:191
        dp .sql ("net_stats").where ("time<?",(OO0000000O00O000O .__O0OOOOOOOO0O0OO00 ['expired'],)).delete ()#line:192
        dp .sql ("net_stats").insert (O0OO0OOO00O000000 )#line:193
    def write_mem (O000OO0OOOO00O000 ,O0OO00O00OO0O00O0 ):#line:195
        O0O0O000O0O0OO0O0 ={"time":time .time (),"mem_limit":O0OO00O00OO0O00O0 ['limit'],"cache":O0OO00O00OO0O00O0 ['cache'],"usage":O0OO00O00OO0O00O0 ['usage'],"usage_total":O0OO00O00OO0O00O0 ['usage_total'],"container_id":O0OO00O00OO0O00O0 ['container_id']}#line:203
        dp .sql ("mem_stats").where ("time<?",(O000OO0OOOO00O000 .__O0OOOOOOOO0O0OO00 ['expired'],)).delete ()#line:204
        dp .sql ("mem_stats").insert (O0O0O000O0O0OO0O0 )#line:205
    def get_container_count (OOOOO00O000O00OO0 ,O0OO0O0000OO0OOOO ):#line:208
        OO0OOOO000O0OO0OO =O0OO0O0000OO0OOOO .url #line:209
        return len (OOOOO00O000O00OO0 .docker_client (OO0OOOO000O0OO0OO ).containers .list ())#line:210
