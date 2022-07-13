#!/usr/bin/python
from projectModel .base import projectBase #line:12
from projectModel import scanningModel #line:13
import sys ,json ,os ,public ,hashlib ,requests ,time #line:14
from BTPanel import cache #line:15
class main (projectBase ):#line:17
    __OOO000OOOOOO0O0OO =scanningModel .main ()#line:18
    __OO000OO00OO0OOOOO =0 #line:19
    __OO00000OOO0O0OOOO ="/www/server/panel/data/webshell_check_shell.txt"#line:20
    def GetWebInfo (OOO00OOO0OO0O0O00 ,O0000OO0O0OOOOO00 ):#line:22
        ""#line:28
        OO00000O0O0O0O000 =public .M ('sites').where ('project_type=? and name=?',('PHP',O0000OO0O0OOOOO00 .name )).count ()#line:29
        if not OO00000O0O0O0O000 :return False #line:30
        OO00000O0O0O0O000 =public .M ('sites').where ('project_type=? and name=?',('PHP',O0000OO0O0OOOOO00 .name )).select ()#line:31
        return OO00000O0O0O0O000 [0 ]#line:32
    def ScanWeb (OO0O0000O000OOOOO ,OOOOOOOO00OO0OO00 ):#line:35
        ""#line:41
        if '_ws'in OOOOOOOO00OO0OO00 :OOOOOOOO00OO0OO00 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOOOOOO00OO0OO00 .ws_callback ,"info":"正在扫描 %s 网站漏洞"%OOOOOOOO00OO0OO00 .name ,"type":"vulscan"}))#line:42
        OO00O000OOOO0O0OO =OO0O0000O000OOOOO .__OOO000OOOOOO0O0OO .startScanWeb (OOOOOOOO00OO0OO00 )#line:43
        if OO00O000OOOO0O0OO ['msg'][0 ]['is_vufix']:#line:44
            if '_ws'in OOOOOOOO00OO0OO00 :OOOOOOOO00OO0OO00 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOOOOOO00OO0OO00 .ws_callback ,"info":"网站 %s 存在漏洞"%OOOOOOOO00OO0OO00 .name ,"type":"vulscan","is_error":True }))#line:45
            return OO00O000OOOO0O0OO ['msg'][0 ]['cms']#line:46
        return {}#line:47
    def WebSSlSecurity (OOO0O00000O0O00O0 ,OO00O0O00OOOOOO0O ,O000O00000O0000OO ):#line:49
        ""#line:55
        if public .get_webserver ()=='nginx':#line:56
            O000O0OOO00O0OOO0 ='/www/server/panel/vhost/nginx/{}.conf'.format (OO00O0O00OOOOOO0O ['name'])#line:57
            if os .path .exists (O000O0OOO00O0OOO0 ):#line:58
                OOO0O00O00OO0OO0O =public .ReadFile (O000O0OOO00O0OOO0 )#line:59
                if 'TLSv1 'in OOO0O00O00OO0OO0O :#line:60
                    if '_ws'in O000O00000O0000OO :O000O00000O0000OO ._ws .send (public .getJson ({"end":False ,"ws_callback":O000O00000O0000OO .ws_callback ,"info":"【%s】 网站启用了不安全的TLS1协议"%OO00O0O00OOOOOO0O ['name'],"type":"webscan","is_error":True ,"dangerous":2 }))#line:63
                    OO00O0O00OOOOOO0O ['result']['webscan'].append ({"name":"【%s】 网站启用了不安全的TLS1协议"%OO00O0O00OOOOOO0O ['name'],"repair":"修复方案：打开配置文件去掉TLS1","dangerous":2 })#line:64
    def WebInfoDisclosure (OO0O000O0OOO0OOOO ,OOOO00OOO0O0OO0O0 ):#line:68
        ""#line:74
        if '_ws'in OOOO00OOO0O0OO0O0 :OOOO00OOO0O0OO0O0 ._ws .send (public .getJson ({"end":False ,"callback":OOOO00OOO0O0OO0O0 .ws_callback ,"info":"正在扫描 %s 网站配置安全性"%OOOO00OOO0O0OO0O0 .name ,"type":"webscan"}))#line:76
        OOOOOOO00000O0O00 =[]#line:77
        if public .get_webserver ()=='nginx':#line:78
            O000000O000OO0OOO ='/www/server/nginx/conf/nginx.conf'#line:79
            if os .path .exists (O000000O000OO0OOO ):#line:80
                OO0OOO00O0OOO00OO =public .ReadFile (O000000O000OO0OOO )#line:81
                if not 'server_tokens off'in OO0OOO00O0OOO00OO :#line:82
                    OOOOOOO00000O0O00 .append ({"name":"Nginx存在版本信息泄露","repair":"打开nginx.conf配置文件，在http { }里加上： server_tokens off;","dangerous":1 })#line:83
        O0000OOOOOO000000 =public .get_site_php_version (OOOO00OOO0O0OO0O0 .name )#line:84
        OOO0OOOOO000O00O0 ='/www/server/php/%s/etc/php.ini'%O0000OOOOOO000000 #line:85
        if os .path .exists (OOO0OOOOO000O00O0 ):#line:86
            O00OOO0OOO00O000O =public .ReadFile (OOO0OOOOO000O00O0 )#line:87
            if not 'expose_php = Off'in O00OOO0OOO00O000O :#line:88
                OOOOOOO00000O0O00 .append ({"name":"PHP %s 存在版本信息泄露"%O0000OOOOOO000000 ,"repair":"修复方案：打开php.ini配置文件，设置expose_php = Off","dangerous":1 })#line:89
        if '_ws'in OOOO00OOO0O0OO0O0 :OOOO00OOO0O0OO0O0 ._ws .send (public .getJson ({"end":False ,"callback":OOOO00OOO0O0OO0O0 .ws_callback ,"info":"扫描 %s 网站配置安全性完成"%OOOO00OOO0O0OO0O0 .name ,"type":"webscan"}))#line:92
        return OOOOOOO00000O0O00 #line:93
    def _send_task (O00OOO0OO000O0000 ,O0O0O0OO0OO0O00O0 ):#line:96
        ""#line:102
        import panelAuth #line:103
        OO00OOO0OO0O0OO00 =panelAuth .panelAuth ().create_serverid (None )#line:104
        OO00OOO0OO0O0OO00 ['url']=O0O0O0OO0OO0O00O0 #line:105
        try :#line:106
            OOO0OO000O000O0O0 =public .httpPost ("http://www.bt.cn/api/local/boce",OO00OOO0OO0O0OO00 ,10 )#line:107
            OOO0OO000O000O0O0 =json .loads (OOO0OO000O000O0O0 )#line:108
            return OOO0OO000O000O0O0 #line:109
        except :#line:110
            return False #line:111
    def WebBtBoce (OO000O00O00O0O0O0 ,O0OO0OO0O0OOOOOO0 ,O0OOO000OO000OOOO ):#line:114
        ""#line:120
        O0OOO000OO000OOOO ['result']['boce']=[]#line:121
        for O000O0OO00O000O0O in O0OO0OO0O0OOOOOO0 .url :#line:122
            if O000O0OO00O000O0O .find ('http://')==-1 and O000O0OO00O000O0O .find ('https://')==-1 :continue #line:123
            if '_ws'in O0OO0OO0O0OOOOOO0 :O0OO0OO0O0OOOOOO0 ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OO0OO0O0OOOOOO0 .ws_callback ,"info":"正在对URL %s 进行拨测"%O000O0OO00O000O0O ,"type":"boce"}))#line:125
            OO0O0OOO0O000OO0O =OO000O00O00O0O0O0 ._send_task (O0OO0OO0O0OOOOOO0 .url )#line:126
            if '_ws'in O0OO0OO0O0OOOOOO0 :O0OO0OO0O0OOOOOO0 ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OO0OO0O0OOOOOO0 .ws_callback ,"info":OO0O0OOO0O000OO0O ,"type":"boce"}))#line:128
            if OO0O0OOO0O000OO0O :#line:129
                O0OOO000OO000OOOO ['result']['boce'].append (OO0O0OOO0O000OO0O )#line:130
    def WebFilePermission (OOO00OO00O00OOO00 ,O0OOOO00OOOOOO000 ,OOOO000OOOOO0O0OO ):#line:132
        ""#line:138
        import pwd #line:139
        OOO0O000000O0OOOO =[]#line:140
        for OO0OOO0OO0O000O0O in os .listdir (O0OOOO00OOOOOO000 ['path']):#line:141
            O000OO00O000O0000 =os .path .join (O0OOOO00OOOOOO000 ['path'],OO0OOO0OO0O000O0O )#line:142
            if os .path .isdir (O000OO00O000O0000 ):#line:143
                OOO0O000000O0OOOO .append (O000OO00O000O0000 )#line:144
                for O0000OOO00OOO00OO in os .listdir (O000OO00O000O0000 ):#line:145
                    OO00O00000O0OOO00 =O000OO00O000O0000 +'/'+O0000OOO00OOO00OO #line:146
                    if os .path .isdir (OO00O00000O0OOO00 ):#line:147
                        OOO0O000000O0OOOO .append (OO00O00000O0OOO00 )#line:148
        if len (OOO0O000000O0OOOO )>=1 :#line:149
            for OOOO00OO00OOO0OO0 in OOO0O000000O0OOOO :#line:150
                if not os .path .exists (OOOO00OO00OOO0OO0 ):continue #line:151
                O0OOO00OOO00O0O0O =os .stat (OOOO00OO00OOO0OO0 )#line:152
                if int (oct (O0OOO00OOO00O0O0O .st_mode )[-3 :])==777 :#line:153
                    if '_ws'in OOOO000OOOOO0O0OO :OOOO000OOOOO0O0OO ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOO000OOOOO0O0OO .ws_callback ,"info":"  【%s】 目录权限错误"%OOOO00OO00OOO0OO0 ,"repair":"设置 【%s】 目录为755"%OOOO00OO00OOO0OO0 ,"type":"webscan","is_error":True ,"dangerous":1 }))#line:156
                    O0OOOO00OOOOOO000 ['result']['webscan'].append ({"name":"  【%s】 目录权限错误"%OOOO00OO00OOO0OO0 ,"repair":"修复方案：设置 【%s】 目录为755"%OOOO00OO00OOO0OO0 ,"dangerous":1 })#line:157
                if pwd .getpwuid (O0OOO00OOO00O0O0O .st_uid ).pw_name !='www':#line:158
                    if '_ws'in OOOO000OOOOO0O0OO :OOOO000OOOOO0O0OO ._ws .send (public .getJson ({"end":False ,"ws_callback":OOOO000OOOOO0O0OO .ws_callback ,"info":"  【%s】 目录权限错误"%OOOO00OO00OOO0OO0 ,"repair":"修复方案：设置 【%s】 目录的用户权限为www"%OOOO00OO00OOO0OO0 ,"type":"webscan","is_error":True ,"dangerous":1 }))#line:161
                    O0OOOO00OOOOOO000 ['result']['webscan'].append ({"name":"  【%s】 目录用户权限错误"%OOOO00OO00OOO0OO0 ,"repair":"设置 【%s】 目录的用户权限为www"%OOOO00OO00OOO0OO0 ,"dangerous":1 })#line:162
    def Getdir (OOOOOOOO00OO0000O ,OO00OO0OO0OO0000O ):#line:165
        ""#line:171
        O00000O0OOO000OOO =[]#line:172
        OOO00O0O00OOO0O0O =[]#line:173
        [[O00000O0OOO000OOO .append (os .path .join (OO0OO000OO0O0000O ,OOOO0O00000OO0000 ))for OOOO0O00000OO0000 in O0OO00O0O00OO0OO0 ]for OO0OO000OO0O0000O ,OO0O000OO0OO00OOO ,O0OO00O0O00OO0OO0 in os .walk (OO00OO0OO0OO0000O )]#line:174
        for O0OOOOOOO0000OOO0 in O00000O0OOO000OOO :#line:175
            if str (O0OOOOOOO0000OOO0 .lower ())[-4 :]=='.php':#line:176
                OOO00O0O00OOO0O0O .append (O0OOOOOOO0000OOO0 )#line:177
        return OOO00O0O00OOO0O0O #line:178
    def ReadFile (O0000000O00O000O0 ,OOOO0OOOO00O00O00 ,mode ='r'):#line:180
        ""#line:186
        import os #line:187
        if not os .path .exists (OOOO0OOOO00O00O00 ):return False #line:188
        try :#line:189
            O000O0OO0000OOO0O =open (OOOO0OOOO00O00O00 ,mode )#line:190
            OO00OO0000OOO000O =O000O0OO0000OOO0O .read ()#line:191
            O000O0OO0000OOO0O .close ()#line:192
        except Exception as O000O0OO0O0OOOOO0 :#line:193
            if sys .version_info [0 ]!=2 :#line:194
                try :#line:195
                    O000O0OO0000OOO0O =open (OOOO0OOOO00O00O00 ,mode ,encoding ="utf-8")#line:196
                    OO00OO0000OOO000O =O000O0OO0000OOO0O .read ()#line:197
                    O000O0OO0000OOO0O .close ()#line:198
                except Exception as OOOOO00OO00OO0O00 :#line:199
                    return False #line:200
            else :#line:201
                return False #line:202
        return OO00OO0000OOO000O #line:203
    def FileMd5 (O00O0O0O00O0O0O0O ,O00O0O0O0OO0O000O ):#line:205
        ""#line:211
        if os .path .exists (O00O0O0O0OO0O000O ):#line:212
            with open (O00O0O0O0OO0O000O ,'rb')as OOO0OO0O00OOO000O :#line:213
                O0OO00O0OO00O00OO =OOO0OO0O00OOO000O .read ()#line:214
            O0O0OOOO0O0000O0O =hashlib .md5 (O0OO00O0OO00O00OO ).hexdigest ()#line:215
            return O0O0OOOO0O0000O0O #line:216
        else :#line:217
            return False #line:218
    def WebshellChop (OO0OOOO0O00OO0O00 ,OO0O0O0OO000OO00O ,OOOO000O00OOO00O0 ,O0OOO00OO00O0O000 ):#line:220
        ""#line:227
        try :#line:228
            OOO00OO0000O000O0 =OOOO000O00OOO00O0 #line:229
            OOO000O0O0O000000 =os .path .getsize (OO0O0O0OO000OO00O )#line:230
            if OOO000O0O0O000000 >1024000 :return False #line:231
            OO0OO0O0OOOOOO000 ={'inputfile':OO0OOOO0O00OO0O00 .ReadFile (OO0O0O0OO000OO00O ),"md5":OO0OOOO0O00OO0O00 .FileMd5 (OO0O0O0OO000OO00O )}#line:232
            public .print_log ("参数: "+json .dumps (OO0OO0O0OOOOOO000 ))#line:233
            public .print_log ("URL "+OOO00OO0000O000O0 )#line:234
            public .print_log (OO0OOOO0O00OO0O00 .FileMd5 (OO0O0O0OO000OO00O )+" "+OO0O0O0OO000OO00O )#line:235
            OO0O00OO000OO0OOO =requests .post (OOO00OO0000O000O0 ,OO0OO0O0OOOOOO000 ,timeout =20 ).json ()#line:236
            public .print_log ("返回:  "+json .dumps (OO0O00OO000OO0OOO ))#line:237
            if OO0O00OO000OO0OOO ['msg']=='ok':#line:238
                if (OO0O00OO000OO0OOO ['data']['data']['level']==5 ):#line:239
                    return True #line:240
                return False #line:241
        except :#line:242
            return False #line:243
    def GetCheckUrl (OOOOOOO000OO0OOO0 ):#line:245
        ""#line:250
        try :#line:251
            O0O0O0O0O0O0OO0OO =requests .get ('http://www.bt.cn/checkWebShell.php').json ()#line:252
            if O0O0O0O0O0O0OO0OO ['status']:#line:253
                return O0O0O0O0O0O0OO0OO ['url']#line:254
            return False #line:255
        except :#line:256
            return False #line:257
    def UploadShell (OO0OOOOOOOOOOOOOO ,O00O00OO0OO0O0O0O ,OOOOOOOOO00O0OO00 ,O00OOOOOOOO00OOO0 ):#line:259
        ""#line:265
        if len (O00O00OO0OO0O0O0O )==0 :return []#line:266
        OOO0OO000000OO000 =OO0OOOOOOOOOOOOOO .GetCheckUrl ()#line:267
        if not OOO0OO000000OO000 :return []#line:268
        O00OOO0OOO0O000O0 =0 #line:269
        O00O00000OO000000 =0 #line:270
        OOOO000OO0O00OOO0 =[]#line:271
        if os .path .exists (OO0OOOOOOOOOOOOOO .__OO00000OOO0O0OOOO ):#line:272
            O00O00000OO000000 =1 #line:273
            try :#line:274
                OOOO000OO0O00OOO0 =json .loads (public .ReadFile (OO0OOOOOOOOOOOOOO .__OO00000OOO0O0OOOO ))#line:275
            except :#line:276
                public .WriteFile (OO0OOOOOOOOOOOOOO .__OO00000OOO0O0OOOO ,[])#line:277
                O00O00000OO000000 =0 #line:278
        for OOOOOO0000000OOO0 in O00O00OO0OO0O0O0O :#line:279
            O00OOO0OOO0O000O0 +=1 #line:280
            if '_ws'in OOOOOOOOO00O0OO00 :OOOOOOOOO00O0OO00 ._ws .send (public .getJson ({"end":False ,"callback":OOOOOOOOO00O0OO00 .ws_callback ,"info":"正在扫描文件是否是木马%s"%OOOOOO0000000OOO0 ,"type":"webscan","count":OO0OOOOOOOOOOOOOO .__OO000OO00OO0OOOOO ,"is_count":O00OOO0OOO0O000O0 }))#line:282
            if O00O00000OO000000 :#line:284
                if OOOOOO0000000OOO0 in OOOO000OO0O00OOO0 :continue #line:285
            if OO0OOOOOOOOOOOOOO .WebshellChop (OOOOOO0000000OOO0 ,OOO0OO000000OO000 ,OOOOOOOOO00O0OO00 ):#line:286
                if '_ws'in OOOOOOOOO00O0OO00 :OOOOOOOOO00O0OO00 ._ws .send (public .getJson ({"end":False ,"callback":OOOOOOOOO00O0OO00 .ws_callback ,"info":"%s 网站木马扫描发现当前文件为木马文件%s"%(OOOOOOOOO00O0OO00 .name ,len (O00OOOOOOOO00OOO0 ['result']['webshell'])),"type":"webscan","count":OO0OOOOOOOOOOOOOO .__OO000OO00OO0OOOOO ,"is_count":O00OOO0OOO0O000O0 ,"is_error":True }))#line:290
                O00OOOOOOOO00OOO0 ['result']['webshell'].append (OOOOOO0000000OOO0 )#line:291
        if '_ws'in OOOOOOOOO00O0OO00 :OOOOOOOOO00O0OO00 ._ws .send (public .getJson ({"end":False ,"callback":OOOOOOOOO00O0OO00 .ws_callback ,"info":"%s 网站木马扫描完成共发现 %s 个木马文件"%(OOOOOOOOO00O0OO00 .name ,len (O00OOOOOOOO00OOO0 ['result']['webshell'])),"type":"webscan","count":OO0OOOOOOOOOOOOOO .__OO000OO00OO0OOOOO ,"is_count":O00OOO0OOO0O000O0 }))#line:293
    def GetDirList (O0OOOOOOO0O00OO0O ,O0O0000O0O00OOOO0 ):#line:296
        ""#line:300
        if os .path .exists (str (O0O0000O0O00OOOO0 )):#line:301
            return O0OOOOOOO0O00OO0O .Getdir (O0O0000O0O00OOOO0 )#line:302
        else :#line:303
            return False #line:304
    def SanDir (O0O000O0O0O000O00 ,O00OO0OOOO0O0OOOO ,O0O00OO0OOOO0OOO0 ):#line:306
        ""#line:312
        O0O000O0O0O000O00 .__OO000OO00OO0OOOOO =0 #line:313
        O0000OOOO000OO000 =O0O000O0O0O000O00 .GetDirList (O00OO0OOOO0O0OOOO ['path'])#line:314
        if not O0000OOOO000OO000 :#line:315
            return []#line:316
        O0O000O0O0O000O00 .__OO000OO00OO0OOOOO =len (O0000OOOO000OO000 )#line:318
        O0000O000O00000O0 =O0O000O0O0O000O00 .UploadShell (O0000OOOO000OO000 ,O0O00OO0OOOO0OOO0 ,O00OO0OOOO0O0OOOO )#line:319
        return O0000O000O00000O0 #line:320
    def UpdateWubao (OOOO0000OO0OO0OO0 ,OO000000OO0O00OO0 ):#line:322
        ""#line:327
        if not os .path .exists (OOOO0000OO0OO0OO0 .__OO00000OOO0O0OOOO ):#line:328
            public .WriteFile (OOOO0000OO0OO0OO0 .__OO00000OOO0O0OOOO ,[OO000000OO0O00OO0 .strip ()])#line:329
        else :#line:330
            try :#line:331
                O0O00OO0OOO0000OO =json .loads (public .ReadFile (OOOO0000OO0OO0OO0 .__OO00000OOO0O0OOOO ))#line:332
                if not OO000000OO0O00OO0 in O0O00OO0OOO0000OO :#line:333
                    O0O00OO0OOO0000OO .append (OO000000OO0O00OO0 )#line:334
                    public .WriteFile (OOOO0000OO0OO0OO0 .__OO00000OOO0O0OOOO ,json .dumps (O0O00OO0OOO0000OO ))#line:335
            except :#line:336
                pass #line:337
    def SendWubao (OOOOO00O0O00OO0OO ,OOOOOO00O000O0O0O ):#line:340
        ""#line:345
        O00O0O000OOO000O0 =json .loads (public .ReadFile ('/www/server/panel/data/userInfo.json'))#line:346
        OO0O00OOOO00OOOO0 ='http://www.bt.cn/api/bt_waf/reportTrojanError'#line:347
        OOOOO00O0O00OO0OO .UpdateWubao (filename =OOOOOO00O000O0O0O .filename )#line:348
        O000OOO00O00OO00O ={'name':OOOOOO00O000O0O0O .filename ,'inputfile':OOOOO00O0O00OO0OO .ReadFile (OOOOOO00O000O0O0O .filename ),"md5":OOOOO00O0O00OO0OO .FileMd5 (OOOOOO00O000O0O0O .filename ),"access_key":O00O0O000OOO000O0 ['access_key'],"uid":O00O0O000OOO000O0 ['uid']}#line:349
        OOO00OO0OO0OO0O0O =public .httpPost (OO0O00OOOO00OOOO0 ,O000OOO00O00OO00O )#line:350
        return public .returnMsg (True ,"提交误报完成")#line:351
    def WebShellKill (O00000OOO0O0O0000 ,OOO0O0000000O00O0 ,O0O00OO000OOOOOOO ):#line:354
        ""#line:360
        O0O00OO000OOOOOOO ['result']['webshell']=[]#line:361
        O00000OOO0O0O0000 .SanDir (O0O00OO000OOOOOOO ,OOO0O0000000O00O0 )#line:362
    def WebFileDisclosure (OO0000OO0O0OOOO0O ,OOOO0OO000O000OO0 ,O0OOO0OO0O0O00O0O ):#line:365
        ""#line:371
        OOOO0OO000O000OO0 ['result']['filescan']=[]#line:372
        for O00000OOOO0OOOOO0 in os .listdir (OOOO0OO000O000OO0 ['path']):#line:373
            O00OOO000O0000OO0 =os .path .join (OOOO0OO000O000OO0 ['path'],O00000OOOO0OOOOO0 )#line:374
            if os .path .isfile (O00OOO000O0000OO0 ):#line:375
                if O00OOO000O0000OO0 .endswith (".sql"):#line:376
                    OOOO0OO000O000OO0 ['result']['filescan'].append ({"name":"  【%s】 网站根目录存在sql备份文件%s"%(OOOO0OO000O000OO0 ['name'],O00OOO000O0000OO0 ),"repair":"修复方案：转移到其他目录或者下载到本地","dangerous":2 })#line:379
                if O00OOO000O0000OO0 .endswith (".zip")or O00OOO000O0000OO0 .endswith (".gz")or O00OOO000O0000OO0 .endswith (".tar")or O00OOO000O0000OO0 .endswith (".7z"):#line:380
                    if OOOO0OO000O000OO0 ['name']in O00OOO000O0000OO0 :#line:381
                        if '_ws'in O0OOO0OO0O0O00O0O :O0OOO0OO0O0O00O0O ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OOO0OO0O0O00O0O .ws_callback ,"info":"  【%s】 网站根目录存在备份文件 %s"%(OOOO0OO000O000OO0 ['name'],O00OOO000O0000OO0 ),"type":"filescan","is_error":True ,"dangerous":2 }))#line:384
                        OOOO0OO000O000OO0 ['result']['filescan'].append ({"name":"  【%s】 网站根目录存在备份文件 %s"%(OOOO0OO000O000OO0 ['name'],O00OOO000O0000OO0 ),"repair":"修复方案：转移到其他目录或者下载到本地","dangerous":2 })#line:385
    def IsBackupSite (O000000OOOO000OOO ,O0O00000OOO0OOOO0 ):#line:387
        ""#line:392
        import crontab #line:393
        OOOOOOOO000OOOO0O =crontab .crontab ()#line:394
        O000O0O000O0O0OOO =OOOOOOOO000OOOO0O .GetCrontab (None )#line:395
        for O0OOOO00OO0OO00O0 in O000O0O000O0O0OOO :#line:396
            if O0OOOO00OO0OO00O0 ['sType']=='site':#line:397
                if O0OOOO00OO0OO00O0 ['sName']=='ALL':#line:398
                    return True #line:399
                if O0OOOO00OO0OO00O0 ['sName']==O0O00000OOO0OOOO0 :#line:400
                    return True #line:401
        return False #line:402
    def WebBackup (OOOOO000OO0O0OOO0 ,OO00O00O000OO0O0O ,OOO0OO000OOO00O00 ):#line:404
        ""#line:410
        OO00O00O000OO0O0O ['result']['backup']=[]#line:411
        if not OOOOO000OO0O0OOO0 .IsBackupSite (OO00O00O000OO0O0O ['name']):#line:412
            if '_ws'in OOO0OO000OOO00O00 :OOO0OO000OOO00O00 ._ws .send (public .getJson ({"end":False ,"ws_callback":OOO0OO000OOO00O00 .ws_callback ,"info":"修复方案：【%s】 在计划任务中创建备份网站任务"%OO00O00O000OO0O0O ['name'],"type":"backup","is_error":True ,"dangerous":2 }))#line:413
            OO00O00O000OO0O0O ['result']['backup'].append ({"name":"  【%s】 缺少计划任务备份"%(OO00O00O000OO0O0O ['name']),"repair":"修复方案：【%s】 在计划任务中创建备份网站任务"%OO00O00O000OO0O0O ['name'],"dangerous":2 })#line:414
    def GetLevelRule (OOOO0OOO0000OOOOO ,O00OOO0O000000OO0 ):#line:416
        O0O00O0O0OO000OOO =[]#line:417
        OOOO0O0OOO00OOOOO =['364c2b553559697066445638','364c2b55354c326a66445638','3537364f3561577a66444577664f694a7375614468513d3d','365a79793649533466444977664f694a7375614468513d3d','36594b41364b2b3366444d7766413d3d','353436773659655266444d77664f574e6d75573971513d3d','63444a7766444d77664f6976694f6d716c773d3d','354c6974357061483561325835626d5666444d77664f694a7375614468513d3d','356232703536576f66445577664f574e6d75573971513d3d','364c53743562327066445577664f574e6d75573971513d3d','356f715635724f6f66445577664f574e6d75573971513d3d','354c71613559326166445577664f574e6d75573971513d3d','354c71613570435066445577664f574e6d75573971513d3d','357065673536434266445977664f694a7375614468513d3d','3570794a3536434266445977664f694a7375614468513d3d','35594733356f754e66445977664f694a7375614468513d3d','35705376354c755966445977664f57626d2b615775656155722b53376d413d3d','356f6951354c713635623278364b654766446377664f694a7375614468513d3d','356f6951354c7136353553313562327866446377664f694a7375614468513d3d','3662754536496d79353732523536755a66446377664f694a7375614468513d3d','3571796e3537364f3562656f354c6d7a66446377664f694a7375614468513d3d','35367973354c6941354c7961356f6d4166446377664f694a7375614468513d3d','36496d79356f4f4666446377664f694a7375614468513d3d','355a7539354c716e51585a384e7a423836496d79356f4f46','354c71613572537951585a384e7a423836496d79356f4f46','3570656c3570797359585a384e7a423836496d79356f4f46','354c6941357079733659475466446377664f694a7375614468513d3d','357065683536434266446377664f694a7375614468513d3d','354c6d463649324a66446377664f694a7375614468513d3d','356f32563662473866446377664f574e6d75573971513d3d','36494342364a6d4f3570793666446377664f574e6d75573971513d3d','35714f4c35346d4d66446377664f574e6d75573971513d3d','36492b6736492b6366446377664f574e6d75573971513d3d','3572367a365a656f66446377664f574e6d75573971513d3d','356f2b513534367766446377664f574e6d75573971513d3d','35615371365a697a355a2b4f66446377664f574e6d75573971513d3d','354c716b35706954356f6d4166446377664f6d376b656542734f533670773d3d','354c756c35615371355a324b6644637766413d3d','3559574e3536322b3537716d66446777664f57626d2b615775656155722b53376d413d3d','3537712f364c657635714f413572574c6644677766413d3d','355932613562327066446777664f574e6d75573971513d3d','364c574d365a4b7866446777664f574e6d75573971513d3d','35616978354c6d51355a793666446777664f574e6d75573971513d3d','624739755a7a68384f4442383559326135623270','3572367a365a656f35615371365a697a355a2b4f66446777664f574e6d75573971513d3d','364a4768354c717366446731664f574e6d75573971513d3d','3659655235724b5a66446731664f574e6d75573971513d3d','365a4f3235724b7a66446731664f574e6d75573971513d3d','3537712f354c694b354c694c35724f6f66446731664f574e6d75573971513d3d','35616978354c6d51355a2b4f66446b77664f574e6d75573971513d3d','3571796e354c7161355a7539365a6d4666446b77664f574e6d75573971513d3d','354c715335593261355a7539365a6d4666446b77664f574e6d75573971513d3d','354c6948364c4771355a7539365a6d4666446b77664f574e6d75573971513d3d','354c6948354c6977355a7539365a6d4666446b77664f574e6d75573971513d3d','354c716135593261355a7539365a6d4666446b77664f574e6d75573971513d3d','355a75623570613535705376354c755966446b77664f57626d2b615775656155722b53376d413d3d','35616942356243383570617666446b31664f574e6d75573971513d3d','35706177364a4768354c717366446b35664f574e6d75573971513d3d','364c574d355a793666446b35664f574e6d75573971513d3d','364c574d3559326166446b35664f574e6d75573971513d3d','35706532357065323562327066446b77664f574e6d75573971513d3d','35595774355a43493562327066446b35664f574e6d75573971513d3d','35616962357169433561433066446777664f574e6d75573971513d3d','3559574e3536322b35705376354c755966446777664f57626d2b615775656155722b53376d413d3d','364c53333571792b66446377664f6976694f6d716c773d3d','35726958365943503572574c364b2b5666445577664f6d376b656542734f533670773d3d','35705337365a697966445577664f6d376b656542734f533670773d3d','35356d39356269393561325166445577664f6d376b656542734f533670773d3d','36627552356269393561325166446377664f6d376b656542734f533670773d3d','35377169356269393561325166445977664f6d376b656542734f533670773d3d','3559614635373252357269583659435066445977664f6d376b656542734f533670773d3d','3559574e3570324166446777664f6d376b656542734f533670773d3d','35727950357253653562656c3559573366446777664f6d376b656542734f533670773d3d','56325669357269583659435066446777664f6d376b656542734f533670773d3d','36594347355a435266446777664f6d376b656542734f533670773d3d','366275523561366966445977664f6d376b656542734f533670773d3d','357036423561366966445177664f6d376b656542734f533670773d3d','35705777356f3275355a53753559325766446377664f6d376b656542734f533670773d3d','353665523561326d354c694b3537325266446b7766465a5154673d3d','35372b3735614b5a66446b7766465a5154673d3d','353732523537756335597167365943666644597766465a5154673d3d','566c424f66446b7766465a5154673d3d','55314e5366446b7766465a5154673d3d','35714b763561325166446b7766465a5154673d3d','646a4a7959586c384f544238566c424f','3559716736594366355a6d6f6644637766465a5154673d3d','3659573436595734354c6d7a66446b7766465a5154673d3d','626d56306432397961794277636d3934655877334d4878575545343d','3559364c355971623572574c364b2b5666446b77664f6d376b656542734f533670773d3d','3572574c3559364c66445177664f6d376b656542734f533670773d3d','35627941356f692f364b36773562325666445977664f6d376b656542734f533670773d3d','35613661354c324e354c2b68356f477666445977664f6d376b656542734f533670773d3d','364b36773562325635702b6c364b2b6966445177664f6d376b656542734f533670773d3d','3659575335627158364b36773562325666446777664f6d376b656542734f533670773d3d','355a794c365a716266444d77664f6976694f6d716c773d3d','356f7156364c4f4866445177664f6976694f6d716c773d3d','356f6951354c713666445977664f694a7375614468513d3d','353665423570794e66446377664f6d376b656542734f533670773d3d','35373252364c533366446377664f6976694f6d716c773d3d','364c326d364c533366446377664f6976694f6d716c773d3d','355943663571792b66446377664f6976694f6d716c773d3d','355969473570796666446377664f6976694f6d716c773d3d','35364342355a574766445531664f57626d2b615775656155722b53376d413d3d','35705376354c755935626d7a35592b7766446b77664f57626d2b615775656155722b53376d413d3d','35705376354c7559356f366c35592b6a66446b77664f57626d2b615775656155722b53376d413d3d','51584277356271553535536f3559694735592b526644597766413d3d','364b69383559693466445177664f6976694f6d716c773d3d','3649324a3571613066446377664f694a7375614468513d3d','35712b5535346d353562694266445977664f6d376b656542734f533670773d3d','56564e45564877324d487a707535486e6762446b7571633d','3535577135592b333537325266445977664f694a7375614468513d3d','3535577135592b333561536e3559576f66445977664f694a7375614468513d3d','3535577135592b333562715466445977664f694a7375614468513d3d','3535577135592b33357043633537536966445977664f694a7375614468513d3d','5156626c7062506c763664384e6a423836496d79356f4f46','356136463535533335366150355969703536532b66445977664f694a7375614468513d3d']#line:418
        for OOO0OO000O0000OO0 in OOOO0O0OOO00OOOOO :#line:419
            O0O00O0O0OO000OOO .append (public .en_hexb (OOO0OO000O0000OO0 ).split ('|'))#line:420
        return O0O00O0O0OO000OOO #line:421
    def WebIndexSecurity (O000O0O00OO0O0O00 ,O0OOO0OO0O00OOO0O ):#line:423
        ""#line:429
        O0O000OOOOOOO000O =[]#line:430
        if 'urllist'in O0OOO0OO0O00OOO0O :#line:431
            OOOOOOOOOO00OO00O =O000O0O00OO0O0O00 .GetLevelRule (None )#line:432
            for OOO0OOO0O000O0000 in O0OOO0OO0O00OOO0O .urllist :#line:433
                try :#line:434
                    if not OOO0OOO0O000O0000 .find ('http://')==-1 and OOO0OOO0O000O0000 .find ('https://')==-1 :#line:435
                        if '_ws'in O0OOO0OO0O00OOO0O :O0OOO0OO0O00OOO0O ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OOO0OO0O00OOO0O .ws_callback ,"info":"正在对URL %s 进行内容风险检测"%O0OOO0OO0O00OOO0O .url ,"type":"index","is_error":True }))#line:436
                        O0O0OO00000000O0O =requests .get (url =OOO0OOO0O000O0000 ,verify =False )#line:437
                        OO0O000000OOO0OO0 =O0O0OO00000000O0O .text #line:438
                        O00O00OOOOO0O0OO0 =0 #line:439
                        O00OO000O0OOO00O0 =[]#line:440
                        for O0000OO0O0OOOOO0O in OOOOOOOOOO00OO00O :#line:441
                            if O0000OO0O0OOOOO0O [0 ]in OO0O000000OOO0OO0 :#line:442
                                O00O00OOOOO0O0OO0 +=int (O0000OO0O0OOOOO0O [1 ])#line:443
                                O00OO000O0OOO00O0 .append (O0000OO0O0OOOOO0O [0 ])#line:444
                        if O00O00OOOOO0O0OO0 >=50 :#line:445
                            if '_ws'in O0OOO0OO0O00OOO0O :O0OOO0OO0O00OOO0O ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OOO0OO0O00OOO0O .ws_callback ,"info":"URL %s 存在内容风险"%OOO0OOO0O000O0000 ,"type":"index","is_error":True }))#line:448
                            O0O000OOOOOOO000O .append ({"name":"url %s 存在内容风险 内容风险的关键词如下:【 %s 】"%(OOO0OOO0O000O0000 ,' , '.join (O00OO000O0OOO00O0 )),"type":"index","repair":"修复方案：检查该页面是否被篡改或清理掉此关键词"})#line:449
                except :continue #line:450
            return O0O000OOOOOOO000O #line:451
        else :#line:452
            return []#line:453
    def GetDoamin (OOOO000O0OOO000OO ,OOOOO00OOO00OO0O0 ):#line:456
        ""#line:462
        OOO0OO0O00O0OOOOO =OOOO000O0OOO000OO .GetWebInfo (OOOOO00OOO00OO0O0 )#line:463
        if not OOO0OO0O00O0OOOOO :return public .returnMsg (False ,'当前网站不存在')#line:464
        if public .M ('domain').where ("pid=?",(OOO0OO0O00O0OOOOO ['id'])).count ()==0 :#line:465
            if not OOO0OO0O00O0OOOOO :return public .returnMsg (False ,'当前网站不存在')#line:466
        return public .returnMsg (True ,public .M ('domain').where ("pid=?",(OOO0OO0O00O0OOOOO ['id'])).select ())#line:467
    def __O000OOO0OO00O00OO (OOO0O00OOOO00OO00 ):#line:470
        try :#line:471
            from pluginAuth import Plugin #line:472
            O0O00O00OOOOO000O =Plugin (False )#line:473
            OO0O00OO00OOOO0OO =O0O00O00OOOOO000O .get_plugin_list ()#line:474
            if int (OO0O00OO00OOOO0OO ['ltd'])>time .time ():#line:475
                return True #line:476
            return False #line:477
        except :return False #line:478
    def ScanSingleSite (OO0OO0OO0OO0OOOO0 ,O0OO00OO00OO00O0O ):#line:480
        ""#line:494
        public .set_module_logs ('webscanning','ScanSingleSite',1 )#line:495
        O000O00OO0000O0O0 =OO0OO0OO0OO0OOOO0 .__O000OOO0OO00O00OO ()#line:496
        if not O000O00OO0000O0O0 :return public .returnMsg (False ,'当前功能为企业版专享')#line:497
        O00OO0O0OOOO0000O =OO0OO0OO0OO0OOOO0 .GetWebInfo (O0OO00OO00OO00O0O )#line:498
        if not O00OO0O0OOOO0000O :return public .returnMsg (False ,'当前网站不存在')#line:499
        O00OO0O0OOOO0000O ['result']={}#line:500
        if '_ws'in O0OO00OO00OO00O0O :#line:501
            for O000O0OO0O000O00O in O0OO00OO00OO00O0O .scan_list :#line:503
                if O000O0OO0O000O00O =='vulscan':#line:504
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在扫描漏洞","type":"vulscan"}))#line:505
                    O00OO0O0OOOO0000O ['result']['vulscan']=OO0OO0OO0OO0OOOO0 .ScanWeb (O0OO00OO00OO00O0O )#line:506
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"ws_callback":O0OO00OO00OO00O0O .ws_callback ,"info":"漏洞扫描完成","type":"vulscan"}))#line:507
                if O000O0OO0O000O00O =='webscan':#line:508
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在扫描网站配置安全性","type":"webscan"}))#line:509
                    O00OO0O0OOOO0000O ['result']['webscan']=OO0OO0OO0OO0OOOO0 .WebInfoDisclosure (O0OO00OO00OO00O0O )#line:510
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在扫描网站权限配置","type":"webscan"}))#line:511
                    OO0OO0OO0OO0OOOO0 .WebFilePermission (O00OO0O0OOOO0000O ,O0OO00OO00OO00O0O )#line:512
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"网站权限配置扫描完成","type":"webscan"}))#line:513
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在扫描SSL安全","type":"webscan"}))#line:515
                    OO0OO0OO0OO0OOOO0 .WebSSlSecurity (O00OO0O0OOOO0000O ,O0OO00OO00OO00O0O )#line:516
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"网站SSL扫描完成","type":"webscan"}))#line:517
                if O000O0OO0O000O00O =='filescan':#line:519
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在扫描文件泄漏","type":"filescan"}))#line:520
                    OO0OO0OO0OO0OOOO0 .WebFileDisclosure (O00OO0O0OOOO0000O ,O0OO00OO00OO00O0O )#line:521
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"文件泄漏扫描完成","type":"filescan"}))#line:522
                if O000O0OO0O000O00O =='backup':#line:524
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在扫描备份文件","type":"backup"}))#line:525
                    OO0OO0OO0OO0OOOO0 .WebBackup (O00OO0O0OOOO0000O ,O0OO00OO00OO00O0O )#line:526
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"备份文件扫描完成","type":"backup"}))#line:527
                if O000O0OO0O000O00O =='webshell':#line:528
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在扫描webshell","type":"webshell"}))#line:529
                    OO0OO0OO0OO0OOOO0 .WebShellKill (O0OO00OO00OO00O0O ,O00OO0O0OOOO0000O )#line:530
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"webshell扫描完成","type":"webshell"}))#line:532
                if O000O0OO0O000O00O =='boce':#line:533
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在进行拨测","type":"boce"}))#line:535
                    if 'url'in O0OO00OO00OO00O0O :#line:536
                        OO0OO0OO0OO0OOOO0 .WebBtBoce (O0OO00OO00OO00O0O ,O00OO0O0OOOO0000O )#line:537
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"拨测完成","type":"boce"}))#line:538
                if O000O0OO0O000O00O =='index':#line:539
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"正在进行页内内容风险检测","type":"index"}))#line:541
                    O00OO0O0OOOO0000O ['result']['index']=OO0OO0OO0OO0OOOO0 .WebIndexSecurity (O0OO00OO00OO00O0O )#line:542
                    O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":False ,"callback":O0OO00OO00OO00O0O .ws_callback ,"info":"页内容风险检测完成","type":"index"}))#line:544
                O0OO00OO00OO00O0O ._ws .send (public .getJson ({"end":True ,"ws_callback":O0OO00OO00OO00O0O .ws_callback ,"info":"扫描完成","type":O000O0OO0O000O00O ,"webinfo":O00OO0O0OOOO0000O }))#line:545
            O0OOO00OO0000OO0O =int (time .time ())#line:546
            public .WriteFile ("/www/server/panel/config/webscaning_time",str (O0OOO00OO0000OO0O ))#line:547
        else :#line:548
            if os .path .exists ("/www/server/panel/config/webscaning_time"):#line:549
                try :#line:550
                    O0OOO00OO0000OO0O =int (public .ReadFile ("/www/server/panel/config/webscaning_time"))#line:551
                    return public .returnMsg (True ,O0OOO00OO0000OO0O )#line:552
                except :#line:553
                    return public .returnMsg (True ,0 )#line:554
            else :#line:555
                return public .returnMsg (True ,0 )#line:556
    def ScanAllSite (O0O000OOO0OO0O00O ,O0000O0OOOOOOOOOO ):#line:578
        ""#line:584
        pass #line:585
    def test2 (O0O0OOO00OOO00OO0 ,OO00OO00O00OO000O ):#line:587
        OO00OO00O00OO000O ._ws .send (OO00OO00O00OO000O .ws_callback )#line:588
        OO00OO00O00OO000O ._ws .send ("11111")#line:589
        return '111'#line:590
