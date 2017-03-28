#!/usr/bin/python
#coding: utf-8
#-----------------------------
# 宝塔Linux面板网站备份工具
#-----------------------------

import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
os.chdir('/www/server/panel');
sys.path.append("class/")
import public,db,time

class backupTools:
    
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
        
        outTime = time.time() - startTime
        pid = sql.table('sites').where('name=?',(name,)).getField('id');
        sql.table('backup').add('type,name,pid,filename,addtime,size',('0',os.path.basename(filename),pid,filename,endDate,os.path.getsize(filename)))
        log = "网站["+name+"]备份成功,用时["+str(round(outTime,2))+"]秒";
        public.WriteLog('计划任务',log)
        print "★["+endDate+"] " + log
        print "|---保留最新的["+count+"]份备份"
        print "|---文件名:"+filename
        
        #清理多余备份     
        backups = sql.table('backup').where('type=? and pid=?',('0',pid)).field('id,filename').select();
        
        num = len(backups) - int(count)
        if  num > 0:
            for backup in backups:
                public.ExecShell("rm -f " + backup['filename']);
                sql.table('backup').where('id=?',(backup['id'],)).delete();
                num -= 1;
                print "|---已清理过期备份文件：" + backup['filename']
                if num < 1: break;
    
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
        
        endDate = time.strftime('%Y/%m/%d %X',time.localtime())
        outTime = time.time() - startTime
        pid = sql.table('databases').where('name=?',(name,)).getField('id');
        
        sql.table('backup').add('type,name,pid,filename,addtime,size',(1,os.path.basename(filename),pid,filename,endDate,os.path.getsize(filename)))
        log = "数据库["+name+"]备份成功,用时["+str(round(outTime,2))+"]秒";
        public.WriteLog('计划任务',log)
        print "★["+endDate+"] " + log
        print "|---保留最新的["+count+"]份备份"
        print "|---文件名:"+filename
        
        #清理多余备份     
        backups = sql.table('backup').where('type=? and pid=?',('1',pid)).field('id,filename').select();
        
        num = len(backups) - int(count)
        if  num > 0:
            for backup in backups:
                public.ExecShell("rm -f " + backup['filename']);
                sql.table('backup').where('id=?',(backup['id'],)).delete();
                num -= 1;
                print "|---已清理过期备份文件：" + backup['filename']
                if num < 1: break;
    
    def backupQiniu(self,name,count):
        pass
    
    
    


if __name__ == "__main__":
    backup = backupTools()
    type = sys.argv[1];
    if type == 'site':
        backup.backupSite(sys.argv[2], sys.argv[3])
    else:
        backup.backupDatabase(sys.argv[2], sys.argv[3])
    