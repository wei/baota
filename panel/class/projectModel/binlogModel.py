import os ,sys ,time ,json ,re ,datetime ,shutil ,threading #line:13
os .chdir ('/www/server/panel')#line:14
sys .path .append ("class/")#line:15
import public #line:16
from projectModel .base import projectBase #line:17
from panelMysql import panelMysql #line:18
from panelBackup import backup #line:19
import db_mysql #line:20
try :#line:21
    import oss2 #line:22
    from qcloud_cos import CosConfig #line:23
    from qcloud_cos import CosS3Client #line:24
    from qiniu import Auth ,put_file ,etag #line:25
    from baidubce .bce_client_configuration import BceClientConfiguration #line:26
    from baidubce .auth .bce_credentials import BceCredentials #line:27
    from baidubce .services .bos .bos_client import BosClient #line:28
    from obs import ObsClient #line:29
except :#line:30
    os .system ('btpip install oss2==2.5.0')#line:31
    os .system ('btpip install cos-python-sdk-v5==1.7.7')#line:33
    os .system ('btpip install qiniu==7.4.1 -I')#line:35
    os .system ('btpip install bce-python-sdk==0.8.62')#line:37
    os .system ('btpip install esdk-obs-python==3.21.8 --trusted-host pypi.org')#line:40
    import oss2 #line:42
    from qcloud_cos import CosConfig #line:43
    from qcloud_cos import CosS3Client #line:44
    from qiniu import Auth ,put_file ,etag #line:45
    from baidubce .bce_client_configuration import BceClientConfiguration #line:46
    from baidubce .auth .bce_credentials import BceCredentials #line:47
    from baidubce .services .bos .bos_client import BosClient #line:48
    from obs import ObsClient #line:49
class main (projectBase ):#line:50
    _setup_path ='/www/server/panel/'#line:51
    _binlog_id =''#line:52
    _db_name =''#line:53
    _zip_password =''#line:54
    _backup_end_time =''#line:55
    _backup_start_time =''#line:56
    _backup_type =''#line:57
    _cloud_name =''#line:58
    _full_zip_name =''#line:59
    _full_file =''#line:60
    _inc_file =''#line:61
    _file =''#line:62
    _pdata ={}#line:63
    _echo_info ={}#line:64
    _inode_min =100 #line:65
    _temp_path ='./temp/'#line:66
    _tables =[]#line:67
    _new_tables =[]#line:68
    _backup_fail_list =[]#line:69
    _backup_full_list =[]#line:70
    _cloud_upload_not =[]#line:71
    _full_info =[]#line:72
    _inc_info =[]#line:73
    _mysql_bin_index ='/www/server/data/mysql-bin.index'#line:74
    _save_cycle =3600 #line:75
    _compress =True #line:76
    _mysqlbinlog_bin ='/www/server/mysql/bin/mysqlbinlog'#line:77
    _save_default_path ='/www/backup/mysql_bin_log/'#line:78
    _mysql_root_password =public .M ('config').where ('id=?',(1 ,)).getField ('mysql_root')#line:79
    _config_path ='{}config/mysqlbinlog_info'.format (_setup_path )#line:80
    _python_path ='{}pyenv/bin/python'.format (_setup_path )#line:81
    _binlogModel_py ='{}class/projectModel/binlogModel.py'.format (_setup_path )#line:82
    _mybackup =backup ()#line:83
    _plugin_path ='{}plugin/'.format (_setup_path )#line:84
    _binlog_conf ='{}config/mysqlbinlog_info/binlog.conf'.format (_setup_path )#line:85
    _start_time_list =[]#line:86
    _db_mysql =db_mysql .panelMysql ()#line:87
    def __init__ (O0O0OOOOO0OO000OO ):#line:90
        if not os .path .exists (O0O0OOOOO0OO000OO ._save_default_path ):#line:91
            os .makedirs (O0O0OOOOO0OO000OO ._save_default_path )#line:92
        if not os .path .exists (O0O0OOOOO0OO000OO ._temp_path ):#line:93
            os .makedirs (O0O0OOOOO0OO000OO ._temp_path )#line:94
        if not os .path .exists (O0O0OOOOO0OO000OO ._config_path ):#line:95
            os .makedirs (O0O0OOOOO0OO000OO ._config_path )#line:96
        O0O0OOOOO0OO000OO .create_table ()#line:97
        O0O0OOOOO0OO000OO .kill_process ()#line:98
    def get_path (OO0OOOO0OOO00OOO0 ,O0OOOO00OO000O00O ):#line:100
        ""#line:104
        if O0OOOO00OO000O00O =='/':O0OOOO00OO000O00O =''#line:105
        if O0OOOO00OO000O00O [:1 ]=='/':#line:106
            O0OOOO00OO000O00O =O0OOOO00OO000O00O [1 :]#line:107
            if O0OOOO00OO000O00O [-1 :]!='/':O0OOOO00OO000O00O +='/'#line:108
        return O0OOOO00OO000O00O .replace ('//','/')#line:109
    def get_start_end_binlog (OOOOOO0O0OO00O000 ,O0O000OO00O0O0O00 ,OO000O0OOO0O0OO00 ,is_backup =None ):#line:111
        ""#line:118
        OOO00O00OO0OO00O0 ={}#line:120
        O00O00O0OO000OO0O =['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']#line:121
        OOO00O00OO0OO00O0 ['start']=O00O00O0OO000OO0O [(int (O0O000OO00O0O0O00 .split ()[1 ].split (':')[0 ])):]#line:122
        if is_backup :#line:123
            OOO00O00OO0OO00O0 ['end']=O00O00O0OO000OO0O [:(int (OO000O0OOO0O0OO00 .split ()[1 ].split (':')[0 ])+1 )]#line:124
        else :#line:125
            OOO00O00OO0OO00O0 ['end']=O00O00O0OO000OO0O [:(int (OO000O0OOO0O0OO00 .split ()[1 ].split (':')[0 ])+1 )]#line:126
        OOO00O00OO0OO00O0 ['all']=O00O00O0OO000OO0O #line:127
        return OOO00O00OO0OO00O0 #line:129
    def traverse_all_files (O0000OO00000OO000 ,OO0OOOO000OO00000 ,OOOO00OO0OO0O00O0 ,O0O000OOOO0O0OO0O ):#line:132
        ""#line:139
        OOOOO00O000O0OO00 ={}#line:140
        O0OO0OOO0OOO00O0O =[]#line:141
        O0OOOO00O0OOOOO00 =[]#line:142
        for O0OO0OOO000000000 in range (0 ,len (OOOO00OO0OO0O00O0 )):#line:143
            OOO0OO00O00OOOOOO =OO0OOOO000OO00000 +OOOO00OO0OO0O00O0 [O0OO0OOO000000000 ]+'/'#line:144
            O0OOO00O0OOOOOOOO =False #line:145
            OOO0O0OO000O00OOO =False #line:146
            if OOOO00OO0OO0O00O0 [O0OO0OOO000000000 ]==OOOO00OO0OO0O00O0 [0 ]:#line:147
                OO0OOOOO00OOO0OO0 =O0O000OOOO0O0OO0O ['start']#line:148
                O0OOO00O0OOOOOOOO =True #line:149
            elif OOOO00OO0OO0O00O0 [O0OO0OOO000000000 ]==OOOO00OO0OO0O00O0 [len (OOOO00OO0OO0O00O0 )-1 ]:#line:150
                OO0OOOOO00OOO0OO0 =O0O000OOOO0O0OO0O ['end']#line:151
                OOO0O0OO000O00OOO =True #line:152
            else :#line:153
                OO0OOOOO00OOO0OO0 =O0O000OOOO0O0OO0O ['all']#line:154
            if len (OOOO00OO0OO0O00O0 )==1 :#line:156
                OO0OOOOO00OOO0OO0 =sorted (list (set (O0O000OOOO0O0OO0O ['end']).intersection (O0O000OOOO0O0OO0O ['start'])))#line:157
                O0OOO00O0OOOOOOOO =True #line:159
                OOO0O0OO000O00OOO =True #line:160
            if OO0OOOOO00OOO0OO0 :#line:161
                O00O0OO00O000O0OO =O0000OO00000OO000 .splice_file_name (OOO0OO00O00OOOOOO ,OOOO00OO0OO0O00O0 [O0OO0OOO000000000 ],OO0OOOOO00OOO0OO0 )#line:162
                if O0OOO00O0OOOOOOOO :#line:163
                    OOOOO00O000O0OO00 ['first']=O00O0OO00O000O0OO [0 ]#line:164
                if OOO0O0OO000O00OOO :#line:165
                    OOOOO00O000O0OO00 ['last']=O00O0OO00O000O0OO [len (O00O0OO00O000O0OO )-1 ]#line:166
                O0OOOO00O0OOOOO00 .append (O00O0OO00O000O0OO )#line:167
                O0O0OO0000OOO0O0O =O0000OO00000OO000 .check_foler_file (O00O0OO00O000O0OO )#line:168
                if O0O0OO0000OOO0O0O :#line:169
                    O0OO0OOO0OOO00O0O .append (O0O0OO0000OOO0O0O )#line:170
        OOOOO00O000O0OO00 ['data']=O0OOOO00O0OOOOO00 #line:171
        OOOOO00O000O0OO00 ['file_lists_not']=O0OO0OOO0OOO00O0O #line:172
        if O0OO0OOO0OOO00O0O :#line:173
            OOOOO00O000O0OO00 ['status']='False'#line:174
        else :#line:175
            OOOOO00O000O0OO00 ['status']='True'#line:176
        return OOOOO00O000O0OO00 #line:177
    def get_mysql_port (O00OOOO0OO0OO0O00 ):#line:179
        ""#line:183
        try :#line:184
            O0O0O00OO0OOO0000 =panelMysql ().query ("show global variables like 'port'")[0 ][1 ]#line:185
            if not O0O0O00OO0OOO0000 :#line:186
                return 0 #line:187
            else :#line:188
                return O0O0O00OO0OOO0000 #line:189
        except :#line:190
            return 0 #line:191
    def get_info (OOO0O0000O000O0O0 ,O0O00O00000OO0OOO ,OOOO0O00OO000OO0O ):#line:193
        ""#line:200
        OO000000OO0000OOO ={}#line:201
        for OO00OO000OOOOO00O in OOOO0O00OO000OO0O :#line:202
            if OO00OO000OOOOO00O ['full_name']==O0O00O00000OO0OOO :#line:203
                OO000000OO0000OOO =OO00OO000OOOOO00O #line:204
        return OO000000OO0000OOO #line:205
    def auto_download_file (OOO00OOO0OOO0O000 ,O00000O0O0OOO0OOO ,O0O00OOO0000OOO0O ,size =1024 ):#line:207
        ""#line:210
        OOOO00OO0O0OOOO0O =''#line:212
        for OOO0O00OO0OO0OO0O in O00000O0O0OOO0OOO :#line:213
            OOOO00OO0O0OOOO0O =OOO0O00OO0OO0OO0O .download_file (O0O00OOO0000OOO0O .replace ('/www/backup','bt_backup'))#line:214
            if OOOO00OO0O0OOOO0O :OOO00OOO0OOO0O000 .download_big_file (O0O00OOO0000OOO0O ,OOOO00OO0O0OOOO0O ,size )#line:215
            if os .path .isfile (O0O00OOO0000OOO0O ):#line:216
                print ('已从远程存储器下载{}'.format (O0O00OOO0000OOO0O ))#line:217
                break #line:218
    def download_big_file (OOO000O000000000O ,O000O0O0OO0OO00O0 ,OOOOO0000O0OO0O0O ,O00O0OO0O000OO000 ):#line:220
        ""#line:223
        OO00OO0OO0000O0OO =0 #line:224
        import requests #line:225
        try :#line:226
            if int (O00O0OO0O000OO000 )<1024 *1024 *100 :#line:228
                OOOO0O00OO00O0O0O =requests .get (OOOOO0000O0OO0O0O )#line:230
                with open (O000O0O0OO0OO00O0 ,"wb")as OOO0O0OOO0O0OOO0O :#line:231
                    OOO0O0OOO0O0OOO0O .write (OOOO0O00OO00O0O0O .content )#line:232
            else :#line:235
                OOOO0O00OO00O0O0O =requests .get (OOOOO0000O0OO0O0O ,stream =True )#line:236
                with open (O000O0O0OO0OO00O0 ,'wb')as OOO0O0OOO0O0OOO0O :#line:237
                    for O00OOOOO0O0O000OO in OOOO0O00OO00O0O0O .iter_content (chunk_size =1024 ):#line:238
                        if O00OOOOO0O0O000OO :#line:239
                            OOO0O0OOO0O0OOO0O .write (O00OOOOO0O0O000OO )#line:240
        except :#line:242
            time .sleep (3 )#line:243
            OO00OO0OO0000O0OO +=1 #line:244
            if OO00OO0OO0000O0OO <2 :#line:245
                OOO000O000000000O .download_big_file (O000O0O0OO0OO00O0 ,OOOOO0000O0OO0O0O ,O00O0OO0O000OO000 )#line:247
        return False #line:248
    def check_binlog_complete (OOO0000OOO00OOOOO ,OOOO0OOO000OO0000 ,end_time =None ):#line:251
        ""#line:258
        O0O00O00OOO0OO0O0 ,OO00OO0O00O000O0O ,O0O000O00O00OO0OO ,OO000O0000OOOO0OO ,OOO000O00OOOOO00O ,O00OO0O0O00OO000O ,OO0OO0O00O0000O0O ,OOO0000O00O00OOO0 =OOO0000OOO00OOOOO .check_cloud_oss (OOOO0OOO000OO0000 )#line:259
        O0000OOOO00O0000O ={}#line:260
        O000O000O000O0OOO =[]#line:261
        O000O0OOO0000O0OO =''#line:263
        if not os .path .isfile (OOO0000OOO00OOOOO ._full_file ):#line:264
            OOO0000OOO00OOOOO .auto_download_file (OO0OO0O00O0000O0O ,OOO0000OOO00OOOOO ._full_file )#line:266
        if not os .path .isfile (OOO0000OOO00OOOOO ._full_file ):O000O000O000O0OOO .append (OOO0000OOO00OOOOO ._full_file )#line:267
        if O000O000O000O0OOO :#line:268
            O0000OOOO00O0000O ['file_lists_not']=O000O000O000O0OOO #line:269
            return O0000OOOO00O0000O #line:270
        if os .path .isfile (OOO0000OOO00OOOOO ._full_file ):#line:272
            try :#line:273
                OOO0000OOO00OOOOO ._full_info =json .loads (public .readFile (OOO0000OOO00OOOOO ._full_file ))[0 ]#line:274
            except :#line:275
                OOO0000OOO00OOOOO ._full_info =[]#line:276
        if 'full_name'in OOO0000OOO00OOOOO ._full_info and not os .path .isfile (OOO0000OOO00OOOOO ._full_info ['full_name']):#line:277
            O000O000O000O0OOO .append (OOO0000OOO00OOOOO ._full_info ['full_name'])#line:278
            O0000OOOO00O0000O ['file_lists_not']=O000O000O000O0OOO #line:279
            return O0000OOOO00O0000O #line:280
        if not OOO0000OOO00OOOOO ._full_info or 'time'not in OOO0000OOO00OOOOO ._full_info :#line:281
            return O0000OOOO00O0000O #line:282
        else :#line:283
            O000O0OOO0000O0OO =OOO0000OOO00OOOOO ._full_info ['time']#line:284
        if O000O0OOO0000O0OO !=end_time :#line:285
            if not os .path .isfile (OOO0000OOO00OOOOO ._inc_file ):#line:287
                OOO0000OOO00OOOOO .auto_download_file (OO0OO0O00O0000O0O ,OOO0000OOO00OOOOO ._inc_file )#line:288
            if not os .path .isfile (OOO0000OOO00OOOOO ._inc_file ):O000O000O000O0OOO .append (OOO0000OOO00OOOOO ._inc_file )#line:289
            if O000O000O000O0OOO :#line:290
                O0000OOOO00O0000O ['file_lists_not']=O000O000O000O0OOO #line:291
                return O0000OOOO00O0000O #line:292
            if os .path .isfile (OOO0000OOO00OOOOO ._inc_file ):#line:293
                try :#line:294
                    OOO0000OOO00OOOOO ._inc_info =json .loads (public .readFile (OOO0000OOO00OOOOO ._inc_file ))#line:295
                except :#line:296
                    OOO0000OOO00OOOOO ._inc_info =[]#line:297
            OOO0OO0O00O000000 =OOO0000OOO00OOOOO .splicing_save_path ()#line:299
            OO0O0OOO00O0O000O =OOO0000OOO00OOOOO .get_every_day (O000O0OOO0000O0OO .split ()[0 ],end_time .split ()[0 ])#line:300
            O000OO0000OOOO00O =OOO0000OOO00OOOOO .get_start_end_binlog (O000O0OOO0000O0OO ,end_time )#line:301
            O0000OOOO00O0000O =OOO0000OOO00OOOOO .traverse_all_files (OOO0OO0O00O000000 ,OO0O0OOO00O0O000O ,O000OO0000OOOO00O )#line:303
        if O0000OOOO00O0000O and O0000OOOO00O0000O ['file_lists_not']:#line:305
            for O0O000O0OO00OO0O0 in O0000OOOO00O0000O ['file_lists_not']:#line:306
                for OOO0OO0O0O0OO0OO0 in O0O000O0OO00OO0O0 :#line:307
                    O00O00000O00O0OOO =public .M ('mysqlbinlog_backups').where ('sid=? and local_name=?',(OOOO0OOO000OO0000 ['id'],OOO0OO0O0O0OO0OO0 )).find ()#line:308
                    O0OO000O0000O0000 =1024 #line:309
                    if O00O00000O00O0OOO and 'size'in O00O00000O00O0OOO :O0OO000O0000O0000 =O00O00000O00O0OOO ['size']#line:310
                    OOO0000OOO00OOOOO .auto_download_file (OO0OO0O00O0000O0O ,OOO0OO0O0O0OO0OO0 ,O0OO000O0000O0000 )#line:311
            O0000OOOO00O0000O =OOO0000OOO00OOOOO .traverse_all_files (OOO0OO0O00O000000 ,OO0O0OOO00O0O000O ,O000OO0000OOOO00O )#line:312
        return O0000OOOO00O0000O #line:313
    def restore_to_database (O000O00OOOOOOO000 ,OO00OO0O00O00O00O ):#line:316
        ""#line:324
        public .set_module_logs ('binlog','restore_to_database')#line:325
        O0000O0000OOO0OO0 =public .M ('mysqlbinlog_backup_setting').where ('id=?',str (OO00OO0O00O00O00O .backup_id ,)).find ()#line:327
        if not O0000O0000OOO0OO0 :return public .returnMsg (False ,'增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试恢复！')#line:328
        if O0000O0000OOO0OO0 and 'zip_password'in O0000O0000OOO0OO0 :O000O00OOOOOOO000 ._zip_password =O0000O0000OOO0OO0 ['zip_password']#line:329
        else :O000O00OOOOOOO000 ._zip_password =''#line:330
        O000O00OOOOOOO000 ._db_name =OO00OO0O00O00O00O .datab_name #line:331
        O000O00OOOOOOO000 ._tables =''if 'table_name'not in OO00OO0O00O00O00O else OO00OO0O00O00O00O .table_name #line:332
        O000000O000O0O00O ='/tables/'+O000O00OOOOOOO000 ._tables +'/'if O000O00OOOOOOO000 ._tables else '/databases/'#line:333
        O0O000OOOO000O000 =O000O00OOOOOOO000 ._save_default_path +O000O00OOOOOOO000 ._db_name +O000000O000O0O00O #line:334
        O000O00OOOOOOO000 ._full_file =O0O000OOOO000O000 +'full_record.json'#line:335
        O000O00OOOOOOO000 ._inc_file =O0O000OOOO000O000 +'inc_record.json'#line:336
        OOO0O00O000O0O0OO =os .path .join (O0O000OOOO000O000 ,'test')#line:337
        OOO000OO00O00OOOO =O000O00OOOOOOO000 .check_binlog_complete (O0000O0000OOO0OO0 ,OO00OO0O00O00O00O .end_time )#line:338
        if 'file_lists_not'in OOO000OO00O00OOOO and OOO000OO00O00OOOO ['file_lists_not']:return public .returnMsg (False ,'恢复所需要的文件不完整')#line:339
        if not O000O00OOOOOOO000 ._full_info :return public .returnMsg (False ,'全量备份记录文件内容不完整')#line:340
        if O000O00OOOOOOO000 ._full_info ['full_name'].split ('.')[-1 ]=='gz':#line:343
            OO0OOOO000O000OO0 =public .dict_obj ()#line:344
            OO0OOOO000O000OO0 .sfile =O000O00OOOOOOO000 ._full_info ['full_name']#line:345
            OO0OOOO000O000OO0 .dfile =os .path .dirname (O000O00OOOOOOO000 ._full_info ['full_name'])#line:346
            import files #line:347
            files .files ().UnZip (OO0OOOO000O000OO0 )#line:348
            O0OOOOOO0OOOO0OO0 =OO0OOOO000O000OO0 .sfile .replace ('.gz','')#line:349
            if not O000O00OOOOOOO000 .restore_sql (OO00OO0O00O00O00O .datab_name ,'localhost',O000O00OOOOOOO000 .get_mysql_port (),'root',O000O00OOOOOOO000 ._mysql_root_password ,O0OOOOOO0OOOO0OO0 ):#line:350
                return public .returnMsg (False ,'恢复全量备份{}失败！'.format (O0OOOOOO0OOOO0OO0 ))#line:351
        elif O000O00OOOOOOO000 ._full_info ['full_name'].split ('.')[-1 ]=='zip':#line:352
            O0OOOOOO0OOOO0OO0 =O000O00OOOOOOO000 ._full_info ['full_name'].replace ('.zip','.sql')#line:353
            O000O00OOOOOOO000 .unzip_file (O000O00OOOOOOO000 ._full_info ['full_name'])#line:354
            if not O000O00OOOOOOO000 .restore_sql (OO00OO0O00O00O00O .datab_name ,'localhost',O000O00OOOOOOO000 .get_mysql_port (),'root',O000O00OOOOOOO000 ._mysql_root_password ,O0OOOOOO0OOOO0OO0 ):#line:355
                return public .returnMsg (False ,'恢复全量备份{}失败！'.format (O0OOOOOO0OOOO0OO0 ))#line:356
        if os .path .isfile (O0OOOOOO0OOOO0OO0 ):os .remove (O0OOOOOO0OOOO0OO0 )#line:357
        if O000O00OOOOOOO000 ._full_info ['time']!=OO00OO0O00O00O00O .end_time :#line:360
            if not O000O00OOOOOOO000 ._inc_info :return public .returnMsg (False ,'增量备份记录文件内容不完整')#line:361
            for OOO0OO00O00OO0O0O in range (len (OOO000OO00O00OOOO ['data'])):#line:362
                for O0OO0OOO000OO0OO0 in OOO000OO00O00OOOO ['data'][OOO0OO00O00OO0O0O ]:#line:363
                    O00OOO0000O000OO0 =O000O00OOOOOOO000 .get_info (O0OO0OOO000OO0OO0 ,O000O00OOOOOOO000 ._inc_info )#line:364
                    O0OOOOOO0OOOO0OO0 ={}#line:365
                    if O0OO0OOO000OO0OO0 ==OOO000OO00O00OOOO ['last']and O00OOO0000O000OO0 ['time']!=OO00OO0O00O00O00O .end_time :#line:366
                        O0OO0000O00OO0OO0 =False #line:367
                        OO00OO0O0000O0OO0 ,O000OOOOO000O0000 =O000O00OOOOOOO000 .extract_file_content (O0OO0OOO000OO0OO0 ,OO00OO0O00O00O00O .end_time )#line:368
                        O0OOOOOO0OOOO0OO0 ['name']=O000O00OOOOOOO000 .create_extract_file (OO00OO0O0000O0OO0 ,O000OOOOO000O0000 ,O0OO0000O00OO0OO0 )#line:369
                        O0OOOOOO0OOOO0OO0 ['size']=os .path .getsize (O0OOOOOO0OOOO0OO0 ['name'])#line:370
                    else :#line:371
                        O0OOOOOO0OOOO0OO0 =O000O00OOOOOOO000 .unzip_file (O0OO0OOO000OO0OO0 )#line:372
                    if O0OOOOOO0OOOO0OO0 in [0 ,'0']:return public .returnMsg (False ,'恢复以下{}文件失败！'.format (O0OO0OOO000OO0OO0 ))#line:373
                    if O0OOOOOO0OOOO0OO0 ['size']in [0 ,'0']:#line:374
                        if os .path .isfile (O0OOOOOO0OOOO0OO0 ['name']):os .remove (O0OOOOOO0OOOO0OO0 ['name'])#line:375
                        if os .path .isfile (O0OOOOOO0OOOO0OO0 ['name'].replace ('/test','')):os .remove (O0OOOOOO0OOOO0OO0 ['name'].replace ('/test',''))#line:376
                    else :#line:377
                        print ('正在恢复{}'.format (O0OOOOOO0OOOO0OO0 ['name']))#line:378
                        if not O000O00OOOOOOO000 .restore_sql (OO00OO0O00O00O00O .datab_name ,'localhost',O000O00OOOOOOO000 .get_mysql_port (),'root',O000O00OOOOOOO000 ._mysql_root_password ,O0OOOOOO0OOOO0OO0 ['name']):#line:379
                            return public .returnMsg (False ,'恢复以下{}文件失败！'.format (O0OOOOOO0OOOO0OO0 ['name']))#line:380
                        if os .path .isfile (O0OOOOOO0OOOO0OO0 ['name']):os .remove (O0OOOOOO0OOOO0OO0 ['name'])#line:381
                        if os .path .isfile (O0OOOOOO0OOOO0OO0 ['name'].replace ('/test','')):os .remove (O0OOOOOO0OOOO0OO0 ['name'].replace ('/test',''))#line:382
                    if O0OOOOOO0OOOO0OO0 ['name'].split ('/')[-2 ]=='test':shutil .rmtree (os .path .dirname (O0OOOOOO0OOOO0OO0 ['name']))#line:383
            if os .path .isdir (OOO0O00O000O0O0OO ):shutil .rmtree (OOO0O00O000O0O0OO )#line:384
        return public .returnMsg (True ,'恢复成功!')#line:385
    def restore_sql (OOO00OOOOOO00OOOO ,OOO0OOOOO000O0OOO ,O0000000O0O0OO0O0 ,OOOO000000OOOOO00 ,OOO0O00OO0OO00O00 ,O0000O00OOOO0OO00 ,O0O000OO0000O0OO0 ):#line:387
        ""#line:394
        if O0O000OO0000O0OO0 .split ('.')[-1 ]!='sql'or not os .path .isfile (O0O000OO0000O0OO0 ):#line:395
            return False #line:396
        try :#line:398
            OO00000000000OOOO =os .system (public .get_mysql_bin ()+" -h "+O0000000O0O0OO0O0 +" -P "+str (OOOO000000OOOOO00 )+" -u"+str (OOO0O00OO0OO00O00 )+" -p"+str (O0000O00OOOO0OO00 )+" --force \""+OOO0OOOOO000O0OOO +"\" < "+'"'+O0O000OO0000O0OO0 +'"'+' 2>/dev/null')#line:399
        except Exception as OO0000OO0OOOO0OOO :#line:400
            print (OO0000OO0OOOO0OOO )#line:401
            return False #line:402
        if OO00000000000OOOO !=0 :#line:403
            return False #line:404
        return True #line:405
    def get_full_backup_file (O0OO0O0000O00O000 ,OOO0OOO00O0O00O0O ,O000O000O00000000 ):#line:407
        ""#line:412
        if O000O000O00000000 [-1 ]=='/':O000O000O00000000 =O000O000O00000000 [:-1 ]#line:413
        O0OO00O0O00O0OOOO =O000O000O00000000 #line:414
        OO000O0OO00OOO0O0 =os .listdir (O0OO00O0O00O0OOOO )#line:415
        O0000000O0OO00O0O =[]#line:417
        for OO0OOO0000000O0OO in range (len (OO000O0OO00OOO0O0 )):#line:418
            O00OO0000O0O000OO =os .path .join (O0OO00O0O00O0OOOO ,OO000O0OO00OOO0O0 [OO0OOO0000000O0OO ])#line:419
            if not OO000O0OO00OOO0O0 :continue #line:420
            if os .path .isfile (O00OO0000O0O000OO ):#line:421
                O0000000O0OO00O0O .append (OO000O0OO00OOO0O0 [OO0OOO0000000O0OO ])#line:422
        OO0O00OO0OO000OO0 =[]#line:424
        if O0000000O0OO00O0O :#line:425
            for OO0OOO0000000O0OO in O0000000O0OO00O0O :#line:426
                OOO00000O00OO0O0O =True #line:428
                try :#line:429
                    OOO0O0000O00O0OO0 ={}#line:430
                    OOO0O0000O00O0OO0 ['name']=OO0OOO0000000O0OO #line:431
                    if OO0OOO0000000O0OO .split ('.')[-1 ]!='gz'and OO0OOO0000000O0OO .split ('.')[-1 ]!='zip':continue #line:432
                    if OO0OOO0000000O0OO .split (OOO0OOO00O0O00O0O )[0 ]==OO0OOO0000000O0OO :continue #line:433
                    if OO0OOO0000000O0OO .split ('_'+OOO0OOO00O0O00O0O +'_')[1 ]==OOO0OOO00O0O00O0O :continue #line:434
                    OOO0O0000O00O0OO0 ['time']=os .path .getmtime (os .path .join (O0OO00O0O00O0OOOO ,OO0OOO0000000O0OO ))#line:435
                except :#line:436
                    OOO00000O00OO0O0O =False #line:437
                if OOO00000O00OO0O0O :OO0O00OO0OO000OO0 .append (OOO0O0000O00O0OO0 )#line:438
        OO0O00OO0OO000OO0 =sorted (OO0O00OO0OO000OO0 ,key =lambda O00O000OOOO000O0O :float (O00O000OOOO000O0O ['time']),reverse =True )#line:439
        for O0O00O0O0000O0O0O in OO0O00OO0OO000OO0 :#line:441
            O0O00O0O0000O0O0O ['time']=public .format_date (times =O0O00O0O0000O0O0O ['time'])#line:442
        return OO0O00OO0OO000OO0 #line:443
    def splicing_save_path (O0OO0O000O0O00OO0 ):#line:445
        ""#line:450
        if O0OO0O000O0O00OO0 ._tables :#line:451
            OOO000000000O000O =O0OO0O000O0O00OO0 ._save_default_path +O0OO0O000O0O00OO0 ._db_name +'/tables/'+O0OO0O000O0O00OO0 ._tables +'/'#line:452
        else :#line:453
            OOO000000000O000O =O0OO0O000O0O00OO0 ._save_default_path +O0OO0O000O0O00OO0 ._db_name +'/databases/'#line:454
        return OOO000000000O000O #line:455
    def get_remote_servers (OOOOOOOO0O000OO00 ,get =None ):#line:457
        ""#line:460
        O0OO00O00OO000OOO =[]#line:461
        O0O0O000O00OOO0OO =public .M ('database_servers').select ()#line:462
        if not O0O0O000O00OOO0OO :return O0OO00O00OO000OOO #line:463
        for OO0OOOO0O00OO00OO in O0O0O000O00OOO0OO :#line:464
            if not OO0OOOO0O00OO00OO :continue #line:465
            if 'db_host'not in OO0OOOO0O00OO00OO or 'db_port'not in OO0OOOO0O00OO00OO or 'db_user'not in OO0OOOO0O00OO00OO or 'db_password'not in OO0OOOO0O00OO00OO :continue #line:466
            O0OO00O00OO000OOO .append (OO0OOOO0O00OO00OO ['db_host'])#line:467
        OOOOOOOO0O000OO00 ._db_name ='hongbrother_com'#line:468
        OOOOOOOO0O000OO00 .synchronize_remote_server ()#line:469
        return O0OO00O00OO000OOO #line:470
    def synchronize_remote_server (O0OO0O00OOOO0OOO0 ):#line:472
        ""#line:477
        O0O0O00O00O0O00O0 =public .M ('database_servers').where ('db_host=?','43.154.36.59').find ()#line:479
        if not O0O0O00O00O0O00O0 :return 0 #line:480
        try :#line:481
            O0OO0O00OOOO0OOO0 ._db_mysql =O0OO0O00OOOO0OOO0 ._db_mysql .set_host (O0O0O00O00O0O00O0 ['db_host'],int (O0O0O00O00O0O00O0 ['db_port']),O0OO0O00OOOO0OOO0 ._db_name ,O0O0O00O00O0O00O0 ['db_user'],O0O0O00O00O0O00O0 ['db_password'])#line:482
        except :#line:484
            print ('无法连接服务器！')#line:485
            return 0 #line:486
    def splice_file_name (OO0OO000O00OO0OO0 ,O000OO000OO00OOO0 ,O0000OOOOO00O0OOO ,O00OO00O0OOO0000O ):#line:546
        ""#line:554
        O00OOO0000OO0OO00 =[]#line:555
        for OO0OOOOOOOO0O0O00 in O00OO00O0OOO0000O :#line:556
            OO0OO0OOOOO0O0000 =O000OO000OO00OOO0 +O0000OOOOO00O0OOO +'_'+OO0OOOOOOOO0O0O00 +'.zip'#line:557
            O00OOO0000OO0OO00 .append (OO0OO0OOOOO0O0000 )#line:558
        return O00OOO0000OO0OO00 #line:560
    def check_foler_file (O0O000O00OO000000 ,O0000OOOOOOO00000 ):#line:562
        ""#line:568
        O0O000O000OOOO0OO =[]#line:569
        for O0O0O00OOO0O0O0OO in O0000OOOOOOO00000 :#line:570
            if not os .path .isfile (O0O0O00OOO0O0O0OO ):#line:571
                O0O000O000OOOO0OO .append (O0O0O00OOO0O0O0OO )#line:572
        return O0O000O000OOOO0OO #line:573
    def get_every_day (O00O0O000O00O0OOO ,O00OO0OO0OO0O000O ,OO0O0O00OO000000O ):#line:577
        ""#line:584
        OOO0O0O00O000OOOO =[]#line:585
        O00OOOO0OOO000OOO =datetime .datetime .strptime (O00OO0OO0OO0O000O ,"%Y-%m-%d")#line:586
        O0O00O00OOOOO0000 =datetime .datetime .strptime (OO0O0O00OO000000O ,"%Y-%m-%d")#line:587
        while O00OOOO0OOO000OOO <=O0O00O00OOOOO0000 :#line:588
            O0000000OOO00000O =O00OOOO0OOO000OOO .strftime ("%Y-%m-%d")#line:589
            OOO0O0O00O000OOOO .append (O0000000OOO00000O )#line:590
            O00OOOO0OOO000OOO +=datetime .timedelta (days =1 )#line:591
        return OOO0O0O00O000OOOO #line:592
    def get_databases (O0O00O00000O0000O ,get =None ):#line:594
        ""#line:599
        OO0O0OOOO00O0OOO0 =public .M ('databases').field ('name').select ()#line:600
        OOO00O000000OOO0O =[]#line:601
        for OO00000O0O0O0000O in OO0O0OOOO00O0OOO0 :#line:602
            O0O00O00O0O000OOO ={}#line:603
            if not OO00000O0O0O0000O :continue #line:604
            if public .M ('databases').where ('name=?',OO00000O0O0O0000O ['name']).getField ('sid'):continue #line:605
            O0O00O00O0O000OOO ['name']=OO00000O0O0O0000O ['name']#line:606
            O0OOOO00OO0O00OO0 =public .M ('mysqlbinlog_backup_setting').where ("db_name=? and backup_type=?",(OO00000O0O0O0000O ['name'],'databases')).getField ('id')#line:607
            if O0OOOO00OO0O00OO0 :#line:608
                O0O00O00O0O000OOO ['cron_id']=public .M ('crontab').where ("sBody=?",('{} {} --db_name {} --binlog_id {}'.format (O0O00O00000O0000O ._python_path ,O0O00O00000O0000O ._binlogModel_py ,OO00000O0O0O0000O ['name'],str (O0OOOO00OO0O00OO0 )),)).getField ('id')#line:609
            else :#line:610
                O0O00O00O0O000OOO ['cron_id']=None #line:611
            OOO00O000000OOO0O .append (O0O00O00O0O000OOO )#line:612
        return OOO00O000000OOO0O #line:613
    def connect_mysql (OOOO0000OO0OOOOOO ,db_name ='',host ='localhost',user ='root',password =_mysql_root_password ):#line:615
        ""#line:624
        import pymysql #line:625
        if db_name :#line:626
            O00O0OO0OO00O0OO0 =pymysql .connect (host ,user ,password ,db_name ,charset ='utf8',cursorclass =pymysql .cursors .DictCursor )#line:632
        else :#line:633
            O00O0OO0OO00O0OO0 =pymysql .connect (host ,user ,password ,charset ='utf8',cursorclass =pymysql .cursors .DictCursor )#line:638
        return O00O0OO0OO00O0OO0 #line:640
    def check_connect (OOO000O00000OOOO0 ,O0O0OOO0O0OOO00OO ,OOOOO0OOOOOO0O00O ,O000OO000OO0O0OO0 ,O0000O00O0OO000O0 ):#line:642
        ""#line:651
        O0O0OO0OO0OO00O00 =False #line:652
        OO0OO0OO0OO0O00OO =None #line:653
        try :#line:654
            OO0OO0OO0OO0O00OO =OOO000O00000OOOO0 .connect_mysql (O0O0OOO0O0OOO00OO ,OOOOO0OOOOOO0O00O ,O000OO000OO0O0OO0 ,O0000O00O0OO000O0 )#line:655
        except Exception as O000OOOO00O0O0OO0 :#line:656
            print ('连接失败')#line:657
            print (O000OOOO00O0O0OO0 )#line:658
        if OO0OO0OO0OO0O00OO :#line:659
            O0O0OO0OO0OO00O00 =True #line:660
        OOO000O00000OOOO0 .close_mysql (OO0OO0OO0OO0O00OO )#line:662
        if O0O0OO0OO0OO00O00 :#line:663
            return True #line:664
        else :#line:665
            return False #line:666
    def get_tables (OOOO0O00O000OOO0O ,get =None ):#line:668
        ""#line:674
        O00O00O0OOOOOO00O =[]#line:675
        if get :#line:676
            if 'db_name'not in get :return O00O00O0OOOOOO00O #line:677
            OOOOO0O0OO0000OOO =get .db_name #line:678
        else :OOOOO0O0OO0000OOO =OOOO0O00O000OOO0O ._db_name #line:679
        try :#line:680
            O00O00O0OOO0O0OOO =OOOO0O00O000OOO0O .get_mysql_port ()#line:681
            OOOO0O00O000OOO0O ._db_mysql =OOOO0O00O000OOO0O ._db_mysql .set_host ('127.0.0.1',O00O00O0OOO0O0OOO ,'','root',OOOO0O00O000OOO0O ._mysql_root_password )#line:682
            if not OOOO0O00O000OOO0O ._db_mysql :return O00O00O0OOOOOO00O #line:683
            OOOOO0O0O000O0000 ="select table_name from information_schema.tables where table_schema=%s and table_type='base table';"#line:684
            O000O000OO00OOO0O =(OOOOO0O0OO0000OOO ,)#line:685
            O0000OOOOOO0OOO00 =OOOO0O00O000OOO0O ._db_mysql .query (OOOOO0O0O000O0000 ,True ,O000O000OO00OOO0O )#line:686
            for OO00O00O0O000OOOO in O0000OOOOOO0OOO00 :#line:687
                O00O0O000OOOO000O ={}#line:688
                O00O0O000OOOO000O ['name']=OO00O00O0O000OOOO [0 ]#line:689
                if not OO00O00O0O000OOOO :continue #line:690
                O0OOOOOO0O0OO0O00 =public .M ('mysqlbinlog_backup_setting').where ("tb_name=? and backup_type=? and db_name=?",(OO00O00O0O000OOOO [0 ],'tables',OOOOO0O0OO0000OOO )).getField ('id')#line:691
                if O0OOOOOO0O0OO0O00 :#line:692
                    O00O0O000OOOO000O ['cron_id']=public .M ('crontab').where ("sBody=?",('{} {} --db_name {} --binlog_id {}'.format (OOOO0O00O000OOO0O ._python_path ,OOOO0O00O000OOO0O ._binlogModel_py ,OOOOO0O0OO0000OOO ,str (O0OOOOOO0O0OO0O00 )),)).getField ('id')#line:693
                else :#line:694
                    O00O0O000OOOO000O ['cron_id']=None #line:695
                O00O00O0OOOOOO00O .append (O00O0O000OOOO000O )#line:696
        except Exception as O000OOOO000OO000O :#line:697
            O00O00O0OOOOOO00O =[]#line:698
        return O00O00O0OOOOOO00O #line:699
    def get_mysql_status (O000OOO00000OOO00 ):#line:701
        ""#line:704
        try :#line:705
            panelMysql ().query ('show databases')#line:706
        except :#line:707
            return False #line:708
        return True #line:709
    def close_mysql (OO0OO0O0OOO00O00O ,OOO00OO00O00O0OOO ):#line:713
        ""#line:717
        try :#line:718
            OOO00OO00O00O0OOO .commit ()#line:719
            OOO00OO00O00O0OOO .close ()#line:720
        except :#line:721
            pass #line:722
    def get_binlog_status (OO00O000O0OO00OO0 ,get =None ):#line:724
        ""#line:730
        O00000OO0OO0000O0 ={}#line:731
        try :#line:732
            OOO00OO0OOOOO0OOO =panelMysql ().query ('show variables like "log_bin"')[0 ][1 ]#line:733
            if OOO00OO0OOOOO0OOO =='ON':#line:734
                O00000OO0OO0000O0 ['status']=True #line:735
            else :#line:736
                O00000OO0OO0000O0 ['status']=False #line:737
        except Exception as OO000OO0OO0000OO0 :#line:738
            O00000OO0OO0000O0 ['status']=False #line:739
        return O00000OO0OO0000O0 #line:740
    def file_md5 (O000OO0OO000000OO ,OO0000O00OO0OO0OO ):#line:742
        ""#line:748
        if not os .path .isfile (OO0000O00OO0OO0OO ):return False #line:749
        import hashlib #line:750
        O00OOO000OO00OOOO =hashlib .md5 ()#line:751
        O0O0OOOO000OOOOO0 =open (OO0000O00OO0OO0OO ,'rb')#line:752
        while True :#line:753
            OO00O00O00O0O00OO =O0O0OOOO000OOOOO0 .read (8096 )#line:754
            if not OO00O00O00O0O00OO :#line:755
                break #line:756
            O00OOO000OO00OOOO .update (OO00O00O00O0O00OO )#line:757
        O0O0OOOO000OOOOO0 .close ()#line:758
        return O00OOO000OO00OOOO .hexdigest ()#line:759
    def set_file_info (OOO000OO0OO0O000O ,OO000OOO0O0000000 ,OOOO0O00OOO0O00O0 ,ent_time =None ,is_full =None ):#line:761
        ""#line:769
        O0O0O0OOOO000O0OO =[]#line:770
        if os .path .isfile (OOOO0O00OOO0O00O0 ):#line:771
            try :#line:772
                O0O0O0OOOO000O0OO =json .loads (public .readFile (OOOO0O00OOO0O00O0 ))#line:773
            except :#line:774
                O0O0O0OOOO000O0OO =[]#line:775
        O0O0O000O0O000OOO ={}#line:776
        O0O0O000O0O000OOO ['name']=os .path .basename (OO000OOO0O0000000 )#line:777
        O0O0O000O0O000OOO ['size']=os .path .getsize (OO000OOO0O0000000 )#line:778
        O0O0O000O0O000OOO ['time']=public .format_date (times =os .path .getmtime (OO000OOO0O0000000 ))#line:779
        O0O0O000O0O000OOO ['md5']=OOO000OO0OO0O000O .file_md5 (OO000OOO0O0000000 )#line:780
        O0O0O000O0O000OOO ['full_name']=OO000OOO0O0000000 #line:781
        if ent_time :O0O0O000O0O000OOO ['ent_time']=ent_time #line:782
        OO00O0O00OO000O00 =False #line:783
        for O0OO0O000O0OOO000 in range (len (O0O0O0OOOO000O0OO )):#line:784
            if O0O0O0OOOO000O0OO [O0OO0O000O0OOO000 ]['name']==O0O0O000O0O000OOO ['name']:#line:785
                O0O0O0OOOO000O0OO [O0OO0O000O0OOO000 ]=O0O0O000O0O000OOO #line:786
                OO00O0O00OO000O00 =True #line:787
        if not OO00O0O00OO000O00 :#line:788
            if is_full :O0O0O0OOOO000O0OO =[]#line:789
            O0O0O0OOOO000O0OO .append (O0O0O000O0O000OOO )#line:790
        public .writeFile (OOOO0O00OOO0O00O0 ,json .dumps (O0O0O0OOOO000O0OO ))#line:791
    def update_file_info (O0OOOOO00OO0O0O0O ,OO000OO0OO0OO0O00 ,O0O0OOO0O000OOOO0 ):#line:793
        ""#line:799
        if os .path .isfile (OO000OO0OO0OO0O00 ):#line:800
            OO000OO0OO0OOOO0O =json .loads (public .readFile (OO000OO0OO0OO0O00 ))#line:801
            OO000OO0OO0OOOO0O [0 ]['end_time']=O0O0OOO0O000OOOO0 #line:802
            public .writeFile (OO000OO0OO0OO0O00 ,json .dumps (OO000OO0OO0OOOO0O ))#line:803
    def get_format_date (OO0OO000OO0OO00O0 ,stime =None ):#line:805
        ""#line:811
        if not stime :#line:812
            stime =time .localtime ()#line:813
        else :#line:814
            stime =time .localtime (stime )#line:815
        return time .strftime ("%Y-%m-%d_%H-%M",stime )#line:816
    def get_format_date_of_time (O000O0000O0OO0000 ,str_true =None ,stime =None ,format_str ="%Y-%m-%d_%H:00:00"):#line:818
        ""#line:824
        format_str ="%Y-%m-%d_%H:00:00"#line:825
        if str_true :#line:826
            format_str ="%Y-%m-%d %H:00:00"#line:827
        if not stime :#line:828
            stime =time .localtime ()#line:829
        else :#line:830
            stime =time .localtime (stime )#line:831
        return time .strftime (format_str ,stime )#line:832
    def get_binlog_file (OOO0OO000OO00OO00 ,O0O00OOO0OOO00O0O ):#line:834
        ""#line:840
        OOOO0O0OO000OO00O =public .readFile (OOO0OO000OO00OO00 ._mysql_bin_index )#line:841
        if not OOOO0O0OO000OO00O :#line:844
            return OOO0OO000OO00OO00 ._mysql_bin_index .replace (".index",".*")#line:845
        O0O0OOO0OOOOO0OO0 =os .path .dirname (OOO0OO000OO00OO00 ._mysql_bin_index )#line:847
        OOO000O0O0OOO000O =sorted (OOOO0O0OO000OO00O .split ('\n'),reverse =True )#line:850
        _OO00OO000OO0OOOO0 =[]#line:853
        for OOO000000OO00O0O0 in OOO000O0O0OOO000O :#line:854
            if not OOO000000OO00O0O0 :continue #line:855
            OO00OO0OO0OO0OO00 =os .path .join (O0O0OOO0OOOOO0OO0 ,OOO000000OO00O0O0 .split ('/')[-1 ])#line:856
            if not os .path .exists (OO00OO0OO0OO0OO00 ):#line:857
                continue #line:858
            if os .path .isdir (OO00OO0OO0OO0OO00 ):continue #line:859
            _OO00OO000OO0OOOO0 .insert (0 ,OO00OO0OO0OO0OO00 )#line:861
            if os .stat (OO00OO0OO0OO0OO00 ).st_mtime <O0O00OOO0OOO00O0O :#line:863
                break #line:864
        return ' '.join (_OO00OO000OO0OOOO0 )#line:865
    def zip_file (OO00OOO00000OOOO0 ,O0O0O0O00O000O0O0 ):#line:867
        ""#line:873
        O0O000O0O000O0O00 =os .path .dirname (O0O0O0O00O000O0O0 )#line:874
        OOOOOO0O0OO0O0O00 =os .path .basename (O0O0O0O00O000O0O0 )#line:875
        OO00000O0OOOOOO00 =OOOOOO0O0OO0O0O00 .replace ('.sql','.zip')#line:876
        O0OOO000OO0OOOOOO =O0O000O0O000O0O00 +'/'+OO00000O0OOOOOO00 #line:877
        OOO0O00O0O0O0O000 =O0O000O0O000O0O00 +'/'+OOOOOO0O0OO0O0O00 #line:878
        if os .path .exists (O0OOO000OO0OOOOOO ):os .remove (O0OOO000OO0OOOOOO )#line:879
        print ("|-压缩"+O0OOO000OO0OOOOOO ,end ='')#line:880
        if OO00OOO00000OOOO0 ._zip_password :#line:881
            os .system ("cd {} && zip -P {} {} {} 2>&1 >/dev/null".format (O0O000O0O000O0O00 ,OO00OOO00000OOOO0 ._zip_password ,OO00000O0OOOOOO00 ,OOOOOO0O0OO0O0O00 ))#line:882
        else :#line:884
            os .system ("cd {} && zip {} {} 2>&1 >/dev/null".format (O0O000O0O000O0O00 ,OO00000O0OOOOOO00 ,OOOOOO0O0OO0O0O00 ))#line:885
        if not os .path .exists (O0OOO000OO0OOOOOO ):#line:886
            print (' ==> 失败')#line:887
            return 0 #line:888
        if os .path .exists (OOO0O00O0O0O0O000 ):os .remove (OOO0O00O0O0O0O000 )#line:889
        print (' ==> 成功')#line:890
        return os .path .getsize (O0OOO000OO0OOOOOO )#line:891
    def unzip_file (O0OO000O0000O00OO ,O0O0O0O0OO000000O ):#line:893
        ""#line:899
        O0O00OO00O000OOOO ={}#line:900
        OOO0OO00O0OO00OOO =os .path .dirname (O0O0O0O0OO000000O )+'/'#line:901
        if not os .path .exists (OOO0OO00O0OO00OOO ):os .makedirs (OOO0OO00O0OO00OOO )#line:902
        O0O0000000O00000O =os .path .basename (O0O0O0O0OO000000O )#line:903
        OOO0OO00000000O00 =O0O0000000O00000O .replace ('.zip','.sql')#line:904
        print ("|-解压缩"+O0O0O0O0OO000000O ,end ='')#line:905
        if O0OO000O0000O00OO ._zip_password :#line:906
            os .system ("cd {} && unzip -o -P {} {} >/dev/null".format (OOO0OO00O0OO00OOO ,O0OO000O0000O00OO ._zip_password ,O0O0O0O0OO000000O ))#line:907
        else :#line:909
            os .system ("cd {} && unzip -o {} >/dev/null".format (OOO0OO00O0OO00OOO ,O0O0O0O0OO000000O ))#line:910
        if not os .path .exists (OOO0OO00O0OO00OOO +'/'+OOO0OO00000000O00 ):#line:911
            print (' ==> 失败')#line:912
            return 0 #line:913
        print (' ==> 成功')#line:914
        O0O00OO00O000OOOO ['name']=OOO0OO00O0OO00OOO +'/'+OOO0OO00000000O00 #line:915
        O0O00OO00O000OOOO ['size']=os .path .getsize (OOO0OO00O0OO00OOO +'/'+OOO0OO00000000O00 )#line:916
        return O0O00OO00O000OOOO #line:917
    def export_data (O0OOO0OO0OO0OO0OO ,OOOO000O0O0OOO0OO ):#line:919
        ""#line:924
        public .set_module_logs ('binlog','export_data')#line:925
        if not os .path .exists ('/temp'):os .makedirs ('/temp')#line:926
        O0000O0OOO0OOOOO0 ={}#line:927
        O00O00O000O00O00O ='tables'if 'table_name'in OOOO000O0O0OOO0OO else 'databases'#line:929
        O00OOOO00OOO0O000 =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(OOOO000O0O0OOO0OO .datab_name ,O00O00O000O00O00O )).find ()#line:930
        if not O00OOOO00OOO0O000 :return public .returnMsg (False ,'增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试下载！')#line:931
        OOOO0O0O000000OOO ,O00O0O00OOOO00OOO ,OOOO0O0OO0OO0OO0O ,OO0OO00O000O0OOO0 ,OO00O0O0OOO0O00O0 ,O00O00O0O0O0000OO ,O0000OOO00OOO0OOO ,OOO000O0O0OOO00OO =O0OOO0OO0OO0OO0OO .check_cloud_oss (O00OOOO00OOO0O000 )#line:932
        O0OOO0OO0OO0OO0OO ._db_name =OOOO000O0O0OOO0OO .datab_name #line:933
        O0OOO0OO0OO0OO0OO ._tables =OOOO000O0O0OOO0OO .table_name if 'table_name'in OOOO000O0O0OOO0OO else ''#line:934
        O0OOO0OO0OO0OO0OO ._zip_password =O00OOOO00OOO0O000 ['zip_password']#line:935
        OO0OO0O00O000OO0O =O0OOO0OO0OO0OO0OO ._save_default_path +OOOO000O0O0OOO0OO .datab_name +'/'+O00O00O000O00O00O +'/'+O0OOO0OO0OO0OO0OO ._tables +'/'#line:936
        OO0OO0O00O000OO0O =OO0OO0O00O000OO0O .replace ('//','/')#line:937
        O00OOO000OOOO000O =os .path .join (OO0OO0O00O000OO0O ,'full_record.json')#line:938
        OOOOOOO00O00OO0O0 =os .path .join (OO0OO0O00O000OO0O ,'inc_record.json')#line:939
        if not os .path .isfile (O00OOO000OOOO000O ):#line:941
            O0OOO0OO0OO0OO0OO .auto_download_file (O0000OOO00OOO0OOO ,O00OOO000OOOO000O )#line:943
        if os .path .isfile (O00OOO000OOOO000O ):#line:944
            OO00O0OO0000OOOOO =json .loads (public .readFile (O00OOO000OOOO000O ))#line:945
            if not os .path .isfile (OO00O0OO0000OOOOO [0 ]['full_name']):#line:947
                O0OOO0OO0OO0OO0OO .auto_download_file (O0000OOO00OOO0OOO ,OO00O0OO0000OOOOO [0 ]['full_name'],OO00O0OO0000OOOOO [0 ]['size'])#line:949
            if not os .path .isfile (OO00O0OO0000OOOOO [0 ]['full_name']):#line:950
                return public .returnMsg (False ,'全量备份数据不存在！')#line:951
        else :#line:952
            return public .returnMsg (False ,'全量备份数据不存在！')#line:953
        OOO00000O0OOOOO0O =OO00O0OO0000OOOOO [0 ]['time']#line:954
        O0000OOOO00OO0O0O =OOOO000O0O0OOO0OO .end_time .replace (' ','__').replace (':','-')#line:955
        OO0OOO0OO00O0O0OO ="db-{}---{}.tar.gz".format (OOOO000O0O0OOO0OO .datab_name ,O0000OOOO00OO0O0O )#line:956
        OO0OOO0OO00O0O0OO ="db-{}---{}---{}.tar.gz".format (OOOO000O0O0OOO0OO .datab_name ,O0OOO0OO0OO0OO0OO ._tables ,O0000OOOO00OO0O0O )if 'table_name'in OOOO000O0O0OOO0OO else OO0OOO0OO00O0O0OO #line:957
        O0OOO0O0OO00O00OO =OO00O0OO0000OOOOO [0 ]['full_name']+' '+O00OOO000OOOO000O #line:959
        if os .path .isfile (OOOOOOO00O00OO0O0 ):#line:960
            O0OOO0O0OO00O00OO =O0OOO0O0OO00O00OO +' '+OOOOOOO00O00OO0O0 #line:961
        OO0000O0O0OO00O0O =[]#line:964
        if os .path .isfile (OOOOOOO00O00OO0O0 ):#line:965
            OO0000O0O0OO00O0O =json .loads (public .readFile (OOOOOOO00O00OO0O0 ))#line:966
            if not OO0000O0O0OO00O0O [0 ]['full_name']:OO0000O0O0OO00O0O =[]#line:967
        O0OOO0OO0OO0OO0OO .update_file_info (O00OOO000OOOO000O ,OOOO000O0O0OOO0OO .end_time )#line:968
        OOO0OOO00O000O0O0 =''#line:969
        OOO000OO00O0OO000 =''#line:970
        if OOOO000O0O0OOO0OO .end_time !=OOO00000O0OOOOO0O :#line:971
            OOO0OOO0O0O0O000O =O0OOO0OO0OO0OO0OO .get_every_day (OOO00000O0OOOOO0O .split ()[0 ],OOOO000O0O0OOO0OO .end_time .split ()[0 ])#line:972
            O000O0OO00OO0OO00 =O0OOO0OO0OO0OO0OO .get_start_end_binlog (OOO00000O0OOOOO0O ,OOOO000O0O0OOO0OO .end_time )#line:973
            if OOOO000O0O0OOO0OO .end_time ==OOOO000O0O0OOO0OO .end_time .split (':')[0 ]+':00:00':#line:975
                O000O0OO00OO0OO00 ['end']=O000O0OO00OO0OO00 ['end'][:-1 ]#line:976
            OOOO00OO0O0OOOOOO =O0OOO0OO0OO0OO0OO .traverse_all_files (OO0OO0O00O000OO0O ,OOO0OOO0O0O0O000O ,O000O0OO00OO0OO00 )#line:977
            if OOOO00OO0O0OOOOOO and OOOO00OO0O0OOOOOO ['file_lists_not']:#line:979
                print ('自动下载前：以下文件不存在{}'.format (OOOO00OO0O0OOOOOO ['file_lists_not']))#line:980
                for OOOOOOO00O00OO0O0 in OOOO00OO0O0OOOOOO ['file_lists_not']:#line:981
                    for OO0O0O00000O000O0 in OOOOOOO00O00OO0O0 :#line:982
                        if not os .path .exists (os .path .dirname (OO0O0O00000O000O0 )):os .makedirs (os .path .dirname (OO0O0O00000O000O0 ))#line:983
                        OO000O00000OO000O =public .M ('mysqlbinlog_backups').where ('sid=? and local_name=?',(O00OOOO00OOO0O000 ['id'],OO0O0O00000O000O0 )).find ()#line:984
                        OO0OOOO000000OOOO =1024 #line:985
                        if OO000O00000OO000O and 'size'in OO000O00000OO000O :OO0OOOO000000OOOO =OO000O00000OO000O ['size']#line:986
                        O0OOO0OO0OO0OO0OO .auto_download_file (O0000OOO00OOO0OOO ,OO0O0O00000O000O0 ,OO0OOOO000000OOOO )#line:987
                OOOO00OO0O0OOOOOO =O0OOO0OO0OO0OO0OO .traverse_all_files (OO0OO0O00O000OO0O ,OOO0OOO0O0O0O000O ,O000O0OO00OO0OO00 )#line:989
            if OOOO00OO0O0OOOOOO ['status']=='False':#line:990
                return public .returnMsg (False ,'选择指定时间段的数据不完整！')#line:991
            for O000O00OOO00OO0OO in range (len (OOOO00OO0O0OOOOOO ['data'])):#line:993
                for OOO0O0OO0000O0OO0 in OOOO00OO0O0OOOOOO ['data'][O000O00OOO00OO0OO ]:#line:994
                    OOOO00O0000O0O0O0 =' '+OOO0O0OO0000O0OO0 #line:995
                    O0OOO0O0OO00O00OO +=OOOO00O0000O0O0O0 #line:996
                    if not O000O0OO00OO0OO00 ['end']:continue #line:997
                    OO000OOOOOOO0O000 =''#line:998
                    if OOO0O0OO0000O0OO0 ==OOOO00OO0O0OOOOOO ['last']:#line:999
                        OO000OOOOOOO0O000 ='end'#line:1000
                    if OO000OOOOOOO0O000 :#line:1001
                        OO00000OO000O0O00 =os .path .dirname (OOO0O0OO0000O0OO0 )+'/'#line:1002
                        if OO000OOOOOOO0O000 =='end':#line:1003
                            OOO0OO0OOO00O0OOO =OOOO000O0O0OOO0OO .end_time #line:1004
                        OOO00O00000O0O0OO ,OO0O0OO0O0O0OO0O0 =O0OOO0OO0OO0OO0OO .extract_file_content (OOO0O0OO0000O0OO0 ,OOO0OO0OOO00O0OOO )#line:1006
                        OOO00O00000O0O0OO =OOO00O00000O0O0OO .replace ('//','/')#line:1007
                        OOO0000O0O0OO000O =O0OOO0OO0OO0OO0OO .create_extract_file (OOO00O00000O0O0OO ,OO0O0OO0O0O0OO0O0 )#line:1009
                        O0OOOO0O000OOO0OO =public .readFile (OOO0000O0O0OO000O )#line:1010
                        os .system ('rm -rf {}'.format (OO00000OO000O0O00 +'test/'))#line:1011
                        if os .path .isfile (OOO0O0OO0000O0OO0 ):#line:1013
                            os .system ('mv -f {} {}'.format (OOO0O0OO0000O0OO0 ,OOO0O0OO0000O0OO0 +'.bak'))#line:1014
                            OOO0OOO00O000O0O0 =OOO0O0OO0000O0OO0 +'.bak'#line:1015
                        if not os .path .isfile (OOO0O0OO0000O0OO0 +'.bak'):continue #line:1016
                        public .writeFile (OOO00O00000O0O0OO ,O0OOOO0O000OOO0OO )#line:1017
                        O0OOO0OO0OO0OO0OO .zip_file (OOO00O00000O0O0OO )#line:1018
        if OOO0OOO00O000O0O0 :#line:1020
            O00O00000O0O0O00O =''#line:1021
            for O000O00OOO00OO0OO in OO0000O0O0OO00O0O :#line:1022
                if O000O00OOO00OO0OO ['full_name']==OOO0OOO00O000O0O0 .replace ('.bak',''):#line:1023
                    O00O00000O0O0O00O =O000O00OOO00OO0OO #line:1024
                    break #line:1025
            if O00O00000O0O0O00O :#line:1026
                OOO000OO00O0OO000 =OO0000O0O0OO00O0O [:OO0000O0O0OO00O0O .index (O00O00000O0O0O00O )+1 ]#line:1027
                public .writeFile (OOOOOOO00O00OO0O0 ,json .dumps (OOO000OO00O0OO000 ))#line:1028
        O0OOO0O0OO00O00OO =O0OOO0O0OO00O00OO .replace (O0OOO0OO0OO0OO0OO ._save_default_path ,'./')#line:1031
        OOOOO0000OO0O000O =O0OOO0OO0OO0OO0OO ._save_default_path +OO0OOO0OO00O0O0OO #line:1033
        O0000O0OOO0OOOOO0 ['name']='/temp/'+OO0OOO0OO00O0O0OO #line:1035
        O0O000O0O00O000O0 =os .system ('cd {} && tar -czf {} {} -C {}'.format (O0OOO0OO0OO0OO0OO ._save_default_path ,OO0OOO0OO00O0O0OO ,O0OOO0O0OO00O00OO ,'/temp'))#line:1036
        public .writeFile (O00OOO000OOOO000O ,json .dumps (OO00O0OO0000OOOOO ))#line:1039
        if OO0000O0O0OO00O0O :#line:1040
            public .writeFile (OOOOOOO00O00OO0O0 ,json .dumps (OO0000O0O0OO00O0O ))#line:1041
        if OOO0OOO00O000O0O0 :os .system ('mv -f {} {}'.format (OOO0OOO00O000O0O0 ,OOO0OOO00O000O0O0 .replace ('.bak','')))#line:1042
        if os .path .isfile (OOOOO0000OO0O000O ):os .system ('mv -f {} {}'.format (OOOOO0000OO0O000O ,O0000O0OOO0OOOOO0 ['name']))#line:1043
        if not os .path .isfile (O0000O0OOO0OOOOO0 ['name']):return public .returnMsg (False ,'导出数据文件{}失败'.format (O0000O0OOO0OOOOO0 ['name']))#line:1044
        for OO0O000O00OO0O00O in os .listdir ('/temp'):#line:1046
            if not OO0O000O00OO0O00O :continue #line:1047
            if os .path .isfile (os .path .join ('/temp',OO0O000O00OO0O00O ))and OO0O000O00OO0O00O .find ('.tar.gz')!=-1 and OO0O000O00OO0O00O .find ('-')!=-1 and OO0O000O00OO0O00O .find ('---')!=-1 and OO0O000O00OO0O00O .split ('-')[0 ]=='db'and OO0O000O00OO0O00O !=OO0OOO0OO00O0O0OO :#line:1048
                OOOOO0OOO0O0OO0O0 ="([0-9]{4})-([0-9]{2})-([0-9]{2})"#line:1049
                O0OO00OOO00O0O00O ="([0-9]{2})-([0-9]{2})-([0-9]{2})"#line:1050
                OOO0O0OO0000O0OO0 =re .search (OOOOO0OOO0O0OO0O0 ,str (OO0O000O00OO0O00O ))#line:1051
                O0O0O0OO0OO0O0OO0 =re .search (O0OO00OOO00O0O00O ,str (OO0O000O00OO0O00O ))#line:1052
                if OOO0O0OO0000O0OO0 and O0O0O0OO0OO0O0OO0 :#line:1053
                    os .remove (os .path .join ('/temp',OO0O000O00OO0O00O ))#line:1054
        return O0000O0OOO0OOOOO0 #line:1062
    def extract_file_content (O00OOOOO0OOO0O0O0 ,O0O0OO0OO0O0OO0O0 ,O0OO0O0OO000O0OO0 ):#line:1064
        ""#line:1070
        O0OOOOOOO0O00O000 =O00OOOOO0OOO0O0O0 .unzip_file (O0O0OO0OO0O0OO0O0 )#line:1071
        OOOOOOOOO00O0OOO0 =O0OOOOOOO0O00O000 ['name']#line:1072
        OOOOO0OO00OO0OO0O =open (OOOOOOOOO00O0OOO0 ,'r')#line:1073
        O0OOOOO0O00O0OOO0 =''#line:1074
        O0O00OO0OO0OO0OOO =O0OO0O0OO000O0OO0 .split ()[1 ].split (':')[1 ]#line:1075
        OO0OO0O00OOO00000 =O0OO0O0OO000O0OO0 .split ()[1 ].split (':')[2 ]#line:1076
        for OOOO0O0O0OO00000O in OOOOO0OO00OO0OO0O .readlines ():#line:1077
            if OOOO0O0O0OO00000O [0 ]!='#':continue #line:1078
            if len (OOOO0O0O0OO00000O .split ()[1 ].split (':'))<3 :continue #line:1079
            if OOOO0O0O0OO00000O .split ()[1 ].split (':')[1 ]==O0O00OO0OO0OO0OOO :#line:1080
                if OOOO0O0O0OO00000O .split ()[1 ].split (':')[2 ]>OO0OO0O00OOO00000 :#line:1081
                    break #line:1082
            if OOOO0O0O0OO00000O .split ()[1 ].split (':')[1 ]>O0O00OO0OO0OO0OOO :#line:1083
                break #line:1084
            O0OOOOO0O00O0OOO0 =OOOO0O0O0OO00000O .strip ()#line:1085
        OOOOO0OO00OO0OO0O .close #line:1086
        return OOOOOOOOO00O0OOO0 ,O0OOOOO0O00O0OOO0 #line:1087
    def create_extract_file (O0OO0OOO0O00O00OO ,O0OO0OO0OO0O0O0O0 ,O0OOOO0O0000O0OO0 ,is_start =False ):#line:1089
        ""#line:1097
        O0OOOO000OO0O0OOO =os .path .dirname (O0OO0OO0OO0O0O0O0 )+'/test/'#line:1098
        if not os .path .exists (O0OOOO000OO0O0OOO ):os .makedirs (O0OOOO000OO0O0OOO )#line:1099
        OO000OO0O000000O0 =os .path .basename (O0OO0OO0OO0O0O0O0 )#line:1100
        OOOO0OOO0000000O0 =O0OOOO000OO0O0OOO +OO000OO0O000000O0 #line:1101
        O0O0O00O00O0OO000 =open (O0OO0OO0OO0O0O0O0 ,'r')#line:1102
        OO00OOO0O0OOO00O0 =open (OOOO0OOO0000000O0 ,"w",encoding ="utf-8")#line:1103
        OOO0OOO00O0OOO0O0 =True #line:1104
        for OO0O0OO00O0OO0000 in O0O0O00O00O0OO000 .readlines ():#line:1105
            OO000OOO0000OO0O0 =re .search (O0OOOO0O0000O0OO0 ,OO0O0OO00O0OO0000 )#line:1106
            if is_start :#line:1107
                if OOO0OOO00O0OOO0O0 ==True :#line:1108
                    if OO000OOO0000OO0O0 :#line:1109
                        OOO0OOO00O0OOO0O0 =False #line:1110
                    continue #line:1111
                else :#line:1112
                    OO00OOO0O0OOO00O0 .write (OO0O0OO00O0OO0000 )#line:1113
            else :#line:1114
                if not OOO0OOO00O0OOO0O0 :break #line:1115
                OO00OOO0O0OOO00O0 .write (OO0O0OO00O0OO0000 )#line:1116
            if OO000OOO0000OO0O0 :#line:1117
                OOO0OOO00O0OOO0O0 =False #line:1118
        O0O0O00O00O0OO000 .close #line:1119
        OO00OOO0O0OOO00O0 .close #line:1120
        return OOOO0OOO0000000O0 #line:1121
    def import_start_end (OOOOOO0OOO0O0O00O ,O00OOO000O000OO0O ,O0O00OOOOOO00O0O0 ):#line:1123
        ""#line:1129
        O0O00OOOOOO00O0O0 =public .to_date (times =O0O00OOOOOO00O0O0 )#line:1130
        O00OOO000O000OO0O =public .to_date (times =O00OOO000O000OO0O )#line:1131
        O00OOO000O000OO0O =OOOOOO0OOO0O0O00O .get_format_date_of_time (True ,O00OOO000O000OO0O )#line:1132
        O00OOO000O000OO0O =public .to_date (times =O00OOO000O000OO0O )#line:1133
        OOOOOO0OOO0O0O00O ._start_time_list .append (O00OOO000O000OO0O )#line:1134
        while True :#line:1135
            O00OOO000O000OO0O +=OOOOOO0OOO0O0O00O ._save_cycle #line:1136
            OOOOOO0OOO0O0O00O ._start_time_list .append (O00OOO000O000OO0O )#line:1137
            if O00OOO000O000OO0O +OOOOOO0OOO0O0O00O ._save_cycle >O0O00OOOOOO00O0O0 :#line:1138
                break #line:1139
        OO0O0OOO0OOOOOOOO =[]#line:1140
        if OOOOOO0OOO0O0O00O ._start_time_list :#line:1141
            O0OOOO00OOO0O0O00 =(datetime .datetime .now ()+datetime .timedelta (hours =1 )).strftime ("%Y-%m-%d %H")+":00:00"#line:1142
            for OOO000OOOOOO0000O in OOOOOO0OOO0O0O00O ._start_time_list :#line:1144
                O0OOOOO0O0OOOO000 ={}#line:1145
                OO00OO000O0O0OOOO =float (OOO000OOOOOO0000O )#line:1146
                OOOO0O0O00OO0O0O0 =float (OOO000OOOOOO0000O )+OOOOOO0OOO0O0O00O ._save_cycle #line:1147
                if OO00OO000O0O0OOOO <public .to_date (times =json .loads (public .readFile (OOOOOO0OOO0O0O00O ._full_file ))[0 ]['time']):#line:1148
                    O00OOO000O000OO0O =json .loads (public .readFile (OOOOOO0OOO0O0O00O ._full_file ))[0 ]['time']#line:1150
                else :#line:1151
                    O00OOO000O000OO0O =public .format_date (times =OO00OO000O0O0OOOO )#line:1152
                if public .to_date (times =O00OOO000O000OO0O )>public .to_date (times =O0OOOO00OOO0O0O00 ):continue #line:1153
                if OOOO0O0O00OO0O0O0 >public .to_date (times =O0OOOO00OOO0O0O00 ):continue #line:1154
                O0O00OOOOOO00O0O0 =public .format_date (times =OOOO0O0O00OO0O0O0 )#line:1155
                O0OOOOO0O0OOOO000 ['start_time']=O00OOO000O000OO0O #line:1156
                O0OOOOO0O0OOOO000 ['end_time']=O0O00OOOOOO00O0O0 #line:1157
                OO0O0OOO0OOOOOOOO .append (O0OOOOO0O0OOOO000 )#line:1158
        return OO0O0OOO0OOOOOOOO #line:1159
    def import_date (OO000OO00O0000O00 ,OO0OOO00OOO000000 ,OOO00O0OOO0OO000O ):#line:1161
        ""#line:1167
        O0O00OOOOO0000O0O =time .time ()#line:1169
        OOOO0O0O00OO000O0 =public .to_date (times =OO0OOO00OOO000000 )#line:1170
        OO0OO00OO0O0O00O0 =OO000OO00O0000O00 .get_format_date (OOOO0O0O00OO000O0 )#line:1171
        O00O0000OOOO0OO00 =OO0OO00OO0O0O00O0 .split ('_')[0 ]#line:1172
        if OO000OO00O0000O00 ._save_default_path [-1 ]=='/':OO000OO00O0000O00 ._save_default_path =OO000OO00O0000O00 ._save_default_path [:-1 ]#line:1174
        O0O0OO0O0OOO0OOOO =OO000OO00O0000O00 ._save_default_path +'/'+O00O0000OOOO0OO00 +'/'#line:1175
        OOO0000000000O00O =OO000OO00O0000O00 ._temp_path +OO000OO00O0000O00 ._db_name +'/'+O00O0000OOOO0OO00 +'/'#line:1176
        if not os .path .exists (O0O0OO0O0OOO0OOOO ):os .makedirs (O0O0OO0O0OOO0OOOO )#line:1177
        if not os .path .exists (OOO0000000000O00O ):os .makedirs (OOO0000000000O00O )#line:1178
        if OO000OO00O0000O00 ._save_cycle ==3600 :#line:1179
            OO0OO00OO0O0O00O0 =OO0OO00OO0O0O00O0 .split ('_')[0 ]+'_'+OO0OO00OO0O0O00O0 .split ('_')[1 ].split ('-')[0 ]#line:1180
        else :#line:1181
            pass #line:1182
        O0OO0O000O0000OO0 ='{}{}.sql'.format (O0O0OO0O0OOO0OOOO ,OO0OO00OO0O0O00O0 )#line:1183
        O0O00O00O0O0OO0OO ='{}{}.sql'.format (OOO0000000000O00O ,OO0OO00OO0O0O00O0 )#line:1184
        OO0O00OOOOO00OOOO =O0OO0O000O0000OO0 .replace ('.sql','.zip')#line:1185
        OO000OO00O0000O00 ._backup_full_list .append (OO0O00OOOOO00OOOO )#line:1186
        if OOO00O0OOO0OO000O ==OO000OO00O0000O00 ._backup_end_time :#line:1187
            if os .path .isfile (OO0O00OOOOO00OOOO ):os .remove (OO0O00OOOOO00OOOO )#line:1188
        print ("|-导出{}".format (O0OO0O000O0000OO0 ),end ='')#line:1189
        if not os .path .exists (O0O00O00O0O0OO0OO ):#line:1190
            O00OOO0OOOOOOO00O ="{} --open-files-limit=1024 --start-datetime='{}' --stop-datetime='{}' -d {} {} > {} 2>/dev/null".format (OO000OO00O0000O00 ._mysqlbinlog_bin ,OO0OOO00OOO000000 ,OOO00O0OOO0OO000O ,OO000OO00O0000O00 ._db_name ,OO000OO00O0000O00 .get_binlog_file (OOOO0O0O00OO000O0 ),O0O00O00O0O0OO0OO )#line:1191
            os .system (O00OOO0OOOOOOO00O )#line:1192
        if not os .path .exists (O0O00O00O0O0OO0OO ):#line:1193
            OO000OO00O0000O00 ._backup_fail_list .append (OO0O00OOOOO00OOOO )#line:1194
            raise Exception ('从二进制日志导出sql文件失败!')#line:1195
        O0O00O00OO0OO0O0O =''#line:1196
        if not OO000OO00O0000O00 ._tables :#line:1197
            if OO000OO00O0000O00 ._pdata and OO000OO00O0000O00 ._pdata ['table_list']:#line:1198
                O0O00O00OO0OO0O0O ='|'.join (list (set (OO000OO00O0000O00 ._pdata ['table_list'].split ('|')).union (set (OO000OO00O0000O00 ._new_tables ))))#line:1199
        else :#line:1200
            O0O00O00OO0OO0O0O =OO000OO00O0000O00 ._tables #line:1201
        os .system ('cat {} |grep -Ee "({})" > {}'.format (O0O00O00O0O0OO0OO ,O0O00O00OO0OO0O0O ,O0OO0O000O0000OO0 ))#line:1206
        if os .path .exists (O0O00O00O0O0OO0OO ):os .remove (O0O00O00O0O0OO0OO )#line:1208
        if not os .path .exists (O0OO0O000O0000OO0 ):#line:1209
            OO000OO00O0000O00 ._backup_fail_list .append (OO0O00OOOOO00OOOO )#line:1210
            raise Exception ('导出sql文件失败!')#line:1211
        print (" ==> 成功")#line:1212
        if OO000OO00O0000O00 ._compress :#line:1213
            _OOOO0O00000O00O0O =OO000OO00O0000O00 .zip_file (O0OO0O000O0000OO0 )#line:1214
        else :#line:1215
            _OOOO0O00000O00O0O =os .path .getsize (O0OO0O000O0000OO0 )#line:1216
        print ("|-文件大小: {}MB, 耗时: {}秒".format (round (_OOOO0O00000O00O0O /1024 /1024 ,2 ),round (time .time ()-O0O00OOOOO0000O0O ,2 )))#line:1217
        print ("-"*60 )#line:1218
    def get_date_folder (O0OOOOOOO0O00OOOO ,OOO000OOOOO0OOOO0 ):#line:1220
        ""#line:1226
        O0OOOO0OOO0OOO000 =[]#line:1227
        for O0000O0OOOOO0OOO0 in os .listdir (OOO000OOOOO0OOOO0 ):#line:1228
            if os .path .isdir (os .path .join (OOO000OOOOO0OOOO0 ,O0000O0OOOOO0OOO0 )):#line:1229
                O000O000OOOOOO0O0 ="([0-9]{4})-([0-9]{2})-([0-9]{2})"#line:1230
                OO0OO0O0O0O00O00O =re .search (O000O000OOOOOO0O0 ,str (O0000O0OOOOO0OOO0 ))#line:1231
                if OO0OO0O0O0O00O00O :#line:1232
                    O0OOOO0OOO0OOO000 .append (OO0OO0O0O0O00O00O [0 ])#line:1233
        return O0OOOO0OOO0OOO000 #line:1234
    def kill_process (O0OO0O00OO000000O ):#line:1236
        ""#line:1240
        for O0O0O0OOOO000OO00 in range (3 ):#line:1241
            OOO00O000O0OO0O0O ="'{} {} --db_name {} --binlog_id'".format (O0OO0O00OO000000O ._python_path ,O0OO0O00OO000000O ._binlogModel_py ,O0OO0O00OO000000O ._db_name )#line:1242
            OO0OOOOO0O000O00O =os .popen ('ps aux | grep {} |grep -v grep'.format (OOO00O000O0OO0O0O ))#line:1243
            OO0000O0O0000000O =OO0OOOOO0O000O00O .read ()#line:1244
            for O0O0O0OOOO000OO00 in OO0000O0O0000000O .strip ().split ('\n'):#line:1245
                if len (O0O0O0OOOO000OO00 .split ())<16 :continue #line:1246
                OO00O0O0O0O0O0000 =int (O0O0O0OOOO000OO00 .split ()[9 ].split (':')[0 ])#line:1247
                OOO000OOOOOO0OO00 =O0O0O0OOOO000OO00 .split ()[1 ]#line:1248
                if not public .M ('mysqlbinlog_backup_setting').where ('id=?',O0O0O0OOOO000OO00 .split ()[15 ]).count ()and OO00O0O0O0O0O0000 >10 :#line:1249
                    os .kill (OOO000OOOOOO0OO00 )#line:1250
                if OO00O0O0O0O0O0000 >50 :#line:1251
                    os .kill (OOO000OOOOOO0OO00 )#line:1252
                if O0OO0O00OO000000O ._binlog_id :#line:1253
                    if O0O0O0OOOO000OO00 .split ()[15 ]==str (O0OO0O00OO000000O ._binlog_id )and OO00O0O0O0O0O0000 >0 :#line:1254
                        os .kill (OOO000OOOOOO0OO00 )#line:1255
        OO0OOOOO0O000O00O =os .popen ('ps aux | grep {} |grep -v grep'.format (OOO00O000O0OO0O0O ))#line:1256
        return OO0OOOOO0O000O00O .read ().strip ().split ('\n')#line:1257
    def full_backup (OO00O000OO00000O0 ):#line:1259
        ""#line:1264
        O0000000OO00O00OO =OO00O000OO00000O0 ._save_default_path +'full_record.json'#line:1265
        O000OO0000000O0O0 =O0000000OO00O00OO .replace ('full','inc')#line:1266
        O0OO00OO0O000O00O =public .get_mysqldump_bin ()#line:1267
        OO000OOO0O00O0O0O =public .format_date ("%Y%m%d_%H%M%S")#line:1268
        if OO00O000OO00000O0 ._tables :#line:1270
            O000O0O0O00OOOOO0 =OO00O000OO00000O0 ._save_default_path +'db_{}_{}_{}.sql'.format (OO00O000OO00000O0 ._db_name ,OO00O000OO00000O0 ._tables ,OO000OOO0O00O0O0O )#line:1271
            O0OO00OOO0O0OOO00 ='{} -uroot -p{} {} {} > {} 2>/dev/null'.format (O0OO00OO0O000O00O ,OO00O000OO00000O0 ._mysql_root_password ,OO00O000OO00000O0 ._db_name ,OO00O000OO00000O0 ._tables ,O000O0O0O00OOOOO0 )#line:1272
        else :#line:1274
            O000O0O0O00OOOOO0 =OO00O000OO00000O0 ._save_default_path +'db_{}_{}.sql'.format (OO00O000OO00000O0 ._db_name ,OO000OOO0O00O0O0O )#line:1275
            O0OO00OOO0O0OOO00 =O0OO00OO0O000O00O +" -E -R --default-character-set="+public .get_database_character (OO00O000OO00000O0 ._db_name )+" --force --hex-blob --opt "+OO00O000OO00000O0 ._db_name +" -u root -p"+str (OO00O000OO00000O0 ._mysql_root_password )+"> {} 2>/dev/null".format (O000O0O0O00OOOOO0 )#line:1276
        try :#line:1277
            os .system (O0OO00OOO0O0OOO00 )#line:1278
            if not os .path .isfile (O000O0O0O00OOOOO0 ):return False #line:1279
            OO00O000OO00000O0 .zip_file (O000O0O0O00OOOOO0 )#line:1280
        except Exception as OOO0O000OOOO0O0OO :#line:1281
            print (OOO0O000OOOO0O0OO )#line:1282
            return False #line:1283
        O00O00000OO0O0000 =O000O0O0O00OOOOO0 .replace ('.sql','.zip')#line:1284
        if not os .path .isfile (O00O00000OO0O0000 ):return False #line:1285
        OO00O000OO00000O0 .clean_local_full_backups (O0000000OO00O00OO ,os .path .basename (O00O00000OO0O0000 ),is_backup =True )#line:1287
        print ('|-已从磁盘清理过期备份文件')#line:1288
        OO00O000OO00000O0 .clean_local_inc_backups (O000OO0000000O0O0 )#line:1290
        OO00O000OO00000O0 ._full_zip_name =OO00O000OO00000O0 ._save_default_path +os .path .basename (O00O00000OO0O0000 )#line:1291
        if OO00O000OO00000O0 ._tables :#line:1292
            print ('|-完全备份数据库{}中表{}成功！'.format (OO00O000OO00000O0 ._db_name ,OO00O000OO00000O0 ._tables ))#line:1293
        else :#line:1294
            print ('|-完全备份数据库{}成功！'.format (OO00O000OO00000O0 ._db_name ))#line:1295
        return True #line:1296
    def clean_local_inc_backups (OOOO0OOO000000OO0 ,OOO0OO0OO00O0OOO0 ):#line:1298
        ""#line:1303
        O0OOO0O00000OO000 =OOOO0OOO000000OO0 .get_date_folder (OOOO0OOO000000OO0 ._save_default_path )#line:1304
        if O0OOO0O00000OO000 :#line:1305
            for O0O0000O0OO00OOO0 in O0OOO0O00000OO000 :#line:1306
                O0OOO0O000OOOO0OO =os .path .join (OOOO0OOO000000OO0 ._save_default_path ,O0O0000O0OO00OOO0 )#line:1307
                if os .path .exists (O0OOO0O000OOOO0OO ):shutil .rmtree (O0OOO0O000OOOO0OO )#line:1308
        if os .path .isfile (OOO0OO0OO00O0OOO0 ):#line:1309
            os .remove (OOO0OO0OO00O0OOO0 )#line:1310
    def clean_local_full_backups (OOO00OOO0OO0OOO0O ,OOOOO0OO0O0OOO00O ,check_name =None ,is_backup =False ,path =None ):#line:1312
        ""#line:1318
        if os .path .isfile (OOOOO0OO0O0OOO00O ):#line:1319
            OOOOO0000O000000O =OOO00OOO0OO0OOO0O .get_full_backup_file (OOO00OOO0OO0OOO0O ._db_name ,OOO00OOO0OO0OOO0O ._save_default_path )#line:1320
            for OOOOOOOO0O000O000 in OOOOO0000O000000O :#line:1321
                OOOOO00OOOO0O0OO0 =os .path .join (OOO00OOO0OO0OOO0O ._save_default_path ,OOOOOOOO0O000O000 ['name'])#line:1322
                if is_backup :#line:1323
                    if OOOOOOOO0O000O000 ['name']!=check_name :OOO00OOO0OO0OOO0O .delete_file (OOOOO00OOOO0O0OO0 )#line:1324
                else :#line:1325
                    OOO00OOO0OO0OOO0O .delete_file (OOOOO00OOOO0O0OO0 )#line:1326
            if not is_backup :OOO00OOO0OO0OOO0O .delete_file (OOOOO0OO0O0OOO00O )#line:1327
    def check_cloud_oss (O0O0O0OOO0OOOOO00 ,O00OOO0000O0O0O00 ):#line:1328
        ""#line:1333
        OO00O00O0O0000OOO =alioss_main ()#line:1335
        O0000O0OOO00OOO0O =txcos_main ()#line:1336
        O000OOO0000000000 =qiniu_main ()#line:1337
        O000OO0OOOOOO000O =bos_main ()#line:1338
        O0O000O0OOOOO00O0 =obs_main ()#line:1339
        OO0O0OOO00O000000 =ftp_main ()#line:1340
        OO0OOOO00O00O0OOO =[]#line:1341
        O0OOO0OO000000000 =[]#line:1342
        OO000O00OOOOO0OO0 =OOO0OO0OOOOOO0O0O =OO00O000O0OO0OOOO =OO00OO0O00O00OO00 =OOOO000OO0O0OOOOO =O0O0000OOO0O0000O =False #line:1344
        if O00OOO0000O0O0O00 ['upload_alioss']=='alioss':#line:1346
            if OO00O00O0O0000OOO .check_config ():#line:1347
                OO0OOOO00O00O0OOO .append (OO00O00O0O0000OOO )#line:1348
                OO000O00OOOOO0OO0 =True #line:1349
            else :O0OOO0OO000000000 .append ('alioss')#line:1350
        if O00OOO0000O0O0O00 ['upload_txcos']=='txcos':#line:1352
            if O0000O0OOO00OOO0O .check_config ():#line:1353
                OO0OOOO00O00O0OOO .append (O0000O0OOO00OOO0O )#line:1354
                OOO0OO0OOOOOO0O0O =True #line:1355
            else :O0OOO0OO000000000 .append ('txcos')#line:1356
        if O00OOO0000O0O0O00 ['upload_qiniu']=='qiniu':#line:1358
            if O000OOO0000000000 .check_config ():#line:1359
                OO0OOOO00O00O0OOO .append (O000OOO0000000000 )#line:1360
                OO00O000O0OO0OOOO =True #line:1361
            else :O0OOO0OO000000000 .append ('qiniu')#line:1362
        if O00OOO0000O0O0O00 ['upload_bos']=='bos':#line:1364
            if O000OO0OOOOOO000O .check_config ():#line:1365
                OO0OOOO00O00O0OOO .append (O000OO0OOOOOO000O )#line:1366
                OO00OO0O00O00OO00 =True #line:1367
            else :O0OOO0OO000000000 .append ('bos')#line:1368
        if O00OOO0000O0O0O00 ['upload_obs']=='obs':#line:1370
            if O0O000O0OOOOO00O0 .check_config ():#line:1371
                OO0OOOO00O00O0OOO .append (O0O000O0OOOOO00O0 )#line:1372
                OOOO000OO0O0OOOOO =True #line:1373
            else :O0OOO0OO000000000 .append ('obs')#line:1374
        if O00OOO0000O0O0O00 ['upload_ftp']=='ftp':#line:1376
            if OO0O0OOO00O000000 .check_config ():#line:1377
                OO0OOOO00O00O0OOO .append (OO0O0OOO00O000000 )#line:1378
                O0O0000OOO0O0000O =True #line:1379
        return OO000O00OOOOO0OO0 ,OOO0OO0OOOOOO0O0O ,OO00O000O0OO0OOOO ,OO00OO0O00O00OO00 ,OOOO000OO0O0OOOOO ,O0O0000OOO0O0000O ,OO0OOOO00O00O0OOO ,O0OOO0OO000000000 #line:1380
    def execute_by_comandline (OO0O0O00OOO00OOO0 ,get =None ):#line:1383
        ""#line:1389
        if get :#line:1390
            OO0O0O00OOO00OOO0 ._db_name =get .databname #line:1391
            OO0O0O00OOO00OOO0 ._binlog_id =get .backup_id #line:1392
        O0OO0O000O00OO0OO =[]#line:1393
        OO0OO00000OO00O0O =OO0O0O00OOO00OOO0 .kill_process ()#line:1396
        if len (OO0OO00000OO00O0O )>0 :#line:1397
            time .sleep (0.01 )#line:1398
        OO0000OO0O0000O0O =False #line:1399
        OOOOOO00O00O00O0O =OO0O0O00OOO00OOO0 .get_binlog_status ()#line:1401
        if OOOOOO00O00O00O0O ['status']==False :#line:1402
            O000O0OO00OO00OO0 ='请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！'#line:1403
            print (O000O0OO00OO00OO0 )#line:1404
            OO0000OO0O0000O0O =True #line:1405
        OO0O0O00OOO00OOO0 ._db_mysql =OO0O0O00OOO00OOO0 ._db_mysql .set_host ('127.0.0.1',OO0O0O00OOO00OOO0 .get_mysql_port (),'','root',OO0O0O00OOO00OOO0 ._mysql_root_password )#line:1407
        O0O0OO0OOO00O00OO ,OO000OO00000O00O0 ,O0O0O0OO0O00000OO =OO0O0O00OOO00OOO0 ._mybackup .get_disk_free (OO0O0O00OOO00OOO0 ._save_default_path )#line:1408
        if not OO0000OO0O0000O0O :#line:1409
            O0000000OOO0OOO0O =''#line:1410
            try :#line:1411
                OO00OO0OO0OOO0O0O ="select sum(DATA_LENGTH)+sum(INDEX_LENGTH) from information_schema.tables where table_schema=%s"#line:1412
                OO0OOO0O0OO00O000 =(OO0O0O00OOO00OOO0 ._db_name ,)#line:1413
                OOOO0000O00OO0OO0 =OO0O0O00OOO00OOO0 ._db_mysql .query (OO00OO0OO0OOO0O0O ,True ,OO0OOO0O0OO00O000 )#line:1414
                O0000000OOO0OOO0O =OO0O0O00OOO00OOO0 ._mybackup .map_to_list (OOOO0000O00OO0OO0 )[0 ][0 ]#line:1415
            except :#line:1416
                OO0000OO0O0000O0O =True #line:1417
                O000O0OO00OO00OO0 ="数据库连接异常，请检查root用户权限或者数据库配置参数是否正确。"#line:1418
                print (O000O0OO00OO00OO0 )#line:1419
                O0OO0O000O00OO0OO .append (O000O0OO00OO00OO0 )#line:1420
            if O0000000OOO0OOO0O ==None :#line:1422
                O000O0OO00OO00OO0 ='指定数据库 `{}` 没有任何数据!'.format (OO0O0O00OOO00OOO0 ._db_name )#line:1423
                OO0000OO0O0000O0O =True #line:1424
                print (O000O0OO00OO00OO0 )#line:1425
                O0OO0O000O00OO0OO .append (O000O0OO00OO00OO0 )#line:1426
            if O0O0OO0OOO00O00OO :#line:1428
                if O0000000OOO0OOO0O :#line:1429
                    if OO000OO00000O00O0 <O0000000OOO0OOO0O :#line:1430
                        O000O0OO00OO00OO0 ="目标分区可用的磁盘空间小于{},无法完成备份，请增加磁盘容量!".format (public .to_size (O0000000OOO0OOO0O ))#line:1431
                        print (O000O0OO00OO00OO0 )#line:1432
                        OO0000OO0O0000O0O =True #line:1433
                        O0OO0O000O00OO0OO .append (O000O0OO00OO00OO0 )#line:1434
                if O0O0O0OO0O00000OO <OO0O0O00OOO00OOO0 ._inode_min :#line:1436
                    O000O0OO00OO00OO0 ="目标分区可用的Inode小于{},无法完成备份，请增加磁盘容量!".format (OO0O0O00OOO00OOO0 ._inode_min )#line:1437
                    print (O000O0OO00OO00OO0 )#line:1438
                    OO0000OO0O0000O0O =True #line:1439
                    O0OO0O000O00OO0OO .append (O000O0OO00OO00OO0 )#line:1440
        OO0O0O00OOO00OOO0 ._pdata =OOOO000O000O00000 =public .M ('mysqlbinlog_backup_setting').where ('id=?',str (OO0O0O00OOO00OOO0 ._binlog_id )).find ()#line:1443
        O00OO0OO0O00O0OO0 =OOOO000O000O00000 ['database_table']if OOOO000O000O00000 else OO0O0O00OOO00OOO0 ._db_name #line:1444
        OO0O0O00OOO00OOO0 ._echo_info ['echo']=public .M ('crontab').where ("sBody=?",('{} {} --db_name {} --binlog_id {}'.format (OO0O0O00OOO00OOO0 ._python_path ,OO0O0O00OOO00OOO0 ._binlogModel_py ,OO0O0O00OOO00OOO0 ._db_name ,str (OO0O0O00OOO00OOO0 ._binlog_id )),)).getField ('echo')#line:1446
        OO0O0O00OOO00OOO0 ._mybackup =backup (cron_info =OO0O0O00OOO00OOO0 ._echo_info )#line:1447
        if not OOOO000O000O00000 :#line:1448
            print ('未在数据库备份记录中找到id为{}的计划任务'.format (OO0O0O00OOO00OOO0 ._binlog_id ))#line:1449
            OO0000OO0O0000O0O =True #line:1450
        if OO0O0O00OOO00OOO0 ._db_name not in OO0O0O00OOO00OOO0 .get_tables_list (OO0O0O00OOO00OOO0 .get_databases ()):#line:1451
            print ('备份的数据库不存在')#line:1452
            OO0000OO0O0000O0O =True #line:1453
        if OO0000OO0O0000O0O :#line:1454
            OO0O0O00OOO00OOO0 .send_failture_notification (O0OO0O000O00OO0OO ,target =O00OO0OO0O00O0OO0 )#line:1456
            return public .returnMsg (False ,'备份失败')#line:1457
        OO0O0O00OOO00OOO0 ._zip_password =OOOO000O000O00000 ['zip_password']#line:1458
        if OOOO000O000O00000 ['backup_type']=='tables':OO0O0O00OOO00OOO0 ._tables =OOOO000O000O00000 ['tb_name']#line:1459
        OO0O0O00OOO00OOO0 ._save_default_path =OOOO000O000O00000 ['save_path']#line:1460
        print ("|-分区{}可用磁盘空间为：{},可用Inode为:{}".format (O0O0OO0OOO00O00OO ,public .to_size (OO000OO00000O00O0 ),O0O0O0OO0O00000OO ))#line:1461
        if not os .path .exists (OO0O0O00OOO00OOO0 ._save_default_path ):#line:1463
            os .makedirs (OO0O0O00OOO00OOO0 ._save_default_path )#line:1464
            O0000OO0O0O0O0000 =True #line:1465
        OO0O0O00OOO00OOO0 ._full_file =OO0O0O00OOO00OOO0 ._save_default_path +'full_record.json'#line:1466
        OO0O0O00OOO00OOO0 ._inc_file =O0O0O000OO0OOOOOO =OO0O0O00OOO00OOO0 ._save_default_path +'inc_record.json'#line:1467
        OOOO000O000O00000 ['last_excute_backup_time']=OO0O0O00OOO00OOO0 ._backup_end_time =public .format_date ()#line:1468
        OO0O0O00OOO00OOO0 ._tables =OOOO000O000O00000 ['tb_name']#line:1469
        OOOO0O0O0OO00O000 ='/tables/'+OO0O0O00OOO00OOO0 ._tables +'/'if OO0O0O00OOO00OOO0 ._tables else '/databases/'#line:1470
        OO0O0O00OOO00OOO0 ._backup_type ='tables'if OO0O0O00OOO00OOO0 ._tables else 'databases'#line:1471
        O0O0000000O00OOOO =OOOO000O000O00000 ['start_backup_time']#line:1473
        O00000O00OO0OOO0O =OOOO000O000O00000 ['end_backup_time']#line:1474
        O0000OO0O0O0O0000 =False #line:1475
        O00OOO0O00000OOO0 ={'alioss':'阿里云OSS','txcos':'腾讯云COS','qiniu':'七牛云存储','bos':'百度云存储','obs':'华为云存储'}#line:1476
        OOOOO0O0O000000O0 ,OOOOOO0OOO0O000OO ,O0OO00O0OOO0O00OO ,O00O0O0O00OO00OO0 ,O0OOO00000OOO00OO ,OOOOO0OOOO00000OO ,OO000O0OOOOO0000O ,O000OO0OO00OOO0OO =OO0O0O00OOO00OOO0 .check_cloud_oss (OOOO000O000O00000 )#line:1478
        if O000OO0OO00OOO0OO :#line:1479
            O0OO0O00000OO00O0 =[]#line:1480
            print ('检测到无法连接上以下云存储：')#line:1481
            for OOO0O00O0OO000OOO in O000OO0OO00OOO0OO :#line:1482
                if not OOO0O00O0OO000OOO :continue #line:1483
                O0OO0O00000OO00O0 .append (O00OOO0O00000OOO0 [OOO0O00O0OO000OOO ])#line:1484
                print ('{}'.format (O00OOO0O00000OOO0 [OOO0O00O0OO000OOO ]))#line:1485
            O000O0OO00OO00OO0 ='检测到无法连接上以下云存储：{}'.format (O0OO0O00000OO00O0 )#line:1486
            print ('请检查配置或者更改备份设置！')#line:1487
            OO0O0O00OOO00OOO0 .send_failture_notification (O000O0OO00OO00OO0 ,target =O00OO0OO0O00O0OO0 )#line:1489
            return public .returnMsg (False ,'备份失败')#line:1490
        if not os .path .isfile (OO0O0O00OOO00OOO0 ._full_file ):#line:1492
            OO0O0O00OOO00OOO0 .auto_download_file (OO000O0OOOOO0000O ,OO0O0O00OOO00OOO0 ._full_file )#line:1494
        O00O00O0O00O00OO0 ={}#line:1495
        if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file ):#line:1496
            try :#line:1497
                O00O00O0O00O00OO0 =json .loads (public .readFile (OO0O0O00OOO00OOO0 ._full_file ))[0 ]#line:1498
                if 'name'not in O00O00O0O00O00OO0 or 'size'not in O00O00O0O00O00OO0 or 'time'not in O00O00O0O00O00OO0 :O0000OO0O0O0O0000 =True #line:1499
                if 'end_time'in O00O00O0O00O00OO0 :#line:1500
                    if O00O00O0O00O00OO0 ['end_time']!=O00O00O0O00O00OO0 ['end_time'].split (':')[0 ]+':00:00':#line:1501
                        O00000O00OO0OOO0O =O00O00O0O00O00OO0 ['end_time'].split (':')[0 ]+':00:00'#line:1502
                if 'full_name'in O00O00O0O00O00OO0 and os .path .isfile (O00O00O0O00O00OO0 ['full_name'])and time .time ()-public .to_date (times =O0O0000000O00OOOO )>604800 :#line:1503
                    O0000OO0O0O0O0000 =True #line:1504
                if 'time'in O00O00O0O00O00OO0 :#line:1506
                    O0O0000000O00OOOO =O00O00O0O00O00OO0 ['time']#line:1507
                    if not os .path .isfile (OO0O0O00OOO00OOO0 ._inc_file )and O00000O00OO0OOO0O !=O00O00O0O00O00OO0 ['time']:#line:1508
                        OO0O0O00OOO00OOO0 .auto_download_file (OO000O0OOOOO0000O ,OO0O0O00OOO00OOO0 ._inc_file )#line:1510
                    if not os .path .isfile (OO0O0O00OOO00OOO0 ._inc_file )and O00000O00OO0OOO0O !=O00O00O0O00O00OO0 ['time']:#line:1511
                        print ('增量备份记录文件不存在,将执行完全备份')#line:1512
                        O0000OO0O0O0O0000 =True #line:1513
            except :#line:1514
                O00O00O0O00O00OO0 ={}#line:1515
                O0000OO0O0O0O0000 =True #line:1516
        else :#line:1517
            O0000OO0O0O0O0000 =True #line:1518
        OOOOOOOOOOOO00OOO =False #line:1519
        if O0000OO0O0O0O0000 :#line:1522
            print ('☆☆☆完全备份开始☆☆☆')#line:1523
            O0O000OOO0OOOO0OO =[]#line:1524
            if not OO0O0O00OOO00OOO0 .full_backup ():#line:1525
                O000O0OO00OO00OO0 ='全量备份数据库[{}]'.format (OO0O0O00OOO00OOO0 ._db_name )#line:1526
                OO0O0O00OOO00OOO0 .send_failture_notification (O000O0OO00OO00OO0 ,target =O00OO0OO0O00O0OO0 )#line:1527
                return public .returnMsg (False ,O000O0OO00OO00OO0 )#line:1528
            if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file ):#line:1529
                try :#line:1530
                    O0O000OOO0OOOO0OO =json .loads (public .readFile (OO0O0O00OOO00OOO0 ._full_file ))#line:1531
                except :#line:1532
                    O0O000OOO0OOOO0OO =[]#line:1533
            OO0O0O00OOO00OOO0 .set_file_info (OO0O0O00OOO00OOO0 ._full_zip_name ,OO0O0O00OOO00OOO0 ._full_file ,is_full =True )#line:1535
            try :#line:1536
                O00O00O0O00O00OO0 =json .loads (public .readFile (OO0O0O00OOO00OOO0 ._full_file ))[0 ]#line:1537
            except :#line:1538
                print ('|-文件写入失败，检查是否有安装安全软件！')#line:1539
                print ('|-备份失败！')#line:1540
                return #line:1541
            OOOO000O000O00000 ['start_backup_time']=OOOO000O000O00000 ['end_backup_time']=O00O00O0O00O00OO0 ['time']#line:1542
            public .M ('mysqlbinlog_backup_setting').where ('id=?',OOOO000O000O00000 ['id']).update (OOOO000O000O00000 )#line:1543
            O0O00O0O0O0000000 ='/bt_backup/mysql_bin_log/'+OO0O0O00OOO00OOO0 ._db_name +OOOO0O0O0OO00O000 #line:1544
            OO0O000OO00O0O00O =O0O00O0O0O0000000 +O00O00O0O00O00OO0 ['name']#line:1545
            O0O00O00000OOOOO0 =O0O00O0O0O0000000 +'full_record.json'#line:1546
            OO0O000OO00O0O00O =OO0O000OO00O0O00O .replace ('//','/')#line:1547
            O0O00O00000OOOOO0 =O0O00O00000OOOOO0 .replace ('//','/')#line:1548
            if OOOOO0O0O000000O0 :#line:1550
                O00O00OOOOO000OO0 =alioss_main ()#line:1551
                if not O00O00OOOOO000OO0 .upload_file_by_path (O00O00O0O00O00OO0 ['full_name'],OO0O000OO00O0O00O ):#line:1552
                        OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O00O00O0O00O00OO0 ['full_name'])#line:1553
                if not O00O00OOOOO000OO0 .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O0O00O00000OOOOO0 ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (OO0O0O00OOO00OOO0 ._full_file )#line:1554
                OO0O0O00OOO00OOO0 .clean_cloud_backups (O0O00O0O0O0000000 ,OO0O0O00OOO00OOO0 ._full_file ,O00O00OOOOO000OO0 ,O00OOO0O00000OOO0 ['alioss'])#line:1556
            else :#line:1557
                if OOOO000O000O00000 ['upload_alioss']=='alioss':#line:1558
                    O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['alioss'],O00OOO0O00000OOO0 ['alioss'])#line:1559
                    OOOOOOOOOOOO00OOO =True #line:1560
                    print (O000O0OO00OO00OO0 )#line:1561
            if OOOOOO0OOO0O000OO :#line:1563
                OOO00O000OO0O0OOO =txcos_main ()#line:1564
                if not OOO00O000OO0O0OOO .upload_file_by_path (O00O00O0O00O00OO0 ['full_name'],OO0O000OO00O0O00O ):#line:1565
                    OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O00O00O0O00O00OO0 ['full_name'])#line:1566
                if not OOO00O000OO0O0OOO .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O0O00O00000OOOOO0 ):#line:1567
                    OO0O0O00OOO00OOO0 ._cloud_upload_not .append (OO0O0O00OOO00OOO0 ._full_file )#line:1568
                OO0O0O00OOO00OOO0 .clean_cloud_backups (O0O00O0O0O0000000 ,OO0O0O00OOO00OOO0 ._full_file ,OOO00O000OO0O0OOO ,O00OOO0O00000OOO0 ['txcos'])#line:1570
            else :#line:1571
                if OOOO000O000O00000 ['upload_txcos']=='txcos':#line:1572
                    O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['txcos'],O00OOO0O00000OOO0 ['txcos'])#line:1573
                    OOOOOOOOOOOO00OOO =True #line:1574
                    print (O000O0OO00OO00OO0 )#line:1575
            if O0OO00O0OOO0O00OO :#line:1577
                OOOO0OO0O000O000O =qiniu_main ()#line:1578
                if not OOOO0OO0O000O000O .upload_file_by_path (O00O00O0O00O00OO0 ['full_name'],OO0O000OO00O0O00O ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O00O00O0O00O00OO0 ['full_name'])#line:1579
                if not OOOO0OO0O000O000O .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O0O00O00000OOOOO0 ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (OO0O0O00OOO00OOO0 ._full_file )#line:1580
                OO0O0O00OOO00OOO0 .clean_cloud_backups (O0O00O0O0O0000000 ,OO0O0O00OOO00OOO0 ._full_file ,OOOO0OO0O000O000O ,O00OOO0O00000OOO0 ['qiniu'])#line:1582
            else :#line:1583
                if OOOO000O000O00000 ['upload_qiniu']=='qiniu':#line:1584
                        O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['qiniu'],O00OOO0O00000OOO0 ['qiniu'])#line:1585
                        OOOOOOOOOOOO00OOO =True #line:1586
                        print (O000O0OO00OO00OO0 )#line:1587
            if O00O0O0O00OO00OO0 :#line:1589
                OOOO000OOO00000O0 =bos_main ()#line:1590
                if not OOOO000OOO00000O0 .upload_file_by_path (O00O00O0O00O00OO0 ['full_name'],OO0O000OO00O0O00O ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O00O00O0O00O00OO0 ['full_name'])#line:1591
                if not OOOO000OOO00000O0 .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O0O00O00000OOOOO0 ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (OO0O0O00OOO00OOO0 ._full_file )#line:1592
                OO0O0O00OOO00OOO0 .clean_cloud_backups (O0O00O0O0O0000000 ,OO0O0O00OOO00OOO0 ._full_file ,OOOO000OOO00000O0 ,O00OOO0O00000OOO0 ['bos'])#line:1594
            else :#line:1595
                if OOOO000O000O00000 ['upload_bos']=='bos':#line:1596
                        O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['bos'],O00OOO0O00000OOO0 ['bos'])#line:1597
                        OOOOOOOOOOOO00OOO =True #line:1598
                        print (O000O0OO00OO00OO0 )#line:1599
            if O0OOO00000OOO00OO :#line:1602
                OO0000O0OO0O00O00 =obs_main ()#line:1603
                if not OO0000O0OO0O00O00 .upload_file_by_path (O00O00O0O00O00OO0 ['full_name'],OO0O000OO00O0O00O ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O00O00O0O00O00OO0 ['full_name'])#line:1604
                if not OO0000O0OO0O00O00 .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O0O00O00000OOOOO0 ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (OO0O0O00OOO00OOO0 ._full_file )#line:1605
                OO0O0O00OOO00OOO0 .clean_cloud_backups (O0O00O0O0O0000000 ,OO0O0O00OOO00OOO0 ._full_file ,OO0000O0OO0O00O00 ,O00OOO0O00000OOO0 ['obs'])#line:1607
            else :#line:1608
                if OOOO000O000O00000 ['upload_obs']=='obs':#line:1609
                        O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['obs'],O00OOO0O00000OOO0 ['obs'])#line:1610
                        OOOOOOOOOOOO00OOO =True #line:1611
                        print (O000O0OO00OO00OO0 )#line:1612
            if OOOOO0OOOO00000OO :#line:1615
                OOO0O0OOOO00O0OO0 =ftp_main ()#line:1616
                if not OOO0O0OOOO00O0OO0 .upload_file_by_path (O00O00O0O00O00OO0 ['full_name'],OO0O000OO00O0O00O ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O00O00O0O00O00OO0 ['full_name'])#line:1617
                if not OOO0O0OOOO00O0OO0 .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O0O00O00000OOOOO0 ):OO0O0O00OOO00OOO0 ._cloud_upload_not .append (OO0O0O00OOO00OOO0 ._full_file )#line:1618
                OO0O0O00OOO00OOO0 .clean_cloud_backups (O0O00O0O0O0000000 ,OO0O0O00OOO00OOO0 ._full_file ,OOO0O0OOOO00O0OO0 ,O00OOO0O00000OOO0 ['ftp'])#line:1620
            else :#line:1621
                if OOOO000O000O00000 ['upload_ftp']=='ftp':#line:1622
                        O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['ftp'],O00OOO0O00000OOO0 ['ftp'])#line:1623
                        OOOOOOOOOOOO00OOO =True #line:1624
                        print (O000O0OO00OO00OO0 )#line:1625
            O000O0OO00OO00OO0 ='以下文件上传失败：{}'.format (OO0O0O00OOO00OOO0 ._cloud_upload_not )#line:1626
            if OO0O0O00OOO00OOO0 ._cloud_upload_not or OOOOOOOOOOOO00OOO :#line:1627
                OO0O0O00OOO00OOO0 .send_failture_notification (O000O0OO00OO00OO0 ,target =O00OO0OO0O00O0OO0 )#line:1628
                if O0O000OOO0OOOO0OO :public .writeFile (OO0O0O00OOO00OOO0 ._full_file ,json .dumps (O0O000OOO0OOOO0OO ))#line:1629
            print ('☆☆☆完全备份结束☆☆☆')#line:1630
            OOO0O00OOOOOO0OOO ='full'#line:1631
            OO00OOO00OO0OO00O =json .loads (public .readFile (OO0O0O00OOO00OOO0 ._full_file ))#line:1632
            OO0O0O00OOO00OOO0 .write_backups (OOO0O00OOOOOO0OOO ,OO00OOO00OO0OO00O )#line:1633
            if OOOO000O000O00000 ['upload_local']==''and os .path .isfile (OO0O0O00OOO00OOO0 ._full_file ):#line:1635
                OO0O0O00OOO00OOO0 .clean_local_full_backups (OO0O0O00OOO00OOO0 ._full_file )#line:1636
                if os .path .isfile (OO0O0O00OOO00OOO0 ._inc_file ):OO0O0O00OOO00OOO0 .clean_local_inc_backups (OO0O0O00OOO00OOO0 ._inc_file )#line:1637
                print ('|-用户设置不保留本地备份，已从本地服务器清理备份')#line:1638
            return public .returnMsg (True ,'完全备份成功！')#line:1639
        OO0O0O00OOO00OOO0 ._backup_add_time =OOOO000O000O00000 ['start_backup_time']#line:1641
        OO0O0O00OOO00OOO0 ._backup_start_time =O00000O00OO0OOO0O #line:1642
        OO0O0O00OOO00OOO0 ._new_tables =OO0O0O00OOO00OOO0 .get_tables_list (OO0O0O00OOO00OOO0 .get_tables ())#line:1643
        if OO0O0O00OOO00OOO0 ._backup_start_time and OO0O0O00OOO00OOO0 ._backup_end_time :#line:1644
            OOO00O0OOO0OO00OO =OO0O0O00OOO00OOO0 .import_start_end (OO0O0O00OOO00OOO0 ._backup_start_time ,OO0O0O00OOO00OOO0 ._backup_end_time )#line:1645
            for OOOO0O0OOOOO00O00 in OOO00O0OOO0OO00OO :#line:1646
                if not OOOO0O0OOOOO00O00 :continue #line:1647
                OO0O0O00OOO00OOO0 ._backup_fail_list =[]#line:1648
                if public .to_date (times =OOOO0O0OOOOO00O00 ['end_time'])>public .to_date (times =OO0O0O00OOO00OOO0 ._backup_end_time ):OOOO0O0OOOOO00O00 ['end_time']=OO0O0O00OOO00OOO0 ._backup_end_time #line:1649
                OO0O0O00OOO00OOO0 .import_date (OOOO0O0OOOOO00O00 ['start_time'],OOOO0O0OOOOO00O00 ['end_time'])#line:1650
        OO0O0O00O00OOOO0O =OOOO000O000O00000 ['save_path']#line:1652
        OOOOO000OO0OOO0OO =OO0O0O00OOO00OOO0 .get_every_day (OO0O0O00OOO00OOO0 ._backup_start_time .split ()[0 ],OO0O0O00OOO00OOO0 ._backup_end_time .split ()[0 ])#line:1653
        OO0OOOO0OOOO0O0O0 ='True'#line:1654
        O00O0O0OO00O00OOO =OO0O0O00OOO00OOO0 .get_start_end_binlog (OO0O0O00OOO00OOO0 ._backup_start_time ,OO0O0O00OOO00OOO0 ._backup_end_time ,OO0OOOO0OOOO0O0O0 )#line:1655
        OO0000O0O0OOOO0O0 =OO0O0O00OOO00OOO0 .traverse_all_files (OO0O0O00O00OOOO0O ,OOOOO000OO0OOO0OO ,O00O0O0OO00O00OOO )#line:1656
        if OO0O0O00OOO00OOO0 ._backup_fail_list or OO0000O0O0OOOO0O0 ['file_lists_not']:#line:1657
            O0OOO0OO00OOO0OOO =''#line:1658
            if OO0O0O00OOO00OOO0 ._backup_fail_list :O0OOO0OO00OOO0OOO =OO0O0O00OOO00OOO0 ._backup_fail_list #line:1659
            else :O0OOO0OO00OOO0OOO =OO0000O0O0OOOO0O0 ['file_lists_not']#line:1660
            O000O0OO00OO00OO0 ='以下文件备份失败{}'.format (O0OOO0OO00OOO0OOO )#line:1662
            OO0O0O00OOO00OOO0 .send_failture_notification (O000O0OO00OO00OO0 ,target =O00OO0OO0O00O0OO0 )#line:1664
            print (O000O0OO00OO00OO0 )#line:1665
            return public .returnMsg (False ,O000O0OO00OO00OO0 )#line:1666
        OOO0O00O00OO00O0O =json .loads (public .readFile (OO0O0O00OOO00OOO0 ._full_file ))#line:1667
        OOOO000O000O00000 ['end_backup_time']=OO0O0O00OOO00OOO0 ._backup_end_time #line:1669
        OOOO000O000O00000 ['table_list']='|'.join (OO0O0O00OOO00OOO0 ._new_tables )#line:1671
        OO0O0O00OOO00OOO0 .update_file_info (OO0O0O00OOO00OOO0 ._full_file ,OO0O0O00OOO00OOO0 ._backup_end_time )#line:1672
        O00OO00OO00OOOOOO =OO0OO0O0O0OOOOOO0 =False #line:1674
        for O0OO00OOOOO0O00OO in OO0000O0O0OOOO0O0 ['data']:#line:1675
            if O0OO00OOOOO0O00OO ==OO0000O0O0OOOO0O0 ['data'][-1 ]:O00OO00OO00OOOOOO =True #line:1676
            for O0O000O0000O0O0OO in O0OO00OOOOO0O00OO :#line:1677
                if O0O000O0000O0O0OO ==O0OO00OOOOO0O00OO [-1 ]:OO0OO0O0O0OOOOOO0 =True #line:1678
                OO0O0O00OOO00OOO0 .set_file_info (O0O000O0000O0O0OO ,O0O0O000OO0OOOOOO )#line:1679
                O00OO0O000OO00OOO ='/bt_backup/mysql_bin_log/'+OO0O0O00OOO00OOO0 ._db_name +OOOO0O0O0OO00O000 #line:1680
                O00O000OO000O0O0O =O00OO0O000OO00OOO +'full_record.json'#line:1681
                OO0OO00O000O0000O =O00OO0O000OO00OOO +'inc_record.json'#line:1682
                OO0O000OO00O0O00O ='/bt_backup/mysql_bin_log/'+OO0O0O00OOO00OOO0 ._db_name +OOOO0O0O0OO00O000 +O0O000O0000O0O0OO .split ('/')[-2 ]+'/'+O0O000O0000O0O0OO .split ('/')[-1 ]#line:1683
                if OOOOO0O0O000000O0 :#line:1684
                    O00O00OOOOO000OO0 =alioss_main ()#line:1685
                    if not O00O00OOOOO000OO0 .upload_file_by_path (O0O000O0000O0O0OO ,OO0O000OO00O0O00O ):#line:1686
                        OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O0O000O0000O0O0OO )#line:1687
                    if os .path .isfile (O0O0O000OO0OOOOOO )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :O00O00OOOOO000OO0 .upload_file_by_path (O0O0O000OO0OOOOOO ,OO0OO00O000O0000O )#line:1688
                    if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :O00O00OOOOO000OO0 .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O00O000OO000O0O0O )#line:1689
                else :#line:1690
                    if OOOO000O000O00000 ['upload_alioss']=='alioss':#line:1691
                            O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['alioss'],O00OOO0O00000OOO0 ['alioss'])#line:1692
                            OOOOOOOOOOOO00OOO =True #line:1693
                            print (O000O0OO00OO00OO0 )#line:1694
                if OOOOOO0OOO0O000OO :#line:1695
                    OOO00O000OO0O0OOO =txcos_main ()#line:1696
                    if not OOO00O000OO0O0OOO .upload_file_by_path (O0O000O0000O0O0OO ,OO0O000OO00O0O00O ):#line:1697
                       OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O0O000O0000O0O0OO )#line:1698
                    if os .path .isfile (O0O0O000OO0OOOOOO )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OOO00O000OO0O0OOO .upload_file_by_path (O0O0O000OO0OOOOOO ,OO0OO00O000O0000O )#line:1699
                    if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OOO00O000OO0O0OOO .upload_file_by_path (O0O0O000OO0OOOOOO ,O00O000OO000O0O0O )#line:1700
                else :#line:1701
                    if OOOO000O000O00000 ['upload_txcos']=='txcos':#line:1702
                            O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['txcos'],O00OOO0O00000OOO0 ['txcos'])#line:1703
                            OOOOOOOOOOOO00OOO =True #line:1704
                            print (O000O0OO00OO00OO0 )#line:1705
                if O0OO00O0OOO0O00OO :#line:1706
                    OOOO0OO0O000O000O =qiniu_main ()#line:1707
                    if not OOOO0OO0O000O000O .upload_file_by_path (O0O000O0000O0O0OO ,OO0O000OO00O0O00O ):#line:1708
                        OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O0O000O0000O0O0OO )#line:1709
                    if os .path .isfile (O0O0O000OO0OOOOOO )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OOOO0OO0O000O000O .upload_file_by_path (O0O0O000OO0OOOOOO ,OO0OO00O000O0000O )#line:1710
                    if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OOOO0OO0O000O000O .upload_file_by_path (O0O0O000OO0OOOOOO ,O00O000OO000O0O0O )#line:1711
                else :#line:1712
                    if OOOO000O000O00000 ['upload_qiniu']=='qiniu':#line:1713
                            O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['qiniu'],O00OOO0O00000OOO0 ['qiniu'])#line:1714
                            OOOOOOOOOOOO00OOO =True #line:1715
                            print (O000O0OO00OO00OO0 )#line:1716
                if O00O0O0O00OO00OO0 :#line:1717
                    OOOO000OOO00000O0 =bos_main ()#line:1718
                    if not OOOO000OOO00000O0 .upload_file_by_path (O0O000O0000O0O0OO ,OO0O000OO00O0O00O ):#line:1719
                        OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O0O000O0000O0O0OO )#line:1720
                    if os .path .isfile (O0O0O000OO0OOOOOO )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OOOO000OOO00000O0 .upload_file_by_path (O0O0O000OO0OOOOOO ,OO0OO00O000O0000O )#line:1721
                    if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OOOO000OOO00000O0 .upload_file_by_path (O0O0O000OO0OOOOOO ,O00O000OO000O0O0O )#line:1722
                else :#line:1723
                    if OOOO000O000O00000 ['upload_bos']=='bos':#line:1724
                            O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['bos'],O00OOO0O00000OOO0 ['bos'])#line:1725
                            OOOOOOOOOOOO00OOO =True #line:1726
                            print (O000O0OO00OO00OO0 )#line:1727
                if O0OOO00000OOO00OO :#line:1729
                    OO0000O0OO0O00O00 =obs_main ()#line:1730
                    if not OO0000O0OO0O00O00 .upload_file_by_path (O0O000O0000O0O0OO ,OO0O000OO00O0O00O ):#line:1731
                        OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O0O000O0000O0O0OO )#line:1732
                    if os .path .isfile (O0O0O000OO0OOOOOO )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OO0000O0OO0O00O00 .upload_file_by_path (O0O0O000OO0OOOOOO ,OO0OO00O000O0000O )#line:1733
                    if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OO0000O0OO0O00O00 .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O00O000OO000O0O0O )#line:1734
                else :#line:1735
                    if OOOO000O000O00000 ['upload_obs']=='obs':#line:1736
                            O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['obs'],O00OOO0O00000OOO0 ['obs'])#line:1737
                            OOOOOOOOOOOO00OOO =True #line:1738
                            print (O000O0OO00OO00OO0 )#line:1739
                if OOOOO0OOOO00000OO :#line:1741
                    OOOO000OOOOO0OOOO =ftp_main ()#line:1742
                    if not OOOO000OOOOO0OOOO .upload_file_by_path (O0O000O0000O0O0OO ,OO0O000OO00O0O00O ):#line:1743
                        OO0O0O00OOO00OOO0 ._cloud_upload_not .append (O0O000O0000O0O0OO )#line:1744
                    if os .path .isfile (O0O0O000OO0OOOOOO )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :OOOO000OOOOO0OOOO .upload_file_by_path (O0O0O000OO0OOOOOO ,OO0OO00O000O0000O )#line:1745
                    if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file )and O00OO00OO00OOOOOO and OO0OO0O0O0OOOOOO0 :#line:1746
                        O00O000OO000O0O0O =os .path .join ('/www/wwwroot/ahongtest',O00O000OO000O0O0O )#line:1747
                        OOOO000OOOOO0OOOO .upload_file_by_path (OO0O0O00OOO00OOO0 ._full_file ,O00O000OO000O0O0O )#line:1748
                else :#line:1749
                    if OOOO000O000O00000 ['upload_ftp']=='ftp':#line:1750
                            O000O0OO00OO00OO0 ='|-无法连接上{}，无法上传到{}'.format (O00OOO0O00000OOO0 ['ftp'],O00OOO0O00000OOO0 ['ftp'])#line:1751
                            OOOOOOOOOOOO00OOO =True #line:1752
                            print (O000O0OO00OO00OO0 )#line:1753
        O000O0OO00OO00OO0 ='以下文件上传失败：{}'.format (OO0O0O00OOO00OOO0 ._cloud_upload_not )#line:1754
        if OO0O0O00OOO00OOO0 ._cloud_upload_not or OOOOOOOOOOOO00OOO :#line:1755
            OO0O0O00OOO00OOO0 .send_failture_notification (O000O0OO00OO00OO0 ,target =O00OO0OO0O00O0OO0 )#line:1756
            if OOO0O00O00OO00O0O :public .writeFile (OO0O0O00OOO00OOO0 ._full_file ,json .dumps (OOO0O00O00OO00O0O ))#line:1757
            return public .returnMsg (False ,'增量备份失败！')#line:1758
        public .M ('mysqlbinlog_backup_setting').where ('id=?',OOOO000O000O00000 ['id']).update (OOOO000O000O00000 )#line:1759
        if not O0000OO0O0O0O0000 :#line:1760
            OOO0O00OOOOOO0OOO ='inc'#line:1761
            OO00OOO00OO0OO00O =json .loads (public .readFile (O0O0O000OO0OOOOOO ))#line:1762
            OO0O0O00OOO00OOO0 .write_backups (OOO0O00OOOOOO0OOO ,OO00OOO00OO0OO00O )#line:1763
        if OOOO000O000O00000 ['upload_local']==''and os .path .isfile (OO0O0O00OOO00OOO0 ._inc_file ):#line:1764
                if os .path .isfile (OO0O0O00OOO00OOO0 ._full_file ):#line:1765
                    OO0O0O00OOO00OOO0 .clean_local_full_backups (OO0O0O00OOO00OOO0 ._full_file )#line:1766
                if os .path .isfile (OO0O0O00OOO00OOO0 ._inc_file ):#line:1768
                    OO0O0O00OOO00OOO0 .clean_local_inc_backups (OO0O0O00OOO00OOO0 ._inc_file )#line:1769
                print ('|-用户设置不保留本地备份，已从本地服务器清理备份')#line:1771
        return public .returnMsg (True ,'执行备份任务成功！')#line:1772
    def write_backups (O00O0OOOOOOO00OOO ,OOO0OOO00OOO00OOO ,OOOOOO0OOO00O0O0O ):#line:1775
        ""#line:1778
        OO000OO00000OO0O0 =O00O0OOOOOOO00OOO ._full_file if OOO0OOO00OOO00OOO =='full'else ''#line:1779
        OO00O0O000OOOO00O =O00O0OOOOOOO00OOO ._inc_file if OOO0OOO00OOO00OOO =='full'else ''#line:1780
        for OOOO0OOO0OOOO0O00 in OOOOOO0OOO00O0O0O :#line:1781
            O0O0OO0O00O0OOO0O =OOOO0OOO0OOOO0O00 ['full_name'].replace ('/www/backup','bt_backup')#line:1782
            OO00O0O0O0O00O00O ={"sid":O00O0OOOOOOO00OOO ._binlog_id ,"size":OOOO0OOO0OOOO0O00 ['size'],"type":OOO0OOO00OOO00OOO ,"full_json":OO000OO00000OO0O0 ,"inc_json":OO00O0O000OOOO00O ,"local_name":OOOO0OOO0OOOO0O00 ['full_name'],"ftp_name":'',"alioss_name":O0O0OO0O00O0OOO0O ,"txcos_name":O0O0OO0O00O0OOO0O ,"qiniu_name":O0O0OO0O00O0OOO0O ,"aws_name":'',"upyun_name":'',"obs_name":O0O0OO0O00O0OOO0O ,"bos_name":O0O0OO0O00O0OOO0O ,"gcloud_storage_name":'',"gdrive_name":'',"msonedrive_name":''}#line:1801
            if OOO0OOO00OOO00OOO =='full'and public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',(OOO0OOO00OOO00OOO ,O00O0OOOOOOO00OOO ._binlog_id )).count ():#line:1803
                O0O00OOOOOO00O0OO =public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',(OOO0OOO00OOO00OOO ,O00O0OOOOOOO00OOO ._binlog_id )).getField ('id')#line:1804
                public .M ('mysqlbinlog_backups').delete (O0O00OOOOOO00O0OO )#line:1805
            if OOO0OOO00OOO00OOO =='full':#line:1807
                OOO00O0O0000OO0OO =public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',('inc',O00O0OOOOOOO00OOO ._binlog_id )).select ()#line:1808
                if OOO00O0O0000OO0OO :#line:1809
                    for O0O0O0O0OO0OOO00O in OOO00O0O0000OO0OO :#line:1810
                        if not O0O0O0O0OO0OOO00O :continue #line:1811
                        if 'id'in O0O0O0O0OO0OOO00O :public .M ('mysqlbinlog_backups').delete (O0O0O0O0OO0OOO00O ['id'])#line:1812
            if not public .M ('mysqlbinlog_backups').where ('type=? AND local_name=? AND sid=?',(OOO0OOO00OOO00OOO ,OOOO0OOO0OOOO0O00 ['full_name'],O00O0OOOOOOO00OOO ._binlog_id )).count ():#line:1814
                public .M ('mysqlbinlog_backups').insert (OO00O0O0O0O00O00O )#line:1815
            else :#line:1817
                O0O00OOOOOO00O0OO =public .M ('mysqlbinlog_backups').where ('type=? AND local_name=? AND sid=?',(OOO0OOO00OOO00OOO ,OOOO0OOO0OOOO0O00 ['full_name'],O00O0OOOOOOO00OOO ._binlog_id )).getField ('id')#line:1818
                public .M ('mysqlbinlog_backups').where ('id=?',O0O00OOOOOO00O0OO ).update (OO00O0O0O0O00O00O )#line:1819
            if OOO0OOO00OOO00OOO =='inc'and not public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',('full',O00O0OOOOOOO00OOO ._binlog_id )).count ():#line:1821
                try :#line:1822
                    OO00OO00000OOOO0O =json .loads (public .readFile (O00O0OOOOOOO00OOO ._full_file ))[0 ]#line:1823
                except :#line:1824
                    OO00OO00000OOOO0O ={}#line:1825
                if OO00OO00000OOOO0O :#line:1826
                    public .M ('mysqlbinlog_backups').insert (OO00O0O0O0O00O00O )#line:1827
    def get_tables_list (O0OO0OOO000OOO000 ,OO00OO0OOO0O00O0O ,type =False ):#line:1829
        ""#line:1832
        OOO0O00O0O0OOOOO0 =[]#line:1833
        for O0OOO000OO0OOO0OO in OO00OO0OOO0O00O0O :#line:1834
            if not O0OOO000OO0OOO0OO :continue #line:1835
            if type :#line:1836
                if O0OOO000OO0OOO0OO .get ('type')!='F':continue #line:1837
            OOO0O00O0O0OOOOO0 .append (O0OOO000OO0OOO0OO ['name'])#line:1838
        return OOO0O00O0O0OOOOO0 #line:1839
    def clean_cloud_backups (OO00O0OO0O0OO00OO ,OO0O0OOO0O0O0OO00 ,O000O0O000O00O00O ,O0O00OO0000000000 ,O0O000OOO0OO0O000 ):#line:1842
        ""#line:1845
        try :#line:1846
            OOO0000OO00OO0OOO =json .loads (public .readFile (O000O0O000O00O00O ))[0 ]#line:1847
        except :#line:1848
            OOO0000OO00OO0OOO =[]#line:1849
        O0O000O00OOOOO0OO =O000O0O00OOO00O00 =OOO0OO00O00O00OOO =O0000OOO0O000O00O =OO0OOO0OOO000OO0O =public .dict_obj ()#line:1850
        O0O000O00OOOOO0OO .path =OO0O0OOO0O0O0OO00 #line:1851
        O0O00O0O0O0OO000O =O0O00OO0000000000 .get_list (O0O000O00OOOOO0OO )#line:1852
        if 'list'in O0O00O0O0O0OO000O :#line:1853
            for OO0OO000OO0O0O0OO in O0O00O0O0O0OO000O ['list']:#line:1854
                if not OO0OO000OO0O0O0OO :continue #line:1855
                if OO0OO000OO0O0O0OO ['name'][-1 ]=='/':#line:1856
                    O000O0O00OOO00O00 .path =OO0O0OOO0O0O0OO00 +OO0OO000OO0O0O0OO ['name']#line:1857
                    O000O0O00OOO00O00 .filename =OO0OO000OO0O0O0OO ['name']#line:1858
                    O00OO00O0000O0OOO =O0O00OO0000000000 .get_list (O000O0O00OOO00O00 )#line:1859
                    O000O0O00OOO00O00 .path =OO0O0OOO0O0O0OO00 #line:1860
                    if O00OO00O0000O0OOO ['list']:#line:1862
                        for OO00OOOO00OOO00OO in O00OO00O0000O0OOO ['list']:#line:1863
                            OOO0OO00O00O00OOO .path =OO0O0OOO0O0O0OO00 +OO0OO000OO0O0O0OO ['name']#line:1864
                            OOO0OO00O00O00OOO .filename =OO00OOOO00OOO00OO ['name']#line:1865
                            O0O00OO0000000000 .remove_file (OOO0OO00O00O00OOO )#line:1866
                    else :#line:1868
                        O0O00OO0000000000 .remove_file (O000O0O00OOO00O00 )#line:1869
                if not OOO0000OO00OO0OOO :continue #line:1871
                if OO0OO000OO0O0O0OO ['name'].split ('.')[-1 ]in ['zip','gz','json']and OO0OO000OO0O0O0OO ['name']!=OOO0000OO00OO0OOO ['name']and OO0OO000OO0O0O0OO ['name']!='full_record.json':#line:1872
                    O0000OOO0O000O00O .path =OO0O0OOO0O0O0OO00 #line:1873
                    O0000OOO0O000O00O .filename =OO0OO000OO0O0O0OO ['name']#line:1874
                    O0O00OO0000000000 .remove_file (O0000OOO0O000O00O )#line:1875
                O0O0O00OOO0000O0O =False #line:1876
                if 'dir'not in OO0OO000OO0O0O0OO :continue #line:1877
                if OO0OO000OO0O0O0OO ['dir']==True :#line:1878
                    try :#line:1879
                        OOO0O0000OO0O0OOO =datetime .datetime .strptime (OO0OO000OO0O0O0OO ['name'],'%Y-%m-%d')#line:1880
                        O0O0O00OOO0000O0O =True #line:1881
                    except :#line:1882
                        pass #line:1883
                O0O0O000OOO000000 =''#line:1884
                if O0O0O00OOO0000O0O :O0O0O000OOO000000 =os .path .join (OO0O0OOO0O0O0OO00 ,OO0OO000OO0O0O0OO ['name'])#line:1885
                if O0O0O000OOO000000 :#line:1886
                    OO0OOO0OOO000OO0O .path =O0O0O000OOO000000 #line:1887
                    OO0OOO0OOO000OO0O .filename =''#line:1888
                    OO0OOO0OOO000OO0O .is_inc =True #line:1889
                    O0O00OO0000000000 .remove_file (OO0OOO0OOO000OO0O )#line:1890
        print ('|-已从{}清理过期备份文件'.format (O0O000OOO0OO0O000 ))#line:1891
    def add_binlog_inc_backup_task (OO0OO00OO0OO0OO0O ,O00O0O0O000OOOOO0 ,O0OO0O0OO0OOO0O0O ):#line:1894
        ""#line:1900
        O000OOO0000O0000O ={"name":"[勿删]数据库增量备份[{}]".format (O00O0O0O000OOOOO0 ['database_table']),"type":O00O0O0O000OOOOO0 ['cron_type'],"where1":O00O0O0O000OOOOO0 ['backup_cycle'],"hour":'',"minute":'0',"sType":'enterpriseBackup',"sName":O00O0O0O000OOOOO0 ['backup_type'],"backupTo":O0OO0O0OO0OOO0O0O ,"save":'1',"save_local":'1',"notice":O00O0O0O000OOOOO0 ['notice'],"notice_channel":O00O0O0O000OOOOO0 ['notice_channel'],"sBody":'{} {} --db_name {} --binlog_id {}'.format (OO0OO00OO0OO0OO0O ._python_path ,OO0OO00OO0OO0OO0O ._binlogModel_py ,OO0OO00OO0OO0OO0O ._db_name ,str (O00O0O0O000OOOOO0 ['id'])),"urladdress":'{}|{}|{}'.format (O00O0O0O000OOOOO0 ['db_name'],O00O0O0O000OOOOO0 ['tb_name'],O00O0O0O000OOOOO0 ['id'])}#line:1916
        import crontab #line:1917
        OO0O00O0O0000O00O =crontab .crontab ().AddCrontab (O000OOO0000O0000O )#line:1918
        if OO0O00O0O0000O00O and "id"in OO0O00O0O0000O00O .keys ():#line:1919
            return True #line:1920
        return False #line:1921
    def create_table (O00O0O00O00O00OOO ):#line:1923
        ""#line:1928
        if not public .M ('sqlite_master').where ('type=? AND name=?',('table','mysqlbinlog_backup_setting')).count ():#line:1930
            public .M ('').execute ('''CREATE TABLE "mysqlbinlog_backup_setting" (
                                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                                "save_path" DEFAULT '',
                                "temp_path" DEFAULT '',
                                "database_table" DEFAULT '',
                                "db_name" DEFAULT '',
                                "tb_name" DEFAULT '',
                                "backup_type" DEFAULT '',
                                "backup_cycle" TEXT DEFAULT '',
                                "zip_password" TEXT DEFAULT '',
                                "cron_type" TEXT DEFAULT '',
                                "where_1" TEXT DEFAULT '',
                                "where_2" INTEGER DEFAULT 0,
                                "table_list" TEXT,
                                "upload_local" TEXT DEFAULT '',
                                "upload_ftp" TEXT DEFAULT '',
                                "upload_alioss" TEXT DEFAULT '',
                                "upload_txcos" TEXT DEFAULT '',
                                "upload_qiniu" TEXT DEFAULT '',
                                "upload_aws" TEXT DEFAULT '',
                                "upload_upyun" TEXT DEFAULT '',
                                "upload_obs" TEXT DEFAULT '',
                                "upload_bos" TEXT DEFAULT '',
                                "upload_gcloud_storage" TEXT DEFAULT '',
                                "upload_gdrive" TEXT DEFAULT '',
                                "upload_msonedrive" ITEXT DEFAULT '',
                                "notice" DEFAULT 0,
                                "notice_channel" ITEXT DEFAULT '',
                                "cron_status"  INTEGER DEFAULT 1,
                                "sync_remote_status" INTEGER DEFAULT 0,
                                'sync_remote_time' INTEGER DEFAULT 0,
                                "start_backup_time"  INTEGER DEFAULT 0,
                                "end_backup_time"  INTEGER DEFAULT 0,
                                "last_excute_backup_time"  INTEGER DEFAULT 1,
                                "add_time" INTEGER);''')#line:1965
        if not public .M ('sqlite_master').where ('type=? AND name=?',('table','mysqlbinlog_backups')).count ():#line:1968
            public .M ('').execute ('''CREATE TABLE "mysqlbinlog_backups" (
                                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                                "sid" INTEGER DEFAULT 0,
                                "size" INTEGER DEFAULT 0,
                                "type" DEFAULT '',
                                "full_json" DEFAULT '',
                                "inc_json" DEFAULT '',
                                "local_name" DEFAULT '',
                                "ftp_name" DEFAULT '',
                                "alioss_name" DEFAULT '',
                                "txcos_name" DEFAULT '',
                                "qiniu_name" DEFAULT '',
                                "aws_name" DEFAULT '',
                                "upyun_name" DEFAULT '',
                                "obs_name" DEFAULT '',
                                "bos_name" DEFAULT '',
                                "gcloud_storage_name" DEFAULT '',
                                "gdrive_name" DEFAULT '',
                                "msonedrive_name" DEFAULT '',
                                "where_1" DEFAULT '',
                                "where_2" DEFAULT '',
                                "where_3" DEFAULT '',
                                "where_4" TEXT DEFAULT '');''')#line:1991
    def add_mysqlbinlog_backup_setting (O00000O0OO000O0O0 ,O00O0O0OO00000O0O ):#line:1994
        ""#line:2000
        public .set_module_logs ('binlog','add_mysqlbinlog_backup_setting')#line:2001
        if not O00O0O0OO00000O0O .get ('datab_name/str',0 ):return public .returnMsg (False ,'当前没有数据库，不能添加！')#line:2002
        if O00O0O0OO00000O0O .datab_name in [0 ,'0']:return public .returnMsg (False ,'当前没有数据库，不能添加！')#line:2003
        if not O00O0O0OO00000O0O .get ('backup_cycle/d',0 )>0 :return public .returnMsg (False ,'备份周期不正确，只能为正整数！')#line:2004
        OO000OOOO0O000000 =OO00000OOOOOOO000 ={}#line:2008
        O00OO0OOO000OO0OO =O00000O0OO000O0O0 .get_binlog_status ()#line:2009
        if O00OO0OOO000OO0OO ['status']==False :return public .returnMsg (False ,'请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')#line:2010
        O00000O0OO000O0O0 ._db_name =OO00000OOOOOOO000 ['db_name']=O00O0O0OO00000O0O .datab_name #line:2011
        O00O0OO000OOOO000 ='databases'if O00O0O0OO00000O0O .backup_type =='databases'else 'tables'#line:2012
        O00000O0OO000O0O0 ._tables =''if 'table_name'not in O00O0O0OO00000O0O else O00O0O0OO00000O0O .table_name #line:2013
        OO000O0O0O0000000 =False #line:2014
        O0O0O0OO0OOOO0000 =''#line:2016
        O0OOOO0OOO0O0000O =''#line:2017
        if O00000O0OO000O0O0 ._tables :#line:2018
            O0O0O0OO0OOOO0000 =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=? and tb_name=?',(O00O0O0OO00000O0O .datab_name ,O00O0OO000OOOO000 ,O00000O0OO000O0O0 ._tables )).find ()#line:2019
            if O0O0O0OO0OOOO0000 :#line:2020
                OO000OOOO0O000000 =O0O0O0OO0OOOO0000 #line:2021
                OO000O0O0O0000000 =True #line:2022
                O0OOOO0OOO0O0000O =public .M ('crontab').where ('sBody=?','{} {} --db_name {} --binlog_id {}'.format (O00000O0OO000O0O0 ._python_path ,O00000O0OO000O0O0 ._binlogModel_py ,O0O0O0OO0OOOO0000 ['db_name'],str (O0O0O0OO0OOOO0000 ['id']))).getField ('id')#line:2023
                if O0OOOO0OOO0O0000O :#line:2024
                    return public .returnMsg (False ,'指定的数据库或者表已经存在备份，不能重复添加！')#line:2025
        else :#line:2026
            O0O0O0OO0OOOO0000 =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(O00O0O0OO00000O0O .datab_name ,O00O0OO000OOOO000 )).find ()#line:2027
            if O0O0O0OO0OOOO0000 :#line:2028
                OO000OOOO0O000000 =O0O0O0OO0OOOO0000 #line:2029
                OO000O0O0O0000000 =True #line:2030
                O0OOOO0OOO0O0000O =public .M ('crontab').where ('sBody=?','{} {} --db_name {} --binlog_id {}'.format (O00000O0OO000O0O0 ._python_path ,O00000O0OO000O0O0 ._binlogModel_py ,O0O0O0OO0OOOO0000 ['db_name'],str (O0O0O0OO0OOOO0000 ['id']))).getField ('id')#line:2031
                if O0OOOO0OOO0O0000O :#line:2032
                    return public .returnMsg (False ,'指定的数据库或者表已经存在备份，不能重复添加！')#line:2033
        OO000OOOO0O000000 ['database_table']=O00O0O0OO00000O0O .datab_name if O00O0O0OO00000O0O .backup_type =='databases'else O00O0O0OO00000O0O .datab_name +'---'+O00O0O0OO00000O0O .table_name #line:2034
        OO000OOOO0O000000 ['backup_type']=O00O0OO000OOOO000 #line:2035
        OO000OOOO0O000000 ['backup_cycle']=O00O0O0OO00000O0O .backup_cycle #line:2036
        OO000OOOO0O000000 ['cron_type']=O00O0O0OO00000O0O .cron_type #line:2037
        OO000OOOO0O000000 ['notice']=O00O0O0OO00000O0O .notice #line:2038
        if O00O0O0OO00000O0O .notice =='1':#line:2039
            OO000OOOO0O000000 ['notice_channel']=O00O0O0OO00000O0O .notice_channel #line:2040
        else :#line:2041
            OO000OOOO0O000000 ['notice_channel']=''#line:2042
        O000OO0OOO00O0000 =public .format_date ()#line:2043
        if O0O0O0OO0OOOO0000 :OO000OOOO0O000000 ['zip_password']=O0O0O0OO0OOOO0000 ['zip_password']#line:2044
        else :OO000OOOO0O000000 ['zip_password']=O00O0O0OO00000O0O .zip_password #line:2045
        OO000OOOO0O000000 ['start_backup_time']=O000OO0OOO00O0000 #line:2046
        OO000OOOO0O000000 ['end_backup_time']=O000OO0OOO00O0000 #line:2047
        OO000OOOO0O000000 ['last_excute_backup_time']=O000OO0OOO00O0000 #line:2048
        OO000OOOO0O000000 ['table_list']='|'.join (O00000O0OO000O0O0 .get_tables_list (O00000O0OO000O0O0 .get_tables ()))#line:2049
        OO000OOOO0O000000 ['cron_status']=1 #line:2050
        OO000OOOO0O000000 ['sync_remote_status']=0 #line:2051
        OO000OOOO0O000000 ['sync_remote_time']=0 #line:2052
        OO000OOOO0O000000 ['add_time']=O000OO0OOO00O0000 #line:2053
        OO000OOOO0O000000 ['db_name']=O00O0O0OO00000O0O .datab_name #line:2054
        OO000OOOO0O000000 ['tb_name']=O00000O0OO000O0O0 ._tables =''if 'table_name'not in O00O0O0OO00000O0O else O00O0O0OO00000O0O .table_name #line:2055
        OO000OOOO0O000000 ['save_path']=O00000O0OO000O0O0 .splicing_save_path ()#line:2056
        OO000OOOO0O000000 ['temp_path']=''#line:2057
        OOOO0O000OO0000OO ='|'#line:2061
        O0OOOOOOOOOO0000O =O000OOO00OO0OOOO0 =OO00OO0O0OOOOO000 =O000000O00000O0OO =OO00OOOOO00O000O0 =O0O0O0OO000000O00 =OOO0O000O0O0OOOO0 =O000O00000O0OOOO0 =OO00O00O000O0O0O0 =O00000O0OOO00000O ='|'#line:2062
        O00O0OOO0O00000O0 =''#line:2063
        if 'upload_localhost'in O00O0O0OO00000O0O :#line:2064
            OO000OOOO0O000000 ['upload_local']=O00O0O0OO00000O0O .upload_localhost #line:2065
            OOOO0O000OO0000OO ='localhost|'#line:2066
        else :#line:2067
            OO000OOOO0O000000 ['upload_local']=''#line:2068
        if 'upload_alioss'in O00O0O0OO00000O0O :#line:2069
            OO000OOOO0O000000 ['upload_alioss']=O00O0O0OO00000O0O .upload_alioss #line:2070
            O0OOOOOOOOOO0000O ='alioss|'#line:2071
        else :#line:2072
            OO000OOOO0O000000 ['upload_alioss']=''#line:2073
        if 'upload_ftp'in O00O0O0OO00000O0O :#line:2074
            OO000OOOO0O000000 ['upload_ftp']=O00O0O0OO00000O0O .upload_ftp #line:2075
            O000OOO00OO0OOOO0 ='ftp|'#line:2076
        else :#line:2077
            OO000OOOO0O000000 ['upload_ftp']=''#line:2078
        if 'upload_txcos'in O00O0O0OO00000O0O :#line:2079
            OO000OOOO0O000000 ['upload_txcos']=O00O0O0OO00000O0O .upload_txcos #line:2080
            OO00OO0O0OOOOO000 ='txcos|'#line:2081
        else :#line:2082
            OO000OOOO0O000000 ['upload_txcos']=''#line:2083
        if 'upload_qiniu'in O00O0O0OO00000O0O :#line:2084
            OO000OOOO0O000000 ['upload_qiniu']=O00O0O0OO00000O0O .upload_qiniu #line:2085
            O000000O00000O0OO ='qiniu|'#line:2086
        else :#line:2087
            OO000OOOO0O000000 ['upload_qiniu']=''#line:2088
        if 'upload_aws'in O00O0O0OO00000O0O :#line:2089
            OO000OOOO0O000000 ['upload_aws']=O00O0O0OO00000O0O .upload_aws #line:2090
            OO00OOOOO00O000O0 ='aws|'#line:2091
        else :#line:2092
            OO000OOOO0O000000 ['upload_aws']=''#line:2093
        if 'upload_upyun'in O00O0O0OO00000O0O :#line:2094
            OO000OOOO0O000000 ['upload_upyun']=O00O0O0OO00000O0O .upload_upyun #line:2095
            O0O0O0OO000000O00 ='upyun|'#line:2096
        else :#line:2097
            OO000OOOO0O000000 ['upload_upyun']=''#line:2098
        if 'upload_obs'in O00O0O0OO00000O0O :#line:2099
            OO000OOOO0O000000 ['upload_obs']=O00O0O0OO00000O0O .upload_obs #line:2100
            OOO0O000O0O0OOOO0 ='obs|'#line:2101
        else :#line:2102
            OO000OOOO0O000000 ['upload_obs']=''#line:2103
        if 'upload_bos'in O00O0O0OO00000O0O :#line:2104
            OO000OOOO0O000000 ['upload_bos']=O00O0O0OO00000O0O .upload_bos #line:2105
            O000O00000O0OOOO0 ='bos|'#line:2106
        else :#line:2107
            OO000OOOO0O000000 ['upload_bos']=''#line:2108
        if 'upload_gcloud_storage'in O00O0O0OO00000O0O :#line:2109
            OO000OOOO0O000000 ['upload_gcloud_storage']=O00O0O0OO00000O0O .upload_gcloud_storage #line:2110
            OO00O00O000O0O0O0 ='gcloud_storage|'#line:2111
        else :#line:2112
            OO000OOOO0O000000 ['upload_gcloud_storage']=''#line:2113
        if 'upload_gdrive'in O00O0O0OO00000O0O :#line:2114
            OO000OOOO0O000000 ['upload_gdrive']=O00O0O0OO00000O0O .upload_gdrive #line:2115
            O00000O0OOO00000O ='gdrive|'#line:2116
        else :#line:2117
            OO000OOOO0O000000 ['upload_gdrive']=''#line:2118
        if 'upload_msonedrive'in O00O0O0OO00000O0O :#line:2119
            OO000OOOO0O000000 ['upload_msonedrive']=O00O0O0OO00000O0O .upload_msonedrive #line:2120
            O00O0OOO0O00000O0 ='msonedrive'#line:2121
        else :#line:2122
            OO000OOOO0O000000 ['upload_msonedrive']=''#line:2123
        OOOO0O000OO0000OO =OOOO0O000OO0000OO +O0OOOOOOOOOO0000O +O000OOO00OO0OOOO0 +OO00OO0O0OOOOO000 +O000000O00000O0OO +OO00OOOOO00O000O0 +O0O0O0OO000000O00 +OOO0O000O0O0OOOO0 +O000O00000O0OOOO0 +OO00O00O000O0O0O0 +O00000O0OOO00000O +O00O0OOO0O00000O0 #line:2124
        if not OO000O0O0O0000000 :#line:2125
            OO000OOOO0O000000 ['id']=public .M ('mysqlbinlog_backup_setting').insert (OO000OOOO0O000000 )#line:2126
        else :#line:2127
            public .M ('mysqlbinlog_backup_setting').where ('id=?',int (OO000OOOO0O000000 ['id'])).update (OO000OOOO0O000000 )#line:2128
            time .sleep (0.01 )#line:2129
        if not O0OOOO0OOO0O0000O :#line:2131
            O00000O0OO000O0O0 .add_binlog_inc_backup_task (OO000OOOO0O000000 ,OOOO0O000OO0000OO )#line:2132
        return public .returnMsg (True ,'添加成功!')#line:2133
    def modify_mysqlbinlog_backup_setting (O0OOO000000O0OO00 ,O0OO00OOO0O000O0O ):#line:2135
        ""#line:2141
        public .set_module_logs ('binlog','modify_mysqlbinlog_backup_setting')#line:2142
        if 'backup_id'not in O0OO00OOO0O000O0O :return public .returnMsg (False ,'错误的参数!')#line:2143
        if not O0OO00OOO0O000O0O .get ('backup_cycle/d',0 )>0 :return public .returnMsg (False ,'备份周期不正确，只能为正整数！')#line:2144
        OOOO000O0000OOO00 =O0OOO000000O0OO00 .get_binlog_status ()#line:2146
        if OOOO000O0000OOO00 ['status']==False :return public .returnMsg (False ,'请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')#line:2147
        OO0000OO0O0O0O0OO =public .M ('mysqlbinlog_backup_setting').where ('id=?',O0OO00OOO0O000O0O .backup_id ).find ()#line:2149
        OO0000OO0O0O0O0OO ['backup_cycle']=O0OO00OOO0O000O0O .backup_cycle #line:2150
        OO0000OO0O0O0O0OO ['notice']=O0OO00OOO0O000O0O .notice #line:2151
        O0OOO000000O0OO00 ._db_name =OO0000OO0O0O0O0OO ['db_name']#line:2152
        if O0OO00OOO0O000O0O .notice =='1':#line:2153
            OO0000OO0O0O0O0OO ['notice_channel']=O0OO00OOO0O000O0O .notice_channel #line:2154
        else :#line:2155
            OO0000OO0O0O0O0OO ['notice_channel']=''#line:2156
        O0O0O0O000O0000O0 ='|'#line:2158
        O0O00OOO000OO0000 =O0OO000O0O00O00OO =OO00OO00OOO00OO0O =OO0OOO0O0O0O0OO0O =O000OOO00000O0OOO =OO0OOOO0OO00OO0OO =O0O000OOOOO0O0000 =OO0O00OOOO0OOO00O =O0000O000O0OO00OO =OOO0O0000OOO000OO ='|'#line:2159
        OOOO00O0O0OOOOO00 =''#line:2160
        if 'upload_localhost'not in O0OO00OOO0O000O0O :#line:2161
            OO0000OO0O0O0O0OO ['upload_local']=''#line:2162
        else :#line:2163
            OO0000OO0O0O0O0OO ['upload_local']=O0OO00OOO0O000O0O .upload_localhost #line:2164
            O0O0O0O000O0000O0 ='localhost|'#line:2165
        if 'upload_alioss'not in O0OO00OOO0O000O0O :#line:2166
            OO0000OO0O0O0O0OO ['upload_alioss']=''#line:2167
        else :#line:2168
            OO0000OO0O0O0O0OO ['upload_alioss']=O0OO00OOO0O000O0O .upload_alioss #line:2169
            O0O00OOO000OO0000 ='alioss|'#line:2170
        if 'upload_ftp'not in O0OO00OOO0O000O0O :#line:2171
            OO0000OO0O0O0O0OO ['upload_ftp']=''#line:2172
        else :#line:2173
            OO0000OO0O0O0O0OO ['upload_ftp']=O0OO00OOO0O000O0O .upload_ftp #line:2174
            O0OO000O0O00O00OO ='ftp|'#line:2175
        if 'upload_txcos'not in O0OO00OOO0O000O0O :#line:2176
             OO0000OO0O0O0O0OO ['upload_txcos']=''#line:2177
        else :#line:2178
            OO0000OO0O0O0O0OO ['upload_txcos']=O0OO00OOO0O000O0O .upload_txcos #line:2179
            OO00OO00OOO00OO0O ='txcos|'#line:2180
        if 'upload_qiniu'not in O0OO00OOO0O000O0O :#line:2181
            OO0000OO0O0O0O0OO ['upload_qiniu']=''#line:2182
        else :#line:2183
            OO0000OO0O0O0O0OO ['upload_qiniu']=O0OO00OOO0O000O0O .upload_qiniu #line:2184
            OO0OOO0O0O0O0OO0O ='qiniu|'#line:2185
        if 'upload_aws'not in O0OO00OOO0O000O0O :#line:2186
            OO0000OO0O0O0O0OO ['upload_aws']=''#line:2187
        else :#line:2188
            OO0000OO0O0O0O0OO ['upload_aws']=O0OO00OOO0O000O0O .upload_aws #line:2189
            O000OOO00000O0OOO ='aws|'#line:2190
        if 'upload_upyun'not in O0OO00OOO0O000O0O :#line:2191
            OO0000OO0O0O0O0OO ['upload_upyun']=''#line:2192
        else :#line:2193
            OO0000OO0O0O0O0OO ['upload_upyun']=O0OO00OOO0O000O0O .upload_upyun #line:2194
            OO0OOOO0OO00OO0OO ='upyun|'#line:2195
        if 'upload_obs'not in O0OO00OOO0O000O0O :#line:2196
            OO0000OO0O0O0O0OO ['upload_obs']=''#line:2197
        else :#line:2198
            OO0000OO0O0O0O0OO ['upload_obs']=O0OO00OOO0O000O0O .upload_obs #line:2199
            O0O000OOOOO0O0000 ='obs|'#line:2200
        if 'upload_bos'not in O0OO00OOO0O000O0O :#line:2201
            OO0000OO0O0O0O0OO ['upload_bos']=''#line:2202
        else :#line:2203
            OO0000OO0O0O0O0OO ['upload_bos']=O0OO00OOO0O000O0O .upload_bos #line:2204
            OO0O00OOOO0OOO00O ='bos|'#line:2205
        if 'upload_gcloud_storage'not in O0OO00OOO0O000O0O :#line:2206
            OO0000OO0O0O0O0OO ['upload_gcloud_storage']=''#line:2207
        else :#line:2208
            OO0000OO0O0O0O0OO ['upload_gcloud_storage']=O0OO00OOO0O000O0O .upload_gcloud_storage #line:2209
            O0000O000O0OO00OO ='gcloud_storage|'#line:2210
        if 'upload_gdrive'not in O0OO00OOO0O000O0O :#line:2211
            OO0000OO0O0O0O0OO ['upload_gdrive']=''#line:2212
        else :#line:2213
            OO0000OO0O0O0O0OO ['upload_gdrive']=O0OO00OOO0O000O0O .upload_gdrive #line:2214
            OOO0O0000OOO000OO ='gdrive|'#line:2215
        if 'upload_msonedrive'not in O0OO00OOO0O000O0O :#line:2216
            OO0000OO0O0O0O0OO ['upload_msonedrive']=''#line:2217
        else :#line:2218
            OO0000OO0O0O0O0OO ['upload_msonedrive']=O0OO00OOO0O000O0O .upload_msonedrive #line:2219
            OOOO00O0O0OOOOO00 ='msonedrive'#line:2220
        O0O0O0O000O0000O0 =O0O0O0O000O0000O0 +O0O00OOO000OO0000 +O0OO000O0O00O00OO +OO00OO00OOO00OO0O +OO0OOO0O0O0O0OO0O +O000OOO00000O0OOO +OO0OOOO0OO00OO0OO +O0O000OOOOO0O0000 +OO0O00OOOO0OOO00O +O0000O000O0OO00OO +OOO0O0000OOO000OO +OOOO00O0O0OOOOO00 #line:2221
        public .M ('mysqlbinlog_backup_setting').where ('id=?',int (O0OO00OOO0O000O0O .backup_id )).update (OO0000OO0O0O0O0OO )#line:2222
        if 'cron_id'in O0OO00OOO0O000O0O :#line:2224
            if O0OO00OOO0O000O0O .cron_id :#line:2225
                O0000OOO000000OOO ={"id":O0OO00OOO0O000O0O .cron_id ,"name":public .M ('crontab').where ("id=?",(O0OO00OOO0O000O0O .cron_id ,)).getField ('name'),"type":OO0000OO0O0O0O0OO ['cron_type'],"where1":OO0000OO0O0O0O0OO ['backup_cycle'],"hour":'',"minute":'0',"sType":'enterpriseBackup',"sName":OO0000OO0O0O0O0OO ['backup_type'],"backupTo":O0O0O0O000O0000O0 ,"save":OO0000OO0O0O0O0OO ['notice'],"save_local":'1',"notice":OO0000OO0O0O0O0OO ['notice'],"notice_channel":OO0000OO0O0O0O0OO ['notice_channel'],"sBody":public .M ('crontab').where ("id=?",(O0OO00OOO0O000O0O .cron_id ,)).getField ('sBody'),"urladdress":'{}|{}|{}'.format (OO0000OO0O0O0O0OO ['db_name'],OO0000OO0O0O0O0OO ['tb_name'],OO0000OO0O0O0O0OO ['id'])}#line:2242
                import crontab #line:2243
                crontab .crontab ().modify_crond (O0000OOO000000OOO )#line:2244
                return public .returnMsg (True ,'编辑成功!')#line:2245
            else :#line:2246
                O0OOO000000O0OO00 .add_binlog_inc_backup_task (OO0000OO0O0O0O0OO ,O0O0O0O000O0000O0 )#line:2247
                return public .returnMsg (True ,'已恢复计划任务!')#line:2248
        else :#line:2249
            O0OOO000000O0OO00 .add_binlog_inc_backup_task (OO0000OO0O0O0O0OO ,O0O0O0O000O0000O0 )#line:2250
            return public .returnMsg (True ,'已恢复计划任务!')#line:2251
    def delete_mysql_binlog_setting (O00OO00O00000O000 ,OO0O00OO0OOOOOOO0 ):#line:2253
        ""#line:2258
        public .set_module_logs ('binlog','delete_mysql_binlog_setting')#line:2259
        if 'backup_id'not in OO0O00OO0OOOOOOO0 and 'cron_id'not in OO0O00OO0OOOOOOO0 :return public .returnMsg (False ,'不存在此增量备份任务!')#line:2260
        OOO0O0OOOO00000O0 =''#line:2261
        if OO0O00OO0OOOOOOO0 .backup_id :#line:2262
            OOO0O0OOOO00000O0 =public .M ('mysqlbinlog_backup_setting').where ('id=?',(OO0O00OO0OOOOOOO0 .backup_id ,)).find ()#line:2263
            O00OO00O00000O000 ._save_default_path =OOO0O0OOOO00000O0 ['save_path']#line:2264
            O00OO00O00000O000 ._db_name =OOO0O0OOOO00000O0 ['db_name']#line:2265
        if 'cron_id'in OO0O00OO0OOOOOOO0 and OO0O00OO0OOOOOOO0 .cron_id :#line:2267
            if public .M ('crontab').where ('id=?',(OO0O00OO0OOOOOOO0 .cron_id ,)).count ():#line:2268
                O0OO0OOO00O00O00O ={"id":OO0O00OO0OOOOOOO0 .cron_id }#line:2269
                import crontab #line:2270
                crontab .crontab ().DelCrontab (O0OO0OOO00O00O00O )#line:2271
        if OO0O00OO0OOOOOOO0 .type =='manager'and OOO0O0OOOO00000O0 :#line:2273
            if public .M ('mysqlbinlog_backup_setting').where ('id=?',(OO0O00OO0OOOOOOO0 .backup_id ,)).count ():#line:2274
                public .M ('mysqlbinlog_backup_setting').where ('id=?',(OO0O00OO0OOOOOOO0 .backup_id ,)).delete ()#line:2275
            OOOOOOO000O0OO0O0 =OOO0O0OOOO00000O0 ['save_path']+'full_record.json'#line:2276
            O00OO0OOOO00O0OO0 =OOO0O0OOOO00000O0 ['save_path']+'inc_record.json'#line:2277
            if os .path .isfile (OOOOOOO000O0OO0O0 ):O00OO00O00000O000 .clean_local_full_backups (OOOOOOO000O0OO0O0 )#line:2278
            if os .path .isfile (O00OO0OOOO00O0OO0 ):O00OO00O00000O000 .clean_local_inc_backups (O00OO0OOOO00O0OO0 )#line:2279
            O0O00OOO0OOOOO0O0 =public .M ('mysqlbinlog_backups').where ('sid=?',OO0O00OO0OOOOOOO0 .backup_id ).select ()#line:2280
            for OO0O0OO0000O00O00 in O0O00OOO0OOOOO0O0 :#line:2281
                if not OO0O0OO0000O00O00 :continue #line:2282
                if 'id'not in OO0O0OO0000O00O00 :continue #line:2283
                public .M ('mysqlbinlog_backups').delete (OO0O0OO0000O00O00 ['id'])#line:2284
        return public .returnMsg (True ,'删除成功')#line:2285
    def get_inc_size (O0O0O0O0000000OO0 ,OOOOOOO0OO0000OO0 ):#line:2287
        ""#line:2293
        O0OO00000OO000OO0 =0 #line:2294
        if os .path .isfile (OOOOOOO0OO0000OO0 ):#line:2295
            try :#line:2296
                OO000OO000O0O00OO =json .loads (public .readFile (OOOOOOO0OO0000OO0 ))#line:2297
                for O00O0OOOO0O0O0O00 in OO000OO000O0O00OO :#line:2298
                    O0OO00000OO000OO0 +=int (O00O0OOOO0O0O0O00 ['size'])#line:2299
            except :#line:2300
                O0OO00000OO000OO0 =0 #line:2301
        return O0OO00000OO000OO0 #line:2302
    def get_time_size (OO00O0O0OO000O00O ,OO0O0000O0OOOO0OO ,O0OOO0000O000O00O ):#line:2304
        ""#line:2309
        OO00O0OOO0OO00000 =json .loads (public .readFile (OO0O0000O0OOOO0OO ))[0 ]#line:2311
        O0OOO0000O000O00O ['start_time']=OO00O0OOO0OO00000 ['time']#line:2312
        if 'end_time'in OO00O0OOO0OO00000 :#line:2313
            O0OOO0000O000O00O ['end_time']=OO00O0OOO0OO00000 ['end_time']#line:2314
            O0OOO0000O000O00O ['excute_time']=OO00O0OOO0OO00000 ['end_time']#line:2315
        else :#line:2316
            O0OOO0000O000O00O ['end_time']=OO00O0OOO0OO00000 ['time']#line:2317
            O0OOO0000O000O00O ['excute_time']=OO00O0OOO0OO00000 ['time']#line:2318
        O0OOO0000O000O00O ['full_size']=OO00O0OOO0OO00000 ['size']#line:2319
        return O0OOO0000O000O00O #line:2320
    def get_database_info (OOO0O00OO0OOO0OO0 ,get =None ):#line:2322
        ""#line:2327
        O0O0OOOO00O000OOO =OOO0O00OO0OOO0OO0 .get_databases ()#line:2328
        OO0OOO0O00O0OO00O ={}#line:2329
        OO0O0O0OOO0O00000 =[]#line:2330
        OO00O00OO0OOO0O00 =[]#line:2331
        if O0O0OOOO00O000OOO :#line:2332
            for OOO00000O0O0000O0 in O0O0OOOO00O000OOO :#line:2333
                if not OOO00000O0O0000O0 :continue #line:2334
                OOOO00O0000O0O000 ={}#line:2335
                OOO0O00OO0OOO0OO0 ._db_name =OOOO00O0000O0O000 ['name']=OOO00000O0O0000O0 ['name']#line:2336
                O000OO0O0O000OOOO =OOO0O00OO0OOO0OO0 ._save_default_path +OOO00000O0O0000O0 ['name']+'/databases/'#line:2337
                OO0O0OOOOO0O0OOOO =OOO0O00OO0OOO0OO0 ._save_default_path +OOO00000O0O0000O0 ['name']+'/tables/'#line:2338
                O00O0OO0OO0OOO0OO =O000OO0O0O000OOOO +'full_record.json'#line:2339
                O0O0O0O0O00O0O0O0 =O000OO0O0O000OOOO +'inc_record.json'#line:2340
                OOOO00O0000O0O000 ['inc_size']=0 if not os .path .isfile (O0O0O0O0O00O0O0O0 )else OOO0O00OO0OOO0OO0 .get_inc_size (O0O0O0O0O00O0O0O0 )#line:2341
                O00O00OO0O0O0OOOO =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(str (OOO00000O0O0000O0 ['name']),'databases')).find ()#line:2343
                if O00O00OO0O0O0OOOO :#line:2344
                    OOOO00O0000O0O000 ['cron_id']=public .M ('crontab').where ('name=?','[勿删]数据库增量备份[{}]'.format (O00O00OO0O0O0OOOO ['db_name'])).getField ('id')#line:2345
                    OOOO00O0000O0O000 ['backup_id']=O00O00OO0O0O0OOOO ['id']#line:2346
                    OOOO00O0000O0O000 ['upload_localhost']=O00O00OO0O0O0OOOO ['upload_local']#line:2347
                    OOOO00O0000O0O000 ['upload_alioss']=O00O00OO0O0O0OOOO ['upload_alioss']#line:2348
                    OOOO00O0000O0O000 ['upload_ftp']=O00O00OO0O0O0OOOO ['upload_ftp']#line:2349
                    OOOO00O0000O0O000 ['upload_txcos']=O00O00OO0O0O0OOOO ['upload_txcos']#line:2350
                    OOOO00O0000O0O000 ['upload_qiniu']=O00O00OO0O0O0OOOO ['upload_qiniu']#line:2351
                    OOOO00O0000O0O000 ['upload_obs']=O00O00OO0O0O0OOOO ['upload_obs']#line:2352
                    OOOO00O0000O0O000 ['upload_bos']=O00O00OO0O0O0OOOO ['upload_bos']#line:2353
                    OOOO00O0000O0O000 ['backup_cycle']=O00O00OO0O0O0OOOO ['backup_cycle']#line:2354
                    OOOO00O0000O0O000 ['notice']=O00O00OO0O0O0OOOO ['notice']#line:2355
                    OOOO00O0000O0O000 ['notice_channel']=O00O00OO0O0O0OOOO ['notice_channel']#line:2356
                    OOOO00O0000O0O000 ['zip_password']=O00O00OO0O0O0OOOO ['zip_password']#line:2357
                    OOOO00O0000O0O000 ['start_time']=O00O00OO0O0O0OOOO ['start_backup_time']#line:2359
                    OOOO00O0000O0O000 ['end_time']=O00O00OO0O0O0OOOO ['end_backup_time']#line:2360
                    OOOO00O0000O0O000 ['excute_time']=O00O00OO0O0O0OOOO ['last_excute_backup_time']#line:2361
                else :#line:2362
                    OOOO00O0000O0O000 ['cron_id']=OOOO00O0000O0O000 ['backup_id']=OOOO00O0000O0O000 ['notice']=OOOO00O0000O0O000 ['upload_alioss']=OOOO00O0000O0O000 ['backup_cycle']=OOOO00O0000O0O000 ['zip_password']=None #line:2363
                    OOOO00O0000O0O000 ['upload_localhost']=OOOO00O0000O0O000 ['upload_alioss']=OOOO00O0000O0O000 ['upload_ftp']=OOOO00O0000O0O000 ['upload_txcos']=OOOO00O0000O0O000 ['upload_qiniu']=OOOO00O0000O0O000 ['upload_obs']=OOOO00O0000O0O000 ['upload_bos']=''#line:2364
                if os .path .isfile (O00O0OO0OO0OOO0OO ):#line:2366
                    OOOO00O0000O0O000 =OOO0O00OO0OOO0OO0 .get_time_size (O00O0OO0OO0OOO0OO ,OOOO00O0000O0O000 )#line:2367
                    if O00O00OO0O0O0OOOO :OOOO00O0000O0O000 ['excute_time']=O00O00OO0O0O0OOOO ['last_excute_backup_time']#line:2368
                    OOOO00O0000O0O000 ['full_size']=public .to_size (OOOO00O0000O0O000 ['full_size']+OOOO00O0000O0O000 ['inc_size'])#line:2369
                    OO0O0O0OOO0O00000 .append (OOOO00O0000O0O000 )#line:2370
                else :#line:2372
                    if O00O00OO0O0O0OOOO :#line:2373
                        OOOO00O0000O0O000 ['full_size']=0 #line:2374
                        O0O0O0OO000O000O0 =public .M ('mysqlbinlog_backups').where ('sid=?',O00O00OO0O0O0OOOO ['id']).select ()#line:2376
                        for O00O00000O00OO000 in O0O0O0OO000O000O0 :#line:2377
                            if not O00O00000O00OO000 :continue #line:2378
                            if 'size'not in O00O00000O00OO000 :continue #line:2379
                            OOOO00O0000O0O000 ['full_size']+=O00O00000O00OO000 ['size']#line:2380
                        OOOO00O0000O0O000 ['full_size']=public .to_size (OOOO00O0000O0O000 ['full_size'])#line:2381
                        OO0O0O0OOO0O00000 .append (OOOO00O0000O0O000 )#line:2382
                O00O00OO0O0O0OOOO =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(str (OOO00000O0O0000O0 ['name']),'tables')).select ()#line:2384
                O0O0O0O0O000O0OOO ={}#line:2385
                O0O0O0O0O000O0OOO ['name']=OOO00000O0O0000O0 ['name']#line:2386
                O0O00OO0O00O0O00O =[]#line:2387
                O0O0OOOOO0OO00O00 =OOO0O00OO0OOO0OO0 .get_tables_list (OOO0O00OO0OOO0OO0 .get_tables ())#line:2388
                for OO0O0000OOO0O0000 in O0O0OOOOO0OO00O00 :#line:2389
                    if not O0O0OOOOO0OO00O00 :continue #line:2390
                    OO000O00O00000OO0 =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and tb_name=? ',(OOO0O00OO0OOO0OO0 ._db_name ,OO0O0000OOO0O0000 )).find ()#line:2391
                    OO00000OOO0OOO000 =OO0O0OOOOO0O0OOOO +OO0O0000OOO0O0000 +'/full_record.json'#line:2392
                    OO00000O0O00OO0OO =OO0O0OOOOO0O0OOOO +OO0O0000OOO0O0000 +'/inc_record.json'#line:2393
                    OOOO00O0000O0O000 ={}#line:2394
                    OOOO00O0000O0O000 ['name']=OO0O0000OOO0O0000 #line:2395
                    OOOO00O0000O0O000 ['inc_size']=OOO0O00OO0OOO0OO0 .get_inc_size (OO00000O0O00OO0OO )#line:2397
                    if OO000O00O00000OO0 :#line:2399
                        OOOO00O0000O0O000 ['cron_id']=public .M ('crontab').where ('sBody=?','{} {} --db_name {} --binlog_id {}'.format (OOO0O00OO0OOO0OO0 ._python_path ,OOO0O00OO0OOO0OO0 ._binlogModel_py ,OO000O00O00000OO0 ['db_name'],str (OO000O00O00000OO0 ['id']))).getField ('id')#line:2400
                        OOOO00O0000O0O000 ['backup_id']=OO000O00O00000OO0 ['id']#line:2401
                        OOOO00O0000O0O000 ['upload_localhost']=OO000O00O00000OO0 ['upload_local']#line:2402
                        OOOO00O0000O0O000 ['upload_alioss']=OO000O00O00000OO0 ['upload_alioss']#line:2403
                        OOOO00O0000O0O000 ['backup_cycle']=OO000O00O00000OO0 ['backup_cycle']#line:2404
                        OOOO00O0000O0O000 ['notice']=OO000O00O00000OO0 ['notice']#line:2405
                        OOOO00O0000O0O000 ['notice_channel']=OO000O00O00000OO0 ['notice_channel']#line:2406
                        OOOO00O0000O0O000 ['excute_time']=OO000O00O00000OO0 ['last_excute_backup_time']#line:2407
                        OOOO00O0000O0O000 ['zip_password']=OO000O00O00000OO0 ['zip_password']#line:2408
                        OOOO00O0000O0O000 ['upload_ftp']=OO000O00O00000OO0 ['upload_ftp']#line:2409
                        OOOO00O0000O0O000 ['upload_txcos']=OO000O00O00000OO0 ['upload_txcos']#line:2410
                        OOOO00O0000O0O000 ['upload_qiniu']=OO000O00O00000OO0 ['upload_qiniu']#line:2411
                        OOOO00O0000O0O000 ['upload_obs']=OO000O00O00000OO0 ['upload_obs']#line:2412
                        OOOO00O0000O0O000 ['upload_bos']=OO000O00O00000OO0 ['upload_bos']#line:2413
                    else :#line:2415
                        OOOO00O0000O0O000 ['cron_id']=OOOO00O0000O0O000 ['backup_id']=OOOO00O0000O0O000 ['notice']=OOOO00O0000O0O000 ['upload_alioss']=OOOO00O0000O0O000 ['backup_cycle']=OOOO00O0000O0O000 ['zip_password']=None #line:2416
                        OOOO00O0000O0O000 ['upload_localhost']=OOOO00O0000O0O000 ['upload_alioss']=OOOO00O0000O0O000 ['upload_ftp']=OOOO00O0000O0O000 ['upload_txcos']=OOOO00O0000O0O000 ['upload_qiniu']=OOOO00O0000O0O000 ['upload_obs']=OOOO00O0000O0O000 ['upload_bos']=''#line:2417
                    if os .path .isfile (OO00000OOO0OOO000 ):#line:2419
                        OOOO00O0000O0O000 =OOO0O00OO0OOO0OO0 .get_time_size (OO00000OOO0OOO000 ,OOOO00O0000O0O000 )#line:2420
                        if OO000O00O00000OO0 :OOOO00O0000O0O000 ['excute_time']=OO000O00O00000OO0 ['last_excute_backup_time']#line:2421
                        OOOO00O0000O0O000 ['full_size']=public .to_size (OOOO00O0000O0O000 ['full_size']+OOOO00O0000O0O000 ['inc_size'])#line:2422
                        O0O00OO0O00O0O00O .append (OOOO00O0000O0O000 )#line:2423
                    else :#line:2425
                        if not OO000O00O00000OO0 :continue #line:2426
                        OOOO00O0000O0O000 ['start_time']=OO000O00O00000OO0 ['start_backup_time']#line:2427
                        OOOO00O0000O0O000 ['end_time']=OO000O00O00000OO0 ['end_backup_time']#line:2428
                        OOOO00O0000O0O000 ['excute_time']=OO000O00O00000OO0 ['last_excute_backup_time']#line:2429
                        OOOO00O0000O0O000 ['full_size']=0 #line:2434
                        O0O0O0OO000O000O0 =public .M ('mysqlbinlog_backups').where ('sid=?',OO000O00O00000OO0 ['id']).select ()#line:2436
                        for OOO0OO00O000O0O0O in O0O0O0OO000O000O0 :#line:2437
                            if not OOO0OO00O000O0O0O :continue #line:2438
                            if 'size'not in OOO0OO00O000O0O0O :continue #line:2439
                            OOOO00O0000O0O000 ['full_size']+=OOO0OO00O000O0O0O ['size']#line:2440
                        OOOO00O0000O0O000 ['full_size']=public .to_size (OOOO00O0000O0O000 ['full_size'])#line:2441
                        O0O00OO0O00O0O00O .append (OOOO00O0000O0O000 )#line:2442
                if O0O00OO0O00O0O00O :#line:2443
                    O0O0O0O0O000O0OOO ['data']=O0O00OO0O00O0O00O #line:2444
                    OO00O00OO0OOO0O00 .append (O0O0O0O0O000O0OOO )#line:2445
        OO0OOO0O00O0OO00O ['databases']=OO0O0O0OOO0O00000 #line:2446
        OO0OOO0O00O0OO00O ['tables']=OO00O00OO0OOO0O00 #line:2447
        return public .returnMsg (True ,OO0OOO0O00O0OO00O )#line:2448
    def get_databases_info (OO00000000O0000OO ,O000OOOOO0OO00OO0 ):#line:2450
        ""#line:2454
        public .set_module_logs ('binlog','get_databases_info')#line:2455
        O00O0OOO0O0OO0O00 =OO00000000O0000OO .get_database_info ()#line:2456
        OO0000OO00OO0O00O =[]#line:2457
        for O000O00000OO00OO0 in O00O0OOO0O0OO0O00 ['msg']['databases']:#line:2458
            O000O00000OO00OO0 ['type']='databases'#line:2459
            OO0000OO00OO0O00O .append (O000O00000OO00OO0 )#line:2460
        return OO00000000O0000OO .get_page (OO0000OO00OO0O00O ,O000OOOOO0OO00OO0 )#line:2461
    def get_specified_database_info (O00000OOO0OO0O0O0 ,O0OOOOOO0OO000O00 ):#line:2463
        ""#line:2467
        public .set_module_logs ('binlog','get_specified_database_info')#line:2468
        OO0OOO00O0OOO0O00 =O00000OOO0OO0O0O0 .get_database_info ()#line:2469
        O0O0OO0O0000OOO00 =[]#line:2470
        O0O00O0O0O0O0OO00 =['databases','all']#line:2471
        OO0OOOOOOO0OO000O =['tables','all']#line:2472
        for O000OOOO00O0O0OOO in OO0OOO00O0OOO0O00 ['msg']['databases']:#line:2473
            if O000OOOO00O0O0OOO ['name']==O0OOOOOO0OO000O00 .datab_name :#line:2474
                O000OOOO00O0O0OOO ['type']='databases'#line:2475
                if hasattr (O0OOOOOO0OO000O00 ,'type')and O0OOOOOO0OO000O00 .type not in O0O00O0O0O0O0OO00 :continue #line:2476
                O0O0OO0O0000OOO00 .append (O000OOOO00O0O0OOO )#line:2477
        for O000OOOO00O0O0OOO in OO0OOO00O0OOO0O00 ['msg']['tables']:#line:2478
            if O000OOOO00O0O0OOO ['name']==O0OOOOOO0OO000O00 .datab_name :#line:2479
                for OOO00OOO0O0O0OOOO in O000OOOO00O0O0OOO ['data']:#line:2480
                    OOO00OOO0O0O0OOOO ['type']='tables'#line:2481
                    if hasattr (O0OOOOOO0OO000O00 ,'type')and O0OOOOOO0OO000O00 .type not in OO0OOOOOOO0OO000O :continue #line:2482
                    O0O0OO0O0000OOO00 .append (OOO00OOO0O0O0OOOO )#line:2483
        return O00000OOO0OO0O0O0 .get_page (O0O0OO0O0000OOO00 ,O0OOOOOO0OO000O00 )#line:2484
    def get_page (OO0OO00OOO0OO0OO0 ,O0O00000000OO00OO ,O00O00O00OO0OO0OO ):#line:2487
        ""#line:2491
        import page #line:2493
        page =page .Page ()#line:2495
        O0OOOOOO0O00OOO0O ={}#line:2497
        O0OOOOOO0O00OOO0O ['count']=len (O0O00000000OO00OO )#line:2498
        O0OOOOOO0O00OOO0O ['row']=10 #line:2499
        O0OOOOOO0O00OOO0O ['p']=1 #line:2500
        if hasattr (O00O00O00OO0OO0OO ,'p'):#line:2501
            O0OOOOOO0O00OOO0O ['p']=int (O00O00O00OO0OO0OO ['p'])#line:2502
        O0OOOOOO0O00OOO0O ['uri']={}#line:2503
        O0OOOOOO0O00OOO0O ['return_js']=''#line:2504
        O000O00OO00O00OOO ={}#line:2506
        O000O00OO00O00OOO ['page']=page .GetPage (O0OOOOOO0O00OOO0O ,limit ='1,2,3,4,5,8')#line:2507
        OOOO0O0OO00OOO0O0 =0 #line:2508
        O000O00OO00O00OOO ['data']=[]#line:2509
        for O00O0O0OO0O0OO00O in range (O0OOOOOO0O00OOO0O ['count']):#line:2510
            if OOOO0O0OO00OOO0O0 >=page .ROW :break #line:2511
            if O00O0O0OO0O0OO00O <page .SHIFT :continue #line:2512
            OOOO0O0OO00OOO0O0 +=1 #line:2513
            O000O00OO00O00OOO ['data'].append (O0O00000000OO00OO [O00O0O0OO0O0OO00O ])#line:2514
        return O000O00OO00O00OOO #line:2515
    def delete_file (O00OOOO00O0O0O0O0 ,OO0000OO0O00O0O0O ):#line:2518
        ""#line:2523
        if os .path .exists (OO0000OO0O00O0O0O ):#line:2524
            os .remove (OO0000OO0O00O0O0O )#line:2525
    def send_failture_notification (OO00OO0O00O00O0O0 ,O0000O0O0OO0OOOOO ,target ="",remark =""):#line:2527
        ""#line:2532
        OOOO0OOOOO000O000 ='数据库增量备份[ {} ]'.format (target )#line:2533
        OO00OOOO000000O0O =OO00OO0O00O00O0O0 ._pdata ['notice']#line:2534
        OO00O00O0OO00OO00 =OO00OO0O00O00O0O0 ._pdata ['notice_channel']#line:2535
        if OO00OOOO000000O0O in [0 ,'0']or not OO00O00O0OO00OO00 :#line:2536
            return #line:2537
        if OO00OOOO000000O0O in [1 ,'1',2 ,'2']:#line:2538
            O00O00OOO0000O0OO ="宝塔计划任务备份失败提醒"#line:2539
            O00O00O000O0OOO00 =OOOO0OOOOO000O000 #line:2540
            OO000000O0OO00OOO =OO00OO0O00O00O0O0 ._mybackup .generate_failture_notice (O00O00O000O0OOO00 ,O0000O0O0OO0OOOOO ,remark )#line:2541
            OO0000000OO00O0OO =OO00OO0O00O00O0O0 ._mybackup .send_notification (OO00O00O0OO00OO00 ,O00O00OOO0000O0OO ,OO000000O0OO00OOO )#line:2542
    def sync_date (OO00000OO0O00OOOO ):#line:2546
        ""#line:2549
        import config #line:2550
        config .config ().syncDate (None )#line:2551
def set_config (O00000OOOO0O0OO0O ,O0OOO000OO00OOO0O ):#line:2556
    ""#line:2559
class alioss_main :#line:2562
    __O0O00OOO00O0O0O00 =None #line:2563
    __O00OOO0O0OOO000O0 =0 #line:2564
    def __OOOOO0O0OOOOOO0OO (O000000O0OOO00OOO ):#line:2565
        ""#line:2569
        if O000000O0OOO00OOO .__O0O00OOO00O0O0O00 :return #line:2570
        OO000O0O0O00OO0OO =O000000O0OOO00OOO .get_config ()#line:2572
        O000000O0OOO00OOO .__OOOO0O0OOO0OOO000 =OO000O0O0O00OO0OO [2 ]#line:2574
        if OO000O0O0O00OO0OO [3 ].find (OO000O0O0O00OO0OO [2 ])!=-1 :OO000O0O0O00OO0OO [3 ]=OO000O0O0O00OO0OO [3 ].replace (OO000O0O0O00OO0OO [2 ]+'.','')#line:2575
        O000000O0OOO00OOO .__OO00OOO00OOO0O00O =OO000O0O0O00OO0OO [3 ]#line:2576
        O000000O0OOO00OOO .__O0O00O0O000OO0O0O =main ().get_path (OO000O0O0O00OO0OO [4 ]+'/bt_backup/')#line:2577
        if O000000O0OOO00OOO .__O0O00O0O000OO0O0O [:1 ]=='/':O000000O0OOO00OOO .__O0O00O0O000OO0O0O =O000000O0OOO00OOO .__O0O00O0O000OO0O0O [1 :]#line:2578
        try :#line:2580
            O000000O0OOO00OOO .__O0O00OOO00O0O0O00 =oss2 .Auth (OO000O0O0O00OO0OO [0 ],OO000O0O0O00OO0OO [1 ])#line:2582
        except Exception as O0O0O0O00OOO0OOOO :#line:2583
            pass #line:2584
    def get_config (O0O0O000OOO0000OO ):#line:2587
        ""#line:2592
        OO0OOOO000O0O0OOO =main ()._config_path +'/alioss.conf'#line:2593
        if not os .path .isfile (OO0OOOO000O0O0OOO ):#line:2595
            OOOOOO0OO000O0O00 =''#line:2596
            if os .path .isfile (main ()._plugin_path +'/alioss/config.conf'):#line:2597
                OOOOOO0OO000O0O00 =main ()._plugin_path +'/alioss/config.conf'#line:2598
            elif os .path .isfile (main ()._setup_path +'/data/aliossAS.conf'):#line:2599
                OOOOOO0OO000O0O00 =main ()._setup_path +'/data/aliossAS.conf'#line:2600
            if OOOOOO0OO000O0O00 :#line:2601
                O0OOOO0OO000OOO00 =json .loads (public .readFile (main ()._setup_path +'/data/aliossAS.conf'))#line:2602
                O0OOOO00OOOOO0OO0 =O0OOOO0OO000OOO00 ['access_key']+'|'+O0OOOO0OO000OOO00 ['secret_key']+'|'+O0OOOO0OO000OOO00 ['bucket_name']+'|'+O0OOOO0OO000OOO00 ['bucket_domain']+'|'+O0OOOO0OO000OOO00 ['backup_path']#line:2603
                public .writeFile (OO0OOOO000O0O0OOO ,O0OOOO00OOOOO0OO0 )#line:2604
        if not os .path .isfile (OO0OOOO000O0O0OOO ):return ['','','','','/']#line:2605
        OOOOOOO0OOOO0OOO0 =public .readFile (OO0OOOO000O0O0OOO )#line:2606
        if not OOOOOOO0OOOO0OOO0 :return ['','','','','/']#line:2608
        OOOOO0O00O0OOOOO0 =OOOOOOO0OOOO0OOO0 .split ('|')#line:2609
        if len (OOOOO0O00O0OOOOO0 )<5 :OOOOO0O00O0OOOOO0 .append ('/')#line:2610
        return OOOOO0O00O0OOOOO0 #line:2611
    def check_config (O00OO000O0O00OOO0 ):#line:2613
        ""#line:2618
        try :#line:2619
            O00OO000O0O00OOO0 .__OOOOO0O0OOOOOO0OO ()#line:2620
            from itertools import islice #line:2622
            O0O0000000000O00O =oss2 .Bucket (O00OO000O0O00OOO0 .__O0O00OOO00O0O0O00 ,O00OO000O0O00OOO0 .__OO00OOO00OOO0O00O ,O00OO000O0O00OOO0 .__OOOO0O0OOO0OOO000 )#line:2623
            O0O0OOOOOOO00OOOO =oss2 .ObjectIterator (O0O0000000000O00O )#line:2624
            OO00O0000OO0O0O00 =[]#line:2625
            O0OOOOOOO0OO0O000 ='/'#line:2626
            '''key, last_modified, etag, type, size, storage_class'''#line:2627
            for O0OO0000OO0O00O00 in islice (oss2 .ObjectIterator (O0O0000000000O00O ,delimiter ='/',prefix ='/'),1000 ):#line:2628
                O0OO0000OO0O00O00 .key =O0OO0000OO0O00O00 .key .replace ('/','')#line:2629
                if not O0OO0000OO0O00O00 .key :continue #line:2630
                O0O00OO0OO00OOO00 ={}#line:2631
                O0O00OO0OO00OOO00 ['name']=O0OO0000OO0O00O00 .key #line:2632
                O0O00OO0OO00OOO00 ['size']=O0OO0000OO0O00O00 .size #line:2633
                O0O00OO0OO00OOO00 ['type']=O0OO0000OO0O00O00 .type #line:2634
                O0O00OO0OO00OOO00 ['download']=O00OO000O0O00OOO0 .download_file (O0OOOOOOO0OO0O000 +O0OO0000OO0O00O00 .key ,False )#line:2635
                O0O00OO0OO00OOO00 ['time']=O0OO0000OO0O00O00 .last_modified #line:2636
                OO00O0000OO0O0O00 .append (O0O00OO0OO00OOO00 )#line:2637
            return True #line:2638
        except :#line:2639
            return False #line:2640
    def get_list (OOO0O0O000O00OO0O ,get =None ):#line:2642
        ""#line:2647
        OOO0O0O000O00OO0O .__OOOOO0O0OOOOOO0OO ()#line:2649
        if not OOO0O0O000O00OO0O .__O0O00OOO00O0O0O00 :#line:2650
            return False #line:2651
        try :#line:2653
            from itertools import islice #line:2654
            O00O00OOO0O0000OO =oss2 .Bucket (OOO0O0O000O00OO0O .__O0O00OOO00O0O0O00 ,OOO0O0O000O00OO0O .__OO00OOO00OOO0O00O ,OOO0O0O000O00OO0O .__OOOO0O0OOO0OOO000 )#line:2655
            OOOO0OOOO000O000O =oss2 .ObjectIterator (O00O00OOO0O0000OO )#line:2656
            OOOO0O0OO0OOO0000 =[]#line:2657
            OOO0000OO00OOOOOO =main ().get_path (get .path )#line:2658
            '''key, last_modified, etag, type, size, storage_class'''#line:2659
            for O0O0OOO0O0O0OOOO0 in islice (oss2 .ObjectIterator (O00O00OOO0O0000OO ,delimiter ='/',prefix =OOO0000OO00OOOOOO ),1000 ):#line:2660
                O0O0OOO0O0O0OOOO0 .key =O0O0OOO0O0O0OOOO0 .key .replace (OOO0000OO00OOOOOO ,'')#line:2661
                if not O0O0OOO0O0O0OOOO0 .key :continue #line:2662
                OO000000OOOOO00O0 ={}#line:2663
                OO000000OOOOO00O0 ['name']=O0O0OOO0O0O0OOOO0 .key #line:2664
                OO000000OOOOO00O0 ['size']=O0O0OOO0O0O0OOOO0 .size #line:2665
                OO000000OOOOO00O0 ['type']=O0O0OOO0O0O0OOOO0 .type #line:2666
                OO000000OOOOO00O0 ['download']=OOO0O0O000O00OO0O .download_file (OOO0000OO00OOOOOO +O0O0OOO0O0O0OOOO0 .key )#line:2667
                OO000000OOOOO00O0 ['time']=O0O0OOO0O0O0OOOO0 .last_modified #line:2668
                OOOO0O0OO0OOO0000 .append (OO000000OOOOO00O0 )#line:2669
            OO0O0O0O00000OO00 ={}#line:2670
            OO0O0O0O00000OO00 ['path']=get .path #line:2671
            OO0O0O0O00000OO00 ['list']=OOOO0O0OO0OOO0000 #line:2672
            return OO0O0O0O00000OO00 #line:2673
        except Exception as O0OO0OOOO0O0OO000 :#line:2674
            return public .returnMsg (False ,str (O0OO0OOOO0O0OO000 ))#line:2675
    def upload_file_by_path (O0OOO0OO00O0OO00O ,OOOOO0OOOO00O0O0O ,OO00OO0000000O0O0 ):#line:2677
        ""#line:2684
        O0OOO0OO00O0OO00O .__OOOOO0O0OOOOOO0OO ()#line:2686
        if not O0OOO0OO00O0OO00O .__O0O00OOO00O0O0O00 :#line:2687
            return False #line:2688
        try :#line:2689
            O0000OO0000O0O000 =main ().get_path (os .path .dirname (OO00OO0000000O0O0 ))+os .path .basename (OO00OO0000000O0O0 )#line:2691
            try :#line:2693
                print ('|-正在上传{}到阿里云OSS'.format (OOOOO0OOOO00O0O0O ),end ='')#line:2694
                OO0O000OO0OO0OO0O =oss2 .Bucket (O0OOO0OO00O0OO00O .__O0O00OOO00O0O0O00 ,O0OOO0OO00O0OO00O .__OO00OOO00OOO0O00O ,O0OOO0OO00O0OO00O .__OOOO0O0OOO0OOO000 )#line:2695
                oss2 .defaults .connection_pool_size =4 #line:2697
                O0O0O00OOOOO0O00O =oss2 .resumable_upload (OO0O000OO0OO0OO0O ,O0000OO0000O0O000 ,OOOOO0OOOO00O0O0O ,store =oss2 .ResumableStore (root ='/tmp'),multipart_threshold =1024 *1024 *2 ,part_size =1024 *1024 ,num_threads =1 )#line:2702
                print (' ==> 成功')#line:2703
            except :#line:2704
                print ('|-无法上传{}到阿里云OSS！请检查阿里云OSS配置是否正确！'.format (OOOOO0OOOO00O0O0O ))#line:2705
            return True #line:2709
        except Exception as OOO00OOOO00O0OO00 :#line:2710
            print (OOO00OOOO00O0OO00 )#line:2711
            if OOO00OOOO00O0OO00 .status ==403 :#line:2712
                time .sleep (5 )#line:2713
                O0OOO0OO00O0OO00O .__O00OOO0O0OOO000O0 +=1 #line:2714
                if O0OOO0OO00O0OO00O .__O00OOO0O0OOO000O0 <2 :#line:2715
                    O0OOO0OO00O0OO00O .upload_file_by_path (OOOOO0OOOO00O0O0O ,OO00OO0000000O0O0 )#line:2717
            return False #line:2718
    def download_file (OOOO0O00OOOO00O0O ,OOOO0000OOOOOO000 ):#line:2720
        ""#line:2726
        OOOO0O00OOOO00O0O .__OOOOO0O0OOOOOO0OO ()#line:2728
        if not OOOO0O00OOOO00O0O .__O0O00OOO00O0O0O00 :#line:2729
            return None #line:2730
        try :#line:2731
            O00OOOO0O00O0OO0O =oss2 .Bucket (OOOO0O00OOOO00O0O .__O0O00OOO00O0O0O00 ,OOOO0O00OOOO00O0O .__OO00OOO00OOO0O00O ,OOOO0O00OOOO00O0O .__OOOO0O0OOO0OOO000 )#line:2732
            OOO0OO00O0OOOO0OO =O00OOOO0O00O0OO0O .sign_url ('GET',OOOO0000OOOOOO000 ,3600 )#line:2733
            return OOO0OO00O0OOOO0OO #line:2734
        except :#line:2735
            print (OOOO0O00OOOO00O0O .__OO0OOO00O00O0OOOO )#line:2736
            return None #line:2737
    def alioss_delete_file (OOOO0000O000OOO0O ,O00OOOOO0OO000O0O ):#line:2739
        ""#line:2745
        OOOO0000O000OOO0O .__OOOOO0O0OOOOOO0OO ()#line:2747
        if not OOOO0000O000OOO0O .__O0O00OOO00O0O0O00 :#line:2748
            return False #line:2749
        try :#line:2751
            OOO0OO00OO00O0OO0 =oss2 .Bucket (OOOO0000O000OOO0O .__O0O00OOO00O0O0O00 ,OOOO0000O000OOO0O .__OO00OOO00OOO0O00O ,OOOO0000O000OOO0O .__OOOO0O0OOO0OOO000 )#line:2752
            OO0O0000O0000O000 =OOO0OO00OO00O0OO0 .delete_object (O00OOOOO0OO000O0O )#line:2753
            return OO0O0000O0000O000 .status #line:2754
        except Exception as O0OO00OOO0OOOO0OO :#line:2755
            if O0OO00OOO0OOOO0OO .status ==403 :#line:2756
                OOOO0000O000OOO0O .__O00OOO0O0OOO000O0 +=1 #line:2757
                if OOOO0000O000OOO0O .__O00OOO0O0OOO000O0 <2 :#line:2758
                    OOOO0000O000OOO0O .alioss_delete_file (O00OOOOO0OO000O0O )#line:2760
            print ('删除失败!')#line:2762
            return None #line:2763
    def remove_file (O00O00O0OO0OO0OO0 ,O000O00O0O000OOOO ):#line:2765
        ""#line:2772
        OO00O0OO0O0O0O0O0 =main ().get_path (O000O00O0O000OOOO .path )#line:2773
        OOO00OO0OOO0O00OO =OO00O0OO0O0O0O0O0 +O000O00O0O000OOOO .filename #line:2774
        O00O00O0OO0OO0OO0 .alioss_delete_file (OOO00OO0OOO0O00OO )#line:2775
        return public .returnMsg (True ,'删除文件成功!{}----{}'.format (OO00O0OO0O0O0O0O0 ,OOO00OO0OOO0O00OO ))#line:2776
class txcos_main :#line:2779
    __O00OOOOOOO0O00OO0 =None #line:2780
    __O00O0O0O0OO0OO0OO =None #line:2781
    __OO0OO00OO0O0OOO00 =0 #line:2782
    __O000O0OOOOOOO0OO0 =None #line:2783
    __OOOO0O0O0OOO00O00 =None #line:2784
    __O0OO0O000O000OOO0 =None #line:2785
    __O00OO0OO0OOO0O0O0 =None #line:2786
    __O0O0OO00O000O0000 ="ERROR: 无法连接腾讯云COS !"#line:2787
    def __init__ (OO0OO0O0OOO00OO0O ):#line:2790
        OO0OO0O0OOO00OO0O .__OOO00O0O0000OOOO0 ()#line:2791
    def __OOO00O0O0000OOOO0 (O0OO0O0OOO00000O0 ):#line:2793
        ""#line:2796
        if O0OO0O0OOO00000O0 .__O00OOOOOOO0O00OO0 :return #line:2797
        OO0OO00OOO0O00O00 =O0OO0O0OOO00000O0 .get_config ()#line:2799
        O0OO0O0OOO00000O0 .__O000O0OOOOOOO0OO0 =OO0OO00OOO0O00O00 [0 ]#line:2800
        O0OO0O0OOO00000O0 .__OOOO0O0O0OOO00O00 =OO0OO00OOO0O00O00 [1 ]#line:2801
        O0OO0O0OOO00000O0 .__O0OO0O000O000OOO0 =OO0OO00OOO0O00O00 [2 ]#line:2802
        O0OO0O0OOO00000O0 .__O00OO0OO0OOO0O0O0 =OO0OO00OOO0O00O00 [3 ]#line:2803
        O0OO0O0OOO00000O0 .__O00O0O0O0OO0OO0OO =main ().get_path (OO0OO00OOO0O00O00 [4 ])#line:2804
        try :#line:2805
            OO0O00OO00OO0O00O =CosConfig (Region =O0OO0O0OOO00000O0 .__O0OO0O000O000OOO0 ,SecretId =O0OO0O0OOO00000O0 .__O000O0OOOOOOO0OO0 ,SecretKey =O0OO0O0OOO00000O0 .__OOOO0O0O0OOO00O00 ,Token =None ,Scheme ='http')#line:2806
            O0OO0O0OOO00000O0 .__O00OOOOOOO0O00OO0 =CosS3Client (OO0O00OO00OO0O00O )#line:2807
        except Exception as O0OO0O0OOOO000000 :#line:2808
            pass #line:2809
    def get_config (O0O0OO0OOOOO0O0OO ,get =None ):#line:2813
        ""#line:2816
        OO0O00OOO0000OO0O =main ()._config_path +'/txcos.conf'#line:2817
        if not os .path .isfile (OO0O00OOO0000OO0O ):#line:2819
            O0O0O000O000O00OO =''#line:2820
            if os .path .isfile (main ()._plugin_path +'/txcos/config.conf'):#line:2821
                O0O0O000O000O00OO =main ()._plugin_path +'/txcos/config.conf'#line:2822
            elif os .path .isfile (main ()._setup_path +'/data/txcosAS.conf'):#line:2823
                O0O0O000O000O00OO =main ()._setup_path +'/data/txcosAS.conf'#line:2824
            if O0O0O000O000O00OO :#line:2825
                OOOO0O0000OOOO00O =json .loads (public .readFile (O0O0O000O000O00OO ))#line:2826
                OOO0OOOOO00O0000O =OOOO0O0000OOOO00O ['secret_id']+'|'+OOOO0O0000OOOO00O ['secret_key']+'|'+OOOO0O0000OOOO00O ['region']+'|'+OOOO0O0000OOOO00O ['bucket_name']+'|'+OOOO0O0000OOOO00O ['backup_path']#line:2827
                public .writeFile (OO0O00OOO0000OO0O ,OOO0OOOOO00O0000O )#line:2828
        if not os .path .isfile (OO0O00OOO0000OO0O ):return ['','','','','/']#line:2829
        OOOO0000OOOOO0O00 =public .readFile (OO0O00OOO0000OO0O )#line:2830
        if not OOOO0000OOOOO0O00 :return ['','','','','/']#line:2831
        O0OOO0O0000000O0O =OOOO0000OOOOO0O00 .split ('|')#line:2832
        if len (O0OOO0O0000000O0O )<5 :O0OOO0O0000000O0O .append ('/')#line:2833
        return O0OOO0O0000000O0O #line:2834
    def check_config (OO00OO00O00O0O0OO ):#line:2837
        try :#line:2838
            OO00O000OO00OOO00 =[]#line:2839
            O0OO0OOO0000O0O0O =[]#line:2840
            O0OO00OO0O0O00OO0 =OO00OO00O00O0O0OO .__O00O0O0O0OO0OO0OO +main ().get_path ('/')#line:2841
            OOOOOO00OO0O0O0O0 =OO00OO00O00O0O0OO .__O00OOOOOOO0O00OO0 .list_objects (Bucket =OO00OO00O00O0O0OO .__O00OO0OO0OOO0O0O0 ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO00OO0O0O00OO0 )#line:2842
            return True #line:2843
        except :#line:2844
            return False #line:2845
    def upload_file (O0OOOO0OOOOOOO0OO ,OO00O000O00000000 ):#line:2847
        ""#line:2851
        O0OOOO0OOOOOOO0OO .__OOO00O0O0000OOOO0 ()#line:2853
        if not O0OOOO0OOOOOOO0OO .__O00OOOOOOO0O00OO0 :#line:2854
            return False #line:2855
        try :#line:2857
            O0O0O00O00000OOOO ,OO00OO0OOO0OOOO00 =os .path .split (OO00O000O00000000 )#line:2859
            OO00OO0OOO0OOOO00 =O0OOOO0OOOOOOO0OO .__O00O0O0O0OO0OO0OO +OO00OO0OOO0OOOO00 #line:2860
            OO00O0O0O00000O0O =O0OOOO0OOOOOOO0OO .__O00OOOOOOO0O00OO0 .upload_file (Bucket =O0OOOO0OOOOOOO0OO .__O00OO0OO0OOO0O0O0 ,Key =OO00OO0OOO0OOOO00 ,MAXThread =10 ,PartSize =5 ,LocalFilePath =OO00O000O00000000 )#line:2867
        except :#line:2868
            time .sleep (1 )#line:2869
            O0OOOO0OOOOOOO0OO .__OO0OO00OO0O0OOO00 +=1 #line:2870
            if O0OOOO0OOOOOOO0OO .__OO0OO00OO0O0OOO00 <2 :#line:2871
                O0OOOO0OOOOOOO0OO .upload_file (OO00O000O00000000 )#line:2873
            print (O0OOOO0OOOOOOO0OO .__O0O0OO00O000O0000 )#line:2874
            return None #line:2875
    def upload_file_by_path (OOOOOOO0O0OOO000O ,OO0O0O0O00OOOO00O ,OO00O00O0O000O00O ):#line:2878
        ""#line:2883
        OOOOOOO0O0OOO000O .__OOO00O0O0000OOOO0 ()#line:2885
        if not OOOOOOO0O0OOO000O .__O00OOOOOOO0O00OO0 :#line:2886
            return False #line:2887
        try :#line:2889
            print ('|-正在上传{}到腾讯云COS'.format (OO0O0O0O00OOOO00O ),end ='')#line:2890
            OOO000O000O0OOOO0 ,O0000OOO0000OO0OO =os .path .split (OO0O0O0O00OOOO00O )#line:2891
            OOOOOOO0O0OOO000O .__O00O0O0O0OO0OO0OO =main ().get_path (os .path .dirname (OO00O00O0O000O00O ))#line:2892
            O0000OOO0000OO0OO =OOOOOOO0O0OOO000O .__O00O0O0O0OO0OO0OO +'/'+O0000OOO0000OO0OO #line:2893
            O00O000OOOOOOOO0O =OOOOOOO0O0OOO000O .__O00OOOOOOO0O00OO0 .upload_file (Bucket =OOOOOOO0O0OOO000O .__O00OO0OO0OOO0O0O0 ,Key =O0000OOO0000OO0OO ,MAXThread =10 ,PartSize =5 ,LocalFilePath =OO0O0O0O00OOOO00O )#line:2896
            print (' ==> 成功')#line:2898
            return True #line:2899
        except Exception as O0O0OOOOO000OOO0O :#line:2900
            time .sleep (1 )#line:2902
            OOOOOOO0O0OOO000O .__OO0OO00OO0O0OOO00 +=1 #line:2903
            if OOOOOOO0O0OOO000O .__OO0OO00OO0O0OOO00 <2 :#line:2904
                OOOOOOO0O0OOO000O .upload_file_by_path (OO0O0O0O00OOOO00O ,OO00O00O0O000O00O )#line:2906
            return False #line:2907
    def create_dir (OO00OO0O0OOOO00O0 ,get =None ):#line:2910
        ""#line:2913
        OO00OO0O0OOOO00O0 .__OOO00O0O0000OOOO0 ()#line:2915
        if not OO00OO0O0OOOO00O0 .__O00OOOOOOO0O00OO0 :#line:2916
            return False #line:2917
        O0O0O000OO0O00OOO =main ().get_path (get .path +get .dirname )#line:2919
        OO000O0O0O0O00OOO ='/tmp/dirname.pl'#line:2920
        public .writeFile (OO000O0O0O0O00OOO ,'')#line:2921
        O0000000O000OOO00 =OO00OO0O0OOOO00O0 .__O00OOOOOOO0O00OO0 .put_object (Bucket =OO00OO0O0OOOO00O0 .__O00OO0OO0OOO0O0O0 ,Body =b'',Key =O0O0O000OO0O00OOO )#line:2922
        os .remove (OO000O0O0O0O00OOO )#line:2923
        return public .returnMsg (True ,'创建成功!')#line:2924
    def get_list (OO000OOOOOO0O000O ,get =None ):#line:2926
        ""#line:2929
        OO000OOOOOO0O000O .__OOO00O0O0000OOOO0 ()#line:2931
        if not OO000OOOOOO0O000O .__O00OOOOOOO0O00OO0 :#line:2932
            return False #line:2933
        try :#line:2935
            O000O000O000O0O00 =[]#line:2936
            O0O000OOO0000OOOO =[]#line:2937
            O0OO0O000000O0000 =main ().get_path (get .path )#line:2938
            if 'Contents'in OO000OOOOOO0O000O .__O00OOOOOOO0O00OO0 .list_objects (Bucket =OO000OOOOOO0O000O .__O00OO0OO0OOO0O0O0 ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO0O000000O0000 ):#line:2939
                for OOOO00OOOO00OO0OO in OO000OOOOOO0O000O .__O00OOOOOOO0O00OO0 .list_objects (Bucket =OO000OOOOOO0O000O .__O00OO0OO0OOO0O0O0 ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO0O000000O0000 )['Contents']:#line:2940
                    OOO00O0OO0O000OO0 ={}#line:2941
                    OOOO00OOOO00OO0OO ['Key']=OOOO00OOOO00OO0OO ['Key'].replace (O0OO0O000000O0000 ,'')#line:2942
                    if not OOOO00OOOO00OO0OO ['Key']:continue #line:2943
                    OOO00O0OO0O000OO0 ['name']=OOOO00OOOO00OO0OO ['Key']#line:2944
                    OOO00O0OO0O000OO0 ['size']=OOOO00OOOO00OO0OO ['Size']#line:2945
                    OOO00O0OO0O000OO0 ['type']=OOOO00OOOO00OO0OO ['StorageClass']#line:2946
                    OOO00O0OO0O000OO0 ['download']=OO000OOOOOO0O000O .download_file (O0OO0O000000O0000 +OOOO00OOOO00OO0OO ['Key'])#line:2947
                    OOO00O0OO0O000OO0 ['time']=OOOO00OOOO00OO0OO ['LastModified']#line:2948
                    O000O000O000O0O00 .append (OOO00O0OO0O000OO0 )#line:2949
            else :#line:2950
                pass #line:2951
            if 'CommonPrefixes'in OO000OOOOOO0O000O .__O00OOOOOOO0O00OO0 .list_objects (Bucket =OO000OOOOOO0O000O .__O00OO0OO0OOO0O0O0 ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO0O000000O0000 ):#line:2952
                for OOOOO000O000O0OO0 in OO000OOOOOO0O000O .__O00OOOOOOO0O00OO0 .list_objects (Bucket =OO000OOOOOO0O000O .__O00OO0OO0OOO0O0O0 ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO0O000000O0000 )['CommonPrefixes']:#line:2953
                    if not OOOOO000O000O0OO0 ['Prefix']:continue #line:2954
                    O00000O0O00O000O0 =OOOOO000O000O0OO0 ['Prefix'].split ('/')[-2 ]+'/'#line:2955
                    O0O000OOO0000OOOO .append (O00000O0O00O000O0 )#line:2956
            else :#line:2957
                pass #line:2958
            OO0OO0OOO0OO00OOO ={}#line:2959
            OO0OO0OOO0OO00OOO ['path']=get .path #line:2960
            OO0OO0OOO0OO00OOO ['list']=O000O000O000O0O00 #line:2961
            OO0OO0OOO0OO00OOO ['dir']=O0O000OOO0000OOOO #line:2962
            return OO0OO0OOO0OO00OOO #line:2963
        except :#line:2964
            OO0OO0OOO0OO00OOO ={}#line:2965
            if OO000OOOOOO0O000O .__O00OOOOOOO0O00OO0 :#line:2966
                OO0OO0OOO0OO00OOO ['status']=True #line:2967
            else :#line:2968
                OO0OO0OOO0OO00OOO ['status']=False #line:2969
            OO0OO0OOO0OO00OOO ['path']=get .path #line:2970
            OO0OO0OOO0OO00OOO ['list']=O000O000O000O0O00 #line:2971
            OO0OO0OOO0OO00OOO ['dir']=O0O000OOO0000OOOO #line:2972
            return OO0OO0OOO0OO00OOO #line:2973
    def download_file (OO0O0O00OOO0OOOOO ,O00O0O0O00O0O000O ,Expired =300 ):#line:2975
        ""#line:2978
        OO0O0O00OOO0OOOOO .__OOO00O0O0000OOOO0 ()#line:2980
        if not OO0O0O00OOO0OOOOO .__O00OOOOOOO0O00OO0 :#line:2981
            return None #line:2982
        try :#line:2983
            O0O00O00OO0OOOOO0 =OO0O0O00OOO0OOOOO .__O00OOOOOOO0O00OO0 .get_presigned_download_url (Bucket =OO0O0O00OOO0OOOOO .__O00OO0OO0OOO0O0O0 ,Key =O00O0O0O00O0O000O )#line:2984
            O0O00O00OO0OOOOO0 =re .findall ('([^?]*)?.*',O0O00O00OO0OOOOO0 )[0 ]#line:2985
            return O0O00O00OO0OOOOO0 #line:2986
        except :#line:2987
            print (OO0O0O00OOO0OOOOO .__O0O0OO00O000O0000 )#line:2988
            return None #line:2989
    def delete_file (OO0OOO0OO0000OOO0 ,O000OOO000O0OO000 ):#line:2991
        ""#line:2995
        OO0OOO0OO0000OOO0 .__OOO00O0O0000OOOO0 ()#line:2997
        if not OO0OOO0OO0000OOO0 .__O00OOOOOOO0O00OO0 :#line:2998
            return False #line:2999
        try :#line:3001
            O00O0OO0OOOO00000 =OO0OOO0OO0000OOO0 .__O00OOOOOOO0O00OO0 .delete_object (Bucket =OO0OOO0OO0000OOO0 .__O00OO0OO0OOO0O0O0 ,Key =O000OOO000O0OO000 )#line:3002
            return O00O0OO0OOOO00000 #line:3003
        except Exception as OO0OOOOOOOOO00000 :#line:3004
            OO0OOO0OO0000OOO0 .__OO0OO00OO0O0OOO00 +=1 #line:3005
            if OO0OOO0OO0000OOO0 .__OO0OO00OO0O0OOO00 <2 :#line:3006
                OO0OOO0OO0000OOO0 .delete_file (O000OOO000O0OO000 )#line:3008
            print (OO0OOO0OO0000OOO0 .__O0O0OO00O000O0000 )#line:3009
            return None #line:3010
    def remove_file (OOO00O0OOO0OO0000 ,O000O000OO00OOO00 ):#line:3013
        O0O0O00OOOO0O0000 =main ().get_path (O000O000OO00OOO00 .path )#line:3014
        OOO0OO000OO000OOO =O0O0O00OOOO0O0000 +O000O000OO00OOO00 .filename #line:3015
        OOO00O0OOO0OO0000 .delete_file (OOO0OO000OO000OOO )#line:3016
        return public .returnMsg (True ,'删除文件成功!')#line:3017
class ftp_main :#line:3020
    __OO000O0O0OOO00O00 ='/'#line:3021
    def __init__ (O0OO00O0O000O00O0 ):#line:3023
        O0OO00O0O000O00O0 .__OO000O0O0OOO00O00 =O0OO00O0O000O00O0 .get_config (None )[3 ]#line:3024
    def get_config (O000O0OOOO000OOO0 ,get =None ):#line:3026
        OO000O00000OOOO00 =main ()._config_path +'/ftp.conf'#line:3027
        if not os .path .isfile (OO000O00000OOOO00 ):#line:3029
            O0O0OOOO0O000O00O =''#line:3030
            if os .path .isfile (main ()._plugin_path +'/ftp/config.conf'):#line:3031
                O0O0OOOO0O000O00O =main ()._plugin_path +'/ftp/config.conf'#line:3032
            elif os .path .isfile (main ()._setup_path +'/data/ftpAS.conf'):#line:3033
                O0O0OOOO0O000O00O =main ()._setup_path +'/data/ftpAS.conf'#line:3034
            if O0O0OOOO0O000O00O :#line:3035
                O00000OO0O00000OO =json .loads (public .readFile (O0O0OOOO0O000O00O ))#line:3036
                O0O000OOO0OOO0O0O =O00000OO0O00000OO ['ftp_host']+'|'+O00000OO0O00000OO ['ftp_user']+'|'+O00000OO0O00000OO ['ftp_pass']+'|'+O00000OO0O00000OO ['backup_path']#line:3037
                public .writeFile (OO000O00000OOOO00 ,O0O000OOO0OOO0O0O )#line:3038
        if not os .path .exists (OO000O00000OOOO00 ):return ['','','','/']#line:3039
        O0000O00O00OOO00O =public .readFile (OO000O00000OOOO00 )#line:3040
        if not O0000O00O00OOO00O :return ['','','','/']#line:3041
        return O0000O00O00OOO00O .split ('|')#line:3042
    def set_config (OO0000OOOO00O000O ,OOOO00OO0O0OOO00O ):#line:3044
        OO0OO0O0OOOOO0000 =main ()._config_path +'/ftp.conf'#line:3045
        O0OO0O0O0OOOO0O0O =OOOO00OO0O0OOO00O .ftp_host +'|'+OOOO00OO0O0OOO00O .ftp_user +'|'+OOOO00OO0O0OOO00O .ftp_pass +'|'+OOOO00OO0O0OOO00O .ftp_path #line:3046
        public .writeFile (OO0OO0O0OOOOO0000 ,O0OO0O0O0OOOO0O0O )#line:3047
        return public .returnMsg (True ,'设置成功!')#line:3048
    def connentFtp (OOOO00O000OOOO000 ):#line:3051
        from ftplib import FTP #line:3052
        O0O0OOOOO00O00000 =OOOO00O000OOOO000 .get_config ()#line:3053
        if O0O0OOOOO00O00000 [0 ].find (':')==-1 :O0O0OOOOO00O00000 [0 ]+=':21'#line:3054
        OOO0O00O00000OO0O =O0O0OOOOO00O00000 [0 ].split (':')#line:3055
        if OOO0O00O00000OO0O [1 ]=='':OOO0O00O00000OO0O [1 ]='21'#line:3056
        O00000000O00OO0OO =FTP ()#line:3057
        O00000000O00OO0OO .set_debuglevel (0 )#line:3058
        O00000000O00OO0OO .connect (OOO0O00O00000OO0O [0 ],int (OOO0O00O00000OO0O [1 ]))#line:3059
        O00000000O00OO0OO .login (O0O0OOOOO00O00000 [1 ],O0O0OOOOO00O00000 [2 ])#line:3060
        if OOOO00O000OOOO000 .__OO000O0O0OOO00O00 !='/':#line:3061
            OOOO00O000OOOO000 .dirname =OOOO00O000OOOO000 .__OO000O0O0OOO00O00 #line:3062
            OOOO00O000OOOO000 .path ='/'#line:3063
            OOOO00O000OOOO000 .createDir (OOOO00O000OOOO000 ,O00000000O00OO0OO )#line:3064
        O00000000O00OO0OO .cwd (OOOO00O000OOOO000 .__OO000O0O0OOO00O00 )#line:3065
        return O00000000O00OO0OO #line:3066
    def check_config (OOO0000OOOOOO0OO0 ):#line:3069
        try :#line:3070
            O00O0OO0OOOO0O0O0 =OOO0000OOOOOO0OO0 .connentFtp ()#line:3071
            if O00O0OO0OOOO0O0O0 :return True #line:3072
        except :#line:3073
            return False #line:3074
    def createDir (OO00OOO0O0000OO00 ,O0OOO00O0O0O00O0O ,ftp =None ):#line:3077
        try :#line:3078
            if not ftp :ftp =OO00OOO0O0000OO00 .connentFtp ()#line:3079
            OOO0000O0O00OOO0O =O0OOO00O0O0O00O0O .dirname .split ('/')#line:3080
            ftp .cwd (O0OOO00O0O0O00O0O .path )#line:3081
            for OOOO000000OOO0O00 in OOO0000O0O00OOO0O :#line:3082
                if not OOOO000000OOO0O00 :continue #line:3083
                if not OOOO000000OOO0O00 in ftp .nlst ():ftp .mkd (OOOO000000OOO0O00 )#line:3084
                ftp .cwd (OOOO000000OOO0O00 )#line:3085
            return public .returnMsg (True ,'目录创建成功!')#line:3086
        except :#line:3087
            return public .returnMsg (False ,'目录创建失败!')#line:3088
    def updateFtp (OOOO000O0OO0O0OO0 ,OO00OO0OOOO00O0O0 ):#line:3091
        try :#line:3092
            O0OOOOOO000OOOOOO =OOOO000O0OO0O0OO0 .connentFtp ()#line:3093
            OOOO0O0OO0000O0O0 =1024 #line:3094
            OO0O00O0O0O0OOO00 =open (OO00OO0OOOO00O0O0 ,'rb')#line:3095
            O0OOOOOO000OOOOOO .storbinary ('STOR %s'%os .path .basename (OO00OO0OOOO00O0O0 ),OO0O00O0O0O0OOO00 ,OOOO0O0OO0000O0O0 )#line:3096
            OO0O00O0O0O0OOO00 .close ()#line:3097
            O0OOOOOO000OOOOOO .quit ()#line:3098
        except :#line:3099
            if os .path .exists (OO00OO0OOOO00O0O0 ):os .remove (OO00OO0OOOO00O0O0 )#line:3100
            print ('连接服务器失败!')#line:3101
            return {'status':False ,'msg':'连接服务器失败!'}#line:3102
    def upload_file_by_path (O0O0000000O0000OO ,OO000O000OOO0OOO0 ,OOO0O00OO0OO0OO00 ):#line:3105
        try :#line:3106
            O0O00OO0OOOOOO0OO =O0O0000000O0000OO .connentFtp ()#line:3107
            O000OO000O00O0O00 =O0O0000000O0000OO .get_config (None )[3 ]#line:3108
            OO0OOOOOO0000OO00 =public .dict_obj ()#line:3109
            if OOO0O00OO0OO0OO00 [0 ]=="/":#line:3110
                OOO0O00OO0OO0OO00 =OOO0O00OO0OO0OO00 [1 :]#line:3111
            OO0OOOOOO0000OO00 .path =O000OO000O00O0O00 #line:3112
            OO0OOOOOO0000OO00 .dirname =os .path .dirname (OOO0O00OO0OO0OO00 )#line:3113
            O0O0000000O0000OO .createDir (OO0OOOOOO0000OO00 )#line:3114
            O00OO0000O0O0O0OO =os .path .join (O000OO000O00O0O00 ,os .path .dirname (OOO0O00OO0OO0OO00 ))#line:3115
            print ("目标上传目录：{}".format (O00OO0000O0O0O0OO ))#line:3116
            O0O00OO0OOOOOO0OO .cwd (O00OO0000O0O0O0OO )#line:3117
            O0OO0OOOOOO00000O =1024 #line:3118
            O0OOOO00OO000O0OO =open (OO000O000OOO0OOO0 ,'rb')#line:3119
            try :#line:3120
                O0O00OO0OOOOOO0OO .storbinary ('STOR %s'%O00OO0000O0O0O0OO +'/'+os .path .basename (OO000O000OOO0OOO0 ),O0OOOO00OO000O0OO ,O0OO0OOOOOO00000O )#line:3121
            except :#line:3122
                O0O00OO0OOOOOO0OO .storbinary ('STOR %s'%os .path .split (OO000O000OOO0OOO0 )[1 ],O0OOOO00OO000O0OO ,O0OO0OOOOOO00000O )#line:3123
            O0OOOO00OO000O0OO .close ()#line:3124
            O0O00OO0OOOOOO0OO .quit ()#line:3125
            return True #line:3126
        except :#line:3127
            print (public .get_error_info ())#line:3128
            return False #line:3129
    def deleteFtp (OOOO0OOO0OOOO00O0 ,O0O000O0OO00O000O ,is_inc =False ):#line:3132
        OOOOO000OOOOOO000 =[]#line:3133
        if os .path .isfile (main ()._full_file ):#line:3134
            try :#line:3135
                OOOOO000OOOOOO000 =json .loads (public .readFile (main ()._full_file ))[0 ]#line:3136
            except :#line:3137
                OOOOO000OOOOOO000 =[]#line:3138
        try :#line:3139
            OO0OO000O0O0OOOO0 =OOOO0OOO0OOOO00O0 .connentFtp ()#line:3140
            if is_inc :#line:3141
                try :#line:3142
                    O0O00OO0OOOOOO0O0 =OO0OO000O0O0OOOO0 .nlst ()#line:3143
                    for O00O0O0OOOOOOO0O0 in O0O00OO0OOOOOO0O0 :#line:3152
                        if O00O0O0OOOOOOO0O0 =='.'or O00O0O0OOOOOOO0O0 =='..':continue #line:3153
                        if O00O0O0OOOOOOO0O0 =='full_record.json':continue #line:3154
                        if OOOOO000OOOOOO000 and 'full_name'in OOOOO000OOOOOO000 and os .path .basename (OOOOO000OOOOOO000 ['full_name'])==O00O0O0OOOOOOO0O0 :continue #line:3155
                        try :#line:3156
                            OO0OO000O0O0OOOO0 .rmd (O00O0O0OOOOOOO0O0 )#line:3157
                        except :#line:3158
                            OO0OO000O0O0OOOO0 .delete (O00O0O0OOOOOOO0O0 )#line:3159
                        print ('|-已从FTP存储空间清理过期备份文件{}'.format (O00O0O0OOOOOOO0O0 ))#line:3160
                    return True #line:3161
                except Exception as OOOO0O00OOO0OOOOO :#line:3162
                    print (OOOO0O00OOO0OOOOO )#line:3163
                    return False #line:3164
            try :#line:3165
                OO0OO000O0O0OOOO0 .rmd (O0O000O0OO00O000O )#line:3166
            except :#line:3167
                OO0OO000O0O0OOOO0 .delete (O0O000O0OO00O000O )#line:3168
            print ('|-已从FTP存储空间清理过期备份文件{}'.format (O0O000O0OO00O000O ))#line:3169
            return True #line:3170
        except Exception as O000O000OOOO0O000 :#line:3171
            print (O000O000OOOO0O000 )#line:3172
            return False #line:3173
    def remove_file (OO0OOOO0O0O0O0O0O ,OO0OO0O00OOO00OOO ):#line:3176
        OO0O00000O00O00OO =OO0OOOO0O0O0O0O0O .get_config (None )[3 ]#line:3177
        if OO0OO0O00OOO00OOO .path [0 ]=="/":#line:3178
            OO0OO0O00OOO00OOO .path =OO0OO0O00OOO00OOO .path [1 :]#line:3179
        OO0OOOO0O0O0O0O0O .__OO000O0O0OOO00O00 =os .path .join (OO0O00000O00O00OO ,OO0OO0O00OOO00OOO .path )#line:3180
        if 'is_inc'not in OO0OO0O00OOO00OOO and OO0OOOO0O0O0O0O0O .deleteFtp (OO0OO0O00OOO00OOO .filename ):#line:3181
            return public .returnMsg (True ,'删除成功!')#line:3182
        if 'is_inc'in OO0OO0O00OOO00OOO and OO0OO0O00OOO00OOO .is_inc :#line:3183
            if OO0OOOO0O0O0O0O0O .deleteFtp (OO0OO0O00OOO00OOO .filename ,True ):#line:3184
                return public .returnMsg (True ,'删除成功!')#line:3185
        return public .returnMsg (False ,'删除失败!')#line:3186
    def get_list (OO0O000OOOO0OO0OO ,get =None ):#line:3189
        try :#line:3190
            OO0O000OOOO0OO0OO .__OO000O0O0OOO00O00 =get .path #line:3191
            O00000000000O00OO =OO0O000OOOO0OO0OO .connentFtp ()#line:3192
            O00O0OOO0OOO0000O =O00000000000O00OO .nlst ()#line:3193
            OOOOO000OOOOOOO0O =[]#line:3195
            OOO000000O0000OOO =[]#line:3196
            O00O0O00O0OO000OO =[]#line:3197
            for O0OOO0OO0000O00OO in O00O0OOO0OOO0000O :#line:3198
                if O0OOO0OO0000O00OO =='.'or O0OOO0OO0000O00OO =='..':continue #line:3199
                O000O0OO00OO0O00O =public .M ('backup').where ('name=?',(O0OOO0OO0000O00OO ,)).field ('size,addtime').find ()#line:3200
                if not O000O0OO00OO0O00O :#line:3201
                    O000O0OO00OO0O00O ={}#line:3202
                    O000O0OO00OO0O00O ['addtime']='1970/01/01 00:00:01'#line:3203
                OOO0000O0O00O0OOO ={}#line:3204
                OOO0000O0O00O0OOO ['name']=O0OOO0OO0000O00OO #line:3205
                OOO0000O0O00O0OOO ['time']=int (time .mktime (time .strptime (O000O0OO00OO0O00O ['addtime'],'%Y/%m/%d %H:%M:%S')))#line:3206
                try :#line:3207
                    OOO0000O0O00O0OOO ['size']=O00000000000O00OO .size (O0OOO0OO0000O00OO )#line:3208
                    OOO0000O0O00O0OOO ['dir']=False #line:3209
                    OOO0000O0O00O0OOO ['download']=OO0O000OOOO0OO0OO .getFile (O0OOO0OO0000O00OO )#line:3210
                    OOO000000O0000OOO .append (OOO0000O0O00O0OOO )#line:3211
                except :#line:3212
                    OOO0000O0O00O0OOO ['size']=0 #line:3213
                    OOO0000O0O00O0OOO ['dir']=True #line:3214
                    OOO0000O0O00O0OOO ['download']=''#line:3215
                    OOOOO000OOOOOOO0O .append (OOO0000O0O00O0OOO )#line:3216
            O00O0O00O0OO000OO =OOOOO000OOOOOOO0O +OOO000000O0000OOO #line:3218
            O0000O00O0000O0OO ={}#line:3219
            O0000O00O0000O0OO ['path']=OO0O000OOOO0OO0OO .__OO000O0O0OOO00O00 #line:3220
            O0000O00O0000O0OO ['list']=O00O0O00O0OO000OO #line:3221
            return O0000O00O0000O0OO #line:3222
        except Exception as O0000O0O0OOOOO0OO :#line:3223
            return {'status':False ,'msg':str (O0000O0O0OOOOO0OO )}#line:3224
    def getFile (O00000OO000OO000O ,OOOO00O00000OO00O ):#line:3227
        try :#line:3228
            O0O00O000OOOOOO00 =O00000OO000OO000O .get_config ()#line:3229
            if O0O00O000OOOOOO00 [0 ].find (':')==-1 :O0O00O000OOOOOO00 [0 ]+=':21'#line:3230
            OOOOOO00OO0O00O00 =O0O00O000OOOOOO00 [0 ].split (':')#line:3231
            if OOOOOO00OO0O00O00 [1 ]=='':OOOOOO00OO0O00O00 [1 ]='21'#line:3232
            O0OOOO0OOOO0O0OO0 ='ftp://'+O0O00O000OOOOOO00 [1 ]+':'+O0O00O000OOOOOO00 [2 ]+'@'+OOOOOO00OO0O00O00 [0 ]+':'+OOOOOO00OO0O00O00 [1 ]+(O00000OO000OO000O .__OO000O0O0OOO00O00 +'/'+OOOO00O00000OO00O ).replace ('//','/')#line:3233
        except :#line:3234
            O0OOOO0OOOO0O0OO0 =None #line:3235
        return O0OOOO0OOOO0O0OO0 #line:3236
    def download_file (OO000000000OO000O ,OO0O0OO00OO0O0OO0 ):#line:3239
        return OO000000000OO000O .getFile (OO0O0OO00OO0O0OO0 )#line:3240
class qiniu_main :#line:3244
    __O0OO0O0O00OO0O0O0 =None #line:3245
    __O0OOOO000OOOOO0OO =None #line:3246
    __OOO0O0O00OOOO0O0O =None #line:3247
    __O000O0OO0OOO0OO00 =None #line:3248
    __O0O0OOOO00O0O0O00 ="ERROR: 无法连接到七牛云OSS服务器，请检查[AccessKeyId/AccessKeySecret]设置是否正确!"#line:3249
    def __init__ (OOO0O000O0OO00O00 ):#line:3251
        OOO0O000O0OO00O00 .__OOOOO000OOO0O0000 ()#line:3252
    def __OOOOO000OOO0O0000 (OO0000O00OO0OOO0O ):#line:3254
        if OO0000O00OO0OOO0O .__O0OO0O0O00OO0O0O0 :return #line:3255
        OOOOOOOOOOO00000O =OO0000O00OO0OOO0O .get_config ()#line:3257
        OO0000O00OO0OOO0O .__O0OOOO000OOOOO0OO =OOOOOOOOOOO00000O [2 ]#line:3259
        if OOOOOOOOOOO00000O [3 ].find (OOOOOOOOOOO00000O [2 ])!=-1 :OOOOOOOOOOO00000O [3 ]=OOOOOOOOOOO00000O [3 ].replace (OOOOOOOOOOO00000O [2 ]+'.','')#line:3260
        OO0000O00OO0OOO0O .__OOO0O0O00OOOO0O0O =OOOOOOOOOOO00000O [3 ]#line:3261
        OO0000O00OO0OOO0O .__O000O0OO0OOO0OO00 =main ().get_path (OOOOOOOOOOO00000O [4 ]+'/bt_backup/')#line:3262
        if OO0000O00OO0OOO0O .__O000O0OO0OOO0OO00 [:1 ]=='/':OO0000O00OO0OOO0O .__O000O0OO0OOO0OO00 =OO0000O00OO0OOO0O .__O000O0OO0OOO0OO00 [1 :]#line:3263
        try :#line:3265
            OO0000O00OO0OOO0O .__O0OO0O0O00OO0O0O0 =Auth (OOOOOOOOOOO00000O [0 ],OOOOOOOOOOO00000O [1 ])#line:3267
        except Exception as O0000O0000000O00O :#line:3268
            pass #line:3269
    def get_config (OO00OOO0O0000OOO0 ,get =None ):#line:3272
        O00OO00O0OO0000O0 =main ()._config_path +'/qiniu.conf'#line:3273
        if not os .path .isfile (O00OO00O0OO0000O0 ):#line:3275
            OO00OOOOO0OO000OO =''#line:3276
            if os .path .isfile (main ()._plugin_path +'/qiniu/config.conf'):#line:3277
                OO00OOOOO0OO000OO =main ()._plugin_path +'/qiniu/config.conf'#line:3278
            elif os .path .isfile (main ()._setup_path +'/data/qiniuAS.conf'):#line:3279
                OO00OOOOO0OO000OO =main ()._plugin_path +'/data/qiniuAS.conf'#line:3280
            if OO00OOOOO0OO000OO :#line:3281
                OOOO0O00OO00OO0OO =json .loads (public .readFile (OO00OOOOO0OO000OO ))#line:3282
                O00000OO000OO0000 =OOOO0O00OO00OO0OO ['access_key_id']+'|'+OOOO0O00OO00OO0OO ['access_key_secret']+'|'+OOOO0O00OO00OO0OO ['bucket_name']+'|'+OOOO0O00OO00OO0OO ['bucket_domain']+'|'+OOOO0O00OO00OO0OO ['backup_path']#line:3283
                public .writeFile (O00OO00O0OO0000O0 ,O00000OO000OO0000 )#line:3284
        if not os .path .isfile (O00OO00O0OO0000O0 ):return ['','','','','/']#line:3285
        OO000OO0000O0OOO0 =public .readFile (O00OO00O0OO0000O0 )#line:3286
        if not OO000OO0000O0OOO0 :return ['','','','','/']#line:3287
        OOOO0OOOOOO00000O =OO000OO0000O0OOO0 .split ('|')#line:3288
        if len (OOOO0OOOOOO00000O )<5 :OOOO0OOOOOO00000O .append ('/')#line:3289
        return OOOO0OOOOOO00000O #line:3290
    def set_config (O00000O0O000O0000 ,O00OOO00O0O0O0O00 ):#line:3292
        OOOO0O00O00000OO0 =['qiniu','txcos','alioss','bos','ftp','obs']#line:3293
        OO00000000OO00000 =O00OOO00O0O0O0O00 .get ('cloud_name/d',0 )#line:3294
        print (OO00000000OO00000 )#line:3295
        if OO00000000OO00000 not in OOOO0O00O00000OO0 :return public .returnMsg (False ,'参数不合法！')#line:3296
        OOO000000O0O0000O =main ()._config_path +'/{}.conf'.format (OO00000000OO00000 )#line:3297
        OOOOOOOO0O0000OO0 =O00OOO00O0O0O0O00 .access_key .strip ()+'|'+O00OOO00O0O0O0O00 .secret_key .strip ()+'|'+O00OOO00O0O0O0O00 .bucket_name .strip ()+'|'+O00OOO00O0O0O0O00 .bucket_domain .strip ()+'|'+O00OOO00O0O0O0O00 .bucket_path .strip ()#line:3299
        return public .returnMsg (True ,'设置成功!')#line:3301
    def check_config (OOOOOOO0OOO0OO0OO ):#line:3304
        try :#line:3305
            OOOO0OO0000O00000 =''#line:3306
            O00OOOOO0O0O00O0O =OOOOOOO0OOO0OO0OO .get_bucket ()#line:3307
            OO0OOOOOOOOOO0000 ='/'#line:3308
            OOOOO0OOOOOOO00OO =None #line:3309
            OO000OO00OO000000 =1000 #line:3310
            OOOO0OO0000O00000 =main ().get_path (OOOO0OO0000O00000 )#line:3311
            OOO0OO00O0OO0OO00 ,OO0OOOOO0OOOOOO00 ,O0O0OOOOO0OOOO00O =O00OOOOO0O0O00O0O .list (OOOOOOO0OOO0OO0OO .__O0OOOO000OOOOO0OO ,OOOO0OO0000O00000 ,OOOOO0OOOOOOO00OO ,OO000OO00OO000000 ,OO0OOOOOOOOOO0000 )#line:3312
            if OOO0OO00O0OO0OO00 :#line:3313
                return True #line:3314
            else :#line:3315
                return False #line:3316
        except :#line:3317
            return False #line:3318
    def get_bucket (OOOOOO00O0000OOOO ):#line:3320
        ""#line:3321
        from qiniu import BucketManager #line:3323
        OOOOOO0000OO0OO0O =BucketManager (OOOOOO00O0000OOOO .__O0OO0O0O00OO0O0O0 )#line:3324
        return OOOOOO0000OO0OO0O #line:3325
    def create_dir (OO00O0O00OOOOOO00 ,O0OOOOOO0O00OOO00 ):#line:3327
        ""#line:3332
        try :#line:3334
            O0OOOOOO0O00OOO00 =main ().get_path (O0OOOOOO0O00OOO00 )#line:3335
            O000OO0000O0O000O ='/tmp/dirname.pl'#line:3336
            public .writeFile (O000OO0000O0O000O ,'')#line:3337
            OOOO00O0O00000000 =OO00O0O00OOOOOO00 .__O0OO0O0O00OO0O0O0 .upload_token (OO00O0O00OOOOOO00 .__O0OOOO000OOOOO0OO ,O0OOOOOO0O00OOO00 )#line:3338
            OOO00OOO0OO00O0OO ,O0OO0OOO000OOOOO0 =put_file (OOOO00O0O00000000 ,O0OOOOOO0O00OOO00 ,O000OO0000O0O000O )#line:3339
            try :#line:3341
                os .remove (O000OO0000O0O000O )#line:3342
            except :#line:3343
                pass #line:3344
            if O0OO0OOO000OOOOO0 .status_code ==200 :#line:3346
                return True #line:3347
            return False #line:3348
        except Exception as O00000000O00OOO0O :#line:3349
            raise RuntimeError ("创建目录出现错误:"+str (O00000000O00OOO0O ))#line:3350
    def get_list (OOO00O000OOOOO0O0 ,get =None ):#line:3352
        OO0OOO000OO000OOO =OOO00O000OOOOO0O0 .get_bucket ()#line:3353
        OOOOOOOO000O0OOO0 ='/'#line:3354
        OO0O00O0000OOO0O0 =None #line:3355
        O00OO0O0OOOO0OOOO =1000 #line:3356
        OO00000O0O0O00O0O =main ().get_path (get .path )#line:3357
        O00O0OOO0OO00000O ,OO00000O000OO00O0 ,O00OO00O0O00OO0O0 =OO0OOO000OO000OOO .list (OOO00O000OOOOO0O0 .__O0OOOO000OOOOO0OO ,OO00000O0O0O00O0O ,OO0O00O0000OOO0O0 ,O00OO0O0OOOO0OOOO ,OOOOOOOO000O0OOO0 )#line:3358
        O000OOOOOOOO0OOOO =[]#line:3359
        if O00O0OOO0OO00000O :#line:3360
            OO000OO0000O00OO0 =O00O0OOO0OO00000O .get ("commonPrefixes")#line:3361
            if OO000OO0000O00OO0 :#line:3362
                for OO0000O000OOOOOO0 in OO000OO0000O00OO0 :#line:3363
                    OOO00O00OO0O00OOO ={}#line:3364
                    OO0O0O00O00OO0O00 =OO0000O000OOOOOO0 .replace (OO00000O0O0O00O0O ,'')#line:3365
                    OOO00O00OO0O00OOO ['name']=OO0O0O00O00OO0O00 #line:3366
                    OOO00O00OO0O00OOO ['type']=None #line:3367
                    O000OOOOOOOO0OOOO .append (OOO00O00OO0O00OOO )#line:3368
            O00O0OOOOO0OOO0OO =O00O0OOO0OO00000O ['items']#line:3370
            for O000OOO00O0O00OO0 in O00O0OOOOO0OOO0OO :#line:3371
                OOO00O00OO0O00OOO ={}#line:3372
                OO0O0O00O00OO0O00 =O000OOO00O0O00OO0 .get ("key")#line:3373
                OO0O0O00O00OO0O00 =OO0O0O00O00OO0O00 .replace (OO00000O0O0O00O0O ,'')#line:3374
                if not OO0O0O00O00OO0O00 :#line:3375
                    continue #line:3376
                OOO00O00OO0O00OOO ['name']=OO0O0O00O00OO0O00 #line:3377
                OOO00O00OO0O00OOO ['size']=O000OOO00O0O00OO0 .get ("fsize")#line:3378
                OOO00O00OO0O00OOO ['type']=O000OOO00O0O00OO0 .get ("type")#line:3379
                OOO00O00OO0O00OOO ['time']=O000OOO00O0O00OO0 .get ("putTime")#line:3380
                OOO00O00OO0O00OOO ['download']=OOO00O000OOOOO0O0 .generate_download_url (OO00000O0O0O00O0O +OO0O0O00O00OO0O00 )#line:3381
                O000OOOOOOOO0OOOO .append (OOO00O00OO0O00OOO )#line:3382
        else :#line:3383
            if hasattr (O00OO00O0O00OO0O0 ,"error"):#line:3384
                raise RuntimeError (O00OO00O0O00OO0O0 .error )#line:3385
        OOOOOOOO000OO0OO0 ={'path':OO00000O0O0O00O0O ,'list':O000OOOOOOOO0OOOO }#line:3386
        return OOOOOOOO000OO0OO0 #line:3387
    def generate_download_url (O000O00000O00O00O ,OO0OOO000O0000OOO ,expires =60 *60 ):#line:3389
        ""#line:3390
        OOOOOOOO0O0OO0O0O =O000O00000O00O00O .__OOO0O0O00OOOO0O0O #line:3391
        O00OO0OO00O00O000 ='http://%s/%s'%(OOOOOOOO0O0OO0O0O ,OO0OOO000O0000OOO )#line:3392
        O00OOO00OO0000OO0 =O000O00000O00O00O .__O0OO0O0O00OO0O0O0 .private_download_url (O00OO0OO00O00O000 ,expires =expires )#line:3393
        return O00OOO00OO0000OO0 #line:3394
    def resumable_upload (O000O00000OO000O0 ,OO000000O000O0OOO ,O000OOO00OO000O0O ,object_name =None ,progress_callback =None ,progress_file_name =None ,retries =5 ):#line:3396
        ""#line:3405
        try :#line:3407
            O000OOO0O0000OOOO =60 *60 #line:3408
            if object_name is None :#line:3410
                OOO0O0000OOOOOO00 ,O0O0OO0000OO0O00O =os .path .split (OO000000O000O0OOO )#line:3411
                O000O00000OO000O0 .__O000O0OO0OOO0OO00 =main ().get_path (os .path .dirname (O000OOO00OO000O0O ))#line:3412
                O0O0OO0000OO0O00O =O000O00000OO000O0 .__O000O0OO0OOO0OO00 +'/'+O0O0OO0000OO0O00O #line:3413
                O0O0OO0000OO0O00O =O0O0OO0000OO0O00O .replace ('//','/')#line:3414
                object_name =O0O0OO0000OO0O00O #line:3415
            OO0OOO0OO0O0O000O =O000O00000OO000O0 .__O0OO0O0O00OO0O0O0 .upload_token (O000O00000OO000O0 .__O0OOOO000OOOOO0OO ,object_name ,O000OOO0O0000OOOO )#line:3416
            if object_name [:1 ]=="/":#line:3418
                object_name =object_name [1 :]#line:3419
            print ("|-正在上传{}到七牛云存储".format (object_name ),end ='')#line:3421
            O0O0OOOOO000OOO00 ,OOO0O000O000O00OO =put_file (OO0OOO0OO0O0O000O ,object_name ,OO000000O000O0OOO ,check_crc =True ,progress_handler =progress_callback ,bucket_name =O000O00000OO000O0 .__O0OOOO000OOOOO0OO ,part_size =1024 *1024 *4 ,version ="v2")#line:3429
            O000OOO000OOOO000 =False #line:3430
            if sys .version_info [0 ]==2 :#line:3431
                O000OOO000OOOO000 =O0O0OOOOO000OOO00 ['key'].encode ('utf-8')==object_name #line:3432
            elif sys .version_info [0 ]==3 :#line:3433
                O000OOO000OOOO000 =O0O0OOOOO000OOO00 ['key']==object_name #line:3434
            if O000OOO000OOOO000 :#line:3435
                print (' ==> 成功')#line:3436
                return O0O0OOOOO000OOO00 ['hash']==etag (OO000000O000O0OOO )#line:3437
            return False #line:3438
        except Exception as O0OO0O0000OO00OOO :#line:3439
            print ("文件上传出现错误：",str (O0OO0O0000OO00OOO ))#line:3440
        if retries >0 :#line:3443
            print ("重试上传文件....")#line:3444
            return O000O00000OO000O0 .resumable_upload (OO000000O000O0OOO ,O000OOO00OO000O0O ,object_name =object_name ,progress_callback =progress_callback ,progress_file_name =progress_file_name ,retries =retries -1 ,)#line:3452
        return False #line:3453
    def upload_file_by_path (OOOOOOO0000000O00 ,O00OO00OO0OOO00O0 ,OOOO0OOO0000O0OO0 ):#line:3456
        return OOOOOOO0000000O00 .resumable_upload (O00OO00OO0OOO00O0 ,OOOO0OOO0000O0OO0 )#line:3457
    def delete_object_by_os (O0O0O0O00OOOO0OO0 ,OO0O00OO0OOOOOOOO ):#line:3459
        ""#line:3460
        OO00OO0O000O000O0 =O0O0O0O00OOOO0OO0 .get_bucket ()#line:3462
        O0O000OO0O000O0OO ,O0O000O00OOO0000O =OO00OO0O000O000O0 .delete (O0O0O0O00OOOO0OO0 .__O0OOOO000OOOOO0OO ,OO0O00OO0OOOOOOOO )#line:3463
        return O0O000OO0O000O0OO =={}#line:3464
    def get_object_info (O0O0000OOOOO000OO ,OOO0O0OOOOO00O000 ):#line:3466
        ""#line:3467
        try :#line:3468
            OO0OOO000O0O0O0OO =O0O0000OOOOO000OO .get_bucket ()#line:3469
            O0OO0OO000O0000O0 =OO0OOO000O0O0O0OO .stat (O0O0000OOOOO000OO .__O0OOOO000OOOOO0OO ,OOO0O0OOOOO00O000 )#line:3470
            return O0OO0OO000O0000O0 [0 ]#line:3471
        except :#line:3472
            return None #line:3473
    def remove_file (OOOOOOOOO00O00OOO ,OO0O000OO00O00OOO ):#line:3477
        try :#line:3478
            OO000OO000O0OO000 =OO0O000OO00O00OOO .filename #line:3479
            OOOOOOOOOOO00O0OO =OO0O000OO00O00OOO .path #line:3480
            if OOOOOOOOOOO00O0OO [-1 ]!="/":#line:3482
                OO000O0O00O000000 =OOOOOOOOOOO00O0OO +"/"+OO000OO000O0OO000 #line:3483
            else :#line:3484
                OO000O0O00O000000 =OOOOOOOOOOO00O0OO +OO000OO000O0OO000 #line:3485
            if OO000O0O00O000000 [-1 ]=="/":#line:3487
                return public .returnMsg (False ,"暂时不支持目录删除！")#line:3488
            if OO000O0O00O000000 [:1 ]=="/":#line:3490
                OO000O0O00O000000 =OO000O0O00O000000 [1 :]#line:3491
            if OOOOOOOOO00O00OOO .delete_object_by_os (OO000O0O00O000000 ):#line:3493
                return public .returnMsg (True ,'删除成功')#line:3494
            return public .returnMsg (False ,'文件{}删除失败, path:{}'.format (OO000O0O00O000000 ,OO0O000OO00O00OOO .path ))#line:3495
        except :#line:3496
            print (OOOOOOOOO00O00OOO .__O0O0OOOO00O0O0O00 )#line:3497
            return False #line:3498
class aws_main :#line:3502
    pass #line:3503
class upyun_main :#line:3505
    pass #line:3506
class obs_main :#line:3508
    __OO00O0O0O000000OO =None #line:3509
    __OOO0OO0O00OO000O0 =None #line:3510
    __O0O0OOOOO0OOO00OO =0 #line:3511
    __O0OOO0O0O000OOOO0 =None #line:3512
    __OOOOOO0OO0OOOO0OO =None #line:3513
    __OOOO0O000OO0O0OO0 =None #line:3514
    __OO00OOOO000OOOO0O =None #line:3515
    __O0O000OOO0O00OOOO ="ERROR: 无法连接华为云OBS !"#line:3516
    def __init__ (OO0OOO0OO0OO0O000 ):#line:3519
        OO0OOO0OO0OO0O000 .__OO0OO00O00OOOOOOO ()#line:3520
    def __OO0OO00O00OOOOOOO (O0O00O0O0000O0OO0 ):#line:3522
        ""#line:3525
        if O0O00O0O0000O0OO0 .__OO00O0O0O000000OO :return #line:3526
        OO000OO0OO00OO000 =O0O00O0O0000O0OO0 .get_config ()#line:3528
        O0O00O0O0000O0OO0 .__O0OOO0O0O000OOOO0 =OO000OO0OO00OO000 [0 ]#line:3529
        O0O00O0O0000O0OO0 .__OOOOOO0OO0OOOO0OO =OO000OO0OO00OO000 [1 ]#line:3530
        O0O00O0O0000O0OO0 .__OOOO0O000OO0O0OO0 =OO000OO0OO00OO000 [2 ]#line:3531
        O0O00O0O0000O0OO0 .__OO00OOOO000OOOO0O =OO000OO0OO00OO000 [3 ]#line:3532
        O0O00O0O0000O0OO0 .__OOO0OO0O00OO000O0 =main ().get_path (OO000OO0OO00OO000 [4 ])#line:3533
        try :#line:3534
            O0O00O0O0000O0OO0 .__OO00O0O0O000000OO =ObsClient (access_key_id =O0O00O0O0000O0OO0 .__O0OOO0O0O000OOOO0 ,secret_access_key =O0O00O0O0000O0OO0 .__OOOOOO0OO0OOOO0OO ,server =O0O00O0O0000O0OO0 .__OO00OOOO000OOOO0O ,)#line:3540
        except Exception as O0O0000O0OOOO00O0 :#line:3541
            pass #line:3542
    def get_config (OOOOOOOOOO000000O ,get =None ):#line:3546
        ""#line:3549
        OOO0OOOO00000OO00 =main ()._config_path +'/obs.conf'#line:3550
        if not os .path .isfile (OOO0OOOO00000OO00 ):#line:3552
            O0000000OO0OOO000 =''#line:3553
            if os .path .isfile (main ()._plugin_path +'/obs/config.conf'):#line:3554
                O0000000OO0OOO000 =main ()._plugin_path +'/obs/config.conf'#line:3555
            elif os .path .isfile (main ()._setup_path +'/data/obsAS.conf'):#line:3556
                O0000000OO0OOO000 =main ()._plugin_path +'/data/obsAS.conf'#line:3557
            if O0000000OO0OOO000 :#line:3558
                OO0000O0O0O0O00O0 =json .loads (public .readFile (O0000000OO0OOO000 ))#line:3559
                O0O00OOOO0O000OOO =OO0000O0O0O0O00O0 ['access_key']+'|'+OO0000O0O0O0O00O0 ['secret_key']+'|'+OO0000O0O0O0O00O0 ['bucket_name']+'|'+OO0000O0O0O0O00O0 ['bucket_domain']+'|'+OO0000O0O0O0O00O0 ['backup_path']#line:3560
                public .writeFile (OOO0OOOO00000OO00 ,O0O00OOOO0O000OOO )#line:3561
        if not os .path .isfile (OOO0OOOO00000OO00 ):return ['','','','','/']#line:3562
        O000O00OOOO00OO00 =public .readFile (OOO0OOOO00000OO00 )#line:3563
        if not O000O00OOOO00OO00 :return ['','','','','/']#line:3564
        OOO000O00O00O000O =O000O00OOOO00OO00 .split ('|')#line:3565
        if len (OOO000O00O00O000O )<5 :OOO000O00O00O000O .append ('/')#line:3566
        return OOO000O00O00O000O #line:3567
    def check_config (O000O000O000OO000 ):#line:3570
        try :#line:3571
            O0OO0O0OO0OO00OO0 =[]#line:3572
            OOOOOOO000O0O000O =main ().get_path ('/')#line:3573
            O00000OOOOOO000O0 =O000O000O000OO000 .__OO00O0O0O000000OO .listObjects (O000O000O000OO000 .__OOOO0O000OO0O0OO0 ,prefix =OOOOOOO000O0O000O ,)#line:3577
            for OOO000O0OO00OOOO0 in O00000OOOOOO000O0 .body .contents :#line:3579
                if OOO000O0OO00OOOO0 .size !=0 :#line:3580
                    if not OOO000O0OO00OOOO0 .key :continue ;#line:3581
                    O000O00O0O00O0OO0 ={}#line:3582
                    O0OO0O00OOO000OOO =OOO000O0OO00OOOO0 .key #line:3583
                    O0OO0O00OOO000OOO =O0OO0O00OOO000OOO [O0OO0O00OOO000OOO .find (OOOOOOO000O0O000O )+len (OOOOOOO000O0O000O ):]#line:3584
                    O0OO0OOO0O0OO0OO0 =OOO000O0OO00OOOO0 .key .split ('/')#line:3585
                    if len (O0OO0OOO0O0OO0OO0 )>1000000 :continue ;#line:3586
                    O0OO00O00OOO0O000 =re .compile (r'/')#line:3587
                    if O0OO00O00OOO0O000 .search (O0OO0O00OOO000OOO )!=None :continue ;#line:3588
                    O000O00O0O00O0OO0 ["type"]=True #line:3589
                    O000O00O0O00O0OO0 ["name"]=O0OO0O00OOO000OOO #line:3590
                    O000O00O0O00O0OO0 ['size']=OOO000O0OO00OOOO0 .size #line:3591
                    O00OO0000O00O0O0O =OOO000O0OO00OOOO0 .lastModified #line:3592
                    O0000OO0OO0OOOOO0 =datetime .datetime .strptime (O00OO0000O00O0O0O ,"%Y/%m/%d %H:%M:%S")#line:3593
                    O0000OO0OO0OOOOO0 +=datetime .timedelta (hours =0 )#line:3594
                    OO0O00O0OOOOO00OO =int ((time .mktime (O0000OO0OO0OOOOO0 .timetuple ())+O0000OO0OO0OOOOO0 .microsecond /1000000.0 ))#line:3595
                    O000O00O0O00O0OO0 ['time']=OO0O00O0OOOOO00OO #line:3596
                    O0OO0O0OO0OO00OO0 .append (O000O00O0O00O0OO0 )#line:3597
                elif OOO000O0OO00OOOO0 .size ==0 :#line:3598
                    if not OOO000O0OO00OOOO0 .key :continue ;#line:3599
                    if OOO000O0OO00OOOO0 .key [-1 ]!="/":continue ;#line:3600
                    O0OO0OOO0O0OO0OO0 =OOO000O0OO00OOOO0 .key .split ('/')#line:3601
                    O000O00O0O00O0OO0 ={}#line:3602
                    O0OO0O00OOO000OOO =OOO000O0OO00OOOO0 .key #line:3603
                    O0OO0O00OOO000OOO =O0OO0O00OOO000OOO [O0OO0O00OOO000OOO .find (OOOOOOO000O0O000O )+len (OOOOOOO000O0O000O ):]#line:3604
                    if OOOOOOO000O0O000O ==""and len (O0OO0OOO0O0OO0OO0 )>2 :continue ;#line:3605
                    if OOOOOOO000O0O000O !="":#line:3606
                        O0OO0OOO0O0OO0OO0 =O0OO0O00OOO000OOO .split ('/')#line:3607
                        if len (O0OO0OOO0O0OO0OO0 )>2 :continue ;#line:3608
                        else :#line:3609
                            O0OO0O00OOO000OOO =O0OO0O00OOO000OOO #line:3610
                    if not O0OO0O00OOO000OOO :continue ;#line:3611
                    O000O00O0O00O0OO0 ["type"]=None #line:3612
                    O000O00O0O00O0OO0 ["name"]=O0OO0O00OOO000OOO #line:3613
                    O000O00O0O00O0OO0 ['size']=OOO000O0OO00OOOO0 .size #line:3614
                    O0OO0O0OO0OO00OO0 .append (O000O00O0O00O0OO0 )#line:3615
            return True #line:3616
        except :#line:3617
            return False #line:3618
    def upload_file_by_path (O000O0O0O0O0OOO00 ,O0O0O00O0O00O00O0 ,O0OO00O0O00O0OOO0 ):#line:3620
        ""#line:3625
        O000O0O0O0O0OOO00 .__OO0OO00O00OOOOOOO ()#line:3627
        if not O000O0O0O0O0OOO00 .__OO00O0O0O000000OO :#line:3628
            return False #line:3629
        if O0OO00O0O00O0OOO0 !=None :#line:3631
            OOOO00O0OO0000000 =O000O0O0O0O0OOO00 .__OO00O0O0O000000OO .listObjects (O000O0O0O0O0OOO00 .__OOOO0O000OO0O0OO0 ,prefix ="",)#line:3635
            O0OOO0000O00OO00O =O0OO00O0O00O0OOO0 .split ("/")#line:3636
            O00O00O0000OO0000 =""#line:3637
            O000O000OO00OO00O =[]#line:3638
            for OO00000O00OO0O00O in OOOO00O0OO0000000 .body .contents :#line:3639
                    if not OO00000O00OO0O00O .key :continue #line:3640
                    O000O000OO00OO00O .append (OO00000O00OO0O00O .key )#line:3641
            for O0OO00OO00O000000 in range (0 ,(len (O0OOO0000O00OO00O )-1 )):#line:3642
                if O00O00O0000OO0000 =="":#line:3643
                    O00O00O0000OO0000 =O0OOO0000O00OO00O [O0OO00OO00O000000 ]+"/"#line:3644
                else :#line:3645
                    O00O00O0000OO0000 =O00O00O0000OO0000 +O0OOO0000O00OO00O [O0OO00OO00O000000 ]+"/"#line:3646
                if not O00O00O0000OO0000 :continue #line:3647
                if main ().get_path (O00O00O0000OO0000 )not in O000O000OO00OO00O :#line:3648
                    OOOO00O0OO0000000 =O000O0O0O0O0OOO00 .__OO00O0O0O000000OO .putContent (O000O0O0O0O0OOO00 .__OOOO0O000OO0O0OO0 ,objectKey =main ().get_path (O00O00O0000OO0000 ),)#line:3652
        try :#line:3654
            print ('|-正在上传{}到华为云存储'.format (O0O0O00O0O00O00O0 ),end ='')#line:3655
            O00OOOO0OOOO00000 ,OOOO0O0000O00O0O0 =os .path .split (O0O0O00O0O00O00O0 )#line:3656
            O000O0O0O0O0OOO00 .__OOO0OO0O00OO000O0 =main ().get_path (os .path .dirname (O0OO00O0O00O0OOO0 ))#line:3657
            OOOO0O0000O00O0O0 =O000O0O0O0O0OOO00 .__OOO0OO0O00OO000O0 +OOOO0O0000O00O0O0 #line:3658
            OOOO0O000OOOO00OO =5 *1024 *1024 #line:3659
            O0OOOO00O0OO0OOOO =O0O0O00O0O00O00O0 #line:3660
            OOO0OOO0O00O00O0O =OOOO0O0000O00O0O0 #line:3661
            OO0000OO0OO0O000O =True #line:3662
            OOOO00O0OO0000000 =O000O0O0O0O0OOO00 .__OO00O0O0O000000OO .uploadFile (O000O0O0O0O0OOO00 .__OOOO0O000OO0O0OO0 ,OOO0OOO0O00O00O0O ,O0OOOO00O0OO0OOOO ,OOOO0O000OOOO00OO ,OO0000OO0OO0O000O ,)#line:3669
            if OOOO00O0OO0000000 .status <300 :#line:3670
                print (' ==> 成功')#line:3671
                return True #line:3672
        except Exception as OO000O00OO0000O00 :#line:3673
            time .sleep (1 )#line:3675
            O000O0O0O0O0OOO00 .__O0O0OOOOO0OOO00OO +=1 #line:3676
            if O000O0O0O0O0OOO00 .__O0O0OOOOO0OOO00OO <2 :#line:3677
                O000O0O0O0O0OOO00 .upload_file_by_path (O0O0O00O0O00O00O0 ,O0OO00O0O00O0OOO0 )#line:3679
            return False #line:3680
    def get_list (O0OO000OO000OOOOO ,get =None ):#line:3683
        ""#line:3686
        O0OO000OO000OOOOO .__OO0OO00O00OOOOOOO ()#line:3688
        if not O0OO000OO000OOOOO .__OO00O0O0O000000OO :#line:3689
            return False #line:3690
        O0O00OO0000OO0O0O =[]#line:3691
        O0O0000OOOO000O0O =main ().get_path (get .path )#line:3692
        O00OOOOOO000OO0OO =O0OO000OO000OOOOO .__OO00O0O0O000000OO .listObjects (O0OO000OO000OOOOO .__OOOO0O000OO0O0OO0 ,prefix =O0O0000OOOO000O0O ,)#line:3696
        for O0O0OOO00O000O0OO in O00OOOOOO000OO0OO .body .contents :#line:3698
            if O0O0OOO00O000O0OO .size !=0 :#line:3699
                if not O0O0OOO00O000O0OO .key :continue ;#line:3700
                O00000O0O00OOOO0O ={}#line:3701
                O000OO0OOOO0O0OOO =O0O0OOO00O000O0OO .key #line:3702
                O000OO0OOOO0O0OOO =O000OO0OOOO0O0OOO [O000OO0OOOO0O0OOO .find (O0O0000OOOO000O0O )+len (O0O0000OOOO000O0O ):]#line:3703
                OO00000O00O00OOOO =O0O0OOO00O000O0OO .key .split ('/')#line:3704
                if len (OO00000O00O00OOOO )>1000000 :continue ;#line:3705
                OO0O0O0O0O0O00O0O =re .compile (r'/')#line:3706
                if OO0O0O0O0O0O00O0O .search (O000OO0OOOO0O0OOO )!=None :continue ;#line:3707
                O00000O0O00OOOO0O ["type"]=True #line:3708
                O00000O0O00OOOO0O ["name"]=O000OO0OOOO0O0OOO #line:3709
                O00000O0O00OOOO0O ['size']=O0O0OOO00O000O0OO .size #line:3710
                O00000O0O00OOOO0O ['download']=O0OO000OO000OOOOO .download_file (O0O0000OOOO000O0O +O000OO0OOOO0O0OOO )#line:3711
                OOO0OOO0O00O0OO0O =O0O0OOO00O000O0OO .lastModified #line:3712
                OO0OOOOO00OO00O0O =datetime .datetime .strptime (OOO0OOO0O00O0OO0O ,"%Y/%m/%d %H:%M:%S")#line:3713
                OO0OOOOO00OO00O0O +=datetime .timedelta (hours =0 )#line:3714
                O0OOO00OOOOOO0OO0 =int ((time .mktime (OO0OOOOO00OO00O0O .timetuple ())+OO0OOOOO00OO00O0O .microsecond /1000000.0 ))#line:3715
                O00000O0O00OOOO0O ['time']=O0OOO00OOOOOO0OO0 #line:3716
                O0O00OO0000OO0O0O .append (O00000O0O00OOOO0O )#line:3717
            elif O0O0OOO00O000O0OO .size ==0 :#line:3718
                if not O0O0OOO00O000O0OO .key :continue ;#line:3719
                if O0O0OOO00O000O0OO .key [-1 ]!="/":continue ;#line:3720
                OO00000O00O00OOOO =O0O0OOO00O000O0OO .key .split ('/')#line:3721
                O00000O0O00OOOO0O ={}#line:3722
                O000OO0OOOO0O0OOO =O0O0OOO00O000O0OO .key #line:3723
                O000OO0OOOO0O0OOO =O000OO0OOOO0O0OOO [O000OO0OOOO0O0OOO .find (O0O0000OOOO000O0O )+len (O0O0000OOOO000O0O ):]#line:3724
                if O0O0000OOOO000O0O ==""and len (OO00000O00O00OOOO )>2 :continue ;#line:3725
                if O0O0000OOOO000O0O !="":#line:3726
                    OO00000O00O00OOOO =O000OO0OOOO0O0OOO .split ('/')#line:3727
                    if len (OO00000O00O00OOOO )>2 :continue ;#line:3728
                    else :#line:3729
                        O000OO0OOOO0O0OOO =O000OO0OOOO0O0OOO #line:3730
                if not O000OO0OOOO0O0OOO :continue ;#line:3731
                O00000O0O00OOOO0O ["type"]=None #line:3732
                O00000O0O00OOOO0O ["name"]=O000OO0OOOO0O0OOO #line:3733
                O00000O0O00OOOO0O ['size']=O0O0OOO00O000O0OO .size #line:3734
                O0O00OO0000OO0O0O .append (O00000O0O00OOOO0O )#line:3735
        O00OO0O00O0OOO000 ={'path':O0O0000OOOO000O0O ,'list':O0O00OO0000OO0O0O }#line:3737
        return O00OO0O00O0OOO000 #line:3738
    def download_file (O000000OO00OO00OO ,OO00O000OO0O000O0 ):#line:3740
        ""#line:3743
        O000000OO00OO00OO .__OO0OO00O00OOOOOOO ()#line:3745
        if not O000000OO00OO00OO .__OO00O0O0O000000OO :#line:3746
            return None #line:3747
        try :#line:3748
            O0OOO00OOOO00OO0O =O000000OO00OO00OO .__OO00O0O0O000000OO .createSignedUrl ('GET',O000000OO00OO00OO .__OOOO0O000OO0O0OO0 ,OO00O000OO0O000O0 ,expires =3600 ,)#line:3753
            OO0O00OO0O0000OO0 =O0OOO00OOOO00OO0O .signedUrl #line:3754
            return OO0O00OO0O0000OO0 #line:3755
        except :#line:3756
            print (O000000OO00OO00OO .__O0O000OOO0O00OOOO )#line:3757
            return None #line:3758
    def delete_file (O0O000O0000OOO000 ,OO000OOO000OOOO0O ):#line:3760
        ""#line:3764
        O0O000O0000OOO000 .__OO0OO00O00OOOOOOO ()#line:3766
        if not O0O000O0000OOO000 .__OO00O0O0O000000OO :#line:3767
            return False #line:3768
        try :#line:3770
            OO0O000OO0OO00OOO =O0O000O0000OOO000 .__OO00O0O0O000000OO .deleteObject (O0O000O0000OOO000 .__OOOO0O000OO0O0OO0 ,OO000OOO000OOOO0O )#line:3771
            return OO0O000OO0OO00OOO #line:3772
        except Exception as OO0O00OOOO00OOOOO :#line:3773
            O0O000O0000OOO000 .__O0O0OOOOO0OOO00OO +=1 #line:3774
            if O0O000O0000OOO000 .__O0O0OOOOO0OOO00OO <2 :#line:3775
                O0O000O0000OOO000 .delete_file (OO000OOO000OOOO0O )#line:3777
            print (O0O000O0000OOO000 .__O0O000OOO0O00OOOO )#line:3778
            return None #line:3779
    def remove_file (O0000OO00OO0O00OO ,OOO00OOOOOO0OO00O ):#line:3782
        O0O0OOO0OOOOOOO0O =main ().get_path (OOO00OOOOOO0OO00O .path )#line:3783
        O0O0000OO0O0O00OO =O0O0OOO0OOOOOOO0O +OOO00OOOOOO0OO00O .filename #line:3784
        O0000OO00OO0O00OO .delete_file (O0O0000OO0O0O00OO )#line:3785
        return public .returnMsg (True ,'删除文件成功!')#line:3786
class bos_main :#line:3790
    __O000O0OOO00O00000 =None #line:3791
    __O0000OOO00O00O00O =0 #line:3792
    __OOOOOO000OOOOOOOO =None #line:3793
    __O0OOOOOOOOO0OOOO0 =None #line:3794
    __OO00O0OOO000O0O00 =None #line:3795
    __OOOO0OOO0O000000O ="ERROR: 无法连接百度云存储 !"#line:3796
    def __init__ (OO000000000O0O0OO ):#line:3799
        OO000000000O0O0OO .__O00000OOOOOOOO0OO ()#line:3800
    def __O00000OOOOOOOO0OO (O00OO0O00OO0OOO0O ):#line:3802
        ""#line:3805
        if O00OO0O00OO0OOO0O .__O000O0OOO00O00000 :return #line:3806
        O000OOOOOO0O00OO0 =O00OO0O00OO0OOO0O .get_config ()#line:3808
        O00OO0O00OO0OOO0O .__OOOOOO000OOOOOOOO =O000OOOOOO0O00OO0 [0 ]#line:3809
        O00OO0O00OO0OOO0O .__O0OOOOOOOOO0OOOO0 =O000OOOOOO0O00OO0 [1 ]#line:3810
        O00OO0O00OO0OOO0O .__O00O0OO0O0000OO00 =O000OOOOOO0O00OO0 [2 ]#line:3811
        O00OO0O00OO0OOO0O .__OO00O0OOO000O0O00 =O000OOOOOO0O00OO0 [3 ]#line:3812
        O00OO0O00OO0OOO0O .__OOOOO0OOO0O00O0O0 =main ().get_path (O000OOOOOO0O00OO0 [4 ])#line:3814
        try :#line:3815
            O0OOO000OO0OOOO0O =BceClientConfiguration (credentials =BceCredentials (O00OO0O00OO0OOO0O .__OOOOOO000OOOOOOOO ,O00OO0O00OO0OOO0O .__O0OOOOOOOOO0OOOO0 ),endpoint =O00OO0O00OO0OOO0O .__OO00O0OOO000O0O00 )#line:3818
            O00OO0O00OO0OOO0O .__O000O0OOO00O00000 =BosClient (O0OOO000OO0OOOO0O )#line:3819
        except Exception as O0OOOOOO0O0OOOOOO :#line:3820
            pass #line:3821
    def get_config (OO000OOOO0000000O ,get =None ):#line:3825
        ""#line:3828
        OO0O0O0OOO0O00OOO =main ()._config_path +'/bos.conf'#line:3829
        if not os .path .isfile (OO0O0O0OOO0O00OOO ):#line:3831
            O0OOOO000O00O0OO0 =''#line:3832
            if os .path .isfile (main ()._plugin_path +'/bos/config.conf'):#line:3833
                O0OOOO000O00O0OO0 =main ()._plugin_path +'/bos/config.conf'#line:3834
            elif os .path .isfile (main ()._setup_path +'/data/bosAS.conf'):#line:3835
                O0OOOO000O00O0OO0 =main ()._setup_path +'/data/bosAS.conf'#line:3836
            if O0OOOO000O00O0OO0 :#line:3837
                OOOOOOOO00O0O00OO =json .loads (public .readFile (O0OOOO000O00O0OO0 ))#line:3838
                OO00OOO0OO0OO00O0 =OOOOOOOO00O0O00OO ['access_key']+'|'+OOOOOOOO00O0O00OO ['secret_key']+'|'+OOOOOOOO00O0O00OO ['bucket_name']+'|'+OOOOOOOO00O0O00OO ['bucket_domain']+'|'+OOOOOOOO00O0O00OO ['backup_path']#line:3839
                public .writeFile (OO0O0O0OOO0O00OOO ,OO00OOO0OO0OO00O0 )#line:3840
        if not os .path .isfile (OO0O0O0OOO0O00OOO ):return ['','','','','/']#line:3841
        OOOOOOOOO0O0O00OO =public .readFile (OO0O0O0OOO0O00OOO )#line:3842
        if not OOOOOOOOO0O0O00OO :return ['','','','','/']#line:3843
        O0O0O0O000OO0OOO0 =OOOOOOOOO0O0O00OO .split ('|')#line:3844
        if len (O0O0O0O000OO0OOO0 )<5 :O0O0O0O000OO0OOO0 .append ('/')#line:3845
        return O0O0O0O000OO0OOO0 #line:3846
    def check_config (O0O0OO000OO0O00OO ):#line:3848
        ""#line:3851
        if not O0O0OO000OO0O00OO .__O000O0OOO00O00000 :return False #line:3852
        try :#line:3853
            OOOO0OO00OOOOOO0O ='/'#line:3854
            OOO0O0OO0OO0O0O0O =O0O0OO000OO0O00OO .__O000O0OOO00O00000 .list_objects (O0O0OO000OO0O00OO .__O00O0OO0O0000OO00 ,prefix =OOOO0OO00OOOOOO0O ,delimiter ="/")#line:3856
            return True #line:3857
        except :#line:3858
            return False #line:3859
    def resumable_upload (OO0O00O0O000OO0OO ,OO000OOO0OOOOOO00 ,object_name =None ,progress_callback =None ,progress_file_name =None ,retries =5 ,):#line:3867
            ""#line:3874
            try :#line:3876
                if object_name [:1 ]=="/":#line:3877
                    object_name =object_name [1 :]#line:3878
                print ("|-正在上传{}到百度云存储".format (object_name ),end ='')#line:3879
                import multiprocessing #line:3880
                O0000O00O00O00OOO =OO000OOO0OOOOOO00 #line:3881
                OO0OOOOO00O0O0O0O =object_name #line:3882
                OO00O00000OO000OO =OO0O00O0O000OO0OO .__O00O0OO0O0000OO00 #line:3883
                OOO0O00OOOOOO0000 =OO0O00O0O000OO0OO .__O000O0OOO00O00000 .put_super_obejct_from_file (OO00O00000OO000OO ,OO0OOOOO00O0O0O0O ,O0000O00O00O00OOO ,chunk_size =5 ,thread_num =multiprocessing .cpu_count ()-1 )#line:3888
                if OOO0O00OOOOOO0000 :#line:3889
                    print (' ==> 成功')#line:3890
                    return True #line:3891
            except Exception as O000O0000O000OO00 :#line:3892
                print ("文件上传出现错误：")#line:3893
                print (O000O0000O000OO00 )#line:3894
            if retries >0 :#line:3897
                print ("重试上传文件....")#line:3898
                return OO0O00O0O000OO0OO .resumable_upload (OO000OOO0OOOOOO00 ,object_name =object_name ,progress_callback =progress_callback ,progress_file_name =progress_file_name ,retries =retries -1 ,)#line:3905
            return False #line:3906
    def upload_file_by_path (OOO000O00O000OO00 ,O0O000000000O00OO ,O00OOO0O0O000O00O ):#line:3908
        ""#line:3911
        return OOO000O00O000OO00 .resumable_upload (O0O000000000O00OO ,O00OOO0O0O000O00O )#line:3912
    def get_list (OOO0OO0O000000OOO ,get =None ):#line:3914
        O00OO0000OOOOO0O0 =[]#line:3915
        OO0000OOO0O0OOOO0 =[]#line:3916
        O0O0O000OOO00OO0O =main ().get_path (get .path )#line:3917
        try :#line:3918
            O0OOO0O00OOO000O0 =OOO0OO0O000000OOO .__O000O0OOO00O00000 .list_objects (OOO0OO0O000000OOO .__O00O0OO0O0000OO00 ,prefix =O0O0O000OOO00OO0O ,delimiter ="/")#line:3920
            for OOOOO0OO00000OOO0 in O0OOO0O00OOO000O0 .contents :#line:3921
                if not OOOOO0OO00000OOO0 .key :continue #line:3922
                OOOO0OO0O0OOOO000 ={}#line:3923
                O0O0000O0000OO000 =OOOOO0OO00000OOO0 .key #line:3924
                O0O0000O0000OO000 =O0O0000O0000OO000 [O0O0000O0000OO000 .find (O0O0O000OOO00OO0O )+len (O0O0O000OOO00OO0O ):]#line:3925
                if not O0O0000O0000OO000 :continue #line:3926
                OOOO0OO0O0OOOO000 ["name"]=O0O0000O0000OO000 #line:3927
                OOOO0OO0O0OOOO000 ['size']=OOOOO0OO00000OOO0 .size #line:3928
                OOOO0OO0O0OOOO000 ["type"]=True #line:3929
                OOOO0OO0O0OOOO000 ['download']=OOO0OO0O000000OOO .download_file (O0O0O000OOO00OO0O +"/"+O0O0000O0000OO000 )#line:3930
                OO00OOOOOO0OO0O00 =OOOOO0OO00000OOO0 .last_modified #line:3931
                OO0OO000O0O000O00 =datetime .datetime .strptime (OO00OOOOOO0OO0O00 ,"%Y-%m-%dT%H:%M:%SZ")#line:3932
                OO0OO000O0O000O00 +=datetime .timedelta (hours =8 )#line:3933
                OOOO0OOOOO0O0O0O0 =int ((time .mktime (OO0OO000O0O000O00 .timetuple ())+OO0OO000O0O000O00 .microsecond /1000000.0 ))#line:3934
                OOOO0OO0O0OOOO000 ['time']=OOOO0OOOOO0O0O0O0 #line:3935
                O00OO0000OOOOO0O0 .append (OOOO0OO0O0OOOO000 )#line:3936
            for O0000OO000OO0000O in O0OOO0O00OOO000O0 .common_prefixes :#line:3937
                if not O0000OO000OO0000O .prefix :continue #line:3938
                if O0000OO000OO0000O .prefix [0 :-1 ]==O0O0O000OOO00OO0O :continue #line:3939
                OOOO0OO0O0OOOO000 ={}#line:3940
                O0000OO000OO0000O .prefix =O0000OO000OO0000O .prefix .replace (O0O0O000OOO00OO0O ,'')#line:3941
                OOOO0OO0O0OOOO000 ["name"]=O0000OO000OO0000O .prefix #line:3942
                OOOO0OO0O0OOOO000 ["type"]=None #line:3943
                OOOO0OO0O0OOOO000 ['size']=O0000OO000OO0000O .size #line:3944
                O00OO0000OOOOO0O0 .append (OOOO0OO0O0OOOO000 )#line:3945
            OO0O0000O00O00O0O ={'path':O0O0O000OOO00OO0O ,'list':O00OO0000OOOOO0O0 }#line:3946
            return OO0O0000O00O00O0O #line:3947
        except :#line:3948
            OO0O0000O00O00O0O ={}#line:3949
            if OOO0OO0O000000OOO .__O000O0OOO00O00000 :#line:3950
                OO0O0000O00O00O0O ['status']=True #line:3951
            else :#line:3952
                OO0O0000O00O00O0O ['status']=False #line:3953
            OO0O0000O00O00O0O ['path']=get .path #line:3954
            OO0O0000O00O00O0O ['list']=O00OO0000OOOOO0O0 #line:3955
            OO0O0000O00O00O0O ['dir']=OO0000OOO0O0OOOO0 #line:3956
            return OO0O0000O00O00O0O #line:3957
    def download_file (OOO0O00O0000OO00O ,O0O0OO0OO0000O00O ):#line:3959
        ""#line:3962
        OOO0O00O0000OO00O .__O00000OOOOOOOO0OO ()#line:3964
        if not OOO0O00O0000OO00O .__O000O0OOO00O00000 :#line:3965
            return None #line:3966
        try :#line:3968
            OOO00O0O0OOOOOO00 =OOO0O00O0000OO00O .__O000O0OOO00O00000 .generate_pre_signed_url (OOO0O00O0000OO00O .__O00O0OO0O0000OO00 ,O0O0OO0OO0000O00O )#line:3969
            _OO00OO0OO0000OOOO =sys .version_info #line:3970
            O00OO00OO00O0O00O =(_OO00OO0OO0000OOOO [0 ]==2 )#line:3972
            O0O000OO0O00OOOOO =(_OO00OO0OO0000OOOO [0 ]==3 )#line:3975
            if O0O000OO0O00OOOOO :#line:3976
                OOO00O0O0OOOOOO00 =str (OOO00O0O0OOOOOO00 ,encoding ="utf-8")#line:3977
            else :#line:3978
                OOO00O0O0OOOOOO00 =OOO00O0O0OOOOOO00 #line:3979
            return OOO00O0O0OOOOOO00 #line:3980
        except :#line:3981
            print (OOO0O00O0000OO00O .__OOOO0OOO0O000000O )#line:3982
            return None #line:3983
    def delete_file (OO00O00000OOO00OO ,OOO000OOO0OOO0000 ):#line:3985
        ""#line:3989
        OO00O00000OOO00OO .__O00000OOOOOOOO0OO ()#line:3991
        if not OO00O00000OOO00OO .__O000O0OOO00O00000 :#line:3992
            return False #line:3993
        try :#line:3995
            OOOOOOOOOOOO00O0O =OO00O00000OOO00OO .__O000O0OOO00O00000 .delete_object (OO00O00000OOO00OO .__O00O0OO0O0000OO00 ,OOO000OOO0OOO0000 )#line:3996
            return OOOOOOOOOOOO00O0O #line:3997
        except Exception as O0O00OO000O0O0O0O :#line:3998
            OO00O00000OOO00OO .__O0000OOO00O00O00O +=1 #line:3999
            if OO00O00000OOO00OO .__O0000OOO00O00O00O <2 :#line:4000
                OO00O00000OOO00OO .delete_file (OOO000OOO0OOO0000 )#line:4002
            print (OO00O00000OOO00OO .__OOOO0OOO0O000000O )#line:4003
            return None #line:4004
    def remove_file (O00OOOO0OOO000O00 ,O0OO00OO0O0OO0OOO ):#line:4007
        OO000OO00O000OO00 =main ().get_path (O0OO00OO0O0OO0OOO .path )#line:4008
        OOO00000OO0OO000O =OO000OO00O000OO00 +O0OO00OO0O0OO0OOO .filename #line:4009
        O00OOOO0OOO000O00 .delete_file (OOO00000OO0OO000O )#line:4010
        return public .returnMsg (True ,'删除文件成功!')#line:4011
class gcloud_storage_main :#line:4014
    pass #line:4015
class gdrive_main :#line:4017
    pass #line:4018
class msonedrive_main :#line:4020
    pass #line:4021
if __name__ =='__main__':#line:4025
    import argparse #line:4026
    args_obj =argparse .ArgumentParser (usage ="必要的参数：--db_name 数据库名称!")#line:4027
    args_obj .add_argument ("--db_name",help ="数据库名称!")#line:4028
    args_obj .add_argument ("--binlog_id",help ="任务id")#line:4029
    args =args_obj .parse_args ()#line:4030
    if not args .db_name :#line:4031
        args_obj .print_help ()#line:4032
    p =main ()#line:4033
    p ._db_name =args .db_name #line:4034
    if args .binlog_id :p ._binlog_id =args .binlog_id #line:4035
    if p ._binlog_id :#line:4037
        p .execute_by_comandline ()#line:4038
