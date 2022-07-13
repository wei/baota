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
    def check_databases (O00OOO00OO0OO0O00 ):#line:30
        ""#line:31
        OO00OOO000OOOOO0O =["app_usage","server_status","backup_status","daily"]#line:32
        import sqlite3 #line:33
        O0OOO0O0000O0O00O =sqlite3 .connect ("/www/server/panel/data/system.db")#line:34
        OO00O0O0O000OO000 =O0OOO0O0000O0O00O .cursor ()#line:35
        OOOO00OOO0O0OO0O0 =",".join (["'"+O000OO0O000O0O00O +"'"for O000OO0O000O0O00O in OO00OOO000OOOOO0O ])#line:36
        OOO00OO0OO0OOOOO0 =OO00O0O0O000OO000 .execute ("SELECT name FROM sqlite_master WHERE type='table' and name in ({})".format (OOOO00OOO0O0OO0O0 ))#line:37
        O0OOOOOOOO0O0000O =OOO00OO0OO0OOOOO0 .fetchall ()#line:38
        OO0O000O0OO00OOOO =False #line:41
        O000O00O0OOOOO0OO =[]#line:42
        if O0OOOOOOOO0O0000O :#line:43
            O000O00O0OOOOO0OO =[O0OOOOO0O0O0OOO0O [0 ]for O0OOOOO0O0O0OOO0O in O0OOOOOOOO0O0000O ]#line:44
        if "app_usage"not in O000O00O0OOOOO0OO :#line:46
            O00OO0OO00OOOO000 ='''CREATE TABLE IF NOT EXISTS `app_usage` (
                    `time_key` INTEGER PRIMARY KEY,
                    `app` TEXT,
                    `disks` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:52
            OO00O0O0O000OO000 .execute (O00OO0OO00OOOO000 )#line:53
            OO0O000O0OO00OOOO =True #line:54
        if "server_status"not in O000O00O0OOOOO0OO :#line:56
            print ("创建server_status表:")#line:57
            O00OO0OO00OOOO000 ='''CREATE TABLE IF NOT EXISTS `server_status` (
                    `status` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:61
            OO00O0O0O000OO000 .execute (O00OO0OO00OOOO000 )#line:62
            OO0O000O0OO00OOOO =True #line:63
        if "backup_status"not in O000O00O0OOOOO0OO :#line:65
            print ("创建备份状态表:")#line:66
            O00OO0OO00OOOO000 ='''CREATE TABLE IF NOT EXISTS `backup_status` (
                    `id` INTEGER,
                    `target` TEXT,
                    `status` INTEGER,
                    `msg` TEXT DEFAULT "",
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:73
            OO00O0O0O000OO000 .execute (O00OO0OO00OOOO000 )#line:74
            OO0O000O0OO00OOOO =True #line:75
        if "daily"not in O000O00O0OOOOO0OO :#line:77
            O00OO0OO00OOOO000 ='''CREATE TABLE IF NOT EXISTS `daily` (
                    `time_key` INTEGER,
                    `evaluate` INTEGER,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:82
            OO00O0O0O000OO000 .execute (O00OO0OO00OOOO000 )#line:83
            OO0O000O0OO00OOOO =True #line:84
        if OO0O000O0OO00OOOO :#line:86
            O0OOO0O0000O0O00O .commit ()#line:87
        OO00O0O0O000OO000 .close ()#line:88
        O0OOO0O0000O0O00O .close ()#line:89
        return True #line:90
    def get_time_key (OOO0OOO0OOO00000O ,date =None ):#line:92
        if date is None :#line:93
            date =time .localtime ()#line:94
        O00OO00O00O0OOOOO =0 #line:95
        O0000O0O0O00OOOOO ="%Y%m%d"#line:96
        if type (date )==time .struct_time :#line:97
            O00OO00O00O0OOOOO =int (time .strftime (O0000O0O0O00OOOOO ,date ))#line:98
        if type (date )==str :#line:99
            O00OO00O00O0OOOOO =int (time .strptime (date ,O0000O0O0O00OOOOO ))#line:100
        return O00OO00O00O0OOOOO #line:101
    def store_app_usage (OO0OO00O0000OOO00 ,time_key =None ):#line:103
        ""#line:111
        OO0OO00O0000OOO00 .check_databases ()#line:113
        if time_key is None :#line:115
            time_key =OO0OO00O0000OOO00 .get_time_key ()#line:116
        O0000OO0OOO0OO000 =public .M ("system").dbfile ("system").table ("app_usage")#line:118
        O0OOOO00OOOOOOOO0 =O0000OO0OOO0OO000 .field ("time_key").where ("time_key=?",(time_key )).find ()#line:119
        if O0OOOO00OOOOOOOO0 and "time_key"in O0OOOO00OOOOOOOO0 :#line:120
            if O0OOOO00OOOOOOOO0 ["time_key"]==time_key :#line:121
                return True #line:123
        OOOOO00OOO000OOOO =public .M ('sites').field ('path').select ()#line:125
        O00000O000OO000O0 =0 #line:126
        for OO0000OOOO0OOO000 in OOOOO00OOO000OOOO :#line:127
            OOOOOOOOOOOOOO0O0 =OO0000OOOO0OOO000 ["path"]#line:128
            if OOOOOOOOOOOOOO0O0 :#line:129
                O00000O000OO000O0 +=public .get_path_size (OOOOOOOOOOOOOO0O0 )#line:130
        OOO00O0O00O00O00O =public .get_path_size ("/www/server/data")#line:132
        O0O0OO00OO0O0O00O =public .M ("ftps").field ("path").select ()#line:134
        O00O0OO00O0O0OOOO =0 #line:135
        for OO0000OOOO0OOO000 in O0O0OO00OO0O0O00O :#line:136
            O00OO0000OO0000O0 =OO0000OOOO0OOO000 ["path"]#line:137
            if O00OO0000OO0000O0 :#line:138
                O00O0OO00O0O0OOOO +=public .get_path_size (O00OO0000OO0000O0 )#line:139
        O00OO0OOOOO0OO000 =public .get_path_size ("/www/server/panel/plugin")#line:141
        O000OO00OOO000O00 =["/www/server/total","/www/server/btwaf","/www/server/coll","/www/server/nginx","/www/server/apache","/www/server/redis"]#line:149
        for O0OO0OO00O0OOO0OO in O000OO00OOO000O00 :#line:150
            O00OO0OOOOO0OO000 +=public .get_path_size (O0OO0OO00O0OOO0OO )#line:151
        OO0OO000OO0OO0O00 =system ().GetDiskInfo2 (human =False )#line:153
        OO00O00O0OO000OOO =""#line:154
        OOO00OO0000OOOO00 =0 #line:155
        OO00OOOOOO000O000 =0 #line:156
        for OOOO000O0O000O0O0 in OO0OO000OO0OO0O00 :#line:157
            O0OO0OOO0O0O00O0O =OOOO000O0O000O0O0 ["path"].replace ("-","_")#line:158
            if OO00O00O0OO000OOO :#line:159
                OO00O00O0OO000OOO +="-"#line:160
            O0O0O000OO0O0OO0O ,OO0000O0O00000000 ,O000OO0O0OO000000 ,OOO0OOOOO0OOOO00O =OOOO000O0O000O0O0 ["size"]#line:161
            O0OOO000OOOOO0OO0 ,O0OOOOO0000O00OO0 ,_O000O0OO00000O0O0 ,_OO0000000000OO0OO =OOOO000O0O000O0O0 ["inodes"]#line:162
            OO00O00O0OO000OOO ="{},{},{},{},{}".format (O0OO0OOO0O0O00O0O ,OO0000O0O00000000 ,O0O0O000OO0O0OO0O ,O0OOOOO0000O00OO0 ,O0OOO000OOOOO0OO0 )#line:163
            if O0OO0OOO0O0O00O0O =="/":#line:164
                OOO00OO0000OOOO00 =O0O0O000OO0O0OO0O #line:165
                OO00OOOOOO000O000 =OO0000O0O00000000 #line:166
        OO00000OO0OOOO0O0 ="{},{},{},{},{},{}".format (OOO00OO0000OOOO00 ,OO00OOOOOO000O000 ,O00000O000OO000O0 ,OOO00O0O00O00O00O ,O00O0OO00O0O0OOOO ,O00OO0OOOOO0OO000 )#line:171
        O0OOOO00O0O00OO00 =public .M ("system").dbfile ("system").table ("app_usage").add ("time_key,app,disks",(time_key ,OO00000OO0OOOO0O0 ,OO00O00O0OO000OOO ))#line:173
        if O0OOOO00O0O00OO00 ==time_key :#line:174
            return True #line:175
        return False #line:178
    def parse_char_unit (O0000O00000000O0O ,O0OO00OOO0O00OOO0 ):#line:180
        OOO00O0O0O0O0O0O0 =0 #line:181
        try :#line:182
            OOO00O0O0O0O0O0O0 =float (O0OO00OOO0O00OOO0 )#line:183
        except :#line:184
            OOO0O0000000OO0OO =O0OO00OOO0O00OOO0 #line:185
            if OOO0O0000000OO0OO .find ("G")!=-1 :#line:186
                OOO0O0000000OO0OO =OOO0O0000000OO0OO .replace ("G","")#line:187
                OOO00O0O0O0O0O0O0 =float (OOO0O0000000OO0OO )*1024 *1024 *1024 #line:188
            elif OOO0O0000000OO0OO .find ("M")!=-1 :#line:189
                OOO0O0000000OO0OO =OOO0O0000000OO0OO .replace ("M","")#line:190
                OOO00O0O0O0O0O0O0 =float (OOO0O0000000OO0OO )*1024 *1024 #line:191
            else :#line:192
                OOO00O0O0O0O0O0O0 =float (OOO0O0000000OO0OO )#line:193
        return OOO00O0O0O0O0O0O0 #line:194
    def parse_app_usage_info (OO00OOO0O000OO0OO ,OOOOOO000O0O0OOO0 ):#line:196
        ""#line:197
        if not OOOOOO000O0O0OOO0 :#line:198
            return {}#line:199
        print (OOOOOO000O0O0OOO0 )#line:200
        OOO0OO00OOOO00000 ,OO00000OO0O000000 ,OO0000OO000OO0O00 ,O0O0OO0OO0OOO00OO ,OOO00O0O0O0000OOO ,OOOO00O0OOO0O00O0 =OOOOOO000O0O0OOO0 ["app"].split (",")#line:201
        O0O00O0O0OO000O0O =OOOOOO000O0O0OOO0 ["disks"].split ("-")#line:202
        O0OO0O0OOOO0O0OO0 ={}#line:203
        print ("disk tmp:")#line:204
        print (O0O00O0O0OO000O0O )#line:205
        for O0OOOO000OO0OOO0O in O0O00O0O0OO000O0O :#line:206
            print (O0OOOO000OO0OOO0O )#line:207
            O0O0OOOO0000OO000 ,OOOO00O0O0O0O00OO ,OOO000O0O0OOO0OO0 ,OOO00O0OOO00O0000 ,OOO00O00000O0OOOO =O0OOOO000OO0OOO0O .split (",")#line:208
            O0O00OO00OOOO00O0 ={}#line:209
            O0O00OO00OOOO00O0 ["usage"]=OO00OOO0O000OO0OO .parse_char_unit (OOOO00O0O0O0O00OO )#line:210
            O0O00OO00OOOO00O0 ["total"]=OO00OOO0O000OO0OO .parse_char_unit (OOO000O0O0OOO0OO0 )#line:211
            O0O00OO00OOOO00O0 ["iusage"]=OOO00O0OOO00O0000 #line:212
            O0O00OO00OOOO00O0 ["itotal"]=OOO00O00000O0OOOO #line:213
            O0OO0O0OOOO0O0OO0 [O0O0OOOO0000OO000 ]=O0O00OO00OOOO00O0 #line:214
        return {"apps":{"disk_total":OOO0OO00OOOO00000 ,"disk_usage":OO00000OO0O000000 ,"sites":OO0000OO000OO0O00 ,"databases":O0O0OO0OO0OOO00OO ,"ftps":OOO00O0O0O0000OOO ,"plugins":OOOO00O0OOO0O00O0 },"disks":O0OO0O0OOOO0O0OO0 }#line:225
    def get_app_usage (OO000OO0OO0OO00OO ,O0000O000OOO00O0O ):#line:227
        O00OO00000O0O00OO =time .localtime ()#line:229
        O000OO00OO000000O =OO000OO0OO0OO00OO .get_time_key ()#line:230
        O000OO00OOOO00OOO =time .localtime (time .mktime ((O00OO00000O0O00OO .tm_year ,O00OO00000O0O00OO .tm_mon ,O00OO00000O0O00OO .tm_mday -1 ,0 ,0 ,0 ,0 ,0 ,0 )))#line:233
        O0OOO0OO000000000 =OO000OO0OO0OO00OO .get_time_key (O000OO00OOOO00OOO )#line:234
        O00OO0O00OOO00O00 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key =? or time_key=?",(O000OO00OO000000O ,O0OOO0OO000000000 ))#line:236
        O00O000O0000000OO =O00OO0O00OOO00O00 .select ()#line:237
        if type (O00O000O0000000OO )==str or not O00O000O0000000OO :#line:240
            return {}#line:241
        OO0000O00OO0O00OO ={}#line:242
        OOO0OOOO0000OO0O0 ={}#line:243
        for O000OOO0OOOO0O00O in O00O000O0000000OO :#line:244
            if O000OOO0OOOO0O00O ["time_key"]==O000OO00OO000000O :#line:245
                OO0000O00OO0O00OO =OO000OO0OO0OO00OO .parse_app_usage_info (O000OOO0OOOO0O00O )#line:246
            if O000OOO0OOOO0O00O ["time_key"]==O0OOO0OO000000000 :#line:247
                OOO0OOOO0000OO0O0 =OO000OO0OO0OO00OO .parse_app_usage_info (O000OOO0OOOO0O00O )#line:248
        if not OO0000O00OO0O00OO :#line:250
            return {}#line:251
        for OO0OO0O0OOOOOOOO0 ,O000OO000O000O0O0 in OO0000O00OO0O00OO ["disks"].items ():#line:254
            O00O00O0OO0000000 =int (O000OO000O000O0O0 ["total"])#line:255
            O00000OOO0OO0OOO0 =int (O000OO000O000O0O0 ["usage"])#line:256
            O0OO00OOOOO0OOOO0 =int (O000OO000O000O0O0 ["itotal"])#line:258
            O0OOO00O00O000O00 =int (O000OO000O000O0O0 ["iusage"])#line:259
            if OOO0OOOO0000OO0O0 and OO0OO0O0OOOOOOOO0 in OOO0OOOO0000OO0O0 ["disks"].keys ():#line:261
                O000OOOO0O0OO0O0O =OOO0OOOO0000OO0O0 ["disks"]#line:262
                O0O00O00000O00O00 =O000OOOO0O0OO0O0O [OO0OO0O0OOOOOOOO0 ]#line:263
                O000OOOO0O000OOOO =int (O0O00O00000O00O00 ["total"])#line:264
                if O000OOOO0O000OOOO ==O00O00O0OO0000000 :#line:265
                    O00O00000O00OO000 =int (O0O00O00000O00O00 ["usage"])#line:266
                    O0OOOO0OOO00000O0 =0 #line:267
                    O00O0OO00OO000O0O =O00000OOO0OO0OOO0 -O00O00000O00OO000 #line:268
                    if O00O0OO00OO000O0O >0 :#line:269
                        O0OOOO0OOO00000O0 =round (O00O0OO00OO000O0O /O00O00O0OO0000000 ,2 )#line:270
                    O000OO000O000O0O0 ["incr"]=O0OOOO0OOO00000O0 #line:271
                OO00OO00O0OOO0000 =int (O0O00O00000O00O00 ["itotal"])#line:274
                if True :#line:275
                    OO000000OOO0O0OO0 =int (O0O00O00000O00O00 ["iusage"])#line:276
                    OO0O0O000OOO0OOO0 =0 #line:277
                    O00O0OO00OO000O0O =O0OOO00O00O000O00 -OO000000OOO0O0OO0 #line:278
                    if O00O0OO00OO000O0O >0 :#line:279
                        OO0O0O000OOO0OOO0 =round (O00O0OO00OO000O0O /O0OO00OOOOO0OOOO0 ,2 )#line:280
                    O000OO000O000O0O0 ["iincr"]=OO0O0O000OOO0OOO0 #line:281
        O000OOO00O0000000 =OO0000O00OO0O00OO ["apps"]#line:285
        O0OOO0O0OO0O000O0 =int (O000OOO00O0000000 ["disk_total"])#line:286
        if OOO0OOOO0000OO0O0 and OOO0OOOO0000OO0O0 ["apps"]["disk_total"]==O000OOO00O0000000 ["disk_total"]:#line:287
            O0000OO0O00OO000O =OOO0OOOO0000OO0O0 ["apps"]#line:288
            for OO000O0O0O000O0O0 ,O000O0O00O000000O in O000OOO00O0000000 .items ():#line:289
                if OO000O0O0O000O0O0 =="disks":continue #line:290
                if OO000O0O0O000O0O0 =="disk_total":continue #line:291
                if OO000O0O0O000O0O0 =="disk_usage":continue #line:292
                O000OOOO0OO0O0000 =0 #line:293
                OO000OOO00OO0O0O0 =int (O000O0O00O000000O )-int (O0000OO0O00OO000O [OO000O0O0O000O0O0 ])#line:294
                if OO000OOO00OO0O0O0 >0 :#line:295
                    O000OOOO0OO0O0000 =round (OO000OOO00OO0O0O0 /O0OOO0O0OO0O000O0 ,2 )#line:296
                O000OOO00O0000000 [OO000O0O0O000O0O0 ]={"val":O000O0O00O000000O ,"incr":O000OOOO0OO0O0000 }#line:301
        return OO0000O00OO0O00OO #line:302
    def get_timestamp_interval (O0000OOO00OO0000O ,O0O0O00OO0O0O0000 ):#line:304
        OO0OOOOOOO0O0O0O0 =None #line:305
        OO00OO000O0O0O0OO =None #line:306
        OO0OOOOOOO0O0O0O0 =time .mktime ((O0O0O00OO0O0O0000 .tm_year ,O0O0O00OO0O0O0000 .tm_mon ,O0O0O00OO0O0O0000 .tm_mday ,0 ,0 ,0 ,0 ,0 ,0 ))#line:308
        OO00OO000O0O0O0OO =time .mktime ((O0O0O00OO0O0O0000 .tm_year ,O0O0O00OO0O0O0000 .tm_mon ,O0O0O00OO0O0O0000 .tm_mday ,23 ,59 ,59 ,0 ,0 ,0 ))#line:310
        return OO0OOOOOOO0O0O0O0 ,OO00OO000O0O0O0OO #line:311
    def check_server (O00O0O000000OOO0O ):#line:314
        try :#line:315
            OO000O000000O00O0 =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:318
            OOO00OO0O0O0OO0OO =panelPlugin ()#line:319
            OOOO0OO0O0000O00O =public .dict_obj ()#line:320
            O0000O0OO0OOO0OOO =""#line:321
            for O0OO00O0O000O00O0 in OO000O000000O00O0 :#line:322
                O0O00O0OOO00OOOOO =False #line:323
                O00OO00O000O000O0 =False #line:324
                OOOO0OO0O0000O00O .name =O0OO00O0O000O00O0 #line:325
                O0OOO0OOO0O0O00OO =OOO00OO0O0O0OO0OO .getPluginInfo (OOOO0OO0O0000O00O )#line:326
                if not O0OOO0OOO0O0O00OO :#line:327
                    continue #line:328
                O0O00OOO0OO0O0O0O =O0OOO0OOO0O0O00OO ["versions"]#line:329
                for OO0O00O00O0O00O0O in O0O00OOO0OO0O0O0O :#line:331
                    if OO0O00O00O0O00O0O ["status"]:#line:334
                        O00OO00O000O000O0 =True #line:335
                    if "run"in OO0O00O00O0O00O0O .keys ()and OO0O00O00O0O00O0O ["run"]:#line:336
                        O00OO00O000O000O0 =True #line:338
                        O0O00O0OOO00OOOOO =True #line:339
                        break #line:340
                O0OOOO00O0O0O0O0O =0 #line:341
                if O00OO00O000O000O0 :#line:342
                    O0OOOO00O0O0O0O0O =1 #line:343
                    if not O0O00O0OOO00OOOOO :#line:345
                        O0OOOO00O0O0O0O0O =2 #line:346
                O0000O0OO0OOO0OOO +=str (O0OOOO00O0O0O0O0O )#line:347
            if '2'in O0000O0OO0OOO0OOO :#line:351
                public .M ("system").dbfile ("server_status").add ("status, addtime",(O0000O0OO0OOO0OOO ,time .time ()))#line:353
        except Exception as O0O00O00000000OO0 :#line:354
            return True #line:356
    def get_daily_data (OO0O0OOO0O0O0OO00 ,O0OO000O0000O0OOO ):#line:358
        ""#line:359
        OOO0O0OOO0O00O000 ="IS_PRO_OR_LTD_FOR_PANEL_DAILY"#line:361
        OO0OOOO00O0OO00OO =cache .get (OOO0O0OOO0O00O000 )#line:362
        if not OO0OOOO00O0OO00OO :#line:363
            try :#line:364
                OOO0O00OOO00000O0 =panelPlugin ()#line:365
                OO00OO000O0O0OO0O =OOO0O00OOO00000O0 .get_soft_list (O0OO000O0000O0OOO )#line:366
                if OO00OO000O0O0OO0O ["pro"]<0 and OO00OO000O0O0OO0O ["ltd"]<0 :#line:367
                    if os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:368
                        os .remove ("/www/server/panel/data/start_daily.pl")#line:369
                    return {"status":False ,"msg":"No authorization.","data":[],"date":O0OO000O0000O0OOO .date }#line:375
                cache .set (OOO0O0OOO0O00O000 ,True ,86400 )#line:376
            except :#line:377
                return {"status":False ,"msg":"获取不到授权信息，请检查网络是否正常","data":[],"date":O0OO000O0000O0OOO .date }#line:383
        if not os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:386
            public .writeFile ("/www/server/panel/data/start_daily.pl",O0OO000O0000O0OOO .date )#line:387
        return OO0O0OOO0O0O0OO00 .get_daily_data_local (O0OO000O0000O0OOO .date )#line:388
    def get_daily_data_local (OOO0O0OOOO00O000O ,OO0O0OO0O00OOOO0O ):#line:390
        OOOO0O0OOOOOOO000 =time .strptime (OO0O0OO0O00OOOO0O ,"%Y%m%d")#line:391
        OO0OOO0O0OO0000O0 =OOO0O0OOOO00O000O .get_time_key (OOOO0O0OOOOOOO000 )#line:392
        OOO0O0OOOO00O000O .check_databases ()#line:394
        O0OO00O0O0O00O0OO =time .strftime ("%Y-%m-%d",OOOO0O0OOOOOOO000 )#line:396
        O0OO0O00OO0OOOO00 =0 #line:397
        O0O0OOO0O000OOOO0 ,OO0OO0OO00O000O0O =OOO0O0OOOO00O000O .get_timestamp_interval (OOOO0O0OOOOOOO000 )#line:398
        OO0OO0OO0OOOOOO0O =public .M ("system").dbfile ("system")#line:399
        OO00OO0OOO0O0OOOO =OO0OO0OO0OOOOOO0O .table ("process_high_percent")#line:400
        O0OO000O0O0OO00OO =OO00OO0OOO0O0OOOO .where ("addtime>=? and addtime<=?",(O0O0OOO0O000OOOO0 ,OO0OO0OO00O000O0O )).order ("addtime").select ()#line:401
        OO00OO0OO00O0OOO0 =[]#line:405
        if len (O0OO000O0O0OO00OO )>0 :#line:406
            for O0O0OOO00O00OOO0O in O0OO000O0O0OO00OO :#line:408
                O0000OOOOO000O00O =int (O0O0OOO00O00OOO0O ["cpu_percent"])#line:410
                if O0000OOOOO000O00O >=80 :#line:411
                    OO00OO0OO00O0OOO0 .append ({"time":O0O0OOO00O00OOO0O ["addtime"],"name":O0O0OOO00O00OOO0O ["name"],"pid":O0O0OOO00O00OOO0O ["pid"],"percent":O0000OOOOO000O00O })#line:419
        OO000OO00O00OO000 =len (OO00OO0OO00O0OOO0 )#line:421
        OOO00O00OOOOOO0OO =0 #line:422
        OOOO00O000OOO00O0 =""#line:423
        if OO000OO00O00OO000 ==0 :#line:424
            OOO00O00OOOOOO0OO =20 #line:425
        else :#line:426
            OOOO00O000OOO00O0 ="CPU出现过载情况"#line:427
        OO00O00OO000O0OO0 ={"ex":OO000OO00O00OO000 ,"detail":OO00OO0OO00O0OOO0 }#line:431
        OOOO0OO000O00O0OO =[]#line:434
        if len (O0OO000O0O0OO00OO )>0 :#line:435
            for O0O0OOO00O00OOO0O in O0OO000O0O0OO00OO :#line:437
                O00000O0O0OO00OOO =float (O0O0OOO00O00OOO0O ["memory"])#line:439
                O00O0OO0OO0O00O0O =psutil .virtual_memory ().total #line:440
                O00OO000OO00OOO00 =round (100 *O00000O0O0OO00OOO /O00O0OO0OO0O00O0O ,2 )#line:441
                if O00OO000OO00OOO00 >=80 :#line:442
                    OOOO0OO000O00O0OO .append ({"time":O0O0OOO00O00OOO0O ["addtime"],"name":O0O0OOO00O00OOO0O ["name"],"pid":O0O0OOO00O00OOO0O ["pid"],"percent":O00OO000OO00OOO00 })#line:450
        OO0O000O0O00OO00O =len (OOOO0OO000O00O0OO )#line:451
        OO0O0OOO00O00000O =""#line:452
        O0OOO0O00OO0OOOO0 =0 #line:453
        if OO0O000O0O00OO00O ==0 :#line:454
            O0OOO0O00OO0OOOO0 =20 #line:455
        else :#line:456
            if OO0O000O0O00OO00O >1 :#line:457
                OO0O0OOO00O00000O ="内存在多个时间点出现占用80%"#line:458
            else :#line:459
                OO0O0OOO00O00000O ="内存出现占用超过80%"#line:460
        O00O000OOOO00OO0O ={"ex":OO0O000O0O00OO00O ,"detail":OOOO0OO000O00O0OO }#line:464
        O0000O000OOO00OO0 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key=?",(OO0OOO0O0OO0000O0 ,))#line:468
        O0000O00OO0O000OO =O0000O000OOO00OO0 .select ()#line:469
        O000OOO00000OO0OO ={}#line:470
        if O0000O00OO0O000OO and type (O0000O00OO0O000OO )!=str :#line:471
            O000OOO00000OO0OO =OOO0O0OOOO00O000O .parse_app_usage_info (O0000O00OO0O000OO [0 ])#line:472
        OOO0OOO000OO000O0 =[]#line:473
        if O000OOO00000OO0OO :#line:474
            O000O00000O0OO0O0 =O000OOO00000OO0OO ["disks"]#line:475
            for OOO0OO00OOO00OOO0 ,OO0OO000O0O000OOO in O000O00000O0OO0O0 .items ():#line:476
                O00O0OOOO0OO00O00 =int (OO0OO000O0O000OOO ["usage"])#line:477
                O00O0OO0OO0O00O0O =int (OO0OO000O0O000OOO ["total"])#line:478
                OO0OOOOOO0O0O0000 =round (O00O0OOOO0OO00O00 /O00O0OO0OO0O00O0O ,2 )#line:479
                OO0OOOOOO00O0OO0O =int (OO0OO000O0O000OOO ["iusage"])#line:480
                OOOOOO0OO0O000OOO =int (OO0OO000O0O000OOO ["itotal"])#line:481
                if OOOOOO0OO0O000OOO >0 :#line:482
                    OO00000OO000O0OOO =round (OO0OOOOOO00O0OO0O /OOOOOO0OO0O000OOO ,2 )#line:483
                else :#line:484
                    OO00000OO000O0OOO =0 #line:485
                if OO0OOOOOO0O0O0000 >=0.8 :#line:489
                    OOO0OOO000OO000O0 .append ({"name":OOO0OO00OOO00OOO0 ,"percent":OO0OOOOOO0O0O0000 *100 ,"ipercent":OO00000OO000O0OOO *100 ,"usage":O00O0OOOO0OO00O00 ,"total":O00O0OO0OO0O00O0O ,"iusage":OO0OOOOOO00O0OO0O ,"itotal":OOOOOO0OO0O000OOO })#line:498
        OO0O000OOO0OO0OO0 =len (OOO0OOO000OO000O0 )#line:500
        OOO0OO0O0OOO00000 =""#line:501
        OO000OO00O0O000O0 =0 #line:502
        if OO0O000OOO0OO0OO0 ==0 :#line:503
            OO000OO00O0O000O0 =20 #line:504
        else :#line:505
            OOO0OO0O0OOO00000 ="有磁盘空间占用已经超过80%"#line:506
        OO0OOOOO00O0O000O ={"ex":OO0O000OOO0OO0OO0 ,"detail":OOO0OOO000OO000O0 }#line:511
        OOO00OO0O00O0O00O =public .M ("system").dbfile ("system").table ("server_status").where ("addtime>=? and addtime<=?",(O0O0OOO0O000OOOO0 ,OO0OO0OO00O000O0O ,)).order ("addtime desc").select ()#line:515
        OOO0O0OOOOOOO0OOO =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:520
        O00OO000O0O0OO000 ={}#line:522
        OOOOOOOOO0000O000 =0 #line:523
        OOOOOO00OOOOO0O00 =""#line:524
        for O0O0O000OOO0O0000 ,O00000OO00OOO00OO in enumerate (OOO0O0OOOOOOO0OOO ):#line:525
            if O00000OO00OOO00OO =="pure-ftpd":#line:526
                O00000OO00OOO00OO ="ftpd"#line:527
            O0O00OO000OOO0O00 =0 #line:528
            OO0OOO00O0OO00OO0 =[]#line:529
            for O0OOO000OO0O0000O in OOO00OO0O00O0O00O :#line:530
                _O000OO00OO0O0O0OO =O0OOO000OO0O0000O ["status"]#line:533
                if O0O0O000OOO0O0000 <len (_O000OO00OO0O0O0OO ):#line:534
                    if _O000OO00OO0O0O0OO [O0O0O000OOO0O0000 ]=="2":#line:535
                        OO0OOO00O0OO00OO0 .append ({"time":O0OOO000OO0O0000O ["addtime"],"desc":"退出"})#line:536
                        O0O00OO000OOO0O00 +=1 #line:537
                        OOOOOOOOO0000O000 +=1 #line:538
            O00OO000O0O0OO000 [O00000OO00OOO00OO ]={"ex":O0O00OO000OOO0O00 ,"detail":OO0OOO00O0OO00OO0 }#line:543
        O00OOO0000O0O00OO =0 #line:545
        if OOOOOOOOO0000O000 ==0 :#line:546
            O00OOO0000O0O00OO =20 #line:547
        else :#line:548
            OOOOOO00OOOOO0O00 ="系统级服务有出现异常退出情况"#line:549
        O0OOOO0OO000O0O0O =public .M ("crontab").field ("sName,sType").where ("sType in (?, ?, ?)",("database","enterpriseBackup","site",)).select ()#line:553
        OOOOO00O000000OO0 =set (O0O000O000O00000O ["sName"]for O0O000O000O00000O in O0OOOO0OO000O0O0O if O0O000O000O00000O ["sType"]=="database"or O0O000O000O00000O ["sType"]=="enterpriseBackup")#line:556
        OOOOOOOOOO00OO00O ="ALL"in OOOOO00O000000OO0 #line:557
        OO0OO0O0OOOO00OOO =set (OO0OO00OO0OOOO00O ["sName"]for OO0OO00OO0OOOO00O in O0OOOO0OO000O0O0O if OO0OO00OO0OOOO00O ["sType"]=="site")#line:558
        OOOO0OO00O00000OO ="ALL"in OO0OO0O0OOOO00OOO #line:559
        OO0O0OOO0000O0000 =[]#line:560
        O0000O0O000OO0O00 =[]#line:561
        if not OOOOOOOOOO00OO00O :#line:562
            O000000OOOO0OO0O0 =public .M ("databases").field ("name").select ()#line:563
            for O0OOO00OO0000OO0O in O000000OOOO0OO0O0 :#line:564
                OO0O000OOOO0OOO00 =O0OOO00OO0000OO0O ["name"]#line:565
                if OO0O000OOOO0OOO00 not in OOOOO00O000000OO0 :#line:566
                    OO0O0OOO0000O0000 .append ({"name":OO0O000OOOO0OOO00 })#line:567
        if not OOOO0OO00O00000OO :#line:569
            OO0O0O00O0O00O000 =public .M ("sites").field ("name").select ()#line:570
            for O0OOOO0O000OO0000 in OO0O0O00O0O00O000 :#line:571
                OO00O0O00OOOO0OOO =O0OOOO0O000OO0000 ["name"]#line:572
                if OO00O0O00OOOO0OOO not in OO0OO0O0OOOO00OOO :#line:573
                    O0000O0O000OO0O00 .append ({"name":OO00O0O00OOOO0OOO })#line:574
        OO0O000OOO00O0OO0 =public .M ("system").dbfile ("system").table ("backup_status").where ("addtime>=? and addtime<=?",(O0O0OOO0O000OOOO0 ,OO0OO0OO00O000O0O )).select ()#line:577
        OO0OOOO00000O0OO0 ={"database":{"no_backup":OO0O0OOO0000O0000 ,"backup":[]},"site":{"no_backup":O0000O0O000OO0O00 ,"backup":[]},"path":{"no_backup":[],"backup":[]}}#line:592
        O0O0O0O0OO00OOOO0 =0 #line:593
        for OO00OO0OO0O0O0000 in OO0O000OOO00O0OO0 :#line:594
            OO0OO0OOOO00OOO0O =OO00OO0OO0O0O0000 ["status"]#line:595
            if OO0OO0OOOO00OOO0O :#line:596
                continue #line:597
            O0O0O0O0OO00OOOO0 +=1 #line:599
            OO0OO0O00O0O000O0 =OO00OO0OO0O0O0000 ["id"]#line:600
            OO0OO00OOO00000O0 =public .M ("crontab").where ("id=?",(OO0OO0O00O0O000O0 )).find ()#line:601
            if not OO0OO00OOO00000O0 :#line:602
                continue #line:603
            OO0OO00OO00O00O00 =OO0OO00OOO00000O0 ["sType"]#line:604
            if not OO0OO00OO00O00O00 :#line:605
                continue #line:606
            OOOOO00O0O0OO0OOO =OO0OO00OOO00000O0 ["name"]#line:607
            OO0OO0O0OOOOO000O =OO00OO0OO0O0O0000 ["addtime"]#line:608
            OO0000OO00O0O000O =OO00OO0OO0O0O0000 ["target"]#line:609
            if OO0OO00OO00O00O00 not in OO0OOOO00000O0OO0 .keys ():#line:610
                OO0OOOO00000O0OO0 [OO0OO00OO00O00O00 ]={}#line:611
                OO0OOOO00000O0OO0 [OO0OO00OO00O00O00 ]["backup"]=[]#line:612
                OO0OOOO00000O0OO0 [OO0OO00OO00O00O00 ]["no_backup"]=[]#line:613
            OO0OOOO00000O0OO0 [OO0OO00OO00O00O00 ]["backup"].append ({"name":OOOOO00O0O0OO0OOO ,"target":OO0000OO00O0O000O ,"status":OO0OO0OOOO00OOO0O ,"target":OO0000OO00O0O000O ,"time":OO0OO0O0OOOOO000O })#line:620
        OOO0O0OOO00O0O0OO =""#line:622
        OOOOOO0000OOO000O =0 #line:623
        if O0O0O0O0OO00OOOO0 ==0 :#line:624
            OOOOOO0000OOO000O =20 #line:625
        else :#line:626
            OOO0O0OOO00O0O0OO ="有计划任务备份失败"#line:627
        if len (OO0O0OOO0000O0000 )==0 :#line:629
            OOOOOO0000OOO000O +=10 #line:630
        else :#line:631
            if OOO0O0OOO00O0O0OO :#line:632
                OOO0O0OOO00O0O0OO +=";"#line:633
            OOO0O0OOO00O0O0OO +="有数据库未及时备份"#line:634
        if len (O0000O0O000OO0O00 )==0 :#line:636
            OOOOOO0000OOO000O +=10 #line:637
        else :#line:638
            if OOO0O0OOO00O0O0OO :#line:639
                OOO0O0OOO00O0O0OO +=";"#line:640
            OOO0O0OOO00O0O0OO +="有网站未备份"#line:641
        OOO0O00O00OOO00OO =0 #line:644
        O00O0OOOO00000OOO =public .M ('logs').where ('addtime like ? and type=?',(str (O0OO00O0O0O00O0OO )+"%",'用户登录',)).select ()#line:645
        OO0OOO00OOOOOO0OO =[]#line:646
        if O00O0OOOO00000OOO and type (O00O0OOOO00000OOO )==list :#line:647
            for O0OOO0OO000OOOO00 in O00O0OOOO00000OOO :#line:648
                OOOOOO0O0OO00OO00 =O0OOO0OO000OOOO00 ["log"]#line:649
                if OOOOOO0O0OO00OO00 .find ("失败")>=0 or OOOOOO0O0OO00OO00 .find ("错误")>=0 :#line:650
                    OOO0O00O00OOO00OO +=1 #line:651
                    OO0OOO00OOOOOO0OO .append ({"time":time .mktime (time .strptime (O0OOO0OO000OOOO00 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O0OOO0OO000OOOO00 ["log"],"username":O0OOO0OO000OOOO00 ["username"],})#line:656
            OO0OOO00OOOOOO0OO .sort (key =lambda OOO0O0000OOOO00OO :OOO0O0000OOOO00OO ["time"])#line:657
        OO00O0000O0OO0O00 =public .M ('logs').where ('type=?',('SSH安全',)).where ("addtime like ?",(str (O0OO00O0O0O00O0OO )+"%",)).select ()#line:659
        O0OO0O000O0O00OOO =[]#line:661
        OO00OO000OO00O000 =0 #line:662
        if OO00O0000O0OO0O00 :#line:663
            for O0OOO0OO000OOOO00 in OO00O0000O0OO0O00 :#line:664
                OOOOOO0O0OO00OO00 =O0OOO0OO000OOOO00 ["log"]#line:665
                if OOOOOO0O0OO00OO00 .find ("存在异常")>=0 :#line:666
                    OO00OO000OO00O000 +=1 #line:667
                    O0OO0O000O0O00OOO .append ({"time":time .mktime (time .strptime (O0OOO0OO000OOOO00 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O0OOO0OO000OOOO00 ["log"],"username":O0OOO0OO000OOOO00 ["username"]})#line:672
            O0OO0O000O0O00OOO .sort (key =lambda OO000O00O000OOOO0 :OO000O00O000OOOO0 ["time"])#line:673
        O000OO00OO00OOOO0 =""#line:675
        O0O00OOO0OO0O000O =0 #line:676
        if OO00OO000OO00O000 ==0 :#line:677
            O0O00OOO0OO0O000O =10 #line:678
        else :#line:679
            O000OO00OO00OOOO0 ="SSH有异常登录"#line:680
        if OOO0O00O00OOO00OO ==0 :#line:682
            O0O00OOO0OO0O000O +=10 #line:683
        else :#line:684
            if OOO0O00O00OOO00OO >10 :#line:685
                O0O00OOO0OO0O000O -=10 #line:686
            if O000OO00OO00OOOO0 :#line:687
                O000OO00OO00OOOO0 +=";"#line:688
            O000OO00OO00OOOO0 +="面板登录有错误".format (OOO0O00O00OOO00OO )#line:689
        OOO00OO0O00O0O00O ={"panel":{"ex":OOO0O00O00OOO00OO ,"detail":OO0OOO00OOOOOO0OO },"ssh":{"ex":OO00OO000OO00O000 ,"detail":O0OO0O000O0O00OOO }}#line:699
        O0OO0O00OO0OOOO00 =OOO00O00OOOOOO0OO +O0OOO0O00OO0OOOO0 +OO000OO00O0O000O0 +O00OOO0000O0O00OO +OOOOOO0000OOO000O +O0O00OOO0OO0O000O #line:701
        O0O0O0000OOO0OOO0 =[OOOO00O000OOO00O0 ,OO0O0OOO00O00000O ,OOO0OO0O0OOO00000 ,OOOOOO00OOOOO0O00 ,OOO0O0OOO00O0O0OO ,O000OO00OO00OOOO0 ]#line:702
        O000O00OO0OOOO0O0 =[]#line:703
        for OO0000OO00OO00000 in O0O0O0000OOO0OOO0 :#line:704
            if OO0000OO00OO00000 :#line:705
                if OO0000OO00OO00000 .find (";")>=0 :#line:706
                    for OOOOO0OO0O0OOOO0O in OO0000OO00OO00000 .split (";"):#line:707
                        O000O00OO0OOOO0O0 .append (OOOOO0OO0O0OOOO0O )#line:708
                else :#line:709
                    O000O00OO0OOOO0O0 .append (OO0000OO00OO00000 )#line:710
        if not O000O00OO0OOOO0O0 :#line:712
            O000O00OO0OOOO0O0 .append ("服务器运行正常，请继续保持！")#line:713
        O0O000O0O000000O0 =OOO0O0OOOO00O000O .evaluate (O0OO0O00OO0OOOO00 )#line:717
        return {"data":{"cpu":OO00O00OO000O0OO0 ,"ram":O00O000OOOO00OO0O ,"disk":OO0OOOOO00O0O000O ,"server":O00OO000O0O0OO000 ,"backup":OO0OOOO00000O0OO0 ,"exception":OOO00OO0O00O0O00O ,},"evaluate":O0O000O0O000000O0 ,"score":O0OO0O00OO0OOOO00 ,"date":OO0OOO0O0OO0000O0 ,"summary":O000O00OO0OOOO0O0 ,"status":True }#line:734
    def evaluate (OO0O0OOOOO00O00O0 ,OOO00OOOO0OOOOOOO ):#line:736
        O0O0O00O00OO0OOO0 =""#line:737
        if OOO00OOOO0OOOOOOO >=100 :#line:738
            O0O0O00O00OO0OOO0 ="正常"#line:739
        elif OOO00OOOO0OOOOOOO >=80 :#line:740
            O0O0O00O00OO0OOO0 ="良好"#line:741
        else :#line:742
            O0O0O00O00OO0OOO0 ="一般"#line:743
        return O0O0O00O00OO0OOO0 #line:744
    def get_daily_list (OOO00O00O0O00OOOO ,O000O00O0OO00OO0O ):#line:746
        OOO00OOOOO00000O0 =public .M ("system").dbfile ("system").table ("daily").where ("time_key>?",0 ).select ()#line:747
        OOO000000OO0000O0 =[]#line:748
        for OO0OO00OO00OOO00O in OOO00OOOOO00000O0 :#line:749
            OO0OO00OO00OOO00O ["evaluate"]=OOO00O00O0O00OOOO .evaluate (OO0OO00OO00OOO00O ["evaluate"])#line:750
            OOO000000OO0000O0 .append (OO0OO00OO00OOO00O )#line:751
        return OOO000000OO0000O0 