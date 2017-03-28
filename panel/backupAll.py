#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

#------------------------------
# 一键备份恢复所有数据
#------------------------------

import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

class backups:
    __SETUP_PATH = '/www'
    __SHELL_PATH = None
    
    def __init__(self):
        self.__SHELL_PATH = os.path.split(os.path.realpath(__file__))[0]
    #备份所有数据
    def backup(self):
        backup_path = self.__SHELL_PATH + '/backup'
        os.system('rm -rf ' + backup_path)
        os.system('mkdir ' + backup_path)
        
        import commands
        password = commands.getstatusoutput('cat ' + self.__SETUP_PATH + '/wwwroot/default/conf/sql.config.php |grep \'DB_PWD\'|awk \'{print $3}\'|sed "s#\'##g"|sed "s#,##g"')
        site_path = commands.getstatusoutput(self.__SETUP_PATH + '/server/mysql/bin/mysql -ubt_default -p'+password[1]+' --default-character-set=utf8 -D bt_default -e "SELECT sites_path FROM bt_config WHERE id=1"')[1].split()[1]
        self.serviceAdmin('stop')
        
        #打包数据库
        print '正在打包数据库...';
        os.system('mkdir -p ' + backup_path + '/data')
        os.system('\\cp -r -a ' + self.__SETUP_PATH + '/server/data/* ' + backup_path + '/data/')
        os.system('\\cp -r -a /etc/my.cnf ' + backup_path + '/my.cnf')
        
        #打包网站文件
        print '正在打包'+self.__SETUP_PATH + '/wwwroot...';
        os.system('rm -rf ' + self.__SETUP_PATH + '/wwwroot/old_default')
        os.system('cd ' + self.__SETUP_PATH + '/wwwroot && mv default old_default')
        os.system('mkdir -p ' + backup_path + '/wwwroot')
        os.system('\\cp -r -a ' + self.__SETUP_PATH + '/wwwroot/* ' + backup_path + '/wwwroot/')
        os.system('cd ' + self.__SETUP_PATH + '/wwwroot && mv old_default default')
       
        print '正在打包'+site_path+'...';
        if site_path != self.__SETUP_PATH+'/wwwroot':
            os.system('mkdir -p ' + backup_path + '/web')
            os.system('\\cp -r -a ' + site_path + '/* ' + backup_path + '/web/')
            fp = open(backup_path+'/site_path.pl','w+')
            fp.write(site_path)
            fp.close()
        
        #打包配置文件
        print '正在打包Nginx配置文件...';
        apath = self.__SETUP_PATH + '/server/nginx'
        if os.path.exists(apath):
            os.system('mkdir -p ' + backup_path + '/nginx')
            os.system('\\cp -r -a ' + apath + '/conf/* ' + backup_path + '/nginx/')
        
        print '正在打包Apache配置文件...';
        apath = self.__SETUP_PATH + '/server/apache'
        if os.path.exists(apath):
            os.system('mkdir -p ' + backup_path + '/apache')
            os.system('\\cp -r -a ' + apath + '/conf/* ' + backup_path + '/apache/')
        
        print '正在打包pure-ftpd配置文件...'
        apath = self.__SETUP_PATH + '/server/pure-ftpd'   
        if os.path.exists(apath):
            os.system('mkdir -p ' + backup_path + '/pure-ftpd')
            os.system('\\cp -r -a ' + apath + '/etc/* ' + backup_path + '/pure-ftpd/')
        
        print '正在打包cron配置文件...';
        apath = self.__SETUP_PATH + '/server/cron'
        if os.path.exists(apath):
            os.system('mkdir -p ' + backup_path + '/cron')
            os.system('\\cp -r -a ' + apath + '/* ' + backup_path + '/cron/')
            os.system('\\cp -r -a /var/spool/cron/root ' + backup_path + '/root')
        
        
        print '正在压缩...'
        os.system('cd ' + self.__SHELL_PATH + ' && zip -r backup.zip backup')
        
        print '清理临时文件...'
        os.system('rm -rf backup')    
        
        print '正在启动受影响服务...'
        self.serviceAdmin('start')
        
        print '======================'
        print '面板数据备份完成!'
        
        
    #恢复面板数据
    def reBackup(self,filename = 'backup.zip'):
        if not os.path.exists(filename):
            print '==================================================='
            print '错误: 找不到备份文件, 请将 backup.zip 文件与程序放在同一目录.'
            exit()
        
        print '正在解压数据...'
        os.system('unzip -o backup.zip')
        
        print '正在停止受影响服务...'
        self.serviceAdmin('stop')
        if os.path.exists('backup/data'):
            print '正在恢复数据库...'
            os.system('mkdir -p '+self.__SETUP_PATH + '/server/data')
            os.system('\\cp -r -a backup/data/* ' + self.__SETUP_PATH + '/server/data/')
            os.system('\\cp -r -a backup/my.cnf /etc/my.cnf')
            os.system('chown -R mysql.mysql ' + self.__SETUP_PATH + '/server/data')
        
        if os.path.exists('backup/wwwroot'):
            print '正在恢复网站目录wwwroot...'
            os.system('mkdir -p ' + self.__SETUP_PATH + '/wwwroot/')
            os.system('\\cp -r -a backup/wwwroot/* ' + self.__SETUP_PATH + '/wwwroot/')
        
        
        if os.path.exists('backup/site_path.pl'):
            fp = open('backup/site_path.pl','r')
            site_path = fp.read().strip()
            fp.close()
            
            print '正在恢复网站目录'+site_path+'...'
            os.system('mkdir -p ' + site_path)
            os.system('\\cp -r -a backup/web/* ' + site_path + '/')
            
        if os.path.exists('backup/nginx'):
            print '正在恢复Nginx配置文件...'
            os.system('\\cp -r -a backup/nginx/* ' + self.__SETUP_PATH + '/server/nginx/conf/')
        
        if os.path.exists('backup/apache'):
            print '正在恢复Apache配置文件...'
            os.system('\\cp -r -a backup/apache/* ' + self.__SETUP_PATH + '/server/apache/conf/')
        
        if os.path.exists('backup/pure-ftpd'):
            print '正在恢复Pure-Ftpd配置文件...'
            os.system('\\cp -r -a backup/pure-ftpd/* ' + self.__SETUP_PATH + '/server/pure-ftpd/etc/')
            
        if os.path.exists('backup/cron'):
            print '正在恢复cron配置文件...'
            os.system('mkdir -p ' + self.__SETUP_PATH + '/server/cron/')
            os.system('\\cp -r -a backup/cron/* ' + self.__SETUP_PATH + '/server/cron/')
            os.system('chmod -R 744 ' + self.__SETUP_PATH + '/server/cron/')
            os.system('\\cp -r -a backup/root /var/spool/cron/root')
            os.system('chmod 600 /var/spool/cron/root')
        
        print '清理临时文件...'
        os.system('rm -rf backup')    
        
        print '正在启动受影响服务...'
        self.serviceAdmin('start')
        
        print '======================'
        print '面板数据恢复完成!'
        
    
    
    
    
    #停止或启动受影响服务
    def serviceAdmin(self,action):
        if os.path.exists('/etc/init.d/mysqld'): os.system('service mysqld ' + action);
        if os.path.exists('/etc/init.d/nginx'): os.system('service nginx ' + action);
        if os.path.exists('/etc/init.d/httpd'): os.system('service httpd ' + action);
        if os.path.exists('/etc/init.d/pure-ftpd'): os.system('service pure-ftpd ' + action);
        
        
if __name__ == "__main__":
    err = '错误: 参数错误'
    if len(sys.argv) < 2:
        print err
        exit()
    type = sys.argv[1];
    
    b = backups();
    if type == 'backup':
        b.backup()
    elif type == 'input':
        b.reBackup()
    else:
        print err
