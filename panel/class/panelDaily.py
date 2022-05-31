import os #line:14
import sys #line:15
import time #line:16
import psutil #line:17
os .chdir ("/www/server/panel")#line:19
sys .path .insert (0 ,"/www/server/panel")#line:20
sys .path .insert (0 ,"class/")#line:21
import public #line:23
from system import system #line:24
from panelPlugin import panelPlugin #line:25
from BTPanel import auth ,cache #line:26
class panelDaily :#line:28
    def check_databases (OO0O00000OOO000OO ):#line:30
        ""#line:31
        OOO0O0O0O000O0OOO =["app_usage","server_status","backup_status","daily"]#line:32
        import sqlite3 #line:33
        O0OO000OO0000OO00 =sqlite3 .connect ("/www/server/panel/data/system.db")#line:34
        O000OOOO00OO0OO00 =O0OO000OO0000OO00 .cursor ()#line:35
        OO0O000O0OO0O0000 =",".join (["'"+OO00O0OOOOOOOOOO0 +"'"for OO00O0OOOOOOOOOO0 in OOO0O0O0O000O0OOO ])#line:36
        O0OO00O000OO0OO00 =O000OOOO00OO0OO00 .execute ("SELECT name FROM sqlite_master WHERE type='table' and name in ({})".format (OO0O000O0OO0O0000 ))#line:37
        OOOO000000O000O0O =O0OO00O000OO0OO00 .fetchall ()#line:38
        O00000000OOOOO000 =False #line:41
        OO00O00O000OOO0OO =[]#line:42
        if OOOO000000O000O0O :#line:43
            OO00O00O000OOO0OO =[O0OO0O0O0OO0O0O0O [0 ]for O0OO0O0O0OO0O0O0O in OOOO000000O000O0O ]#line:44
        if "app_usage"not in OO00O00O000OOO0OO :#line:46
            O00OOO000O0O00000 ='''CREATE TABLE IF NOT EXISTS `app_usage` (
                    `time_key` INTEGER PRIMARY KEY,
                    `app` TEXT,
                    `disks` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:52
            O000OOOO00OO0OO00 .execute (O00OOO000O0O00000 )#line:53
            O00000000OOOOO000 =True #line:54
        if "server_status"not in OO00O00O000OOO0OO :#line:56
            print ("创建server_status表:")#line:57
            O00OOO000O0O00000 ='''CREATE TABLE IF NOT EXISTS `server_status` (
                    `status` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:61
            O000OOOO00OO0OO00 .execute (O00OOO000O0O00000 )#line:62
            O00000000OOOOO000 =True #line:63
        if "backup_status"not in OO00O00O000OOO0OO :#line:65
            print ("创建备份状态表:")#line:66
            O00OOO000O0O00000 ='''CREATE TABLE IF NOT EXISTS `backup_status` (
                    `id` INTEGER,
                    `target` TEXT,
                    `status` INTEGER,
                    `msg` TEXT DEFAULT "",
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:73
            O000OOOO00OO0OO00 .execute (O00OOO000O0O00000 )#line:74
            O00000000OOOOO000 =True #line:75
        if "daily"not in OO00O00O000OOO0OO :#line:77
            O00OOO000O0O00000 ='''CREATE TABLE IF NOT EXISTS `daily` (
                    `time_key` INTEGER,
                    `evaluate` INTEGER,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:82
            O000OOOO00OO0OO00 .execute (O00OOO000O0O00000 )#line:83
            O00000000OOOOO000 =True #line:84
        if O00000000OOOOO000 :#line:86
            O0OO000OO0000OO00 .commit ()#line:87
        O000OOOO00OO0OO00 .close ()#line:88
        O0OO000OO0000OO00 .close ()#line:89
        return True #line:90
    def get_time_key (OO0O0OO00OO000O00 ,date =None ):#line:92
        if date is None :#line:93
            date =time .localtime ()#line:94
        OOOOO00O0OOO0OOOO =0 #line:95
        O0OOOO000OO00O00O ="%Y%m%d"#line:96
        if type (date )==time .struct_time :#line:97
            OOOOO00O0OOO0OOOO =int (time .strftime (O0OOOO000OO00O00O ,date ))#line:98
        if type (date )==str :#line:99
            OOOOO00O0OOO0OOOO =int (time .strptime (date ,O0OOOO000OO00O00O ))#line:100
        return OOOOO00O0OOO0OOOO #line:101
    def store_app_usage (OOO0000000OO00000 ,time_key =None ):#line:103
        ""#line:111
        OOO0000000OO00000 .check_databases ()#line:113
        if time_key is None :#line:115
            time_key =OOO0000000OO00000 .get_time_key ()#line:116
        O0OOOOO000OOO00OO =public .M ("system").dbfile ("system").table ("app_usage")#line:118
        O000OOOOO00OO00O0 =O0OOOOO000OOO00OO .field ("time_key").where ("time_key=?",(time_key )).find ()#line:119
        if O000OOOOO00OO00O0 and "time_key"in O000OOOOO00OO00O0 :#line:120
            if O000OOOOO00OO00O0 ["time_key"]==time_key :#line:121
                return True #line:123
        O00O00OO0OO0000O0 =public .M ('sites').field ('path').select ()#line:125
        O00O00000OO00000O =0 #line:126
        for OOO0OOO0O0O0O0O0O in O00O00OO0OO0000O0 :#line:127
            O0OO000OOO0OO0000 =OOO0OOO0O0O0O0O0O ["path"]#line:128
            if O0OO000OOO0OO0000 :#line:129
                O00O00000OO00000O +=public .get_path_size (O0OO000OOO0OO0000 )#line:130
        O0O0OOO00O00000OO =public .get_path_size ("/www/server/data")#line:132
        O0OOOO000O0O00O0O =public .M ("ftps").field ("path").select ()#line:134
        O0OO000O0OO000O00 =0 #line:135
        for OOO0OOO0O0O0O0O0O in O0OOOO000O0O00O0O :#line:136
            O00OO00OOO0O00OO0 =OOO0OOO0O0O0O0O0O ["path"]#line:137
            if O00OO00OOO0O00OO0 :#line:138
                O0OO000O0OO000O00 +=public .get_path_size (O00OO00OOO0O00OO0 )#line:139
        OOO0OOOOOO0O000OO =public .get_path_size ("/www/server/panel/plugin")#line:141
        O00OO00OO0OO0000O =["/www/server/total","/www/server/btwaf","/www/server/coll","/www/server/nginx","/www/server/apache","/www/server/redis"]#line:149
        for OOOO00OOO00O0OOO0 in O00OO00OO0OO0000O :#line:150
            OOO0OOOOOO0O000OO +=public .get_path_size (OOOO00OOO00O0OOO0 )#line:151
        OO00OO000000O0O00 =system ().GetDiskInfo2 (human =False )#line:153
        OO0OOO0OO0O00O00O =""#line:154
        OOO000OO00OO0000O =0 #line:155
        OOOO000OO00OOO00O =0 #line:156
        for OOO0000OO00OO0O0O in OO00OO000000O0O00 :#line:157
            O00O0OO0000OO0O0O =OOO0000OO00OO0O0O ["path"]#line:158
            if OO0OOO0OO0O00O00O :#line:159
                OO0OOO0OO0O00O00O +="-"#line:160
            O0O00O0OO0O00O00O ,O0000OO00OOOOO000 ,O0O00000OO00O00OO ,OO000O0000OO0000O =OOO0000OO00OO0O0O ["size"]#line:161
            O0OO0O000OOOOO0O0 ,OO0O0O0O0000000OO ,_O0O0OOO0000O0O0O0 ,_OOO00OO0000OOO00O =OOO0000OO00OO0O0O ["inodes"]#line:162
            OO0OOO0OO0O00O00O ="{},{},{},{},{}".format (O00O0OO0000OO0O0O ,O0000OO00OOOOO000 ,O0O00O0OO0O00O00O ,OO0O0O0O0000000OO ,O0OO0O000OOOOO0O0 )#line:163
            if O00O0OO0000OO0O0O =="/":#line:164
                OOO000OO00OO0000O =O0O00O0OO0O00O00O #line:165
                OOOO000OO00OOO00O =O0000OO00OOOOO000 #line:166
        OO000OO0O00O0OO0O ="{},{},{},{},{},{}".format (OOO000OO00OO0000O ,OOOO000OO00OOO00O ,O00O00000OO00000O ,O0O0OOO00O00000OO ,O0OO000O0OO000O00 ,OOO0OOOOOO0O000OO )#line:171
        OO0000O0OO000O000 =public .M ("system").dbfile ("system").table ("app_usage").add ("time_key,app,disks",(time_key ,OO000OO0O00O0OO0O ,OO0OOO0OO0O00O00O ))#line:173
        if OO0000O0OO000O000 ==time_key :#line:174
            return True #line:175
        return False #line:178
    def parse_app_usage_info (OO0OOO0O0O00OO000 ,O0OO0OOO0O000O000 ):#line:180
        ""#line:181
        if not O0OO0OOO0O000O000 :#line:182
            return {}#line:183
        print (O0OO0OOO0O000O000 )#line:184
        O0OO000OOOO0OOOO0 ,O000OO0O00OO00O00 ,OOOO0O0O0O00OO000 ,OO00000O0OO00OOOO ,OOO00OO00OO00OOO0 ,OOOO0OO0000O0OOOO =O0OO0OOO0O000O000 ["app"].split (",")#line:185
        O0O0OO00O0O00OO00 =O0OO0OOO0O000O000 ["disks"].split ("-")#line:186
        O0O0OO0O00O0O000O ={}#line:187
        for OO0OOOO000O0O0O00 in O0O0OO00O0O00OO00 :#line:188
            OO0OO0000O0OOO0O0 ,O0000OO00O00OOOO0 ,OO000O0O0OOO0O0O0 ,O0O00000OO0O0OO0O ,OO000OO0OO00O0000 =OO0OOOO000O0O0O00 .split (",")#line:189
            OO0O0O00OOO0OOOO0 ={}#line:190
            OO0O0O00OOO0OOOO0 ["usage"]=O0000OO00O00OOOO0 #line:191
            OO0O0O00OOO0OOOO0 ["total"]=OO000O0O0OOO0O0O0 #line:192
            OO0O0O00OOO0OOOO0 ["iusage"]=O0O00000OO0O0OO0O #line:193
            OO0O0O00OOO0OOOO0 ["itotal"]=OO000OO0OO00O0000 #line:194
            O0O0OO0O00O0O000O [OO0OO0000O0OOO0O0 ]=OO0O0O00OOO0OOOO0 #line:195
        return {"apps":{"disk_total":O0OO000OOOO0OOOO0 ,"disk_usage":O000OO0O00OO00O00 ,"sites":OOOO0O0O0O00OO000 ,"databases":OO00000O0OO00OOOO ,"ftps":OOO00OO00OO00OOO0 ,"plugins":OOOO0OO0000O0OOOO },"disks":O0O0OO0O00O0O000O }#line:206
    def get_app_usage (OOO00000O00OO00OO ,O0OO0O0O0O0O0OO0O ):#line:208
        O0O000O00O0O0O000 =time .localtime ()#line:210
        O0O00OOO0OOO00O0O =OOO00000O00OO00OO .get_time_key ()#line:211
        OO0O0O0O000O0OO0O =time .localtime (time .mktime ((O0O000O00O0O0O000 .tm_year ,O0O000O00O0O0O000 .tm_mon ,O0O000O00O0O0O000 .tm_mday -1 ,0 ,0 ,0 ,0 ,0 ,0 )))#line:214
        OOOOOOO0O0000000O =OOO00000O00OO00OO .get_time_key (OO0O0O0O000O0OO0O )#line:215
        O0O0OOO000O00OO00 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key =? or time_key=?",(O0O00OOO0OOO00O0O ,OOOOOOO0O0000000O ))#line:217
        O0O000OOO0OOOO000 =O0O0OOO000O00OO00 .select ()#line:218
        if type (O0O000OOO0OOOO000 )==str or not O0O000OOO0OOOO000 :#line:221
            return {}#line:222
        OO000O0O0OO00O00O ={}#line:223
        O0OO0O0O00OOOOOOO ={}#line:224
        for O0OOOO00O00000000 in O0O000OOO0OOOO000 :#line:225
            if O0OOOO00O00000000 ["time_key"]==O0O00OOO0OOO00O0O :#line:226
                OO000O0O0OO00O00O =OOO00000O00OO00OO .parse_app_usage_info (O0OOOO00O00000000 )#line:227
            if O0OOOO00O00000000 ["time_key"]==OOOOOOO0O0000000O :#line:228
                O0OO0O0O00OOOOOOO =OOO00000O00OO00OO .parse_app_usage_info (O0OOOO00O00000000 )#line:229
        if not OO000O0O0OO00O00O :#line:231
            return {}#line:232
        for OOO000O0000OOOO00 ,OO00O00O0000OOO0O in OO000O0O0OO00O00O ["disks"].items ():#line:235
            O00OO0O0O0OOOO000 =int (OO00O00O0000OOO0O ["total"])#line:236
            O0O0000000OOO00OO =int (OO00O00O0000OOO0O ["usage"])#line:237
            O00O00OOO00OOO00O =int (OO00O00O0000OOO0O ["itotal"])#line:239
            OOO00000OO000O0O0 =int (OO00O00O0000OOO0O ["iusage"])#line:240
            if O0OO0O0O00OOOOOOO and OOO000O0000OOOO00 in O0OO0O0O00OOOOOOO ["disks"].keys ():#line:242
                O000OOO000O000O00 =O0OO0O0O00OOOOOOO ["disks"]#line:243
                O0000OO0OO0O00OO0 =O000OOO000O000O00 [OOO000O0000OOOO00 ]#line:244
                O0O0O0000O00O0O0O =int (O0000OO0OO0O00OO0 ["total"])#line:245
                if O0O0O0000O00O0O0O ==O00OO0O0O0OOOO000 :#line:246
                    OO0000OOOO000OO0O =int (O0000OO0OO0O00OO0 ["usage"])#line:247
                    OO0000000O0O0O00O =0 #line:248
                    O00000O0O0O0OO000 =O0O0000000OOO00OO -OO0000OOOO000OO0O #line:249
                    if O00000O0O0O0OO000 >0 :#line:250
                        OO0000000O0O0O00O =round (O00000O0O0O0OO000 /O00OO0O0O0OOOO000 ,2 )#line:251
                    OO00O00O0000OOO0O ["incr"]=OO0000000O0O0O00O #line:252
                O00O00O00OOOO0O0O =int (O0000OO0OO0O00OO0 ["itotal"])#line:255
                if True :#line:256
                    O000O00OOOOO0O000 =int (O0000OO0OO0O00OO0 ["iusage"])#line:257
                    OO0OO0OO000O0O000 =0 #line:258
                    O00000O0O0O0OO000 =OOO00000OO000O0O0 -O000O00OOOOO0O000 #line:259
                    if O00000O0O0O0OO000 >0 :#line:260
                        OO0OO0OO000O0O000 =round (O00000O0O0O0OO000 /O00O00OOO00OOO00O ,2 )#line:261
                    OO00O00O0000OOO0O ["iincr"]=OO0OO0OO000O0O000 #line:262
        OO0O0OOOOOO0O0O0O =OO000O0O0OO00O00O ["apps"]#line:266
        OO0OO0O00O00OO0O0 =int (OO0O0OOOOOO0O0O0O ["disk_total"])#line:267
        if O0OO0O0O00OOOOOOO and O0OO0O0O00OOOOOOO ["apps"]["disk_total"]==OO0O0OOOOOO0O0O0O ["disk_total"]:#line:268
            OOOOO0OOOO000OOOO =O0OO0O0O00OOOOOOO ["apps"]#line:269
            for OO0O00O00O00OOO00 ,O00O0000OOO0O00OO in OO0O0OOOOOO0O0O0O .items ():#line:270
                if OO0O00O00O00OOO00 =="disks":continue #line:271
                if OO0O00O00O00OOO00 =="disk_total":continue #line:272
                if OO0O00O00O00OOO00 =="disk_usage":continue #line:273
                OO0OO000O00O0OOOO =0 #line:274
                OO00OO0OOOO000000 =int (O00O0000OOO0O00OO )-int (OOOOO0OOOO000OOOO [OO0O00O00O00OOO00 ])#line:275
                if OO00OO0OOOO000000 >0 :#line:276
                    OO0OO000O00O0OOOO =round (OO00OO0OOOO000000 /OO0OO0O00O00OO0O0 ,2 )#line:277
                OO0O0OOOOOO0O0O0O [OO0O00O00O00OOO00 ]={"val":O00O0000OOO0O00OO ,"incr":OO0OO000O00O0OOOO }#line:282
        return OO000O0O0OO00O00O #line:283
    def get_timestamp_interval (OO00O00O0OO0000OO ,OOOOOO0OOOO00000O ):#line:285
        OO0OOO0000OO00O00 =None #line:286
        O0O0O00000O0O0O00 =None #line:287
        OO0OOO0000OO00O00 =time .mktime ((OOOOOO0OOOO00000O .tm_year ,OOOOOO0OOOO00000O .tm_mon ,OOOOOO0OOOO00000O .tm_mday ,0 ,0 ,0 ,0 ,0 ,0 ))#line:289
        O0O0O00000O0O0O00 =time .mktime ((OOOOOO0OOOO00000O .tm_year ,OOOOOO0OOOO00000O .tm_mon ,OOOOOO0OOOO00000O .tm_mday ,23 ,59 ,59 ,0 ,0 ,0 ))#line:291
        return OO0OOO0000OO00O00 ,O0O0O00000O0O0O00 #line:292
    def check_server (OO0O0000O0O00O0O0 ):#line:295
        try :#line:296
            O0O00O00OOO00O0O0 =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:299
            OOO00O000O0OO0OOO =panelPlugin ()#line:300
            OOO000O0000O0O000 =public .dict_obj ()#line:301
            O0O000OO0O000O00O =""#line:302
            for O0O00OO0O0OOO0O00 in O0O00O00OOO00O0O0 :#line:303
                O00OO0O0O0000OO00 =False #line:304
                O0OOO000O000OO00O =False #line:305
                OOO000O0000O0O000 .name =O0O00OO0O0OOO0O00 #line:306
                O0O0O0O00O00O0OOO =OOO00O000O0OO0OOO .getPluginInfo (OOO000O0000O0O000 )#line:307
                if not O0O0O0O00O00O0OOO :#line:308
                    continue #line:309
                OOO0OO0O00O00O00O =O0O0O0O00O00O0OOO ["versions"]#line:310
                for O0000OO0OO000O0O0 in OOO0OO0O00O00O00O :#line:312
                    if O0000OO0OO000O0O0 ["status"]:#line:315
                        O0OOO000O000OO00O =True #line:316
                    if "run"in O0000OO0OO000O0O0 .keys ()and O0000OO0OO000O0O0 ["run"]:#line:317
                        O0OOO000O000OO00O =True #line:319
                        O00OO0O0O0000OO00 =True #line:320
                        break #line:321
                O000000OO00OOOO00 =0 #line:322
                if O0OOO000O000OO00O :#line:323
                    O000000OO00OOOO00 =1 #line:324
                    if not O00OO0O0O0000OO00 :#line:326
                        O000000OO00OOOO00 =2 #line:327
                O0O000OO0O000O00O +=str (O000000OO00OOOO00 )#line:328
            if '2'in O0O000OO0O000O00O :#line:332
                public .M ("system").dbfile ("server_status").add ("status, addtime",(O0O000OO0O000O00O ,time .time ()))#line:334
        except Exception as O0O0OOO00O0OOO0OO :#line:335
            return True #line:337
    def get_daily_data (OOOO00O00OOOO0OO0 ,OOO0OO00OOOO0OO0O ):#line:339
        ""#line:340
        O00OOOOOO00O00O0O ="IS_PRO_OR_LTD_FOR_PANEL_DAILY"#line:342
        OO00O0000OO0OO00O =cache .get (O00OOOOOO00O00O0O )#line:343
        if not OO00O0000OO0OO00O :#line:344
            try :#line:345
                O0OOOO0O00OOOOOO0 =panelPlugin ()#line:346
                OO000000OOO000O0O =O0OOOO0O00OOOOOO0 .get_soft_list (OOO0OO00OOOO0OO0O )#line:347
                if OO000000OOO000O0O ["pro"]<0 and OO000000OOO000O0O ["ltd"]<0 :#line:348
                    if os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:349
                        os .remove ("/www/server/panel/data/start_daily.pl")#line:350
                    return {"status":False ,"msg":"No authorization.","data":[],"date":OOO0OO00OOOO0OO0O .date }#line:356
                cache .set (O00OOOOOO00O00O0O ,True ,86400 )#line:357
            except :#line:358
                return {"status":False ,"msg":"获取不到授权信息，请检查网络是否正常","data":[],"date":OOO0OO00OOOO0OO0O .date }#line:364
        if not os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:367
            public .writeFile ("/www/server/panel/data/start_daily.pl",OOO0OO00OOOO0OO0O .date )#line:368
        return OOOO00O00OOOO0OO0 .get_daily_data_local (OOO0OO00OOOO0OO0O .date )#line:369
    def get_daily_data_local (OO0O0O0OOOOOO0O00 ,O0O0000000OO00OOO ):#line:371
        O00OO00O0000O0O0O =time .strptime (O0O0000000OO00OOO ,"%Y%m%d")#line:372
        O0O0O0O0OOOO000O0 =OO0O0O0OOOOOO0O00 .get_time_key (O00OO00O0000O0O0O )#line:373
        OO0O0O0OOOOOO0O00 .check_databases ()#line:375
        OO00000000OOOOO00 =time .strftime ("%Y-%m-%d",O00OO00O0000O0O0O )#line:377
        OO0O000O00O0O0000 =0 #line:378
        O0000OOOOOOOOO00O ,O0OO0O00OO0O00OOO =OO0O0O0OOOOOO0O00 .get_timestamp_interval (O00OO00O0000O0O0O )#line:379
        OO0OO0O00O00O00O0 =public .M ("system").dbfile ("system")#line:380
        OOO0O0OO000000O0O =OO0OO0O00O00O00O0 .table ("process_high_percent")#line:381
        O0000OO0O00000OOO =OOO0O0OO000000O0O .where ("addtime>=? and addtime<=?",(O0000OOOOOOOOO00O ,O0OO0O00OO0O00OOO )).order ("addtime").select ()#line:382
        OO0OOOO0OOOOO00OO =[]#line:386
        if len (O0000OO0O00000OOO )>0 :#line:387
            for O0OO0OOOOOOOOOO0O in O0000OO0O00000OOO :#line:389
                OOO0OOO0OO00O0OOO =int (O0OO0OOOOOOOOOO0O ["cpu_percent"])#line:391
                if OOO0OOO0OO00O0OOO >=80 :#line:392
                    OO0OOOO0OOOOO00OO .append ({"time":O0OO0OOOOOOOOOO0O ["addtime"],"name":O0OO0OOOOOOOOOO0O ["name"],"pid":O0OO0OOOOOOOOOO0O ["pid"],"percent":OOO0OOO0OO00O0OOO })#line:400
        OOO00O000O000O0OO =len (OO0OOOO0OOOOO00OO )#line:402
        OOO00OOO000000000 =0 #line:403
        OOO000O00O0O00OO0 =""#line:404
        if OOO00O000O000O0OO ==0 :#line:405
            OOO00OOO000000000 =20 #line:406
        else :#line:407
            OOO000O00O0O00OO0 ="CPU出现过载情况"#line:408
        O00O0O0O0OO0O000O ={"ex":OOO00O000O000O0OO ,"detail":OO0OOOO0OOOOO00OO }#line:412
        O00OOO000OO0O0000 =[]#line:415
        if len (O0000OO0O00000OOO )>0 :#line:416
            for O0OO0OOOOOOOOOO0O in O0000OO0O00000OOO :#line:418
                O0OO0OO0OO00OO00O =float (O0OO0OOOOOOOOOO0O ["memory"])#line:420
                O0O00000O0OO0OO00 =psutil .virtual_memory ().total #line:421
                OO0O0000OOOO00OO0 =round (100 *O0OO0OO0OO00OO00O /O0O00000O0OO0OO00 ,2 )#line:422
                if OO0O0000OOOO00OO0 >=80 :#line:423
                    O00OOO000OO0O0000 .append ({"time":O0OO0OOOOOOOOOO0O ["addtime"],"name":O0OO0OOOOOOOOOO0O ["name"],"pid":O0OO0OOOOOOOOOO0O ["pid"],"percent":OO0O0000OOOO00OO0 })#line:431
        O000O0O0O0000OO0O =len (O00OOO000OO0O0000 )#line:432
        OO0O0000O0OOO0OOO =""#line:433
        O0O0OOO000O000000 =0 #line:434
        if O000O0O0O0000OO0O ==0 :#line:435
            O0O0OOO000O000000 =20 #line:436
        else :#line:437
            if O000O0O0O0000OO0O >1 :#line:438
                OO0O0000O0OOO0OOO ="内存在多个时间点出现占用80%"#line:439
            else :#line:440
                OO0O0000O0OOO0OOO ="内存出现占用超过80%"#line:441
        O0O00O0OO0O0O0OO0 ={"ex":O000O0O0O0000OO0O ,"detail":O00OOO000OO0O0000 }#line:445
        OOO0O000OOO0000OO =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key=?",(O0O0O0O0OOOO000O0 ,))#line:449
        O0OO0O00OO00OOOO0 =OOO0O000OOO0000OO .select ()#line:450
        O0O00O00OO00OO00O ={}#line:451
        if O0OO0O00OO00OOOO0 and type (O0OO0O00OO00OOOO0 )!=str :#line:452
            O0O00O00OO00OO00O =OO0O0O0OOOOOO0O00 .parse_app_usage_info (O0OO0O00OO00OOOO0 [0 ])#line:453
        O0O0O0O00OO0OOO0O =[]#line:454
        if O0O00O00OO00OO00O :#line:455
            OOOOOO000000O0O00 =O0O00O00OO00OO00O ["disks"]#line:456
            for OOO000O00OO0O000O ,OO0O000O0OOO0OOOO in OOOOOO000000O0O00 .items ():#line:457
                O0O00O0000OOOO00O =int (OO0O000O0OOO0OOOO ["usage"])#line:458
                O0O00000O0OO0OO00 =int (OO0O000O0OOO0OOOO ["total"])#line:459
                O00OO00000O0O0O0O =round (O0O00O0000OOOO00O /O0O00000O0OO0OO00 ,2 )#line:460
                O0O0OO0O0OO00OO0O =int (OO0O000O0OOO0OOOO ["iusage"])#line:462
                OO00O00OO0OO000O0 =int (OO0O000O0OOO0OOOO ["itotal"])#line:463
                if OO00O00OO0OO000O0 >0 :#line:464
                    OOOOOO0O0OO0OOOO0 =round (O0O0OO0O0OO00OO0O /OO00O00OO0OO000O0 ,2 )#line:465
                else :#line:466
                    OOOOOO0O0OO0OOOO0 =0 #line:467
                if O00OO00000O0O0O0O >=0.8 :#line:471
                    O0O0O0O00OO0OOO0O .append ({"name":OOO000O00OO0O000O ,"percent":O00OO00000O0O0O0O *100 ,"ipercent":OOOOOO0O0OO0OOOO0 *100 ,"usage":O0O00O0000OOOO00O ,"total":O0O00000O0OO0OO00 ,"iusage":O0O0OO0O0OO00OO0O ,"itotal":OO00O00OO0OO000O0 })#line:480
        O00OO00O0OOO0000O =len (O0O0O0O00OO0OOO0O )#line:482
        O00000OO000OO00OO =""#line:483
        O0O0O00000OOOO00O =0 #line:484
        if O00OO00O0OOO0000O ==0 :#line:485
            O0O0O00000OOOO00O =20 #line:486
        else :#line:487
            O00000OO000OO00OO ="有磁盘空间占用已经超过80%"#line:488
        OO00O0O000O00O0O0 ={"ex":O00OO00O0OOO0000O ,"detail":O0O0O0O00OO0OOO0O }#line:493
        OOOO0OO0O0O00OO00 =public .M ("system").dbfile ("system").table ("server_status").where ("addtime>=? and addtime<=?",(O0000OOOOOOOOO00O ,O0OO0O00OO0O00OOO ,)).order ("addtime desc").select ()#line:497
        OOOO0O00OO00000OO =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:502
        O0OOOOOO00OOO0OOO ={}#line:504
        OO0O00O00OO0O00O0 =0 #line:505
        OO0000O000OO00O00 =""#line:506
        for O000OO00O0000OO0O ,OOO0OOOOOO0OO00O0 in enumerate (OOOO0O00OO00000OO ):#line:507
            if OOO0OOOOOO0OO00O0 =="pure-ftpd":#line:508
                OOO0OOOOOO0OO00O0 ="ftpd"#line:509
            OOO000O00000OOO0O =0 #line:510
            O00O00O0OOOOOOO0O =[]#line:511
            for OOOO0O000OO000OOO in OOOO0OO0O0O00OO00 :#line:512
                _OOO0OO0O00000O0O0 =OOOO0O000OO000OOO ["status"]#line:515
                if O000OO00O0000OO0O <len (_OOO0OO0O00000O0O0 ):#line:516
                    if _OOO0OO0O00000O0O0 [O000OO00O0000OO0O ]=="2":#line:517
                        O00O00O0OOOOOOO0O .append ({"time":OOOO0O000OO000OOO ["addtime"],"desc":"退出"})#line:518
                        OOO000O00000OOO0O +=1 #line:519
                        OO0O00O00OO0O00O0 +=1 #line:520
            O0OOOOOO00OOO0OOO [OOO0OOOOOO0OO00O0 ]={"ex":OOO000O00000OOO0O ,"detail":O00O00O0OOOOOOO0O }#line:525
        O0O0OOOOOOO00O000 =0 #line:527
        if OO0O00O00OO0O00O0 ==0 :#line:528
            O0O0OOOOOOO00O000 =20 #line:529
        else :#line:530
            OO0000O000OO00O00 ="系统级服务有出现异常退出情况"#line:531
        O0O0O000O0000OOOO =public .M ("crontab").field ("sName,sType").where ("sType in (?, ?)",("database","site",)).select ()#line:534
        OO0OOOO000000O000 =set (OOO0000OOO00OO000 ["sName"]for OOO0000OOO00OO000 in O0O0O000O0000OOOO if OOO0000OOO00OO000 ["sType"]=="database")#line:537
        O00OOOO0OOOO00O00 ="ALL"in OO0OOOO000000O000 #line:538
        OO0OOO0O0O000OO00 =set (O000O00O0OO0O0O00 ["sName"]for O000O00O0OO0O0O00 in O0O0O000O0000OOOO if O000O00O0OO0O0O00 ["sType"]=="site")#line:539
        O000OO00OO00O000O ="ALL"in OO0OOO0O0O000OO00 #line:540
        OO0O00OOOOO0000O0 =[]#line:541
        O00O0000OOO000O00 =[]#line:542
        if not O00OOOO0OOOO00O00 :#line:543
            OOO0OO000OO0O0OO0 =public .M ("databases").field ("name").select ()#line:544
            for O00OO00O00OO0000O in OOO0OO000OO0O0OO0 :#line:545
                OOOOO0OOOOO000OOO =O00OO00O00OO0000O ["name"]#line:546
                if OOOOO0OOOOO000OOO not in OO0OOOO000000O000 :#line:547
                    OO0O00OOOOO0000O0 .append ({"name":OOOOO0OOOOO000OOO })#line:548
        if not O000OO00OO00O000O :#line:550
            OOOOO0000OOOOOOO0 =public .M ("sites").field ("name").select ()#line:551
            for O0OO0O000000O0O0O in OOOOO0000OOOOOOO0 :#line:552
                OOOOOO0OO0OOO000O =O0OO0O000000O0O0O ["name"]#line:553
                if OOOOOO0OO0OOO000O not in OO0OOO0O0O000OO00 :#line:554
                    O00O0000OOO000O00 .append ({"name":OOOOOO0OO0OOO000O })#line:555
        OO0OO000O0OOO0OOO =public .M ("system").dbfile ("system").table ("backup_status").where ("addtime>=? and addtime<=?",(O0000OOOOOOOOO00O ,O0OO0O00OO0O00OOO )).select ()#line:558
        OO00000OOOOOO00O0 ={"database":{"no_backup":OO0O00OOOOO0000O0 ,"backup":[]},"site":{"no_backup":O00O0000OOO000O00 ,"backup":[]},"path":{"no_backup":[],"backup":[]}}#line:573
        O0O000O000000OOOO =0 #line:574
        for OOO000OO000OOO000 in OO0OO000O0OOO0OOO :#line:575
            O0OOOOO000OOOOOO0 =OOO000OO000OOO000 ["status"]#line:576
            if O0OOOOO000OOOOOO0 :#line:577
                continue #line:578
            O0O000O000000OOOO +=1 #line:580
            OO0O0000O00O0O0OO =OOO000OO000OOO000 ["id"]#line:581
            O0O00000OOOOOOO00 =public .M ("crontab").where ("id=?",(OO0O0000O00O0O0OO )).find ()#line:582
            if not O0O00000OOOOOOO00 :#line:583
                continue #line:584
            OO0O000O0O0OO0O00 =O0O00000OOOOOOO00 ["sType"]#line:585
            if not OO0O000O0O0OO0O00 :#line:586
                continue #line:587
            OOOOO000000O0OO0O =O0O00000OOOOOOO00 ["name"]#line:588
            OO00OO0O0O0O00O0O =OOO000OO000OOO000 ["addtime"]#line:589
            O000O0OO000O0OOOO =OOO000OO000OOO000 ["target"]#line:590
            if OO0O000O0O0OO0O00 not in OO00000OOOOOO00O0 .keys ():#line:591
                OO00000OOOOOO00O0 [OO0O000O0O0OO0O00 ]={}#line:592
                OO00000OOOOOO00O0 [OO0O000O0O0OO0O00 ]["backup"]=[]#line:593
                OO00000OOOOOO00O0 [OO0O000O0O0OO0O00 ]["no_backup"]=[]#line:594
            OO00000OOOOOO00O0 [OO0O000O0O0OO0O00 ]["backup"].append ({"name":OOOOO000000O0OO0O ,"target":O000O0OO000O0OOOO ,"status":O0OOOOO000OOOOOO0 ,"target":O000O0OO000O0OOOO ,"time":OO00OO0O0O0O00O0O })#line:601
        O000OOOOO00OO0O00 =""#line:603
        OOO000O0OO00OO0OO =0 #line:604
        if O0O000O000000OOOO ==0 :#line:605
            OOO000O0OO00OO0OO =20 #line:606
        else :#line:607
            O000OOOOO00OO0O00 ="有计划任务备份失败"#line:608
        if len (OO0O00OOOOO0000O0 )==0 :#line:610
            OOO000O0OO00OO0OO +=10 #line:611
        else :#line:612
            if O000OOOOO00OO0O00 :#line:613
                O000OOOOO00OO0O00 +=";"#line:614
            O000OOOOO00OO0O00 +="有数据库未及时备份"#line:615
        if len (O00O0000OOO000O00 )==0 :#line:617
            OOO000O0OO00OO0OO +=10 #line:618
        else :#line:619
            if O000OOOOO00OO0O00 :#line:620
                O000OOOOO00OO0O00 +=";"#line:621
            O000OOOOO00OO0O00 +="有网站未备份"#line:622
        O0O0OO0OOOOO000O0 =0 #line:625
        O00OOO000O00O000O =public .M ('logs').where ('addtime like ? and type=?',(str (OO00000000OOOOO00 )+"%",'用户登录',)).select ()#line:626
        O000OO0OOO0OO0O0O =[]#line:627
        if O00OOO000O00O000O and type (O00OOO000O00O000O )==list :#line:628
            for O0OO00OOOOO0O0OO0 in O00OOO000O00O000O :#line:629
                OO0OO0OOOOO0OO000 =O0OO00OOOOO0O0OO0 ["log"]#line:630
                if OO0OO0OOOOO0OO000 .find ("失败")>=0 or OO0OO0OOOOO0OO000 .find ("错误")>=0 :#line:631
                    O0O0OO0OOOOO000O0 +=1 #line:632
                    O000OO0OOO0OO0O0O .append ({"time":time .mktime (time .strptime (O0OO00OOOOO0O0OO0 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O0OO00OOOOO0O0OO0 ["log"],"username":O0OO00OOOOO0O0OO0 ["username"],})#line:637
            O000OO0OOO0OO0O0O .sort (key =lambda O000000O00OO000O0 :O000000O00OO000O0 ["time"])#line:638
        O00OO000OO0O00OO0 =public .M ('logs').where ('type=?',('SSH安全',)).where ("addtime like ?",(str (OO00000000OOOOO00 )+"%",)).select ()#line:640
        OO000000O0O00000O =[]#line:642
        O0O0000O0OOO0OO0O =0 #line:643
        if O00OO000OO0O00OO0 :#line:644
            for O0OO00OOOOO0O0OO0 in O00OO000OO0O00OO0 :#line:645
                OO0OO0OOOOO0OO000 =O0OO00OOOOO0O0OO0 ["log"]#line:646
                if OO0OO0OOOOO0OO000 .find ("存在异常")>=0 :#line:647
                    O0O0000O0OOO0OO0O +=1 #line:648
                    OO000000O0O00000O .append ({"time":time .mktime (time .strptime (O0OO00OOOOO0O0OO0 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O0OO00OOOOO0O0OO0 ["log"],"username":O0OO00OOOOO0O0OO0 ["username"]})#line:653
            OO000000O0O00000O .sort (key =lambda OOOOOO0O0OO000OOO :OOOOOO0O0OO000OOO ["time"])#line:654
        OOOO0OOOO0OOOO0O0 =""#line:656
        O0O00O0O00OOO0OO0 =0 #line:657
        if O0O0000O0OOO0OO0O ==0 :#line:658
            O0O00O0O00OOO0OO0 =10 #line:659
        else :#line:660
            OOOO0OOOO0OOOO0O0 ="SSH有异常登录"#line:661
        if O0O0OO0OOOOO000O0 ==0 :#line:663
            O0O00O0O00OOO0OO0 +=10 #line:664
        else :#line:665
            if O0O0OO0OOOOO000O0 >10 :#line:666
                O0O00O0O00OOO0OO0 -=10 #line:667
            if OOOO0OOOO0OOOO0O0 :#line:668
                OOOO0OOOO0OOOO0O0 +=";"#line:669
            OOOO0OOOO0OOOO0O0 +="面板登录有错误".format (O0O0OO0OOOOO000O0 )#line:670
        OOOO0OO0O0O00OO00 ={"panel":{"ex":O0O0OO0OOOOO000O0 ,"detail":O000OO0OOO0OO0O0O },"ssh":{"ex":O0O0000O0OOO0OO0O ,"detail":OO000000O0O00000O }}#line:680
        OO0O000O00O0O0000 =OOO00OOO000000000 +O0O0OOO000O000000 +O0O0O00000OOOO00O +O0O0OOOOOOO00O000 +OOO000O0OO00OO0OO +O0O00O0O00OOO0OO0 #line:682
        OO000OOO0000O0O0O =[OOO000O00O0O00OO0 ,OO0O0000O0OOO0OOO ,O00000OO000OO00OO ,OO0000O000OO00O00 ,O000OOOOO00OO0O00 ,OOOO0OOOO0OOOO0O0 ]#line:683
        OOOOOOO000000O000 =[]#line:684
        for OOO000O0O0OO00O00 in OO000OOO0000O0O0O :#line:685
            if OOO000O0O0OO00O00 :#line:686
                if OOO000O0O0OO00O00 .find (";")>=0 :#line:687
                    for O000O000O0O00OO00 in OOO000O0O0OO00O00 .split (";"):#line:688
                        OOOOOOO000000O000 .append (O000O000O0O00OO00 )#line:689
                else :#line:690
                    OOOOOOO000000O000 .append (OOO000O0O0OO00O00 )#line:691
        if not OOOOOOO000000O000 :#line:693
            OOOOOOO000000O000 .append ("服务器运行正常，请继续保持！")#line:694
        O0OOOOO00O0O0OOO0 =OO0O0O0OOOOOO0O00 .evaluate (OO0O000O00O0O0000 )#line:698
        return {"data":{"cpu":O00O0O0O0OO0O000O ,"ram":O0O00O0OO0O0O0OO0 ,"disk":OO00O0O000O00O0O0 ,"server":O0OOOOOO00OOO0OOO ,"backup":OO00000OOOOOO00O0 ,"exception":OOOO0OO0O0O00OO00 ,},"evaluate":O0OOOOO00O0O0OOO0 ,"score":OO0O000O00O0O0000 ,"date":O0O0O0O0OOOO000O0 ,"summary":OOOOOOO000000O000 ,"status":True }#line:715
    def evaluate (O00O0OO0O0OOO00OO ,OO00OOO0OO0O0000O ):#line:717
        OO0O00O0O0OO0O0O0 =""#line:718
        if OO00OOO0OO0O0000O >=100 :#line:719
            OO0O00O0O0OO0O0O0 ="正常"#line:720
        elif OO00OOO0OO0O0000O >=80 :#line:721
            OO0O00O0O0OO0O0O0 ="良好"#line:722
        else :#line:723
            OO0O00O0O0OO0O0O0 ="一般"#line:724
        return OO0O00O0O0OO0O0O0 #line:725
    def get_daily_list (O0OOO0OOO0000000O ,O0O00OOOOO000OOO0 ):#line:727
        O00O0000O00000O0O =public .M ("system").dbfile ("system").table ("daily").where ("time_key>?",0 ).select ()#line:728
        OOO00OO0OO0O0OOOO =[]#line:729
        for O0O0OO00OOO000OOO in O00O0000O00000O0O :#line:730
            O0O0OO00OOO000OOO ["evaluate"]=O0OOO0OOO0000000O .evaluate (O0O0OO00OOO000OOO ["evaluate"])#line:731
            OOO00OO0OO0O0OOOO .append (O0O0OO00OOO000OOO )#line:732
        return OOO00OO0OO0O0OOOO 