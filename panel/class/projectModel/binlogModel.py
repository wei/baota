import os, sys, time, json, re, datetime, shutil, threading  #line:13

os.chdir('/www/server/panel')  #line:14
sys.path.append("class/")  #line:15
import public  #line:16
from projectModel.base import projectBase  #line:17
from panelMysql import panelMysql  #line:18
from panelBackup import backup  #line:19
import db_mysql  #line:20
try:  #line:21
    import oss2  #line:22
except:
    pass  #line:23
try:  #line:24
    from qcloud_cos import CosConfig  #line:25
    from qcloud_cos import CosS3Client  #line:26
except:
    pass  #line:27
try:  #line:28
    from qiniu import Auth, put_file, etag  #line:29
except:
    pass  #line:30
try:  #line:31
    from baidubce.bce_client_configuration import BceClientConfiguration  #line:32
    from baidubce.auth.bce_credentials import BceCredentials  #line:33
    from baidubce.services.bos.bos_client import BosClient  #line:34
except:
    pass  #line:35
try:  #line:36
    from obs import ObsClient  #line:37
except:
    pass  #line:38


class main(projectBase):  #line:39
    _setup_path = '/www/server/panel/'  #line:40
    _binlog_id = ''  #line:41
    _db_name = ''  #line:42
    _zip_password = ''  #line:43
    _backup_end_time = ''  #line:44
    _backup_start_time = ''  #line:45
    _backup_type = ''  #line:46
    _cloud_name = ''  #line:47
    _full_zip_name = ''  #line:48
    _full_file = ''  #line:49
    _inc_file = ''  #line:50
    _file = ''  #line:51
    _pdata = {}  #line:52
    _echo_info = {}  #line:53
    _inode_min = 100  #line:54
    _temp_path = './temp/'  #line:55
    _tables = []  #line:56
    _new_tables = []  #line:57
    _backup_fail_list = []  #line:58
    _backup_full_list = []  #line:59
    _cloud_upload_not = []  #line:60
    _full_info = []  #line:61
    _inc_info = []  #line:62
    _mysql_bin_index = '/www/server/data/mysql-bin.index'  #line:63
    _save_cycle = 3600  #line:64
    _compress = True  #line:65
    _mysqlbinlog_bin = '/www/server/mysql/bin/mysqlbinlog'  #line:66
    _save_default_path = '/www/backup/mysql_bin_log/'  #line:67
    _mysql_root_password = public.M('config').where('id=?', (1, )).getField(
        'mysql_root')  #line:68
    _install_path = '{}script/binlog_cloud.sh'.format(_setup_path)  #line:69
    _config_path = '{}config/mysqlbinlog_info'.format(_setup_path)  #line:70
    _python_path = '{}pyenv/bin/python'.format(_setup_path)  #line:71
    _binlogModel_py = '{}class/projectModel/binlogModel.py'.format(
        _setup_path)  #line:72
    _mybackup = backup()  #line:73
    _plugin_path = '{}plugin/'.format(_setup_path)  #line:74
    _binlog_conf = '{}config/mysqlbinlog_info/binlog.conf'.format(
        _setup_path)  #line:75
    _start_time_list = []  #line:76
    _db_mysql = db_mysql.panelMysql()  #line:77

    def __init__(O0000OOOO0O00OOO0):  #line:80
        if not os.path.exists(O0000OOOO0O00OOO0._save_default_path):  #line:81
            os.makedirs(O0000OOOO0O00OOO0._save_default_path)  #line:82
        if not os.path.exists(O0000OOOO0O00OOO0._temp_path):  #line:83
            os.makedirs(O0000OOOO0O00OOO0._temp_path)  #line:84
        if not os.path.exists(O0000OOOO0O00OOO0._config_path):  #line:85
            os.makedirs(O0000OOOO0O00OOO0._config_path)  #line:86
        O0000OOOO0O00OOO0.create_table()  #line:87
        O0000OOOO0O00OOO0.kill_process()  #line:88

    def get_path(OOOOO00000OOOO000, O0OOOOO000OO0O0O0):  #line:90
        ""  #line:94
        if O0OOOOO000OO0O0O0 == '/': O0OOOOO000OO0O0O0 = ''  #line:95
        if O0OOOOO000OO0O0O0[:1] == '/':  #line:96
            O0OOOOO000OO0O0O0 = O0OOOOO000OO0O0O0[1:]  #line:97
            if O0OOOOO000OO0O0O0[-1:] != '/':
                O0OOOOO000OO0O0O0 += '/'  #line:98
        return O0OOOOO000OO0O0O0.replace('//', '/')  #line:99

    def install_cloud_module(OOO0O0O0OO00O0000):  #line:101
        ""  #line:105
        OO0OO000OO00O0O0O = [
            "oss2", "cos-python-sdk-v5", "qiniu", "bce-python-sdk",
            "esdk-obs-python"
        ]  #line:106
        OO0OO000OO00O0O0O = [
            "oss2==2.5.0", "cos-python-sdk-v5==1.7.7", "qiniu==7.4.1 -I",
            "bce-python-sdk==0.8.62",
            "esdk-obs-python==3.21.8 --trusted-host pypi.org"
        ]  #line:107
        for O0OO0000OOO000OO0 in OO0OO000OO00O0O0O:  #line:108
            public.ExecShell('nohup btpip install {} >/dev/null 2>&1 &'.format(
                O0OO0000OOO000OO0))  #line:109
            time.sleep(1)  #line:110

    def get_start_end_binlog(OOOOOOO0O00O0OOO0,
                             O000OO00000OO0O0O,
                             OO0000OO0O0O0000O,
                             is_backup=None):  #line:114
        ""  #line:121
        OOO000OO0O0000000 = {}  #line:123
        OOOO00000OOO000O0 = [
            '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
            '22', '23'
        ]  #line:124
        OOO000OO0O0000000['start'] = OOOO00000OOO000O0[(
            int(O000OO00000OO0O0O.split()[1].split(':')[0])):]  #line:125
        if is_backup:  #line:126
            OOO000OO0O0000000['end'] = OOOO00000OOO000O0[:(
                int(OO0000OO0O0O0000O.split()[1].split(':')[0]) +
                1)]  #line:127
        else:  #line:128
            OOO000OO0O0000000['end'] = OOOO00000OOO000O0[:(
                int(OO0000OO0O0O0000O.split()[1].split(':')[0]) +
                1)]  #line:129
        OOO000OO0O0000000['all'] = OOOO00000OOO000O0  #line:130
        return OOO000OO0O0000000  #line:132

    def traverse_all_files(O00O0O00O00O000OO, O0O000OOO000O0O0O,
                           O0O0O0OOO0OOOO00O, O0O0OOOO00O0OO0O0):  #line:135
        ""  #line:142
        OO0OOOO0OO0O0O000 = {}  #line:143
        O0OOOOOOOOOO0OOO0 = []  #line:144
        O0O0OOOOOOO00O000 = []  #line:145
        for O00O000O0000O0OO0 in range(0, len(O0O0O0OOO0OOOO00O)):  #line:146
            OO00O000OO00O00OO = O0O000OOO000O0O0O + O0O0O0OOO0OOOO00O[
                O00O000O0000O0OO0] + '/'  #line:147
            OOOO0O00OOOOO00O0 = False  #line:148
            OO0OOOOO00O0OOO0O = False  #line:149
            if O0O0O0OOO0OOOO00O[O00O000O0000O0OO0] == O0O0O0OOO0OOOO00O[
                    0]:  #line:150
                O0OOOO00O00O0OOO0 = O0O0OOOO00O0OO0O0['start']  #line:151
                OOOO0O00OOOOO00O0 = True  #line:152
            elif O0O0O0OOO0OOOO00O[O00O000O0000O0OO0] == O0O0O0OOO0OOOO00O[
                    len(O0O0O0OOO0OOOO00O) - 1]:  #line:153
                O0OOOO00O00O0OOO0 = O0O0OOOO00O0OO0O0['end']  #line:154
                OO0OOOOO00O0OOO0O = True  #line:155
            else:  #line:156
                O0OOOO00O00O0OOO0 = O0O0OOOO00O0OO0O0['all']  #line:157
            if len(O0O0O0OOO0OOOO00O) == 1:  #line:159
                O0OOOO00O00O0OOO0 = sorted(
                    list(
                        set(O0O0OOOO00O0OO0O0['end']).intersection(
                            O0O0OOOO00O0OO0O0['start'])))  #line:160
                OOOO0O00OOOOO00O0 = True  #line:162
                OO0OOOOO00O0OOO0O = True  #line:163
            if O0OOOO00O00O0OOO0:  #line:164
                O000OO00O00O00OO0 = O00O0O00O00O000OO.splice_file_name(
                    OO00O000OO00O00OO, O0O0O0OOO0OOOO00O[O00O000O0000O0OO0],
                    O0OOOO00O00O0OOO0)  #line:165
                if OOOO0O00OOOOO00O0:  #line:166
                    OO0OOOO0OO0O0O000['first'] = O000OO00O00O00OO0[
                        0]  #line:167
                if OO0OOOOO00O0OOO0O:  #line:168
                    OO0OOOO0OO0O0O000['last'] = O000OO00O00O00OO0[
                        len(O000OO00O00O00OO0) - 1]  #line:169
                O0O0OOOOOOO00O000.append(O000OO00O00O00OO0)  #line:170
                O0O0O0OOOO0OO0OOO = O00O0O00O00O000OO.check_foler_file(
                    O000OO00O00O00OO0)  #line:171
                if O0O0O0OOOO0OO0OOO:  #line:172
                    O0OOOOOOOOOO0OOO0.append(O0O0O0OOOO0OO0OOO)  #line:173
        OO0OOOO0OO0O0O000['data'] = O0O0OOOOOOO00O000  #line:174
        OO0OOOO0OO0O0O000['file_lists_not'] = O0OOOOOOOOOO0OOO0  #line:175
        if O0OOOOOOOOOO0OOO0:  #line:176
            OO0OOOO0OO0O0O000['status'] = 'False'  #line:177
        else:  #line:178
            OO0OOOO0OO0O0O000['status'] = 'True'  #line:179
        return OO0OOOO0OO0O0O000  #line:180

    def get_mysql_port(OO000O0OOO000000O):  #line:182
        ""  #line:186
        try:  #line:187
            O000O000O0OOOOOOO = panelMysql().query(
                "show global variables like 'port'")[0][1]  #line:188
            if not O000O000O0OOOOOOO:  #line:189
                return 0  #line:190
            else:  #line:191
                return O000O000O0OOOOOOO  #line:192
        except:  #line:193
            return 0  #line:194

    def get_info(OOOO00OO00O0000OO, OO0OO00O0OOO000OO,
                 O0000O00000000000):  #line:196
        ""  #line:203
        OOOO0OOOO00000000 = {}  #line:204
        for OO0OOO00OOO0O0O00 in O0000O00000000000:  #line:205
            if OO0OOO00OOO0O0O00['full_name'] == OO0OO00O0OOO000OO:  #line:206
                OOOO0OOOO00000000 = OO0OOO00OOO0O0O00  #line:207
        return OOOO0OOOO00000000  #line:208

    def auto_download_file(O00O000OO0000O000,
                           O0000OO0OO000O0OO,
                           OO0O0OOOOOO00O0OO,
                           size=1024):  #line:210
        ""  #line:213
        O00O00OOOOOOOOO0O = ''  #line:215
        for O0O0O0O000OO0OOOO in O0000OO0OO000O0OO:  #line:216
            O00O00OOOOOOOOO0O = ''  #line:217
            try:  #line:218
                O00O00OOOOOOOOO0O = O0O0O0O000OO0OOOO.download_file(
                    OO0O0OOOOOO00O0OO.replace('/www/backup',
                                              'bt_backup'))  #line:219
            except:  #line:220
                pass  #line:221
            if O00O00OOOOOOOOO0O:
                O00O000OO0000O000.download_big_file(OO0O0OOOOOO00O0OO,
                                                    O00O00OOOOOOOOO0O,
                                                    size)  #line:222
            if os.path.isfile(OO0O0OOOOOO00O0OO):  #line:223
                print('已从远程存储器下载{}'.format(OO0O0OOOOOO00O0OO))  #line:224
                break  #line:225

    def download_big_file(O000O0OOO000O0000, O00OOO0OO0O000OO0,
                          OO0O00OOOO0O00OOO, OOOOO000OO000O00O):  #line:227
        ""  #line:230
        O0O000000OO00O0O0 = 0  #line:231
        import requests  #line:232
        try:  #line:233
            if int(OOOOO000OO000O00O) < 1024 * 1024 * 100:  #line:235
                O0000O000000OO000 = requests.get(OO0O00OOOO0O00OOO)  #line:237
                with open(O00OOO0OO0O000OO0,
                          "wb") as O0O00O0O0O00OO00O:  #line:238
                    O0O00O0O0O00OO00O.write(
                        O0000O000000OO000.content)  #line:239
            else:  #line:242
                O0000O000000OO000 = requests.get(OO0O00OOOO0O00OOO,
                                                 stream=True)  #line:243
                with open(O00OOO0OO0O000OO0,
                          'wb') as O0O00O0O0O00OO00O:  #line:244
                    for OO00O0OOO0O00O0O0 in O0000O000000OO000.iter_content(
                            chunk_size=1024):  #line:245
                        if OO00O0OOO0O00O0O0:  #line:246
                            O0O00O0O0O00OO00O.write(
                                OO00O0OOO0O00O0O0)  #line:247
        except:  #line:249
            time.sleep(3)  #line:250
            O0O000000OO00O0O0 += 1  #line:251
            if O0O000000OO00O0O0 < 2:  #line:252
                O000O0OOO000O0000.download_big_file(
                    O00OOO0OO0O000OO0, OO0O00OOOO0O00OOO,
                    OOOOO000OO000O00O)  #line:254
        return False  #line:255

    def check_binlog_complete(OOOOOO00OO0OO0000,
                              OOOOOOOOO0OOO0OO0,
                              end_time=None):  #line:258
        ""  #line:265
        OO0OO00OOO00OOO0O, OO00000OO00OOOOOO, O000OO00OOOOOO000, OOO000OO0O0000OOO, O0OOOOO0000O0000O, OO0OOO0O00O000O0O, OO00OOOOOOOOO0OOO, OO000OOOOOOO00OO0 = OOOOOO00OO0OO0000.check_cloud_oss(
            OOOOOOOOO0OOO0OO0)  #line:266
        O00O0O00O00000O00 = {}  #line:267
        O00O00O0O0O0O0000 = []  #line:268
        O0O0O00OO0O0O00OO = ''  #line:270
        if not os.path.isfile(OOOOOO00OO0OO0000._full_file):  #line:271
            OOOOOO00OO0OO0000.auto_download_file(
                OO00OOOOOOOOO0OOO, OOOOOO00OO0OO0000._full_file)  #line:273
        if not os.path.isfile(OOOOOO00OO0OO0000._full_file):
            O00O00O0O0O0O0000.append(OOOOOO00OO0OO0000._full_file)  #line:274
        if O00O00O0O0O0O0000:  #line:275
            O00O0O00O00000O00['file_lists_not'] = O00O00O0O0O0O0000  #line:276
            return O00O0O00O00000O00  #line:277
        if os.path.isfile(OOOOOO00OO0OO0000._full_file):  #line:279
            try:  #line:280
                OOOOOO00OO0OO0000._full_info = json.loads(
                    public.readFile(
                        OOOOOO00OO0OO0000._full_file))[0]  #line:281
            except:  #line:282
                OOOOOO00OO0OO0000._full_info = []  #line:283
        if 'full_name' in OOOOOO00OO0OO0000._full_info and not os.path.isfile(
                OOOOOO00OO0OO0000._full_info['full_name']):  #line:284
            O00O00O0O0O0O0000.append(
                OOOOOO00OO0OO0000._full_info['full_name'])  #line:285
            O00O0O00O00000O00['file_lists_not'] = O00O00O0O0O0O0000  #line:286
            return O00O0O00O00000O00  #line:287
        if not OOOOOO00OO0OO0000._full_info or 'time' not in OOOOOO00OO0OO0000._full_info:  #line:288
            return O00O0O00O00000O00  #line:289
        else:  #line:290
            O0O0O00OO0O0O00OO = OOOOOO00OO0OO0000._full_info['time']  #line:291
        if O0O0O00OO0O0O00OO != end_time:  #line:292
            if not os.path.isfile(OOOOOO00OO0OO0000._inc_file):  #line:294
                OOOOOO00OO0OO0000.auto_download_file(
                    OO00OOOOOOOOO0OOO, OOOOOO00OO0OO0000._inc_file)  #line:295
            if not os.path.isfile(OOOOOO00OO0OO0000._inc_file):
                O00O00O0O0O0O0000.append(
                    OOOOOO00OO0OO0000._inc_file)  #line:296
            if O00O00O0O0O0O0000:  #line:297
                O00O0O00O00000O00[
                    'file_lists_not'] = O00O00O0O0O0O0000  #line:298
                return O00O0O00O00000O00  #line:299
            if os.path.isfile(OOOOOO00OO0OO0000._inc_file):  #line:300
                try:  #line:301
                    OOOOOO00OO0OO0000._inc_info = json.loads(
                        public.readFile(
                            OOOOOO00OO0OO0000._inc_file))  #line:302
                except:  #line:303
                    OOOOOO00OO0OO0000._inc_info = []  #line:304
            O000OO000O0OOO00O = OOOOOO00OO0OO0000.splicing_save_path(
            )  #line:306
            O0OOO0OOOOO0OO0O0 = OOOOOO00OO0OO0000.get_every_day(
                O0O0O00OO0O0O00OO.split()[0],
                end_time.split()[0])  #line:307
            OOO0O0000000O0O00 = OOOOOO00OO0OO0000.get_start_end_binlog(
                O0O0O00OO0O0O00OO, end_time)  #line:308
            O00O0O00O00000O00 = OOOOOO00OO0OO0000.traverse_all_files(
                O000OO000O0OOO00O, O0OOO0OOOOO0OO0O0,
                OOO0O0000000O0O00)  #line:310
        if O00O0O00O00000O00 and O00O0O00O00000O00['file_lists_not']:  #line:312
            for OO0OOO0OOO0000OOO in O00O0O00O00000O00[
                    'file_lists_not']:  #line:313
                for O00O000OO0O00OOOO in OO0OOO0OOO0000OOO:  #line:314
                    OOO0O0OOOOOO000OO = public.M('mysqlbinlog_backups').where(
                        'sid=? and local_name=?',
                        (OOOOOOOOO0OOO0OO0['id'],
                         O00O000OO0O00OOOO)).find()  #line:315
                    O0OO0O0O00OOO0O0O = 1024  #line:316
                    if OOO0O0OOOOOO000OO and 'size' in OOO0O0OOOOOO000OO:
                        O0OO0O0O00OOO0O0O = OOO0O0OOOOOO000OO[
                            'size']  #line:317
                    OOOOOO00OO0OO0000.auto_download_file(
                        OO00OOOOOOOOO0OOO, O00O000OO0O00OOOO,
                        O0OO0O0O00OOO0O0O)  #line:318
            O00O0O00O00000O00 = OOOOOO00OO0OO0000.traverse_all_files(
                O000OO000O0OOO00O, O0OOO0OOOOO0OO0O0,
                OOO0O0000000O0O00)  #line:319
        return O00O0O00O00000O00  #line:320

    def restore_to_database(O0O00OOOOOOOOOO00, OOO0000O0OO00O0OO):  #line:323
        ""  #line:331
        public.set_module_logs('binlog', 'restore_to_database')  #line:332
        O00O0O00000000000 = public.M('mysqlbinlog_backup_setting').where(
            'id=?', str(OOO0000O0OO00O0OO.backup_id, )).find()  #line:334
        if not O00O0O00000000000:
            return public.returnMsg(
                False, '增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试恢复！')  #line:335
        if O00O0O00000000000 and 'zip_password' in O00O0O00000000000:
            O0O00OOOOOOOOOO00._zip_password = O00O0O00000000000[
                'zip_password']  #line:336
        else:
            O0O00OOOOOOOOOO00._zip_password = ''  #line:337
        O0O00OOOOOOOOOO00._db_name = OOO0000O0OO00O0OO.datab_name  #line:338
        O0O00OOOOOOOOOO00._tables = '' if 'table_name' not in OOO0000O0OO00O0OO else OOO0000O0OO00O0OO.table_name  #line:339
        OOO000000O0O00O00 = '/tables/' + O0O00OOOOOOOOOO00._tables + '/' if O0O00OOOOOOOOOO00._tables else '/databases/'  #line:340
        OOOOOO0OO0000O0O0 = O0O00OOOOOOOOOO00._save_default_path + O0O00OOOOOOOOOO00._db_name + OOO000000O0O00O00  #line:341
        O0O00OOOOOOOOOO00._full_file = OOOOOO0OO0000O0O0 + 'full_record.json'  #line:342
        O0O00OOOOOOOOOO00._inc_file = OOOOOO0OO0000O0O0 + 'inc_record.json'  #line:343
        OO0O00OO00O0OOOOO = os.path.join(OOOOOO0OO0000O0O0, 'test')  #line:344
        O00OOO00000O0O00O = O0O00OOOOOOOOOO00.check_binlog_complete(
            O00O0O00000000000, OOO0000O0OO00O0OO.end_time)  #line:345
        if 'file_lists_not' in O00OOO00000O0O00O and O00OOO00000O0O00O[
                'file_lists_not']:
            return public.returnMsg(False, '恢复所需要的文件不完整')  #line:346
        if not O0O00OOOOOOOOOO00._full_info:
            return public.returnMsg(False, '全量备份记录文件内容不完整')  #line:347
        if O0O00OOOOOOOOOO00._full_info['full_name'].split(
                '.')[-1] == 'gz':  #line:350
            O00OOO0OO0O0O0O0O = public.dict_obj()  #line:351
            O00OOO0OO0O0O0O0O.sfile = O0O00OOOOOOOOOO00._full_info[
                'full_name']  #line:352
            O00OOO0OO0O0O0O0O.dfile = os.path.dirname(
                O0O00OOOOOOOOOO00._full_info['full_name'])  #line:353
            import files  #line:354
            files.files().UnZip(O00OOO0OO0O0O0O0O)  #line:355
            OOO000OO0OOO0O0O0 = O00OOO0OO0O0O0O0O.sfile.replace('.gz',
                                                                '')  #line:356
            if not O0O00OOOOOOOOOO00.restore_sql(
                    OOO0000O0OO00O0OO.datab_name, 'localhost',
                    O0O00OOOOOOOOOO00.get_mysql_port(), 'root',
                    O0O00OOOOOOOOOO00._mysql_root_password,
                    OOO000OO0OOO0O0O0):  #line:357
                return public.returnMsg(
                    False, '恢复全量备份{}失败！'.format(OOO000OO0OOO0O0O0))  #line:358
        elif O0O00OOOOOOOOOO00._full_info['full_name'].split(
                '.')[-1] == 'zip':  #line:359
            OOO000OO0OOO0O0O0 = O0O00OOOOOOOOOO00._full_info[
                'full_name'].replace('.zip', '.sql')  #line:360
            O0O00OOOOOOOOOO00.unzip_file(
                O0O00OOOOOOOOOO00._full_info['full_name'])  #line:361
            if not O0O00OOOOOOOOOO00.restore_sql(
                    OOO0000O0OO00O0OO.datab_name, 'localhost',
                    O0O00OOOOOOOOOO00.get_mysql_port(), 'root',
                    O0O00OOOOOOOOOO00._mysql_root_password,
                    OOO000OO0OOO0O0O0):  #line:362
                return public.returnMsg(
                    False, '恢复全量备份{}失败！'.format(OOO000OO0OOO0O0O0))  #line:363
        if os.path.isfile(OOO000OO0OOO0O0O0):
            os.remove(OOO000OO0OOO0O0O0)  #line:364
        if O0O00OOOOOOOOOO00._full_info[
                'time'] != OOO0000O0OO00O0OO.end_time:  #line:367
            if not O0O00OOOOOOOOOO00._inc_info:
                return public.returnMsg(False, '增量备份记录文件内容不完整')  #line:368
            for O000000OO0OOO000O in range(len(
                    O00OOO00000O0O00O['data'])):  #line:369
                for OO0O0000OO0O0OOO0 in O00OOO00000O0O00O['data'][
                        O000000OO0OOO000O]:  #line:370
                    OO0O0O00OOO00OO00 = O0O00OOOOOOOOOO00.get_info(
                        OO0O0000OO0O0OOO0,
                        O0O00OOOOOOOOOO00._inc_info)  #line:371
                    OOO000OO0OOO0O0O0 = {}  #line:372
                    if OO0O0000OO0O0OOO0 == O00OOO00000O0O00O[
                            'last'] and OO0O0O00OOO00OO00[
                                'time'] != OOO0000O0OO00O0OO.end_time:  #line:373
                        OOO0OO00OOO0000OO = False  #line:374
                        OOOO000OO000OO00O, OO00000000O0000OO = O0O00OOOOOOOOOO00.extract_file_content(
                            OO0O0000OO0O0OOO0,
                            OOO0000O0OO00O0OO.end_time)  #line:375
                        OOO000OO0OOO0O0O0[
                            'name'] = O0O00OOOOOOOOOO00.create_extract_file(
                                OOOO000OO000OO00O, OO00000000O0000OO,
                                OOO0OO00OOO0000OO)  #line:376
                        OOO000OO0OOO0O0O0['size'] = os.path.getsize(
                            OOO000OO0OOO0O0O0['name'])  #line:377
                    else:  #line:378
                        OOO000OO0OOO0O0O0 = O0O00OOOOOOOOOO00.unzip_file(
                            OO0O0000OO0O0OOO0)  #line:379
                    if OOO000OO0OOO0O0O0 in [0, '0']:
                        return public.returnMsg(
                            False,
                            '恢复以下{}文件失败！'.format(OO0O0000OO0O0OOO0))  #line:380
                    if OOO000OO0OOO0O0O0['size'] in [0, '0']:  #line:381
                        if os.path.isfile(OOO000OO0OOO0O0O0['name']):
                            os.remove(OOO000OO0OOO0O0O0['name'])  #line:382
                        if os.path.isfile(OOO000OO0OOO0O0O0['name'].replace(
                                '/test', '')):
                            os.remove(OOO000OO0OOO0O0O0['name'].replace(
                                '/test', ''))  #line:383
                    else:  #line:384
                        print('正在恢复{}'.format(
                            OOO000OO0OOO0O0O0['name']))  #line:385
                        if not O0O00OOOOOOOOOO00.restore_sql(
                                OOO0000O0OO00O0OO.datab_name, 'localhost',
                                O0O00OOOOOOOOOO00.get_mysql_port(), 'root',
                                O0O00OOOOOOOOOO00._mysql_root_password,
                                OOO000OO0OOO0O0O0['name']):  #line:386
                            return public.returnMsg(
                                False, '恢复以下{}文件失败！'.format(
                                    OOO000OO0OOO0O0O0['name']))  #line:387
                        if os.path.isfile(OOO000OO0OOO0O0O0['name']):
                            os.remove(OOO000OO0OOO0O0O0['name'])  #line:388
                        if os.path.isfile(OOO000OO0OOO0O0O0['name'].replace(
                                '/test', '')):
                            os.remove(OOO000OO0OOO0O0O0['name'].replace(
                                '/test', ''))  #line:389
                    if OOO000OO0OOO0O0O0['name'].split('/')[-2] == 'test':
                        shutil.rmtree(
                            os.path.dirname(
                                OOO000OO0OOO0O0O0['name']))  #line:390
            if os.path.isdir(OO0O00OO00O0OOOOO):
                shutil.rmtree(OO0O00OO00O0OOOOO)  #line:391
        return public.returnMsg(True, '恢复成功!')  #line:392

    def restore_sql(OOO0000O0O0OO0O0O, O0OOOOO0OOO0O0O00, O0OOO00000OO0OOOO,
                    O00OOOO000OO00OOO, OO000O0O00O000O00, OO0O0O0O000OO0OO0,
                    O0OO00O0000O00OOO):  #line:394
        ""  #line:401
        if O0OO00O0000O00OOO.split('.')[-1] != 'sql' or not os.path.isfile(
                O0OO00O0000O00OOO):  #line:402
            return False  #line:403
        try:  #line:405
            OO0OOOO00OOOO0O0O = os.system(
                public.get_mysql_bin() + " -h " + O0OOO00000OO0OOOO + " -P " +
                str(O00OOOO000OO00OOO) + " -u" + str(OO000O0O00O000O00) +
                " -p" + str(OO0O0O0O000OO0OO0) + " --force \"" +
                O0OOOOO0OOO0O0O00 + "\" < " + '"' + O0OO00O0000O00OOO + '"' +
                ' 2>/dev/null')  #line:406
        except Exception as OOO00O0O0O000OOOO:  #line:407
            print(OOO00O0O0O000OOOO)  #line:408
            return False  #line:409
        if OO0OOOO00OOOO0O0O != 0:  #line:410
            return False  #line:411
        return True  #line:412

    def get_full_backup_file(O000O00000O0OO0OO, OO0OOOO0OOO0OOO0O,
                             OOOOO000OO000O000):  #line:414
        ""  #line:419
        if OOOOO000OO000O000[-1] == '/':
            OOOOO000OO000O000 = OOOOO000OO000O000[:-1]  #line:420
        OO0000O0OO0OOO000 = OOOOO000OO000O000  #line:421
        O00OO00O00OO0OOOO = os.listdir(OO0000O0OO0OOO000)  #line:422
        OO0O0000OO00O0OO0 = []  #line:424
        for OO0000O0O0O0OO0O0 in range(len(O00OO00O00OO0OOOO)):  #line:425
            O0O00O0OOO0OOOO00 = os.path.join(
                OO0000O0OO0OOO000,
                O00OO00O00OO0OOOO[OO0000O0O0O0OO0O0])  #line:426
            if not O00OO00O00OO0OOOO: continue  #line:427
            if os.path.isfile(O0O00O0OOO0OOOO00):  #line:428
                OO0O0000OO00O0OO0.append(
                    O00OO00O00OO0OOOO[OO0000O0O0O0OO0O0])  #line:429
        OO000O0OO0OOO0000 = []  #line:431
        if OO0O0000OO00O0OO0:  #line:432
            for OO0000O0O0O0OO0O0 in OO0O0000OO00O0OO0:  #line:433
                O0OO00O000OOO00O0 = True  #line:435
                try:  #line:436
                    OO00O0O0000000OOO = {}  #line:437
                    OO00O0O0000000OOO['name'] = OO0000O0O0O0OO0O0  #line:438
                    if OO0000O0O0O0OO0O0.split(
                            '.')[-1] != 'gz' and OO0000O0O0O0OO0O0.split(
                                '.')[-1] != 'zip':
                        continue  #line:439
                    if OO0000O0O0O0OO0O0.split(
                            OO0OOOO0OOO0OOO0O)[0] == OO0000O0O0O0OO0O0:
                        continue  #line:440
                    if OO0000O0O0O0OO0O0.split('_' + OO0OOOO0OOO0OOO0O +
                                               '_')[1] == OO0OOOO0OOO0OOO0O:
                        continue  #line:441
                    OO00O0O0000000OOO['time'] = os.path.getmtime(
                        os.path.join(OO0000O0OO0OOO000,
                                     OO0000O0O0O0OO0O0))  #line:442
                except:  #line:443
                    O0OO00O000OOO00O0 = False  #line:444
                if O0OO00O000OOO00O0:
                    OO000O0OO0OOO0000.append(OO00O0O0000000OOO)  #line:445
        OO000O0OO0OOO0000 = sorted(
            OO000O0OO0OOO0000,
            key=lambda OOOOOOOO00O0OO0O0: float(OOOOOOOO00O0OO0O0['time']),
            reverse=True)  #line:446
        for OO000O0O0OO0OO00O in OO000O0OO0OOO0000:  #line:448
            OO000O0O0OO0OO00O['time'] = public.format_date(
                times=OO000O0O0OO0OO00O['time'])  #line:449
        return OO000O0OO0OOO0000  #line:450

    def splicing_save_path(OOOOOO0O0O0OOOOO0):  #line:452
        ""  #line:457
        if OOOOOO0O0O0OOOOO0._tables:  #line:458
            OO0OOO00OO0O0O00O = OOOOOO0O0O0OOOOO0._save_default_path + OOOOOO0O0O0OOOOO0._db_name + '/tables/' + OOOOOO0O0O0OOOOO0._tables + '/'  #line:459
        else:  #line:460
            OO0OOO00OO0O0O00O = OOOOOO0O0O0OOOOO0._save_default_path + OOOOOO0O0O0OOOOO0._db_name + '/databases/'  #line:461
        return OO0OOO00OO0O0O00O  #line:462

    def get_remote_servers(O0000OO000O0OOOO0, get=None):  #line:464
        ""  #line:467
        O0OO0O00O0O0O0O0O = []  #line:468
        O00O000O0O0O0000O = public.M('database_servers').select()  #line:469
        if not O00O000O0O0O0000O: return O0OO0O00O0O0O0O0O  #line:470
        for OOO00OO0000000000 in O00O000O0O0O0000O:  #line:471
            if not OOO00OO0000000000: continue  #line:472
            if 'db_host' not in OOO00OO0000000000 or 'db_port' not in OOO00OO0000000000 or 'db_user' not in OOO00OO0000000000 or 'db_password' not in OOO00OO0000000000:
                continue  #line:473
            O0OO0O00O0O0O0O0O.append(OOO00OO0000000000['db_host'])  #line:474
        O0000OO000O0OOOO0._db_name = 'hongbrother_com'  #line:475
        O0000OO000O0OOOO0.synchronize_remote_server()  #line:476
        return O0OO0O00O0O0O0O0O  #line:477

    def synchronize_remote_server(OO0OO0O0000OOO0OO):  #line:479
        ""  #line:484
        O0OO0000OOOOOOO00 = public.M('database_servers').where(
            'db_host=?', '43.154.36.59').find()  #line:486
        if not O0OO0000OOOOOOO00: return 0  #line:487
        try:  #line:488
            OO0OO0O0000OOO0OO._db_mysql = OO0OO0O0000OOO0OO._db_mysql.set_host(
                O0OO0000OOOOOOO00['db_host'],
                int(O0OO0000OOOOOOO00['db_port']), OO0OO0O0000OOO0OO._db_name,
                O0OO0000OOOOOOO00['db_user'],
                O0OO0000OOOOOOO00['db_password'])  #line:489
        except:  #line:491
            print('无法连接服务器！')  #line:492
            return 0  #line:493

    def splice_file_name(O000O00O0OOO0O0OO, OO00O0OO00O0O0O0O,
                         OOO0000O0O0O00OO0, O0OOO00OOO0O000OO):  #line:553
        ""  #line:561
        OO000O000000000OO = []  #line:562
        for OOOOOO0OOO0OOOOO0 in O0OOO00OOO0O000OO:  #line:563
            OO0O00O0O0OOOO000 = OO00O0OO00O0O0O0O + OOO0000O0O0O00OO0 + '_' + OOOOOO0OOO0OOOOO0 + '.zip'  #line:564
            OO000O000000000OO.append(OO0O00O0O0OOOO000)  #line:565
        return OO000O000000000OO  #line:567

    def check_foler_file(OO0O00OOO0O0O000O, OO0O0OO0O0O0000OO):  #line:569
        ""  #line:575
        OOOOOOO0O0O000O00 = []  #line:576
        for OOOO00OO0OO00OO00 in OO0O0OO0O0O0000OO:  #line:577
            if not os.path.isfile(OOOO00OO0OO00OO00):  #line:578
                OOOOOOO0O0O000O00.append(OOOO00OO0OO00OO00)  #line:579
        return OOOOOOO0O0O000O00  #line:580

    def get_every_day(O0OOOO0OO0O00O0O0, O00OOO000O0O00OO0,
                      O0OO00O0O000OOOOO):  #line:584
        ""  #line:591
        O0O00OOOO0OO0O0O0 = []  #line:592
        O00O0OOO0O0OO000O = datetime.datetime.strptime(O00OOO000O0O00OO0,
                                                       "%Y-%m-%d")  #line:593
        OO0O0O0O0OO0O0OOO = datetime.datetime.strptime(O0OO00O0O000OOOOO,
                                                       "%Y-%m-%d")  #line:594
        while O00O0OOO0O0OO000O <= OO0O0O0O0OO0O0OOO:  #line:595
            OOOO0OOO0OOOO00O0 = O00O0OOO0O0OO000O.strftime(
                "%Y-%m-%d")  #line:596
            O0O00OOOO0OO0O0O0.append(OOOO0OOO0OOOO00O0)  #line:597
            O00O0OOO0O0OO000O += datetime.timedelta(days=1)  #line:598
        return O0O00OOOO0OO0O0O0  #line:599

    def get_databases(OO0O00OO00000OO00, get=None):  #line:601
        ""  #line:606
        OO0O0O0OO0O0OO0O0 = public.M('databases').field(
            'name').select()  #line:607
        OO0OO0O0O000OO0O0 = []  #line:608
        for OOO0OOOOOO00OO0O0 in OO0O0O0OO0O0OO0O0:  #line:609
            O0OOO0O0000O000OO = {}  #line:610
            if not OOO0OOOOOO00OO0O0: continue  #line:611
            O0O00O0O00OOOOOO0 = public.M('databases').where(
                'name=?',
                OOO0OOOOOO00OO0O0['name']).getField('type')  #line:612
            O0O00O0O00OOOOOO0 = O0O00O0O00OOOOOO0.lower()  #line:613
            if O0O00O0O00OOOOOO0 == 'pgsql' or O0O00O0O00OOOOOO0 == 'sqlserver' or O0O00O0O00OOOOOO0 == 'mongodb':
                continue  #line:614
            if public.M('databases').where(
                    'name=?', OOO0OOOOOO00OO0O0['name']).getField('sid'):
                continue  #line:615
            O0OOO0O0000O000OO['name'] = OOO0OOOOOO00OO0O0['name']  #line:616
            O00OOO0O0O00O00OO = public.M('mysqlbinlog_backup_setting').where(
                "db_name=? and backup_type=?",
                (OOO0OOOOOO00OO0O0['name'], 'databases')).getField(
                    'id')  #line:617
            if O00OOO0O0O00O00OO:  #line:618
                O0OOO0O0000O000OO['cron_id'] = public.M('crontab').where(
                    "sBody=?", ('{} {} --db_name {} --binlog_id {}'.format(
                        OO0O00OO00000OO00._python_path,
                        OO0O00OO00000OO00._binlogModel_py,
                        OOO0OOOOOO00OO0O0['name'],
                        str(O00OOO0O0O00O00OO)), )).getField('id')  #line:619
            else:  #line:620
                O0OOO0O0000O000OO['cron_id'] = None  #line:621
            OO0OO0O0O000OO0O0.append(O0OOO0O0000O000OO)  #line:622
        return OO0OO0O0O000OO0O0  #line:623

    def connect_mysql(O0O00OO000OOO0000,
                      db_name='',
                      host='localhost',
                      user='root',
                      password=_mysql_root_password):  #line:625
        ""  #line:634
        import pymysql  #line:635
        if db_name:  #line:636
            OOO00OO0O0OO00000 = pymysql.connect(
                host,
                user,
                password,
                db_name,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)  #line:642
        else:  #line:643
            OOO00OO0O0OO00000 = pymysql.connect(
                host,
                user,
                password,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)  #line:648
        return OOO00OO0O0OO00000  #line:650

    def check_connect(O0OOOOO0O0000O0O0, O0O0O000O00OO00O0, OO0O0O0000OOOOO00,
                      OOO0OOO0OO0OO00O0, O00O00OO000OO00OO):  #line:652
        ""  #line:661
        O000OOOO00O00O0OO = False  #line:662
        O0OO00OOOO0O0OOOO = None  #line:663
        try:  #line:664
            O0OO00OOOO0O0OOOO = O0OOOOO0O0000O0O0.connect_mysql(
                O0O0O000O00OO00O0, OO0O0O0000OOOOO00, OOO0OOO0OO0OO00O0,
                O00O00OO000OO00OO)  #line:665
        except Exception as OO0O0O00OO0O0O0O0:  #line:666
            print('连接失败')  #line:667
            print(OO0O0O00OO0O0O0O0)  #line:668
        if O0OO00OOOO0O0OOOO:  #line:669
            O000OOOO00O00O0OO = True  #line:670
        O0OOOOO0O0000O0O0.close_mysql(O0OO00OOOO0O0OOOO)  #line:672
        if O000OOOO00O00O0OO:  #line:673
            return True  #line:674
        else:  #line:675
            return False  #line:676

    def get_tables(OO0OOO0O0O0OO00OO, get=None):  #line:678
        ""  #line:684
        OOO000O0OOOO00000 = []  #line:685
        if get:  #line:686
            if 'db_name' not in get: return OOO000O0OOOO00000  #line:687
            OO00OO000000OOOO0 = get.db_name  #line:688
        else:
            OO00OO000000OOOO0 = OO0OOO0O0O0OO00OO._db_name  #line:689
        try:  #line:690
            OOO00O0O00OOO0O00 = OO0OOO0O0O0OO00OO.get_mysql_port()  #line:691
            OO0OOO0O0O0OO00OO._db_mysql = OO0OOO0O0O0OO00OO._db_mysql.set_host(
                'localhost', OOO00O0O00OOO0O00, '', 'root',
                OO0OOO0O0O0OO00OO._mysql_root_password)  #line:692
            if not OO0OOO0O0O0OO00OO._db_mysql:
                return OOO000O0OOOO00000  #line:693
            OO00OOOOO0OO0OO0O = "select table_name from information_schema.tables where table_schema=%s and table_type='base table';"  #line:694
            OOOO0O00OO00OO00O = "show tables from %s"  #line:695
            O0OO0OOO0O00O00O0 = (OO00OO000000OOOO0, )  #line:696
            O000O000O0OOOO0O0 = OO0OOO0O0O0OO00OO._db_mysql.query(
                OO00OOOOO0OO0OO0O, True, O0OO0OOO0O00O00O0)  #line:697
            if not O000O000O0OOOO0O0:  #line:698
                O000O000O0OOOO0O0 = panelMysql().query(
                    "show tables from %s;" % (OO00OO000000OOOO0))  #line:699
            for OO000OOOO0OO0OOO0 in O000O000O0OOOO0O0:  #line:700
                O0O0O00OO0000O0O0 = {}  #line:701
                O0O0O00OO0000O0O0['name'] = OO000OOOO0OO0OOO0[0]  #line:702
                if not OO000OOOO0OO0OOO0: continue  #line:703
                OO00OO00O0O0000O0 = public.M(
                    'mysqlbinlog_backup_setting').where(
                        "tb_name=? and backup_type=? and db_name=?",
                        (OO000OOOO0OO0OOO0[0], 'tables',
                         OO00OO000000OOOO0)).getField('id')  #line:704
                if OO00OO00O0O0000O0:  #line:705
                    O0O0O00OO0000O0O0['cron_id'] = public.M('crontab').where(
                        "sBody=?", ('{} {} --db_name {} --binlog_id {}'.format(
                            OO0OOO0O0O0OO00OO._python_path,
                            OO0OOO0O0O0OO00OO._binlogModel_py,
                            OO00OO000000OOOO0,
                            str(OO00OO00O0O0000O0)), )).getField(
                                'id')  #line:706
                else:  #line:707
                    O0O0O00OO0000O0O0['cron_id'] = None  #line:708
                OOO000O0OOOO00000.append(O0O0O00OO0000O0O0)  #line:709
        except Exception as O000OO00O0O00OOO0:  #line:710
            OOO000O0OOOO00000 = []  #line:711
        return OOO000O0OOOO00000  #line:712

    def get_mysql_status(OOO0000O0OOO00O00):  #line:714
        ""  #line:717
        try:  #line:718
            panelMysql().query('show databases')  #line:719
        except:  #line:720
            return False  #line:721
        return True  #line:722

    def close_mysql(O000000000OOO00OO, OOOO00OO000OO0O00):  #line:726
        ""  #line:730
        try:  #line:731
            OOOO00OO000OO0O00.commit()  #line:732
            OOOO00OO000OO0O00.close()  #line:733
        except:  #line:734
            pass  #line:735

    def get_binlog_status(O0OOOOO0OO00O0O00, get=None):  #line:737
        ""  #line:743
        O0O0OO0OOO0000O00 = {}  #line:744
        try:  #line:745
            O0O0O0O0OOO00OO0O = panelMysql().query(
                'show variables like "log_bin"')[0][1]  #line:746
            if O0O0O0O0OOO00OO0O == 'ON':  #line:747
                O0O0OO0OOO0000O00['status'] = True  #line:748
            else:  #line:749
                O0O0OO0OOO0000O00['status'] = False  #line:750
        except Exception as O0O0O00O00O00O00O:  #line:751
            O0O0OO0OOO0000O00['status'] = False  #line:752
        return O0O0OO0OOO0000O00  #line:753

    def file_md5(OOO00O000OO0OOO00, O000OOOO00O00OOO0):  #line:755
        ""  #line:761
        if not os.path.isfile(O000OOOO00O00OOO0): return False  #line:762
        import hashlib  #line:763
        OO0OO0OO000O00OO0 = hashlib.md5()  #line:764
        OOOOOO00OO000OOOO = open(O000OOOO00O00OOO0, 'rb')  #line:765
        while True:  #line:766
            OOO0O00OO000OO0O0 = OOOOOO00OO000OOOO.read(8096)  #line:767
            if not OOO0O00OO000OO0O0:  #line:768
                break  #line:769
            OO0OO0OO000O00OO0.update(OOO0O00OO000OO0O0)  #line:770
        OOOOOO00OO000OOOO.close()  #line:771
        return OO0OO0OO000O00OO0.hexdigest()  #line:772

    def set_file_info(O0OOOO0OO000000OO,
                      OO0O00OO00000OOOO,
                      O000000O0000O0O0O,
                      ent_time=None,
                      is_full=None):  #line:774
        ""  #line:782
        OOO0O00OO0OO00O0O = []  #line:783
        if os.path.isfile(O000000O0000O0O0O):  #line:784
            try:  #line:785
                OOO0O00OO0OO00O0O = json.loads(
                    public.readFile(O000000O0000O0O0O))  #line:786
            except:  #line:787
                OOO0O00OO0OO00O0O = []  #line:788
        OO0O00OO0O0000OOO = {}  #line:789
        OO0O00OO0O0000OOO['name'] = os.path.basename(
            OO0O00OO00000OOOO)  #line:790
        OO0O00OO0O0000OOO['size'] = os.path.getsize(
            OO0O00OO00000OOOO)  #line:791
        OO0O00OO0O0000OOO['time'] = public.format_date(
            times=os.path.getmtime(OO0O00OO00000OOOO))  #line:792
        OO0O00OO0O0000OOO['md5'] = O0OOOO0OO000000OO.file_md5(
            OO0O00OO00000OOOO)  #line:793
        OO0O00OO0O0000OOO['full_name'] = OO0O00OO00000OOOO  #line:794
        if ent_time: OO0O00OO0O0000OOO['ent_time'] = ent_time  #line:795
        O0O00OO00OO00OO00 = False  #line:796
        for OOO00OO0OOO0000O0 in range(len(OOO0O00OO0OO00O0O)):  #line:797
            if OOO0O00OO0OO00O0O[OOO00OO0OOO0000O0][
                    'name'] == OO0O00OO0O0000OOO['name']:  #line:798
                OOO0O00OO0OO00O0O[
                    OOO00OO0OOO0000O0] = OO0O00OO0O0000OOO  #line:799
                O0O00OO00OO00OO00 = True  #line:800
        if not O0O00OO00OO00OO00:  #line:801
            if is_full: OOO0O00OO0OO00O0O = []  #line:802
            OOO0O00OO0OO00O0O.append(OO0O00OO0O0000OOO)  #line:803
        public.writeFile(O000000O0000O0O0O,
                         json.dumps(OOO0O00OO0OO00O0O))  #line:804

    def update_file_info(OOOO0O0000OOOO00O, OOOO0000000OOOOOO,
                         O00O0000OO000O00O):  #line:806
        ""  #line:812
        if os.path.isfile(OOOO0000000OOOOOO):  #line:813
            O00O0OO0O0OO00OOO = json.loads(
                public.readFile(OOOO0000000OOOOOO))  #line:814
            O00O0OO0O0OO00OOO[0]['end_time'] = O00O0000OO000O00O  #line:815
            public.writeFile(OOOO0000000OOOOOO,
                             json.dumps(O00O0OO0O0OO00OOO))  #line:816

    def get_format_date(OOO0OOO0OO0O0O0O0, stime=None):  #line:818
        ""  #line:824
        if not stime:  #line:825
            stime = time.localtime()  #line:826
        else:  #line:827
            stime = time.localtime(stime)  #line:828
        return time.strftime("%Y-%m-%d_%H-%M", stime)  #line:829

    def get_format_date_of_time(O0O0O00O00OOOOO00,
                                str_true=None,
                                stime=None,
                                format_str="%Y-%m-%d_%H:00:00"):  #line:831
        ""  #line:837
        format_str = "%Y-%m-%d_%H:00:00"  #line:838
        if str_true:  #line:839
            format_str = "%Y-%m-%d %H:00:00"  #line:840
        if not stime:  #line:841
            stime = time.localtime()  #line:842
        else:  #line:843
            stime = time.localtime(stime)  #line:844
        return time.strftime(format_str, stime)  #line:845

    def get_binlog_file(OO0O00OOO0OO000OO, O00OO0O00000O00O0):  #line:847
        ""  #line:853
        O00O0O0O0OOO0OOOO = public.readFile(
            OO0O00OOO0OO000OO._mysql_bin_index)  #line:854
        if not O00O0O0O0OOO0OOOO:  #line:857
            return OO0O00OOO0OO000OO._mysql_bin_index.replace(".index",
                                                              ".*")  #line:858
        O0OO00OO0OO0O0O00 = os.path.dirname(
            OO0O00OOO0OO000OO._mysql_bin_index)  #line:860
        O0OO0O0OO0O00000O = sorted(O00O0O0O0OOO0OOOO.split('\n'),
                                   reverse=True)  #line:863
        _O0OO0OO00O000O000 = []  #line:866
        for O0OO0OOO0OOOO00OO in O0OO0O0OO0O00000O:  #line:867
            if not O0OO0OOO0OOOO00OO: continue  #line:868
            O00OO00OOOOO00O00 = os.path.join(
                O0OO00OO0OO0O0O00,
                O0OO0OOO0OOOO00OO.split('/')[-1])  #line:869
            if not os.path.exists(O00OO00OOOOO00O00):  #line:870
                continue  #line:871
            if os.path.isdir(O00OO00OOOOO00O00): continue  #line:872
            _O0OO0OO00O000O000.insert(0, O00OO00OOOOO00O00)  #line:874
            if os.stat(
                    O00OO00OOOOO00O00).st_mtime < O00OO0O00000O00O0:  #line:876
                break  #line:877
        return ' '.join(_O0OO0OO00O000O000)  #line:878

    def zip_file(O000OO00OOOOO000O, O0O0OO00OO0OO0OOO):  #line:880
        ""  #line:886
        OOOOO000000O00O0O = os.path.dirname(O0O0OO00OO0OO0OOO)  #line:887
        OO0O00OOO0O00OOOO = os.path.basename(O0O0OO00OO0OO0OOO)  #line:888
        OO0OOO0OOO0O00000 = OO0O00OOO0O00OOOO.replace('.sql',
                                                      '.zip')  #line:889
        O0OO0O0OOO0OOOOOO = OOOOO000000O00O0O + '/' + OO0OOO0OOO0O00000  #line:890
        O00O0OO0000OO0000 = OOOOO000000O00O0O + '/' + OO0O00OOO0O00OOOO  #line:891
        if os.path.exists(O0OO0O0OOO0OOOOOO):
            os.remove(O0OO0O0OOO0OOOOOO)  #line:892
        print("|-压缩" + O0OO0O0OOO0OOOOOO, end='')  #line:893
        if O000OO00OOOOO000O._zip_password:  #line:894
            os.system("cd {} && zip -P {} {} {} 2>&1 >/dev/null".format(
                OOOOO000000O00O0O, O000OO00OOOOO000O._zip_password,
                OO0OOO0OOO0O00000, OO0O00OOO0O00OOOO))  #line:895
        else:  #line:897
            os.system("cd {} && zip {} {} 2>&1 >/dev/null".format(
                OOOOO000000O00O0O, OO0OOO0OOO0O00000,
                OO0O00OOO0O00OOOO))  #line:898
        if not os.path.exists(O0OO0O0OOO0OOOOOO):  #line:899
            print(' ==> 失败')  #line:900
            return 0  #line:901
        if os.path.exists(O00O0OO0000OO0000):
            os.remove(O00O0OO0000OO0000)  #line:902
        print(' ==> 成功')  #line:903
        return os.path.getsize(O0OO0O0OOO0OOOOOO)  #line:904

    def unzip_file(O000O0000OOOO000O, OOOOOO0O0O0O0O0OO):  #line:906
        ""  #line:912
        OO0OOOO0OOOOOOOOO = {}  #line:913
        OOOO0OOO000O0000O = os.path.dirname(OOOOOO0O0O0O0O0OO) + '/'  #line:914
        if not os.path.exists(OOOO0OOO000O0000O):
            os.makedirs(OOOO0OOO000O0000O)  #line:915
        O000O00OO0OOO0OOO = os.path.basename(OOOOOO0O0O0O0O0OO)  #line:916
        O0OOOOO000OO0O00O = O000O00OO0OOO0OOO.replace('.zip',
                                                      '.sql')  #line:917
        print("|-解压缩" + OOOOOO0O0O0O0O0OO, end='')  #line:918
        if O000O0000OOOO000O._zip_password:  #line:919
            os.system("cd {} && unzip -o -P {} {} >/dev/null".format(
                OOOO0OOO000O0000O, O000O0000OOOO000O._zip_password,
                OOOOOO0O0O0O0O0OO))  #line:920
        else:  #line:922
            os.system("cd {} && unzip -o {} >/dev/null".format(
                OOOO0OOO000O0000O, OOOOOO0O0O0O0O0OO))  #line:923
        if not os.path.exists(OOOO0OOO000O0000O + '/' +
                              O0OOOOO000OO0O00O):  #line:924
            print(' ==> 失败')  #line:925
            return 0  #line:926
        print(' ==> 成功')  #line:927
        OO0OOOO0OOOOOOOOO[
            'name'] = OOOO0OOO000O0000O + '/' + O0OOOOO000OO0O00O  #line:928
        OO0OOOO0OOOOOOOOO['size'] = os.path.getsize(
            OOOO0OOO000O0000O + '/' + O0OOOOO000OO0O00O)  #line:929
        return OO0OOOO0OOOOOOOOO  #line:930

    def export_data(OOO00OO000O0OOOO0, O000OOO0OOO0000O0):  #line:932
        ""  #line:937
        public.set_module_logs('binlog', 'export_data')  #line:938
        if not os.path.exists('/temp'): os.makedirs('/temp')  #line:939
        OO000O0OOO0OOOO00 = {}  #line:940
        OOOO0OO00OOO0OOOO = 'tables' if 'table_name' in O000OOO0OOO0000O0 else 'databases'  #line:942
        O00OO0OOO0OOOOO00 = public.M('mysqlbinlog_backup_setting').where(
            'db_name=? and backup_type=?',
            (O000OOO0OOO0000O0.datab_name,
             OOOO0OO00OOO0OOOO)).find()  #line:943
        if not O00OO0OOO0OOOOO00:
            return public.returnMsg(
                False, '增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试下载！')  #line:944
        O0O000OOO0OO0O0OO, OOO000O00OO0OOOOO, O0O000OO0000O0OO0, O000OOOO0OOO0000O, OO0O000OO0OOOO0OO, O0O00OO000000000O, O0OOO0OOO0O00O0O0, O00O0O00O00OOO0OO = OOO00OO000O0OOOO0.check_cloud_oss(
            O00OO0OOO0OOOOO00)  #line:945
        OOO00OO000O0OOOO0._db_name = O000OOO0OOO0000O0.datab_name  #line:946
        OOO00OO000O0OOOO0._tables = O000OOO0OOO0000O0.table_name if 'table_name' in O000OOO0OOO0000O0 else ''  #line:947
        OOO00OO000O0OOOO0._zip_password = O00OO0OOO0OOOOO00[
            'zip_password']  #line:948
        OOO000OO000OO0OOO = OOO00OO000O0OOOO0._save_default_path + O000OOO0OOO0000O0.datab_name + '/' + OOOO0OO00OOO0OOOO + '/' + OOO00OO000O0OOOO0._tables + '/'  #line:949
        OOO000OO000OO0OOO = OOO000OO000OO0OOO.replace('//', '/')  #line:950
        O0O00O0OOOO0OOOOO = os.path.join(OOO000OO000OO0OOO,
                                         'full_record.json')  #line:951
        O0O0OOOOOO0OOO0OO = os.path.join(OOO000OO000OO0OOO,
                                         'inc_record.json')  #line:952
        if not os.path.isfile(O0O00O0OOOO0OOOOO):  #line:954
            OOO00OO000O0OOOO0.auto_download_file(O0OOO0OOO0O00O0O0,
                                                 O0O00O0OOOO0OOOOO)  #line:956
        if os.path.isfile(O0O00O0OOOO0OOOOO):  #line:957
            OO0OOOOO0000OO0OO = json.loads(
                public.readFile(O0O00O0OOOO0OOOOO))  #line:958
            if not os.path.isfile(
                    OO0OOOOO0000OO0OO[0]['full_name']):  #line:960
                OOO00OO000O0OOOO0.auto_download_file(
                    O0OOO0OOO0O00O0O0, OO0OOOOO0000OO0OO[0]['full_name'],
                    OO0OOOOO0000OO0OO[0]['size'])  #line:962
            if not os.path.isfile(
                    OO0OOOOO0000OO0OO[0]['full_name']):  #line:963
                return public.returnMsg(False, '全量备份数据不存在！')  #line:964
        else:  #line:965
            return public.returnMsg(False, '全量备份数据不存在！')  #line:966
        OO00000000OO0O000 = OO0OOOOO0000OO0OO[0]['time']  #line:967
        O0O00000OO0OO0OO0 = O000OOO0OOO0000O0.end_time.replace(
            ' ', '__').replace(':', '-')  #line:968
        OOO0OOOOO0OOOOOOO = "db-{}---{}.tar.gz".format(
            O000OOO0OOO0000O0.datab_name, O0O00000OO0OO0OO0)  #line:969
        OOO0OOOOO0OOOOOOO = "db-{}---{}---{}.tar.gz".format(
            O000OOO0OOO0000O0.datab_name, OOO00OO000O0OOOO0._tables,
            O0O00000OO0OO0OO0
        ) if 'table_name' in O000OOO0OOO0000O0 else OOO0OOOOO0OOOOOOO  #line:970
        O00O0000OOO000OO0 = OO0OOOOO0000OO0OO[0][
            'full_name'] + ' ' + O0O00O0OOOO0OOOOO  #line:972
        if os.path.isfile(O0O0OOOOOO0OOO0OO):  #line:973
            O00O0000OOO000OO0 = O00O0000OOO000OO0 + ' ' + O0O0OOOOOO0OOO0OO  #line:974
        O0O0000O0O00O0OOO = []  #line:977
        if os.path.isfile(O0O0OOOOOO0OOO0OO):  #line:978
            O0O0000O0O00O0OOO = json.loads(
                public.readFile(O0O0OOOOOO0OOO0OO))  #line:979
            if not O0O0000O0O00O0OOO[0]['full_name']:
                O0O0000O0O00O0OOO = []  #line:980
        OOO00OO000O0OOOO0.update_file_info(
            O0O00O0OOOO0OOOOO, O000OOO0OOO0000O0.end_time)  #line:981
        OOOO00OO0OOOO0O0O = ''  #line:982
        O0000O000OOO0O000 = ''  #line:983
        if O000OOO0OOO0000O0.end_time != OO00000000OO0O000:  #line:984
            OOO0OO0O0O00OO0O0 = OOO00OO000O0OOOO0.get_every_day(
                OO00000000OO0O000.split()[0],
                O000OOO0OOO0000O0.end_time.split()[0])  #line:985
            O00O0O0OO00O0O000 = OOO00OO000O0OOOO0.get_start_end_binlog(
                OO00000000OO0O000, O000OOO0OOO0000O0.end_time)  #line:986
            if O000OOO0OOO0000O0.end_time == O000OOO0OOO0000O0.end_time.split(
                    ':')[0] + ':00:00':  #line:988
                O00O0O0OO00O0O000['end'] = O00O0O0OO00O0O000[
                    'end'][:-1]  #line:989
            OO0OO00OO00OOOO00 = OOO00OO000O0OOOO0.traverse_all_files(
                OOO000OO000OO0OOO, OOO0OO0O0O00OO0O0,
                O00O0O0OO00O0O000)  #line:990
            if OO0OO00OO00OOOO00 and OO0OO00OO00OOOO00[
                    'file_lists_not']:  #line:992
                print('自动下载前：以下文件不存在{}'.format(
                    OO0OO00OO00OOOO00['file_lists_not']))  #line:993
                for O0O0OOOOOO0OOO0OO in OO0OO00OO00OOOO00[
                        'file_lists_not']:  #line:994
                    for O00O000O0O0000OOO in O0O0OOOOOO0OOO0OO:  #line:995
                        if not os.path.exists(
                                os.path.dirname(O00O000O0O0000OOO)):
                            os.makedirs(
                                os.path.dirname(O00O000O0O0000OOO))  #line:996
                        OO000000O0OOOO0OO = public.M(
                            'mysqlbinlog_backups').where(
                                'sid=? and local_name=?',
                                (O00OO0OOO0OOOOO00['id'],
                                 O00O000O0O0000OOO)).find()  #line:997
                        O0OOOOO00O0O0O00O = 1024  #line:998
                        if OO000000O0OOOO0OO and 'size' in OO000000O0OOOO0OO:
                            O0OOOOO00O0O0O00O = OO000000O0OOOO0OO[
                                'size']  #line:999
                        OOO00OO000O0OOOO0.auto_download_file(
                            O0OOO0OOO0O00O0O0, O00O000O0O0000OOO,
                            O0OOOOO00O0O0O00O)  #line:1000
                OO0OO00OO00OOOO00 = OOO00OO000O0OOOO0.traverse_all_files(
                    OOO000OO000OO0OOO, OOO0OO0O0O00OO0O0,
                    O00O0O0OO00O0O000)  #line:1002
            if OO0OO00OO00OOOO00['status'] == 'False':  #line:1003
                return public.returnMsg(False, '选择指定时间段的数据不完整！')  #line:1004
            for OO0O000000OOOOO0O in range(len(
                    OO0OO00OO00OOOO00['data'])):  #line:1006
                for O0O0O0O0O0O000OOO in OO0OO00OO00OOOO00['data'][
                        OO0O000000OOOOO0O]:  #line:1007
                    OO00000O0OOOOOOOO = ' ' + O0O0O0O0O0O000OOO  #line:1008
                    O00O0000OOO000OO0 += OO00000O0OOOOOOOO  #line:1009
                    if not O00O0O0OO00O0O000['end']: continue  #line:1010
                    O00O00O0000OO000O = ''  #line:1011
                    if O0O0O0O0O0O000OOO == OO0OO00OO00OOOO00[
                            'last']:  #line:1012
                        O00O00O0000OO000O = 'end'  #line:1013
                    if O00O00O0000OO000O:  #line:1014
                        OOO0O000OO0O0OO0O = os.path.dirname(
                            O0O0O0O0O0O000OOO) + '/'  #line:1015
                        if O00O00O0000OO000O == 'end':  #line:1016
                            OOO00O00000O0OOOO = O000OOO0OOO0000O0.end_time  #line:1017
                        O0OOOO0O0O00O00OO, O0OO00OOOO00000OO = OOO00OO000O0OOOO0.extract_file_content(
                            O0O0O0O0O0O000OOO, OOO00O00000O0OOOO)  #line:1019
                        O0OOOO0O0O00O00OO = O0OOOO0O0O00O00OO.replace(
                            '//', '/')  #line:1020
                        O00O0O000OO0OO0OO = OOO00OO000O0OOOO0.create_extract_file(
                            O0OOOO0O0O00O00OO, O0OO00OOOO00000OO)  #line:1022
                        OO000OO00OOOOO0OO = public.readFile(
                            O00O0O000OO0OO0OO)  #line:1023
                        os.system('rm -rf {}'.format(OOO0O000OO0O0OO0O +
                                                     'test/'))  #line:1024
                        if os.path.isfile(O0O0O0O0O0O000OOO):  #line:1026
                            os.system('mv -f {} {}'.format(
                                O0O0O0O0O0O000OOO,
                                O0O0O0O0O0O000OOO + '.bak'))  #line:1027
                            OOOO00OO0OOOO0O0O = O0O0O0O0O0O000OOO + '.bak'  #line:1028
                        if not os.path.isfile(O0O0O0O0O0O000OOO + '.bak'):
                            continue  #line:1029
                        public.writeFile(O0OOOO0O0O00O00OO,
                                         OO000OO00OOOOO0OO)  #line:1030
                        OOO00OO000O0OOOO0.zip_file(
                            O0OOOO0O0O00O00OO)  #line:1031
        if OOOO00OO0OOOO0O0O:  #line:1033
            O0OO0OOOOO00OO00O = ''  #line:1034
            for OO0O000000OOOOO0O in O0O0000O0O00O0OOO:  #line:1035
                if OO0O000000OOOOO0O['full_name'] == OOOO00OO0OOOO0O0O.replace(
                        '.bak', ''):  #line:1036
                    O0OO0OOOOO00OO00O = OO0O000000OOOOO0O  #line:1037
                    break  #line:1038
            if O0OO0OOOOO00OO00O:  #line:1039
                O0000O000OOO0O000 = O0O0000O0O00O0OOO[:O0O0000O0O00O0OOO.index(
                    O0OO0OOOOO00OO00O) + 1]  #line:1040
                public.writeFile(O0O0OOOOOO0OOO0OO,
                                 json.dumps(O0000O000OOO0O000))  #line:1041
        O00O0000OOO000OO0 = O00O0000OOO000OO0.replace(
            OOO00OO000O0OOOO0._save_default_path, './')  #line:1044
        O0OO00OOO0000O0OO = OOO00OO000O0OOOO0._save_default_path + OOO0OOOOO0OOOOOOO  #line:1046
        OO000O0OOO0OOOO00['name'] = '/temp/' + OOO0OOOOO0OOOOOOO  #line:1048
        O0O0O000OOO0O0OOO = os.system('cd {} && tar -czf {} {} -C {}'.format(
            OOO00OO000O0OOOO0._save_default_path, OOO0OOOOO0OOOOOOO,
            O00O0000OOO000OO0, '/temp'))  #line:1049
        public.writeFile(O0O00O0OOOO0OOOOO,
                         json.dumps(OO0OOOOO0000OO0OO))  #line:1052
        if O0O0000O0O00O0OOO:  #line:1053
            public.writeFile(O0O0OOOOOO0OOO0OO,
                             json.dumps(O0O0000O0O00O0OOO))  #line:1054
        if OOOO00OO0OOOO0O0O:
            os.system('mv -f {} {}'.format(
                OOOO00OO0OOOO0O0O, OOOO00OO0OOOO0O0O.replace('.bak',
                                                             '')))  #line:1055
        if os.path.isfile(O0OO00OOO0000O0OO):
            os.system('mv -f {} {}'.format(
                O0OO00OOO0000O0OO, OO000O0OOO0OOOO00['name']))  #line:1056
        if not os.path.isfile(OO000O0OOO0OOOO00['name']):
            return public.returnMsg(False, '导出数据文件{}失败'.format(
                OO000O0OOO0OOOO00['name']))  #line:1057
        for O00O00000O0000OO0 in os.listdir('/temp'):  #line:1059
            if not O00O00000O0000OO0: continue  #line:1060
            if os.path.isfile(
                    os.path.join('/temp', O00O00000O0000OO0)
            ) and O00O00000O0000OO0.find(
                    '.tar.gz'
            ) != -1 and O00O00000O0000OO0.find(
                    '-'
            ) != -1 and O00O00000O0000OO0.find(
                    '---'
            ) != -1 and O00O00000O0000OO0.split(
                    '-'
            )[0] == 'db' and O00O00000O0000OO0 != OOO0OOOOO0OOOOOOO:  #line:1061
                OO0OO000OO0OOOOOO = "([0-9]{4})-([0-9]{2})-([0-9]{2})"  #line:1062
                OO00OOO00O0OO0O0O = "([0-9]{2})-([0-9]{2})-([0-9]{2})"  #line:1063
                O0O0O0O0O0O000OOO = re.search(
                    OO0OO000OO0OOOOOO, str(O00O00000O0000OO0))  #line:1064
                OOOO00O000OOOOO0O = re.search(
                    OO00OOO00O0OO0O0O, str(O00O00000O0000OO0))  #line:1065
                if O0O0O0O0O0O000OOO and OOOO00O000OOOOO0O:  #line:1066
                    os.remove(os.path.join('/temp',
                                           O00O00000O0000OO0))  #line:1067
        return OO000O0OOO0OOOO00  #line:1075

    def extract_file_content(O00OOOO0O00O0O00O, O0O00O00OO00000O0,
                             O000O0O0O0O0000OO):  #line:1077
        ""  #line:1083
        O0O000OO000OO00OO = O00OOOO0O00O0O00O.unzip_file(
            O0O00O00OO00000O0)  #line:1084
        O0O000000000O0O0O = O0O000OO000OO00OO['name']  #line:1085
        O0OO0O0OOO0O00OOO = open(O0O000000000O0O0O, 'r')  #line:1086
        OO00O00O0000O0OO0 = ''  #line:1087
        OOO00OO0OOOO00O00 = O000O0O0O0O0000OO.split()[1].split(':')[
            1]  #line:1088
        OOO0O0O00000O0OOO = O000O0O0O0O0000OO.split()[1].split(':')[
            2]  #line:1089
        for O00O0O0OO00O000OO in O0OO0O0OOO0O00OOO.readlines():  #line:1090
            if O00O0O0OO00O000OO[0] != '#': continue  #line:1091
            if len(O00O0O0OO00O000OO.split()[1].split(':')) < 3:
                continue  #line:1092
            if O00O0O0OO00O000OO.split()[1].split(
                    ':')[1] == OOO00OO0OOOO00O00:  #line:1093
                if O00O0O0OO00O000OO.split()[1].split(
                        ':')[2] > OOO0O0O00000O0OOO:  #line:1094
                    break  #line:1095
            if O00O0O0OO00O000OO.split()[1].split(
                    ':')[1] > OOO00OO0OOOO00O00:  #line:1096
                break  #line:1097
            OO00O00O0000O0OO0 = O00O0O0OO00O000OO.strip()  #line:1098
        O0OO0O0OOO0O00OOO.close  #line:1099
        return O0O000000000O0O0O, OO00O00O0000O0OO0  #line:1100

    def create_extract_file(O0OOOOOO000OO0O0O,
                            O0O000O0O0O0OO0OO,
                            O000000000O0OO00O,
                            is_start=False):  #line:1102
        ""  #line:1110
        OO0OOO0O00OOOO00O = os.path.dirname(
            O0O000O0O0O0OO0OO) + '/test/'  #line:1111
        if not os.path.exists(OO0OOO0O00OOOO00O):
            os.makedirs(OO0OOO0O00OOOO00O)  #line:1112
        O00O0OO00O0O0OOO0 = os.path.basename(O0O000O0O0O0OO0OO)  #line:1113
        OOOOOOO0O0OO000O0 = OO0OOO0O00OOOO00O + O00O0OO00O0O0OOO0  #line:1114
        O0O0OO00O0O0OO0O0 = open(O0O000O0O0O0OO0OO, 'r')  #line:1115
        O0OOO00000OOOOOOO = open(OOOOOOO0O0OO000O0, "w",
                                 encoding="utf-8")  #line:1116
        O0O00O0OO0O00O0OO = True  #line:1117
        for OO000O00O0O0OOO0O in O0O0OO00O0O0OO0O0.readlines():  #line:1118
            OOO0O0OO00O0OO00O = re.search(O000000000O0OO00O,
                                          OO000O00O0O0OOO0O)  #line:1119
            if is_start:  #line:1120
                if O0O00O0OO0O00O0OO == True:  #line:1121
                    if OOO0O0OO00O0OO00O:  #line:1122
                        O0O00O0OO0O00O0OO = False  #line:1123
                    continue  #line:1124
                else:  #line:1125
                    O0OOO00000OOOOOOO.write(OO000O00O0O0OOO0O)  #line:1126
            else:  #line:1127
                if not O0O00O0OO0O00O0OO: break  #line:1128
                O0OOO00000OOOOOOO.write(OO000O00O0O0OOO0O)  #line:1129
            if OOO0O0OO00O0OO00O:  #line:1130
                O0O00O0OO0O00O0OO = False  #line:1131
        O0O0OO00O0O0OO0O0.close  #line:1132
        O0OOO00000OOOOOOO.close  #line:1133
        return OOOOOOO0O0OO000O0  #line:1134

    def import_start_end(OO0000O0OO00000OO, O0O0OO0OO0000O00O,
                         O0O00OO0O0000O000):  #line:1136
        ""  #line:1142
        O0O00OO0O0000O000 = public.to_date(times=O0O00OO0O0000O000)  #line:1143
        O0O0OO0OO0000O00O = public.to_date(times=O0O0OO0OO0000O00O)  #line:1144
        O0O0OO0OO0000O00O = OO0000O0OO00000OO.get_format_date_of_time(
            True, O0O0OO0OO0000O00O)  #line:1145
        O0O0OO0OO0000O00O = public.to_date(times=O0O0OO0OO0000O00O)  #line:1146
        OO0000O0OO00000OO._start_time_list.append(
            O0O0OO0OO0000O00O)  #line:1147
        while True:  #line:1148
            O0O0OO0OO0000O00O += OO0000O0OO00000OO._save_cycle  #line:1149
            OO0000O0OO00000OO._start_time_list.append(
                O0O0OO0OO0000O00O)  #line:1150
            if O0O0OO0OO0000O00O + OO0000O0OO00000OO._save_cycle > O0O00OO0O0000O000:  #line:1151
                break  #line:1152
        O0OOOOO00O0OO0O00 = []  #line:1153
        if OO0000O0OO00000OO._start_time_list:  #line:1154
            O0OOOOOOOOOO0000O = (datetime.datetime.now() + datetime.timedelta(
                hours=1)).strftime("%Y-%m-%d %H") + ":00:00"  #line:1155
            for O0O0O0O000O00000O in OO0000O0OO00000OO._start_time_list:  #line:1157
                OO0OO0O00OO00O0O0 = {}  #line:1158
                OOO0O0O0O000OO000 = float(O0O0O0O000O00000O)  #line:1159
                OO0O000O0OO0OO0OO = float(
                    O0O0O0O000O00000O
                ) + OO0000O0OO00000OO._save_cycle  #line:1160
                if OOO0O0O0O000OO000 < public.to_date(times=json.loads(
                        public.readFile(OO0000O0OO00000OO._full_file))[0]
                                                      ['time']):  #line:1161
                    O0O0OO0OO0000O00O = json.loads(
                        public.readFile(OO0000O0OO00000OO._full_file))[0][
                            'time']  #line:1163
                else:  #line:1164
                    O0O0OO0OO0000O00O = public.format_date(
                        times=OOO0O0O0O000OO000)  #line:1165
                if public.to_date(times=O0O0OO0OO0000O00O) > public.to_date(
                        times=O0OOOOOOOOOO0000O):
                    continue  #line:1166
                if OO0O000O0OO0OO0OO > public.to_date(times=O0OOOOOOOOOO0000O):
                    continue  #line:1167
                O0O00OO0O0000O000 = public.format_date(
                    times=OO0O000O0OO0OO0OO)  #line:1168
                OO0OO0O00OO00O0O0['start_time'] = O0O0OO0OO0000O00O  #line:1169
                OO0OO0O00OO00O0O0['end_time'] = O0O00OO0O0000O000  #line:1170
                O0OOOOO00O0OO0O00.append(OO0OO0O00OO00O0O0)  #line:1171
        return O0OOOOO00O0OO0O00  #line:1172

    def import_date(OOOO00000000000OO, OO000O0O0O00OOO00,
                    O00OOO0OO00000O00):  #line:1174
        ""  #line:1180
        OO00OOO0000000OOO = time.time()  #line:1182
        OOO0000O0O00OOOO0 = public.to_date(times=OO000O0O0O00OOO00)  #line:1183
        O0O0O0OOO0OOOOO00 = OOOO00000000000OO.get_format_date(
            OOO0000O0O00OOOO0)  #line:1184
        OO0O00000O0O0OO00 = O0O0O0OOO0OOOOO00.split('_')[0]  #line:1185
        if OOOO00000000000OO._save_default_path[-1] == '/':
            OOOO00000000000OO._save_default_path = OOOO00000000000OO._save_default_path[:
                                                                                        -1]  #line:1187
        O0000000OO0000OO0 = OOOO00000000000OO._save_default_path + '/' + OO0O00000O0O0OO00 + '/'  #line:1188
        OO0O00000OO0000OO = OOOO00000000000OO._temp_path + OOOO00000000000OO._db_name + '/' + OO0O00000O0O0OO00 + '/'  #line:1189
        if not os.path.exists(O0000000OO0000OO0):
            os.makedirs(O0000000OO0000OO0)  #line:1190
        if not os.path.exists(OO0O00000OO0000OO):
            os.makedirs(OO0O00000OO0000OO)  #line:1191
        if OOOO00000000000OO._save_cycle == 3600:  #line:1192
            O0O0O0OOO0OOOOO00 = O0O0O0OOO0OOOOO00.split(
                '_')[0] + '_' + O0O0O0OOO0OOOOO00.split('_')[1].split('-')[
                    0]  #line:1193
        else:  #line:1194
            pass  #line:1195
        OOO00OO0O0O0OO00O = '{}{}.sql'.format(O0000000OO0000OO0,
                                              O0O0O0OOO0OOOOO00)  #line:1196
        O0O0OOOO0OOO00OO0 = '{}{}.sql'.format(OO0O00000OO0000OO,
                                              O0O0O0OOO0OOOOO00)  #line:1197
        OO0OOOO00O0OOO0OO = OOO00OO0O0O0OO00O.replace('.sql',
                                                      '.zip')  #line:1198
        OOOO00000000000OO._backup_full_list.append(
            OO0OOOO00O0OOO0OO)  #line:1199
        if O00OOO0OO00000O00 == OOOO00000000000OO._backup_end_time:  #line:1200
            if os.path.isfile(OO0OOOO00O0OOO0OO):
                os.remove(OO0OOOO00O0OOO0OO)  #line:1201
        print("|-导出{}".format(OOO00OO0O0O0OO00O), end='')  #line:1202
        if not os.path.exists(O0O0OOOO0OOO00OO0):  #line:1203
            O0O0O0OOO00O0OOOO = "{} --open-files-limit=1024 --start-datetime='{}' --stop-datetime='{}' -d {} {} > {} 2>/dev/null".format(
                OOOO00000000000OO._mysqlbinlog_bin, OO000O0O0O00OOO00,
                O00OOO0OO00000O00, OOOO00000000000OO._db_name,
                OOOO00000000000OO.get_binlog_file(OOO0000O0O00OOOO0),
                O0O0OOOO0OOO00OO0)  #line:1204
            os.system(O0O0O0OOO00O0OOOO)  #line:1205
        if not os.path.exists(O0O0OOOO0OOO00OO0):  #line:1206
            OOOO00000000000OO._backup_fail_list.append(
                OO0OOOO00O0OOO0OO)  #line:1207
            raise Exception('从二进制日志导出sql文件失败!')  #line:1208
        O00O0OOOO00O00000 = ''  #line:1209
        if not OOOO00000000000OO._tables:  #line:1210
            if OOOO00000000000OO._pdata and OOOO00000000000OO._pdata[
                    'table_list']:  #line:1211
                O00O0OOOO00O00000 = '|'.join(
                    list(
                        set(OOOO00000000000OO._pdata['table_list'].split(
                            '|')).union(set(
                                OOOO00000000000OO._new_tables))))  #line:1212
        else:  #line:1213
            O00O0OOOO00O00000 = OOOO00000000000OO._tables  #line:1214
        os.system('cat {} |grep -Ee "({})" > {}'.format(
            O0O0OOOO0OOO00OO0, O00O0OOOO00O00000,
            OOO00OO0O0O0OO00O))  #line:1219
        if os.path.exists(O0O0OOOO0OOO00OO0):
            os.remove(O0O0OOOO0OOO00OO0)  #line:1221
        if not os.path.exists(OOO00OO0O0O0OO00O):  #line:1222
            OOOO00000000000OO._backup_fail_list.append(
                OO0OOOO00O0OOO0OO)  #line:1223
            raise Exception('导出sql文件失败!')  #line:1224
        print(" ==> 成功")  #line:1225
        if OOOO00000000000OO._compress:  #line:1226
            _O00O0O0O0OO0O0000 = OOOO00000000000OO.zip_file(
                OOO00OO0O0O0OO00O)  #line:1227
        else:  #line:1228
            _O00O0O0O0OO0O0000 = os.path.getsize(OOO00OO0O0O0OO00O)  #line:1229
        print("|-文件大小: {}MB, 耗时: {}秒".format(
            round(_O00O0O0O0OO0O0000 / 1024 / 1024, 2),
            round(time.time() - OO00OOO0000000OOO, 2)))  #line:1230
        print("-" * 60)  #line:1231

    def get_date_folder(O0OO0OOOO00O0OOOO, OOO00OO000O00O00O):  #line:1233
        ""  #line:1239
        OOO0O0OOO000O0O0O = []  #line:1240
        for O0O0O0O0OO0000O00 in os.listdir(OOO00OO000O00O00O):  #line:1241
            if os.path.isdir(os.path.join(OOO00OO000O00O00O,
                                          O0O0O0O0OO0000O00)):  #line:1242
                OOOO00OOO0OO0O0O0 = "([0-9]{4})-([0-9]{2})-([0-9]{2})"  #line:1243
                O0O0O0O000OOOO0O0 = re.search(
                    OOOO00OOO0OO0O0O0, str(O0O0O0O0OO0000O00))  #line:1244
                if O0O0O0O000OOOO0O0:  #line:1245
                    OOO0O0OOO000O0O0O.append(O0O0O0O000OOOO0O0[0])  #line:1246
        return OOO0O0OOO000O0O0O  #line:1247

    def kill_process(OOO0O0OO0OOOOO0OO):  #line:1249
        ""  #line:1253
        for O0OO00OOOO0OOOO00 in range(3):  #line:1254
            O00OOO0OOOOOOOO0O = "'{} {} --db_name {} --binlog_id'".format(
                OOO0O0OO0OOOOO0OO._python_path,
                OOO0O0OO0OOOOO0OO._binlogModel_py,
                OOO0O0OO0OOOOO0OO._db_name)  #line:1255
            OO0OO0OOO0000OOO0 = os.popen(
                'ps aux | grep {} |grep -v grep'.format(
                    O00OOO0OOOOOOOO0O))  #line:1256
            OOOOO00O0O000OO00 = OO0OO0OOO0000OOO0.read()  #line:1257
            for O0OO00OOOO0OOOO00 in OOOOO00O0O000OO00.strip().split(
                    '\n'):  #line:1258
                if len(O0OO00OOOO0OOOO00.split()) < 16: continue  #line:1259
                OO0OOOO00OO0OOO0O = int(
                    O0OO00OOOO0OOOO00.split()[9].split(':')[0])  #line:1260
                OOO0OO00O000OOO00 = O0OO00OOOO0OOOO00.split()[1]  #line:1261
                if not public.M('mysqlbinlog_backup_setting').where(
                        'id=?',
                        O0OO00OOOO0OOOO00.split()
                    [15]).count() and OO0OOOO00OO0OOO0O > 10:  #line:1262
                    os.kill(OOO0OO00O000OOO00)  #line:1263
                if OO0OOOO00OO0OOO0O > 50:  #line:1264
                    os.kill(OOO0OO00O000OOO00)  #line:1265
                if OOO0O0OO0OOOOO0OO._binlog_id:  #line:1266
                    if O0OO00OOOO0OOOO00.split()[15] == str(
                            OOO0O0OO0OOOOO0OO._binlog_id
                    ) and OO0OOOO00OO0OOO0O > 0:  #line:1267
                        os.kill(OOO0OO00O000OOO00)  #line:1268
        OO0OO0OOO0000OOO0 = os.popen('ps aux | grep {} |grep -v grep'.format(
            O00OOO0OOOOOOOO0O))  #line:1269
        return OO0OO0OOO0000OOO0.read().strip().split('\n')  #line:1270

    def full_backup(OO00OOOOOO0000000):  #line:1272
        ""  #line:1277
        OO00OO0O0O00O0O00 = OO00OOOOOO0000000._save_default_path + 'full_record.json'  #line:1278
        OOO0OO0OOO0O000O0 = OO00OO0O0O00O0O00.replace('full',
                                                      'inc')  #line:1279
        OO0OO00O00O0OO00O = public.get_mysqldump_bin()  #line:1280
        O0O000OO00OOO0OOO = public.format_date("%Y%m%d_%H%M%S")  #line:1281
        if OO00OOOOOO0000000._tables:  #line:1283
            O0OOOO00000OO000O = OO00OOOOOO0000000._save_default_path + 'db_{}_{}_{}.sql'.format(
                OO00OOOOOO0000000._db_name, OO00OOOOOO0000000._tables,
                O0O000OO00OOO0OOO)  #line:1284
            O0OO00O0000000000 = '{} -uroot -p{} {} {} > {} 2>/dev/null'.format(
                OO0OO00O00O0OO00O, OO00OOOOOO0000000._mysql_root_password,
                OO00OOOOOO0000000._db_name, OO00OOOOOO0000000._tables,
                O0OOOO00000OO000O)  #line:1285
        else:  #line:1287
            O0OOOO00000OO000O = OO00OOOOOO0000000._save_default_path + 'db_{}_{}.sql'.format(
                OO00OOOOOO0000000._db_name, O0O000OO00OOO0OOO)  #line:1288
            O0OO00O0000000000 = OO0OO00O00O0OO00O + " -E -R --default-character-set=" + public.get_database_character(
                OO00OOOOOO0000000._db_name
            ) + " --force --hex-blob --opt " + OO00OOOOOO0000000._db_name + " -u root -p" + str(
                OO00OOOOOO0000000._mysql_root_password
            ) + "> {} 2>/dev/null".format(O0OOOO00000OO000O)  #line:1289
        try:  #line:1290
            os.system(O0OO00O0000000000)  #line:1291
            if not os.path.isfile(O0OOOO00000OO000O): return False  #line:1292
            OO00OOOOOO0000000.zip_file(O0OOOO00000OO000O)  #line:1293
        except Exception as O00OOO0000O0O0000:  #line:1294
            print(O00OOO0000O0O0000)  #line:1295
            return False  #line:1296
        OO00O00OOOO0OO0OO = O0OOOO00000OO000O.replace('.sql',
                                                      '.zip')  #line:1297
        if not os.path.isfile(OO00O00OOOO0OO0OO): return False  #line:1298
        OO00OOOOOO0000000.clean_local_full_backups(
            OO00OO0O0O00O0O00,
            os.path.basename(OO00O00OOOO0OO0OO),
            is_backup=True)  #line:1300
        print('|-已从磁盘清理过期备份文件')  #line:1301
        OO00OOOOOO0000000.clean_local_inc_backups(
            OOO0OO0OOO0O000O0)  #line:1303
        OO00OOOOOO0000000._full_zip_name = OO00OOOOOO0000000._save_default_path + os.path.basename(
            OO00O00OOOO0OO0OO)  #line:1304
        if OO00OOOOOO0000000._tables:  #line:1305
            print('|-完全备份数据库{}中表{}成功！'.format(
                OO00OOOOOO0000000._db_name,
                OO00OOOOOO0000000._tables))  #line:1306
        else:  #line:1307
            print('|-完全备份数据库{}成功！'.format(
                OO00OOOOOO0000000._db_name))  #line:1308
        return True  #line:1309

    def clean_local_inc_backups(O0O000OO0OO0O00O0,
                                OO0OO0O0OO00O0O00):  #line:1311
        ""  #line:1316
        OO00OOO0O0000O000 = O0O000OO0OO0O00O0.get_date_folder(
            O0O000OO0OO0O00O0._save_default_path)  #line:1317
        if OO00OOO0O0000O000:  #line:1318
            for OO0O0O0O0O0O0O00O in OO00OOO0O0000O000:  #line:1319
                O0OOOO00OOO0000O0 = os.path.join(
                    O0O000OO0OO0O00O0._save_default_path,
                    OO0O0O0O0O0O0O00O)  #line:1320
                if os.path.exists(O0OOOO00OOO0000O0):
                    shutil.rmtree(O0OOOO00OOO0000O0)  #line:1321
        if os.path.isfile(OO0OO0O0OO00O0O00):  #line:1322
            os.remove(OO0OO0O0OO00O0O00)  #line:1323

    def clean_local_full_backups(OOOOO00OOO0OO0O00,
                                 OOO0OO0OOOO0000OO,
                                 check_name=None,
                                 is_backup=False,
                                 path=None):  #line:1325
        ""  #line:1331
        if os.path.isfile(OOO0OO0OOOO0000OO):  #line:1332
            O00OO00OOOO0O00O0 = OOOOO00OOO0OO0O00.get_full_backup_file(
                OOOOO00OOO0OO0O00._db_name,
                OOOOO00OOO0OO0O00._save_default_path)  #line:1333
            for O00000O0000000OOO in O00OO00OOOO0O00O0:  #line:1334
                OO0O000O0O000000O = os.path.join(
                    OOOOO00OOO0OO0O00._save_default_path,
                    O00000O0000000OOO['name'])  #line:1335
                if is_backup:  #line:1336
                    if O00000O0000000OOO['name'] != check_name:
                        OOOOO00OOO0OO0O00.delete_file(
                            OO0O000O0O000000O)  #line:1337
                else:  #line:1338
                    OOOOO00OOO0OO0O00.delete_file(
                        OO0O000O0O000000O)  #line:1339
            if not is_backup:
                OOOOO00OOO0OO0O00.delete_file(OOO0OO0OOOO0000OO)  #line:1340

    def check_cloud_oss(OOO00O0OOO0O00000, OO0O0O0O0OOOOOOOO):  #line:1341
        ""  #line:1346
        OO00OO000O0O0OO00 = alioss_main()  #line:1348
        OO0O000OOO00O0OO0 = txcos_main()  #line:1349
        OOO00000O0O0O0O00 = qiniu_main()  #line:1350
        OO0OO0O0O0O0OOOO0 = bos_main()  #line:1351
        OO0O0OOOOO0O0O0O0 = obs_main()  #line:1352
        O0OOO00OO0OO00000 = ftp_main()  #line:1353
        OOOOO0OOOO00OOOOO = []  #line:1354
        O000OOOOOOOO000OO = []  #line:1355
        OO00O0O0O0OOO000O = OOOOO0000000OOO0O = O00O0O0OOO0000OO0 = OOOOOO00O000O0000 = O0O0O00O00O0OOOO0 = O000OOOO00OOO0OOO = False  #line:1357
        if OO0O0O0O0OOOOOOOO['upload_alioss'] == 'alioss':  #line:1359
            if OO00OO000O0O0OO00.check_config():  #line:1360
                OOOOO0OOOO00OOOOO.append(OO00OO000O0O0OO00)  #line:1361
                OO00O0O0O0OOO000O = True  #line:1362
            else:
                O000OOOOOOOO000OO.append('alioss')  #line:1363
        if OO0O0O0O0OOOOOOOO['upload_txcos'] == 'txcos':  #line:1365
            if OO0O000OOO00O0OO0.check_config():  #line:1366
                OOOOO0OOOO00OOOOO.append(OO0O000OOO00O0OO0)  #line:1367
                OOOOO0000000OOO0O = True  #line:1368
            else:
                O000OOOOOOOO000OO.append('txcos')  #line:1369
        if OO0O0O0O0OOOOOOOO['upload_qiniu'] == 'qiniu':  #line:1371
            if OOO00000O0O0O0O00.check_config():  #line:1372
                OOOOO0OOOO00OOOOO.append(OOO00000O0O0O0O00)  #line:1373
                O00O0O0OOO0000OO0 = True  #line:1374
            else:
                O000OOOOOOOO000OO.append('qiniu')  #line:1375
        if OO0O0O0O0OOOOOOOO['upload_bos'] == 'bos':  #line:1377
            if OO0OO0O0O0O0OOOO0.check_config():  #line:1378
                OOOOO0OOOO00OOOOO.append(OO0OO0O0O0O0OOOO0)  #line:1379
                OOOOOO00O000O0000 = True  #line:1380
            else:
                O000OOOOOOOO000OO.append('bos')  #line:1381
        if OO0O0O0O0OOOOOOOO['upload_obs'] == 'obs':  #line:1383
            if OO0O0OOOOO0O0O0O0.check_config():  #line:1384
                OOOOO0OOOO00OOOOO.append(OO0O0OOOOO0O0O0O0)  #line:1385
                O0O0O00O00O0OOOO0 = True  #line:1386
            else:
                O000OOOOOOOO000OO.append('obs')  #line:1387
        if OO0O0O0O0OOOOOOOO['upload_ftp'] == 'ftp':  #line:1389
            if O0OOO00OO0OO00000.check_config():  #line:1390
                OOOOO0OOOO00OOOOO.append(O0OOO00OO0OO00000)  #line:1391
                O000OOOO00OOO0OOO = True  #line:1392
        return OO00O0O0O0OOO000O, OOOOO0000000OOO0O, O00O0O0OOO0000OO0, OOOOOO00O000O0000, O0O0O00O00O0OOOO0, O000OOOO00OOO0OOO, OOOOO0OOOO00OOOOO, O000OOOOOOOO000OO  #line:1393

    def execute_by_comandline(O0O0O0O0OOOO0O0O0, get=None):  #line:1396
        ""  #line:1402
        O0O0O0O0OOOO0O0O0.install_cloud_module()  #line:1403
        if get:  #line:1404
            O0O0O0O0OOOO0O0O0._db_name = get.databname  #line:1405
            O0O0O0O0OOOO0O0O0._binlog_id = get.backup_id  #line:1406
        O0O0O0OOOO0O0OOO0 = []  #line:1407
        OOOOO0OOO000OOO0O = O0O0O0O0OOOO0O0O0.kill_process()  #line:1410
        if len(OOOOO0OOO000OOO0O) > 0:  #line:1411
            time.sleep(0.01)  #line:1412
        O0OO0000OO0OOOOOO = False  #line:1413
        OO0OO0O0OOO0OO00O = O0O0O0O0OOOO0O0O0.get_binlog_status()  #line:1415
        if OO0OO0O0OOO0OO00O['status'] == False:  #line:1416
            O0000O00O00O0OOO0 = '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！'  #line:1417
            print(O0000O00O00O0OOO0)  #line:1418
            O0OO0000OO0OOOOOO = True  #line:1419
        O0O0O0O0OOOO0O0O0._db_mysql = O0O0O0O0OOOO0O0O0._db_mysql.set_host(
            'localhost', O0O0O0O0OOOO0O0O0.get_mysql_port(), '', 'root',
            O0O0O0O0OOOO0O0O0._mysql_root_password)  #line:1421
        OOOOOOO0O0OO00OOO, O0O0000O0O0000O00, O00OO00O0O0O0OO00 = O0O0O0O0OOOO0O0O0._mybackup.get_disk_free(
            O0O0O0O0OOOO0O0O0._save_default_path)  #line:1422
        if not O0OO0000OO0OOOOOO:  #line:1423
            OO00O0O00O0O00000 = ''  #line:1424
            try:  #line:1425
                O00OO0000O0OOOO00 = "select sum(DATA_LENGTH)+sum(INDEX_LENGTH) from information_schema.tables where table_schema=%s"  #line:1426
                OOO00OOOOO00OOOO0 = (O0O0O0O0OOOO0O0O0._db_name, )  #line:1427
                O0O00O000OOO0OOOO = O0O0O0O0OOOO0O0O0._db_mysql.query(
                    O00OO0000O0OOOO00, True, OOO00OOOOO00OOOO0)  #line:1428
                OO00O0O00O0O00000 = O0O0O0O0OOOO0O0O0._mybackup.map_to_list(
                    O0O00O000OOO0OOOO)[0][0]  #line:1429
            except:  #line:1430
                O0OO0000OO0OOOOOO = True  #line:1431
                O0000O00O00O0OOO0 = "数据库连接异常，请检查root用户权限或者数据库配置参数是否正确。"  #line:1432
                print(O0000O00O00O0OOO0)  #line:1433
                O0O0O0OOOO0O0OOO0.append(O0000O00O00O0OOO0)  #line:1434
            if OO00O0O00O0O00000 == None:  #line:1436
                O0000O00O00O0OOO0 = '指定数据库 `{}` 没有任何数据!'.format(
                    O0O0O0O0OOOO0O0O0._db_name)  #line:1437
                O0OO0000OO0OOOOOO = True  #line:1438
                print(O0000O00O00O0OOO0)  #line:1439
                O0O0O0OOOO0O0OOO0.append(O0000O00O00O0OOO0)  #line:1440
            if OOOOOOO0O0OO00OOO:  #line:1442
                if OO00O0O00O0O00000:  #line:1443
                    if O0O0000O0O0000O00 < OO00O0O00O0O00000:  #line:1444
                        O0000O00O00O0OOO0 = "目标分区可用的磁盘空间小于{},无法完成备份，请增加磁盘容量!".format(
                            public.to_size(OO00O0O00O0O00000))  #line:1445
                        print(O0000O00O00O0OOO0)  #line:1446
                        O0OO0000OO0OOOOOO = True  #line:1447
                        O0O0O0OOOO0O0OOO0.append(O0000O00O00O0OOO0)  #line:1448
                if O00OO00O0O0O0OO00 < O0O0O0O0OOOO0O0O0._inode_min:  #line:1450
                    O0000O00O00O0OOO0 = "目标分区可用的Inode小于{},无法完成备份，请增加磁盘容量!".format(
                        O0O0O0O0OOOO0O0O0._inode_min)  #line:1451
                    print(O0000O00O00O0OOO0)  #line:1452
                    O0OO0000OO0OOOOOO = True  #line:1453
                    O0O0O0OOOO0O0OOO0.append(O0000O00O00O0OOO0)  #line:1454
        O0O0O0O0OOOO0O0O0._pdata = OO0O0O0000O0OO00O = public.M(
            'mysqlbinlog_backup_setting').where(
                'id=?', str(O0O0O0O0OOOO0O0O0._binlog_id)).find()  #line:1457
        OOO00000O0OO00O0O = OO0O0O0000O0OO00O[
            'database_table'] if OO0O0O0000O0OO00O else O0O0O0O0OOOO0O0O0._db_name  #line:1458
        O0O0O0O0OOOO0O0O0._echo_info['echo'] = public.M('crontab').where(
            "sBody=?", ('{} {} --db_name {} --binlog_id {}'.format(
                O0O0O0O0OOOO0O0O0._python_path,
                O0O0O0O0OOOO0O0O0._binlogModel_py, O0O0O0O0OOOO0O0O0._db_name,
                str(O0O0O0O0OOOO0O0O0._binlog_id)), )).getField(
                    'echo')  #line:1460
        O0O0O0O0OOOO0O0O0._mybackup = backup(
            cron_info=O0O0O0O0OOOO0O0O0._echo_info)  #line:1461
        if not OO0O0O0000O0OO00O:  #line:1462
            print('未在数据库备份记录中找到id为{}的计划任务'.format(
                O0O0O0O0OOOO0O0O0._binlog_id))  #line:1463
            O0OO0000OO0OOOOOO = True  #line:1464
        if O0O0O0O0OOOO0O0O0._db_name not in O0O0O0O0OOOO0O0O0.get_tables_list(
                O0O0O0O0OOOO0O0O0.get_databases()):  #line:1465
            print('备份的数据库不存在')  #line:1466
            O0OO0000OO0OOOOOO = True  #line:1467
        if O0OO0000OO0OOOOOO:  #line:1468
            O0O0O0O0OOOO0O0O0.send_failture_notification(
                O0O0O0OOOO0O0OOO0, target=OOO00000O0OO00O0O)  #line:1470
            return public.returnMsg(False, '备份失败')  #line:1471
        O0O0O0O0OOOO0O0O0._zip_password = OO0O0O0000O0OO00O[
            'zip_password']  #line:1472
        if OO0O0O0000O0OO00O['backup_type'] == 'tables':
            O0O0O0O0OOOO0O0O0._tables = OO0O0O0000O0OO00O[
                'tb_name']  #line:1473
        O0O0O0O0OOOO0O0O0._save_default_path = OO0O0O0000O0OO00O[
            'save_path']  #line:1474
        print("|-分区{}可用磁盘空间为：{},可用Inode为:{}".format(
            OOOOOOO0O0OO00OOO, public.to_size(O0O0000O0O0000O00),
            O00OO00O0O0O0OO00))  #line:1475
        if not os.path.exists(
                O0O0O0O0OOOO0O0O0._save_default_path):  #line:1477
            os.makedirs(O0O0O0O0OOOO0O0O0._save_default_path)  #line:1478
            OOO0000OOO00O00OO = True  #line:1479
        O0O0O0O0OOOO0O0O0._full_file = O0O0O0O0OOOO0O0O0._save_default_path + 'full_record.json'  #line:1480
        O0O0O0O0OOOO0O0O0._inc_file = O0O0O0OO00OOOO00O = O0O0O0O0OOOO0O0O0._save_default_path + 'inc_record.json'  #line:1481
        OO0O0O0000O0OO00O[
            'last_excute_backup_time'] = O0O0O0O0OOOO0O0O0._backup_end_time = public.format_date(
            )  #line:1482
        O0O0O0O0OOOO0O0O0._tables = OO0O0O0000O0OO00O['tb_name']  #line:1483
        O0O00000OOO0OO00O = '/tables/' + O0O0O0O0OOOO0O0O0._tables + '/' if O0O0O0O0OOOO0O0O0._tables else '/databases/'  #line:1484
        O0O0O0O0OOOO0O0O0._backup_type = 'tables' if O0O0O0O0OOOO0O0O0._tables else 'databases'  #line:1485
        O00OOO0OOOOO0O0OO = OO0O0O0000O0OO00O['start_backup_time']  #line:1487
        OO0O0O00OO0OO0O0O = OO0O0O0000O0OO00O['end_backup_time']  #line:1488
        OOO0000OOO00O00OO = False  #line:1489
        O00O000O00OOO00OO = {
            'alioss': '阿里云OSS',
            'txcos': '腾讯云COS',
            'qiniu': '七牛云存储',
            'bos': '百度云存储',
            'obs': '华为云存储'
        }  #line:1490
        OO0O0OO00OO0O00OO, OOOO0O00OO0OO0O00, O0O0OO0OOOOO0000O, O0OOO0OOO000O0O00, OO00O0OO000O0OO00, OO0O0OOO000O0OO00, O0OOOO00OOO0OOOOO, O0OOO0OO0O000OOO0 = O0O0O0O0OOOO0O0O0.check_cloud_oss(
            OO0O0O0000O0OO00O)  #line:1492
        if O0OOO0OO0O000OOO0:  #line:1493
            OOO0OOO0OOO0000OO = []  #line:1494
            print('检测到无法连接上以下云存储：')  #line:1495
            for OO0O0O0000OOOO0OO in O0OOO0OO0O000OOO0:  #line:1496
                if not OO0O0O0000OOOO0OO: continue  #line:1497
                OOO0OOO0OOO0000OO.append(
                    O00O000O00OOO00OO[OO0O0O0000OOOO0OO])  #line:1498
                print('{}'.format(
                    O00O000O00OOO00OO[OO0O0O0000OOOO0OO]))  #line:1499
            O0000O00O00O0OOO0 = '检测到无法连接上以下云存储：{}'.format(
                OOO0OOO0OOO0000OO)  #line:1500
            print('请检查配置或者更改备份设置！')  #line:1501
            O0O0O0O0OOOO0O0O0.send_failture_notification(
                O0000O00O00O0OOO0, target=OOO00000O0OO00O0O)  #line:1503
            return public.returnMsg(False, '备份失败')  #line:1504
        if not os.path.isfile(O0O0O0O0OOOO0O0O0._full_file):  #line:1506
            O0O0O0O0OOOO0O0O0.auto_download_file(
                O0OOOO00OOO0OOOOO, O0O0O0O0OOOO0O0O0._full_file)  #line:1508
        O000O0OO0O0OOOOOO = {}  #line:1509
        if os.path.isfile(O0O0O0O0OOOO0O0O0._full_file):  #line:1510
            try:  #line:1511
                O000O0OO0O0OOOOOO = json.loads(
                    public.readFile(
                        O0O0O0O0OOOO0O0O0._full_file))[0]  #line:1512
                if 'name' not in O000O0OO0O0OOOOOO or 'size' not in O000O0OO0O0OOOOOO or 'time' not in O000O0OO0O0OOOOOO:
                    OOO0000OOO00O00OO = True  #line:1513
                if 'end_time' in O000O0OO0O0OOOOOO:  #line:1514
                    if O000O0OO0O0OOOOOO['end_time'] != O000O0OO0O0OOOOOO[
                            'end_time'].split(':')[0] + ':00:00':  #line:1515
                        OO0O0O00OO0OO0O0O = O000O0OO0O0OOOOOO[
                            'end_time'].split(':')[0] + ':00:00'  #line:1516
                if 'full_name' in O000O0OO0O0OOOOOO and os.path.isfile(
                        O000O0OO0O0OOOOOO['full_name']
                ) and time.time() - public.to_date(
                        times=O00OOO0OOOOO0O0OO) > 604800:  #line:1517
                    OOO0000OOO00O00OO = True  #line:1518
                if 'time' in O000O0OO0O0OOOOOO:  #line:1520
                    O00OOO0OOOOO0O0OO = O000O0OO0O0OOOOOO['time']  #line:1521
                    if not os.path.isfile(
                            O0O0O0O0OOOO0O0O0._inc_file
                    ) and OO0O0O00OO0OO0O0O != O000O0OO0O0OOOOOO[
                            'time']:  #line:1522
                        O0O0O0O0OOOO0O0O0.auto_download_file(
                            O0OOOO00OOO0OOOOO,
                            O0O0O0O0OOOO0O0O0._inc_file)  #line:1524
                    if not os.path.isfile(
                            O0O0O0O0OOOO0O0O0._inc_file
                    ) and OO0O0O00OO0OO0O0O != O000O0OO0O0OOOOOO[
                            'time']:  #line:1525
                        print('增量备份记录文件不存在,将执行完全备份')  #line:1526
                        OOO0000OOO00O00OO = True  #line:1527
            except:  #line:1528
                O000O0OO0O0OOOOOO = {}  #line:1529
                OOO0000OOO00O00OO = True  #line:1530
        else:  #line:1531
            OOO0000OOO00O00OO = True  #line:1532
        O00O0O0O0O0OOOOO0 = False  #line:1533
        if OOO0000OOO00O00OO:  #line:1536
            print('☆☆☆完全备份开始☆☆☆')  #line:1537
            OO000OOOO000OOOOO = []  #line:1538
            if not O0O0O0O0OOOO0O0O0.full_backup():  #line:1539
                O0000O00O00O0OOO0 = '全量备份数据库[{}]'.format(
                    O0O0O0O0OOOO0O0O0._db_name)  #line:1540
                O0O0O0O0OOOO0O0O0.send_failture_notification(
                    O0000O00O00O0OOO0, target=OOO00000O0OO00O0O)  #line:1541
                return public.returnMsg(False, O0000O00O00O0OOO0)  #line:1542
            if os.path.isfile(O0O0O0O0OOOO0O0O0._full_file):  #line:1543
                try:  #line:1544
                    OO000OOOO000OOOOO = json.loads(
                        public.readFile(
                            O0O0O0O0OOOO0O0O0._full_file))  #line:1545
                except:  #line:1546
                    OO000OOOO000OOOOO = []  #line:1547
            O0O0O0O0OOOO0O0O0.set_file_info(O0O0O0O0OOOO0O0O0._full_zip_name,
                                            O0O0O0O0OOOO0O0O0._full_file,
                                            is_full=True)  #line:1549
            try:  #line:1550
                O000O0OO0O0OOOOOO = json.loads(
                    public.readFile(
                        O0O0O0O0OOOO0O0O0._full_file))[0]  #line:1551
            except:  #line:1552
                print('|-文件写入失败，检查是否有安装安全软件！')  #line:1553
                print('|-备份失败！')  #line:1554
                return  #line:1555
            OO0O0O0000O0OO00O['start_backup_time'] = OO0O0O0000O0OO00O[
                'end_backup_time'] = O000O0OO0O0OOOOOO['time']  #line:1556
            public.M('mysqlbinlog_backup_setting').where(
                'id=?',
                OO0O0O0000O0OO00O['id']).update(OO0O0O0000O0OO00O)  #line:1557
            OO0OOO00O0000O0OO = '/bt_backup/mysql_bin_log/' + O0O0O0O0OOOO0O0O0._db_name + O0O00000OOO0OO00O  #line:1558
            OOO000000OO000000 = OO0OOO00O0000O0OO + O000O0OO0O0OOOOOO[
                'name']  #line:1559
            OOOO0OOOOO000O0O0 = OO0OOO00O0000O0OO + 'full_record.json'  #line:1560
            OOO000000OO000000 = OOO000000OO000000.replace('//',
                                                          '/')  #line:1561
            OOOO0OOOOO000O0O0 = OOOO0OOOOO000O0O0.replace('//',
                                                          '/')  #line:1562
            if OO0O0OO00OO0O00OO:  #line:1564
                OO0OOOOOO0OO0OOOO = alioss_main()  #line:1565
                if not OO0OOOOOO0OO0OOOO.upload_file_by_path(
                        O000O0OO0O0OOOOOO['full_name'],
                        OOO000000OO000000):  #line:1566
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O000O0OO0O0OOOOOO['full_name'])  #line:1567
                if not OO0OOOOOO0OO0OOOO.upload_file_by_path(
                        O0O0O0O0OOOO0O0O0._full_file, OOOO0OOOOO000O0O0):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O0O0O0O0OOOO0O0O0._full_file)  #line:1568
                O0O0O0O0OOOO0O0O0.clean_cloud_backups(
                    OO0OOO00O0000O0OO, O0O0O0O0OOOO0O0O0._full_file,
                    OO0OOOOOO0OO0OOOO, O00O000O00OOO00OO['alioss'])  #line:1570
            else:  #line:1571
                if OO0O0O0000O0OO00O['upload_alioss'] == 'alioss':  #line:1572
                    O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                        O00O000O00OOO00OO['alioss'],
                        O00O000O00OOO00OO['alioss'])  #line:1573
                    O00O0O0O0O0OOOOO0 = True  #line:1574
                    print(O0000O00O00O0OOO0)  #line:1575
            if OOOO0O00OO0OO0O00:  #line:1577
                OO000000000O0O0O0 = txcos_main()  #line:1578
                if not OO000000000O0O0O0.upload_file_by_path(
                        O000O0OO0O0OOOOOO['full_name'],
                        OOO000000OO000000):  #line:1579
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O000O0OO0O0OOOOOO['full_name'])  #line:1580
                if not OO000000000O0O0O0.upload_file_by_path(
                        O0O0O0O0OOOO0O0O0._full_file,
                        OOOO0OOOOO000O0O0):  #line:1581
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O0O0O0O0OOOO0O0O0._full_file)  #line:1582
                O0O0O0O0OOOO0O0O0.clean_cloud_backups(
                    OO0OOO00O0000O0OO, O0O0O0O0OOOO0O0O0._full_file,
                    OO000000000O0O0O0, O00O000O00OOO00OO['txcos'])  #line:1584
            else:  #line:1585
                if OO0O0O0000O0OO00O['upload_txcos'] == 'txcos':  #line:1586
                    O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                        O00O000O00OOO00OO['txcos'],
                        O00O000O00OOO00OO['txcos'])  #line:1587
                    O00O0O0O0O0OOOOO0 = True  #line:1588
                    print(O0000O00O00O0OOO0)  #line:1589
            if O0O0OO0OOOOO0000O:  #line:1591
                OOOO00000OOO0OO00 = qiniu_main()  #line:1592
                if not OOOO00000OOO0OO00.upload_file_by_path(
                        O000O0OO0O0OOOOOO['full_name'], OOO000000OO000000):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O000O0OO0O0OOOOOO['full_name'])  #line:1593
                if not OOOO00000OOO0OO00.upload_file_by_path(
                        O0O0O0O0OOOO0O0O0._full_file, OOOO0OOOOO000O0O0):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O0O0O0O0OOOO0O0O0._full_file)  #line:1594
                O0O0O0O0OOOO0O0O0.clean_cloud_backups(
                    OO0OOO00O0000O0OO, O0O0O0O0OOOO0O0O0._full_file,
                    OOOO00000OOO0OO00, O00O000O00OOO00OO['qiniu'])  #line:1596
            else:  #line:1597
                if OO0O0O0000O0OO00O['upload_qiniu'] == 'qiniu':  #line:1598
                    O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                        O00O000O00OOO00OO['qiniu'],
                        O00O000O00OOO00OO['qiniu'])  #line:1599
                    O00O0O0O0O0OOOOO0 = True  #line:1600
                    print(O0000O00O00O0OOO0)  #line:1601
            if O0OOO0OOO000O0O00:  #line:1603
                O0O0O0O0O0O00OOOO = bos_main()  #line:1604
                if not O0O0O0O0O0O00OOOO.upload_file_by_path(
                        O000O0OO0O0OOOOOO['full_name'], OOO000000OO000000):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O000O0OO0O0OOOOOO['full_name'])  #line:1605
                if not O0O0O0O0O0O00OOOO.upload_file_by_path(
                        O0O0O0O0OOOO0O0O0._full_file, OOOO0OOOOO000O0O0):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O0O0O0O0OOOO0O0O0._full_file)  #line:1606
                O0O0O0O0OOOO0O0O0.clean_cloud_backups(
                    OO0OOO00O0000O0OO, O0O0O0O0OOOO0O0O0._full_file,
                    O0O0O0O0O0O00OOOO, O00O000O00OOO00OO['bos'])  #line:1608
            else:  #line:1609
                if OO0O0O0000O0OO00O['upload_bos'] == 'bos':  #line:1610
                    O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                        O00O000O00OOO00OO['bos'],
                        O00O000O00OOO00OO['bos'])  #line:1611
                    O00O0O0O0O0OOOOO0 = True  #line:1612
                    print(O0000O00O00O0OOO0)  #line:1613
            if OO00O0OO000O0OO00:  #line:1616
                OOO00O0O000000000 = obs_main()  #line:1617
                if not OOO00O0O000000000.upload_file_by_path(
                        O000O0OO0O0OOOOOO['full_name'], OOO000000OO000000):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O000O0OO0O0OOOOOO['full_name'])  #line:1618
                if not OOO00O0O000000000.upload_file_by_path(
                        O0O0O0O0OOOO0O0O0._full_file, OOOO0OOOOO000O0O0):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O0O0O0O0OOOO0O0O0._full_file)  #line:1619
                O0O0O0O0OOOO0O0O0.clean_cloud_backups(
                    OO0OOO00O0000O0OO, O0O0O0O0OOOO0O0O0._full_file,
                    OOO00O0O000000000, O00O000O00OOO00OO['obs'])  #line:1621
            else:  #line:1622
                if OO0O0O0000O0OO00O['upload_obs'] == 'obs':  #line:1623
                    O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                        O00O000O00OOO00OO['obs'],
                        O00O000O00OOO00OO['obs'])  #line:1624
                    O00O0O0O0O0OOOOO0 = True  #line:1625
                    print(O0000O00O00O0OOO0)  #line:1626
            if OO0O0OOO000O0OO00:  #line:1629
                OO0000OO0O00OO00O = ftp_main()  #line:1630
                if not OO0000OO0O00OO00O.upload_file_by_path(
                        O000O0OO0O0OOOOOO['full_name'], OOO000000OO000000):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O000O0OO0O0OOOOOO['full_name'])  #line:1631
                if not OO0000OO0O00OO00O.upload_file_by_path(
                        O0O0O0O0OOOO0O0O0._full_file, OOOO0OOOOO000O0O0):
                    O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                        O0O0O0O0OOOO0O0O0._full_file)  #line:1632
                O0O0O0O0OOOO0O0O0.clean_cloud_backups(
                    OO0OOO00O0000O0OO, O0O0O0O0OOOO0O0O0._full_file,
                    OO0000OO0O00OO00O, O00O000O00OOO00OO['ftp'])  #line:1634
            else:  #line:1635
                if OO0O0O0000O0OO00O['upload_ftp'] == 'ftp':  #line:1636
                    O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                        O00O000O00OOO00OO['ftp'],
                        O00O000O00OOO00OO['ftp'])  #line:1637
                    O00O0O0O0O0OOOOO0 = True  #line:1638
                    print(O0000O00O00O0OOO0)  #line:1639
            O0000O00O00O0OOO0 = '以下文件上传失败：{}'.format(
                O0O0O0O0OOOO0O0O0._cloud_upload_not)  #line:1640
            if O0O0O0O0OOOO0O0O0._cloud_upload_not or O00O0O0O0O0OOOOO0:  #line:1641
                O0O0O0O0OOOO0O0O0.send_failture_notification(
                    O0000O00O00O0OOO0, target=OOO00000O0OO00O0O)  #line:1642
                if OO000OOOO000OOOOO:
                    public.writeFile(O0O0O0O0OOOO0O0O0._full_file,
                                     json.dumps(OO000OOOO000OOOOO))  #line:1643
            print('☆☆☆完全备份结束☆☆☆')  #line:1644
            OO0OOOOO0OOO0O000 = 'full'  #line:1645
            O0O0000000O0O0OO0 = json.loads(
                public.readFile(O0O0O0O0OOOO0O0O0._full_file))  #line:1646
            O0O0O0O0OOOO0O0O0.write_backups(OO0OOOOO0OOO0O000,
                                            O0O0000000O0O0OO0)  #line:1647
            if OO0O0O0000O0OO00O['upload_local'] == '' and os.path.isfile(
                    O0O0O0O0OOOO0O0O0._full_file):  #line:1649
                O0O0O0O0OOOO0O0O0.clean_local_full_backups(
                    O0O0O0O0OOOO0O0O0._full_file)  #line:1650
                if os.path.isfile(O0O0O0O0OOOO0O0O0._inc_file):
                    O0O0O0O0OOOO0O0O0.clean_local_inc_backups(
                        O0O0O0O0OOOO0O0O0._inc_file)  #line:1651
                print('|-用户设置不保留本地备份，已从本地服务器清理备份')  #line:1652
            return public.returnMsg(True, '完全备份成功！')  #line:1653
        O0O0O0O0OOOO0O0O0._backup_add_time = OO0O0O0000O0OO00O[
            'start_backup_time']  #line:1655
        O0O0O0O0OOOO0O0O0._backup_start_time = OO0O0O00OO0OO0O0O  #line:1656
        O0O0O0O0OOOO0O0O0._new_tables = O0O0O0O0OOOO0O0O0.get_tables_list(
            O0O0O0O0OOOO0O0O0.get_tables())  #line:1657
        if O0O0O0O0OOOO0O0O0._backup_start_time and O0O0O0O0OOOO0O0O0._backup_end_time:  #line:1658
            OO0OOO00OO0OO0OO0 = O0O0O0O0OOOO0O0O0.import_start_end(
                O0O0O0O0OOOO0O0O0._backup_start_time,
                O0O0O0O0OOOO0O0O0._backup_end_time)  #line:1659
            for O000OOO0000000O0O in OO0OOO00OO0OO0OO0:  #line:1660
                if not O000OOO0000000O0O: continue  #line:1661
                O0O0O0O0OOOO0O0O0._backup_fail_list = []  #line:1662
                if public.to_date(
                        times=O000OOO0000000O0O['end_time']) > public.to_date(
                            times=O0O0O0O0OOOO0O0O0._backup_end_time):
                    O000OOO0000000O0O[
                        'end_time'] = O0O0O0O0OOOO0O0O0._backup_end_time  #line:1663
                O0O0O0O0OOOO0O0O0.import_date(
                    O000OOO0000000O0O['start_time'],
                    O000OOO0000000O0O['end_time'])  #line:1664
        OOO00O00OOO0O0OOO = OO0O0O0000O0OO00O['save_path']  #line:1666
        OO00OO00OO0OO0000 = O0O0O0O0OOOO0O0O0.get_every_day(
            O0O0O0O0OOOO0O0O0._backup_start_time.split()[0],
            O0O0O0O0OOOO0O0O0._backup_end_time.split()[0])  #line:1667
        O00O0OOOOO00OO0OO = 'True'  #line:1668
        OO0OOOOO0OOO00OO0 = O0O0O0O0OOOO0O0O0.get_start_end_binlog(
            O0O0O0O0OOOO0O0O0._backup_start_time,
            O0O0O0O0OOOO0O0O0._backup_end_time, O00O0OOOOO00OO0OO)  #line:1669
        OOO0O00OOOOO00OO0 = O0O0O0O0OOOO0O0O0.traverse_all_files(
            OOO00O00OOO0O0OOO, OO00OO00OO0OO0000,
            OO0OOOOO0OOO00OO0)  #line:1670
        if O0O0O0O0OOOO0O0O0._backup_fail_list or OOO0O00OOOOO00OO0[
                'file_lists_not']:  #line:1671
            O0O000OOOOOO0OOO0 = ''  #line:1672
            if O0O0O0O0OOOO0O0O0._backup_fail_list:
                O0O000OOOOOO0OOO0 = O0O0O0O0OOOO0O0O0._backup_fail_list  #line:1673
            else:
                O0O000OOOOOO0OOO0 = OOO0O00OOOOO00OO0[
                    'file_lists_not']  #line:1674
            O0000O00O00O0OOO0 = '以下文件备份失败{}'.format(
                O0O000OOOOOO0OOO0)  #line:1676
            O0O0O0O0OOOO0O0O0.send_failture_notification(
                O0000O00O00O0OOO0, target=OOO00000O0OO00O0O)  #line:1678
            print(O0000O00O00O0OOO0)  #line:1679
            return public.returnMsg(False, O0000O00O00O0OOO0)  #line:1680
        OO000OOOOO00OOO0O = json.loads(
            public.readFile(O0O0O0O0OOOO0O0O0._full_file))  #line:1681
        OO0O0O0000O0OO00O[
            'end_backup_time'] = O0O0O0O0OOOO0O0O0._backup_end_time  #line:1683
        OO0O0O0000O0OO00O['table_list'] = '|'.join(
            O0O0O0O0OOOO0O0O0._new_tables)  #line:1685
        O0O0O0O0OOOO0O0O0.update_file_info(
            O0O0O0O0OOOO0O0O0._full_file,
            O0O0O0O0OOOO0O0O0._backup_end_time)  #line:1686
        OOO000OOOO0O0OO00 = OOOO0OO0O0000O0OO = False  #line:1688
        for OO0O00O000OO00OOO in OOO0O00OOOOO00OO0['data']:  #line:1689
            if OO0O00O000OO00OOO == OOO0O00OOOOO00OO0['data'][-1]:
                OOO000OOOO0O0OO00 = True  #line:1690
            for O000000000O000OO0 in OO0O00O000OO00OOO:  #line:1691
                if O000000000O000OO0 == OO0O00O000OO00OOO[-1]:
                    OOOO0OO0O0000O0OO = True  #line:1692
                O0O0O0O0OOOO0O0O0.set_file_info(O000000000O000OO0,
                                                O0O0O0OO00OOOO00O)  #line:1693
                OOO0OO0OO0OO00000 = '/bt_backup/mysql_bin_log/' + O0O0O0O0OOOO0O0O0._db_name + O0O00000OOO0OO00O  #line:1694
                OOOOOOO0O00O00O00 = OOO0OO0OO0OO00000 + 'full_record.json'  #line:1695
                O0O0O000O0OOOOOOO = OOO0OO0OO0OO00000 + 'inc_record.json'  #line:1696
                OOO000000OO000000 = '/bt_backup/mysql_bin_log/' + O0O0O0O0OOOO0O0O0._db_name + O0O00000OOO0OO00O + O000000000O000OO0.split(
                    '/')[-2] + '/' + O000000000O000OO0.split('/')[
                        -1]  #line:1697
                if OO0O0OO00OO0O00OO:  #line:1698
                    OO0OOOOOO0OO0OOOO = alioss_main()  #line:1699
                    if not OO0OOOOOO0OO0OOOO.upload_file_by_path(
                            O000000000O000OO0, OOO000000OO000000):  #line:1700
                        O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                            O000000000O000OO0)  #line:1701
                    if os.path.isfile(
                            O0O0O0OO00OOOO00O
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OO0OOOOOO0OO0OOOO.upload_file_by_path(
                            O0O0O0OO00OOOO00O, O0O0O000O0OOOOOOO)  #line:1702
                    if os.path.isfile(
                            O0O0O0O0OOOO0O0O0._full_file
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OO0OOOOOO0OO0OOOO.upload_file_by_path(
                            O0O0O0O0OOOO0O0O0._full_file,
                            OOOOOOO0O00O00O00)  #line:1703
                else:  #line:1704
                    if OO0O0O0000O0OO00O[
                            'upload_alioss'] == 'alioss':  #line:1705
                        O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                            O00O000O00OOO00OO['alioss'],
                            O00O000O00OOO00OO['alioss'])  #line:1706
                        O00O0O0O0O0OOOOO0 = True  #line:1707
                        print(O0000O00O00O0OOO0)  #line:1708
                if OOOO0O00OO0OO0O00:  #line:1709
                    OO000000000O0O0O0 = txcos_main()  #line:1710
                    if not OO000000000O0O0O0.upload_file_by_path(
                            O000000000O000OO0, OOO000000OO000000):  #line:1711
                        O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                            O000000000O000OO0)  #line:1712
                    if os.path.isfile(
                            O0O0O0OO00OOOO00O
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OO000000000O0O0O0.upload_file_by_path(
                            O0O0O0OO00OOOO00O, O0O0O000O0OOOOOOO)  #line:1713
                    if os.path.isfile(
                            O0O0O0O0OOOO0O0O0._full_file
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OO000000000O0O0O0.upload_file_by_path(
                            O0O0O0OO00OOOO00O, OOOOOOO0O00O00O00)  #line:1714
                else:  #line:1715
                    if OO0O0O0000O0OO00O[
                            'upload_txcos'] == 'txcos':  #line:1716
                        O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                            O00O000O00OOO00OO['txcos'],
                            O00O000O00OOO00OO['txcos'])  #line:1717
                        O00O0O0O0O0OOOOO0 = True  #line:1718
                        print(O0000O00O00O0OOO0)  #line:1719
                if O0O0OO0OOOOO0000O:  #line:1720
                    OOOO00000OOO0OO00 = qiniu_main()  #line:1721
                    if not OOOO00000OOO0OO00.upload_file_by_path(
                            O000000000O000OO0, OOO000000OO000000):  #line:1722
                        O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                            O000000000O000OO0)  #line:1723
                    if os.path.isfile(
                            O0O0O0OO00OOOO00O
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OOOO00000OOO0OO00.upload_file_by_path(
                            O0O0O0OO00OOOO00O, O0O0O000O0OOOOOOO)  #line:1724
                    if os.path.isfile(
                            O0O0O0O0OOOO0O0O0._full_file
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OOOO00000OOO0OO00.upload_file_by_path(
                            O0O0O0OO00OOOO00O, OOOOOOO0O00O00O00)  #line:1725
                else:  #line:1726
                    if OO0O0O0000O0OO00O[
                            'upload_qiniu'] == 'qiniu':  #line:1727
                        O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                            O00O000O00OOO00OO['qiniu'],
                            O00O000O00OOO00OO['qiniu'])  #line:1728
                        O00O0O0O0O0OOOOO0 = True  #line:1729
                        print(O0000O00O00O0OOO0)  #line:1730
                if O0OOO0OOO000O0O00:  #line:1731
                    O0O0O0O0O0O00OOOO = bos_main()  #line:1732
                    if not O0O0O0O0O0O00OOOO.upload_file_by_path(
                            O000000000O000OO0, OOO000000OO000000):  #line:1733
                        O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                            O000000000O000OO0)  #line:1734
                    if os.path.isfile(
                            O0O0O0OO00OOOO00O
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        O0O0O0O0O0O00OOOO.upload_file_by_path(
                            O0O0O0OO00OOOO00O, O0O0O000O0OOOOOOO)  #line:1735
                    if os.path.isfile(
                            O0O0O0O0OOOO0O0O0._full_file
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        O0O0O0O0O0O00OOOO.upload_file_by_path(
                            O0O0O0OO00OOOO00O, OOOOOOO0O00O00O00)  #line:1736
                else:  #line:1737
                    if OO0O0O0000O0OO00O['upload_bos'] == 'bos':  #line:1738
                        O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                            O00O000O00OOO00OO['bos'],
                            O00O000O00OOO00OO['bos'])  #line:1739
                        O00O0O0O0O0OOOOO0 = True  #line:1740
                        print(O0000O00O00O0OOO0)  #line:1741
                if OO00O0OO000O0OO00:  #line:1743
                    OOO00O0O000000000 = obs_main()  #line:1744
                    if not OOO00O0O000000000.upload_file_by_path(
                            O000000000O000OO0, OOO000000OO000000):  #line:1745
                        O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                            O000000000O000OO0)  #line:1746
                    if os.path.isfile(
                            O0O0O0OO00OOOO00O
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OOO00O0O000000000.upload_file_by_path(
                            O0O0O0OO00OOOO00O, O0O0O000O0OOOOOOO)  #line:1747
                    if os.path.isfile(
                            O0O0O0O0OOOO0O0O0._full_file
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OOO00O0O000000000.upload_file_by_path(
                            O0O0O0O0OOOO0O0O0._full_file,
                            OOOOOOO0O00O00O00)  #line:1748
                else:  #line:1749
                    if OO0O0O0000O0OO00O['upload_obs'] == 'obs':  #line:1750
                        O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                            O00O000O00OOO00OO['obs'],
                            O00O000O00OOO00OO['obs'])  #line:1751
                        O00O0O0O0O0OOOOO0 = True  #line:1752
                        print(O0000O00O00O0OOO0)  #line:1753
                if OO0O0OOO000O0OO00:  #line:1755
                    OO00OO0O0OO0O0O0O = ftp_main()  #line:1756
                    if not OO00OO0O0OO0O0O0O.upload_file_by_path(
                            O000000000O000OO0, OOO000000OO000000):  #line:1757
                        O0O0O0O0OOOO0O0O0._cloud_upload_not.append(
                            O000000000O000OO0)  #line:1758
                    if os.path.isfile(
                            O0O0O0OO00OOOO00O
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:
                        OO00OO0O0OO0O0O0O.upload_file_by_path(
                            O0O0O0OO00OOOO00O, O0O0O000O0OOOOOOO)  #line:1759
                    if os.path.isfile(
                            O0O0O0O0OOOO0O0O0._full_file
                    ) and OOO000OOOO0O0OO00 and OOOO0OO0O0000O0OO:  #line:1760
                        OOOOOOO0O00O00O00 = os.path.join(
                            '/www/wwwroot/ahongtest',
                            OOOOOOO0O00O00O00)  #line:1761
                        OO00OO0O0OO0O0O0O.upload_file_by_path(
                            O0O0O0O0OOOO0O0O0._full_file,
                            OOOOOOO0O00O00O00)  #line:1762
                else:  #line:1763
                    if OO0O0O0000O0OO00O['upload_ftp'] == 'ftp':  #line:1764
                        O0000O00O00O0OOO0 = '|-无法连接上{}，无法上传到{}'.format(
                            O00O000O00OOO00OO['ftp'],
                            O00O000O00OOO00OO['ftp'])  #line:1765
                        O00O0O0O0O0OOOOO0 = True  #line:1766
                        print(O0000O00O00O0OOO0)  #line:1767
        O0000O00O00O0OOO0 = '以下文件上传失败：{}'.format(
            O0O0O0O0OOOO0O0O0._cloud_upload_not)  #line:1768
        if O0O0O0O0OOOO0O0O0._cloud_upload_not or O00O0O0O0O0OOOOO0:  #line:1769
            O0O0O0O0OOOO0O0O0.send_failture_notification(
                O0000O00O00O0OOO0, target=OOO00000O0OO00O0O)  #line:1770
            if OO000OOOOO00OOO0O:
                public.writeFile(O0O0O0O0OOOO0O0O0._full_file,
                                 json.dumps(OO000OOOOO00OOO0O))  #line:1771
            return public.returnMsg(False, '增量备份失败！')  #line:1772
        public.M('mysqlbinlog_backup_setting').where(
            'id=?',
            OO0O0O0000O0OO00O['id']).update(OO0O0O0000O0OO00O)  #line:1773
        if not OOO0000OOO00O00OO:  #line:1774
            OO0OOOOO0OOO0O000 = 'inc'  #line:1775
            O0O0000000O0O0OO0 = json.loads(
                public.readFile(O0O0O0OO00OOOO00O))  #line:1776
            O0O0O0O0OOOO0O0O0.write_backups(OO0OOOOO0OOO0O000,
                                            O0O0000000O0O0OO0)  #line:1777
        if OO0O0O0000O0OO00O['upload_local'] == '' and os.path.isfile(
                O0O0O0O0OOOO0O0O0._inc_file):  #line:1778
            if os.path.isfile(O0O0O0O0OOOO0O0O0._full_file):  #line:1779
                O0O0O0O0OOOO0O0O0.clean_local_full_backups(
                    O0O0O0O0OOOO0O0O0._full_file)  #line:1780
            if os.path.isfile(O0O0O0O0OOOO0O0O0._inc_file):  #line:1782
                O0O0O0O0OOOO0O0O0.clean_local_inc_backups(
                    O0O0O0O0OOOO0O0O0._inc_file)  #line:1783
            print('|-用户设置不保留本地备份，已从本地服务器清理备份')  #line:1785
        return public.returnMsg(True, '执行备份任务成功！')  #line:1786

    def write_backups(O0O00O0OOO00O000O, O00OOO0O00O000OO0,
                      OO00OOO0OO0O0O0OO):  #line:1789
        ""  #line:1792
        OO0OO0OO00O0OOOOO = O0O00O0OOO00O000O._full_file if O00OOO0O00O000OO0 == 'full' else ''  #line:1793
        O00OO0OOO0OO0000O = O0O00O0OOO00O000O._inc_file if O00OOO0O00O000OO0 == 'full' else ''  #line:1794
        for O00O00O0O00O00OOO in OO00OOO0OO0O0O0OO:  #line:1795
            O0000OOO0OOOOO0O0 = O00O00O0O00O00OOO['full_name'].replace(
                '/www/backup', 'bt_backup')  #line:1796
            OOOOOO0O0O0OOO0O0 = {
                "sid": O0O00O0OOO00O000O._binlog_id,
                "size": O00O00O0O00O00OOO['size'],
                "type": O00OOO0O00O000OO0,
                "full_json": OO0OO0OO00O0OOOOO,
                "inc_json": O00OO0OOO0OO0000O,
                "local_name": O00O00O0O00O00OOO['full_name'],
                "ftp_name": '',
                "alioss_name": O0000OOO0OOOOO0O0,
                "txcos_name": O0000OOO0OOOOO0O0,
                "qiniu_name": O0000OOO0OOOOO0O0,
                "aws_name": '',
                "upyun_name": '',
                "obs_name": O0000OOO0OOOOO0O0,
                "bos_name": O0000OOO0OOOOO0O0,
                "gcloud_storage_name": '',
                "gdrive_name": '',
                "msonedrive_name": ''
            }  #line:1815
            if O00OOO0O00O000OO0 == 'full' and public.M(
                    'mysqlbinlog_backups').where(
                        'type=? AND sid=?',
                        (O00OOO0O00O000OO0,
                         O0O00O0OOO00O000O._binlog_id)).count():  #line:1817
                OO0OOOO000OO0OOO0 = public.M('mysqlbinlog_backups').where(
                    'type=? AND sid=?',
                    (O00OOO0O00O000OO0,
                     O0O00O0OOO00O000O._binlog_id)).getField('id')  #line:1818
                public.M('mysqlbinlog_backups').delete(
                    OO0OOOO000OO0OOO0)  #line:1819
            if O00OOO0O00O000OO0 == 'full':  #line:1821
                OOOOOOO0O0000O000 = public.M('mysqlbinlog_backups').where(
                    'type=? AND sid=?',
                    ('inc', O0O00O0OOO00O000O._binlog_id)).select()  #line:1822
                if OOOOOOO0O0000O000:  #line:1823
                    for O0000OOOOOOO0OOO0 in OOOOOOO0O0000O000:  #line:1824
                        if not O0000OOOOOOO0OOO0: continue  #line:1825
                        if 'id' in O0000OOOOOOO0OOO0:
                            public.M('mysqlbinlog_backups').delete(
                                O0000OOOOOOO0OOO0['id'])  #line:1826
            if not public.M('mysqlbinlog_backups').where(
                    'type=? AND local_name=? AND sid=?',
                (O00OOO0O00O000OO0, O00O00O0O00O00OOO['full_name'],
                 O0O00O0OOO00O000O._binlog_id)).count():  #line:1828
                public.M('mysqlbinlog_backups').insert(
                    OOOOOO0O0O0OOO0O0)  #line:1829
            else:  #line:1831
                OO0OOOO000OO0OOO0 = public.M('mysqlbinlog_backups').where(
                    'type=? AND local_name=? AND sid=?',
                    (O00OOO0O00O000OO0, O00O00O0O00O00OOO['full_name'],
                     O0O00O0OOO00O000O._binlog_id)).getField('id')  #line:1832
                public.M('mysqlbinlog_backups').where(
                    'id=?',
                    OO0OOOO000OO0OOO0).update(OOOOOO0O0O0OOO0O0)  #line:1833
            if O00OOO0O00O000OO0 == 'inc' and not public.M(
                    'mysqlbinlog_backups').where(
                        'type=? AND sid=?',
                        ('full',
                         O0O00O0OOO00O000O._binlog_id)).count():  #line:1835
                try:  #line:1836
                    OOOOO0000OO0O0OOO = json.loads(
                        public.readFile(
                            O0O00O0OOO00O000O._full_file))[0]  #line:1837
                except:  #line:1838
                    OOOOO0000OO0O0OOO = {}  #line:1839
                if OOOOO0000OO0O0OOO:  #line:1840
                    public.M('mysqlbinlog_backups').insert(
                        OOOOOO0O0O0OOO0O0)  #line:1841

    def get_tables_list(OOOOOO00O0O000OOO,
                        O0OOO0O0OOO0OOOO0,
                        type=False):  #line:1843
        ""  #line:1846
        O00000000OO0OO0OO = []  #line:1847
        for O0000O00O0O0O0OOO in O0OOO0O0OOO0OOOO0:  #line:1848
            if not O0000O00O0O0O0OOO: continue  #line:1849
            if type:  #line:1850
                if O0000O00O0O0O0OOO.get('type') != 'F': continue  #line:1851
            O00000000OO0OO0OO.append(O0000O00O0O0O0OOO['name'])  #line:1852
        return O00000000OO0OO0OO  #line:1853

    def clean_cloud_backups(O00OOOO00O0OO0OOO, OOOOO000O0O00O00O,
                            O00O00OO00000O0OO, OO0O000O0OO0OO00O,
                            OOO0000OOOO00OO0O):  #line:1856
        ""  #line:1859
        try:  #line:1860
            OOO00O000O0OO00O0 = json.loads(
                public.readFile(O00O00OO00000O0OO))[0]  #line:1861
        except:  #line:1862
            OOO00O000O0OO00O0 = []  #line:1863
        OO0OO0O000OO000OO = O0000O000O00000OO = O0OOOO00O0000OOO0 = O00OOO0OOOOOO0O0O = O00O0OOO0OO0O00OO = public.dict_obj(
        )  #line:1864
        OO0OO0O000OO000OO.path = OOOOO000O0O00O00O  #line:1865
        OO0O00OO0O0000OO0 = OO0O000O0OO0OO00O.get_list(
            OO0OO0O000OO000OO)  #line:1866
        if 'list' in OO0O00OO0O0000OO0:  #line:1867
            for O00O0OOO0O000O0O0 in OO0O00OO0O0000OO0['list']:  #line:1868
                if not O00O0OOO0O000O0O0: continue  #line:1869
                if O00O0OOO0O000O0O0['name'][-1] == '/':  #line:1870
                    O0000O000O00000OO.path = OOOOO000O0O00O00O + O00O0OOO0O000O0O0[
                        'name']  #line:1871
                    O0000O000O00000OO.filename = O00O0OOO0O000O0O0[
                        'name']  #line:1872
                    O00O0OOOOO00OOOO0 = OO0O000O0OO0OO00O.get_list(
                        O0000O000O00000OO)  #line:1873
                    O0000O000O00000OO.path = OOOOO000O0O00O00O  #line:1874
                    if O00O0OOOOO00OOOO0['list']:  #line:1876
                        for OO0OO00O000O0O0OO in O00O0OOOOO00OOOO0[
                                'list']:  #line:1877
                            O0OOOO00O0000OOO0.path = OOOOO000O0O00O00O + O00O0OOO0O000O0O0[
                                'name']  #line:1878
                            O0OOOO00O0000OOO0.filename = OO0OO00O000O0O0OO[
                                'name']  #line:1879
                            OO0O000O0OO0OO00O.remove_file(
                                O0OOOO00O0000OOO0)  #line:1880
                    else:  #line:1882
                        OO0O000O0OO0OO00O.remove_file(
                            O0000O000O00000OO)  #line:1883
                if not OOO00O000O0OO00O0: continue  #line:1885
                if O00O0OOO0O000O0O0['name'].split('.')[-1] in [
                        'zip', 'gz', 'json'
                ] and O00O0OOO0O000O0O0['name'] != OOO00O000O0OO00O0[
                        'name'] and O00O0OOO0O000O0O0[
                            'name'] != 'full_record.json':  #line:1886
                    O00OOO0OOOOOO0O0O.path = OOOOO000O0O00O00O  #line:1887
                    O00OOO0OOOOOO0O0O.filename = O00O0OOO0O000O0O0[
                        'name']  #line:1888
                    OO0O000O0OO0OO00O.remove_file(
                        O00OOO0OOOOOO0O0O)  #line:1889
                OOOO00O0O0O00O00O = False  #line:1890
                if 'dir' not in O00O0OOO0O000O0O0: continue  #line:1891
                if O00O0OOO0O000O0O0['dir'] == True:  #line:1892
                    try:  #line:1893
                        O00O0OO0OO00000OO = datetime.datetime.strptime(
                            O00O0OOO0O000O0O0['name'], '%Y-%m-%d')  #line:1894
                        OOOO00O0O0O00O00O = True  #line:1895
                    except:  #line:1896
                        pass  #line:1897
                O00O0O0000OOOO000 = ''  #line:1898
                if OOOO00O0O0O00O00O:
                    O00O0O0000OOOO000 = os.path.join(
                        OOOOO000O0O00O00O,
                        O00O0OOO0O000O0O0['name'])  #line:1899
                if O00O0O0000OOOO000:  #line:1900
                    O00O0OOO0OO0O00OO.path = O00O0O0000OOOO000  #line:1901
                    O00O0OOO0OO0O00OO.filename = ''  #line:1902
                    O00O0OOO0OO0O00OO.is_inc = True  #line:1903
                    OO0O000O0OO0OO00O.remove_file(
                        O00O0OOO0OO0O00OO)  #line:1904
        print('|-已从{}清理过期备份文件'.format(OOO0000OOOO00OO0O))  #line:1905

    def add_binlog_inc_backup_task(O0O0O00O0O00O0OO0, OO0O0O00O00O0O000,
                                   OO0O0OO00O00000OO):  #line:1908
        ""  #line:1914
        OOOOOO0OOOO0O0OOO = {
            "name":
            "[勿删]数据库增量备份[{}]".format(OO0O0O00O00O0O000['database_table']),
            "type":
            OO0O0O00O00O0O000['cron_type'],
            "where1":
            OO0O0O00O00O0O000['backup_cycle'],
            "hour":
            '',
            "minute":
            '0',
            "sType":
            'enterpriseBackup',
            "sName":
            OO0O0O00O00O0O000['backup_type'],
            "backupTo":
            OO0O0OO00O00000OO,
            "save":
            '1',
            "save_local":
            '1',
            "notice":
            OO0O0O00O00O0O000['notice'],
            "notice_channel":
            OO0O0O00O00O0O000['notice_channel'],
            "sBody":
            '{} {} --db_name {} --binlog_id {}'.format(
                O0O0O00O0O00O0OO0._python_path,
                O0O0O00O0O00O0OO0._binlogModel_py, O0O0O00O0O00O0OO0._db_name,
                str(OO0O0O00O00O0O000['id'])),
            "urladdress":
            '{}|{}|{}'.format(OO0O0O00O00O0O000['db_name'],
                              OO0O0O00O00O0O000['tb_name'],
                              OO0O0O00O00O0O000['id'])
        }  #line:1930
        import crontab  #line:1931
        O0OO0000000OO0000 = crontab.crontab().AddCrontab(
            OOOOOO0OOOO0O0OOO)  #line:1932
        if O0OO0000000OO0000 and "id" in O0OO0000000OO0000.keys():  #line:1933
            return True  #line:1934
        return False  #line:1935

    def create_table(OOO0OO00OOOO0OO0O):  #line:1937
        ""  #line:1942
        if not public.M('sqlite_master').where(
                'type=? AND name=?',
            ('table', 'mysqlbinlog_backup_setting')).count():  #line:1944
            public.M('').execute('''CREATE TABLE "mysqlbinlog_backup_setting" (
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
                                "add_time" INTEGER);''')  #line:1979
        if not public.M('sqlite_master').where(
                'type=? AND name=?',
            ('table', 'mysqlbinlog_backups')).count():  #line:1982
            public.M('').execute('''CREATE TABLE "mysqlbinlog_backups" (
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
                                "where_4" TEXT DEFAULT '');''')  #line:2005

    def add_mysqlbinlog_backup_setting(O0OOO00O0O00OOO0O,
                                       O0OOOO0O000OO0OO0):  #line:2008
        ""  #line:2014
        public.set_module_logs('binlog',
                               'add_mysqlbinlog_backup_setting')  #line:2015
        if not O0OOOO0O000OO0OO0.get('datab_name/str', 0):
            return public.returnMsg(False, '当前没有数据库，不能添加！')  #line:2016
        if O0OOOO0O000OO0OO0.datab_name in [0, '0']:
            return public.returnMsg(False, '当前没有数据库，不能添加！')  #line:2017
        if not O0OOOO0O000OO0OO0.get('backup_cycle/d', 0) > 0:
            return public.returnMsg(False, '备份周期不正确，只能为正整数！')  #line:2018
        OO00O000O0O0OO0O0 = OO00OOO0O000OO0O0 = {}  #line:2022
        OOOOOOOO0OO000OO0 = O0OOO00O0O00OOO0O.get_binlog_status()  #line:2023
        if OOOOOOOO0OO000OO0['status'] == False:
            return public.returnMsg(
                False, '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')  #line:2024
        O0OOO00O0O00OOO0O._db_name = OO00OOO0O000OO0O0[
            'db_name'] = O0OOOO0O000OO0OO0.datab_name  #line:2025
        O00O0OOO000OO0OOO = 'databases' if O0OOOO0O000OO0OO0.backup_type == 'databases' else 'tables'  #line:2026
        O0OOO00O0O00OOO0O._tables = '' if 'table_name' not in O0OOOO0O000OO0OO0 else O0OOOO0O000OO0OO0.table_name  #line:2027
        OO00OO00000O00O0O = False  #line:2028
        O0000O0000O000OO0 = ''  #line:2030
        OOO00O0O0OO0OO0O0 = ''  #line:2031
        if O0OOO00O0O00OOO0O._tables:  #line:2032
            O0000O0000O000OO0 = public.M('mysqlbinlog_backup_setting').where(
                'db_name=? and backup_type=? and tb_name=?',
                (O0OOOO0O000OO0OO0.datab_name, O00O0OOO000OO0OOO,
                 O0OOO00O0O00OOO0O._tables)).find()  #line:2033
            if O0000O0000O000OO0:  #line:2034
                OO00O000O0O0OO0O0 = O0000O0000O000OO0  #line:2035
                OO00OO00000O00O0O = True  #line:2036
                OOO00O0O0OO0OO0O0 = public.M('crontab').where(
                    'sBody=?', '{} {} --db_name {} --binlog_id {}'.format(
                        O0OOO00O0O00OOO0O._python_path,
                        O0OOO00O0O00OOO0O._binlogModel_py,
                        O0000O0000O000OO0['db_name'],
                        str(O0000O0000O000OO0['id']))).getField(
                            'id')  #line:2037
                if OOO00O0O0OO0OO0O0:  #line:2038
                    return public.returnMsg(
                        False, '指定的数据库或者表已经存在备份，不能重复添加！')  #line:2039
        else:  #line:2040
            O0000O0000O000OO0 = public.M('mysqlbinlog_backup_setting').where(
                'db_name=? and backup_type=?',
                (O0OOOO0O000OO0OO0.datab_name,
                 O00O0OOO000OO0OOO)).find()  #line:2041
            if O0000O0000O000OO0:  #line:2042
                OO00O000O0O0OO0O0 = O0000O0000O000OO0  #line:2043
                OO00OO00000O00O0O = True  #line:2044
                OOO00O0O0OO0OO0O0 = public.M('crontab').where(
                    'sBody=?', '{} {} --db_name {} --binlog_id {}'.format(
                        O0OOO00O0O00OOO0O._python_path,
                        O0OOO00O0O00OOO0O._binlogModel_py,
                        O0000O0000O000OO0['db_name'],
                        str(O0000O0000O000OO0['id']))).getField(
                            'id')  #line:2045
                if OOO00O0O0OO0OO0O0:  #line:2046
                    return public.returnMsg(
                        False, '指定的数据库或者表已经存在备份，不能重复添加！')  #line:2047
        OO00O000O0O0OO0O0[
            'database_table'] = O0OOOO0O000OO0OO0.datab_name if O0OOOO0O000OO0OO0.backup_type == 'databases' else O0OOOO0O000OO0OO0.datab_name + '---' + O0OOOO0O000OO0OO0.table_name  #line:2048
        OO00O000O0O0OO0O0['backup_type'] = O00O0OOO000OO0OOO  #line:2049
        OO00O000O0O0OO0O0[
            'backup_cycle'] = O0OOOO0O000OO0OO0.backup_cycle  #line:2050
        OO00O000O0O0OO0O0[
            'cron_type'] = O0OOOO0O000OO0OO0.cron_type  #line:2051
        OO00O000O0O0OO0O0['notice'] = O0OOOO0O000OO0OO0.notice  #line:2052
        if O0OOOO0O000OO0OO0.notice == '1':  #line:2053
            OO00O000O0O0OO0O0[
                'notice_channel'] = O0OOOO0O000OO0OO0.notice_channel  #line:2054
        else:  #line:2055
            OO00O000O0O0OO0O0['notice_channel'] = ''  #line:2056
        O00000OO0O00000O0 = public.format_date()  #line:2057
        if O0000O0000O000OO0:
            OO00O000O0O0OO0O0['zip_password'] = O0000O0000O000OO0[
                'zip_password']  #line:2058
        else:
            OO00O000O0O0OO0O0[
                'zip_password'] = O0OOOO0O000OO0OO0.zip_password  #line:2059
        OO00O000O0O0OO0O0['start_backup_time'] = O00000OO0O00000O0  #line:2060
        OO00O000O0O0OO0O0['end_backup_time'] = O00000OO0O00000O0  #line:2061
        OO00O000O0O0OO0O0[
            'last_excute_backup_time'] = O00000OO0O00000O0  #line:2062
        OO00O000O0O0OO0O0['table_list'] = '|'.join(
            O0OOO00O0O00OOO0O.get_tables_list(
                O0OOO00O0O00OOO0O.get_tables()))  #line:2063
        OO00O000O0O0OO0O0['cron_status'] = 1  #line:2064
        OO00O000O0O0OO0O0['sync_remote_status'] = 0  #line:2065
        OO00O000O0O0OO0O0['sync_remote_time'] = 0  #line:2066
        OO00O000O0O0OO0O0['add_time'] = O00000OO0O00000O0  #line:2067
        OO00O000O0O0OO0O0['db_name'] = O0OOOO0O000OO0OO0.datab_name  #line:2068
        OO00O000O0O0OO0O0[
            'tb_name'] = O0OOO00O0O00OOO0O._tables = '' if 'table_name' not in O0OOOO0O000OO0OO0 else O0OOOO0O000OO0OO0.table_name  #line:2069
        OO00O000O0O0OO0O0['save_path'] = O0OOO00O0O00OOO0O.splicing_save_path(
        )  #line:2070
        OO00O000O0O0OO0O0['temp_path'] = ''  #line:2071
        OOO00OO0OO00O0OOO = '|'  #line:2075
        O000O0O0O00O0O0O0 = O0OO0O00O0OO0OOOO = O00000OOOO0OOOO0O = OOOOO0000OOO00O0O = OO00OOO00OO00O0O0 = O0O0OOO0OO00000O0 = O0OOO00O0000OOO0O = OOOOOOOO0O000000O = O00000O000O00000O = OOO0O0OOOO00OOO00 = '|'  #line:2076
        OO000O0O00OOOOOO0 = ''  #line:2077
        if 'upload_localhost' in O0OOOO0O000OO0OO0:  #line:2078
            OO00O000O0O0OO0O0[
                'upload_local'] = O0OOOO0O000OO0OO0.upload_localhost  #line:2079
            OOO00OO0OO00O0OOO = 'localhost|'  #line:2080
        else:  #line:2081
            OO00O000O0O0OO0O0['upload_local'] = ''  #line:2082
        if 'upload_alioss' in O0OOOO0O000OO0OO0:  #line:2083
            OO00O000O0O0OO0O0[
                'upload_alioss'] = O0OOOO0O000OO0OO0.upload_alioss  #line:2084
            O000O0O0O00O0O0O0 = 'alioss|'  #line:2085
        else:  #line:2086
            OO00O000O0O0OO0O0['upload_alioss'] = ''  #line:2087
        if 'upload_ftp' in O0OOOO0O000OO0OO0:  #line:2088
            OO00O000O0O0OO0O0[
                'upload_ftp'] = O0OOOO0O000OO0OO0.upload_ftp  #line:2089
            O0OO0O00O0OO0OOOO = 'ftp|'  #line:2090
        else:  #line:2091
            OO00O000O0O0OO0O0['upload_ftp'] = ''  #line:2092
        if 'upload_txcos' in O0OOOO0O000OO0OO0:  #line:2093
            OO00O000O0O0OO0O0[
                'upload_txcos'] = O0OOOO0O000OO0OO0.upload_txcos  #line:2094
            O00000OOOO0OOOO0O = 'txcos|'  #line:2095
        else:  #line:2096
            OO00O000O0O0OO0O0['upload_txcos'] = ''  #line:2097
        if 'upload_qiniu' in O0OOOO0O000OO0OO0:  #line:2098
            OO00O000O0O0OO0O0[
                'upload_qiniu'] = O0OOOO0O000OO0OO0.upload_qiniu  #line:2099
            OOOOO0000OOO00O0O = 'qiniu|'  #line:2100
        else:  #line:2101
            OO00O000O0O0OO0O0['upload_qiniu'] = ''  #line:2102
        if 'upload_aws' in O0OOOO0O000OO0OO0:  #line:2103
            OO00O000O0O0OO0O0[
                'upload_aws'] = O0OOOO0O000OO0OO0.upload_aws  #line:2104
            OO00OOO00OO00O0O0 = 'aws|'  #line:2105
        else:  #line:2106
            OO00O000O0O0OO0O0['upload_aws'] = ''  #line:2107
        if 'upload_upyun' in O0OOOO0O000OO0OO0:  #line:2108
            OO00O000O0O0OO0O0[
                'upload_upyun'] = O0OOOO0O000OO0OO0.upload_upyun  #line:2109
            O0O0OOO0OO00000O0 = 'upyun|'  #line:2110
        else:  #line:2111
            OO00O000O0O0OO0O0['upload_upyun'] = ''  #line:2112
        if 'upload_obs' in O0OOOO0O000OO0OO0:  #line:2113
            OO00O000O0O0OO0O0[
                'upload_obs'] = O0OOOO0O000OO0OO0.upload_obs  #line:2114
            O0OOO00O0000OOO0O = 'obs|'  #line:2115
        else:  #line:2116
            OO00O000O0O0OO0O0['upload_obs'] = ''  #line:2117
        if 'upload_bos' in O0OOOO0O000OO0OO0:  #line:2118
            OO00O000O0O0OO0O0[
                'upload_bos'] = O0OOOO0O000OO0OO0.upload_bos  #line:2119
            OOOOOOOO0O000000O = 'bos|'  #line:2120
        else:  #line:2121
            OO00O000O0O0OO0O0['upload_bos'] = ''  #line:2122
        if 'upload_gcloud_storage' in O0OOOO0O000OO0OO0:  #line:2123
            OO00O000O0O0OO0O0[
                'upload_gcloud_storage'] = O0OOOO0O000OO0OO0.upload_gcloud_storage  #line:2124
            O00000O000O00000O = 'gcloud_storage|'  #line:2125
        else:  #line:2126
            OO00O000O0O0OO0O0['upload_gcloud_storage'] = ''  #line:2127
        if 'upload_gdrive' in O0OOOO0O000OO0OO0:  #line:2128
            OO00O000O0O0OO0O0[
                'upload_gdrive'] = O0OOOO0O000OO0OO0.upload_gdrive  #line:2129
            OOO0O0OOOO00OOO00 = 'gdrive|'  #line:2130
        else:  #line:2131
            OO00O000O0O0OO0O0['upload_gdrive'] = ''  #line:2132
        if 'upload_msonedrive' in O0OOOO0O000OO0OO0:  #line:2133
            OO00O000O0O0OO0O0[
                'upload_msonedrive'] = O0OOOO0O000OO0OO0.upload_msonedrive  #line:2134
            OO000O0O00OOOOOO0 = 'msonedrive'  #line:2135
        else:  #line:2136
            OO00O000O0O0OO0O0['upload_msonedrive'] = ''  #line:2137
        OOO00OO0OO00O0OOO = OOO00OO0OO00O0OOO + O000O0O0O00O0O0O0 + O0OO0O00O0OO0OOOO + O00000OOOO0OOOO0O + OOOOO0000OOO00O0O + OO00OOO00OO00O0O0 + O0O0OOO0OO00000O0 + O0OOO00O0000OOO0O + OOOOOOOO0O000000O + O00000O000O00000O + OOO0O0OOOO00OOO00 + OO000O0O00OOOOOO0  #line:2138
        if not OO00OO00000O00O0O:  #line:2139
            OO00O000O0O0OO0O0['id'] = public.M(
                'mysqlbinlog_backup_setting').insert(
                    OO00O000O0O0OO0O0)  #line:2140
        else:  #line:2141
            public.M('mysqlbinlog_backup_setting').where(
                'id=?', int(OO00O000O0O0OO0O0['id'])).update(
                    OO00O000O0O0OO0O0)  #line:2142
            time.sleep(0.01)  #line:2143
        if not OOO00O0O0OO0OO0O0:  #line:2145
            O0OOO00O0O00OOO0O.add_binlog_inc_backup_task(
                OO00O000O0O0OO0O0, OOO00OO0OO00O0OOO)  #line:2146
        return public.returnMsg(True, '添加成功!')  #line:2147

    def modify_mysqlbinlog_backup_setting(O00O0OO0OOO0OOOO0,
                                          OO0OOOO0OO0000OOO):  #line:2149
        ""  #line:2155
        public.set_module_logs('binlog',
                               'modify_mysqlbinlog_backup_setting')  #line:2156
        if 'backup_id' not in OO0OOOO0OO0000OOO:
            return public.returnMsg(False, '错误的参数!')  #line:2157
        if not OO0OOOO0OO0000OOO.get('backup_cycle/d', 0) > 0:
            return public.returnMsg(False, '备份周期不正确，只能为正整数！')  #line:2158
        O0000OOOO0O0O0000 = O00O0OO0OOO0OOOO0.get_binlog_status()  #line:2160
        if O0000OOOO0O0O0000['status'] == False:
            return public.returnMsg(
                False, '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')  #line:2161
        OOO0OOO00OO00O00O = public.M('mysqlbinlog_backup_setting').where(
            'id=?', OO0OOOO0OO0000OOO.backup_id).find()  #line:2163
        OOO0OOO00OO00O00O[
            'backup_cycle'] = OO0OOOO0OO0000OOO.backup_cycle  #line:2164
        OOO0OOO00OO00O00O['notice'] = OO0OOOO0OO0000OOO.notice  #line:2165
        O00O0OO0OOO0OOOO0._db_name = OOO0OOO00OO00O00O['db_name']  #line:2166
        if OO0OOOO0OO0000OOO.notice == '1':  #line:2167
            OOO0OOO00OO00O00O[
                'notice_channel'] = OO0OOOO0OO0000OOO.notice_channel  #line:2168
        else:  #line:2169
            OOO0OOO00OO00O00O['notice_channel'] = ''  #line:2170
        O0OOO0000O000O0OO = '|'  #line:2172
        O0O00OO00OO0000OO = O00O00000O00OOOO0 = O0OO0O000O000OO00 = O00000OOO0000O0OO = OO00000O0O0O00O00 = OOOO0O0OO00O00O00 = O00000OO00000O000 = OOOOOO0OO000O00O0 = O0OO00O0000OO0000 = OO000O00O00OOOO00 = '|'  #line:2173
        OOOO00O000O00000O = ''  #line:2174
        if 'upload_localhost' not in OO0OOOO0OO0000OOO:  #line:2175
            OOO0OOO00OO00O00O['upload_local'] = ''  #line:2176
        else:  #line:2177
            OOO0OOO00OO00O00O[
                'upload_local'] = OO0OOOO0OO0000OOO.upload_localhost  #line:2178
            O0OOO0000O000O0OO = 'localhost|'  #line:2179
        if 'upload_alioss' not in OO0OOOO0OO0000OOO:  #line:2180
            OOO0OOO00OO00O00O['upload_alioss'] = ''  #line:2181
        else:  #line:2182
            OOO0OOO00OO00O00O[
                'upload_alioss'] = OO0OOOO0OO0000OOO.upload_alioss  #line:2183
            O0O00OO00OO0000OO = 'alioss|'  #line:2184
        if 'upload_ftp' not in OO0OOOO0OO0000OOO:  #line:2185
            OOO0OOO00OO00O00O['upload_ftp'] = ''  #line:2186
        else:  #line:2187
            OOO0OOO00OO00O00O[
                'upload_ftp'] = OO0OOOO0OO0000OOO.upload_ftp  #line:2188
            O00O00000O00OOOO0 = 'ftp|'  #line:2189
        if 'upload_txcos' not in OO0OOOO0OO0000OOO:  #line:2190
            OOO0OOO00OO00O00O['upload_txcos'] = ''  #line:2191
        else:  #line:2192
            OOO0OOO00OO00O00O[
                'upload_txcos'] = OO0OOOO0OO0000OOO.upload_txcos  #line:2193
            O0OO0O000O000OO00 = 'txcos|'  #line:2194
        if 'upload_qiniu' not in OO0OOOO0OO0000OOO:  #line:2195
            OOO0OOO00OO00O00O['upload_qiniu'] = ''  #line:2196
        else:  #line:2197
            OOO0OOO00OO00O00O[
                'upload_qiniu'] = OO0OOOO0OO0000OOO.upload_qiniu  #line:2198
            O00000OOO0000O0OO = 'qiniu|'  #line:2199
        if 'upload_aws' not in OO0OOOO0OO0000OOO:  #line:2200
            OOO0OOO00OO00O00O['upload_aws'] = ''  #line:2201
        else:  #line:2202
            OOO0OOO00OO00O00O[
                'upload_aws'] = OO0OOOO0OO0000OOO.upload_aws  #line:2203
            OO00000O0O0O00O00 = 'aws|'  #line:2204
        if 'upload_upyun' not in OO0OOOO0OO0000OOO:  #line:2205
            OOO0OOO00OO00O00O['upload_upyun'] = ''  #line:2206
        else:  #line:2207
            OOO0OOO00OO00O00O[
                'upload_upyun'] = OO0OOOO0OO0000OOO.upload_upyun  #line:2208
            OOOO0O0OO00O00O00 = 'upyun|'  #line:2209
        if 'upload_obs' not in OO0OOOO0OO0000OOO:  #line:2210
            OOO0OOO00OO00O00O['upload_obs'] = ''  #line:2211
        else:  #line:2212
            OOO0OOO00OO00O00O[
                'upload_obs'] = OO0OOOO0OO0000OOO.upload_obs  #line:2213
            O00000OO00000O000 = 'obs|'  #line:2214
        if 'upload_bos' not in OO0OOOO0OO0000OOO:  #line:2215
            OOO0OOO00OO00O00O['upload_bos'] = ''  #line:2216
        else:  #line:2217
            OOO0OOO00OO00O00O[
                'upload_bos'] = OO0OOOO0OO0000OOO.upload_bos  #line:2218
            OOOOOO0OO000O00O0 = 'bos|'  #line:2219
        if 'upload_gcloud_storage' not in OO0OOOO0OO0000OOO:  #line:2220
            OOO0OOO00OO00O00O['upload_gcloud_storage'] = ''  #line:2221
        else:  #line:2222
            OOO0OOO00OO00O00O[
                'upload_gcloud_storage'] = OO0OOOO0OO0000OOO.upload_gcloud_storage  #line:2223
            O0OO00O0000OO0000 = 'gcloud_storage|'  #line:2224
        if 'upload_gdrive' not in OO0OOOO0OO0000OOO:  #line:2225
            OOO0OOO00OO00O00O['upload_gdrive'] = ''  #line:2226
        else:  #line:2227
            OOO0OOO00OO00O00O[
                'upload_gdrive'] = OO0OOOO0OO0000OOO.upload_gdrive  #line:2228
            OO000O00O00OOOO00 = 'gdrive|'  #line:2229
        if 'upload_msonedrive' not in OO0OOOO0OO0000OOO:  #line:2230
            OOO0OOO00OO00O00O['upload_msonedrive'] = ''  #line:2231
        else:  #line:2232
            OOO0OOO00OO00O00O[
                'upload_msonedrive'] = OO0OOOO0OO0000OOO.upload_msonedrive  #line:2233
            OOOO00O000O00000O = 'msonedrive'  #line:2234
        O0OOO0000O000O0OO = O0OOO0000O000O0OO + O0O00OO00OO0000OO + O00O00000O00OOOO0 + O0OO0O000O000OO00 + O00000OOO0000O0OO + OO00000O0O0O00O00 + OOOO0O0OO00O00O00 + O00000OO00000O000 + OOOOOO0OO000O00O0 + O0OO00O0000OO0000 + OO000O00O00OOOO00 + OOOO00O000O00000O  #line:2235
        public.M('mysqlbinlog_backup_setting').where(
            'id=?', int(OO0OOOO0OO0000OOO.backup_id)).update(
                OOO0OOO00OO00O00O)  #line:2236
        if 'cron_id' in OO0OOOO0OO0000OOO:  #line:2238
            if OO0OOOO0OO0000OOO.cron_id:  #line:2239
                OO0O0O0O0OOO00O00 = {
                    "id":
                    OO0OOOO0OO0000OOO.cron_id,
                    "name":
                    public.M('crontab').where(
                        "id=?",
                        (OO0OOOO0OO0000OOO.cron_id, )).getField('name'),
                    "type":
                    OOO0OOO00OO00O00O['cron_type'],
                    "where1":
                    OOO0OOO00OO00O00O['backup_cycle'],
                    "hour":
                    '',
                    "minute":
                    '0',
                    "sType":
                    'enterpriseBackup',
                    "sName":
                    OOO0OOO00OO00O00O['backup_type'],
                    "backupTo":
                    O0OOO0000O000O0OO,
                    "save":
                    OOO0OOO00OO00O00O['notice'],
                    "save_local":
                    '1',
                    "notice":
                    OOO0OOO00OO00O00O['notice'],
                    "notice_channel":
                    OOO0OOO00OO00O00O['notice_channel'],
                    "sBody":
                    public.M('crontab').where(
                        "id=?",
                        (OO0OOOO0OO0000OOO.cron_id, )).getField('sBody'),
                    "urladdress":
                    '{}|{}|{}'.format(OOO0OOO00OO00O00O['db_name'],
                                      OOO0OOO00OO00O00O['tb_name'],
                                      OOO0OOO00OO00O00O['id'])
                }  #line:2256
                import crontab  #line:2257
                crontab.crontab().modify_crond(OO0O0O0O0OOO00O00)  #line:2258
                return public.returnMsg(True, '编辑成功!')  #line:2259
            else:  #line:2260
                O00O0OO0OOO0OOOO0.add_binlog_inc_backup_task(
                    OOO0OOO00OO00O00O, O0OOO0000O000O0OO)  #line:2261
                return public.returnMsg(True, '已恢复计划任务!')  #line:2262
        else:  #line:2263
            O00O0OO0OOO0OOOO0.add_binlog_inc_backup_task(
                OOO0OOO00OO00O00O, O0OOO0000O000O0OO)  #line:2264
            return public.returnMsg(True, '已恢复计划任务!')  #line:2265

    def delete_mysql_binlog_setting(O0O0000O0O0000OOO,
                                    O0O00OO0OO0O0O0O0):  #line:2267
        ""  #line:2272
        public.set_module_logs('binlog',
                               'delete_mysql_binlog_setting')  #line:2273
        if 'backup_id' not in O0O00OO0OO0O0O0O0 and 'cron_id' not in O0O00OO0OO0O0O0O0:
            return public.returnMsg(False, '不存在此增量备份任务!')  #line:2274
        OO0OO0O0OO0O0OOO0 = ''  #line:2275
        if O0O00OO0OO0O0O0O0.backup_id:  #line:2276
            OO0OO0O0OO0O0OOO0 = public.M('mysqlbinlog_backup_setting').where(
                'id=?', (O0O00OO0OO0O0O0O0.backup_id, )).find()  #line:2277
            if OO0OO0O0OO0O0OOO0:  #line:2278
                O0O0000O0O0000OOO._save_default_path = OO0OO0O0OO0O0OOO0[
                    'save_path']  #line:2279
                O0O0000O0O0000OOO._db_name = OO0OO0O0OO0O0OOO0[
                    'db_name']  #line:2280
        if 'cron_id' in O0O00OO0OO0O0O0O0 and O0O00OO0OO0O0O0O0.cron_id:  #line:2282
            if public.M('crontab').where(
                    'id=?', (O0O00OO0OO0O0O0O0.cron_id, )).count():  #line:2283
                O0O0O000OOOOOOO0O = {
                    "id": O0O00OO0OO0O0O0O0.cron_id
                }  #line:2284
                import crontab  #line:2285
                crontab.crontab().DelCrontab(O0O0O000OOOOOOO0O)  #line:2286
        if O0O00OO0OO0O0O0O0.type == 'manager' and OO0OO0O0OO0O0OOO0:  #line:2288
            if public.M('mysqlbinlog_backup_setting').where(
                    'id=?',
                (O0O00OO0OO0O0O0O0.backup_id, )).count():  #line:2289
                public.M('mysqlbinlog_backup_setting').where(
                    'id=?',
                    (O0O00OO0OO0O0O0O0.backup_id, )).delete()  #line:2290
            O00OO00OOO000OOOO = OO0OO0O0OO0O0OOO0[
                'save_path'] + 'full_record.json'  #line:2291
            OO00000OOOO00000O = OO0OO0O0OO0O0OOO0[
                'save_path'] + 'inc_record.json'  #line:2292
            if os.path.isfile(O00OO00OOO000OOOO):
                O0O0000O0O0000OOO.clean_local_full_backups(
                    O00OO00OOO000OOOO)  #line:2293
            if os.path.isfile(OO00000OOOO00000O):
                O0O0000O0O0000OOO.clean_local_inc_backups(
                    OO00000OOOO00000O)  #line:2294
            OO0000O0O0OOO0OOO = public.M('mysqlbinlog_backups').where(
                'sid=?', O0O00OO0OO0O0O0O0.backup_id).select()  #line:2295
            for O0O00O0OO0O0OO000 in OO0000O0O0OOO0OOO:  #line:2296
                if not O0O00O0OO0O0OO000: continue  #line:2297
                if 'id' not in O0O00O0OO0O0OO000: continue  #line:2298
                public.M('mysqlbinlog_backups').delete(
                    O0O00O0OO0O0OO000['id'])  #line:2299
        return public.returnMsg(True, '删除成功')  #line:2300

    def get_inc_size(O0O0O00OOOO00OO0O, O00000000O0O0O00O):  #line:2302
        ""  #line:2308
        O0O0O0OO0O00OO00O = 0  #line:2309
        if os.path.isfile(O00000000O0O0O00O):  #line:2310
            try:  #line:2311
                O000000O0000OOOOO = json.loads(
                    public.readFile(O00000000O0O0O00O))  #line:2312
                for O0O00O0000O0000OO in O000000O0000OOOOO:  #line:2313
                    O0O0O0OO0O00OO00O += int(
                        O0O00O0000O0000OO['size'])  #line:2314
            except:  #line:2315
                O0O0O0OO0O00OO00O = 0  #line:2316
        return O0O0O0OO0O00OO00O  #line:2317

    def get_time_size(OO00OO00OO0O00OOO, OOO000OOOO00O000O,
                      OO0O0O0OOO0O000O0):  #line:2319
        ""  #line:2324
        O0OO0000O0O00OOOO = json.loads(
            public.readFile(OOO000OOOO00O000O))[0]  #line:2326
        OO0O0O0OOO0O000O0['start_time'] = O0OO0000O0O00OOOO['time']  #line:2327
        if 'end_time' in O0OO0000O0O00OOOO:  #line:2328
            OO0O0O0OOO0O000O0['end_time'] = O0OO0000O0O00OOOO[
                'end_time']  #line:2329
            OO0O0O0OOO0O000O0['excute_time'] = O0OO0000O0O00OOOO[
                'end_time']  #line:2330
        else:  #line:2331
            OO0O0O0OOO0O000O0['end_time'] = O0OO0000O0O00OOOO[
                'time']  #line:2332
            OO0O0O0OOO0O000O0['excute_time'] = O0OO0000O0O00OOOO[
                'time']  #line:2333
        OO0O0O0OOO0O000O0['full_size'] = O0OO0000O0O00OOOO['size']  #line:2334
        return OO0O0O0OOO0O000O0  #line:2335

    def get_database_info(O0O0O000OOOOOOOO0, get=None):  #line:2337
        ""  #line:2342
        O00OOOO00000OOOOO = O0O0O000OOOOOOOO0.get_databases()  #line:2343
        OOO00OO00000OO00O = {}  #line:2344
        O0OO00O00O0O0O000 = []  #line:2345
        O00OO0OOOOO0OO00O = []  #line:2346
        if O00OOOO00000OOOOO:  #line:2347
            for O000O0O00OO0O0OO0 in O00OOOO00000OOOOO:  #line:2348
                if not O000O0O00OO0O0OO0: continue  #line:2349
                OO00OOOO0O0OO0OO0 = {}  #line:2350
                O0O0O000OOOOOOOO0._db_name = OO00OOOO0O0OO0OO0[
                    'name'] = O000O0O00OO0O0OO0['name']  #line:2351
                O0OOOOOOO00O0O000 = O0O0O000OOOOOOOO0._save_default_path + O000O0O00OO0O0OO0[
                    'name'] + '/databases/'  #line:2352
                O00O0O0OO0O0OOO00 = O0O0O000OOOOOOOO0._save_default_path + O000O0O00OO0O0OO0[
                    'name'] + '/tables/'  #line:2353
                O00O00OO00OO00OOO = O0OOOOOOO00O0O000 + 'full_record.json'  #line:2354
                OO0O0OO0O0OO000O0 = O0OOOOOOO00O0O000 + 'inc_record.json'  #line:2355
                OO00OOOO0O0OO0OO0['inc_size'] = 0 if not os.path.isfile(
                    OO0O0OO0O0OO000O0) else O0O0O000OOOOOOOO0.get_inc_size(
                        OO0O0OO0O0OO000O0)  #line:2356
                OOOO000O000OOO0OO = public.M(
                    'mysqlbinlog_backup_setting').where(
                        'db_name=? and backup_type=?',
                        (str(O000O0O00OO0O0OO0['name']),
                         'databases')).find()  #line:2358
                if OOOO000O000OOO0OO:  #line:2359
                    OO00OOOO0O0OO0OO0['cron_id'] = public.M('crontab').where(
                        'name=?', '[勿删]数据库增量备份[{}]'.format(
                            OOOO000O000OOO0OO['db_name'])).getField(
                                'id')  #line:2360
                    OO00OOOO0O0OO0OO0['backup_id'] = OOOO000O000OOO0OO[
                        'id']  #line:2361
                    OO00OOOO0O0OO0OO0['upload_localhost'] = OOOO000O000OOO0OO[
                        'upload_local']  #line:2362
                    OO00OOOO0O0OO0OO0['upload_alioss'] = OOOO000O000OOO0OO[
                        'upload_alioss']  #line:2363
                    OO00OOOO0O0OO0OO0['upload_ftp'] = OOOO000O000OOO0OO[
                        'upload_ftp']  #line:2364
                    OO00OOOO0O0OO0OO0['upload_txcos'] = OOOO000O000OOO0OO[
                        'upload_txcos']  #line:2365
                    OO00OOOO0O0OO0OO0['upload_qiniu'] = OOOO000O000OOO0OO[
                        'upload_qiniu']  #line:2366
                    OO00OOOO0O0OO0OO0['upload_obs'] = OOOO000O000OOO0OO[
                        'upload_obs']  #line:2367
                    OO00OOOO0O0OO0OO0['upload_bos'] = OOOO000O000OOO0OO[
                        'upload_bos']  #line:2368
                    OO00OOOO0O0OO0OO0['backup_cycle'] = OOOO000O000OOO0OO[
                        'backup_cycle']  #line:2369
                    OO00OOOO0O0OO0OO0['notice'] = OOOO000O000OOO0OO[
                        'notice']  #line:2370
                    OO00OOOO0O0OO0OO0['notice_channel'] = OOOO000O000OOO0OO[
                        'notice_channel']  #line:2371
                    OO00OOOO0O0OO0OO0['zip_password'] = OOOO000O000OOO0OO[
                        'zip_password']  #line:2372
                    OO00OOOO0O0OO0OO0['start_time'] = OOOO000O000OOO0OO[
                        'start_backup_time']  #line:2374
                    OO00OOOO0O0OO0OO0['end_time'] = OOOO000O000OOO0OO[
                        'end_backup_time']  #line:2375
                    OO00OOOO0O0OO0OO0['excute_time'] = OOOO000O000OOO0OO[
                        'last_excute_backup_time']  #line:2376
                else:  #line:2377
                    OO00OOOO0O0OO0OO0['cron_id'] = OO00OOOO0O0OO0OO0[
                        'backup_id'] = OO00OOOO0O0OO0OO0[
                            'notice'] = OO00OOOO0O0OO0OO0[
                                'upload_alioss'] = OO00OOOO0O0OO0OO0[
                                    'backup_cycle'] = OO00OOOO0O0OO0OO0[
                                        'zip_password'] = None  #line:2378
                    OO00OOOO0O0OO0OO0['upload_localhost'] = OO00OOOO0O0OO0OO0[
                        'upload_alioss'] = OO00OOOO0O0OO0OO0[
                            'upload_ftp'] = OO00OOOO0O0OO0OO0[
                                'upload_txcos'] = OO00OOOO0O0OO0OO0[
                                    'upload_qiniu'] = OO00OOOO0O0OO0OO0[
                                        'upload_obs'] = OO00OOOO0O0OO0OO0[
                                            'upload_bos'] = ''  #line:2379
                if os.path.isfile(O00O00OO00OO00OOO):  #line:2381
                    OO00OOOO0O0OO0OO0 = O0O0O000OOOOOOOO0.get_time_size(
                        O00O00OO00OO00OOO, OO00OOOO0O0OO0OO0)  #line:2382
                    if OOOO000O000OOO0OO:
                        OO00OOOO0O0OO0OO0['excute_time'] = OOOO000O000OOO0OO[
                            'last_excute_backup_time']  #line:2383
                    OO00OOOO0O0OO0OO0['full_size'] = public.to_size(
                        OO00OOOO0O0OO0OO0['full_size'] +
                        OO00OOOO0O0OO0OO0['inc_size'])  #line:2384
                    O0OO00O00O0O0O000.append(OO00OOOO0O0OO0OO0)  #line:2385
                else:  #line:2387
                    if OOOO000O000OOO0OO:  #line:2388
                        OO00OOOO0O0OO0OO0['full_size'] = 0  #line:2389
                        O0O000O0OOOOO000O = public.M(
                            'mysqlbinlog_backups').where(
                                'sid=?',
                                OOOO000O000OOO0OO['id']).select()  #line:2391
                        for OO0OO0O00OO000000 in O0O000O0OOOOO000O:  #line:2392
                            if not OO0OO0O00OO000000: continue  #line:2393
                            if 'size' not in OO0OO0O00OO000000:
                                continue  #line:2394
                            OO00OOOO0O0OO0OO0[
                                'full_size'] += OO0OO0O00OO000000[
                                    'size']  #line:2395
                        OO00OOOO0O0OO0OO0['full_size'] = public.to_size(
                            OO00OOOO0O0OO0OO0['full_size'])  #line:2396
                        O0OO00O00O0O0O000.append(OO00OOOO0O0OO0OO0)  #line:2397
                OOOO000O000OOO0OO = public.M(
                    'mysqlbinlog_backup_setting').where(
                        'db_name=? and backup_type=?',
                        (str(O000O0O00OO0O0OO0['name']),
                         'tables')).select()  #line:2399
                OOOOO000O00O00OO0 = {}  #line:2400
                OOOOO000O00O00OO0['name'] = O000O0O00OO0O0OO0[
                    'name']  #line:2401
                O0O000O00OOOOO000 = []  #line:2402
                O0O0OOO0000O0O0O0 = O0O0O000OOOOOOOO0.get_tables_list(
                    O0O0O000OOOOOOOO0.get_tables())  #line:2403
                for OO0O0O0OOO00O0OO0 in O0O0OOO0000O0O0O0:  #line:2404
                    if not O0O0OOO0000O0O0O0: continue  #line:2405
                    O00000O00O00000OO = public.M(
                        'mysqlbinlog_backup_setting').where(
                            'db_name=? and tb_name=? ',
                            (O0O0O000OOOOOOOO0._db_name,
                             OO0O0O0OOO00O0OO0)).find()  #line:2406
                    OOO000OO00OOO000O = O00O0O0OO0O0OOO00 + OO0O0O0OOO00O0OO0 + '/full_record.json'  #line:2407
                    O0OOO0OO0O000O00O = O00O0O0OO0O0OOO00 + OO0O0O0OOO00O0OO0 + '/inc_record.json'  #line:2408
                    OO00OOOO0O0OO0OO0 = {}  #line:2409
                    OO00OOOO0O0OO0OO0['name'] = OO0O0O0OOO00O0OO0  #line:2410
                    OO00OOOO0O0OO0OO0[
                        'inc_size'] = O0O0O000OOOOOOOO0.get_inc_size(
                            O0OOO0OO0O000O00O)  #line:2412
                    if O00000O00O00000OO:  #line:2414
                        OO00OOOO0O0OO0OO0['cron_id'] = public.M(
                            'crontab').where(
                                'sBody=?',
                                '{} {} --db_name {} --binlog_id {}'.format(
                                    O0O0O000OOOOOOOO0._python_path,
                                    O0O0O000OOOOOOOO0._binlogModel_py,
                                    O00000O00O00000OO['db_name'],
                                    str(O00000O00O00000OO['id']))).getField(
                                        'id')  #line:2415
                        OO00OOOO0O0OO0OO0['backup_id'] = O00000O00O00000OO[
                            'id']  #line:2416
                        OO00OOOO0O0OO0OO0[
                            'upload_localhost'] = O00000O00O00000OO[
                                'upload_local']  #line:2417
                        OO00OOOO0O0OO0OO0['upload_alioss'] = O00000O00O00000OO[
                            'upload_alioss']  #line:2418
                        OO00OOOO0O0OO0OO0['backup_cycle'] = O00000O00O00000OO[
                            'backup_cycle']  #line:2419
                        OO00OOOO0O0OO0OO0['notice'] = O00000O00O00000OO[
                            'notice']  #line:2420
                        OO00OOOO0O0OO0OO0[
                            'notice_channel'] = O00000O00O00000OO[
                                'notice_channel']  #line:2421
                        OO00OOOO0O0OO0OO0['excute_time'] = O00000O00O00000OO[
                            'last_excute_backup_time']  #line:2422
                        OO00OOOO0O0OO0OO0['zip_password'] = O00000O00O00000OO[
                            'zip_password']  #line:2423
                        OO00OOOO0O0OO0OO0['upload_ftp'] = O00000O00O00000OO[
                            'upload_ftp']  #line:2424
                        OO00OOOO0O0OO0OO0['upload_txcos'] = O00000O00O00000OO[
                            'upload_txcos']  #line:2425
                        OO00OOOO0O0OO0OO0['upload_qiniu'] = O00000O00O00000OO[
                            'upload_qiniu']  #line:2426
                        OO00OOOO0O0OO0OO0['upload_obs'] = O00000O00O00000OO[
                            'upload_obs']  #line:2427
                        OO00OOOO0O0OO0OO0['upload_bos'] = O00000O00O00000OO[
                            'upload_bos']  #line:2428
                    else:  #line:2430
                        OO00OOOO0O0OO0OO0['cron_id'] = OO00OOOO0O0OO0OO0[
                            'backup_id'] = OO00OOOO0O0OO0OO0[
                                'notice'] = OO00OOOO0O0OO0OO0[
                                    'upload_alioss'] = OO00OOOO0O0OO0OO0[
                                        'backup_cycle'] = OO00OOOO0O0OO0OO0[
                                            'zip_password'] = None  #line:2431
                        OO00OOOO0O0OO0OO0['upload_localhost'] = OO00OOOO0O0OO0OO0[
                            'upload_alioss'] = OO00OOOO0O0OO0OO0[
                                'upload_ftp'] = OO00OOOO0O0OO0OO0[
                                    'upload_txcos'] = OO00OOOO0O0OO0OO0[
                                        'upload_qiniu'] = OO00OOOO0O0OO0OO0[
                                            'upload_obs'] = OO00OOOO0O0OO0OO0[
                                                'upload_bos'] = ''  #line:2432
                    if os.path.isfile(OOO000OO00OOO000O):  #line:2434
                        OO00OOOO0O0OO0OO0 = O0O0O000OOOOOOOO0.get_time_size(
                            OOO000OO00OOO000O, OO00OOOO0O0OO0OO0)  #line:2435
                        if O00000O00O00000OO:
                            OO00OOOO0O0OO0OO0[
                                'excute_time'] = O00000O00O00000OO[
                                    'last_excute_backup_time']  #line:2436
                        OO00OOOO0O0OO0OO0['full_size'] = public.to_size(
                            OO00OOOO0O0OO0OO0['full_size'] +
                            OO00OOOO0O0OO0OO0['inc_size'])  #line:2437
                        O0O000O00OOOOO000.append(OO00OOOO0O0OO0OO0)  #line:2438
                    else:  #line:2440
                        if not O00000O00O00000OO: continue  #line:2441
                        OO00OOOO0O0OO0OO0['start_time'] = O00000O00O00000OO[
                            'start_backup_time']  #line:2442
                        OO00OOOO0O0OO0OO0['end_time'] = O00000O00O00000OO[
                            'end_backup_time']  #line:2443
                        OO00OOOO0O0OO0OO0['excute_time'] = O00000O00O00000OO[
                            'last_excute_backup_time']  #line:2444
                        OO00OOOO0O0OO0OO0['full_size'] = 0  #line:2449
                        O0O000O0OOOOO000O = public.M(
                            'mysqlbinlog_backups').where(
                                'sid=?',
                                O00000O00O00000OO['id']).select()  #line:2451
                        for O0OO0O00O00OO00OO in O0O000O0OOOOO000O:  #line:2452
                            if not O0OO0O00O00OO00OO: continue  #line:2453
                            if 'size' not in O0OO0O00O00OO00OO:
                                continue  #line:2454
                            OO00OOOO0O0OO0OO0[
                                'full_size'] += O0OO0O00O00OO00OO[
                                    'size']  #line:2455
                        OO00OOOO0O0OO0OO0['full_size'] = public.to_size(
                            OO00OOOO0O0OO0OO0['full_size'])  #line:2456
                        O0O000O00OOOOO000.append(OO00OOOO0O0OO0OO0)  #line:2457
                if O0O000O00OOOOO000:  #line:2458
                    OOOOO000O00O00OO0['data'] = O0O000O00OOOOO000  #line:2459
                    O00OO0OOOOO0OO00O.append(OOOOO000O00O00OO0)  #line:2460
        OOO00OO00000OO00O['databases'] = O0OO00O00O0O0O000  #line:2461
        OOO00OO00000OO00O['tables'] = O00OO0OOOOO0OO00O  #line:2462
        return public.returnMsg(True, OOO00OO00000OO00O)  #line:2463

    def get_databases_info(OOOO0000O0OOOO00O, OO0O0OOO00O000OO0):  #line:2465
        ""  #line:2469
        OO0OOO0OO0O0OOOO0 = OOOO0000O0OOOO00O.get_database_info()  #line:2470
        O0OO000OO0OOO00O0 = []  #line:2471
        for OO0OOOO00O0000000 in OO0OOO0OO0O0OOOO0['msg'][
                'databases']:  #line:2472
            OO0OOOO00O0000000['type'] = 'databases'  #line:2473
            O0OO000OO0OOO00O0.append(OO0OOOO00O0000000)  #line:2474
        return OOOO0000O0OOOO00O.get_page(O0OO000OO0OOO00O0,
                                          OO0O0OOO00O000OO0)  #line:2475

    def get_specified_database_info(OOOOO0OOO0OO0OOOO,
                                    O0O000O0O0O0O0O00):  #line:2477
        ""  #line:2481
        OOOOOO0OOO0O0O0O0 = OOOOO0OOO0OO0OOOO.get_database_info()  #line:2482
        O00O00O00OO0O00O0 = []  #line:2483
        O0OOO00OOOO0OO0O0 = ['databases', 'all']  #line:2484
        OO000OO0O00OO00OO = ['tables', 'all']  #line:2485
        for O0O00O0O0O00O0OOO in OOOOOO0OOO0O0O0O0['msg'][
                'databases']:  #line:2486
            if O0O00O0O0O00O0OOO[
                    'name'] == O0O000O0O0O0O0O00.datab_name:  #line:2487
                O0O00O0O0O00O0OOO['type'] = 'databases'  #line:2488
                if hasattr(
                        O0O000O0O0O0O0O00, 'type'
                ) and O0O000O0O0O0O0O00.type not in O0OOO00OOOO0OO0O0:
                    continue  #line:2489
                O00O00O00OO0O00O0.append(O0O00O0O0O00O0OOO)  #line:2490
        for O0O00O0O0O00O0OOO in OOOOOO0OOO0O0O0O0['msg'][
                'tables']:  #line:2491
            if O0O00O0O0O00O0OOO[
                    'name'] == O0O000O0O0O0O0O00.datab_name:  #line:2492
                for OO00O0O0OO0O00O00 in O0O00O0O0O00O0OOO['data']:  #line:2493
                    OO00O0O0OO0O00O00['type'] = 'tables'  #line:2494
                    if hasattr(
                            O0O000O0O0O0O0O00, 'type'
                    ) and O0O000O0O0O0O0O00.type not in OO000OO0O00OO00OO:
                        continue  #line:2495
                    O00O00O00OO0O00O0.append(OO00O0O0OO0O00O00)  #line:2496
        return OOOOO0OOO0OO0OOOO.get_page(O00O00O00OO0O00O0,
                                          O0O000O0O0O0O0O00)  #line:2497

    def get_page(O0OOO000O000O0O00, O0000O00O0O00O000,
                 OOO0000OOO00O000O):  #line:2500
        ""  #line:2504
        import page  #line:2506
        page = page.Page()  #line:2508
        O0O0O0OO00OO0OO0O = {}  #line:2510
        O0O0O0OO00OO0OO0O['count'] = len(O0000O00O0O00O000)  #line:2511
        O0O0O0OO00OO0OO0O['row'] = 10  #line:2512
        O0O0O0OO00OO0OO0O['p'] = 1  #line:2513
        if hasattr(OOO0000OOO00O000O, 'p'):  #line:2514
            O0O0O0OO00OO0OO0O['p'] = int(OOO0000OOO00O000O['p'])  #line:2515
        O0O0O0OO00OO0OO0O['uri'] = {}  #line:2516
        O0O0O0OO00OO0OO0O['return_js'] = ''  #line:2517
        OO0OOOOO00OOOO0O0 = {}  #line:2519
        OO0OOOOO00OOOO0O0['page'] = page.GetPage(
            O0O0O0OO00OO0OO0O, limit='1,2,3,4,5,8')  #line:2520
        O00O0OO0OO0O00OO0 = 0  #line:2521
        OO0OOOOO00OOOO0O0['data'] = []  #line:2522
        for O0O0O0OOOOO0O0OO0 in range(O0O0O0OO00OO0OO0O['count']):  #line:2523
            if O00O0OO0OO0O00OO0 >= page.ROW: break  #line:2524
            if O0O0O0OOOOO0O0OO0 < page.SHIFT: continue  #line:2525
            O00O0OO0OO0O00OO0 += 1  #line:2526
            OO0OOOOO00OOOO0O0['data'].append(
                O0000O00O0O00O000[O0O0O0OOOOO0O0OO0])  #line:2527
        return OO0OOOOO00OOOO0O0  #line:2528

    def delete_file(OO0O0O000OOOO0000, OO0OOOOO000OO00OO):  #line:2531
        ""  #line:2536
        if os.path.exists(OO0OOOOO000OO00OO):  #line:2537
            os.remove(OO0OOOOO000OO00OO)  #line:2538

    def send_failture_notification(O00OO00OO00OO0O00,
                                   O0OO0OO000000O00O,
                                   target="",
                                   remark=""):  #line:2540
        ""  #line:2545
        O000OOOOO0OOO00OO = '数据库增量备份[ {} ]'.format(target)  #line:2546
        OOOO0000O000OO0O0 = O00OO00OO00OO0O00._pdata['notice']  #line:2547
        OO0OO00000OOO00OO = O00OO00OO00OO0O00._pdata[
            'notice_channel']  #line:2548
        if OOOO0000O000OO0O0 in [0, '0'] or not OO0OO00000OOO00OO:  #line:2549
            return  #line:2550
        if OOOO0000O000OO0O0 in [1, '1', 2, '2']:  #line:2551
            O00000000O0O00OO0 = "宝塔计划任务备份失败提醒"  #line:2552
            OOOO00OOOOOO0OOO0 = O000OOOOO0OOO00OO  #line:2553
            O000O00O00OO00OOO = O00OO00OO00OO0O00._mybackup.generate_failture_notice(
                OOOO00OOOOOO0OOO0, O0OO0OO000000O00O, remark)  #line:2554
            OOO000OOO0O00O000 = O00OO00OO00OO0O00._mybackup.send_notification(
                OO0OO00000OOO00OO, O00000000O0O00OO0,
                O000O00O00OO00OOO)  #line:2555
            if OOO000OOO0O00O000:  #line:2556
                print('|-消息通知已发送。')  #line:2557

    def sync_date(O0OOO00000OOOO0OO):  #line:2559
        ""  #line:2562
        import config  #line:2563
        config.config().syncDate(None)  #line:2564

    def get_config(OO00O00OO0OO0O0OO, O0OOOO0O0OO00O000):  #line:2569
        ""  #line:2572
        OO0O0OO0OOOO0O0OO = O0OOOO0O0OO00O000 + 'As.conf'  #line:2573
        OO00O00O0O0000000 = os.path.join(public.get_datadir(),
                                         OO0O0OO0OOOO0O0OO)  #line:2574
        O0OO0O0000O000O0O = os.path.join(public.get_panel_path(),
                                         'data/a_pass.pl')  #line:2575
        O0O0OOO00O000O0O0 = O0OOOO0O0OO00O000 + '/config.conf'  #line:2576
        O000OOOOOO0O0OOO0 = os.path.join(public.get_plugin_path(),
                                         O0O0OOO00O000O0O0)  #line:2577
        OO0O000O0O00O000O = os.path.join(public.get_plugin_path(),
                                         O0OOOO0O0OO00O000)  #line:2578
        OOO00O00OOO0000OO = os.path.join(OO0O000O0O00O000O,
                                         'aes_status')  #line:2579
        OO00O00000OOO0OO0 = False  #line:2580
        if os.path.isfile(OOO00O00OOO0000OO):  #line:2581
            OO00O00000OOO0OO0 = True  #line:2582
        OOO00OOO000OOO0O0 = ''  #line:2583
        if os.path.isfile(O000OOOOOO0O0OOO0):  #line:2584
            OOO00OOO000OOO0O0 = O000OOOOOO0O0OOO0  #line:2585
        elif os.path.isfile(OO00O00O0O0000000):  #line:2586
            OOO00OOO000OOO0O0 = OO00O00O0O0000000  #line:2587
        if not OOO00OOO000OOO0O0: return ['', '', '', '', '/']  #line:2588
        O000OO0O0O0OOO0OO = public.readFile(OOO00OOO000OOO0O0)  #line:2589
        if OO00O00000OOO0OO0:  #line:2590
            try:  #line:2591
                OO0O000O000O00OOO = public.readFile(
                    O0OO0O0000O000O0O)  #line:2592
                O000OO0O0O0OOO0OO = public.aes_decrypt(
                    O000OO0O0O0OOO0OO, OO0O000O000O00OOO)  #line:2593
            except:
                O000OO0O0O0OOO0OO = {}  #line:2594
        else:  #line:2595
            O000OO0O0O0OOO0OO = json.loads(O000OO0O0O0OOO0OO)  #line:2596
        O00OO0000000OOO0O = OO00O00OO0OO0O0OO._config_path + '/' + OO0O0OO0OOOO0O0OO  #line:2597
        if not os.path.isfile(O00OO0000000OOO0O) and not O000OO0O0O0OOO0OO:
            return ['', '', '', '', '/']  #line:2598
        if not O000OO0O0O0OOO0OO and os.path.isfile(
                O00OO0000000OOO0O):  #line:2599
            O000OO0O0O0OOO0OO = public.readFile(O00OO0000000OOO0O)  #line:2600
        if not O000OO0O0O0OOO0OO: return ['', '', '', '', '/']  #line:2601
        OO0O0O00OO00OOO00 = O000OO0O0O0OOO0OO.split('|')  #line:2602
        if len(OO0O0O00OO00OOO00) < 5:
            OO0O0O00OO00OOO00.append('/')  #line:2603
        return OO0O0O00OO00OOO00  #line:2604


class alioss_main:  #line:2607
    __OOO0O0OO0OOO00OOO = None  #line:2608
    __OO00OOO0O00000O0O = 0  #line:2609

    def __OO00000O0O000000O(OO0O0O0000OO00000):  #line:2610
        ""  #line:2614
        if OO0O0O0000OO00000.__OOO0O0OO0OOO00OOO: return  #line:2615
        O0000OOO000O00OOO = OO0O0O0000OO00000.get_config()  #line:2617
        OO0O0O0000OO00000.__OOO0O0O00O00OO0O0 = O0000OOO000O00OOO[
            2]  #line:2619
        if O0000OOO000O00OOO[3].find(O0000OOO000O00OOO[2]) != -1:
            O0000OOO000O00OOO[3] = O0000OOO000O00OOO[3].replace(
                O0000OOO000O00OOO[2] + '.', '')  #line:2620
        OO0O0O0000OO00000.__OO00OOO00OO0O0O00 = O0000OOO000O00OOO[
            3]  #line:2621
        OO0O0O0000OO00000.__OO0O0O0OOO000OOOO = main().get_path(
            O0000OOO000O00OOO[4] + '/bt_backup/')  #line:2622
        if OO0O0O0000OO00000.__OO0O0O0OOO000OOOO[:1] == '/':
            OO0O0O0000OO00000.__OO0O0O0OOO000OOOO = OO0O0O0000OO00000.__OO0O0O0OOO000OOOO[
                1:]  #line:2623
        try:  #line:2625
            OO0O0O0000OO00000.__OOO0O0OO0OOO00OOO = oss2.Auth(
                O0000OOO000O00OOO[0], O0000OOO000O00OOO[1])  #line:2627
        except Exception as O00O00O0OO00OOO00:  #line:2628
            pass  #line:2629

    def get_config(OOOO000O00OO0OOOO):  #line:2632
        ""  #line:2637
        return main().get_config('alioss')  #line:2638

    def check_config(OOO0OOOOOOO000O00):  #line:2642
        ""  #line:2647
        try:  #line:2648
            OOO0OOOOOOO000O00.__OO00000O0O000000O()  #line:2649
            from itertools import islice  #line:2651
            O000O0O0000OOOO00 = oss2.Bucket(
                OOO0OOOOOOO000O00.__OOO0O0OO0OOO00OOO,
                OOO0OOOOOOO000O00.__OO00OOO00OO0O0O00,
                OOO0OOOOOOO000O00.__OOO0O0O00O00OO0O0)  #line:2652
            OO0OO0OO00O0000O0 = oss2.ObjectIterator(
                O000O0O0000OOOO00)  #line:2653
            OOOOOO0O0OO0O0000 = []  #line:2654
            O00O0OOO0OO0O0O00 = '/'  #line:2655
            '''key, last_modified, etag, type, size, storage_class'''  #line:2656
            for OO000OOO0OOOO0O0O in islice(
                    oss2.ObjectIterator(O000O0O0000OOOO00,
                                        delimiter='/',
                                        prefix='/'), 1000):  #line:2657
                OO000OOO0OOOO0O0O.key = OO000OOO0OOOO0O0O.key.replace(
                    '/', '')  #line:2658
                if not OO000OOO0OOOO0O0O.key: continue  #line:2659
                O0000O0OO0O0O0000 = {}  #line:2660
                O0000O0OO0O0O0000['name'] = OO000OOO0OOOO0O0O.key  #line:2661
                O0000O0OO0O0O0000['size'] = OO000OOO0OOOO0O0O.size  #line:2662
                O0000O0OO0O0O0000['type'] = OO000OOO0OOOO0O0O.type  #line:2663
                O0000O0OO0O0O0000[
                    'download'] = OOO0OOOOOOO000O00.download_file(
                        O00O0OOO0OO0O0O00 + OO000OOO0OOOO0O0O.key,
                        False)  #line:2664
                O0000O0OO0O0O0000[
                    'time'] = OO000OOO0OOOO0O0O.last_modified  #line:2665
                OOOOOO0O0OO0O0000.append(O0000O0OO0O0O0000)  #line:2666
            return True  #line:2667
        except:  #line:2668
            return False  #line:2669

    def get_list(O00O00O0OOOO00OOO, get=None):  #line:2671
        ""  #line:2676
        O00O00O0OOOO00OOO.__OO00000O0O000000O()  #line:2678
        if not O00O00O0OOOO00OOO.__OOO0O0OO0OOO00OOO:  #line:2679
            return False  #line:2680
        try:  #line:2682
            from itertools import islice  #line:2683
            O0O0O0OO0O00OO0OO = oss2.Bucket(
                O00O00O0OOOO00OOO.__OOO0O0OO0OOO00OOO,
                O00O00O0OOOO00OOO.__OO00OOO00OO0O0O00,
                O00O00O0OOOO00OOO.__OOO0O0O00O00OO0O0)  #line:2684
            OO000O0O000OOO000 = oss2.ObjectIterator(
                O0O0O0OO0O00OO0OO)  #line:2685
            OO0000OO0O0O000OO = []  #line:2686
            OOO000000000OO0O0 = main().get_path(get.path)  #line:2687
            '''key, last_modified, etag, type, size, storage_class'''  #line:2688
            for OOO0OO00O0O0O0O0O in islice(
                    oss2.ObjectIterator(O0O0O0OO0O00OO0OO,
                                        delimiter='/',
                                        prefix=OOO000000000OO0O0),
                    1000):  #line:2689
                OOO0OO00O0O0O0O0O.key = OOO0OO00O0O0O0O0O.key.replace(
                    OOO000000000OO0O0, '')  #line:2690
                if not OOO0OO00O0O0O0O0O.key: continue  #line:2691
                OOOOO000OO0OO0OOO = {}  #line:2692
                OOOOO000OO0OO0OOO['name'] = OOO0OO00O0O0O0O0O.key  #line:2693
                OOOOO000OO0OO0OOO['size'] = OOO0OO00O0O0O0O0O.size  #line:2694
                OOOOO000OO0OO0OOO['type'] = OOO0OO00O0O0O0O0O.type  #line:2695
                OOOOO000OO0OO0OOO[
                    'download'] = O00O00O0OOOO00OOO.download_file(
                        OOO000000000OO0O0 + OOO0OO00O0O0O0O0O.key)  #line:2696
                OOOOO000OO0OO0OOO[
                    'time'] = OOO0OO00O0O0O0O0O.last_modified  #line:2697
                OO0000OO0O0O000OO.append(OOOOO000OO0OO0OOO)  #line:2698
            OO00OO0OOOOOOO0O0 = {}  #line:2699
            OO00OO0OOOOOOO0O0['path'] = get.path  #line:2700
            OO00OO0OOOOOOO0O0['list'] = OO0000OO0O0O000OO  #line:2701
            return OO00OO0OOOOOOO0O0  #line:2702
        except Exception as O0000O000O0O00O0O:  #line:2703
            return public.returnMsg(False, str(O0000O000O0O00O0O))  #line:2704

    def upload_file_by_path(OOOO000O0O0O0O00O, O000O00OO00OO0O0O,
                            O0OOO00O000O0OO00):  #line:2706
        ""  #line:2713
        OOOO000O0O0O0O00O.__OO00000O0O000000O()  #line:2715
        if not OOOO000O0O0O0O00O.__OOO0O0OO0OOO00OOO:  #line:2716
            return False  #line:2717
        try:  #line:2718
            OO0OOO0OO000O00O0 = main().get_path(
                os.path.dirname(O0OOO00O000O0OO00)) + os.path.basename(
                    O0OOO00O000O0OO00)  #line:2720
            try:  #line:2722
                print('|-正在上传{}到阿里云OSS'.format(O000O00OO00OO0O0O),
                      end='')  #line:2723
                O00OOOO0000O0OOOO = oss2.Bucket(
                    OOOO000O0O0O0O00O.__OOO0O0OO0OOO00OOO,
                    OOOO000O0O0O0O00O.__OO00OOO00OO0O0O00,
                    OOOO000O0O0O0O00O.__OOO0O0O00O00OO0O0)  #line:2724
                oss2.defaults.connection_pool_size = 4  #line:2726
                OOO0O0OOOOO00OOO0 = oss2.resumable_upload(
                    O00OOOO0000O0OOOO,
                    OO0OOO0OO000O00O0,
                    O000O00OO00OO0O0O,
                    store=oss2.ResumableStore(root='/tmp'),
                    multipart_threshold=1024 * 1024 * 2,
                    part_size=1024 * 1024,
                    num_threads=1)  #line:2731
                print(' ==> 成功')  #line:2732
            except:  #line:2733
                print('|-无法上传{}到阿里云OSS！请检查阿里云OSS配置是否正确！'.format(
                    O000O00OO00OO0O0O))  #line:2734
            return True  #line:2738
        except Exception as O00O0O0OOO0000000:  #line:2739
            print(O00O0O0OOO0000000)  #line:2740
            if O00O0O0OOO0000000.status == 403:  #line:2741
                time.sleep(5)  #line:2742
                OOOO000O0O0O0O00O.__OO00OOO0O00000O0O += 1  #line:2743
                if OOOO000O0O0O0O00O.__OO00OOO0O00000O0O < 2:  #line:2744
                    OOOO000O0O0O0O00O.upload_file_by_path(
                        O000O00OO00OO0O0O, O0OOO00O000O0OO00)  #line:2746
            return False  #line:2747

    def download_file(O0O0O000OOO00OOO0, OOO0OOOOO00000OOO):  #line:2749
        ""  #line:2755
        O0O0O000OOO00OOO0.__OO00000O0O000000O()  #line:2757
        if not O0O0O000OOO00OOO0.__OOO0O0OO0OOO00OOO:  #line:2758
            return None  #line:2759
        try:  #line:2760
            O0O0OO000O0O0OO0O = oss2.Bucket(
                O0O0O000OOO00OOO0.__OOO0O0OO0OOO00OOO,
                O0O0O000OOO00OOO0.__OO00OOO00OO0O0O00,
                O0O0O000OOO00OOO0.__OOO0O0O00O00OO0O0)  #line:2761
            O0OOO0OO0O0000OOO = O0O0OO000O0O0OO0O.sign_url(
                'GET', OOO0OOOOO00000OOO, 3600)  #line:2762
            return O0OOO0OO0O0000OOO  #line:2763
        except:  #line:2764
            print(O0O0O000OOO00OOO0.__OOO0O0OO0O0O0OOOO)  #line:2765
            return None  #line:2766

    def alioss_delete_file(O0O00O0OOOOOO00OO, O00OOOO000000O0O0):  #line:2768
        ""  #line:2774
        O0O00O0OOOOOO00OO.__OO00000O0O000000O()  #line:2776
        if not O0O00O0OOOOOO00OO.__OOO0O0OO0OOO00OOO:  #line:2777
            return False  #line:2778
        try:  #line:2780
            OOO0O0OOOOOO00000 = oss2.Bucket(
                O0O00O0OOOOOO00OO.__OOO0O0OO0OOO00OOO,
                O0O00O0OOOOOO00OO.__OO00OOO00OO0O0O00,
                O0O00O0OOOOOO00OO.__OOO0O0O00O00OO0O0)  #line:2781
            OOOOO0OO0OO0O000O = OOO0O0OOOOOO00000.delete_object(
                O00OOOO000000O0O0)  #line:2782
            return OOOOO0OO0OO0O000O.status  #line:2783
        except Exception as O00O0O00OOO0O00OO:  #line:2784
            if O00O0O00OOO0O00OO.status == 403:  #line:2785
                O0O00O0OOOOOO00OO.__OO00OOO0O00000O0O += 1  #line:2786
                if O0O00O0OOOOOO00OO.__OO00OOO0O00000O0O < 2:  #line:2787
                    O0O00O0OOOOOO00OO.alioss_delete_file(
                        O00OOOO000000O0O0)  #line:2789
            print('删除失败!')  #line:2791
            return None  #line:2792

    def remove_file(O0OOOOO00000OOO00, OO0000O0O00OOO00O):  #line:2794
        ""  #line:2801
        O0000OO0O0O0O0OO0 = main().get_path(OO0000O0O00OOO00O.path)  #line:2802
        OO000OOO0O0000O0O = O0000OO0O0O0O0OO0 + OO0000O0O00OOO00O.filename  #line:2803
        O0OOOOO00000OOO00.alioss_delete_file(OO000OOO0O0000O0O)  #line:2804
        return public.returnMsg(True, '删除文件成功!{}----{}'.format(
            O0000OO0O0O0O0OO0, OO000OOO0O0000O0O))  #line:2805


class txcos_main:  #line:2808
    __O0O0O0OOOOO0000OO = None  #line:2809
    __O00000OO0OO00O00O = None  #line:2810
    __OOO0OOO0O0O000O0O = 0  #line:2811
    __OO000OOOOO0O000O0 = None  #line:2812
    __OOO000OOO00OO0O0O = None  #line:2813
    __O0OOOOO00OOOO0000 = None  #line:2814
    __OOOOO0O0OOOO0000O = None  #line:2815
    __OO0O0OO00O0OO0O0O = "ERROR: 无法连接腾讯云COS !"  #line:2816

    def __init__(O0O0O0O00OO0O000O):  #line:2819
        O0O0O0O00OO0O000O.__OO0O00OOOO0OOOO0O()  #line:2820

    def __OO0O00OOOO0OOOO0O(OOOO000OOOO0O00O0):  #line:2822
        ""  #line:2825
        if OOOO000OOOO0O00O0.__O0O0O0OOOOO0000OO: return  #line:2826
        OOOO000O00O00O00O = OOOO000OOOO0O00O0.get_config()  #line:2828
        OOOO000OOOO0O00O0.__OO000OOOOO0O000O0 = OOOO000O00O00O00O[
            0]  #line:2829
        OOOO000OOOO0O00O0.__OOO000OOO00OO0O0O = OOOO000O00O00O00O[
            1]  #line:2830
        OOOO000OOOO0O00O0.__O0OOOOO00OOOO0000 = OOOO000O00O00O00O[
            2]  #line:2831
        OOOO000OOOO0O00O0.__OOOOO0O0OOOO0000O = OOOO000O00O00O00O[
            3]  #line:2832
        OOOO000OOOO0O00O0.__O00000OO0OO00O00O = main().get_path(
            OOOO000O00O00O00O[4])  #line:2833
        try:  #line:2834
            O0O00OO0OO00O000O = CosConfig(
                Region=OOOO000OOOO0O00O0.__O0OOOOO00OOOO0000,
                SecretId=OOOO000OOOO0O00O0.__OO000OOOOO0O000O0,
                SecretKey=OOOO000OOOO0O00O0.__OOO000OOO00OO0O0O,
                Token=None,
                Scheme='http')  #line:2835
            OOOO000OOOO0O00O0.__O0O0O0OOOOO0000OO = CosS3Client(
                O0O00OO0OO00O000O)  #line:2836
        except Exception as OO0000O0OOO0OOO00:  #line:2837
            pass  #line:2838

    def get_config(OOO00OO000OO000O0, get=None):  #line:2842
        ""  #line:2845
        return main().get_config('txcos')  #line:2846

    def check_config(O00OO0O000O00O0O0):  #line:2851
        try:  #line:2852
            O000O00O0O000000O = []  #line:2853
            O0O0O0O0OOOO00OO0 = []  #line:2854
            OO0O0OO0O0OO00000 = O00OO0O000O00O0O0.__O00000OO0OO00O00O + main(
            ).get_path('/')  #line:2855
            OO0000000OOO00O0O = O00OO0O000O00O0O0.__O0O0O0OOOOO0000OO.list_objects(
                Bucket=O00OO0O000O00O0O0.__OOOOO0O0OOOO0000O,
                MaxKeys=100,
                Delimiter='/',
                Prefix=OO0O0OO0O0OO00000)  #line:2856
            return True  #line:2857
        except:  #line:2858
            return False  #line:2859

    def upload_file(O000000000000OOOO, O00OO0O00O0OOOO0O):  #line:2861
        ""  #line:2865
        O000000000000OOOO.__OO0O00OOOO0OOOO0O()  #line:2867
        if not O000000000000OOOO.__O0O0O0OOOOO0000OO:  #line:2868
            return False  #line:2869
        try:  #line:2871
            O00000O00O00OO000, OO0O0O00OO00OOOO0 = os.path.split(
                O00OO0O00O0OOOO0O)  #line:2873
            OO0O0O00OO00OOOO0 = O000000000000OOOO.__O00000OO0OO00O00O + OO0O0O00OO00OOOO0  #line:2874
            OO00O00OO0OO00O0O = O000000000000OOOO.__O0O0O0OOOOO0000OO.upload_file(
                Bucket=O000000000000OOOO.__OOOOO0O0OOOO0000O,
                Key=OO0O0O00OO00OOOO0,
                MAXThread=10,
                PartSize=5,
                LocalFilePath=O00OO0O00O0OOOO0O)  #line:2881
        except:  #line:2882
            time.sleep(1)  #line:2883
            O000000000000OOOO.__OOO0OOO0O0O000O0O += 1  #line:2884
            if O000000000000OOOO.__OOO0OOO0O0O000O0O < 2:  #line:2885
                O000000000000OOOO.upload_file(O00OO0O00O0OOOO0O)  #line:2887
            print(O000000000000OOOO.__OO0O0OO00O0OO0O0O)  #line:2888
            return None  #line:2889

    def upload_file_by_path(O0O0O00000O000O00, O00000O00O0O0O000,
                            O00000OOO0O00OO00):  #line:2892
        ""  #line:2897
        O0O0O00000O000O00.__OO0O00OOOO0OOOO0O()  #line:2899
        if not O0O0O00000O000O00.__O0O0O0OOOOO0000OO:  #line:2900
            return False  #line:2901
        try:  #line:2903
            print('|-正在上传{}到腾讯云COS'.format(O00000O00O0O0O000),
                  end='')  #line:2904
            OOO0O0OOO0OO0OO0O, OOOOO0000O0O0OOO0 = os.path.split(
                O00000O00O0O0O000)  #line:2905
            O0O0O00000O000O00.__O00000OO0OO00O00O = main().get_path(
                os.path.dirname(O00000OOO0O00OO00))  #line:2906
            OOOOO0000O0O0OOO0 = O0O0O00000O000O00.__O00000OO0OO00O00O + '/' + OOOOO0000O0O0OOO0  #line:2907
            OO00OO0O00O0O0000 = O0O0O00000O000O00.__O0O0O0OOOOO0000OO.upload_file(
                Bucket=O0O0O00000O000O00.__OOOOO0O0OOOO0000O,
                Key=OOOOO0000O0O0OOO0,
                MAXThread=10,
                PartSize=5,
                LocalFilePath=O00000O00O0O0O000)  #line:2910
            print(' ==> 成功')  #line:2912
            return True  #line:2913
        except Exception as O0O0OO00O00OO000O:  #line:2914
            time.sleep(1)  #line:2916
            O0O0O00000O000O00.__OOO0OOO0O0O000O0O += 1  #line:2917
            if O0O0O00000O000O00.__OOO0OOO0O0O000O0O < 2:  #line:2918
                O0O0O00000O000O00.upload_file_by_path(
                    O00000O00O0O0O000, O00000OOO0O00OO00)  #line:2920
            return False  #line:2921

    def create_dir(O0OO00OO0OOOOOO0O, get=None):  #line:2924
        ""  #line:2927
        O0OO00OO0OOOOOO0O.__OO0O00OOOO0OOOO0O()  #line:2929
        if not O0OO00OO0OOOOOO0O.__O0O0O0OOOOO0000OO:  #line:2930
            return False  #line:2931
        OOO0O00OOO0OO0000 = main().get_path(get.path + get.dirname)  #line:2933
        O0OOOOO00O000O0O0 = '/tmp/dirname.pl'  #line:2934
        public.writeFile(O0OOOOO00O000O0O0, '')  #line:2935
        O0OOOOOOOOO00O0OO = O0OO00OO0OOOOOO0O.__O0O0O0OOOOO0000OO.put_object(
            Bucket=O0OO00OO0OOOOOO0O.__OOOOO0O0OOOO0000O,
            Body=b'',
            Key=OOO0O00OOO0OO0000)  #line:2936
        os.remove(O0OOOOO00O000O0O0)  #line:2937
        return public.returnMsg(True, '创建成功!')  #line:2938

    def get_list(OOOOO0O0000OOO00O, get=None):  #line:2940
        ""  #line:2943
        OOOOO0O0000OOO00O.__OO0O00OOOO0OOOO0O()  #line:2945
        if not OOOOO0O0000OOO00O.__O0O0O0OOOOO0000OO:  #line:2946
            return False  #line:2947
        try:  #line:2949
            OO00000OO00000OOO = []  #line:2950
            OO000OO0OO0OO0000 = []  #line:2951
            OOOOO000O0OOOOOOO = main().get_path(get.path)  #line:2952
            if 'Contents' in OOOOO0O0000OOO00O.__O0O0O0OOOOO0000OO.list_objects(
                    Bucket=OOOOO0O0000OOO00O.__OOOOO0O0OOOO0000O,
                    MaxKeys=100,
                    Delimiter='/',
                    Prefix=OOOOO000O0OOOOOOO):  #line:2953
                for O0OO0O0OOOO00OOOO in OOOOO0O0000OOO00O.__O0O0O0OOOOO0000OO.list_objects(
                        Bucket=OOOOO0O0000OOO00O.__OOOOO0O0OOOO0000O,
                        MaxKeys=100,
                        Delimiter='/',
                        Prefix=OOOOO000O0OOOOOOO)['Contents']:  #line:2954
                    OO0OOO00O0000O00O = {}  #line:2955
                    O0OO0O0OOOO00OOOO['Key'] = O0OO0O0OOOO00OOOO[
                        'Key'].replace(OOOOO000O0OOOOOOO, '')  #line:2956
                    if not O0OO0O0OOOO00OOOO['Key']: continue  #line:2957
                    OO0OOO00O0000O00O['name'] = O0OO0O0OOOO00OOOO[
                        'Key']  #line:2958
                    OO0OOO00O0000O00O['size'] = O0OO0O0OOOO00OOOO[
                        'Size']  #line:2959
                    OO0OOO00O0000O00O['type'] = O0OO0O0OOOO00OOOO[
                        'StorageClass']  #line:2960
                    OO0OOO00O0000O00O[
                        'download'] = OOOOO0O0000OOO00O.download_file(
                            OOOOO000O0OOOOOOO +
                            O0OO0O0OOOO00OOOO['Key'])  #line:2961
                    OO0OOO00O0000O00O['time'] = O0OO0O0OOOO00OOOO[
                        'LastModified']  #line:2962
                    OO00000OO00000OOO.append(OO0OOO00O0000O00O)  #line:2963
            else:  #line:2964
                pass  #line:2965
            if 'CommonPrefixes' in OOOOO0O0000OOO00O.__O0O0O0OOOOO0000OO.list_objects(
                    Bucket=OOOOO0O0000OOO00O.__OOOOO0O0OOOO0000O,
                    MaxKeys=100,
                    Delimiter='/',
                    Prefix=OOOOO000O0OOOOOOO):  #line:2966
                for O0O000OOO0OO00000 in OOOOO0O0000OOO00O.__O0O0O0OOOOO0000OO.list_objects(
                        Bucket=OOOOO0O0000OOO00O.__OOOOO0O0OOOO0000O,
                        MaxKeys=100,
                        Delimiter='/',
                        Prefix=OOOOO000O0OOOOOOO
                )['CommonPrefixes']:  #line:2967
                    if not O0O000OOO0OO00000['Prefix']: continue  #line:2968
                    OO0OOOOOO0O0O0OOO = O0O000OOO0OO00000['Prefix'].split(
                        '/')[-2] + '/'  #line:2969
                    OO000OO0OO0OO0000.append(OO0OOOOOO0O0O0OOO)  #line:2970
            else:  #line:2971
                pass  #line:2972
            OO00O00O000OO00OO = {}  #line:2973
            OO00O00O000OO00OO['path'] = get.path  #line:2974
            OO00O00O000OO00OO['list'] = OO00000OO00000OOO  #line:2975
            OO00O00O000OO00OO['dir'] = OO000OO0OO0OO0000  #line:2976
            return OO00O00O000OO00OO  #line:2977
        except:  #line:2978
            OO00O00O000OO00OO = {}  #line:2979
            if OOOOO0O0000OOO00O.__O0O0O0OOOOO0000OO:  #line:2980
                OO00O00O000OO00OO['status'] = True  #line:2981
            else:  #line:2982
                OO00O00O000OO00OO['status'] = False  #line:2983
            OO00O00O000OO00OO['path'] = get.path  #line:2984
            OO00O00O000OO00OO['list'] = OO00000OO00000OOO  #line:2985
            OO00O00O000OO00OO['dir'] = OO000OO0OO0OO0000  #line:2986
            return OO00O00O000OO00OO  #line:2987

    def download_file(O0O0O00000OO0O00O,
                      OOOOOO0O0O000OO0O,
                      Expired=300):  #line:2989
        ""  #line:2992
        O0O0O00000OO0O00O.__OO0O00OOOO0OOOO0O()  #line:2994
        if not O0O0O00000OO0O00O.__O0O0O0OOOOO0000OO:  #line:2995
            return None  #line:2996
        try:  #line:2997
            OOO0O000O0000O00O = O0O0O00000OO0O00O.__O0O0O0OOOOO0000OO.get_presigned_download_url(
                Bucket=O0O0O00000OO0O00O.__OOOOO0O0OOOO0000O,
                Key=OOOOOO0O0O000OO0O)  #line:2998
            OOO0O000O0000O00O = re.findall('([^?]*)?.*',
                                           OOO0O000O0000O00O)[0]  #line:2999
            return OOO0O000O0000O00O  #line:3000
        except:  #line:3001
            print(O0O0O00000OO0O00O.__OO0O0OO00O0OO0O0O)  #line:3002
            return None  #line:3003

    def delete_file(O00O0OOOO0O000O00, OOOOO0OOOO0O0O000):  #line:3005
        ""  #line:3009
        O00O0OOOO0O000O00.__OO0O00OOOO0OOOO0O()  #line:3011
        if not O00O0OOOO0O000O00.__O0O0O0OOOOO0000OO:  #line:3012
            return False  #line:3013
        try:  #line:3015
            OO000O000OO0OO00O = O00O0OOOO0O000O00.__O0O0O0OOOOO0000OO.delete_object(
                Bucket=O00O0OOOO0O000O00.__OOOOO0O0OOOO0000O,
                Key=OOOOO0OOOO0O0O000)  #line:3016
            return OO000O000OO0OO00O  #line:3017
        except Exception as O0OOOO0O0OO0O00O0:  #line:3018
            O00O0OOOO0O000O00.__OOO0OOO0O0O000O0O += 1  #line:3019
            if O00O0OOOO0O000O00.__OOO0OOO0O0O000O0O < 2:  #line:3020
                O00O0OOOO0O000O00.delete_file(OOOOO0OOOO0O0O000)  #line:3022
            print(O00O0OOOO0O000O00.__OO0O0OO00O0OO0O0O)  #line:3023
            return None  #line:3024

    def remove_file(O00OOOO000O0OO0O0, OOO0000O000OOO0OO):  #line:3027
        OOO000O00O0OO0O00 = main().get_path(OOO0000O000OOO0OO.path)  #line:3028
        OOOO0O0OO00OO0OOO = OOO000O00O0OO0O00 + OOO0000O000OOO0OO.filename  #line:3029
        O00OOOO000O0OO0O0.delete_file(OOOO0O0OO00OO0OOO)  #line:3030
        return public.returnMsg(True, '删除文件成功!')  #line:3031


class ftp_main:  #line:3034
    __OOO000OO000OOO000 = '/'  #line:3035

    def __init__(OOO000OOOO0OO000O):  #line:3037
        OOO000OOOO0OO000O.__OOO000OO000OOO000 = OOO000OOOO0OO000O.get_config(
            None)[3]  #line:3038

    def get_config(O0000OOO0O0O0OOO0, get=None):  #line:3040
        return main().get_config('ftp')  #line:3041

    def set_config(O0O0OOOOO0O0O0OOO, O00O0OO000000OO0O):  #line:3044
        O0O00O00O000O0OOO = main()._config_path + '/ftp.conf'  #line:3045
        OO0O0OO0O00O000O0 = O00O0OO000000OO0O.ftp_host + '|' + O00O0OO000000OO0O.ftp_user + '|' + O00O0OO000000OO0O.ftp_pass + '|' + O00O0OO000000OO0O.ftp_path  #line:3046
        public.writeFile(O0O00O00O000O0OOO, OO0O0OO0O00O000O0)  #line:3047
        return public.returnMsg(True, '设置成功!')  #line:3048

    def connentFtp(OOOOOO0OOOO0O0OO0):  #line:3051
        from ftplib import FTP  #line:3052
        OOOO0O000OOOOO0O0 = OOOOOO0OOOO0O0OO0.get_config()  #line:3053
        if OOOO0O000OOOOO0O0[0].find(':') == -1:
            OOOO0O000OOOOO0O0[0] += ':21'  #line:3054
        O0000000O00OO0O00 = OOOO0O000OOOOO0O0[0].split(':')  #line:3055
        if O0000000O00OO0O00[1] == '': O0000000O00OO0O00[1] = '21'  #line:3056
        OO00000000O00OO0O = FTP()  #line:3057
        OO00000000O00OO0O.set_debuglevel(0)  #line:3058
        OO00000000O00OO0O.connect(O0000000O00OO0O00[0],
                                  int(O0000000O00OO0O00[1]))  #line:3059
        OO00000000O00OO0O.login(OOOO0O000OOOOO0O0[1],
                                OOOO0O000OOOOO0O0[2])  #line:3060
        if OOOOOO0OOOO0O0OO0.__OOO000OO000OOO000 != '/':  #line:3061
            OOOOOO0OOOO0O0OO0.dirname = OOOOOO0OOOO0O0OO0.__OOO000OO000OOO000  #line:3062
            OOOOOO0OOOO0O0OO0.path = '/'  #line:3063
            OOOOOO0OOOO0O0OO0.createDir(OOOOOO0OOOO0O0OO0,
                                        OO00000000O00OO0O)  #line:3064
        OO00000000O00OO0O.cwd(
            OOOOOO0OOOO0O0OO0.__OOO000OO000OOO000)  #line:3065
        return OO00000000O00OO0O  #line:3066

    def check_config(OO0000O0O00O0O0O0):  #line:3069
        try:  #line:3070
            OO00O0OO0000OOOO0 = OO0000O0O00O0O0O0.connentFtp()  #line:3071
            if OO00O0OO0000OOOO0: return True  #line:3072
        except:  #line:3073
            return False  #line:3074

    def createDir(OOO0OOOO00O00O000, O0000OO0O0O00O0OO, ftp=None):  #line:3077
        try:  #line:3078
            if not ftp: ftp = OOO0OOOO00O00O000.connentFtp()  #line:3079
            O00O00000O000000O = O0000OO0O0O00O0OO.dirname.split(
                '/')  #line:3080
            ftp.cwd(O0000OO0O0O00O0OO.path)  #line:3081
            for O00OOOOOO0O000OO0 in O00O00000O000000O:  #line:3082
                if not O00OOOOOO0O000OO0: continue  #line:3083
                if not O00OOOOOO0O000OO0 in ftp.nlst():
                    ftp.mkd(O00OOOOOO0O000OO0)  #line:3084
                ftp.cwd(O00OOOOOO0O000OO0)  #line:3085
            return public.returnMsg(True, '目录创建成功!')  #line:3086
        except:  #line:3087
            return public.returnMsg(False, '目录创建失败!')  #line:3088

    def updateFtp(OOO000OOOOOOO0O00, O000000O0O0OOO000):  #line:3091
        try:  #line:3092
            O0OO00OO0O0OOO0OO = OOO000OOOOOOO0O00.connentFtp()  #line:3093
            OOO000O0O00000OO0 = 1024  #line:3094
            OOOO0O00O0000OOO0 = open(O000000O0O0OOO000, 'rb')  #line:3095
            O0OO00OO0O0OOO0OO.storbinary(
                'STOR %s' % os.path.basename(O000000O0O0OOO000),
                OOOO0O00O0000OOO0, OOO000O0O00000OO0)  #line:3096
            OOOO0O00O0000OOO0.close()  #line:3097
            O0OO00OO0O0OOO0OO.quit()  #line:3098
        except:  #line:3099
            if os.path.exists(O000000O0O0OOO000):
                os.remove(O000000O0O0OOO000)  #line:3100
            print('连接服务器失败!')  #line:3101
            return {'status': False, 'msg': '连接服务器失败!'}  #line:3102

    def upload_file_by_path(O0O0OOO0O00OO000O, O0O0OO0OOOOOO0000,
                            O000O0O00O0OOOO00):  #line:3105
        try:  #line:3106
            O000OO000000000OO = O0O0OOO0O00OO000O.connentFtp()  #line:3107
            OO0O0O0O00000000O = O0O0OOO0O00OO000O.get_config(None)[
                3]  #line:3108
            OO000O0OO00O0O0O0 = public.dict_obj()  #line:3109
            if O000O0O00O0OOOO00[0] == "/":  #line:3110
                O000O0O00O0OOOO00 = O000O0O00O0OOOO00[1:]  #line:3111
            OO000O0OO00O0O0O0.path = OO0O0O0O00000000O  #line:3112
            OO000O0OO00O0O0O0.dirname = os.path.dirname(
                O000O0O00O0OOOO00)  #line:3113
            O0O0OOO0O00OO000O.createDir(OO000O0OO00O0O0O0)  #line:3114
            OOOOO00OO0O000000 = os.path.join(
                OO0O0O0O00000000O,
                os.path.dirname(O000O0O00O0OOOO00))  #line:3115
            print("目标上传目录：{}".format(OOOOO00OO0O000000))  #line:3116
            O000OO000000000OO.cwd(OOOOO00OO0O000000)  #line:3117
            OOO0OOOO0O000O0OO = 1024  #line:3118
            OO0000O00O0O000O0 = open(O0O0OO0OOOOOO0000, 'rb')  #line:3119
            try:  #line:3120
                O000OO000000000OO.storbinary(
                    'STOR %s' % OOOOO00OO0O000000 + '/' +
                    os.path.basename(O0O0OO0OOOOOO0000), OO0000O00O0O000O0,
                    OOO0OOOO0O000O0OO)  #line:3121
            except:  #line:3122
                O000OO000000000OO.storbinary(
                    'STOR %s' % os.path.split(O0O0OO0OOOOOO0000)[1],
                    OO0000O00O0O000O0, OOO0OOOO0O000O0OO)  #line:3123
            OO0000O00O0O000O0.close()  #line:3124
            O000OO000000000OO.quit()  #line:3125
            return True  #line:3126
        except:  #line:3127
            print(public.get_error_info())  #line:3128
            return False  #line:3129

    def deleteFtp(OOOO000O0O00O0OO0,
                  OOOOOO000OOOOOOO0,
                  is_inc=False):  #line:3132
        O0OOO0000OOO0O0OO = []  #line:3133
        if os.path.isfile(main()._full_file):  #line:3134
            try:  #line:3135
                O0OOO0000OOO0O0OO = json.loads(
                    public.readFile(main()._full_file))[0]  #line:3136
            except:  #line:3137
                O0OOO0000OOO0O0OO = []  #line:3138
        try:  #line:3139
            OO000O00O0O000OOO = OOOO000O0O00O0OO0.connentFtp()  #line:3140
            if is_inc:  #line:3141
                try:  #line:3142
                    OO0O0O0O0O0OOO0O0 = OO000O00O0O000OOO.nlst()  #line:3143
                    for OOOO000OOOOO000O0 in OO0O0O0O0O0OOO0O0:  #line:3152
                        if OOOO000OOOOO000O0 == '.' or OOOO000OOOOO000O0 == '..':
                            continue  #line:3153
                        if OOOO000OOOOO000O0 == 'full_record.json':
                            continue  #line:3154
                        if O0OOO0000OOO0O0OO and 'full_name' in O0OOO0000OOO0O0OO and os.path.basename(
                                O0OOO0000OOO0O0OO['full_name']
                        ) == OOOO000OOOOO000O0:
                            continue  #line:3155
                        try:  #line:3156
                            OO000O00O0O000OOO.rmd(
                                OOOO000OOOOO000O0)  #line:3157
                        except:  #line:3158
                            OO000O00O0O000OOO.delete(
                                OOOO000OOOOO000O0)  #line:3159
                        print('|-已从FTP存储空间清理过期备份文件{}'.format(
                            OOOO000OOOOO000O0))  #line:3160
                    return True  #line:3161
                except Exception as OO00O00000O000O00:  #line:3162
                    print(OO00O00000O000O00)  #line:3163
                    return False  #line:3164
            try:  #line:3165
                OO000O00O0O000OOO.rmd(OOOOOO000OOOOOOO0)  #line:3166
            except:  #line:3167
                OO000O00O0O000OOO.delete(OOOOOO000OOOOOOO0)  #line:3168
            print(
                '|-已从FTP存储空间清理过期备份文件{}'.format(OOOOOO000OOOOOOO0))  #line:3169
            return True  #line:3170
        except Exception as OO000OO0O0OOO00O0:  #line:3171
            print(OO000OO0O0OOO00O0)  #line:3172
            return False  #line:3173

    def remove_file(OOOOO0O0000OOO0O0, OO0O0O0OO0O0O0000):  #line:3176
        O0000OOOO0O000O0O = OOOOO0O0000OOO0O0.get_config(None)[3]  #line:3177
        if OO0O0O0OO0O0O0000.path[0] == "/":  #line:3178
            OO0O0O0OO0O0O0000.path = OO0O0O0OO0O0O0000.path[1:]  #line:3179
        OOOOO0O0000OOO0O0.__OOO000OO000OOO000 = os.path.join(
            O0000OOOO0O000O0O, OO0O0O0OO0O0O0000.path)  #line:3180
        if 'is_inc' not in OO0O0O0OO0O0O0000 and OOOOO0O0000OOO0O0.deleteFtp(
                OO0O0O0OO0O0O0000.filename):  #line:3181
            return public.returnMsg(True, '删除成功!')  #line:3182
        if 'is_inc' in OO0O0O0OO0O0O0000 and OO0O0O0OO0O0O0000.is_inc:  #line:3183
            if OOOOO0O0000OOO0O0.deleteFtp(OO0O0O0OO0O0O0000.filename,
                                           True):  #line:3184
                return public.returnMsg(True, '删除成功!')  #line:3185
        return public.returnMsg(False, '删除失败!')  #line:3186

    def get_list(OO00OO000O0O00OOO, get=None):  #line:3189
        try:  #line:3190
            OO00OO000O0O00OOO.__OOO000OO000OOO000 = get.path  #line:3191
            O00O000000O0OO00O = OO00OO000O0O00OOO.connentFtp()  #line:3192
            O000OOOOO0OOOO0OO = O00O000000O0OO00O.nlst()  #line:3193
            OOO000000000000O0 = []  #line:3195
            OOO0O000OOO00O000 = []  #line:3196
            O00OO00OOO0OO0O00 = []  #line:3197
            for OOO0000OOOOOO0O0O in O000OOOOO0OOOO0OO:  #line:3198
                if OOO0000OOOOOO0O0O == '.' or OOO0000OOOOOO0O0O == '..':
                    continue  #line:3199
                O0O0OOO000O00O0O0 = public.M('backup').where(
                    'name=?', (OOO0000OOOOOO0O0O,
                               )).field('size,addtime').find()  #line:3200
                if not O0O0OOO000O00O0O0:  #line:3201
                    O0O0OOO000O00O0O0 = {}  #line:3202
                    O0O0OOO000O00O0O0[
                        'addtime'] = '1970/01/01 00:00:01'  #line:3203
                OO00OOOO00O000OO0 = {}  #line:3204
                OO00OOOO00O000OO0['name'] = OOO0000OOOOOO0O0O  #line:3205
                OO00OOOO00O000OO0['time'] = int(
                    time.mktime(
                        time.strptime(O0O0OOO000O00O0O0['addtime'],
                                      '%Y/%m/%d %H:%M:%S')))  #line:3206
                try:  #line:3207
                    OO00OOOO00O000OO0['size'] = O00O000000O0OO00O.size(
                        OOO0000OOOOOO0O0O)  #line:3208
                    OO00OOOO00O000OO0['dir'] = False  #line:3209
                    OO00OOOO00O000OO0['download'] = OO00OO000O0O00OOO.getFile(
                        OOO0000OOOOOO0O0O)  #line:3210
                    OOO0O000OOO00O000.append(OO00OOOO00O000OO0)  #line:3211
                except:  #line:3212
                    OO00OOOO00O000OO0['size'] = 0  #line:3213
                    OO00OOOO00O000OO0['dir'] = True  #line:3214
                    OO00OOOO00O000OO0['download'] = ''  #line:3215
                    OOO000000000000O0.append(OO00OOOO00O000OO0)  #line:3216
            O00OO00OOO0OO0O00 = OOO000000000000O0 + OOO0O000OOO00O000  #line:3218
            OOOOOOOOOO0O0O0OO = {}  #line:3219
            OOOOOOOOOO0O0O0OO[
                'path'] = OO00OO000O0O00OOO.__OOO000OO000OOO000  #line:3220
            OOOOOOOOOO0O0O0OO['list'] = O00OO00OOO0OO0O00  #line:3221
            return OOOOOOOOOO0O0O0OO  #line:3222
        except Exception as OO00OO00O00O0OOOO:  #line:3223
            return {'status': False, 'msg': str(OO00OO00O00O0OOOO)}  #line:3224

    def getFile(OO0OO0O0O0O0OOO00, OO0O0O0OO0O0O0O00):  #line:3227
        try:  #line:3228
            O0OO0O00O0000OOO0 = OO0OO0O0O0O0OOO00.get_config()  #line:3229
            if O0OO0O00O0000OOO0[0].find(':') == -1:
                O0OO0O00O0000OOO0[0] += ':21'  #line:3230
            OOOOOOO0000O0O000 = O0OO0O00O0000OOO0[0].split(':')  #line:3231
            if OOOOOOO0000O0O000[1] == '':
                OOOOOOO0000O0O000[1] = '21'  #line:3232
            OOOOO000O00OOO0OO = 'ftp://' + O0OO0O00O0000OOO0[
                1] + ':' + O0OO0O00O0000OOO0[2] + '@' + OOOOOOO0000O0O000[
                    0] + ':' + OOOOOOO0000O0O000[1] + (
                        OO0OO0O0O0O0OOO00.__OOO000OO000OOO000 + '/' +
                        OO0O0O0OO0O0O0O00).replace('//', '/')  #line:3233
        except:  #line:3234
            OOOOO000O00OOO0OO = None  #line:3235
        return OOOOO000O00OOO0OO  #line:3236

    def download_file(OOO0O0OOOOOO0O0OO, OOOO00OO0OO0OOOO0):  #line:3239
        return OOO0O0OOOOOO0O0OO.getFile(OOOO00OO0OO0OOOO0)  #line:3240


class qiniu_main:  #line:3244
    __OOO0O00000OO000O0 = None  #line:3245
    __O000OOO00OOO0O000 = None  #line:3246
    __OOO0OOOOO00O0O0O0 = None  #line:3247
    __OO0OOO0000OO000O0 = None  #line:3248
    __O0000OO0OO0OO0OO0 = "ERROR: 无法连接到七牛云OSS服务器，请检查[AccessKeyId/AccessKeySecret]设置是否正确!"  #line:3249

    def __init__(O0O00000OO0O0O00O):  #line:3251
        O0O00000OO0O0O00O.__O00O0O0OO0O0OOOO0()  #line:3252

    def __O00O0O0OO0O0OOOO0(OOO0O0000OO0O000O):  #line:3254
        if OOO0O0000OO0O000O.__OOO0O00000OO000O0: return  #line:3255
        OO00000000OOO00OO = OOO0O0000OO0O000O.get_config()  #line:3257
        OOO0O0000OO0O000O.__O000OOO00OOO0O000 = OO00000000OOO00OO[
            3]  #line:3259
        if OO00000000OOO00OO[2].find(OO00000000OOO00OO[3]) != -1:
            OO00000000OOO00OO[2] = OO00000000OOO00OO[2].replace(
                OO00000000OOO00OO[3] + '.', '')  #line:3260
        OOO0O0000OO0O000O.__OOO0OOOOO00O0O0O0 = OO00000000OOO00OO[
            2]  #line:3261
        OOO0O0000OO0O000O.__OO0OOO0000OO000O0 = main().get_path(
            OO00000000OOO00OO[4] + '/bt_backup/')  #line:3262
        if OOO0O0000OO0O000O.__OO0OOO0000OO000O0[:1] == '/':
            OOO0O0000OO0O000O.__OO0OOO0000OO000O0 = OOO0O0000OO0O000O.__OO0OOO0000OO000O0[
                1:]  #line:3263
        try:  #line:3265
            OOO0O0000OO0O000O.__OOO0O00000OO000O0 = Auth(
                OO00000000OOO00OO[0], OO00000000OOO00OO[1])  #line:3267
        except Exception as OO0O0OOOO0OOO000O:  #line:3268
            pass  #line:3269

    def get_config(O000O0OO0OO00OO0O, get=None):  #line:3272
        return main().get_config('qiniu')  #line:3273

    def set_config(OOOOOO0O0OO00O00O, O00OO0O00OOO0O0O0):  #line:3277
        OO0O0OO00OO0OOOO0 = ['qiniu', 'txcos', 'alioss', 'bos', 'ftp',
                             'obs']  #line:3278
        OO00000O0O0O000O0 = O00OO0O00OOO0O0O0.get('cloud_name/d',
                                                  0)  #line:3279
        print(OO00000O0O0O000O0)  #line:3280
        if OO00000O0O0O000O0 not in OO0O0OO00OO0OOOO0:
            return public.returnMsg(False, '参数不合法！')  #line:3281
        OOOO0O000OOO00000 = main()._config_path + '/{}.conf'.format(
            OO00000O0O0O000O0)  #line:3282
        OOOO0OOO0000O0OO0 = O00OO0O00OOO0O0O0.access_key.strip(
        ) + '|' + O00OO0O00OOO0O0O0.secret_key.strip(
        ) + '|' + O00OO0O00OOO0O0O0.bucket_name.strip(
        ) + '|' + O00OO0O00OOO0O0O0.bucket_domain.strip(
        ) + '|' + O00OO0O00OOO0O0O0.bucket_path.strip()  #line:3284
        return public.returnMsg(True, '设置成功!')  #line:3286

    def check_config(O00O0OOO000000O00):  #line:3289
        try:  #line:3290
            O00OOO0OO000O0O0O = ''  #line:3291
            OOOO000O0O00O0OOO = O00O0OOO000000O00.get_bucket()  #line:3292
            OOOOOO0O00O0O00OO = '/'  #line:3293
            O0000O00000O0OO0O = None  #line:3294
            O0O0O00OOOO0O00OO = 1000  #line:3295
            O00OOO0OO000O0O0O = main().get_path(O00OOO0OO000O0O0O)  #line:3296
            OOOO00O0O00OO00O0, OO0OOO0O0000OO0O0, O000O0000O00O0OOO = OOOO000O0O00O0OOO.list(
                O00O0OOO000000O00.__O000OOO00OOO0O000, O00OOO0OO000O0O0O,
                O0000O00000O0OO0O, O0O0O00OOOO0O00OO,
                OOOOOO0O00O0O00OO)  #line:3297
            if OOOO00O0O00OO00O0:  #line:3298
                return True  #line:3299
            else:  #line:3300
                return False  #line:3301
        except:  #line:3302
            return False  #line:3303

    def get_bucket(OO0OO0000OO0O0O00):  #line:3305
        ""  #line:3306
        from qiniu import BucketManager  #line:3308
        O000O000000000O0O = BucketManager(
            OO0OO0000OO0O0O00.__OOO0O00000OO000O0)  #line:3309
        return O000O000000000O0O  #line:3310

    def create_dir(OO00OOOOOOO000OO0, O0O00OO000OOO0OOO):  #line:3312
        ""  #line:3317
        try:  #line:3319
            O0O00OO000OOO0OOO = main().get_path(O0O00OO000OOO0OOO)  #line:3320
            O00O0OO00O00O0O00 = '/tmp/dirname.pl'  #line:3321
            public.writeFile(O00O0OO00O00O0O00, '')  #line:3322
            OO0OOOOO000OO0O0O = OO00OOOOOOO000OO0.__OOO0O00000OO000O0.upload_token(
                OO00OOOOOOO000OO0.__O000OOO00OOO0O000,
                O0O00OO000OOO0OOO)  #line:3323
            OO0O00O0000O0OO0O, O0O000O0O0OOO00OO = put_file(
                OO0OOOOO000OO0O0O, O0O00OO000OOO0OOO,
                O00O0OO00O00O0O00)  #line:3324
            try:  #line:3326
                os.remove(O00O0OO00O00O0O00)  #line:3327
            except:  #line:3328
                pass  #line:3329
            if O0O000O0O0OOO00OO.status_code == 200:  #line:3331
                return True  #line:3332
            return False  #line:3333
        except Exception as O0000O0O000O0OOOO:  #line:3334
            raise RuntimeError("创建目录出现错误:" +
                               str(O0000O0O000O0OOOO))  #line:3335

    def get_list(OO0OOOOOO0OO0O0OO, get=None):  #line:3337
        O00O0OO00O0OO00O0 = OO0OOOOOO0OO0O0OO.get_bucket()  #line:3338
        O00OO0O0O00OOO000 = '/'  #line:3339
        OOO0O00OOO00OO000 = None  #line:3340
        O0OOOOO0OO0O0OO00 = 1000  #line:3341
        OOO0OOO00OO0OO00O = main().get_path(get.path)  #line:3342
        O0OOO0O0OO00O0OO0, OOO0OOOO0OO0O0OO0, O0000O0OOO00O0OOO = O00O0OO00O0OO00O0.list(
            OO0OOOOOO0OO0O0OO.__O000OOO00OOO0O000, OOO0OOO00OO0OO00O,
            OOO0O00OOO00OO000, O0OOOOO0OO0O0OO00,
            O00OO0O0O00OOO000)  #line:3343
        OO000000OO00O0OO0 = []  #line:3344
        if O0OOO0O0OO00O0OO0:  #line:3345
            OOO00OO00O0O00OOO = O0OOO0O0OO00O0OO0.get(
                "commonPrefixes")  #line:3346
            if OOO00OO00O0O00OOO:  #line:3347
                for OO00O0OOOOOOOO000 in OOO00OO00O0O00OOO:  #line:3348
                    O0OOO0OOOOO0O0OOO = {}  #line:3349
                    O00O0OOO00O0O00O0 = OO00O0OOOOOOOO000.replace(
                        OOO0OOO00OO0OO00O, '')  #line:3350
                    O0OOO0OOOOO0O0OOO['name'] = O00O0OOO00O0O00O0  #line:3351
                    O0OOO0OOOOO0O0OOO['type'] = None  #line:3352
                    OO000000OO00O0OO0.append(O0OOO0OOOOO0O0OOO)  #line:3353
            OO0O00OOOO0OO0000 = O0OOO0O0OO00O0OO0['items']  #line:3355
            for O0OO000000O0OO00O in OO0O00OOOO0OO0000:  #line:3356
                O0OOO0OOOOO0O0OOO = {}  #line:3357
                O00O0OOO00O0O00O0 = O0OO000000O0OO00O.get("key")  #line:3358
                O00O0OOO00O0O00O0 = O00O0OOO00O0O00O0.replace(
                    OOO0OOO00OO0OO00O, '')  #line:3359
                if not O00O0OOO00O0O00O0:  #line:3360
                    continue  #line:3361
                O0OOO0OOOOO0O0OOO['name'] = O00O0OOO00O0O00O0  #line:3362
                O0OOO0OOOOO0O0OOO['size'] = O0OO000000O0OO00O.get(
                    "fsize")  #line:3363
                O0OOO0OOOOO0O0OOO['type'] = O0OO000000O0OO00O.get(
                    "type")  #line:3364
                O0OOO0OOOOO0O0OOO['time'] = O0OO000000O0OO00O.get(
                    "putTime")  #line:3365
                O0OOO0OOOOO0O0OOO[
                    'download'] = OO0OOOOOO0OO0O0OO.generate_download_url(
                        OOO0OOO00OO0OO00O + O00O0OOO00O0O00O0)  #line:3366
                OO000000OO00O0OO0.append(O0OOO0OOOOO0O0OOO)  #line:3367
        else:  #line:3368
            if hasattr(O0000O0OOO00O0OOO, "error"):  #line:3369
                raise RuntimeError(O0000O0OOO00O0OOO.error)  #line:3370
        OO00OOO0OOOO00OOO = {
            'path': OOO0OOO00OO0OO00O,
            'list': OO000000OO00O0OO0
        }  #line:3371
        return OO00OOO0OOOO00OOO  #line:3372

    def generate_download_url(OO00OO000OOOOO0OO,
                              O000O0OOO00OO0O00,
                              expires=60 * 60):  #line:3374
        ""  #line:3375
        OOOOOOO0OO0OO000O = OO00OO000OOOOO0OO.__OOO0OOOOO00O0O0O0  #line:3376
        O0000OOOOO00OOO0O = 'http://%s/%s' % (
            OOOOOOO0OO0OO000O, O000O0OOO00OO0O00)  #line:3377
        O00O0OO0O0OOOO0OO = OO00OO000OOOOO0OO.__OOO0O00000OO000O0.private_download_url(
            O0000OOOOO00OOO0O, expires=expires)  #line:3378
        return O00O0OO0O0OOOO0OO  #line:3379

    def resumable_upload(O000OO0OOO0OO0000,
                         O00000OO0OOO000OO,
                         OOO0OO00OO00OO000,
                         object_name=None,
                         progress_callback=None,
                         progress_file_name=None,
                         retries=5):  #line:3381
        ""  #line:3390
        try:  #line:3392
            O000000O00OO000OO = 60 * 60  #line:3393
            if object_name is None:  #line:3395
                OO00OOO00O00OOOOO, OO00O0OOO00O0O000 = os.path.split(
                    O00000OO0OOO000OO)  #line:3396
                O000OO0OOO0OO0000.__OO0OOO0000OO000O0 = main().get_path(
                    os.path.dirname(OOO0OO00OO00OO000))  #line:3397
                OO00O0OOO00O0O000 = O000OO0OOO0OO0000.__OO0OOO0000OO000O0 + '/' + OO00O0OOO00O0O000  #line:3398
                OO00O0OOO00O0O000 = OO00O0OOO00O0O000.replace('//',
                                                              '/')  #line:3399
                object_name = OO00O0OOO00O0O000  #line:3400
            O0OO000000O0O0OO0 = O000OO0OOO0OO0000.__OOO0O00000OO000O0.upload_token(
                O000OO0OOO0OO0000.__O000OOO00OOO0O000, object_name,
                O000000O00OO000OO)  #line:3401
            if object_name[:1] == "/":  #line:3403
                object_name = object_name[1:]  #line:3404
            print("|-正在上传{}到七牛云存储".format(object_name), end='')  #line:3406
            OO0O00OO00OOO0O0O, OOO0O0OO0OOO00O0O = put_file(
                O0OO000000O0O0OO0,
                object_name,
                O00000OO0OOO000OO,
                check_crc=True,
                progress_handler=progress_callback,
                bucket_name=O000OO0OOO0OO0000.__O000OOO00OOO0O000,
                part_size=1024 * 1024 * 4,
                version="v2")  #line:3414
            OO00O000OOOOOO000 = False  #line:3415
            if sys.version_info[0] == 2:  #line:3416
                OO00O000OOOOOO000 = OO0O00OO00OOO0O0O['key'].encode(
                    'utf-8') == object_name  #line:3417
            elif sys.version_info[0] == 3:  #line:3418
                OO00O000OOOOOO000 = OO0O00OO00OOO0O0O[
                    'key'] == object_name  #line:3419
            if OO00O000OOOOOO000:  #line:3420
                print(' ==> 成功')  #line:3421
                return OO0O00OO00OOO0O0O['hash'] == etag(
                    O00000OO0OOO000OO)  #line:3422
            return False  #line:3423
        except Exception as OO0O0OOO0OOOO0O0O:  #line:3424
            print("文件上传出现错误：", str(OO0O0OOO0OOOO0O0O))  #line:3425
        if retries > 0:  #line:3428
            print("重试上传文件....")  #line:3429
            return O000OO0OOO0OO0000.resumable_upload(
                O00000OO0OOO000OO,
                OOO0OO00OO00OO000,
                object_name=object_name,
                progress_callback=progress_callback,
                progress_file_name=progress_file_name,
                retries=retries - 1,
            )  #line:3437
        return False  #line:3438

    def upload_file_by_path(OO00000O00000OO00, O0000O00OOO0OOO0O,
                            OO0OO0OOOO000OOO0):  #line:3441
        return OO00000O00000OO00.resumable_upload(
            O0000O00OOO0OOO0O, OO0OO0OOOO000OOO0)  #line:3442

    def delete_object_by_os(O000OO00O00OO0000, O0O0000O0OOOO0O00):  #line:3444
        ""  #line:3445
        O00O0O0O0OOOO0000 = O000OO00O00OO0000.get_bucket()  #line:3447
        O00000O000OOOOO0O, OO0O000O00O0OO000 = O00O0O0O0OOOO0000.delete(
            O000OO00O00OO0000.__O000OOO00OOO0O000,
            O0O0000O0OOOO0O00)  #line:3448
        return O00000O000OOOOO0O == {}  #line:3449

    def get_object_info(O000O000OOO00O0O0, O0O0OO00O0O0O0000):  #line:3451
        ""  #line:3452
        try:  #line:3453
            OO0OO0O00OOO0O00O = O000O000OOO00O0O0.get_bucket()  #line:3454
            OOOOOOO0O000OOO00 = OO0OO0O00OOO0O00O.stat(
                O000O000OOO00O0O0.__O000OOO00OOO0O000,
                O0O0OO00O0O0O0000)  #line:3455
            return OOOOOOO0O000OOO00[0]  #line:3456
        except:  #line:3457
            return None  #line:3458

    def remove_file(OOO0O0O0O0O00O000, OOOOOOO0OOO0O00OO):  #line:3462
        try:  #line:3463
            OO00O0OOO00O0O00O = OOOOOOO0OOO0O00OO.filename  #line:3464
            O0OO0O0O0O0O00OOO = OOOOOOO0OOO0O00OO.path  #line:3465
            if O0OO0O0O0O0O00OOO[-1] != "/":  #line:3467
                O000OO000O00000O0 = O0OO0O0O0O0O00OOO + "/" + OO00O0OOO00O0O00O  #line:3468
            else:  #line:3469
                O000OO000O00000O0 = O0OO0O0O0O0O00OOO + OO00O0OOO00O0O00O  #line:3470
            if O000OO000O00000O0[-1] == "/":  #line:3472
                return public.returnMsg(False, "暂时不支持目录删除！")  #line:3473
            if O000OO000O00000O0[:1] == "/":  #line:3475
                O000OO000O00000O0 = O000OO000O00000O0[1:]  #line:3476
            if OOO0O0O0O0O00O000.delete_object_by_os(
                    O000OO000O00000O0):  #line:3478
                return public.returnMsg(True, '删除成功')  #line:3479
            return public.returnMsg(False, '文件{}删除失败, path:{}'.format(
                O000OO000O00000O0, OOOOOOO0OOO0O00OO.path))  #line:3480
        except:  #line:3481
            print(OOO0O0O0O0O00O000.__O0000OO0OO0OO0OO0)  #line:3482
            return False  #line:3483


class aws_main:  #line:3487
    pass  #line:3488


class upyun_main:  #line:3490
    pass  #line:3491


class obs_main:  #line:3493
    __OO0000O0000OOO00O = None  #line:3494
    __OOO0O00000OOO0O00 = None  #line:3495
    __O0000OO0000O0O000 = 0  #line:3496
    __OO0OO000O0O0000O0 = None  #line:3497
    __O0OOO0000OOO0O00O = None  #line:3498
    __O0O0O0O0O0000O0O0 = None  #line:3499
    __OO000OO00O0O0O0O0 = None  #line:3500
    __OOO0000OO00O0O0O0 = "ERROR: 无法连接华为云OBS !"  #line:3501

    def __init__(O0OO00O000O00OOO0):  #line:3504
        O0OO00O000O00OOO0.__OOO0OO0O00OOOO0O0()  #line:3505

    def __OOO0OO0O00OOOO0O0(O0O0O0OO0O0000OO0):  #line:3507
        ""  #line:3510
        if O0O0O0OO0O0000OO0.__OO0000O0000OOO00O: return  #line:3511
        OO000OOO00OO0O000 = O0O0O0OO0O0000OO0.get_config()  #line:3513
        O0O0O0OO0O0000OO0.__OO0OO000O0O0000O0 = OO000OOO00OO0O000[
            0]  #line:3514
        O0O0O0OO0O0000OO0.__O0OOO0000OOO0O00O = OO000OOO00OO0O000[
            1]  #line:3515
        O0O0O0OO0O0000OO0.__O0O0O0O0O0000O0O0 = OO000OOO00OO0O000[
            3]  #line:3516
        O0O0O0OO0O0000OO0.__OO000OO00O0O0O0O0 = OO000OOO00OO0O000[
            2]  #line:3517
        O0O0O0OO0O0000OO0.__OOO0O00000OOO0O00 = main().get_path(
            OO000OOO00OO0O000[4])  #line:3518
        try:  #line:3519
            O0O0O0OO0O0000OO0.__OO0000O0000OOO00O = ObsClient(
                access_key_id=O0O0O0OO0O0000OO0.__OO0OO000O0O0000O0,
                secret_access_key=O0O0O0OO0O0000OO0.__O0OOO0000OOO0O00O,
                server=O0O0O0OO0O0000OO0.__OO000OO00O0O0O0O0,
            )  #line:3525
        except Exception as O0O0O00OOOOOOO0OO:  #line:3526
            pass  #line:3527

    def get_config(O00O0O0000000OO0O, get=None):  #line:3531
        ""  #line:3534
        return main().get_config('obs')  #line:3535

    def check_config(O0OOO0O00000O0000):  #line:3538
        try:  #line:3539
            O0OO0OO0O0O000O00 = []  #line:3540
            OO00000OOO0O000OO = main().get_path('/')  #line:3541
            O0OO00000000O0O00 = O0OOO0O00000O0000.__OO0000O0000OOO00O.listObjects(
                O0OOO0O00000O0000.__O0O0O0O0O0000O0O0,
                prefix=OO00000OOO0O000OO,
            )  #line:3545
            for OOOOO0O00000OOO0O in O0OO00000000O0O00.body.contents:  #line:3547
                if OOOOO0O00000OOO0O.size != 0:  #line:3548
                    if not OOOOO0O00000OOO0O.key:
                        continue
                        #line:3549
                    O00OOO0O0OOO00O0O = {}  #line:3550
                    OO0OOO000O000O0O0 = OOOOO0O00000OOO0O.key  #line:3551
                    OO0OOO000O000O0O0 = OO0OOO000O000O0O0[
                        OO0OOO000O000O0O0.find(OO00000OOO0O000OO) +
                        len(OO00000OOO0O000OO):]  #line:3552
                    O0OO0OOO0OOOO000O = OOOOO0O00000OOO0O.key.split(
                        '/')  #line:3553
                    if len(O0OO0OOO0OOOO000O) > 1000000:
                        continue
                        #line:3554
                    OOOOO0OOO0OO000O0 = re.compile(r'/')  #line:3555
                    if OOOOO0OOO0OO000O0.search(OO0OOO000O000O0O0) != None:
                        continue
                        #line:3556
                    O00OOO0O0OOO00O0O["type"] = True  #line:3557
                    O00OOO0O0OOO00O0O["name"] = OO0OOO000O000O0O0  #line:3558
                    O00OOO0O0OOO00O0O[
                        'size'] = OOOOO0O00000OOO0O.size  #line:3559
                    OO0000OOOOO0OO0O0 = OOOOO0O00000OOO0O.lastModified  #line:3560
                    OO00OO000O0O0000O = datetime.datetime.strptime(
                        OO0000OOOOO0OO0O0, "%Y/%m/%d %H:%M:%S")  #line:3561
                    OO00OO000O0O0000O += datetime.timedelta(
                        hours=0)  #line:3562
                    OO0O0O0O000O0OOO0 = int((
                        time.mktime(OO00OO000O0O0000O.timetuple()) +
                        OO00OO000O0O0000O.microsecond / 1000000.0))  #line:3563
                    O00OOO0O0OOO00O0O['time'] = OO0O0O0O000O0OOO0  #line:3564
                    O0OO0OO0O0O000O00.append(O00OOO0O0OOO00O0O)  #line:3565
                elif OOOOO0O00000OOO0O.size == 0:  #line:3566
                    if not OOOOO0O00000OOO0O.key:
                        continue
                        #line:3567
                    if OOOOO0O00000OOO0O.key[-1] != "/":
                        continue
                        #line:3568
                    O0OO0OOO0OOOO000O = OOOOO0O00000OOO0O.key.split(
                        '/')  #line:3569
                    O00OOO0O0OOO00O0O = {}  #line:3570
                    OO0OOO000O000O0O0 = OOOOO0O00000OOO0O.key  #line:3571
                    OO0OOO000O000O0O0 = OO0OOO000O000O0O0[
                        OO0OOO000O000O0O0.find(OO00000OOO0O000OO) +
                        len(OO00000OOO0O000OO):]  #line:3572
                    if OO00000OOO0O000OO == "" and len(O0OO0OOO0OOOO000O) > 2:
                        continue
                        #line:3573
                    if OO00000OOO0O000OO != "":  #line:3574
                        O0OO0OOO0OOOO000O = OO0OOO000O000O0O0.split(
                            '/')  #line:3575
                        if len(O0OO0OOO0OOOO000O) > 2:
                            continue
                            #line:3576
                        else:  #line:3577
                            OO0OOO000O000O0O0 = OO0OOO000O000O0O0  #line:3578
                    if not OO0OOO000O000O0O0:
                        continue
                        #line:3579
                    O00OOO0O0OOO00O0O["type"] = None  #line:3580
                    O00OOO0O0OOO00O0O["name"] = OO0OOO000O000O0O0  #line:3581
                    O00OOO0O0OOO00O0O[
                        'size'] = OOOOO0O00000OOO0O.size  #line:3582
                    O0OO0OO0O0O000O00.append(O00OOO0O0OOO00O0O)  #line:3583
            return True  #line:3584
        except:  #line:3585
            return False  #line:3586

    def upload_file_by_path(O000O0OO000OOO0OO, OOOOO000OOOOOOO0O,
                            OOOO0OO0O00O00000):  #line:3588
        ""  #line:3593
        O000O0OO000OOO0OO.__OOO0OO0O00OOOO0O0()  #line:3595
        if not O000O0OO000OOO0OO.__OO0000O0000OOO00O:  #line:3596
            return False  #line:3597
        if OOOO0OO0O00O00000 != None:  #line:3599
            OOO00O00O0OO0OOOO = O000O0OO000OOO0OO.__OO0000O0000OOO00O.listObjects(
                O000O0OO000OOO0OO.__O0O0O0O0O0000O0O0,
                prefix="",
            )  #line:3603
            O00OO0O000OOOOO0O = OOOO0OO0O00O00000.split("/")  #line:3604
            OO00OO0OO00O00O00 = ""  #line:3605
            O00OO0000OO00O0O0 = []  #line:3606
            for OO0O000O0OO000000 in OOO00O00O0OO0OOOO.body.contents:  #line:3607
                if not OO0O000O0OO000000.key: continue  #line:3608
                O00OO0000OO00O0O0.append(OO0O000O0OO000000.key)  #line:3609
            for OOOO000OOO000O00O in range(
                    0, (len(O00OO0O000OOOOO0O) - 1)):  #line:3610
                if OO00OO0OO00O00O00 == "":  #line:3611
                    OO00OO0OO00O00O00 = O00OO0O000OOOOO0O[
                        OOOO000OOO000O00O] + "/"  #line:3612
                else:  #line:3613
                    OO00OO0OO00O00O00 = OO00OO0OO00O00O00 + O00OO0O000OOOOO0O[
                        OOOO000OOO000O00O] + "/"  #line:3614
                if not OO00OO0OO00O00O00: continue  #line:3615
                if main().get_path(OO00OO0OO00O00O00
                                   ) not in O00OO0000OO00O0O0:  #line:3616
                    OOO00O00O0OO0OOOO = O000O0OO000OOO0OO.__OO0000O0000OOO00O.putContent(
                        O000O0OO000OOO0OO.__O0O0O0O0O0000O0O0,
                        objectKey=main().get_path(OO00OO0OO00O00O00),
                    )  #line:3620
        try:  #line:3622
            print('|-正在上传{}到华为云存储'.format(OOOOO000OOOOOOO0O),
                  end='')  #line:3623
            O0O0O000O00O000O0, O0O0O0OO000O0OOO0 = os.path.split(
                OOOOO000OOOOOOO0O)  #line:3624
            O000O0OO000OOO0OO.__OOO0O00000OOO0O00 = main().get_path(
                os.path.dirname(OOOO0OO0O00O00000))  #line:3625
            O0O0O0OO000O0OOO0 = O000O0OO000OOO0OO.__OOO0O00000OOO0O00 + O0O0O0OO000O0OOO0  #line:3626
            OO000000OOOOOOOOO = 5 * 1024 * 1024  #line:3627
            O0OOO00OO0000O0O0 = OOOOO000OOOOOOO0O  #line:3628
            O0000OOOO0O000OO0 = O0O0O0OO000O0OOO0  #line:3629
            O0000OOO0000OOO0O = True  #line:3630
            OOO00O00O0OO0OOOO = O000O0OO000OOO0OO.__OO0000O0000OOO00O.uploadFile(
                O000O0OO000OOO0OO.__O0O0O0O0O0000O0O0,
                O0000OOOO0O000OO0,
                O0OOO00OO0000O0O0,
                OO000000OOOOOOOOO,
                O0000OOO0000OOO0O,
            )  #line:3637
            if OOO00O00O0OO0OOOO.status < 300:  #line:3638
                print(' ==> 成功')  #line:3639
                return True  #line:3640
        except Exception as OO00OOOOOOO000O0O:  #line:3641
            time.sleep(1)  #line:3643
            O000O0OO000OOO0OO.__O0000OO0000O0O000 += 1  #line:3644
            if O000O0OO000OOO0OO.__O0000OO0000O0O000 < 2:  #line:3645
                O000O0OO000OOO0OO.upload_file_by_path(
                    OOOOO000OOOOOOO0O, OOOO0OO0O00O00000)  #line:3647
            return False  #line:3648

    def get_list(O0O0O000O00O0OOOO, get=None):  #line:3651
        ""  #line:3654
        O0O0O000O00O0OOOO.__OOO0OO0O00OOOO0O0()  #line:3656
        if not O0O0O000O00O0OOOO.__OO0000O0000OOO00O:  #line:3657
            return False  #line:3658
        OOO00O000O00OOOO0 = []  #line:3659
        OO0OO0OO00O0OO0OO = main().get_path(get.path)  #line:3660
        O00O0OO0OO0O0000O = O0O0O000O00O0OOOO.__OO0000O0000OOO00O.listObjects(
            O0O0O000O00O0OOOO.__O0O0O0O0O0000O0O0,
            prefix=OO0OO0OO00O0OO0OO,
        )  #line:3664
        for O0OOOO0O00OOO0O0O in O00O0OO0OO0O0000O.body.contents:  #line:3666
            if O0OOOO0O00OOO0O0O.size != 0:  #line:3667
                if not O0OOOO0O00OOO0O0O.key:
                    continue
                    #line:3668
                OO00O000OO0O00OOO = {}  #line:3669
                O0OO00O0OOOO0OOO0 = O0OOOO0O00OOO0O0O.key  #line:3670
                O0OO00O0OOOO0OOO0 = O0OO00O0OOOO0OOO0[
                    O0OO00O0OOOO0OOO0.find(OO0OO0OO00O0OO0OO) +
                    len(OO0OO0OO00O0OO0OO):]  #line:3671
                O00OO00OO0O00OO00 = O0OOOO0O00OOO0O0O.key.split(
                    '/')  #line:3672
                if len(O00OO00OO0O00OO00) > 1000000:
                    continue
                    #line:3673
                OO00O0OOOOOO0OOOO = re.compile(r'/')  #line:3674
                if OO00O0OOOOOO0OOOO.search(O0OO00O0OOOO0OOO0) != None:
                    continue
                    #line:3675
                OO00O000OO0O00OOO["type"] = True  #line:3676
                OO00O000OO0O00OOO["name"] = O0OO00O0OOOO0OOO0  #line:3677
                OO00O000OO0O00OOO['size'] = O0OOOO0O00OOO0O0O.size  #line:3678
                OO00O000OO0O00OOO[
                    'download'] = O0O0O000O00O0OOOO.download_file(
                        OO0OO0OO00O0OO0OO + O0OO00O0OOOO0OOO0)  #line:3679
                OOO000OOO0000000O = O0OOOO0O00OOO0O0O.lastModified  #line:3680
                OO000O0O00O0OOO0O = datetime.datetime.strptime(
                    OOO000OOO0000000O, "%Y/%m/%d %H:%M:%S")  #line:3681
                OO000O0O00O0OOO0O += datetime.timedelta(hours=0)  #line:3682
                OO0O000000OO0O0OO = int(
                    (time.mktime(OO000O0O00O0OOO0O.timetuple()) +
                     OO000O0O00O0OOO0O.microsecond / 1000000.0))  #line:3683
                OO00O000OO0O00OOO['time'] = OO0O000000OO0O0OO  #line:3684
                OOO00O000O00OOOO0.append(OO00O000OO0O00OOO)  #line:3685
            elif O0OOOO0O00OOO0O0O.size == 0:  #line:3686
                if not O0OOOO0O00OOO0O0O.key:
                    continue
                    #line:3687
                if O0OOOO0O00OOO0O0O.key[-1] != "/":
                    continue
                    #line:3688
                O00OO00OO0O00OO00 = O0OOOO0O00OOO0O0O.key.split(
                    '/')  #line:3689
                OO00O000OO0O00OOO = {}  #line:3690
                O0OO00O0OOOO0OOO0 = O0OOOO0O00OOO0O0O.key  #line:3691
                O0OO00O0OOOO0OOO0 = O0OO00O0OOOO0OOO0[
                    O0OO00O0OOOO0OOO0.find(OO0OO0OO00O0OO0OO) +
                    len(OO0OO0OO00O0OO0OO):]  #line:3692
                if OO0OO0OO00O0OO0OO == "" and len(O00OO00OO0O00OO00) > 2:
                    continue
                    #line:3693
                if OO0OO0OO00O0OO0OO != "":  #line:3694
                    O00OO00OO0O00OO00 = O0OO00O0OOOO0OOO0.split(
                        '/')  #line:3695
                    if len(O00OO00OO0O00OO00) > 2:
                        continue
                        #line:3696
                    else:  #line:3697
                        O0OO00O0OOOO0OOO0 = O0OO00O0OOOO0OOO0  #line:3698
                if not O0OO00O0OOOO0OOO0:
                    continue
                    #line:3699
                OO00O000OO0O00OOO["type"] = None  #line:3700
                OO00O000OO0O00OOO["name"] = O0OO00O0OOOO0OOO0  #line:3701
                OO00O000OO0O00OOO['size'] = O0OOOO0O00OOO0O0O.size  #line:3702
                OOO00O000O00OOOO0.append(OO00O000OO0O00OOO)  #line:3703
        O0O00O0O000O00O0O = {
            'path': OO0OO0OO00O0OO0OO,
            'list': OOO00O000O00OOOO0
        }  #line:3705
        return O0O00O0O000O00O0O  #line:3706

    def download_file(O000OO0OOO000OOO0, O0O0000000OO0OO0O):  #line:3708
        ""  #line:3711
        O000OO0OOO000OOO0.__OOO0OO0O00OOOO0O0()  #line:3713
        if not O000OO0OOO000OOO0.__OO0000O0000OOO00O:  #line:3714
            return None  #line:3715
        try:  #line:3716
            O00O000OOOOO0OOOO = O000OO0OOO000OOO0.__OO0000O0000OOO00O.createSignedUrl(
                'GET',
                O000OO0OOO000OOO0.__O0O0O0O0O0000O0O0,
                O0O0000000OO0OO0O,
                expires=3600,
            )  #line:3721
            O0O00O00O0OOOOO00 = O00O000OOOOO0OOOO.signedUrl  #line:3722
            return O0O00O00O0OOOOO00  #line:3723
        except:  #line:3724
            print(O000OO0OOO000OOO0.__OOO0000OO00O0O0O0)  #line:3725
            return None  #line:3726

    def delete_file(OO000000OOO00O0OO, OOO0000OO0OO0O000):  #line:3728
        ""  #line:3732
        OO000000OOO00O0OO.__OOO0OO0O00OOOO0O0()  #line:3734
        if not OO000000OOO00O0OO.__OO0000O0000OOO00O:  #line:3735
            return False  #line:3736
        try:  #line:3738
            O0000O0OOOOOOO0O0 = OO000000OOO00O0OO.__OO0000O0000OOO00O.deleteObject(
                OO000000OOO00O0OO.__O0O0O0O0O0000O0O0,
                OOO0000OO0OO0O000)  #line:3739
            return O0000O0OOOOOOO0O0  #line:3740
        except Exception as OO0OOO00O00000O0O:  #line:3741
            OO000000OOO00O0OO.__O0000OO0000O0O000 += 1  #line:3742
            if OO000000OOO00O0OO.__O0000OO0000O0O000 < 2:  #line:3743
                OO000000OOO00O0OO.delete_file(OOO0000OO0OO0O000)  #line:3745
            print(OO000000OOO00O0OO.__OOO0000OO00O0O0O0)  #line:3746
            return None  #line:3747

    def remove_file(OOO0OO00OO0O00OO0, O0O0OO0OOOOO0O000):  #line:3750
        O0OOO00O00O0O00OO = main().get_path(O0O0OO0OOOOO0O000.path)  #line:3751
        OO0O00OOO0O00OO0O = O0OOO00O00O0O00OO + O0O0OO0OOOOO0O000.filename  #line:3752
        OOO0OO00OO0O00OO0.delete_file(OO0O00OOO0O00OO0O)  #line:3753
        return public.returnMsg(True, '删除文件成功!')  #line:3754


class bos_main:  #line:3758
    __OO0000O00O0O0O00O = None  #line:3759
    __O0O0OO0O00OO00000 = 0  #line:3760
    __OOOO0OO00O00O0OO0 = None  #line:3761
    __O0OOO0OOOO00OO0OO = None  #line:3762
    __O000O0OO00O0OOO0O = None  #line:3763
    __OO0O00000OO0OOOO0 = "ERROR: 无法连接百度云存储 !"  #line:3764

    def __init__(OO0O0O0000O0O0O0O):  #line:3767
        OO0O0O0000O0O0O0O.__O0O0000OOOO0O00OO()  #line:3768

    def __O0O0000OOOO0O00OO(O00OO0OOOOO0OO000):  #line:3770
        ""  #line:3773
        if O00OO0OOOOO0OO000.__OO0000O00O0O0O00O: return  #line:3774
        O0000000O00000OOO = O00OO0OOOOO0OO000.get_config()  #line:3776
        O00OO0OOOOO0OO000.__OOOO0OO00O00O0OO0 = O0000000O00000OOO[
            0]  #line:3777
        O00OO0OOOOO0OO000.__O0OOO0OOOO00OO0OO = O0000000O00000OOO[
            1]  #line:3778
        O00OO0OOOOO0OO000.__OOO000OO00O0O00OO = O0000000O00000OOO[
            3]  #line:3779
        O00OO0OOOOO0OO000.__O000O0OO00O0OOO0O = O0000000O00000OOO[
            2]  #line:3780
        O00OO0OOOOO0OO000.__OO00OOO0OO00O00OO = main().get_path(
            O0000000O00000OOO[4])  #line:3782
        try:  #line:3783
            OOOO00000000O0OOO = BceClientConfiguration(
                credentials=BceCredentials(
                    O00OO0OOOOO0OO000.__OOOO0OO00O00O0OO0,
                    O00OO0OOOOO0OO000.__O0OOO0OOOO00OO0OO),
                endpoint=O00OO0OOOOO0OO000.__O000O0OO00O0OOO0O)  #line:3786
            O00OO0OOOOO0OO000.__OO0000O00O0O0O00O = BosClient(
                OOOO00000000O0OOO)  #line:3787
        except Exception as OO0O0OO00O00OOOO0:  #line:3788
            pass  #line:3789

    def get_config(O0OOO00O000O0O0OO, get=None):  #line:3792
        ""  #line:3795
        return main().get_config('bos')  #line:3796

    def check_config(O0O0O00000000O000):  #line:3800
        ""  #line:3803
        if not O0O0O00000000O000.__OO0000O00O0O0O00O: return False  #line:3804
        try:  #line:3805
            O0OO0OOO00O0OOO00 = '/'  #line:3806
            OO0O00000O000OOO0 = O0O0O00000000O000.__OO0000O00O0O0O00O.list_objects(
                O0O0O00000000O000.__OOO000OO00O0O00OO,
                prefix=O0OO0OOO00O0OOO00,
                delimiter="/")  #line:3808
            return True  #line:3809
        except:  #line:3810
            return False  #line:3811

    def resumable_upload(
        OO000OOOOO0O0O0OO,
        OO000O0O00O0O0OO0,
        object_name=None,
        progress_callback=None,
        progress_file_name=None,
        retries=5,
    ):  #line:3819
        ""  #line:3826
        try:  #line:3828
            if object_name[:1] == "/":  #line:3829
                object_name = object_name[1:]  #line:3830
            print("|-正在上传{}到百度云存储".format(object_name), end='')  #line:3831
            import multiprocessing  #line:3832
            OOO000O0O0O0OOOO0 = OO000O0O00O0O0OO0  #line:3833
            O0O00O0O0OOOO000O = object_name  #line:3834
            O00O0O0000O0OO0O0 = OO000OOOOO0O0O0OO.__OOO000OO00O0O00OO  #line:3835
            OO000000OO00O00O0 = OO000OOOOO0O0O0OO.__OO0000O00O0O0O00O.put_super_obejct_from_file(
                O00O0O0000O0OO0O0,
                O0O00O0O0OOOO000O,
                OOO000O0O0O0OOOO0,
                chunk_size=5,
                thread_num=multiprocessing.cpu_count() - 1)  #line:3840
            if OO000000OO00O00O0:  #line:3841
                print(' ==> 成功')  #line:3842
                return True  #line:3843
        except Exception as OOO0O0O0O0O0000OO:  #line:3844
            print("文件上传出现错误：")  #line:3845
            print(OOO0O0O0O0O0000OO)  #line:3846
        if retries > 0:  #line:3849
            print("重试上传文件....")  #line:3850
            return OO000OOOOO0O0O0OO.resumable_upload(
                OO000O0O00O0O0OO0,
                object_name=object_name,
                progress_callback=progress_callback,
                progress_file_name=progress_file_name,
                retries=retries - 1,
            )  #line:3857
        return False  #line:3858

    def upload_file_by_path(OOO000O0OOO000000, OO0O0OO00O0O0O0OO,
                            OOOO0OOO000OO00OO):  #line:3860
        ""  #line:3863
        return OOO000O0OOO000000.resumable_upload(
            OO0O0OO00O0O0O0OO, OOOO0OOO000OO00OO)  #line:3864

    def get_list(O0O0OO00OOO0000OO, get=None):  #line:3866
        O00O0OO0OOO0O00OO = []  #line:3867
        OOOO0OOOOO0OOO0O0 = []  #line:3868
        OOO00O0OO0OO0O00O = main().get_path(get.path)  #line:3869
        try:  #line:3870
            O0O0O00000OO000OO = O0O0OO00OOO0000OO.__OO0000O00O0O0O00O.list_objects(
                O0O0OO00OOO0000OO.__OOO000OO00O0O00OO,
                prefix=OOO00O0OO0OO0O00O,
                delimiter="/")  #line:3872
            for O0O00O0O0O0O0OO0O in O0O0O00000OO000OO.contents:  #line:3873
                if not O0O00O0O0O0O0OO0O.key: continue  #line:3874
                OO0OOO00000O000OO = {}  #line:3875
                OOOO0O00O00O00O0O = O0O00O0O0O0O0OO0O.key  #line:3876
                OOOO0O00O00O00O0O = OOOO0O00O00O00O0O[
                    OOOO0O00O00O00O0O.find(OOO00O0OO0OO0O00O) +
                    len(OOO00O0OO0OO0O00O):]  #line:3877
                if not OOOO0O00O00O00O0O: continue  #line:3878
                OO0OOO00000O000OO["name"] = OOOO0O00O00O00O0O  #line:3879
                OO0OOO00000O000OO['size'] = O0O00O0O0O0O0OO0O.size  #line:3880
                OO0OOO00000O000OO["type"] = True  #line:3881
                OO0OOO00000O000OO[
                    'download'] = O0O0OO00OOO0000OO.download_file(
                        OOO00O0OO0OO0O00O + "/" +
                        OOOO0O00O00O00O0O)  #line:3882
                OO000OO000000000O = O0O00O0O0O0O0OO0O.last_modified  #line:3883
                OO000000OOO0OOOO0 = datetime.datetime.strptime(
                    OO000OO000000000O, "%Y-%m-%dT%H:%M:%SZ")  #line:3884
                OO000000OOO0OOOO0 += datetime.timedelta(hours=8)  #line:3885
                O0O0OOOO000O00OO0 = int(
                    (time.mktime(OO000000OOO0OOOO0.timetuple()) +
                     OO000000OOO0OOOO0.microsecond / 1000000.0))  #line:3886
                OO0OOO00000O000OO['time'] = O0O0OOOO000O00OO0  #line:3887
                O00O0OO0OOO0O00OO.append(OO0OOO00000O000OO)  #line:3888
            for O00O00O00OOO000OO in O0O0O00000OO000OO.common_prefixes:  #line:3889
                if not O00O00O00OOO000OO.prefix: continue  #line:3890
                if O00O00O00OOO000OO.prefix[0:-1] == OOO00O0OO0OO0O00O:
                    continue  #line:3891
                OO0OOO00000O000OO = {}  #line:3892
                O00O00O00OOO000OO.prefix = O00O00O00OOO000OO.prefix.replace(
                    OOO00O0OO0OO0O00O, '')  #line:3893
                OO0OOO00000O000OO[
                    "name"] = O00O00O00OOO000OO.prefix  #line:3894
                OO0OOO00000O000OO["type"] = None  #line:3895
                OO0OOO00000O000OO['size'] = O00O00O00OOO000OO.size  #line:3896
                O00O0OO0OOO0O00OO.append(OO0OOO00000O000OO)  #line:3897
            O0000O0OO0O0O000O = {
                'path': OOO00O0OO0OO0O00O,
                'list': O00O0OO0OOO0O00OO
            }  #line:3898
            return O0000O0OO0O0O000O  #line:3899
        except:  #line:3900
            O0000O0OO0O0O000O = {}  #line:3901
            if O0O0OO00OOO0000OO.__OO0000O00O0O0O00O:  #line:3902
                O0000O0OO0O0O000O['status'] = True  #line:3903
            else:  #line:3904
                O0000O0OO0O0O000O['status'] = False  #line:3905
            O0000O0OO0O0O000O['path'] = get.path  #line:3906
            O0000O0OO0O0O000O['list'] = O00O0OO0OOO0O00OO  #line:3907
            O0000O0OO0O0O000O['dir'] = OOOO0OOOOO0OOO0O0  #line:3908
            return O0000O0OO0O0O000O  #line:3909

    def download_file(O00OO00000OOOOOO0, O0000OO000000OOOO):  #line:3911
        ""  #line:3914
        O00OO00000OOOOOO0.__O0O0000OOOO0O00OO()  #line:3916
        if not O00OO00000OOOOOO0.__OO0000O00O0O0O00O:  #line:3917
            return None  #line:3918
        try:  #line:3920
            OO00O00OOO0000OO0 = O00OO00000OOOOOO0.__OO0000O00O0O0O00O.generate_pre_signed_url(
                O00OO00000OOOOOO0.__OOO000OO00O0O00OO,
                O0000OO000000OOOO)  #line:3921
            _O000O0OOO0O00OO0O = sys.version_info  #line:3922
            OO0O0O0000O0OO0OO = (_O000O0OOO0O00OO0O[0] == 2)  #line:3924
            OOO00O00O00000OO0 = (_O000O0OOO0O00OO0O[0] == 3)  #line:3927
            if OOO00O00O00000OO0:  #line:3928
                OO00O00OOO0000OO0 = str(OO00O00OOO0000OO0,
                                        encoding="utf-8")  #line:3929
            else:  #line:3930
                OO00O00OOO0000OO0 = OO00O00OOO0000OO0  #line:3931
            return OO00O00OOO0000OO0  #line:3932
        except:  #line:3933
            print(O00OO00000OOOOOO0.__OO0O00000OO0OOOO0)  #line:3934
            return None  #line:3935

    def delete_file(O000O00OO00OOOO00, OO0000000000000OO):  #line:3937
        ""  #line:3941
        O000O00OO00OOOO00.__O0O0000OOOO0O00OO()  #line:3943
        if not O000O00OO00OOOO00.__OO0000O00O0O0O00O:  #line:3944
            return False  #line:3945
        try:  #line:3947
            O000OOOOOO0O0O000 = O000O00OO00OOOO00.__OO0000O00O0O0O00O.delete_object(
                O000O00OO00OOOO00.__OOO000OO00O0O00OO,
                OO0000000000000OO)  #line:3948
            return O000OOOOOO0O0O000  #line:3949
        except Exception as OOOO00OOOO0OOOOOO:  #line:3950
            O000O00OO00OOOO00.__O0O0OO0O00OO00000 += 1  #line:3951
            if O000O00OO00OOOO00.__O0O0OO0O00OO00000 < 2:  #line:3952
                O000O00OO00OOOO00.delete_file(OO0000000000000OO)  #line:3954
            print(O000O00OO00OOOO00.__OO0O00000OO0OOOO0)  #line:3955
            return None  #line:3956

    def remove_file(OOOOOOO000O0OOO00, O0OOO00O00OOO0OOO):  #line:3959
        O0O0O0OO0000000OO = main().get_path(O0OOO00O00OOO0OOO.path)  #line:3960
        OO0OO0O0O00O0O0O0 = O0O0O0OO0000000OO + O0OOO00O00OOO0OOO.filename  #line:3961
        OOOOOOO000O0OOO00.delete_file(OO0OO0O0O00O0O0O0)  #line:3962
        return public.returnMsg(True, '删除文件成功!')  #line:3963


class gcloud_storage_main:  #line:3966
    pass  #line:3967


class gdrive_main:  #line:3969
    pass  #line:3970


class msonedrive_main:  #line:3972
    pass  #line:3973


if __name__ == '__main__':  #line:3977
    import argparse  #line:3978
    args_obj = argparse.ArgumentParser(
        usage="必要的参数：--db_name 数据库名称!")  #line:3979
    args_obj.add_argument("--db_name", help="数据库名称!")  #line:3980
    args_obj.add_argument("--binlog_id", help="任务id")  #line:3981
    args = args_obj.parse_args()  #line:3982
    if not args.db_name:  #line:3983
        args_obj.print_help()  #line:3984
    p = main()  #line:3985
    p._db_name = args.db_name  #line:3986
    if args.binlog_id: p._binlog_id = args.binlog_id  #line:3987
    if p._binlog_id:  #line:3989
        p.execute_by_comandline()  #line:3990
