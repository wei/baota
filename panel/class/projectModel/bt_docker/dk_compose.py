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
    __OOO0000OOOO00000O ="/tmp/dockertmp.log"#line:24
    def check_conf (OO00OOO0O0O0O0O00 ,OO00O0O00OOO00000 ):#line:27
        OOOOOOOOO0O0OOO00 ="/usr/bin/docker-compose -f {} config".format (OO00O0O00OOO00000 )#line:28
        OOO00O000O00O00O0 ,O0OOOO00O00O0OO0O =public .ExecShell (OOOOOOOOO0O0OOO00 )#line:29
        if O0OOOO00O00O0OO0O :#line:30
            return public .returnMsg (False ,"检测失败: {}".format (O0OOOO00O00O0OO0O ))#line:31
        return public .returnMsg (True ,"检测通过!")#line:32
    def add_template_gui (OO0OO0OO000OO000O ,OOOO0OO00OOO0O0O0 ):#line:35
        ""#line:69
        import yaml #line:70
        O0OO000OO000OO00O ="{}/template".format (OO0OO0OO000OO000O .compose_path )#line:71
        O0000O0O00O0OO000 ="{}/{}.yaml".format (O0OO000OO000OO00O ,OOOO0OO00OOO0O0O0 .name )#line:72
        if not os .path .exists (O0OO000OO000OO00O ):#line:73
            os .makedirs (O0OO000OO000OO00O )#line:74
        O0OO000OOOO0O00O0 =json .loads (OOOO0OO00OOO0O0O0 .data )#line:75
        yaml .dump (O0OO000OOOO0O00O0 ,O0000O0O00O0OO000 )#line:76
    def get_template_kw (O000OOOOO0O00000O ,O0O000O0OOOO00OOO ):#line:78
        O0O0O0OOOO0OO00O0 ={"version":"","services":{"server_name_str":{"build":{"context":"str","dockerfile":"str","args":[],"cache_from":[],"labels":[],"network":"str","shm_size":"str","target":"str"},"cap_add":"","cap_drop":"","cgroup_parent":"str","command":"str","configs":{"my_config_str":[]},"container_name":"str","credential_spec":{"file":"str","registry":"str"},"depends_on":[],"deploy":{"endpoint_mode":"str","labels":{"key":"value"},"mode":"str","placement":[{"key":"value"}],"max_replicas_per_node":"int","replicas":"int","resources":{"limits":{"cpus":"str","memory":"str",},"reservations":{"cpus":"str","memory":"str",},"restart_policy":{"condition":"str","delay":"str","max_attempts":"int","window":"str"}}}}}}#line:134
    def add_template (OOOO0O0O00O00000O ,O0OOO0OO000OO0O00 ):#line:137
        ""#line:145
        import re #line:146
        O0O0O0OOO00OOO000 =O0OOO0OO000OO0O00 .name #line:147
        if not re .search (r"^[\w\.\-]+$",O0O0O0OOO00OOO000 ):#line:148
            return public .returnMsg (False ,"模板名不能包含特殊字符，仅支持字母、数字、下划线、点、中划线")#line:149
        OO00O00OOO00O000O =OOOO0O0O00O00000O .template_list (O0OOO0OO000OO0O00 )['msg']['template']#line:150
        for O0OOOO00O000OO0O0 in OO00O00OOO00O000O :#line:151
            if O0O0O0OOO00OOO000 ==O0OOOO00O000OO0O0 ['name']:#line:152
                return public .returnMsg (False ,"This template name already exists!")#line:153
        OO0OOOOO00O00O00O ="{}/{}/template".format (OOOO0O0O00O00000O .compose_path ,O0O0O0OOO00OOO000 )#line:154
        O0OOOOOO0OOO0O00O ="{}/{}.yaml".format (OO0OOOOO00O00O00O ,O0O0O0OOO00OOO000 )#line:155
        if not os .path .exists (OO0OOOOO00O00O00O ):#line:156
            os .makedirs (OO0OOOOO00O00O00O )#line:157
        public .writeFile (O0OOOOOO0OOO0O00O ,O0OOO0OO000OO0O00 .data )#line:158
        OOOO000OOOOO0O0OO =OOOO0O0O00O00000O .check_conf (O0OOOOOO0OOO0O00O )#line:159
        if not OOOO000OOOOO0O0OO ['status']:#line:160
            if os .path .exists (O0OOOOOO0OOO0O00O ):#line:161
                os .remove (O0OOOOOO0OOO0O00O )#line:162
            return OOOO000OOOOO0O0OO #line:164
        O00OO000OO00OO0O0 ={"name":O0O0O0OOO00OOO000 ,"remark":O0OOO0OO000OO0O00 .remark ,"path":O0OOOOOO0OOO0O00O }#line:169
        dp .sql ("templates").insert (O00OO000OO00OO0O0 )#line:170
        dp .write_log ("Add template [{}] successful!".format (O0O0O0OOO00OOO000 ))#line:171
        public .set_module_logs ('docker','add_template',1 )#line:172
        return public .returnMsg (True ,"模板添加成功!")#line:173
    def edit_template (OOOOO00OOO0OO0000 ,O0O00OO0O0000OO0O ):#line:175
        ""#line:182
        O00O0OO00O0000OOO =dp .sql ("templates").where ("id=?",(O0O00OO0O0000OO0O .id ,)).find ()#line:183
        if not O00O0OO00O0000OOO :#line:184
            return public .returnMsg (False ,"This template was not found!")#line:185
        public .writeFile (O00O0OO00O0000OOO ['path'],O0O00OO0O0000OO0O .data )#line:186
        OO00OOOOO0O00O0OO =OOOOO00OOO0OO0000 .check_conf (O00O0OO00O0000OOO ['path'])#line:187
        if not OO00OOOOO0O00O0OO ['status']:#line:188
            return OO00OOOOO0O00O0OO #line:189
        O000OO000000O0O0O ={"name":O00O0OO00O0000OOO ['name'],"remark":O0O00OO0O0000OO0O .remark ,"path":O00O0OO00O0000OOO ['path']}#line:194
        dp .sql ("templates").where ("id=?",(O0O00OO0O0000OO0O .id ,)).update (O000OO000000O0O0O )#line:195
        dp .write_log ("编辑模板 [{}] 成功!".format (O00O0OO00O0000OOO ['name']))#line:196
        return public .returnMsg (True ,"修改模板成功！")#line:197
    def get_template (OOOOOO0OOO00OOOOO ,OO0OOO0OOO00OOO00 ):#line:199
        ""#line:204
        OOOOO0OOOO000O0OO =dp .sql ("templates").where ("id=?",(OO0OOO0OOO00OOO00 .id ,)).find ()#line:205
        if not OOOOO0OOOO000O0OO :#line:206
            return public .returnMsg (False ,"没有找到此模板!")#line:207
        return public .returnMsg (True ,public .readFile (OOOOO0OOOO000O0OO ['path']))#line:208
    def template_list (O0OOOO00OOO00O0OO ,OO0O0000000OO0OOO ):#line:210
        ""#line:215
        import projectModel .bt_docker .dk_setup as ds #line:216
        O0O00O0O0O0OO00O0 =ds .main ()#line:217
        OOOOO00OO000O000O =dp .sql ("templates").select ()[::-1 ]#line:218
        if not isinstance (OOOOO00OO000O000O ,list ):#line:219
            OOOOO00OO000O000O =[]#line:220
        O00000O0O00000O0O ={"template":OOOOO00OO000O000O ,"installed":O0O00O0O0O0OO00O0 .check_docker_program (),"service_status":O0O00O0O0O0OO00O0 .get_service_status ()}#line:225
        return public .returnMsg (True ,O00000O0O00000O0O )#line:226
    def remove_template (OOO00OO0OO00OOOOO ,O0O0OOOO00O00O0OO ):#line:228
        ""#line:234
        OO00OO00OOO0OO0OO =dp .sql ("templates").where ("id=?",(O0O0OOOO00O00O0OO .template_id ,)).find ()#line:235
        if not OO00OO00OOO0OO0OO :#line:236
            return public .returnMsg (False ,"没有找到此模板!")#line:237
        if os .path .exists (OO00OO00OOO0OO0OO ['path']):#line:238
            os .remove (OO00OO00OOO0OO0OO ['path'])#line:239
        dp .sql ("templates").delete (id =O0O0OOOO00O00O0OO .template_id )#line:240
        dp .write_log ("删除模板 [{}] 成功!".format (OO00OO00OOO0OO0OO ['name']))#line:241
        return public .returnMsg (True ,"删除成功!")#line:242
    def edit_project_remark (OO000OOOOOO000000 ,O0O00OOOO00OOO00O ):#line:244
        ""#line:251
        O0OOO00O000O000OO =dp .sql ("stacks").where ("id=?",(O0O00OOOO00OOO00O .project_id ,)).find ()#line:252
        if not O0OOO00O000O000OO :#line:253
            return public .returnMsg (False ,"The item was not found!")#line:254
        O0OOO000O0O0OO00O ={"remark":O0O00OOOO00OOO00O .remark }#line:257
        dp .write_log ("项目 [{}] 的备注修改成功 [{}] --> [{}]!".format (O0OOO00O000O000OO ['name'],O0OOO00O000O000OO ['remark'],O0O00OOOO00OOO00O .remark ))#line:258
        dp .sql ("stacks").where ("id=?",(O0O00OOOO00OOO00O .project_id ,)).update (O0OOO000O0O0OO00O )#line:259
    def edit_template_remark (OO0O0OOOO0O0OO0OO ,O0O0O0OOO0O00O0OO ):#line:261
        ""#line:268
        OOOO0O000O0OOOOO0 =dp .sql ("templates").where ("id=?",(O0O0O0OOO0O00O0OO .templates_id ,)).find ()#line:269
        if not OOOO0O000O0OOOOO0 :#line:270
            return public .returnMsg (False ,"The template was not found!")#line:271
        OOO0OO0O00OOOOOO0 ={"remark":O0O0O0OOO0O00O0OO .remark }#line:274
        dp .write_log ("修改模板 [{}] 备注成功 [{}] --> [{}]!".format (OOOO0O000O0OOOOO0 ['name'],OOOO0O000O0OOOOO0 ['remark'],O0O0O0OOO0O00O0OO .remark ))#line:275
        dp .sql ("templates").where ("id=?",(O0O0O0OOO0O00O0OO .templates_id ,)).update (OOO0OO0O00OOOOOO0 )#line:276
    def create_project_in_path (O00000O000O00O0OO ,O00O0000OOOOOOO00 ,OOO00OO0O000O0000 ):#line:278
        OO0OOO0OOOO00O0O0 ="cd {} && /usr/bin/docker-compose -p {} up -d &> {}".format ("/".join (OOO00OO0O000O0000 .split ("/")[:-1 ]),O00O0000OOOOOOO00 ,O00000O000O00O0OO .__OOO0000OOOO00000O )#line:279
        public .ExecShell (OO0OOO0OOOO00O0O0 )#line:280
    def create_project_in_file (OO0000OOOO0O0OO00 ,OOO000OOO00000O0O ,O0OO0O0OOOO0OO000 ):#line:282
        OO00O0O000O0000O0 ="{}/{}".format (OO0000OOOO0O0OO00 .compose_path ,OOO000OOO00000O0O )#line:283
        O0OO0OOOO00O0O0O0 ="{}/docker-compose.yaml".format (OO00O0O000O0000O0 )#line:284
        if not os .path .exists (OO00O0O000O0000O0 ):#line:285
            os .makedirs (OO00O0O000O0000O0 )#line:286
        O0OOOO0O0000OO00O =public .readFile (O0OO0O0OOOO0OO000 )#line:287
        public .writeFile (O0OO0OOOO00O0O0O0 ,O0OOOO0O0000OO00O )#line:288
        OO0OO0OOO00OO00OO ="/usr/bin/docker-compose -p {} -f {} up -d &> {}".format (OOO000OOO00000O0O ,O0OO0OOOO00O0O0O0 ,OO0000OOOO0O0OO00 .__OOO0000OOOO00000O )#line:289
        public .ExecShell (OO0OO0OOO00OO00OO )#line:290
    def check_project_container_name (OOOOOO00000O0OO0O ,O0O0O0OO0OOO0O000 ,OO0OOOO00O000OOOO ):#line:292
        ""#line:296
        import re #line:297
        import projectModel .bt_docker .dk_container as dc #line:298
        O00O0OOO00OOOO000 =[]#line:299
        OO0000OO00O0O0O00 =re .findall ("container_name\s*:\s*[\"\']+(.*)[\'\"]",O0O0O0OO0OOO0O000 )#line:300
        OO00OO0OO0OOO00O0 =dc .main ().get_list (OO0OOOO00O000OOOO )#line:301
        if not OO00OO0OO0OOO00O0 ["status"]:#line:302
            return public .returnMsg (False ,"获取容器列表失败!")#line:303
        OO00OO0OO0OOO00O0 =OO00OO0OO0OOO00O0 ['msg']['container_list']#line:304
        for O0O000O0O00OOO0OO in OO00OO0OO0OOO00O0 :#line:305
            if O0O000O0O00OOO0OO ['name']in OO0000OO00O0O0O00 :#line:306
                O00O0OOO00OOOO000 .append (O0O000O0O00OOO0OO ['name'])#line:307
        if O00O0OOO00OOOO000 :#line:308
            return public .returnMsg (False ,"容器名已经存在！: <br>[{}]".format (", ".join (O00O0OOO00OOOO000 )))#line:309
        OO0O00OOO0OO00OOO ="(\d+):\d+"#line:311
        O0OOO0OO00O0OO0O0 =re .findall (OO0O00OOO0OO00OOO ,O0O0O0OO0OOO0O000 )#line:312
        for OO0O0O0OO000O000O in O0OOO0OO00O0OO0O0 :#line:313
            if dp .check_socket (OO0O0O0OO000O000O ):#line:314
                return public .returnMsg (False ,"此端口 [{}] 已经被其他模板使用！".format (OO0O0O0OO000O000O ))#line:315
    def create (O00O00OO000OOO0O0 ,O0OOOOOOO0O0O0OO0 ):#line:318
        ""#line:325
        O0O0O000O0O0OO00O =public .md5 (O0OOOOOOO0O0O0OO0 .project_name )#line:326
        O00O00O000O0OOOOO =dp .sql ("templates").where ("id=?",(O0OOOOOOO0O0O0OO0 .template_id ,)).find ()#line:327
        if not os .path .exists (O00O00O000O0OOOOO ['path']):#line:328
            return public .returnMsg (False ,"模板文件不存在!")#line:329
        O00O00O0O0OO00OOO =O00O00OO000OOO0O0 .check_project_container_name (public .readFile (O00O00O000O0OOOOO ['path']),O0OOOOOOO0O0O0OO0 )#line:330
        if O00O00O0O0OO00OOO :#line:331
            return O00O00O0O0OO00OOO #line:332
        OO0O0000O00000OOO =dp .sql ("stacks").where ("name=?",(O0O0O000O0O0OO00O )).find ()#line:333
        if not OO0O0000O00000OOO :#line:334
            OOOO0O000OO0000OO ={"name":O0OOOOOOO0O0O0OO0 .project_name ,"status":"1","path":O00O00O000O0OOOOO ['path'],"template_id":O0OOOOOOO0O0O0OO0 .template_id ,"time":time .time (),"remark":O0OOOOOOO0O0O0OO0 .remark }#line:342
            dp .sql ("stacks").insert (OOOO0O000OO0000OO )#line:343
        else :#line:344
            return public .returnMsg (False ,"项目名已经存在!")#line:345
        if O00O00O000O0OOOOO ['add_in_path']==1 :#line:346
            O00O00OO000OOO0O0 .create_project_in_path (O0O0O000O0O0OO00O ,O00O00O000O0OOOOO ['path'])#line:350
        else :#line:351
            O00O00OO000OOO0O0 .create_project_in_file (O0O0O000O0O0OO00O ,O00O00O000O0OOOOO ['path'])#line:355
        dp .write_log ("项目 [{}] 部署成功!".format (O0O0O000O0O0OO00O ))#line:356
        public .set_module_logs ('docker','add_project',1 )#line:357
        return public .returnMsg (True ,"部署成功!")#line:358
    def compose_project_list (OO0OO0OOO0OOO0OO0 ,O0O00OO000OO0O000 ):#line:374
        ""#line:377
        O0O00OO000OO0O000 .url ="unix:///var/run/docker.sock"#line:378
        O00O0O0O000OOO000 =dc .main ().get_list (O0O00OO000OO0O000 )#line:379
        if not O00O0O0O000OOO000 ['status']:#line:380
            return public .returnMsg (False ,"启动容器失败，请检查docker服务是否在运行!")#line:381
        if not O00O0O0O000OOO000 ['msg']['service_status']or not O00O0O0O000OOO000 ['msg']['installed']:#line:382
            OOOOOOOOOOO0OOO0O ={"project_list":[],"template":[],"service_status":O00O0O0O000OOO000 ['msg']['service_status'],"installed":O00O0O0O000OOO000 ['msg']['installed']}#line:388
            return public .returnMsg (True ,OOOOOOOOOOO0OOO0O )#line:389
        OOO0000OO0OOO00OO =dp .sql ("stacks").select ()#line:390
        if isinstance (OOO0000OO0OOO00OO ,list ):#line:391
            for O00OO00OO0O0OO0O0 in OOO0000OO0OOO00OO :#line:392
                O0OOOO0000OOO00O0 =[]#line:393
                for OO0OO00OOOOOOOOOO in O00O0O0O000OOO000 ['msg']["container_list"]:#line:394
                    try :#line:395
                        if 'com.docker.compose.project'not in OO0OO00OOOOOOOOOO ["detail"]['Config']['Labels']:#line:396
                            continue #line:397
                    except :#line:398
                        continue #line:399
                    if OO0OO00OOOOOOOOOO ["detail"]['Config']['Labels']['com.docker.compose.project']==public .md5 (O00OO00OO0O0OO0O0 ['name']):#line:400
                        O0OOOO0000OOO00O0 .append (OO0OO00OOOOOOOOOO )#line:401
                O00OOOOO000OOOO0O =O0OOOO0000OOO00O0 #line:402
                O00OO00OO0O0OO0O0 ['container']=O00OOOOO000OOOO0O #line:403
        else :#line:404
            OOO0000OO0OOO00OO =[]#line:405
        OOO0000OO00O0OOO0 =OO0OO0OOO0OOO0OO0 .template_list (O0O00OO000OO0O000 )#line:406
        if not OOO0000OO00O0OOO0 ['status']:#line:407
            OOO0000OO00O0OOO0 =list ()#line:408
        else :#line:409
            OOO0000OO00O0OOO0 =OOO0000OO00O0OOO0 ['msg']['template']#line:410
        O00000O0000O00000 =ds .main ()#line:411
        OOOOOOOOOOO0OOO0O ={"project_list":OOO0000OO0OOO00OO ,"template":OOO0000OO00O0OOO0 ,"service_status":O00000O0000O00000 .get_service_status (),"installed":O00000O0000O00000 .check_docker_program ()}#line:417
        return public .returnMsg (True ,OOOOOOOOOOO0OOO0O )#line:418
    def remove (OOO0OOOOO0000O0OO ,O000OOOO00000000O ):#line:421
        ""#line:426
        O00O0OOOO00OOO0OO =dp .sql ("stacks").where ("id=?",(O000OOOO00000000O .project_id ,)).find ()#line:427
        if not O00O0OOOO00OOO0OO :#line:428
            return public .returnMsg (True ,"没有找到该项目名!")#line:429
        OOOOO0O00OO0O00O0 ="/usr/bin/docker-compose -p {} -f {} down &> {}".format (public .md5 (O00O0OOOO00OOO0OO ['name']),O00O0OOOO00OOO0OO ['path'],OOO0OOOOO0000O0OO .__OOO0000OOOO00000O )#line:430
        O000O0O0OO00OO0OO ,OOO00OO0O0OO0OO0O =public .ExecShell (OOOOO0O00OO0O00O0 )#line:431
        dp .sql ("stacks").delete (id =O000OOOO00000000O .project_id )#line:432
        dp .write_log ("删除项目 [{}] 成功!".format (O00O0OOOO00OOO0OO ['name']))#line:433
        return public .returnMsg (True ,"删除成功!")#line:434
    def stop (O00000O0OOOOO000O ,O0OO0O000O0OOOO00 ):#line:437
        ""#line:443
        OO0O00O00O00O0OO0 =dp .sql ("stacks").where ("id=?",(O0OO0O000O0OOOO00 .project_id ,)).find ()#line:444
        if not OO0O00O00O00O0OO0 :#line:445
            return public .returnMsg (True ,"没找到项目配置!")#line:446
        OOO0OOO00O0000O0O ="/usr/bin/docker-compose -p {} -f {} stop &> {}".format (public .md5 (OO0O00O00O00O0OO0 ['name']),OO0O00O00O00O0OO0 ['path'],O00000O0OOOOO000O .__OOO0000OOOO00000O )#line:448
        O00O0OO00O000OO0O ,O00O000O000O0OO0O =public .ExecShell (OOO0OOO00O0000O0O )#line:449
        dp .write_log ("停止项目 [{}] 成功!".format (OO0O00O00O00O0OO0 ['name']))#line:450
        return public .returnMsg (True ,"设置成功!")#line:451
    def start (OO0OO0O0O0O00000O ,O00000O00O0000000 ):#line:454
        ""#line:459
        O000OOO00000OO0O0 =dp .sql ("stacks").where ("id=?",(O00000O00O0000000 .project_id ,)).find ()#line:460
        if not O000OOO00000OO0O0 :#line:461
            return public .returnMsg (False ,"没找到项目配置!")#line:462
        OOOO0O0000O00OO00 ="/usr/bin/docker-compose -p {} -f {} start > {}".format (public .md5 (O000OOO00000OO0O0 ['name']),O000OOO00000OO0O0 ['path'],OO0OO0O0O0O00000O .__OOO0000OOOO00000O )#line:463
        OO00O0O0O00O00OOO ,OOOO0OO0OOO0000OO =public .ExecShell (OOOO0O0000O00OO00 )#line:464
        dp .write_log ("启动项目 [{}] 成功!".format (O000OOO00000OO0O0 ['name']))#line:465
        return public .returnMsg (True ,"设置成功!")#line:466
    def restart (OOOOO000O000O0000 ,OO000000O0OO0O00O ):#line:469
        ""#line:474
        OO00OOO0OOOOO0O00 =dp .sql ("stacks").where ("id=?",(OO000000O0OO0O00O .project_id ,)).find ()#line:475
        if not OO00OOO0OOOOO0O00 :#line:476
            return public .returnMsg (True ,"没找到项目配置!")#line:477
        O0OO0OOO0000O00O0 ="/usr/bin/docker-compose -p {} -f {} restart &> {}".format (public .md5 (OO00OOO0OOOOO0O00 ['name']),OO00OOO0OOOOO0O00 ['path'],OOOOO000O000O0000 .__OOO0000OOOO00000O )#line:478
        O0000OO0OO00O0O00 ,O0O000OO0OO000O0O =public .ExecShell (O0OO0OOO0000O00O0 )#line:479
        dp .write_log ("重启项目 [{}] 成功!".format (OO00OOO0OOOOO0O00 ['name']))#line:480
        return public .returnMsg (True ,"设置成功!")#line:481
    def pull (O0OO0OOO00OO00000 ,OOOO0OOOOO00OOOOO ):#line:484
        ""#line:489
        O0O0OO0O0O00O0O0O =dp .sql ("templates").where ("id=?",(OOOO0OOOOO00OOOOO .template_id ,)).find ()#line:490
        if not O0O0OO0O0O00O0O0O :#line:491
            return public .returnMsg (True ,"没有找到该模板!")#line:492
        O0O00O000000OO0O0 ="/usr/bin/docker-compose -p {} -f {} pull &> {}".format (O0O0OO0O0O00O0O0O ['name'],O0O0OO0O0O00O0O0O ['path'],O0OO0OOO00OO00000 .__OOO0000OOOO00000O )#line:493
        O000OO00OO0O0OO0O ,O00O0O0OOO00OO0OO =public .ExecShell (O0O00O000000OO0O0 )#line:494
        dp .write_log ("模板 [{}] 内的镜像拉取成功  !".format (O0O0OO0O0O00O0O0O ['name']))#line:495
        return public .returnMsg (True ,"拉取成功!")#line:496
    def pause (OO00OO0O0OOOO00OO ,OO0O00000OO0O0O0O ):#line:499
        ""#line:504
        O0OOOO0000OO00OO0 =dp .sql ("stacks").where ("id=?",(OO0O00000OO0O0O0O .project_id ,)).find ()#line:505
        if not O0OOOO0000OO00OO0 :#line:506
            return public .returnMsg (True ,"没找到项目配置!")#line:507
        OOOO000O00OO0O0OO ="/usr/bin/docker-compose -p {} -f {} pause &> {}".format (public .md5 (O0OOOO0000OO00OO0 ['name']),O0OOOO0000OO00OO0 ['path'],OO00OO0O0OOOO00OO .__OOO0000OOOO00000O )#line:508
        OOOO00OO0OO0OOOOO ,OOOOO0O0O0O0O0OOO =public .ExecShell (OOOO000O00OO0O0OO )#line:509
        dp .write_log ("暂停 [{}] 成功!".format (O0OOOO0000OO00OO0 ['name']))#line:510
        return public .returnMsg (True ,"设置成功!")#line:511
    def unpause (OOOO0OOO0000O0O0O ,OO00OOO000OO0O000 ):#line:514
        ""#line:519
        O0OO0O0000000O0O0 =dp .sql ("stacks").where ("id=?",(OO00OOO000OO0O000 .project_id ,)).find ()#line:520
        if not O0OO0O0000000O0O0 :#line:521
            return public .returnMsg (True ,"没找到项目配置!")#line:522
        OOO0O0OO000O0O0OO ="/usr/bin/docker-compose -p {} -f {} unpause &> {}".format (public .md5 (O0OO0O0000000O0O0 ['name']),O0OO0O0000000O0O0 ['path'],OOOO0OOO0000O0O0O .__OOO0000OOOO00000O )#line:523
        O0O0OOOOOOOO0OOO0 ,O00OOO0000OO000O0 =public .ExecShell (OOO0O0OO000O0O0OO )#line:524
        dp .write_log ("取消暂停 [{}] 成功!".format (O0OO0O0000000O0O0 ['name']))#line:525
        return public .returnMsg (True ,"设置成功!")#line:526
    def scan_compose_file (OO00O0O0O0OO000O0 ,OO00O000O0OOO0OOO ,O0OOOOOO0OO000O0O ):#line:529
        ""#line:535
        O00OOO00O0OO0OO0O =os .listdir (OO00O000O0OOO0OOO )#line:536
        for O0OO00O0O0000O0O0 in O00OOO00O0OO0OO0O :#line:537
            O0OO0OOO0O00O0OOO =os .path .join (OO00O000O0OOO0OOO ,O0OO00O0O0000O0O0 )#line:538
            if os .path .isdir (O0OO0OOO0O00O0OOO ):#line:540
                OO00O0O0O0OO000O0 .scan_compose_file (O0OO0OOO0O00O0OOO ,O0OOOOOO0OO000O0O )#line:541
            else :#line:542
                if O0OO00O0O0000O0O0 =="docker-compose.yaml"or O0OO00O0O0000O0O0 =="docker-compose.yam"or O0OO00O0O0000O0O0 =="docker-compose.yml":#line:543
                    if "/www/server/panel/data/compose"in O0OO0OOO0O00O0OOO :#line:544
                        continue #line:545
                    O0OOOOOO0OO000O0O .append (O0OO0OOO0O00O0OOO )#line:546
        return O0OOOOOO0OO000O0O #line:547
    def get_compose_project (O000O0OO0OOOO0O00 ,OOO0O0OOO0O0O0O00 ):#line:550
        ""#line:556
        OO0O0000O000000O0 =list ()#line:557
        if OOO0O0OOO0O0O0O00 .path =="/":#line:558
            return public .returnMsg (False ,"无法扫描根目录，文件数量太多!")#line:559
        if OOO0O0OOO0O0O0O00 .path [-1 ]=="/":#line:560
            OOO0O0OOO0O0O0O00 .path =OOO0O0OOO0O0O0O00 .path [:-1 ]#line:561
        if str (OOO0O0OOO0O0O0O00 .sub_dir )=="1":#line:562
            O0O0000O0O00OO0OO =O000O0OO0OOOO0O00 .scan_compose_file (OOO0O0OOO0O0O0O00 .path ,OO0O0000O000000O0 )#line:563
            if not O0O0000O0O00OO0OO :#line:564
                O0O0000O0O00OO0OO =[]#line:565
            else :#line:566
                O0O0OO00O00O0OO00 =list ()#line:567
                for O000O0O0OO0OOOOO0 in O0O0000O0O00OO0OO :#line:568
                    O0O0OO00O00O0OO00 .append ({"project_name":O000O0O0OO0OOOOO0 .split ("/")[-2 ],"conf_file":"/".join (O000O0O0OO0OOOOO0 .split ("/")),"remark":"从本地添加"})#line:575
                O0O0000O0O00OO0OO =O0O0OO00O00O0OO00 #line:576
        else :#line:577
            O00OO0OOO000O0OO0 ="{}/docker-compose.yaml".format (OOO0O0OOO0O0O0O00 .path )#line:578
            OO0O0OOO0O00OOO0O ="{}/docker-compose.yam".format (OOO0O0OOO0O0O0O00 .path )#line:579
            if os .path .exists (O00OO0OOO000O0OO0 ):#line:580
                O0O0000O0O00OO0OO =[{"project_name":OOO0O0OOO0O0O0O00 .path .split ("/")[-1 ],"conf_file":O00OO0OOO000O0OO0 ,"remark":"从本地添加"}]#line:585
            elif os .path .exists (OO0O0OOO0O00OOO0O ):#line:586
                O0O0000O0O00OO0OO =[{"project_name":OOO0O0OOO0O0O0O00 .path .split ("/")[-1 ],"conf_file":OO0O0OOO0O00OOO0O ,"remark":"从本地添加"}]#line:591
            else :#line:592
                O0O0000O0O00OO0OO =list ()#line:593
        return O0O0000O0O00OO0OO #line:595
    def add_template_in_path (O0O000O000OOOO0O0 ,OO00O0O00O00OOOO0 ):#line:598
        ""#line:603
        OOO0O00O0O000O000 =dict ()#line:604
        O0OOOOOOOOO0O0OOO =dict ()#line:605
        for O0O000000O00OOO0O in OO00O0O00O00OOOO0 .template_list :#line:606
            O0OOOO0O0OOOO0O00 =O0O000000O00OOO0O ['conf_file']#line:607
            O0O00OOOO0OO0OOO0 =O0O000000O00OOO0O ['project_name']#line:608
            OO0OO0OOO00OO000O =O0O000000O00OOO0O ['remark']#line:609
            OOO0OOO0O0O00000O =O0O000O000OOOO0O0 .template_list (OO00O0O00O00OOOO0 )['msg']['template']#line:610
            for OOOO0O0OOOO000OOO in OOO0OOO0O0O00000O :#line:611
                if O0O00OOOO0OO0OOO0 ==OOOO0O0OOOO000OOO ['name']:#line:612
                    OOO0O00O0O000O000 [O0O00OOOO0OO0OOO0 ]="模板已存在!"#line:613
                    continue #line:614
            if not os .path .exists (O0OOOO0O0OOOO0O00 ):#line:616
                OOO0O00O0O000O000 [O0O00OOOO0OO0OOO0 ]="没找到此模板!"#line:617
                continue #line:618
            O0O0O0000O0OOOO00 =O0O000O000OOOO0O0 .check_conf (O0OOOO0O0OOOO0O00 )#line:620
            if not O0O0O0000O0OOOO00 ['status']:#line:621
                OOO0O00O0O000O000 [O0O00OOOO0OO0OOO0 ]="模板验证失败，可能格式错误!"#line:622
                continue #line:623
            OOOOOOO0O00O00O0O ={"name":O0O00OOOO0OO0OOO0 ,"remark":OO0OO0OOO00OO000O ,"path":O0OOOO0O0OOOO0O00 ,"add_in_path":1 }#line:630
            print (OOOOOOO0O00O00O0O )#line:631
            dp .sql ("templates").insert (OOOOOOO0O00O00O0O )#line:632
            O0OOOOOOOOO0O0OOO [O0O00OOOO0OO0OOO0 ]="模板添加成功!"#line:633
        print (OOO0O00O0O000O000 )#line:635
        for OOOO0O0OOOO000OOO in OOO0O00O0O000O000 :#line:636
            if OOOO0O0OOOO000OOO in O0OOOOOOOOO0O0OOO :#line:637
                del (O0OOOOOOOOO0O0OOO [OOOO0O0OOOO000OOO ])#line:638
            else :#line:639
                dp .write_log ("从路径 [{}] 添加模板成功!".format (OOOO0O0OOOO000OOO ))#line:640
        if not OOO0O00O0O000O000 and O0OOOOOOOOO0O0OOO :#line:641
            return {'status':True ,'msg':'添加模板成功: [{}]'.format (','.join (O0OOOOOOOOO0O0OOO ))}#line:642
        elif not O0OOOOOOOOO0O0OOO and OOO0O00O0O000O000 :#line:643
            return {'status':True ,'msg':'添加模板失败: 模板名已经存在或格式错误 [{}]'.format (','.join (OOO0O00O0O000O000 ))}#line:644
        return {'status':True ,'msg':'这些模板成功: [{}]<br>这些模板失败: 模板名已经存在或格式错误 [{}]'.format (','.join (O0OOOOOOOOO0O0OOO ),','.join (OOO0O00O0O000O000 ))}#line:645
