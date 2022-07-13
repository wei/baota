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

import db #line:14
import public #line:15
import json #line:16
def sql (OO0OOO00OOO000O00 ):#line:18
    with db .Sql ()as O0O0O000O000O00OO :#line:19
        O0O0O000O000O00OO .dbfile ("docker")#line:20
        return O0O0O000O000O00OO .table (OO0OOO00OOO000O00 )#line:21
def docker_client (url ="unix:///var/run/docker.sock"):#line:24
    import docker #line:25
    """
    目前仅支持本地服务器
    :param url: unix:///var/run/docker.sock
    :return:
    """#line:30
    try :#line:31
        OO0O0OO0OO000000O =docker .DockerClient (base_url =url )#line:32
        OO0O0OO0OO000000O .networks .list ()#line:33
        return OO0O0OO0OO000000O #line:34
    except :#line:35
        return False #line:36
def docker_client_low (url ="unix:///var/run/docker.sock"):#line:38
    ""#line:43
    import docker #line:44
    try :#line:45
        O0OO0OO000OO00O00 =docker .APIClient (base_url =url )#line:46
        return O0OO0OO000OO00O00 #line:47
    except docker .errors .DockerException :#line:48
        return False #line:49
def get_cpu_count ():#line:52
    import re #line:53
    O0OOOOOO0000OOO00 =open ('/proc/cpuinfo','r').read ()#line:54
    OOO00O0O000OO0O0O ="processor\s*:"#line:55
    OOOO0O000O0OOO000 =re .findall (OOO00O0O000OO0O0O ,O0OOOOOO0000OOO00 )#line:56
    if not OOOO0O000O0OOO000 :#line:57
        return 0 #line:58
    return len (OOOO0O000O0OOO000 )#line:59
def set_kv (O0OOOOO0OOOOOOOO0 ):#line:61
    ""#line:66
    if not O0OOOOO0OOOOOOOO0 :#line:67
        return None #line:68
    OO000O00000OOOOO0 =O0OOOOO0OOOOOOOO0 .split ('\n')#line:69
    O0OOOO0OO00OOO0OO =dict ()#line:70
    for OOO00OOOOOO0000OO in OO000O00000OOOOO0 :#line:71
        OOO00OOOOOO0000OO =OOO00OOOOOO0000OO .strip ()#line:72
        if not OOO00OOOOOO0000OO :#line:73
            continue #line:74
        O0O0OO0OO00O0O0O0 ,O0O00OOOOO0O000O0 =OOO00OOOOOO0000OO .split ('=')#line:75
        O0OOOO0OO00OOO0OO [O0O0OO0OO00O0O0O0 ]=O0O00OOOOO0O000O0 #line:76
    return O0OOOO0OO00OOO0OO #line:77
def get_mem_info ():#line:79
    import psutil #line:81
    OO0O0OO0OOO0O00O0 =psutil .virtual_memory ()#line:82
    OO0OO00OO000OO0O0 =int (OO0O0OO0OOO0O00O0 .total )#line:83
    return OO0OO00OO000OO0O0 #line:84
def byte_conversion (OOO0O0OO0000OOOOO ):#line:86
    if "b"in OOO0O0OO0000OOOOO :#line:87
        return int (OOO0O0OO0000OOOOO .replace ('b',''))#line:88
    elif "KB"in OOO0O0OO0000OOOOO :#line:89
        return int (OOO0O0OO0000OOOOO .replace ('KB',''))*1024 #line:90
    elif "MB"in OOO0O0OO0000OOOOO :#line:91
        return int (OOO0O0OO0000OOOOO .replace ('MB',''))*1024 *1024 #line:92
    elif "GB"in OOO0O0OO0000OOOOO :#line:93
        return int (OOO0O0OO0000OOOOO .replace ('GB',''))*1024 *1024 *1024 #line:94
    else :#line:95
        return False #line:96
def log_docker (O0O00000O00O00OOO ,OOO000O000O00O000 ):#line:98
    __O000O0O0OO0OOO0O0 ='/tmp/dockertmp.log'#line:99
    while True :#line:100
        try :#line:101
            OO0OO0000OO0OO000 =O0O00000O00O00OOO .__next__ ()#line:102
            try :#line:103
                OO0OO0000OO0OO000 =json .loads (OO0OO0000OO0OO000 )#line:104
                if 'status'in OO0OO0000OO0OO000 :#line:105
                    OOOO0O0O000O00O00 ="{}\n".format (OO0OO0000OO0OO000 ['status'])#line:106
                    public .writeFile (__O000O0O0OO0OOO0O0 ,OOOO0O0O000O00O00 ,'a+')#line:107
            except :#line:108
                public .writeFile (__O000O0O0OO0OOO0O0 ,public .get_error_info (),'a+')#line:109
            if 'stream'in OO0OO0000OO0OO000 :#line:110
                OOOO0O0O000O00O00 =OO0OO0000OO0OO000 ['stream']#line:111
                public .writeFile (__O000O0O0OO0OOO0O0 ,OOOO0O0O000O00O00 ,'a+')#line:112
        except StopIteration :#line:113
            public .writeFile (__O000O0O0OO0OOO0O0 ,f'{OOO000O000O00O000} complete.','a+')#line:114
            break #line:115
        except ValueError :#line:116
            public .writeFile (log_path ,f'Error parsing output from {OOO000O000O00O000}: {OO0OO0000OO0OO000}','a+')#line:117
def docker_conf ():#line:119
    ""#line:125
    O0O000OOO00OO0000 =public .readFile ("{}/data/docker.conf".format (public .get_panel_path ()))#line:126
    if not O0O000OOO00OO0000 :#line:127
        return {"SAVE":30 }#line:128
    O00O0000O0O000OOO =dict ()#line:129
    for O0O0O00O00OOOOO00 in O0O000OOO00OO0000 .split ("\n"):#line:130
        if not O0O0O00O00OOOOO00 :#line:131
            continue #line:132
        O0OOO00OOOO0O0000 ,O000OO000O0000OOO =O0O0O00O00OOOOO00 .split ("=")#line:133
        if O0OOO00OOOO0O0000 =="SAVE":#line:134
            O000OO000O0000OOO =int (O000OO000O0000OOO )#line:135
        O00O0000O0O000OOO [O0OOO00OOOO0O0000 ]=O000OO000O0000OOO #line:136
    return O00O0000O0O000OOO #line:137
def get_process_id (O0O0O000O0O0OO0O0 ,O0OOOO00OO0O0O00O ):#line:139
    import psutil #line:140
    O0OO0OO0OOO00OO00 =psutil .pids ()#line:141
    for O0OO0O0O00O00O000 in O0OO0OO0OOO00OO00 :#line:142
        try :#line:143
            O0O00O0O00OO00000 =psutil .Process (O0OO0O0O00O00O000 )#line:144
            if O0O00O0O00OO00000 .name ()==O0O0O000O0O0OO0O0 and O0OOOO00OO0O0O00O in O0O00O0O00OO00000 .cmdline ():#line:145
                return O0OO0O0O00O00O000 #line:146
        except :#line:147
            pass #line:148
    return False #line:149
def write_log (OO000OO00O0OO0O00 ):#line:151
    public .WriteLog ("Docker模块",OO000OO00O0OO0O00 )#line:152
def check_socket (OOO0O0O0OOO00O00O ):#line:154
    import socket #line:155
    O0O00000OOOO000O0 =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:156
    OOOO0O00O000O0000 =("127.0.0.1",int (OOO0O0O0OOO00O00O ))#line:157
    OOOOO00OO00O00000 =O0O00000OOOO000O0 .connect_ex (OOOO0O00O000O0000 )#line:158
    O0O00000OOOO000O0 .close ()#line:159
    if OOOOO00OO00O00000 ==0 :#line:160
        return True #line:161
    else :#line:162
        return False