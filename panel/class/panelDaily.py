import os #line:15
import sys #line:16
import time #line:17
import psutil #line:18
import json #line:19
os .chdir ("/www/server/panel")#line:21
sys .path .insert (0 ,"/www/server/panel")#line:22
sys .path .insert (0 ,"class/")#line:23
import public #line:25
from system import system #line:26
from panelPlugin import panelPlugin #line:27
from BTPanel import auth ,cache #line:28
class panelDaily :#line:30
    def check_databases (OO0O0OOO000OO00O0 ):#line:32
        ""#line:33
        O0O0OOO0OO000O0OO =["app_usage","server_status","backup_status","daily"]#line:34
        import sqlite3 #line:35
        O00O000OOO0OOO0O0 =sqlite3 .connect ("/www/server/panel/data/system.db")#line:36
        O0OOO00O00O0OOOOO =O00O000OOO0OOO0O0 .cursor ()#line:37
        OO00O0OOOOOOO0OO0 =",".join (["'"+OO0000O000O00O0O0 +"'"for OO0000O000O00O0O0 in O0O0OOO0OO000O0OO ])#line:38
        OO000O0O0O00O0O00 =O0OOO00O00O0OOOOO .execute ("SELECT name FROM sqlite_master WHERE type='table' and name in ({})".format (OO00O0OOOOOOO0OO0 ))#line:39
        O0O00000OOO00O00O =OO000O0O0O00O0O00 .fetchall ()#line:40
        OO00OOO000O0O0O0O =False #line:43
        OOO0OO00O00000O00 =[]#line:44
        if O0O00000OOO00O00O :#line:45
            OOO0OO00O00000O00 =[OOOOO0OOOO00OOO00 [0 ]for OOOOO0OOOO00OOO00 in O0O00000OOO00O00O ]#line:46
        if "app_usage"not in OOO0OO00O00000O00 :#line:48
            OO0OOOOO0000OO0OO ='''CREATE TABLE IF NOT EXISTS `app_usage` (
                    `time_key` INTEGER PRIMARY KEY,
                    `app` TEXT,
                    `disks` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:54
            O0OOO00O00O0OOOOO .execute (OO0OOOOO0000OO0OO )#line:55
            OO00OOO000O0O0O0O =True #line:56
        if "server_status"not in OOO0OO00O00000O00 :#line:58
            print ("创建server_status表:")#line:59
            OO0OOOOO0000OO0OO ='''CREATE TABLE IF NOT EXISTS `server_status` (
                    `status` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:63
            O0OOO00O00O0OOOOO .execute (OO0OOOOO0000OO0OO )#line:64
            OO00OOO000O0O0O0O =True #line:65
        if "backup_status"not in OOO0OO00O00000O00 :#line:67
            print ("创建备份状态表:")#line:68
            OO0OOOOO0000OO0OO ='''CREATE TABLE IF NOT EXISTS `backup_status` (
                    `id` INTEGER,
                    `target` TEXT,
                    `status` INTEGER,
                    `msg` TEXT DEFAULT "",
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:75
            O0OOO00O00O0OOOOO .execute (OO0OOOOO0000OO0OO )#line:76
            OO00OOO000O0O0O0O =True #line:77
        if "daily"not in OOO0OO00O00000O00 :#line:79
            OO0OOOOO0000OO0OO ='''CREATE TABLE IF NOT EXISTS `daily` (
                    `time_key` INTEGER,
                    `evaluate` INTEGER,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:84
            O0OOO00O00O0OOOOO .execute (OO0OOOOO0000OO0OO )#line:85
            OO00OOO000O0O0O0O =True #line:86
        if OO00OOO000O0O0O0O :#line:88
            O00O000OOO0OOO0O0 .commit ()#line:89
        O0OOO00O00O0OOOOO .close ()#line:90
        O00O000OOO0OOO0O0 .close ()#line:91
        return True #line:92
    def get_time_key (OOOOOOO0O00000OOO ,date =None ):#line:94
        if date is None :#line:95
            date =time .localtime ()#line:96
        OOOO0OOOOO0O000OO =0 #line:97
        OO00OO00O00OO0O00 ="%Y%m%d"#line:98
        if type (date )==time .struct_time :#line:99
            OOOO0OOOOO0O000OO =int (time .strftime (OO00OO00O00OO0O00 ,date ))#line:100
        if type (date )==str :#line:101
            OOOO0OOOOO0O000OO =int (time .strptime (date ,OO00OO00O00OO0O00 ))#line:102
        return OOOO0OOOOO0O000OO #line:103
    def store_app_usage (OOO000O0O0O0O0OO0 ,time_key =None ):#line:105
        ""#line:113
        OOO000O0O0O0O0OO0 .check_databases ()#line:115
        if time_key is None :#line:117
            time_key =OOO000O0O0O0O0OO0 .get_time_key ()#line:118
        OO00OO00OOOOO0OOO =public .M ("system").dbfile ("system").table ("app_usage")#line:120
        O000000OO0OO0O000 =OO00OO00OOOOO0OOO .field ("time_key").where ("time_key=?",(time_key )).find ()#line:121
        if O000000OO0OO0O000 and "time_key"in O000000OO0OO0O000 :#line:122
            if O000000OO0OO0O000 ["time_key"]==time_key :#line:123
                return True #line:125
        O00OO000OOO000O00 =public .M ('sites').field ('path').select ()#line:127
        OOO000O00O000O0OO =0 #line:128
        for OO000O0O0O00000OO in O00OO000OOO000O00 :#line:129
            O0O000000OOOO0OO0 =OO000O0O0O00000OO ["path"]#line:130
            if O0O000000OOOO0OO0 :#line:131
                OOO000O00O000O0OO +=public .get_path_size (O0O000000OOOO0OO0 )#line:132
        O0O00OOOOO0O0O000 =public .get_path_size ("/www/server/data")#line:134
        O0O000O000OOO00O0 =public .M ("ftps").field ("path").select ()#line:136
        OO00OO00O000O0OOO =0 #line:137
        for OO000O0O0O00000OO in O0O000O000OOO00O0 :#line:138
            O0O0000000O0OO00O =OO000O0O0O00000OO ["path"]#line:139
            if O0O0000000O0OO00O :#line:140
                OO00OO00O000O0OOO +=public .get_path_size (O0O0000000O0OO00O )#line:141
        OOO0O0OOOO0O000OO =public .get_path_size ("/www/server/panel/plugin")#line:143
        O00000OO0OO00OO00 =["/www/server/total","/www/server/btwaf","/www/server/coll","/www/server/nginx","/www/server/apache","/www/server/redis"]#line:151
        for O0OOOO00000O0O0OO in O00000OO0OO00OO00 :#line:152
            OOO0O0OOOO0O000OO +=public .get_path_size (O0OOOO00000O0O0OO )#line:153
        O00O0OOOOO0000O00 =system ().GetDiskInfo2 (human =False )#line:155
        O000000OO000O0OO0 =""#line:156
        O0O0OOO000OO0O000 =0 #line:157
        O0000O000000OO000 =0 #line:158
        for OOO0OO0O0OOOOO00O in O00O0OOOOO0000O00 :#line:159
            O00OO000O00O00O00 =OOO0OO0O0OOOOO00O ["path"].replace ("-","_")#line:160
            if O000000OO000O0OO0 :#line:161
                O000000OO000O0OO0 +="-"#line:162
            O000OOOO0O00O0O0O ,OOO0O0OOO0OOO0O00 ,OO00OO0O0O00O0OO0 ,OO0O0O00O000O0OOO =OOO0OO0O0OOOOO00O ["size"]#line:163
            OO0O0O00000OOOO00 ,O0O00OO0O000O00O0 ,_OOO0OOO000O000O00 ,_O0000000O0OOOOOOO =OOO0OO0O0OOOOO00O ["inodes"]#line:164
            O000000OO000O0OO0 ="{},{},{},{},{}".format (O00OO000O00O00O00 ,OOO0O0OOO0OOO0O00 ,O000OOOO0O00O0O0O ,O0O00OO0O000O00O0 ,OO0O0O00000OOOO00 )#line:165
            if O00OO000O00O00O00 =="/":#line:166
                O0O0OOO000OO0O000 =O000OOOO0O00O0O0O #line:167
                O0000O000000OO000 =OOO0O0OOO0OOO0O00 #line:168
        OOOOO00O00O0OOO0O ="{},{},{},{},{},{}".format (O0O0OOO000OO0O000 ,O0000O000000OO000 ,OOO000O00O000O0OO ,O0O00OOOOO0O0O000 ,OO00OO00O000O0OOO ,OOO0O0OOOO0O000OO )#line:173
        OOO0000000O00O0OO =public .M ("system").dbfile ("system").table ("app_usage").add ("time_key,app,disks",(time_key ,OOOOO00O00O0OOO0O ,O000000OO000O0OO0 ))#line:175
        if OOO0000000O00O0OO ==time_key :#line:176
            return True #line:177
        return False #line:180
    def parse_char_unit (OOOO0O00O0OOOO0OO ,O0O00O000000O0O0O ):#line:182
        O00O0OO0O0OO0O0O0 =0 #line:183
        try :#line:184
            O00O0OO0O0OO0O0O0 =float (O0O00O000000O0O0O )#line:185
        except :#line:186
            OO0O00OO00000OO00 =O0O00O000000O0O0O #line:187
            if OO0O00OO00000OO00 .find ("G")!=-1 :#line:188
                OO0O00OO00000OO00 =OO0O00OO00000OO00 .replace ("G","")#line:189
                O00O0OO0O0OO0O0O0 =float (OO0O00OO00000OO00 )*1024 *1024 *1024 #line:190
            elif OO0O00OO00000OO00 .find ("M")!=-1 :#line:191
                OO0O00OO00000OO00 =OO0O00OO00000OO00 .replace ("M","")#line:192
                O00O0OO0O0OO0O0O0 =float (OO0O00OO00000OO00 )*1024 *1024 #line:193
            else :#line:194
                O00O0OO0O0OO0O0O0 =float (OO0O00OO00000OO00 )#line:195
        return O00O0OO0O0OO0O0O0 #line:196
    def parse_app_usage_info (OOOO000000000O000 ,O000O000OO00OO0OO ):#line:198
        ""#line:199
        if not O000O000OO00OO0OO :#line:200
            return {}#line:201
        print (O000O000OO00OO0OO )#line:202
        O000OO000OO0OOO0O ,O0O0OO00O00O000O0 ,OO0OO000O0000O0OO ,OOO000000OOO00O00 ,OOOO0OO0OO000OO0O ,O00O0O0OO0O000O0O =O000O000OO00OO0OO ["app"].split (",")#line:203
        OO0000O0OO00O00OO =O000O000OO00OO0OO ["disks"].split ("-")#line:204
        O0O00000OOOO000OO ={}#line:205
        print ("disk tmp:")#line:206
        print (OO0000O0OO00O00OO )#line:207
        for OOO00OO0OOO0O000O in OO0000O0OO00O00OO :#line:208
            print (OOO00OO0OOO0O000O )#line:209
            OOO0OO00000OOO0OO ,O0O000O0O0O0O00O0 ,O0OO00O0OO000000O ,O0O0O000OO0OO0000 ,OOOOO0OO0OOOO00O0 =OOO00OO0OOO0O000O .split (",")#line:210
            OO000000000O00O0O ={}#line:211
            OO000000000O00O0O ["usage"]=OOOO000000000O000 .parse_char_unit (O0O000O0O0O0O00O0 )#line:212
            OO000000000O00O0O ["total"]=OOOO000000000O000 .parse_char_unit (O0OO00O0OO000000O )#line:213
            OO000000000O00O0O ["iusage"]=O0O0O000OO0OO0000 #line:214
            OO000000000O00O0O ["itotal"]=OOOOO0OO0OOOO00O0 #line:215
            O0O00000OOOO000OO [OOO0OO00000OOO0OO ]=OO000000000O00O0O #line:216
        return {"apps":{"disk_total":O000OO000OO0OOO0O ,"disk_usage":O0O0OO00O00O000O0 ,"sites":OO0OO000O0000O0OO ,"databases":OOO000000OOO00O00 ,"ftps":OOOO0OO0OO000OO0O ,"plugins":O00O0O0OO0O000O0O },"disks":O0O00000OOOO000OO }#line:227
    def get_app_usage (O00O00OOO0OO0O000 ,O00OO0000O00O0OOO ):#line:229
        O000O00OO00OO0O00 =time .localtime ()#line:231
        O0OOO0OOOO0O00O00 =O00O00OOO0OO0O000 .get_time_key ()#line:232
        OO0OO00O0O000O00O =time .localtime (time .mktime ((O000O00OO00OO0O00 .tm_year ,O000O00OO00OO0O00 .tm_mon ,O000O00OO00OO0O00 .tm_mday -1 ,0 ,0 ,0 ,0 ,0 ,0 )))#line:235
        OOO000OO0O0O00OO0 =O00O00OOO0OO0O000 .get_time_key (OO0OO00O0O000O00O )#line:236
        OO0O00OO0000OO0O0 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key =? or time_key=?",(O0OOO0OOOO0O00O00 ,OOO000OO0O0O00OO0 ))#line:238
        OOO0O0OOO00OOOO00 =OO0O00OO0000OO0O0 .select ()#line:239
        if type (OOO0O0OOO00OOOO00 )==str or not OOO0O0OOO00OOOO00 :#line:242
            return {}#line:243
        OO0OOOOOOOOO0OOOO ={}#line:244
        OO0O000OO0000O0OO ={}#line:245
        for OO0OOO000OOOOOOO0 in OOO0O0OOO00OOOO00 :#line:246
            if OO0OOO000OOOOOOO0 ["time_key"]==O0OOO0OOOO0O00O00 :#line:247
                OO0OOOOOOOOO0OOOO =O00O00OOO0OO0O000 .parse_app_usage_info (OO0OOO000OOOOOOO0 )#line:248
            if OO0OOO000OOOOOOO0 ["time_key"]==OOO000OO0O0O00OO0 :#line:249
                OO0O000OO0000O0OO =O00O00OOO0OO0O000 .parse_app_usage_info (OO0OOO000OOOOOOO0 )#line:250
        if not OO0OOOOOOOOO0OOOO :#line:252
            return {}#line:253
        for OO000O000OO00O0OO ,OO00OOOOO0OO0O00O in OO0OOOOOOOOO0OOOO ["disks"].items ():#line:256
            OOO0OO00OO000O00O =int (OO00OOOOO0OO0O00O ["total"])#line:257
            OOO0O0OO0O000O00O =int (OO00OOOOO0OO0O00O ["usage"])#line:258
            OO000O00O00O00000 =int (OO00OOOOO0OO0O00O ["itotal"])#line:260
            O00O00O00O0000OOO =int (OO00OOOOO0OO0O00O ["iusage"])#line:261
            if OO0O000OO0000O0OO and OO000O000OO00O0OO in OO0O000OO0000O0OO ["disks"].keys ():#line:263
                OOO0000OO0O0O0OOO =OO0O000OO0000O0OO ["disks"]#line:264
                OOOOO0O000000O0O0 =OOO0000OO0O0O0OOO [OO000O000OO00O0OO ]#line:265
                O00O0O0O0OOO00O0O =int (OOOOO0O000000O0O0 ["total"])#line:266
                if O00O0O0O0OOO00O0O ==OOO0OO00OO000O00O :#line:267
                    OOO000OOO0O000OO0 =int (OOOOO0O000000O0O0 ["usage"])#line:268
                    OO00O0000OO0000O0 =0 #line:269
                    O00O0O00O0OOO0O0O =OOO0O0OO0O000O00O -OOO000OOO0O000OO0 #line:270
                    if O00O0O00O0OOO0O0O >0 :#line:271
                        OO00O0000OO0000O0 =round (O00O0O00O0OOO0O0O /OOO0OO00OO000O00O ,2 )#line:272
                    OO00OOOOO0OO0O00O ["incr"]=OO00O0000OO0000O0 #line:273
                O0OO00O0OOO0OO00O =int (OOOOO0O000000O0O0 ["itotal"])#line:276
                if True :#line:277
                    OOOOOO00O0O0OOO0O =int (OOOOO0O000000O0O0 ["iusage"])#line:278
                    O0OOOOOO00O0OOO0O =0 #line:279
                    O00O0O00O0OOO0O0O =O00O00O00O0000OOO -OOOOOO00O0O0OOO0O #line:280
                    if O00O0O00O0OOO0O0O >0 :#line:281
                        O0OOOOOO00O0OOO0O =round (O00O0O00O0OOO0O0O /OO000O00O00O00000 ,2 )#line:282
                    OO00OOOOO0OO0O00O ["iincr"]=O0OOOOOO00O0OOO0O #line:283
        OO0O0OOOO0O0OOO00 =OO0OOOOOOOOO0OOOO ["apps"]#line:287
        OO0OOO000OOOOOOOO =int (OO0O0OOOO0O0OOO00 ["disk_total"])#line:288
        if OO0O000OO0000O0OO and OO0O000OO0000O0OO ["apps"]["disk_total"]==OO0O0OOOO0O0OOO00 ["disk_total"]:#line:289
            OOO00OOOO0OO00O00 =OO0O000OO0000O0OO ["apps"]#line:290
            for O0000000O0000O00O ,OOOO00O000O00O000 in OO0O0OOOO0O0OOO00 .items ():#line:291
                if O0000000O0000O00O =="disks":continue #line:292
                if O0000000O0000O00O =="disk_total":continue #line:293
                if O0000000O0000O00O =="disk_usage":continue #line:294
                OOO0OO0O0O0OO00O0 =0 #line:295
                O00OOOO0000000O00 =int (OOOO00O000O00O000 )-int (OOO00OOOO0OO00O00 [O0000000O0000O00O ])#line:296
                if O00OOOO0000000O00 >0 :#line:297
                    OOO0OO0O0O0OO00O0 =round (O00OOOO0000000O00 /OO0OOO000OOOOOOOO ,2 )#line:298
                OO0O0OOOO0O0OOO00 [O0000000O0000O00O ]={"val":OOOO00O000O00O000 ,"incr":OOO0OO0O0O0OO00O0 }#line:303
        return OO0OOOOOOOOO0OOOO #line:304
    def get_timestamp_interval (OO0000OO0O00O00O0 ,OO0OO00O0O0OOOO00 ):#line:306
        O0000O0O000O00OOO =None #line:307
        O0OOO00O0O0OO0O00 =None #line:308
        O0000O0O000O00OOO =time .mktime ((OO0OO00O0O0OOOO00 .tm_year ,OO0OO00O0O0OOOO00 .tm_mon ,OO0OO00O0O0OOOO00 .tm_mday ,0 ,0 ,0 ,0 ,0 ,0 ))#line:310
        O0OOO00O0O0OO0O00 =time .mktime ((OO0OO00O0O0OOOO00 .tm_year ,OO0OO00O0O0OOOO00 .tm_mon ,OO0OO00O0O0OOOO00 .tm_mday ,23 ,59 ,59 ,0 ,0 ,0 ))#line:312
        return O0000O0O000O00OOO ,O0OOO00O0O0OO0O00 #line:313
    def check_server (OO0OOO0O00O00000O ):#line:316
        try :#line:317
            O00O00O0000O000O0 =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:320
            O000OOOOOO00OO00O =panelPlugin ()#line:321
            O00OOOO0OO0OOO0O0 =public .dict_obj ()#line:322
            O0OO000O00O00O0OO =""#line:323
            for O00O000000O0O0OOO in O00O00O0000O000O0 :#line:324
                O0OO0O0O0000O0000 =False #line:325
                OOOO0OO0O0000O00O =False #line:326
                O00OOOO0OO0OOO0O0 .name =O00O000000O0O0OOO #line:327
                O00OO0OOO00O0O0O0 =O000OOOOOO00OO00O .getPluginInfo (O00OOOO0OO0OOO0O0 )#line:328
                if not O00OO0OOO00O0O0O0 :#line:329
                    continue #line:330
                OO0O000O0OO00OO00 =O00OO0OOO00O0O0O0 ["versions"]#line:331
                for OO0OOO00O000OO000 in OO0O000O0OO00OO00 :#line:333
                    if OO0OOO00O000OO000 ["status"]:#line:336
                        OOOO0OO0O0000O00O =True #line:337
                    if "run"in OO0OOO00O000OO000 .keys ()and OO0OOO00O000OO000 ["run"]:#line:338
                        OOOO0OO0O0000O00O =True #line:340
                        O0OO0O0O0000O0000 =True #line:341
                        break #line:342
                OOO0OOOOOO00O0OO0 =0 #line:343
                if OOOO0OO0O0000O00O :#line:344
                    OOO0OOOOOO00O0OO0 =1 #line:345
                    if not O0OO0O0O0000O0000 :#line:347
                        OOO0OOOOOO00O0OO0 =2 #line:348
                O0OO000O00O00O0OO +=str (OOO0OOOOOO00O0OO0 )#line:349
            if '2'in O0OO000O00O00O0OO :#line:353
                public .M ("system").dbfile ("server_status").add ("status, addtime",(O0OO000O00O00O0OO ,time .time ()))#line:355
        except Exception as O00OOOO000O00O0O0 :#line:356
            return True #line:358
    def get_daily_data (O0OOO0OO0000OO00O ,OOOOO0OOO0OO0O000 ):#line:360
        ""#line:361
        O0OO0O00O0O00000O ="IS_PRO_OR_LTD_FOR_PANEL_DAILY"#line:363
        OO00OOOOO00000O00 =cache .get (O0OO0O00O0O00000O )#line:364
        if not OO00OOOOO00000O00 :#line:365
            try :#line:366
                OOO00O000O0000OOO =panelPlugin ()#line:367
                O00O0O00OOO00O0O0 =OOO00O000O0000OOO .get_soft_list (OOOOO0OOO0OO0O000 )#line:368
                if O00O0O00OOO00O0O0 ["pro"]<0 and O00O0O00OOO00O0O0 ["ltd"]<0 :#line:369
                    if os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:370
                        os .remove ("/www/server/panel/data/start_daily.pl")#line:371
                    return {"status":False ,"msg":"No authorization.","data":[],"date":OOOOO0OOO0OO0O000 .date }#line:377
                cache .set (O0OO0O00O0O00000O ,True ,86400 )#line:378
            except :#line:379
                return {"status":False ,"msg":"获取不到授权信息，请检查网络是否正常","data":[],"date":OOOOO0OOO0OO0O000 .date }#line:385
        if not os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:388
            public .writeFile ("/www/server/panel/data/start_daily.pl",OOOOO0OOO0OO0O000 .date )#line:389
        return O0OOO0OO0000OO00O .get_daily_data_local (OOOOO0OOO0OO0O000 .date )#line:390
    def get_daily_data_local (O000OOO0OOO0O0O0O ,OO00OOO00O00OO0O0 ):#line:392
        O0OOO0O0O0OOOOOOO =time .strptime (OO00OOO00O00OO0O0 ,"%Y%m%d")#line:393
        O0O0O00OOOOO0O000 =O000OOO0OOO0O0O0O .get_time_key (O0OOO0O0O0OOOOOOO )#line:394
        O000OOO0OOO0O0O0O .check_databases ()#line:396
        O0OOO0O0OO0O00O0O =time .strftime ("%Y-%m-%d",O0OOO0O0O0OOOOOOO )#line:398
        O00000O00OO00OO00 =0 #line:399
        O0OO0OOOO0O000OO0 ,O0O0O00OOO0000O0O =O000OOO0OOO0O0O0O .get_timestamp_interval (O0OOO0O0O0OOOOOOO )#line:400
        OO00O0O0OOOO0O000 =public .M ("system").dbfile ("system")#line:401
        O0O0O0OO0000OO0OO =OO00O0O0OOOO0O000 .table ("process_high_percent")#line:402
        O00O0OO0OO00O0000 =O0O0O0OO0000OO0OO .where ("addtime>=? and addtime<=?",(O0OO0OOOO0O000OO0 ,O0O0O00OOO0000O0O )).order ("addtime").select ()#line:403
        O0O0OOOO000O000OO =[]#line:406
        try :#line:407
            if len (O00O0OO0OO00O0000 )>0 :#line:408
                for O0O0O0OOO000O0O00 in O00O0OO0OO00O0000 :#line:410
                    try :#line:412
                        O00O0OOO0000OOO0O =int (O0O0O0OOO000O0O00 ["cpu_percent"])#line:413
                        if O00O0OOO0000OOO0O >=80 :#line:414
                            O0O0OOOO000O000OO .append ({"time":O0O0O0OOO000O0O00 ["addtime"],"name":O0O0O0OOO000O0O00 ["name"],"pid":O0O0O0OOO000O0O00 ["pid"],"percent":O00O0OOO0000OOO0O })#line:422
                    except :pass #line:423
        except :#line:424
            O0O0O0OO0000OO0OO =OO00O0O0OOOO0O000 .table ("process_top_list")#line:425
            O00O0OO0OO00O0000 =O0O0O0OO0000OO0OO .where ("addtime>=? and addtime<=?",(O0OO0OOOO0O000OO0 ,O0O0O00OOO0000O0O )).order ("addtime").select ()#line:426
            if len (O00O0OO0OO00O0000 )>0 :#line:427
                for O0O0O0OOO000O0O00 in O00O0OO0OO00O0000 :#line:428
                    OOO00OO00O0OOO00O =json .loads (O0O0O0OOO000O0O00 ["cpu_top"])#line:429
                    for O0O00OOOO0O0OO000 in OOO00OO00O0OOO00O :#line:430
                        O00O0OOO0000OOO0O =int (O0O00OOOO0O0OO000 [0 ])#line:431
                        if O00O0OOO0000OOO0O >=80 :#line:432
                            O0O0OOOO000O000OO .append ({"time":O0O00OOOO0O0OO000 [5 ],"name":O0O00OOOO0O0OO000 [3 ],"pid":O0O00OOOO0O0OO000 [1 ],"percent":O00O0OOO0000OOO0O })#line:440
        O00O0000OO000OO0O =len (O0O0OOOO000O000OO )#line:441
        OO0OOO00O000O0000 =0 #line:442
        OOO00O0OO0OOO0O00 =""#line:443
        if O00O0000OO000OO0O ==0 :#line:444
            OO0OOO00O000O0000 =20 #line:445
        else :#line:446
            OOO00O0OO0OOO0O00 ="CPU出现过载情况"#line:447
        O0OO000O0O0000OOO ={"ex":O00O0000OO000OO0O ,"detail":O0O0OOOO000O000OO }#line:451
        OOOO0OO0000O00OOO =[]#line:454
        if len (O00O0OO0OO00O0000 )>0 :#line:455
            try :#line:456
                for O0O0O0OOO000O0O00 in O00O0OO0OO00O0000 :#line:458
                    try :#line:460
                        OOO000O0O00O0OO00 =float (O0O0O0OOO000O0O00 ["memory"])#line:461
                        O0000OO0000000O00 =psutil .virtual_memory ().total #line:462
                        OO000O0OOO0O0000O =round (100 *OOO000O0O00O0OO00 /O0000OO0000000O00 ,2 )#line:463
                        if OO000O0OOO0O0000O >=80 :#line:464
                            OOOO0OO0000O00OOO .append ({"time":O0O0O0OOO000O0O00 ["addtime"],"name":O0O0O0OOO000O0O00 ["name"],"pid":O0O0O0OOO000O0O00 ["pid"],"percent":OO000O0OOO0O0000O })#line:472
                    except :pass #line:473
            except :#line:474
                for O0O0O0OOO000O0O00 in O00O0OO0OO00O0000 :#line:475
                    O00O00OO0O0OO0OO0 =json .loads (O0O0O0OOO000O0O00 ["memory_top"])#line:476
                    O0000OO0000000O00 =psutil .virtual_memory ().total #line:477
                    for O0O00OOOO0O0OO000 in O00O00OO0O0OO0OO0 :#line:478
                        OO000O0OOO0O0000O =round (100 *O0O00OOOO0O0OO000 [0 ]/O0000OO0000000O00 ,2 )#line:480
                        if OO000O0OOO0O0000O >=80 :#line:482
                            OOOO0OO0000O00OOO .append ({"time":O0O00OOOO0O0OO000 [5 ],"name":O0O00OOOO0O0OO000 [3 ],"pid":O0O00OOOO0O0OO000 [1 ],"percent":OO000O0OOO0O0000O })#line:490
        O00000OOO0000000O =len (OOOO0OO0000O00OOO )#line:491
        OOOOO00OO00OOOOOO =""#line:492
        OO00OOOOOO00O0O0O =0 #line:493
        if O00000OOO0000000O ==0 :#line:494
            OO00OOOOOO00O0O0O =20 #line:495
        else :#line:496
            if O00000OOO0000000O >1 :#line:497
                OOOOO00OO00OOOOOO ="内存在多个时间点出现占用80%"#line:498
            else :#line:499
                OOOOO00OO00OOOOOO ="内存出现占用超过80%"#line:500
        OO0O0000O0O000O0O ={"ex":O00000OOO0000000O ,"detail":OOOO0OO0000O00OOO }#line:504
        OO0OO000OO00OO0OO =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key=?",(O0O0O00OOOOO0O000 ,))#line:508
        O0O00O00O00OOOO00 =OO0OO000OO00OO0OO .select ()#line:509
        O0OO000OOOO0OO0O0 ={}#line:510
        if O0O00O00O00OOOO00 and type (O0O00O00O00OOOO00 )!=str :#line:511
            O0OO000OOOO0OO0O0 =O000OOO0OOO0O0O0O .parse_app_usage_info (O0O00O00O00OOOO00 [0 ])#line:512
        O0OO0O0O0O00OOOOO =[]#line:513
        if O0OO000OOOO0OO0O0 :#line:514
            O000O0O0000O00000 =O0OO000OOOO0OO0O0 ["disks"]#line:515
            for O000O00O0OO0OO000 ,OOO0O00OOOOOOO0O0 in O000O0O0000O00000 .items ():#line:516
                OO00OO0OOOO0OOO0O =int (OOO0O00OOOOOOO0O0 ["usage"])#line:517
                O0000OO0000000O00 =int (OOO0O00OOOOOOO0O0 ["total"])#line:518
                OO0OO0OOOOOO0O0O0 =round (OO00OO0OOOO0OOO0O /O0000OO0000000O00 ,2 )#line:519
                O0O00OOOOOOO00O0O =int (OOO0O00OOOOOOO0O0 ["iusage"])#line:520
                OOO00O00OOO000000 =int (OOO0O00OOOOOOO0O0 ["itotal"])#line:521
                if OOO00O00OOO000000 >0 :#line:522
                    O0OO0OO0OOO000O00 =round (O0O00OOOOOOO00O0O /OOO00O00OOO000000 ,2 )#line:523
                else :#line:524
                    O0OO0OO0OOO000O00 =0 #line:525
                if OO0OO0OOOOOO0O0O0 >=0.8 :#line:529
                    O0OO0O0O0O00OOOOO .append ({"name":O000O00O0OO0OO000 ,"percent":OO0OO0OOOOOO0O0O0 *100 ,"ipercent":O0OO0OO0OOO000O00 *100 ,"usage":OO00OO0OOOO0OOO0O ,"total":O0000OO0000000O00 ,"iusage":O0O00OOOOOOO00O0O ,"itotal":OOO00O00OOO000000 })#line:538
        O000OOO00O00OO00O =len (O0OO0O0O0O00OOOOO )#line:540
        OOO0O0OOO0O0O0O0O =""#line:541
        OOOOO0O00000OOO00 =0 #line:542
        if O000OOO00O00OO00O ==0 :#line:543
            OOOOO0O00000OOO00 =20 #line:544
        else :#line:545
            OOO0O0OOO0O0O0O0O ="有磁盘空间占用已经超过80%"#line:546
        O0O0O0OOOO000OOOO ={"ex":O000OOO00O00OO00O ,"detail":O0OO0O0O0O00OOOOO }#line:551
        O0OOO0OOO00OO0000 =public .M ("system").dbfile ("system").table ("server_status").where ("addtime>=? and addtime<=?",(O0OO0OOOO0O000OO0 ,O0O0O00OOO0000O0O ,)).order ("addtime desc").select ()#line:555
        O00O0000OO00O00OO =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:560
        O000OO0OOOO00OO0O ={}#line:562
        OO0OO0OO0OO000OO0 =0 #line:563
        OOOOO0000000OOO0O =""#line:564
        for O00O0OOO00O000OOO ,O0O000O00OO0000OO in enumerate (O00O0000OO00O00OO ):#line:565
            if O0O000O00OO0000OO =="pure-ftpd":#line:566
                O0O000O00OO0000OO ="ftpd"#line:567
            OOO0OOO000OOOOOOO =0 #line:568
            OOO0O0OOO000OO000 =[]#line:569
            for O000OO00O00OOO0O0 in O0OOO0OOO00OO0000 :#line:570
                _O00OOO0O0OOOO0O00 =O000OO00O00OOO0O0 ["status"]#line:573
                if O00O0OOO00O000OOO <len (_O00OOO0O0OOOO0O00 ):#line:574
                    if _O00OOO0O0OOOO0O00 [O00O0OOO00O000OOO ]=="2":#line:575
                        OOO0O0OOO000OO000 .append ({"time":O000OO00O00OOO0O0 ["addtime"],"desc":"退出"})#line:576
                        OOO0OOO000OOOOOOO +=1 #line:577
                        OO0OO0OO0OO000OO0 +=1 #line:578
            O000OO0OOOO00OO0O [O0O000O00OO0000OO ]={"ex":OOO0OOO000OOOOOOO ,"detail":OOO0O0OOO000OO000 }#line:583
        OO0OO0O0OO0OO00O0 =0 #line:585
        if OO0OO0OO0OO000OO0 ==0 :#line:586
            OO0OO0O0OO0OO00O0 =20 #line:587
        else :#line:588
            OOOOO0000000OOO0O ="系统级服务有出现异常退出情况"#line:589
        O0O000O0O0OO0OOO0 =public .M ("crontab").field ("name,sName,sType").where ("sType in (?, ?, ?)",("database","enterpriseBackup","site",)).select ()#line:593
        O0O0O00OOO0000OOO =set ()#line:596
        for OO0OOOOOO000OOO00 in O0O000O0O0OO0OOO0 :#line:597
            if OO0OOOOOO000OOO00 ["sType"]=="database":#line:598
                O0O0O00OOO0000OOO .add (OO0OOOOOO000OOO00 ["sName"])#line:599
            elif OO0OOOOOO000OOO00 ["sType"]=="enterpriseBackup":#line:600
                O00O0O0OOOOOOO00O =OO0OOOOOO000OOO00 ["name"]#line:601
                OOO0O00OO000OOO0O =O00O0O0OOOOOOO00O [O00O0O0OOOOOOO00O .rfind ("[")+1 :O00O0O0OOOOOOO00O .rfind ("]")]#line:602
                O0O0O00OOO0000OOO .add (OOO0O00OO000OOO0O )#line:603
        O00O0000O00OO0O00 ="ALL"in O0O0O00OOO0000OOO #line:607
        OOO000O0000OO00OO =set (OO0000000O0O00O00 ["sName"]for OO0000000O0O00O00 in O0O000O0O0OO0OOO0 if OO0000000O0O00O00 ["sType"]=="site")#line:608
        OOO00000OOOO0O0OO ="ALL"in OOO000O0000OO00OO #line:609
        O0O0O00O0O000OOO0 =[]#line:610
        O00OOO0O00O000O00 =[]#line:611
        if not O00O0000O00OO0O00 :#line:612
            O0O00OO00O0OOO0O0 =public .M ("databases").field ("name").select ()#line:613
            for O0O0O0OO0OO00OOOO in O0O00OO00O0OOO0O0 :#line:614
                O0O00O0OOOO000O00 =O0O0O0OO0OO00OOOO ["name"]#line:615
                if O0O00O0OOOO000O00 not in O0O0O00OOO0000OOO :#line:616
                    O0O0O00O0O000OOO0 .append ({"name":O0O00O0OOOO000O00 })#line:617
        if not OOO00000OOOO0O0OO :#line:619
            OOO0O0OO00O00OOOO =public .M ("sites").field ("name").select ()#line:620
            for OOO0OO0OOO00OOOO0 in OOO0O0OO00O00OOOO :#line:621
                OOOOO00OOO0O00O0O =OOO0OO0OOO00OOOO0 ["name"]#line:622
                if OOOOO00OOO0O00O0O not in OOO000O0000OO00OO :#line:623
                    O00OOO0O00O000O00 .append ({"name":OOOOO00OOO0O00O0O })#line:624
        OOOO0000O0OO0O0O0 =public .M ("system").dbfile ("system").table ("backup_status").where ("addtime>=? and addtime<=?",(O0OO0OOOO0O000OO0 ,O0O0O00OOO0000O0O )).select ()#line:627
        O00OOO0OO0000O0OO ={"database":{"no_backup":O0O0O00O0O000OOO0 ,"backup":[]},"site":{"no_backup":O00OOO0O00O000O00 ,"backup":[]},"path":{"no_backup":[],"backup":[]}}#line:642
        OOO000OO00OO00O00 =0 #line:643
        for OOO0OOOO000OOOOO0 in OOOO0000O0OO0O0O0 :#line:644
            OOO00OOOOO00O0OO0 =OOO0OOOO000OOOOO0 ["status"]#line:645
            if OOO00OOOOO00O0OO0 :#line:646
                continue #line:647
            OOO000OO00OO00O00 +=1 #line:649
            OO0O00OOOOO0OOOOO =OOO0OOOO000OOOOO0 ["id"]#line:650
            O00OOO00OOO000OO0 =public .M ("crontab").where ("id=?",(OO0O00OOOOO0OOOOO )).find ()#line:651
            if not O00OOO00OOO000OO0 :#line:652
                continue #line:653
            O000O0O00000O0OO0 =O00OOO00OOO000OO0 ["sType"]#line:654
            if not O000O0O00000O0OO0 :#line:655
                continue #line:656
            OOO0O00OO000OOO0O =O00OOO00OOO000OO0 ["name"]#line:657
            O0O0000O00O0OO00O =OOO0OOOO000OOOOO0 ["addtime"]#line:658
            O00OO0OO0O0O00OO0 =OOO0OOOO000OOOOO0 ["target"]#line:659
            if O000O0O00000O0OO0 not in O00OOO0OO0000O0OO .keys ():#line:660
                O00OOO0OO0000O0OO [O000O0O00000O0OO0 ]={}#line:661
                O00OOO0OO0000O0OO [O000O0O00000O0OO0 ]["backup"]=[]#line:662
                O00OOO0OO0000O0OO [O000O0O00000O0OO0 ]["no_backup"]=[]#line:663
            O00OOO0OO0000O0OO [O000O0O00000O0OO0 ]["backup"].append ({"name":OOO0O00OO000OOO0O ,"target":O00OO0OO0O0O00OO0 ,"status":OOO00OOOOO00O0OO0 ,"target":O00OO0OO0O0O00OO0 ,"time":O0O0000O00O0OO00O })#line:670
        OO00O0OOO0OO0OO0O =""#line:672
        O000OO000O0O0OOO0 =0 #line:673
        if OOO000OO00OO00O00 ==0 :#line:674
            O000OO000O0O0OOO0 =20 #line:675
        else :#line:676
            OO00O0OOO0OO0OO0O ="有计划任务备份失败"#line:677
        if len (O0O0O00O0O000OOO0 )==0 :#line:679
            O000OO000O0O0OOO0 +=10 #line:680
        else :#line:681
            if OO00O0OOO0OO0OO0O :#line:682
                OO00O0OOO0OO0OO0O +=";"#line:683
            OO00O0OOO0OO0OO0O +="有数据库未及时备份"#line:684
        if len (O00OOO0O00O000O00 )==0 :#line:686
            O000OO000O0O0OOO0 +=10 #line:687
        else :#line:688
            if OO00O0OOO0OO0OO0O :#line:689
                OO00O0OOO0OO0OO0O +=";"#line:690
            OO00O0OOO0OO0OO0O +="有网站未备份"#line:691
        O0OO00O000OO000OO =0 #line:694
        OO0OO0000OO0O00OO =public .M ('logs').where ('addtime like ? and type=?',(str (O0OOO0O0OO0O00O0O )+"%",'用户登录',)).select ()#line:695
        OOO0O0O00000000OO =[]#line:696
        if OO0OO0000OO0O00OO and type (OO0OO0000OO0O00OO )==list :#line:697
            for OO0OOOOO0O00O0OO0 in OO0OO0000OO0O00OO :#line:698
                OOO0OO0O0OOOOOOO0 =OO0OOOOO0O00O0OO0 ["log"]#line:699
                if OOO0OO0O0OOOOOOO0 .find ("失败")>=0 or OOO0OO0O0OOOOOOO0 .find ("错误")>=0 :#line:700
                    O0OO00O000OO000OO +=1 #line:701
                    OOO0O0O00000000OO .append ({"time":time .mktime (time .strptime (OO0OOOOO0O00O0OO0 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":OO0OOOOO0O00O0OO0 ["log"],"username":OO0OOOOO0O00O0OO0 ["username"],})#line:706
            OOO0O0O00000000OO .sort (key =lambda OO0OOO00O0O000O00 :OO0OOO00O0O000O00 ["time"])#line:707
        O00OO0000OO000O00 =public .M ('logs').where ('type=?',('SSH安全',)).where ("addtime like ?",(str (O0OOO0O0OO0O00O0O )+"%",)).select ()#line:709
        OOOO000000OO0O0O0 =[]#line:711
        O0O00OOOOO0OOO0O0 =0 #line:712
        if O00OO0000OO000O00 :#line:713
            for OO0OOOOO0O00O0OO0 in O00OO0000OO000O00 :#line:714
                OOO0OO0O0OOOOOOO0 =OO0OOOOO0O00O0OO0 ["log"]#line:715
                if OOO0OO0O0OOOOOOO0 .find ("存在异常")>=0 :#line:716
                    O0O00OOOOO0OOO0O0 +=1 #line:717
                    OOOO000000OO0O0O0 .append ({"time":time .mktime (time .strptime (OO0OOOOO0O00O0OO0 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":OO0OOOOO0O00O0OO0 ["log"],"username":OO0OOOOO0O00O0OO0 ["username"]})#line:722
            OOOO000000OO0O0O0 .sort (key =lambda OO0OO0OO000O0OO0O :OO0OO0OO000O0OO0O ["time"])#line:723
        OOO00OOOO00OO0OO0 =""#line:725
        OO00000O00O00OO0O =0 #line:726
        if O0O00OOOOO0OOO0O0 ==0 :#line:727
            OO00000O00O00OO0O =10 #line:728
        else :#line:729
            OOO00OOOO00OO0OO0 ="SSH有异常登录"#line:730
        if O0OO00O000OO000OO ==0 :#line:732
            OO00000O00O00OO0O +=10 #line:733
        else :#line:734
            if O0OO00O000OO000OO >10 :#line:735
                OO00000O00O00OO0O -=10 #line:736
            if OOO00OOOO00OO0OO0 :#line:737
                OOO00OOOO00OO0OO0 +=";"#line:738
            OOO00OOOO00OO0OO0 +="面板登录有错误".format (O0OO00O000OO000OO )#line:739
        O0OOO0OOO00OO0000 ={"panel":{"ex":O0OO00O000OO000OO ,"detail":OOO0O0O00000000OO },"ssh":{"ex":O0O00OOOOO0OOO0O0 ,"detail":OOOO000000OO0O0O0 }}#line:749
        O00000O00OO00OO00 =OO0OOO00O000O0000 +OO00OOOOOO00O0O0O +OOOOO0O00000OOO00 +OO0OO0O0OO0OO00O0 +O000OO000O0O0OOO0 +OO00000O00O00OO0O #line:751
        OOOO0OO0OO00000O0 =[OOO00O0OO0OOO0O00 ,OOOOO00OO00OOOOOO ,OOO0O0OOO0O0O0O0O ,OOOOO0000000OOO0O ,OO00O0OOO0OO0OO0O ,OOO00OOOO00OO0OO0 ]#line:752
        O000O0O0O00000OOO =[]#line:753
        for O0000O00O00OO0OOO in OOOO0OO0OO00000O0 :#line:754
            if O0000O00O00OO0OOO :#line:755
                if O0000O00O00OO0OOO .find (";")>=0 :#line:756
                    for OO00O0O00OOOOOOO0 in O0000O00O00OO0OOO .split (";"):#line:757
                        O000O0O0O00000OOO .append (OO00O0O00OOOOOOO0 )#line:758
                else :#line:759
                    O000O0O0O00000OOO .append (O0000O00O00OO0OOO )#line:760
        if not O000O0O0O00000OOO :#line:762
            O000O0O0O00000OOO .append ("服务器运行正常，请继续保持！")#line:763
        O0O0000O0O0OOOOO0 =O000OOO0OOO0O0O0O .evaluate (O00000O00OO00OO00 )#line:767
        return {"data":{"cpu":O0OO000O0O0000OOO ,"ram":OO0O0000O0O000O0O ,"disk":O0O0O0OOOO000OOOO ,"server":O000OO0OOOO00OO0O ,"backup":O00OOO0OO0000O0OO ,"exception":O0OOO0OOO00OO0000 ,},"evaluate":O0O0000O0O0OOOOO0 ,"score":O00000O00OO00OO00 ,"date":O0O0O00OOOOO0O000 ,"summary":O000O0O0O00000OOO ,"status":True }#line:784
    def evaluate (OO000000OO00000OO ,OOO000OOOOOO000OO ):#line:786
        OOO00O00O0O00O00O =""#line:787
        if OOO000OOOOOO000OO >=100 :#line:788
            OOO00O00O0O00O00O ="正常"#line:789
        elif OOO000OOOOOO000OO >=80 :#line:790
            OOO00O00O0O00O00O ="良好"#line:791
        else :#line:792
            OOO00O00O0O00O00O ="一般"#line:793
        return OOO00O00O0O00O00O #line:794
    def get_daily_list (O00O00O000OOO0O0O ,O0OOOO00OO0OO0OOO ):#line:796
        OOO0O0OO000OO00OO =public .M ("system").dbfile ("system").table ("daily").where ("time_key>?",0 ).select ()#line:797
        O0O0OOO0O00O0O00O =[]#line:798
        for OOOOO00OOO0O00OOO in OOO0O0OO000OO00OO :#line:799
            OOOOO00OOO0O00OOO ["evaluate"]=O00O00O000OOO0O0O .evaluate (OOOOO00OOO0O00OOO ["evaluate"])#line:800
            O0O0OOO0O00O0O00O .append (OOOOO00OOO0O00OOO )#line:801
        return O0O0OOO0O00O0O00O