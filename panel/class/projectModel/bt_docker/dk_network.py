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
    def docker_client (O0O0O000OOOO00O0O ,O000O0O00O00O0O00 ):#line:19
        import projectModel .bt_docker .dk_public as dp #line:20
        return dp .docker_client (O000O0O00O00O0O00 )#line:21
    def get_host_network (O00OOO00O0O00O0OO ,O0OO0OOOOO0O000OO ):#line:23
        ""#line:28
        import projectModel .bt_docker .dk_setup as ds #line:29
        OOOOO0000O00OO00O =ds .main ()#line:30
        OO00OO0O00000OO00 =OOOOO0000O00OO00O .check_docker_program ()#line:31
        OOO0O000O0OO0OOOO =OOOOO0000O00OO00O .get_service_status ()#line:32
        OOOO0OO000O0O00O0 =O00OOO00O0O00O0OO .docker_client (O0OO0OOOOO0O000OO .url )#line:33
        if not OOOO0OO000O0O00O0 :#line:34
            OOOO0O0OOOO000000 ={"images_list":[],"registry_list":[],"installed":OO00OO0O00000OO00 ,"service_status":OOO0O000O0OO0OOOO }#line:40
            return public .returnMsg (True ,OOOO0O0OOOO000000 )#line:41
        OO000OO0OO00O00OO =OOOO0OO000O0O00O0 .networks #line:42
        OO000O00O0O0O00OO =O00OOO00O0O00O0OO .get_network_attr (OO000OO0OO00O00OO )#line:43
        OOOO0O0OOOO000000 =list ()#line:44
        for OO0O00OO0O0O0O0OO in OO000O00O0O0O00OO :#line:45
            OO00OO0O000OOO0OO =""#line:46
            O0OO0OO0OO0000O0O =""#line:47
            if OO0O00OO0O0O0O0OO ["IPAM"]["Config"]:#line:48
                if "Subnet"in OO0O00OO0O0O0O0OO ["IPAM"]["Config"][0 ]:#line:49
                    OO00OO0O000OOO0OO =OO0O00OO0O0O0O0OO ["IPAM"]["Config"][0 ]["Subnet"]#line:50
                if "Gateway"in OO0O00OO0O0O0O0OO ["IPAM"]["Config"][0 ]:#line:51
                    O0OO0OO0OO0000O0O =OO0O00OO0O0O0O0OO ["IPAM"]["Config"][0 ]["Gateway"]#line:52
            OOO0O0O00O0O0000O ={"id":OO0O00OO0O0O0O0OO ["Id"],"name":OO0O00OO0O0O0O0OO ["Name"],"time":OO0O00OO0O0O0O0OO ["Created"],"driver":OO0O00OO0O0O0O0OO ["IPAM"]["Driver"],"subnet":OO00OO0O000OOO0OO ,"gateway":O0OO0OO0OO0000O0O ,"labels":OO0O00OO0O0O0O0OO ["Labels"]}#line:61
            OOOO0O0OOOO000000 .append (OOO0O0O00O0O0000O )#line:62
        O00OOOO0OO000O000 ={"network":OOOO0O0OOOO000000 ,"installed":OO00OO0O00000OO00 ,"service_status":OOO0O000O0OO0OOOO }#line:68
        return public .returnMsg (True ,O00OOOO0OO000O000 )#line:69
    def get_network_attr (OOO00O0O00OOO00O0 ,OOO000000O0O0OOO0 ):#line:71
        OO0O0OO0OOO00OOO0 =OOO000000O0O0OOO0 .list ()#line:72
        return [OOOO00O0OO000O000 .attrs for OOOO00O0OO000O000 in OO0O0OO0OOO00OOO0 ]#line:73
    def add (O00O000000O00OO0O ,O0O0OO00O000OOOOO ):#line:75
        ""#line:87
        import docker #line:88
        OO00O0OO00OO0OO0O =docker .types .IPAMPool (subnet =O0O0OO00O000OOOOO .subnet ,gateway =O0O0OO00O000OOOOO .gateway ,iprange =O0O0OO00O000OOOOO .iprange )#line:93
        OOO0O0O0OO00OOO00 =docker .types .IPAMConfig (pool_configs =[OO00O0OO00OO0OO0O ])#line:96
        O00O000000O00OO0O .docker_client (O0O0OO00O000OOOOO .url ).networks .create (name =O0O0OO00O000OOOOO .name ,options =O0O0OO00O000OOOOO .options if O0O0OO00O000OOOOO .options else None ,driver ="bridge",ipam =OOO0O0O0OO00OOO00 ,labels =dp .set_kv (O0O0OO00O000OOOOO .labels ))#line:103
        dp .write_log ("添加网络【{}】【{}】成功！".format (O0O0OO00O000OOOOO .name ,O0O0OO00O000OOOOO .iprange ))#line:104
        return public .returnMsg (True ,"添加成功！")#line:105
    def del_network (O00000OO000O0O00O ,OOOOOO00O000OOOOO ):#line:107
        ""#line:112
        try :#line:113
            O0OOO0O0000OOO00O =O00000OO000O0O00O .docker_client (OOOOOO00O000OOOOO .url ).networks .get (OOOOOO00O000OOOOO .id )#line:115
            OOOO0OO0OOOOOO0O0 =O0OOO0O0000OOO00O .attrs #line:116
            if OOOO0OO0OOOOOO0O0 ['Name']in ["bridge","none"]:#line:117
                return public .returnMsg (False ,"系统默认网络无法删除！")#line:118
            O0OOO0O0000OOO00O .remove ()#line:119
            dp .write_log ("删除网络【{}】成功！".format (OOOO0OO0OOOOOO0O0 ['Name']))#line:120
            return public .returnMsg (True ,"删除成功！")#line:121
        except docker .errors .APIError as OO0OO0OOOOO00OO0O :#line:122
            if " has active endpoints"in str (OO0OO0OOOOO00OO0O ):#line:123
                return public .returnMsg (False ,"该网络正在使用中无法删除！")#line:124
            return public .returnMsg (False ,"删除失败！{}".format (str (OO0OO0OOOOO00OO0O )))