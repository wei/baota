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
    __OOOOO00OOOOOO0000 ='/tmp/dockertmp.log'#line:19
    def docker_client (O0OO0O00O000O0000 ,OOOOOO0OOOOOO0OO0 ):#line:20
        import projectModel .bt_docker .dk_public as dp #line:21
        return dp .docker_client (OOOOOO0OOOOOO0OO0 )#line:22
    def save (OOO00OOOO000OOO0O ,OO00O00OO0O000000 ):#line:25
        ""#line:33
        try :#line:34
            if "tar"in OO00O00OO0O000000 .name :#line:35
                O0OOOOOO00O0O00OO ='{}/{}'.format (OO00O00OO0O000000 .path ,OO00O00OO0O000000 .name )#line:36
            else :#line:37
                O0OOOOOO00O0O00OO ='{}/{}.tar'.format (OO00O00OO0O000000 .path ,OO00O00OO0O000000 .name )#line:38
            if not os .path .exists (OO00O00OO0O000000 .path ):#line:39
                os .makedirs (OO00O00OO0O000000 .path )#line:40
            public .writeFile (O0OOOOOO00O0O00OO ,"")#line:41
            OOO0O00O0O0OO0000 =open (O0OOOOOO00O0O00OO ,'wb')#line:42
            O000OO0OOOO0OOO0O =OOO00OOOO000OOO0O .docker_client (OO00O00OO0O000000 .url ).images .get (OO00O00OO0O000000 .id )#line:43
            for OOO0000OO0O0OO0O0 in O000OO0OOOO0OOO0O .save (named =True ):#line:44
                OOO0O00O0O0OO0000 .write (OOO0000OO0O0OO0O0 )#line:45
            OOO0O00O0O0OO0000 .close ()#line:46
            dp .write_log ("镜像【{}】导出到【{}】成功！".format (OO00O00OO0O000000 .id ,O0OOOOOO00O0O00OO ))#line:47
            return public .returnMsg (True ,"成功保存到: {}".format (O0OOOOOO00O0O00OO ))#line:48
        except docker .errors .APIError as O0O00OO00O0OOO0O0 :#line:49
            if "empty export - not implemented"in str (O0O00OO00O0OOO0O0 ):#line:50
                return public .returnMsg (False ,"不能导出空镜像！")#line:51
            return public .get_error_info ()#line:52
    def load (O0O00OOO0OOOO00O0 ,O0OOO00OO000000O0 ):#line:55
        ""#line:60
        OO0OOO00OOOO00OO0 =O0O00OOO0OOOO00O0 .docker_client (O0OOO00OO000000O0 .url ).images #line:61
        with open (O0OOO00OO000000O0 .path ,'rb')as O0OOO000OOOOO0000 :#line:62
            OO0OOO00OOOO00OO0 .load (O0OOO000OOOOO0000 )#line:65
        dp .write_log ("镜像【{}】导入成功！".format (O0OOO00OO000000O0 .path ))#line:66
        return public .returnMsg (True ,"导入成功！{}".format (O0OOO00OO000000O0 .path ))#line:67
    def image_list (OOOOOOO0OOO0OOOOO ,O000OOO0OOO0O0OO0 ):#line:70
        ""#line:75
        import projectModel .bt_docker .dk_registry as dr #line:76
        import projectModel .bt_docker .dk_setup as ds #line:77
        O00O0O00OO00O0000 =list ()#line:78
        OO00O0O00000O000O =OOOOOOO0OOO0OOOOO .docker_client (O000OOO0OOO0O0OO0 .url )#line:79
        OO0O0OO0OOO0000OO =ds .main ()#line:80
        O0O00O00000000OOO =OO0O0OO0OOO0000OO .check_docker_program ()#line:81
        O00OO000O0OOOO0O0 =OO0O0OO0OOO0000OO .get_service_status ()#line:82
        if not OO00O0O00000O000O :#line:83
            O00O0O00OO00O0000 ={"images_list":[],"registry_list":[],"installed":O0O00O00000000OOO ,"service_status":O00OO000O0OOOO0O0 }#line:89
            return public .returnMsg (True ,O00O0O00OO00O0000 )#line:90
        O0O0OO00O0O000000 =OO00O0O00000O000O .images #line:91
        OO0000O000O0OOOO0 =OOOOOOO0OOO0OOOOO .get_image_attr (O0O0OO00O0O000000 )#line:92
        O0OOO0OOOO0OO0OO0 =dr .main ().registry_list (O000OOO0OOO0O0OO0 )#line:93
        if O0OOO0OOOO0OO0OO0 ['status']:#line:94
            O0OOO0OOOO0OO0OO0 =O0OOO0OOOO0OO0OO0 ['msg']['registry']#line:95
        else :#line:96
            O0OOO0OOOO0OO0OO0 =[]#line:97
        for OOO0O00O00O00OOO0 in OO0000O000O0OOOO0 :#line:98
            if len (OOO0O00O00O00OOO0 ['RepoTags'])==1 :#line:99
                OOOO0000OOO00O000 ={"id":OOO0O00O00O00OOO0 ["Id"],"tags":OOO0O00O00O00OOO0 ["RepoTags"],"time":OOO0O00O00O00OOO0 ["Created"],"name":OOO0O00O00O00OOO0 ['RepoTags'][0 ],"size":OOO0O00O00O00OOO0 ["Size"],"detail":OOO0O00O00O00OOO0 }#line:107
                O00O0O00OO00O0000 .append (OOOO0000OOO00O000 )#line:108
            elif len (OOO0O00O00O00OOO0 ['RepoTags'])>1 :#line:109
                for O00OO0OOO0000O000 in range (len (OOO0O00O00O00OOO0 ['RepoTags'])):#line:110
                    OOOO0000OOO00O000 ={"id":OOO0O00O00O00OOO0 ["Id"],"tags":OOO0O00O00O00OOO0 ["RepoTags"],"time":OOO0O00O00O00OOO0 ["Created"],"name":OOO0O00O00O00OOO0 ['RepoTags'][O00OO0OOO0000O000 ],"size":OOO0O00O00O00OOO0 ["Size"],"detail":OOO0O00O00O00OOO0 }#line:118
                    O00O0O00OO00O0000 .append (OOOO0000OOO00O000 )#line:119
            elif not OOO0O00O00O00OOO0 ['RepoTags']:#line:120
                OOOO0000OOO00O000 ={"id":OOO0O00O00O00OOO0 ["Id"],"tags":OOO0O00O00O00OOO0 ["RepoTags"],"time":OOO0O00O00O00OOO0 ["Created"],"name":OOO0O00O00O00OOO0 ["Id"],"size":OOO0O00O00O00OOO0 ["Size"],"detail":OOO0O00O00O00OOO0 }#line:128
                O00O0O00OO00O0000 .append (OOOO0000OOO00O000 )#line:129
        O00O0O00OO00O0000 ={"images_list":O00O0O00OO00O0000 ,"registry_list":O0OOO0OOOO0OO0OO0 ,"installed":O0O00O00000000OOO ,"service_status":O00OO000O0OOOO0O0 }#line:135
        return public .returnMsg (True ,O00O0O00OO00O0000 )#line:136
    def get_image_attr (OOO000OOO0OOO0000 ,OO0OO000OOO0O0O0O ):#line:138
        O000OO0O0O0O00OOO =OO0OO000OOO0O0O0O .list ()#line:139
        return [O00O0O0O00O0O0OO0 .attrs for O00O0O0O00O0O0OO0 in O000OO0O0O0O00OOO ]#line:140
    def get_logs (OOOO00OOO0OO00000 ,O0O0000OO0O00O0OO ):#line:142
        import files #line:143
        OOOOO0OOOOOO0OOO0 =O0O0000OO0O00O0OO .logs_file #line:144
        return public .returnMsg (True ,files .files ().GetLastLine (OOOOO0OOOOOO0OOO0 ,20 ))#line:145
    def build (O0O00O00O0O00000O ,O0O0O0O0O0O0000OO ):#line:148
        ""#line:156
        public .writeFile (O0O00O00O0O00000O .__OOOOO00OOOOOO0000 ,"开始构建镜像！")#line:157
        public .writeFile ('/tmp/dockertmp.log',"开始构造镜像")#line:158
        if not hasattr (O0O0O0O0O0O0000OO ,"pull"):#line:159
            O0O0O0O0O0O0000OO .pull =False #line:160
        if hasattr (O0O0O0O0O0O0000OO ,"data")and O0O0O0O0O0O0000OO .data :#line:161
            O0O0O0O0O0O0000OO .path ="/tmp/dockerfile"#line:162
            public .writeFile (O0O0O0O0O0O0000OO .path ,O0O0O0O0O0O0000OO .data )#line:163
            with open (O0O0O0O0O0O0000OO .path ,'rb')as OOO0O000OO0O00OOO :#line:164
                O0O0O0O000OOOOOO0 ,OOOOOO0000OO0O000 =O0O00O00O0O00000O .docker_client (O0O0O0O0O0O0000OO .url ).images .build (pull =True if O0O0O0O0O0O0000OO .pull =="1"else False ,fileobj =OOO0O000OO0O00OOO ,tag =O0O0O0O0O0O0000OO .tag )#line:169
            os .remove (O0O0O0O0O0O0000OO .path )#line:170
        else :#line:171
            if not os .path .isdir (O0O0O0O0O0O0000OO .path ):#line:172
                O0O0O0O0O0O0000OO .path ='/'.join (O0O0O0O0O0O0000OO .path .split ('/')[:-1 ])#line:173
            O0O0O0O000OOOOOO0 ,OOOOOO0000OO0O000 =O0O00O00O0O00000O .docker_client (O0O0O0O0O0O0000OO .url ).images .build (pull =True if O0O0O0O0O0O0000OO .pull =="1"else False ,path =O0O0O0O0O0O0000OO .path ,tag =O0O0O0O0O0O0000OO .tag )#line:178
        dp .log_docker (OOOOOO0000OO0O000 ,"Docker 构建任务")#line:180
        dp .write_log ("构建镜像【{}】成功！".format (O0O0O0O0O0O0000OO .tag ))#line:181
        return public .returnMsg (True ,"构造成功！")#line:182
    def remove (OO0OOOOOO0OOOOOO0 ,O00000OOOOO00O0OO ):#line:185
        ""#line:193
        try :#line:194
            OO0OOOOOO0OOOOOO0 .docker_client (O00000OOOOO00O0OO .url ).images .remove (O00000OOOOO00O0OO .name )#line:195
            dp .write_log ("删除镜像【{}】成功！".format (O00000OOOOO00O0OO .name ))#line:196
            return public .returnMsg (True ,"镜像删除成功！")#line:197
        except docker .errors .ImageNotFound as OOOOO0OO000OOO00O :#line:198
            return public .returnMsg (False ,"删除镜像失败，可能是镜像不存在！")#line:199
        except docker .errors .APIError as OOOOO0OO000OOO00O :#line:200
            if "image is referenced in multiple repositories"in str (OOOOO0OO000OOO00O ):#line:201
                return public .returnMsg (False ,"该镜像ID被用于多个镜像中，请勾选【强制删除】！")#line:202
            if "using its referenced image"in str (OOOOO0OO000OOO00O ):#line:203
                return public .returnMsg (False ,"该镜像正在使用，请删除容器后再删除！")#line:204
            return public .returnMsg (False ,"删除镜像失败！<br> {}".format (OOOOO0OO000OOO00O ))#line:205
    def pull_from_some_registry (OOOOO00O0000O00O0 ,OOO0OOO00OO000000 ):#line:208
        ""#line:215
        import projectModel .bt_docker .dk_registry as br #line:216
        OO0OOOO0O0OOOO0O0 =br .main ().registry_info (OOO0OOO00OO000000 .name )#line:217
        O0OO00OO00OO0OOO0 =br .main ().login (OOO0OOO00OO000000 .url ,OO0OOOO0O0OOOO0O0 ['url'],OO0OOOO0O0OOOO0O0 ['username'],OO0OOOO0O0OOOO0O0 ['password'])['status']#line:218
        if not O0OO00OO00OO0OOO0 :#line:219
            return O0OO00OO00OO0OOO0 #line:220
        OOO0OOO00OO000000 .username =OO0OOOO0O0OOOO0O0 ['username']#line:221
        OOO0OOO00OO000000 .password =OO0OOOO0O0OOOO0O0 ['password']#line:222
        OOO0OOO00OO000000 .registry =OO0OOOO0O0OOOO0O0 ['url']#line:223
        OOO0OOO00OO000000 .namespace =OO0OOOO0O0OOOO0O0 ['namespace']#line:224
        return OOOOO00O0000O00O0 .pull (OOO0OOO00OO000000 )#line:225
    def push (OOO00O0OO00OO0000 ,OO0OO0OO0000O0OO0 ):#line:228
        ""#line:236
        if "/"in OO0OO0OO0000O0OO0 .tag :#line:237
            return public .returnMsg (False ,"推送的镜像名不可以包含符号 [/] ，请使用如下格式：image:v1 (镜像名：版本号)")#line:238
        if ":"not in OO0OO0OO0000O0OO0 .tag :#line:239
            return public .returnMsg (False ,"推送的镜像名需包含符号 [ : ] ，请使用如下格式：image:v1 (镜像名：版本号)")#line:240
        public .writeFile (OOO00O0OO00OO0000 .__OOOOO00OOOOOO0000 ,"开始推送镜像！\n")#line:241
        import projectModel .bt_docker .dk_registry as br #line:242
        OOO0OOOO0OO0OOOOO =br .main ().registry_info (OO0OO0OO0000O0OO0 .name )#line:243
        if OO0OO0OO0000O0OO0 .name =="docker官方库"and OOO0OOOO0OO0OOOOO ['url']=="docker.io":#line:244
            public .writeFile (OOO00O0OO00OO0000 .__OOOOO00OOOOOO0000 ,"镜像无法推送到Docker公共仓库！\n")#line:245
            return public .returnMsg (False ,"无法推送到Docker公共仓库！")#line:246
        O0OO000OO0O0OO0OO =br .main ().login (OO0OO0OO0000O0OO0 .url ,OOO0OOOO0OO0OOOOO ['url'],OOO0OOOO0OO0OOOOO ['username'],OOO0OOOO0OO0OOOOO ['password'])['status']#line:247
        OOO0OO000O0OOO0O0 =OO0OO0OO0000O0OO0 .tag #line:248
        if not O0OO000OO0O0OO0OO :#line:249
            return O0OO000OO0O0OO0OO #line:250
        OO0OOOO0OOO00O000 ={"username":OOO0OOOO0OO0OOOOO ['username'],"password":OOO0OOOO0OO0OOOOO ['password'],"registry":OOO0OOOO0OO0OOOOO ['url']}#line:254
        if ":"not in OOO0OO000O0OOO0O0 :#line:256
            OOO0OO000O0OOO0O0 ="{}:latest".format (OOO0OO000O0OOO0O0 )#line:257
        O0000OO00OO00O0O0 =OOO0OOOO0OO0OOOOO ['url']#line:258
        OOOO000OO0O000OO0 ="{}/{}/{}".format (O0000OO00OO00O0O0 ,OOO0OOOO0OO0OOOOO ['namespace'],OO0OO0OO0000O0OO0 .tag )#line:259
        OOO00O0OO00OO0000 .tag (OO0OO0OO0000O0OO0 .url ,OO0OO0OO0000O0OO0 .id ,OOOO000OO0O000OO0 )#line:260
        O00O0O0O0000OO0OO =OOO00O0OO00OO0000 .docker_client (OO0OO0OO0000O0OO0 .url ).images .push (repository =OOOO000OO0O000OO0 .split (":")[0 ],tag =OOO0OO000O0OOO0O0 .split (":")[-1 ],auth_config =OO0OOOO0OOO00O000 ,stream =True )#line:266
        dp .log_docker (O00O0O0O0000OO0OO ,"镜像推送任务")#line:267
        OO0OO0OO0000O0OO0 .name =OOOO000OO0O000OO0 #line:269
        OOO00O0OO00OO0000 .remove (OO0OO0OO0000O0OO0 )#line:270
        dp .write_log ("镜像【{}】推送成功！".format (OOOO000OO0O000OO0 ))#line:271
        return public .returnMsg (True ,"推送成功！{}".format (str (O00O0O0O0000OO0OO )))#line:272
    def tag (OO00OOOO00O0O000O ,OO0OO0O0O0O0OOOOO ,O000O00OOO00OO0OO ,OOOO0O000OO0OOO0O ):#line:274
        ""#line:281
        O0OO00O0O0OOOO00O =OOOO0O000OO0OOO0O .split (":")[0 ]#line:282
        O0O00O00OOO00O00O =OOOO0O000OO0OOO0O .split (":")[1 ]#line:283
        OO00OOOO00O0O000O .docker_client (OO0OO0O0O0O0OOOOO ).images .get (O000O00OOO00OO0OO ).tag (repository =O0OO00O0O0OOOO00O ,tag =O0O00O00OOO00O00O )#line:287
        return public .returnMsg (True ,"设置成功")#line:288
    def pull (O00O000O0O0O000OO ,OO0OO0O0OOO0000OO ):#line:290
        ""#line:299
        public .writeFile (O00O000O0O0O000OO .__OOOOO00OOOOOO0000 ,"开始拉取镜像！")#line:300
        import docker .errors #line:301
        try :#line:302
            if ':'not in OO0OO0O0OOO0000OO .image :#line:303
                OO0OO0O0OOO0000OO .image ='{}:latest'.format (OO0OO0O0OOO0000OO .image )#line:304
            O0OO000O0O00OO0OO ={"username":OO0OO0O0OOO0000OO .username ,"password":OO0OO0O0OOO0000OO .password ,"registry":OO0OO0O0OOO0000OO .registry if OO0OO0O0OOO0000OO .registry else None }if OO0OO0O0OOO0000OO .username else None #line:308
            if not hasattr (OO0OO0O0OOO0000OO ,"tag"):#line:309
                OO0OO0O0OOO0000OO .tag =OO0OO0O0OOO0000OO .image .split (":")[-1 ]#line:310
            if OO0OO0O0OOO0000OO .registry !="docker.io":#line:311
                OO0OO0O0OOO0000OO .image ="{}/{}/{}".format (OO0OO0O0OOO0000OO .registry ,OO0OO0O0OOO0000OO .namespace ,OO0OO0O0OOO0000OO .image )#line:312
            O000000OOO0000OOO =dp .docker_client_low (OO0OO0O0OOO0000OO .url ).pull (repository =OO0OO0O0OOO0000OO .image ,auth_config =O0OO000O0O00OO0OO ,tag =OO0OO0O0OOO0000OO .tag ,stream =True )#line:318
            dp .log_docker (O000000OOO0000OOO ,"镜像拉取任务")#line:319
            if O000000OOO0000OOO :#line:320
                dp .write_log ("镜像【{}:{}】拉取成功！".format (OO0OO0O0OOO0000OO .image ,OO0OO0O0OOO0000OO .tag ))#line:321
                return public .returnMsg (True ,'拉取镜像成功.')#line:322
            else :#line:323
                return public .returnMsg (False ,'可能没有这个镜像.')#line:324
        except docker .errors .ImageNotFound as O0000OOO0OOO00OO0 :#line:325
            if "pull access denied for"in str (O0000OOO0OOO00OO0 ):#line:326
                return public .returnMsg (False ,"拉取失败，该镜像为私有镜像需要输入dockerhub的账号密码！")#line:327
            return public .returnMsg (False ,"拉取失败<br><br>原因: {}".format (O0000OOO0OOO00OO0 ))#line:329
        except docker .errors .NotFound as O0000OOO0OOO00OO0 :#line:331
            if "not found: manifest unknown"in str (O0000OOO0OOO00OO0 ):#line:332
                return public .returnMsg (False ,"拉取失败，仓库没有该镜像！")#line:333
            return public .returnMsg (False ,"拉取失败<br><br>原因: {}".format (O0000OOO0OOO00OO0 ))#line:334
        except docker .errors .APIError as O0000OOO0OOO00OO0 :#line:335
            if "invalid tag format"in str (O0000OOO0OOO00OO0 ):#line:336
                return public .returnMsg (False ,"拉取失败，镜像格式错误，格式应该为：nginx:v1！")#line:337
            return public .returnMsg (False ,"拉取失败！{}".format (O0000OOO0OOO00OO0 ))#line:338
    def pull_high_api (O0000O00O00OOOOOO ,OOOOOOO00OO0OOO0O ):#line:342
        ""#line:351
        import docker .errors #line:352
        try :#line:353
            if ':'not in OOOOOOO00OO0OOO0O .image :#line:354
                OOOOOOO00OO0OOO0O .image ='{}:latest'.format (OOOOOOO00OO0OOO0O .image )#line:355
            O00O000OO000OOOOO ={"username":OOOOOOO00OO0OOO0O .username ,"password":OOOOOOO00OO0OOO0O .password ,"registry":OOOOOOO00OO0OOO0O .registry if OOOOOOO00OO0OOO0O .registry else None }if OOOOOOO00OO0OOO0O .username else None #line:359
            if OOOOOOO00OO0OOO0O .registry !="docker.io":#line:361
                OOOOOOO00OO0OOO0O .image ="{}/{}/{}".format (OOOOOOO00OO0OOO0O .registry ,OOOOOOO00OO0OOO0O .namespace ,OOOOOOO00OO0OOO0O .image )#line:362
            OO0O00O0OOO000O0O =O0000O00O00OOOOOO .docker_client (OOOOOOO00OO0OOO0O .url ).images .pull (repository =OOOOOOO00OO0OOO0O .image ,auth_config =O00O000OO000OOOOO ,)#line:366
            if OO0O00O0OOO000O0O :#line:367
                return public .returnMsg (True ,'拉取镜像成功.')#line:368
            else :#line:369
                return public .returnMsg (False ,'可能没有这个镜像.')#line:370
        except docker .errors .ImageNotFound as OOOOO000000000O00 :#line:371
            if "pull access denied for"in str (OOOOO000000000O00 ):#line:372
                return public .returnMsg (False ,"拉取失败，该镜像为私有镜像需要输入dockerhub的账号密码！")#line:373
            return public .returnMsg (False ,"拉取失败<br><br>原因: {}".format (OOOOO000000000O00 ))#line:374
    def image_for_host (O00OOO00000O0OO0O ,OO000000000OOOO0O ):#line:376
        ""#line:381
        O0OOOO00OO0OO000O =O00OOO00000O0OO0O .image_list (OO000000000OOOO0O )#line:382
        if not O0OOOO00OO0OO000O ['status']:#line:383
            return O0OOOO00OO0OO000O #line:384
        OOOOO00OO0000OOO0 =len (O0OOOO00OO0OO000O ['msg']['images_list'])#line:385
        O000OOOOOOO00O00O =0 #line:386
        for O00OO00O00O0O00OO in O0OOOO00OO0OO000O ['msg']['images_list']:#line:387
            O000OOOOOOO00O00O +=O00OO00O00O0O00OO ['size']#line:388
        return public .returnMsg (True ,{'num':OOOOO00OO0000OOO0 ,'size':O000OOOOOOO00O00O })