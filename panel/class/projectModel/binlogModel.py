import os, sys, time, json, re, datetime, shutil, threading  #line:13

os.chdir('/www/server/panel')  #line:15
sys.path.append("class/")  #line:16
import public  #line:17
from projectModel.base import projectBase  #line:18
from panelMysql import panelMysql  #line:19
from panelBackup import backup  #line:20
import db_mysql  #line:21


class main(projectBase):  #line:24
    _setup_path = '/www/server/panel/'  #line:25
    _binlog_id = ''  #line:26
    _db_name = ''  #line:27
    _zip_password = ''  #line:28
    _backup_end_time = ''  #line:29
    _backup_start_time = ''  #line:30
    _backup_type = ''  #line:31
    _cloud_name = ''  #line:32
    _full_zip_name = ''  #line:33
    _full_file = ''  #line:34
    _inc_file = ''  #line:35
    _file = ''  #line:36
    _pdata = {}  #line:37
    _echo_info = {}  #line:38
    _inode_min = 100  #line:39
    _temp_path = './temp/'  #line:40
    _tables = []  #line:41
    _new_tables = []  #line:42
    _backup_fail_list = []  #line:43
    _backup_full_list = []  #line:44
    _cloud_upload_not = []  #line:45
    _full_info = []  #line:46
    _inc_info = []  #line:47
    _mysql_bin_index = '/www/server/data/mysql-bin.index'  #line:48
    _save_cycle = 3600  #line:49
    _compress = True  #line:50
    _mysqlbinlog_bin = '/www/server/mysql/bin/mysqlbinlog'  #line:51
    _save_default_path = '/www/backup/mysql_bin_log/'  #line:52
    _mysql_root_password = public.M('config').where('id=?', (1, )).getField(
        'mysql_root')  #line:54
    _install_path = '{}script/binlog_cloud.sh'.format(_setup_path)  #line:55
    _config_path = '{}config/mysqlbinlog_info'.format(_setup_path)  #line:56
    _python_path = '{}pyenv/bin/python'.format(_setup_path)  #line:57
    _binlogModel_py = '{}class/projectModel/binlogModel.py'.format(
        _setup_path)  #line:58
    _mybackup = backup()  #line:59
    _plugin_path = '{}plugin/'.format(_setup_path)  #line:60
    _binlog_conf = '{}config/mysqlbinlog_info/binlog.conf'.format(
        _setup_path)  #line:61
    _start_time_list = []  #line:62
    _db_mysql = db_mysql.panelMysql()  #line:63

    def __init__(O00O000O0O000OOOO):  #line:65
        if not os.path.exists(O00O000O0O000OOOO._save_default_path):  #line:66
            os.makedirs(O00O000O0O000OOOO._save_default_path)  #line:67
        if not os.path.exists(O00O000O0O000OOOO._temp_path):  #line:68
            os.makedirs(O00O000O0O000OOOO._temp_path)  #line:69
        if not os.path.exists(O00O000O0O000OOOO._config_path):  #line:70
            os.makedirs(O00O000O0O000OOOO._config_path)  #line:71
        O00O000O0O000OOOO.create_table()  #line:72
        O00O000O0O000OOOO.kill_process()  #line:73

    def get_path(OOOOOO0OO0O00O00O, OOOO00OO0OO00000O):  #line:75
        ""  #line:79
        if OOOO00OO0OO00000O == '/': OOOO00OO0OO00000O = ''  #line:80
        if OOOO00OO0OO00000O[:1] == '/':  #line:81
            OOOO00OO0OO00000O = OOOO00OO0OO00000O[1:]  #line:82
            if OOOO00OO0OO00000O[-1:] != '/':
                OOOO00OO0OO00000O += '/'  #line:83
        return OOOO00OO0OO00000O.replace('//', '/')  #line:84

    def install_cloud_module(OO0OO0OOOO000OO00):  #line:86
        ""  #line:90
        O0O000O0OOO00OO00 = [
            "oss2", "cos-python-sdk-v5", "qiniu", "bce-python-sdk",
            "esdk-obs-python"
        ]  #line:94
        O0O000O0OOO00OO00 = [
            "oss2==2.5.0", "cos-python-sdk-v5==1.7.7", "qiniu==7.4.1 -I",
            "bce-python-sdk==0.8.62",
            "esdk-obs-python==3.21.8 --trusted-host pypi.org"
        ]  #line:99
        for OOO0OOO0OO0OO00O0 in O0O000O0OOO00OO00:  #line:100
            public.ExecShell('nohup btpip install {} >/dev/null 2>&1 &'.format(
                OOO0OOO0OO0OO00O0))  #line:102
            time.sleep(1)  #line:103

    def get_start_end_binlog(OO000O0O00OOO00O0,
                             O00OO000OOO0OOOO0,
                             OO0OOOO000OOO00O0,
                             is_backup=None):  #line:105
        ""  #line:112
        O0OOOO000O0O000OO = {}  #line:114
        OOO0OOOOOO0000O0O = [
            '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
            '22', '23'
        ]  #line:119
        O0OOOO000O0O000OO['start'] = OOO0OOOOOO0000O0O[(
            int(O00OO000OOO0OOOO0.split()[1].split(':')[0])):]  #line:121
        if is_backup:  #line:122
            O0OOOO000O0O000OO['end'] = OOO0OOOOOO0000O0O[:(
                int(OO0OOOO000OOO00O0.split()[1].split(':')[0]) +
                1)]  #line:124
        else:  #line:125
            O0OOOO000O0O000OO['end'] = OOO0OOOOOO0000O0O[:(
                int(OO0OOOO000OOO00O0.split()[1].split(':')[0]) +
                1)]  #line:127
        O0OOOO000O0O000OO['all'] = OOO0OOOOOO0000O0O  #line:128
        return O0OOOO000O0O000OO  #line:130

    def traverse_all_files(O00O0OO00OOOO0000, OOO000OOOOO0OOOOO,
                           OO00OOO00O0O00OOO, O000OO00OO000OO0O):  #line:132
        ""  #line:139
        OO0O0OO0O00OOOO00 = {}  #line:140
        OOO00O0O0OOOOO00O = []  #line:141
        O00OOOO000O00000O = []  #line:142
        for O0000OO0O00O00000 in range(0, len(OO00OOO00O0O00OOO)):  #line:143
            O00O000000O0O0OOO = OOO000OOOOO0OOOOO + OO00OOO00O0O00OOO[
                O0000OO0O00O00000] + '/'  #line:144
            O00O0OO00OO000OO0 = False  #line:145
            OO00OO000OO000O00 = False  #line:146
            if OO00OOO00O0O00OOO[O0000OO0O00O00000] == OO00OOO00O0O00OOO[
                    0]:  #line:147
                OO0O00O000OOOO0OO = O000OO00OO000OO0O['start']  #line:148
                O00O0OO00OO000OO0 = True  #line:149
            elif OO00OOO00O0O00OOO[O0000OO0O00O00000] == OO00OOO00O0O00OOO[
                    len(OO00OOO00O0O00OOO) - 1]:  #line:151
                OO0O00O000OOOO0OO = O000OO00OO000OO0O['end']  #line:152
                OO00OO000OO000O00 = True  #line:153
            else:  #line:154
                OO0O00O000OOOO0OO = O000OO00OO000OO0O['all']  #line:155
            if len(OO00OOO00O0O00OOO) == 1:  #line:157
                OO0O00O000OOOO0OO = sorted(
                    list(
                        set(O000OO00OO000OO0O['end']).intersection(
                            O000OO00OO000OO0O['start'])))  #line:161
                O00O0OO00OO000OO0 = True  #line:163
                OO00OO000OO000O00 = True  #line:164
            if OO0O00O000OOOO0OO:  #line:165
                OOO0000O00OOO0000 = O00O0OO00OOOO0000.splice_file_name(
                    O00O000000O0O0OOO, OO00OOO00O0O00OOO[O0000OO0O00O00000],
                    OO0O00O000OOOO0OO)  #line:168
                if O00O0OO00OO000OO0:  #line:169
                    OO0O0OO0O00OOOO00['first'] = OOO0000O00OOO0000[
                        0]  #line:170
                if OO00OO000OO000O00:  #line:171
                    OO0O0OO0O00OOOO00['last'] = OOO0000O00OOO0000[
                        len(OOO0000O00OOO0000) - 1]  #line:172
                O00OOOO000O00000O.append(OOO0000O00OOO0000)  #line:173
                O00OOO0O0O0O00OOO = O00O0OO00OOOO0000.check_foler_file(
                    OOO0000O00OOO0000)  #line:174
                if O00OOO0O0O0O00OOO:  #line:175
                    OOO00O0O0OOOOO00O.append(O00OOO0O0O0O00OOO)  #line:176
        OO0O0OO0O00OOOO00['data'] = O00OOOO000O00000O  #line:177
        OO0O0OO0O00OOOO00['file_lists_not'] = OOO00O0O0OOOOO00O  #line:178
        if OOO00O0O0OOOOO00O:  #line:179
            OO0O0OO0O00OOOO00['status'] = 'False'  #line:180
        else:  #line:181
            OO0O0OO0O00OOOO00['status'] = 'True'  #line:182
        return OO0O0OO0O00OOOO00  #line:183

    def get_mysql_port(O00O0O0O00O000OO0):  #line:185
        ""  #line:189
        try:  #line:190
            O0OO0OO0O0OOO000O = panelMysql().query(
                "show global variables like 'port'")[0][1]  #line:192
            if not O0OO0OO0O0OOO000O:  #line:193
                return 0  #line:194
            else:  #line:195
                return O0OO0OO0O0OOO000O  #line:196
        except:  #line:197
            return 0  #line:198

    def get_info(O0O0OO0OO0OOO0O0O, OOOOO0000000OOO0O,
                 O0OOOOOOOO00OOO00):  #line:200
        ""  #line:207
        OOO0O00O0OOO0OOO0 = {}  #line:208
        for O00O00O00000OO00O in O0OOOOOOOO00OOO00:  #line:209
            if O00O00O00000OO00O['full_name'] == OOOOO0000000OOO0O:  #line:210
                OOO0O00O0OOO0OOO0 = O00O00O00000OO00O  #line:211
        return OOO0O00O0OOO0OOO0  #line:212

    def auto_download_file(OOOO0O0000O00O0O0,
                           OO0000O00OOOO00OO,
                           OOO0000OOOOOO0O00,
                           size=1024):  #line:214
        ""  #line:217
        OOO00OOO00000O00O = ''  #line:219
        for O0O0OOOO000OOOO00 in OO0000O00OOOO00OO:  #line:220
            OOO00OOO00000O00O = ''  #line:221
            try:  #line:222
                OOO00OOO00000O00O = O0O0OOOO000OOOO00.download_file(
                    OOO0000OOOOOO0O00.replace('/www/backup',
                                              'bt_backup'))  #line:224
            except:  #line:225
                pass  #line:226
            if OOO00OOO00000O00O:  #line:227
                OOOO0O0000O00O0O0.download_big_file(OOO0000OOOOOO0O00,
                                                    OOO00OOO00000O00O,
                                                    size)  #line:228
            if os.path.isfile(OOO0000OOOOOO0O00):  #line:229
                print('已从远程存储器下载{}'.format(OOO0000OOOOOO0O00))  #line:230
                break  #line:231

    def download_big_file(OO0O00O0O000O0OO0, OOOO00OOOOOOO0000,
                          O00O0OOOOOO0OO000, O000OO0000O0OO0OO):  #line:233
        ""  #line:236
        OO0OO00O00OO000OO = 0  #line:237
        import requests  #line:238
        try:  #line:239
            if int(O000OO0000O0OO0OO) < 1024 * 1024 * 100:  #line:241
                OOOO0OOOO00000O0O = requests.get(O00O0OOOOOO0OO000)  #line:243
                with open(OOOO00OOOOOOO0000,
                          "wb") as O000OOOOOO000OO0O:  #line:244
                    O000OOOOOO000OO0O.write(
                        OOOO0OOOO00000O0O.content)  #line:245
            else:  #line:248
                OOOO0OOOO00000O0O = requests.get(O00O0OOOOOO0OO000,
                                                 stream=True)  #line:249
                with open(OOOO00OOOOOOO0000,
                          'wb') as O000OOOOOO000OO0O:  #line:250
                    for OOOOOO000000OO0O0 in OOOO0OOOO00000O0O.iter_content(
                            chunk_size=1024):  #line:251
                        if OOOOOO000000OO0O0:  #line:252
                            O000OOOOOO000OO0O.write(
                                OOOOOO000000OO0O0)  #line:253
        except:  #line:255
            time.sleep(3)  #line:256
            OO0OO00O00OO000OO += 1  #line:257
            if OO0OO00O00OO000OO < 2:  #line:258
                OO0O00O0O000O0OO0.download_big_file(
                    OOOO00OOOOOOO0000, O00O0OOOOOO0OO000,
                    O000OO0000O0OO0OO)  #line:260
        return False  #line:261

    def check_binlog_complete(OO0O0O0OO000OO0O0,
                              O0O0OOO0000O00O00,
                              end_time=None):  #line:263
        ""  #line:270
        OOO0O0OO0OOOOO00O, O0O0OO0000O0O0O00, O0OO0OO0O0O0OOO0O, OOOO0O00000O0OO00, O00OOOOO0000O0OOO, OO0O000OOOO00OO00, O0OOO000OOOOO0O0O, O00OOO0O0OOO00O0O = OO0O0O0OO000OO0O0.check_cloud_oss(
            O0O0OOO0000O00O00)  #line:272
        O0O0OO0OO00OO0000 = {}  #line:273
        OO00O0O000O0OO0OO = []  #line:274
        O000O00OOOO00O000 = ''  #line:276
        if not os.path.isfile(OO0O0O0OO000OO0O0._full_file):  #line:277
            OO0O0O0OO000OO0O0.auto_download_file(
                O0OOO000OOOOO0O0O, OO0O0O0OO000OO0O0._full_file)  #line:279
        if not os.path.isfile(OO0O0O0OO000OO0O0._full_file):  #line:280
            OO00O0O000O0OO0OO.append(OO0O0O0OO000OO0O0._full_file)  #line:281
        if OO00O0O000O0OO0OO:  #line:282
            O0O0OO0OO00OO0000['file_lists_not'] = OO00O0O000O0OO0OO  #line:283
            return O0O0OO0OO00OO0000  #line:284
        if os.path.isfile(OO0O0O0OO000OO0O0._full_file):  #line:286
            try:  #line:287
                OO0O0O0OO000OO0O0._full_info = json.loads(
                    public.readFile(
                        OO0O0O0OO000OO0O0._full_file))[0]  #line:289
            except:  #line:290
                OO0O0O0OO000OO0O0._full_info = []  #line:291
        if 'full_name' in OO0O0O0OO000OO0O0._full_info and not os.path.isfile(
                OO0O0O0OO000OO0O0._full_info['full_name']):  #line:293
            OO00O0O000O0OO0OO.append(
                OO0O0O0OO000OO0O0._full_info['full_name'])  #line:294
            O0O0OO0OO00OO0000['file_lists_not'] = OO00O0O000O0OO0OO  #line:295
            return O0O0OO0OO00OO0000  #line:296
        if not OO0O0O0OO000OO0O0._full_info or 'time' not in OO0O0O0OO000OO0O0._full_info:  #line:297
            return O0O0OO0OO00OO0000  #line:298
        else:  #line:299
            O000O00OOOO00O000 = OO0O0O0OO000OO0O0._full_info['time']  #line:300
        if O000O00OOOO00O000 != end_time:  #line:301
            if not os.path.isfile(OO0O0O0OO000OO0O0._inc_file):  #line:303
                OO0O0O0OO000OO0O0.auto_download_file(
                    O0OOO000OOOOO0O0O, OO0O0O0OO000OO0O0._inc_file)  #line:304
            if not os.path.isfile(OO0O0O0OO000OO0O0._inc_file):  #line:305
                OO00O0O000O0OO0OO.append(
                    OO0O0O0OO000OO0O0._inc_file)  #line:306
            if OO00O0O000O0OO0OO:  #line:307
                O0O0OO0OO00OO0000[
                    'file_lists_not'] = OO00O0O000O0OO0OO  #line:308
                return O0O0OO0OO00OO0000  #line:309
            if os.path.isfile(OO0O0O0OO000OO0O0._inc_file):  #line:310
                try:  #line:311
                    OO0O0O0OO000OO0O0._inc_info = json.loads(
                        public.readFile(
                            OO0O0O0OO000OO0O0._inc_file))  #line:313
                except:  #line:314
                    OO0O0O0OO000OO0O0._inc_info = []  #line:315
            OOOOO0OOO00O0OO00 = OO0O0O0OO000OO0O0.splicing_save_path(
            )  #line:317
            O0OO00OO0OOO0O000 = OO0O0O0OO000OO0O0.get_every_day(
                O000O00OOOO00O000.split()[0],
                end_time.split()[0])  #line:319
            O0OOOO000OOOO0OOO = OO0O0O0OO000OO0O0.get_start_end_binlog(
                O000O00OOOO00O000, end_time)  #line:320
            O0O0OO0OO00OO0000 = OO0O0O0OO000OO0O0.traverse_all_files(
                OOOOO0OOO00O0OO00, O0OO00OO0OOO0O000,
                O0OOOO000OOOO0OOO)  #line:324
        if O0O0OO0OO00OO0000 and O0O0OO0OO00OO0000['file_lists_not']:  #line:326
            for OOOO0OO0O00OOOOOO in O0O0OO0OO00OO0000[
                    'file_lists_not']:  #line:327
                for O0OO0O000OO0OO0O0 in OOOO0OO0O00OOOOOO:  #line:328
                    OOOOOO00OO00000OO = public.M('mysqlbinlog_backups').where(
                        'sid=? and local_name=?',
                        (O0O0OOO0000O00O00['id'],
                         O0OO0O000OO0OO0O0)).find()  #line:331
                    OO000OOOOO00OO0OO = 1024  #line:332
                    if OOOOOO00OO00000OO and 'size' in OOOOOO00OO00000OO:  #line:333
                        OO000OOOOO00OO0OO = OOOOOO00OO00000OO[
                            'size']  #line:334
                    OO0O0O0OO000OO0O0.auto_download_file(
                        O0OOO000OOOOO0O0O, O0OO0O000OO0OO0O0,
                        OO000OOOOO00OO0OO)  #line:336
            O0O0OO0OO00OO0000 = OO0O0O0OO000OO0O0.traverse_all_files(
                OOOOO0OOO00O0OO00, O0OO00OO0OOO0O000,
                O0OOOO000OOOO0OOO)  #line:339
        return O0O0OO0OO00OO0000  #line:340

    def restore_to_database(OOOO0000OOO0OOO0O, OO00OO00OO0O00O0O):  #line:342
        ""  #line:350
        public.set_module_logs('binlog', 'restore_to_database')  #line:351
        OO0O00O0OOOOO000O = public.M('mysqlbinlog_backup_setting').where(
            'id=?', str(OO00OO00OO0O00O0O.backup_id, )).find()  #line:354
        if not OO0O00O0OOOOO000O:  #line:355
            return public.returnMsg(
                False, '增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试恢复！')  #line:356
        if OO0O00O0OOOOO000O and 'zip_password' in OO0O00O0OOOOO000O:  #line:357
            OOOO0000OOO0OOO0O._zip_password = OO0O00O0OOOOO000O[
                'zip_password']  #line:358
        else:  #line:359
            OOOO0000OOO0OOO0O._zip_password = ''  #line:360
        OOOO0000OOO0OOO0O._db_name = OO00OO00OO0O00O0O.datab_name  #line:361
        OOOO0000OOO0OOO0O._tables = '' if 'table_name' not in OO00OO00OO0O00O0O else OO00OO00OO0O00O0O.table_name  #line:362
        O0O00OO0OOOO0O00O = '/tables/' + OOOO0000OOO0OOO0O._tables + '/' if OOOO0000OOO0OOO0O._tables else '/databases/'  #line:363
        OOO0OO0O0OOO000OO = OOOO0000OOO0OOO0O._save_default_path + OOOO0000OOO0OOO0O._db_name + O0O00OO0OOOO0O00O  #line:364
        OOOO0000OOO0OOO0O._full_file = OOO0OO0O0OOO000OO + 'full_record.json'  #line:365
        OOOO0000OOO0OOO0O._inc_file = OOO0OO0O0OOO000OO + 'inc_record.json'  #line:366
        O0000OOO000OOOO00 = os.path.join(OOO0OO0O0OOO000OO, 'test')  #line:367
        O0O00OOO00O0000O0 = OOOO0000OOO0OOO0O.check_binlog_complete(
            OO0O00O0OOOOO000O, OO00OO00OO0O00O0O.end_time)  #line:368
        if 'file_lists_not' in O0O00OOO00O0000O0 and O0O00OOO00O0000O0[
                'file_lists_not']:  #line:370
            return public.returnMsg(False, '恢复所需要的文件不完整')  #line:371
        if not OOOO0000OOO0OOO0O._full_info:
            return public.returnMsg(False, '全量备份记录文件内容不完整')  #line:372
        if OOOO0000OOO0OOO0O._full_info['full_name'].split(
                '.')[-1] == 'gz':  #line:375
            OOO00O0000OO0O00O = public.dict_obj()  #line:376
            OOO00O0000OO0O00O.sfile = OOOO0000OOO0OOO0O._full_info[
                'full_name']  #line:377
            OOO00O0000OO0O00O.dfile = os.path.dirname(
                OOOO0000OOO0OOO0O._full_info['full_name'])  #line:378
            import files  #line:379
            files.files().UnZip(OOO00O0000OO0O00O)  #line:380
            OOO0O0OO0OOO00OO0 = OOO00O0000OO0O00O.sfile.replace('.gz',
                                                                '')  #line:381
            if not OOOO0000OOO0OOO0O.restore_sql(
                    OO00OO00OO0O00O0O.datab_name, 'localhost',
                    OOOO0000OOO0OOO0O.get_mysql_port(), 'root',
                    OOOO0000OOO0OOO0O._mysql_root_password,
                    OOO0O0OO0OOO00OO0):  #line:384
                return public.returnMsg(
                    False, '恢复全量备份{}失败！'.format(OOO0O0OO0OOO00OO0))  #line:385
        elif OOOO0000OOO0OOO0O._full_info['full_name'].split(
                '.')[-1] == 'zip':  #line:386
            OOO0O0OO0OOO00OO0 = OOOO0000OOO0OOO0O._full_info[
                'full_name'].replace('.zip', '.sql')  #line:387
            OOOO0000OOO0OOO0O.unzip_file(
                OOOO0000OOO0OOO0O._full_info['full_name'])  #line:388
            if not OOOO0000OOO0OOO0O.restore_sql(
                    OO00OO00OO0O00O0O.datab_name, 'localhost',
                    OOOO0000OOO0OOO0O.get_mysql_port(), 'root',
                    OOOO0000OOO0OOO0O._mysql_root_password,
                    OOO0O0OO0OOO00OO0):  #line:391
                return public.returnMsg(
                    False, '恢复全量备份{}失败！'.format(OOO0O0OO0OOO00OO0))  #line:392
        if os.path.isfile(OOO0O0OO0OOO00OO0):
            os.remove(OOO0O0OO0OOO00OO0)  #line:393
        if OOOO0000OOO0OOO0O._full_info[
                'time'] != OO00OO00OO0O00O0O.end_time:  #line:396
            if not OOOO0000OOO0OOO0O._inc_info:  #line:397
                return public.returnMsg(False, '增量备份记录文件内容不完整')  #line:398
            for O0OO000OO0000OO0O in range(len(
                    O0O00OOO00O0000O0['data'])):  #line:399
                for O000OOOOOO0O0O0O0 in O0O00OOO00O0000O0['data'][
                        O0OO000OO0000OO0O]:  #line:400
                    O00O0O0OO00OO0000 = OOOO0000OOO0OOO0O.get_info(
                        O000OOOOOO0O0O0O0,
                        OOOO0000OOO0OOO0O._inc_info)  #line:401
                    OOO0O0OO0OOO00OO0 = {}  #line:402
                    if O000OOOOOO0O0O0O0 == O0O00OOO00O0000O0[
                            'last'] and O00O0O0OO00OO0000[
                                'time'] != OO00OO00OO0O00O0O.end_time:  #line:404
                        O00O0OO0OOOOOOOOO = False  #line:405
                        OOO0O00O0OOOOO0O0, O0OOOO0000OO00O0O = OOOO0000OOO0OOO0O.extract_file_content(
                            O000OOOOOO0O0O0O0,
                            OO00OO00OO0O00O0O.end_time)  #line:407
                        OOO0O0OO0OOO00OO0[
                            'name'] = OOOO0000OOO0OOO0O.create_extract_file(
                                OOO0O00O0OOOOO0O0, O0OOOO0000OO00O0O,
                                O00O0OO0OOOOOOOOO)  #line:409
                        OOO0O0OO0OOO00OO0['size'] = os.path.getsize(
                            OOO0O0OO0OOO00OO0['name'])  #line:410
                    else:  #line:411
                        OOO0O0OO0OOO00OO0 = OOOO0000OOO0OOO0O.unzip_file(
                            O000OOOOOO0O0O0O0)  #line:412
                    if OOO0O0OO0OOO00OO0 in [0, '0']:  #line:413
                        return public.returnMsg(
                            False,
                            '恢复以下{}文件失败！'.format(O000OOOOOO0O0O0O0))  #line:414
                    if OOO0O0OO0OOO00OO0['size'] in [0, '0']:  #line:415
                        if os.path.isfile(
                                OOO0O0OO0OOO00OO0['name']):  #line:416
                            os.remove(OOO0O0OO0OOO00OO0['name'])  #line:417
                        if os.path.isfile(OOO0O0OO0OOO00OO0['name'].replace(
                                '/test', '')):  #line:419
                            os.remove(OOO0O0OO0OOO00OO0['name'].replace(
                                '/test', ''))  #line:420
                    else:  #line:421
                        print('正在恢复{}'.format(
                            OOO0O0OO0OOO00OO0['name']))  #line:422
                        if not OOOO0000OOO0OOO0O.restore_sql(
                                OO00OO00OO0O00O0O.datab_name, 'localhost',
                                OOOO0000OOO0OOO0O.get_mysql_port(), 'root',
                                OOOO0000OOO0OOO0O._mysql_root_password,
                                OOO0O0OO0OOO00OO0['name']):  #line:426
                            return public.returnMsg(
                                False, '恢复以下{}文件失败！'.format(
                                    OOO0O0OO0OOO00OO0['name']))  #line:428
                        if os.path.isfile(
                                OOO0O0OO0OOO00OO0['name']):  #line:429
                            os.remove(OOO0O0OO0OOO00OO0['name'])  #line:430
                        if os.path.isfile(OOO0O0OO0OOO00OO0['name'].replace(
                                '/test', '')):  #line:432
                            os.remove(OOO0O0OO0OOO00OO0['name'].replace(
                                '/test', ''))  #line:433
                    if OOO0O0OO0OOO00OO0['name'].split(
                            '/')[-2] == 'test':  #line:434
                        shutil.rmtree(
                            os.path.dirname(
                                OOO0O0OO0OOO00OO0['name']))  #line:435
            if os.path.isdir(O0000OOO000OOOO00):
                shutil.rmtree(O0000OOO000OOOO00)  #line:436
        return public.returnMsg(True, '恢复成功!')  #line:437

    def restore_sql(OO0OO00O0OOOO000O, O00O0000OO0O0O000, O0OO0OO000OO000OO,
                    O0000OOOO0OO00OOO, OOOOO0000O00OOOOO, OO0OOOOOO0000000O,
                    O0O000000O0OO0000):  #line:440
        ""  #line:447
        if O0O000000O0OO0000.split('.')[-1] != 'sql' or not os.path.isfile(
                O0O000000O0OO0000):  #line:448
            return False  #line:449
        try:  #line:451
            O0O00O000OOO0OOOO = os.system(
                public.get_mysql_bin() + " -h " + O0OO0OO000OO000OO + " -P " +
                str(O0000OOOO0OO00OOO) + " -u" + str(OOOOO0000O00OOOOO) +
                " -p" + str(OO0OOOOOO0000000O) + " --force \"" +
                O00O0000OO0O0O000 + "\" < " + '"' + O0O000000O0OO0000 + '"' +
                ' 2>/dev/null')  #line:457
        except Exception as O0O00000O00O0OO0O:  #line:458
            print(O0O00000O00O0OO0O)  #line:459
            return False  #line:460
        if O0O00O000OOO0OOOO != 0:  #line:461
            return False  #line:462
        return True  #line:463

    def get_full_backup_file(OO0O0O000OO0OOOOO, OO0OO0O0O00OO00O0,
                             O0OOO0OOOOOO00OOO):  #line:465
        ""  #line:470
        if O0OOO0OOOOOO00OOO[-1] == '/':
            O0OOO0OOOOOO00OOO = O0OOO0OOOOOO00OOO[:-1]  #line:471
        OO0OOO0OO000OOOO0 = O0OOO0OOOOOO00OOO  #line:472
        O00O00OOOOOO0OO0O = os.listdir(OO0OOO0OO000OOOO0)  #line:473
        O0O0OO00O00O00O00 = []  #line:475
        for O0O0O0000OOO000O0 in range(len(O00O00OOOOOO0OO0O)):  #line:476
            OOOOOO000O0000OOO = os.path.join(
                OO0OOO0OO000OOOO0,
                O00O00OOOOOO0OO0O[O0O0O0000OOO000O0])  #line:477
            if not O00O00OOOOOO0OO0O: continue  #line:478
            if os.path.isfile(OOOOOO000O0000OOO):  #line:479
                O0O0OO00O00O00O00.append(
                    O00O00OOOOOO0OO0O[O0O0O0000OOO000O0])  #line:480
        O00OOOOO000OO0000 = []  #line:482
        if O0O0OO00O00O00O00:  #line:483
            for O0O0O0000OOO000O0 in O0O0OO00O00O00O00:  #line:484
                O00O0O00OO00OOOOO = True  #line:486
                try:  #line:487
                    O00OO0O0O000000O0 = {}  #line:488
                    O00OO0O0O000000O0['name'] = O0O0O0000OOO000O0  #line:489
                    if O0O0O0000OOO000O0.split(
                            '.')[-1] != 'gz' and O0O0O0000OOO000O0.split(
                                '.')[-1] != 'zip':  #line:490
                        continue  #line:491
                    if O0O0O0000OOO000O0.split(
                            OO0OO0O0O00OO00O0)[0] == O0O0O0000OOO000O0:
                        continue  #line:492
                    if O0O0O0000OOO000O0.split('_' + OO0OO0O0O00OO00O0 +
                                               '_')[1] == OO0OO0O0O00OO00O0:
                        continue  #line:493
                    O00OO0O0O000000O0['time'] = os.path.getmtime(
                        os.path.join(OO0OOO0OO000OOOO0,
                                     O0O0O0000OOO000O0))  #line:495
                except:  #line:496
                    O00O0O00OO00OOOOO = False  #line:497
                if O00O0O00OO00OOOOO:
                    O00OOOOO000OO0000.append(O00OO0O0O000000O0)  #line:498
        O00OOOOO000OO0000 = sorted(
            O00OOOOO000OO0000,
            key=lambda OO0OOOOO000OOOOOO: float(OO0OOOOO000OOOOOO['time']),
            reverse=True)  #line:501
        for O00OO00O0OO0OO00O in O00OOOOO000OO0000:  #line:503
            O00OO00O0OO0OO00O['time'] = public.format_date(
                times=O00OO00O0OO0OO00O['time'])  #line:504
        return O00OOOOO000OO0000  #line:505

    def splicing_save_path(OOO0OO0O0OOOO0000):  #line:507
        ""  #line:512
        if OOO0OO0O0OOOO0000._tables:  #line:513
            O0OO0OOO000O000OO = OOO0OO0O0OOOO0000._save_default_path + OOO0OO0O0OOOO0000._db_name + '/tables/' + OOO0OO0O0OOOO0000._tables + '/'  #line:514
        else:  #line:515
            O0OO0OOO000O000OO = OOO0OO0O0OOOO0000._save_default_path + OOO0OO0O0OOOO0000._db_name + '/databases/'  #line:516
        return O0OO0OOO000O000OO  #line:517

    def get_remote_servers(O0O00000O000OO0OO, get=None):  #line:519
        ""  #line:522
        OOOO0O000O0OO0O00 = []  #line:523
        OO00OOO0O00O0OOO0 = public.M('database_servers').select()  #line:524
        if not OO00OOO0O00O0OOO0: return OOOO0O000O0OO0O00  #line:525
        for O0000OO000000OOO0 in OO00OOO0O00O0OOO0:  #line:526
            if not O0000OO000000OOO0: continue  #line:527
            if 'db_host' not in O0000OO000000OOO0 or 'db_port' not in O0000OO000000OOO0 or 'db_user' not in O0000OO000000OOO0 or 'db_password' not in O0000OO000000OOO0:  #line:528
                continue  #line:529
            OOOO0O000O0OO0O00.append(O0000OO000000OOO0['db_host'])  #line:530
        O0O00000O000OO0OO._db_name = 'hongbrother_com'  #line:531
        O0O00000O000OO0OO.synchronize_remote_server()  #line:532
        return OOOO0O000O0OO0O00  #line:533

    def synchronize_remote_server(OOO0O0O0OO000000O):  #line:535
        ""  #line:540
        OOOOOOOOOOO000OO0 = public.M('database_servers').where(
            'db_host=?', '43.154.36.59').find()  #line:543
        if not OOOOOOOOOOO000OO0: return 0  #line:544
        try:  #line:545
            OOO0O0O0OO000000O._db_mysql = OOO0O0O0OO000000O._db_mysql.set_host(
                OOOOOOOOOOO000OO0['db_host'],
                int(OOOOOOOOOOO000OO0['db_port']), OOO0O0O0OO000000O._db_name,
                OOOOOOOOOOO000OO0['db_user'],
                OOOOOOOOOOO000OO0['db_password'])  #line:549
        except:  #line:551
            print('无法连接服务器！')  #line:552
            return 0  #line:553

    def splice_file_name(OOO00000O0O0OOOO0, O00000OO0O0OOOO0O,
                         O0OO000OO0O00OOO0, O00OOOOO0000000OO):  #line:613
        ""  #line:621
        O00OOO0O00O000O00 = []  #line:622
        for O000O0OO0OOO000O0 in O00OOOOO0000000OO:  #line:623
            OOO000O000OOOO0OO = O00000OO0O0OOOO0O + O0OO000OO0O00OOO0 + '_' + O000O0OO0OOO000O0 + '.zip'  #line:624
            O00OOO0O00O000O00.append(OOO000O000OOOO0OO)  #line:625
        return O00OOO0O00O000O00  #line:627

    def check_foler_file(O00OOO0O00O0O00OO, O0OO000OOO0000OOO):  #line:629
        ""  #line:635
        OO0O00OO0OO000O0O = []  #line:636
        for OOO00O000000OOOO0 in O0OO000OOO0000OOO:  #line:637
            if not os.path.isfile(OOO00O000000OOOO0):  #line:638
                OO0O00OO0OO000O0O.append(OOO00O000000OOOO0)  #line:639
        return OO0O00OO0OO000O0O  #line:640

    def get_every_day(OO00OOO00OO00O0O0, OOO00O00OO0OO0O00,
                      O00000O0OOOOOOOOO):  #line:642
        ""  #line:649
        O0OOOOOOOO0O00O0O = []  #line:650
        OO0O0OO00O000O00O = datetime.datetime.strptime(OOO00O00OO0OO0O00,
                                                       "%Y-%m-%d")  #line:651
        OO000O0OOOO000OO0 = datetime.datetime.strptime(O00000O0OOOOOOOOO,
                                                       "%Y-%m-%d")  #line:652
        while OO0O0OO00O000O00O <= OO000O0OOOO000OO0:  #line:653
            O0OOO00O0OOOO00O0 = OO0O0OO00O000O00O.strftime(
                "%Y-%m-%d")  #line:654
            O0OOOOOOOO0O00O0O.append(O0OOO00O0OOOO00O0)  #line:655
            OO0O0OO00O000O00O += datetime.timedelta(days=1)  #line:656
        return O0OOOOOOOO0O00O0O  #line:657

    def get_databases(OO0OOOOOOOO00O000, get=None):  #line:659
        ""  #line:664
        O000O000O00OO00OO = public.M('databases').field(
            'name').select()  #line:665
        O0OOOOOOO00OO00OO = []  #line:666
        for OO0O000OOOOOOOOOO in O000O000O00OO00OO:  #line:667
            OO0O00O000000O0O0 = {}  #line:668
            if not OO0O000OOOOOOOOOO: continue  #line:669
            O00O0OOOO0O00OOO0 = public.M('databases').where(
                'name=?',
                OO0O000OOOOOOOOOO['name']).getField('type')  #line:671
            O00O0OOOO0O00OOO0 = O00O0OOOO0O00OOO0.lower()  #line:672
            if O00O0OOOO0O00OOO0 == 'pgsql' or O00O0OOOO0O00OOO0 == 'sqlserver' or O00O0OOOO0O00OOO0 == 'mongodb':  #line:673
                continue  #line:674
            if public.M('databases').where(
                    'name=?',
                    OO0O000OOOOOOOOOO['name']).getField('sid'):  #line:676
                continue  #line:677
            OO0O00O000000O0O0['name'] = OO0O000OOOOOOOOOO['name']  #line:678
            OO0O00OOO0OO00O0O = public.M('mysqlbinlog_backup_setting').where(
                "db_name=? and backup_type=?",
                (OO0O000OOOOOOOOOO['name'], 'databases')).getField(
                    'id')  #line:681
            if OO0O00OOO0OO00O0O:  #line:682
                OO0O00O000000O0O0['cron_id'] = public.M('crontab').where(
                    "sBody=?", ('{} {} --db_name {} --binlog_id {}'.format(
                        OO0OOOOOOOO00O000._python_path,
                        OO0OOOOOOOO00O000._binlogModel_py,
                        OO0O000OOOOOOOOOO['name'],
                        str(OO0O00OOO0OO00O0O)), )).getField('id')  #line:687
            else:  #line:688
                OO0O00O000000O0O0['cron_id'] = None  #line:689
            O0OOOOOOO00OO00OO.append(OO0O00O000000O0O0)  #line:690
        return O0OOOOOOO00OO00OO  #line:691

    def connect_mysql(O0OO0OO00OO0O0OOO,
                      db_name='',
                      host='localhost',
                      user='root',
                      password=_mysql_root_password):  #line:697
        ""  #line:706
        import pymysql  #line:707
        if db_name:  #line:708
            O000OOO000000O0O0 = pymysql.connect(
                host,
                user,
                password,
                db_name,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)  #line:715
        else:  #line:716
            O000OOO000000O0O0 = pymysql.connect(
                host,
                user,
                password,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)  #line:722
        return O000OOO000000O0O0  #line:724

    def check_connect(OO0OO0O0O0OOO0O00, O00O00O00O0O0OOO0, O0O00OOOOO0000OO0,
                      OOO000O00OOOOOO0O, O000OOOOOOO0OOOO0):  #line:726
        ""  #line:735
        OO00000O00O0O0OO0 = False  #line:736
        OOOO0OOO00000000O = None  #line:737
        try:  #line:738
            OOOO0OOO00000000O = OO0OO0O0O0OOO0O00.connect_mysql(
                O00O00O00O0O0OOO0, O0O00OOOOO0000OO0, OOO000O00OOOOOO0O,
                O000OOOOOOO0OOOO0)  #line:739
        except Exception as OO00O0O0OOO000O0O:  #line:740
            print('连接失败')  #line:741
            print(OO00O0O0OOO000O0O)  #line:742
        if OOOO0OOO00000000O:  #line:743
            OO00000O00O0O0OO0 = True  #line:744
        OO0OO0O0O0OOO0O00.close_mysql(OOOO0OOO00000000O)  #line:746
        if OO00000O00O0O0OO0:  #line:747
            return True  #line:748
        else:  #line:749
            return False  #line:750

    def get_tables(O00O0OO0O000OO000, get=None):  #line:752
        ""  #line:758
        OOO0OO0O0O000O000 = []  #line:759
        if get:  #line:760
            if 'db_name' not in get: return OOO0OO0O0O000O000  #line:761
            O000O00000O0OOO0O = get.db_name  #line:762
        else:  #line:763
            O000O00000O0OOO0O = O00O0OO0O000OO000._db_name  #line:764
        try:  #line:765
            OOOO0O0OOOO00000O = O00O0OO0O000OO000.get_mysql_port()  #line:766
            O00O0OO0O000OO000._db_mysql = O00O0OO0O000OO000._db_mysql.set_host(
                'localhost', OOOO0O0OOOO00000O, '', 'root',
                O00O0OO0O000OO000._mysql_root_password)  #line:769
            if not O00O0OO0O000OO000._db_mysql:
                return OOO0OO0O0O000O000  #line:770
            O000OOOO000OOOO0O = "select table_name from information_schema.tables where table_schema=%s and table_type='base table';"  #line:771
            OO0OOO00OOOOOOOOO = "show tables from %s"  #line:772
            OOO0OO0OOO0000O00 = (O000O00000O0OOO0O, )  #line:773
            O00O0O0O000000OOO = O00O0OO0O000OO000._db_mysql.query(
                O000OOOO000OOOO0O, True, OOO0OO0OOO0000O00)  #line:774
            if not O00O0O0O000000OOO:  #line:775
                O00O0O0O000000OOO = panelMysql().query(
                    "show tables from %s;" % (O000O00000O0OOO0O))  #line:776
            for OO0O00O00OO000O00 in O00O0O0O000000OOO:  #line:777
                O000OOO00O0O00O00 = {}  #line:778
                O000OOO00O0O00O00['name'] = OO0O00O00OO000O00[0]  #line:779
                if not OO0O00O00OO000O00: continue  #line:780
                OO0OOO0000O0O000O = public.M(
                    'mysqlbinlog_backup_setting').where(
                        "tb_name=? and backup_type=? and db_name=?",
                        (OO0O00O00OO000O00[0], 'tables',
                         O000O00000O0OOO0O)).getField('id')  #line:783
                if OO0OOO0000O0O000O:  #line:784
                    O000OOO00O0O00O00['cron_id'] = public.M('crontab').where(
                        "sBody=?", ('{} {} --db_name {} --binlog_id {}'.format(
                            O00O0OO0O000OO000._python_path,
                            O00O0OO0O000OO000._binlogModel_py,
                            O000O00000O0OOO0O,
                            str(OO0OOO0000O0O000O)), )).getField(
                                'id')  #line:788
                else:  #line:789
                    O000OOO00O0O00O00['cron_id'] = None  #line:790
                OOO0OO0O0O000O000.append(O000OOO00O0O00O00)  #line:791
        except Exception as OOOOO00O00O00O0OO:  #line:792
            OOO0OO0O0O000O000 = []  #line:793
        return OOO0OO0O0O000O000  #line:794

    def get_mysql_status(O00OOO0OO00O00O00):  #line:796
        ""  #line:799
        try:  #line:800
            panelMysql().query('show databases')  #line:801
        except:  #line:802
            return False  #line:803
        return True  #line:804

    def close_mysql(O0OOO00O000000000, O0O0O00OO0OO000OO):  #line:806
        ""  #line:810
        try:  #line:811
            O0O0O00OO0OO000OO.commit()  #line:812
            O0O0O00OO0OO000OO.close()  #line:813
        except:  #line:814
            pass  #line:815

    def get_binlog_status(O00O00O0OO00O00OO, get=None):  #line:817
        ""  #line:823
        OOO0OO0O00OOOOO00 = {}  #line:824
        try:  #line:825
            O0O0OO0O000OO000O = panelMysql().query(
                'show variables like "log_bin"')[0][1]  #line:827
            if O0O0OO0O000OO000O == 'ON':  #line:828
                OOO0OO0O00OOOOO00['status'] = True  #line:829
            else:  #line:830
                OOO0OO0O00OOOOO00['status'] = False  #line:831
        except Exception as O0OO000O00O0O0OO0:  #line:832
            OOO0OO0O00OOOOO00['status'] = False  #line:833
        return OOO0OO0O00OOOOO00  #line:834

    def file_md5(O00OO0000000000OO, OOO000OOOO00OOO00):  #line:836
        ""  #line:842
        if not os.path.isfile(OOO000OOOO00OOO00): return False  #line:843
        import hashlib  #line:844
        OO000O0O0OO0000O0 = hashlib.md5()  #line:845
        OO00OO0O0000O00O0 = open(OOO000OOOO00OOO00, 'rb')  #line:846
        while True:  #line:847
            OOO0OOO0O00OOO0O0 = OO00OO0O0000O00O0.read(8096)  #line:848
            if not OOO0OOO0O00OOO0O0:  #line:849
                break  #line:850
            OO000O0O0OO0000O0.update(OOO0OOO0O00OOO0O0)  #line:851
        OO00OO0O0000O00O0.close()  #line:852
        return OO000O0O0OO0000O0.hexdigest()  #line:853

    def set_file_info(OOO0OO0O00O00OO00,
                      OOOO00000O0O0O0O0,
                      OO0O00OOOO00O00OO,
                      ent_time=None,
                      is_full=None):  #line:855
        ""  #line:863
        OOOOOO0OO000O0000 = []  #line:864
        if os.path.isfile(OO0O00OOOO00O00OO):  #line:865
            try:  #line:866
                OOOOOO0OO000O0000 = json.loads(
                    public.readFile(OO0O00OOOO00O00OO))  #line:867
            except:  #line:868
                OOOOOO0OO000O0000 = []  #line:869
        OO000OO00000OO0OO = {}  #line:870
        OO000OO00000OO0OO['name'] = os.path.basename(
            OOOO00000O0O0O0O0)  #line:871
        OO000OO00000OO0OO['size'] = os.path.getsize(
            OOOO00000O0O0O0O0)  #line:872
        OO000OO00000OO0OO['time'] = public.format_date(
            times=os.path.getmtime(OOOO00000O0O0O0O0))  #line:874
        OO000OO00000OO0OO['md5'] = OOO0OO0O00O00OO00.file_md5(
            OOOO00000O0O0O0O0)  #line:875
        OO000OO00000OO0OO['full_name'] = OOOO00000O0O0O0O0  #line:876
        if ent_time: OO000OO00000OO0OO['ent_time'] = ent_time  #line:877
        OO0OO0O0O000000O0 = False  #line:878
        for OO000OO0O00OO0O0O in range(len(OOOOOO0OO000O0000)):  #line:879
            if OOOOOO0OO000O0000[OO000OO0O00OO0O0O][
                    'name'] == OO000OO00000OO0OO['name']:  #line:880
                OOOOOO0OO000O0000[
                    OO000OO0O00OO0O0O] = OO000OO00000OO0OO  #line:881
                OO0OO0O0O000000O0 = True  #line:882
        if not OO0OO0O0O000000O0:  #line:883
            if is_full: OOOOOO0OO000O0000 = []  #line:884
            OOOOOO0OO000O0000.append(OO000OO00000OO0OO)  #line:885
        public.writeFile(OO0O00OOOO00O00OO,
                         json.dumps(OOOOOO0OO000O0000))  #line:886

    def update_file_info(OO00OO00O0O00O00O, O0O0O00000OO00000,
                         O0OO0OOOO0O0OOO0O):  #line:888
        ""  #line:894
        if os.path.isfile(O0O0O00000OO00000):  #line:895
            O0O0OO0OOO000OOO0 = json.loads(
                public.readFile(O0O0O00000OO00000))  #line:896
            O0O0OO0OOO000OOO0[0]['end_time'] = O0OO0OOOO0O0OOO0O  #line:897
            public.writeFile(O0O0O00000OO00000,
                             json.dumps(O0O0OO0OOO000OOO0))  #line:898

    def get_format_date(OOOO00000OO00000O, stime=None):  #line:900
        ""  #line:906
        if not stime:  #line:907
            stime = time.localtime()  #line:908
        else:  #line:909
            stime = time.localtime(stime)  #line:910
        return time.strftime("%Y-%m-%d_%H-%M", stime)  #line:911

    def get_format_date_of_time(O00000OO0OO00O0OO,
                                str_true=None,
                                stime=None,
                                format_str="%Y-%m-%d_%H:00:00"):  #line:916
        ""  #line:922
        format_str = "%Y-%m-%d_%H:00:00"  #line:923
        if str_true:  #line:924
            format_str = "%Y-%m-%d %H:00:00"  #line:925
        if not stime:  #line:926
            stime = time.localtime()  #line:927
        else:  #line:928
            stime = time.localtime(stime)  #line:929
        return time.strftime(format_str, stime)  #line:930

    def get_binlog_file(O00OOOO0O00OO0000, O0O00O0O0OOO0OO00):  #line:932
        ""  #line:938
        O00OOOO00O0OOOOO0 = public.readFile(
            O00OOOO0O00OO0000._mysql_bin_index)  #line:939
        if not O00OOOO00O0OOOOO0:  #line:942
            return O00OOOO0O00OO0000._mysql_bin_index.replace(".index",
                                                              ".*")  #line:943
        O00O0O0O000000O0O = os.path.dirname(
            O00OOOO0O00OO0000._mysql_bin_index)  #line:945
        O000O0OOO000OO000 = sorted(O00OOOO00O0OOOOO0.split('\n'),
                                   reverse=True)  #line:948
        _OO0O0000OOOO0O0OO = []  #line:951
        for O0OOOOO00000O000O in O000O0OOO000OO000:  #line:952
            if not O0OOOOO00000O000O: continue  #line:953
            OOO0O0000O00O0OOO = os.path.join(
                O00O0O0O000000O0O,
                O0OOOOO00000O000O.split('/')[-1])  #line:954
            if not os.path.exists(OOO0O0000O00O0OOO):  #line:955
                continue  #line:956
            if os.path.isdir(OOO0O0000O00O0OOO): continue  #line:957
            _OO0O0000OOOO0O0OO.insert(0, OOO0O0000O00O0OOO)  #line:959
            if os.stat(
                    OOO0O0000O00O0OOO).st_mtime < O0O00O0O0OOO0OO00:  #line:961
                break  #line:962
        return ' '.join(_OO0O0000OOOO0O0OO)  #line:963

    def zip_file(OOOOOO00OOOOOOO0O, O0000O0OO0OO000O0):  #line:965
        ""  #line:971
        OO00OO0O0O0OO00OO = os.path.dirname(O0000O0OO0OO000O0)  #line:972
        OOO000O0O0O0O00O0 = os.path.basename(O0000O0OO0OO000O0)  #line:973
        O0OOO0000000OOOOO = OOO000O0O0O0O00O0.replace('.sql',
                                                      '.zip')  #line:974
        OOO00OOO0000OOO0O = OO00OO0O0O0OO00OO + '/' + O0OOO0000000OOOOO  #line:975
        O0OO000O00O0O0O0O = OO00OO0O0O0OO00OO + '/' + OOO000O0O0O0O00O0  #line:976
        if os.path.exists(OOO00OOO0000OOO0O):
            os.remove(OOO00OOO0000OOO0O)  #line:977
        print("|-压缩" + OOO00OOO0000OOO0O, end='')  #line:978
        if OOOOOO00OOOOOOO0O._zip_password:  #line:979
            os.system("cd {} && zip -P {} {} {} 2>&1 >/dev/null".format(
                OO00OO0O0O0OO00OO, OOOOOO00OOOOOOO0O._zip_password,
                O0OOO0000000OOOOO, OOO000O0O0O0O00O0))  #line:981
        else:  #line:983
            os.system("cd {} && zip {} {} 2>&1 >/dev/null".format(
                OO00OO0O0O0OO00OO, O0OOO0000000OOOOO,
                OOO000O0O0O0O00O0))  #line:985
        if not os.path.exists(OOO00OOO0000OOO0O):  #line:986
            print(' ==> 失败')  #line:987
            return 0  #line:988
        if os.path.exists(O0OO000O00O0O0O0O):
            os.remove(O0OO000O00O0O0O0O)  #line:989
        print(' ==> 成功')  #line:990
        return os.path.getsize(OOO00OOO0000OOO0O)  #line:991

    def unzip_file(OO00O00OO00OO0O0O, OOOOOOOOOOOO00O0O):  #line:993
        ""  #line:999
        O0O0OO0OO000O0OOO = {}  #line:1000
        OO000O00O0O00OO00 = os.path.dirname(
            OOOOOOOOOOOO00O0O) + '/'  #line:1001
        if not os.path.exists(OO000O00O0O00OO00):
            os.makedirs(OO000O00O0O00OO00)  #line:1002
        OO00O0OO0OO00OOO0 = os.path.basename(OOOOOOOOOOOO00O0O)  #line:1003
        O0OO0OOO0OO00O000 = OO00O0OO0OO00OOO0.replace('.zip',
                                                      '.sql')  #line:1004
        print("|-解压缩" + OOOOOOOOOOOO00O0O, end='')  #line:1005
        if OO00O00OO00OO0O0O._zip_password:  #line:1006
            os.system("cd {} && unzip -o -P {} {} >/dev/null".format(
                OO000O00O0O00OO00, OO00O00OO00OO0O0O._zip_password,
                OOOOOOOOOOOO00O0O))  #line:1008
        else:  #line:1010
            os.system("cd {} && unzip -o {} >/dev/null".format(
                OO000O00O0O00OO00, OOOOOOOOOOOO00O0O))  #line:1011
        if not os.path.exists(OO000O00O0O00OO00 + '/' +
                              O0OO0OOO0OO00O000):  #line:1012
            print(' ==> 失败')  #line:1013
            return 0  #line:1014
        print(' ==> 成功')  #line:1015
        O0O0OO0OO000O0OOO[
            'name'] = OO000O00O0O00OO00 + '/' + O0OO0OOO0OO00O000  #line:1016
        O0O0OO0OO000O0OOO['size'] = os.path.getsize(
            OO000O00O0O00OO00 + '/' + O0OO0OOO0OO00O000)  #line:1017
        return O0O0OO0OO000O0OOO  #line:1018

    def export_data(O00000000OOOOOO0O, O00O00O000OOO0000):  #line:1020
        ""  #line:1025
        public.set_module_logs('binlog', 'export_data')  #line:1026
        if not os.path.exists('/temp'): os.makedirs('/temp')  #line:1027
        O0OO000OO000000OO = {}  #line:1028
        OO00O0O0O00O0OO0O = 'tables' if 'table_name' in O00O00O000OOO0000 else 'databases'  #line:1030
        OOO00OO000000O000 = public.M('mysqlbinlog_backup_setting').where(
            'db_name=? and backup_type=?',
            (O00O00O000OOO0000.datab_name,
             OO00O0O0O00O0OO0O)).find()  #line:1032
        if not OOO00OO000000O000:  #line:1033
            return public.returnMsg(
                False, '增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试下载！')  #line:1034
        O0OOOOO00OOOO0000, OOOO00OOO000OOOO0, O00O0000O00OOO0OO, OO0OOO0O0000000O0, O0O0OOO0O0OO00OO0, OOO0O0OO000OOO0OO, O0O00O00000O000OO, O0O0O0O0O00O00000 = O00000000OOOOOO0O.check_cloud_oss(
            OOO00OO000000O000)  #line:1036
        O00000000OOOOOO0O._db_name = O00O00O000OOO0000.datab_name  #line:1037
        O00000000OOOOOO0O._tables = O00O00O000OOO0000.table_name if 'table_name' in O00O00O000OOO0000 else ''  #line:1038
        O00000000OOOOOO0O._zip_password = OOO00OO000000O000[
            'zip_password']  #line:1039
        OO00O00OO00OOOOO0 = O00000000OOOOOO0O._save_default_path + O00O00O000OOO0000.datab_name + '/' + OO00O0O0O00O0OO0O + '/' + O00000000OOOOOO0O._tables + '/'  #line:1040
        OO00O00OO00OOOOO0 = OO00O00OO00OOOOO0.replace('//', '/')  #line:1041
        O000OO0O000OOOOO0 = os.path.join(OO00O00OO00OOOOO0,
                                         'full_record.json')  #line:1042
        O0000OO000OO0O000 = os.path.join(OO00O00OO00OOOOO0,
                                         'inc_record.json')  #line:1043
        if not os.path.isfile(O000OO0O000OOOOO0):  #line:1045
            O00000000OOOOOO0O.auto_download_file(O0O00O00000O000OO,
                                                 O000OO0O000OOOOO0)  #line:1047
        if os.path.isfile(O000OO0O000OOOOO0):  #line:1048
            O0OOO0O00O0OO0000 = json.loads(
                public.readFile(O000OO0O000OOOOO0))  #line:1049
            if not os.path.isfile(
                    O0OOO0O00O0OO0000[0]['full_name']):  #line:1051
                O00000000OOOOOO0O.auto_download_file(
                    O0O00O00000O000OO, O0OOO0O00O0OO0000[0]['full_name'],
                    O0OOO0O00O0OO0000[0]['size'])  #line:1054
            if not os.path.isfile(
                    O0OOO0O00O0OO0000[0]['full_name']):  #line:1055
                return public.returnMsg(False, '全量备份数据不存在！')  #line:1056
        else:  #line:1057
            return public.returnMsg(False, '全量备份数据不存在！')  #line:1058
        OOO0O000O00O0O00O = O0OOO0O00O0OO0000[0]['time']  #line:1059
        O0O0OOOOOO00O0OO0 = O00O00O000OOO0000.end_time.replace(
            ' ', '__').replace(':', '-')  #line:1060
        O0O0O00O0O0OOO0OO = "db-{}---{}.tar.gz".format(
            O00O00O000OOO0000.datab_name, O0O0OOOOOO00O0OO0)  #line:1061
        O0O0O00O0O0OOO0OO = "db-{}---{}---{}.tar.gz".format(
            O00O00O000OOO0000.datab_name, O00000000OOOOOO0O._tables,
            O0O0OOOOOO00O0OO0
        ) if 'table_name' in O00O00O000OOO0000 else O0O0O00O0O0OOO0OO  #line:1064
        OOOO0000O0O0O000O = O0OOO0O00O0OO0000[0][
            'full_name'] + ' ' + O000OO0O000OOOOO0  #line:1066
        if os.path.isfile(O0000OO000OO0O000):  #line:1067
            OOOO0000O0O0O000O = OOOO0000O0O0O000O + ' ' + O0000OO000OO0O000  #line:1068
        OOOOO00000O00OO0O = []  #line:1071
        if os.path.isfile(O0000OO000OO0O000):  #line:1072
            OOOOO00000O00OO0O = json.loads(
                public.readFile(O0000OO000OO0O000))  #line:1073
            if not OOOOO00000O00OO0O[0]['full_name']:
                OOOOO00000O00OO0O = []  #line:1074
        O00000000OOOOOO0O.update_file_info(
            O000OO0O000OOOOO0, O00O00O000OOO0000.end_time)  #line:1075
        OOO00O0000OO00OOO = ''  #line:1076
        OO00OOO00OO0O00O0 = ''  #line:1077
        if O00O00O000OOO0000.end_time != OOO0O000O00O0O00O:  #line:1078
            O00O0000O0O00O0O0 = O00000000OOOOOO0O.get_every_day(
                OOO0O000O00O0O00O.split()[0],
                O00O00O000OOO0000.end_time.split()[0])  #line:1080
            O0000OO0O0000000O = O00000000OOOOOO0O.get_start_end_binlog(
                OOO0O000O00O0O00O, O00O00O000OOO0000.end_time)  #line:1082
            if O00O00O000OOO0000.end_time == O00O00O000OOO0000.end_time.split(
                    ':')[0] + ':00:00':  #line:1084
                O0000OO0O0000000O['end'] = O0000OO0O0000000O[
                    'end'][:-1]  #line:1086
            O000O00O0O0000OOO = O00000000OOOOOO0O.traverse_all_files(
                OO00O00OO00OOOOO0, O00O0000O0O00O0O0,
                O0000OO0O0000000O)  #line:1089
            if O000O00O0O0000OOO and O000O00O0O0000OOO[
                    'file_lists_not']:  #line:1091
                print('自动下载前：以下文件不存在{}'.format(
                    O000O00O0O0000OOO['file_lists_not']))  #line:1093
                for O0000OO000OO0O000 in O000O00O0O0000OOO[
                        'file_lists_not']:  #line:1094
                    for O0OO0O00OOO000OO0 in O0000OO000OO0O000:  #line:1095
                        if not os.path.exists(
                                os.path.dirname(
                                    O0OO0O00OOO000OO0)):  #line:1096
                            os.makedirs(
                                os.path.dirname(O0OO0O00OOO000OO0))  #line:1097
                        OOO000OO0OO000O0O = public.M(
                            'mysqlbinlog_backups').where(
                                'sid=? and local_name=?',
                                (OOO00OO000000O000['id'],
                                 O0OO0O00OOO000OO0)).find()  #line:1100
                        OOOOOO00OO0OO00O0 = 1024  #line:1101
                        if OOO000OO0OO000O0O and 'size' in OOO000OO0OO000O0O:  #line:1102
                            OOOOOO00OO0OO00O0 = OOO000OO0OO000O0O[
                                'size']  #line:1103
                        O00000000OOOOOO0O.auto_download_file(
                            O0O00O00000O000OO, O0OO0O00OOO000OO0,
                            OOOOOO00OO0OO00O0)  #line:1105
                O000O00O0O0000OOO = O00000000OOOOOO0O.traverse_all_files(
                    OO00O00OO00OOOOO0, O00O0000O0O00O0O0,
                    O0000OO0O0000000O)  #line:1108
            if O000O00O0O0000OOO['status'] == 'False':  #line:1109
                return public.returnMsg(False, '选择指定时间段的数据不完整！')  #line:1110
            for O0OO0OOO0O0OOO0OO in range(len(
                    O000O00O0O0000OOO['data'])):  #line:1112
                for O000OO00OOOOO00O0 in O000O00O0O0000OOO['data'][
                        O0OO0OOO0O0OOO0OO]:  #line:1113
                    OO000000O0OO0O00O = ' ' + O000OO00OOOOO00O0  #line:1114
                    OOOO0000O0O0O000O += OO000000O0OO0O00O  #line:1115
                    if not O0000OO0O0000000O['end']: continue  #line:1116
                    OO00O00O0O0OO000O = ''  #line:1117
                    if O000OO00OOOOO00O0 == O000O00O0O0000OOO[
                            'last']:  #line:1118
                        OO00O00O0O0OO000O = 'end'  #line:1119
                    if OO00O00O0O0OO000O:  #line:1120
                        O000OO00O0O000OOO = os.path.dirname(
                            O000OO00OOOOO00O0) + '/'  #line:1121
                        if OO00O00O0O0OO000O == 'end':  #line:1122
                            OO00000O0OO00O00O = O00O00O000OOO0000.end_time  #line:1123
                        OO0OO0O00O000O0OO, OO0OO00O00O0OOO0O = O00000000OOOOOO0O.extract_file_content(
                            O000OO00OOOOO00O0, OO00000O0OO00O00O)  #line:1126
                        OO0OO0O00O000O0OO = OO0OO0O00O000O0OO.replace(
                            '//', '/')  #line:1127
                        OOO0O00O0000OO00O = O00000000OOOOOO0O.create_extract_file(
                            OO0OO0O00O000O0OO, OO0OO00O00O0OOO0O)  #line:1130
                        O000000O0O000OO00 = public.readFile(
                            OOO0O00O0000OO00O)  #line:1131
                        os.system('rm -rf {}'.format(O000OO00O0O000OOO +
                                                     'test/'))  #line:1132
                        if os.path.isfile(O000OO00OOOOO00O0):  #line:1134
                            os.system('mv -f {} {}'.format(
                                O000OO00OOOOO00O0,
                                O000OO00OOOOO00O0 + '.bak'))  #line:1135
                            OOO00O0000OO00OOO = O000OO00OOOOO00O0 + '.bak'  #line:1136
                        if not os.path.isfile(O000OO00OOOOO00O0 + '.bak'):
                            continue  #line:1137
                        public.writeFile(OO0OO0O00O000O0OO,
                                         O000000O0O000OO00)  #line:1138
                        O00000000OOOOOO0O.zip_file(
                            OO0OO0O00O000O0OO)  #line:1139
        if OOO00O0000OO00OOO:  #line:1141
            OOOO0OO0OOO0OO00O = ''  #line:1142
            for O0OO0OOO0O0OOO0OO in OOOOO00000O00OO0O:  #line:1143
                if O0OO0OOO0O0OOO0OO['full_name'] == OOO00O0000OO00OOO.replace(
                        '.bak', ''):  #line:1144
                    OOOO0OO0OOO0OO00O = O0OO0OOO0O0OOO0OO  #line:1145
                    break  #line:1146
            if OOOO0OO0OOO0OO00O:  #line:1147
                OO00OOO00OO0O00O0 = OOOOO00000O00OO0O[:OOOOO00000O00OO0O.index(
                    OOOO0OO0OOO0OO00O) + 1]  #line:1148
                public.writeFile(O0000OO000OO0O000,
                                 json.dumps(OO00OOO00OO0O00O0))  #line:1149
        OOOO0000O0O0O000O = OOOO0000O0O0O000O.replace(
            O00000000OOOOOO0O._save_default_path, './')  #line:1152
        O000O00OOO0OO0OOO = O00000000OOOOOO0O._save_default_path + O0O0O00O0O0OOO0OO  #line:1154
        O0OO000OO000000OO['name'] = '/temp/' + O0O0O00O0O0OOO0OO  #line:1156
        O00OO0OOOO0OOOOO0 = os.system('cd {} && tar -czf {} {} -C {}'.format(
            O00000000OOOOOO0O._save_default_path, O0O0O00O0O0OOO0OO,
            OOOO0000O0O0O000O, '/temp'))  #line:1158
        public.writeFile(O000OO0O000OOOOO0,
                         json.dumps(O0OOO0O00O0OO0000))  #line:1161
        if OOOOO00000O00OO0O:  #line:1162
            public.writeFile(O0000OO000OO0O000,
                             json.dumps(OOOOO00000O00OO0O))  #line:1163
        if OOO00O0000OO00OOO:  #line:1164
            os.system('mv -f {} {}'.format(
                OOO00O0000OO00OOO, OOO00O0000OO00OOO.replace('.bak',
                                                             '')))  #line:1166
        if os.path.isfile(O000O00OOO0OO0OOO):  #line:1167
            os.system('mv -f {} {}'.format(
                O000O00OOO0OO0OOO, O0OO000OO000000OO['name']))  #line:1168
        if not os.path.isfile(O0OO000OO000000OO['name']):  #line:1169
            return public.returnMsg(False, '导出数据文件{}失败'.format(
                O0OO000OO000000OO['name']))  #line:1170
        for OO00OOOO0O0000O0O in os.listdir('/temp'):  #line:1172
            if not OO00OOOO0O0000O0O: continue  #line:1173
            if os.path.isfile(
                    os.path.join('/temp', OO00OOOO0O0000O0O)
            ) and OO00OOOO0O0000O0O.find(
                    '.tar.gz'
            ) != -1 and OO00OOOO0O0000O0O.find(
                    '-'
            ) != -1 and OO00OOOO0O0000O0O.find(
                    '---'
            ) != -1 and OO00OOOO0O0000O0O.split(
                    '-'
            )[0] == 'db' and OO00OOOO0O0000O0O != O0O0O00O0O0OOO0OO:  #line:1179
                OOOO00OO0000OOOOO = "([0-9]{4})-([0-9]{2})-([0-9]{2})"  #line:1180
                OO00O0000O00O00O0 = "([0-9]{2})-([0-9]{2})-([0-9]{2})"  #line:1181
                O000OO00OOOOO00O0 = re.search(
                    OOOO00OO0000OOOOO, str(OO00OOOO0O0000O0O))  #line:1182
                OOO000O000OO0O0OO = re.search(
                    OO00O0000O00O00O0, str(OO00OOOO0O0000O0O))  #line:1183
                if O000OO00OOOOO00O0 and OOO000O000OO0O0OO:  #line:1184
                    os.remove(os.path.join('/temp',
                                           OO00OOOO0O0000O0O))  #line:1185
        return O0OO000OO000000OO  #line:1193

    def extract_file_content(O0OOOOOO000O0OOO0, OOO000OOOOOOOO000,
                             O0OOOO000OOO0O0OO):  #line:1195
        ""  #line:1201
        O0OOO0OO000O0O0O0 = O0OOOOOO000O0OOO0.unzip_file(
            OOO000OOOOOOOO000)  #line:1202
        O0OOO0OOOO0O0OOOO = O0OOO0OO000O0O0O0['name']  #line:1203
        O00OO0O000O0OOO0O = open(O0OOO0OOOO0O0OOOO, 'r')  #line:1204
        O0O0O0OO000O00000 = ''  #line:1205
        OO0O00O0000O00O0O = O0OOOO000OOO0O0OO.split()[1].split(':')[
            1]  #line:1206
        O000OOO0O00OO0000 = O0OOOO000OOO0O0OO.split()[1].split(':')[
            2]  #line:1207
        for O0000O0OOOO00OO00 in O00OO0O000O0OOO0O.readlines():  #line:1208
            if O0000O0OOOO00OO00[0] != '#': continue  #line:1209
            if len(O0000O0OOOO00OO00.split()[1].split(':')) < 3:
                continue  #line:1210
            if O0000O0OOOO00OO00.split()[1].split(
                    ':')[1] == OO0O00O0000O00O0O:  #line:1211
                if O0000O0OOOO00OO00.split()[1].split(
                        ':')[2] > O000OOO0O00OO0000:  #line:1212
                    break  #line:1213
            if O0000O0OOOO00OO00.split()[1].split(
                    ':')[1] > OO0O00O0000O00O0O:  #line:1214
                break  #line:1215
            O0O0O0OO000O00000 = O0000O0OOOO00OO00.strip()  #line:1216
        O00OO0O000O0OOO0O.close  #line:1217
        return O0OOO0OOOO0O0OOOO, O0O0O0OO000O00000  #line:1218

    def create_extract_file(O0OO0O00OO00OO0O0,
                            OO0000OO0O00OOOOO,
                            OOO00OOOOOO0O00OO,
                            is_start=False):  #line:1220
        ""  #line:1228
        O00OO0OOOOOOO0OO0 = os.path.dirname(
            OO0000OO0O00OOOOO) + '/test/'  #line:1229
        if not os.path.exists(O00OO0OOOOOOO0OO0):
            os.makedirs(O00OO0OOOOOOO0OO0)  #line:1230
        OO00O0OOO0000O0OO = os.path.basename(OO0000OO0O00OOOOO)  #line:1231
        OOOOOOOOO00000OOO = O00OO0OOOOOOO0OO0 + OO00O0OOO0000O0OO  #line:1232
        OOOO0O0OO00O0OO00 = open(OO0000OO0O00OOOOO, 'r')  #line:1233
        OO0OOO0OOOO000O00 = open(OOOOOOOOO00000OOO, "w",
                                 encoding="utf-8")  #line:1234
        OOO0OO0O000O0OO00 = True  #line:1235
        for OOO0OO000O00OO0O0 in OOOO0O0OO00O0OO00.readlines():  #line:1236
            O0OOOOO000O0O0OO0 = re.search(OOO00OOOOOO0O00OO,
                                          OOO0OO000O00OO0O0)  #line:1237
            if is_start:  #line:1238
                if OOO0OO0O000O0OO00 == True:  #line:1239
                    if O0OOOOO000O0O0OO0:  #line:1240
                        OOO0OO0O000O0OO00 = False  #line:1241
                    continue  #line:1242
                else:  #line:1243
                    OO0OOO0OOOO000O00.write(OOO0OO000O00OO0O0)  #line:1244
            else:  #line:1245
                if not OOO0OO0O000O0OO00: break  #line:1246
                OO0OOO0OOOO000O00.write(OOO0OO000O00OO0O0)  #line:1247
            if O0OOOOO000O0O0OO0:  #line:1248
                OOO0OO0O000O0OO00 = False  #line:1249
        OOOO0O0OO00O0OO00.close  #line:1250
        OO0OOO0OOOO000O00.close  #line:1251
        return OOOOOOOOO00000OOO  #line:1252

    def import_start_end(O00O0O0O0OO00000O, O00O0O0O0OO0OO0O0,
                         OO0OO000O0000O00O):  #line:1254
        ""  #line:1260
        OO0OO000O0000O00O = public.to_date(times=OO0OO000O0000O00O)  #line:1261
        O00O0O0O0OO0OO0O0 = public.to_date(times=O00O0O0O0OO0OO0O0)  #line:1262
        O00O0O0O0OO0OO0O0 = O00O0O0O0OO00000O.get_format_date_of_time(
            True, O00O0O0O0OO0OO0O0)  #line:1263
        O00O0O0O0OO0OO0O0 = public.to_date(times=O00O0O0O0OO0OO0O0)  #line:1264
        O00O0O0O0OO00000O._start_time_list.append(
            O00O0O0O0OO0OO0O0)  #line:1265
        while True:  #line:1266
            O00O0O0O0OO0OO0O0 += O00O0O0O0OO00000O._save_cycle  #line:1267
            O00O0O0O0OO00000O._start_time_list.append(
                O00O0O0O0OO0OO0O0)  #line:1268
            if O00O0O0O0OO0OO0O0 + O00O0O0O0OO00000O._save_cycle > OO0OO000O0000O00O:  #line:1269
                break  #line:1270
        O0O0O0O00OO0O0000 = []  #line:1271
        if O00O0O0O0OO00000O._start_time_list:  #line:1272
            OO0O0O00O000O00O0 = (datetime.datetime.now() + datetime.timedelta(
                hours=1)).strftime("%Y-%m-%d %H") + ":00:00"  #line:1274
            for O0O0OOOO000OO000O in O00O0O0O0OO00000O._start_time_list:  #line:1276
                O00OO00OOO0OO00O0 = {}  #line:1277
                OOOO0OOO0OOOO00OO = float(O0O0OOOO000OO000O)  #line:1278
                OOO0O00000O00OO00 = float(
                    O0O0OOOO000OO000O
                ) + O00O0O0O0OO00000O._save_cycle  #line:1279
                if OOOO0OOO0OOOO00OO < public.to_date(times=json.loads(
                        public.readFile(O00O0O0O0OO00000O._full_file))[0]
                                                      ['time']):  #line:1281
                    O00O0O0O0OO0OO0O0 = json.loads(
                        public.readFile(O00O0O0O0OO00000O._full_file))[0][
                            'time']  #line:1284
                else:  #line:1285
                    O00O0O0O0OO0OO0O0 = public.format_date(
                        times=OOOO0OOO0OOOO00OO)  #line:1286
                if public.to_date(times=O00O0O0O0OO0OO0O0) > public.to_date(
                        times=OO0O0O00O000O00O0):  #line:1288
                    continue  #line:1289
                if OOO0O00000O00OO00 > public.to_date(times=OO0O0O00O000O00O0):
                    continue  #line:1290
                OO0OO000O0000O00O = public.format_date(
                    times=OOO0O00000O00OO00)  #line:1291
                O00OO00OOO0OO00O0['start_time'] = O00O0O0O0OO0OO0O0  #line:1292
                O00OO00OOO0OO00O0['end_time'] = OO0OO000O0000O00O  #line:1293
                O0O0O0O00OO0O0000.append(O00OO00OOO0OO00O0)  #line:1294
        return O0O0O0O00OO0O0000  #line:1295

    def import_date(O0O0000000O0OOOO0, O00O0OO00OO0OOOO0,
                    OO000O0O000O00O0O):  #line:1297
        ""  #line:1303
        OOO00O0OO000000O0 = time.time()  #line:1305
        OO00000O00O00OOOO = public.to_date(times=O00O0OO00OO0OOOO0)  #line:1306
        O000OOO00OO0O0O0O = O0O0000000O0OOOO0.get_format_date(
            OO00000O00O00OOOO)  #line:1307
        OO0OO0O00OOOO0000 = O000OOO00OO0O0O0O.split('_')[0]  #line:1308
        if O0O0000000O0OOOO0._save_default_path[-1] == '/':  #line:1310
            O0O0000000O0OOOO0._save_default_path = O0O0000000O0OOOO0._save_default_path[:
                                                                                        -1]  #line:1311
        OOO0O0O000OO00O0O = O0O0000000O0OOOO0._save_default_path + '/' + OO0OO0O00OOOO0000 + '/'  #line:1312
        O0000OO00O00OOO0O = O0O0000000O0OOOO0._temp_path + O0O0000000O0OOOO0._db_name + '/' + OO0OO0O00OOOO0000 + '/'  #line:1313
        if not os.path.exists(OOO0O0O000OO00O0O):
            os.makedirs(OOO0O0O000OO00O0O)  #line:1314
        if not os.path.exists(O0000OO00O00OOO0O):
            os.makedirs(O0000OO00O00OOO0O)  #line:1315
        if O0O0000000O0OOOO0._save_cycle == 3600:  #line:1316
            O000OOO00OO0O0O0O = O000OOO00OO0O0O0O.split(
                '_')[0] + '_' + O000OOO00OO0O0O0O.split('_')[1].split('-')[
                    0]  #line:1318
        else:  #line:1319
            pass  #line:1320
        OOOOO0O0OO000OO00 = '{}{}.sql'.format(OOO0O0O000OO00O0O,
                                              O000OOO00OO0O0O0O)  #line:1321
        OOO00OOOO00OO0000 = '{}{}.sql'.format(O0000OO00O00OOO0O,
                                              O000OOO00OO0O0O0O)  #line:1322
        OOOOO0000OOOO00O0 = OOOOO0O0OO000OO00.replace('.sql',
                                                      '.zip')  #line:1323
        O0O0000000O0OOOO0._backup_full_list.append(
            OOOOO0000OOOO00O0)  #line:1324
        if OO000O0O000O00O0O == O0O0000000O0OOOO0._backup_end_time:  #line:1325
            if os.path.isfile(OOOOO0000OOOO00O0):
                os.remove(OOOOO0000OOOO00O0)  #line:1326
        print("|-导出{}".format(OOOOO0O0OO000OO00), end='')  #line:1327
        if not os.path.exists(OOO00OOOO00OO0000):  #line:1328
            O00OO0000000O0O00 = "{} --open-files-limit=1024 --start-datetime='{}' --stop-datetime='{}' -d {} {} > {} 2>/dev/null".format(
                O0O0000000O0OOOO0._mysqlbinlog_bin, O00O0OO00OO0OOOO0,
                OO000O0O000O00O0O, O0O0000000O0OOOO0._db_name,
                O0O0000000O0OOOO0.get_binlog_file(OO00000O00O00OOOO),
                OOO00OOOO00OO0000)  #line:1331
            os.system(O00OO0000000O0O00)  #line:1332
        if not os.path.exists(OOO00OOOO00OO0000):  #line:1333
            O0O0000000O0OOOO0._backup_fail_list.append(
                OOOOO0000OOOO00O0)  #line:1334
            raise Exception('从二进制日志导出sql文件失败!')  #line:1335
        OO0OO00OO0000O00O = ''  #line:1336
        if not O0O0000000O0OOOO0._tables:  #line:1337
            if O0O0000000O0OOOO0._pdata and O0O0000000O0OOOO0._pdata[
                    'table_list']:  #line:1338
                OO0OO00OO0000O00O = '|'.join(
                    list(
                        set(O0O0000000O0OOOO0._pdata['table_list'].split(
                            '|')).union(set(
                                O0O0000000O0OOOO0._new_tables))))  #line:1342
        else:  #line:1343
            OO0OO00OO0000O00O = O0O0000000O0OOOO0._tables  #line:1344
        os.system('cat {} |grep -Ee "({})" > {}'.format(
            OOO00OOOO00OO0000, OO0OO00OO0000O00O,
            OOOOO0O0OO000OO00))  #line:1346
        if os.path.exists(OOO00OOOO00OO0000):
            os.remove(OOO00OOOO00OO0000)  #line:1348
        if not os.path.exists(OOOOO0O0OO000OO00):  #line:1349
            O0O0000000O0OOOO0._backup_fail_list.append(
                OOOOO0000OOOO00O0)  #line:1350
            raise Exception('导出sql文件失败!')  #line:1351
        print(" ==> 成功")  #line:1352
        if O0O0000000O0OOOO0._compress:  #line:1353
            _OO00O0OOOOOO00OOO = O0O0000000O0OOOO0.zip_file(
                OOOOO0O0OO000OO00)  #line:1354
        else:  #line:1355
            _OO00O0OOOOOO00OOO = os.path.getsize(OOOOO0O0OO000OO00)  #line:1356
        print("|-文件大小: {}MB, 耗时: {}秒".format(
            round(_OO00O0OOOOOO00OOO / 1024 / 1024, 2),
            round(time.time() - OOO00O0OO000000O0, 2)))  #line:1358
        print("-" * 60)  #line:1359

    def get_date_folder(OO0O000OO0OO00000, OOO0OOO000OO0000O):  #line:1361
        ""  #line:1367
        OOO00O0O00000O0O0 = []  #line:1368
        for O00O0OO000O0O0000 in os.listdir(OOO0OOO000OO0000O):  #line:1369
            if os.path.isdir(os.path.join(OOO0OOO000OO0000O,
                                          O00O0OO000O0O0000)):  #line:1370
                OO0OO0OOOOOO0O000 = "([0-9]{4})-([0-9]{2})-([0-9]{2})"  #line:1371
                O000OOO000O0OOO0O = re.search(
                    OO0OO0OOOOOO0O000, str(O00O0OO000O0O0000))  #line:1372
                if O000OOO000O0OOO0O:  #line:1373
                    OOO00O0O00000O0O0.append(O000OOO000O0OOO0O[0])  #line:1374
        return OOO00O0O00000O0O0  #line:1375

    def kill_process(OOOO0O00OOOOOOO00):  #line:1377
        ""  #line:1381
        for O0O00OO0OOO00OOOO in range(3):  #line:1382
            O0OO0OO0O000OO0OO = "'{} {} --db_name {} --binlog_id'".format(
                OOOO0O00OOOOOOO00._python_path,
                OOOO0O00OOOOOOO00._binlogModel_py,
                OOOO0O00OOOOOOO00._db_name)  #line:1384
            OO000O00O0O0O0OO0 = os.popen(
                'ps aux | grep {} |grep -v grep'.format(
                    O0OO0OO0O000OO0OO))  #line:1386
            OOOOOO0O0OOO0OOOO = OO000O00O0O0O0OO0.read()  #line:1387
            for O0O00OO0OOO00OOOO in OOOOOO0O0OOO0OOOO.strip().split(
                    '\n'):  #line:1388
                if len(O0O00OO0OOO00OOOO.split()) < 16: continue  #line:1389
                O00OO0O0O00OOOO0O = int(
                    O0O00OO0OOO00OOOO.split()[9].split(':')[0])  #line:1390
                OOO0O00O0OO0O0O0O = O0O00OO0OOO00OOOO.split()[1]  #line:1391
                if not public.M('mysqlbinlog_backup_setting').where(
                        'id=?',
                        O0O00OO0OOO00OOOO.split()
                    [15]).count() and O00OO0O0O00OOOO0O > 10:  #line:1394
                    os.kill(OOO0O00O0OO0O0O0O)  #line:1395
                if O00OO0O0O00OOOO0O > 50:  #line:1396
                    os.kill(OOO0O00O0OO0O0O0O)  #line:1397
                if OOOO0O00OOOOOOO00._binlog_id:  #line:1398
                    if O0O00OO0OOO00OOOO.split()[15] == str(
                            OOOO0O00OOOOOOO00._binlog_id
                    ) and O00OO0O0O00OOOO0O > 0:  #line:1400
                        os.kill(OOO0O00O0OO0O0O0O)  #line:1401
        OO000O00O0O0O0OO0 = os.popen('ps aux | grep {} |grep -v grep'.format(
            O0OO0OO0O000OO0OO))  #line:1403
        return OO000O00O0O0O0OO0.read().strip().split('\n')  #line:1404

    def full_backup(O00O00O000O000000):  #line:1406
        ""  #line:1411
        O00OO00O0OOOOO0OO = O00O00O000O000000._save_default_path + 'full_record.json'  #line:1412
        OO00O00OO0O0OO000 = O00OO00O0OOOOO0OO.replace('full',
                                                      'inc')  #line:1413
        O00OOO0OOOOO0OOOO = public.get_mysqldump_bin()  #line:1414
        OO0000OO0OO00O000 = public.format_date("%Y%m%d_%H%M%S")  #line:1415
        if O00O00O000O000000._tables:  #line:1417
            O0O00O0O00OO00000 = O00O00O000O000000._save_default_path + 'db_{}_{}_{}.sql'.format(
                O00O00O000O000000._db_name, O00O00O000O000000._tables,
                OO0000OO0OO00O000)  #line:1419
            OO0O00O0OOOOO0000 = '{} -uroot -p{} {} {} > {} 2>/dev/null'.format(
                O00OOO0OOOOO0OOOO, O00O00O000O000000._mysql_root_password,
                O00O00O000O000000._db_name, O00O00O000O000000._tables,
                O0O00O0O00OO00000)  #line:1422
        else:  #line:1424
            O0O00O0O00OO00000 = O00O00O000O000000._save_default_path + 'db_{}_{}.sql'.format(
                O00O00O000O000000._db_name, OO0000OO0OO00O000)  #line:1426
            OO0O00O0OOOOO0000 = O00OOO0OOOOO0OOOO + " -E -R --default-character-set=" + public.get_database_character(
                O00O00O000O000000._db_name
            ) + " --force --hex-blob --opt " + O00O00O000O000000._db_name + " -u root -p" + str(
                O00O00O000O000000._mysql_root_password
            ) + "> {} 2>/dev/null".format(O0O00O0O00OO00000)  #line:1431
        try:  #line:1432
            os.system(OO0O00O0OOOOO0000)  #line:1433
            if not os.path.isfile(O0O00O0O00OO00000): return False  #line:1434
            O00O00O000O000000.zip_file(O0O00O0O00OO00000)  #line:1435
        except Exception as OOOOOO0O0O0OO000O:  #line:1436
            print(OOOOOO0O0O0OO000O)  #line:1437
            return False  #line:1438
        O0OOO0OO0000O0O0O = O0O00O0O00OO00000.replace('.sql',
                                                      '.zip')  #line:1439
        if not os.path.isfile(O0OOO0OO0000O0O0O): return False  #line:1440
        O00O00O000O000000.clean_local_full_backups(
            O00OO00O0OOOOO0OO,
            os.path.basename(O0OOO0OO0000O0O0O),
            is_backup=True)  #line:1444
        print('|-已从磁盘清理过期备份文件')  #line:1445
        O00O00O000O000000.clean_local_inc_backups(
            OO00O00OO0O0OO000)  #line:1447
        O00O00O000O000000._full_zip_name = O00O00O000O000000._save_default_path + os.path.basename(
            O0OOO0OO0000O0O0O)  #line:1449
        if O00O00O000O000000._tables:  #line:1450
            print('|-完全备份数据库{}中表{}成功！'.format(
                O00O00O000O000000._db_name,
                O00O00O000O000000._tables))  #line:1451
        else:  #line:1452
            print('|-完全备份数据库{}成功！'.format(
                O00O00O000O000000._db_name))  #line:1453
        return True  #line:1454

    def clean_local_inc_backups(O0O0000O0OO0O0O0O,
                                O0OO000OOO00OOOO0):  #line:1456
        ""  #line:1461
        O0000O0O0O00000OO = O0O0000O0OO0O0O0O.get_date_folder(
            O0O0000O0OO0O0O0O._save_default_path)  #line:1462
        if O0000O0O0O00000OO:  #line:1463
            for OOO0OO0000O00000O in O0000O0O0O00000OO:  #line:1464
                OOOOO000O00OO00OO = os.path.join(
                    O0O0000O0OO0O0O0O._save_default_path,
                    OOO0OO0000O00000O)  #line:1465
                if os.path.exists(OOOOO000O00OO00OO):
                    shutil.rmtree(OOOOO000O00OO00OO)  #line:1466
        if os.path.isfile(O0OO000OOO00OOOO0):  #line:1467
            os.remove(O0OO000OOO00OOOO0)  #line:1468

    def clean_local_full_backups(O0OOO00O00OO0O000,
                                 O0O0OO000000OOOOO,
                                 check_name=None,
                                 is_backup=False,
                                 path=None):  #line:1474
        ""  #line:1480
        if os.path.isfile(O0O0OO000000OOOOO):  #line:1481
            OOOO0OOOO0OOOO0OO = O0OOO00O00OO0O000.get_full_backup_file(
                O0OOO00O00OO0O000._db_name,
                O0OOO00O00OO0O000._save_default_path)  #line:1483
            for O0O00O0OO000O0O00 in OOOO0OOOO0OOOO0OO:  #line:1484
                O0O0O000OO0O0O0OO = os.path.join(
                    O0OOO00O00OO0O000._save_default_path,
                    O0O00O0OO000O0O00['name'])  #line:1485
                if is_backup:  #line:1486
                    if O0O00O0OO000O0O00['name'] != check_name:
                        O0OOO00O00OO0O000.delete_file(
                            O0O0O000OO0O0O0OO)  #line:1487
                else:  #line:1488
                    O0OOO00O00OO0O000.delete_file(
                        O0O0O000OO0O0O0OO)  #line:1489
            if not is_backup:
                O0OOO00O00OO0O000.delete_file(O0O0OO000000OOOOO)  #line:1490

    def check_cloud_oss(O000O00OO00OOO0OO, O0O00OOO000000O0O):  #line:1492
        ""  #line:1497
        OO0OO0OOO0OOOOOO0 = alioss_main()  #line:1499
        O0O0O0OO00000000O = txcos_main()  #line:1500
        O0OOO0OOOOOO00OO0 = qiniu_main()  #line:1501
        OO0OOOOO00000000O = bos_main()  #line:1502
        O0OOOOO00OO0O0OOO = obs_main()  #line:1503
        O0O000OO0O00OO0O0 = ftp_main()  #line:1504
        OO0000000O00OO0OO = []  #line:1505
        O0OO000OOOO0O000O = []  #line:1506
        OO0O0000O0OO0O0OO = OO00O0OOO00OOO0OO = O0OOO0O0OOO0000O0 = O0OOO0OO0000O0O00 = O0OOOOOO0O0OOO00O = OO0000O0O0OO00O00 = False  #line:1508
        if O0O00OOO000000O0O['upload_alioss'] == 'alioss':  #line:1510
            if OO0OO0OOO0OOOOOO0.check_config():  #line:1511
                OO0000000O00OO0OO.append(OO0OO0OOO0OOOOOO0)  #line:1512
                OO0O0000O0OO0O0OO = True  #line:1513
            else:  #line:1514
                O0OO000OOOO0O000O.append('alioss')  #line:1515
        if O0O00OOO000000O0O['upload_txcos'] == 'txcos':  #line:1517
            if O0O0O0OO00000000O.check_config():  #line:1518
                OO0000000O00OO0OO.append(O0O0O0OO00000000O)  #line:1519
                OO00O0OOO00OOO0OO = True  #line:1520
            else:  #line:1521
                O0OO000OOOO0O000O.append('txcos')  #line:1522
        if O0O00OOO000000O0O['upload_qiniu'] == 'qiniu':  #line:1524
            if O0OOO0OOOOOO00OO0.check_config():  #line:1525
                OO0000000O00OO0OO.append(O0OOO0OOOOOO00OO0)  #line:1526
                O0OOO0O0OOO0000O0 = True  #line:1527
            else:  #line:1528
                O0OO000OOOO0O000O.append('qiniu')  #line:1529
        if O0O00OOO000000O0O['upload_bos'] == 'bos':  #line:1531
            if OO0OOOOO00000000O.check_config():  #line:1532
                OO0000000O00OO0OO.append(OO0OOOOO00000000O)  #line:1533
                O0OOO0OO0000O0O00 = True  #line:1534
            else:  #line:1535
                O0OO000OOOO0O000O.append('bos')  #line:1536
        if O0O00OOO000000O0O['upload_obs'] == 'obs':  #line:1538
            if O0OOOOO00OO0O0OOO.check_config():  #line:1539
                OO0000000O00OO0OO.append(O0OOOOO00OO0O0OOO)  #line:1540
                O0OOOOOO0O0OOO00O = True  #line:1541
            else:  #line:1542
                O0OO000OOOO0O000O.append('obs')  #line:1543
        if O0O00OOO000000O0O['upload_ftp'] == 'ftp':  #line:1545
            if O0O000OO0O00OO0O0.check_config():  #line:1546
                OO0000000O00OO0OO.append(O0O000OO0O00OO0O0)  #line:1547
                OO0000O0O0OO00O00 = True  #line:1548
        return OO0O0000O0OO0O0OO, OO00O0OOO00OOO0OO, O0OOO0O0OOO0000O0, O0OOO0OO0000O0O00, O0OOOOOO0O0OOO00O, OO0000O0O0OO00O00, OO0000000O00OO0OO, O0OO000OOOO0O000O  #line:1549

    def execute_by_comandline(O00O0000O00O000OO, get=None):  #line:1551
        ""  #line:1557
        O00O0000O00O000OO.install_cloud_module()  #line:1558
        if get:  #line:1559
            O00O0000O00O000OO._db_name = get.databname  #line:1560
            O00O0000O00O000OO._binlog_id = get.backup_id  #line:1561
        OOO0O0OOO0O000OOO = []  #line:1562
        OO0OOO0OO0O000000 = O00O0000O00O000OO.kill_process()  #line:1565
        if len(OO0OOO0OO0O000000) > 0:  #line:1566
            time.sleep(0.01)  #line:1567
        O0000000O00OO000O = False  #line:1568
        O000O00O000OOOOOO = O00O0000O00O000OO.get_binlog_status()  #line:1570
        if O000O00O000OOOOOO['status'] == False:  #line:1571
            OO0OO00OO00OO0000 = '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！'  #line:1572
            print(OO0OO00OO00OO0000)  #line:1573
            O0000000O00OO000O = True  #line:1574
        O00O0000O00O000OO._db_mysql = O00O0000O00O000OO._db_mysql.set_host(
            'localhost', O00O0000O00O000OO.get_mysql_port(), '', 'root',
            O00O0000O00O000OO._mysql_root_password)  #line:1579
        OOOOOOO0OO0O00OOO, OOOO0O000OOO0OOO0, OO0OO0O00OOO0O000 = O00O0000O00O000OO._mybackup.get_disk_free(
            O00O0000O00O000OO._save_default_path)  #line:1581
        if not O0000000O00OO000O:  #line:1582
            O0OO0O0OO00OO00OO = ''  #line:1583
            try:  #line:1584
                OOO0O00O0OOO0O0OO = "select sum(DATA_LENGTH)+sum(INDEX_LENGTH) from information_schema.tables where table_schema=%s"  #line:1585
                OO0OOO0O00000OOO0 = (O00O0000O00O000OO._db_name, )  #line:1586
                O000O0O0O0O000OOO = O00O0000O00O000OO._db_mysql.query(
                    OOO0O00O0OOO0O0OO, True, OO0OOO0O00000OOO0)  #line:1587
                O0OO0O0OO00OO00OO = O00O0000O00O000OO._mybackup.map_to_list(
                    O000O0O0O0O000OOO)[0][0]  #line:1588
            except:  #line:1589
                O0000000O00OO000O = True  #line:1590
                OO0OO00OO00OO0000 = "数据库连接异常，请检查root用户权限或者数据库配置参数是否正确。"  #line:1591
                print(OO0OO00OO00OO0000)  #line:1592
                OOO0O0OOO0O000OOO.append(OO0OO00OO00OO0000)  #line:1593
            if O0OO0O0OO00OO00OO == None:  #line:1595
                OO0OO00OO00OO0000 = '指定数据库 `{}` 没有任何数据!'.format(
                    O00O0000O00O000OO._db_name)  #line:1596
                O0000000O00OO000O = True  #line:1597
                print(OO0OO00OO00OO0000)  #line:1598
                OOO0O0OOO0O000OOO.append(OO0OO00OO00OO0000)  #line:1599
            if OOOOOOO0OO0O00OOO:  #line:1601
                if O0OO0O0OO00OO00OO:  #line:1602
                    if OOOO0O000OOO0OOO0 < O0OO0O0OO00OO00OO:  #line:1603
                        OO0OO00OO00OO0000 = "目标分区可用的磁盘空间小于{},无法完成备份，请增加磁盘容量!".format(
                            public.to_size(O0OO0O0OO00OO00OO))  #line:1605
                        print(OO0OO00OO00OO0000)  #line:1606
                        O0000000O00OO000O = True  #line:1607
                        OOO0O0OOO0O000OOO.append(OO0OO00OO00OO0000)  #line:1608
                if OO0OO0O00OOO0O000 < O00O0000O00O000OO._inode_min:  #line:1610
                    OO0OO00OO00OO0000 = "目标分区可用的Inode小于{},无法完成备份，请增加磁盘容量!".format(
                        O00O0000O00O000OO._inode_min)  #line:1612
                    print(OO0OO00OO00OO0000)  #line:1613
                    O0000000O00OO000O = True  #line:1614
                    OOO0O0OOO0O000OOO.append(OO0OO00OO00OO0000)  #line:1615
        O00O0000O00O000OO._pdata = O000OO0000000OOO0 = public.M(
            'mysqlbinlog_backup_setting').where(
                'id=?', str(O00O0000O00O000OO._binlog_id)).find()  #line:1619
        O0OOOOO00000OOOO0 = O000OO0000000OOO0[
            'database_table'] if O000OO0000000OOO0 else O00O0000O00O000OO._db_name  #line:1620
        O00O0000O00O000OO._echo_info['echo'] = public.M('crontab').where(
            "sBody=?", ('{} {} --db_name {} --binlog_id {}'.format(
                O00O0000O00O000OO._python_path,
                O00O0000O00O000OO._binlogModel_py, O00O0000O00O000OO._db_name,
                str(O00O0000O00O000OO._binlog_id)), )).getField(
                    'echo')  #line:1625
        O00O0000O00O000OO._mybackup = backup(
            cron_info=O00O0000O00O000OO._echo_info)  #line:1626
        if not O000OO0000000OOO0:  #line:1627
            print('未在数据库备份记录中找到id为{}的计划任务'.format(
                O00O0000O00O000OO._binlog_id))  #line:1628
            O0000000O00OO000O = True  #line:1629
        if O00O0000O00O000OO._db_name not in O00O0000O00O000OO.get_tables_list(
                O00O0000O00O000OO.get_databases()):  #line:1630
            print('备份的数据库不存在')  #line:1631
            O0000000O00OO000O = True  #line:1632
        if O0000000O00OO000O:  #line:1633
            O00O0000O00O000OO.send_failture_notification(
                OOO0O0OOO0O000OOO, target=O0OOOOO00000OOOO0)  #line:1635
            return public.returnMsg(False, '备份失败')  #line:1636
        O00O0000O00O000OO._zip_password = O000OO0000000OOO0[
            'zip_password']  #line:1637
        if O000OO0000000OOO0['backup_type'] == 'tables':
            O00O0000O00O000OO._tables = O000OO0000000OOO0[
                'tb_name']  #line:1638
        O00O0000O00O000OO._save_default_path = O000OO0000000OOO0[
            'save_path']  #line:1639
        print("|-分区{}可用磁盘空间为：{},可用Inode为:{}".format(
            OOOOOOO0OO0O00OOO, public.to_size(OOOO0O000OOO0OOO0),
            OO0OO0O00OOO0O000))  #line:1642
        if not os.path.exists(
                O00O0000O00O000OO._save_default_path):  #line:1644
            os.makedirs(O00O0000O00O000OO._save_default_path)  #line:1645
            O000OOO0OOO0OO0O0 = True  #line:1646
        O00O0000O00O000OO._full_file = O00O0000O00O000OO._save_default_path + 'full_record.json'  #line:1647
        O00O0000O00O000OO._inc_file = OO00O0OO000OO000O = O00O0000O00O000OO._save_default_path + 'inc_record.json'  #line:1648
        O000OO0000000OOO0[
            'last_excute_backup_time'] = O00O0000O00O000OO._backup_end_time = public.format_date(
            )  #line:1651
        O00O0000O00O000OO._tables = O000OO0000000OOO0['tb_name']  #line:1652
        OO000000000000O00 = '/tables/' + O00O0000O00O000OO._tables + '/' if O00O0000O00O000OO._tables else '/databases/'  #line:1653
        O00O0000O00O000OO._backup_type = 'tables' if O00O0000O00O000OO._tables else 'databases'  #line:1654
        OOO0OOOOOO0O00O00 = O000OO0000000OOO0['start_backup_time']  #line:1656
        O00OOOO0O0OOO0000 = O000OO0000000OOO0['end_backup_time']  #line:1657
        O000OOO0OOO0OO0O0 = False  #line:1658
        OO000O00O0OOO0000 = {
            'alioss': '阿里云OSS',
            'txcos': '腾讯云COS',
            'qiniu': '七牛云存储',
            'bos': '百度云存储',
            'obs': '华为云存储'
        }  #line:1665
        O00O0O00OOO0O0O0O, O000OOO0OO0O00OOO, OOOOOOO000O00O000, O000O0OO000O000OO, OO0OOO0O00O0OO0OO, OO00000OO00000O00, O0000O00000OOO00O, OO0O000O00O0OOOOO = O00O0000O00O000OO.check_cloud_oss(
            O000OO0000000OOO0)  #line:1668
        if OO0O000O00O0OOOOO:  #line:1669
            OOOOO0000OOOO00OO = []  #line:1670
            print('检测到无法连接上以下云存储：')  #line:1671
            for OO0OO0OOOOO0O0O0O in OO0O000O00O0OOOOO:  #line:1672
                if not OO0OO0OOOOO0O0O0O: continue  #line:1673
                OOOOO0000OOOO00OO.append(
                    OO000O00O0OOO0000[OO0OO0OOOOO0O0O0O])  #line:1674
                print('{}'.format(
                    OO000O00O0OOO0000[OO0OO0OOOOO0O0O0O]))  #line:1675
            OO0OO00OO00OO0000 = '检测到无法连接上以下云存储：{}'.format(
                OOOOO0000OOOO00OO)  #line:1676
            print('请检查配置或者更改备份设置！')  #line:1677
            O00O0000O00O000OO.send_failture_notification(
                OO0OO00OO00OO0000, target=O0OOOOO00000OOOO0)  #line:1679
            return public.returnMsg(False, '备份失败')  #line:1680
        if not os.path.isfile(O00O0000O00O000OO._full_file):  #line:1682
            O00O0000O00O000OO.auto_download_file(
                O0000O00000OOO00O, O00O0000O00O000OO._full_file)  #line:1684
        OO00O000OOOOOO0O0 = {}  #line:1685
        if os.path.isfile(O00O0000O00O000OO._full_file):  #line:1686
            try:  #line:1687
                OO00O000OOOOOO0O0 = json.loads(
                    public.readFile(
                        O00O0000O00O000OO._full_file))[0]  #line:1688
                if 'name' not in OO00O000OOOOOO0O0 or 'size' not in OO00O000OOOOOO0O0 or 'time' not in OO00O000OOOOOO0O0:  #line:1689
                    O000OOO0OOO0OO0O0 = True  #line:1690
                if 'end_time' in OO00O000OOOOOO0O0:  #line:1691
                    if OO00O000OOOOOO0O0['end_time'] != OO00O000OOOOOO0O0[
                            'end_time'].split(':')[0] + ':00:00':  #line:1693
                        O00OOOO0O0OOO0000 = OO00O000OOOOOO0O0[
                            'end_time'].split(':')[0] + ':00:00'  #line:1695
                if 'full_name' in OO00O000OOOOOO0O0 and os.path.isfile(
                        OO00O000OOOOOO0O0['full_name']
                ) and time.time() - public.to_date(
                        times=OOO0OOOOOO0O00O00) > 604800:  #line:1698
                    O000OOO0OOO0OO0O0 = True  #line:1699
                if 'time' in OO00O000OOOOOO0O0:  #line:1701
                    OOO0OOOOOO0O00O00 = OO00O000OOOOOO0O0['time']  #line:1702
                    if not os.path.isfile(
                            O00O0000O00O000OO._inc_file
                    ) and O00OOOO0O0OOO0000 != OO00O000OOOOOO0O0[
                            'time']:  #line:1705
                        O00O0000O00O000OO.auto_download_file(
                            O0000O00000OOO00O,
                            O00O0000O00O000OO._inc_file)  #line:1707
                    if not os.path.isfile(
                            O00O0000O00O000OO._inc_file
                    ) and O00OOOO0O0OOO0000 != OO00O000OOOOOO0O0[
                            'time']:  #line:1710
                        print('增量备份记录文件不存在,将执行完全备份')  #line:1711
                        O000OOO0OOO0OO0O0 = True  #line:1712
            except:  #line:1713
                OO00O000OOOOOO0O0 = {}  #line:1714
                O000OOO0OOO0OO0O0 = True  #line:1715
        else:  #line:1716
            O000OOO0OOO0OO0O0 = True  #line:1717
        O0O0O000OO0OOOOOO = False  #line:1718
        if O000OOO0OOO0OO0O0:  #line:1721
            print('☆☆☆完全备份开始☆☆☆')  #line:1722
            OO0OOO0O000OO000O = []  #line:1723
            if not O00O0000O00O000OO.full_backup():  #line:1724
                OO0OO00OO00OO0000 = '全量备份数据库[{}]'.format(
                    O00O0000O00O000OO._db_name)  #line:1725
                O00O0000O00O000OO.send_failture_notification(
                    OO0OO00OO00OO0000, target=O0OOOOO00000OOOO0)  #line:1726
                return public.returnMsg(False, OO0OO00OO00OO0000)  #line:1727
            if os.path.isfile(O00O0000O00O000OO._full_file):  #line:1728
                try:  #line:1729
                    OO0OOO0O000OO000O = json.loads(
                        public.readFile(
                            O00O0000O00O000OO._full_file))  #line:1730
                except:  #line:1731
                    OO0OOO0O000OO000O = []  #line:1732
            O00O0000O00O000OO.set_file_info(O00O0000O00O000OO._full_zip_name,
                                            O00O0000O00O000OO._full_file,
                                            is_full=True)  #line:1736
            try:  #line:1737
                OO00O000OOOOOO0O0 = json.loads(
                    public.readFile(
                        O00O0000O00O000OO._full_file))[0]  #line:1738
            except:  #line:1739
                print('|-文件写入失败，检查是否有安装安全软件！')  #line:1740
                print('|-备份失败！')  #line:1741
                return  #line:1742
            O000OO0000000OOO0['start_backup_time'] = O000OO0000000OOO0[
                'end_backup_time'] = OO00O000OOOOOO0O0['time']  #line:1744
            public.M('mysqlbinlog_backup_setting').where(
                'id=?',
                O000OO0000000OOO0['id']).update(O000OO0000000OOO0)  #line:1746
            O0OOO0OOO00OOO0O0 = '/bt_backup/mysql_bin_log/' + O00O0000O00O000OO._db_name + OO000000000000O00  #line:1747
            OO00O0OOOO0O0O0O0 = O0OOO0OOO00OOO0O0 + OO00O000OOOOOO0O0[
                'name']  #line:1748
            OO0000000000OOOO0 = O0OOO0OOO00OOO0O0 + 'full_record.json'  #line:1749
            OO00O0OOOO0O0O0O0 = OO00O0OOOO0O0O0O0.replace('//',
                                                          '/')  #line:1750
            OO0000000000OOOO0 = OO0000000000OOOO0.replace('//',
                                                          '/')  #line:1751
            if O00O0O00OOO0O0O0O:  #line:1753
                OOO0O0O0O00O0OOO0 = alioss_main()  #line:1754
                if not OOO0O0O0O00O0OOO0.upload_file_by_path(
                        OO00O000OOOOOO0O0['full_name'],
                        OO00O0OOOO0O0O0O0):  #line:1756
                    O00O0000O00O000OO._cloud_upload_not.append(
                        OO00O000OOOOOO0O0['full_name'])  #line:1757
                if not OOO0O0O0O00O0OOO0.upload_file_by_path(
                        O00O0000O00O000OO._full_file,
                        OO0000000000OOOO0):  #line:1758
                    O00O0000O00O000OO._cloud_upload_not.append(
                        O00O0000O00O000OO._full_file)  #line:1759
                O00O0000O00O000OO.clean_cloud_backups(
                    O0OOO0OOO00OOO0O0, O00O0000O00O000OO._full_file,
                    OOO0O0O0O00O0OOO0, OO000O00O0OOO0000['alioss'])  #line:1762
            else:  #line:1763
                if O000OO0000000OOO0['upload_alioss'] == 'alioss':  #line:1764
                    OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                        OO000O00O0OOO0000['alioss'],
                        OO000O00O0OOO0000['alioss'])  #line:1766
                    O0O0O000OO0OOOOOO = True  #line:1767
                    print(OO0OO00OO00OO0000)  #line:1768
            if O000OOO0OO0O00OOO:  #line:1770
                OOOO0OOO000O0O000 = txcos_main()  #line:1771
                if not OOOO0OOO000O0O000.upload_file_by_path(
                        OO00O000OOOOOO0O0['full_name'],
                        OO00O0OOOO0O0O0O0):  #line:1773
                    O00O0000O00O000OO._cloud_upload_not.append(
                        OO00O000OOOOOO0O0['full_name'])  #line:1774
                if not OOOO0OOO000O0O000.upload_file_by_path(
                        O00O0000O00O000OO._full_file,
                        OO0000000000OOOO0):  #line:1775
                    O00O0000O00O000OO._cloud_upload_not.append(
                        O00O0000O00O000OO._full_file)  #line:1776
                O00O0000O00O000OO.clean_cloud_backups(
                    O0OOO0OOO00OOO0O0, O00O0000O00O000OO._full_file,
                    OOOO0OOO000O0O000, OO000O00O0OOO0000['txcos'])  #line:1779
            else:  #line:1780
                if O000OO0000000OOO0['upload_txcos'] == 'txcos':  #line:1781
                    OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                        OO000O00O0OOO0000['txcos'],
                        OO000O00O0OOO0000['txcos'])  #line:1783
                    O0O0O000OO0OOOOOO = True  #line:1784
                    print(OO0OO00OO00OO0000)  #line:1785
            if OOOOOOO000O00O000:  #line:1787
                O00O0OOOO0O0O0OO0 = qiniu_main()  #line:1788
                if not O00O0OOOO0O0O0OO0.upload_file_by_path(
                        OO00O000OOOOOO0O0['full_name'],
                        OO00O0OOOO0O0O0O0):  #line:1790
                    O00O0000O00O000OO._cloud_upload_not.append(
                        OO00O000OOOOOO0O0['full_name'])  #line:1791
                if not O00O0OOOO0O0O0OO0.upload_file_by_path(
                        O00O0000O00O000OO._full_file,
                        OO0000000000OOOO0):  #line:1792
                    O00O0000O00O000OO._cloud_upload_not.append(
                        O00O0000O00O000OO._full_file)  #line:1793
                O00O0000O00O000OO.clean_cloud_backups(
                    O0OOO0OOO00OOO0O0, O00O0000O00O000OO._full_file,
                    O00O0OOOO0O0O0OO0, OO000O00O0OOO0000['qiniu'])  #line:1796
            else:  #line:1797
                if O000OO0000000OOO0['upload_qiniu'] == 'qiniu':  #line:1798
                    OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                        OO000O00O0OOO0000['qiniu'],
                        OO000O00O0OOO0000['qiniu'])  #line:1800
                    O0O0O000OO0OOOOOO = True  #line:1801
                    print(OO0OO00OO00OO0000)  #line:1802
            if O000O0OO000O000OO:  #line:1804
                O0OOOO0O00OO000O0 = bos_main()  #line:1805
                if not O0OOOO0O00OO000O0.upload_file_by_path(
                        OO00O000OOOOOO0O0['full_name'],
                        OO00O0OOOO0O0O0O0):  #line:1807
                    O00O0000O00O000OO._cloud_upload_not.append(
                        OO00O000OOOOOO0O0['full_name'])  #line:1808
                if not O0OOOO0O00OO000O0.upload_file_by_path(
                        O00O0000O00O000OO._full_file,
                        OO0000000000OOOO0):  #line:1809
                    O00O0000O00O000OO._cloud_upload_not.append(
                        O00O0000O00O000OO._full_file)  #line:1810
                O00O0000O00O000OO.clean_cloud_backups(
                    O0OOO0OOO00OOO0O0, O00O0000O00O000OO._full_file,
                    O0OOOO0O00OO000O0, OO000O00O0OOO0000['bos'])  #line:1813
            else:  #line:1814
                if O000OO0000000OOO0['upload_bos'] == 'bos':  #line:1815
                    OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                        OO000O00O0OOO0000['bos'],
                        OO000O00O0OOO0000['bos'])  #line:1817
                    O0O0O000OO0OOOOOO = True  #line:1818
                    print(OO0OO00OO00OO0000)  #line:1819
            if OO0OOO0O00O0OO0OO:  #line:1822
                O00O00OOOO00O0O0O = obs_main()  #line:1823
                if not O00O00OOOO00O0O0O.upload_file_by_path(
                        OO00O000OOOOOO0O0['full_name'],
                        OO00O0OOOO0O0O0O0):  #line:1825
                    O00O0000O00O000OO._cloud_upload_not.append(
                        OO00O000OOOOOO0O0['full_name'])  #line:1826
                if not O00O00OOOO00O0O0O.upload_file_by_path(
                        O00O0000O00O000OO._full_file,
                        OO0000000000OOOO0):  #line:1827
                    O00O0000O00O000OO._cloud_upload_not.append(
                        O00O0000O00O000OO._full_file)  #line:1828
                O00O0000O00O000OO.clean_cloud_backups(
                    O0OOO0OOO00OOO0O0, O00O0000O00O000OO._full_file,
                    O00O00OOOO00O0O0O, OO000O00O0OOO0000['obs'])  #line:1831
            else:  #line:1832
                if O000OO0000000OOO0['upload_obs'] == 'obs':  #line:1833
                    OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                        OO000O00O0OOO0000['obs'],
                        OO000O00O0OOO0000['obs'])  #line:1835
                    O0O0O000OO0OOOOOO = True  #line:1836
                    print(OO0OO00OO00OO0000)  #line:1837
            if OO00000OO00000O00:  #line:1840
                OO000O0OOOO0O000O = ftp_main()  #line:1841
                if not OO000O0OOOO0O000O.upload_file_by_path(
                        OO00O000OOOOOO0O0['full_name'],
                        OO00O0OOOO0O0O0O0):  #line:1843
                    O00O0000O00O000OO._cloud_upload_not.append(
                        OO00O000OOOOOO0O0['full_name'])  #line:1844
                if not OO000O0OOOO0O000O.upload_file_by_path(
                        O00O0000O00O000OO._full_file,
                        OO0000000000OOOO0):  #line:1845
                    O00O0000O00O000OO._cloud_upload_not.append(
                        O00O0000O00O000OO._full_file)  #line:1846
                O00O0000O00O000OO.clean_cloud_backups(
                    O0OOO0OOO00OOO0O0, O00O0000O00O000OO._full_file,
                    OO000O0OOOO0O000O, OO000O00O0OOO0000['ftp'])  #line:1849
            else:  #line:1850
                if O000OO0000000OOO0['upload_ftp'] == 'ftp':  #line:1851
                    OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                        OO000O00O0OOO0000['ftp'],
                        OO000O00O0OOO0000['ftp'])  #line:1853
                    O0O0O000OO0OOOOOO = True  #line:1854
                    print(OO0OO00OO00OO0000)  #line:1855
            OO0OO00OO00OO0000 = '以下文件上传失败：{}'.format(
                O00O0000O00O000OO._cloud_upload_not)  #line:1856
            if O00O0000O00O000OO._cloud_upload_not or O0O0O000OO0OOOOOO:  #line:1857
                O00O0000O00O000OO.send_failture_notification(
                    OO0OO00OO00OO0000, target=O0OOOOO00000OOOO0)  #line:1858
                if OO0OOO0O000OO000O:  #line:1859
                    public.writeFile(O00O0000O00O000OO._full_file,
                                     json.dumps(OO0OOO0O000OO000O))  #line:1860
            print('☆☆☆完全备份结束☆☆☆')  #line:1861
            OOOO000O0O0OOO000 = 'full'  #line:1862
            OO000O0OO0000000O = json.loads(
                public.readFile(O00O0000O00O000OO._full_file))  #line:1863
            O00O0000O00O000OO.write_backups(OOOO000O0O0OOO000,
                                            OO000O0OO0000000O)  #line:1864
            if O000OO0000000OOO0['upload_local'] == '' and os.path.isfile(
                    O00O0000O00O000OO._full_file):  #line:1866
                O00O0000O00O000OO.clean_local_full_backups(
                    O00O0000O00O000OO._full_file)  #line:1867
                if os.path.isfile(O00O0000O00O000OO._inc_file):  #line:1868
                    O00O0000O00O000OO.clean_local_inc_backups(
                        O00O0000O00O000OO._inc_file)  #line:1869
                print('|-用户设置不保留本地备份，已从本地服务器清理备份')  #line:1870
            return public.returnMsg(True, '完全备份成功！')  #line:1871
        O00O0000O00O000OO._backup_add_time = O000OO0000000OOO0[
            'start_backup_time']  #line:1873
        O00O0000O00O000OO._backup_start_time = O00OOOO0O0OOO0000  #line:1874
        O00O0000O00O000OO._new_tables = O00O0000O00O000OO.get_tables_list(
            O00O0000O00O000OO.get_tables())  #line:1875
        if O00O0000O00O000OO._backup_start_time and O00O0000O00O000OO._backup_end_time:  #line:1876
            O0O000OOOO0OO000O = O00O0000O00O000OO.import_start_end(
                O00O0000O00O000OO._backup_start_time,
                O00O0000O00O000OO._backup_end_time)  #line:1878
            for O00O0000O0000OOO0 in O0O000OOOO0OO000O:  #line:1879
                if not O00O0000O0000OOO0: continue  #line:1880
                O00O0000O00O000OO._backup_fail_list = []  #line:1881
                if public.to_date(
                        times=O00O0000O0000OOO0['end_time']) > public.to_date(
                            times=O00O0000O00O000OO._backup_end_time
                        ):  #line:1883
                    O00O0000O0000OOO0[
                        'end_time'] = O00O0000O00O000OO._backup_end_time  #line:1884
                O00O0000O00O000OO.import_date(
                    O00O0000O0000OOO0['start_time'],
                    O00O0000O0000OOO0['end_time'])  #line:1885
        O0O000OOOOO0O0O0O = O000OO0000000OOO0['save_path']  #line:1887
        O000OOO0O0O0000OO = O00O0000O00O000OO.get_every_day(
            O00O0000O00O000OO._backup_start_time.split()[0],
            O00O0000O00O000OO._backup_end_time.split()[0])  #line:1890
        O00O00OO0O0O00000 = 'True'  #line:1891
        O00OOO0O0OO000000 = O00O0000O00O000OO.get_start_end_binlog(
            O00O0000O00O000OO._backup_start_time,
            O00O0000O00O000OO._backup_end_time, O00O00OO0O0O00000)  #line:1893
        O00OO00OO0OO0OOOO = O00O0000O00O000OO.traverse_all_files(
            O0O000OOOOO0O0O0O, O000OOO0O0O0000OO,
            O00OOO0O0OO000000)  #line:1895
        if O00O0000O00O000OO._backup_fail_list or O00OO00OO0OO0OOOO[
                'file_lists_not']:  #line:1896
            OOOOOO00O00O0OOO0 = ''  #line:1897
            if O00O0000O00O000OO._backup_fail_list:
                OOOOOO00O00O0OOO0 = O00O0000O00O000OO._backup_fail_list  #line:1898
            else:
                OOOOOO00O00O0OOO0 = O00OO00OO0OO0OOOO[
                    'file_lists_not']  #line:1899
            OO0OO00OO00OO0000 = '以下文件备份失败{}'.format(
                OOOOOO00O00O0OOO0)  #line:1901
            O00O0000O00O000OO.send_failture_notification(
                OO0OO00OO00OO0000, target=O0OOOOO00000OOOO0)  #line:1903
            print(OO0OO00OO00OO0000)  #line:1904
            return public.returnMsg(False, OO0OO00OO00OO0000)  #line:1905
        O0000OOO00000OO00 = json.loads(
            public.readFile(O00O0000O00O000OO._full_file))  #line:1906
        O000OO0000000OOO0[
            'end_backup_time'] = O00O0000O00O000OO._backup_end_time  #line:1908
        O000OO0000000OOO0['table_list'] = '|'.join(
            O00O0000O00O000OO._new_tables)  #line:1910
        O00O0000O00O000OO.update_file_info(
            O00O0000O00O000OO._full_file,
            O00O0000O00O000OO._backup_end_time)  #line:1911
        O00OOOOOOO00O0OO0 = OOO0OOO0O000O000O = False  #line:1913
        for OO00000000OO000OO in O00OO00OO0OO0OOOO['data']:  #line:1914
            if OO00000000OO000OO == O00OO00OO0OO0OOOO['data'][-1]:
                O00OOOOOOO00O0OO0 = True  #line:1915
            for OO0OO00O0000O0OO0 in OO00000000OO000OO:  #line:1916
                if OO0OO00O0000O0OO0 == OO00000000OO000OO[-1]:
                    OOO0OOO0O000O000O = True  #line:1917
                O00O0000O00O000OO.set_file_info(OO0OO00O0000O0OO0,
                                                OO00O0OO000OO000O)  #line:1918
                OO0O00OO0O000OOOO = '/bt_backup/mysql_bin_log/' + O00O0000O00O000OO._db_name + OO000000000000O00  #line:1919
                OOOOOOO0OOO0O000O = OO0O00OO0O000OOOO + 'full_record.json'  #line:1920
                OO000O0OO00O00O0O = OO0O00OO0O000OOOO + 'inc_record.json'  #line:1921
                OO00O0OOOO0O0O0O0 = '/bt_backup/mysql_bin_log/' + O00O0000O00O000OO._db_name + OO000000000000O00 + OO0OO00O0000O0OO0.split(
                    '/')[-2] + '/' + OO0OO00O0000O0OO0.split('/')[
                        -1]  #line:1923
                if O00O0O00OOO0O0O0O:  #line:1924
                    OOO0O0O0O00O0OOO0 = alioss_main()  #line:1925
                    if not OOO0O0O0O00O0OOO0.upload_file_by_path(
                            OO0OO00O0000O0OO0, OO00O0OOOO0O0O0O0):  #line:1926
                        O00O0000O00O000OO._cloud_upload_not.append(
                            OO0OO00O0000O0OO0)  #line:1927
                    if os.path.isfile(
                            OO00O0OO000OO000O
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1928
                        OOO0O0O0O00O0OOO0.upload_file_by_path(
                            OO00O0OO000OO000O, OO000O0OO00O00O0O)  #line:1929
                    if os.path.isfile(
                            O00O0000O00O000OO._full_file
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1931
                        OOO0O0O0O00O0OOO0.upload_file_by_path(
                            O00O0000O00O000OO._full_file,
                            OOOOOOO0OOO0O000O)  #line:1933
                else:  #line:1934
                    if O000OO0000000OOO0[
                            'upload_alioss'] == 'alioss':  #line:1935
                        OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                            OO000O00O0OOO0000['alioss'],
                            OO000O00O0OOO0000['alioss'])  #line:1937
                        O0O0O000OO0OOOOOO = True  #line:1938
                        print(OO0OO00OO00OO0000)  #line:1939
                if O000OOO0OO0O00OOO:  #line:1940
                    OOOO0OOO000O0O000 = txcos_main()  #line:1941
                    if not OOOO0OOO000O0O000.upload_file_by_path(
                            OO0OO00O0000O0OO0, OO00O0OOOO0O0O0O0):  #line:1942
                        O00O0000O00O000OO._cloud_upload_not.append(
                            OO0OO00O0000O0OO0)  #line:1943
                    if os.path.isfile(
                            OO00O0OO000OO000O
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1944
                        OOOO0OOO000O0O000.upload_file_by_path(
                            OO00O0OO000OO000O, OO000O0OO00O00O0O)  #line:1945
                    if os.path.isfile(
                            O00O0000O00O000OO._full_file
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1947
                        OOOO0OOO000O0O000.upload_file_by_path(
                            OO00O0OO000OO000O, OOOOOOO0OOO0O000O)  #line:1948
                else:  #line:1949
                    if O000OO0000000OOO0[
                            'upload_txcos'] == 'txcos':  #line:1950
                        OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                            OO000O00O0OOO0000['txcos'],
                            OO000O00O0OOO0000['txcos'])  #line:1952
                        O0O0O000OO0OOOOOO = True  #line:1953
                        print(OO0OO00OO00OO0000)  #line:1954
                if OOOOOOO000O00O000:  #line:1955
                    O00O0OOOO0O0O0OO0 = qiniu_main()  #line:1956
                    if not O00O0OOOO0O0O0OO0.upload_file_by_path(
                            OO0OO00O0000O0OO0, OO00O0OOOO0O0O0O0):  #line:1957
                        O00O0000O00O000OO._cloud_upload_not.append(
                            OO0OO00O0000O0OO0)  #line:1958
                    if os.path.isfile(
                            OO00O0OO000OO000O
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1959
                        O00O0OOOO0O0O0OO0.upload_file_by_path(
                            OO00O0OO000OO000O, OO000O0OO00O00O0O)  #line:1960
                    if os.path.isfile(
                            O00O0000O00O000OO._full_file
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1962
                        O00O0OOOO0O0O0OO0.upload_file_by_path(
                            OO00O0OO000OO000O, OOOOOOO0OOO0O000O)  #line:1963
                else:  #line:1964
                    if O000OO0000000OOO0[
                            'upload_qiniu'] == 'qiniu':  #line:1965
                        OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                            OO000O00O0OOO0000['qiniu'],
                            OO000O00O0OOO0000['qiniu'])  #line:1967
                        O0O0O000OO0OOOOOO = True  #line:1968
                        print(OO0OO00OO00OO0000)  #line:1969
                if O000O0OO000O000OO:  #line:1970
                    O0OOOO0O00OO000O0 = bos_main()  #line:1971
                    if not O0OOOO0O00OO000O0.upload_file_by_path(
                            OO0OO00O0000O0OO0, OO00O0OOOO0O0O0O0):  #line:1972
                        O00O0000O00O000OO._cloud_upload_not.append(
                            OO0OO00O0000O0OO0)  #line:1973
                    if os.path.isfile(
                            OO00O0OO000OO000O
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1974
                        O0OOOO0O00OO000O0.upload_file_by_path(
                            OO00O0OO000OO000O, OO000O0OO00O00O0O)  #line:1975
                    if os.path.isfile(
                            O00O0000O00O000OO._full_file
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1977
                        O0OOOO0O00OO000O0.upload_file_by_path(
                            OO00O0OO000OO000O, OOOOOOO0OOO0O000O)  #line:1978
                else:  #line:1979
                    if O000OO0000000OOO0['upload_bos'] == 'bos':  #line:1980
                        OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                            OO000O00O0OOO0000['bos'],
                            OO000O00O0OOO0000['bos'])  #line:1982
                        O0O0O000OO0OOOOOO = True  #line:1983
                        print(OO0OO00OO00OO0000)  #line:1984
                if OO0OOO0O00O0OO0OO:  #line:1986
                    O00O00OOOO00O0O0O = obs_main()  #line:1987
                    if not O00O00OOOO00O0O0O.upload_file_by_path(
                            OO0OO00O0000O0OO0, OO00O0OOOO0O0O0O0):  #line:1988
                        O00O0000O00O000OO._cloud_upload_not.append(
                            OO0OO00O0000O0OO0)  #line:1989
                    if os.path.isfile(
                            OO00O0OO000OO000O
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1990
                        O00O00OOOO00O0O0O.upload_file_by_path(
                            OO00O0OO000OO000O, OO000O0OO00O00O0O)  #line:1991
                    if os.path.isfile(
                            O00O0000O00O000OO._full_file
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:1993
                        O00O00OOOO00O0O0O.upload_file_by_path(
                            O00O0000O00O000OO._full_file,
                            OOOOOOO0OOO0O000O)  #line:1995
                else:  #line:1996
                    if O000OO0000000OOO0['upload_obs'] == 'obs':  #line:1997
                        OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                            OO000O00O0OOO0000['obs'],
                            OO000O00O0OOO0000['obs'])  #line:1999
                        O0O0O000OO0OOOOOO = True  #line:2000
                        print(OO0OO00OO00OO0000)  #line:2001
                if OO00000OO00000O00:  #line:2003
                    OO0OO00OOOOO0000O = ftp_main()  #line:2004
                    if not OO0OO00OOOOO0000O.upload_file_by_path(
                            OO0OO00O0000O0OO0, OO00O0OOOO0O0O0O0):  #line:2005
                        O00O0000O00O000OO._cloud_upload_not.append(
                            OO0OO00O0000O0OO0)  #line:2006
                    if os.path.isfile(
                            OO00O0OO000OO000O
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:2007
                        OO0OO00OOOOO0000O.upload_file_by_path(
                            OO00O0OO000OO000O, OO000O0OO00O00O0O)  #line:2008
                    if os.path.isfile(
                            O00O0000O00O000OO._full_file
                    ) and O00OOOOOOO00O0OO0 and OOO0OOO0O000O000O:  #line:2010
                        OOOOOOO0OOO0O000O = os.path.join(
                            '/www/wwwroot/ahongtest',
                            OOOOOOO0OOO0O000O)  #line:2012
                        OO0OO00OOOOO0000O.upload_file_by_path(
                            O00O0000O00O000OO._full_file,
                            OOOOOOO0OOO0O000O)  #line:2014
                else:  #line:2015
                    if O000OO0000000OOO0['upload_ftp'] == 'ftp':  #line:2016
                        OO0OO00OO00OO0000 = '|-无法连接上{}，无法上传到{}'.format(
                            OO000O00O0OOO0000['ftp'],
                            OO000O00O0OOO0000['ftp'])  #line:2018
                        O0O0O000OO0OOOOOO = True  #line:2019
                        print(OO0OO00OO00OO0000)  #line:2020
        OO0OO00OO00OO0000 = '以下文件上传失败：{}'.format(
            O00O0000O00O000OO._cloud_upload_not)  #line:2021
        if O00O0000O00O000OO._cloud_upload_not or O0O0O000OO0OOOOOO:  #line:2022
            O00O0000O00O000OO.send_failture_notification(
                OO0OO00OO00OO0000, target=O0OOOOO00000OOOO0)  #line:2023
            if O0000OOO00000OO00:  #line:2024
                public.writeFile(O00O0000O00O000OO._full_file,
                                 json.dumps(O0000OOO00000OO00))  #line:2025
            return public.returnMsg(False, '增量备份失败！')  #line:2026
        public.M('mysqlbinlog_backup_setting').where(
            'id=?',
            O000OO0000000OOO0['id']).update(O000OO0000000OOO0)  #line:2028
        if not O000OOO0OOO0OO0O0:  #line:2029
            OOOO000O0O0OOO000 = 'inc'  #line:2030
            OO000O0OO0000000O = json.loads(
                public.readFile(OO00O0OO000OO000O))  #line:2031
            O00O0000O00O000OO.write_backups(OOOO000O0O0OOO000,
                                            OO000O0OO0000000O)  #line:2032
        if O000OO0000000OOO0['upload_local'] == '' and os.path.isfile(
                O00O0000O00O000OO._inc_file):  #line:2033
            if os.path.isfile(O00O0000O00O000OO._full_file):  #line:2034
                O00O0000O00O000OO.clean_local_full_backups(
                    O00O0000O00O000OO._full_file)  #line:2035
            if os.path.isfile(O00O0000O00O000OO._inc_file):  #line:2037
                O00O0000O00O000OO.clean_local_inc_backups(
                    O00O0000O00O000OO._inc_file)  #line:2038
            print('|-用户设置不保留本地备份，已从本地服务器清理备份')  #line:2040
        return public.returnMsg(True, '执行备份任务成功！')  #line:2041

    def write_backups(O0OOO0OOOO0O0O00O, OOOO00000O0OOOO00,
                      O00OOO0OO0O0O0000):  #line:2043
        ""  #line:2046
        OO000O0O000OO00OO = O0OOO0OOOO0O0O00O._full_file if OOOO00000O0OOOO00 == 'full' else ''  #line:2047
        O0OOO000000OO0000 = O0OOO0OOOO0O0O00O._inc_file if OOOO00000O0OOOO00 == 'full' else ''  #line:2048
        for OOOO0OOO0O0O00O0O in O00OOO0OO0O0O0000:  #line:2049
            O0OO0OO0O0O0000OO = OOOO0OOO0O0O00O0O['full_name'].replace(
                '/www/backup', 'bt_backup')  #line:2051
            OO00O00OO00O00O00 = {
                "sid": O0OOO0OOOO0O0O00O._binlog_id,
                "size": OOOO0OOO0O0O00O0O['size'],
                "type": OOOO00000O0OOOO00,
                "full_json": OO000O0O000OO00OO,
                "inc_json": O0OOO000000OO0000,
                "local_name": OOOO0OOO0O0O00O0O['full_name'],
                "ftp_name": '',
                "alioss_name": O0OO0OO0O0O0000OO,
                "txcos_name": O0OO0OO0O0O0000OO,
                "qiniu_name": O0OO0OO0O0O0000OO,
                "aws_name": '',
                "upyun_name": '',
                "obs_name": O0OO0OO0O0O0000OO,
                "bos_name": O0OO0OO0O0O0000OO,
                "gcloud_storage_name": '',
                "gdrive_name": '',
                "msonedrive_name": ''
            }  #line:2070
            if OOOO00000O0OOOO00 == 'full' and public.M(
                    'mysqlbinlog_backups').where(
                        'type=? AND sid=?',
                        (OOOO00000O0OOOO00,
                         O0OOO0OOOO0O0O00O._binlog_id)).count():  #line:2074
                OO0OO000OOO0OOOO0 = public.M('mysqlbinlog_backups').where(
                    'type=? AND sid=?',
                    (OOOO00000O0OOOO00,
                     O0OOO0OOOO0O0O00O._binlog_id)).getField('id')  #line:2077
                public.M('mysqlbinlog_backups').delete(
                    OO0OO000OOO0OOOO0)  #line:2078
            if OOOO00000O0OOOO00 == 'full':  #line:2080
                OO0OO0O0OO0OO0000 = public.M('mysqlbinlog_backups').where(
                    'type=? AND sid=?',
                    ('inc', O0OOO0OOOO0O0O00O._binlog_id)).select()  #line:2082
                if OO0OO0O0OO0OO0000:  #line:2083
                    for OOOO0OO00OOOO000O in OO0OO0O0OO0OO0000:  #line:2084
                        if not OOOO0OO00OOOO000O: continue  #line:2085
                        if 'id' in OOOO0OO00OOOO000O:  #line:2086
                            public.M('mysqlbinlog_backups').delete(
                                OOOO0OO00OOOO000O['id'])  #line:2087
            if not public.M('mysqlbinlog_backups').where(
                    'type=? AND local_name=? AND sid=?',
                (OOOO00000O0OOOO00, OOOO0OOO0O0O00O0O['full_name'],
                 O0OOO0OOOO0O0O00O._binlog_id)).count():  #line:2092
                public.M('mysqlbinlog_backups').insert(
                    OO00O00OO00O00O00)  #line:2093
            else:  #line:2095
                OO0OO000OOO0OOOO0 = public.M('mysqlbinlog_backups').where(
                    'type=? AND local_name=? AND sid=?',
                    (OOOO00000O0OOOO00, OOOO0OOO0O0O00O0O['full_name'],
                     O0OOO0OOOO0O0O00O._binlog_id)).getField('id')  #line:2099
                public.M('mysqlbinlog_backups').where(
                    'id=?',
                    OO0OO000OOO0OOOO0).update(OO00O00OO00O00O00)  #line:2101
            if OOOO00000O0OOOO00 == 'inc' and not public.M(
                    'mysqlbinlog_backups').where(
                        'type=? AND sid=?',
                        ('full',
                         O0OOO0OOOO0O0O00O._binlog_id)).count():  #line:2105
                try:  #line:2106
                    OOO000OO00OO0OO00 = json.loads(
                        public.readFile(
                            O0OOO0OOOO0O0O00O._full_file))[0]  #line:2107
                except:  #line:2108
                    OOO000OO00OO0OO00 = {}  #line:2109
                if OOO000OO00OO0OO00:  #line:2110
                    public.M('mysqlbinlog_backups').insert(
                        OO00O00OO00O00O00)  #line:2111

    def get_tables_list(O0O0O000000O0O0O0,
                        O0OO0O00000000OOO,
                        type=False):  #line:2113
        ""  #line:2116
        O0O00O000OOO00O00 = []  #line:2117
        for OOOO0OO000O0O0000 in O0OO0O00000000OOO:  #line:2118
            if not OOOO0OO000O0O0000: continue  #line:2119
            if type:  #line:2120
                if OOOO0OO000O0O0000.get('type') != 'F': continue  #line:2121
            O0O00O000OOO00O00.append(OOOO0OO000O0O0000['name'])  #line:2122
        return O0O00O000OOO00O00  #line:2123

    def clean_cloud_backups(O0O000000O0O0000O, O0O0OO0000OO0000O,
                            O0O0OOOO0000O00O0, O00000OO0000O00OO,
                            O0O0OO0000000O0OO):  #line:2126
        ""  #line:2129
        try:  #line:2130
            O0000O00O00OO0OO0 = json.loads(
                public.readFile(O0O0OOOO0000O00O0))[0]  #line:2131
        except:  #line:2132
            O0000O00O00OO0OO0 = []  #line:2133
        O000O0OOO00O00000 = O00OOO0OO0O000OOO = O0OO0000O0OO0O0O0 = O000OOOOOO000O00O = O0OO0O0O0O00O0OOO = public.dict_obj(
        )  #line:2135
        O000O0OOO00O00000.path = O0O0OO0000OO0000O  #line:2136
        OO0000O0000O00O0O = O00000OO0000O00OO.get_list(
            O000O0OOO00O00000)  #line:2137
        if 'list' in OO0000O0000O00O0O:  #line:2138
            for O000O000000000000 in OO0000O0000O00O0O['list']:  #line:2139
                if not O000O000000000000: continue  #line:2140
                if O000O000000000000['name'][-1] == '/':  #line:2141
                    O00OOO0OO0O000OOO.path = O0O0OO0000OO0000O + O000O000000000000[
                        'name']  #line:2142
                    O00OOO0OO0O000OOO.filename = O000O000000000000[
                        'name']  #line:2143
                    O00O0O0O0OOOO0000 = O00000OO0000O00OO.get_list(
                        O00OOO0OO0O000OOO)  #line:2144
                    O00OOO0OO0O000OOO.path = O0O0OO0000OO0000O  #line:2145
                    if O00O0O0O0OOOO0000['list']:  #line:2147
                        for OO00OOO000OOO0OOO in O00O0O0O0OOOO0000[
                                'list']:  #line:2148
                            O0OO0000O0OO0O0O0.path = O0O0OO0000OO0000O + O000O000000000000[
                                'name']  #line:2149
                            O0OO0000O0OO0O0O0.filename = OO00OOO000OOO0OOO[
                                'name']  #line:2150
                            O00000OO0000O00OO.remove_file(
                                O0OO0000O0OO0O0O0)  #line:2151
                    else:  #line:2153
                        O00000OO0000O00OO.remove_file(
                            O00OOO0OO0O000OOO)  #line:2154
                if not O0000O00O00OO0OO0: continue  #line:2156
                if O000O000000000000['name'].split('.')[-1] in [
                        'zip', 'gz', 'json'
                ] and O000O000000000000['name'] != O0000O00O00OO0OO0[
                        'name'] and O000O000000000000[
                            'name'] != 'full_record.json':  #line:2160
                    O000OOOOOO000O00O.path = O0O0OO0000OO0000O  #line:2161
                    O000OOOOOO000O00O.filename = O000O000000000000[
                        'name']  #line:2162
                    O00000OO0000O00OO.remove_file(
                        O000OOOOOO000O00O)  #line:2163
                OO000O0OOO00000O0 = False  #line:2164
                if 'dir' not in O000O000000000000: continue  #line:2165
                if O000O000000000000['dir'] == True:  #line:2166
                    try:  #line:2167
                        OOOOO0OO000OO0OOO = datetime.datetime.strptime(
                            O000O000000000000['name'], '%Y-%m-%d')  #line:2169
                        OO000O0OOO00000O0 = True  #line:2170
                    except:  #line:2171
                        pass  #line:2172
                OO0O000O0O0O0O0O0 = ''  #line:2173
                if OO000O0OOO00000O0:
                    OO0O000O0O0O0O0O0 = os.path.join(
                        O0O0OO0000OO0000O,
                        O000O000000000000['name'])  #line:2174
                if OO0O000O0O0O0O0O0:  #line:2175
                    O0OO0O0O0O00O0OOO.path = OO0O000O0O0O0O0O0  #line:2176
                    O0OO0O0O0O00O0OOO.filename = ''  #line:2177
                    O0OO0O0O0O00O0OOO.is_inc = True  #line:2178
                    O00000OO0000O00OO.remove_file(
                        O0OO0O0O0O00O0OOO)  #line:2179
        print('|-已从{}清理过期备份文件'.format(O0O0OO0000000O0OO))  #line:2180

    def add_binlog_inc_backup_task(OOOO0OO0O000O0O00, O000OO0OOOOOO0000,
                                   O000O000OO0O00000):  #line:2182
        ""  #line:2188
        OO0000OO000O0OO00 = {
            "name":
            "[勿删]数据库增量备份[{}]".format(O000OO0OOOOOO0000['database_table']),
            "type":
            O000OO0OOOOOO0000['cron_type'],
            "where1":
            O000OO0OOOOOO0000['backup_cycle'],
            "hour":
            '',
            "minute":
            '0',
            "sType":
            'enterpriseBackup',
            "sName":
            O000OO0OOOOOO0000['backup_type'],
            "backupTo":
            O000O000OO0O00000,
            "save":
            '1',
            "save_local":
            '1',
            "notice":
            O000OO0OOOOOO0000['notice'],
            "notice_channel":
            O000OO0OOOOOO0000['notice_channel'],
            "sBody":
            '{} {} --db_name {} --binlog_id {}'.format(
                OOOO0OO0O000O0O00._python_path,
                OOOO0OO0O000O0O00._binlogModel_py, OOOO0OO0O000O0O00._db_name,
                str(O000OO0OOOOOO0000['id'])),
            "urladdress":
            '{}|{}|{}'.format(O000OO0OOOOOO0000['db_name'],
                              O000OO0OOOOOO0000['tb_name'],
                              O000OO0OOOOOO0000['id'])
        }  #line:2221
        import crontab  #line:2222
        OO00OO0OO0OO000O0 = crontab.crontab().AddCrontab(
            OO0000OO000O0OO00)  #line:2223
        if OO00OO0OO0OO000O0 and "id" in OO00OO0OO0OO000O0.keys():  #line:2224
            return True  #line:2225
        return False  #line:2226

    def create_table(O0O00000OOOO0OO0O):  #line:2228
        ""  #line:2233
        if not public.M('sqlite_master').where(
                'type=? AND name=?',
            ('table', 'mysqlbinlog_backup_setting')).count():  #line:2237
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
                                "add_time" INTEGER);''')  #line:2272
        if not public.M('sqlite_master').where(
                'type=? AND name=?',
            ('table', 'mysqlbinlog_backups')).count():  #line:2276
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
                                "where_4" TEXT DEFAULT '');''')  #line:2299

    def add_mysqlbinlog_backup_setting(O0OO0O0O0O0000O00,
                                       OO00O0O000O000000):  #line:2301
        ""  #line:2307
        public.set_module_logs('binlog',
                               'add_mysqlbinlog_backup_setting')  #line:2308
        if not OO00O0O000O000000.get('datab_name/str', 0):  #line:2309
            return public.returnMsg(False, '当前没有数据库，不能添加！')  #line:2310
        if OO00O0O000O000000.datab_name in [0, '0']:  #line:2311
            return public.returnMsg(False, '当前没有数据库，不能添加！')  #line:2312
        if not OO00O0O000O000000.get('backup_cycle/d', 0) > 0:  #line:2313
            return public.returnMsg(False, '备份周期不正确，只能为正整数！')  #line:2314
        OO000OOOOO0O00O0O = OOOOO000O00O0O0OO = {}  #line:2318
        O0OOO0000OOO00OOO = O0OO0O0O0O0000O00.get_binlog_status()  #line:2319
        if O0OOO0000OOO00OOO['status'] == False:  #line:2320
            return public.returnMsg(
                False, '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')  #line:2322
        O0OO0O0O0O0000O00._db_name = OOOOO000O00O0O0OO[
            'db_name'] = OO00O0O000O000000.datab_name  #line:2323
        O000O0O00OO000O0O = 'databases' if OO00O0O000O000000.backup_type == 'databases' else 'tables'  #line:2324
        O0OO0O0O0O0000O00._tables = '' if 'table_name' not in OO00O0O000O000000 else OO00O0O000O000000.table_name  #line:2325
        OO0O00OO00OO0O00O = False  #line:2326
        O0OOOOOOOOOOO0O0O = ''  #line:2328
        O000OOOOO0OO00000 = ''  #line:2329
        if O0OO0O0O0O0000O00._tables:  #line:2330
            O0OOOOOOOOOOO0O0O = public.M('mysqlbinlog_backup_setting').where(
                'db_name=? and backup_type=? and tb_name=?',
                (OO00O0O000O000000.datab_name, O000O0O00OO000O0O,
                 O0OO0O0O0O0000O00._tables)).find()  #line:2333
            if O0OOOOOOOOOOO0O0O:  #line:2334
                OO000OOOOO0O00O0O = O0OOOOOOOOOOO0O0O  #line:2335
                OO0O00OO00OO0O00O = True  #line:2336
                O000OOOOO0OO00000 = public.M('crontab').where(
                    'sBody=?', '{} {} --db_name {} --binlog_id {}'.format(
                        O0OO0O0O0O0000O00._python_path,
                        O0OO0O0O0O0000O00._binlogModel_py,
                        O0OOOOOOOOOOO0O0O['db_name'],
                        str(O0OOOOOOOOOOO0O0O['id']))).getField(
                            'id')  #line:2341
                if O000OOOOO0OO00000:  #line:2342
                    return public.returnMsg(
                        False, '指定的数据库或者表已经存在备份，不能重复添加！')  #line:2343
        else:  #line:2344
            O0OOOOOOOOOOO0O0O = public.M('mysqlbinlog_backup_setting').where(
                'db_name=? and backup_type=?',
                (OO00O0O000O000000.datab_name,
                 O000O0O00OO000O0O)).find()  #line:2347
            if O0OOOOOOOOOOO0O0O:  #line:2348
                OO000OOOOO0O00O0O = O0OOOOOOOOOOO0O0O  #line:2349
                OO0O00OO00OO0O00O = True  #line:2350
                O000OOOOO0OO00000 = public.M('crontab').where(
                    'sBody=?', '{} {} --db_name {} --binlog_id {}'.format(
                        O0OO0O0O0O0000O00._python_path,
                        O0OO0O0O0O0000O00._binlogModel_py,
                        O0OOOOOOOOOOO0O0O['db_name'],
                        str(O0OOOOOOOOOOO0O0O['id']))).getField(
                            'id')  #line:2355
                if O000OOOOO0OO00000:  #line:2356
                    return public.returnMsg(
                        False, '指定的数据库或者表已经存在备份，不能重复添加！')  #line:2357
        OO000OOOOO0O00O0O[
            'database_table'] = OO00O0O000O000000.datab_name if OO00O0O000O000000.backup_type == 'databases' else OO00O0O000O000000.datab_name + '---' + OO00O0O000O000000.table_name  #line:2359
        OO000OOOOO0O00O0O['backup_type'] = O000O0O00OO000O0O  #line:2360
        OO000OOOOO0O00O0O[
            'backup_cycle'] = OO00O0O000O000000.backup_cycle  #line:2361
        OO000OOOOO0O00O0O[
            'cron_type'] = OO00O0O000O000000.cron_type  #line:2362
        OO000OOOOO0O00O0O['notice'] = OO00O0O000O000000.notice  #line:2363
        if OO00O0O000O000000.notice == '1':  #line:2364
            OO000OOOOO0O00O0O[
                'notice_channel'] = OO00O0O000O000000.notice_channel  #line:2365
        else:  #line:2366
            OO000OOOOO0O00O0O['notice_channel'] = ''  #line:2367
        OOO0O000OOO0OO0O0 = public.format_date()  #line:2368
        if O0OOOOOOOOOOO0O0O:
            OO000OOOOO0O00O0O['zip_password'] = O0OOOOOOOOOOO0O0O[
                'zip_password']  #line:2369
        else:
            OO000OOOOO0O00O0O[
                'zip_password'] = OO00O0O000O000000.zip_password  #line:2370
        OO000OOOOO0O00O0O['start_backup_time'] = OOO0O000OOO0OO0O0  #line:2371
        OO000OOOOO0O00O0O['end_backup_time'] = OOO0O000OOO0OO0O0  #line:2372
        OO000OOOOO0O00O0O[
            'last_excute_backup_time'] = OOO0O000OOO0OO0O0  #line:2373
        OO000OOOOO0O00O0O['table_list'] = '|'.join(
            O0OO0O0O0O0000O00.get_tables_list(
                O0OO0O0O0O0000O00.get_tables()))  #line:2374
        OO000OOOOO0O00O0O['cron_status'] = 1  #line:2375
        OO000OOOOO0O00O0O['sync_remote_status'] = 0  #line:2376
        OO000OOOOO0O00O0O['sync_remote_time'] = 0  #line:2377
        OO000OOOOO0O00O0O['add_time'] = OOO0O000OOO0OO0O0  #line:2378
        OO000OOOOO0O00O0O['db_name'] = OO00O0O000O000000.datab_name  #line:2379
        OO000OOOOO0O00O0O[
            'tb_name'] = O0OO0O0O0O0000O00._tables = '' if 'table_name' not in OO00O0O000O000000 else OO00O0O000O000000.table_name  #line:2381
        OO000OOOOO0O00O0O['save_path'] = O0OO0O0O0O0000O00.splicing_save_path(
        )  #line:2382
        OO000OOOOO0O00O0O['temp_path'] = ''  #line:2383
        OOOOO00OO0O0O00O0 = '|'  #line:2387
        OOO00O0000OOO00OO = O00OO00OO000O0OOO = O0O00O0OOOO0OO00O = O0000000OO0OO0000 = OOOOO00OO0000O000 = OOOO0OOOOO0000O00 = OO0OOO0O0OOO00OO0 = OOO0000O0OOOOO000 = O0OO0O0OOOOO0OOO0 = O00O000OO0OOOO000 = '|'  #line:2388
        OOOO0O0O00OOO0O0O = ''  #line:2389
        if 'upload_localhost' in OO00O0O000O000000:  #line:2390
            OO000OOOOO0O00O0O[
                'upload_local'] = OO00O0O000O000000.upload_localhost  #line:2391
            OOOOO00OO0O0O00O0 = 'localhost|'  #line:2392
        else:  #line:2393
            OO000OOOOO0O00O0O['upload_local'] = ''  #line:2394
        if 'upload_alioss' in OO00O0O000O000000:  #line:2395
            OO000OOOOO0O00O0O[
                'upload_alioss'] = OO00O0O000O000000.upload_alioss  #line:2396
            OOO00O0000OOO00OO = 'alioss|'  #line:2397
        else:  #line:2398
            OO000OOOOO0O00O0O['upload_alioss'] = ''  #line:2399
        if 'upload_ftp' in OO00O0O000O000000:  #line:2400
            OO000OOOOO0O00O0O[
                'upload_ftp'] = OO00O0O000O000000.upload_ftp  #line:2401
            O00OO00OO000O0OOO = 'ftp|'  #line:2402
        else:  #line:2403
            OO000OOOOO0O00O0O['upload_ftp'] = ''  #line:2404
        if 'upload_txcos' in OO00O0O000O000000:  #line:2405
            OO000OOOOO0O00O0O[
                'upload_txcos'] = OO00O0O000O000000.upload_txcos  #line:2406
            O0O00O0OOOO0OO00O = 'txcos|'  #line:2407
        else:  #line:2408
            OO000OOOOO0O00O0O['upload_txcos'] = ''  #line:2409
        if 'upload_qiniu' in OO00O0O000O000000:  #line:2410
            OO000OOOOO0O00O0O[
                'upload_qiniu'] = OO00O0O000O000000.upload_qiniu  #line:2411
            O0000000OO0OO0000 = 'qiniu|'  #line:2412
        else:  #line:2413
            OO000OOOOO0O00O0O['upload_qiniu'] = ''  #line:2414
        if 'upload_aws' in OO00O0O000O000000:  #line:2415
            OO000OOOOO0O00O0O[
                'upload_aws'] = OO00O0O000O000000.upload_aws  #line:2416
            OOOOO00OO0000O000 = 'aws|'  #line:2417
        else:  #line:2418
            OO000OOOOO0O00O0O['upload_aws'] = ''  #line:2419
        if 'upload_upyun' in OO00O0O000O000000:  #line:2420
            OO000OOOOO0O00O0O[
                'upload_upyun'] = OO00O0O000O000000.upload_upyun  #line:2421
            OOOO0OOOOO0000O00 = 'upyun|'  #line:2422
        else:  #line:2423
            OO000OOOOO0O00O0O['upload_upyun'] = ''  #line:2424
        if 'upload_obs' in OO00O0O000O000000:  #line:2425
            OO000OOOOO0O00O0O[
                'upload_obs'] = OO00O0O000O000000.upload_obs  #line:2426
            OO0OOO0O0OOO00OO0 = 'obs|'  #line:2427
        else:  #line:2428
            OO000OOOOO0O00O0O['upload_obs'] = ''  #line:2429
        if 'upload_bos' in OO00O0O000O000000:  #line:2430
            OO000OOOOO0O00O0O[
                'upload_bos'] = OO00O0O000O000000.upload_bos  #line:2431
            OOO0000O0OOOOO000 = 'bos|'  #line:2432
        else:  #line:2433
            OO000OOOOO0O00O0O['upload_bos'] = ''  #line:2434
        if 'upload_gcloud_storage' in OO00O0O000O000000:  #line:2435
            OO000OOOOO0O00O0O[
                'upload_gcloud_storage'] = OO00O0O000O000000.upload_gcloud_storage  #line:2436
            O0OO0O0OOOOO0OOO0 = 'gcloud_storage|'  #line:2437
        else:  #line:2438
            OO000OOOOO0O00O0O['upload_gcloud_storage'] = ''  #line:2439
        if 'upload_gdrive' in OO00O0O000O000000:  #line:2440
            OO000OOOOO0O00O0O[
                'upload_gdrive'] = OO00O0O000O000000.upload_gdrive  #line:2441
            O00O000OO0OOOO000 = 'gdrive|'  #line:2442
        else:  #line:2443
            OO000OOOOO0O00O0O['upload_gdrive'] = ''  #line:2444
        if 'upload_msonedrive' in OO00O0O000O000000:  #line:2445
            OO000OOOOO0O00O0O[
                'upload_msonedrive'] = OO00O0O000O000000.upload_msonedrive  #line:2446
            OOOO0O0O00OOO0O0O = 'msonedrive'  #line:2447
        else:  #line:2448
            OO000OOOOO0O00O0O['upload_msonedrive'] = ''  #line:2449
        OOOOO00OO0O0O00O0 = OOOOO00OO0O0O00O0 + OOO00O0000OOO00OO + O00OO00OO000O0OOO + O0O00O0OOOO0OO00O + O0000000OO0OO0000 + OOOOO00OO0000O000 + OOOO0OOOOO0000O00 + OO0OOO0O0OOO00OO0 + OOO0000O0OOOOO000 + O0OO0O0OOOOO0OOO0 + O00O000OO0OOOO000 + OOOO0O0O00OOO0O0O  #line:2450
        if not OO0O00OO00OO0O00O:  #line:2451
            OO000OOOOO0O00O0O['id'] = public.M(
                'mysqlbinlog_backup_setting').insert(
                    OO000OOOOO0O00O0O)  #line:2452
        else:  #line:2453
            public.M('mysqlbinlog_backup_setting').where(
                'id=?', int(OO000OOOOO0O00O0O['id'])).update(
                    OO000OOOOO0O00O0O)  #line:2455
            time.sleep(0.01)  #line:2456
        if not O000OOOOO0OO00000:  #line:2458
            O0OO0O0O0O0000O00.add_binlog_inc_backup_task(
                OO000OOOOO0O00O0O, OOOOO00OO0O0O00O0)  #line:2459
        return public.returnMsg(True, '添加成功!')  #line:2460

    def modify_mysqlbinlog_backup_setting(O00O000O00O00O0O0,
                                          OOO00O0OOOO0OOOO0):  #line:2462
        ""  #line:2468
        public.set_module_logs('binlog',
                               'modify_mysqlbinlog_backup_setting')  #line:2469
        if 'backup_id' not in OOO00O0OOOO0OOOO0:
            return public.returnMsg(False, '错误的参数!')  #line:2470
        if not OOO00O0OOOO0OOOO0.get('backup_cycle/d', 0) > 0:  #line:2471
            return public.returnMsg(False, '备份周期不正确，只能为正整数！')  #line:2472
        O00O00O0O0O0O0O00 = O00O000O00O00O0O0.get_binlog_status()  #line:2474
        if O00O00O0O0O0O0O00['status'] == False:  #line:2475
            return public.returnMsg(
                False, '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')  #line:2477
        OOO0OO0OOOO00OO0O = public.M('mysqlbinlog_backup_setting').where(
            'id=?', OOO00O0OOOO0OOOO0.backup_id).find()  #line:2480
        OOO0OO0OOOO00OO0O[
            'backup_cycle'] = OOO00O0OOOO0OOOO0.backup_cycle  #line:2481
        OOO0OO0OOOO00OO0O['notice'] = OOO00O0OOOO0OOOO0.notice  #line:2482
        O00O000O00O00O0O0._db_name = OOO0OO0OOOO00OO0O['db_name']  #line:2483
        if OOO00O0OOOO0OOOO0.notice == '1':  #line:2484
            OOO0OO0OOOO00OO0O[
                'notice_channel'] = OOO00O0OOOO0OOOO0.notice_channel  #line:2485
        else:  #line:2486
            OOO0OO0OOOO00OO0O['notice_channel'] = ''  #line:2487
        OO0O000OO000O0000 = '|'  #line:2489
        O0000O0OO000O0O0O = OO0OO000OO0OOOO00 = O00OOOO00OOO0OOO0 = OOOOO00O0O0000000 = OO0O0O0O0O00OO000 = O000OOOOO0OO00O0O = O00000OO000000O00 = OOO000OO0O00OOOO0 = OOO00O00OO0O00O0O = OOO00OOOOOOOOOOO0 = '|'  #line:2490
        O0O00OOOOO0000OOO = ''  #line:2491
        if 'upload_localhost' not in OOO00O0OOOO0OOOO0:  #line:2492
            OOO0OO0OOOO00OO0O['upload_local'] = ''  #line:2493
        else:  #line:2494
            OOO0OO0OOOO00OO0O[
                'upload_local'] = OOO00O0OOOO0OOOO0.upload_localhost  #line:2495
            OO0O000OO000O0000 = 'localhost|'  #line:2496
        if 'upload_alioss' not in OOO00O0OOOO0OOOO0:  #line:2497
            OOO0OO0OOOO00OO0O['upload_alioss'] = ''  #line:2498
        else:  #line:2499
            OOO0OO0OOOO00OO0O[
                'upload_alioss'] = OOO00O0OOOO0OOOO0.upload_alioss  #line:2500
            O0000O0OO000O0O0O = 'alioss|'  #line:2501
        if 'upload_ftp' not in OOO00O0OOOO0OOOO0:  #line:2502
            OOO0OO0OOOO00OO0O['upload_ftp'] = ''  #line:2503
        else:  #line:2504
            OOO0OO0OOOO00OO0O[
                'upload_ftp'] = OOO00O0OOOO0OOOO0.upload_ftp  #line:2505
            OO0OO000OO0OOOO00 = 'ftp|'  #line:2506
        if 'upload_txcos' not in OOO00O0OOOO0OOOO0:  #line:2507
            OOO0OO0OOOO00OO0O['upload_txcos'] = ''  #line:2508
        else:  #line:2509
            OOO0OO0OOOO00OO0O[
                'upload_txcos'] = OOO00O0OOOO0OOOO0.upload_txcos  #line:2510
            O00OOOO00OOO0OOO0 = 'txcos|'  #line:2511
        if 'upload_qiniu' not in OOO00O0OOOO0OOOO0:  #line:2512
            OOO0OO0OOOO00OO0O['upload_qiniu'] = ''  #line:2513
        else:  #line:2514
            OOO0OO0OOOO00OO0O[
                'upload_qiniu'] = OOO00O0OOOO0OOOO0.upload_qiniu  #line:2515
            OOOOO00O0O0000000 = 'qiniu|'  #line:2516
        if 'upload_aws' not in OOO00O0OOOO0OOOO0:  #line:2517
            OOO0OO0OOOO00OO0O['upload_aws'] = ''  #line:2518
        else:  #line:2519
            OOO0OO0OOOO00OO0O[
                'upload_aws'] = OOO00O0OOOO0OOOO0.upload_aws  #line:2520
            OO0O0O0O0O00OO000 = 'aws|'  #line:2521
        if 'upload_upyun' not in OOO00O0OOOO0OOOO0:  #line:2522
            OOO0OO0OOOO00OO0O['upload_upyun'] = ''  #line:2523
        else:  #line:2524
            OOO0OO0OOOO00OO0O[
                'upload_upyun'] = OOO00O0OOOO0OOOO0.upload_upyun  #line:2525
            O000OOOOO0OO00O0O = 'upyun|'  #line:2526
        if 'upload_obs' not in OOO00O0OOOO0OOOO0:  #line:2527
            OOO0OO0OOOO00OO0O['upload_obs'] = ''  #line:2528
        else:  #line:2529
            OOO0OO0OOOO00OO0O[
                'upload_obs'] = OOO00O0OOOO0OOOO0.upload_obs  #line:2530
            O00000OO000000O00 = 'obs|'  #line:2531
        if 'upload_bos' not in OOO00O0OOOO0OOOO0:  #line:2532
            OOO0OO0OOOO00OO0O['upload_bos'] = ''  #line:2533
        else:  #line:2534
            OOO0OO0OOOO00OO0O[
                'upload_bos'] = OOO00O0OOOO0OOOO0.upload_bos  #line:2535
            OOO000OO0O00OOOO0 = 'bos|'  #line:2536
        if 'upload_gcloud_storage' not in OOO00O0OOOO0OOOO0:  #line:2537
            OOO0OO0OOOO00OO0O['upload_gcloud_storage'] = ''  #line:2538
        else:  #line:2539
            OOO0OO0OOOO00OO0O[
                'upload_gcloud_storage'] = OOO00O0OOOO0OOOO0.upload_gcloud_storage  #line:2540
            OOO00O00OO0O00O0O = 'gcloud_storage|'  #line:2541
        if 'upload_gdrive' not in OOO00O0OOOO0OOOO0:  #line:2542
            OOO0OO0OOOO00OO0O['upload_gdrive'] = ''  #line:2543
        else:  #line:2544
            OOO0OO0OOOO00OO0O[
                'upload_gdrive'] = OOO00O0OOOO0OOOO0.upload_gdrive  #line:2545
            OOO00OOOOOOOOOOO0 = 'gdrive|'  #line:2546
        if 'upload_msonedrive' not in OOO00O0OOOO0OOOO0:  #line:2547
            OOO0OO0OOOO00OO0O['upload_msonedrive'] = ''  #line:2548
        else:  #line:2549
            OOO0OO0OOOO00OO0O[
                'upload_msonedrive'] = OOO00O0OOOO0OOOO0.upload_msonedrive  #line:2550
            O0O00OOOOO0000OOO = 'msonedrive'  #line:2551
        OO0O000OO000O0000 = OO0O000OO000O0000 + O0000O0OO000O0O0O + OO0OO000OO0OOOO00 + O00OOOO00OOO0OOO0 + OOOOO00O0O0000000 + OO0O0O0O0O00OO000 + O000OOOOO0OO00O0O + O00000OO000000O00 + OOO000OO0O00OOOO0 + OOO00O00OO0O00O0O + OOO00OOOOOOOOOOO0 + O0O00OOOOO0000OOO  #line:2552
        public.M('mysqlbinlog_backup_setting').where(
            'id=?', int(OOO00O0OOOO0OOOO0.backup_id)).update(
                OOO0OO0OOOO00OO0O)  #line:2554
        if 'cron_id' in OOO00O0OOOO0OOOO0:  #line:2556
            if OOO00O0OOOO0OOOO0.cron_id:  #line:2557
                OO0O0OOO000000OO0 = {
                    "id":
                    OOO00O0OOOO0OOOO0.cron_id,
                    "name":
                    public.M('crontab').where(
                        "id=?",
                        (OOO00O0OOOO0OOOO0.cron_id, )).getField('name'),
                    "type":
                    OOO0OO0OOOO00OO0O['cron_type'],
                    "where1":
                    OOO0OO0OOOO00OO0O['backup_cycle'],
                    "hour":
                    '',
                    "minute":
                    '0',
                    "sType":
                    'enterpriseBackup',
                    "sName":
                    OOO0OO0OOOO00OO0O['backup_type'],
                    "backupTo":
                    OO0O000OO000O0000,
                    "save":
                    OOO0OO0OOOO00OO0O['notice'],
                    "save_local":
                    '1',
                    "notice":
                    OOO0OO0OOOO00OO0O['notice'],
                    "notice_channel":
                    OOO0OO0OOOO00OO0O['notice_channel'],
                    "sBody":
                    public.M('crontab').where(
                        "id=?",
                        (OOO00O0OOOO0OOOO0.cron_id, )).getField('sBody'),
                    "urladdress":
                    '{}|{}|{}'.format(OOO0OO0OOOO00OO0O['db_name'],
                                      OOO0OO0OOOO00OO0O['tb_name'],
                                      OOO0OO0OOOO00OO0O['id'])
                }  #line:2592
                import crontab  #line:2593
                crontab.crontab().modify_crond(OO0O0OOO000000OO0)  #line:2594
                return public.returnMsg(True, '编辑成功!')  #line:2595
            else:  #line:2596
                O00O000O00O00O0O0.add_binlog_inc_backup_task(
                    OOO0OO0OOOO00OO0O, OO0O000OO000O0000)  #line:2597
                return public.returnMsg(True, '已恢复计划任务!')  #line:2598
        else:  #line:2599
            O00O000O00O00O0O0.add_binlog_inc_backup_task(
                OOO0OO0OOOO00OO0O, OO0O000OO000O0000)  #line:2600
            return public.returnMsg(True, '已恢复计划任务!')  #line:2601

    def delete_mysql_binlog_setting(OO00O000O0O000OO0,
                                    O00OOOOOO0O000OO0):  #line:2603
        ""  #line:2608
        public.set_module_logs('binlog',
                               'delete_mysql_binlog_setting')  #line:2609
        if 'backup_id' not in O00OOOOOO0O000OO0 and 'cron_id' not in O00OOOOOO0O000OO0:  #line:2610
            return public.returnMsg(False, '不存在此增量备份任务!')  #line:2611
        O0O0O0O0O000OOO00 = ''  #line:2612
        if O00OOOOOO0O000OO0.backup_id:  #line:2613
            O0O0O0O0O000OOO00 = public.M('mysqlbinlog_backup_setting').where(
                'id=?', (O00OOOOOO0O000OO0.backup_id, )).find()  #line:2615
            if O0O0O0O0O000OOO00:  #line:2616
                OO00O000O0O000OO0._save_default_path = O0O0O0O0O000OOO00[
                    'save_path']  #line:2617
                OO00O000O0O000OO0._db_name = O0O0O0O0O000OOO00[
                    'db_name']  #line:2618
        if 'cron_id' in O00OOOOOO0O000OO0 and O00OOOOOO0O000OO0.cron_id:  #line:2620
            if public.M('crontab').where(
                    'id=?', (O00OOOOOO0O000OO0.cron_id, )).count():  #line:2621
                O00OOO0OO00O00OOO = {
                    "id": O00OOOOOO0O000OO0.cron_id
                }  #line:2622
                import crontab  #line:2623
                crontab.crontab().DelCrontab(O00OOO0OO00O00OOO)  #line:2624
        if O00OOOOOO0O000OO0.type == 'manager' and O0O0O0O0O000OOO00:  #line:2626
            if public.M('mysqlbinlog_backup_setting').where(
                    'id=?',
                (O00OOOOOO0O000OO0.backup_id, )).count():  #line:2628
                public.M('mysqlbinlog_backup_setting').where(
                    'id=?',
                    (O00OOOOOO0O000OO0.backup_id, )).delete()  #line:2630
            O000O0O0OO0OO0OOO = O0O0O0O0O000OOO00[
                'save_path'] + 'full_record.json'  #line:2631
            OO000O00O0000000O = O0O0O0O0O000OOO00[
                'save_path'] + 'inc_record.json'  #line:2632
            if os.path.isfile(O000O0O0OO0OO0OOO):  #line:2633
                OO00O000O0O000OO0.clean_local_full_backups(
                    O000O0O0OO0OO0OOO)  #line:2634
            if os.path.isfile(OO000O00O0000000O):  #line:2635
                OO00O000O0O000OO0.clean_local_inc_backups(
                    OO000O00O0000000O)  #line:2636
            O00OO0O0000O000OO = public.M('mysqlbinlog_backups').where(
                'sid=?', O00OOOOOO0O000OO0.backup_id).select()  #line:2638
            for O0O000O0O0000OO00 in O00OO0O0000O000OO:  #line:2639
                if not O0O000O0O0000OO00: continue  #line:2640
                if 'id' not in O0O000O0O0000OO00: continue  #line:2641
                public.M('mysqlbinlog_backups').delete(
                    O0O000O0O0000OO00['id'])  #line:2642
        return public.returnMsg(True, '删除成功')  #line:2643

    def get_inc_size(O00OOO0OOOOO0O00O, OO0OOOOOOOO0000OO):  #line:2645
        ""  #line:2651
        O0OO00000O0O00O0O = 0  #line:2652
        if os.path.isfile(OO0OOOOOOOO0000OO):  #line:2653
            try:  #line:2654
                O00O0O000O0O0O000 = json.loads(
                    public.readFile(OO0OOOOOOOO0000OO))  #line:2655
                for OOOO000OOO00OO000 in O00O0O000O0O0O000:  #line:2656
                    O0OO00000O0O00O0O += int(
                        OOOO000OOO00OO000['size'])  #line:2657
            except:  #line:2658
                O0OO00000O0O00O0O = 0  #line:2659
        return O0OO00000O0O00O0O  #line:2660

    def get_time_size(OOOOO0O0OO0O0O0OO, OOO0O0O000OO00000,
                      OOOO0O000O0O0OOOO):  #line:2662
        ""  #line:2667
        O0OO0O0O0OO00O0OO = json.loads(
            public.readFile(OOO0O0O000OO00000))[0]  #line:2669
        OOOO0O000O0O0OOOO['start_time'] = O0OO0O0O0OO00O0OO['time']  #line:2670
        if 'end_time' in O0OO0O0O0OO00O0OO:  #line:2671
            OOOO0O000O0O0OOOO['end_time'] = O0OO0O0O0OO00O0OO[
                'end_time']  #line:2672
            OOOO0O000O0O0OOOO['excute_time'] = O0OO0O0O0OO00O0OO[
                'end_time']  #line:2673
        else:  #line:2674
            OOOO0O000O0O0OOOO['end_time'] = O0OO0O0O0OO00O0OO[
                'time']  #line:2675
            OOOO0O000O0O0OOOO['excute_time'] = O0OO0O0O0OO00O0OO[
                'time']  #line:2676
        OOOO0O000O0O0OOOO['full_size'] = O0OO0O0O0OO00O0OO['size']  #line:2677
        return OOOO0O000O0O0OOOO  #line:2678

    def get_database_info(O0OOOO00OOO0O0000, get=None):  #line:2680
        ""  #line:2685
        OO00000OO00O0O0O0 = O0OOOO00OOO0O0000.get_databases()  #line:2686
        O0O00O0O00O0OO0O0 = {}  #line:2687
        O00O0OOOO0OOO0O00 = []  #line:2688
        OOOO0OOO0O0OO00O0 = []  #line:2689
        if OO00000OO00O0O0O0:  #line:2690
            for OOO00OO0O0OOO0O00 in OO00000OO00O0O0O0:  #line:2691
                if not OOO00OO0O0OOO0O00: continue  #line:2692
                O0OOOO00OOO00O0OO = {}  #line:2693
                O0OOOO00OOO0O0000._db_name = O0OOOO00OOO00O0OO[
                    'name'] = OOO00OO0O0OOO0O00['name']  #line:2694
                OO0O00OO00O0OO00O = O0OOOO00OOO0O0000._save_default_path + OOO00OO0O0OOO0O00[
                    'name'] + '/databases/'  #line:2696
                OOO000O0OO00000O0 = O0OOOO00OOO0O0000._save_default_path + OOO00OO0O0OOO0O00[
                    'name'] + '/tables/'  #line:2697
                O0OO0O0000OOO0000 = OO0O00OO00O0OO00O + 'full_record.json'  #line:2698
                OO0O00O00O0O00000 = OO0O00OO00O0OO00O + 'inc_record.json'  #line:2699
                O0OOOO00OOO00O0OO['inc_size'] = 0 if not os.path.isfile(
                    OO0O00O00O0O00000) else O0OOOO00OOO0O0000.get_inc_size(
                        OO0O00O00O0O00000)  #line:2701
                O00OOO00000O0O00O = public.M(
                    'mysqlbinlog_backup_setting').where(
                        'db_name=? and backup_type=?',
                        (str(OOO00OO0O0OOO0O00['name']),
                         'databases')).find()  #line:2705
                if O00OOO00000O0O00O:  #line:2706
                    O0OOOO00OOO00O0OO['cron_id'] = public.M('crontab').where(
                        'name=?', '[勿删]数据库增量备份[{}]'.format(
                            O00OOO00000O0O00O['db_name'])).getField(
                                'id')  #line:2709
                    O0OOOO00OOO00O0OO['backup_id'] = O00OOO00000O0O00O[
                        'id']  #line:2710
                    O0OOOO00OOO00O0OO['upload_localhost'] = O00OOO00000O0O00O[
                        'upload_local']  #line:2711
                    O0OOOO00OOO00O0OO['upload_alioss'] = O00OOO00000O0O00O[
                        'upload_alioss']  #line:2712
                    O0OOOO00OOO00O0OO['upload_ftp'] = O00OOO00000O0O00O[
                        'upload_ftp']  #line:2713
                    O0OOOO00OOO00O0OO['upload_txcos'] = O00OOO00000O0O00O[
                        'upload_txcos']  #line:2714
                    O0OOOO00OOO00O0OO['upload_qiniu'] = O00OOO00000O0O00O[
                        'upload_qiniu']  #line:2715
                    O0OOOO00OOO00O0OO['upload_obs'] = O00OOO00000O0O00O[
                        'upload_obs']  #line:2716
                    O0OOOO00OOO00O0OO['upload_bos'] = O00OOO00000O0O00O[
                        'upload_bos']  #line:2717
                    O0OOOO00OOO00O0OO['backup_cycle'] = O00OOO00000O0O00O[
                        'backup_cycle']  #line:2718
                    O0OOOO00OOO00O0OO['notice'] = O00OOO00000O0O00O[
                        'notice']  #line:2719
                    O0OOOO00OOO00O0OO['notice_channel'] = O00OOO00000O0O00O[
                        'notice_channel']  #line:2720
                    O0OOOO00OOO00O0OO['zip_password'] = O00OOO00000O0O00O[
                        'zip_password']  #line:2721
                    O0OOOO00OOO00O0OO['start_time'] = O00OOO00000O0O00O[
                        'start_backup_time']  #line:2723
                    O0OOOO00OOO00O0OO['end_time'] = O00OOO00000O0O00O[
                        'end_backup_time']  #line:2724
                    O0OOOO00OOO00O0OO['excute_time'] = O00OOO00000O0O00O[
                        'last_excute_backup_time']  #line:2726
                else:  #line:2727
                    O0OOOO00OOO00O0OO['cron_id'] = O0OOOO00OOO00O0OO[
                        'backup_id'] = O0OOOO00OOO00O0OO[
                            'notice'] = O0OOOO00OOO00O0OO[
                                'upload_alioss'] = O0OOOO00OOO00O0OO[
                                    'backup_cycle'] = O0OOOO00OOO00O0OO[
                                        'zip_password'] = None  #line:2732
                    O0OOOO00OOO00O0OO['upload_localhost'] = O0OOOO00OOO00O0OO[
                        'upload_alioss'] = O0OOOO00OOO00O0OO[
                            'upload_ftp'] = O0OOOO00OOO00O0OO[
                                'upload_txcos'] = O0OOOO00OOO00O0OO[
                                    'upload_qiniu'] = O0OOOO00OOO00O0OO[
                                        'upload_obs'] = O0OOOO00OOO00O0OO[
                                            'upload_bos'] = ''  #line:2739
                if os.path.isfile(O0OO0O0000OOO0000):  #line:2741
                    O0OOOO00OOO00O0OO = O0OOOO00OOO0O0000.get_time_size(
                        O0OO0O0000OOO0000, O0OOOO00OOO00O0OO)  #line:2743
                    if O00OOO00000O0O00O:  #line:2744
                        O0OOOO00OOO00O0OO['excute_time'] = O00OOO00000O0O00O[
                            'last_excute_backup_time']  #line:2746
                    O0OOOO00OOO00O0OO['full_size'] = public.to_size(
                        O0OOOO00OOO00O0OO['full_size'] +
                        O0OOOO00OOO00O0OO['inc_size'])  #line:2748
                    O00O0OOOO0OOO0O00.append(O0OOOO00OOO00O0OO)  #line:2749
                else:  #line:2751
                    if O00OOO00000O0O00O:  #line:2752
                        O0OOOO00OOO00O0OO['full_size'] = 0  #line:2753
                        O000000000O00O000 = public.M(
                            'mysqlbinlog_backups').where(
                                'sid=?',
                                O00OOO00000O0O00O['id']).select()  #line:2756
                        for OOOO00OOOO0OO0O00 in O000000000O00O000:  #line:2757
                            if not OOOO00OOOO0OO0O00: continue  #line:2758
                            if 'size' not in OOOO00OOOO0OO0O00:
                                continue  #line:2759
                            O0OOOO00OOO00O0OO[
                                'full_size'] += OOOO00OOOO0OO0O00[
                                    'size']  #line:2760
                        O0OOOO00OOO00O0OO['full_size'] = public.to_size(
                            O0OOOO00OOO00O0OO['full_size'])  #line:2762
                        O00O0OOOO0OOO0O00.append(O0OOOO00OOO00O0OO)  #line:2763
                O00OOO00000O0O00O = public.M(
                    'mysqlbinlog_backup_setting').where(
                        'db_name=? and backup_type=?',
                        (str(OOO00OO0O0OOO0O00['name']),
                         'tables')).select()  #line:2767
                OOOOOOOO0000OOOOO = {}  #line:2768
                OOOOOOOO0000OOOOO['name'] = OOO00OO0O0OOO0O00[
                    'name']  #line:2769
                OOOOOOO00OO0OOO0O = []  #line:2770
                OOO00O0000OO0OOOO = O0OOOO00OOO0O0000.get_tables_list(
                    O0OOOO00OOO0O0000.get_tables())  #line:2771
                for O0O0000O000O0O0O0 in OOO00O0000OO0OOOO:  #line:2772
                    if not OOO00O0000OO0OOOO: continue  #line:2773
                    O000O00000OOO0000 = public.M(
                        'mysqlbinlog_backup_setting').where(
                            'db_name=? and tb_name=? ',
                            (O0OOOO00OOO0O0000._db_name,
                             O0O0000O000O0O0O0)).find()  #line:2775
                    OOO000O00O0O00OOO = OOO000O0OO00000O0 + O0O0000O000O0O0O0 + '/full_record.json'  #line:2776
                    OOO0O00OO00O0OOO0 = OOO000O0OO00000O0 + O0O0000O000O0O0O0 + '/inc_record.json'  #line:2777
                    O0OOOO00OOO00O0OO = {}  #line:2778
                    O0OOOO00OOO00O0OO['name'] = O0O0000O000O0O0O0  #line:2779
                    O0OOOO00OOO00O0OO[
                        'inc_size'] = O0OOOO00OOO0O0000.get_inc_size(
                            OOO0O00OO00O0OOO0)  #line:2781
                    if O000O00000OOO0000:  #line:2783
                        O0OOOO00OOO00O0OO['cron_id'] = public.M(
                            'crontab').where(
                                'sBody=?',
                                '{} {} --db_name {} --binlog_id {}'.format(
                                    O0OOOO00OOO0O0000._python_path,
                                    O0OOOO00OOO0O0000._binlogModel_py,
                                    O000O00000OOO0000['db_name'],
                                    str(O000O00000OOO0000['id']))).getField(
                                        'id')  #line:2789
                        O0OOOO00OOO00O0OO['backup_id'] = O000O00000OOO0000[
                            'id']  #line:2790
                        O0OOOO00OOO00O0OO[
                            'upload_localhost'] = O000O00000OOO0000[
                                'upload_local']  #line:2792
                        O0OOOO00OOO00O0OO['upload_alioss'] = O000O00000OOO0000[
                            'upload_alioss']  #line:2794
                        O0OOOO00OOO00O0OO['backup_cycle'] = O000O00000OOO0000[
                            'backup_cycle']  #line:2795
                        O0OOOO00OOO00O0OO['notice'] = O000O00000OOO0000[
                            'notice']  #line:2796
                        O0OOOO00OOO00O0OO[
                            'notice_channel'] = O000O00000OOO0000[
                                'notice_channel']  #line:2798
                        O0OOOO00OOO00O0OO['excute_time'] = O000O00000OOO0000[
                            'last_excute_backup_time']  #line:2800
                        O0OOOO00OOO00O0OO['zip_password'] = O000O00000OOO0000[
                            'zip_password']  #line:2801
                        O0OOOO00OOO00O0OO['upload_ftp'] = O000O00000OOO0000[
                            'upload_ftp']  #line:2802
                        O0OOOO00OOO00O0OO['upload_txcos'] = O000O00000OOO0000[
                            'upload_txcos']  #line:2803
                        O0OOOO00OOO00O0OO['upload_qiniu'] = O000O00000OOO0000[
                            'upload_qiniu']  #line:2804
                        O0OOOO00OOO00O0OO['upload_obs'] = O000O00000OOO0000[
                            'upload_obs']  #line:2805
                        O0OOOO00OOO00O0OO['upload_bos'] = O000O00000OOO0000[
                            'upload_bos']  #line:2806
                    else:  #line:2808
                        O0OOOO00OOO00O0OO['cron_id'] = O0OOOO00OOO00O0OO[
                            'backup_id'] = O0OOOO00OOO00O0OO[
                                'notice'] = O0OOOO00OOO00O0OO[
                                    'upload_alioss'] = O0OOOO00OOO00O0OO[
                                        'backup_cycle'] = O0OOOO00OOO00O0OO[
                                            'zip_password'] = None  #line:2814
                        O0OOOO00OOO00O0OO['upload_localhost'] = O0OOOO00OOO00O0OO[
                            'upload_alioss'] = O0OOOO00OOO00O0OO[
                                'upload_ftp'] = O0OOOO00OOO00O0OO[
                                    'upload_txcos'] = O0OOOO00OOO00O0OO[
                                        'upload_qiniu'] = O0OOOO00OOO00O0OO[
                                            'upload_obs'] = O0OOOO00OOO00O0OO[
                                                'upload_bos'] = ''  #line:2821
                    if os.path.isfile(OOO000O00O0O00OOO):  #line:2823
                        O0OOOO00OOO00O0OO = O0OOOO00OOO0O0000.get_time_size(
                            OOO000O00O0O00OOO, O0OOOO00OOO00O0OO)  #line:2825
                        if O000O00000OOO0000:  #line:2826
                            O0OOOO00OOO00O0OO[
                                'excute_time'] = O000O00000OOO0000[
                                    'last_excute_backup_time']  #line:2828
                        O0OOOO00OOO00O0OO['full_size'] = public.to_size(
                            O0OOOO00OOO00O0OO['full_size'] +
                            O0OOOO00OOO00O0OO['inc_size'])  #line:2831
                        OOOOOOO00OO0OOO0O.append(O0OOOO00OOO00O0OO)  #line:2832
                    else:  #line:2834
                        if not O000O00000OOO0000: continue  #line:2835
                        O0OOOO00OOO00O0OO['start_time'] = O000O00000OOO0000[
                            'start_backup_time']  #line:2837
                        O0OOOO00OOO00O0OO['end_time'] = O000O00000OOO0000[
                            'end_backup_time']  #line:2838
                        O0OOOO00OOO00O0OO['excute_time'] = O000O00000OOO0000[
                            'last_excute_backup_time']  #line:2840
                        O0OOOO00OOO00O0OO['full_size'] = 0  #line:2844
                        O000000000O00O000 = public.M(
                            'mysqlbinlog_backups').where(
                                'sid=?',
                                O000O00000OOO0000['id']).select()  #line:2847
                        for OO00OOOO0000O0O0O in O000000000O00O000:  #line:2848
                            if not OO00OOOO0000O0O0O: continue  #line:2849
                            if 'size' not in OO00OOOO0000O0O0O:
                                continue  #line:2850
                            O0OOOO00OOO00O0OO[
                                'full_size'] += OO00OOOO0000O0O0O[
                                    'size']  #line:2851
                        O0OOOO00OOO00O0OO['full_size'] = public.to_size(
                            O0OOOO00OOO00O0OO['full_size'])  #line:2853
                        OOOOOOO00OO0OOO0O.append(O0OOOO00OOO00O0OO)  #line:2854
                if OOOOOOO00OO0OOO0O:  #line:2855
                    OOOOOOOO0000OOOOO['data'] = OOOOOOO00OO0OOO0O  #line:2856
                    OOOO0OOO0O0OO00O0.append(OOOOOOOO0000OOOOO)  #line:2857
        O0O00O0O00O0OO0O0['databases'] = O00O0OOOO0OOO0O00  #line:2858
        O0O00O0O00O0OO0O0['tables'] = OOOO0OOO0O0OO00O0  #line:2859
        return public.returnMsg(True, O0O00O0O00O0OO0O0)  #line:2860

    def get_databases_info(O0000O00O0000000O, OO0O0O0OOO0OOO0OO):  #line:2862
        ""  #line:2866
        O00000OOO0O0O0OO0 = O0000O00O0000000O.get_database_info()  #line:2867
        OOOOOOOO0OO00OOOO = []  #line:2868
        for OO000O000O0OO0O00 in O00000OOO0O0O0OO0['msg'][
                'databases']:  #line:2869
            OO000O000O0OO0O00['type'] = 'databases'  #line:2870
            OOOOOOOO0OO00OOOO.append(OO000O000O0OO0O00)  #line:2871
        return O0000O00O0000000O.get_page(OOOOOOOO0OO00OOOO,
                                          OO0O0O0OOO0OOO0OO)  #line:2872

    def get_specified_database_info(OO00OOO00O000OO0O,
                                    O0O000000000O0O00):  #line:2874
        ""  #line:2878
        O0O000OO000OOO0O0 = OO00OOO00O000OO0O.get_database_info()  #line:2879
        OO0O0O0OOO00O0O0O = []  #line:2880
        OOOOOO000OOO00OOO = ['databases', 'all']  #line:2881
        O0OOO0O0OOO00O000 = ['tables', 'all']  #line:2882
        for O0OOO0OO0OOOO00O0 in O0O000OO000OOO0O0['msg'][
                'databases']:  #line:2883
            if O0OOO0OO0OOOO00O0[
                    'name'] == O0O000000000O0O00.datab_name:  #line:2884
                O0OOO0OO0OOOO00O0['type'] = 'databases'  #line:2885
                if hasattr(
                        O0O000000000O0O00, 'type'
                ) and O0O000000000O0O00.type not in OOOOOO000OOO00OOO:
                    continue  #line:2886
                OO0O0O0OOO00O0O0O.append(O0OOO0OO0OOOO00O0)  #line:2887
        for O0OOO0OO0OOOO00O0 in O0O000OO000OOO0O0['msg'][
                'tables']:  #line:2888
            if O0OOO0OO0OOOO00O0[
                    'name'] == O0O000000000O0O00.datab_name:  #line:2889
                for O0O0OOO00O00O0OO0 in O0OOO0OO0OOOO00O0['data']:  #line:2890
                    O0O0OOO00O00O0OO0['type'] = 'tables'  #line:2891
                    if hasattr(
                            O0O000000000O0O00, 'type'
                    ) and O0O000000000O0O00.type not in O0OOO0O0OOO00O000:  #line:2892
                        continue  #line:2893
                    OO0O0O0OOO00O0O0O.append(O0O0OOO00O00O0OO0)  #line:2894
        return OO00OOO00O000OO0O.get_page(OO0O0O0OOO00O0O0O,
                                          O0O000000000O0O00)  #line:2895

    def get_page(OO0000O0O0OO00OOO, OOO00O0OO000OO000,
                 O0OOOO0OOOOO0O0OO):  #line:2897
        ""  #line:2901
        import page  #line:2903
        page = page.Page()  #line:2905
        O000OO0O0O00OO000 = {}  #line:2907
        O000OO0O0O00OO000['count'] = len(OOO00O0OO000OO000)  #line:2908
        O000OO0O0O00OO000['row'] = 10  #line:2909
        O000OO0O0O00OO000['p'] = 1  #line:2910
        if hasattr(O0OOOO0OOOOO0O0OO, 'p'):  #line:2911
            O000OO0O0O00OO000['p'] = int(O0OOOO0OOOOO0O0OO['p'])  #line:2912
        O000OO0O0O00OO000['uri'] = {}  #line:2913
        O000OO0O0O00OO000['return_js'] = ''  #line:2914
        OOO0OO0O00000O0OO = {}  #line:2916
        OOO0OO0O00000O0OO['page'] = page.GetPage(
            O000OO0O0O00OO000, limit='1,2,3,4,5,8')  #line:2917
        OOOO0OOOOOO0000OO = 0  #line:2918
        OOO0OO0O00000O0OO['data'] = []  #line:2919
        for OO00OOOOO0O0OO0O0 in range(O000OO0O0O00OO000['count']):  #line:2920
            if OOOO0OOOOOO0000OO >= page.ROW: break  #line:2921
            if OO00OOOOO0O0OO0O0 < page.SHIFT: continue  #line:2922
            OOOO0OOOOOO0000OO += 1  #line:2923
            OOO0OO0O00000O0OO['data'].append(
                OOO00O0OO000OO000[OO00OOOOO0O0OO0O0])  #line:2924
        return OOO0OO0O00000O0OO  #line:2925

    def delete_file(OO00OOOO0000000OO, OO0OO00OO0OO0OO00):  #line:2927
        ""  #line:2932
        if os.path.exists(OO0OO00OO0OO0OO00):  #line:2933
            os.remove(OO0OO00OO0OO0OO00)  #line:2934

    def send_failture_notification(OOOOOO00OOOO00OO0,
                                   OO0O00000O00OO00O,
                                   target="",
                                   remark=""):  #line:2936
        ""  #line:2941
        OO00OO00OOOOO0O0O = '数据库增量备份[ {} ]'.format(target)  #line:2942
        O0OOOOO0O0OOO000O = OOOOOO00OOOO00OO0._pdata['notice']  #line:2943
        OO00O0OOOOO00OOOO = OOOOOO00OOOO00OO0._pdata[
            'notice_channel']  #line:2944
        if O0OOOOO0O0OOO000O in [0, '0'] or not OO00O0OOOOO00OOOO:  #line:2945
            return  #line:2946
        if O0OOOOO0O0OOO000O in [1, '1', 2, '2']:  #line:2947
            OOO000O0O0OO00O0O = "宝塔计划任务备份失败提醒"  #line:2948
            OO00O0OO00O0000O0 = OO00OO00OOOOO0O0O  #line:2949
            O0O0O0OOOO000O00O = OOOOOO00OOOO00OO0._mybackup.generate_failture_notice(
                OO00O0OO00O0000O0, OO0O00000O00OO00O, remark)  #line:2951
            O00OOO00O00O0O0O0 = OOOOOO00OOOO00OO0._mybackup.send_notification(
                OO00O0OOOOO00OOOO, OOO000O0O0OO00O0O,
                O0O0O0OOOO000O00O)  #line:2952
            if O00OOO00O00O0O0O0:  #line:2953
                print('|-消息通知已发送。')  #line:2954

    def sync_date(O0OO00O0OOOOO0O00):  #line:2956
        ""  #line:2959
        import config  #line:2960
        config.config().syncDate(None)  #line:2961

    def get_config(OO0OOOO000OOO0O00, OOOOOO00OO000000O):  #line:2965
        ""  #line:2968
        O00O00OO00OO000O0 = OOOOOO00OO000000O + 'As.conf'  #line:2969
        O0OO00OOO0O0O0000 = os.path.join(public.get_datadir(),
                                         O00O00OO00OO000O0)  #line:2970
        O0O00OO00OOO00OOO = os.path.join(public.get_panel_path(),
                                         'data/a_pass.pl')  #line:2971
        OOO00OO0000O0OO00 = OOOOOO00OO000000O + '/config.conf'  #line:2972
        OOO0O00OO000O0O0O = os.path.join(public.get_plugin_path(),
                                         OOO00OO0000O0OO00)  #line:2973
        O000OO00OOO0O0O00 = os.path.join(public.get_plugin_path(),
                                         OOOOOO00OO000000O)  #line:2974
        O00OO0OOOOO000000 = os.path.join(O000OO00OOO0O0O00,
                                         'aes_status')  #line:2975
        O000OOOO0O0OOOO00 = False  #line:2976
        if os.path.isfile(O00OO0OOOOO000000):  #line:2977
            O000OOOO0O0OOOO00 = True  #line:2978
        OOOO0OOOO000O0O0O = ''  #line:2979
        if os.path.isfile(OOO0O00OO000O0O0O):  #line:2980
            OOOO0OOOO000O0O0O = OOO0O00OO000O0O0O  #line:2981
        elif os.path.isfile(O0OO00OOO0O0O0000):  #line:2982
            OOOO0OOOO000O0O0O = O0OO00OOO0O0O0000  #line:2983
        if not OOOO0OOOO000O0O0O:  #line:2984
            return ['', '', '', '', '/']  #line:2986
        O00OO00000O0000OO = public.readFile(OOOO0OOOO000O0O0O)  #line:2987
        if O000OOOO0O0OOOO00:  #line:2988
            try:  #line:2989
                O0OOOOOO000O0O0O0 = public.readFile(
                    O0O00OO00OOO00OOO)  #line:2990
                O00OO00000O0000OO = public.aes_decrypt(
                    O00OO00000O0000OO, O0OOOOOO000O0O0O0)  #line:2991
            except:  #line:2992
                O00OO00000O0000OO = {}  #line:2993
        else:  #line:2994
            O00OO00000O0000OO = json.loads(O00OO00000O0000OO)  #line:2995
        OOOO0OO0OOO000OOO = OO0OOOO000OOO0O00._config_path + '/' + O00O00OO00OO000O0  #line:2996
        if not os.path.isfile(
                OOOO0OO0OOO000OOO) and not O00OO00000O0000OO:  #line:2997
            return ['', '', '', '', '/']  #line:2998
        if not O00OO00000O0000OO and os.path.isfile(
                OOOO0OO0OOO000OOO):  #line:2999
            O00OO00000O0000OO = public.readFile(OOOO0OO0OOO000OOO)  #line:3000
        if not O00OO00000O0000OO: return ['', '', '', '', '/']  #line:3001
        OO000O0O0OOOOO00O = O00OO00000O0000OO.split('|')  #line:3002
        if len(OO000O0O0OOOOO00O) < 5:
            OO000O0O0OOOOO00O.append('/')  #line:3003
        return OO000O0O0OOOOO00O  #line:3004


class alioss_main:  #line:3008
    __OOOOOO00O000000O0 = None  #line:3009
    __O00000OOOOO00OOOO = 0  #line:3010

    def __OO0OO0O0O000OO0OO(OO000O000O0000000):  #line:3012
        ""  #line:3016
        if OO000O000O0000000.__OOOOOO00O000000O0: return  #line:3017
        OO00OO0OO0O0OO000 = OO000O000O0000000.get_config()  #line:3019
        OO000O000O0000000.__O0O0OO000OO0O0OO0 = OO00OO0OO0O0OO000[
            2]  #line:3021
        if OO00OO0OO0O0OO000[3].find(OO00OO0OO0O0OO000[2]) != -1:  #line:3022
            OO00OO0OO0O0OO000[3] = OO00OO0OO0O0OO000[3].replace(
                OO00OO0OO0O0OO000[2] + '.', '')  #line:3023
        OO000O000O0000000.__OOOOO0O0000OOO00O = OO00OO0OO0O0OO000[
            3]  #line:3024
        OO000O000O0000000.__O0O0O0O0000O00000 = main().get_path(
            OO00OO0OO0O0OO000[4] + '/bt_backup/')  #line:3025
        if OO000O000O0000000.__O0O0O0O0000O00000[:1] == '/':  #line:3026
            OO000O000O0000000.__O0O0O0O0000O00000 = OO000O000O0000000.__O0O0O0O0000O00000[
                1:]  #line:3027
        try:  #line:3029
            import oss2  #line:3031
            OO000O000O0000000.__OOOOOO00O000000O0 = oss2.Auth(
                OO00OO0OO0O0OO000[0], OO00OO0OO0O0OO000[1])  #line:3032
        except Exception as O0O0O0O00OO00OOOO:  #line:3033
            pass  #line:3034

    def get_config(OOO0OOO0O00O0OOOO):  #line:3037
        ""  #line:3042
        return main().get_config('alioss')  #line:3043

    def check_config(OO0O000O0OO000000):  #line:3045
        ""  #line:3050
        try:  #line:3051
            OO0O000O0OO000000.__OO0OO0O0O000OO0OO()  #line:3052
            import oss2  #line:3053
            from itertools import islice  #line:3054
            O0O00O00OOO0O00OO = oss2.Bucket(
                OO0O000O0OO000000.__OOOOOO00O000000O0,
                OO0O000O0OO000000.__OOOOO0O0000OOO00O,
                OO0O000O0OO000000.__O0O0OO000OO0O0OO0)  #line:3056
            OO00O00O00OOO00O0 = oss2.ObjectIterator(
                O0O00O00OOO0O00OO)  #line:3057
            O0O0000O0OO0000O0 = []  #line:3058
            OOOOOO0O00000O0O0 = '/'  #line:3059
            '''key, last_modified, etag, type, size, storage_class'''  #line:3060
            for OOOO0O0O0000O0O00 in islice(
                    oss2.ObjectIterator(O0O00O00OOO0O00OO,
                                        delimiter='/',
                                        prefix='/'), 1000):  #line:3063
                OOOO0O0O0000O0O00.key = OOOO0O0O0000O0O00.key.replace(
                    '/', '')  #line:3064
                if not OOOO0O0O0000O0O00.key: continue  #line:3065
                OO0O00O00O0000O0O = {}  #line:3066
                OO0O00O00O0000O0O['name'] = OOOO0O0O0000O0O00.key  #line:3067
                OO0O00O00O0000O0O['size'] = OOOO0O0O0000O0O00.size  #line:3068
                OO0O00O00O0000O0O['type'] = OOOO0O0O0000O0O00.type  #line:3069
                OO0O00O00O0000O0O[
                    'download'] = OO0O000O0OO000000.download_file(
                        OOOOOO0O00000O0O0 + OOOO0O0O0000O0O00.key,
                        False)  #line:3070
                OO0O00O00O0000O0O[
                    'time'] = OOOO0O0O0000O0O00.last_modified  #line:3071
                O0O0000O0OO0000O0.append(OO0O00O00O0000O0O)  #line:3072
            return True  #line:3073
        except:  #line:3074
            return False  #line:3075

    def get_list(OOOO00O00000O00O0, get=None):  #line:3077
        ""  #line:3082
        OOOO00O00000O00O0.__OO0OO0O0O000OO0OO()  #line:3084
        if not OOOO00O00000O00O0.__OOOOOO00O000000O0:  #line:3085
            return False  #line:3086
        try:  #line:3088
            from itertools import islice  #line:3089
            import oss2  #line:3090
            O0O00O00O0OO00O0O = oss2.Bucket(
                OOOO00O00000O00O0.__OOOOOO00O000000O0,
                OOOO00O00000O00O0.__OOOOO0O0000OOO00O,
                OOOO00O00000O00O0.__O0O0OO000OO0O0OO0)  #line:3092
            O0OOO0000OOO0OO0O = oss2.ObjectIterator(
                O0O00O00O0OO00O0O)  #line:3093
            O000OO0O0O000O0O0 = []  #line:3094
            OOOOOOO000OO00OO0 = main().get_path(get.path)  #line:3095
            '''key, last_modified, etag, type, size, storage_class'''  #line:3096
            for O0O0000O000O0O000 in islice(
                    oss2.ObjectIterator(O0O00O00O0OO00O0O,
                                        delimiter='/',
                                        prefix=OOOOOOO000OO00OO0),
                    1000):  #line:3099
                O0O0000O000O0O000.key = O0O0000O000O0O000.key.replace(
                    OOOOOOO000OO00OO0, '')  #line:3100
                if not O0O0000O000O0O000.key: continue  #line:3101
                OO00OO0OOOO0O0O00 = {}  #line:3102
                OO00OO0OOOO0O0O00['name'] = O0O0000O000O0O000.key  #line:3103
                OO00OO0OOOO0O0O00['size'] = O0O0000O000O0O000.size  #line:3104
                OO00OO0OOOO0O0O00['type'] = O0O0000O000O0O000.type  #line:3105
                OO00OO0OOOO0O0O00[
                    'download'] = OOOO00O00000O00O0.download_file(
                        OOOOOOO000OO00OO0 + O0O0000O000O0O000.key)  #line:3106
                OO00OO0OOOO0O0O00[
                    'time'] = O0O0000O000O0O000.last_modified  #line:3107
                O000OO0O0O000O0O0.append(OO00OO0OOOO0O0O00)  #line:3108
            O0O0OOOOOO0O0O00O = {}  #line:3109
            O0O0OOOOOO0O0O00O['path'] = get.path  #line:3110
            O0O0OOOOOO0O0O00O['list'] = O000OO0O0O000O0O0  #line:3111
            return O0O0OOOOOO0O0O00O  #line:3112
        except Exception as OO0OOO000OO0OOOO0:  #line:3113
            return public.returnMsg(False, str(OO0OOO000OO0OOOO0))  #line:3114

    def upload_file_by_path(O000O000000000OOO, O00OOO0000OOOO0O0,
                            O000OO00O0O00OOOO):  #line:3116
        ""  #line:3123
        O000O000000000OOO.__OO0OO0O0O000OO0OO()  #line:3125
        if not O000O000000000OOO.__OOOOOO00O000000O0:  #line:3126
            return False  #line:3127
        try:  #line:3128
            OO0OO0000OO00OO00 = main().get_path(
                os.path.dirname(O000OO00O0O00OOOO)) + os.path.basename(
                    O000OO00O0O00OOOO)  #line:3131
            try:  #line:3133
                import oss2  #line:3134
                print('|-正在上传{}到阿里云OSS'.format(O00OOO0000OOOO0O0),
                      end='')  #line:3135
                OOOOO00OO00OOO000 = oss2.Bucket(
                    O000O000000000OOO.__OOOOOO00O000000O0,
                    O000O000000000OOO.__OOOOO0O0000OOO00O,
                    O000O000000000OOO.__O0O0OO000OO0O0OO0)  #line:3137
                oss2.defaults.connection_pool_size = 4  #line:3139
                O000OOO0O0O0O00O0 = oss2.resumable_upload(
                    OOOOO00OO00OOO000,
                    OO0OO0000OO00OO00,
                    O00OOO0000OOOO0O0,
                    store=oss2.ResumableStore(root='/tmp'),
                    multipart_threshold=1024 * 1024 * 2,
                    part_size=1024 * 1024,
                    num_threads=1)  #line:3147
                print(' ==> 成功')  #line:3148
            except:  #line:3149
                print('|-无法上传{}到阿里云OSS！请检查阿里云OSS配置是否正确！'.format(
                    O00OOO0000OOOO0O0))  #line:3150
            return True  #line:3154
        except Exception as OO0O00O0OO00000OO:  #line:3155
            print(OO0O00O0OO00000OO)  #line:3156
            if OO0O00O0OO00000OO.status == 403:  #line:3157
                time.sleep(5)  #line:3158
                O000O000000000OOO.__O00000OOOOO00OOOO += 1  #line:3159
                if O000O000000000OOO.__O00000OOOOO00OOOO < 2:  #line:3160
                    O000O000000000OOO.upload_file_by_path(
                        O00OOO0000OOOO0O0, O000OO00O0O00OOOO)  #line:3162
            return False  #line:3163

    def download_file(O0O0O0OO0OOO0O0O0, OO0OO0O0000000O00):  #line:3165
        ""  #line:3171
        O0O0O0OO0OOO0O0O0.__OO0OO0O0O000OO0OO()  #line:3173
        if not O0O0O0OO0OOO0O0O0.__OOOOOO00O000000O0:  #line:3174
            return None  #line:3175
        try:  #line:3176
            import oss2  #line:3177
            O00O0O0O0O0OOOOO0 = oss2.Bucket(
                O0O0O0OO0OOO0O0O0.__OOOOOO00O000000O0,
                O0O0O0OO0OOO0O0O0.__OOOOO0O0000OOO00O,
                O0O0O0OO0OOO0O0O0.__O0O0OO000OO0O0OO0)  #line:3179
            OOO00O0OOO0OO00O0 = O00O0O0O0O0OOOOO0.sign_url(
                'GET', OO0OO0O0000000O00, 3600)  #line:3180
            return OOO00O0OOO0OO00O0  #line:3181
        except:  #line:3182
            print(O0O0O0OO0OOO0O0O0.__O000OOOO0O000O000)  #line:3183
            return None  #line:3184

    def alioss_delete_file(O0OOO0000OO0OOOO0, OO0OO0OO000O0O00O):  #line:3186
        ""  #line:3192
        O0OOO0000OO0OOOO0.__OO0OO0O0O000OO0OO()  #line:3194
        if not O0OOO0000OO0OOOO0.__OOOOOO00O000000O0:  #line:3195
            return False  #line:3196
        try:  #line:3198
            import oss2  #line:3199
            O00OOO0O00OO00000 = oss2.Bucket(
                O0OOO0000OO0OOOO0.__OOOOOO00O000000O0,
                O0OOO0000OO0OOOO0.__OOOOO0O0000OOO00O,
                O0OOO0000OO0OOOO0.__O0O0OO000OO0O0OO0)  #line:3201
            OO0OOOO00O00OO0OO = O00OOO0O00OO00000.delete_object(
                OO0OO0OO000O0O00O)  #line:3202
            return OO0OOOO00O00OO0OO.status  #line:3203
        except Exception as O0O0OO00O0OOOOOOO:  #line:3204
            if O0O0OO00O0OOOOOOO.status == 403:  #line:3205
                O0OOO0000OO0OOOO0.__O00000OOOOO00OOOO += 1  #line:3206
                if O0OOO0000OO0OOOO0.__O00000OOOOO00OOOO < 2:  #line:3207
                    O0OOO0000OO0OOOO0.alioss_delete_file(
                        OO0OO0OO000O0O00O)  #line:3209
            print('删除失败!')  #line:3211
            return None  #line:3212

    def remove_file(O00OOOO000OO0000O, O00OOOOO00000O0O0):  #line:3214
        ""  #line:3221
        OOOO00O0OO00OO000 = main().get_path(O00OOOOO00000O0O0.path)  #line:3222
        OO00O00OO0OO0O000 = OOOO00O0OO00OO000 + O00OOOOO00000O0O0.filename  #line:3223
        O00OOOO000OO0000O.alioss_delete_file(OO00O00OO0OO0O000)  #line:3224
        return public.returnMsg(True, '删除文件成功!{}----{}'.format(
            OOOO00O0OO00OO000, OO00O00OO0OO0O000))  #line:3225


class txcos_main:  #line:3229
    __O00000OOOO0000O0O = None  #line:3230
    __OOOOOOOOO00000OO0 = None  #line:3231
    __O0OO00OO0OOOO00O0 = 0  #line:3232
    __OOOOOOO00000OOO0O = None  #line:3233
    __OOOOOO0O0O0O00OO0 = None  #line:3234
    __OOO0OOOOOO0OO0OO0 = None  #line:3235
    __O0OO0O000OOO0OO0O = None  #line:3236
    __OOOOOOOO0O00O0O00 = "ERROR: 无法连接腾讯云COS !"  #line:3237

    def __init__(OO0000O00O000OO00):  #line:3239
        OO0000O00O000OO00.__O0OOO0OO00OO00000()  #line:3240

    def __O0OOO0OO00OO00000(O000OO00OOOO0O00O):  #line:3242
        ""  #line:3245
        if O000OO00OOOO0O00O.__O00000OOOO0000O0O: return  #line:3246
        O00O000O0OOO000O0 = O000OO00OOOO0O00O.get_config()  #line:3248
        O000OO00OOOO0O00O.__OOOOOOO00000OOO0O = O00O000O0OOO000O0[
            0]  #line:3249
        O000OO00OOOO0O00O.__OOOOOO0O0O0O00OO0 = O00O000O0OOO000O0[
            1]  #line:3250
        O000OO00OOOO0O00O.__OOO0OOOOOO0OO0OO0 = O00O000O0OOO000O0[
            2]  #line:3251
        O000OO00OOOO0O00O.__O0OO0O000OOO0OO0O = O00O000O0OOO000O0[
            3]  #line:3252
        O000OO00OOOO0O00O.__OOOOOOOOO00000OO0 = main().get_path(
            O00O000O0OOO000O0[4])  #line:3253
        try:  #line:3254
            from qcloud_cos import CosConfig  #line:3255
            from qcloud_cos import CosS3Client  #line:3256
            O0OO0OOOOOO00OO00 = CosConfig(
                Region=O000OO00OOOO0O00O.__OOO0OOOOOO0OO0OO0,
                SecretId=O000OO00OOOO0O00O.__OOOOOOO00000OOO0O,
                SecretKey=O000OO00OOOO0O00O.__OOOOOO0O0O0O00OO0,
                Token=None,
                Scheme='http')  #line:3261
            O000OO00OOOO0O00O.__O00000OOOO0000O0O = CosS3Client(
                O0OO0OOOOOO00OO00)  #line:3262
        except Exception as OOOOOOOOO0O000O00:  #line:3263
            pass  #line:3264

    def get_config(O0OO00OOO0000OO0O, get=None):  #line:3267
        ""  #line:3270
        return main().get_config('txcos')  #line:3271

    def check_config(OOOO00O0O00OOO0OO):  #line:3274
        try:  #line:3275
            OO000O000OO00OO0O = []  #line:3276
            O0OO0O00O0O0O0OOO = []  #line:3277
            O00OO00O0O0000OO0 = OOOO00O0O00OOO0OO.__OOOOOOOOO00000OO0 + main(
            ).get_path('/')  #line:3278
            O0O000OOO00OO0OOO = OOOO00O0O00OOO0OO.__O00000OOOO0000O0O.list_objects(
                Bucket=OOOO00O0O00OOO0OO.__O0OO0O000OOO0OO0O,
                MaxKeys=100,
                Delimiter='/',
                Prefix=O00OO00O0O0000OO0)  #line:3282
            return True  #line:3283
        except:  #line:3284
            return False  #line:3285

    def upload_file(O0OOO0O000O0OO000, O00O000OO000O0OOO):  #line:3287
        ""  #line:3291
        O0OOO0O000O0OO000.__O0OOO0OO00OO00000()  #line:3293
        if not O0OOO0O000O0OO000.__O00000OOOO0000O0O:  #line:3294
            return False  #line:3295
        try:  #line:3297
            OOOOOOO0OO0OO00O0, OOOOOOOO0000OO0OO = os.path.split(
                O00O000OO000O0OOO)  #line:3299
            OOOOOOOO0000OO0OO = O0OOO0O000O0OO000.__OOOOOOOOO00000OO0 + OOOOOOOO0000OO0OO  #line:3300
            O0O0OO000OOOO0000 = O0OOO0O000O0OO000.__O00000OOOO0000O0O.upload_file(
                Bucket=O0OOO0O000O0OO000.__O0OO0O000OOO0OO0O,
                Key=OOOOOOOO0000OO0OO,
                MAXThread=10,
                PartSize=5,
                LocalFilePath=O00O000OO000O0OOO)  #line:3306
        except:  #line:3307
            time.sleep(1)  #line:3308
            O0OOO0O000O0OO000.__O0OO00OO0OOOO00O0 += 1  #line:3309
            if O0OOO0O000O0OO000.__O0OO00OO0OOOO00O0 < 2:  #line:3310
                O0OOO0O000O0OO000.upload_file(O00O000OO000O0OOO)  #line:3312
            print(O0OOO0O000O0OO000.__OOOOOOOO0O00O0O00)  #line:3313
            return None  #line:3314

    def upload_file_by_path(OO0OO0O00O0O0OOOO, O0O00O0OO00OOOO00,
                            O00O000000O000O00):  #line:3316
        ""  #line:3321
        OO0OO0O00O0O0OOOO.__O0OOO0OO00OO00000()  #line:3323
        if not OO0OO0O00O0O0OOOO.__O00000OOOO0000O0O:  #line:3324
            return False  #line:3325
        try:  #line:3327
            print('|-正在上传{}到腾讯云COS'.format(O0O00O0OO00OOOO00),
                  end='')  #line:3328
            OOOO000OO0000OOO0, OO0000O00OOOOOOOO = os.path.split(
                O0O00O0OO00OOOO00)  #line:3329
            OO0OO0O00O0O0OOOO.__OOOOOOOOO00000OO0 = main().get_path(
                os.path.dirname(O00O000000O000O00))  #line:3330
            OO0000O00OOOOOOOO = OO0OO0O00O0O0OOOO.__OOOOOOOOO00000OO0 + '/' + OO0000O00OOOOOOOO  #line:3331
            OOO0O0OO00OO0O000 = OO0OO0O00O0O0OOOO.__O00000OOOO0000O0O.upload_file(
                Bucket=OO0OO0O00O0O0OOOO.__O0OO0O000OOO0OO0O,
                Key=OO0000O00OOOOOOOO,
                MAXThread=10,
                PartSize=5,
                LocalFilePath=O0O00O0OO00OOOO00)  #line:3338
            print(' ==> 成功')  #line:3340
            return True  #line:3341
        except Exception as O0O0OOOO0O00OO00O:  #line:3342
            time.sleep(1)  #line:3344
            OO0OO0O00O0O0OOOO.__O0OO00OO0OOOO00O0 += 1  #line:3345
            if OO0OO0O00O0O0OOOO.__O0OO00OO0OOOO00O0 < 2:  #line:3346
                OO0OO0O00O0O0OOOO.upload_file_by_path(
                    O0O00O0OO00OOOO00, O00O000000O000O00)  #line:3348
            return False  #line:3349

    def create_dir(O0O0OOO0OOO0O00O0, get=None):  #line:3351
        ""  #line:3354
        O0O0OOO0OOO0O00O0.__O0OOO0OO00OO00000()  #line:3356
        if not O0O0OOO0OOO0O00O0.__O00000OOOO0000O0O:  #line:3357
            return False  #line:3358
        O00000OO0OOOO000O = main().get_path(get.path + get.dirname)  #line:3360
        OO000OOO0O000OO00 = '/tmp/dirname.pl'  #line:3361
        public.writeFile(OO000OOO0O000OO00, '')  #line:3362
        OO00OOOO0O0O0O00O = O0O0OOO0OOO0O00O0.__O00000OOOO0000O0O.put_object(
            Bucket=O0O0OOO0OOO0O00O0.__O0OO0O000OOO0OO0O,
            Body=b'',
            Key=O00000OO0OOOO000O)  #line:3365
        os.remove(OO000OOO0O000OO00)  #line:3366
        return public.returnMsg(True, '创建成功!')  #line:3367

    def get_list(OO00OOOO0OOO00OO0, get=None):  #line:3369
        ""  #line:3372
        OO00OOOO0OOO00OO0.__O0OOO0OO00OO00000()  #line:3374
        if not OO00OOOO0OOO00OO0.__O00000OOOO0000O0O:  #line:3375
            return False  #line:3376
        try:  #line:3378
            O00000OO00OO0OO00 = []  #line:3379
            O000OOOO00OO00O00 = []  #line:3380
            OOO00OOO0O00O0O00 = main().get_path(get.path)  #line:3381
            if 'Contents' in OO00OOOO0OOO00OO0.__O00000OOOO0000O0O.list_objects(
                    Bucket=OO00OOOO0OOO00OO0.__O0OO0O000OOO0OO0O,
                    MaxKeys=100,
                    Delimiter='/',
                    Prefix=OOO00OOO0O00O0O00):  #line:3385
                for OOOOO0000OOO00O0O in OO00OOOO0OOO00OO0.__O00000OOOO0000O0O.list_objects(
                        Bucket=OO00OOOO0OOO00OO0.__O0OO0O000OOO0OO0O,
                        MaxKeys=100,
                        Delimiter='/',
                        Prefix=OOO00OOO0O00O0O00)['Contents']:  #line:3389
                    O00O000OOOO0OO000 = {}  #line:3390
                    OOOOO0000OOO00O0O['Key'] = OOOOO0000OOO00O0O[
                        'Key'].replace(OOO00OOO0O00O0O00, '')  #line:3391
                    if not OOOOO0000OOO00O0O['Key']: continue  #line:3392
                    O00O000OOOO0OO000['name'] = OOOOO0000OOO00O0O[
                        'Key']  #line:3393
                    O00O000OOOO0OO000['size'] = OOOOO0000OOO00O0O[
                        'Size']  #line:3394
                    O00O000OOOO0OO000['type'] = OOOOO0000OOO00O0O[
                        'StorageClass']  #line:3395
                    O00O000OOOO0OO000[
                        'download'] = OO00OOOO0OOO00OO0.download_file(
                            OOO00OOO0O00O0O00 +
                            OOOOO0000OOO00O0O['Key'])  #line:3396
                    O00O000OOOO0OO000['time'] = OOOOO0000OOO00O0O[
                        'LastModified']  #line:3397
                    O00000OO00OO0OO00.append(O00O000OOOO0OO000)  #line:3398
            else:  #line:3399
                pass  #line:3400
            if 'CommonPrefixes' in OO00OOOO0OOO00OO0.__O00000OOOO0000O0O.list_objects(
                    Bucket=OO00OOOO0OOO00OO0.__O0OO0O000OOO0OO0O,
                    MaxKeys=100,
                    Delimiter='/',
                    Prefix=OOO00OOO0O00O0O00):  #line:3403
                for O0O00OOO0O0O000O0 in OO00OOOO0OOO00OO0.__O00000OOOO0000O0O.list_objects(
                        Bucket=OO00OOOO0OOO00OO0.__O0OO0O000OOO0OO0O,
                        MaxKeys=100,
                        Delimiter='/',
                        Prefix=OOO00OOO0O00O0O00
                )['CommonPrefixes']:  #line:3408
                    if not O0O00OOO0O0O000O0['Prefix']: continue  #line:3409
                    O0O0O000OOO0O000O = O0O00OOO0O0O000O0['Prefix'].split(
                        '/')[-2] + '/'  #line:3410
                    O000OOOO00OO00O00.append(O0O0O000OOO0O000O)  #line:3411
            else:  #line:3412
                pass  #line:3413
            O0000OO0OO0O0OO0O = {}  #line:3414
            O0000OO0OO0O0OO0O['path'] = get.path  #line:3415
            O0000OO0OO0O0OO0O['list'] = O00000OO00OO0OO00  #line:3416
            O0000OO0OO0O0OO0O['dir'] = O000OOOO00OO00O00  #line:3417
            return O0000OO0OO0O0OO0O  #line:3418
        except:  #line:3419
            O0000OO0OO0O0OO0O = {}  #line:3420
            if OO00OOOO0OOO00OO0.__O00000OOOO0000O0O:  #line:3421
                O0000OO0OO0O0OO0O['status'] = True  #line:3422
            else:  #line:3423
                O0000OO0OO0O0OO0O['status'] = False  #line:3424
            O0000OO0OO0O0OO0O['path'] = get.path  #line:3425
            O0000OO0OO0O0OO0O['list'] = O00000OO00OO0OO00  #line:3426
            O0000OO0OO0O0OO0O['dir'] = O000OOOO00OO00O00  #line:3427
            return O0000OO0OO0O0OO0O  #line:3428

    def download_file(OO00OO00000O0OOO0,
                      O0OO00O0OO0O0OOO0,
                      Expired=300):  #line:3430
        ""  #line:3433
        OO00OO00000O0OOO0.__O0OOO0OO00OO00000()  #line:3435
        if not OO00OO00000O0OOO0.__O00000OOOO0000O0O:  #line:3436
            return None  #line:3437
        try:  #line:3438
            O0O0OO0OOOO0OOO00 = OO00OO00000O0OOO0.__O00000OOOO0000O0O.get_presigned_download_url(
                Bucket=OO00OO00000O0OOO0.__O0OO0O000OOO0OO0O,
                Key=O0OO00O0OO0O0OOO0)  #line:3440
            O0O0OO0OOOO0OOO00 = re.findall('([^?]*)?.*',
                                           O0O0OO0OOOO0OOO00)[0]  #line:3441
            return O0O0OO0OOOO0OOO00  #line:3442
        except:  #line:3443
            print(OO00OO00000O0OOO0.__OOOOOOOO0O00O0O00)  #line:3444
            return None  #line:3445

    def delete_file(O00OO000O0OO0OO0O, OO0OO0O0O0O000OO0):  #line:3447
        ""  #line:3451
        O00OO000O0OO0OO0O.__O0OOO0OO00OO00000()  #line:3453
        if not O00OO000O0OO0OO0O.__O00000OOOO0000O0O:  #line:3454
            return False  #line:3455
        try:  #line:3457
            O00OO000O0OOOOO00 = O00OO000O0OO0OO0O.__O00000OOOO0000O0O.delete_object(
                Bucket=O00OO000O0OO0OO0O.__O0OO0O000OOO0OO0O,
                Key=OO0OO0O0O0O000OO0)  #line:3459
            return O00OO000O0OOOOO00  #line:3460
        except Exception as OOOOOOOOOO0000OOO:  #line:3461
            O00OO000O0OO0OO0O.__O0OO00OO0OOOO00O0 += 1  #line:3462
            if O00OO000O0OO0OO0O.__O0OO00OO0OOOO00O0 < 2:  #line:3463
                O00OO000O0OO0OO0O.delete_file(OO0OO0O0O0O000OO0)  #line:3465
            print(O00OO000O0OO0OO0O.__OOOOOOOO0O00O0O00)  #line:3466
            return None  #line:3467

    def remove_file(OOOOO0OOOOOO0O000, O000000OO0O00O0OO):  #line:3470
        OOOOOO000O00O0O00 = main().get_path(O000000OO0O00O0OO.path)  #line:3471
        O0O0O00000OOO0OOO = OOOOOO000O00O0O00 + O000000OO0O00O0OO.filename  #line:3472
        OOOOO0OOOOOO0O000.delete_file(O0O0O00000OOO0OOO)  #line:3473
        return public.returnMsg(True, '删除文件成功!')  #line:3474


class ftp_main:  #line:3478
    __O0OO00O00O00000OO = '/'  #line:3479

    def __init__(OOOO00OO000O0O00O):  #line:3481
        OOOO00OO000O0O00O.__O0OO00O00O00000OO = OOOO00OO000O0O00O.get_config(
            None)[3]  #line:3482

    def get_config(O000O00O00OOO0OOO, get=None):  #line:3484
        return main().get_config('ftp')  #line:3485

    def set_config(O0O00OOOO000O00O0, O000O0O0O00000000):  #line:3487
        OO0OO0000O00O0OOO = main()._config_path + '/ftp.conf'  #line:3488
        OO0OO0O0O0O0000O0 = O000O0O0O00000000.ftp_host + '|' + O000O0O0O00000000.ftp_user + '|' + O000O0O0O00000000.ftp_pass + '|' + O000O0O0O00000000.ftp_path  #line:3489
        public.writeFile(OO0OO0000O00O0OOO, OO0OO0O0O0O0000O0)  #line:3490
        return public.returnMsg(True, '设置成功!')  #line:3491

    def connentFtp(O00OOOO0O0O00OOOO):  #line:3494
        from ftplib import FTP  #line:3495
        OOOO0OOO0OO0O0000 = O00OOOO0O0O00OOOO.get_config()  #line:3496
        if OOOO0OOO0OO0O0000[0].find(':') == -1:
            OOOO0OOO0OO0O0000[0] += ':21'  #line:3497
        O000OOO00O0O00OOO = OOOO0OOO0OO0O0000[0].split(':')  #line:3498
        if O000OOO00O0O00OOO[1] == '': O000OOO00O0O00OOO[1] = '21'  #line:3499
        O0000O000OO000000 = FTP()  #line:3500
        O0000O000OO000000.set_debuglevel(0)  #line:3501
        O0000O000OO000000.connect(O000OOO00O0O00OOO[0],
                                  int(O000OOO00O0O00OOO[1]))  #line:3502
        O0000O000OO000000.login(OOOO0OOO0OO0O0000[1],
                                OOOO0OOO0OO0O0000[2])  #line:3503
        if O00OOOO0O0O00OOOO.__O0OO00O00O00000OO != '/':  #line:3504
            O00OOOO0O0O00OOOO.dirname = O00OOOO0O0O00OOOO.__O0OO00O00O00000OO  #line:3505
            O00OOOO0O0O00OOOO.path = '/'  #line:3506
            O00OOOO0O0O00OOOO.createDir(O00OOOO0O0O00OOOO,
                                        O0000O000OO000000)  #line:3507
        O0000O000OO000000.cwd(
            O00OOOO0O0O00OOOO.__O0OO00O00O00000OO)  #line:3508
        return O0000O000OO000000  #line:3509

    def check_config(OO00O0O0O00O0O000):  #line:3512
        try:  #line:3513
            O0O00O000O0O00O0O = OO00O0O0O00O0O000.connentFtp()  #line:3514
            if O0O00O000O0O00O0O: return True  #line:3515
        except:  #line:3516
            return False  #line:3517

    def createDir(O000OOOO0OOO0OO0O, OO0O0O0OO0OOOOO0O, ftp=None):  #line:3520
        try:  #line:3521
            if not ftp: ftp = O000OOOO0OOO0OO0O.connentFtp()  #line:3522
            O0O0O000O0OO00OO0 = OO0O0O0OO0OOOOO0O.dirname.split(
                '/')  #line:3523
            ftp.cwd(OO0O0O0OO0OOOOO0O.path)  #line:3524
            for OO00OO0OOOOO0O00O in O0O0O000O0OO00OO0:  #line:3525
                if not OO00OO0OOOOO0O00O: continue  #line:3526
                if not OO00OO0OOOOO0O00O in ftp.nlst():
                    ftp.mkd(OO00OO0OOOOO0O00O)  #line:3527
                ftp.cwd(OO00OO0OOOOO0O00O)  #line:3528
            return public.returnMsg(True, '目录创建成功!')  #line:3529
        except:  #line:3530
            return public.returnMsg(False, '目录创建失败!')  #line:3531

    def updateFtp(OOOO0OOOO00000OO0, OOO00OOOOOO000OO0):  #line:3534
        try:  #line:3535
            O0O0O0O00O0OOO0O0 = OOOO0OOOO00000OO0.connentFtp()  #line:3536
            OO0OOOOOOOOO00000 = 1024  #line:3537
            O00OOO00O0OOO0000 = open(OOO00OOOOOO000OO0, 'rb')  #line:3538
            O0O0O0O00O0OOO0O0.storbinary(
                'STOR %s' % os.path.basename(OOO00OOOOOO000OO0),
                O00OOO00O0OOO0000, OO0OOOOOOOOO00000)  #line:3540
            O00OOO00O0OOO0000.close()  #line:3541
            O0O0O0O00O0OOO0O0.quit()  #line:3542
        except:  #line:3543
            if os.path.exists(OOO00OOOOOO000OO0):
                os.remove(OOO00OOOOOO000OO0)  #line:3544
            print('连接服务器失败!')  #line:3545
            return {'status': False, 'msg': '连接服务器失败!'}  #line:3546

    def upload_file_by_path(O0OOOO0O000O0O0O0, O000OOOO00OO0000O,
                            O0OO0O0O0000000OO):  #line:3549
        try:  #line:3550
            O0OOO0O0O0O0OOO00 = O0OOOO0O000O0O0O0.connentFtp()  #line:3551
            O00OOO0OOO00O0O00 = O0OOOO0O000O0O0O0.get_config(None)[
                3]  #line:3552
            O0OOOOOOO0O00OOO0 = public.dict_obj()  #line:3553
            if O0OO0O0O0000000OO[0] == "/":  #line:3554
                O0OO0O0O0000000OO = O0OO0O0O0000000OO[1:]  #line:3555
            O0OOOOOOO0O00OOO0.path = O00OOO0OOO00O0O00  #line:3556
            O0OOOOOOO0O00OOO0.dirname = os.path.dirname(
                O0OO0O0O0000000OO)  #line:3557
            O0OOOO0O000O0O0O0.createDir(O0OOOOOOO0O00OOO0)  #line:3558
            OOO0O000OOOOOO0OO = os.path.join(
                O00OOO0OOO00O0O00,
                os.path.dirname(O0OO0O0O0000000OO))  #line:3559
            print("目标上传目录：{}".format(OOO0O000OOOOOO0OO))  #line:3560
            O0OOO0O0O0O0OOO00.cwd(OOO0O000OOOOOO0OO)  #line:3561
            O0OO00OO000OOO00O = 1024  #line:3562
            O0O00O000OOO0OO00 = open(O000OOOO00OO0000O, 'rb')  #line:3563
            try:  #line:3564
                O0OOO0O0O0O0OOO00.storbinary(
                    'STOR %s' % OOO0O000OOOOOO0OO + '/' +
                    os.path.basename(O000OOOO00OO0000O), O0O00O000OOO0OO00,
                    O0OO00OO000OOO00O)  #line:3567
            except:  #line:3568
                O0OOO0O0O0O0OOO00.storbinary(
                    'STOR %s' % os.path.split(O000OOOO00OO0000O)[1],
                    O0O00O000OOO0OO00, O0OO00OO000OOO00O)  #line:3570
            O0O00O000OOO0OO00.close()  #line:3571
            O0OOO0O0O0O0OOO00.quit()  #line:3572
            return True  #line:3573
        except:  #line:3574
            print(public.get_error_info())  #line:3575
            return False  #line:3576

    def deleteFtp(O0O00OO0OOO0000OO,
                  OO00OOO00OO0OOO0O,
                  is_inc=False):  #line:3579
        O0OOO0O0OOO0OOO00 = []  #line:3580
        if os.path.isfile(main()._full_file):  #line:3581
            try:  #line:3582
                O0OOO0O0OOO0OOO00 = json.loads(
                    public.readFile(main()._full_file))[0]  #line:3584
            except:  #line:3585
                O0OOO0O0OOO0OOO00 = []  #line:3586
        try:  #line:3587
            O00O000OOOOO0O0O0 = O0O00OO0OOO0000OO.connentFtp()  #line:3588
            if is_inc:  #line:3589
                try:  #line:3590
                    O000O00O000O0OOO0 = O00O000OOOOO0O0O0.nlst()  #line:3591
                    for OOOOO0OO0OOOOO000 in O000O00O000O0OOO0:  #line:3600
                        if OOOOO0OO0OOOOO000 == '.' or OOOOO0OO0OOOOO000 == '..':
                            continue  #line:3601
                        if OOOOO0OO0OOOOO000 == 'full_record.json':
                            continue  #line:3602
                        if O0OOO0O0OOO0OOO00 and 'full_name' in O0OOO0O0OOO0OOO00 and os.path.basename(
                                O0OOO0O0OOO0OOO00['full_name']
                        ) == OOOOO0OO0OOOOO000:  #line:3604
                            continue  #line:3605
                        try:  #line:3606
                            O00O000OOOOO0O0O0.rmd(
                                OOOOO0OO0OOOOO000)  #line:3607
                        except:  #line:3608
                            O00O000OOOOO0O0O0.delete(
                                OOOOO0OO0OOOOO000)  #line:3609
                        print('|-已从FTP存储空间清理过期备份文件{}'.format(
                            OOOOO0OO0OOOOO000))  #line:3610
                    return True  #line:3611
                except Exception as OOOO000OOOOO0O00O:  #line:3612
                    print(OOOO000OOOOO0O00O)  #line:3613
                    return False  #line:3614
            try:  #line:3615
                O00O000OOOOO0O0O0.rmd(OO00OOO00OO0OOO0O)  #line:3616
            except:  #line:3617
                O00O000OOOOO0O0O0.delete(OO00OOO00OO0OOO0O)  #line:3618
            print(
                '|-已从FTP存储空间清理过期备份文件{}'.format(OO00OOO00OO0OOO0O))  #line:3619
            return True  #line:3620
        except Exception as OO0O00O00000OO0O0:  #line:3621
            print(OO0O00O00000OO0O0)  #line:3622
            return False  #line:3623

    def remove_file(OOO00O0O00OO0O0O0, OO000OOOOO0000OOO):  #line:3626
        O00OOOOOO000OO0OO = OOO00O0O00OO0O0O0.get_config(None)[3]  #line:3627
        if OO000OOOOO0000OOO.path[0] == "/":  #line:3628
            OO000OOOOO0000OOO.path = OO000OOOOO0000OOO.path[1:]  #line:3629
        OOO00O0O00OO0O0O0.__O0OO00O00O00000OO = os.path.join(
            O00OOOOOO000OO0OO, OO000OOOOO0000OOO.path)  #line:3630
        if 'is_inc' not in OO000OOOOO0000OOO and OOO00O0O00OO0O0O0.deleteFtp(
                OO000OOOOO0000OOO.filename):  #line:3631
            return public.returnMsg(True, '删除成功!')  #line:3632
        if 'is_inc' in OO000OOOOO0000OOO and OO000OOOOO0000OOO.is_inc:  #line:3633
            if OOO00O0O00OO0O0O0.deleteFtp(OO000OOOOO0000OOO.filename,
                                           True):  #line:3634
                return public.returnMsg(True, '删除成功!')  #line:3635
        return public.returnMsg(False, '删除失败!')  #line:3636

    def get_list(O000000OO0OOOO000, get=None):  #line:3639
        try:  #line:3640
            O000000OO0OOOO000.__O0OO00O00O00000OO = get.path  #line:3641
            OOO0O0OOO00OOO0OO = O000000OO0OOOO000.connentFtp()  #line:3642
            O000OO0O00O0OOO0O = OOO0O0OOO00OOO0OO.nlst()  #line:3643
            OO000000OO0O0O0O0 = []  #line:3645
            O0O0OOOO0OO0OO0O0 = []  #line:3646
            O0OOOOOOOO000O0OO = []  #line:3647
            for O0O0OOO0000OO00OO in O000OO0O00O0OOO0O:  #line:3648
                if O0O0OOO0000OO00OO == '.' or O0O0OOO0000OO00OO == '..':
                    continue  #line:3649
                OO00O00O0O00O0OO0 = public.M('backup').where(
                    'name=?', (O0O0OOO0000OO00OO,
                               )).field('size,addtime').find()  #line:3651
                if not OO00O00O0O00O0OO0:  #line:3652
                    OO00O00O0O00O0OO0 = {}  #line:3653
                    OO00O00O0O00O0OO0[
                        'addtime'] = '1970/01/01 00:00:01'  #line:3654
                OOO0O0OO0O00O0O00 = {}  #line:3655
                OOO0O0OO0O00O0O00['name'] = O0O0OOO0000OO00OO  #line:3656
                OOO0O0OO0O00O0O00['time'] = int(
                    time.mktime(
                        time.strptime(OO00O00O0O00O0OO0['addtime'],
                                      '%Y/%m/%d %H:%M:%S')))  #line:3659
                try:  #line:3660
                    OOO0O0OO0O00O0O00['size'] = OOO0O0OOO00OOO0OO.size(
                        O0O0OOO0000OO00OO)  #line:3661
                    OOO0O0OO0O00O0O00['dir'] = False  #line:3662
                    OOO0O0OO0O00O0O00['download'] = O000000OO0OOOO000.getFile(
                        O0O0OOO0000OO00OO)  #line:3663
                    O0O0OOOO0OO0OO0O0.append(OOO0O0OO0O00O0O00)  #line:3664
                except:  #line:3665
                    OOO0O0OO0O00O0O00['size'] = 0  #line:3666
                    OOO0O0OO0O00O0O00['dir'] = True  #line:3667
                    OOO0O0OO0O00O0O00['download'] = ''  #line:3668
                    OO000000OO0O0O0O0.append(OOO0O0OO0O00O0O00)  #line:3669
            O0OOOOOOOO000O0OO = OO000000OO0O0O0O0 + O0O0OOOO0OO0OO0O0  #line:3671
            O00O00O0OOOO0O00O = {}  #line:3672
            O00O00O0OOOO0O00O[
                'path'] = O000000OO0OOOO000.__O0OO00O00O00000OO  #line:3673
            O00O00O0OOOO0O00O['list'] = O0OOOOOOOO000O0OO  #line:3674
            return O00O00O0OOOO0O00O  #line:3675
        except Exception as O0O0OOO0O00O0OO0O:  #line:3676
            return {'status': False, 'msg': str(O0O0OOO0O00O0OO0O)}  #line:3677

    def getFile(OOOO000OO00OOO00O, O0O0000000OOO0O00):  #line:3680
        try:  #line:3681
            OO00O000O000O0000 = OOOO000OO00OOO00O.get_config()  #line:3682
            if OO00O000O000O0000[0].find(':') == -1:
                OO00O000O000O0000[0] += ':21'  #line:3683
            O0OO00OOO0OO0O000 = OO00O000O000O0000[0].split(':')  #line:3684
            if O0OO00OOO0OO0O000[1] == '':
                O0OO00OOO0OO0O000[1] = '21'  #line:3685
            O00O0OOO0OOO0O0O0 = 'ftp://' + OO00O000O000O0000[
                1] + ':' + OO00O000O000O0000[2] + '@' + O0OO00OOO0OO0O000[
                    0] + ':' + O0OO00OOO0OO0O000[1] + (
                        OOOO000OO00OOO00O.__O0OO00O00O00000OO + '/' +
                        O0O0000000OOO0O00).replace('//', '/')  #line:3688
        except:  #line:3689
            O00O0OOO0OOO0O0O0 = None  #line:3690
        return O00O0OOO0OOO0O0O0  #line:3691

    def download_file(OO00OO000OO0OO0OO, O0O000O00OOOOOO00):  #line:3694
        return OO00OO000OO0OO0OO.getFile(O0O000O00OOOOOO00)  #line:3695


class qiniu_main:  #line:3699
    __O00O000OOOOOOO0OO = None  #line:3700
    __O00000000OOOOO000 = None  #line:3701
    __OO0OO00OO0OO0O0O0 = None  #line:3702
    __OOOO00O000000O00O = None  #line:3703
    __OO0O00OO0OO00O00O = "ERROR: 无法连接到七牛云OSS服务器，请检查[AccessKeyId/AccessKeySecret]设置是否正确!"  #line:3704

    def __init__(OO00OO00OO00OOOO0):  #line:3706
        OO00OO00OO00OOOO0.__O0O0OO0000O0O0000()  #line:3707

    def __O0O0OO0000O0O0000(OO00O0OOOOOO0O000):  #line:3709
        if OO00O0OOOOOO0O000.__O00O000OOOOOOO0OO: return  #line:3710
        OO0000O0O00OO0000 = OO00O0OOOOOO0O000.get_config()  #line:3712
        OO00O0OOOOOO0O000.__O00000000OOOOO000 = OO0000O0O00OO0000[
            3]  #line:3714
        if OO0000O0O00OO0000[2].find(OO0000O0O00OO0000[3]) != -1:  #line:3715
            OO0000O0O00OO0000[2] = OO0000O0O00OO0000[2].replace(
                OO0000O0O00OO0000[3] + '.', '')  #line:3716
        OO00O0OOOOOO0O000.__OO0OO00OO0OO0O0O0 = OO0000O0O00OO0000[
            2]  #line:3717
        OO00O0OOOOOO0O000.__OOOO00O000000O00O = main().get_path(
            OO0000O0O00OO0000[4] + '/bt_backup/')  #line:3718
        if OO00O0OOOOOO0O000.__OOOO00O000000O00O[:1] == '/':  #line:3719
            OO00O0OOOOOO0O000.__OOOO00O000000O00O = OO00O0OOOOOO0O000.__OOOO00O000000O00O[
                1:]  #line:3720
        try:  #line:3722
            from qiniu import Auth  #line:3723
            OO00O0OOOOOO0O000.__O00O000OOOOOOO0OO = Auth(
                OO0000O0O00OO0000[0], OO0000O0O00OO0000[1])  #line:3725
        except Exception as O0OOO0OOO0OOOO00O:  #line:3726
            pass  #line:3727

    def get_config(O00O0000O00O0O0OO, get=None):  #line:3730
        return main().get_config('qiniu')  #line:3731

    def set_config(OO0OOO0OO000O000O, OOOOOO00OO0O0O0OO):  #line:3733
        O0O0000OOO0OO000O = ['qiniu', 'txcos', 'alioss', 'bos', 'ftp',
                             'obs']  #line:3734
        O0O0O000OO000O000 = OOOOOO00OO0O0O0OO.get('cloud_name/d',
                                                  0)  #line:3735
        print(O0O0O000OO000O000)  #line:3736
        if O0O0O000OO000O000 not in O0O0000OOO0OO000O:  #line:3737
            return public.returnMsg(False, '参数不合法！')  #line:3738
        OO00O0OO00000O000 = main()._config_path + '/{}.conf'.format(
            O0O0O000OO000O000)  #line:3739
        O00OOO00O000O0O00 = OOOOOO00OO0O0O0OO.access_key.strip(
        ) + '|' + OOOOOO00OO0O0O0OO.secret_key.strip(
        ) + '|' + OOOOOO00OO0O0O0OO.bucket_name.strip(
        ) + '|' + OOOOOO00OO0O0O0OO.bucket_domain.strip(
        ) + '|' + OOOOOO00OO0O0O0OO.bucket_path.strip()  #line:3743
        return public.returnMsg(True, '设置成功!')  #line:3745

    def check_config(O0OO00O000O00000O):  #line:3748
        try:  #line:3749
            OOO0O0000O0O0OO00 = ''  #line:3750
            O0OO000OOO00OOO0O = O0OO00O000O00000O.get_bucket()  #line:3751
            OO000O00OOOO0OOO0 = '/'  #line:3752
            OOOO0OOOOOO0OO000 = None  #line:3753
            OO000O0000O0000OO = 1000  #line:3754
            OOO0O0000O0O0OO00 = main().get_path(OOO0O0000O0O0OO00)  #line:3755
            O0OOO0OO00000O000, OOO000O0OO000OO00, O0OO00OOOO00OO000 = O0OO000OOO00OOO0O.list(
                O0OO00O000O00000O.__O00000000OOOOO000, OOO0O0000O0O0OO00,
                OOOO0OOOOOO0OO000, OO000O0000O0000OO,
                OO000O00OOOO0OOO0)  #line:3757
            if O0OOO0OO00000O000:  #line:3758
                return True  #line:3759
            else:  #line:3760
                return False  #line:3761
        except:  #line:3762
            return False  #line:3763

    def get_bucket(O0O0O0OOO0O00000O):  #line:3765
        ""  #line:3766
        from qiniu import BucketManager  #line:3768
        OOOO000OO0O000O00 = BucketManager(
            O0O0O0OOO0O00000O.__O00O000OOOOOOO0OO)  #line:3769
        return OOOO000OO0O000O00  #line:3770

    def create_dir(O00O0OO0O0O000OOO, O0OOOOOO00O000OO0):  #line:3772
        ""  #line:3777
        try:  #line:3779
            from qiniu import put_file  #line:3780
            O0OOOOOO00O000OO0 = main().get_path(O0OOOOOO00O000OO0)  #line:3781
            OOOOOO0000OO0O0O0 = '/tmp/dirname.pl'  #line:3782
            public.writeFile(OOOOOO0000OO0O0O0, '')  #line:3783
            O0O0O00000O00O00O = O00O0OO0O0O000OOO.__O00O000OOOOOOO0OO.upload_token(
                O00O0OO0O0O000OOO.__O00000000OOOOO000,
                O0OOOOOO00O000OO0)  #line:3784
            OO0OO0OO00O0O0000, OO0O0000OOO00OO00 = put_file(
                O0O0O00000O00O00O, O0OOOOOO00O000OO0,
                OOOOOO0000OO0O0O0)  #line:3785
            try:  #line:3787
                os.remove(OOOOOO0000OO0O0O0)  #line:3788
            except:  #line:3789
                pass  #line:3790
            if OO0O0000OOO00OO00.status_code == 200:  #line:3792
                return True  #line:3793
            return False  #line:3794
        except Exception as O00OO000OO00OOOO0:  #line:3795
            raise RuntimeError("创建目录出现错误:" +
                               str(O00OO000OO00OOOO0))  #line:3796

    def get_list(O000OO0O0O0OOO00O, get=None):  #line:3798
        OO0O0OOOOO0OO000O = O000OO0O0O0OOO00O.get_bucket()  #line:3799
        O0OO000O0OO000O00 = '/'  #line:3800
        OO00OOO0000OO0OOO = None  #line:3801
        OO00OO0000OO0O000 = 1000  #line:3802
        O00O0O00000000OOO = main().get_path(get.path)  #line:3803
        OOOOOO0O0000OO000, O00000O0O00O00000, OO0OO0OOO0OOO0O0O = OO0O0OOOOO0OO000O.list(
            O000OO0O0O0OOO00O.__O00000000OOOOO000, O00O0O00000000OOO,
            OO00OOO0000OO0OOO, OO00OO0000OO0O000,
            O0OO000O0OO000O00)  #line:3805
        OOOOOOO0O0000OOOO = []  #line:3806
        if OOOOOO0O0000OO000:  #line:3807
            O00000000OOO0O000 = OOOOOO0O0000OO000.get(
                "commonPrefixes")  #line:3808
            if O00000000OOO0O000:  #line:3809
                for O000000OOO0OOOO00 in O00000000OOO0O000:  #line:3810
                    O0O00O0O00O0O0OO0 = {}  #line:3811
                    OOO0OOOO0O000000O = O000000OOO0OOOO00.replace(
                        O00O0O00000000OOO, '')  #line:3812
                    O0O00O0O00O0O0OO0['name'] = OOO0OOOO0O000000O  #line:3813
                    O0O00O0O00O0O0OO0['type'] = None  #line:3814
                    OOOOOOO0O0000OOOO.append(O0O00O0O00O0O0OO0)  #line:3815
            OOO0OOOOOOOOO0O00 = OOOOOO0O0000OO000['items']  #line:3817
            for OOO0OO000OOO0OO0O in OOO0OOOOOOOOO0O00:  #line:3818
                O0O00O0O00O0O0OO0 = {}  #line:3819
                OOO0OOOO0O000000O = OOO0OO000OOO0OO0O.get("key")  #line:3820
                OOO0OOOO0O000000O = OOO0OOOO0O000000O.replace(
                    O00O0O00000000OOO, '')  #line:3821
                if not OOO0OOOO0O000000O:  #line:3822
                    continue  #line:3823
                O0O00O0O00O0O0OO0['name'] = OOO0OOOO0O000000O  #line:3824
                O0O00O0O00O0O0OO0['size'] = OOO0OO000OOO0OO0O.get(
                    "fsize")  #line:3825
                O0O00O0O00O0O0OO0['type'] = OOO0OO000OOO0OO0O.get(
                    "type")  #line:3826
                O0O00O0O00O0O0OO0['time'] = OOO0OO000OOO0OO0O.get(
                    "putTime")  #line:3827
                O0O00O0O00O0O0OO0[
                    'download'] = O000OO0O0O0OOO00O.generate_download_url(
                        O00O0O00000000OOO + OOO0OOOO0O000000O)  #line:3828
                OOOOOOO0O0000OOOO.append(O0O00O0O00O0O0OO0)  #line:3829
        else:  #line:3830
            if hasattr(OO0OO0OOO0OOO0O0O, "error"):  #line:3831
                raise RuntimeError(OO0OO0OOO0OOO0O0O.error)  #line:3832
        O000OO0O0OOO0OOOO = {
            'path': O00O0O00000000OOO,
            'list': OOOOOOO0O0000OOOO
        }  #line:3833
        return O000OO0O0OOO0OOOO  #line:3834

    def generate_download_url(OOOO000OO000OO000,
                              OOOO0000OO0000O00,
                              expires=60 * 60):  #line:3836
        ""  #line:3837
        OOO0000O0000OOOO0 = OOOO000OO000OO000.__OO0OO00OO0OO0O0O0  #line:3838
        OOO0OO0OO0OOOOOOO = 'http://%s/%s' % (
            OOO0000O0000OOOO0, OOOO0000OO0000O00)  #line:3839
        O00O0O0O0OO000000 = OOOO000OO000OO000.__O00O000OOOOOOO0OO.private_download_url(
            OOO0OO0OO0OOOOOOO, expires=expires)  #line:3841
        return O00O0O0O0OO000000  #line:3842

    def resumable_upload(OOO0000OOOO0OOO0O,
                         OOOOO0O0O0O00OOOO,
                         O00O0OO00OOOOOOOO,
                         object_name=None,
                         progress_callback=None,
                         progress_file_name=None,
                         retries=5):  #line:3850
        ""  #line:3859
        try:  #line:3861
            from qiniu import put_file, etag  #line:3862
            O0OO0OO0O00O00OO0 = 60 * 60  #line:3863
            if object_name is None:  #line:3864
                OOO0OO0OO00O000O0, OOOO000OO00OO0O00 = os.path.split(
                    OOOOO0O0O0O00OOOO)  #line:3865
                OOO0000OOOO0OOO0O.__OOOO00O000000O00O = main().get_path(
                    os.path.dirname(O00O0OO00OOOOOOOO))  #line:3867
                OOOO000OO00OO0O00 = OOO0000OOOO0OOO0O.__OOOO00O000000O00O + '/' + OOOO000OO00OO0O00  #line:3868
                OOOO000OO00OO0O00 = OOOO000OO00OO0O00.replace('//',
                                                              '/')  #line:3869
                object_name = OOOO000OO00OO0O00  #line:3870
            OOOOO0O0OO0OO000O = OOO0000OOOO0OOO0O.__O00O000OOOOOOO0OO.upload_token(
                OOO0000OOOO0OOO0O.__O00000000OOOOO000, object_name,
                O0OO0OO0O00O00OO0)  #line:3872
            if object_name[:1] == "/":  #line:3874
                object_name = object_name[1:]  #line:3875
            print("|-正在上传{}到七牛云存储".format(object_name), end='')  #line:3877
            OO00OOO00O0O0OOOO, O000O0O000OOO00O0 = put_file(
                OOOOO0O0OO0OO000O,
                object_name,
                OOOOO0O0O0O00OOOO,
                check_crc=True,
                progress_handler=progress_callback,
                bucket_name=OOO0000OOOO0OOO0O.__O00000000OOOOO000,
                part_size=1024 * 1024 * 4,
                version="v2")  #line:3885
            O00OO0OO0O00O0O00 = False  #line:3886
            if sys.version_info[0] == 2:  #line:3887
                O00OO0OO0O00O0O00 = OO00OOO00O0O0OOOO['key'].encode(
                    'utf-8') == object_name  #line:3888
            elif sys.version_info[0] == 3:  #line:3889
                O00OO0OO0O00O0O00 = OO00OOO00O0O0OOOO[
                    'key'] == object_name  #line:3890
            if O00OO0OO0O00O0O00:  #line:3891
                print(' ==> 成功')  #line:3892
                return OO00OOO00O0O0OOOO['hash'] == etag(
                    OOOOO0O0O0O00OOOO)  #line:3893
            return False  #line:3894
        except Exception as OOOO0O00OOO0OOO0O:  #line:3895
            print("文件上传出现错误：", str(OOOO0O00OOO0OOO0O))  #line:3896
        if retries > 0:  #line:3899
            print("重试上传文件....")  #line:3900
            return OOO0000OOOO0OOO0O.resumable_upload(
                OOOOO0O0O0O00OOOO,
                O00O0OO00OOOOOOOO,
                object_name=object_name,
                progress_callback=progress_callback,
                progress_file_name=progress_file_name,
                retries=retries - 1,
            )  #line:3908
        return False  #line:3909

    def upload_file_by_path(O0O0OOOOOO0OOO000, OO00000OOOOOOO000,
                            O0OOO0O00OOOOOO00):  #line:3912
        return O0O0OOOOOO0OOO000.resumable_upload(
            OO00000OOOOOOO000, O0OOO0O00OOOOOO00)  #line:3913

    def delete_object_by_os(OOOOO000OOOOO0OO0, O0O0O00O00OOOO0OO):  #line:3915
        ""  #line:3916
        O000O0OOO00O00OO0 = OOOOO000OOOOO0OO0.get_bucket()  #line:3918
        O0OO0OO0OOOO000OO, O0OO0O000000O00O0 = O000O0OOO00O00OO0.delete(
            OOOOO000OOOOO0OO0.__O00000000OOOOO000,
            O0O0O00O00OOOO0OO)  #line:3919
        return O0OO0OO0OOOO000OO == {}  #line:3920

    def get_object_info(OOO00OO00O000O0O0, O0O000O00000OO000):  #line:3922
        ""  #line:3923
        try:  #line:3924
            OOOO0OO0O0OO00O0O = OOO00OO00O000O0O0.get_bucket()  #line:3925
            OOOOOOOOOOOO00O00 = OOOO0OO0O0OO00O0O.stat(
                OOO00OO00O000O0O0.__O00000000OOOOO000,
                O0O000O00000OO000)  #line:3926
            return OOOOOOOOOOOO00O00[0]  #line:3927
        except:  #line:3928
            return None  #line:3929

    def remove_file(O0000OOO0OOOOO00O, OOOOOOO0OOO00OO0O):  #line:3932
        try:  #line:3933
            OOOO000OOO0OO00OO = OOOOOOO0OOO00OO0O.filename  #line:3934
            OOOOO000OOO0O00O0 = OOOOOOO0OOO00OO0O.path  #line:3935
            if OOOOO000OOO0O00O0[-1] != "/":  #line:3937
                OO0O0OO000OOO0000 = OOOOO000OOO0O00O0 + "/" + OOOO000OOO0OO00OO  #line:3938
            else:  #line:3939
                OO0O0OO000OOO0000 = OOOOO000OOO0O00O0 + OOOO000OOO0OO00OO  #line:3940
            if OO0O0OO000OOO0000[-1] == "/":  #line:3942
                return public.returnMsg(False, "暂时不支持目录删除！")  #line:3943
            if OO0O0OO000OOO0000[:1] == "/":  #line:3945
                OO0O0OO000OOO0000 = OO0O0OO000OOO0000[1:]  #line:3946
            if O0000OOO0OOOOO00O.delete_object_by_os(
                    OO0O0OO000OOO0000):  #line:3948
                return public.returnMsg(True, '删除成功')  #line:3949
            return public.returnMsg(False, '文件{}删除失败, path:{}'.format(
                OO0O0OO000OOO0000, OOOOOOO0OOO00OO0O.path))  #line:3951
        except:  #line:3952
            print(O0000OOO0OOOOO00O.__OO0O00OO0OO00O00O)  #line:3953
            return False  #line:3954


class aws_main:  #line:3958
    pass  #line:3959


class upyun_main:  #line:3963
    pass  #line:3964


class obs_main:  #line:3968
    __OOOO0OO00O0O00OO0 = None  #line:3969
    __O0OO000OOO0OOOOO0 = None  #line:3970
    __O0O0OO0OOO0OOOOOO = 0  #line:3971
    __O000O0OO0O000OOOO = None  #line:3972
    __OO0OO0000OO0000O0 = None  #line:3973
    __OOO00O00OOO0OOO0O = None  #line:3974
    __O0000OOOO000O0OOO = None  #line:3975
    __OO0OO0O0OO0OOO00O = "ERROR: 无法连接华为云OBS !"  #line:3976

    def __init__(O00O0O0000O0000O0):  #line:3978
        O00O0O0000O0000O0.__OO00OOO00O00O00O0()  #line:3979

    def __OO00OOO00O00O00O0(OO0O00OO0O0OOOO00):  #line:3981
        ""  #line:3984
        if OO0O00OO0O0OOOO00.__OOOO0OO00O0O00OO0: return  #line:3985
        O00OOOOOO0OO0000O = OO0O00OO0O0OOOO00.get_config()  #line:3987
        OO0O00OO0O0OOOO00.__O000O0OO0O000OOOO = O00OOOOOO0OO0000O[
            0]  #line:3988
        OO0O00OO0O0OOOO00.__OO0OO0000OO0000O0 = O00OOOOOO0OO0000O[
            1]  #line:3989
        OO0O00OO0O0OOOO00.__OOO00O00OOO0OOO0O = O00OOOOOO0OO0000O[
            3]  #line:3990
        OO0O00OO0O0OOOO00.__O0000OOOO000O0OOO = O00OOOOOO0OO0000O[
            2]  #line:3991
        OO0O00OO0O0OOOO00.__O0OO000OOO0OOOOO0 = main().get_path(
            O00OOOOOO0OO0000O[4])  #line:3992
        try:  #line:3993
            from obs import ObsClient  #line:3994
            OO0O00OO0O0OOOO00.__OOOO0OO00O0O00OO0 = ObsClient(
                access_key_id=OO0O00OO0O0OOOO00.__O000O0OO0O000OOOO,
                secret_access_key=OO0O00OO0O0OOOO00.__OO0OO0000OO0000O0,
                server=OO0O00OO0O0OOOO00.__O0000OOOO000O0OOO,
            )  #line:3999
        except Exception as OOO00OO0O0O00O0O0:  #line:4000
            pass  #line:4001

    def get_config(O0O0O0OO00OO0O00O, get=None):  #line:4004
        ""  #line:4007
        return main().get_config('obs')  #line:4008

    def check_config(OO000OOO0O000O0O0):  #line:4011
        try:  #line:4012
            OO0000000OOOOO000 = []  #line:4013
            O0O0000OO0O00OO0O = main().get_path('/')  #line:4014
            O000O0OOOO0OOO0OO = OO000OOO0O000O0O0.__OOOO0OO00O0O00OO0.listObjects(
                OO000OOO0O000O0O0.__OOO00O00OOO0OOO0O,
                prefix=O0O0000OO0O00OO0O,
            )  #line:4018
            for OO00OOOOO0OO000O0 in O000O0OOOO0OOO0OO.body.contents:  #line:4020
                if OO00OOOOO0OO000O0.size != 0:  #line:4021
                    if not OO00OOOOO0OO000O0.key: continue  #line:4022
                    OO0OOO0OOOO00OOO0 = {}  #line:4023
                    OO000000OO0OOO000 = OO00OOOOO0OO000O0.key  #line:4024
                    OO000000OO0OOO000 = OO000000OO0OOO000[
                        OO000000OO0OOO000.find(O0O0000OO0O00OO0O) +
                        len(O0O0000OO0O00OO0O):]  #line:4025
                    OO0OO0OO0OOO0OOOO = OO00OOOOO0OO000O0.key.split(
                        '/')  #line:4026
                    if len(OO0OO0OO0OOO0OOOO) > 1000000: continue  #line:4027
                    O00OO00OO0OOO0O0O = re.compile(r'/')  #line:4028
                    if O00OO00OO0OOO0O0O.search(OO000000OO0OOO000) != None:
                        continue  #line:4029
                    OO0OOO0OOOO00OOO0["type"] = True  #line:4030
                    OO0OOO0OOOO00OOO0["name"] = OO000000OO0OOO000  #line:4031
                    OO0OOO0OOOO00OOO0[
                        'size'] = OO00OOOOO0OO000O0.size  #line:4032
                    OOOOO000000OO0000 = OO00OOOOO0OO000O0.lastModified  #line:4033
                    OO000OOOO0000O0OO = datetime.datetime.strptime(
                        OOOOO000000OO0000, "%Y/%m/%d %H:%M:%S")  #line:4034
                    OO000OOOO0000O0OO += datetime.timedelta(
                        hours=0)  #line:4035
                    O0O0O0OOOO00O0OO0 = int((
                        time.mktime(OO000OOOO0000O0OO.timetuple()) +
                        OO000OOOO0000O0OO.microsecond / 1000000.0))  #line:4037
                    OO0OOO0OOOO00OOO0['time'] = O0O0O0OOOO00O0OO0  #line:4038
                    OO0000000OOOOO000.append(OO0OOO0OOOO00OOO0)  #line:4039
                elif OO00OOOOO0OO000O0.size == 0:  #line:4040
                    if not OO00OOOOO0OO000O0.key: continue  #line:4041
                    if OO00OOOOO0OO000O0.key[-1] != "/": continue  #line:4042
                    OO0OO0OO0OOO0OOOO = OO00OOOOO0OO000O0.key.split(
                        '/')  #line:4043
                    OO0OOO0OOOO00OOO0 = {}  #line:4044
                    OO000000OO0OOO000 = OO00OOOOO0OO000O0.key  #line:4045
                    OO000000OO0OOO000 = OO000000OO0OOO000[
                        OO000000OO0OOO000.find(O0O0000OO0O00OO0O) +
                        len(O0O0000OO0O00OO0O):]  #line:4046
                    if O0O0000OO0O00OO0O == "" and len(OO0OO0OO0OOO0OOOO) > 2:
                        continue  #line:4047
                    if O0O0000OO0O00OO0O != "":  #line:4048
                        OO0OO0OO0OOO0OOOO = OO000000OO0OOO000.split(
                            '/')  #line:4049
                        if len(OO0OO0OO0OOO0OOOO) > 2: continue  #line:4050
                        else:  #line:4051
                            OO000000OO0OOO000 = OO000000OO0OOO000  #line:4052
                    if not OO000000OO0OOO000: continue  #line:4053
                    OO0OOO0OOOO00OOO0["type"] = None  #line:4054
                    OO0OOO0OOOO00OOO0["name"] = OO000000OO0OOO000  #line:4055
                    OO0OOO0OOOO00OOO0[
                        'size'] = OO00OOOOO0OO000O0.size  #line:4056
                    OO0000000OOOOO000.append(OO0OOO0OOOO00OOO0)  #line:4057
            return True  #line:4058
        except:  #line:4059
            return False  #line:4060

    def upload_file_by_path(OOOO0OOO000O0O0OO, OOOOO00OOOOOO0O0O,
                            O00O0OOO0OO0O00OO):  #line:4062
        ""  #line:4067
        OOOO0OOO000O0O0OO.__OO00OOO00O00O00O0()  #line:4069
        if not OOOO0OOO000O0O0OO.__OOOO0OO00O0O00OO0:  #line:4070
            return False  #line:4071
        if O00O0OOO0OO0O00OO != None:  #line:4073
            OOOO00O000OOOOOOO = OOOO0OOO000O0O0OO.__OOOO0OO00O0O00OO0.listObjects(
                OOOO0OOO000O0O0OO.__OOO00O00OOO0OOO0O,
                prefix="",
            )  #line:4077
            O0OO0O000O000O0O0 = O00O0OOO0OO0O00OO.split("/")  #line:4078
            OOO00O0OO0OO0O0O0 = ""  #line:4079
            OO00OO0O0O0OO0000 = []  #line:4080
            for OOO0O0000O0OO0O00 in OOOO00O000OOOOOOO.body.contents:  #line:4081
                if not OOO0O0000O0OO0O00.key: continue  #line:4082
                OO00OO0O0O0OO0000.append(OOO0O0000O0OO0O00.key)  #line:4083
            for O0O00O00OO0000O0O in range(
                    0, (len(O0OO0O000O000O0O0) - 1)):  #line:4084
                if OOO00O0OO0OO0O0O0 == "":  #line:4085
                    OOO00O0OO0OO0O0O0 = O0OO0O000O000O0O0[
                        O0O00O00OO0000O0O] + "/"  #line:4086
                else:  #line:4087
                    OOO00O0OO0OO0O0O0 = OOO00O0OO0OO0O0O0 + O0OO0O000O000O0O0[
                        O0O00O00OO0000O0O] + "/"  #line:4088
                if not OOO00O0OO0OO0O0O0: continue  #line:4089
                if main().get_path(OOO00O0OO0OO0O0O0
                                   ) not in OO00OO0O0O0OO0000:  #line:4090
                    OOOO00O000OOOOOOO = OOOO0OOO000O0O0OO.__OOOO0OO00O0O00OO0.putContent(
                        OOOO0OOO000O0O0OO.__OOO00O00OOO0OOO0O,
                        objectKey=main().get_path(OOO00O0OO0OO0O0O0),
                    )  #line:4094
        try:  #line:4096
            print('|-正在上传{}到华为云存储'.format(OOOOO00OOOOOO0O0O),
                  end='')  #line:4097
            O000OO0OO0O00OOO0, OOO0OOOO000OO000O = os.path.split(
                OOOOO00OOOOOO0O0O)  #line:4098
            OOOO0OOO000O0O0OO.__O0OO000OOO0OOOOO0 = main().get_path(
                os.path.dirname(O00O0OOO0OO0O00OO))  #line:4099
            OOO0OOOO000OO000O = OOOO0OOO000O0O0OO.__O0OO000OOO0OOOOO0 + OOO0OOOO000OO000O  #line:4100
            OOOO0O0OO00O0O000 = 5 * 1024 * 1024  #line:4101
            OO0O0OO0O0OO00OOO = OOOOO00OOOOOO0O0O  #line:4102
            OO0OO0O0OO0OOO000 = OOO0OOOO000OO000O  #line:4103
            O0OO000O000O00OO0 = True  #line:4104
            OOOO00O000OOOOOOO = OOOO0OOO000O0O0OO.__OOOO0OO00O0O00OO0.uploadFile(
                OOOO0OOO000O0O0OO.__OOO00O00OOO0OOO0O,
                OO0OO0O0OO0OOO000,
                OO0O0OO0O0OO00OOO,
                OOOO0O0OO00O0O000,
                O0OO000O000O00OO0,
            )  #line:4111
            if OOOO00O000OOOOOOO.status < 300:  #line:4112
                print(' ==> 成功')  #line:4113
                return True  #line:4114
        except Exception as OOOO00OO0OO0O0000:  #line:4115
            time.sleep(1)  #line:4117
            OOOO0OOO000O0O0OO.__O0O0OO0OOO0OOOOOO += 1  #line:4118
            if OOOO0OOO000O0O0OO.__O0O0OO0OOO0OOOOOO < 2:  #line:4119
                OOOO0OOO000O0O0OO.upload_file_by_path(
                    OOOOO00OOOOOO0O0O, O00O0OOO0OO0O00OO)  #line:4121
            return False  #line:4122

    def get_list(O00OO0OOOO0OO0OO0, get=None):  #line:4124
        ""  #line:4127
        O00OO0OOOO0OO0OO0.__OO00OOO00O00O00O0()  #line:4129
        if not O00OO0OOOO0OO0OO0.__OOOO0OO00O0O00OO0:  #line:4130
            return False  #line:4131
        O0OOO000O0O0OOOOO = []  #line:4132
        O0000OOOO00000OO0 = main().get_path(get.path)  #line:4133
        O000OO0OO00OO000O = O00OO0OOOO0OO0OO0.__OOOO0OO00O0O00OO0.listObjects(
            O00OO0OOOO0OO0OO0.__OOO00O00OOO0OOO0O,
            prefix=O0000OOOO00000OO0,
        )  #line:4137
        for O00OOOOOO0OOOOOO0 in O000OO0OO00OO000O.body.contents:  #line:4139
            if O00OOOOOO0OOOOOO0.size != 0:  #line:4140
                if not O00OOOOOO0OOOOOO0.key: continue  #line:4141
                O0OOOOO00OO00OO0O = {}  #line:4142
                O000000O0OOO00OOO = O00OOOOOO0OOOOOO0.key  #line:4143
                O000000O0OOO00OOO = O000000O0OOO00OOO[
                    O000000O0OOO00OOO.find(O0000OOOO00000OO0) +
                    len(O0000OOOO00000OO0):]  #line:4144
                OO00O0O0OOOOO0OO0 = O00OOOOOO0OOOOOO0.key.split(
                    '/')  #line:4145
                if len(OO00O0O0OOOOO0OO0) > 1000000: continue  #line:4146
                OOOOO0O00OOO0OO0O = re.compile(r'/')  #line:4147
                if OOOOO0O00OOO0OO0O.search(O000000O0OOO00OOO) != None:
                    continue  #line:4148
                O0OOOOO00OO00OO0O["type"] = True  #line:4149
                O0OOOOO00OO00OO0O["name"] = O000000O0OOO00OOO  #line:4150
                O0OOOOO00OO00OO0O['size'] = O00OOOOOO0OOOOOO0.size  #line:4151
                O0OOOOO00OO00OO0O[
                    'download'] = O00OO0OOOO0OO0OO0.download_file(
                        O0000OOOO00000OO0 + O000000O0OOO00OOO)  #line:4152
                OOOO000OO0O0OO0OO = O00OOOOOO0OOOOOO0.lastModified  #line:4153
                OO00O0O000000OO0O = datetime.datetime.strptime(
                    OOOO000OO0O0OO0OO, "%Y/%m/%d %H:%M:%S")  #line:4154
                OO00O0O000000OO0O += datetime.timedelta(hours=0)  #line:4155
                OOOO0O000OOOO000O = int(
                    (time.mktime(OO00O0O000000OO0O.timetuple()) +
                     OO00O0O000000OO0O.microsecond / 1000000.0))  #line:4157
                O0OOOOO00OO00OO0O['time'] = OOOO0O000OOOO000O  #line:4158
                O0OOO000O0O0OOOOO.append(O0OOOOO00OO00OO0O)  #line:4159
            elif O00OOOOOO0OOOOOO0.size == 0:  #line:4160
                if not O00OOOOOO0OOOOOO0.key: continue  #line:4161
                if O00OOOOOO0OOOOOO0.key[-1] != "/": continue  #line:4162
                OO00O0O0OOOOO0OO0 = O00OOOOOO0OOOOOO0.key.split(
                    '/')  #line:4163
                O0OOOOO00OO00OO0O = {}  #line:4164
                O000000O0OOO00OOO = O00OOOOOO0OOOOOO0.key  #line:4165
                O000000O0OOO00OOO = O000000O0OOO00OOO[
                    O000000O0OOO00OOO.find(O0000OOOO00000OO0) +
                    len(O0000OOOO00000OO0):]  #line:4166
                if O0000OOOO00000OO0 == "" and len(OO00O0O0OOOOO0OO0) > 2:
                    continue  #line:4167
                if O0000OOOO00000OO0 != "":  #line:4168
                    OO00O0O0OOOOO0OO0 = O000000O0OOO00OOO.split(
                        '/')  #line:4169
                    if len(OO00O0O0OOOOO0OO0) > 2: continue  #line:4170
                    else:  #line:4171
                        O000000O0OOO00OOO = O000000O0OOO00OOO  #line:4172
                if not O000000O0OOO00OOO: continue  #line:4173
                O0OOOOO00OO00OO0O["type"] = None  #line:4174
                O0OOOOO00OO00OO0O["name"] = O000000O0OOO00OOO  #line:4175
                O0OOOOO00OO00OO0O['size'] = O00OOOOOO0OOOOOO0.size  #line:4176
                O0OOO000O0O0OOOOO.append(O0OOOOO00OO00OO0O)  #line:4177
        O00O000O0O0O0000O = {
            'path': O0000OOOO00000OO0,
            'list': O0OOO000O0O0OOOOO
        }  #line:4179
        return O00O000O0O0O0000O  #line:4180

    def download_file(OO0O0O0O00O0O0OO0, O00OO0000OO0OOOOO):  #line:4182
        ""  #line:4185
        OO0O0O0O00O0O0OO0.__OO00OOO00O00O00O0()  #line:4187
        if not OO0O0O0O00O0O0OO0.__OOOO0OO00O0O00OO0:  #line:4188
            return None  #line:4189
        try:  #line:4190
            O0OOOO0O0OO00OOOO = OO0O0O0O00O0O0OO0.__OOOO0OO00O0O00OO0.createSignedUrl(
                'GET',
                OO0O0O0O00O0O0OO0.__OOO00O00OOO0OOO0O,
                O00OO0000OO0OOOOO,
                expires=3600,
            )  #line:4196
            O00O00OO00O00O0OO = O0OOOO0O0OO00OOOO.signedUrl  #line:4197
            return O00O00OO00O00O0OO  #line:4198
        except:  #line:4199
            print(OO0O0O0O00O0O0OO0.__OO0OO0O0OO0OOO00O)  #line:4200
            return None  #line:4201

    def delete_file(O00O0OO0O000OOOO0, O0O0OOOOOO0OO000O):  #line:4203
        ""  #line:4207
        O00O0OO0O000OOOO0.__OO00OOO00O00O00O0()  #line:4209
        if not O00O0OO0O000OOOO0.__OOOO0OO00O0O00OO0:  #line:4210
            return False  #line:4211
        try:  #line:4213
            OO0OO0O0000OO0O0O = O00O0OO0O000OOOO0.__OOOO0OO00O0O00OO0.deleteObject(
                O00O0OO0O000OOOO0.__OOO00O00OOO0OOO0O,
                O0O0OOOOOO0OO000O)  #line:4214
            return OO0OO0O0000OO0O0O  #line:4215
        except Exception as OOOO0OO0OOOOOO00O:  #line:4216
            O00O0OO0O000OOOO0.__O0O0OO0OOO0OOOOOO += 1  #line:4217
            if O00O0OO0O000OOOO0.__O0O0OO0OOO0OOOOOO < 2:  #line:4218
                O00O0OO0O000OOOO0.delete_file(O0O0OOOOOO0OO000O)  #line:4220
            print(O00O0OO0O000OOOO0.__OO0OO0O0OO0OOO00O)  #line:4221
            return None  #line:4222

    def remove_file(OOOO00OO00OOOO00O, OOOO0OO0OO000000O):  #line:4225
        OO0000OOO0O00O0O0 = main().get_path(OOOO0OO0OO000000O.path)  #line:4226
        O0O000000OO0O0000 = OO0000OOO0O00O0O0 + OOOO0OO0OO000000O.filename  #line:4227
        OOOO00OO00OOOO00O.delete_file(O0O000000OO0O0000)  #line:4228
        return public.returnMsg(True, '删除文件成功!')  #line:4229


class bos_main:  #line:4233
    __O00O0OOO000O0000O = None  #line:4234
    __OO000O00OO0O0000O = 0  #line:4235
    __OOO0OO00OOOOOO000 = None  #line:4236
    __O00OOOOO0O00O00OO = None  #line:4237
    __O0OOO0O0OO0O000O0 = None  #line:4238
    __OO000O000O0O0OOOO = "ERROR: 无法连接百度云存储 !"  #line:4239

    def __init__(O00O00O00OO00OOOO):  #line:4241
        O00O00O00OO00OOOO.__OOOOOOO0O00O00OOO()  #line:4242

    def __OOOOOOO0O00O00OOO(OOO0O0OOOO0O0O000):  #line:4244
        ""  #line:4247
        if OOO0O0OOOO0O0O000.__O00O0OOO000O0000O: return  #line:4248
        O0OO0OOOOO0OOO0OO = OOO0O0OOOO0O0O000.get_config()  #line:4250
        OOO0O0OOOO0O0O000.__OOO0OO00OOOOOO000 = O0OO0OOOOO0OOO0OO[
            0]  #line:4251
        OOO0O0OOOO0O0O000.__O00OOOOO0O00O00OO = O0OO0OOOOO0OOO0OO[
            1]  #line:4252
        OOO0O0OOOO0O0O000.__O0OO0OOO00OO0O00O = O0OO0OOOOO0OOO0OO[
            3]  #line:4253
        OOO0O0OOOO0O0O000.__O0OOO0O0OO0O000O0 = O0OO0OOOOO0OOO0OO[
            2]  #line:4254
        OOO0O0OOOO0O0O000.__O0OOOOO0O00000OO0 = main().get_path(
            O0OO0OOOOO0OOO0OO[4])  #line:4256
        try:  #line:4257
            from baidubce.bce_client_configuration import BceClientConfiguration  #line:4258
            from baidubce.auth.bce_credentials import BceCredentials  #line:4259
            from baidubce.services.bos.bos_client import BosClient  #line:4260
            OOO0OOOO0O000OOOO = BceClientConfiguration(
                credentials=BceCredentials(
                    OOO0O0OOOO0O0O000.__OOO0OO00OOOOOO000,
                    OOO0O0OOOO0O0O000.__O00OOOOO0O00O00OO),
                endpoint=OOO0O0OOOO0O0O000.__O0OOO0O0OO0O000O0)  #line:4263
            OOO0O0OOOO0O0O000.__O00O0OOO000O0000O = BosClient(
                OOO0OOOO0O000OOOO)  #line:4264
        except Exception as OO0OO0O000O000000:  #line:4265
            pass  #line:4266

    def get_config(O00OO00OO000000OO, get=None):  #line:4269
        ""  #line:4272
        return main().get_config('bos')  #line:4273

    def check_config(OO0O00000000O0O0O):  #line:4275
        ""  #line:4278
        if not OO0O00000000O0O0O.__O00O0OOO000O0000O: return False  #line:4279
        try:  #line:4280
            OO0OOO0O0OO00O00O = '/'  #line:4281
            O0000O0000OO0OO00 = OO0O00000000O0O0O.__O00O0OOO000O0000O.list_objects(
                OO0O00000000O0O0O.__O0OO0OOO00OO0O00O,
                prefix=OO0OOO0O0OO00O00O,
                delimiter="/")  #line:4284
            return True  #line:4285
        except:  #line:4286
            return False  #line:4287

    def resumable_upload(
        O00OOO0O0000000OO,
        OOOO00O0O0000O00O,
        object_name=None,
        progress_callback=None,
        progress_file_name=None,
        retries=5,
    ):  #line:4296
        ""  #line:4303
        try:  #line:4305
            if object_name[:1] == "/":  #line:4306
                object_name = object_name[1:]  #line:4307
            print("|-正在上传{}到百度云存储".format(object_name), end='')  #line:4308
            import multiprocessing  #line:4309
            O000OO0OO00000000 = OOOO00O0O0000O00O  #line:4310
            OOO0O00000000OOOO = object_name  #line:4311
            OOO00O00O0OOO000O = O00OOO0O0000000OO.__O0OO0OOO00OO0O00O  #line:4312
            O0O00OO0OOO000000 = O00OOO0O0000000OO.__O00O0OOO000O0000O.put_super_obejct_from_file(
                OOO00O00O0OOO000O,
                OOO0O00000000OOOO,
                O000OO0OO00000000,
                chunk_size=5,
                thread_num=multiprocessing.cpu_count() - 1)  #line:4318
            if O0O00OO0OOO000000:  #line:4319
                print(' ==> 成功')  #line:4320
                return True  #line:4321
        except Exception as OOO0OOO00O0OOO0OO:  #line:4322
            print("文件上传出现错误：")  #line:4323
            print(OOO0OOO00O0OOO0OO)  #line:4324
        if retries > 0:  #line:4327
            print("重试上传文件....")  #line:4328
            return O00OOO0O0000000OO.resumable_upload(
                OOOO00O0O0000O00O,
                object_name=object_name,
                progress_callback=progress_callback,
                progress_file_name=progress_file_name,
                retries=retries - 1,
            )  #line:4335
        return False  #line:4336

    def upload_file_by_path(OO0OOOO00OOOO00O0, OOOOO0OO0OO0O0000,
                            O0O0OO0O00O0OOOOO):  #line:4338
        ""  #line:4341
        return OO0OOOO00OOOO00O0.resumable_upload(
            OOOOO0OO0OO0O0000, O0O0OO0O00O0OOOOO)  #line:4342

    def get_list(O0OOO0O00OOOOO000, get=None):  #line:4344
        O0000000000OO0OO0 = []  #line:4345
        OOO0O0OOOO00OO0OO = []  #line:4346
        OOOO00OO00O0OO0OO = main().get_path(get.path)  #line:4347
        try:  #line:4348
            OO00OO0000O0O0OOO = O0OOO0O00OOOOO000.__O00O0OOO000O0000O.list_objects(
                O0OOO0O00OOOOO000.__O0OO0OOO00OO0O00O,
                prefix=OOOO00OO00O0OO0OO,
                delimiter="/")  #line:4351
            for OO0OOO0OO0OOOOO0O in OO00OO0000O0O0OOO.contents:  #line:4352
                if not OO0OOO0OO0OOOOO0O.key: continue  #line:4353
                OOO00O00O00OOO0OO = {}  #line:4354
                O0O0O0O0OO00OO000 = OO0OOO0OO0OOOOO0O.key  #line:4355
                O0O0O0O0OO00OO000 = O0O0O0O0OO00OO000[
                    O0O0O0O0OO00OO000.find(OOOO00OO00O0OO0OO) +
                    len(OOOO00OO00O0OO0OO):]  #line:4356
                if not O0O0O0O0OO00OO000: continue  #line:4357
                OOO00O00O00OOO0OO["name"] = O0O0O0O0OO00OO000  #line:4358
                OOO00O00O00OOO0OO['size'] = OO0OOO0OO0OOOOO0O.size  #line:4359
                OOO00O00O00OOO0OO["type"] = True  #line:4360
                OOO00O00O00OOO0OO[
                    'download'] = O0OOO0O00OOOOO000.download_file(
                        OOOO00OO00O0OO0OO + "/" +
                        O0O0O0O0OO00OO000)  #line:4361
                O0O0000000O00OOOO = OO0OOO0OO0OOOOO0O.last_modified  #line:4362
                OO00000O00O0O0O00 = datetime.datetime.strptime(
                    O0O0000000O00OOOO, "%Y-%m-%dT%H:%M:%SZ")  #line:4363
                OO00000O00O0O0O00 += datetime.timedelta(hours=8)  #line:4364
                O0O00OOO000OO00O0 = int(
                    (time.mktime(OO00000O00O0O0O00.timetuple()) +
                     OO00000O00O0O0O00.microsecond / 1000000.0))  #line:4366
                OOO00O00O00OOO0OO['time'] = O0O00OOO000OO00O0  #line:4367
                O0000000000OO0OO0.append(OOO00O00O00OOO0OO)  #line:4368
            for OOO000OO000OOO000 in OO00OO0000O0O0OOO.common_prefixes:  #line:4369
                if not OOO000OO000OOO000.prefix: continue  #line:4370
                if OOO000OO000OOO000.prefix[0:-1] == OOOO00OO00O0OO0OO:
                    continue  #line:4371
                OOO00O00O00OOO0OO = {}  #line:4372
                OOO000OO000OOO000.prefix = OOO000OO000OOO000.prefix.replace(
                    OOOO00OO00O0OO0OO, '')  #line:4373
                OOO00O00O00OOO0OO[
                    "name"] = OOO000OO000OOO000.prefix  #line:4374
                OOO00O00O00OOO0OO["type"] = None  #line:4375
                OOO00O00O00OOO0OO['size'] = OOO000OO000OOO000.size  #line:4376
                O0000000000OO0OO0.append(OOO00O00O00OOO0OO)  #line:4377
            O00OO0OOO0OO0OO0O = {
                'path': OOOO00OO00O0OO0OO,
                'list': O0000000000OO0OO0
            }  #line:4378
            return O00OO0OOO0OO0OO0O  #line:4379
        except:  #line:4380
            O00OO0OOO0OO0OO0O = {}  #line:4381
            if O0OOO0O00OOOOO000.__O00O0OOO000O0000O:  #line:4382
                O00OO0OOO0OO0OO0O['status'] = True  #line:4383
            else:  #line:4384
                O00OO0OOO0OO0OO0O['status'] = False  #line:4385
            O00OO0OOO0OO0OO0O['path'] = get.path  #line:4386
            O00OO0OOO0OO0OO0O['list'] = O0000000000OO0OO0  #line:4387
            O00OO0OOO0OO0OO0O['dir'] = OOO0O0OOOO00OO0OO  #line:4388
            return O00OO0OOO0OO0OO0O  #line:4389

    def download_file(OO0000OO0000O0000, O0OOO0OOO0O0000O0):  #line:4391
        ""  #line:4394
        OO0000OO0000O0000.__OOOOOOO0O00O00OOO()  #line:4396
        if not OO0000OO0000O0000.__O00O0OOO000O0000O:  #line:4397
            return None  #line:4398
        try:  #line:4400
            O00OO0OO0OO0OO0O0 = OO0000OO0000O0000.__O00O0OOO000O0000O.generate_pre_signed_url(
                OO0000OO0000O0000.__O0OO0OOO00OO0O00O,
                O0OOO0OOO0O0000O0)  #line:4401
            _O0OOOO0OO000O000O = sys.version_info  #line:4402
            OOOO0OO0O000O0000 = (_O0OOOO0OO000O000O[0] == 2)  #line:4404
            OOO0O0OOO00O000O0 = (_O0OOOO0OO000O000O[0] == 3)  #line:4407
            if OOO0O0OOO00O000O0:  #line:4408
                O00OO0OO0OO0OO0O0 = str(O00OO0OO0OO0OO0O0,
                                        encoding="utf-8")  #line:4409
            else:  #line:4410
                O00OO0OO0OO0OO0O0 = O00OO0OO0OO0OO0O0  #line:4411
            return O00OO0OO0OO0OO0O0  #line:4412
        except:  #line:4413
            print(OO0000OO0000O0000.__OO000O000O0O0OOOO)  #line:4414
            return None  #line:4415

    def delete_file(OOO00O0000O0OO0OO, OO0OO00OOO0OOO0OO):  #line:4417
        ""  #line:4421
        OOO00O0000O0OO0OO.__OOOOOOO0O00O00OOO()  #line:4423
        if not OOO00O0000O0OO0OO.__O00O0OOO000O0000O:  #line:4424
            return False  #line:4425
        try:  #line:4427
            OO00OOO000OOO00OO = OOO00O0000O0OO0OO.__O00O0OOO000O0000O.delete_object(
                OOO00O0000O0OO0OO.__O0OO0OOO00OO0O00O,
                OO0OO00OOO0OOO0OO)  #line:4428
            return OO00OOO000OOO00OO  #line:4429
        except Exception as OOO00000O00000OO0:  #line:4430
            OOO00O0000O0OO0OO.__OO000O00OO0O0000O += 1  #line:4431
            if OOO00O0000O0OO0OO.__OO000O00OO0O0000O < 2:  #line:4432
                OOO00O0000O0OO0OO.delete_file(OO0OO00OOO0OOO0OO)  #line:4434
            print(OOO00O0000O0OO0OO.__OO000O000O0O0OOOO)  #line:4435
            return None  #line:4436

    def remove_file(O0O0O0O00O00O00OO, O0OO00OO000O0O000):  #line:4439
        O000O0OOO000OOOOO = main().get_path(O0OO00OO000O0O000.path)  #line:4440
        O0OOO00OOOO00O0OO = O000O0OOO000OOOOO + O0OO00OO000O0O000.filename  #line:4441
        O0O0O0O00O00O00OO.delete_file(O0OOO00OOOO00O0OO)  #line:4442
        return public.returnMsg(True, '删除文件成功!')  #line:4443


class gcloud_storage_main:  #line:4447
    pass  #line:4448


class gdrive_main:  #line:4452
    pass  #line:4453


class msonedrive_main:  #line:4457
    pass  #line:4458


if __name__ == '__main__':  #line:4461
    import argparse  #line:4462
    args_obj = argparse.ArgumentParser(
        usage="必要的参数：--db_name 数据库名称!")  #line:4463
    args_obj.add_argument("--db_name", help="数据库名称!")  #line:4464
    args_obj.add_argument("--binlog_id", help="任务id")  #line:4465
    args = args_obj.parse_args()  #line:4466
    if not args.db_name:  #line:4467
        args_obj.print_help()  #line:4468
    p = main()  #line:4469
    p._db_name = args.db_name  #line:4470
    if args.binlog_id: p._binlog_id = args.binlog_id  #line:4471
    if p._binlog_id:  #line:4473
        p.execute_by_comandline()  #line:4474
