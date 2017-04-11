#!/usr/bin/python
#coding: utf-8
#-----------------------------
# 宝塔Linux面板网站备份工具 - ALIOSS
#-----------------------------
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
os.chdir('/www/server/panel');
sys.path.append("class/")
import public,db,time

import oss2



class aliossBackup:
    __oss = None
    __bucket_name = None
    __bucket_domain = None
    __error_count = 0
    __error_msg = "ERROR: 无法连接到阿里云OSS服务器，请检查[AccessKeyId/AccessKeySecret/Endpoint]设置是否正确!"
    def __init__(self):
        #获取阿里云秘钥
        fp = open('data/aliossAs.conf','r');
        if not fp:
            print 'ERROR: 请检查aliossAs.conf文件中是否有阿里云AccessKey相关信息!';
            exit();
        keys = fp.read().split('|');
        if len(keys) < 4:
            print 'ERROR: 请检查aliossAs.conf文件中的阿里云AccessKey信息是否完整!';
            exit();
        
        self.__bucket_name     = keys[2];
        if keys[3].find(keys[2]) != -1: keys[3] = keys[3].replace(keys[2]+'.','');
        self.__bucket_domain     = keys[3];
        
        #构建鉴权对象
        self.__oss = oss2.Auth(keys[0], keys[1]);
        
        
        
    #上传文件
    def upload_file(self,filename):
        try:
            #保存的文件名
            key = filename.split('/')[-1];
            bucket = oss2.Bucket(self.__oss,self.__bucket_domain,self.__bucket_name)
            result = bucket.put_object_from_file(key, filename)
            return result.status
        except Exception,ex:
            if ex.status == 403: 
                self.__error_count += 1;
                if self.__error_count < 2: 
                    self.sync_date();
                    self.upload_file(filename);
                
            print self.__error_msg
            return None
    
    #取回文件列表
    def get_list(self):
        try:
            from itertools import islice
            bucket = oss2.Bucket(self.__oss,self.__bucket_domain,self.__bucket_name)
            result = oss2.ObjectIterator(bucket);
            data = [];
            '''key, last_modified, etag, type, size, storage_class'''
            for b in islice(oss2.ObjectIterator(bucket), 10):
                tmp = {}
                tmp['key'] = b.key
                tmp['fsize'] = b.size
                tmp['mimeType'] = b.type
                tmp['hash'] = b.storage_class
                tmp['putTime'] = b.last_modified
                data.append(tmp)
            
            if len(data) < 1: return [{"mimeType": "application/test", "fsize": 0, "hash": "", "key": "没有文件", "putTime": 14845314157209192}];
            return data
        
        except Exception,ex:
            if ex.status == 403: 
                self.__error_count += 1;
                if self.__error_count < 2: 
                    self.sync_date();
                    self.get_list();
                
            print self.__error_msg
            return None
    def sync_date(self):
        public.ExecShell("ntpdate 0.asia.pool.ntp.org");
    
    #下载文件
    def download_file(self,filename):
        try:
            bucket = oss2.Bucket(self.__oss,self.__bucket_domain,self.__bucket_name)
            private_url = bucket.sign_url('GET', filename, 3600)
            return private_url
        except:
            print self.__error_msg
            return None

    #删除文件
    def delete_file(self,filename):
        try:
            bucket = oss2.Bucket(self.__oss,self.__bucket_domain,self.__bucket_name)
            result = bucket.delete_object(filename)
            return result.status
        except Exception,ex:
            if ex.status == 403: 
                self.__error_count += 1;
                if self.__error_count < 2: 
                    self.sync_date();
                    self.delete_file(filename);
                
            print self.__error_msg
            return None
        
    #备份网站
    def backupSite(self,name,count):
        sql = db.Sql();
        path = sql.table('sites').where('name=?',(name,)).getField('path');
        startTime = time.time();
        if not path:
            endDate = time.strftime('%Y/%m/%d %X',time.localtime())
            log = "网站["+name+"]不存在!"
            print "★["+endDate+"] "+log
            print "----------------------------------------------------------------------------"
            return;
        
        backup_path = sql.table('config').where("id=?",(1,)).getField('backup_path') + '/site';
        if not os.path.exists(backup_path): public.ExecShell("mkdir -p " + backup_path);
        
        filename= backup_path + "/Web_" + name + "_" + time.strftime('%Y%m%d_%H%M%S',time.localtime()) + '.tar.gz'
        public.ExecShell("cd " + os.path.dirname(path) + " && tar zcvf '" + filename + "' '" + os.path.basename(path) + "' > /dev/null")
        endDate = time.strftime('%Y/%m/%d %X',time.localtime())
        
        if not os.path.exists(filename):
            log = "网站["+name+"]备份失败!"
            print "★["+endDate+"] "+log
            print "----------------------------------------------------------------------------"
            return;
        
        #上传文件
        self.upload_file(filename);
        
        outTime = time.time() - startTime
        pid = sql.table('sites').where('name=?',(name,)).getField('id');
        sql.table('backup').add('type,name,pid,filename,addtime,size',('0',os.path.basename(filename),pid,'alioss',endDate,os.path.getsize(filename)))
        log = "网站["+name+"]已成功备份到阿里云OSS,用时["+str(round(outTime,2))+"]秒";
        public.WriteLog('计划任务',log)
        print "★["+endDate+"] " + log
        print "|---保留最新的["+count+"]份备份"
        print "|---文件名:"+os.path.basename(filename)
        
        #清理本地文件
        public.ExecShell("rm -f " + filename)
        
        #清理多余备份     
        backups = sql.table('backup').where('type=? and pid=?',('0',pid)).field('id,name,filename').select();
        
        num = len(backups) - int(count)
        if  num > 0:
            for backup in backups:
                if os.path.exists(backup['filename']):
                    public.ExecShell("rm -f " + backup['filename']);
                self.delete_file(backup['name']);
                sql.table('backup').where('id=?',(backup['id'],)).delete();
                num -= 1;
                print "|---已清理过期备份文件：" + backup['name']
                if num < 1: break;
        return None
    
    #备份数据库
    def backupDatabase(self,name,count):
        sql = db.Sql();
        path = sql.table('databases').where('name=?',(name,)).getField('path');
        startTime = time.time();
        if not path:
            endDate = time.strftime('%Y/%m/%d %X',time.localtime())
            log = "数据库["+name+"]不存在!"
            print "★["+endDate+"] "+log
            print "----------------------------------------------------------------------------"
            return;
        
        
        backup_path = sql.table('config').where("id=?",(1,)).getField('backup_path') + '/database';
        if not os.path.exists(backup_path): public.ExecShell("mkdir -p " + backup_path);
        
        filename = backup_path + "/Db_" + name + "_" + time.strftime('%Y%m%d_%H%M%S',time.localtime())+".sql.gz"
        
        import re
        mysql_root = sql.table('config').where("id=?",(1,)).getField('mysql_root')
        mycnf = public.readFile('/etc/my.cnf');
        rep = "\[mysqldump\]\nuser=root"
        sea = '[mysqldump]\n'
        subStr = sea + "user=root\npassword=" + mysql_root+"\n";
        mycnf = mycnf.replace(sea,subStr)
        public.writeFile('/etc/my.cnf',mycnf);
        
        public.ExecShell("/www/server/mysql/bin/mysqldump --opt --default-character-set=utf8 " + name + " | gzip > " + filename)
        
        if not os.path.exists(filename):
            endDate = time.strftime('%Y/%m/%d %X',time.localtime())
            log = "数据库["+name+"]备份失败!"
            print "★["+endDate+"] "+log
            print "----------------------------------------------------------------------------"
            return;

        mycnf = public.readFile('/etc/my.cnf');
        mycnf = mycnf.replace(subStr,sea)
        public.writeFile('/etc/my.cnf',mycnf);
        
        #上传
        self.upload_file(filename);
        
        endDate = time.strftime('%Y/%m/%d %X',time.localtime())
        outTime = time.time() - startTime
        pid = sql.table('databases').where('name=?',(name,)).getField('id');
        
        sql.table('backup').add('type,name,pid,filename,addtime,size',(1,os.path.basename(filename),pid,'alioss',endDate,os.path.getsize(filename)))
        log = "数据库["+name+"]已成功备份到阿里云OSS,用时["+str(round(outTime,2))+"]秒";
        public.WriteLog('计划任务',log)
        print "★["+endDate+"] " + log
        print "|---保留最新的["+count+"]份备份"
        print "|---文件名:"+os.path.basename(filename)
        
        #清理本地文件
        public.ExecShell("rm -f " + filename)
        
        #清理多余备份     
        backups = sql.table('backup').where('type=? and pid=?',('1',pid)).field('id,name,filename').select();
        
        num = len(backups) - int(count)
        if  num > 0:
            for backup in backups:
                if os.path.exists(backup['filename']):
                    public.ExecShell("rm -f " + backup['filename']);
                    
                self.delete_file(backup['name']);
                sql.table('backup').where('id=?',(backup['id'],)).delete();
                num -= 1;
                print "|---已清理过期备份文件：" + backup['name']
                if num < 1: break;
        return None
    
    
    
if __name__ == "__main__":
    import json
    data = None
    q = aliossBackup();
    type = sys.argv[1];
    if type == 'site':
        data = q.backupSite(sys.argv[2],sys.argv[3]);
        exit()
    elif type == 'database':
        data = q.backupDatabase(sys.argv[2],sys.argv[3]);
        exit()
    elif type == 'upload':
        data = q.upload_file(sys.argv[2]);
    elif type == 'download':
        data = q.download_file(sys.argv[2]);
    elif type == 'get':
        data = q.get_files(sys.argv[2]);
    elif type == 'list':
        data = q.get_list();
    elif type == 'delete_file':
        data = q.delete_file(sys.argv[2]);
    else:
        data = 'ERROR: 参数不正确!';
    
    print json.dumps(data)