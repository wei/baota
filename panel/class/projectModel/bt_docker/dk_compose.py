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
import time #line:15
import projectModel .bt_docker .dk_public as dp #line:16
import projectModel .bt_docker .dk_container as dc #line:17
import projectModel .bt_docker .dk_setup as ds #line:18
import json #line:19
class main :#line:22
    compose_path ="{}/data/compose".format (public .get_panel_path ())#line:23
    __OOO00OO0OO00OO0O0 ="/tmp/dockertmp.log"#line:24
    def check_conf (OO00OOOO00O00O0O0 ,OO00OO00OOOO00000 ):#line:27
        OO00000O0OO0OO0O0 ="/usr/bin/docker-compose -f {} config".format (OO00OO00OOOO00000 )#line:28
        O000OOOOO0O0O0O0O ,OOOO0O0000OOO0O00 =public .ExecShell (OO00000O0OO0OO0O0 )#line:29
        if OOOO0O0000OOO0O00 :#line:30
            return public .returnMsg (False ,"验证失败: {}".format (OOOO0O0000OOO0O00 ))#line:31
        return public .returnMsg (True ,"验证通过！")#line:32
    def add_template_gui (OO0OO00000000OOO0 ,O00O0OOOO000O00O0 ):#line:35
        ""#line:69
        import yaml #line:70
        O000OO0O0OO0O0O0O ="{}/template".format (OO0OO00000000OOO0 .compose_path )#line:71
        O0000O0O0O0OO00O0 ="{}/{}.yaml".format (O000OO0O0OO0O0O0O ,O00O0OOOO000O00O0 .name )#line:72
        if not os .path .exists (O000OO0O0OO0O0O0O ):#line:73
            os .makedirs (O000OO0O0OO0O0O0O )#line:74
        OO000000OO0000OO0 =json .loads (O00O0OOOO000O00O0 .data )#line:75
        yaml .dump (OO000000OO0000OO0 ,O0000O0O0O0OO00O0 )#line:76
    def get_template_kw (OO0OO0OO00OO00OO0 ,OO00O0000O0000O0O ):#line:78
        O0O0OO0OO0000O0OO ={"version":"","services":{"server_name_str":{"build":{"context":"str","dockerfile":"str","args":[],"cache_from":[],"labels":[],"network":"str","shm_size":"str","target":"str"},"cap_add":"","cap_drop":"","cgroup_parent":"str","command":"str","configs":{"my_config_str":[]},"container_name":"str","credential_spec":{"file":"str","registry":"str"},"depends_on":[],"deploy":{"endpoint_mode":"str","labels":{"key":"value"},"mode":"str","placement":[{"key":"value"}],"max_replicas_per_node":"int","replicas":"int","resources":{"limits":{"cpus":"str","memory":"str",},"reservations":{"cpus":"str","memory":"str",},"restart_policy":{"condition":"str","delay":"str","max_attempts":"int","window":"str"}}}}}}#line:134
    def add_template (O0O0000OOOOOOO0OO ,OOOO0OOO000O0O00O ):#line:137
        ""#line:145
        O0O0O0OO0000OO00O =O0O0000OOOOOOO0OO .template_list (OOOO0OOO000O0O00O )['msg']['template']#line:146
        for O00O0O0O00O00000O in O0O0O0OO0000OO00O :#line:147
            if OOOO0OOO000O0O00O .name ==O00O0O0O00O00000O ['name']:#line:148
                return public .returnMsg (False ,"此模板名已经存在！")#line:149
        OOO0O0000O0O00O0O ="{}/{}/template".format (O0O0000OOOOOOO0OO .compose_path ,OOOO0OOO000O0O00O .name )#line:150
        O000OO00OO0O0O000 ="{}/{}.yaml".format (OOO0O0000O0O00O0O ,OOOO0OOO000O0O00O .name )#line:151
        if not os .path .exists (OOO0O0000O0O00O0O ):#line:152
            os .makedirs (OOO0O0000O0O00O0O )#line:153
        public .writeFile (O000OO00OO0O0O000 ,OOOO0OOO000O0O00O .data )#line:154
        O000O00000O00OO00 =O0O0000OOOOOOO0OO .check_conf (O000OO00OO0O0O000 )#line:155
        if not O000O00000O00OO00 ['status']:#line:156
            if os .path .exists (O000OO00OO0O0O000 ):#line:157
                os .remove (O000OO00OO0O0O000 )#line:158
            return O000O00000O00OO00 #line:160
        OO0OO0OO0O000OOOO ={"name":OOOO0OOO000O0O00O .name ,"remark":OOOO0OOO000O0O00O .remark ,"path":O000OO00OO0O0O000 }#line:165
        dp .sql ("templates").insert (OO0OO0OO0O000OOOO )#line:166
        dp .write_log ("添加模板【{}】成功！".format (OOOO0OOO000O0O00O .name ))#line:167
        public .set_module_logs ('docker','add_template',1 )#line:168
        return public .returnMsg (True ,"模板添加成功！")#line:169
    def edit_template (OO0O000O0OOOOO0O0 ,OOOO0OO0OOO0OOO00 ):#line:171
        ""#line:178
        O0OO0000OO0O00OOO =dp .sql ("templates").where ("id=?",(OOOO0OO0OOO0OOO00 .id ,)).find ()#line:179
        if not O0OO0000OO0O00OOO :#line:180
            return public .returnMsg (False ,"没有找到这个模板！")#line:181
        public .writeFile (O0OO0000OO0O00OOO ['path'],OOOO0OO0OOO0OOO00 .data )#line:182
        O0O0O0OOOO00O0000 =OO0O000O0OOOOO0O0 .check_conf (O0OO0000OO0O00OOO ['path'])#line:183
        if not O0O0O0OOOO00O0000 ['status']:#line:184
            return O0O0O0OOOO00O0000 #line:185
        OO00O00OOO0O0O000 ={"name":O0OO0000OO0O00OOO ['name'],"remark":OOOO0OO0OOO0OOO00 .remark ,"path":O0OO0000OO0O00OOO ['path']}#line:190
        dp .sql ("templates").where ("id=?",(OOOO0OO0OOO0OOO00 .id ,)).update (OO00O00OOO0O0O000 )#line:191
        dp .write_log ("编辑模板【{}】成功！".format (O0OO0000OO0O00OOO ['name']))#line:192
        return public .returnMsg (True ,"修改模板成功！")#line:193
    def get_template (OO000000OO0OOO00O ,OOOOO0OO00O00OO0O ):#line:195
        ""#line:200
        OO0OOO0000000OOOO =dp .sql ("templates").where ("id=?",(OOOOO0OO00O00OO0O .id ,)).find ()#line:201
        if not OO0OOO0000000OOOO :#line:202
            return public .returnMsg (False ,"没有找到这个模板！")#line:203
        return public .returnMsg (True ,public .readFile (OO0OOO0000000OOOO ['path']))#line:204
    def template_list (OOO0O0000OO000O0O ,OO0O00OOOOOO0O0O0 ):#line:206
        ""#line:211
        import projectModel .bt_docker .dk_setup as ds #line:212
        O000O0O0OOOOO0OO0 =ds .main ()#line:213
        OO00OOO0O00OO0O0O =dp .sql ("templates").select ()[::-1 ]#line:214
        if not isinstance (OO00OOO0O00OO0O0O ,list ):#line:215
            OO00OOO0O00OO0O0O =[]#line:216
        OO0000000O00O0O00 ={"template":OO00OOO0O00OO0O0O ,"installed":O000O0O0OOOOO0OO0 .check_docker_program (),"service_status":O000O0O0OOOOO0OO0 .get_service_status ()}#line:221
        return public .returnMsg (True ,OO0000000O00O0O00 )#line:222
    def remove_template (O0OOOOOO00O0O0000 ,O00O000OOO0OOOOOO ):#line:224
        ""#line:230
        O0O00O0O00OOO0O00 =dp .sql ("templates").where ("id=?",(O00O000OOO0OOOOOO .template_id ,)).find ()#line:231
        if not O0O00O0O00OOO0O00 :#line:232
            return public .returnMsg (False ,"没有找到这个模板！")#line:233
        if os .path .exists (O0O00O0O00OOO0O00 ['path']):#line:234
            os .remove (O0O00O0O00OOO0O00 ['path'])#line:235
        dp .sql ("templates").delete (id =O00O000OOO0OOOOOO .template_id )#line:236
        dp .write_log ("删除模板【{}】成功！".format (O0O00O0O00OOO0O00 ['name']))#line:237
        return public .returnMsg (True ,"删除成功！")#line:238
    def edit_project_remark (OO0OO0O00O0O0O0O0 ,O0O0O0O000OO00OOO ):#line:240
        ""#line:247
        OOOOOO0O0O0OOO0O0 =dp .sql ("stacks").where ("id=?",(O0O0O0O000OO00OOO .project_id ,)).find ()#line:248
        if not OOOOOO0O0O0OOO0O0 :#line:249
            return public .returnMsg (False ,"没有找到该项目！")#line:250
        OO00OO00O0O0OO000 ={"remark":O0O0O0O000OO00OOO .remark }#line:253
        dp .write_log ("修改项目【{}】备注【{}】为【{}】成功！".format (OOOOOO0O0O0OOO0O0 ['name'],OOOOOO0O0O0OOO0O0 ['remark'],O0O0O0O000OO00OOO .remark ))#line:254
        dp .sql ("stacks").where ("id=?",(O0O0O0O000OO00OOO .project_id ,)).update (OO00OO00O0O0OO000 )#line:255
    def edit_template_remark (OO00OO000O0OO0000 ,O00OO00OO0OOOO000 ):#line:257
        ""#line:264
        OOOO0OO0OO0O0000O =dp .sql ("templates").where ("id=?",(O00OO00OO0OOOO000 .templates_id ,)).find ()#line:265
        if not OOOO0OO0OO0O0000O :#line:266
            return public .returnMsg (False ,"没有找到该模板！")#line:267
        O0OOO0000000O0O0O ={"remark":O00OO00OO0OOOO000 .remark }#line:270
        dp .write_log ("修改模板【{}】备注【{}】为【{}】成功！".format (OOOO0OO0OO0O0000O ['name'],OOOO0OO0OO0O0000O ['remark'],O00OO00OO0OOOO000 .remark ))#line:271
        dp .sql ("templates").where ("id=?",(O00OO00OO0OOOO000 .templates_id ,)).update (O0OOO0000000O0O0O )#line:272
    def create_project_in_path (OOOO000O0OOO00O0O ,OO00OO00OO00OO0O0 ,OO0O0OO00OOOOOOO0 ):#line:274
        O000O00OOO0OO0000 ="cd {} && /usr/bin/docker-compose -p {} up -d &> {}".format ("/".join (OO0O0OO00OOOOOOO0 .split ("/")[:-1 ]),OO00OO00OO00OO0O0 ,OOOO000O0OOO00O0O .__OOO00OO0OO00OO0O0 )#line:275
        public .ExecShell (O000O00OOO0OO0000 )#line:276
    def create_project_in_file (O00O000O000O0O000 ,O0OO0000O0O0O000O ,O00000OO00O00OO0O ):#line:278
        OOO0O0000000OO0O0 ="{}/{}".format (O00O000O000O0O000 .compose_path ,O0OO0000O0O0O000O )#line:279
        O0OO0O00000O0O000 ="{}/docker-compose.yaml".format (OOO0O0000000OO0O0 )#line:280
        if not os .path .exists (OOO0O0000000OO0O0 ):#line:281
            os .makedirs (OOO0O0000000OO0O0 )#line:282
        O00OOO0O0O000O000 =public .readFile (O00000OO00O00OO0O )#line:283
        public .writeFile (O0OO0O00000O0O000 ,O00OOO0O0O000O000 )#line:284
        O0OO000OOOO0000O0 ="/usr/bin/docker-compose -p {} -f {} up -d &> {}".format (O0OO0000O0O0O000O ,O0OO0O00000O0O000 ,O00O000O000O0O000 .__OOO00OO0OO00OO0O0 )#line:285
        public .ExecShell (O0OO000OOOO0000O0 )#line:286
    def check_project_container_name (OO000000O0OOOO0OO ,OOOOO00OOO000OO00 ,OOO00O0O0OOO00OOO ):#line:288
        ""#line:292
        import re #line:293
        import projectModel .bt_docker .dk_container as dc #line:294
        O000O0O00000OOOO0 =[]#line:295
        O0O000OO00000OO00 =re .findall ("container_name\s*:\s*[\"\']+(.*)[\'\"]",OOOOO00OOO000OO00 )#line:296
        OOO00OOOO0O000000 =dc .main ().get_list (OOO00O0O0OOO00OOO )#line:297
        if not OOO00OOOO0O000000 ["status"]:#line:298
            return public .returnMsg (False ,"获取容器列表出错了！")#line:299
        OOO00OOOO0O000000 =OOO00OOOO0O000000 ['msg']['container_list']#line:300
        for OO0OO00000OO00O00 in OOO00OOOO0O000000 :#line:301
            if OO0OO00000OO00O00 ['name']in O0O000OO00000OO00 :#line:302
                O000O0O00000OOOO0 .append (OO0OO00000OO00O00 ['name'])#line:303
        if O000O0O00000OOOO0 :#line:304
            return public .returnMsg (False ,"模板中的容器名:<br>【{}】已经存在！".format (", ".join (O000O0O00000OOOO0 )))#line:305
        OOOOOO00O0000O00O ="(\d+):\d+"#line:307
        OOOO00OO000O0O000 =re .findall (OOOOOO00O0000O00O ,OOOOO00OOO000OO00 )#line:308
        for OO00O00O0OO0O0OOO in OOOO00OO000O0O000 :#line:309
            if dp .check_socket (OO00O00O0OO0O0OOO ):#line:310
                return public .returnMsg (False ,"模板中的端口【{}】已经在使用中，请修改模板中的服务端端口！".format (OO00O00O0OO0O0OOO ))#line:311
    def create (OO0O00OO0O0O0OOO0 ,O00O00OO0OOO0O0O0 ):#line:314
        ""#line:321
        O0OOO0OOOO0000O00 =public .md5 (O00O00OO0OOO0O0O0 .project_name )#line:322
        O000OO0OOOOO0OOOO =dp .sql ("templates").where ("id=?",(O00O00OO0OOO0O0O0 .template_id ,)).find ()#line:323
        if not os .path .exists (O000OO0OOOOO0OOOO ['path']):#line:324
            return public .returnMsg (False ,"没有找到模板文件")#line:325
        O00OO00OOOOOOOO00 =OO0O00OO0O0O0OOO0 .check_project_container_name (public .readFile (O000OO0OOOOO0OOOO ['path']),O00O00OO0OOO0O0O0 )#line:326
        if O00OO00OOOOOOOO00 :#line:327
            return O00OO00OOOOOOOO00 #line:328
        O0O00O0O0O0OO00O0 =dp .sql ("stacks").where ("name=?",(O0OOO0OOOO0000O00 )).find ()#line:329
        if not O0O00O0O0O0OO00O0 :#line:330
            OOO0O0OOOOOOOOOOO ={"name":O00O00OO0OOO0O0O0 .project_name ,"status":"1","path":O000OO0OOOOO0OOOO ['path'],"template_id":O00O00OO0OOO0O0O0 .template_id ,"time":time .time (),"remark":O00O00OO0OOO0O0O0 .remark }#line:338
            dp .sql ("stacks").insert (OOO0O0OOOOOOOOOOO )#line:339
        else :#line:340
            return public .returnMsg (False ,"此项目名已经存在！")#line:341
        if O000OO0OOOOO0OOOO ['add_in_path']==1 :#line:342
            OO0O00OO0O0O0OOO0 .create_project_in_path (O0OOO0OOOO0000O00 ,O000OO0OOOOO0OOOO ['path'])#line:346
        else :#line:347
            OO0O00OO0O0O0OOO0 .create_project_in_file (O0OOO0OOOO0000O00 ,O000OO0OOOOO0OOOO ['path'])#line:351
        dp .write_log ("项目【{}】部署成功！".format (O0OOO0OOOO0000O00 ))#line:352
        public .set_module_logs ('docker','add_project',1 )#line:353
        return public .returnMsg (True ,"部署成功！")#line:354
    def compose_project_list (OOOO0OO0O000OO00O ,OOO00O0OOOO0O0000 ):#line:370
        ""#line:373
        OOO00O0OOOO0O0000 .url ="unix:///var/run/docker.sock"#line:374
        OOOOOOO00O000OOO0 =dc .main ().get_list (OOO00O0OOOO0O0000 )#line:375
        if not OOOOOOO00O000OOO0 ['status']:#line:376
            return public .returnMsg (False ,"获取容器失败,可能是docker服务未启动！")#line:377
        if not OOOOOOO00O000OOO0 ['msg']['service_status']or not OOOOOOO00O000OOO0 ['msg']['installed']:#line:378
            O0O00OOOO0O0O0000 ={"project_list":[],"template":[],"service_status":OOOOOOO00O000OOO0 ['msg']['service_status'],"installed":OOOOOOO00O000OOO0 ['msg']['installed']}#line:384
            return public .returnMsg (True ,O0O00OOOO0O0O0000 )#line:385
        O0O0OOO0000000OOO =dp .sql ("stacks").select ()#line:386
        if isinstance (O0O0OOO0000000OOO ,list ):#line:387
            for OO0OO00O000O0OOOO in O0O0OOO0000000OOO :#line:388
                OOO0000O0O000OO0O =[]#line:389
                for OO0O0OOOOOOO00O00 in OOOOOOO00O000OOO0 ['msg']["container_list"]:#line:390
                    try :#line:391
                        if 'com.docker.compose.project'not in OO0O0OOOOOOO00O00 ["detail"]['Config']['Labels']:#line:392
                            continue #line:393
                    except :#line:394
                        continue #line:395
                    if OO0O0OOOOOOO00O00 ["detail"]['Config']['Labels']['com.docker.compose.project']==public .md5 (OO0OO00O000O0OOOO ['name']):#line:396
                        OOO0000O0O000OO0O .append (OO0O0OOOOOOO00O00 )#line:397
                O00000000OO0O0OOO =OOO0000O0O000OO0O #line:398
                OO0OO00O000O0OOOO ['container']=O00000000OO0O0OOO #line:399
        else :#line:400
            O0O0OOO0000000OOO =[]#line:401
        O0000O0O000O0O0O0 =OOOO0OO0O000OO00O .template_list (OOO00O0OOOO0O0000 )#line:402
        if not O0000O0O000O0O0O0 ['status']:#line:403
            O0000O0O000O0O0O0 =list ()#line:404
        else :#line:405
            O0000O0O000O0O0O0 =O0000O0O000O0O0O0 ['msg']['template']#line:406
        OOOOO0000O0000000 =ds .main ()#line:407
        O0O00OOOO0O0O0000 ={"project_list":O0O0OOO0000000OOO ,"template":O0000O0O000O0O0O0 ,"service_status":OOOOO0000O0000000 .get_service_status (),"installed":OOOOO0000O0000000 .check_docker_program ()}#line:413
        return public .returnMsg (True ,O0O00OOOO0O0O0000 )#line:414
    def remove (OO0OOOO00000O0000 ,OO00O0O000OOOO0OO ):#line:417
        ""#line:422
        O0000000OO00O00OO =dp .sql ("stacks").where ("id=?",(OO00O0O000OOOO0OO .project_id ,)).find ()#line:423
        if not O0000000OO00O00OO :#line:424
            return public .returnMsg (True ,"未找到该项目配置！")#line:425
        OO0O0O00OO0O0000O ="/usr/bin/docker-compose -p {} -f {} down &> {}".format (public .md5 (O0000000OO00O00OO ['name']),O0000000OO00O00OO ['path'],OO0OOOO00000O0000 .__OOO00OO0OO00OO0O0 )#line:426
        O00O0OO0OO0OOOO0O ,O0O000OOOO0OO0OOO =public .ExecShell (OO0O0O00OO0O0000O )#line:427
        dp .sql ("stacks").delete (id =OO00O0O000OOOO0OO .project_id )#line:428
        dp .write_log ("删除项目【{}】成功！".format (O0000000OO00O00OO ['name']))#line:429
        return public .returnMsg (True ,"删除成功！")#line:430
    def stop (OOO0OO0O0O0OO0O0O ,O0O00000O000O0O00 ):#line:433
        ""#line:439
        OOO0O0000O0O00000 =dp .sql ("stacks").where ("id=?",(O0O00000O000O0O00 .project_id ,)).find ()#line:440
        if not OOO0O0000O0O00000 :#line:441
            return public .returnMsg (True ,"未找到该项目配置！")#line:442
        O0O0OO000OOO00O0O ="/usr/bin/docker-compose -p {} -f {} stop &> {}".format (public .md5 (OOO0O0000O0O00000 ['name']),OOO0O0000O0O00000 ['path'],OOO0OO0O0O0OO0O0O .__OOO00OO0OO00OO0O0 )#line:444
        OOOO0O000O00O00OO ,OOOO00O0000O0000O =public .ExecShell (O0O0OO000OOO00O0O )#line:445
        dp .write_log ("停止项目【{}】成功！".format (OOO0O0000O0O00000 ['name']))#line:446
        return public .returnMsg (True ,"设置成功！")#line:447
    def start (OO00O0OO00O0O00O0 ,OOO00O0O00OO0O000 ):#line:450
        ""#line:455
        O000000O0OO000000 =dp .sql ("stacks").where ("id=?",(OOO00O0O00OO0O000 .project_id ,)).find ()#line:456
        if not O000000O0OO000000 :#line:457
            return public .returnMsg (False ,"未找到该项目配置！")#line:458
        O00OOOOOO00OO000O ="/usr/bin/docker-compose -p {} -f {} start > {}".format (public .md5 (O000000O0OO000000 ['name']),O000000O0OO000000 ['path'],OO00O0OO00O0O00O0 .__OOO00OO0OO00OO0O0 )#line:459
        O00O00O0O0O0O00O0 ,OO00O000O0O000O0O =public .ExecShell (O00OOOOOO00OO000O )#line:460
        dp .write_log ("启动项目【{}】成功！".format (O000000O0OO000000 ['name']))#line:461
        return public .returnMsg (True ,"设置成功！")#line:462
    def restart (OOO0O000OO00OOO00 ,OOO0OOOOO0OO000OO ):#line:465
        ""#line:470
        O000OO0O00000OO0O =dp .sql ("stacks").where ("id=?",(OOO0OOOOO0OO000OO .project_id ,)).find ()#line:471
        if not O000OO0O00000OO0O :#line:472
            return public .returnMsg (True ,"未找到该项目配置！")#line:473
        OO000O0O000OO00OO ="/usr/bin/docker-compose -p {} -f {} restart &> {}".format (public .md5 (O000OO0O00000OO0O ['name']),O000OO0O00000OO0O ['path'],OOO0O000OO00OOO00 .__OOO00OO0OO00OO0O0 )#line:474
        OOO0OO00O0OOO0O0O ,OOOO00OO00OOO00O0 =public .ExecShell (OO000O0O000OO00OO )#line:475
        dp .write_log ("重启项目【{}】成功！".format (O000OO0O00000OO0O ['name']))#line:476
        return public .returnMsg (True ,"设置成功！")#line:477
    def pull (OO0O0O00OO0000O00 ,O0O0OOOOOO000O0O0 ):#line:480
        ""#line:485
        OO00O00O00OOO000O =dp .sql ("templates").where ("id=?",(O0O0OOOOOO000O0O0 .template_id ,)).find ()#line:486
        if not OO00O00O00OOO000O :#line:487
            return public .returnMsg (True ,"未找到该模板！")#line:488
        OO0OO00000OO000OO ="/usr/bin/docker-compose -p {} -f {} pull &> {}".format (OO00O00O00OOO000O ['name'],OO00O00O00OOO000O ['path'],OO0O0O00OO0000O00 .__OOO00OO0OO00OO0O0 )#line:489
        OOO00OO0000OO00OO ,OO0O0O00000000OO0 =public .ExecShell (OO0OO00000OO000OO )#line:490
        dp .write_log ("拉取模板【{}】的镜像成功！".format (OO00O00O00OOO000O ['name']))#line:491
        return public .returnMsg (True ,"拉取成功！")#line:492
    def pause (O0O00O0O0O0O0O00O ,OOOO0OOO0O00O0OOO ):#line:495
        ""#line:500
        O00000O0000OOO0O0 =dp .sql ("stacks").where ("id=?",(OOOO0OOO0O00O0OOO .project_id ,)).find ()#line:501
        if not O00000O0000OOO0O0 :#line:502
            return public .returnMsg (True ,"未找到该项目配置！")#line:503
        O00OO0000OOOO0O00 ="/usr/bin/docker-compose -p {} -f {} pause &> {}".format (public .md5 (O00000O0000OOO0O0 ['name']),O00000O0000OOO0O0 ['path'],O0O00O0O0O0O0O00O .__OOO00OO0OO00OO0O0 )#line:504
        OO0OO0O0OOO00O000 ,OOO0O0O0OOO00OO00 =public .ExecShell (O00OO0000OOOO0O00 )#line:505
        dp .write_log ("暂停【{}】成功！".format (O00000O0000OOO0O0 ['name']))#line:506
        return public .returnMsg (True ,"设置成功！")#line:507
    def unpause (OO0O0OO0OO0OOOO00 ,OO0OO0O0O00O0OO0O ):#line:510
        ""#line:515
        O0OOO0OOO00O0OOO0 =dp .sql ("stacks").where ("id=?",(OO0OO0O0O00O0OO0O .project_id ,)).find ()#line:516
        if not O0OOO0OOO00O0OOO0 :#line:517
            return public .returnMsg (True ,"未找到该项目配置！")#line:518
        OOOO00OO00O00O00O ="/usr/bin/docker-compose -p {} -f {} unpause &> {}".format (public .md5 (O0OOO0OOO00O0OOO0 ['name']),O0OOO0OOO00O0OOO0 ['path'],OO0O0OO0OO0OOOO00 .__OOO00OO0OO00OO0O0 )#line:519
        OOOOO00O0OO0OO000 ,OO0O0O000OOO0OOO0 =public .ExecShell (OOOO00OO00O00O00O )#line:520
        dp .write_log ("取消暂停项目【{}】成功！".format (O0OOO0OOO00O0OOO0 ['name']))#line:521
        return public .returnMsg (True ,"设置成功！")#line:522
    def scan_compose_file (OO0O0O0O000O0O0O0 ,O0OOO0OO000000O00 ,O0OO00O0O0000O00O ):#line:525
        ""#line:531
        O000OOO0OOO0OO000 =os .listdir (O0OOO0OO000000O00 )#line:532
        for O0OOO0O00O00OO0O0 in O000OOO0OOO0OO000 :#line:533
            O00000000OO000OOO =os .path .join (O0OOO0OO000000O00 ,O0OOO0O00O00OO0O0 )#line:534
            if os .path .isdir (O00000000OO000OOO ):#line:536
                OO0O0O0O000O0O0O0 .scan_compose_file (O00000000OO000OOO ,O0OO00O0O0000O00O )#line:537
            else :#line:538
                if O0OOO0O00O00OO0O0 =="docker-compose.yaml"or O0OOO0O00O00OO0O0 =="docker-compose.yam"or O0OOO0O00O00OO0O0 =="docker-compose.yml":#line:539
                    if "/www/server/panel/data/compose"in O00000000OO000OOO :#line:540
                        continue #line:541
                    O0OO00O0O0000O00O .append (O00000000OO000OOO )#line:542
        return O0OO00O0O0000O00O #line:543
    def get_compose_project (O000O0OOO0000OOO0 ,O000OO0O0OOO0O00O ):#line:546
        ""#line:552
        O000O00OO0OOOOOOO =list ()#line:553
        if O000OO0O0OOO0O00O .path =="/":#line:554
            return public .returnMsg (False ,"不能从根目录开始扫描！")#line:555
        if O000OO0O0OOO0O00O .path [-1 ]=="/":#line:556
            O000OO0O0OOO0O00O .path =O000OO0O0OOO0O00O .path [:-1 ]#line:557
        if str (O000OO0O0OOO0O00O .sub_dir )=="1":#line:558
            O00OOOO00O0OOO00O =O000O0OOO0000OOO0 .scan_compose_file (O000OO0O0OOO0O00O .path ,O000O00OO0OOOOOOO )#line:559
            if not O00OOOO00O0OOO00O :#line:560
                O00OOOO00O0OOO00O =[]#line:561
            else :#line:562
                O0OO0O00000OOO0OO =list ()#line:563
                for OOO0OO00O0O0O00O0 in O00OOOO00O0OOO00O :#line:564
                    O0OO0O00000OOO0OO .append ({"project_name":OOO0OO00O0O0O00O0 .split ("/")[-2 ],"conf_file":"/".join (OOO0OO00O0O0O00O0 .split ("/")),"remark":"通过目录添加"})#line:571
                O00OOOO00O0OOO00O =O0OO0O00000OOO0OO #line:572
        else :#line:573
            OO0O00OOO0OO000O0 ="{}/docker-compose.yaml".format (O000OO0O0OOO0O00O .path )#line:574
            O0O0O0O00O0O0OOO0 ="{}/docker-compose.yam".format (O000OO0O0OOO0O00O .path )#line:575
            if os .path .exists (OO0O00OOO0OO000O0 ):#line:576
                O00OOOO00O0OOO00O =[{"project_name":O000OO0O0OOO0O00O .path .split ("/")[-1 ],"conf_file":OO0O00OOO0OO000O0 ,"remark":"通过目录添加"}]#line:581
            elif os .path .exists (O0O0O0O00O0O0OOO0 ):#line:582
                O00OOOO00O0OOO00O =[{"project_name":O000OO0O0OOO0O00O .path .split ("/")[-1 ],"conf_file":O0O0O0O00O0O0OOO0 ,"remark":"通过目录添加"}]#line:587
            else :#line:588
                O00OOOO00O0OOO00O =list ()#line:589
        return O00OOOO00O0OOO00O #line:591
    def add_template_in_path (OOOOOOO0O000O000O ,OOOO0000O0OO00000 ):#line:594
        ""#line:599
        OOOO0O00OOOO0O00O =dict ()#line:600
        O0O0OOOO00O000O00 =dict ()#line:601
        for OO0O000O0O00000O0 in OOOO0000O0OO00000 .template_list :#line:602
            O0OOO00OOOOOOO0OO =OO0O000O0O00000O0 ['conf_file']#line:603
            O0OOO00OOOO0000O0 =OO0O000O0O00000O0 ['project_name']#line:604
            OOO0OOO0OO0000O00 =OO0O000O0O00000O0 ['remark']#line:605
            OO000O0OO000O00O0 =OOOOOOO0O000O000O .template_list (OOOO0000O0OO00000 )['msg']['template']#line:606
            for OO00O0000O00000OO in OO000O0OO000O00O0 :#line:607
                if O0OOO00OOOO0000O0 ==OO00O0000O00000OO ['name']:#line:608
                    OOOO0O00OOOO0O00O [O0OOO00OOOO0000O0 ]="模板已经存在！"#line:609
                    continue #line:610
            if not os .path .exists (O0OOO00OOOOOOO0OO ):#line:612
                OOOO0O00OOOO0O00O [O0OOO00OOOO0000O0 ]="没有找到该模板！"#line:613
                continue #line:614
            O00OOO00O0OOO0O0O =OOOOOOO0O000O000O .check_conf (O0OOO00OOOOOOO0OO )#line:616
            if not O00OOO00O0OOO0O0O ['status']:#line:617
                OOOO0O00OOOO0O00O [O0OOO00OOOO0000O0 ]="模板验证失败，可能是格式错误！"#line:618
                continue #line:619
            O00OO0OO0O00OO0O0 ={"name":O0OOO00OOOO0000O0 ,"remark":OOO0OOO0OO0000O00 ,"path":O0OOO00OOOOOOO0OO ,"add_in_path":1 }#line:626
            print (O00OO0OO0O00OO0O0 )#line:627
            dp .sql ("templates").insert (O00OO0OO0O00OO0O0 )#line:628
            O0O0OOOO00O000O00 [O0OOO00OOOO0000O0 ]="模板添加成功！"#line:629
        print (OOOO0O00OOOO0O00O )#line:631
        for OO00O0000O00000OO in OOOO0O00OOOO0O00O :#line:632
            if OO00O0000O00000OO in O0O0OOOO00O000O00 :#line:633
                del (O0O0OOOO00O000O00 [OO00O0000O00000OO ])#line:634
            else :#line:635
                dp .write_log ("从路径中添加模板【{}】成功！".format (OO00O0000O00000OO ))#line:636
        if not OOOO0O00OOOO0O00O and O0O0OOOO00O000O00 :#line:637
            return {'status':True ,'msg':'添加模板成功： 【{}】'.format (','.join (O0O0OOOO00O000O00 ))}#line:638
        elif not O0O0OOOO00O000O00 and OOOO0O00OOOO0O00O :#line:639
            return {'status':True ,'msg':'添加模板失败：模板名已经存在或格式验证错误【{}】'.format (','.join (OOOO0O00OOOO0O00O ))}#line:640
        return {'status':True ,'msg':'添加模板成功： 【{}】<br>添加模板失败：模板名已经存在或格式验证错误【{}】'.format (','.join (O0O0OOOO00O000O00 ),','.join (OOOO0O00OOOO0O00O ))}#line:641
