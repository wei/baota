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
import docker .errors #line:14
import projectModel .bt_docker .dk_public as dp #line:15
class main :#line:16
    def __init__ (O00OOOOO00OO0O000 ):#line:18
        O00OOOOO00OO0O000 .alter_table ()#line:19
    def alter_table (O00OOOOOO0O0O0000 ):#line:21
        if not dp .sql ('sqlite_master').where ('type=? AND name=? AND sql LIKE ?',('table','container','%sid%')).count ():#line:23
            dp .sql ('container').execute ("alter TABLE container add container_name VARCHAR DEFAULT ''",())#line:24
    def docker_client (O0O000OOO00O00O00 ,OOO0O0O0000O0O0OO ):#line:26
        return dp .docker_client (OOO0O0O0000O0O0OO )#line:27
    def run (O00OOOOOOOO0OOO00 ,OO0OO000OO00O0OO0 ):#line:30
        ""#line:43
        if not hasattr (OO0OO000OO00O0OO0 ,'ports'):#line:44
            OO0OO000OO00O0OO0 .ports =False #line:45
        if not hasattr (OO0OO000OO00O0OO0 ,'volumes'):#line:46
            OO0OO000OO00O0OO0 .volumes =False #line:47
        if OO0OO000OO00O0OO0 .ports :#line:49
            for O00O0000OO0O0O0O0 in OO0OO000OO00O0OO0 .ports :#line:50
                if dp .check_socket (OO0OO000OO00O0OO0 .ports [O00O0000OO0O0O0O0 ]):#line:51
                    return public .returnMsg (False ,"服务端端口【{}】已经被使用,请更换其他端口！".format (OO0OO000OO00O0OO0 .ports [O00O0000OO0O0O0O0 ]))#line:52
        if not OO0OO000OO00O0OO0 .image :#line:53
            return public .returnMsg (False ,"没有选择镜像，请先到镜像标签拉取你需要的镜像！")#line:54
        if OO0OO000OO00O0OO0 .restart_policy ['Name']=="always":#line:55
            OO0OO000OO00O0OO0 .restart_policy ={"Name":"always"}#line:56
        OO0OO000OO00O0OO0 .cpu_quota =float (OO0OO000OO00O0OO0 .cpuset_cpus )*100000 #line:59
        try :#line:60
            if not OO0OO000OO00O0OO0 .name :#line:61
                OO0OO000OO00O0OO0 .name ="{}-{}".format (OO0OO000OO00O0OO0 .image ,public .GetRandomString (8 ))#line:62
            if int (OO0OO000OO00O0OO0 .cpu_quota )/100000 >dp .get_cpu_count ():#line:63
                return public .returnMsg (False ,"CPU配额已超过可用的核心数！")#line:64
            O00O0O0O00000000O =dp .byte_conversion (OO0OO000OO00O0OO0 .mem_limit )#line:65
            if O00O0O0O00000000O >dp .get_mem_info ():#line:66
                return public .returnMsg (False ,"内存配额已超过可用数！")#line:67
            O0OO00O000O00O0O0 =O00OOOOOOOO0OOO00 .docker_client (OO0OO000OO00O0OO0 .url ).containers .run (name =OO0OO000OO00O0OO0 .name ,image =OO0OO000OO00O0OO0 .image ,detach =True ,publish_all_ports =True if OO0OO000OO00O0OO0 .publish_all_ports =="1"else False ,ports =OO0OO000OO00O0OO0 .ports if OO0OO000OO00O0OO0 .ports else None ,command =OO0OO000OO00O0OO0 .command ,auto_remove =True if str (OO0OO000OO00O0OO0 .auto_remove )=="1"else False ,environment =dp .set_kv (OO0OO000OO00O0OO0 .environment ),volumes =OO0OO000OO00O0OO0 .volumes ,cpu_quota =int (OO0OO000OO00O0OO0 .cpu_quota ),mem_limit =OO0OO000OO00O0OO0 .mem_limit ,restart_policy =OO0OO000OO00O0OO0 .restart_policy ,labels =dp .set_kv (OO0OO000OO00O0OO0 .labels ))#line:84
            if O0OO00O000O00O0O0 :#line:85
                OOO0OOO0O000O00O0 ={"cpu_limit":str (OO0OO000OO00O0OO0 .cpu_quota ),"container_name":OO0OO000OO00O0OO0 .name }#line:89
                dp .sql ('container').insert (OOO0OOO0O000O00O0 )#line:90
                public .set_module_logs ('docker','run_container',1 )#line:91
                dp .write_log ("创建容器【{}】成功！".format (OO0OO000OO00O0OO0 .name ))#line:92
                return public .returnMsg (True ,"容器创建成功！")#line:93
            return public .returnMsg (False ,'创建失败!')#line:94
        except docker .errors .APIError as O00O0O0O0OO0OO000 :#line:95
            if "container to be able to reuse that name."in str (O00O0O0O0OO0OO000 ):#line:96
                return public .returnMsg (False ,"该容器名已经存在！")#line:97
            if "Invalid container name"in str (O00O0O0O0OO0OO000 ):#line:98
                return public .returnMsg (False ,"容器名不合法, 请不要使用中文容器名！")#line:99
            if "bind: address already in use"in str (O00O0O0O0OO0OO000 ):#line:100
                OOOO0OOO000OOOO00 =""#line:101
                for O00O0000OO0O0O0O0 in OO0OO000OO00O0OO0 .ports :#line:102
                    if ":{}:".format (OO0OO000OO00O0OO0 .ports [O00O0000OO0O0O0O0 ])in str (O00O0O0O0OO0OO000 ):#line:103
                        OOOO0OOO000OOOO00 =OO0OO000OO00O0OO0 .ports [O00O0000OO0O0O0O0 ]#line:104
                OO0OO000OO00O0OO0 .id =OO0OO000OO00O0OO0 .name #line:105
                O00OOOOOOOO0OOO00 .del_container (OO0OO000OO00O0OO0 )#line:106
                return public .returnMsg (False ,"服务端端口{}正在使用中！请更换其他端口".format (OOOO0OOO000OOOO00 ))#line:107
            return public .returnMsg (False ,'创建失败! {}'.format (public .get_error_info ()))#line:108
    def commit (OOO0OO0OOOO000O00 ,OO0000OOO0OO0O00O ):#line:111
        ""#line:123
        if not hasattr (OO0000OOO0OO0O00O ,'conf')or not OO0000OOO0OO0O00O .conf :#line:124
            OO0000OOO0OO0O00O .conf =None #line:125
        if OO0000OOO0OO0O00O .repository =="docker.io":#line:126
            OO0000OOO0OO0O00O .repository =""#line:127
        OO00O0O00O0O0OOO0 =OOO0OO0OOOO000O00 .docker_client (OO0000OOO0OO0O00O .url ).containers .get (OO0000OOO0OO0O00O .id )#line:128
        OO00O0O00O0O0OOO0 .commit (repository =OO0000OOO0OO0O00O .repository if OO0000OOO0OO0O00O .repository else None ,tag =OO0000OOO0OO0O00O .tag if OO0000OOO0OO0O00O .tag else None ,message =OO0000OOO0OO0O00O .message if OO0000OOO0OO0O00O .message else None ,author =OO0000OOO0OO0O00O .author if OO0000OOO0OO0O00O .author else None ,conf =OO0000OOO0OO0O00O .conf )#line:136
        if hasattr (OO0000OOO0OO0O00O ,"path")and OO0000OOO0OO0O00O .path :#line:137
            OO0000OOO0OO0O00O .id ="{}:{}".format (OO0000OOO0OO0O00O .name ,OO0000OOO0OO0O00O .tag )#line:138
            import projectModel .bt_docker .dk_image as dk #line:139
            return dk .main ().save (OO0000OOO0OO0O00O )#line:140
        dp .write_log ("将容器【{}】提交为镜像【{}】成功！".format (OO00O0O00O0O0OOO0 .attrs ['Name'],OO0000OOO0OO0O00O .tag ))#line:141
        return public .returnMsg (True ,"提交成功！")#line:142
    def docker_shell (OO0O0O000O0O00OO0 ,O000OOO0OO00O0OOO ):#line:145
        ""#line:150
        try :#line:151
            OO0O0O000O0O00OO0 .docker_client (O000OOO0OO00O0OOO .url ).containers .get (O000OOO0OO00O0OOO .container_id )#line:152
            OO00OO0OOO0OOOO0O ='docker container exec -it {} /bin/bash'.format (O000OOO0OO00O0OOO .container_id )#line:153
            return public .returnMsg (True ,OO00OO0OOO0OOOO0O )#line:154
        except docker .errors .APIError as OOOO000OOO00OOO00 :#line:155
            return public .returnMsg (False ,'获取容器失败')#line:156
    def export (O00OO0000OO0O0O0O ,O00OO0O0OO0OOO0O0 ):#line:159
        ""#line:165
        from os import path as ospath #line:166
        from os import makedirs as makedirs #line:167
        try :#line:168
            if "tar"in O00OO0O0OO0OOO0O0 .name :#line:169
                O00O0OOO0O00OO00O ='{}/{}'.format (O00OO0O0OO0OOO0O0 .path ,O00OO0O0OO0OOO0O0 .name )#line:170
            else :#line:171
                O00O0OOO0O00OO00O ='{}/{}.tar'.format (O00OO0O0OO0OOO0O0 .path ,O00OO0O0OO0OOO0O0 .name )#line:172
            if not ospath .exists (O00OO0O0OO0OOO0O0 .path ):#line:173
                makedirs (O00OO0O0OO0OOO0O0 .path )#line:174
            public .writeFile (O00O0OOO0O00OO00O ,'')#line:175
            O0OO000OOO00O000O =open (O00O0OOO0O00OO00O ,'wb')#line:176
            OO0O00OO000O0OO0O =O00OO0000OO0O0O0O .docker_client (O00OO0O0OO0OOO0O0 .url ).containers .get (O00OO0O0OO0OOO0O0 .id )#line:177
            OOOO00O000O000000 =OO0O00OO000O0OO0O .export ()#line:178
            for O0O000OO0O0OO0OO0 in OOOO00O000O000000 :#line:179
                O0OO000OOO00O000O .write (O0O000OO0O0OO0OO0 )#line:180
            O0OO000OOO00O000O .close ()#line:181
            return public .returnMsg (True ,"成功导出到: {}".format (O00O0OOO0O00OO00O ))#line:182
        except :#line:183
            return public .returnMsg (False ,'操作失败: '+str (public .get_error_info ()))#line:184
    def del_container (OOO00O000000OOOO0 ,OO0O0OO0O00OO0OO0 ):#line:187
        ""#line:190
        import projectModel .bt_docker .dk_public as dp #line:191
        OOOO000OOO000OO0O =OOO00O000000OOOO0 .docker_client (OO0O0OO0O00OO0OO0 .url ).containers .get (OO0O0OO0O00OO0OO0 .id )#line:192
        OOOO000OOO000OO0O .remove (force =True )#line:193
        dp .sql ("cpu_stats").where ("container_id=?",(OO0O0OO0O00OO0OO0 .id ,)).delete ()#line:194
        dp .sql ("io_stats").where ("container_id=?",(OO0O0OO0O00OO0OO0 .id ,)).delete ()#line:195
        dp .sql ("mem_stats").where ("container_id=?",(OO0O0OO0O00OO0OO0 .id ,)).delete ()#line:196
        dp .sql ("net_stats").where ("container_id=?",(OO0O0OO0O00OO0OO0 .id ,)).delete ()#line:197
        dp .sql ("container").where ("container_nam=?",(OOOO000OOO000OO0O .attrs ['Name'])).delete ()#line:198
        dp .write_log ("删除容器【{}】成功！".format (OOOO000OOO000OO0O .attrs ['Name']))#line:199
        return public .returnMsg (True ,"删除成功！")#line:200
    def set_container_status (OO00O00OOO0000000 ,O00O0OOOO0O000OO0 ):#line:203
        import time #line:204
        OO0OOO00OOO00OOOO =OO00O00OOO0000000 .docker_client (O00O0OOOO0O000OO0 .url ).containers .get (O00O0OOOO0O000OO0 .id )#line:205
        if O00O0OOOO0O000OO0 .act =="start":#line:206
            OO0OOO00OOO00OOOO .start ()#line:207
        elif O00O0OOOO0O000OO0 .act =="stop":#line:208
            OO0OOO00OOO00OOOO .stop ()#line:209
        elif O00O0OOOO0O000OO0 .act =="pause":#line:210
            OO0OOO00OOO00OOOO .pause ()#line:211
        elif O00O0OOOO0O000OO0 .act =="unpause":#line:212
            OO0OOO00OOO00OOOO .unpause ()#line:213
        elif O00O0OOOO0O000OO0 .act =="reload":#line:214
            OO0OOO00OOO00OOOO .reload ()#line:215
        else :#line:216
            OO0OOO00OOO00OOOO .restart ()#line:217
        time .sleep (1 )#line:218
        OO00O00O00OOOO0O0 =OO00O00OOO0000000 .docker_client (O00O0OOOO0O000OO0 .url ).containers .get (O00O0OOOO0O000OO0 .id )#line:219
        return {"name":OO0OOO00OOO00OOOO .attrs ['Name'].replace ('/',''),"status":OO00O00O00OOOO0O0 .attrs ['State']['Status']}#line:220
    def stop (O0000OOO00O0O000O ,OO000O0OOO0OOO0OO ):#line:224
        ""#line:230
        try :#line:231
            OO000O0OOO0OOO0OO .act ="stop"#line:232
            OOOOO00O0OO0O0OO0 =O0000OOO00O0O000O .set_container_status (OO000O0OOO0OOO0OO )#line:233
            if OOOOO00O0OO0O0OO0 ['status']!="exited":#line:234
                return public .returnMsg (False ,"停止失败！")#line:235
            dp .write_log ("停止容器【{}】成功！".format (OOOOO00O0OO0O0OO0 ['name']))#line:236
            return public .returnMsg (True ,"停止成功！")#line:237
        except docker .errors .APIError as OO0OO0OOOOO0O0000 :#line:238
            if "is already paused"in str (OO0OO0OOOOO0O0000 ):#line:239
                return public .returnMsg (False ,"容器已经暂停！")#line:240
            if "No such container"in str (OO0OO0OOOOO0O0000 ):#line:241
                return public .returnMsg (True ,"容器已经停止并删除,因为容器勾选了停止后自动删除选项！")#line:242
            return public .returnMsg (False ,"停止失败！{}".format (OO0OO0OOOOO0O0000 ))#line:243
    def start (O000O000000OOO0OO ,O0000O0OOOO0000OO ):#line:245
        ""#line:251
        try :#line:252
            O0000O0OOOO0000OO .act ="start"#line:253
            O0OOOOOO0O0OO0O00 =O000O000000OOO0OO .set_container_status (O0000O0OOOO0000OO )#line:254
            if O0OOOOOO0O0OO0O00 ['status']!="running":#line:255
                return public .returnMsg (False ,"启动失败!")#line:256
            dp .write_log ("启动容器【{}】成功！".format (O0OOOOOO0O0OO0O00 ['name']))#line:257
            return public .returnMsg (True ,"启动成功！")#line:258
        except docker .errors .APIError as OOOOOOO00O0OOOO00 :#line:259
            if "cannot start a paused container, try unpause instead"in str (OOOOOOO00O0OOOO00 ):#line:260
                return O000O000000OOO0OO .unpause (O0000O0OOOO0000OO )#line:261
    def pause (OO000OO00000OO0O0 ,OOOO00OO00OOO00OO ):#line:263
        ""#line:270
        try :#line:271
            OOOO00OO00OOO00OO .act ="pause"#line:272
            OO00OOO000O0O0O00 =OO000OO00000OO0O0 .set_container_status (OOOO00OO00OOO00OO )#line:273
            if OO00OOO000O0O0O00 ['status']!="paused":#line:274
                return public .returnMsg (False ,"容器暂停失败！")#line:275
            dp .write_log ("暂停容器【{}】成功！".format (OO00OOO000O0O0O00 ['name']))#line:276
            return public .returnMsg (True ,"容器暂停成功！")#line:277
        except docker .errors .APIError as OO0O00000OO0O0O0O :#line:278
            if "is already paused"in str (OO0O00000OO0O0O0O ):#line:279
                return public .returnMsg (False ,"容器已经暂停！")#line:280
            if "is not running"in str (OO0O00000OO0O0O0O ):#line:281
                return public .returnMsg (False ,"容器没有启动，无法暂停！")#line:282
            if "is not paused"in str (OO0O00000OO0O0O0O ):#line:283
                return public .returnMsg (False ,"容器未没有暂停！")#line:284
            return str (OO0O00000OO0O0O0O )#line:285
    def unpause (O0OO00O00OO000OOO ,O0O000000O000000O ):#line:287
        ""#line:294
        try :#line:295
            O0O000000O000000O .act ="unpause"#line:296
            OOOOOO00OO0OO0000 =O0OO00O00OO000OOO .set_container_status (O0O000000O000000O )#line:297
            if OOOOOO00OO0OO0000 ['status']!="running":#line:298
                return public .returnMsg (False ,"启动失败！")#line:299
            dp .write_log ("取消暂停容器【{}】成功！".format (OOOOOO00OO0OO0000 ['name']))#line:300
            return public .returnMsg (True ,"容器取消暂停成功！")#line:301
        except docker .errors .APIError as OOOOOO0OO0OOO00OO :#line:302
            if "is already paused"in str (OOOOOO0OO0OOO00OO ):#line:303
                return public .returnMsg (False ,"容器已经暂停！")#line:304
            if "is not running"in str (OOOOOO0OO0OOO00OO ):#line:305
                return public .returnMsg (False ,"容器没有启动，无法暂停！")#line:306
            if "is not paused"in str (OOOOOO0OO0OOO00OO ):#line:307
                return public .returnMsg (False ,"容器未没有暂停！")#line:308
            return str (OOOOOO0OO0OOO00OO )#line:309
    def reload (O00O0OO0O00O0O00O ,OOO000O00OO00O000 ):#line:311
        ""#line:318
        OOO000O00OO00O000 .act ="reload"#line:319
        OOOO00O0OO0O000OO =O00O0OO0O00O0O00O .set_container_status (OOO000O00OO00O000 )#line:320
        if OOOO00O0OO0O000OO ['status']!="running":#line:321
            return public .returnMsg (False ,"启动失败！")#line:322
        dp .write_log ("重载容器【{}】成功！".format (OOOO00O0OO0O000OO ['name']))#line:323
        return public .returnMsg (True ,"容器重载成功！")#line:324
    def restart (O00OO0OOOOOOO0000 ,OO0OOO0O00O0OO0OO ):#line:326
        ""#line:333
        OO0OOO0O00O0OO0OO .act ="restart"#line:334
        O0O000OO000O00O0O =O00OO0OOOOOOO0000 .set_container_status (OO0OOO0O00O0OO0OO )#line:335
        if O0O000OO000O00O0O ['status']!="running":#line:336
            return public .returnMsg (False ,"启动失败！")#line:337
        dp .write_log ("重启容器【{}】成功！".format (O0O000OO000O00O0O ['name']))#line:338
        return public .returnMsg (True ,"容器重启成功！")#line:339
    def get_container_ip (O0OO0OOOO0000OO00 ,OOOOO00O0OOO00OO0 ):#line:341
        O0OOOO00000O000O0 =list ()#line:342
        for O0OOOOOO0O000OO0O in OOOOO00O0OOO00OO0 :#line:343
            O0OOOO00000O000O0 .append (OOOOO00O0OOO00OO0 [O0OOOOOO0O000OO0O ]['IPAddress'])#line:344
        return O0OOOO00000O000O0 #line:345
    def get_container_path (OO0OOO00000O000OO ,OOOO0000O00OO0OOO ):#line:347
        import os #line:348
        if not "GraphDriver"in OOOO0000O00OO0OOO :#line:349
            return False #line:350
        if "Data"not in OOOO0000O00OO0OOO ["GraphDriver"]:#line:351
            return False #line:352
        if "MergedDir"not in OOOO0000O00OO0OOO ["GraphDriver"]["Data"]:#line:353
            return False #line:354
        OOO0OO0OO0OOO0OOO =OOOO0000O00OO0OOO ["GraphDriver"]["Data"]["MergedDir"]#line:355
        if not os .path .exists (OOO0OO0OO0OOO0OOO ):#line:356
            return ""#line:357
        return OOO0OO0OO0OOO0OOO #line:358
    def get_other_data_for_container_list (O00O0OO00000O0OOO ,OOO00OO00O00OO0O0 ):#line:361
        import projectModel .bt_docker .dk_image as di #line:362
        import projectModel .bt_docker .dk_volume as dv #line:363
        import projectModel .bt_docker .dk_compose as dc #line:364
        import projectModel .bt_docker .dk_setup as ds #line:365
        O00OOO0O0OO0O0O0O =di .main ().image_list (OOO00OO00O00OO0O0 )#line:367
        if O00OOO0O0OO0O0O0O ['status']:#line:368
            O00OOO0O0OO0O0O0O =O00OOO0O0OO0O0O0O ['msg']['images_list']#line:369
        else :#line:370
            O00OOO0O0OO0O0O0O =list ()#line:371
        O0O0000000O0O00OO =dv .main ().get_volume_list (OOO00OO00O00OO0O0 )#line:373
        if O0O0000000O0O00OO ['status']:#line:374
            O0O0000000O0O00OO =O0O0000000O0O00OO ['msg']['volume']#line:375
        else :#line:376
            O0O0000000O0O00OO =list ()#line:377
        OO0O00000O0O00O0O =dc .main ().template_list (OOO00OO00O00OO0O0 )#line:379
        if OO0O00000O0O00O0O ['status']:#line:380
            OO0O00000O0O00O0O =OO0O00000O0O00O0O ['msg']['template']#line:381
        else :#line:382
            OO0O00000O0O00O0O =list ()#line:383
        OOOOO0O000O000O00 =dp .get_cpu_count ()#line:384
        OO0O00O00OO0O00OO =dp .get_mem_info ()#line:385
        OO00000OO0OO00OOO =ds .main ()#line:386
        return {"images":O00OOO0O0OO0O0O0O ,"volumes":O0O0000000O0O00OO ,"template":OO0O00000O0O00O0O ,"online_cpus":OOOOO0O000O000O00 ,"mem_total":OO0O00O00OO0O00OO ,"installed":OO00000OO0OO00OOO .check_docker_program (),"service_status":OO00000OO0OO00OOO .get_service_status ()}#line:395
    def get_list (OOOOO0O0OO0OO0OOO ,O0O00O0O00O00O0OO ):#line:398
        ""#line:402
        import projectModel .bt_docker .dk_setup as ds #line:404
        OOO0O000OO000O0OO =OOOOO0O0OO0OO0OOO .get_other_data_for_container_list (O0O00O0O00O00O0OO )#line:405
        if not ds .main ().check_docker_program ():#line:406
            OOO0O000OO000O0OO ['container_list']=list ()#line:407
            return public .returnMsg (True ,OOO0O000OO000O0OO )#line:408
        OO0O000OO0O000OOO =OOOOO0O0OO0OO0OOO .docker_client (O0O00O0O00O00O0OO .url )#line:409
        if not OO0O000OO0O000OOO :#line:410
            return public .returnMsg (True ,OOO0O000OO000O0OO )#line:412
        O0O0OOOOOOOO00OOO =OO0O000OO0O000OOO .containers #line:413
        O00O0OO0O0OO0O000 =OOOOO0O0OO0OO0OOO .get_container_attr (O0O0OOOOOOOO00OOO )#line:414
        OOO00OO0OO0OO0OO0 =list ()#line:416
        for OO0O0OOOOO00OO0O0 in O00O0OO0O0OO0O000 :#line:417
            OOO0OOOO0OO000OOO =dp .sql ("cpu_stats").where ("container_id=?",(OO0O0OOOOO00OO0O0 ["Id"],)).select ()#line:418
            if OOO0OOOO0OO000OOO and isinstance (OOO0OOOO0OO000OOO ,list ):#line:419
                OOO0OOOO0OO000OOO =OOO0OOOO0OO000OOO [-1 ]['cpu_usage']#line:420
            else :#line:421
                OOO0OOOO0OO000OOO ="0.0"#line:422
            OOOO0OO0000O000O0 ={"id":OO0O0OOOOO00OO0O0 ["Id"],"name":OO0O0OOOOO00OO0O0 ['Name'].replace ("/",""),"status":OO0O0OOOOO00OO0O0 ["State"]["Status"],"image":OO0O0OOOOO00OO0O0 ["Config"]["Image"],"time":OO0O0OOOOO00OO0O0 ["Created"],"merged":OOOOO0O0OO0OO0OOO .get_container_path (OO0O0OOOOO00OO0O0 ),"ip":OOOOO0O0OO0OO0OOO .get_container_ip (OO0O0OOOOO00OO0O0 ["NetworkSettings"]['Networks']),"ports":OO0O0OOOOO00OO0O0 ["NetworkSettings"]["Ports"],"detail":OO0O0OOOOO00OO0O0 ,"cpu_usage":OOO0OOOO0OO000OOO if OO0O0OOOOO00OO0O0 ["State"]["Status"]=="running"else ""}#line:434
            OOO00OO0OO0OO0OO0 .append (OOOO0OO0000O000O0 )#line:435
        OOO0O000OO000O0OO ['container_list']=OOO00OO0OO0OO0OO0 #line:436
        return public .returnMsg (True ,OOO0O000OO000O0OO )#line:437
    def get_container_attr (OOO0O0000OO0OOOOO ,O0O0OO0OOO00O000O ):#line:440
        O0O00O0OO00OOOOO0 =O0O0OO0OOO00O000O .list (all =True )#line:441
        return [OO0O0OO000OOOOOOO .attrs for OO0O0OO000OOOOOOO in O0O00O0OO00OOOOO0 ]#line:442
    def get_logs (O0OO00OO0OO0O0OO0 ,OOO0O0O0000O0O00O ):#line:445
        ""#line:451
        try :#line:452
            OO0OO0O0O00000O0O =O0OO00OO0OO0O0OO0 .docker_client (OOO0O0O0000O0O00O .url ).containers .get (OOO0O0O0000O0O00O .id )#line:453
            O00OO0OO00OOO0O0O =OO0OO0O0O00000O0O .logs ().decode ()#line:454
            return public .returnMsg (True ,O00OO0OO00OOO0O0O )#line:455
        except docker .errors .APIError as O0OO00O00O000OO00 :#line:456
            if "configured logging driver does not support reading"in str (O0OO00O00O000OO00 ):#line:457
                return public .returnMsg (False ,"该容器没有日志文件！")#line:458
    # 获取容器配置文件