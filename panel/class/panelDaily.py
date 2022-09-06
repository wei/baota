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
    def check_databases (O0O00O0O0O00O0OO0 ):#line:30
        ""#line:31
        O00OOOOO00O0O0O00 =["app_usage","server_status","backup_status","daily"]#line:32
        import sqlite3 #line:33
        OOOO0000O0OO0O000 =sqlite3 .connect ("/www/server/panel/data/system.db")#line:34
        OOOO000O000O0O0OO =OOOO0000O0OO0O000 .cursor ()#line:35
        OOOO0OO0O0O00000O =",".join (["'"+O000OO0O0O00O0OOO +"'"for O000OO0O0O00O0OOO in O00OOOOO00O0O0O00 ])#line:36
        O00O00OO0O0OOO0O0 =OOOO000O000O0O0OO .execute ("SELECT name FROM sqlite_master WHERE type='table' and name in ({})".format (OOOO0OO0O0O00000O ))#line:37
        OOO0000O0OOO000O0 =O00O00OO0O0OOO0O0 .fetchall ()#line:38
        OO00OO0OO00O0O0OO =False #line:41
        OO00OO0OO0O0O00O0 =[]#line:42
        if OOO0000O0OOO000O0 :#line:43
            OO00OO0OO0O0O00O0 =[OOO0O0000OOOO0O0O [0 ]for OOO0O0000OOOO0O0O in OOO0000O0OOO000O0 ]#line:44
        if "app_usage"not in OO00OO0OO0O0O00O0 :#line:46
            O0OOOOOOO00OO0O00 ='''CREATE TABLE IF NOT EXISTS `app_usage` (
                    `time_key` INTEGER PRIMARY KEY,
                    `app` TEXT,
                    `disks` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:52
            OOOO000O000O0O0OO .execute (O0OOOOOOO00OO0O00 )#line:53
            OO00OO0OO00O0O0OO =True #line:54
        if "server_status"not in OO00OO0OO0O0O00O0 :#line:56
            print ("创建server_status表:")#line:57
            O0OOOOOOO00OO0O00 ='''CREATE TABLE IF NOT EXISTS `server_status` (
                    `status` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:61
            OOOO000O000O0O0OO .execute (O0OOOOOOO00OO0O00 )#line:62
            OO00OO0OO00O0O0OO =True #line:63
        if "backup_status"not in OO00OO0OO0O0O00O0 :#line:65
            print ("创建备份状态表:")#line:66
            O0OOOOOOO00OO0O00 ='''CREATE TABLE IF NOT EXISTS `backup_status` (
                    `id` INTEGER,
                    `target` TEXT,
                    `status` INTEGER,
                    `msg` TEXT DEFAULT "",
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:73
            OOOO000O000O0O0OO .execute (O0OOOOOOO00OO0O00 )#line:74
            OO00OO0OO00O0O0OO =True #line:75
        if "daily"not in OO00OO0OO0O0O00O0 :#line:77
            O0OOOOOOO00OO0O00 ='''CREATE TABLE IF NOT EXISTS `daily` (
                    `time_key` INTEGER,
                    `evaluate` INTEGER,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:82
            OOOO000O000O0O0OO .execute (O0OOOOOOO00OO0O00 )#line:83
            OO00OO0OO00O0O0OO =True #line:84
        if OO00OO0OO00O0O0OO :#line:86
            OOOO0000O0OO0O000 .commit ()#line:87
        OOOO000O000O0O0OO .close ()#line:88
        OOOO0000O0OO0O000 .close ()#line:89
        return True #line:90
    def get_time_key (O00OO0OOOOOOOO00O ,date =None ):#line:92
        if date is None :#line:93
            date =time .localtime ()#line:94
        O0OOOO00OO00O0O0O =0 #line:95
        O0O00OOO0O0O0O0OO ="%Y%m%d"#line:96
        if type (date )==time .struct_time :#line:97
            O0OOOO00OO00O0O0O =int (time .strftime (O0O00OOO0O0O0O0OO ,date ))#line:98
        if type (date )==str :#line:99
            O0OOOO00OO00O0O0O =int (time .strptime (date ,O0O00OOO0O0O0O0OO ))#line:100
        return O0OOOO00OO00O0O0O #line:101
    def store_app_usage (O00000O000O0000OO ,time_key =None ):#line:103
        ""#line:111
        O00000O000O0000OO .check_databases ()#line:113
        if time_key is None :#line:115
            time_key =O00000O000O0000OO .get_time_key ()#line:116
        OO00OOOO0O00OOOOO =public .M ("system").dbfile ("system").table ("app_usage")#line:118
        OOO0O0O0OOO0O0OOO =OO00OOOO0O00OOOOO .field ("time_key").where ("time_key=?",(time_key )).find ()#line:119
        if OOO0O0O0OOO0O0OOO and "time_key"in OOO0O0O0OOO0O0OOO :#line:120
            if OOO0O0O0OOO0O0OOO ["time_key"]==time_key :#line:121
                return True #line:123
        OOOOOO00O0OO00OOO =public .M ('sites').field ('path').select ()#line:125
        O00O00OOOO0000O0O =0 #line:126
        for OOOO0OOOO0O0OOO00 in OOOOOO00O0OO00OOO :#line:127
            O0O000OOOO00O0O0O =OOOO0OOOO0O0OOO00 ["path"]#line:128
            if O0O000OOOO00O0O0O :#line:129
                O00O00OOOO0000O0O +=public .get_path_size (O0O000OOOO00O0O0O )#line:130
        O000O00OO000O000O =public .get_path_size ("/www/server/data")#line:132
        O0O0OOOOO0O00O00O =public .M ("ftps").field ("path").select ()#line:134
        O000000000OO00O00 =0 #line:135
        for OOOO0OOOO0O0OOO00 in O0O0OOOOO0O00O00O :#line:136
            OOO000O000OO0OO0O =OOOO0OOOO0O0OOO00 ["path"]#line:137
            if OOO000O000OO0OO0O :#line:138
                O000000000OO00O00 +=public .get_path_size (OOO000O000OO0OO0O )#line:139
        OO0O00OOO00OOO0O0 =public .get_path_size ("/www/server/panel/plugin")#line:141
        OO00O000OOO000O0O =["/www/server/total","/www/server/btwaf","/www/server/coll","/www/server/nginx","/www/server/apache","/www/server/redis"]#line:149
        for O00OO0OOO00O00O0O in OO00O000OOO000O0O :#line:150
            OO0O00OOO00OOO0O0 +=public .get_path_size (O00OO0OOO00O00O0O )#line:151
        OO000O0O0O0OO0000 =system ().GetDiskInfo2 (human =False )#line:153
        O00O0OOOOOOOOO0OO =""#line:154
        OO00OO000OO0OO00O =0 #line:155
        O0OO0O0OO000000OO =0 #line:156
        for OOOO0O00OOO0O000O in OO000O0O0O0OO0000 :#line:157
            O0O000OO0O000OO00 =OOOO0O00OOO0O000O ["path"]#line:158
            if O00O0OOOOOOOOO0OO :#line:159
                O00O0OOOOOOOOO0OO +="-"#line:160
            OO00O0OO00OO0000O ,OO00OO0OO0O000OOO ,O0OOO00000OO0O00O ,O0O0O000000O00O0O =OOOO0O00OOO0O000O ["size"]#line:161
            OO0O00000O000OO0O ,OO0O0000OO000O0O0 ,_OO0000000O0000O0O ,_O00OOOOOOOO000000 =OOOO0O00OOO0O000O ["inodes"]#line:162
            O00O0OOOOOOOOO0OO ="{},{},{},{},{}".format (O0O000OO0O000OO00 ,OO00OO0OO0O000OOO ,OO00O0OO00OO0000O ,OO0O0000OO000O0O0 ,OO0O00000O000OO0O )#line:163
            if O0O000OO0O000OO00 =="/":#line:164
                OO00OO000OO0OO00O =OO00O0OO00OO0000O #line:165
                O0OO0O0OO000000OO =OO00OO0OO0O000OOO #line:166
        OOOO0O0OOOOO00000 ="{},{},{},{},{},{}".format (OO00OO000OO0OO00O ,O0OO0O0OO000000OO ,O00O00OOOO0000O0O ,O000O00OO000O000O ,O000000000OO00O00 ,OO0O00OOO00OOO0O0 )#line:171
        OOOO0OO0OOOOO00O0 =public .M ("system").dbfile ("system").table ("app_usage").add ("time_key,app,disks",(time_key ,OOOO0O0OOOOO00000 ,O00O0OOOOOOOOO0OO ))#line:173
        if OOOO0OO0OOOOO00O0 ==time_key :#line:174
            return True #line:175
        return False #line:178
    def parse_char_unit (OOOO000000O00O000 ,O0OOO0O000000O000 ):#line:180
        OO00OOO000OOO0O00 =0 #line:181
        try :#line:182
            OO00OOO000OOO0O00 =float(O0OOO0O000000O000 )#line:183
        except :#line:184
            O00OOOO0OOO0OO00O =O0OOO0O000000O000 #line:185
            if O00OOOO0OOO0OO00O .find ("G")!=-1 :#line:186
                O00OOOO0OOO0OO00O =O00OOOO0OOO0OO00O .replace ("G","")#line:187
                OO00OOO000OOO0O00 =float(O00OOOO0OOO0OO00O )*1024 *1024 *1024 #line:188
            elif O00OOOO0OOO0OO00O .find ("M")!=-1 :#line:189
                O00OOOO0OOO0OO00O =O00OOOO0OOO0OO00O .replace ("M","")#line:190
                OO00OOO000OOO0O00 =float(O00OOOO0OOO0OO00O )*1024 *1024 #line:191
            else :#line:192
                OO00OOO000OOO0O00 =float(O00OOOO0OOO0OO00O )#line:193
        return OO00OOO000OOO0O00 #line:194
    def parse_app_usage_info (O0OOO0OOO0OO0OOO0 ,OO0OO00O0OO00000O ):#line:196
        ""#line:197
        if not OO0OO00O0OO00000O :#line:198
            return {}#line:199
        print (OO0OO00O0OO00000O )#line:200
        O0OOO00O00000O000 ,OOOO0O0O0O00OO000 ,OO0OOO0OOO0000OOO ,O00O00000000O00OO ,O00OO00O0O000O000 ,OOOO00000O00O0000 =OO0OO00O0OO00000O ["app"].split (",")#line:201
        OO00O00O0O0OO00OO =OO0OO00O0OO00000O ["disks"].split ("-")#line:202
        OOOOO0OOOOO00OOO0 ={}#line:203
        for OOOOO0000O0OO00O0 in OO00O00O0O0OO00OO :#line:204
            OO00O0O0OO0O0O000 ,O0OOO0OO000000O0O ,OO000O00O0OOO0O00 ,OO000OO0OOOO00O0O ,O00O0000OO0O0O0OO =OOOOO0000O0OO00O0 .split (",")#line:205
            O00OO0O00OOOOO0O0 ={}#line:206
            O00OO0O00OOOOO0O0 ["usage"]=O0OOO0OOO0OO0OOO0 .parse_char_unit (O0OOO0OO000000O0O )#line:207
            O00OO0O00OOOOO0O0 ["total"]=O0OOO0OOO0OO0OOO0 .parse_char_unit (OO000O00O0OOO0O00 )#line:208
            O00OO0O00OOOOO0O0 ["iusage"]=OO000OO0OOOO00O0O #line:209
            O00OO0O00OOOOO0O0 ["itotal"]=O00O0000OO0O0O0OO #line:210
            OOOOO0OOOOO00OOO0 [OO00O0O0OO0O0O000 ]=O00OO0O00OOOOO0O0 #line:211
        return {"apps":{"disk_total":O0OOO00O00000O000 ,"disk_usage":OOOO0O0O0O00OO000 ,"sites":OO0OOO0OOO0000OOO ,"databases":O00O00000000O00OO ,"ftps":O00OO00O0O000O000 ,"plugins":OOOO00000O00O0000 },"disks":OOOOO0OOOOO00OOO0 }#line:222
    def get_app_usage (O00O00O0O000OOOO0 ,OO000O000O00OO0O0 ):#line:224
        O000O0O00OO000O00 =time .localtime ()#line:226
        O00O00OOOO0O00OOO =O00O00O0O000OOOO0 .get_time_key ()#line:227
        OO00000OOO0O0000O =time .localtime (time .mktime ((O000O0O00OO000O00 .tm_year ,O000O0O00OO000O00 .tm_mon ,O000O0O00OO000O00 .tm_mday -1 ,0 ,0 ,0 ,0 ,0 ,0 )))#line:230
        O0O0OOO0OO00O000O =O00O00O0O000OOOO0 .get_time_key (OO00000OOO0O0000O )#line:231
        O0OO0OO00000000O0 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key =? or time_key=?",(O00O00OOOO0O00OOO ,O0O0OOO0OO00O000O ))#line:233
        OO00OO00OOOO00000 =O0OO0OO00000000O0 .select ()#line:234
        if type (OO00OO00OOOO00000 )==str or not OO00OO00OOOO00000 :#line:237
            return {}#line:238
        O0000OO0OO0O000OO ={}#line:239
        OO00000OOO0OOOOO0 ={}#line:240
        for O0OO0OO000OO000OO in OO00OO00OOOO00000 :#line:241
            if O0OO0OO000OO000OO ["time_key"]==O00O00OOOO0O00OOO :#line:242
                O0000OO0OO0O000OO =O00O00O0O000OOOO0 .parse_app_usage_info (O0OO0OO000OO000OO )#line:243
            if O0OO0OO000OO000OO ["time_key"]==O0O0OOO0OO00O000O :#line:244
                OO00000OOO0OOOOO0 =O00O00O0O000OOOO0 .parse_app_usage_info (O0OO0OO000OO000OO )#line:245
        if not O0000OO0OO0O000OO :#line:247
            return {}#line:248
        for O00OOOO0OOOOO00OO ,OO00O0OOOOOO0OO0O in O0000OO0OO0O000OO ["disks"].items ():#line:251
            OO0OO0O0000O0O0OO =int (OO00O0OOOOOO0OO0O ["total"])#line:252
            OOO0O00OOOO0000O0 =int (OO00O0OOOOOO0OO0O ["usage"])#line:253
            OO0OO00OO0OO0000O =int (OO00O0OOOOOO0OO0O ["itotal"])#line:255
            OOOO000000O000OO0 =int (OO00O0OOOOOO0OO0O ["iusage"])#line:256
            if OO00000OOO0OOOOO0 and O00OOOO0OOOOO00OO in OO00000OOO0OOOOO0 ["disks"].keys ():#line:258
                O0O0OOO0O0OO0O00O =OO00000OOO0OOOOO0 ["disks"]#line:259
                O00OOO0000OOOOOOO =O0O0OOO0O0OO0O00O [O00OOOO0OOOOO00OO ]#line:260
                O00OO00O00000OOOO =int (O00OOO0000OOOOOOO ["total"])#line:261
                if O00OO00O00000OOOO ==OO0OO0O0000O0O0OO :#line:262
                    O0OO0OO00OOO0O0O0 =int (O00OOO0000OOOOOOO ["usage"])#line:263
                    OO0O0O000O0O000O0 =0 #line:264
                    OOO0O0OO00O0OO0OO =OOO0O00OOOO0000O0 -O0OO0OO00OOO0O0O0 #line:265
                    if OOO0O0OO00O0OO0OO >0 :#line:266
                        OO0O0O000O0O000O0 =round (OOO0O0OO00O0OO0OO /OO0OO0O0000O0O0OO ,2 )#line:267
                    OO00O0OOOOOO0OO0O ["incr"]=OO0O0O000O0O000O0 #line:268
                O000OO0000OO00OOO =int (O00OOO0000OOOOOOO ["itotal"])#line:271
                if True :#line:272
                    OOOO0O0OO0OO0000O =int (O00OOO0000OOOOOOO ["iusage"])#line:273
                    OOO00000O00O000O0 =0 #line:274
                    OOO0O0OO00O0OO0OO =OOOO000000O000OO0 -OOOO0O0OO0OO0000O #line:275
                    if OOO0O0OO00O0OO0OO >0 :#line:276
                        OOO00000O00O000O0 =round (OOO0O0OO00O0OO0OO /OO0OO00OO0OO0000O ,2 )#line:277
                    OO00O0OOOOOO0OO0O ["iincr"]=OOO00000O00O000O0 #line:278
        O000OO00000000000 =O0000OO0OO0O000OO ["apps"]#line:282
        O00O0O0000O0OO00O =int (O000OO00000000000 ["disk_total"])#line:283
        if OO00000OOO0OOOOO0 and OO00000OOO0OOOOO0 ["apps"]["disk_total"]==O000OO00000000000 ["disk_total"]:#line:284
            OOOOOO0O00OO0O0O0 =OO00000OOO0OOOOO0 ["apps"]#line:285
            for OO0OO0OO000OOOOO0 ,O00O000O0000O00OO in O000OO00000000000 .items ():#line:286
                if OO0OO0OO000OOOOO0 =="disks":continue #line:287
                if OO0OO0OO000OOOOO0 =="disk_total":continue #line:288
                if OO0OO0OO000OOOOO0 =="disk_usage":continue #line:289
                OO0O0000O000O000O =0 #line:290
                OO0OO0O00OO0OO00O =int (O00O000O0000O00OO )-int (OOOOOO0O00OO0O0O0 [OO0OO0OO000OOOOO0 ])#line:291
                if OO0OO0O00OO0OO00O >0 :#line:292
                    OO0O0000O000O000O =round (OO0OO0O00OO0OO00O /O00O0O0000O0OO00O ,2 )#line:293
                O000OO00000000000 [OO0OO0OO000OOOOO0 ]={"val":O00O000O0000O00OO ,"incr":OO0O0000O000O000O }#line:298
        return O0000OO0OO0O000OO #line:299
    def get_timestamp_interval (O000O0OO000OOOOOO ,O00O0OOOO00O0OOOO ):#line:301
        OO0OOOO000OOOOO0O =None #line:302
        O0OO0O0OOO00OOOOO =None #line:303
        OO0OOOO000OOOOO0O =time .mktime ((O00O0OOOO00O0OOOO .tm_year ,O00O0OOOO00O0OOOO .tm_mon ,O00O0OOOO00O0OOOO .tm_mday ,0 ,0 ,0 ,0 ,0 ,0 ))#line:305
        O0OO0O0OOO00OOOOO =time .mktime ((O00O0OOOO00O0OOOO .tm_year ,O00O0OOOO00O0OOOO .tm_mon ,O00O0OOOO00O0OOOO .tm_mday ,23 ,59 ,59 ,0 ,0 ,0 ))#line:307
        return OO0OOOO000OOOOO0O ,O0OO0O0OOO00OOOOO #line:308
    def check_server (OO0OO00OOOO0O0O00 ):#line:311
        try :#line:312
            OO000O00OO0O0OOOO =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:315
            OOO0O00OO00OOO00O =panelPlugin ()#line:316
            OOO0OO0O00OO0OO00 =public .dict_obj ()#line:317
            OO0O00OOO00O0OOOO =""#line:318
            for O000OOO000OO0OO00 in OO000O00OO0O0OOOO :#line:319
                O0O0000O00OO00000 =False #line:320
                O0O0O00000OOO0000 =False #line:321
                OOO0OO0O00OO0OO00 .name =O000OOO000OO0OO00 #line:322
                OO0O0O0O0000OO0OO =OOO0O00OO00OOO00O .getPluginInfo (OOO0OO0O00OO0OO00 )#line:323
                if not OO0O0O0O0000OO0OO :#line:324
                    continue #line:325
                O0OO00OOOO0OO0OO0 =OO0O0O0O0000OO0OO ["versions"]#line:326
                for O0000OO00O0O0O0OO in O0OO00OOOO0OO0OO0 :#line:328
                    if O0000OO00O0O0O0OO ["status"]:#line:331
                        O0O0O00000OOO0000 =True #line:332
                    if "run"in O0000OO00O0O0O0OO .keys ()and O0000OO00O0O0O0OO ["run"]:#line:333
                        O0O0O00000OOO0000 =True #line:335
                        O0O0000O00OO00000 =True #line:336
                        break #line:337
                OOOO0OOOO000OO00O =0 #line:338
                if O0O0O00000OOO0000 :#line:339
                    OOOO0OOOO000OO00O =1 #line:340
                    if not O0O0000O00OO00000 :#line:342
                        OOOO0OOOO000OO00O =2 #line:343
                OO0O00OOO00O0OOOO +=str (OOOO0OOOO000OO00O )#line:344
            if '2'in OO0O00OOO00O0OOOO :#line:348
                public .M ("system").dbfile ("server_status").add ("status, addtime",(OO0O00OOO00O0OOOO ,time .time ()))#line:350
        except Exception as O000OO0OOOO0OO0O0 :#line:351
            return True #line:353
    def get_daily_data (OOO0000OO00OO0OOO ,O0O0OO0OO0OO0O00O ):#line:355
        ""#line:356
        OO0O00O00O0O0OOO0 ="IS_PRO_OR_LTD_FOR_PANEL_DAILY"#line:358
        OO00OO0OO00000OOO =cache .get (OO0O00O00O0O0OOO0 )#line:359
        if not OO00OO0OO00000OOO :#line:360
            try :#line:361
                O0O00OO0OOOOOO000 =panelPlugin ()#line:362
                O000O0OOO00O0OO00 =O0O00OO0OOOOOO000 .get_soft_list (O0O0OO0OO0OO0O00O )#line:363
                if O000O0OOO00O0OO00 ["pro"]<0 and O000O0OOO00O0OO00 ["ltd"]<0 :#line:364
                    if os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:365
                        os .remove ("/www/server/panel/data/start_daily.pl")#line:366
                    return {"status":False ,"msg":"No authorization.","data":[],"date":O0O0OO0OO0OO0O00O .date }#line:372
                cache .set (OO0O00O00O0O0OOO0 ,True ,86400 )#line:373
            except :#line:374
                return {"status":False ,"msg":"获取不到授权信息，请检查网络是否正常","data":[],"date":O0O0OO0OO0OO0O00O .date }#line:380
        if not os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:383
            public .writeFile ("/www/server/panel/data/start_daily.pl",O0O0OO0OO0OO0O00O .date )#line:384
        return OOO0000OO00OO0OOO .get_daily_data_local (O0O0OO0OO0OO0O00O .date )#line:385
    def get_daily_data_local (O0OOO00000OO0O0OO ,OOO000O000O00000O ):#line:387
        O0OOOOOO0000OO000 =time .strptime (OOO000O000O00000O ,"%Y%m%d")#line:388
        O0OOO0OOO0O00O0OO =O0OOO00000OO0O0OO .get_time_key (O0OOOOOO0000OO000 )#line:389
        O0OOO00000OO0O0OO .check_databases ()#line:391
        OOOO0O0OO0OO00O00 =time .strftime ("%Y-%m-%d",O0OOOOOO0000OO000 )#line:393
        OO0O0O00O00OOO000 =0 #line:394
        OOOO0O0OOO000OO00 ,O0OO000O00OOO0O00 =O0OOO00000OO0O0OO .get_timestamp_interval (O0OOOOOO0000OO000 )#line:395
        OOO00OO0O000OO00O =public .M ("system").dbfile ("system")#line:396
        OO0OOOO0O0OO0OOO0 =OOO00OO0O000OO00O .table ("process_high_percent")#line:397
        OO00O0OO0O0O00OO0 =OO0OOOO0O0OO0OOO0 .where ("addtime>=? and addtime<=?",(OOOO0O0OOO000OO00 ,O0OO000O00OOO0O00 )).order ("addtime").select ()#line:398
        OOOO0000OOOOOO0O0 =[]#line:402
        if len (OO00O0OO0O0O00OO0 )>0 :#line:403
            for O000O0OO00O0O0O00 in OO00O0OO0O0O00OO0 :#line:405
                O0O00O0000O0OO00O =int (O000O0OO00O0O0O00 ["cpu_percent"])#line:407
                if O0O00O0000O0OO00O >=80 :#line:408
                    OOOO0000OOOOOO0O0 .append ({"time":O000O0OO00O0O0O00 ["addtime"],"name":O000O0OO00O0O0O00 ["name"],"pid":O000O0OO00O0O0O00 ["pid"],"percent":O0O00O0000O0OO00O })#line:416
        OO00OOOO0O0O0O00O =len (OOOO0000OOOOOO0O0 )#line:418
        OO0O000O0000OO000 =0 #line:419
        O000OOO0O0O0000O0 =""#line:420
        if OO00OOOO0O0O0O00O ==0 :#line:421
            OO0O000O0000OO000 =20 #line:422
        else :#line:423
            O000OOO0O0O0000O0 ="CPU出现过载情况"#line:424
        OOOOOO00000OOO0OO ={"ex":OO00OOOO0O0O0O00O ,"detail":OOOO0000OOOOOO0O0 }#line:428
        OOOO0O0OO0OOO0O00 =[]#line:431
        if len (OO00O0OO0O0O00OO0 )>0 :#line:432
            for O000O0OO00O0O0O00 in OO00O0OO0O0O00OO0 :#line:434
                O0O0OO0OOO00OOO0O =float (O000O0OO00O0O0O00 ["memory"])#line:436
                OOOO0000O0OOO00O0 =psutil .virtual_memory ().total #line:437
                OO0OO00O00000O0O0 =round (100 *O0O0OO0OOO00OOO0O /OOOO0000O0OOO00O0 ,2 )#line:438
                if OO0OO00O00000O0O0 >=80 :#line:439
                    OOOO0O0OO0OOO0O00 .append ({"time":O000O0OO00O0O0O00 ["addtime"],"name":O000O0OO00O0O0O00 ["name"],"pid":O000O0OO00O0O0O00 ["pid"],"percent":OO0OO00O00000O0O0 })#line:447
        OO0O0O00OO000000O =len (OOOO0O0OO0OOO0O00 )#line:448
        O00OOO0OO0000O000 =""#line:449
        O00O00000O0000OO0 =0 #line:450
        if OO0O0O00OO000000O ==0 :#line:451
            O00O00000O0000OO0 =20 #line:452
        else :#line:453
            if OO0O0O00OO000000O >1 :#line:454
                O00OOO0OO0000O000 ="内存在多个时间点出现占用80%"#line:455
            else :#line:456
                O00OOO0OO0000O000 ="内存出现占用超过80%"#line:457
        O0OOO000O000O0000 ={"ex":OO0O0O00OO000000O ,"detail":OOOO0O0OO0OOO0O00 }#line:461
        OOO00OOO0O0O00O00 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key=?",(O0OOO0OOO0O00O0OO ,))#line:465
        O00000O0OO0OO00OO =OOO00OOO0O0O00O00 .select ()#line:466
        OOO00OO0O0OOO00OO ={}#line:467
        if O00000O0OO0OO00OO and type (O00000O0OO0OO00OO )!=str :#line:468
            OOO00OO0O0OOO00OO =O0OOO00000OO0O0OO .parse_app_usage_info (O00000O0OO0OO00OO [0 ])#line:469
        OO00OO0O0O00O000O =[]#line:470
        if OOO00OO0O0OOO00OO :#line:471
            OO000OO00OOO0O000 =OOO00OO0O0OOO00OO ["disks"]#line:472
            for OOO0OOOOO00OOO00O ,O0000OOOOO00OO0O0 in OO000OO00OOO0O000 .items ():#line:473
                OO00000O00O00OOOO =int (O0000OOOOO00OO0O0 ["usage"])#line:474
                OOOO0000O0OOO00O0 =int (O0000OOOOO00OO0O0 ["total"])#line:475
                OO000O000O0OO00O0 =round (OO00000O00O00OOOO /OOOO0000O0OOO00O0 ,2 )#line:476
                O0O00OO0OO0OO00O0 =int (O0000OOOOO00OO0O0 ["iusage"])#line:477
                OOOO0O00OO0OOOO0O =int (O0000OOOOO00OO0O0 ["itotal"])#line:478
                if OOOO0O00OO0OOOO0O >0 :#line:479
                    O0OO00000O0OOO0OO =round (O0O00OO0OO0OO00O0 /OOOO0O00OO0OOOO0O ,2 )#line:480
                else :#line:481
                    O0OO00000O0OOO0OO =0 #line:482
                if OO000O000O0OO00O0 >=0.8 :#line:486
                    OO00OO0O0O00O000O .append ({"name":OOO0OOOOO00OOO00O ,"percent":OO000O000O0OO00O0 *100 ,"ipercent":O0OO00000O0OOO0OO *100 ,"usage":OO00000O00O00OOOO ,"total":OOOO0000O0OOO00O0 ,"iusage":O0O00OO0OO0OO00O0 ,"itotal":OOOO0O00OO0OOOO0O })#line:495
        OO0O00OOO00O00O0O =len (OO00OO0O0O00O000O )#line:497
        O0O0OOOO0OOO00O0O =""#line:498
        OO00O0O0000O0OO00 =0 #line:499
        if OO0O00OOO00O00O0O ==0 :#line:500
            OO00O0O0000O0OO00 =20 #line:501
        else :#line:502
            O0O0OOOO0OOO00O0O ="有磁盘空间占用已经超过80%"#line:503
        O000OOO00OOO0O000 ={"ex":OO0O00OOO00O00O0O ,"detail":OO00OO0O0O00O000O }#line:508
        OO00000O00O000O00 =public .M ("system").dbfile ("system").table ("server_status").where ("addtime>=? and addtime<=?",(OOOO0O0OOO000OO00 ,O0OO000O00OOO0O00 ,)).order ("addtime desc").select ()#line:512
        O0O0O00O000O00OOO =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:517
        O0OOO00OO0O00OOO0 ={}#line:519
        OOOOO0OO00O00OOO0 =0 #line:520
        O0OOOOO0OO000OO0O =""#line:521
        for O0OOO0O00OO00O000 ,OO00O0OO00000OO0O in enumerate (O0O0O00O000O00OOO ):#line:522
            if OO00O0OO00000OO0O =="pure-ftpd":#line:523
                OO00O0OO00000OO0O ="ftpd"#line:524
            O00O00OO0O00O00O0 =0 #line:525
            O0OOOO0OOO00OO0OO =[]#line:526
            for OO0O0000O00000000 in OO00000O00O000O00 :#line:527
                _OOOO0OOO0OOO0OO0O =OO0O0000O00000000 ["status"]#line:530
                if O0OOO0O00OO00O000 <len (_OOOO0OOO0OOO0OO0O ):#line:531
                    if _OOOO0OOO0OOO0OO0O [O0OOO0O00OO00O000 ]=="2":#line:532
                        O0OOOO0OOO00OO0OO .append ({"time":OO0O0000O00000000 ["addtime"],"desc":"退出"})#line:533
                        O00O00OO0O00O00O0 +=1 #line:534
                        OOOOO0OO00O00OOO0 +=1 #line:535
            O0OOO00OO0O00OOO0 [OO00O0OO00000OO0O ]={"ex":O00O00OO0O00O00O0 ,"detail":O0OOOO0OOO00OO0OO }#line:540
        O0O00OOOO000OO00O =0 #line:542
        if OOOOO0OO00O00OOO0 ==0 :#line:543
            O0O00OOOO000OO00O =20 #line:544
        else :#line:545
            O0OOOOO0OO000OO0O ="系统级服务有出现异常退出情况"#line:546
        O00O0OO0000OOO00O =public .M ("crontab").field ("sName,sType").where ("sType in (?, ?)",("database","site",)).select ()#line:549
        OO0000O0OOOO00OOO =set (OO0O00OOO0OO0OOOO ["sName"]for OO0O00OOO0OO0OOOO in O00O0OO0000OOO00O if OO0O00OOO0OO0OOOO ["sType"]=="database")#line:552
        O0OO0000000OOO00O ="ALL"in OO0000O0OOOO00OOO #line:553
        O0OO00O0OOOOOOOO0 =set (O00000OO0O0O0O000 ["sName"]for O00000OO0O0O0O000 in O00O0OO0000OOO00O if O00000OO0O0O0O000 ["sType"]=="site")#line:554
        OOO0O0OOOOO00OO00 ="ALL"in O0OO00O0OOOOOOOO0 #line:555
        O0OO000O0OOO0000O =[]#line:556
        O0O0OOO0000OOOOOO =[]#line:557
        if not O0OO0000000OOO00O :#line:558
            OO000O00OOO00OO0O =public .M ("databases").field ("name").select ()#line:559
            for OO0OOO000O0O0O00O in OO000O00OOO00OO0O :#line:560
                O00OOO0OO0O0OO00O =OO0OOO000O0O0O00O ["name"]#line:561
                if O00OOO0OO0O0OO00O not in OO0000O0OOOO00OOO :#line:562
                    O0OO000O0OOO0000O .append ({"name":O00OOO0OO0O0OO00O })#line:563
        if not OOO0O0OOOOO00OO00 :#line:565
            O0O00O0O00OO0O00O =public .M ("sites").field ("name").select ()#line:566
            for O000O0OOOOO00O0O0 in O0O00O0O00OO0O00O :#line:567
                O0000OO0O00O000OO =O000O0OOOOO00O0O0 ["name"]#line:568
                if O0000OO0O00O000OO not in O0OO00O0OOOOOOOO0 :#line:569
                    O0O0OOO0000OOOOOO .append ({"name":O0000OO0O00O000OO })#line:570
        OO00OO0O000O00000 =public .M ("system").dbfile ("system").table ("backup_status").where ("addtime>=? and addtime<=?",(OOOO0O0OOO000OO00 ,O0OO000O00OOO0O00 )).select ()#line:573
        O00O000OO0O000000 ={"database":{"no_backup":O0OO000O0OOO0000O ,"backup":[]},"site":{"no_backup":O0O0OOO0000OOOOOO ,"backup":[]},"path":{"no_backup":[],"backup":[]}}#line:588
        O00OO00O0OOOO000O =0 #line:589
        for OOOO0O0O000OO0000 in OO00OO0O000O00000 :#line:590
            O0OOOO000O00000O0 =OOOO0O0O000OO0000 ["status"]#line:591
            if O0OOOO000O00000O0 :#line:592
                continue #line:593
            O00OO00O0OOOO000O +=1 #line:595
            O000O0OOO0OO0OOO0 =OOOO0O0O000OO0000 ["id"]#line:596
            O00O00OOOOOOOOO00 =public .M ("crontab").where ("id=?",(O000O0OOO0OO0OOO0 )).find ()#line:597
            if not O00O00OOOOOOOOO00 :#line:598
                continue #line:599
            OO0O0OOOO00OO0OO0 =O00O00OOOOOOOOO00 ["sType"]#line:600
            if not OO0O0OOOO00OO0OO0 :#line:601
                continue #line:602
            OO00OO0OO0OO00OOO =O00O00OOOOOOOOO00 ["name"]#line:603
            OOOO00OOO00O0OO0O =OOOO0O0O000OO0000 ["addtime"]#line:604
            O00O000O0OO00OOO0 =OOOO0O0O000OO0000 ["target"]#line:605
            if OO0O0OOOO00OO0OO0 not in O00O000OO0O000000 .keys ():#line:606
                O00O000OO0O000000 [OO0O0OOOO00OO0OO0 ]={}#line:607
                O00O000OO0O000000 [OO0O0OOOO00OO0OO0 ]["backup"]=[]#line:608
                O00O000OO0O000000 [OO0O0OOOO00OO0OO0 ]["no_backup"]=[]#line:609
            O00O000OO0O000000 [OO0O0OOOO00OO0OO0 ]["backup"].append ({"name":OO00OO0OO0OO00OOO ,"target":O00O000O0OO00OOO0 ,"status":O0OOOO000O00000O0 ,"target":O00O000O0OO00OOO0 ,"time":OOOO00OOO00O0OO0O })#line:616
        O00O0OO0OO00OO00O =""#line:618
        O000OO0OO0OOO00O0 =0 #line:619
        if O00OO00O0OOOO000O ==0 :#line:620
            O000OO0OO0OOO00O0 =20 #line:621
        else :#line:622
            O00O0OO0OO00OO00O ="有计划任务备份失败"#line:623
        if len (O0OO000O0OOO0000O )==0 :#line:625
            O000OO0OO0OOO00O0 +=10 #line:626
        else :#line:627
            if O00O0OO0OO00OO00O :#line:628
                O00O0OO0OO00OO00O +=";"#line:629
            O00O0OO0OO00OO00O +="有数据库未及时备份"#line:630
        if len (O0O0OOO0000OOOOOO )==0 :#line:632
            O000OO0OO0OOO00O0 +=10 #line:633
        else :#line:634
            if O00O0OO0OO00OO00O :#line:635
                O00O0OO0OO00OO00O +=";"#line:636
            O00O0OO0OO00OO00O +="有网站未备份"#line:637
        O00OO0O0000OOOOOO =0 #line:640
        OO00OOOO00OOO0000 =public .M ('logs').where ('addtime like ? and type=?',(str (OOOO0O0OO0OO00O00 )+"%",'用户登录',)).select ()#line:641
        OO00O0O0OO0O00O0O =[]#line:642
        if OO00OOOO00OOO0000 and type (OO00OOOO00OOO0000 )==list :#line:643
            for O00OO0O000OOOO0OO in OO00OOOO00OOO0000 :#line:644
                O0O0O00O00O000O00 =O00OO0O000OOOO0OO ["log"]#line:645
                if O0O0O00O00O000O00 .find ("失败")>=0 or O0O0O00O00O000O00 .find ("错误")>=0 :#line:646
                    O00OO0O0000OOOOOO +=1 #line:647
                    OO00O0O0OO0O00O0O .append ({"time":time .mktime (time .strptime (O00OO0O000OOOO0OO ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O00OO0O000OOOO0OO ["log"],"username":O00OO0O000OOOO0OO ["username"],})#line:652
            OO00O0O0OO0O00O0O .sort (key =lambda OOOO0O00O00O0000O :OOOO0O00O00O0000O ["time"])#line:653
        OOOO000O00O0OO0OO =public .M ('logs').where ('type=?',('SSH安全',)).where ("addtime like ?",(str (OOOO0O0OO0OO00O00 )+"%",)).select ()#line:655
        OO00OOO0O00OO0OO0 =[]#line:657
        O0O0OOOO0OOOOOO00 =0 #line:658
        if OOOO000O00O0OO0OO :#line:659
            for O00OO0O000OOOO0OO in OOOO000O00O0OO0OO :#line:660
                O0O0O00O00O000O00 =O00OO0O000OOOO0OO ["log"]#line:661
                if O0O0O00O00O000O00 .find ("存在异常")>=0 :#line:662
                    O0O0OOOO0OOOOOO00 +=1 #line:663
                    OO00OOO0O00OO0OO0 .append ({"time":time .mktime (time .strptime (O00OO0O000OOOO0OO ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O00OO0O000OOOO0OO ["log"],"username":O00OO0O000OOOO0OO ["username"]})#line:668
            OO00OOO0O00OO0OO0 .sort (key =lambda O00O000OOO0OO000O :O00O000OOO0OO000O ["time"])#line:669
        OOO000O000O00OOOO =""#line:671
        OO00O00OO0000O000 =0 #line:672
        if O0O0OOOO0OOOOOO00 ==0 :#line:673
            OO00O00OO0000O000 =10 #line:674
        else :#line:675
            OOO000O000O00OOOO ="SSH有异常登录"#line:676
        if O00OO0O0000OOOOOO ==0 :#line:678
            OO00O00OO0000O000 +=10 #line:679
        else :#line:680
            if O00OO0O0000OOOOOO >10 :#line:681
                OO00O00OO0000O000 -=10 #line:682
            if OOO000O000O00OOOO :#line:683
                OOO000O000O00OOOO +=";"#line:684
            OOO000O000O00OOOO +="面板登录有错误".format (O00OO0O0000OOOOOO )#line:685
        OO00000O00O000O00 ={"panel":{"ex":O00OO0O0000OOOOOO ,"detail":OO00O0O0OO0O00O0O },"ssh":{"ex":O0O0OOOO0OOOOOO00 ,"detail":OO00OOO0O00OO0OO0 }}#line:695
        OO0O0O00O00OOO000 =OO0O000O0000OO000 +O00O00000O0000OO0 +OO00O0O0000O0OO00 +O0O00OOOO000OO00O +O000OO0OO0OOO00O0 +OO00O00OO0000O000 #line:697
        O0OOO0O00O0O0OO0O =[O000OOO0O0O0000O0 ,O00OOO0OO0000O000 ,O0O0OOOO0OOO00O0O ,O0OOOOO0OO000OO0O ,O00O0OO0OO00OO00O ,OOO000O000O00OOOO ]#line:698
        OOOOO00O000O0OOOO =[]#line:699
        for O00OOO0OOO000O00O in O0OOO0O00O0O0OO0O :#line:700
            if O00OOO0OOO000O00O :#line:701
                if O00OOO0OOO000O00O .find (";")>=0 :#line:702
                    for O0OO0OO00000O0O00 in O00OOO0OOO000O00O .split (";"):#line:703
                        OOOOO00O000O0OOOO .append (O0OO0OO00000O0O00 )#line:704
                else :#line:705
                    OOOOO00O000O0OOOO .append (O00OOO0OOO000O00O )#line:706
        if not OOOOO00O000O0OOOO :#line:708
            OOOOO00O000O0OOOO .append ("服务器运行正常，请继续保持！")#line:709
        OO0OOOOO00OOOOOO0 =O0OOO00000OO0O0OO .evaluate (OO0O0O00O00OOO000 )#line:713
        return {"data":{"cpu":OOOOOO00000OOO0OO ,"ram":O0OOO000O000O0000 ,"disk":O000OOO00OOO0O000 ,"server":O0OOO00OO0O00OOO0 ,"backup":O00O000OO0O000000 ,"exception":OO00000O00O000O00 ,},"evaluate":OO0OOOOO00OOOOOO0 ,"score":OO0O0O00O00OOO000 ,"date":O0OOO0OOO0O00O0OO ,"summary":OOOOO00O000O0OOOO ,"status":True }#line:730
    def evaluate (O00O00OOOO0OO0O0O ,O0OOOO000OOOO000O ):#line:732
        OO0O0O0O00OO0OO00 =""#line:733
        if O0OOOO000OOOO000O >=100 :#line:734
            OO0O0O0O00OO0OO00 ="正常"#line:735
        elif O0OOOO000OOOO000O >=80 :#line:736
            OO0O0O0O00OO0OO00 ="良好"#line:737
        else :#line:738
            OO0O0O0O00OO0OO00 ="一般"#line:739
        return OO0O0O0O00OO0OO00 #line:740
    def get_daily_list (O0OO0OO0OOO00O000 ,OOOO000O0O000OO00 ):#line:742
        O0O0O0OOO0O00000O =public .M ("system").dbfile ("system").table ("daily").where ("time_key>?",0 ).select ()#line:743
        OO0O00OO00O0O0000 =[]#line:744
        for OOOOO000O000O0000 in O0O0O0OOO0O00000O :#line:745
            OOOOO000O000O0000 ["evaluate"]=O0OO0OO0OOO00O000 .evaluate (OOOOO000O000O0000 ["evaluate"])#line:746
            OO0O00OO00O0O0000 .append (OOOOO000O000O0000 )#line:747
        return OO0O00OO00O0O0000