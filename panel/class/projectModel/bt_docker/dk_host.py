# coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: zouhw <zhw@bt.cn>
# -------------------------------------------------------------------

# ------------------------------
# Docker模型
# ------------------------------
import public #line:13
import projectModel .bt_docker .dk_public as dp #line:14
class main :#line:16
    def get_list (OO0OO00OOOO00OOOO ,args =None ):#line:19
        O00000O00OO0O0OOO =dp .sql ("hosts").select ()#line:20
        for OOOOO0O0O0O0OO0O0 in O00000O00OO0O0OOO :#line:21
            if dp .docker_client (OOOOO0O0O0O0OO0O0 ['url']):#line:22
                OOOOO0O0O0O0OO0O0 ['status']=True #line:23
            else :#line:24
                OOOOO0O0O0O0OO0O0 ['status']=False #line:25
        return O00000O00OO0O0OOO #line:26
    def add (O0O0O0OO00OOO00OO ,OO000OO0000OOO00O ):#line:29
        ""#line:34
        import time #line:35
        OO00O0O0OO0OO0O0O =O0O0O0OO00OOO00OO .get_list ()#line:36
        for O0000OO0O0OO0O000 in OO00O0O0OO0OO0O0O :#line:37
            if O0000OO0O0OO0O000 ['url']==OO000OO0000OOO00O .url :#line:38
                return public .returnMsg (False ,"此主机已经存在！")#line:39
        if not dp .docker_client (OO000OO0000OOO00O .url ):#line:41
            return public .returnMsg (False ,"连接服务器失败，请检查docker是否已经启动！")#line:42
        OOOOOOOOO00O00000 ={"url":OO000OO0000OOO00O .url ,"remark":OO000OO0000OOO00O .remark ,"time":int (time .time ())}#line:47
        dp .write_log ("添加主机【{}】成功！".format (OO000OO0000OOO00O .url ))#line:48
        dp .sql ('hosts').insert (OOOOOOOOO00O00000 )#line:49
        return public .returnMsg (True ,"添加docker主机成功！")#line:50
    def delete (OOO0OO000000OOO00 ,O0O0OO0O00O0O000O ):#line:52
        ""#line:56
        O0OOOO0OO00O00OOO =dp .sql ('hosts').where ('id=?',O0O0OO0O00O0O000O (O0O0OO0O00O0O000O .id ,)).find ()#line:57
        dp .sql ('hosts').delete (id =O0O0OO0O00O0O000O .id )#line:58
        dp .write_log ("删除主机【{}】成功！".format (O0OOOO0OO00O00OOO ['url']))#line:59
        return public .returnMsg (True ,"删除主机成功！")