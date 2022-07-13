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
    def docker_client (O0O0000O00O00OO00 ,O0000O000000O000O ):#line:19
        import projectModel .bt_docker .dk_public as dp #line:20
        return dp .docker_client (O0000O000000O000O )#line:21
    def get_host_network (OO0O000O00OO00O00 ,O000OO00O0OO0O0OO ):#line:23
        ""#line:28
        import projectModel .bt_docker .dk_setup as ds #line:29
        O00000O0OO0O0OO00 =ds .main ()#line:30
        O0O000O00O0OO0000 =O00000O0OO0O0OO00 .check_docker_program ()#line:31
        OOO00O00OOO0O00OO =O00000O0OO0O0OO00 .get_service_status ()#line:32
        OO0000O00O0O0O0O0 =OO0O000O00OO00O00 .docker_client (O000OO00O0OO0O0OO .url )#line:33
        if not OO0000O00O0O0O0O0 :#line:34
            OO00O00000OO00O00 ={"images_list":[],"registry_list":[],"installed":O0O000O00O0OO0000 ,"service_status":OOO00O00OOO0O00OO }#line:40
            return public .returnMsg (True ,OO00O00000OO00O00 )#line:41
        O0O00OOO00O00OO00 =OO0000O00O0O0O0O0 .networks #line:42
        O0O0O00OOO00000O0 =OO0O000O00OO00O00 .get_network_attr (O0O00OOO00O00OO00 )#line:43
        OO00O00000OO00O00 =list ()#line:44
        for O0OOOOOO0O0O0O00O in O0O0O00OOO00000O0 :#line:45
            O000O0OOOO0O0OOO0 =""#line:46
            OOO00O00O00OO0O0O =""#line:47
            if O0OOOOOO0O0O0O00O ["IPAM"]["Config"]:#line:48
                if "Subnet"in O0OOOOOO0O0O0O00O ["IPAM"]["Config"][0 ]:#line:49
                    O000O0OOOO0O0OOO0 =O0OOOOOO0O0O0O00O ["IPAM"]["Config"][0 ]["Subnet"]#line:50
                if "Gateway"in O0OOOOOO0O0O0O00O ["IPAM"]["Config"][0 ]:#line:51
                    OOO00O00O00OO0O0O =O0OOOOOO0O0O0O00O ["IPAM"]["Config"][0 ]["Gateway"]#line:52
            O00O00O0OOO0OO00O ={"id":O0OOOOOO0O0O0O00O ["Id"],"name":O0OOOOOO0O0O0O00O ["Name"],"time":O0OOOOOO0O0O0O00O ["Created"],"driver":O0OOOOOO0O0O0O00O ["Driver"],"subnet":O000O0OOOO0O0OOO0 ,"gateway":OOO00O00O00OO0O0O ,"labels":O0OOOOOO0O0O0O00O ["Labels"]}#line:61
            OO00O00000OO00O00 .append (O00O00O0OOO0OO00O )#line:62
        O0O0000O00OO0O0OO ={"network":OO00O00000OO00O00 ,"installed":O0O000O00O0OO0000 ,"service_status":OOO00O00OOO0O00OO }#line:68
        return public .returnMsg (True ,O0O0000O00OO0O0OO )#line:69
    def get_network_attr (OOO0OOO0OOOO0OOO0 ,O00O0O00O0O0OOO0O ):#line:71
        O00OOOOO00OO00O00 =O00O0O00O0O0OOO0O .list ()#line:72
        return [OOO000OO0OO0000OO .attrs for OOO000OO0OO0000OO in O00OOOOO00OO00O00 ]#line:73
    def add (OO0000000OO0O00O0 ,OOO0OO00OO0000O0O ):#line:75
        ""#line:87
        import docker #line:88
        O0OOO0O0O00O0O000 =docker .types .IPAMPool (subnet =OOO0OO00OO0000O0O .subnet ,gateway =OOO0OO00OO0000O0O .gateway ,iprange =OOO0OO00OO0000O0O .iprange )#line:93
        OOO000OO00OO0OO00 =docker .types .IPAMConfig (pool_configs =[O0OOO0O0O00O0O000 ])#line:96
        OO0000000OO0O00O0 .docker_client (OOO0OO00OO0000O0O .url ).networks .create (name =OOO0OO00OO0000O0O .name ,options =dp .set_kv (OOO0OO00OO0000O0O .options ),driver ="bridge",ipam =OOO000OO00OO0OO00 ,labels =dp .set_kv (OOO0OO00OO0000O0O .labels ))#line:103
        dp .write_log ("添加网络 [{}] [{}] 成功!".format (OOO0OO00OO0000O0O .name ,OOO0OO00OO0000O0O .iprange ))#line:104
        return public .returnMsg (True ,"添加网络成功!")#line:105
    def del_network (O0O0O00OO00OOO00O ,O0OO0O0O0000O0OO0 ):#line:107
        ""#line:112
        try :#line:113
            O0000OO0OO000O0O0 =O0O0O00OO00OOO00O .docker_client (O0OO0O0O0000O0OO0 .url ).networks .get (O0OO0O0O0000O0OO0 .id )#line:115
            OO0O0OOO0O0O0O0OO =O0000OO0OO000O0O0 .attrs #line:116
            if OO0O0OOO0O0O0O0OO ['Name']in ["bridge","none"]:#line:117
                return public .returnMsg (False ,"系统默认网络不能被删除！")#line:118
            O0000OO0OO000O0O0 .remove ()#line:119
            dp .write_log ("删除网络 [{}] 成功!".format (OO0O0OOO0O0O0O0OO ['Name']))#line:120
            return public .returnMsg (True ,"删除成功！")#line:121
        except docker .errors .APIError as O00OO000OO00OO00O :#line:122
            if " has active endpoints"in str (O00OO000OO00OO00O ):#line:123
                return public .returnMsg (False ,"网络正在被使用中无法被删除!")#line:124
            return public .returnMsg (False ,"删除失败! {}".format (str (O00OO000OO00OO00O )))