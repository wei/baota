#!/usr/bin/python
from projectModel .base import projectBase #line:12
from projectModel import scanningModel #line:13
import sys ,json ,os ,public ,hashlib ,requests ,time #line:14
from BTPanel import cache #line:15
class main (projectBase ):#line:17
    __OO0O00O000OOO0000 =scanningModel .main ()#line:18
    __OO00OO0OOOOO0O00O =0 #line:19
    __OOO0000OO0OOO0O0O ="/www/server/panel/data/webshell_check_shell.txt"#line:20
    def GetWebInfo (O00OOO000O0O0O0O0 ,O00OO000O0O00O00O ):#line:22
        ""#line:28
        O000000OOOOOOOO00 =public .M ('sites').where ('project_type=? and name=?',('PHP',O00OO000O0O00O00O .name )).count ()#line:29
        if not O000000OOOOOOOO00 :return False #line:30
        O000000OOOOOOOO00 =public .M ('sites').where ('project_type=? and name=?',('PHP',O00OO000O0O00O00O .name )).select ()#line:31
        return O000000OOOOOOOO00 [0 ]#line:32
    def ScanWeb (O0000O00O0OOOO00O ,OOOO0000OO0OOO000 ):#line:35
        ""#line:41
        if '_ws'in OOOO0000OO0OOO000 :OOOO0000OO0OOO000 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOO0000OO0OOO000 .ws_callback ,"info":"正在扫描 %s 网站漏洞"%OOOO0000OO0OOO000 .name ,"type":"vulscan"}))#line:42
        OO000O0OO0000OO0O =O0000O00O0OOOO00O .__OO0O00O000OOO0000 .startScanWeb (OOOO0000OO0OOO000 )#line:43
        if OO000O0OO0000OO0O ['msg'][0 ]['is_vufix']:#line:44
            if '_ws'in OOOO0000OO0OOO000 :OOOO0000OO0OOO000 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOO0000OO0OOO000 .ws_callback ,"info":"网站 %s 存在漏洞"%OOOO0000OO0OOO000 .name ,"type":"vulscan","is_error":True }))#line:45
            return OO000O0OO0000OO0O ['msg'][0 ]['cms']#line:46
        return {}#line:47
    def WebSSlSecurity (O0O00OOOOO00O0O00 ,O0OOOOO0OO0OOO0OO ,OO0OOO00O00O0OO00 ):#line:49
        ""#line:55
        if public .get_webserver ()=='nginx':#line:56
            O00O0000000O00OO0 ='/www/server/panel/vhost/nginx/{}.conf'.format (O0OOOOO0OO0OOO0OO ['name'])#line:57
            if os .path .exists (O00O0000000O00OO0 ):#line:58
                OOOOOO0OO0OOOO0O0 =public .ReadFile (O00O0000000O00OO0 )#line:59
                if 'TLSv1 'in OOOOOO0OO0OOOO0O0 :#line:60
                    if '_ws'in OO0OOO00O00O0OO00 :OO0OOO00O00O0OO00 ._ws .send (public .getJson ({"end":False ,"ws_callback":OO0OOO00O00O0OO00 .ws_callback ,"info":"【%s】 网站启用了不安全的TLS1协议"%O0OOOOO0OO0OOO0OO ['name'],"type":"webscan","is_error":True ,"dangerous":2 }))#line:63
                    O0OOOOO0OO0OOO0OO ['result']['webscan'].append ({"name":"【%s】 网站启用了不安全的TLS1协议"%O0OOOOO0OO0OOO0OO ['name'],"repair":"修复方案：打开配置文件去掉TLS1","dangerous":2 })#line:64
    def WebInfoDisclosure (O0O00O0O00OOOO00O ,OOOO0OO0000O00OO0 ):#line:68
        ""#line:74
        if '_ws'in OOOO0OO0000O00OO0 :OOOO0OO0000O00OO0 ._ws .send (public .getJson ({"end":False ,"callback":OOOO0OO0000O00OO0 .ws_callback ,"info":"正在扫描 %s 网站配置安全性"%OOOO0OO0000O00OO0 .name ,"type":"webscan"}))#line:76
        OOO000O0OO00OOOOO =[]#line:77
        if public .get_webserver ()=='nginx':#line:78
            OO0OOO0O00O000000 ='/www/server/nginx/conf/nginx.conf'#line:79
            if os .path .exists (OO0OOO0O00O000000 ):#line:80
                OOO00OO0OO00OO0O0 =public .ReadFile (OO0OOO0O00O000000 )#line:81
                if not 'server_tokens off'in OOO00OO0OO00OO0O0 :#line:82
                    OOO000O0OO00OOOOO .append ({"name":"Nginx存在版本信息泄露","repair":"打开nginx.conf配置文件，在http { }里加上： server_tokens off;","dangerous":1 })#line:83
        O0OOO00000OOO0000 =public .get_site_php_version (OOOO0OO0000O00OO0 .name )#line:84
        OOO0O0000OO0OO0O0 ='/www/server/php/%s/etc/php.ini'%O0OOO00000OOO0000 #line:85
        if os .path .exists (OOO0O0000OO0OO0O0 ):#line:86
            OOOOOOO0OO0O00000 =public .ReadFile (OOO0O0000OO0OO0O0 )#line:87
            if not 'expose_php = Off'in OOOOOOO0OO0O00000 :#line:88
                OOO000O0OO00OOOOO .append ({"name":"PHP %s 存在版本信息泄露"%O0OOO00000OOO0000 ,"repair":"修复方案：打开php.ini配置文件，设置expose_php = Off","dangerous":1 })#line:89
        if '_ws'in OOOO0OO0000O00OO0 :OOOO0OO0000O00OO0 ._ws .send (public .getJson ({"end":False ,"callback":OOOO0OO0000O00OO0 .ws_callback ,"info":"扫描 %s 网站配置安全性完成"%OOOO0OO0000O00OO0 .name ,"type":"webscan"}))#line:92
        return OOO000O0OO00OOOOO #line:93
    def _send_task (O0OO0O0OOO0OOO0O0 ,O0OOOO0O00OO00O0O ):#line:96
        ""#line:102
        import panelAuth #line:103
        OOOOOOO0O0O00OO0O =panelAuth .panelAuth ().create_serverid (None )#line:104
        OOOOOOO0O0O00OO0O ['url']=O0OOOO0O00OO00O0O #line:105
        try :#line:106
            O00O0O0O00OOOO0O0 =public .httpPost ("http://www.bt.cn/api/local/boce",OOOOOOO0O0O00OO0O ,10 )#line:107
            O00O0O0O00OOOO0O0 =json .loads (O00O0O0O00OOOO0O0 )#line:108
            return O00O0O0O00OOOO0O0 #line:109
        except :#line:110
            return False #line:111
    def WebBtBoce (O0O0OOO0OOO0O00OO ,OOOOOOO0OOO00O000 ,OO0000OOOOO0O000O ):#line:114
        ""#line:120
        OO0000OOOOO0O000O ['result']['boce']=[]#line:121
        for O0OO0000OOO00OO0O in OOOOOOO0OOO00O000 .url :#line:122
            if O0OO0000OOO00OO0O .find ('http://')==-1 and O0OO0000OOO00OO0O .find ('https://')==-1 :continue #line:123
            if '_ws'in OOOOOOO0OOO00O000 :OOOOOOO0OOO00O000 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOOOOO0OOO00O000 .ws_callback ,"info":"正在对URL %s 进行拨测"%O0OO0000OOO00OO0O ,"type":"boce"}))#line:125
            OOO0O0OOO00OO0OOO =O0O0OOO0OOO0O00OO ._send_task (OOOOOOO0OOO00O000 .url )#line:126
            if '_ws'in OOOOOOO0OOO00O000 :OOOOOOO0OOO00O000 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOOOOO0OOO00O000 .ws_callback ,"info":OOO0O0OOO00OO0OOO ,"type":"boce"}))#line:128
            if OOO0O0OOO00OO0OOO :#line:129
                OO0000OOOOO0O000O ['result']['boce'].append (OOO0O0OOO00OO0OOO )#line:130
    def WebFilePermission (O000OO00O00O000O0 ,OOO0OO00O00OOOO00 ,O0OOOOOO00O0OOOO0 ):#line:132
        ""#line:138
        import pwd #line:139
        OOOOOOOOO000O00OO =[]#line:140
        for O0O0OOO0O000O000O in os .listdir (OOO0OO00O00OOOO00 ['path']):#line:141
            OOOO0OOOOO0OOO000 =os .path .join (OOO0OO00O00OOOO00 ['path'],O0O0OOO0O000O000O )#line:142
            if os .path .isdir (OOOO0OOOOO0OOO000 ):#line:143
                OOOOOOOOO000O00OO .append (OOOO0OOOOO0OOO000 )#line:144
                for O00OO00O0OO0OOO0O in os .listdir (OOOO0OOOOO0OOO000 ):#line:145
                    O0000OOOOOOO00OOO =OOOO0OOOOO0OOO000 +'/'+O00OO00O0OO0OOO0O #line:146
                    if os .path .isdir (O0000OOOOOOO00OOO ):#line:147
                        OOOOOOOOO000O00OO .append (O0000OOOOOOO00OOO )#line:148
        if len (OOOOOOOOO000O00OO )>=1 :#line:149
            for O00OO00OOO000O00O in OOOOOOOOO000O00OO :#line:150
                if not os .path .exists (O00OO00OOO000O00O ):continue #line:151
                OO0O00O0OOOOO00OO =os .stat (O00OO00OOO000O00O )#line:152
                if int (oct (OO0O00O0OOOOO00OO .st_mode )[-3 :])==777 :#line:153
                    if '_ws'in O0OOOOOO00O0OOOO0 :O0OOOOOO00O0OOOO0 ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OOOOOO00O0OOOO0 .ws_callback ,"info":"  【%s】 目录权限错误"%O00OO00OOO000O00O ,"repair":"设置 【%s】 目录为755"%O00OO00OOO000O00O ,"type":"webscan","is_error":True ,"dangerous":1 }))#line:156
                    OOO0OO00O00OOOO00 ['result']['webscan'].append ({"name":"  【%s】 目录权限错误"%O00OO00OOO000O00O ,"repair":"修复方案：设置 【%s】 目录为755"%O00OO00OOO000O00O ,"dangerous":1 })#line:157
                if pwd .getpwuid (OO0O00O0OOOOO00OO .st_uid ).pw_name !='www':#line:158
                    if '_ws'in O0OOOOOO00O0OOOO0 :O0OOOOOO00O0OOOO0 ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OOOOOO00O0OOOO0 .ws_callback ,"info":"  【%s】 目录权限错误"%O00OO00OOO000O00O ,"repair":"修复方案：设置 【%s】 目录的用户权限为www"%O00OO00OOO000O00O ,"type":"webscan","is_error":True ,"dangerous":1 }))#line:161
                    OOO0OO00O00OOOO00 ['result']['webscan'].append ({"name":"  【%s】 目录用户权限错误"%O00OO00OOO000O00O ,"repair":"设置 【%s】 目录的用户权限为www"%O00OO00OOO000O00O ,"dangerous":1 })#line:162
    def Getdir (O0OOOO0OO0OO0OOO0 ,OO00OO0O0O0O00OO0 ):#line:165
        ""#line:171
        O0O0O0OO000OO0OOO =[]#line:172
        O000O0OOOOO00OOO0 =[]#line:173
        [[O0O0O0OO000OO0OOO .append (os .path .join (OO0000O00O000000O ,OO00O0OO0000OO0O0 ))for OO00O0OO0000OO0O0 in OO000O000O000O000 ]for OO0000O00O000000O ,OOOO0OOO0OO0OO000 ,OO000O000O000O000 in os .walk (OO00OO0O0O0O00OO0 )]#line:174
        for OOO0O000OO00OOO0O in O0O0O0OO000OO0OOO :#line:175
            if str (OOO0O000OO00OOO0O .lower ())[-4 :]=='.php':#line:176
                O000O0OOOOO00OOO0 .append (OOO0O000OO00OOO0O )#line:177
        return O000O0OOOOO00OOO0 #line:178
    def ReadFile (O000O0O0O0OO0OOO0 ,OO0O0O000O00OO00O ,mode ='r'):#line:180
        ""#line:186
        import os #line:187
        if not os .path .exists (OO0O0O000O00OO00O ):return False #line:188
        try :#line:189
            O0O00OO0OOOO0OO0O =open (OO0O0O000O00OO00O ,mode )#line:190
            OOO00O0O0OO00O0OO =O0O00OO0OOOO0OO0O .read ()#line:191
            O0O00OO0OOOO0OO0O .close ()#line:192
        except Exception as OO0OO000O000OOOO0 :#line:193
            if sys .version_info [0 ]!=2 :#line:194
                try :#line:195
                    O0O00OO0OOOO0OO0O =open (OO0O0O000O00OO00O ,mode ,encoding ="utf-8")#line:196
                    OOO00O0O0OO00O0OO =O0O00OO0OOOO0OO0O .read ()#line:197
                    O0O00OO0OOOO0OO0O .close ()#line:198
                except Exception as O0OO000OO0OOO0O00 :#line:199
                    return False #line:200
            else :#line:201
                return False #line:202
        return OOO00O0O0OO00O0OO #line:203
    def FileMd5 (O0OO0000OO00O00OO ,O0000OO0000OOOOO0 ):#line:205
        ""#line:211
        if os .path .exists (O0000OO0000OOOOO0 ):#line:212
            with open (O0000OO0000OOOOO0 ,'rb')as O0OOOO0OOOOOOOO0O :#line:213
                O000O0000OOOOO000 =O0OOOO0OOOOOOOO0O .read ()#line:214
            O0O00O0OO0OOOO0O0 =hashlib .md5 (O000O0000OOOOO000 ).hexdigest ()#line:215
            return O0O00O0OO0OOOO0O0 #line:216
        else :#line:217
            return False #line:218
    def WebshellChop (OO0O0O0O00OOO0OOO ,O00OOOO0OO0O00O0O ,O0O0O0O0OO0000000 ,O0O00O00O000OOOOO ):#line:220
        ""#line:227
        try :#line:228
            OO0OO00000O00O00O =O0O0O0O0OO0000000 #line:229
            O0000OO0O000OOOOO =os .path .getsize (O00OOOO0OO0O00O0O )#line:230
            if O0000OO0O000OOOOO >1024000 :return False #line:231
            O0OO0000O0OO0O00O ={'inputfile':OO0O0O0O00OOO0OOO .ReadFile (O00OOOO0OO0O00O0O ),"md5":OO0O0O0O00OOO0OOO .FileMd5 (O00OOOO0OO0O00O0O )}#line:232
            public .print_log ("参数: "+json .dumps (O0OO0000O0OO0O00O ))#line:233
            public .print_log ("URL "+OO0OO00000O00O00O )#line:234
            public .print_log (OO0O0O0O00OOO0OOO .FileMd5 (O00OOOO0OO0O00O0O )+" "+O00OOOO0OO0O00O0O )#line:235
            OO0OOOO0O0OOOOO0O =requests .post (OO0OO00000O00O00O ,O0OO0000O0OO0O00O ,timeout =20 ).json ()#line:236
            public .print_log ("返回:  "+json .dumps (OO0OOOO0O0OOOOO0O ))#line:237
            if OO0OOOO0O0OOOOO0O ['msg']=='ok':#line:238
                if (OO0OOOO0O0OOOOO0O ['data']['data']['level']==5 ):#line:239
                    return True #line:240
                return False #line:241
        except :#line:242
            return False #line:243
    def GetCheckUrl (OOO0O000O0OOO00OO ):#line:245
        ""#line:250
        try :#line:251
            OO000O0O0OOOO00OO =requests .get ('http://www.bt.cn/checkWebShell.php').json ()#line:252
            if OO000O0O0OOOO00OO ['status']:#line:253
                return OO000O0O0OOOO00OO ['url']#line:254
            return False #line:255
        except :#line:256
            return False #line:257
    def UploadShell (O0000O000O0OOOO0O ,O00O00O000OOO00OO ,OOOO0O000O00O0000 ,OO0OOO0OO0O00O000 ):#line:259
        ""#line:265
        if len (O00O00O000OOO00OO )==0 :return []#line:266
        OOO0O00OO00OO00O0 =O0000O000O0OOOO0O .GetCheckUrl ()#line:267
        if not OOO0O00OO00OO00O0 :return []#line:268
        OO00O00OOO000O0OO =0 #line:269
        OO000OO00O0000000 =0 #line:270
        O00OOO00O00OOOO00 =[]#line:271
        if os .path .exists (O0000O000O0OOOO0O .__OOO0000OO0OOO0O0O ):#line:272
            OO000OO00O0000000 =1 #line:273
            try :#line:274
                O00OOO00O00OOOO00 =json .loads (public .ReadFile (O0000O000O0OOOO0O .__OOO0000OO0OOO0O0O ))#line:275
            except :#line:276
                public .WriteFile (O0000O000O0OOOO0O .__OOO0000OO0OOO0O0O ,[])#line:277
                OO000OO00O0000000 =0 #line:278
        for OO0OOO0000OO000OO in O00O00O000OOO00OO :#line:279
            OO00O00OOO000O0OO +=1 #line:280
            if '_ws'in OOOO0O000O00O0000 :OOOO0O000O00O0000 ._ws .send (public .getJson ({"end":False ,"callback":OOOO0O000O00O0000 .ws_callback ,"info":"正在扫描文件是否是木马%s"%OO0OOO0000OO000OO ,"type":"webscan","count":O0000O000O0OOOO0O .__OO00OO0OOOOO0O00O ,"is_count":OO00O00OOO000O0OO }))#line:282
            if OO000OO00O0000000 :#line:284
                if OO0OOO0000OO000OO in O00OOO00O00OOOO00 :continue #line:285
            if O0000O000O0OOOO0O .WebshellChop (OO0OOO0000OO000OO ,OOO0O00OO00OO00O0 ,OOOO0O000O00O0000 ):#line:286
                if '_ws'in OOOO0O000O00O0000 :OOOO0O000O00O0000 ._ws .send (public .getJson ({"end":False ,"callback":OOOO0O000O00O0000 .ws_callback ,"info":"%s 网站木马扫描发现当前文件为木马文件%s"%(OOOO0O000O00O0000 .name ,len (OO0OOO0OO0O00O000 ['result']['webshell'])),"type":"webscan","count":O0000O000O0OOOO0O .__OO00OO0OOOOO0O00O ,"is_count":OO00O00OOO000O0OO ,"is_error":True }))#line:290
                OO0OOO0OO0O00O000 ['result']['webshell'].append (OO0OOO0000OO000OO )#line:291
        if '_ws'in OOOO0O000O00O0000 :OOOO0O000O00O0000 ._ws .send (public .getJson ({"end":False ,"callback":OOOO0O000O00O0000 .ws_callback ,"info":"%s 网站木马扫描完成共发现 %s 个木马文件"%(OOOO0O000O00O0000 .name ,len (OO0OOO0OO0O00O000 ['result']['webshell'])),"type":"webscan","count":O0000O000O0OOOO0O .__OO00OO0OOOOO0O00O ,"is_count":OO00O00OOO000O0OO }))#line:293
    def GetDirList (OOO00O000OO0O0OO0 ,OOO0O00OOO00OOO00 ):#line:296
        ""#line:300
        if os .path .exists (str (OOO0O00OOO00OOO00 )):#line:301
            return OOO00O000OO0O0OO0 .Getdir (OOO0O00OOO00OOO00 )#line:302
        else :#line:303
            return False #line:304
    def SanDir (O0OO0000OOO0OOOOO ,O00OOOO0OO0OOOOOO ,OOOOOO0O00OO00000 ):#line:306
        ""#line:312
        O0OO0000OOO0OOOOO .__OO00OO0OOOOO0O00O =0 #line:313
        O0000000000OO0000 =O0OO0000OOO0OOOOO .GetDirList (O00OOOO0OO0OOOOOO ['path'])#line:314
        if not O0000000000OO0000 :#line:315
            return []#line:316
        O0OO0000OOO0OOOOO .__OO00OO0OOOOO0O00O =len (O0000000000OO0000 )#line:318
        O0O0O0O0OOOO0O0OO =O0OO0000OOO0OOOOO .UploadShell (O0000000000OO0000 ,OOOOOO0O00OO00000 ,O00OOOO0OO0OOOOOO )#line:319
        return O0O0O0O0OOOO0O0OO #line:320
    def UpdateWubao (O00OOO0OOO00O00O0 ,OOOOO0OO000O0OOOO ):#line:322
        ""#line:327
        if not os .path .exists (O00OOO0OOO00O00O0 .__OOO0000OO0OOO0O0O ):#line:328
            public .WriteFile (O00OOO0OOO00O00O0 .__OOO0000OO0OOO0O0O ,[OOOOO0OO000O0OOOO .strip ()])#line:329
        else :#line:330
            try :#line:331
                O0000OO00O0O0O0OO =json .loads (public .ReadFile (O00OOO0OOO00O00O0 .__OOO0000OO0OOO0O0O ))#line:332
                if not OOOOO0OO000O0OOOO in O0000OO00O0O0O0OO :#line:333
                    O0000OO00O0O0O0OO .append (OOOOO0OO000O0OOOO )#line:334
                    public .WriteFile (O00OOO0OOO00O00O0 .__OOO0000OO0OOO0O0O ,json .dumps (O0000OO00O0O0O0OO ))#line:335
            except :#line:336
                pass #line:337
    def SendWubao (O0O0OO0000OOO0O0O ,O000O00OOOOOO000O ):#line:340
        ""#line:345
        OO0000OOO00OO0OOO =json .loads (public .ReadFile ('/www/server/panel/data/userInfo.json'))#line:346
        O0O000O0OOO0000O0 ='http://www.bt.cn/api/bt_waf/reportTrojanError'#line:347
        O0O0OO0000OOO0O0O .UpdateWubao (filename =O000O00OOOOOO000O .filename )#line:348
        OO0000OOOO000OOO0 ={'name':O000O00OOOOOO000O .filename ,'inputfile':O0O0OO0000OOO0O0O .ReadFile (O000O00OOOOOO000O .filename ),"md5":O0O0OO0000OOO0O0O .FileMd5 (O000O00OOOOOO000O .filename ),"access_key":OO0000OOO00OO0OOO ['access_key'],"uid":OO0000OOO00OO0OOO ['uid']}#line:349
        OO00OOO0OO000OO00 =public .httpPost (O0O000O0OOO0000O0 ,OO0000OOOO000OOO0 )#line:350
        return public .returnMsg (True ,"提交误报完成")#line:351
    def WebShellKill (OOO00O0O0O00OO0O0 ,OO0OOO00OO0000O0O ,O0OOO000OOOOOO00O ):#line:354
        ""#line:360
        O0OOO000OOOOOO00O ['result']['webshell']=[]#line:361
        OOO00O0O0O00OO0O0 .SanDir (O0OOO000OOOOOO00O ,OO0OOO00OO0000O0O )#line:362
    def WebFileDisclosure (O0O0OOOO000000O00 ,OOO00O0O0000OOO0O ,O0O00O0OOOOOOO000 ):#line:365
        ""#line:371
        OOO00O0O0000OOO0O ['result']['filescan']=[]#line:372
        for OOOO0O00OOO0O0OOO in os .listdir (OOO00O0O0000OOO0O ['path']):#line:373
            OOOOOO0OO00OO00OO =os .path .join (OOO00O0O0000OOO0O ['path'],OOOO0O00OOO0O0OOO )#line:374
            if os .path .isfile (OOOOOO0OO00OO00OO ):#line:375
                if OOOOOO0OO00OO00OO .endswith (".sql"):#line:376
                    OOO00O0O0000OOO0O ['result']['filescan'].append ({"name":"  【%s】 网站根目录存在sql备份文件%s"%(OOO00O0O0000OOO0O ['name'],OOOOOO0OO00OO00OO ),"repair":"修复方案：转移到其他目录或者下载到本地","dangerous":2 })#line:379
                if OOOOOO0OO00OO00OO .endswith (".zip")or OOOOOO0OO00OO00OO .endswith (".gz")or OOOOOO0OO00OO00OO .endswith (".tar")or OOOOOO0OO00OO00OO .endswith (".7z"):#line:380
                    if OOO00O0O0000OOO0O ['name']in OOOOOO0OO00OO00OO :#line:381
                        if '_ws'in O0O00O0OOOOOOO000 :O0O00O0OOOOOOO000 ._ws .send (public .getJson ({"end":False ,"ws_callback":O0O00O0OOOOOOO000 .ws_callback ,"info":"  【%s】 网站根目录存在备份文件 %s"%(OOO00O0O0000OOO0O ['name'],OOOOOO0OO00OO00OO ),"type":"filescan","is_error":True ,"dangerous":2 }))#line:384
                        OOO00O0O0000OOO0O ['result']['filescan'].append ({"name":"  【%s】 网站根目录存在备份文件 %s"%(OOO00O0O0000OOO0O ['name'],OOOOOO0OO00OO00OO ),"repair":"修复方案：转移到其他目录或者下载到本地","dangerous":2 })#line:385
    def IsBackupSite (OO000O0OO0O00O00O ,OOO00O0OOOOO00000 ):#line:387
        ""#line:392
        import crontab #line:393
        O00000OO00O0O0O0O =crontab .crontab ()#line:394
        OO0OOOOOO00OOOOOO =O00000OO00O0O0O0O .GetCrontab (None )#line:395
        for OO00OO000O0OOO0O0 in OO0OOOOOO00OOOOOO :#line:396
            if OO00OO000O0OOO0O0 ['sType']=='site':#line:397
                if OO00OO000O0OOO0O0 ['sName']=='ALL':#line:398
                    return True #line:399
                if OO00OO000O0OOO0O0 ['sName']==OOO00O0OOOOO00000 :#line:400
                    return True #line:401
        return False #line:402
    def WebBackup (O0OOOOO0O000O0O00 ,OO0O00O00O0O00O00 ,OOO00OOOOO0OOOOO0 ):#line:404
        ""#line:410
        OO0O00O00O0O00O00 ['result']['backup']=[]#line:411
        if not O0OOOOO0O000O0O00 .IsBackupSite (OO0O00O00O0O00O00 ['name']):#line:412
            if '_ws'in OOO00OOOOO0OOOOO0 :OOO00OOOOO0OOOOO0 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOO00OOOOO0OOOOO0 .ws_callback ,"info":"修复方案：【%s】 在计划任务中创建备份网站任务"%OO0O00O00O0O00O00 ['name'],"type":"backup","is_error":True ,"dangerous":2 }))#line:413
            OO0O00O00O0O00O00 ['result']['backup'].append ({"name":"  【%s】 缺少计划任务备份"%(OO0O00O00O0O00O00 ['name']),"repair":"修复方案：【%s】 在计划任务中创建备份网站任务"%OO0O00O00O0O00O00 ['name'],"dangerous":2 })#line:414
    def GetLevelRule (O000OOO0O0O0OOOO0 ,OO0O0OOO0O0O0O0OO ):#line:416
        OOO000OOOOOOOOOOO =[]#line:417
        O0OOOOOO0OOO0O00O =['364c2b553559697066445638','364c2b55354c326a66445638','3537364f3561577a66444577664f694a7375614468513d3d','365a79793649533466444977664f694a7375614468513d3d','36594b41364b2b3366444d7766413d3d','353436773659655266444d77664f574e6d75573971513d3d','63444a7766444d77664f6976694f6d716c773d3d','354c6974357061483561325835626d5666444d77664f694a7375614468513d3d','356232703536576f66445577664f574e6d75573971513d3d','364c53743562327066445577664f574e6d75573971513d3d','356f715635724f6f66445577664f574e6d75573971513d3d','354c71613559326166445577664f574e6d75573971513d3d','354c71613570435066445577664f574e6d75573971513d3d','357065673536434266445977664f694a7375614468513d3d','3570794a3536434266445977664f694a7375614468513d3d','35594733356f754e66445977664f694a7375614468513d3d','35705376354c755966445977664f57626d2b615775656155722b53376d413d3d','356f6951354c713635623278364b654766446377664f694a7375614468513d3d','356f6951354c7136353553313562327866446377664f694a7375614468513d3d','3662754536496d79353732523536755a66446377664f694a7375614468513d3d','3571796e3537364f3562656f354c6d7a66446377664f694a7375614468513d3d','35367973354c6941354c7961356f6d4166446377664f694a7375614468513d3d','36496d79356f4f4666446377664f694a7375614468513d3d','355a7539354c716e51585a384e7a423836496d79356f4f46','354c71613572537951585a384e7a423836496d79356f4f46','3570656c3570797359585a384e7a423836496d79356f4f46','354c6941357079733659475466446377664f694a7375614468513d3d','357065683536434266446377664f694a7375614468513d3d','354c6d463649324a66446377664f694a7375614468513d3d','356f32563662473866446377664f574e6d75573971513d3d','36494342364a6d4f3570793666446377664f574e6d75573971513d3d','35714f4c35346d4d66446377664f574e6d75573971513d3d','36492b6736492b6366446377664f574e6d75573971513d3d','3572367a365a656f66446377664f574e6d75573971513d3d','356f2b513534367766446377664f574e6d75573971513d3d','35615371365a697a355a2b4f66446377664f574e6d75573971513d3d','354c716b35706954356f6d4166446377664f6d376b656542734f533670773d3d','354c756c35615371355a324b6644637766413d3d','3559574e3536322b3537716d66446777664f57626d2b615775656155722b53376d413d3d','3537712f364c657635714f413572574c6644677766413d3d','355932613562327066446777664f574e6d75573971513d3d','364c574d365a4b7866446777664f574e6d75573971513d3d','35616978354c6d51355a793666446777664f574e6d75573971513d3d','624739755a7a68384f4442383559326135623270','3572367a365a656f35615371365a697a355a2b4f66446777664f574e6d75573971513d3d','364a4768354c717366446731664f574e6d75573971513d3d','3659655235724b5a66446731664f574e6d75573971513d3d','365a4f3235724b7a66446731664f574e6d75573971513d3d','3537712f354c694b354c694c35724f6f66446731664f574e6d75573971513d3d','35616978354c6d51355a2b4f66446b77664f574e6d75573971513d3d','3571796e354c7161355a7539365a6d4666446b77664f574e6d75573971513d3d','354c715335593261355a7539365a6d4666446b77664f574e6d75573971513d3d','354c6948364c4771355a7539365a6d4666446b77664f574e6d75573971513d3d','354c6948354c6977355a7539365a6d4666446b77664f574e6d75573971513d3d','354c716135593261355a7539365a6d4666446b77664f574e6d75573971513d3d','355a75623570613535705376354c755966446b77664f57626d2b615775656155722b53376d413d3d','35616942356243383570617666446b31664f574e6d75573971513d3d','35706177364a4768354c717366446b35664f574e6d75573971513d3d','364c574d355a793666446b35664f574e6d75573971513d3d','364c574d3559326166446b35664f574e6d75573971513d3d','35706532357065323562327066446b77664f574e6d75573971513d3d','35595774355a43493562327066446b35664f574e6d75573971513d3d','35616962357169433561433066446777664f574e6d75573971513d3d','3559574e3536322b35705376354c755966446777664f57626d2b615775656155722b53376d413d3d','364c53333571792b66446377664f6976694f6d716c773d3d','35726958365943503572574c364b2b5666445577664f6d376b656542734f533670773d3d','35705337365a697966445577664f6d376b656542734f533670773d3d','35356d39356269393561325166445577664f6d376b656542734f533670773d3d','36627552356269393561325166446377664f6d376b656542734f533670773d3d','35377169356269393561325166445977664f6d376b656542734f533670773d3d','3559614635373252357269583659435066445977664f6d376b656542734f533670773d3d','3559574e3570324166446777664f6d376b656542734f533670773d3d','35727950357253653562656c3559573366446777664f6d376b656542734f533670773d3d','56325669357269583659435066446777664f6d376b656542734f533670773d3d','36594347355a435266446777664f6d376b656542734f533670773d3d','366275523561366966445977664f6d376b656542734f533670773d3d','357036423561366966445177664f6d376b656542734f533670773d3d','35705777356f3275355a53753559325766446377664f6d376b656542734f533670773d3d','353665523561326d354c694b3537325266446b7766465a5154673d3d','35372b3735614b5a66446b7766465a5154673d3d','353732523537756335597167365943666644597766465a5154673d3d','566c424f66446b7766465a5154673d3d','55314e5366446b7766465a5154673d3d','35714b763561325166446b7766465a5154673d3d','646a4a7959586c384f544238566c424f','3559716736594366355a6d6f6644637766465a5154673d3d','3659573436595734354c6d7a66446b7766465a5154673d3d','626d56306432397961794277636d3934655877334d4878575545343d','3559364c355971623572574c364b2b5666446b77664f6d376b656542734f533670773d3d','3572574c3559364c66445177664f6d376b656542734f533670773d3d','35627941356f692f364b36773562325666445977664f6d376b656542734f533670773d3d','35613661354c324e354c2b68356f477666445977664f6d376b656542734f533670773d3d','364b36773562325635702b6c364b2b6966445177664f6d376b656542734f533670773d3d','3659575335627158364b36773562325666446777664f6d376b656542734f533670773d3d','355a794c365a716266444d77664f6976694f6d716c773d3d','356f7156364c4f4866445177664f6976694f6d716c773d3d','356f6951354c713666445977664f694a7375614468513d3d','353665423570794e66446377664f6d376b656542734f533670773d3d','35373252364c533366446377664f6976694f6d716c773d3d','364c326d364c533366446377664f6976694f6d716c773d3d','355943663571792b66446377664f6976694f6d716c773d3d','355969473570796666446377664f6976694f6d716c773d3d','35364342355a574766445531664f57626d2b615775656155722b53376d413d3d','35705376354c755935626d7a35592b7766446b77664f57626d2b615775656155722b53376d413d3d','35705376354c7559356f366c35592b6a66446b77664f57626d2b615775656155722b53376d413d3d','51584277356271553535536f3559694735592b526644597766413d3d','364b69383559693466445177664f6976694f6d716c773d3d','3649324a3571613066446377664f694a7375614468513d3d','35712b5535346d353562694266445977664f6d376b656542734f533670773d3d','56564e45564877324d487a707535486e6762446b7571633d','3535577135592b333537325266445977664f694a7375614468513d3d','3535577135592b333561536e3559576f66445977664f694a7375614468513d3d','3535577135592b333562715466445977664f694a7375614468513d3d','3535577135592b33357043633537536966445977664f694a7375614468513d3d','5156626c7062506c763664384e6a423836496d79356f4f46','356136463535533335366150355969703536532b66445977664f694a7375614468513d3d']#line:418
        for O0OOO0O000O0O0OO0 in O0OOOOOO0OOO0O00O :#line:419
            OOO000OOOOOOOOOOO .append (public .en_hexb (O0OOO0O000O0O0OO0 ).split ('|'))#line:420
        return OOO000OOOOOOOOOOO #line:421
    def WebIndexSecurity (OO00O000OOO000OOO ,OOO00O0O0OOOOOO00 ):#line:423
        ""#line:429
        O00O000OO0O0O0O0O =[]#line:430
        if 'urllist'in OOO00O0O0OOOOOO00 :#line:431
            O0OO00000O0O0O00O =OO00O000OOO000OOO .GetLevelRule (None )#line:432
            for O0OOO0000000OOO0O in OOO00O0O0OOOOOO00 .urllist :#line:433
                try :#line:434
                    if not O0OOO0000000OOO0O .find ('http://')==-1 and O0OOO0000000OOO0O .find ('https://')==-1 :#line:435
                        if '_ws'in OOO00O0O0OOOOOO00 :OOO00O0O0OOOOOO00 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOO00O0O0OOOOOO00 .ws_callback ,"info":"正在对URL %s 进行内容风险检测"%OOO00O0O0OOOOOO00 .url ,"type":"index","is_error":True }))#line:436
                        O0O00OO0O0O0OO0OO =requests .get (url =O0OOO0000000OOO0O ,verify =False )#line:437
                        O00OO000O0OO0000O =O0O00OO0O0O0OO0OO .text #line:438
                        O0OO000OO0O0000O0 =0 #line:439
                        O00O0OO0O0O0O0000 =[]#line:440
                        for O0OO00O00O0O00000 in O0OO00000O0O0O00O :#line:441
                            if O0OO00O00O0O00000 [0 ]in O00OO000O0OO0000O :#line:442
                                O0OO000OO0O0000O0 +=int (O0OO00O00O0O00000 [1 ])#line:443
                                O00O0OO0O0O0O0000 .append (O0OO00O00O0O00000 [0 ])#line:444
                        if O0OO000OO0O0000O0 >=50 :#line:445
                            if '_ws'in OOO00O0O0OOOOOO00 :OOO00O0O0OOOOOO00 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOO00O0O0OOOOOO00 .ws_callback ,"info":"URL %s 存在内容风险"%O0OOO0000000OOO0O ,"type":"index","is_error":True }))#line:448
                            O00O000OO0O0O0O0O .append ({"name":"url %s 存在内容风险 内容风险的关键词如下:【 %s 】"%(O0OOO0000000OOO0O ,' , '.join (O00O0OO0O0O0O0000 )),"type":"index","repair":"修复方案：检查该页面是否被篡改或清理掉此关键词"})#line:449
                except :continue #line:450
            return O00O000OO0O0O0O0O #line:451
        else :#line:452
            return []#line:453
    def GetDoamin (O00O00OO00OOO00O0 ,O000000OOOOOO0OOO ):#line:456
        ""#line:462
        OO0OOO0O0O000OO0O =O00O00OO00OOO00O0 .GetWebInfo (O000000OOOOOO0OOO )#line:463
        if not OO0OOO0O0O000OO0O :return public .returnMsg (False ,'当前网站不存在')#line:464
        if public .M ('domain').where ("pid=?",(OO0OOO0O0O000OO0O ['id'])).count ()==0 :#line:465
            if not OO0OOO0O0O000OO0O :return public .returnMsg (False ,'当前网站不存在')#line:466
        return public .returnMsg (True ,public .M ('domain').where ("pid=?",(OO0OOO0O0O000OO0O ['id'])).select ())#line:467
    def __O0OOOO0OOOOOO0O00 (OOO00O0O0000OOOO0 ):#line:470
        try :#line:471
            from pluginAuth import Plugin #line:472
            O000O0O0O0O00O000 =Plugin (False )#line:473
            O0OOO00000OO0O0O0 =O000O0O0O0O00O000 .get_plugin_list ()#line:474
            if int (O0OOO00000OO0O0O0 ['ltd'])>time .time ():#line:475
                return True #line:476
            return False #line:477
        except :return False #line:478
    def ScanSingleSite (OOOO000O00O0OO0OO ,O0OOO00O0OOO000O0 ):#line:480
        ""#line:494
        public .set_module_logs ('webscanning','ScanSingleSite',1 )#line:495
        OO0OO0000OOOO0OOO =OOOO000O00O0OO0OO .__O0OOOO0OOOOOO0O00 ()#line:496
        if not OO0OO0000OOOO0OOO :return public .returnMsg (False ,'当前功能为企业版专享')#line:497
        O000O0O0OOOO000O0 =OOOO000O00O0OO0OO .GetWebInfo (O0OOO00O0OOO000O0 )#line:498
        if not O000O0O0OOOO000O0 :return public .returnMsg (False ,'当前网站不存在')#line:499
        O000O0O0OOOO000O0 ['result']={}#line:500
        if '_ws'in O0OOO00O0OOO000O0 :#line:501
            for OO0OOO0000O0OO0O0 in O0OOO00O0OOO000O0 .scan_list :#line:503
                if OO0OOO0000O0OO0O0 =='vulscan':#line:504
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在扫描漏洞","type":"vulscan"}))#line:505
                    O000O0O0OOOO000O0 ['result']['vulscan']=OOOO000O00O0OO0OO .ScanWeb (O0OOO00O0OOO000O0 )#line:506
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"漏洞扫描完成","type":"vulscan"}))#line:507
                if OO0OOO0000O0OO0O0 =='webscan':#line:508
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在扫描网站配置安全性","type":"webscan"}))#line:509
                    O000O0O0OOOO000O0 ['result']['webscan']=OOOO000O00O0OO0OO .WebInfoDisclosure (O0OOO00O0OOO000O0 )#line:510
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在扫描网站权限配置","type":"webscan"}))#line:511
                    OOOO000O00O0OO0OO .WebFilePermission (O000O0O0OOOO000O0 ,O0OOO00O0OOO000O0 )#line:512
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"网站权限配置扫描完成","type":"webscan"}))#line:513
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在扫描SSL安全","type":"webscan"}))#line:515
                    OOOO000O00O0OO0OO .WebSSlSecurity (O000O0O0OOOO000O0 ,O0OOO00O0OOO000O0 )#line:516
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"网站SSL扫描完成","type":"webscan"}))#line:517
                if OO0OOO0000O0OO0O0 =='filescan':#line:519
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在扫描文件泄漏","type":"filescan"}))#line:520
                    OOOO000O00O0OO0OO .WebFileDisclosure (O000O0O0OOOO000O0 ,O0OOO00O0OOO000O0 )#line:521
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"文件泄漏扫描完成","type":"filescan"}))#line:522
                if OO0OOO0000O0OO0O0 =='backup':#line:524
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在扫描备份文件","type":"backup"}))#line:525
                    OOOO000O00O0OO0OO .WebBackup (O000O0O0OOOO000O0 ,O0OOO00O0OOO000O0 )#line:526
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"备份文件扫描完成","type":"backup"}))#line:527
                if OO0OOO0000O0OO0O0 =='webshell':#line:528
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在扫描webshell","type":"webshell"}))#line:529
                    OOOO000O00O0OO0OO .WebShellKill (O0OOO00O0OOO000O0 ,O000O0O0OOOO000O0 )#line:530
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"webshell扫描完成","type":"webshell"}))#line:532
                if OO0OOO0000O0OO0O0 =='boce':#line:533
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在进行拨测","type":"boce"}))#line:535
                    if 'url'in O0OOO00O0OOO000O0 :#line:536
                        OOOO000O00O0OO0OO .WebBtBoce (O0OOO00O0OOO000O0 ,O000O0O0OOOO000O0 )#line:537
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"拨测完成","type":"boce"}))#line:538
                if OO0OOO0000O0OO0O0 =='index':#line:539
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"正在进行页内内容风险检测","type":"index"}))#line:541
                    O000O0O0OOOO000O0 ['result']['index']=OOOO000O00O0OO0OO .WebIndexSecurity (O0OOO00O0OOO000O0 )#line:542
                    O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":False ,"callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"页内容风险检测完成","type":"index"}))#line:544
                O0OOO00O0OOO000O0 ._ws .send (public .getJson ({"end":True ,"ws_callback":O0OOO00O0OOO000O0 .ws_callback ,"info":"扫描完成","type":OO0OOO0000O0OO0O0 ,"webinfo":O000O0O0OOOO000O0 }))#line:545
            O0O00O0OOO0O0000O =int (time .time ())#line:546
            public .WriteFile ("/www/server/panel/config/webscaning_time",str (O0O00O0OOO0O0000O ))#line:547
        else :#line:548
            if os .path .exists ("/www/server/panel/config/webscaning_time"):#line:549
                try :#line:550
                    O0O00O0OOO0O0000O =int (public .ReadFile ("/www/server/panel/config/webscaning_time"))#line:551
                    return public .returnMsg (True ,O0O00O0OOO0O0000O )#line:552
                except :#line:553
                    return public .returnMsg (True ,0 )#line:554
            else :#line:555
                return public .returnMsg (True ,0 )#line:556
    def ScanAllSite (OOO0O0O0OO0OOOOO0 ,O00O0OO0OO00OOO00 ):#line:578
        ""#line:584
        pass #line:585
    def test2 (O0000000O0OO000OO ,OOOO00O000OOO0O0O ):#line:587
        OOOO00O000OOO0O0O ._ws .send (OOOO00O000OOO0O0O .ws_callback )#line:588
        OOOO00O000OOO0O0O ._ws .send ("11111")#line:589
        return '111'#line:590
