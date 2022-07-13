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
import os #line:13
import public #line:14
import docker .errors #line:15
import projectModel .bt_docker .dk_public as dp #line:16
class main :#line:18
    __OO0OO00OO0O0OOO00 ='/tmp/dockertmp.log'#line:19
    def docker_client (OOO000OO0OOO0O00O ,O0O0O0OOO0O0O0OOO ):#line:20
        import projectModel .bt_docker .dk_public as dp #line:21
        return dp .docker_client (O0O0O0OOO0O0O0OOO )#line:22
    def save (OOO000OO0O0000OOO ,OOOOOOOOOO0000OOO ):#line:25
        ""#line:33
        try :#line:34
            if "tar"in OOOOOOOOOO0000OOO .name :#line:35
                O0OO0OOO000000OOO ='{}/{}'.format (OOOOOOOOOO0000OOO .path ,OOOOOOOOOO0000OOO .name )#line:36
            else :#line:37
                O0OO0OOO000000OOO ='{}/{}.tar'.format (OOOOOOOOOO0000OOO .path ,OOOOOOOOOO0000OOO .name )#line:38
            if not os .path .exists (OOOOOOOOOO0000OOO .path ):#line:39
                os .makedirs (OOOOOOOOOO0000OOO .path )#line:40
            public .writeFile (O0OO0OOO000000OOO ,"")#line:41
            O0000OOO0OO000O00 =open (O0OO0OOO000000OOO ,'wb')#line:42
            O000O0000OO000O00 =OOO000OO0O0000OOO .docker_client (OOOOOOOOOO0000OOO .url ).images .get (OOOOOOOOOO0000OOO .id )#line:43
            for OOO0O0OOOO00OO0O0 in O000O0000OO000O00 .save (named =True ):#line:44
                O0000OOO0OO000O00 .write (OOO0O0OOOO00OO0O0 )#line:45
            O0000OOO0OO000O00 .close ()#line:46
            dp .write_log ("镜像 [{}] 导出到 [{}] 成功".format (OOOOOOOOOO0000OOO .id ,O0OO0OOO000000OOO ))#line:47
            return public .returnMsg (True ,"Saved successfully to: {}".format (O0OO0OOO000000OOO ))#line:48
        except docker .errors .APIError as O00OO0O000O00O00O :#line:49
            if "empty export - not implemented"in str (O00OO0O000O00O00O ):#line:50
                return public .returnMsg (False ,"不能导出镜像！")#line:51
            return public .get_error_info ()#line:52
    def load (OO0OOOOOOO0000OOO ,OOO0000OO000OO000 ):#line:55
        ""#line:60
        O0O00OOOOO00O000O =OO0OOOOOOO0000OOO .docker_client (OOO0000OO000OO000 .url ).images #line:61
        with open (OOO0000OO000OO000 .path ,'rb')as OOO0000O0O0OO0OOO :#line:62
            O0O00OOOOO00O000O .load (OOO0000O0O0OO0OOO )#line:65
        dp .write_log ("镜像 [{}] 导入成功!".format (OOO0000OO000OO000 .path ))#line:66
        return public .returnMsg (True ,"镜像导入成功！{}".format (OOO0000OO000OO000 .path ))#line:67
    def image_list (OOO00O0000O0O0O00 ,OO0O0OO00O0OO000O ):#line:70
        ""#line:75
        import projectModel .bt_docker .dk_registry as dr #line:76
        import projectModel .bt_docker .dk_setup as ds #line:77
        OOOO00OOO00000OO0 =list ()#line:78
        OOO00OO00OOOOOO0O =OOO00O0000O0O0O00 .docker_client (OO0O0OO00O0OO000O .url )#line:79
        OOOOO0OO0OO000O0O =ds .main ()#line:80
        O0OOO0O000000OO00 =OOOOO0OO0OO000O0O .check_docker_program ()#line:81
        OOOO000OOO00OOO00 =OOOOO0OO0OO000O0O .get_service_status ()#line:82
        if not OOO00OO00OOOOOO0O :#line:83
            OOOO00OOO00000OO0 ={"images_list":[],"registry_list":[],"installed":O0OOO0O000000OO00 ,"service_status":OOOO000OOO00OOO00 }#line:89
            return public .returnMsg (True ,OOOO00OOO00000OO0 )#line:90
        O000O0OOO00O0O00O =OOO00OO00OOOOOO0O .images #line:91
        OO0OOOOOOOOO000O0 =OOO00O0000O0O0O00 .get_image_attr (O000O0OOO00O0O00O )#line:92
        O0O0O000O0OO000OO =dr .main ().registry_list (OO0O0OO00O0OO000O )#line:93
        if O0O0O000O0OO000OO ['status']:#line:94
            O0O0O000O0OO000OO =O0O0O000O0OO000OO ['msg']['registry']#line:95
        else :#line:96
            O0O0O000O0OO000OO =[]#line:97
        for OOOOOO0O0OO000O00 in OO0OOOOOOOOO000O0 :#line:98
            if len (OOOOOO0O0OO000O00 ['RepoTags'])==1 :#line:99
                O000O0O00OO00O0OO ={"id":OOOOOO0O0OO000O00 ["Id"],"tags":OOOOOO0O0OO000O00 ["RepoTags"],"time":OOOOOO0O0OO000O00 ["Created"],"name":OOOOOO0O0OO000O00 ['RepoTags'][0 ],"size":OOOOOO0O0OO000O00 ["Size"],"detail":OOOOOO0O0OO000O00 }#line:107
                OOOO00OOO00000OO0 .append (O000O0O00OO00O0OO )#line:108
            elif len (OOOOOO0O0OO000O00 ['RepoTags'])>1 :#line:109
                for O00OOOO000O00OOO0 in range (len (OOOOOO0O0OO000O00 ['RepoTags'])):#line:110
                    O000O0O00OO00O0OO ={"id":OOOOOO0O0OO000O00 ["Id"],"tags":OOOOOO0O0OO000O00 ["RepoTags"],"time":OOOOOO0O0OO000O00 ["Created"],"name":OOOOOO0O0OO000O00 ['RepoTags'][O00OOOO000O00OOO0 ],"size":OOOOOO0O0OO000O00 ["Size"],"detail":OOOOOO0O0OO000O00 }#line:118
                    OOOO00OOO00000OO0 .append (O000O0O00OO00O0OO )#line:119
            elif not OOOOOO0O0OO000O00 ['RepoTags']:#line:120
                O000O0O00OO00O0OO ={"id":OOOOOO0O0OO000O00 ["Id"],"tags":OOOOOO0O0OO000O00 ["RepoTags"],"time":OOOOOO0O0OO000O00 ["Created"],"name":OOOOOO0O0OO000O00 ["Id"],"size":OOOOOO0O0OO000O00 ["Size"],"detail":OOOOOO0O0OO000O00 }#line:128
                OOOO00OOO00000OO0 .append (O000O0O00OO00O0OO )#line:129
        OOOO00OOO00000OO0 ={"images_list":OOOO00OOO00000OO0 ,"registry_list":O0O0O000O0OO000OO ,"installed":O0OOO0O000000OO00 ,"service_status":OOOO000OOO00OOO00 }#line:135
        return public .returnMsg (True ,OOOO00OOO00000OO0 )#line:136
    def get_image_attr (O0OO0OO00OOOOO0OO ,OO0OOO00O000OOOOO ):#line:138
        O00O0OO0O0OOO0O00 =OO0OOO00O000OOOOO .list ()#line:139
        return [O000O0O0O0OO000OO .attrs for O000O0O0O0OO000OO in O00O0OO0O0OOO0O00 ]#line:140
    def get_logs (OOOOOO00O0OO0OO00 ,OO0OO00OO0O0O0O0O ):#line:142
        import files #line:143
        O000O0OO0OO000OOO =OO0OO00OO0O0O0O0O .logs_file #line:144
        return public .returnMsg (True ,files .files ().GetLastLine (O000O0OO0OO000OOO ,20 ))#line:145
    def build (O00O0O00OO00OOOO0 ,O00O000O00O00OO0O ):#line:148
        ""#line:156
        public .writeFile (O00O0O00OO00OOOO0 .__OO0OO00OO0O0OOO00 ,"开始构建镜像！")#line:157
        public .writeFile ('/tmp/dockertmp.log',"开始构建镜像！")#line:158
        if not hasattr (O00O000O00O00OO0O ,"pull"):#line:159
            O00O000O00O00OO0O .pull =False #line:160
        if hasattr (O00O000O00O00OO0O ,"data")and O00O000O00O00OO0O .data :#line:161
            O00O000O00O00OO0O .path ="/tmp/dockerfile"#line:162
            public .writeFile (O00O000O00O00OO0O .path ,O00O000O00O00OO0O .data )#line:163
            with open (O00O000O00O00OO0O .path ,'rb')as OO0O0000O0OOOO0OO :#line:164
                OOOOO000O0OOO00O0 ,OO0000O0000OO00O0 =O00O0O00OO00OOOO0 .docker_client (O00O000O00O00OO0O .url ).images .build (pull =True if O00O000O00O00OO0O .pull =="1"else False ,fileobj =OO0O0000O0OOOO0OO ,tag =O00O000O00O00OO0O .tag ,forcerm =True )#line:170
            os .remove (O00O000O00O00OO0O .path )#line:171
        else :#line:172
            if not os .path .exists (O00O000O00O00OO0O .path ):#line:173
                return public .returnMsg (True ,"请输入正确的DockerFile路径！")#line:174
            if not os .path .isdir (O00O000O00O00OO0O .path ):#line:175
                O00O000O00O00OO0O .path ='/'.join (O00O000O00O00OO0O .path .split ('/')[:-1 ])#line:176
            OOOOO000O0OOO00O0 ,OO0000O0000OO00O0 =O00O0O00OO00OOOO0 .docker_client (O00O000O00O00OO0O .url ).images .build (pull =True if O00O000O00O00OO0O .pull =="1"else False ,path =O00O000O00O00OO0O .path ,tag =O00O000O00O00OO0O .tag ,forcerm =True )#line:182
        dp .log_docker (OO0000O0000OO00O0 ,"Docker 构建任务！")#line:184
        dp .write_log ("构建镜像 [{}] 成功!".format (O00O000O00O00OO0O .tag ))#line:185
        return public .returnMsg (True ,"构建镜像成功!")#line:186
    def remove (OOO00OOOOOO0O00O0 ,O0OOOO00O000000OO ):#line:189
        ""#line:197
        try :#line:198
            OOO00OOOOOO0O00O0 .docker_client (O0OOOO00O000000OO .url ).images .remove (O0OOOO00O000000OO .name )#line:199
            dp .write_log ("删除镜像【{}】成功!".format (O0OOOO00O000000OO .name ))#line:200
            return public .returnMsg (True ,"删除镜像成功!")#line:201
        except docker .errors .ImageNotFound as OO000O0O00OOOO000 :#line:202
            return public .returnMsg (False ,"删除进行失败，镜像可能不存在!")#line:203
        except docker .errors .APIError as OO000O0O00OOOO000 :#line:204
            if "image is referenced in multiple repositories"in str (OO000O0O00OOOO000 ):#line:205
                return public .returnMsg (False ,"镜像 ID 用在多个镜像中，请强制删除镜像!")#line:206
            if "using its referenced image"in str (OO000O0O00OOOO000 ):#line:207
                return public .returnMsg (False ,"镜像正在使用中，请删除容器后再删除镜像!")#line:208
            return public .returnMsg (False ,"删除镜像失败!<br> {}".format (OO000O0O00OOOO000 ))#line:209
    def pull_from_some_registry (O0OO00OO0O00O00OO ,OOOOO0OO000O0000O ):#line:212
        ""#line:219
        import projectModel .bt_docker .dk_registry as br #line:220
        OOO0O00OOOOO0OO00 =br .main ().registry_info (OOOOO0OO000O0000O .name )#line:221
        OOOO0O0OOO0O0OO00 =br .main ().login (OOOOO0OO000O0000O .url ,OOO0O00OOOOO0OO00 ['url'],OOO0O00OOOOO0OO00 ['username'],OOO0O00OOOOO0OO00 ['password'])['status']#line:222
        if not OOOO0O0OOO0O0OO00 :#line:223
            return OOOO0O0OOO0O0OO00 #line:224
        OOOOO0OO000O0000O .username =OOO0O00OOOOO0OO00 ['username']#line:225
        OOOOO0OO000O0000O .password =OOO0O00OOOOO0OO00 ['password']#line:226
        OOOOO0OO000O0000O .registry =OOO0O00OOOOO0OO00 ['url']#line:227
        OOOOO0OO000O0000O .namespace =OOO0O00OOOOO0OO00 ['namespace']#line:228
        return O0OO00OO0O00O00OO .pull (OOOOO0OO000O0000O )#line:229
    def push (OO0O0O0000O000O00 ,OO0OO00OO0O00OO0O ):#line:232
        ""#line:240
        if "/"in OO0OO00OO0O00OO0O .tag :#line:241
            return public .returnMsg (False ,"推送的镜像不能包含 [/] , 请使用以下格式: image:v1 (镜像名:版本)")#line:242
        if ":"not in OO0OO00OO0O00OO0O .tag :#line:243
            return public .returnMsg (False ,"推送的镜像不能包含 [ : ] , 请使用以下格式: image:v1 (image_name:version_number)")#line:244
        public .writeFile (OO0O0O0000O000O00 .__OO0OO00OO0O0OOO00 ,"开始推镜像!\n")#line:245
        import projectModel .bt_docker .dk_registry as br #line:246
        O0O00O0000O00000O =br .main ().registry_info (OO0OO00OO0O00OO0O .name )#line:247
        if OO0OO00OO0O00OO0O .name =="docker official"and O0O00O0000O00000O ['url']=="docker.io":#line:248
            public .writeFile (OO0O0O0000O000O00 .__OO0OO00OO0O0OOO00 ,"镜像无法推送到 Docker 公共仓库!\n")#line:249
            return public .returnMsg (False ,"无法推送到 Docker 公共仓库!")#line:250
        OOOO0000OOOOO0OO0 =br .main ().login (OO0OO00OO0O00OO0O .url ,O0O00O0000O00000O ['url'],O0O00O0000O00000O ['username'],O0O00O0000O00000O ['password'])['status']#line:251
        OOOO00OOOOOOO0000 =OO0OO00OO0O00OO0O .tag #line:252
        if not OOOO0000OOOOO0OO0 :#line:253
            return OOOO0000OOOOO0OO0 #line:254
        O0OO00O00OO00OO0O ={"username":O0O00O0000O00000O ['username'],"password":O0O00O0000O00000O ['password'],"registry":O0O00O0000O00000O ['url']}#line:258
        if ":"not in OOOO00OOOOOOO0000 :#line:260
            OOOO00OOOOOOO0000 ="{}:latest".format (OOOO00OOOOOOO0000 )#line:261
        O00OO000OOO000OOO =O0O00O0000O00000O ['url']#line:262
        OO0O00O0OO0O0OOO0 ="{}/{}/{}".format (O00OO000OOO000OOO ,O0O00O0000O00000O ['namespace'],OO0OO00OO0O00OO0O .tag )#line:263
        OO0O0O0000O000O00 .tag (OO0OO00OO0O00OO0O .url ,OO0OO00OO0O00OO0O .id ,OO0O00O0OO0O0OOO0 )#line:264
        O0OOOOO0O0OO00O00 =OO0O0O0000O000O00 .docker_client (OO0OO00OO0O00OO0O .url ).images .push (repository =OO0O00O0OO0O0OOO0 .split (":")[0 ],tag =OOOO00OOOOOOO0000 .split (":")[-1 ],auth_config =O0OO00O00OO00OO0O ,stream =True )#line:270
        dp .log_docker (O0OOOOO0O0OO00O00 ,"Image push task")#line:271
        OO0OO00OO0O00OO0O .name =OO0O00O0OO0O0OOO0 #line:273
        OO0O0O0000O000O00 .remove (OO0OO00OO0O00OO0O )#line:274
        dp .write_log ("镜像 [{}] 推送成功！".format (OO0O00O0OO0O0OOO0 ))#line:275
        return public .returnMsg (True ,"推送成功！{}".format (str (O0OOOOO0O0OO00O00 )))#line:276
    def tag (OOO0O0OO0O000O0O0 ,OO00000OO0000000O ,O0O0OOOOO0OOO0O00 ,OO00000O00O0OO0OO ):#line:278
        ""#line:285
        O00O0O0O00OO00000 =OO00000O00O0OO0OO .split (":")[0 ]#line:286
        OO0O0O0OOO00OO0OO =OO00000O00O0OO0OO .split (":")[1 ]#line:287
        OOO0O0OO0O000O0O0 .docker_client (OO00000OO0000000O ).images .get (O0O0OOOOO0OOO0O00 ).tag (repository =O00O0O0O00OO00000 ,tag =OO0O0O0OOO00OO0OO )#line:291
        return public .returnMsg (True ,"设置成功！")#line:292
    def pull (O0OO00OO00O0OOOO0 ,OOOOOO0OO0OO0000O ):#line:294
        ""#line:303
        public .writeFile (O0OO00OO00O0OOOO0 .__OO0OO00OO0O0OOO00 ,"开始推送镜像!")#line:304
        import docker .errors #line:305
        try :#line:306
            if ':'not in OOOOOO0OO0OO0000O .image :#line:307
                OOOOOO0OO0OO0000O .image ='{}:latest'.format (OOOOOO0OO0OO0000O .image )#line:308
            OOO0000OOOOO0O000 ={"username":OOOOOO0OO0OO0000O .username ,"password":OOOOOO0OO0OO0000O .password ,"registry":OOOOOO0OO0OO0000O .registry if OOOOOO0OO0OO0000O .registry else None }if OOOOOO0OO0OO0000O .username else None #line:312
            if not hasattr (OOOOOO0OO0OO0000O ,"tag"):#line:313
                OOOOOO0OO0OO0000O .tag =OOOOOO0OO0OO0000O .image .split (":")[-1 ]#line:314
            if OOOOOO0OO0OO0000O .registry !="docker.io":#line:315
                OOOOOO0OO0OO0000O .image ="{}/{}/{}".format (OOOOOO0OO0OO0000O .registry ,OOOOOO0OO0OO0000O .namespace ,OOOOOO0OO0OO0000O .image )#line:316
            O0O0O0OO00OO0OOOO =dp .docker_client_low (OOOOOO0OO0OO0000O .url ).pull (repository =OOOOOO0OO0OO0000O .image ,auth_config =OOO0000OOOOO0O000 ,tag =OOOOOO0OO0OO0000O .tag ,stream =True )#line:322
            dp .log_docker (O0O0O0OO00OO0OOOO ,"镜像拉取任务")#line:323
            if O0O0O0OO00OO0OOOO :#line:324
                dp .write_log ("镜像拉取 [{}:{}] 成功".format (OOOOOO0OO0OO0000O .image ,OOOOOO0OO0OO0000O .tag ))#line:325
                return public .returnMsg (True ,'镜像拉取成功.')#line:326
            else :#line:327
                return public .returnMsg (False ,'可能没有这个镜像.')#line:328
        except docker .errors .ImageNotFound as OO0O0OOO00000O0O0 :#line:329
            if "pull access denied for"in str (OO0O0OOO00000O0O0 ):#line:330
                return public .returnMsg (False ,"拉取失败，镜像为私有镜像，需要输入dockerhub的账号密码!")#line:331
            return public .returnMsg (False ,"拉取失败<br><br>原因: {}".format (OO0O0OOO00000O0O0 ))#line:333
        except docker .errors .NotFound as OO0O0OOO00000O0O0 :#line:335
            if "not found: manifest unknown"in str (OO0O0OOO00000O0O0 ):#line:336
                return public .returnMsg (False ,"镜像拉取失败，仓库中没有这个镜像!")#line:337
            return public .returnMsg (False ,"Pull failed<br><br>reason:{}".format (OO0O0OOO00000O0O0 ))#line:338
        except docker .errors .APIError as OO0O0OOO00000O0O0 :#line:339
            if "invalid tag format"in str (OO0O0OOO00000O0O0 ):#line:340
                return public .returnMsg (False ,"拉取失败, 镜像格式错误, 如: nginx:v 1!")#line:341
            return public .returnMsg (False ,"拉取失败!{}".format (OO0O0OOO00000O0O0 ))#line:342
    def pull_high_api (OO000OOO0O0O0OOO0 ,OO000O0OOO00OOOOO ):#line:346
        ""#line:355
        import docker .errors #line:356
        try :#line:357
            if ':'not in OO000O0OOO00OOOOO .image :#line:358
                OO000O0OOO00OOOOO .image ='{}:latest'.format (OO000O0OOO00OOOOO .image )#line:359
            OO00O0OOOO0000O0O ={"username":OO000O0OOO00OOOOO .username ,"password":OO000O0OOO00OOOOO .password ,"registry":OO000O0OOO00OOOOO .registry if OO000O0OOO00OOOOO .registry else None }if OO000O0OOO00OOOOO .username else None #line:363
            if OO000O0OOO00OOOOO .registry !="docker.io":#line:365
                OO000O0OOO00OOOOO .image ="{}/{}/{}".format (OO000O0OOO00OOOOO .registry ,OO000O0OOO00OOOOO .namespace ,OO000O0OOO00OOOOO .image )#line:366
            OOOO00OOO0OOO00O0 =OO000OOO0O0O0OOO0 .docker_client (OO000O0OOO00OOOOO .url ).images .pull (repository =OO000O0OOO00OOOOO .image ,auth_config =OO00O0OOOO0000O0O ,)#line:370
            if OOOO00OOO0OOO00O0 :#line:371
                return public .returnMsg (True ,'拉取镜像成功.')#line:372
            else :#line:373
                return public .returnMsg (False ,'可能没有这个镜像.')#line:374
        except docker .errors .ImageNotFound as OOOOOOO0OO0OOO0OO :#line:375
            if "pull access denied for"in str (OOOOOOO0OO0OOO0OO ):#line:376
                return public .returnMsg (False ,"拉取镜像失败, 这个是私有镜像，请输入账号密码!")#line:377
            return public .returnMsg (False ,"拉取镜像失败<br><br>原因: {}".format (OOOOOOO0OO0OOO0OO ))#line:378
    def image_for_host (OO0O0O00O000O0O0O ,OO0OO0OOOOO0OOO00 ):#line:380
        ""#line:385
        O000000OOOO00OO0O =OO0O0O00O000O0O0O .image_list (OO0OO0OOOOO0OOO00 )#line:386
        if not O000000OOOO00OO0O ['status']:#line:387
            return O000000OOOO00OO0O #line:388
        OO0000O0O0000OOOO =len (O000000OOOO00OO0O ['msg']['images_list'])#line:389
        O0OOO0O0O000OOO0O =0 #line:390
        for O00OO00OOOO0000OO in O000000OOOO00OO0O ['msg']['images_list']:#line:391
            O0OOO0O0O000OOO0O +=O00OO00OOOO0000OO ['size']#line:392
        return public .returnMsg (True ,{'num':OO0000O0O0000OOOO ,'size':O0OOO0O0O000OOO0O })