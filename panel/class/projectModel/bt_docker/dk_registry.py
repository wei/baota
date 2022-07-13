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
import os #line:14
import json #line:15
import projectModel .bt_docker .dk_public as dp #line:16
class main :#line:18
    def docker_client (O0000O0000OOO000O ,O0OO0OOOOO0O00000 ):#line:20
        return dp .docker_client (O0OO0OOOOO0O00000 )#line:21
    def add (OO0OO0OO0O0OOO000 ,OO00OO00OOO00OOO0 ):#line:23
        ""#line:34
        if not OO00OO00OOO00OOO0 .registry :#line:36
            OO00OO00OOO00OOO0 .registry ="docker.io"#line:37
        O0O00000O000O0OO0 =OO0OO0OO0O0OOO000 .login (OO00OO00OOO00OOO0 .url ,OO00OO00OOO00OOO0 .registry ,OO00OO00OOO00OOO0 .username ,OO00OO00OOO00OOO0 .password )#line:38
        if not O0O00000O000O0OO0 ['status']:#line:39
            return O0O00000O000O0OO0 #line:40
        O000OO0O00OO00O00 =OO0OO0OO0O0OOO000 .registry_list ("get")['msg']['registry']#line:41
        for OOOOOOOO0O0OO00OO in O000OO0O00OO00O00 :#line:42
            if OOOOOOOO0O0OO00OO ['name']==OO00OO00OOO00OOO0 .name :#line:43
                return public .returnMsg (False ,"名称已经存在！<br><br>名称: {}".format (OO00OO00OOO00OOO0 .name ))#line:44
            if OOOOOOOO0O0OO00OO ['username']==OO00OO00OOO00OOO0 .username and OO00OO00OOO00OOO0 .registry ==OOOOOOOO0O0OO00OO ['url']:#line:45
                return public .returnMsg (False ,"该仓库信息已经存在！")#line:46
        O00OO0O0OO0000O0O ={"name":OO00OO00OOO00OOO0 .name ,"url":OO00OO00OOO00OOO0 .registry ,"namespace":OO00OO00OOO00OOO0 .namespace ,"username":OO00OO00OOO00OOO0 .username ,"password":OO00OO00OOO00OOO0 .password ,"remark":OO00OO00OOO00OOO0 .remark }#line:54
        dp .sql ("registry").insert (O00OO0O0OO0000O0O )#line:55
        dp .write_log ("添加仓库【{}】【{}】成功！".format (OO00OO00OOO00OOO0 .name ,OO00OO00OOO00OOO0 .registry ))#line:56
        return public .returnMsg (True ,"添加成功！")#line:57
    def edit (O0O0O00O000000O0O ,O0O0000O0O0O00OOO ):#line:59
        ""#line:70
        if str (O0O0000O0O0O00OOO .id )=="1":#line:72
            return public .returnMsg (False ,"不能对【Docker官方仓库】进行编辑！")#line:73
        if not O0O0000O0O0O00OOO .registry :#line:74
            O0O0000O0O0O00OOO .registry ="docker.io"#line:75
        OOO0O0OO00O0O0OOO =O0O0O00O000000O0O .login (O0O0000O0O0O00OOO .url ,O0O0000O0O0O00OOO .registry ,O0O0000O0O0O00OOO .username ,O0O0000O0O0O00OOO .password )#line:76
        if not OOO0O0OO00O0O0OOO ['status']:#line:77
            return OOO0O0OO00O0O0OOO #line:78
        OOO0O0OO00O0O0OOO =dp .sql ("registry").where ("id=?",(O0O0000O0O0O00OOO .id ,)).find ()#line:79
        if not OOO0O0OO00O0O0OOO :#line:80
            return public .returnMsg (False ,"没有找到这个仓库")#line:81
        O000000OO0OO000OO ={"name":O0O0000O0O0O00OOO .name ,"url":O0O0000O0O0O00OOO .registry ,"username":O0O0000O0O0O00OOO .username ,"password":O0O0000O0O0O00OOO .password ,"namespace":O0O0000O0O0O00OOO .namespace ,"remark":O0O0000O0O0O00OOO .remark }#line:89
        dp .sql ("registry").where ("id=?",(O0O0000O0O0O00OOO .id ,)).update (O000000OO0OO000OO )#line:90
        dp .write_log ("编辑仓库【{}】【{}】成功！".format (O0O0000O0O0O00OOO .name ,O0O0000O0O0O00OOO .registry ))#line:91
        return public .returnMsg (True ,"编辑成功！")#line:92
    def remove (OO00O0O0O000OO0OO ,OOO0O0OOOO0O0OOO0 ):#line:94
        ""#line:100
        if str (OOO0O0OOOO0O0OOO0 .id )=="1":#line:101
            return public .returnMsg (False ,"不能删除【Docker官方仓库】！")#line:102
        OO0OOOO000OO000OO =dp .sql ("registry").where ("id=?",(OOO0O0OOOO0O0OOO0 .id )).find ()#line:103
        dp .sql ("registry").where ("id=?",(OOO0O0OOOO0O0OOO0 .id ,)).delete ()#line:104
        dp .write_log ("删除仓库【{}】【{}】成功！".format (OO0OOOO000OO000OO ['name'],OO0OOOO000OO000OO ['url']))#line:105
        return public .returnMsg (True ,"删除成功！")#line:106
    def registry_list (OO0OO00O00O0O0OO0 ,OOO000000O000OOOO ):#line:108
        ""#line:112
        import projectModel .bt_docker .dk_setup as ds #line:113
        O000O000000OO00O0 =dp .sql ("registry").select ()#line:114
        if not isinstance (O000O000000OO00O0 ,list ):#line:115
            O000O000000OO00O0 =[]#line:116
        O0O0OO0OO000OO0OO =ds .main ()#line:117
        OOO0OO000O0000O00 ={"registry":O000O000000OO00O0 ,"installed":O0O0OO0OO000OO0OO .check_docker_program (),"service_status":O0O0OO0OO000OO0OO .get_service_status ()}#line:122
        return public .returnMsg (True ,OOO0OO000O0000O00 )#line:123
    def registry_info (O0OO0O0O0OOO0O0OO ,O00O0O0O0OOO00O00 ):#line:125
        return dp .sql ("registry").where ("name=?",(O00O0O0O0OOO00O00 ,)).find ()#line:126
    def login (O0O00000OOOO0OO0O ,O0OO0OOOO0OOOO000 ,OOOO00O0O0OO0OO0O ,O00OO0O00OOOO00O0 ,OOOO0O00000OO0O0O ):#line:128
        ""#line:133
        import docker .errors #line:134
        try :#line:135
            O0O00000OO0000OOO =O0O00000OOOO0OO0O .docker_client (O0OO0OOOO0OOOO000 ).login (registry =OOOO00O0O0OO0OO0O ,username =O00OO0O00OOOO00O0 ,password =OOOO0O00000OO0O0O ,reauth =False )#line:141
            return public .returnMsg (True ,str (O0O00000OO0000OOO ))#line:142
        except docker .errors .APIError as OO0O00000O00O0OOO :#line:143
            if "unauthorized: incorrect username or password"in str (OO0O00000O00O0OOO ):#line:144
                return public .returnMsg (False ,"登录测试失败！<br><br>原因: 账号密码错误！{}".format (OO0O00000O00O0OOO ))#line:145
            return public .returnMsg (False ,"登录测试失败！<br><br>原因: {}".format (OO0O00000O00O0OOO ))