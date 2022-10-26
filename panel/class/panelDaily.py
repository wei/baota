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
    def check_databases (O0O0O000000O0OOOO ):#line:30
        ""#line:31
        O0OOOOOOO00O0OOO0 =["app_usage","server_status","backup_status","daily"]#line:32
        import sqlite3 #line:33
        O0O0O0O0OO00OO0OO =sqlite3 .connect ("/www/server/panel/data/system.db")#line:34
        OOOOOO0OO0OO00O00 =O0O0O0O0OO00OO0OO .cursor ()#line:35
        O0O0OOOO00OOO0OO0 =",".join (["'"+OO000OO0O0OOO00O0 +"'"for OO000OO0O0OOO00O0 in O0OOOOOOO00O0OOO0 ])#line:36
        O0OOO0000O00O0O0O =OOOOOO0OO0OO00O00 .execute ("SELECT name FROM sqlite_master WHERE type='table' and name in ({})".format (O0O0OOOO00OOO0OO0 ))#line:37
        O00OO00OO00O0O000 =O0OOO0000O00O0O0O .fetchall ()#line:38
        O00O00O0O0OO00O0O =False #line:41
        OO00O0O000000O00O =[]#line:42
        if O00OO00OO00O0O000 :#line:43
            OO00O0O000000O00O =[OO00O000O00000O00 [0 ]for OO00O000O00000O00 in O00OO00OO00O0O000 ]#line:44
        if "app_usage"not in OO00O0O000000O00O :#line:46
            O0000O000000OO0O0 ='''CREATE TABLE IF NOT EXISTS `app_usage` (
                    `time_key` INTEGER PRIMARY KEY,
                    `app` TEXT,
                    `disks` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:52
            OOOOOO0OO0OO00O00 .execute (O0000O000000OO0O0 )#line:53
            O00O00O0O0OO00O0O =True #line:54
        if "server_status"not in OO00O0O000000O00O :#line:56
            print ("创建server_status表:")#line:57
            O0000O000000OO0O0 ='''CREATE TABLE IF NOT EXISTS `server_status` (
                    `status` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:61
            OOOOOO0OO0OO00O00 .execute (O0000O000000OO0O0 )#line:62
            O00O00O0O0OO00O0O =True #line:63
        if "backup_status"not in OO00O0O000000O00O :#line:65
            print ("创建备份状态表:")#line:66
            O0000O000000OO0O0 ='''CREATE TABLE IF NOT EXISTS `backup_status` (
                    `id` INTEGER,
                    `target` TEXT,
                    `status` INTEGER,
                    `msg` TEXT DEFAULT "",
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:73
            OOOOOO0OO0OO00O00 .execute (O0000O000000OO0O0 )#line:74
            O00O00O0O0OO00O0O =True #line:75
        if "daily"not in OO00O0O000000O00O :#line:77
            O0000O000000OO0O0 ='''CREATE TABLE IF NOT EXISTS `daily` (
                    `time_key` INTEGER,
                    `evaluate` INTEGER,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:82
            OOOOOO0OO0OO00O00 .execute (O0000O000000OO0O0 )#line:83
            O00O00O0O0OO00O0O =True #line:84
        if O00O00O0O0OO00O0O :#line:86
            O0O0O0O0OO00OO0OO .commit ()#line:87
        OOOOOO0OO0OO00O00 .close ()#line:88
        O0O0O0O0OO00OO0OO .close ()#line:89
        return True #line:90
    def get_time_key (O00OOO00O0O0OOO00 ,date =None ):#line:92
        if date is None :#line:93
            date =time .localtime ()#line:94
        O0O0OO0O0000O00OO =0 #line:95
        O00O00OOOO0OO0OOO ="%Y%m%d"#line:96
        if type (date )==time .struct_time :#line:97
            O0O0OO0O0000O00OO =int (time .strftime (O00O00OOOO0OO0OOO ,date ))#line:98
        if type (date )==str :#line:99
            O0O0OO0O0000O00OO =int (time .strptime (date ,O00O00OOOO0OO0OOO ))#line:100
        return O0O0OO0O0000O00OO #line:101
    def store_app_usage (O000OO000OOO00O00 ,time_key =None ):#line:103
        ""#line:111
        O000OO000OOO00O00 .check_databases ()#line:113
        if time_key is None :#line:115
            time_key =O000OO000OOO00O00 .get_time_key ()#line:116
        O0000O000O00O00OO =public .M ("system").dbfile ("system").table ("app_usage")#line:118
        O000O0O00OOOOOOO0 =O0000O000O00O00OO .field ("time_key").where ("time_key=?",(time_key )).find ()#line:119
        if O000O0O00OOOOOOO0 and "time_key"in O000O0O00OOOOOOO0 :#line:120
            if O000O0O00OOOOOOO0 ["time_key"]==time_key :#line:121
                return True #line:123
        O0O00O0O0O00OOO0O =public .M ('sites').field ('path').select ()#line:125
        O00OO0OOOO0O000O0 =0 #line:126
        for O0O00O0OOOOO00OOO in O0O00O0O0O00OOO0O :#line:127
            O000OO0OOO000O0O0 =O0O00O0OOOOO00OOO ["path"]#line:128
            if O000OO0OOO000O0O0 :#line:129
                O00OO0OOOO0O000O0 +=public .get_path_size (O000OO0OOO000O0O0 )#line:130
        OO0OOOO00OO00000O =public .get_path_size ("/www/server/data")#line:132
        O0O0O0O00000OO00O =public .M ("ftps").field ("path").select ()#line:134
        O0OO0O00OOO0O000O =0 #line:135
        for O0O00O0OOOOO00OOO in O0O0O0O00000OO00O :#line:136
            O0000OO00OO000O00 =O0O00O0OOOOO00OOO ["path"]#line:137
            if O0000OO00OO000O00 :#line:138
                O0OO0O00OOO0O000O +=public .get_path_size (O0000OO00OO000O00 )#line:139
        OOO0O0O000OO0000O =public .get_path_size ("/www/server/panel/plugin")#line:141
        O0O00O0OO00O0O0O0 =["/www/server/total","/www/server/btwaf","/www/server/coll","/www/server/nginx","/www/server/apache","/www/server/redis"]#line:149
        for O0OOO00OO0OOOO0O0 in O0O00O0OO00O0O0O0 :#line:150
            OOO0O0O000OO0000O +=public .get_path_size (O0OOO00OO0OOOO0O0 )#line:151
        OO0OO000OO00OO0O0 =system ().GetDiskInfo2 (human =False )#line:153
        OO000000OO00OOOOO =""#line:154
        O0OOOO00OOOOOO0O0 =0 #line:155
        O00000OO0O0OOOO0O =0 #line:156
        for OOOOOOO0O0OO000OO in OO0OO000OO00OO0O0 :#line:157
            O0O00O0000OO0O00O =OOOOOOO0O0OO000OO ["path"].replace ("-","_")#line:158
            if OO000000OO00OOOOO :#line:159
                OO000000OO00OOOOO +="-"#line:160
            O0000O0OO000OOO0O ,O0OO00OO000O0O00O ,OO00O00O000OO0000 ,O00OO00000OO0O0O0 =OOOOOOO0O0OO000OO ["size"]#line:161
            OOO0OOO00OOOOOO00 ,OOO0OO000O00OO00O ,_O0O0O0O00OOO00000 ,_OO00O00000OOOOO0O =OOOOOOO0O0OO000OO ["inodes"]#line:162
            OO000000OO00OOOOO ="{},{},{},{},{}".format (O0O00O0000OO0O00O ,O0OO00OO000O0O00O ,O0000O0OO000OOO0O ,OOO0OO000O00OO00O ,OOO0OOO00OOOOOO00 )#line:163
            if O0O00O0000OO0O00O =="/":#line:164
                O0OOOO00OOOOOO0O0 =O0000O0OO000OOO0O #line:165
                O00000OO0O0OOOO0O =O0OO00OO000O0O00O #line:166
        OO0OOO0O0000O0000 ="{},{},{},{},{},{}".format (O0OOOO00OOOOOO0O0 ,O00000OO0O0OOOO0O ,O00OO0OOOO0O000O0 ,OO0OOOO00OO00000O ,O0OO0O00OOO0O000O ,OOO0O0O000OO0000O )#line:171
        OO0OOO0OOOOO0O000 =public .M ("system").dbfile ("system").table ("app_usage").add ("time_key,app,disks",(time_key ,OO0OOO0O0000O0000 ,OO000000OO00OOOOO ))#line:173
        if OO0OOO0OOOOO0O000 ==time_key :#line:174
            return True #line:175
        return False #line:178
    def parse_char_unit (O0OOO0OOOO00OOO0O ,OOO00000OOOOO0O0O ):#line:180
        O0O0O0OO00O00O0OO =0 #line:181
        try :#line:182
            O0O0O0OO00O00O0OO =float (OOO00000OOOOO0O0O )#line:183
        except :#line:184
            OOO000O0O0O0OO000 =OOO00000OOOOO0O0O #line:185
            if OOO000O0O0O0OO000 .find ("G")!=-1 :#line:186
                OOO000O0O0O0OO000 =OOO000O0O0O0OO000 .replace ("G","")#line:187
                O0O0O0OO00O00O0OO =float (OOO000O0O0O0OO000 )*1024 *1024 *1024 #line:188
            elif OOO000O0O0O0OO000 .find ("M")!=-1 :#line:189
                OOO000O0O0O0OO000 =OOO000O0O0O0OO000 .replace ("M","")#line:190
                O0O0O0OO00O00O0OO =float (OOO000O0O0O0OO000 )*1024 *1024 #line:191
            else :#line:192
                O0O0O0OO00O00O0OO =float (OOO000O0O0O0OO000 )#line:193
        return O0O0O0OO00O00O0OO #line:194
    def parse_app_usage_info (OO00OO0OOOOOOO0O0 ,OO0O000O00O00OOO0 ):#line:196
        ""#line:197
        if not OO0O000O00O00OOO0 :#line:198
            return {}#line:199
        print (OO0O000O00O00OOO0 )#line:200
        O0O0O0OO0OO000OO0 ,O0OOO0OO0000O00O0 ,OO0O00OOOO0O00OO0 ,OO00OOOOOO0OOO000 ,OOO0OOO00000000O0 ,O000O0OOO0000OO00 =OO0O000O00O00OOO0 ["app"].split (",")#line:201
        OOOOOO0O0O000O0O0 =OO0O000O00O00OOO0 ["disks"].split ("-")#line:202
        OOOO0OO000000OOOO ={}#line:203
        print ("disk tmp:")#line:204
        print (OOOOOO0O0O000O0O0 )#line:205
        for O0OO0OO000OO0O0O0 in OOOOOO0O0O000O0O0 :#line:206
            print (O0OO0OO000OO0O0O0 )#line:207
            O0OOOOOOOOOOOO0OO ,O00O00O0OOO000OOO ,OOOOO0OOOO0000OOO ,OO0OOOO0O000OOOO0 ,OOO000O0000OO0O00 =O0OO0OO000OO0O0O0 .split (",")#line:208
            OO00OOOO0OO00OO0O ={}#line:209
            OO00OOOO0OO00OO0O ["usage"]=OO00OO0OOOOOOO0O0 .parse_char_unit (O00O00O0OOO000OOO )#line:210
            OO00OOOO0OO00OO0O ["total"]=OO00OO0OOOOOOO0O0 .parse_char_unit (OOOOO0OOOO0000OOO )#line:211
            OO00OOOO0OO00OO0O ["iusage"]=OO0OOOO0O000OOOO0 #line:212
            OO00OOOO0OO00OO0O ["itotal"]=OOO000O0000OO0O00 #line:213
            OOOO0OO000000OOOO [O0OOOOOOOOOOOO0OO ]=OO00OOOO0OO00OO0O #line:214
        return {"apps":{"disk_total":O0O0O0OO0OO000OO0 ,"disk_usage":O0OOO0OO0000O00O0 ,"sites":OO0O00OOOO0O00OO0 ,"databases":OO00OOOOOO0OOO000 ,"ftps":OOO0OOO00000000O0 ,"plugins":O000O0OOO0000OO00 },"disks":OOOO0OO000000OOOO }#line:225
    def get_app_usage (OOO0O0OOO00000OO0 ,O0O0OOO00000OOO00 ):#line:227
        OOO0O00O00OO00000 =time .localtime ()#line:229
        O0O000O00OOO0000O =OOO0O0OOO00000OO0 .get_time_key ()#line:230
        OOOO000OOOO00O000 =time .localtime (time .mktime ((OOO0O00O00OO00000 .tm_year ,OOO0O00O00OO00000 .tm_mon ,OOO0O00O00OO00000 .tm_mday -1 ,0 ,0 ,0 ,0 ,0 ,0 )))#line:233
        O0000OO00OOO00OO0 =OOO0O0OOO00000OO0 .get_time_key (OOOO000OOOO00O000 )#line:234
        OO00OOO0OO00000OO =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key =? or time_key=?",(O0O000O00OOO0000O ,O0000OO00OOO00OO0 ))#line:236
        OO0000O0OO0O0O00O =OO00OOO0OO00000OO .select ()#line:237
        if type (OO0000O0OO0O0O00O )==str or not OO0000O0OO0O0O00O :#line:240
            return {}#line:241
        O000OOOO0000OO0O0 ={}#line:242
        OOO0O000OO0OOO0O0 ={}#line:243
        for O0OOO00000OO0OOO0 in OO0000O0OO0O0O00O :#line:244
            if O0OOO00000OO0OOO0 ["time_key"]==O0O000O00OOO0000O :#line:245
                O000OOOO0000OO0O0 =OOO0O0OOO00000OO0 .parse_app_usage_info (O0OOO00000OO0OOO0 )#line:246
            if O0OOO00000OO0OOO0 ["time_key"]==O0000OO00OOO00OO0 :#line:247
                OOO0O000OO0OOO0O0 =OOO0O0OOO00000OO0 .parse_app_usage_info (O0OOO00000OO0OOO0 )#line:248
        if not O000OOOO0000OO0O0 :#line:250
            return {}#line:251
        for OOOO0OOOOO0OO0O0O ,O0O00OO00OO0000OO in O000OOOO0000OO0O0 ["disks"].items ():#line:254
            O0OOO00O0000000O0 =int (O0O00OO00OO0000OO ["total"])#line:255
            O0OO00O0O0000OOOO =int (O0O00OO00OO0000OO ["usage"])#line:256
            O0000O0O0OOOO0000 =int (O0O00OO00OO0000OO ["itotal"])#line:258
            O0OOOOO000OOO00OO =int (O0O00OO00OO0000OO ["iusage"])#line:259
            if OOO0O000OO0OOO0O0 and OOOO0OOOOO0OO0O0O in OOO0O000OO0OOO0O0 ["disks"].keys ():#line:261
                O0000OO0OO000O0O0 =OOO0O000OO0OOO0O0 ["disks"]#line:262
                OO000OO0O0O000O00 =O0000OO0OO000O0O0 [OOOO0OOOOO0OO0O0O ]#line:263
                OOOO00O0OOOO000OO =int (OO000OO0O0O000O00 ["total"])#line:264
                if OOOO00O0OOOO000OO ==O0OOO00O0000000O0 :#line:265
                    O0000O00O0000O0OO =int (OO000OO0O0O000O00 ["usage"])#line:266
                    O0OO0OOO0000OOOO0 =0 #line:267
                    O0OOO000O000O0O00 =O0OO00O0O0000OOOO -O0000O00O0000O0OO #line:268
                    if O0OOO000O000O0O00 >0 :#line:269
                        O0OO0OOO0000OOOO0 =round (O0OOO000O000O0O00 /O0OOO00O0000000O0 ,2 )#line:270
                    O0O00OO00OO0000OO ["incr"]=O0OO0OOO0000OOOO0 #line:271
                O00OO0OO00O0O0O00 =int (OO000OO0O0O000O00 ["itotal"])#line:274
                if True :#line:275
                    O00OO0O000OO0O000 =int (OO000OO0O0O000O00 ["iusage"])#line:276
                    OOOO0O0O00OOO00OO =0 #line:277
                    O0OOO000O000O0O00 =O0OOOOO000OOO00OO -O00OO0O000OO0O000 #line:278
                    if O0OOO000O000O0O00 >0 :#line:279
                        OOOO0O0O00OOO00OO =round (O0OOO000O000O0O00 /O0000O0O0OOOO0000 ,2 )#line:280
                    O0O00OO00OO0000OO ["iincr"]=OOOO0O0O00OOO00OO #line:281
        OO0O000OOOOO0OOO0 =O000OOOO0000OO0O0 ["apps"]#line:285
        OOOOOO000000OO00O =int (OO0O000OOOOO0OOO0 ["disk_total"])#line:286
        if OOO0O000OO0OOO0O0 and OOO0O000OO0OOO0O0 ["apps"]["disk_total"]==OO0O000OOOOO0OOO0 ["disk_total"]:#line:287
            OO00O0OO000000000 =OOO0O000OO0OOO0O0 ["apps"]#line:288
            for O00OOOO0O00OO00OO ,OO0OO00O000OOOOO0 in OO0O000OOOOO0OOO0 .items ():#line:289
                if O00OOOO0O00OO00OO =="disks":continue #line:290
                if O00OOOO0O00OO00OO =="disk_total":continue #line:291
                if O00OOOO0O00OO00OO =="disk_usage":continue #line:292
                OOOOOOO0OO000OO00 =0 #line:293
                OOOOOO00O0O0O0OOO =int (OO0OO00O000OOOOO0 )-int (OO00O0OO000000000 [O00OOOO0O00OO00OO ])#line:294
                if OOOOOO00O0O0O0OOO >0 :#line:295
                    OOOOOOO0OO000OO00 =round (OOOOOO00O0O0O0OOO /OOOOOO000000OO00O ,2 )#line:296
                OO0O000OOOOO0OOO0 [O00OOOO0O00OO00OO ]={"val":OO0OO00O000OOOOO0 ,"incr":OOOOOOO0OO000OO00 }#line:301
        return O000OOOO0000OO0O0 #line:302
    def get_timestamp_interval (OO000O00OO0O0O00O ,O00OO000OOO000OOO ):#line:304
        O0O0O0O00000O00OO =None #line:305
        O000000O0OOO0OO00 =None #line:306
        O0O0O0O00000O00OO =time .mktime ((O00OO000OOO000OOO .tm_year ,O00OO000OOO000OOO .tm_mon ,O00OO000OOO000OOO .tm_mday ,0 ,0 ,0 ,0 ,0 ,0 ))#line:308
        O000000O0OOO0OO00 =time .mktime ((O00OO000OOO000OOO .tm_year ,O00OO000OOO000OOO .tm_mon ,O00OO000OOO000OOO .tm_mday ,23 ,59 ,59 ,0 ,0 ,0 ))#line:310
        return O0O0O0O00000O00OO ,O000000O0OOO0OO00 #line:311
    def check_server (OOOOOOOO000000O0O ):#line:314
        try :#line:315
            OO0OO0OO0OOOO0OO0 =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:318
            O0OOO0O000OO0000O =panelPlugin ()#line:319
            OO0000O0O00000000 =public .dict_obj ()#line:320
            OO0OOOOO0O00OOO00 =""#line:321
            for O00O00000OO00O00O in OO0OO0OO0OOOO0OO0 :#line:322
                OOO0000O00OO000O0 =False #line:323
                OOOO0OOOO00000OOO =False #line:324
                OO0000O0O00000000 .name =O00O00000OO00O00O #line:325
                OOOOO00000O0O0OO0 =O0OOO0O000OO0000O .getPluginInfo (OO0000O0O00000000 )#line:326
                if not OOOOO00000O0O0OO0 :#line:327
                    continue #line:328
                O0000000OOOO0O000 =OOOOO00000O0O0OO0 ["versions"]#line:329
                for O0OO000O0O0O0000O in O0000000OOOO0O000 :#line:331
                    if O0OO000O0O0O0000O ["status"]:#line:334
                        OOOO0OOOO00000OOO =True #line:335
                    if "run"in O0OO000O0O0O0000O .keys ()and O0OO000O0O0O0000O ["run"]:#line:336
                        OOOO0OOOO00000OOO =True #line:338
                        OOO0000O00OO000O0 =True #line:339
                        break #line:340
                OOO0OOOOOO00OOO00 =0 #line:341
                if OOOO0OOOO00000OOO :#line:342
                    OOO0OOOOOO00OOO00 =1 #line:343
                    if not OOO0000O00OO000O0 :#line:345
                        OOO0OOOOOO00OOO00 =2 #line:346
                OO0OOOOO0O00OOO00 +=str (OOO0OOOOOO00OOO00 )#line:347
            if '2'in OO0OOOOO0O00OOO00 :#line:351
                public .M ("system").dbfile ("server_status").add ("status, addtime",(OO0OOOOO0O00OOO00 ,time .time ()))#line:353
        except Exception as OO0OOOO0O000OOOOO :#line:354
            return True #line:356
    def get_daily_data (O00000O00O00OOO0O ,OOO00OOO00O0OO00O ):#line:358
        ""#line:359
        OO00O0000000OO0OO ="IS_PRO_OR_LTD_FOR_PANEL_DAILY"#line:361
        OOOO0O00O0OOOO000 =cache .get (OO00O0000000OO0OO )#line:362
        if not OOOO0O00O0OOOO000 :#line:363
            try :#line:364
                OOO00OO00OO0O000O =panelPlugin ()#line:365
                OOOO000OOOOO0000O =OOO00OO00OO0O000O .get_soft_list (OOO00OOO00O0OO00O )#line:366
                if OOOO000OOOOO0000O ["pro"]<0 and OOOO000OOOOO0000O ["ltd"]<0 :#line:367
                    if os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:368
                        os .remove ("/www/server/panel/data/start_daily.pl")#line:369
                    return {"status":False ,"msg":"No authorization.","data":[],"date":OOO00OOO00O0OO00O .date }#line:375
                cache .set (OO00O0000000OO0OO ,True ,86400 )#line:376
            except :#line:377
                return {"status":False ,"msg":"获取不到授权信息，请检查网络是否正常","data":[],"date":OOO00OOO00O0OO00O .date }#line:383
        if not os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:386
            public .writeFile ("/www/server/panel/data/start_daily.pl",OOO00OOO00O0OO00O .date )#line:387
        return O00000O00O00OOO0O .get_daily_data_local (OOO00OOO00O0OO00O .date )#line:388
    def get_daily_data_local (OO0OOOOOO0000OO0O ,O00O0O00OO00OOOOO ):#line:390
        O00O0O0OOO0OO000O =time .strptime (O00O0O00OO00OOOOO ,"%Y%m%d")#line:391
        O0O00OO0O0O0000OO =OO0OOOOOO0000OO0O .get_time_key (O00O0O0OOO0OO000O )#line:392
        OO0OOOOOO0000OO0O .check_databases ()#line:394
        OO0O00O00OO00000O =time .strftime ("%Y-%m-%d",O00O0O0OOO0OO000O )#line:396
        O0OOO0O000OOOO000 =0 #line:397
        OOO0O0OO0OO00O0OO ,OOOOOO000OOO000O0 =OO0OOOOOO0000OO0O .get_timestamp_interval (O00O0O0OOO0OO000O )#line:398
        OO0OO0OOO0OOO00O0 =public .M ("system").dbfile ("system")#line:399
        OO0O0O0OOO0O0O00O =OO0OO0OOO0OOO00O0 .table ("process_high_percent")#line:400
        OOOO000O0O0O0OOOO =OO0O0O0OOO0O0O00O .where ("addtime>=? and addtime<=?",(OOO0O0OO0OO00O0OO ,OOOOOO000OOO000O0 )).order ("addtime").select ()#line:401
        O000OO00O0O0OOO00 =[]#line:405
        if len (OOOO000O0O0O0OOOO )>0 :#line:406
            for O0000O000O0O00OO0 in OOOO000O0O0O0OOOO :#line:408
                OO00O00O00O0O000O =int (O0000O000O0O00OO0 ["cpu_percent"])#line:410
                if OO00O00O00O0O000O >=80 :#line:411
                    O000OO00O0O0OOO00 .append ({"time":O0000O000O0O00OO0 ["addtime"],"name":O0000O000O0O00OO0 ["name"],"pid":O0000O000O0O00OO0 ["pid"],"percent":OO00O00O00O0O000O })#line:419
        O0OO0000OOO00O00O =len (O000OO00O0O0OOO00 )#line:421
        O0O00OOOO000OOOOO =0 #line:422
        O0OOO0O0O00O00OO0 =""#line:423
        if O0OO0000OOO00O00O ==0 :#line:424
            O0O00OOOO000OOOOO =20 #line:425
        else :#line:426
            O0OOO0O0O00O00OO0 ="CPU出现过载情况"#line:427
        O00O00O0O00000OOO ={"ex":O0OO0000OOO00O00O ,"detail":O000OO00O0O0OOO00 }#line:431
        OOOOOO00OOOO00000 =[]#line:434
        if len (OOOO000O0O0O0OOOO )>0 :#line:435
            for O0000O000O0O00OO0 in OOOO000O0O0O0OOOO :#line:437
                OO0O0O000OO0000OO =float (O0000O000O0O00OO0 ["memory"])#line:439
                OOO000O0OO0OOOOOO =psutil .virtual_memory ().total #line:440
                OOO000OOO0O000000 =round (100 *OO0O0O000OO0000OO /OOO000O0OO0OOOOOO ,2 )#line:441
                if OOO000OOO0O000000 >=80 :#line:442
                    OOOOOO00OOOO00000 .append ({"time":O0000O000O0O00OO0 ["addtime"],"name":O0000O000O0O00OO0 ["name"],"pid":O0000O000O0O00OO0 ["pid"],"percent":OOO000OOO0O000000 })#line:450
        O0O00O0OOO00OOO0O =len (OOOOOO00OOOO00000 )#line:451
        OOOOOO0000OOO00OO =""#line:452
        O0OOO0O00OO00000O =0 #line:453
        if O0O00O0OOO00OOO0O ==0 :#line:454
            O0OOO0O00OO00000O =20 #line:455
        else :#line:456
            if O0O00O0OOO00OOO0O >1 :#line:457
                OOOOOO0000OOO00OO ="内存在多个时间点出现占用80%"#line:458
            else :#line:459
                OOOOOO0000OOO00OO ="内存出现占用超过80%"#line:460
        OOOOOO0O000OO00OO ={"ex":O0O00O0OOO00OOO0O ,"detail":OOOOOO00OOOO00000 }#line:464
        OO0OO0O00OOOO000O =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key=?",(O0O00OO0O0O0000OO ,))#line:468
        O0O0OO00OO00OOOOO =OO0OO0O00OOOO000O .select ()#line:469
        O0OO0O0O0OO00O000 ={}#line:470
        if O0O0OO00OO00OOOOO and type (O0O0OO00OO00OOOOO )!=str :#line:471
            O0OO0O0O0OO00O000 =OO0OOOOOO0000OO0O .parse_app_usage_info (O0O0OO00OO00OOOOO [0 ])#line:472
        O00OO0OOO000O00O0 =[]#line:473
        if O0OO0O0O0OO00O000 :#line:474
            OO0O0000O00O00000 =O0OO0O0O0OO00O000 ["disks"]#line:475
            for O00O0OO0OOO0000OO ,OO000OOOOO000000O in OO0O0000O00O00000 .items ():#line:476
                O0OO0OO0OO0O0OOOO =int (OO000OOOOO000000O ["usage"])#line:477
                OOO000O0OO0OOOOOO =int (OO000OOOOO000000O ["total"])#line:478
                O0OOOO00OOO0OOOOO =round (O0OO0OO0OO0O0OOOO /OOO000O0OO0OOOOOO ,2 )#line:479
                OOO0000OO00000OOO =int (OO000OOOOO000000O ["iusage"])#line:480
                O00OO00OO0O000OOO =int (OO000OOOOO000000O ["itotal"])#line:481
                if O00OO00OO0O000OOO >0 :#line:482
                    O00OO0OO0000O00OO =round (OOO0000OO00000OOO /O00OO00OO0O000OOO ,2 )#line:483
                else :#line:484
                    O00OO0OO0000O00OO =0 #line:485
                if O0OOOO00OOO0OOOOO >=0.8 :#line:489
                    O00OO0OOO000O00O0 .append ({"name":O00O0OO0OOO0000OO ,"percent":O0OOOO00OOO0OOOOO *100 ,"ipercent":O00OO0OO0000O00OO *100 ,"usage":O0OO0OO0OO0O0OOOO ,"total":OOO000O0OO0OOOOOO ,"iusage":OOO0000OO00000OOO ,"itotal":O00OO00OO0O000OOO })#line:498
        OO0O000000000O0O0 =len (O00OO0OOO000O00O0 )#line:500
        O0O000O0000O000OO =""#line:501
        O000O0OO0000OO0O0 =0 #line:502
        if OO0O000000000O0O0 ==0 :#line:503
            O000O0OO0000OO0O0 =20 #line:504
        else :#line:505
            O0O000O0000O000OO ="有磁盘空间占用已经超过80%"#line:506
        O0OO0OO000O0OO00O ={"ex":OO0O000000000O0O0 ,"detail":O00OO0OOO000O00O0 }#line:511
        OO00000O000O000O0 =public .M ("system").dbfile ("system").table ("server_status").where ("addtime>=? and addtime<=?",(OOO0O0OO0OO00O0OO ,OOOOOO000OOO000O0 ,)).order ("addtime desc").select ()#line:515
        OOOO00OOOOO0O0O0O =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:520
        O0O0O0OOO000000OO ={}#line:522
        OO0OO0000O0000000 =0 #line:523
        OOO000O0O0O0OO0OO =""#line:524
        for O0O00OO0OO00O0OO0 ,OO0OOO000OOOO0OO0 in enumerate (OOOO00OOOOO0O0O0O ):#line:525
            if OO0OOO000OOOO0OO0 =="pure-ftpd":#line:526
                OO0OOO000OOOO0OO0 ="ftpd"#line:527
            OO0O000OO00OO00O0 =0 #line:528
            OO00O0000O0OOOOOO =[]#line:529
            for OOOO0O0OOO0OOO0OO in OO00000O000O000O0 :#line:530
                _O0OOO0O0O0OOO00OO =OOOO0O0OOO0OOO0OO ["status"]#line:533
                if O0O00OO0OO00O0OO0 <len (_O0OOO0O0O0OOO00OO ):#line:534
                    if _O0OOO0O0O0OOO00OO [O0O00OO0OO00O0OO0 ]=="2":#line:535
                        OO00O0000O0OOOOOO .append ({"time":OOOO0O0OOO0OOO0OO ["addtime"],"desc":"退出"})#line:536
                        OO0O000OO00OO00O0 +=1 #line:537
                        OO0OO0000O0000000 +=1 #line:538
            O0O0O0OOO000000OO [OO0OOO000OOOO0OO0 ]={"ex":OO0O000OO00OO00O0 ,"detail":OO00O0000O0OOOOOO }#line:543
        O0OO000O0OOO00OO0 =0 #line:545
        if OO0OO0000O0000000 ==0 :#line:546
            O0OO000O0OOO00OO0 =20 #line:547
        else :#line:548
            OOO000O0O0O0OO0OO ="系统级服务有出现异常退出情况"#line:549
        OO0OOOOO000000OOO =public .M ("crontab").field ("name,sName,sType").where ("sType in (?, ?, ?)",("database","enterpriseBackup","site",)).select ()#line:553
        OOOOO0OOO0O0000OO =set ()#line:556
        for OO000OOOO00O00O0O in OO0OOOOO000000OOO :#line:557
            if OO000OOOO00O00O0O ["sType"]=="database":#line:558
                OOOOO0OOO0O0000OO .add (OO000OOOO00O00O0O ["sName"])#line:559
            elif OO000OOOO00O00O0O ["sType"]=="enterpriseBackup":#line:560
                O0000OO000O00O000 =OO000OOOO00O00O0O ["name"]#line:561
                O0OOOO0O0O00O0OOO =O0000OO000O00O000 [O0000OO000O00O000 .rfind ("[")+1 :O0000OO000O00O000 .rfind ("]")]#line:562
                OOOOO0OOO0O0000OO .add (O0OOOO0O0O00O0OOO )#line:563
        OOO00O000OOOOO0O0 ="ALL"in OOOOO0OOO0O0000OO #line:567
        OO0OOOOO00O0OO0O0 =set (OO0O000000OO0OO0O ["sName"]for OO0O000000OO0OO0O in OO0OOOOO000000OOO if OO0O000000OO0OO0O ["sType"]=="site")#line:568
        O00O0OOO000O00O0O ="ALL"in OO0OOOOO00O0OO0O0 #line:569
        OOOO00O0000O0OOOO =[]#line:570
        O0O0OO0OO0O0O0000 =[]#line:571
        if not OOO00O000OOOOO0O0 :#line:572
            OOOOOO000OO0OOOOO =public .M ("databases").field ("name").select ()#line:573
            for OOO00O00000OOOO0O in OOOOOO000OO0OOOOO :#line:574
                OOO0000O00OOOO00O =OOO00O00000OOOO0O ["name"]#line:575
                if OOO0000O00OOOO00O not in OOOOO0OOO0O0000OO :#line:576
                    OOOO00O0000O0OOOO .append ({"name":OOO0000O00OOOO00O })#line:577
        if not O00O0OOO000O00O0O :#line:579
            O0OO00000O0O00OO0 =public .M ("sites").field ("name").select ()#line:580
            for O0O0O00O000OO0OOO in O0OO00000O0O00OO0 :#line:581
                O0OO00O0000OOO0O0 =O0O0O00O000OO0OOO ["name"]#line:582
                if O0OO00O0000OOO0O0 not in OO0OOOOO00O0OO0O0 :#line:583
                    O0O0OO0OO0O0O0000 .append ({"name":O0OO00O0000OOO0O0 })#line:584
        O00000O0OOOOO0OOO =public .M ("system").dbfile ("system").table ("backup_status").where ("addtime>=? and addtime<=?",(OOO0O0OO0OO00O0OO ,OOOOOO000OOO000O0 )).select ()#line:587
        O000O0O0O0000OOO0 ={"database":{"no_backup":OOOO00O0000O0OOOO ,"backup":[]},"site":{"no_backup":O0O0OO0OO0O0O0000 ,"backup":[]},"path":{"no_backup":[],"backup":[]}}#line:602
        O000O000000O00OOO =0 #line:603
        for O0O000OO000OO00O0 in O00000O0OOOOO0OOO :#line:604
            O00OO0OOOOO000OO0 =O0O000OO000OO00O0 ["status"]#line:605
            if O00OO0OOOOO000OO0 :#line:606
                continue #line:607
            O000O000000O00OOO +=1 #line:609
            O0OO000000O0O0O0O =O0O000OO000OO00O0 ["id"]#line:610
            OO000OO00O00OOO00 =public .M ("crontab").where ("id=?",(O0OO000000O0O0O0O )).find ()#line:611
            if not OO000OO00O00OOO00 :#line:612
                continue #line:613
            O0O00OOO000O00OOO =OO000OO00O00OOO00 ["sType"]#line:614
            if not O0O00OOO000O00OOO :#line:615
                continue #line:616
            O0OOOO0O0O00O0OOO =OO000OO00O00OOO00 ["name"]#line:617
            OOOOOO0OOO0000000 =O0O000OO000OO00O0 ["addtime"]#line:618
            OO000O00OO0000OO0 =O0O000OO000OO00O0 ["target"]#line:619
            if O0O00OOO000O00OOO not in O000O0O0O0000OOO0 .keys ():#line:620
                O000O0O0O0000OOO0 [O0O00OOO000O00OOO ]={}#line:621
                O000O0O0O0000OOO0 [O0O00OOO000O00OOO ]["backup"]=[]#line:622
                O000O0O0O0000OOO0 [O0O00OOO000O00OOO ]["no_backup"]=[]#line:623
            O000O0O0O0000OOO0 [O0O00OOO000O00OOO ]["backup"].append ({"name":O0OOOO0O0O00O0OOO ,"target":OO000O00OO0000OO0 ,"status":O00OO0OOOOO000OO0 ,"target":OO000O00OO0000OO0 ,"time":OOOOOO0OOO0000000 })#line:630
        OO0O0OO00OOO0OO0O =""#line:632
        O000O000OO00OO000 =0 #line:633
        if O000O000000O00OOO ==0 :#line:634
            O000O000OO00OO000 =20 #line:635
        else :#line:636
            OO0O0OO00OOO0OO0O ="有计划任务备份失败"#line:637
        if len (OOOO00O0000O0OOOO )==0 :#line:639
            O000O000OO00OO000 +=10 #line:640
        else :#line:641
            if OO0O0OO00OOO0OO0O :#line:642
                OO0O0OO00OOO0OO0O +=";"#line:643
            OO0O0OO00OOO0OO0O +="有数据库未及时备份"#line:644
        if len (O0O0OO0OO0O0O0000 )==0 :#line:646
            O000O000OO00OO000 +=10 #line:647
        else :#line:648
            if OO0O0OO00OOO0OO0O :#line:649
                OO0O0OO00OOO0OO0O +=";"#line:650
            OO0O0OO00OOO0OO0O +="有网站未备份"#line:651
        O0OOOO0O00O000OO0 =0 #line:654
        O0O0000O0O0OO000O =public .M ('logs').where ('addtime like ? and type=?',(str (OO0O00O00OO00000O )+"%",'用户登录',)).select ()#line:655
        OOO0OO000OO00O000 =[]#line:656
        if O0O0000O0O0OO000O and type (O0O0000O0O0OO000O )==list :#line:657
            for OOOO0O00OO000000O in O0O0000O0O0OO000O :#line:658
                OOOOO00000OO0O00O =OOOO0O00OO000000O ["log"]#line:659
                if OOOOO00000OO0O00O .find ("失败")>=0 or OOOOO00000OO0O00O .find ("错误")>=0 :#line:660
                    O0OOOO0O00O000OO0 +=1 #line:661
                    OOO0OO000OO00O000 .append ({"time":time .mktime (time .strptime (OOOO0O00OO000000O ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":OOOO0O00OO000000O ["log"],"username":OOOO0O00OO000000O ["username"],})#line:666
            OOO0OO000OO00O000 .sort (key =lambda O0OOOOOOO0OO0OOOO :O0OOOOOOO0OO0OOOO ["time"])#line:667
        OO00OOOOOO0O000OO =public .M ('logs').where ('type=?',('SSH安全',)).where ("addtime like ?",(str (OO0O00O00OO00000O )+"%",)).select ()#line:669
        OO0OOO0OOO0000OOO =[]#line:671
        O0O000000O0O0O0OO =0 #line:672
        if OO00OOOOOO0O000OO :#line:673
            for OOOO0O00OO000000O in OO00OOOOOO0O000OO :#line:674
                OOOOO00000OO0O00O =OOOO0O00OO000000O ["log"]#line:675
                if OOOOO00000OO0O00O .find ("存在异常")>=0 :#line:676
                    O0O000000O0O0O0OO +=1 #line:677
                    OO0OOO0OOO0000OOO .append ({"time":time .mktime (time .strptime (OOOO0O00OO000000O ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":OOOO0O00OO000000O ["log"],"username":OOOO0O00OO000000O ["username"]})#line:682
            OO0OOO0OOO0000OOO .sort (key =lambda O0OOOO000O00O0000 :O0OOOO000O00O0000 ["time"])#line:683
        O00O0O0O0O00O0OOO =""#line:685
        O0000O00000OOO0OO =0 #line:686
        if O0O000000O0O0O0OO ==0 :#line:687
            O0000O00000OOO0OO =10 #line:688
        else :#line:689
            O00O0O0O0O00O0OOO ="SSH有异常登录"#line:690
        if O0OOOO0O00O000OO0 ==0 :#line:692
            O0000O00000OOO0OO +=10 #line:693
        else :#line:694
            if O0OOOO0O00O000OO0 >10 :#line:695
                O0000O00000OOO0OO -=10 #line:696
            if O00O0O0O0O00O0OOO :#line:697
                O00O0O0O0O00O0OOO +=";"#line:698
            O00O0O0O0O00O0OOO +="面板登录有错误".format (O0OOOO0O00O000OO0 )#line:699
        OO00000O000O000O0 ={"panel":{"ex":O0OOOO0O00O000OO0 ,"detail":OOO0OO000OO00O000 },"ssh":{"ex":O0O000000O0O0O0OO ,"detail":OO0OOO0OOO0000OOO }}#line:709
        O0OOO0O000OOOO000 =O0O00OOOO000OOOOO +O0OOO0O00OO00000O +O000O0OO0000OO0O0 +O0OO000O0OOO00OO0 +O000O000OO00OO000 +O0000O00000OOO0OO #line:711
        O0OO000O00OOOO00O =[O0OOO0O0O00O00OO0 ,OOOOOO0000OOO00OO ,O0O000O0000O000OO ,OOO000O0O0O0OO0OO ,OO0O0OO00OOO0OO0O ,O00O0O0O0O00O0OOO ]#line:712
        OO0O00OO0OOO0O00O =[]#line:713
        for O00O0OOO000O00000 in O0OO000O00OOOO00O :#line:714
            if O00O0OOO000O00000 :#line:715
                if O00O0OOO000O00000 .find (";")>=0 :#line:716
                    for OO0O0OO0O00OOO0O0 in O00O0OOO000O00000 .split (";"):#line:717
                        OO0O00OO0OOO0O00O .append (OO0O0OO0O00OOO0O0 )#line:718
                else :#line:719
                    OO0O00OO0OOO0O00O .append (O00O0OOO000O00000 )#line:720
        if not OO0O00OO0OOO0O00O :#line:722
            OO0O00OO0OOO0O00O .append ("服务器运行正常，请继续保持！")#line:723
        O00OOO0OOO0000000 =OO0OOOOOO0000OO0O .evaluate (O0OOO0O000OOOO000 )#line:727
        return {"data":{"cpu":O00O00O0O00000OOO ,"ram":OOOOOO0O000OO00OO ,"disk":O0OO0OO000O0OO00O ,"server":O0O0O0OOO000000OO ,"backup":O000O0O0O0000OOO0 ,"exception":OO00000O000O000O0 ,},"evaluate":O00OOO0OOO0000000 ,"score":O0OOO0O000OOOO000 ,"date":O0O00OO0O0O0000OO ,"summary":OO0O00OO0OOO0O00O ,"status":True }#line:744
    def evaluate (OO0OO0O0O00OOOOO0 ,O0000O0OO00O00000 ):#line:746
        OO00O00000OOOO0O0 =""#line:747
        if O0000O0OO00O00000 >=100 :#line:748
            OO00O00000OOOO0O0 ="正常"#line:749
        elif O0000O0OO00O00000 >=80 :#line:750
            OO00O00000OOOO0O0 ="良好"#line:751
        else :#line:752
            OO00O00000OOOO0O0 ="一般"#line:753
        return OO00O00000OOOO0O0 #line:754
    def get_daily_list (O0O0O00O0000O0O00 ,OOOO00OO00000O0OO ):#line:756
        OOO00OO0000OOOO00 =public .M ("system").dbfile ("system").table ("daily").where ("time_key>?",0 ).select ()#line:757
        OOO000OOO00OO0O0O =[]#line:758
        for O0OOO00OO00O0OO00 in OOO00OO0000OOOO00 :#line:759
            O0OOO00OO00O0OO00 ["evaluate"]=O0O0O00O0000O0O00 .evaluate (O0OOO00OO00O0OO00 ["evaluate"])#line:760
            OOO000OOO00OO0O0O .append (O0OOO00OO00O0OO00 )#line:761
        return OOO000OOO00OO0O0O 