#coding: utf-8
#-------------------------------------------------------------------
# 宝塔Linux面板
#-------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http:#bt.cn) All rights reserved.
#-------------------------------------------------------------------
# Author: hezhihong <bt_ahong@qq.com>
#-------------------------------------------------------------------

#------------------------------
# MySQL二进制日志备份
#------------------------------
import os,sys,time,json,re,datetime,shutil,threading
os.chdir('/www/server/panel')
sys.path.append("class/")
import public
from projectModel.base import projectBase
from panelMysql import panelMysql
from panelBackup import backup
import db_mysql
try:
    import oss2
except:pass
try:
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
except:pass
try:
    from qiniu import Auth, put_file, etag
except:pass
try:
    from baidubce.bce_client_configuration import BceClientConfiguration
    from baidubce.auth.bce_credentials import BceCredentials
    from baidubce.services.bos.bos_client import BosClient
except:pass
try:
    from obs import ObsClient
except:pass
class main(projectBase):
    _setup_path = '/www/server/panel/'
    _binlog_id = ''
    _db_name =''
    _zip_password =''
    _backup_end_time =''
    _backup_start_time =''
    _backup_type =''
    _cloud_name =''
    _full_zip_name =''
    _full_file =''
    _inc_file =''
    _file= ''
    _pdata= {}
    _echo_info= {}
    _inode_min = 100
    _temp_path = './temp/'
    _tables = []
    _new_tables =[]
    _backup_fail_list =[]
    _backup_full_list =[]
    _cloud_upload_not = []
    _full_info=[]
    _inc_info=[]
    _mysql_bin_index = '/www/server/data/mysql-bin.index'
    _save_cycle = 3600
    _compress = True
    _mysqlbinlog_bin = '/www/server/mysql/bin/mysqlbinlog'
    _save_default_path = '/www/backup/mysql_bin_log/'
    _mysql_root_password = public.M('config').where('id=?',(1,)).getField('mysql_root')
    _install_path = '{}script/binlog_cloud.sh'.format(_setup_path)
    _config_path = '{}config/mysqlbinlog_info'.format(_setup_path)
    _python_path = '{}pyenv/bin/python'.format(_setup_path)
    _binlogModel_py = '{}class/projectModel/binlogModel.py'.format(_setup_path)
    _mybackup = backup()
    _plugin_path = '{}plugin/'.format(_setup_path)
    _binlog_conf = '{}config/mysqlbinlog_info/binlog.conf'.format(_setup_path)
    _start_time_list = []
    _db_mysql = db_mysql.panelMysql()
    

    def __init__(self):
        if not os.path.exists(self._save_default_path):
            os.makedirs(self._save_default_path)
        if not os.path.exists(self._temp_path):
            os.makedirs(self._temp_path)
        if not os.path.exists(self._config_path):
            os.makedirs(self._config_path)
        self.create_table()
        self.kill_process()

    def get_path(self, path):
        """
        @name 过滤路径后缀
        @param path 路径
        """
        if path == '/': path = ''
        if path[:1] == '/':
            path = path[1:]
            if path[-1:] != '/': path += '/'
        return path.replace('//', '/')

    def install_cloud_module(self):
        """
        @name 安装云存储依赖模块
        @auther hezhihong<2022-05-25>
        """
        module_list = ["oss2","cos-python-sdk-v5","qiniu","bce-python-sdk","esdk-obs-python"]
        module_list = ["oss2==2.5.0","cos-python-sdk-v5==1.7.7","qiniu==7.4.1 -I","bce-python-sdk==0.8.62","esdk-obs-python==3.21.8 --trusted-host pypi.org"]
        for module_i in module_list:
            public.ExecShell('nohup btpip install {} >/dev/null 2>&1 &'.format(module_i))
            time.sleep(1)

        

    def get_start_end_binlog(self,start_time,end_time,is_backup=None):
        """
        @name 取起始binglog压缩文件列表
        @auther hezhihong<2022-04-15>
        @param start_time 格式 如"2022-03-06 17:15:26" string
        @param end_time 格式 如"2022-03-06 17:15:26" string
        @return 文件列表
        """
        #以增量备份包时间切片获取，兼容多种时间颗粒度切片
        start_end = {}
        all_list = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
        start_end['start']=all_list[(int(start_time.split()[1].split(':')[0])):]
        if is_backup:
            start_end['end']=all_list[:(int(end_time.split()[1].split(':')[0])+1)]
        else:
            start_end['end']=all_list[:(int(end_time.split()[1].split(':')[0])+1)]
        start_end['all'] = all_list

        return start_end 


    def traverse_all_files(self,check_path,check_date_list,start_end):
        '''
        @name 遍历指定时间段内的所有文件
        @auther hezhihong<2022-04-20>
        @param check_date_list list 遍历的日期时间段
        @param start_end dict 起止包
        @return
        '''
        file_lists_data={}
        file_lists_not = []
        file_all_data = []
        for i in range(0,len(check_date_list)):
            file_path=check_path+check_date_list[i]+'/'
            is_start= False
            is_end = False
            if check_date_list[i] == check_date_list[0]:
                start_end_zip = start_end['start']
                is_start = True
            elif check_date_list[i] == check_date_list[len(check_date_list)-1]:
                start_end_zip = start_end['end']
                is_end = True
            else: 
                start_end_zip = start_end['all']
            #判断遍历日期是否只有一天
            if len(check_date_list) ==1:
                start_end_zip = sorted(list(set(start_end['end']).intersection(start_end['start'])))
                # print(start_end_zip)
                is_start = True
                is_end = True
            if start_end_zip:
                file_lists=self.splice_file_name(file_path,check_date_list[i],start_end_zip)
                if is_start:
                    file_lists_data['first']=file_lists[0]
                if is_end:
                    file_lists_data['last']=file_lists[len(file_lists)-1]
                file_all_data.append(file_lists)
                check_result = self.check_foler_file(file_lists)
                if check_result:
                    file_lists_not.append(check_result)
        file_lists_data['data'] = file_all_data
        file_lists_data['file_lists_not'] = file_lists_not
        if file_lists_not:      
            file_lists_data['status'] = 'False'
        else:
            file_lists_data['status'] = 'True'
        return file_lists_data

    def get_mysql_port(self):
        """
        @name 取mysql端口
        @return string 端口
        """
        try:
            port = panelMysql().query("show global variables like 'port'")[0][1]
            if not port:
                return 0
            else:
                return port
        except:
            return 0

    def get_info(self,file,info_list):
        """
        @name 取list指定信息
        @auther hezhihong<2022-04-29>
        @param file 文件名
        @param info_list json文件内容
        @return dict
        """
        dict_value = {}
        for full_name in info_list:
            if full_name['full_name'] == file:
                dict_value= full_name
        return dict_value
    
    def auto_download_file(self,cloud_list,local_file_name,size=1024):
        """
        @name 自动从云存储下载文件
        """

        download_url = ''
        for cloud in cloud_list:
            download_url=cloud.download_file(local_file_name.replace('/www/backup','bt_backup'))
            if download_url:self.download_big_file(local_file_name, download_url, size)
            if os.path.isfile(local_file_name):
                print('已从远程存储器下载{}'.format(local_file_name))
                break

    def download_big_file(self,local_file, url, file_size):
        """
        @name 根据下载url下载文件
        """
        error_count=0
        import requests
        try:
            # 小于100M的文件直接下载
            if int(file_size) < 1024 * 1024 * 100:
                # print('小文件下载')
                r = requests.get(url)
                with open(local_file, "wb") as f:
                    f.write(r.content)
                # print('下载成功')
            # 大于100M的文件分片下载
            else:
                r = requests.get(url, stream=True)
                with open(local_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                # print('下载成功')
        except:
            time.sleep(3)
            error_count += 1
            if error_count < 2:  # 重试2次
                # main().sync_date()
                self.download_big_file(local_file, url, file_size)
        return False


    def check_binlog_complete(self,pdata,end_time=None):
        """
        @name 检查mysql二进制日志完整性，恢复数据前置检查
        @auther hezhihong<2022-04-15>
        @param start_time 开始的binlog日志时间点 格式如'2022-04-05 17:53:06'
        @param end_time 恢复数据库到指定的截止时间点  string如'2022-04-05 17:53:06'
        @return 二进制日志文件列表和完整性状态
        """
        alioss_value,txcos_value,qiniu_value,bos_value,obs_value,ftp_value,cloud_list,cloud_not= self.check_cloud_oss(pdata)
        file_lists_data = {}
        file_not = []
        #检测全量备份记录文件
        start_time = ''
        if not os.path.isfile(self._full_file):
            #尝试从远程存储器下载
            self.auto_download_file(cloud_list,self._full_file)
        if not os.path.isfile(self._full_file):file_not.append(self._full_file)
        if file_not:
            file_lists_data['file_lists_not'] = file_not
            return file_lists_data
        #检测完全备份文件
        if os.path.isfile(self._full_file):
            try:
                self._full_info = json.loads(public.readFile(self._full_file))[0]
            except:
                self._full_info = []
        if 'full_name' in self._full_info and not os.path.isfile(self._full_info['full_name']):
            file_not.append(self._full_info['full_name'])
            file_lists_data['file_lists_not'] = file_not
            return file_lists_data
        if not self._full_info or 'time' not in self._full_info:
            return file_lists_data
        else:
            start_time = self._full_info['time']
        if start_time != end_time:
            #检测增量备份记录文件，如缺失则尝试到远程存储器下载
            if not os.path.isfile(self._inc_file):
                self.auto_download_file(cloud_list,self._inc_file)
            if not os.path.isfile(self._inc_file):file_not.append(self._inc_file)
            if file_not:
                file_lists_data['file_lists_not'] = file_not
                return file_lists_data
            if os.path.isfile(self._inc_file):
                try:
                    self._inc_info = json.loads(public.readFile(self._inc_file))
                except:
                    self._inc_info = []
            #检测增量备份文件完整性
            check_path = self.splicing_save_path()
            check_date_list = self.get_every_day(start_time.split()[0],end_time.split()[0])
            start_end=self.get_start_end_binlog(start_time,end_time)
            #检查二进制日志完整性
            file_lists_data=self.traverse_all_files(check_path,check_date_list,start_end)
        #尝试从远程存储器下载增量备份缺失文件
        if file_lists_data and file_lists_data['file_lists_not']:
            for i in file_lists_data['file_lists_not']:
                for filename in i:
                    download_info=public.M('mysqlbinlog_backups').where('sid=? and local_name=?',(pdata['id'],filename)).find()
                    download_size = 1024
                    if download_info and 'size' in download_info:download_size = download_info['size']
                    self.auto_download_file(cloud_list,filename,download_size)
            file_lists_data=self.traverse_all_files(check_path,check_date_list,start_end)
        return file_lists_data


    def restore_to_database(self,get):
        """
        @name 恢复数据到数据库 依赖.sql文件
        @auther hezhihong<2022-04-15>
        @param database_name  数据库名
        @param start_time 开始时间
        @param end_time 结束时间
        @return 
        """
        public.set_module_logs('binlog','restore_to_database')
        #检查备份文件完整性
        pdata = public.M('mysqlbinlog_backup_setting').where('id=?',str(get.backup_id,)).find()
        if not pdata:return  public.returnMsg(False, '增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试恢复！')
        if pdata and 'zip_password' in pdata: self._zip_password = pdata['zip_password']
        else:self._zip_password = ''
        self._db_name = get.datab_name
        self._tables = '' if 'table_name' not in get else get.table_name
        add_type = '/tables/'+self._tables+'/' if self._tables else '/databases/'
        restore_path = self._save_default_path+self._db_name+add_type
        self._full_file= restore_path+'full_record.json'
        self._inc_file = restore_path+'inc_record.json'
        tmp_path = os.path.join(restore_path,'test')
        file_lists_data = self.check_binlog_complete(pdata,get.end_time)
        if 'file_lists_not' in file_lists_data and file_lists_data['file_lists_not']:return public.returnMsg(False,'恢复所需要的文件不完整')
        if not self._full_info:return public.returnMsg(False,'全量备份记录文件内容不完整')
        #恢复完全备份
        #兼容gz和zip后缀备份文件恢复
        if self._full_info['full_name'].split('.')[-1]=='gz':
            args = public.dict_obj()
            args.sfile = self._full_info['full_name']
            args.dfile = os.path.dirname(self._full_info['full_name'])
            import files
            files.files().UnZip(args)
            sql_file = args.sfile.replace('.gz','')
            if not self.restore_sql(get.datab_name,'localhost',self.get_mysql_port(),'root',self._mysql_root_password,sql_file):
                return public.returnMsg(False, '恢复全量备份{}失败！'.format(sql_file))
        elif self._full_info['full_name'].split('.')[-1]=='zip':
            sql_file = self._full_info['full_name'].replace('.zip','.sql')
            self.unzip_file(self._full_info['full_name'])
            if not self.restore_sql(get.datab_name,'localhost',self.get_mysql_port(),'root',self._mysql_root_password,sql_file):
                return public.returnMsg(False, '恢复全量备份{}失败！'.format(sql_file))
        if os.path.isfile(sql_file):os.remove(sql_file)

        #如恢复截止时间不等于全量备份时间，则恢复增量二进制日志sql
        if self._full_info['time'] != get.end_time:
            if not self._inc_info:return public.returnMsg(False,'增量备份记录文件内容不完整')
            for i in range(len(file_lists_data['data'])):
                for c in file_lists_data['data'][i]:
                    check_info = self.get_info(c,self._inc_info)
                    sql_file = {}
                    if c == file_lists_data['last'] and check_info['time'] != get.end_time:
                        is_start = False
                        tmp_src_name,tmp_mark_line=self.extract_file_content(c,get.end_time)
                        sql_file['name'] = self.create_extract_file(tmp_src_name,tmp_mark_line,is_start)
                        sql_file['size'] = os.path.getsize(sql_file['name'])
                    else:
                        sql_file = self.unzip_file(c)
                    if sql_file in [0,'0']:return public.returnMsg(False, '恢复以下{}文件失败！'.format(c))
                    if sql_file['size'] in [0,'0']: 
                        if os.path.isfile(sql_file['name']):os.remove(sql_file['name'])
                        if os.path.isfile(sql_file['name'].replace('/test','')):os.remove(sql_file['name'].replace('/test',''))
                    else:
                        print('正在恢复{}'.format(sql_file['name']))
                        if not self.restore_sql(get.datab_name,'localhost',self.get_mysql_port(),'root',self._mysql_root_password,sql_file['name']):
                            return public.returnMsg(False, '恢复以下{}文件失败！'.format(sql_file['name']))
                        if os.path.isfile(sql_file['name']):os.remove(sql_file['name'])
                        if os.path.isfile(sql_file['name'].replace('/test','')):os.remove(sql_file['name'].replace('/test',''))
                    if sql_file['name'].split('/')[-2]=='test':shutil.rmtree(os.path.dirname(sql_file['name']))
            if os.path.isdir(tmp_path):shutil.rmtree(tmp_path)
        return public.returnMsg(True, '恢复成功!')

    def restore_sql(self,db_name,host_name,mysql_port,user_name,mysql_root_password,sql_file):
        """
        @name 恢复数据到数据库 依赖.sql文件
        @auther hezhihong<2022-04-15>
        @param db_name 恢复的数据库名
        @param sql_file 恢复的sql文件
        @return True or False
        """
        if sql_file.split('.')[-1] != 'sql' or not os.path.isfile(sql_file):
            return False
        #恢复sql
        try:
            result = os.system(public.get_mysql_bin() + " -h "+ host_name +" -P "+str(mysql_port)+" -u"+str(user_name)+" -p" + str(mysql_root_password) + " --force \"" + db_name + "\" < " +'"'+ sql_file +'"'+' 2>/dev/null')
        except Exception as e:
            print(e)
            return False
        if result != 0:
            return False
        return True

    def get_full_backup_file(self,db_name,path):
        """
        @name 取全量备份包名
        @auther hezhihong<2022-04-15>
        @return list 文件列表
        """
        if path[-1] == '/': path = path[:-1]
        backup_path = path
        all_list = os.listdir(backup_path)
        #取所有数据库备份包
        files_list = []
        for i in range(len(all_list)):
            path_name =  os.path.join(backup_path,all_list[i])
            if not all_list: continue
            if os.path.isfile(path_name):
                files_list.append(all_list[i])
        #过滤仅包含db_name的备份包
        full_bakcup_list=[]
        if files_list:
            for i in files_list:
                # path_name = backup_path+'/'+[i]
                is_add =True
                try:
                    temp_dict = {}
                    temp_dict['name'] = i
                    if i.split('.')[-1]!='gz' and i.split('.')[-1]!='zip': continue
                    if i.split(db_name)[0] == i: continue
                    if i.split('_'+db_name+'_')[1] == db_name: continue
                    temp_dict['time']=os.path.getmtime(os.path.join(backup_path,i))
                except:
                    is_add =False
                if is_add:full_bakcup_list.append(temp_dict)
        full_bakcup_list = sorted(full_bakcup_list,key=lambda x:float(x['time']),reverse=True)
        #时间戳格式化输出
        for c in full_bakcup_list:
            c['time'] = public.format_date(times =c['time'])
        return full_bakcup_list

    def splicing_save_path(self):
        """
        @name 拼接保存路径
        @auther hezhihong<2022-04-29>
        @return 路径
        """
        if self._tables:
            save_path = self._save_default_path + self._db_name + '/tables/' + self._tables +'/'
        else:
            save_path = self._save_default_path + self._db_name + '/databases/'
        return save_path

    def get_remote_servers(self,get=None):
        """
        @name 取远程服务器列表
        """
        data = []
        servers = public.M('database_servers').select()
        if not servers:return data
        for i in servers:
            if not i:continue
            if 'db_host' not in i or 'db_port' not in i or 'db_user' not in i or 'db_password' not in i:continue
            data.append(i['db_host'])
        self._db_name = 'hongbrother_com'
        self.synchronize_remote_server()
        return data

    def synchronize_remote_server(self):
        """
        @name 同步到指定数据库服务器
        @auther hezhihong<2022-04-24>
        @return 
        """
        #取同步开始时间
        conn_config = public.M('database_servers').where('db_host=?','43.154.36.59').find()
        if not conn_config:return 0
        try :
            self._db_mysql = self._db_mysql.set_host(conn_config['db_host'],int(conn_config['db_port']),self._db_name,conn_config['db_user'],conn_config['db_password'])
            # self._db_mysql.execute("show databases;")
        except:
            print('无法连接服务器！')
            return 0
        # backup_time = os.path.getmtime(full_backup)
        # start_time = public.format_date(times =(int(backup_time)+1))
        # pdata = public.M('mysqlbinlog_backup_setting').where('database_table=?', db_name).find()
        #检测远程数据库连接
        # if self.check_connect(db_name='',host=host_name,user=user_name,password=mysql_root_password):
        #     if not self.check_connect(db_name=db_name,host=host_name,user=user_name,password=mysql_root_password):
        #         connection = self.connect_mysql(db_name='',host=host_name,user=user_name,password=mysql_root_password)
        #         if connection:
        #             self.close_mysql(connection)
        #             print('检查远程服务器数据库{}是否存在'.format(db_name))
        #             #如db_name不存在，自动创建
        #             # try:
        #             #     with connection.cursor() as cursor:
        #             #         cursor.execute("create database `" + db_name + "` DEFAULT CHARACTER SET " + 'utf8' + " COLLATE " + 'utf8_general_ci')
        #             #         if not self.check_connect(db_name=db_name,host=host_name,user=user_name,password=mysql_root_password):
        #             #             print('检查远程服务器数据库{}是否存在'.format(db_name))
        #             # except:
        #             #     print('数据库连接失败')
        # else:
        #     return 0
        #同步到指定数据库服务器
        # if pdata['sync_remote_status'] == 0:
        #     print('从未同步过')
        #     if not self.restore_sql(db_name,host_name,mysql_port,user_name,mysql_root_password):
        #         raise
            # pdata = {
            # pdata['sync_remote_time'] = public.format_date(times =int(backup_time))
            # public.M('mysqlbinlog_backup_setting').where('database_table=?', db_name).update(pdata)
        #取备份包时间到现在的所有包
        # end_time = public.getDate()
        # check_date_list = self.get_every_day(str(start_time).split()[0],str(end_time).split()[0])
        # print(check_date_list)
        # restore_start_end_zip=self.get_start_end_binlog(start_time,end_time)
        # print(restore_start_end_zip)
        # check_path = self.splicing_save_path()
        # file_lists_data=self.traverse_all_files(check_path,check_date_list,restore_start_end_zip)
        # print(file_lists_data['data'])
        # if file_lists_data['status'] == 'False':
        #     if file_lists_data['first']==file_lists_data['file_lists_not'][0][0]:
        #         print(file_lists_data['file_lists_not'][0][0])
        #         print('增量备份包不存在')
        #         return 0
        #     else:
        #         pass
            # print(file_lists_data['file_lists_not'][0][0])
        # if file_lists_data['data']:
        #     for i in file_lists_data['data']:
        #         for c in i:
        #             if c == file_lists_data['file_lists_not'][0][0]:
        #                 break
        #             if not self.restore_sql(db_name,host_name,mysql_port,user_name,mysql_root_password,i):
        #                 raise
        # else:
        #     print('跳过')
        #更新同步时间记录
        # temp_name = os.path.basename(file_lists_data['file_lists_not'][0][0])
        # pdata['sync_remote_time']  = temp_name.split('_')[0]+' '+temp_name.split('_')[1].split('-')[0]+':'+temp_name.split('_')[1].split('-')[1].replace('.zip','')+':00'
        # public.M('mysqlbinlog_backup_setting').where('id=?', pdata['id']).update(pdata)

    def splice_file_name(self,path,check_day,check_hour_list):
        """
        @name 拼接文件名
        @auther hezhihong<2022-04-15>
        @param path文件绝对路径
        @param check_day 检查日期
        @param check_hour_list 检查小时列表
        @return 文件名列表
        """
        file_list= []
        for i in check_hour_list:
            add_data = path+check_day+'_'+i+'.zip'
            file_list.append(add_data)
        # print(file_list)
        return file_list

    def check_foler_file(self,file_list):
        """
        @name 检查文件是否存在
        @auther hezhihong<2022-04-15>
        @param file_list 文件列表
        @return file_name或者None
        """
        file_not = []
        for i in file_list:
            if not os.path.isfile(i):
                file_not.append(i)
        return file_not



    def get_every_day(self,start_date_str,end_date_str):
        """
        @name 取指定时间日期段内的所有日期
        @auther hezhihong<2022-04-15>
        @param start_date_str string 开始日期
        @param end_date_str string 截止日期
        @return list 起始截止时间段的每一天日期列表
        """
        date_list = []
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        while start_date <= end_date:
            date_str =  start_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            start_date += datetime.timedelta(days=1)
        return date_list

    def get_databases(self,get=None):
        """
        @name 取所有数据库名
        @auther hezhihong<2022-04-15>
        @return list 数据库名列表
        """
        databases = public.M('databases').field('name').select()
        database_list = []
        for database in databases:
            data = {}
            if not database: continue
            check_type = public.M('databases').where('name=?',database['name']).getField('type')
            check_type=check_type.lower()
            if check_type=='pgsql' or check_type=='sqlserver' or check_type=='mongodb':continue
            if public.M('databases').where('name=?',database['name']).getField('sid'):continue
            data['name'] = database['name']
            tmp_backup_id = public.M('mysqlbinlog_backup_setting').where("db_name=? and backup_type=?",(database['name'],'databases')).getField('id')
            if tmp_backup_id:
                data['cron_id'] = public.M('crontab').where("sBody=?",('{} {} --db_name {} --binlog_id {}'.format(self._python_path,self._binlogModel_py,database['name'],str(tmp_backup_id)),)).getField('id')
            else:
                data['cron_id'] = None
            database_list.append(data)
        return database_list

    def connect_mysql(self,db_name='',host='localhost',user='root',password=_mysql_root_password):
        """
        @name 连接数据库
        @auther hezhihong<2022-04-15>
        @param db_name 数据库名
        @param host 登录主机名
        @param user 登录用户名
        @param password 登录密码
        @return 连接
        """
        import pymysql
        if db_name:
            connection = pymysql.connect(host,
                user,
                password,
                db_name,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)
        else:
            connection = pymysql.connect(host,
                user,
                password,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)

        return connection

    def check_connect(self,db_name,host,user,password):
        """
        @name 检查数据库链接
        @author hezhihong<2022-04-15>
        @param db_name 数据库名
        @param host 登录主机名
        @param user 登录用户名
        @param password 登录密码
        @return True or False
        """
        is_conconnection = False
        connection =None
        try:
            connection = self.connect_mysql(db_name,host,user,password)
        except Exception as e:
            print('连接失败')
            print(e)
        if connection:
            is_conconnection = True
            # print('连接成功')
        self.close_mysql(connection)
        if is_conconnection:
            return True
        else:
            return False

    def get_tables(self,get=None):
        """
        @name 取所有表名
        @author hezhihong<2022-04-15>
        @param db_name 数据库名
        @return list 指定数据库的所有表名列表
        """
        tables_list= []
        if get:
            if 'db_name' not in get:return tables_list
            db_name =get.db_name 
        else: db_name =self._db_name
        try:
            mysql_port = self.get_mysql_port()
            self._db_mysql = self._db_mysql.set_host('localhost',mysql_port,'','root',self._mysql_root_password)
            if not self._db_mysql:return tables_list
            sql = "select table_name from information_schema.tables where table_schema=%s and table_type='base table';"
            sql_two = "show tables from %s"
            param = (db_name,)
            tables= self._db_mysql.query(sql,True,param)
            if not tables:
                tables= panelMysql().query("show tables from %s;" % (db_name))
            for i in tables:
                tmp_table_data = {}
                tmp_table_data['name'] = i[0]
                if not i:continue
                tmp_backup_id = public.M('mysqlbinlog_backup_setting').where("tb_name=? and backup_type=? and db_name=?",(i[0],'tables',db_name)).getField('id')
                if tmp_backup_id:
                    tmp_table_data['cron_id'] = public.M('crontab').where("sBody=?",('{} {} --db_name {} --binlog_id {}'.format(self._python_path,self._binlogModel_py,db_name,str(tmp_backup_id)),)).getField('id')
                else:
                    tmp_table_data['cron_id'] = None
                tables_list.append(tmp_table_data)
        except Exception as e:
            tables_list= []
        return tables_list

    def get_mysql_status(self):
        """
        @name 检测mysql运行状态
        """
        try:
            panelMysql().query('show databases')
        except:
            return False
        return True



    def close_mysql(self,connection):
        """
        @name 关闭mysql链接
        @author hezhihong<2022-04-15>
        """
        try:
            connection.commit()
            connection.close()
        except:
            pass

    def get_binlog_status(self,get=None):
        """
        @name 检测二进制日志是否开启
        @author hezhihong<2022-04-15>
        @param db_name 数据库名
        @return {'status':value}
        """
        binlog_status = {}
        try:
            on_or_off = panelMysql().query('show variables like "log_bin"')[0][1]
            if on_or_off == 'ON':
                binlog_status['status'] = True
            else:
                binlog_status['status'] = False
        except Exception as e:
            binlog_status['status'] = False
        return binlog_status

    def file_md5(self,filename):
        """
            @name 生成文件的MD5
            @author hezhihong<2022-04-15>
            @param filename 文件名
            @return string(32) or False
        """
        if not os.path.isfile(filename): return False
        import hashlib
        my_hash = hashlib.md5()
        f = open(filename,'rb')
        while True:
            b = f.read(8096)
            if not b :
                break
            my_hash.update(b)
        f.close()
        return my_hash.hexdigest()
    
    def set_file_info(self,save_file,json_file,ent_time=None,is_full=None):
        '''
            @name 写入文件信息
            @author hezhihong<2022-04-15>
            @param save_file 保存文件
            @param json_file 写入的存储文件
            @param end_time 结束时间
            @param is_full 是否覆盖写入
        '''
        info = []
        if os.path.isfile(json_file):
            try:
                info = json.loads(public.readFile(json_file))
            except:
                info = []
        file_info = {}
        file_info['name'] = os.path.basename(save_file)
        file_info['size'] = os.path.getsize(save_file)
        file_info['time'] = public.format_date(times=os.path.getmtime(save_file))
        file_info['md5'] = self.file_md5(save_file)
        file_info['full_name'] = save_file
        if ent_time:file_info['ent_time']= ent_time
        is_rep = False
        for i in range(len(info)):
            if info[i]['name'] == file_info['name']:
                info[i] = file_info
                is_rep = True
        if not is_rep: 
            if is_full: info = []
            info.append(file_info)
        public.writeFile(json_file,json.dumps(info))

    def update_file_info(self,json_file,end_time):
        """
        @name 更新文件信息
        @author hezhihong<2022-04-20>
        @param json_file 更新文件
        @param end_time 结束时间
        """
        if os.path.isfile(json_file):
            info = json.loads(public.readFile(json_file))
            info[0]['end_time']= end_time
            public.writeFile(json_file,json.dumps(info))

    def get_format_date(self,stime=None):
        """
            @name 获取时间，如2022-04-08_11
            @author hezhihong<2022-04-20>
            @param stime 开始时间
            @return string(如2022-04-08_11)
        """
        if not stime:
            stime = time.localtime()
        else:
            stime = time.localtime(stime)
        return time.strftime("%Y-%m-%d_%H-%M", stime)
        
    def get_format_date_of_time(self,str_true=None,stime = None,format_str = "%Y-%m-%d_%H:00:00"):
        """
            @name 获取时间，如2022-04-08_11:00:00
            @author hezhihong<2022-04-20>
            @param stime 开始时间
            @return string(如2022-04-08_11:00:00)
        """
        format_str = "%Y-%m-%d_%H:00:00"
        if str_true:
            format_str = "%Y-%m-%d %H:00:00"
        if not stime:
            stime = time.localtime()
        else:
            stime = time.localtime(stime)
        return time.strftime(format_str, stime)

    def get_binlog_file(self,start_time):
        """
            @name 获取binlog文件名
            @auther hezhihong<2022-04-15>
            @param start_time string 开始时间
            @return  list 二进制文件列表
        """
        binlog_files = public.readFile(self._mysql_bin_index)

        # 如果binlog-index文件不存在，则返回通配所有二进制日志文件
        if not binlog_files:
            return self._mysql_bin_index.replace(".index",".*")
        
        data_path = os.path.dirname(self._mysql_bin_index)

        # 降序排列
        binlog_list = sorted(binlog_files.split('\n'),reverse=True)

        # 遍历binlog文件
        _list = []
        for fname in binlog_list:
            if not fname: continue
            filename = os.path.join(data_path,fname.split('/')[-1])
            if not os.path.exists(filename):
                continue
            if os.path.isdir(filename): continue

            _list.insert(0,filename)
            # 只处理开始时间之后的binlog文件
            if os.stat(filename).st_mtime < start_time:
                break
        return ' '.join(_list)
            
    def zip_file(self,filename):
        """
            @name 加密压缩文件并将文件名后缀由.sql替换为.zip
            @auther hezhihong<2022-04-15>
            @param filename 需要压缩的文件名
            @return 文件大小
        """
        path = os.path.dirname(filename)
        src_name = os.path.basename(filename)
        zip_name = src_name.replace('.sql','.zip')
        zip_file = path + '/' + zip_name
        src_file = path + '/' + src_name
        if os.path.exists(zip_file): os.remove(zip_file)
        print("|-压缩"+zip_file,end='')
        if self._zip_password:
            os.system("cd {} && zip -P {} {} {} 2>&1 >/dev/null".format(path,self._zip_password,zip_name,src_name))
        #兼容空密码
        else:
            os.system("cd {} && zip {} {} 2>&1 >/dev/null".format(path,zip_name,src_name))
        if not os.path.exists(zip_file): 
            print(' ==> 失败')
            return 0
        if os.path.exists(src_file): os.remove(src_file)
        print(' ==> 成功')
        return os.path.getsize(zip_file)
        
    def unzip_file(self,filename):
        """
            @name 解压文件
            @auther hezhihong<2022-04-15>
            @param filename 需要解压缩的文件名
            @return dict 包含文件名、大小  
        """
        unzip_file_info = {}
        path = os.path.dirname(filename)+'/'
        if not os.path.exists(path): os.makedirs(path)
        src_name = os.path.basename(filename)
        unzip_name = src_name.replace('.zip','.sql')
        print("|-解压缩"+filename,end='')
        if self._zip_password:
            os.system("cd {} && unzip -o -P {} {} >/dev/null".format(path,self._zip_password,filename))
        #兼容空密码
        else:
            os.system("cd {} && unzip -o {} >/dev/null".format(path,filename))
        if not os.path.exists(path+'/'+unzip_name): 
            print(' ==> 失败')
            return 0
        print(' ==> 成功')
        unzip_file_info['name'] = path+'/'+unzip_name
        unzip_file_info['size'] = os.path.getsize(path+'/'+unzip_name)
        return  unzip_file_info      

    def export_data(self,get):
        """
            @name 导出指定截止时间数据
            @auther hezhihong<2022-04-20>
            @return string 导出文件zip包名  
        """
        public.set_module_logs('binlog','export_data')
        if not os.path.exists('/temp'): os.makedirs('/temp')
        data = {}
        #检测导出截止时间数据完整性
        add_type = 'tables' if 'table_name' in get else 'databases'
        pdata = public.M('mysqlbinlog_backup_setting').where('db_name=? and backup_type=?', (get.datab_name,add_type)).find()
        if not pdata:return public.returnMsg(False, '增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试下载！')
        alioss_value,txcos_value,qiniu_value,bos_value,obs_value,ftp_value,cloud_list,cloud_not= self.check_cloud_oss(pdata)
        self._db_name=get.datab_name
        self._tables = get.table_name if 'table_name' in get else ''
        self._zip_password = pdata['zip_password']
        check_path = self._save_default_path+get.datab_name+'/'+add_type+'/'+self._tables+'/'
        check_path = check_path.replace('//','/')
        full_file =os.path.join(check_path,'full_record.json')
        inc_file = os.path.join(check_path,'inc_record.json')
        #检测全量备份记录文件，兼容不保留本地备份情况
        if not os.path.isfile(full_file):
            #尝试从远程存储器下载
            self.auto_download_file(cloud_list,full_file)
        if os.path.isfile(full_file):
            full_info = json.loads(public.readFile(full_file))
            # if not full_info[0]['full_name']:return  public.returnMsg(False,'全量备份记录文件不存在！')
            if not os.path.isfile(full_info[0]['full_name']):
                #尝试从远程存储器下载
                self.auto_download_file(cloud_list,full_info[0]['full_name'],full_info[0]['size'])
            if not os.path.isfile(full_info[0]['full_name']):
                return public.returnMsg(False,'全量备份数据不存在！')
        else:
            return public.returnMsg(False,'全量备份数据不存在！')
        start_time = full_info[0]['time']
        tmp_end_time = get.end_time.replace(' ','__').replace(':','-')
        file_name = "db-{}---{}.tar.gz".format(get.datab_name,tmp_end_time)
        file_name = "db-{}---{}---{}.tar.gz".format(get.datab_name,self._tables,tmp_end_time) if 'table_name' in get else file_name
        #取压缩文件名字符
        tar_str = full_info[0]['full_name']+' '+full_file
        if os.path.isfile(inc_file):
            tar_str = tar_str+ ' '+inc_file
        # print(get.end_time)
        # print(start_time)
        inc_conf = []
        if os.path.isfile(inc_file):
            inc_conf = json.loads(public.readFile(inc_file))
            if not inc_conf[0]['full_name']:inc_conf=[]
        self.update_file_info(full_file,get.end_time)
        end_file = ''
        inc_write_conf = ''
        if get.end_time != start_time: 
            check_date_list = self.get_every_day(start_time.split()[0],get.end_time.split()[0])
            restore_start_end_zip=self.get_start_end_binlog(start_time,get.end_time)
            #是否为整点，如15:00:00
            if get.end_time == get.end_time.split(':')[0]+':00:00':
                restore_start_end_zip['end'] = restore_start_end_zip['end'][:-1]
            file_lists_data=self.traverse_all_files(check_path,check_date_list,restore_start_end_zip)
            #尝试从远程存储器下载
            if file_lists_data and file_lists_data['file_lists_not']:
                print('自动下载前：以下文件不存在{}'.format(file_lists_data['file_lists_not']))
                for inc_file in file_lists_data['file_lists_not']:
                    for inc_filename in inc_file:
                        if not os.path.exists(os.path.dirname(inc_filename)): os.makedirs(os.path.dirname(inc_filename))
                        download_info=public.M('mysqlbinlog_backups').where('sid=? and local_name=?',(pdata['id'],inc_filename)).find()
                        download_size = 1024
                        if download_info and 'size' in download_info:download_size = download_info['size']
                        self.auto_download_file(cloud_list,inc_filename,download_size)
                        # self.auto_download_file(cloud_list,inc_filename)
                file_lists_data=self.traverse_all_files(check_path,check_date_list,restore_start_end_zip)
            if file_lists_data['status'] == 'False':
                return public.returnMsg(False,'选择指定时间段的数据不完整！')
            #提取截止时间文件数据
            for i in range(len(file_lists_data['data'])):
                for c in  file_lists_data['data'][i]:
                    tmp_c = ' '+c
                    tar_str+=tmp_c
                    if not restore_start_end_zip['end']:continue
                    replace_value = ''
                    if c == file_lists_data['last']:
                        replace_value = 'end'
                    if replace_value:
                        c_path = os.path.dirname(c)+'/'
                        if replace_value == 'end':
                            tmp_mark_time = get.end_time
                        #取标记行内容  
                        tmp_src_name,tmp_mark_line=self.extract_file_content(c,tmp_mark_time)
                        tmp_src_name = tmp_src_name.replace('//','/')
                        #以标记行内容提取sql文件内容
                        tmp_extract_file_name = self.create_extract_file(tmp_src_name,tmp_mark_line)
                        end_conf = public.readFile(tmp_extract_file_name)
                        os.system('rm -rf {}'.format(c_path+'test/'))
                        #备份原文件
                        if os.path.isfile(c):
                            os.system('mv -f {} {}'.format(c,c+'.bak'))
                            end_file = c+'.bak'
                        if not os.path.isfile(c+'.bak'):continue
                        public.writeFile(tmp_src_name,end_conf)
                        self.zip_file(tmp_src_name)
        #提取截止时间点增备记录文件数据
        if end_file:
            tmp_conf = ''
            for i in inc_conf:
                if i['full_name'] == end_file.replace('.bak',''):
                    tmp_conf = i
                    break
            if tmp_conf:
                inc_write_conf=inc_conf[:inc_conf.index(tmp_conf)+1]
                public.writeFile(inc_file,json.dumps(inc_write_conf))
        
        #压缩导出数据包
        tar_str = tar_str.replace(self._save_default_path,'./')
        # print(tar_str)
        tar_name = self._save_default_path+file_name
        # print(tar_name)
        data['name'] = '/temp/'+file_name
        result =os.system('cd {} && tar -czf {} {} -C {}'.format(self._save_default_path,file_name,tar_str,'/temp'))
        # print(result)
        #恢复原文件
        public.writeFile(full_file,json.dumps(full_info))
        if inc_conf:
            public.writeFile(inc_file,json.dumps(inc_conf))
        if end_file:os.system('mv -f {} {}'.format(end_file,end_file.replace('.bak','')))
        if os.path.isfile(tar_name): os.system('mv -f {} {}'.format(tar_name,data['name']))
        if not os.path.isfile(data['name']): return public.returnMsg(False,'导出数据文件{}失败'.format(data['name']))
        #清理历史导出文件
        for delete_name in os.listdir('/temp'):
            if not delete_name:continue
            if os.path.isfile(os.path.join('/temp',delete_name)) and delete_name.find('.tar.gz') !=-1 and delete_name.find('-') !=-1 and delete_name.find('---')!=-1 and delete_name.split('-')[0]=='db' and delete_name!=file_name:
                rep_one = "([0-9]{4})-([0-9]{2})-([0-9]{2})"
                rep_two = "([0-9]{2})-([0-9]{2})-([0-9]{2})"
                c = re.search(rep_one,str(delete_name))
                d = re.search(rep_two,str(delete_name))
                if c and d:
                    os.remove(os.path.join('/temp',delete_name))
        # #清理下载的文件
        # if pdata['upload_local'] == '':
        #     if os.path.isfile(full_file):
        #         self.clean_local_full_backups(full_file)
        #         # print('已从本地磁盘清理过期完全备份')
        #     if os.path.isfile(inc_file):
        #         self.clean_local_inc_backups(inc_file)
        return data

    def extract_file_content(self,filename,mark_time):
        """
            @name 取文件截取标记行内容
            @auther hezhihong<2022-04-15>
            @param filename 文件绝对路径名
            @return 标记行内容 
        """
        unzip_file_info  =self.unzip_file(filename)
        src_name = unzip_file_info['name']
        f =open(src_name, 'r')
        mark_line=''
        compare_minutes=mark_time.split()[1].split(':')[1]
        compare_seconds=mark_time.split()[1].split(':')[2]
        for line in f.readlines():
            if line[0]!='#': continue
            if len(line.split()[1].split(':'))<3: continue
            if line.split()[1].split(':')[1] == compare_minutes:
                if line.split()[1].split(':')[2]>compare_seconds:
                    break
            if  line.split()[1].split(':')[1] > compare_minutes:
                break
            mark_line=line.strip()
        f.close
        return src_name,mark_line
    
    def create_extract_file(self,filename,mark_line,is_start=False):
        """
            @name 以标识行提取起始文件内容并生成新文件
            @auther hezhihong<2022-04-15>
            @param is_start 判断是开始文件还是结束文件 True为开始文件，False为结束文件
            @param mark_line string 标识行
            @param filename string 文件绝对路径名
            @return string 生成的新文件名  
        """
        path = os.path.dirname(filename)+'/test/'
        if not os.path.exists(path): os.makedirs(path)
        tmp_file_name = os.path.basename(filename)
        extract_file_name=path+tmp_file_name
        f =open(filename, 'r')
        f_w = open(extract_file_name, "w", encoding="utf-8")
        is_write = True
        for line in f.readlines():
            result =re.search(mark_line, line)
            if is_start:
                if is_write == True: 
                    if result:
                        is_write = False
                    continue
                else:
                    f_w.write(line)
            else: 
                if not is_write: break
                f_w.write(line)
            if result:
                is_write = False
        f.close
        f_w.close
        return extract_file_name
    
    def import_start_end(self,start_time,end_time):
        """
            @name 导入起止时间生成备份起止时间列表
            @param start_time string 开始时间 如2022-04-05 17:06:05
            @param end_time  string 结束时间 如2022-04-10 17:06:05 
            return list 
        """
        end_time = public.to_date(times = end_time)
        start_time = public.to_date(times = start_time)
        start_time=self.get_format_date_of_time(True,start_time)
        start_time = public.to_date(times = start_time)
        self._start_time_list.append(start_time)
        while True:
            start_time += self._save_cycle
            self._start_time_list.append(start_time)
            if start_time+self._save_cycle > end_time:
                break
        time_list = []
        if self._start_time_list:
            now_time= (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H")   +":00:00"
            # before_time = (datetime.datetime.now()+datetime.timedelta(hours=-48)).strftime("%Y-%m-%d %H")   +":00:00"
            for time in self._start_time_list:
                tmp_dict = {}
                st_time = float(time)
                stime = float(time) + self._save_cycle
                if st_time < public.to_date(times = json.loads(public.readFile(self._full_file))[0]['time']):
                #从完整备份时间开始至整点，如2022-04-09 14:32:07至2022-04-13 15:00:00
                    start_time = json.loads(public.readFile(self._full_file))[0]['time']
                else: 
                    start_time = public.format_date(times = st_time)
                if public.to_date(times=start_time) > public.to_date(times=now_time):continue
                if stime > public.to_date(times=now_time):continue
                end_time  = public.format_date(times = stime)
                tmp_dict['start_time'] = start_time
                tmp_dict['end_time'] = end_time
                time_list.append(tmp_dict)
        return time_list

    def import_date(self,start_time,end_time):
        """
            @name 从二进制日志中导出指定开始和截止时间点的sql语句
            @auther hezhihong<2022-04-15>
            @param stime开始时间
            @return 文件大小
        """

        sss = time.time()
        temp_time = public.to_date(times = start_time)
        sql_name = self.get_format_date(temp_time)
        day_name = sql_name.split('_')[0]
        #设置本地备份路径
        if self._save_default_path[-1] =='/':self._save_default_path = self._save_default_path[:-1]
        save_path = self._save_default_path+ '/'+day_name + '/'
        temp_path = self._temp_path + self._db_name + '/' + day_name + '/'
        if not os.path.exists(save_path): os.makedirs(save_path)
        if not os.path.exists(temp_path): os.makedirs(temp_path)
        if self._save_cycle == 3600:
            sql_name = sql_name.split('_')[0]+'_'+sql_name.split('_')[1].split('-')[0]
        else:
            pass
        sql_file = '{}{}.sql'.format(save_path,sql_name)
        temp_file = '{}{}.sql'.format(temp_path,sql_name)
        upload_file_name = sql_file.replace('.sql','.zip')
        self._backup_full_list.append(upload_file_name)
        if end_time == self._backup_end_time:
            if os.path.isfile(upload_file_name):os.remove(upload_file_name)
        print("|-导出{}".format(sql_file),end='')
        if not os.path.exists(temp_file):
            execute_cmd="{} --open-files-limit=1024 --start-datetime='{}' --stop-datetime='{}' -d {} {} > {} 2>/dev/null".format(self._mysqlbinlog_bin,start_time,end_time,self._db_name,self.get_binlog_file(temp_time),temp_file)
            os.system(execute_cmd)
        if not os.path.exists(temp_file):
            self._backup_fail_list.append(upload_file_name)
            raise Exception('从二进制日志导出sql文件失败!')
        table_list = ''
        if not self._tables:
            if self._pdata and self._pdata['table_list']:
                table_list = '|'.join(list(set(self._pdata['table_list'].split('|')).union(set(self._new_tables))))
        else:
            table_list = self._tables
        os.system('cat {} |grep -Ee "({})" > {}'.format(
            temp_file,
            table_list,
            sql_file
        ))

        if os.path.exists(temp_file): os.remove(temp_file)
        if not os.path.exists(sql_file):
            self._backup_fail_list.append(upload_file_name)
            raise Exception('导出sql文件失败!')
        print(" ==> 成功")
        if self._compress: 
            _size = self.zip_file(sql_file)
        else:
            _size = os.path.getsize(sql_file)
        print("|-文件大小: {}MB, 耗时: {}秒".format(round(_size / 1024 / 1024,2),round(time.time() - sss,2)))
        print("-"*60)

    def get_date_folder(self,path):
        """
        @name 取指定路径下指定格式(xxxx-xx-xx)目录列表
        @param path 指定路径
        @author hezhihong(2022-04-30)
        return list 目录列表
        """
        folder_list = []
        for i in os.listdir(path):
            if os.path.isdir(os.path.join(path,i)):
                rep = "([0-9]{4})-([0-9]{2})-([0-9]{2})"
                c = re.search(rep,str(i))
                if c:
                    folder_list.append(c[0])
        return folder_list

    def kill_process(self):
        """
        @name 清理阻塞进程
        @author hezhihong<2022-04-30>
        """
        for i in range(3):#重试3次
            process_name="'{} {} --db_name {} --binlog_id'".format(self._python_path,self._binlogModel_py,self._db_name)
            process = os.popen('ps aux | grep {} |grep -v grep'.format(process_name))
            process_info = process.read()
            for i in process_info.strip().split('\n'):
                if len(i.split()) < 16:continue
                check_time = int(i.split()[9].split(':')[0])
                kill_pid = i.split()[1]
                if not public.M('mysqlbinlog_backup_setting').where('id=?',i.split()[15]).count() and check_time>10:
                    os.kill(kill_pid)
                if check_time>50:
                    os.kill(kill_pid)
                if self._binlog_id:
                    if i.split()[15] == str(self._binlog_id) and check_time>0:
                        os.kill(kill_pid)
        process = os.popen('ps aux | grep {} |grep -v grep'.format(process_name))
        return process.read().strip().split('\n')

    def full_backup(self):
        """
        @name全量备份指定数据库或指定数据库的某张表
        @author hezhihong(2022-04-30)
        @return True or False
        """
        full_record_file = self._save_default_path+'full_record.json'
        inc_record_file = full_record_file.replace('full','inc')
        mysqldump_bin =public.get_mysqldump_bin()
        date_str=public.format_date("%Y%m%d_%H%M%S")
        #表完全备份
        if self._tables:
            tmp_src_name = self._save_default_path+'db_{}_{}_{}.sql'.format(self._db_name,self._tables,date_str)
            backup_cmd='{} -uroot -p{} {} {} > {} 2>/dev/null'.format(mysqldump_bin,self._mysql_root_password,self._db_name,self._tables,tmp_src_name)
        #整库完全备份
        else:
            tmp_src_name = self._save_default_path+'db_{}_{}.sql'.format(self._db_name,date_str)
            backup_cmd = mysqldump_bin + " -E -R --default-character-set="+ public.get_database_character(self._db_name) +" --force --hex-blob --opt " + self._db_name + " -u root -p" + str(self._mysql_root_password) + "> {} 2>/dev/null".format(tmp_src_name)
        try:
            os.system(backup_cmd)
            if not os.path.isfile(tmp_src_name):return False 
            self.zip_file(tmp_src_name)
        except Exception as e:
            print(e)
            return False
        tmp_zip_name=tmp_src_name.replace('.sql','.zip')
        if not os.path.isfile(tmp_zip_name):return False
        #清理本地多余完全备份，保留最新一份
        self.clean_local_full_backups(full_record_file,os.path.basename(tmp_zip_name),is_backup=True)
        print('|-已从磁盘清理过期备份文件')
        #清理本地增量备份
        self.clean_local_inc_backups(inc_record_file)
        self._full_zip_name = self._save_default_path+os.path.basename(tmp_zip_name)
        if self._tables:
            print('|-完全备份数据库{}中表{}成功！'.format(self._db_name,self._tables))
        else:
            print('|-完全备份数据库{}成功！'.format(self._db_name))
        return True

    def clean_local_inc_backups(self,inc_record_file):
        """
            @name 清理本地增量备份
            @auther hezhihong<2022-04-25>
            @param inc_record_file 增量备份记录文件
        """
        folder_list = self.get_date_folder(self._save_default_path)
        if folder_list:
            for i in folder_list:
                delete_name = os.path.join(self._save_default_path,i)
                if os.path.exists(delete_name):shutil.rmtree(delete_name)
        if os.path.isfile(inc_record_file):
            os.remove(inc_record_file)

    def clean_local_full_backups(self,full_record_file,check_name =None,is_backup=False,path = None):
        """
            @name 清理本地完全备份
            @auther hezhihong<2022-04-21>
            @param full_record_file 增量备份记录文件
            @param is_backup 是否为备份任务
        """
        if os.path.isfile(full_record_file):
            full_bakcup_list = self.get_full_backup_file(self._db_name,self._save_default_path)
            for i in full_bakcup_list:
                delete_name = os.path.join(self._save_default_path,i['name'])
                if is_backup :
                    if i['name'] != check_name:self.delete_file(delete_name)
                else:
                    self.delete_file(delete_name)
            if not is_backup:self.delete_file(full_record_file)
    def check_cloud_oss(self,pdata):
        """
        @name 检测云存储是否可用
        @auther hezhihong<2022-05-08>
        @param pdata 增量备份表记录数据
        """
        #实例化远程存储器
        alioss = alioss_main()
        txcos=txcos_main()
        qiniu=qiniu_main()
        bos=bos_main()
        obs=obs_main()
        ftp=ftp_main()
        cloud_list=[]
        cloud_not=[]
        #检测云存储是否可用
        alioss_value =txcos_value=qiniu_value=bos_value =obs_value=ftp_value =  False
        #检测阿里云OSS
        if pdata['upload_alioss'] == 'alioss':
            if alioss.check_config():
                cloud_list.append(alioss)
                alioss_value = True
            else:cloud_not.append('alioss')
        #检测腾讯云COS
        if pdata['upload_txcos'] == 'txcos':
            if txcos.check_config():
                cloud_list.append(txcos)
                txcos_value = True
            else:cloud_not.append('txcos')
        #检测七牛云存储
        if pdata['upload_qiniu'] == 'qiniu':
            if qiniu.check_config():
                cloud_list.append(qiniu)
                qiniu_value = True
            else:cloud_not.append('qiniu')
        #检测百度云存储
        if pdata['upload_bos'] == 'bos':
            if bos.check_config():
                cloud_list.append(bos)
                bos_value = True
            else:cloud_not.append('bos')
        #检测华为云存储
        if pdata['upload_obs'] == 'obs':
            if obs.check_config():
                cloud_list.append(obs)
                obs_value = True
            else:cloud_not.append('obs')
        #检测FTP存储空间
        if pdata['upload_ftp'] == 'ftp':
            if ftp.check_config():
                cloud_list.append(ftp)
                ftp_value = True
        return alioss_value,txcos_value,qiniu_value,bos_value,obs_value,ftp_value,cloud_list,cloud_not
    

    def execute_by_comandline(self,get=None):
        """
            @name 命令行或计划任务调用
            @auther hezhihong<2022-04-21>
            @param 
            @return 
        """
        self.install_cloud_module()
        if get:
            self._db_name = get.databname
            self._binlog_id = get.backup_id
        error_msg_list = []
        #self.sync_date()
        #清理阻塞进程
        process_list = self.kill_process()
        if len(process_list)>0:
            time.sleep(0.01)
        is_notice = False
        #检测是否开启二进制日志
        binlog_status = self.get_binlog_status()
        if binlog_status['status'] == False: 
            error_msg = '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！'
            print(error_msg)
            is_notice = True
        #检测磁盘空间
        self._db_mysql = self._db_mysql.set_host('localhost',self.get_mysql_port(),'','root',self._mysql_root_password)
        disk_path,disk_free,disk_inode = self._mybackup.get_disk_free(self._save_default_path)
        if not is_notice:
            p_size= ''
            try:
                sql = "select sum(DATA_LENGTH)+sum(INDEX_LENGTH) from information_schema.tables where table_schema=%s"
                param=(self._db_name,)
                d_tmp = self._db_mysql.query(sql,True,param)
                p_size = self._mybackup.map_to_list(d_tmp)[0][0]
            except:
                is_notice = True
                error_msg = "数据库连接异常，请检查root用户权限或者数据库配置参数是否正确。"
                print(error_msg)
                error_msg_list.append(error_msg)
            # return public.returnMsg(False,error_msg)
            if p_size == None:
                error_msg = '指定数据库 `{}` 没有任何数据!'.format(self._db_name)
                is_notice = True
                print(error_msg)
                error_msg_list.append(error_msg)
            # return public.returnMsg(False,error_msg)
            if disk_path:
                if p_size:
                    if disk_free < p_size:
                        error_msg = "目标分区可用的磁盘空间小于{},无法完成备份，请增加磁盘容量!".format(public.to_size(p_size))
                        print(error_msg)
                        is_notice = True
                        error_msg_list.append(error_msg)
                        # return public.returnMsg(False,error_msg)
                if disk_inode < self._inode_min:
                    error_msg = "目标分区可用的Inode小于{},无法完成备份，请增加磁盘容量!".format(self._inode_min)
                    print(error_msg)
                    is_notice = True
                    error_msg_list.append(error_msg)
                # return public.returnMsg(False,error_msg_list)    
        #取备份配置信息
        self._pdata = pdata = public.M('mysqlbinlog_backup_setting').where('id=?',str(self._binlog_id)).find()
        notice_str = pdata['database_table'] if pdata else self._db_name
        #取备份任务echo
        self._echo_info['echo']=public.M('crontab').where("sBody=?",('{} {} --db_name {} --binlog_id {}'.format(self._python_path,self._binlogModel_py,self._db_name,str(self._binlog_id)),)).getField('echo')
        self._mybackup = backup(cron_info=self._echo_info)
        if not pdata:
            print('未在数据库备份记录中找到id为{}的计划任务'.format(self._binlog_id))
            is_notice = True
        if self._db_name not in self.get_tables_list(self.get_databases()): 
            print('备份的数据库不存在')
            is_notice = True 
        if is_notice:
            #发送备份失败通知 
            self.send_failture_notification(error_msg_list, target=notice_str)        
            return public.returnMsg(False,'备份失败') 
        self._zip_password = pdata['zip_password']
        if pdata['backup_type'] == 'tables': self._tables = pdata['tb_name']
        self._save_default_path = pdata['save_path']
        print("|-分区{}可用磁盘空间为：{},可用Inode为:{}".format(disk_path,public.to_size(disk_free),disk_inode))
        #如不存在全量备份，则执行全量备份
        if not os.path.exists(self._save_default_path): 
            os.makedirs(self._save_default_path)
            is_full =True
        self._full_file =  self._save_default_path+'full_record.json'
        self._inc_file =inc_file= self._save_default_path+'inc_record.json'
        pdata['last_excute_backup_time']= self._backup_end_time = public.format_date()
        self._tables = pdata['tb_name']
        add_type= '/tables/'+self._tables+'/' if self._tables else '/databases/'
        self._backup_type = 'tables' if self._tables else 'databases'
        #判断全量备份包是否为一周前的备份
        check_full_time = pdata['start_backup_time']
        check_inc_time = pdata['end_backup_time']
        is_full =False
        cloud_chinese = {'alioss':'阿里云OSS','txcos':'腾讯云COS','qiniu':'七牛云存储','bos':'百度云存储','obs':'华为云存储'}
        #检测云存储是否可用
        alioss_value,txcos_value,qiniu_value,bos_value,obs_value,ftp_value,cloud_list,cloud_not= self.check_cloud_oss(pdata)
        if cloud_not:
            cloud_fail_list = []
            print('检测到无法连接上以下云存储：')
            for cloud_fail in cloud_not:
                if not cloud_fail:continue
                cloud_fail_list.append(cloud_chinese[cloud_fail])
                print('{}'.format(cloud_chinese[cloud_fail]))
            error_msg='检测到无法连接上以下云存储：{}'.format(cloud_fail_list)
            print('请检查配置或者更改备份设置！')
            #发送备份失败通知 
            self.send_failture_notification(error_msg, target=notice_str)        
            return public.returnMsg(False,'备份失败') 
        #检测全量备份记录文件，兼容不保留本地备份情况
        if not os.path.isfile(self._full_file):
            #尝试从远程存储器下载
            self.auto_download_file(cloud_list,self._full_file)
        full_info = {}
        if os.path.isfile(self._full_file):
            try:
                full_info = json.loads(public.readFile(self._full_file))[0]
                if 'name' not in full_info or 'size' not in full_info or 'time' not in full_info:is_full =True
                if 'end_time' in full_info:
                    if full_info['end_time'] != full_info['end_time'].split(':')[0]+':00:00':
                        check_inc_time=full_info['end_time'].split(':')[0]+':00:00'
                if 'full_name' in full_info and os.path.isfile(full_info['full_name']) and time.time()-public.to_date(times =check_full_time) > 604800:
                    is_full =True
                #检测二进制日志记录文件，兼容不保留本地备份情况
                if 'time' in full_info:
                    check_full_time=full_info['time']
                    if not os.path.isfile(self._inc_file) and check_inc_time != full_info['time']:
                        #尝试从远程存储器下载
                        self.auto_download_file(cloud_list,self._inc_file)
                    if not os.path.isfile(self._inc_file) and check_inc_time != full_info['time']:
                        print('增量备份记录文件不存在,将执行完全备份')
                        is_full =True
            except:
                full_info = {}
                is_full =True
        else:
            is_full =True
        backup_not = False
        # is_full =True
        #全量备份
        if is_full:
            print('☆☆☆完全备份开始☆☆☆')
            full_conf = []
            if not self.full_backup():
                error_msg = '全量备份数据库[{}]'.format(self._db_name)
                self.send_failture_notification(error_msg, target=notice_str)
                return public.returnMsg(False,error_msg)
            if os.path.isfile(self._full_file):
                try:
                    full_conf = json.loads(public.readFile(self._full_file))
                except:
                    full_conf = []
            #写完全备份记录
            self.set_file_info(self._full_zip_name,self._full_file,is_full = True)
            try:
                full_info = json.loads(public.readFile(self._full_file))[0]
            except:
                print('|-文件写入失败，检查是否有安装安全软件！')
                print('|-备份失败！')
                return
            pdata['start_backup_time'] =pdata['end_backup_time']= full_info['time']
            public.M('mysqlbinlog_backup_setting').where('id=?', pdata['id']).update(pdata)
            file_path = '/bt_backup/mysql_bin_log/'+self._db_name+add_type
            file_name =  file_path+full_info['name']
            full_name = file_path+'full_record.json'
            file_name = file_name.replace('//','/')
            full_name = full_name.replace('//','/')
            #上传到阿里云
            if alioss_value:
                alioss = alioss_main()
                if not alioss.upload_file_by_path(full_info['full_name'],file_name):
                        self._cloud_upload_not.append(full_info['full_name'])
                if not alioss.upload_file_by_path(self._full_file,full_name):self._cloud_upload_not.append(self._full_file)
                #清理阿里云存储过期完全备份和增量备份
                self.clean_cloud_backups(file_path,self._full_file,alioss,cloud_chinese['alioss'])
            else:
                if pdata['upload_alioss'] == 'alioss':
                    error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['alioss'],cloud_chinese['alioss'])
                    backup_not = True
                    print(error_msg)
            #上传到腾讯云
            if txcos_value:
                txcos = txcos_main()
                if not txcos.upload_file_by_path(full_info['full_name'],file_name):
                    self._cloud_upload_not.append(full_info['full_name'])
                if not txcos.upload_file_by_path(self._full_file,full_name):
                    self._cloud_upload_not.append(self._full_file)
                #清理腾讯云COS过期完全备份和增量备份
                self.clean_cloud_backups(file_path,self._full_file,txcos,cloud_chinese['txcos'])
            else:
                if pdata['upload_txcos'] == 'txcos':
                    error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['txcos'],cloud_chinese['txcos'])
                    backup_not = True
                    print(error_msg)
            #上传到七牛云
            if qiniu_value:
                qiniu = qiniu_main()
                if not qiniu.upload_file_by_path(full_info['full_name'],file_name):self._cloud_upload_not.append(full_info['full_name'])
                if not qiniu.upload_file_by_path(self._full_file,full_name):self._cloud_upload_not.append(self._full_file)
                #清理七牛云存储过期完全备份和增量备份
                self.clean_cloud_backups(file_path,self._full_file,qiniu,cloud_chinese['qiniu'])
            else:
                if pdata['upload_qiniu'] == 'qiniu':
                        error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['qiniu'],cloud_chinese['qiniu'])
                        backup_not = True
                        print(error_msg)
            #上传到百度云存储
            if bos_value:
                bos = bos_main()
                if not bos.upload_file_by_path(full_info['full_name'],file_name):self._cloud_upload_not.append(full_info['full_name'])
                if not bos.upload_file_by_path(self._full_file,full_name):self._cloud_upload_not.append(self._full_file)
                #清理百度云存储过期完全备份和增量备份
                self.clean_cloud_backups(file_path,self._full_file,bos,cloud_chinese['bos'])
            else:
                if pdata['upload_bos'] == 'bos':
                        error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['bos'],cloud_chinese['bos'])
                        backup_not = True
                        print(error_msg)
            #上传到华为云存储
            # obs_value = True
            if obs_value:
                obs =obs_main()
                if not obs.upload_file_by_path(full_info['full_name'],file_name):self._cloud_upload_not.append(full_info['full_name'])
                if not obs.upload_file_by_path(self._full_file,full_name):self._cloud_upload_not.append(self._full_file)
                #清理华为云存储过期完全备份和增量备份
                self.clean_cloud_backups(file_path,self._full_file,obs,cloud_chinese['obs'])
            else:
                if pdata['upload_obs'] == 'obs':
                        error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['obs'],cloud_chinese['obs'])
                        backup_not = True
                        print(error_msg)
            #上传到FTP存储空间
            # ftp_value = True
            if ftp_value:
                ftp_c =ftp_main()
                if not ftp_c.upload_file_by_path(full_info['full_name'],file_name):self._cloud_upload_not.append(full_info['full_name'])
                if not ftp_c.upload_file_by_path(self._full_file,full_name):self._cloud_upload_not.append(self._full_file)
                #清理TP存储空间过期完全备份和增量备份
                self.clean_cloud_backups(file_path,self._full_file,ftp_c,cloud_chinese['ftp'])
            else:
                if pdata['upload_ftp'] == 'ftp':
                        error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['ftp'],cloud_chinese['ftp'])
                        backup_not = True
                        print(error_msg)
            error_msg = '以下文件上传失败：{}'.format(self._cloud_upload_not)
            if self._cloud_upload_not or backup_not:
                self.send_failture_notification(error_msg, target=notice_str)
                if full_conf:public.writeFile(self._full_file,json.dumps(full_conf))
            print('☆☆☆完全备份结束☆☆☆')
            backup_type = 'full'
            info = json.loads(public.readFile(self._full_file))
            self.write_backups(backup_type,info)
            #清理本地备份
            if pdata['upload_local'] == '' and os.path.isfile(self._full_file):
                self.clean_local_full_backups(self._full_file)
                if os.path.isfile(self._inc_file):self.clean_local_inc_backups(self._inc_file)
                print('|-用户设置不保留本地备份，已从本地服务器清理备份')
            return public.returnMsg(True,'完全备份成功！')
        #二进制日志备份
        self._backup_add_time = pdata['start_backup_time']
        self._backup_start_time = check_inc_time
        self._new_tables = self.get_tables_list(self.get_tables())
        if self._backup_start_time and self._backup_end_time:
            time_list = self.import_start_end(self._backup_start_time,self._backup_end_time)
            for tmp_time in time_list:
                if not tmp_time:continue
                self._backup_fail_list = []
                if public.to_date(times=tmp_time['end_time']) > public.to_date(times=self._backup_end_time):tmp_time['end_time'] = self._backup_end_time
                self.import_date(tmp_time['start_time'],tmp_time['end_time'])
        #检测本地备份是否成功
        check_path= pdata['save_path']
        check_date_list = self.get_every_day(self._backup_start_time.split()[0],self._backup_end_time.split()[0])
        is_backup='True'
        restore_start_end_zip=self.get_start_end_binlog(self._backup_start_time,self._backup_end_time,is_backup)
        file_lists_data=self.traverse_all_files(check_path,check_date_list,restore_start_end_zip)
        if self._backup_fail_list or file_lists_data['file_lists_not']:
            add_data = ''
            if self._backup_fail_list:add_data=self._backup_fail_list
            else:add_data=file_lists_data['file_lists_not']
            
            error_msg = '以下文件备份失败{}'.format(add_data)
            #发送备份失败通知
            self.send_failture_notification(error_msg, target=notice_str)
            print(error_msg)
            return public.returnMsg(False,error_msg)
        tmp_full_conf = json.loads(public.readFile(self._full_file)) 
        #更新记录备份开始时间
        pdata['end_backup_time']=self._backup_end_time
        #更新备份记录表
        pdata['table_list'] = '|'.join(self._new_tables)
        self.update_file_info(self._full_file,self._backup_end_time)
        #上传到云存储
        last_one =last_two = False
        for ii in file_lists_data['data']:
            if ii == file_lists_data['data'][-1]:last_one=True
            for c in ii:
                if c == ii[-1]:last_two=True
                self.set_file_info(c,inc_file)
                inc_file_path = '/bt_backup/mysql_bin_log/'+self._db_name+add_type
                full_file_name = inc_file_path+'full_record.json'
                inc_file_name = inc_file_path+'inc_record.json'
                file_name =  '/bt_backup/mysql_bin_log/'+self._db_name+add_type+c.split('/')[-2]+'/'+c.split('/')[-1]
                if alioss_value:
                    alioss = alioss_main()
                    if not alioss.upload_file_by_path(c,file_name):
                        self._cloud_upload_not.append(c)
                    if os.path.isfile(inc_file) and last_one and last_two:alioss.upload_file_by_path(inc_file,inc_file_name)
                    if os.path.isfile(self._full_file) and last_one and last_two:alioss.upload_file_by_path(self._full_file,full_file_name)
                else:
                    if pdata['upload_alioss'] == 'alioss':
                            error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['alioss'],cloud_chinese['alioss'])
                            backup_not = True
                            print(error_msg)
                if txcos_value:
                    txcos = txcos_main()
                    if not txcos.upload_file_by_path(c,file_name):
                       self._cloud_upload_not.append(c)
                    if os.path.isfile(inc_file) and last_one and last_two:txcos.upload_file_by_path(inc_file,inc_file_name)
                    if os.path.isfile(self._full_file) and last_one and last_two:txcos.upload_file_by_path(inc_file,full_file_name)
                else:
                    if pdata['upload_txcos'] == 'txcos':
                            error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['txcos'],cloud_chinese['txcos'])
                            backup_not = True
                            print(error_msg)
                if qiniu_value:
                    qiniu = qiniu_main()
                    if not qiniu.upload_file_by_path(c,file_name):
                        self._cloud_upload_not.append(c)
                    if os.path.isfile(inc_file) and last_one and last_two:qiniu.upload_file_by_path(inc_file,inc_file_name)
                    if os.path.isfile(self._full_file) and last_one and last_two:qiniu.upload_file_by_path(inc_file,full_file_name)
                else:
                    if pdata['upload_qiniu'] == 'qiniu':
                            error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['qiniu'],cloud_chinese['qiniu'])
                            backup_not = True
                            print(error_msg)
                if bos_value:
                    bos = bos_main()
                    if not bos.upload_file_by_path(c,file_name):
                        self._cloud_upload_not.append(c)
                    if os.path.isfile(inc_file) and last_one and last_two:bos.upload_file_by_path(inc_file,inc_file_name)
                    if os.path.isfile(self._full_file) and last_one and last_two:bos.upload_file_by_path(inc_file,full_file_name)
                else:
                    if pdata['upload_bos'] == 'bos':
                            error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['bos'],cloud_chinese['bos'])
                            backup_not = True
                            print(error_msg)
                # obs_value = True
                if obs_value:
                    obs = obs_main()
                    if not obs.upload_file_by_path(c,file_name):
                        self._cloud_upload_not.append(c)
                    if os.path.isfile(inc_file) and last_one and last_two:obs.upload_file_by_path(inc_file,inc_file_name)
                    if os.path.isfile(self._full_file) and last_one and last_two:obs.upload_file_by_path(self._full_file,full_file_name)
                else:
                    if pdata['upload_obs'] == 'obs':
                            error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['obs'],cloud_chinese['obs'])
                            backup_not = True
                            print(error_msg)
                # ftp_value =True
                if ftp_value:
                    ftp = ftp_main()
                    if not ftp.upload_file_by_path(c,file_name):
                        self._cloud_upload_not.append(c)
                    if os.path.isfile(inc_file) and last_one and last_two:ftp.upload_file_by_path(inc_file,inc_file_name)
                    if os.path.isfile(self._full_file) and last_one and last_two:
                        full_file_name=os.path.join('/www/wwwroot/ahongtest',full_file_name)
                        ftp.upload_file_by_path(self._full_file,full_file_name)
                else:
                    if pdata['upload_ftp'] == 'ftp':
                            error_msg = '|-无法连接上{}，无法上传到{}'.format(cloud_chinese['ftp'],cloud_chinese['ftp'])
                            backup_not = True
                            print(error_msg)
        error_msg = '以下文件上传失败：{}'.format(self._cloud_upload_not)
        if self._cloud_upload_not or backup_not:
            self.send_failture_notification(error_msg, target=notice_str)
            if tmp_full_conf:public.writeFile(self._full_file,json.dumps(tmp_full_conf))
            return public.returnMsg(False,'增量备份失败！')
        public.M('mysqlbinlog_backup_setting').where('id=?', pdata['id']).update(pdata)
        if not is_full:
            backup_type = 'inc'
            info = json.loads(public.readFile(inc_file))
            self.write_backups(backup_type,info)
        if pdata['upload_local'] == '' and os.path.isfile(self._inc_file):
                if os.path.isfile(self._full_file):
                    self.clean_local_full_backups(self._full_file)
                    # print('已从本地磁盘清理过期完全备份')
                if os.path.isfile(self._inc_file):
                    self.clean_local_inc_backups(self._inc_file)
                    # print('已从本地磁盘清理过期增量备份')
                print('|-用户设置不保留本地备份，已从本地服务器清理备份')
        return public.returnMsg(True,'执行备份任务成功！')


    def write_backups(self,backup_type,info):
        """
        @name 写备份包记录表
        """
        full_json = self._full_file if backup_type=='full' else ''
        inc_json= self._inc_file if backup_type=='full' else ''
        for info_dict in info:
            cloud_name = info_dict['full_name'].replace('/www/backup','bt_backup')
            write_pdata = {
                "sid": self._binlog_id,
                "size":info_dict['size'] ,
                "type": backup_type,
                "full_json":full_json,
                "inc_json": inc_json,
                "local_name":info_dict['full_name'],
                "ftp_name": '',
                "alioss_name": cloud_name,
                "txcos_name":cloud_name,
                "qiniu_name":cloud_name,
                "aws_name":'',
                "upyun_name":'',
                "obs_name": cloud_name,
                "bos_name": cloud_name,
                "gcloud_storage_name": '',
                "gdrive_name":'',
                "msonedrive_name":''
            }
            #完全备份时，已经存在完全备份记录，自动清理
            if backup_type=='full' and public.M('mysqlbinlog_backups').where('type=? AND sid=?', (backup_type,self._binlog_id)).count():
                info_id = public.M('mysqlbinlog_backups').where('type=? AND sid=?', (backup_type,self._binlog_id)).getField('id')
                public.M('mysqlbinlog_backups').delete(info_id)
            #完全备份时，清理增量备份记录
            if backup_type=='full':
                clean_count = public.M('mysqlbinlog_backups').where('type=? AND sid=?', ('inc',self._binlog_id)).select()
                if clean_count:
                    for clean in clean_count:
                        if not clean:continue
                        if 'id' in clean:public.M('mysqlbinlog_backups').delete(clean['id'])
            #当备份记录不存在，自动写入
            if not public.M('mysqlbinlog_backups').where('type=? AND local_name=? AND sid=?', (backup_type,info_dict['full_name'],self._binlog_id)).count():
                public.M('mysqlbinlog_backups').insert(write_pdata)
            #当备份记录已存在，则更新
            else:
                info_id = public.M('mysqlbinlog_backups').where('type=? AND local_name=? AND sid=?', (backup_type,info_dict['full_name'],self._binlog_id)).getField('id')
                public.M('mysqlbinlog_backups').where('id=?', info_id).update(write_pdata)
            #增量备份时，完全备份记录不存在自动补全
            if backup_type=='inc' and not public.M('mysqlbinlog_backups').where('type=? AND sid=?', ('full',self._binlog_id)).count():
                try:
                    full_info = json.loads(public.readFile(self._full_file))[0]
                except:
                    full_info={}
                if full_info:
                    public.M('mysqlbinlog_backups').insert(write_pdata)

    def get_tables_list(self,data_list,type=False):
        """
        @name 只取列表'name'字段
        """ 
        tmp_data = []
        for p in data_list:
            if not p:continue
            if type:
                if p.get('type') != 'F':continue
            tmp_data.append(p['name'])
        return tmp_data


    def clean_cloud_backups(self,file_path,full_file,cloud_name,upload_name):
        """
        @name清理云存储过期备份
        """
        try:
            full_info = json.loads(public.readFile(full_file))[0]
        except:
            full_info=[]
        args_one = args_two =args_three=args_four=args_five=public.dict_obj()
        args_one.path = file_path
        alioss_list = cloud_name.get_list(args_one)
        if 'list' in alioss_list:
            for l in alioss_list['list']:
                if not l:continue
                if l['name'][-1] == '/':
                    args_two.path = file_path+l['name']
                    args_two.filename = l['name']
                    tmp_alioss_list = cloud_name.get_list(args_two)
                    args_two.path = file_path
                    #清理增备目录内文件
                    if tmp_alioss_list['list']:
                        for n in tmp_alioss_list['list']:
                            args_three.path = file_path+l['name']
                            args_three.filename = n['name']
                            cloud_name.remove_file(args_three)
                    #清理增备空目录
                    else:
                        cloud_name.remove_file(args_two)
                #清理增备完全备份
                if not full_info:continue
                if l['name'].split('.')[-1] in ['zip','gz','json'] and l['name'] != full_info['name'] and l['name'] != 'full_record.json':
                    args_four.path = file_path
                    args_four.filename = l['name']
                    cloud_name.remove_file(args_four)
                is_date = False
                if 'dir' not in l:continue
                if l['dir']==True:
                    try:
                        tmp_check =datetime.datetime.strptime(l['name'],'%Y-%m-%d')
                        is_date = True
                    except:
                        pass
                tmp_path = ''
                if is_date:tmp_path = os.path.join(file_path,l['name'])
                if tmp_path:
                    args_five.path=tmp_path
                    args_five.filename=''
                    args_five.is_inc = True
                    cloud_name.remove_file(args_five)
        print('|-已从{}清理过期备份文件'.format(upload_name))


    def add_binlog_inc_backup_task(self,pdata,backupTo):
        """
            @name binlog配置信息写入计划任务
            @auther hezhihong<2022-04-22>
            @param 
            @return 
        """
        args = {
            "name": "[勿删]数据库增量备份[{}]".format(pdata['database_table']),
            "type": pdata['cron_type'],
            "where1": pdata['backup_cycle'],
            "hour": '',
            "minute": '0',
            "sType":'enterpriseBackup',
            "sName": pdata['backup_type'],
            "backupTo": backupTo,
            "save":'1',
            "save_local":'1',
            "notice":pdata['notice'],
            "notice_channel":pdata['notice_channel'],
            "sBody": '{} {} --db_name {} --binlog_id {}'.format(self._python_path,self._binlogModel_py,self._db_name,str(pdata['id'])),
            "urladdress": '{}|{}|{}'.format(pdata['db_name'],pdata['tb_name'],pdata['id'])
        }
        import crontab
        res = crontab.crontab().AddCrontab(args)
        if res and "id" in res.keys():
            return True
        return False

    def create_table(self):
        """
            @name 创建增量日志配置信息表
            @auther hezhihong<2022-04-22>
            @return 
        """
        # 增量备份配置信息表
        if not public.M('sqlite_master').where('type=? AND name=?', ('table', 'mysqlbinlog_backup_setting')).count():
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
                                "add_time" INTEGER);''')

        #备份包信息记录表
        if not public.M('sqlite_master').where('type=? AND name=?', ('table', 'mysqlbinlog_backups')).count():
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
                                "where_4" TEXT DEFAULT '');''')


    def add_mysqlbinlog_backup_setting(self,get):
        """
            @name 增加mysqlbinlog日志增量备份设置
            @auther hezhihong<2022-04-22>
            @param 
            @return 
        """
        public.set_module_logs('binlog','add_mysqlbinlog_backup_setting')
        if not get.get('datab_name/str',0):return public.returnMsg(False, '当前没有数据库，不能添加！')
        if get.datab_name in [0,'0']:return public.returnMsg(False, '当前没有数据库，不能添加！')
        if not get.get('backup_cycle/d',0)>0:return public.returnMsg(False, '备份周期不正确，只能为正整数！')
        # if len(get.backup_cycle.split('.'))>1:return public.returnMsg(False, '备份周期只能为整数小时，不能有小数')
        # if get.backup_cycle=='0':return public.returnMsg(False, '备份周期不能设置为0')
        #检测是否开启binlog日志
        pdata =add_data= {}
        binlog_status = self.get_binlog_status()
        if binlog_status['status'] == False: return public.returnMsg(False, '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')
        self._db_name = add_data['db_name'] = get.datab_name
        add_type = 'databases' if get.backup_type=='databases' else 'tables'
        self._tables = '' if 'table_name' not in get else get.table_name 
        is_backup = False
        #判断是否已经存在备份
        check_pdata = ''
        check_cron_id = ''
        if self._tables:
            check_pdata = public.M('mysqlbinlog_backup_setting').where('db_name=? and backup_type=? and tb_name=?', (get.datab_name,add_type,self._tables)).find()
            if check_pdata:
                pdata =check_pdata
                is_backup = True
                check_cron_id = public.M('crontab').where('sBody=?', '{} {} --db_name {} --binlog_id {}'.format(self._python_path,self._binlogModel_py,check_pdata['db_name'],str(check_pdata['id']))).getField('id')
                if check_cron_id:
                    return public.returnMsg(False, '指定的数据库或者表已经存在备份，不能重复添加！')
        else:
            check_pdata = public.M('mysqlbinlog_backup_setting').where('db_name=? and backup_type=?', (get.datab_name,add_type)).find()
            if check_pdata:
                pdata =check_pdata
                is_backup = True
                check_cron_id = public.M('crontab').where('sBody=?', '{} {} --db_name {} --binlog_id {}'.format(self._python_path,self._binlogModel_py,check_pdata['db_name'],str(check_pdata['id']))).getField('id')
                if check_cron_id:
                    return public.returnMsg(False, '指定的数据库或者表已经存在备份，不能重复添加！')
        pdata['database_table'] = get.datab_name if get.backup_type=='databases' else get.datab_name+'---'+get.table_name
        pdata['backup_type'] = add_type
        pdata['backup_cycle'] = get.backup_cycle
        pdata['cron_type'] = get.cron_type
        pdata['notice'] = get.notice
        if get.notice == '1':
            pdata['notice_channel'] = get.notice_channel
        else:
            pdata['notice_channel'] = ''
        add_time = public.format_date()
        if check_pdata:pdata['zip_password'] = check_pdata['zip_password']
        else:pdata['zip_password'] = get.zip_password
        pdata['start_backup_time'] = add_time
        pdata['end_backup_time'] = add_time
        pdata['last_excute_backup_time'] = add_time
        pdata['table_list'] = '|'.join(self.get_tables_list(self.get_tables()))
        pdata['cron_status'] = 1
        pdata['sync_remote_status']=0
        pdata['sync_remote_time']=0
        pdata['add_time'] = add_time
        pdata['db_name'] = get.datab_name
        pdata['tb_name'] = self._tables = '' if 'table_name' not in get else get.table_name 
        pdata['save_path'] = self.splicing_save_path()
        pdata['temp_path']= ''
        # pdata['upload_local'] = 'localhost'

        #远程存储器参数
        backupTo = '|'
        alioss=ftp=txcos=qiniu=aws=upyun=obs=bos=gcloud_storage=gdrive='|'
        msonedrive=''
        if 'upload_localhost' in get:
            pdata['upload_local'] = get.upload_localhost
            backupTo='localhost|'
        else:
            pdata['upload_local']=''
        if 'upload_alioss' in get:
            pdata['upload_alioss'] = get.upload_alioss
            alioss='alioss|'
        else:
            pdata['upload_alioss']=''
        if 'upload_ftp' in get: 
            pdata['upload_ftp'] = get.upload_ftp
            ftp = 'ftp|'
        else:
            pdata['upload_ftp']=''
        if 'upload_txcos' in get: 
            pdata['upload_txcos'] = get.upload_txcos
            txcos = 'txcos|'
        else:
            pdata['upload_txcos']=''
        if 'upload_qiniu' in get: 
            pdata['upload_qiniu'] = get.upload_qiniu
            qiniu='qiniu|'
        else:
            pdata['upload_qiniu']=''
        if 'upload_aws' in get: 
            pdata['upload_aws'] = get.upload_aws
            aws = 'aws|'
        else:
            pdata['upload_aws']=''
        if 'upload_upyun' in get: 
            pdata['upload_upyun'] = get.upload_upyun
            upyun='upyun|'
        else:
            pdata['upload_upyun']=''
        if 'upload_obs' in get: 
            pdata['upload_obs'] = get.upload_obs
            obs='obs|'
        else:
            pdata['upload_obs']=''
        if 'upload_bos' in get: 
            pdata['upload_bos'] = get.upload_bos
            bos='bos|'
        else:
            pdata['upload_bos']=''
        if 'upload_gcloud_storage' in get: 
            pdata['upload_gcloud_storage'] = get.upload_gcloud_storage
            gcloud_storage='gcloud_storage|'
        else:
            pdata['upload_gcloud_storage']=''
        if 'upload_gdrive' in get: 
            pdata['upload_gdrive'] = get.upload_gdrive
            gdrive='gdrive|'
        else:
            pdata['upload_gdrive']=''
        if 'upload_msonedrive' in get: 
            pdata['upload_msonedrive'] = get.upload_msonedrive
            msonedrive='msonedrive'
        else:
            pdata['upload_msonedrive']=''
        backupTo=backupTo+alioss+ftp+txcos+qiniu+aws+upyun+obs+bos+gcloud_storage+gdrive+msonedrive
        if not is_backup:
            pdata['id'] = public.M('mysqlbinlog_backup_setting').insert(pdata)
        else:
            public.M('mysqlbinlog_backup_setting').where('id=?', int(pdata['id'])).update(pdata)
            time.sleep(0.01)
        #添加到计划任务
        if not check_cron_id:
            self.add_binlog_inc_backup_task(pdata,backupTo)
        return public.returnMsg(True, '添加成功!')

    def modify_mysqlbinlog_backup_setting(self,get):
        """
            @name 更新mysqlbinlog日志增量备份设置
            @auther hezhihong<2022-04-22>
            @param 
            @return 
        """
        public.set_module_logs('binlog','modify_mysqlbinlog_backup_setting')
        if 'backup_id' not in get: return public.returnMsg(False, '错误的参数!')
        if not get.get('backup_cycle/d',0)>0:return public.returnMsg(False, '备份周期不正确，只能为正整数！')
        #检测是否开启binlog日志
        binlog_status = self.get_binlog_status()
        if binlog_status['status'] == False: return public.returnMsg(False, '请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')
        #更新binlog配置信息
        pdata = public.M('mysqlbinlog_backup_setting').where('id=?', get.backup_id).find()
        pdata['backup_cycle'] = get.backup_cycle
        pdata['notice'] = get.notice
        self._db_name = pdata['db_name']
        if get.notice == '1':
            pdata['notice_channel'] = get.notice_channel
        else:
            pdata['notice_channel'] = ''
        #远程存储器参数
        backupTo = '|'
        alioss=ftp=txcos=qiniu=aws=upyun=obs=bos=gcloud_storage=gdrive='|'
        msonedrive=''
        if 'upload_localhost' not in get:
            pdata['upload_local'] = '' 
        else:
            pdata['upload_local'] =get.upload_localhost
            backupTo='localhost|'
        if 'upload_alioss' not in get:
            pdata['upload_alioss'] = '' 
        else:
            pdata['upload_alioss'] =get.upload_alioss
            alioss='alioss|'
        if 'upload_ftp' not in get: 
            pdata['upload_ftp'] =''
        else:
            pdata['upload_ftp'] = get.upload_ftp
            ftp = 'ftp|'
        if 'upload_txcos' not in get: 
             pdata['upload_txcos'] = ''
        else:
            pdata['upload_txcos'] = get.upload_txcos
            txcos = 'txcos|'
        if 'upload_qiniu' not in get: 
            pdata['upload_qiniu'] = ''
        else:
            pdata['upload_qiniu'] = get.upload_qiniu
            qiniu='qiniu|'
        if 'upload_aws' not in get: 
            pdata['upload_aws'] = ''
        else:
            pdata['upload_aws'] = get.upload_aws
            aws = 'aws|'
        if 'upload_upyun' not in get: 
            pdata['upload_upyun'] = ''
        else:
            pdata['upload_upyun'] = get.upload_upyun
            upyun='upyun|'
        if 'upload_obs' not in get: 
            pdata['upload_obs'] = ''
        else:
            pdata['upload_obs'] = get.upload_obs
            obs='obs|'
        if 'upload_bos' not in get: 
            pdata['upload_bos'] = ''
        else:
            pdata['upload_bos'] = get.upload_bos
            bos='bos|'
        if 'upload_gcloud_storage' not in get: 
            pdata['upload_gcloud_storage'] = ''
        else:
            pdata['upload_gcloud_storage'] = get.upload_gcloud_storage
            gcloud_storage='gcloud_storage|'
        if 'upload_gdrive' not in get: 
            pdata['upload_gdrive'] = ''
        else:
            pdata['upload_gdrive'] = get.upload_gdrive
            gdrive='gdrive|'
        if 'upload_msonedrive' not in get: 
            pdata['upload_msonedrive'] = ''
        else:
            pdata['upload_msonedrive'] = get.upload_msonedrive
            msonedrive='msonedrive'
        backupTo=backupTo+alioss+ftp+txcos+qiniu+aws+upyun+obs+bos+gcloud_storage+gdrive+msonedrive
        public.M('mysqlbinlog_backup_setting').where('id=?', int(get.backup_id)).update(pdata)
        #更新计划任务
        if 'cron_id' in get:
            if get.cron_id:
                args = {
                    "id": get.cron_id,
                    "name": public.M('crontab').where("id=?",(get.cron_id,)).getField('name'),
                    "type": pdata['cron_type'],
                    "where1": pdata['backup_cycle'],
                    "hour": '',
                    "minute": '0',
                    "sType":'enterpriseBackup',
                    "sName": pdata['backup_type'],
                    "backupTo": backupTo,
                    "save":pdata['notice'],
                    "save_local":'1',
                    "notice":pdata['notice'],
                    "notice_channel":pdata['notice_channel'],
                    "sBody": public.M('crontab').where("id=?",(get.cron_id,)).getField('sBody'),
                    "urladdress": '{}|{}|{}'.format(pdata['db_name'],pdata['tb_name'],pdata['id'])
                }
                import crontab
                crontab.crontab().modify_crond(args)
                return public.returnMsg(True, '编辑成功!')
            else:
                self.add_binlog_inc_backup_task(pdata,backupTo)
                return public.returnMsg(True, '已恢复计划任务!')
        else:
            self.add_binlog_inc_backup_task(pdata,backupTo)
            return public.returnMsg(True, '已恢复计划任务!')

    def delete_mysql_binlog_setting(self,get):
        """
        @name 删除增量备份设置
        @auther hezhihong<2022-04-29>
        return 
        """
        public.set_module_logs('binlog','delete_mysql_binlog_setting')
        if 'backup_id' not in get and 'cron_id' not in get : return public.returnMsg(False, '不存在此增量备份任务!')
        pdata = ''
        if get.backup_id:
            pdata = public.M('mysqlbinlog_backup_setting').where('id=?', (get.backup_id, )).find()
            self._save_default_path = pdata['save_path']
            self._db_name = pdata['db_name']
        # 删除计划任务
        if 'cron_id' in get and get.cron_id:
            if public.M('crontab').where('id=?', (get.cron_id, )).count():
                args = {"id": get.cron_id}
                import crontab
                crontab.crontab().DelCrontab(args)
        #删除数据库增量备份设置
        if get.type == 'manager' and pdata:
            if public.M('mysqlbinlog_backup_setting').where('id=?', (get.backup_id, )).count():
                public.M('mysqlbinlog_backup_setting').where('id=?', (get.backup_id,)).delete()
            full_record_file = pdata['save_path']+'full_record.json'
            inc_record_file = pdata['save_path']+'inc_record.json'
            if os.path.isfile(full_record_file):self.clean_local_full_backups(full_record_file)
            if os.path.isfile(inc_record_file):self.clean_local_inc_backups(inc_record_file)
            info_count = public.M('mysqlbinlog_backups').where('sid=?', get.backup_id).select()
            for clean_info in info_count:
                if not clean_info:continue
                if 'id' not in clean_info:continue
                public.M('mysqlbinlog_backups').delete(clean_info['id'])
        return public.returnMsg(True, '删除成功')

    def get_inc_size(self,file_name):
        """
        @name 取增备大小
        @auther hezhihong<2022-04-29>
        @param file_name 文件名
        @return int size
        """ 
        size = 0
        if os.path.isfile(file_name):
            try:
                inc_info = json.loads(public.readFile(file_name))
                for g in inc_info:
                    size += int(g['size'])
            except:
                size = 0
        return size

    def get_time_size(self,file_name,database_info):
        """
        @name 取时间和全备大小
        @auther hezhihong<2022-04-29>
        @return database_info
        """
        
        tb_info = json.loads(public.readFile(file_name))[0]
        database_info['start_time'] = tb_info['time']
        if 'end_time' in tb_info:
            database_info['end_time']=tb_info['end_time']
            database_info['excute_time']=tb_info['end_time']
        else:
            database_info['end_time']=tb_info['time']
            database_info['excute_time']=tb_info['time']
        database_info['full_size'] = tb_info['size']
        return database_info

    def get_database_info(self,get=None):
        """
        @name 取所有数据库备份信息
        @auther hezhihong<2022-04-29>
        @return backup_info 所有数据库和所有数据库表的备份信息
        """
        databases = self.get_databases()
        backup_info = {}
        backup_database = []
        backup_table = []
        if databases:
            for i in databases:
                if not i:continue
                database_info = {}
                self._db_name=database_info['name'] = i['name']
                db_tmp_path = self._save_default_path+i['name']+'/databases/'
                tb_tmp_path = self._save_default_path+i['name']+'/tables/'
                db_full_file = db_tmp_path+'full_record.json'
                db_inc_file = db_tmp_path+'inc_record.json'
                database_info['inc_size'] =0 if not os.path.isfile(db_inc_file) else self.get_inc_size(db_inc_file)
                #取数据库备份信息
                pdata = public.M('mysqlbinlog_backup_setting').where('db_name=? and backup_type=?', (str(i['name']),'databases')).find()
                if pdata: 
                    database_info['cron_id'] = public.M('crontab').where('name=?', '[勿删]数据库增量备份[{}]'.format(pdata['db_name'])).getField('id')
                    database_info['backup_id'] = pdata['id']
                    database_info['upload_localhost']=pdata['upload_local']
                    database_info['upload_alioss'] = pdata['upload_alioss'] 
                    database_info['upload_ftp'] = pdata['upload_ftp']
                    database_info['upload_txcos'] = pdata['upload_txcos']
                    database_info['upload_qiniu'] = pdata['upload_qiniu']
                    database_info['upload_obs'] = pdata['upload_obs']
                    database_info['upload_bos'] = pdata['upload_bos']
                    database_info['backup_cycle'] = pdata['backup_cycle']
                    database_info['notice'] = pdata['notice']
                    database_info['notice_channel'] = pdata['notice_channel']
                    database_info['zip_password']=pdata['zip_password']

                    database_info['start_time'] = pdata['start_backup_time']
                    database_info['end_time'] = pdata['end_backup_time'] 
                    database_info['excute_time'] = pdata['last_excute_backup_time']
                else:
                    database_info['cron_id']=database_info['backup_id']=database_info['notice']=database_info['upload_alioss']=database_info['backup_cycle']=database_info['zip_password']=None
                    database_info['upload_localhost']=database_info['upload_alioss']=database_info['upload_ftp'] = database_info['upload_txcos'] = database_info['upload_qiniu'] = database_info['upload_obs'] = database_info['upload_bos'] = ''
                #兼容已删除增量备份信息情况
                if os.path.isfile(db_full_file):
                    database_info=self.get_time_size(db_full_file,database_info)
                    if pdata:database_info['excute_time']=pdata['last_excute_backup_time']
                    database_info['full_size']=public.to_size(database_info['full_size']+database_info['inc_size'])
                    backup_database.append(database_info)
                #兼容不保留本地设置情况取备份大小
                else: 
                    if pdata:
                        database_info['full_size']=0
                        #从备份包记录表取完全备份大小
                        count_info = public.M('mysqlbinlog_backups').where('sid=?', pdata['id']).select()
                        for file_size in count_info:
                            if not file_size:continue
                            if 'size' not in file_size:continue
                            database_info['full_size']+=file_size['size']
                        database_info['full_size']=public.to_size(database_info['full_size'])
                        backup_database.append(database_info)
                #取表备份信息
                pdata = public.M('mysqlbinlog_backup_setting').where('db_name=? and backup_type=?', (str(i['name']),'tables')).select()
                table_data = {}
                table_data['name'] = i['name']
                data = []
                tables = self.get_tables_list(self.get_tables())
                for c in tables:
                    if not tables:continue
                    c_pdata = public.M('mysqlbinlog_backup_setting').where('db_name=? and tb_name=? ', (self._db_name,c)).find()
                    tb_full_file = tb_tmp_path+c+'/full_record.json'
                    tb_inc_file = tb_tmp_path+c+'/inc_record.json'
                    database_info = {}
                    database_info['name']=c
                    # database_info['inc_size'] = public.to_size(self.get_inc_size(tb_inc_file))
                    database_info['inc_size'] = self.get_inc_size(tb_inc_file)
                    #存在增备信息取参数
                    if c_pdata: 
                        database_info['cron_id'] = public.M('crontab').where('sBody=?', '{} {} --db_name {} --binlog_id {}'.format(self._python_path,self._binlogModel_py,c_pdata['db_name'],str(c_pdata['id']))).getField('id')
                        database_info['backup_id'] = c_pdata['id']
                        database_info['upload_localhost']=c_pdata['upload_local']
                        database_info['upload_alioss'] = c_pdata['upload_alioss'] 
                        database_info['backup_cycle'] = c_pdata['backup_cycle']
                        database_info['notice'] = c_pdata['notice']
                        database_info['notice_channel'] = c_pdata['notice_channel']
                        database_info['excute_time']=c_pdata['last_excute_backup_time']
                        database_info['zip_password']=c_pdata['zip_password']
                        database_info['upload_ftp'] = c_pdata['upload_ftp']
                        database_info['upload_txcos'] = c_pdata['upload_txcos']
                        database_info['upload_qiniu'] = c_pdata['upload_qiniu']
                        database_info['upload_obs'] = c_pdata['upload_obs']
                        database_info['upload_bos'] = c_pdata['upload_bos']
                    #不存在增备信息取参数
                    else:
                        database_info['cron_id']=database_info['backup_id']=database_info['notice']=database_info['upload_alioss']=database_info['backup_cycle']=database_info['zip_password']=None
                        database_info['upload_localhost']=database_info['upload_alioss']=database_info['upload_ftp'] = database_info['upload_txcos'] = database_info['upload_qiniu'] = database_info['upload_obs'] = database_info['upload_bos'] = ''
                    #从文件信息获取
                    if os.path.isfile(tb_full_file):
                        database_info=self.get_time_size(tb_full_file,database_info)
                        if c_pdata:database_info['excute_time']=c_pdata['last_excute_backup_time']
                        database_info['full_size']=public.to_size(database_info['full_size']+database_info['inc_size'])
                        data.append(database_info)
                    #兼容不保留本地设置情况取备份大小
                    else:
                        if not c_pdata:continue
                        database_info['start_time'] = c_pdata['start_backup_time']
                        database_info['end_time'] = c_pdata['end_backup_time']
                        database_info['excute_time'] = c_pdata['last_excute_backup_time'] 
                        # database_info['full_size']=public.to_size(database_info['inc_size'])
                        # data.append(database_info)


                        database_info['full_size']=0
                        #从备份包记录表取完全备份大小
                        count_info = public.M('mysqlbinlog_backups').where('sid=?', c_pdata['id']).select()
                        for tb_size in count_info:
                            if not tb_size:continue
                            if 'size' not in tb_size:continue
                            database_info['full_size']+=tb_size['size']
                        database_info['full_size']=public.to_size(database_info['full_size'])
                        data.append(database_info)
                if data:
                    table_data['data'] = data
                    backup_table.append(table_data)
        backup_info['databases'] = backup_database
        backup_info['tables'] = backup_table
        return public.returnMsg(True, backup_info)

    def get_databases_info(self,get):
        """
        @name 取所有数据库备份信息
        @auther hezhihong<2022-04-30>
        """
        temp_data = self.get_database_info()
        data = []
        for i in temp_data['msg']['databases']:
            i['type'] ='databases'
            data.append(i)
        return self.get_page(data, get)

    def get_specified_database_info(self,get):
        """
        @name 取指定数据库内所有表备份信息
        @auther hezhihong<2022-04-30>
        """
        temp_data = self.get_database_info()
        data = []
        type_one = ['databases','all']
        type_two = ['tables','all']
        for i in temp_data['msg']['databases']:
            if i['name'] == get.datab_name:
                i['type'] ='databases'
                if hasattr(get,'type') and get.type not in type_one: continue
                data.append(i)
        for i in temp_data['msg']['tables']:
            if i['name'] == get.datab_name:
                for h in i['data']: 
                    h['type'] = 'tables'
                    if hasattr(get,'type') and get.type not in type_two: continue
                    data.append(h)
        return self.get_page(data, get)


    def get_page(self, data, get):
        """
        @name 取分页
        @return 指定分页数据
        """
        # 包含分页类
        import page
        # 实例化分页类
        page = page.Page()

        info = {}
        info['count'] = len(data)
        info['row'] = 10
        info['p'] = 1
        if hasattr(get, 'p'):
            info['p'] = int(get['p'])
        info['uri'] = {}
        info['return_js'] = ''
        # 获取分页数据
        result = {}
        result['page'] = page.GetPage(info, limit='1,2,3,4,5,8')
        n = 0
        result['data'] = []
        for i in range(info['count']):
            if n >= page.ROW: break
            if i < page.SHIFT: continue
            n += 1
            result['data'].append(data[i])
        return result


    def delete_file(self,filename):
        """
            @name 删除文件
            @auther hezhihong<2022-04-25>
            @param filename 需要删除的文件名
        """
        if os.path.exists(filename):
            os.remove(filename)

    def send_failture_notification(self, error_msg, target="", remark=""):
        """
        @name 备份失败发送消息通知
        @param error_msg 错误信息
        :remark 备注
        """
        cron_title = '数据库增量备份[ {} ]'.format(target)
        notice = self._pdata['notice']
        notice_channel = self._pdata['notice_channel']
        if notice in [0,'0'] or not notice_channel:
            return
        if notice in [1,'1',2,'2']:
            title = "宝塔计划任务备份失败提醒"
            task_name = cron_title 
            msg = self._mybackup.generate_failture_notice(task_name, error_msg, remark)
            res = self._mybackup.send_notification(notice_channel, title, msg)
            if res:
                print('|-消息通知已发送。')
    
    def sync_date(self):
        """
        @name 同步服务器时间
        """
        import config
        config.config().syncDate(None)



# ==========================云存储相关方法==========================
def set_config(self, get):
    """
    @name 设置云存储参数
    """

#阿里云OSS
class alioss_main:
    __oss = None
    __error_count = 0
    def __conn(self):
        """
            @name 构建鉴权对象
            @auther hezhihong<2022-04-25>
        """
        if self.__oss: return
        # 获取阿里云秘钥
        keys = self.get_config()

        self.__bucket_name = keys[2]
        if keys[3].find(keys[2]) != -1: keys[3] = keys[3].replace(keys[2] + '.', '')
        self.__bucket_domain = keys[3]
        self.__bucket_path = main().get_path(keys[4] + '/bt_backup/')
        if self.__bucket_path[:1] == '/': self.__bucket_path = self.__bucket_path[1:]

        try:
            # 构建鉴权对象
            self.__oss = oss2.Auth(keys[0], keys[1])
        except Exception as ex:
            pass
            # print(str(ex))

    def get_config(self):
        """
            @name 取配置密钥信息
            @auther hezhihong<2022-04-25>
            @return 以|为连接的密钥信息
        """
        path = main()._config_path + '/alioss.conf'
        #从阿里云存储插件配置取配置密钥信息
        if not os.path.isfile(path):
            file_name = ''
            if os.path.isfile(main()._plugin_path+'alioss/config.conf'):
                file_name = main()._plugin_path+'alioss/config.conf'
            elif os.path.isfile(main()._setup_path+'data/aliossAS.conf'):
                file_name=main()._setup_path+'data/aliossAS.conf'
            oss_info=None
            if os.path.isfile(file_name):
                try:
                    oss_info = json.loads(public.readFile(main()._setup_path+'data/aliossAS.conf'))
                except:
                    pass
                if 'access_key' not in oss_info or 'secret_key' not in oss_info or 'bucket_name' not in oss_info or 'bucket_domain' not in oss_info:oss_info=None
                if oss_info:
                    add_str = oss_info['access_key']+'|'+oss_info['secret_key']+'|'+oss_info['bucket_name']+'|'+oss_info['bucket_domain']+'|'+oss_info['backup_path']
                    public.writeFile(path, add_str)
        if not os.path.isfile(path): return ['', '', '', '', '/']
        conf = public.readFile(path)
        # print(conf)
        if not conf: return ['', '', '', '', '/']
        result = conf.split('|')
        if len(result) < 5: result.append('/')
        return result
        
    

    def check_config(self):
        """
            @name 检测alioss是否可用
            @auther hezhihong<2022-04-25>
            @return True 或者 False
        """ 
        try:
            self.__conn()

            from itertools import islice
            bucket = oss2.Bucket(self.__oss, self.__bucket_domain, self.__bucket_name)
            result = oss2.ObjectIterator(bucket)
            data = []
            path = '/'
            '''key, last_modified, etag, type, size, storage_class'''
            for b in islice(oss2.ObjectIterator(bucket, delimiter='/', prefix='/'), 1000):
                b.key = b.key.replace('/', '')
                if not b.key: continue
                tmp = {}
                tmp['name'] = b.key
                tmp['size'] = b.size
                tmp['type'] = b.type
                tmp['download'] = self.download_file(path + b.key, False)
                tmp['time'] = b.last_modified
                data.append(tmp)
            return True
        except:
            return False

    def get_list(self,get=None):
        """
            @name 取云存储文件列表
            @auther hezhihong<2022-04-25>
            @return 文件列表信息
        """ 
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            from itertools import islice
            bucket = oss2.Bucket(self.__oss, self.__bucket_domain, self.__bucket_name)
            result = oss2.ObjectIterator(bucket)
            data = []
            path = main().get_path(get.path)
            '''key, last_modified, etag, type, size, storage_class'''
            for b in islice(oss2.ObjectIterator(bucket, delimiter='/', prefix=path), 1000):
                b.key = b.key.replace(path, '')
                if not b.key: continue
                tmp = {}
                tmp['name'] = b.key
                tmp['size'] = b.size
                tmp['type'] = b.type
                tmp['download'] = self.download_file(path + b.key)
                tmp['time'] = b.last_modified
                data.append(tmp)
            mlist = {}
            mlist['path'] = get.path
            mlist['list'] = data
            return mlist
        except Exception as ex:
            return public.returnMsg(False, str(ex))

    def upload_file_by_path(self, filename, bucket_path):
        """
            @name 上传文件到指定目录
            @auther hezhihong<2022-04-25>
            @param filename 上传的文件名，不包含路径
            @param bucket_path 云存储保存路径 
            @return 文件列表信息
        """ 
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False
        try:
            # 保存的文件名
            key = main().get_path(os.path.dirname(bucket_path))+os.path.basename(bucket_path)
            # 获取存储对象
            try:
                print('|-正在上传{}到阿里云OSS'.format(filename),end='')
                bucket = oss2.Bucket(self.__oss, self.__bucket_domain, self.__bucket_name)
                # 使用断点续传
                oss2.defaults.connection_pool_size = 4
                result = oss2.resumable_upload(bucket, key, filename,
                                            store=oss2.ResumableStore(root='/tmp'),  # 进度保存目录
                                            multipart_threshold=1024 * 1024 * 2,
                                            part_size=1024 * 1024,  # 分片大小
                                            num_threads=1)  # 线程数
                print(' ==> 成功')
            except:
                print('|-无法上传{}到阿里云OSS！请检查阿里云OSS配置是否正确！'.format(filename))
            
            # print('上传文件到阿里云OSS返回结果：', result)
            # 
            return True
        except Exception as ex:
            print(ex)
            if ex.status == 403:
                time.sleep(5)
                self.__error_count += 1
                if self.__error_count < 2:  # 重试2次
                    # main().sync_date()
                    self.upload_file_by_path(filename, bucket_path)
            return False

    def download_file(self, filename):
        """
            @name 下载文件
            @auther hezhihong<2022-04-25>
            @param filename 需要下载的文件名 
            @return 下载url
        """ 
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return None
        try:
            bucket = oss2.Bucket(self.__oss, self.__bucket_domain, self.__bucket_name)
            private_url = bucket.sign_url('GET', filename, 3600)
            return private_url
        except:
            print(self.__error_msg)
            return None

    def alioss_delete_file(self,filename):
        """
            @name 删除阿里云存储文件
            @auther hezhihong<2022-04-25>
            @param filename 需要删除的文件名 
            @return 删除的状态
        """ 
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            bucket = oss2.Bucket(self.__oss, self.__bucket_domain, self.__bucket_name)
            result = bucket.delete_object(filename)
            return result.status
        except Exception as ex:
            if ex.status == 403:
                self.__error_count += 1
                if self.__error_count < 2:
                    # main().sync_date()
                    self.alioss_delete_file(filename)

            print('删除失败!')
            return None

    def remove_file(self, get):
        """
            @name 删除文件前端调用方法
            @auther hezhihong<2022-04-25>
            @param get.path 删除文件的路径，不包含文件名
            @param get.filename 删除文件名，不包含路径
            @return 删除的状态
        """ 
        path = main().get_path(get.path)
        filename = path + get.filename
        self.alioss_delete_file(filename)
        return public.returnMsg(True, '删除文件成功!{}----{}'.format(path,filename))

#腾讯云COS
class txcos_main:
    __oss = None
    __bucket_path = None
    __error_count = 0
    __secret_id = None
    __secret_key = None
    __region = None
    __Bucket = None
    __error_msg = "ERROR: 无法连接腾讯云COS !"


    def __init__(self):
        self.__conn()

    def __conn(self):
        """
        @name 构建鉴权对象
        """
        if self.__oss: return

        keys = self.get_config()
        self.__secret_id = keys[0]
        self.__secret_key = keys[1]
        self.__region = keys[2]
        self.__Bucket = keys[3]
        self.__bucket_path = main().get_path(keys[4])
        try:
            config = CosConfig(Region=self.__region, SecretId=self.__secret_id, SecretKey=self.__secret_key, Token=None, Scheme='http')
            self.__oss = CosS3Client(config)
        except Exception as ex:
            pass
            # print(self.__error_msg, str(ex))


    def get_config(self, get=None):
        """
        @name 设置腾讯云COS密码信息
        """
        path = main()._config_path + '/txcos.conf'
        #从腾讯云COS插件配置取配置密钥信息
        if not os.path.isfile(path):
            file_name = ''
            if os.path.isfile(main()._plugin_path+'txcos/config.conf'):
                file_name=main()._plugin_path+'txcos/config.conf'
            elif os.path.isfile(main()._setup_path+'data/txcosAS.conf'):
                file_name=main()._setup_path+'data/txcosAS.conf'
            file_name =file_name.replace('//', '/')
            oss_info=None
            if os.path.isfile(file_name):
                try:
                    oss_info = json.loads(public.readFile(file_name))
                except:
                    pass
                if 'access_key' not in oss_info or 'secret_key' not in oss_info or 'bucket_name' not in oss_info or 'bucket_domain' not in oss_info:oss_info=None
                if oss_info:
                    add_str = oss_info['secret_id']+'|'+oss_info['secret_key']+'|'+oss_info['region']+'|'+oss_info['bucket_name']+'|'+oss_info['backup_path']
                    public.writeFile(path, add_str)
        if not os.path.isfile(path): return ['', '', '', '', '/']
        conf = public.readFile(path)
        if not conf: return ['', '', '', '', '/']
        result = conf.split('|')
        if len(result) < 5: result.append('/')
        return result
        
        

    # 检测txcos是否可用
    def check_config(self):
        try:
            data = []
            dir_list = []
            path = self.__bucket_path + main().get_path('/')
            response = self.__oss.list_objects(Bucket=self.__Bucket, MaxKeys=100, Delimiter='/', Prefix=path)
            return True
        except:
            return False

    def upload_file(self, filename):
        """
        @name 上传文件
        @param filename 上传的文件名
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            # 断点续传
            filepath, key = os.path.split(filename)
            key = self.__bucket_path + key
            # 短点续传
            response = self.__oss.upload_file(
                Bucket=self.__Bucket,
                Key=key,
                MAXThread=10,
                PartSize=5,
                LocalFilePath=filename)
        except:
            time.sleep(1)
            self.__error_count += 1
            if self.__error_count < 2:  # 重试2次
                # main().sync_date()
                self.upload_file(filename)
            print(self.__error_msg)
            return None


    def upload_file_by_path(self, filename, bucket_path):
        """
        @name 上传文件
        @param filename 上传的文件名
        @param bucket_path 腾讯云cos保存的文件名
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            print('|-正在上传{}到腾讯云COS'.format(filename),end='')
            filepath, key = os.path.split(filename)
            self.__bucket_path = main().get_path(os.path.dirname(bucket_path))
            key = self.__bucket_path + '/' + key
            # print(key)
            # 断点续传
            response = self.__oss.upload_file(Bucket=self.__Bucket, Key=key, MAXThread=10, PartSize=5, LocalFilePath=filename)
            # print(u'上传文件到腾讯云COS返回结果：', response)
            print(' ==> 成功')
            return True
        except Exception as ex:
            # print(ex)
            time.sleep(1)
            self.__error_count += 1
            if self.__error_count < 2:  # 重试2次
                # main().sync_date()
                self.upload_file_by_path(filename, bucket_path)
            return False


    def create_dir(self, get=None):
        """
        @name 创建目录
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        path = main().get_path(get.path + get.dirname)
        filename = '/tmp/dirname.pl'
        public.writeFile(filename, '')
        response = self.__oss.put_object(Bucket=self.__Bucket, Body=b'', Key=path)
        os.remove(filename)
        return public.returnMsg(True, '创建成功!')

    def get_list(self, get=None):
        """
        @name 取文件列表信息
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            data = []
            dir_list = []
            path = main().get_path(get.path)
            if 'Contents' in self.__oss.list_objects(Bucket=self.__Bucket, MaxKeys=100, Delimiter='/', Prefix=path):
                for b in self.__oss.list_objects(Bucket=self.__Bucket, MaxKeys=100, Delimiter='/', Prefix=path)['Contents']:
                    tmp = {}
                    b['Key'] = b['Key'].replace(path, '')
                    if not b['Key']: continue
                    tmp['name'] = b['Key']
                    tmp['size'] = b['Size']
                    tmp['type'] = b['StorageClass']
                    tmp['download'] = self.download_file(path + b['Key'])
                    tmp['time'] = b['LastModified']
                    data.append(tmp)
            else:
                pass
            if 'CommonPrefixes' in self.__oss.list_objects(Bucket=self.__Bucket, MaxKeys=100, Delimiter='/', Prefix=path):
                for i in self.__oss.list_objects(Bucket=self.__Bucket, MaxKeys=100, Delimiter='/', Prefix=path)['CommonPrefixes']:
                    if not i['Prefix']: continue
                    dir_dir = i['Prefix'].split('/')[-2] + '/'
                    dir_list.append(dir_dir)
            else:
                pass
            mlist = {}
            mlist['path'] = get.path
            mlist['list'] = data
            mlist['dir'] = dir_list
            return mlist
        except:
            mlist = {}
            if self.__oss:
                mlist['status'] = True
            else:
                mlist['status'] = False
            mlist['path'] = get.path
            mlist['list'] = data
            mlist['dir'] = dir_list
            return mlist

    def download_file(self, filename, Expired=300):
        """
        @name 下载文件
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return None
        try:
            response = self.__oss.get_presigned_download_url(Bucket=self.__Bucket, Key=filename)
            response = re.findall('([^?]*)?.*', response)[0]
            return response
        except:
            print(self.__error_msg)
            return None

    def delete_file(self, filename):
        """
        @ name 删除文件
        @param filename 需要删除的文件名
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            response = self.__oss.delete_object(Bucket=self.__Bucket, Key=filename)
            return response
        except Exception as ex:
            self.__error_count += 1
            if self.__error_count < 2:
                # main().sync_date()
                self.delete_file(filename)
            print(self.__error_msg)
            return None

    # 删除文件
    def remove_file(self, get):
        path = main().get_path(get.path)
        filename = path + get.filename
        self.delete_file(filename)
        return public.returnMsg(True, '删除文件成功!')

#ftp存储空间
class ftp_main:
    __path = '/'

    def __init__(self):
        self.__path = self.get_config(None)[3]

    def get_config(self, get=None):
        path = main()._config_path + '/ftp.conf'
        #从FTP存储空间插件配置取配置密钥信息
        if not os.path.isfile(path):
            file_name = ''
            if os.path.isfile(main()._plugin_path+'ftp/config.conf'):
                file_name=main()._plugin_path+'ftp/config.conf'
            elif os.path.isfile(main()._setup_path+'data/ftpAS.conf'):
                file_name=main()._setup_path+'data/ftpAS.conf'
            file_name =file_name.replace('//', '/')
            oss_info=None
            if os.path.isfile(file_name):
                try:
                    oss_info = json.loads(public.readFile(file_name))
                except:
                    pass
                if 'ftp_host' not in oss_info or 'ftp_user' not in oss_info or 'ftp_pass' not in oss_info or 'backup_path' not in oss_info:oss_info=None
                if oss_info:
                    add_str = oss_info['ftp_host']+'|'+oss_info['ftp_user']+'|'+oss_info['ftp_pass']+'|'+oss_info['backup_path']
                    public.writeFile(path, add_str)
        if not os.path.exists(path): return ['', '', '', '/']
        conf = public.readFile(path)
        if not conf: return ['', '', '', '/']
        return conf.split('|')
        

    def set_config(self, get):
        path = main()._config_path + '/ftp.conf'
        conf = get.ftp_host + '|' + get.ftp_user + '|' + get.ftp_pass + '|' + get.ftp_path
        public.writeFile(path, conf)
        return public.returnMsg(True, '设置成功!')

    # 连接FTP
    def connentFtp(self):
        from ftplib import FTP
        tmp = self.get_config()
        if tmp[0].find(':') == -1: tmp[0] += ':21'
        host = tmp[0].split(':')
        if host[1] == '': host[1] = '21'
        ftp = FTP()
        ftp.set_debuglevel(0)
        ftp.connect(host[0], int(host[1]))
        ftp.login(tmp[1], tmp[2])
        if self.__path != '/':
            self.dirname = self.__path
            self.path = '/'
            self.createDir(self, ftp)
        ftp.cwd(self.__path)
        return ftp

    # 检测ftp是否可用
    def check_config(self):
        try:
            ftp = self.connentFtp()
            if ftp: return True
        except:
            return False

    # 创建目录
    def createDir(self, get, ftp=None):
        try:
            if not ftp: ftp = self.connentFtp()
            dirnames = get.dirname.split('/')
            ftp.cwd(get.path)
            for dirname in dirnames:
                if not dirname: continue
                if not dirname in ftp.nlst(): ftp.mkd(dirname)
                ftp.cwd(dirname)
            return public.returnMsg(True, '目录创建成功!')
        except:
            return public.returnMsg(False, '目录创建失败!')

    # 上传文件
    def updateFtp(self, filename):
        try:
            ftp = self.connentFtp()
            bufsize = 1024
            file_handler = open(filename, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(filename), file_handler, bufsize)
            file_handler.close()
            ftp.quit()
        except:
            if os.path.exists(filename): os.remove(filename)
            print('连接服务器失败!')
            return {'status': False, 'msg': '连接服务器失败!'}

    # 上传文件到指定目录
    def upload_file_by_path(self, filename, back_path):
        try:
            ftp = self.connentFtp()
            root_path = self.get_config(None)[3]
            get = public.dict_obj()
            if back_path[0] == "/":
                back_path = back_path[1:]
            get.path = root_path
            get.dirname = os.path.dirname(back_path)
            self.createDir(get)
            target_path = os.path.join(root_path,os.path.dirname(back_path))
            print("目标上传目录：{}".format(target_path))
            ftp.cwd(target_path)
            bufsize = 1024
            file_handler = open(filename, 'rb')
            try:
                ftp.storbinary('STOR %s' % target_path+'/'+os.path.basename(filename), file_handler, bufsize)
            except:
                ftp.storbinary('STOR %s' % os.path.split(filename)[1], file_handler, bufsize)
            file_handler.close()
            ftp.quit()
            return True
        except:
            print(public.get_error_info())
            return False

    # 从FTP删除文件
    def deleteFtp(self, filename,is_inc = False):
        delete_full_info =[]
        if os.path.isfile(main()._full_file): 
            try:
                delete_full_info = json.loads(public.readFile(main()._full_file))[0]
            except:
                delete_full_info =[]
        try:
            ftp = self.connentFtp()
            if is_inc:
                try:
                    result = ftp.nlst()
                    # print('result:')
                    # print(result)
                    # data = []
                    # for tf in result:
                    #     if tf == '.' or tf == '..': continue
                    #     data.append(tf)
                    # print('data:')
                    # print(data)
                    for df in result:
                        if df == '.' or df == '..': continue
                        if df == 'full_record.json':continue
                        if delete_full_info and 'full_name' in delete_full_info and os.path.basename(delete_full_info['full_name'])==df:continue
                        try:
                            ftp.rmd(df)
                        except:
                            ftp.delete(df)
                        print('|-已从FTP存储空间清理过期备份文件{}'.format(df))
                    return True
                except Exception as exx:
                    print(exx)
                    return False
            try:
                ftp.rmd(filename)
            except:
                ftp.delete(filename)
            print('|-已从FTP存储空间清理过期备份文件{}'.format(filename))
            return True
        except Exception as ex:
            print(ex)
            return False

    # 删除文件或目录
    def remove_file(self, get):
        root_path = self.get_config(None)[3]
        if get.path[0] == "/":
            get.path = get.path[1:]
        self.__path = os.path.join(root_path, get.path)
        if 'is_inc' not in get and self.deleteFtp(get.filename):
            return public.returnMsg(True, '删除成功!')
        if 'is_inc' in get and get.is_inc:
            if self.deleteFtp(get.filename,True):
                return public.returnMsg(True, '删除成功!')
        return public.returnMsg(False, '删除失败!')

    # 获取列表
    def get_list(self, get=None):
        try:
            self.__path = get.path
            ftp = self.connentFtp()
            result = ftp.nlst()

            dirs = []
            files = []
            data = []
            for dt in result:
                if dt == '.' or dt == '..': continue
                sfind = public.M('backup').where('name=?', (dt,)).field('size,addtime').find()
                if not sfind:
                    sfind = {}
                    sfind['addtime'] = '1970/01/01 00:00:01'
                tmp = {}
                tmp['name'] = dt
                tmp['time'] = int(time.mktime(time.strptime(sfind['addtime'], '%Y/%m/%d %H:%M:%S')))
                try:
                    tmp['size'] = ftp.size(dt)
                    tmp['dir'] = False
                    tmp['download'] = self.getFile(dt)
                    files.append(tmp)
                except:
                    tmp['size'] = 0
                    tmp['dir'] = True
                    tmp['download'] = ''
                    dirs.append(tmp)

            data = dirs + files
            mlist = {}
            mlist['path'] = self.__path
            mlist['list'] = data
            return mlist
        except Exception as ex:
            return {'status': False, 'msg': str(ex)}

    # 获取文件地址
    def getFile(self, filename):
        try:
            tmp = self.get_config()
            if tmp[0].find(':') == -1: tmp[0] += ':21'
            host = tmp[0].split(':')
            if host[1] == '': host[1] = '21'
            url = 'ftp://' + tmp[1] + ':' + tmp[2] + '@' + host[0] + ':' + host[1] + (self.__path + '/' + filename).replace('//', '/')
        except:
            url = None
        return url

    # 获取文件地址2
    def download_file(self, filename):
        return self.getFile(filename)


#七牛云存储
class qiniu_main:
    __oss = None
    __bucket_name = None
    __bucket_domain = None
    __bucket_path = None
    __error_msg = "ERROR: 无法连接到七牛云OSS服务器，请检查[AccessKeyId/AccessKeySecret]设置是否正确!"

    def __init__(self):
        self.__conn()

    def __conn(self):
        if self.__oss: return
        # 获取秘钥
        keys = self.get_config()

        self.__bucket_name = keys[2]
        if keys[3].find(keys[2]) != -1: keys[3] = keys[3].replace(keys[2] + '.', '')
        self.__bucket_domain = keys[3]
        self.__bucket_path = main().get_path(keys[4] + '/bt_backup/')
        if self.__bucket_path[:1] == '/': self.__bucket_path = self.__bucket_path[1:]

        try:
            # 构建鉴权对象
            self.__oss = Auth(keys[0], keys[1])
        except Exception as ex:
            pass
            # print(self.__error_msg, str(ex))

    def get_config(self, get=None):
        path = main()._config_path + '/qiniu.conf'
        #从七牛云存储插件配置取配置密钥信息
        if not os.path.isfile(path):
            file_name = ''
            if os.path.isfile(main()._plugin_path+'qiniu/config.conf'):
                file_name = main()._plugin_path+'qiniu/config.conf'
            elif os.path.isfile(main()._setup_path+'data/qiniuAS.conf'):
                file_name = main()._setup_path+'data/qiniuAS.conf'
            file_name =file_name.replace('//', '/')
            oss_info=None
            if os.path.isfile(file_name):
                try:
                    oss_info = json.loads(public.readFile(file_name))
                except:
                    pass
                if 'access_key_id' not in oss_info or 'access_key_secret' not in oss_info or 'bucket_name' not in oss_info or 'bucket_domain' not in oss_info:oss_info=None
                if oss_info:
                    add_str = oss_info['access_key_id']+'|'+oss_info['access_key_secret']+'|'+oss_info['bucket_name']+'|'+oss_info['bucket_domain']+'|'+oss_info['backup_path']
                    public.writeFile(path, add_str)
        if not os.path.isfile(path): return ['', '', '', '', '/']
        conf = public.readFile(path)
        if not conf: return ['', '', '', '', '/']
        result = conf.split('|')
        if len(result) < 5: result.append('/')
        return result
        
        

    def set_config(self, get):
        check_list = ['qiniu','txcos','alioss','bos','ftp','obs']
        cloud_name = get.get('cloud_name/d',0)
        print(cloud_name)
        if cloud_name not in check_list:return public.returnMsg(False,'参数不合法！')
        path = main()._config_path + '/{}.conf'.format(cloud_name)
        # path = main()._config_path + '/qiniu.conf'
        conf = get.access_key.strip() + '|' + get.secret_key.strip() + '|' + get.bucket_name.strip() + '|' + get.bucket_domain.strip() + '|' + get.bucket_path.strip()
        # public.writeFile(path, conf)
        return public.returnMsg(True, '设置成功!')

    # 检测是否可用
    def check_config(self):
        try:
            path = ''
            bucket = self.get_bucket()
            delimiter = '/'
            marker = None
            limit = 1000
            path = main().get_path(path)
            ret, eof, info = bucket.list(self.__bucket_name, path, marker, limit, delimiter)
            if ret:
                return True
            else:
                return False
        except:
            return False

    def get_bucket(self):
        """获取存储空间"""

        from qiniu import BucketManager
        bucket = BucketManager(self.__oss)
        return bucket

    def create_dir(self, dir_name):
        """创建远程目录

        :param dir_name: 目录名称
        :return:
        """

        try:
            dir_name = main().get_path(dir_name)
            local_file_name = '/tmp/dirname.pl'
            public.writeFile(local_file_name, '')
            token = self.__oss.upload_token(self.__bucket_name, dir_name)
            ret, info = put_file(token, dir_name, local_file_name)

            try:
                os.remove(local_file_name)
            except:
                pass

            if info.status_code == 200:
                return True
            return False
        except Exception as e:
            raise RuntimeError("创建目录出现错误:" + str(e))

    def get_list(self, get=None):
        bucket = self.get_bucket()
        delimiter = '/'
        marker = None
        limit = 1000
        path = main().get_path(get.path)
        ret, eof, info = bucket.list(self.__bucket_name, path, marker, limit, delimiter)
        data = []
        if ret:
            commonPrefixes = ret.get("commonPrefixes")
            if commonPrefixes:
                for prefix in commonPrefixes:
                    tmp = {}
                    key = prefix.replace(path, '')
                    tmp['name'] = key
                    tmp['type'] = None
                    data.append(tmp)

            items = ret['items']
            for item in items:
                tmp = {}
                key = item.get("key")
                key = key.replace(path, '')
                if not key:
                    continue
                tmp['name'] = key
                tmp['size'] = item.get("fsize")
                tmp['type'] = item.get("type")
                tmp['time'] = item.get("putTime")
                tmp['download'] = self.generate_download_url(path + key)
                data.append(tmp)
        else:
            if hasattr(info, "error"):
                raise RuntimeError(info.error)
        mlist = {'path': path, 'list': data}
        return mlist

    def generate_download_url(self, object_name, expires=60 * 60):
        """生成时效下载链接"""
        domain = self.__bucket_domain
        base_url = 'http://%s/%s' % (domain, object_name)
        timestamp_url = self.__oss.private_download_url(base_url, expires=expires)
        return timestamp_url

    def resumable_upload(self, local_file_name, bucket_path, object_name=None, progress_callback=None, progress_file_name=None, retries=5):
        """断点续传

        :param local_file_name: 本地文件名称
        :param object_name: 指定OS中存储的对象名称
        :param progress_callback: 进度回调函数，默认是把进度信息输出到标准输出。
        :param progress_file_name: 进度信息保存文件，进度格式参见[report_progress]
        :param retries: 上传重试次数
        :return: True上传成功/False or None上传失败
        """

        try:
            upload_expires = 60 * 60

            if object_name is None:
                filepath, key = os.path.split(local_file_name)
                self.__bucket_path = main().get_path(os.path.dirname(bucket_path))
                key = self.__bucket_path + '/' + key
                key = key.replace('//','/')
                object_name = key
            token = self.__oss.upload_token(self.__bucket_name, object_name, upload_expires)

            if object_name[:1] == "/":
                object_name = object_name[1:]

            print("|-正在上传{}到七牛云存储".format(object_name),end='')
            ret, info = put_file(token,
                                 object_name,
                                 local_file_name,
                                 check_crc=True,
                                 progress_handler=progress_callback,
                                 bucket_name=self.__bucket_name,
                                 part_size=1024 * 1024 * 4,
                                 version="v2")
            upload_status = False
            if sys.version_info[0] == 2:
                upload_status = ret['key'].encode('utf-8') == object_name
            elif sys.version_info[0] == 3:
                upload_status = ret['key'] == object_name
            if upload_status:
                print(' ==> 成功')
                return ret['hash'] == etag(local_file_name)
            return False
        except Exception as e:
            print("文件上传出现错误：", str(e))

        # 重试断点续传
        if retries > 0:
            print("重试上传文件....")
            return self.resumable_upload(
                local_file_name,
                bucket_path,
                object_name=object_name,
                progress_callback=progress_callback,
                progress_file_name=progress_file_name,
                retries=retries - 1,
            )
        return False

    # 上传文件到指定目录
    def upload_file_by_path(self, filename, bucket_path):
        return self.resumable_upload(filename, bucket_path)

    def delete_object_by_os(self, object_name):
        """删除对象"""

        bucket = self.get_bucket()
        res, info = bucket.delete(self.__bucket_name, object_name)
        return res == {}

    def get_object_info(self, object_name):
        """获取文件对象信息"""
        try:
            bucket = self.get_bucket()
            result = bucket.stat(self.__bucket_name, object_name)
            return result[0]
        except:
            return None


    # 删除文件
    def remove_file(self, get):
        try:
            filename = get.filename
            path = get.path

            if path[-1] != "/":
                file_name = path + "/" + filename
            else:
                file_name = path + filename

            if file_name[-1] == "/":
                return public.returnMsg(False, "暂时不支持目录删除！")

            if file_name[:1] == "/":
                file_name = file_name[1:]

            if self.delete_object_by_os(file_name):
                return public.returnMsg(True, '删除成功')
            return public.returnMsg(False, '文件{}删除失败, path:{}'.format(file_name, get.path))
        except:
            print(self.__error_msg)
            return False


#亚马逊S3云存储
class aws_main:
    pass
#又拍云存储
class upyun_main:
    pass
#华为云存储
class obs_main:
    __oss = None
    __bucket_path = None
    __error_count = 0
    __secret_id = None
    __secret_key = None
    __region = None
    __Bucket = None
    __error_msg = "ERROR: 无法连接华为云OBS !"


    def __init__(self):
        self.__conn()

    def __conn(self):
        """
        @name 构建鉴权对象
        """
        if self.__oss: return

        keys = self.get_config()
        self.__secret_id = keys[0]
        self.__secret_key = keys[1]
        self.__region = keys[2]
        self.__Bucket = keys[3]
        self.__bucket_path = main().get_path(keys[4])
        try:
            # from obs import ObsClient
            self.__oss = ObsClient(
                    access_key_id = self.__secret_id,
                    secret_access_key = self.__secret_key,
                    server = self.__Bucket,
            )
        except Exception as ex:
            pass
            # print(self.__error_msg, str(ex))


    def get_config(self, get=None):
        """
        @name 获取华为云密钥信息
        """
        path = main()._config_path + '/obs.conf'
        # print(path)
        #从华为云OBS插件配置取配置密钥信息
        if not os.path.isfile(path):
            file_name = ''
            # print((main()._plugin_path)
            if os.path.isfile(main()._plugin_path+'obs/config.conf'):
                file_name=main()._plugin_path+'obs/config.conf'
            elif os.path.isfile(main()._setup_path+'data/obsAS.conf'):
                file_name = main()._setup_path+'data/obsAS.conf'
            file_name =file_name.replace('//', '/')
            obs_info=None
            if os.path.isfile(file_name):
                try:
                    obs_info = json.loads(public.readFile(file_name))
                except:
                    pass
                if 'access_key' not in obs_info or 'secret_key' not in obs_info or 'bucket_name' not in obs_info or 'bucket_domain' not in obs_info:obs_info=None
                if obs_info:
                    add_str = obs_info['access_key']+'|'+obs_info['secret_key']+'|'+obs_info['bucket_name']+'|'+obs_info['bucket_domain']+'|'+obs_info['backup_path']
                    public.writeFile(path, add_str)
        if not os.path.isfile(path): return ['', '', '', '', '/']
        conf = public.readFile(path)
        if not conf: return ['', '', '', '', '/']
        result = conf.split('|')
        if len(result) < 5: result.append('/')
        # print('result:')
        # print(result)
        return result

    # 检测华为云存储是否可用
    def check_config(self):
        try:
            data = []
            path = main().get_path('/')
            resp =  self.__oss.listObjects(
                self.__region,
                prefix=path,
                )

            for b in resp.body.contents:
                if b.size != 0 :
                    if not b.key: continue;
                    tmp = {}
                    name = b.key
                    name = name[name.find(path) + len(path):] 
                    dir_dir = b.key.split('/')
                    if len(dir_dir) > 1000000: continue;
                    rep = re.compile(r'/')
                    if rep.search(name) != None: continue;
                    tmp["type"] = True
                    tmp["name"] = name
                    tmp['size'] = b.size
                    tstr = b.lastModified
                    t = datetime.datetime.strptime(tstr, "%Y/%m/%d %H:%M:%S")
                    t += datetime.timedelta(hours=0)
                    ts = int((time.mktime(t.timetuple()) + t.microsecond / 1000000.0))
                    tmp['time'] = ts
                    data.append(tmp)
                elif b.size == 0:
                    if not b.key: continue;
                    if b.key[-1] != "/": continue;
                    dir_dir = b.key.split('/')
                    tmp = {}
                    name = b.key
                    name = name[name.find(path) + len(path):] 
                    if path == "" and len(dir_dir) > 2: continue;
                    if path != "": 
                        dir_dir = name.split('/')
                        if len(dir_dir) > 2: continue;
                        else:
                            name = name
                    if not name: continue;
                    tmp["type"] = None
                    tmp["name"] = name
                    tmp['size'] = b.size
                    data.append(tmp)
            return True
        except:
            return False

    def upload_file_by_path(self, filename, bucket_path):
        """
        @name 上传文件
        @param filename 上传的文件名
        @param bucket_path 腾讯云cos保存的文件名
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False
        #以下代码解决华为云存储上传的对象后无法获取对象问题
        if bucket_path != None:
            resp = self.__oss.listObjects(
                self.__region,
                prefix="",
                )
            dir_dir = bucket_path.split("/")
            dir_d = ""
            keylist = []
            for c  in resp.body.contents:
                    if not c.key: continue
                    keylist.append(c.key)
            for i in range(0,(len(dir_dir) - 1)):
                if dir_d == "":
                    dir_d = dir_dir[i]+"/"
                else:
                    dir_d = dir_d +dir_dir[i]+"/"
                if not dir_d: continue
                if main().get_path(dir_d) not in keylist:
                    resp = self.__oss.putContent(
                        self.__region,
                        objectKey = main().get_path(dir_d),
                        )

        try:
            print('|-正在上传{}到华为云存储'.format(filename),end='')
            filepath, key = os.path.split(filename)
            self.__bucket_path = main().get_path(os.path.dirname(bucket_path))
            key = self.__bucket_path + key
            partSize = 5 * 1024 * 1024
            uploadFile = filename
            objectKey = key
            enableCheckpoint = True
            resp = self.__oss.uploadFile(
                self.__region,
                objectKey, 
                uploadFile,
                partSize,
                enableCheckpoint,
                )
            if resp.status < 300:
                print(' ==> 成功')
                return True
        except Exception as ex:
            # print(ex)
            time.sleep(1)
            self.__error_count += 1
            if self.__error_count < 2:  # 重试2次
                # main().sync_date()
                self.upload_file_by_path(filename, bucket_path)
            return False


    def get_list(self, get=None):
        """
        @name 取文件列表信息
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False
        data = []
        path = main().get_path(get.path)
        resp = self.__oss.listObjects(
            self.__region,
            prefix=path,
            )

        for b in resp.body.contents:
            if b.size != 0 :
                if not b.key: continue;
                tmp = {}
                name = b.key
                name = name[name.find(path) + len(path):] 
                dir_dir = b.key.split('/')
                if len(dir_dir) > 1000000: continue;
                rep = re.compile(r'/')
                if rep.search(name) != None: continue;
                tmp["type"] = True
                tmp["name"] = name
                tmp['size'] = b.size
                tmp['download'] = self.download_file(path+name)
                tstr = b.lastModified
                t = datetime.datetime.strptime(tstr, "%Y/%m/%d %H:%M:%S")
                t += datetime.timedelta(hours=0)
                ts = int((time.mktime(t.timetuple()) + t.microsecond / 1000000.0))
                tmp['time'] = ts
                data.append(tmp)
            elif b.size == 0:
                if not b.key: continue;
                if b.key[-1] != "/": continue;
                dir_dir = b.key.split('/')
                tmp = {}
                name = b.key
                name = name[name.find(path) + len(path):] 
                if path == "" and len(dir_dir) > 2: continue;
                if path != "": 
                    dir_dir = name.split('/')
                    if len(dir_dir) > 2: continue;
                    else:
                        name = name
                if not name: continue;
                tmp["type"] = None
                tmp["name"] = name
                tmp['size'] = b.size
                data.append(tmp)
            
        mlist = {'path': path, 'list': data}
        return mlist

    def download_file(self, filename):
        """
        @name 下载文件
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return None
        try:
            response = self.__oss.createSignedUrl('GET', 
            self.__region, 
            filename, 
            expires= 3600,
            )
            url = response.signedUrl
            return url
        except:
            print(self.__error_msg)
            return None

    def delete_file(self, filename):
        """
        @ name 删除文件
        @param filename 需要删除的文件名
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            response = self.__oss.deleteObject(self.__region,filename)
            return response
        except Exception as ex:
            self.__error_count += 1
            if self.__error_count < 2:
                # main().sync_date()
                self.delete_file(filename)
            print(self.__error_msg)
            return None

    # 删除文件
    def remove_file(self, get):
        path = main().get_path(get.path)
        filename = path + get.filename
        self.delete_file(filename)
        return public.returnMsg(True, '删除文件成功!')


#百度云存储
class bos_main:
    __oss = None
    __error_count = 0
    __secret_id = None
    __secret_key = None
    __Bucket = None
    __error_msg = "ERROR: 无法连接百度云存储 !"


    def __init__(self):
        self.__conn()

    def __conn(self):
        """
        @name 构建鉴权对象
        """
        if self.__oss: return

        keys = self.get_config()
        self.__secret_id = keys[0]
        self.__secret_key = keys[1]
        self.__region = keys[2]
        self.__Bucket = keys[3]
        # self.__bucket_path = keys[4]
        self.__bucket_path = main().get_path(keys[4])
        try:
            config = BceClientConfiguration(
                credentials=BceCredentials(self.__secret_id, self.__secret_key),
                endpoint=self.__Bucket)
            self.__oss = BosClient(config)
        except Exception as ex:
            pass
            # print(self.__error_msg, str(ex))


    def get_config(self, get=None):
        """
        @name 设置百度云存储设置密钥信息
        """
        path = main()._config_path + '/bos.conf'
        #从百度云存储插件配置取配置密钥信息
        if not os.path.isfile(path):
            file_name = ''
            if os.path.isfile(main()._plugin_path+'bos/config.conf'):
                file_name = main()._plugin_path+'bos/config.conf'
            elif os.path.isfile(main()._setup_path+'data/bosAS.conf'):
                file_name=main()._setup_path+'data/bosAS.conf'
            file_name =file_name.replace('//', '/')
            oss_info=None
            if os.path.isfile(file_name):
                try:
                    oss_info = json.loads(public.readFile(file_name))
                except:
                    pass
                if 'access_key' not in oss_info or 'secret_key' not in oss_info or 'bucket_name' not in oss_info or 'bucket_domain' not in oss_info:oss_info=None
                if oss_info:
                    add_str = oss_info['access_key']+'|'+oss_info['secret_key']+'|'+oss_info['bucket_name']+'|'+oss_info['bucket_domain']+'|'+oss_info['backup_path']
                    public.writeFile(path, add_str)
        if not os.path.isfile(path): return ['', '', '', '', '/']
        conf = public.readFile(path)
        if not conf: return ['', '', '', '', '/']
        result = conf.split('|')
        if len(result) < 5: result.append('/')
        return result
        
        

    def check_config(self):
        """
        @name 检测百度云存储是否可用
        """
        if not self.__oss:return False
        try:
            path = '/'
            response = self.__oss.list_objects(self.__region, prefix=path,
                                        delimiter="/")
            return True
        except:
            return False

    def resumable_upload(self,
                            local_file_name,
                            object_name=None,
                            progress_callback=None,
                            progress_file_name=None,
                            retries=5,
                            ):
            """断点续传

            :param local_file_name: 本地文件名称
            :param object_name: 指定OS中存储的对象名称
            :param retries: 上传重试次数
            :return: True上传成功/False or None上传失败
            """

            try:
                if object_name[:1] == "/":
                    object_name = object_name[1:]
                print("|-正在上传{}到百度云存储".format(object_name),end='')
                import multiprocessing
                file_name = local_file_name
                key = object_name
                bucket_name = self.__region
                result = self.__oss.put_super_obejct_from_file(
                    bucket_name,
                    key, file_name,
                    chunk_size=5,
                    thread_num=multiprocessing.cpu_count() - 1)
                if result:
                    print(' ==> 成功')
                    return True
            except Exception as e:
                print("文件上传出现错误：")
                print(e)

            # 重试断点续传
            if retries > 0:
                print("重试上传文件....")
                return self.resumable_upload(
                    local_file_name,
                    object_name=object_name,
                    progress_callback=progress_callback,
                    progress_file_name=progress_file_name,
                    retries=retries - 1,
                )
            return False

    def upload_file_by_path(self, filename, bucket_path):
        """
        @name 上传文件
        """
        return self.resumable_upload(filename, bucket_path)

    def get_list(self, get=None):
        data = []
        dir_list = []
        path = main().get_path(get.path)
        try:
            response = self.__oss.list_objects(self.__region, prefix=path,
                                        delimiter="/")
            for b in response.contents:
                if not b.key: continue
                tmp = {}
                name = b.key
                name = name[name.find(path) + len(path):]
                if not name: continue
                tmp["name"] = name
                tmp['size'] = b.size
                tmp["type"] = True
                tmp['download'] = self.download_file(path + "/" + name)
                tstr = b.last_modified
                t = datetime.datetime.strptime(tstr, "%Y-%m-%dT%H:%M:%SZ")
                t += datetime.timedelta(hours=8)
                ts = int((time.mktime(t.timetuple()) + t.microsecond / 1000000.0))
                tmp['time'] = ts
                data.append(tmp)
            for i in response.common_prefixes:
                if not i.prefix: continue
                if i.prefix[0:-1] == path: continue
                tmp = {}
                i.prefix = i.prefix.replace(path, '')
                tmp["name"] = i.prefix
                tmp["type"] = None
                tmp['size'] = i.size
                data.append(tmp)
            mlist = {'path': path, 'list': data}
            return mlist
        except:
            mlist = {}
            if self.__oss:
                mlist['status'] = True
            else:
                mlist['status'] = False
            mlist['path'] = get.path
            mlist['list'] = data
            mlist['dir'] = dir_list
            return mlist

    def download_file(self, filename):
        """
        @name 下载文件
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return None

        try:
            url = self.__oss.generate_pre_signed_url(self.__region, filename)
            _ver = sys.version_info
            #: Python 2.x?
            is_py2 = (_ver[0] == 2)

            #: Python 3.x?
            is_py3 = (_ver[0] == 3)
            if is_py3:
                url = str(url, encoding="utf-8")
            else:
                url = url
            return url
        except:
            print(self.__error_msg)
            return None

    def delete_file(self, filename):
        """
        @ name 删除文件
        @param filename 需要删除的文件名
        """
        # 连接OSS服务器
        self.__conn()
        if not self.__oss:
            return False

        try:
            response = self.__oss.delete_object(self.__region,filename)
            return response
        except Exception as ex:
            self.__error_count += 1
            if self.__error_count < 2:
                # main().sync_date()
                self.delete_file(filename)
            print(self.__error_msg)
            return None

    # 删除文件
    def remove_file(self, get):
        path = main().get_path(get.path)
        filename = path + get.filename
        self.delete_file(filename)
        return public.returnMsg(True, '删除文件成功!')

#谷歌云存储
class gcloud_storage_main:
    pass
#谷歌云网盘
class gdrive_main:
    pass
#微软onedrive
class msonedrive_main:
    pass



if __name__ == '__main__':
    import argparse
    args_obj = argparse.ArgumentParser(usage="必要的参数：--db_name 数据库名称!")
    args_obj.add_argument("--db_name", help="数据库名称!")
    args_obj.add_argument("--binlog_id", help="任务id")
    args = args_obj.parse_args()
    if not args.db_name:
        args_obj.print_help()
    p = main()
    p._db_name = args.db_name
    if args.binlog_id: p._binlog_id = args.binlog_id
    #计划任务脚本调用
    if p._binlog_id:
        p.execute_by_comandline()



