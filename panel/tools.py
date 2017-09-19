#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

#------------------------------
# 工具箱
#------------------------------
import sys,os
panelPath = '/www/server/panel/';
os.chdir(panelPath)
sys.path.append(panelPath + "class/")
import public,time

#设置MySQL密码
def set_mysql_root(password):
    import db,os
    sql = db.Sql()
    
    root_mysql = '''#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
pwd=$1
service mysqld stop
mysqld_safe --skip-grant-tables&
echo '正在修改密码...';
echo 'The set password...';
sleep 6
mysql -uroot -e "insert into mysql.user(Select_priv,Insert_priv,Update_priv,Delete_priv,Create_priv,Drop_priv,Reload_priv,Shutdown_priv,Process_priv,File_priv,Grant_priv,References_priv,Index_priv,Alter_priv,Show_db_priv,Super_priv,Create_tmp_table_priv,Lock_tables_priv,Execute_priv,Repl_slave_priv,Repl_client_priv,Create_view_priv,Show_view_priv,Create_routine_priv,Alter_routine_priv,Create_user_priv,Event_priv,Trigger_priv,Create_tablespace_priv,User,Password,host)values('Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','root',password('${pwd}'),'127.0.0.1')"
mysql -uroot -e "insert into mysql.user(Select_priv,Insert_priv,Update_priv,Delete_priv,Create_priv,Drop_priv,Reload_priv,Shutdown_priv,Process_priv,File_priv,Grant_priv,References_priv,Index_priv,Alter_priv,Show_db_priv,Super_priv,Create_tmp_table_priv,Lock_tables_priv,Execute_priv,Repl_slave_priv,Repl_client_priv,Create_view_priv,Show_view_priv,Create_routine_priv,Alter_routine_priv,Create_user_priv,Event_priv,Trigger_priv,Create_tablespace_priv,User,Password,host)values('Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','root',password('${pwd}'),'localhost')"
mysql -uroot -e "UPDATE mysql.user SET password=PASSWORD('${pwd}') WHERE user='root'";
mysql -uroot -e "UPDATE mysql.user SET authentication_string=PASSWORD('${pwd}') WHERE user='root'";
mysql -uroot -e "FLUSH PRIVILEGES";
pkill -9 mysqld_safe
pkill -9 mysqld
sleep 2
service mysqld start

echo '==========================================='
echo "root密码成功修改为: ${pwd}"
echo "The root password set ${pwd}  successuful"''';
    
    public.writeFile('mysql_root.sh',root_mysql)
    os.system("/bin/bash mysql_root.sh " + password)
    os.system("rm -f mysql_root.sh")
    
    result = sql.table('config').where('id=?',(1,)).setField('mysql_root',password)
    print result;

#设置面板密码
def set_panel_pwd(password):
    import db
    sql = db.Sql()
    result = sql.table('users').where('id=?',(1,)).setField('password',public.md5(password))
    username = sql.table('users').where('id=?',(1,)).getField('username')
    print username;

#设置数据库目录
def set_mysql_dir(path):
    mysql_dir = '''#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
oldDir=`cat /etc/my.cnf |grep 'datadir'|awk '{print $3}'`
newDir=$1
mkdir $newDir
if [ ! -d "${newDir}" ];then
    echo 'The specified storage path does not exist!'
    exit
fi
echo "Stopping MySQL service..."
service mysqld stop

echo "Copying files, please wait..."
\cp -r -a $oldDir/* $newDir
chown -R mysql.mysql $newDir
sed -i "s#$oldDir#$newDir#" /etc/my.cnf

echo "Starting MySQL service..."
service mysqld start
echo ''
echo 'Successful'
echo '---------------------------------------------------------------------'
echo "Has changed the MySQL storage directory to: $newDir"
echo '---------------------------------------------------------------------'
''';


    public.writeFile('mysql_dir.sh',mysql_dir)
    os.system("/bin/bash mysql_dir.sh " + path)
    os.system("rm -f mysql_dir.sh")

#2.x转3.x
def panel2To3():
    try:
        filename = '/www/server/apache/version.pl'
        if os.path.exists(filename):
            version = public.readFile(filename);
            if version.find('2.2') != -1:
                print 'BT-Panel 3.x does not support apache2.2';
                return;
    except:
        pass
    
    
    import mysql,db,os,shutil,time
    os.system('service mysqld stop')
    os.system('pkill -9 mysqld_safe')
    os.system('pkill -9 mysqld')
    os.system('sleep 2')
    os.system('service mysqld start');
    os.system('service mysqld stop')
    os.system('mysqld_safe --skip-grant-tables&')
    
    
    time.sleep(3);
    sql = mysql.mysql();
    sqldb = db.Sql();
    
    #转移配置
    arr = sql.query('select * from bt_default.bt_config')[0]
    sqldb.table('config').where('id=?',(1,)).save('webserver,backup_path,sites_path,mysql_root',(arr[1],arr[2],arr[3],arr[5]));
    webserver = arr[1];
    setupPath = '/www/server';
    
    if webserver == 'nginx':
        #处理Nginx配置文件
        filename = setupPath + "/nginx/conf/nginx.conf"
        if os.path.exists(filename):
            conf = public.readFile(filename);
            if conf.find('include vhost/*.conf;') != -1:
                conf = conf.replace('include vhost/*.conf;','include ' + setupPath + '/panel/vhost/nginx/*.conf;');
                public.writeFile(filename,conf);
        #处理伪静态文件
        dstPath = setupPath + '/panel/vhost/rewrite'
        srcPath = setupPath + '/nginx/conf/rewrite'
        if os.path.exists(srcPath):
            if os.path.exists(dstPath): os.system('mv -f ' + dstPath + ' ' + dstPath + '_backup_' + time.strftime('%Y%m%d_%H%M%S',time.localtime()));
            os.system('cp -a -r ' + srcPath + ' ' + dstPath);
            os.system('chmod -R 644 ' + dstPath);
    else:
        #处理Apache配置文件
        filename = setupPath + "/apache/conf/httpd.conf"
        if os.path.exists(filename):
            conf = public.readFile(filename);
            if conf.find('IncludeOptional conf/vhost/*.conf') != -1:
                conf = conf.replace('IncludeOptional conf/vhost/*.conf','IncludeOptional ' + setupPath + '/panel/vhost/apache/*.conf');
                public.writeFile(filename,conf);
               
    
    #转移站点
    arr = sql.query('select * from bt_default.bt_sites')
    for siteArr in arr:
        #站点
        pid = sqldb.table('sites').add('name,path,status,ps,addtime',(siteArr[1],siteArr[3],siteArr[4],siteArr[6],str(siteArr[7])))
        
        #域名
        domains = siteArr[2].split(',');
        for domain in domains:
            tmp = domain.split(':');
            if len(tmp) < 2: tmp.append('80');
            sqldb.table('domain').add('pid,name,port,addtime',(pid,tmp[0],tmp[1],public.getDate()))
        
        #子目录
        barr = sql.query("select * from bt_default.bt_binding where pid='"+str(siteArr[0])+"'")
        for binding in barr:
            sqldb.table('binding').add('pid,domain,path,port,addtime',(pid,binding[2],binding[3],str(binding[4]),str(binding[5])))
        
        #迁移配置文件
        letPath = '/etc/letsencrypt/live';
        dstKey = letPath + '/' + siteArr[1] + '/privkey.pem';
        dstCsr = letPath + '/' + siteArr[1] + '/fullchain.pem';
        if webserver == 'nginx':
            confFile = setupPath + '/nginx/conf/vhost/' + siteArr[1] + '.conf';
            if os.path.exists(confFile):
                conf = public.readFile(confFile);
                conf = conf.replace('rewrite/',setupPath+'/panel/vhost/rewrite/').replace('key/' + siteArr[1] + '/key.key',dstKey).replace('key/' + siteArr[1] + '/key.csr',dstCsr);
                filename = setupPath + '/panel/vhost/nginx/' + siteArr[1] + '.conf';
                public.writeFile(filename,conf);
                os.system('chmod 644 ' + filename);
        else:
            confFile = setupPath + '/apache/conf/vhost/' + siteArr[1] + '.conf';
            if os.path.exists(confFile):
                conf = public.readFile(confFile);
                conf = conf.replace('conf/key/' + siteArr[1] + '/key.key',dstKey).replace('conf/key/' + siteArr[1] + '/key.csr',dstCsr);
                filename = setupPath + '/panel/vhost/apache/' + siteArr[1] + '.conf';
                public.writeFile(filename,conf);
                os.system('chmod 644 ' + filename);
        
        #转移其它配置文件
        try:
            otherConf = setupPath + '/'+webserver+'/conf/vhost/default.conf';
            if os.path.exists(otherConf):
                dstOther = setupPath + '/panel/vhost/'+webserver+'/default.conf';
                public.ExecShell('\\cp -a -r ' + otherConf + ' ' + dstOther)
            
            otherConf = setupPath + '/'+webserver+'/conf/vhost/phpfpm_status.conf';
            if os.path.exists(otherConf):
                dstOther = setupPath + '/panel/vhost/'+webserver+'/phpfpm_status.conf';
                public.ExecShell('\\cp -a -r ' + otherConf + ' ' + dstOther)
        except:
            pass
        
        #迁移证书
        srcKey = setupPath + '/' + webserver + '/conf/key/' + siteArr[1] + '/key.key'
        if os.path.exists(srcKey):
            os.system('mkdir -p ' + letPath + '/' + siteArr[1]);
            public.ExecShell('\\cp -a -r ' + srcKey + ' ' + dstKey)
            
        srcCsr = setupPath + '/' + webserver + '/conf/key/'+ siteArr[1] + '/key.csr'
        if os.path.exists(srcCsr):
            public.ExecShell('\\cp -a -r ' + srcCsr + ' ' + dstCsr)
        
        print siteArr[1] + ' -> done.\n';
    
    
    
    #转移数据库
    arr = sql.query('select * from bt_default.bt_databases');
    for databaseArr in arr:
        sqldb.table('databases').add('name,username,password,accept,ps,addtime',(databaseArr[1],databaseArr[2],databaseArr[3],databaseArr[4],databaseArr[5],str(databaseArr[6])));
    
    
    #转移FTP
    arr = sql.query('select * from bt_default.bt_ftps');
    for ftpArr in arr:
        sqldb.table('ftps').add('name,password,path,status,ps,addtime',(ftpArr[1],ftpArr[2],ftpArr[3],ftpArr[4],ftpArr[5],str(ftpArr[6])))
    
    #转移用户
    #arr = sql.query('select * from bt_default.bt_user')[0]
    #sqldb.table('users').where('id=?',(1,)).save('username,password,login_ip,login_time',(arr[1],arr[2],arr[3],arr[4]))
    
    
    #转移日志
    arr = sql.query('select * from bt_default.bt_logs');
    for log in arr:
        sqldb.table('logs').add('type,log,addtime',(log[1],log[2],log[3]))
    
    
    #转移防火墙记录
    arr = sql.query('select * from bt_default.bt_firewall');
    ports = ['80','22','21','20','888','8888']
    for fw in arr:
        if str(fw[1]) in ports: continue;
        sqldb.table('firewall').add('port,ps,addtime',(fw[1],fw[2],fw[3]))
    
    
    #转移计划任务记录
    try:
        arr = sql.query('select * from bt_default.bt_crontab');
        for cron in arr:
            sqldb.table('crontab').add('name,type,where1,where_hour,where_minute,echo,addtime',(cron[1],cron[2],cron[3],cron[4],cron[5],cron[6],cron[7]))
    except:
        pass
    
    
    os.system('/etc/init.d/yunclient stop')
    os.system('chkconfig --del yunclient')
    os.system('rm -f /etc/init.d/yunclient')
    os.system('pkill -9 mysqld_safe')
    os.system('pkill -9 mysqld')
    os.system('sleep 2 && service mysqld start')
    if os.path.exists('/etc/init.d/nginx'): os.system('/etc/init.d/nginx reload');
    if os.path.exists('/etc/init.d/httpd'): os.system('/etc/init.d/httpd reload');
    
    print '=========================';
    print 'successful!'

#封装
def PackagePanel():
    print '========================================================'
    print '|-正在清理日志信息...',
    public.M('logs').where('id!=?',(0,)).delete();
    print '\t\t\033[1;32m[done]\033[0m'
    print '|-正在清理任务历史...',
    public.M('tasks').where('id!=?',(0,)).delete();
    print '\t\t\033[1;32m[done]\033[0m'
    print '|-正在清理网络监控记录...',
    public.M('network').dbfile('system').where('id!=?',(0,)).delete();
    print '\t\033[1;32m[done]\033[0m'
    print '|-正在清理CPU监控记录...',
    public.M('cpuio').dbfile('system').where('id!=?',(0,)).delete();
    print '\t\033[1;32m[done]\033[0m'
    print '|-正在清理磁盘监控记录...',
    public.M('diskio').dbfile('system').where('id!=?',(0,)).delete();
    print '\t\033[1;32m[done]\033[0m'
    print '|-正在清理IP信息...',
    os.system('rm -f /www/server/panel/data/iplist.txt')
    os.system('rm -f /www/server/panel/data/address.pl')
    os.system('rm -f /www/server/panel/data/*.login')
    os.system('rm -f /www/server/panel/data/domain.conf')
    print '\t\033[1;32m[done]\033[0m'
    public.writeFile('/www/server/panel/install.pl',"True");
    port = public.readFile('data/port.pl').strip();
    print '========================================================'
    print '\033[1;32m|-面板封装成功,请不要再登陆面板做任何其它操作!\033[0m'
    print '\033[1;41m|-面板初始化地址: http://{SERVERIP}:'+port+'/install\033[0m'

#清空正在执行的任务
def CloseTask():
    ncount = public.M('tasks').where('status!=?',(1,)).delete();
    os.system("kill `ps -ef |grep 'python panelSafe.pyc'|grep -v grep|grep -v panelExec|awk '{print $2}'`");
    os.system("kill `ps -ef |grep 'install_soft.sh'|grep -v grep|grep -v panelExec|awk '{print $2}'`");
    os.system('/etc/init.d/bt restart');
    print "成功清理 " + int(ncount) + " 个任务!"
    
#自签证书
def CreateSSL():
    import OpenSSL
    key = OpenSSL.crypto.PKey()
    key.generate_key( OpenSSL.crypto.TYPE_RSA, 2048 )
    cert = OpenSSL.crypto.X509()
    cert.set_serial_number(0)
    cert.get_subject().CN = public.GetLocalIp();
    cert.set_issuer(cert.get_subject())
    cert.gmtime_adj_notBefore( 0 )
    cert.gmtime_adj_notAfter( 10*365*24*60*60 )
    cert.set_pubkey( key )
    cert.sign( key, 'md5' )
    cert_ca = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    private_key = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
    if len(cert_ca) > 100 and len(private_key) > 100:
        public.writeFile('ssl/certificate.pem',cert_ca)
        public.writeFile('ssl/privateKey.pem',private_key)
        print 'success';
        return;
    print 'error';

#创建文件
def CreateFiles(path,num):
    if not os.path.exists(path): os.system('mkdir -p ' + path);
    import time;
    for i in range(num):
        filename = path + '/' + str(time.time()) + '__' + str(i)
        open(path,'w+').close()

#计算文件数量
def GetFilesCount(path):
    i=0;
    for name in os.listdir(path): i += 1;
    return i;


#清理系统垃圾
def ClearSystem():
    count = total = 0;
    tmp_total,tmp_count = ClearMail();
    count += tmp_count;
    total += tmp_total;
    print '======================================================================='
    tmp_total,tmp_count = ClearSession();
    count += tmp_count;
    total += tmp_total;
    print '======================================================================='
    tmp_total,tmp_count = ClearOther();
    count += tmp_count;
    total += tmp_total;
    print '======================================================================='
    print '\033[1;32m|-系统垃圾清理完成，共删除['+str(count)+']个文件,释放磁盘空间['+ToSize(total)+']\033[0m';

#清理邮件日志
def ClearMail():
    rpath = '/var/spool';
    total = count = 0;
    import shutil
    con = ['cron','anacron','mail'];
    for d in os.listdir(rpath):
        if d in con: continue;
        dpath = rpath + '/' + d
        print '|-正在清理' + dpath + ' ...';
        time.sleep(0.2);
        num = size = 0;
        for n in os.listdir(dpath):
            filename = dpath + '/' + n
            fsize = os.path.getsize(filename);
            print '|---['+ToSize(fsize)+'] del ' + filename,
            size += fsize
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)
            print '\t\033[1;32m[OK]\033[0m'
            num += 1
        print '|-已清理['+dpath+'],删除['+str(num)+']个文件,共释放磁盘空间['+ToSize(size)+']';
        total += size;
        count += num;
    print '======================================================================='
    print '|-已完成spool的清理，删除['+str(count)+']个文件,共释放磁盘空间['+ToSize(total)+']';
    return total,count

#清理php_session文件
def ClearSession():
    spath = '/tmp'
    total = count = 0;
    import shutil
    print '|-正在清理PHP_SESSION ...';
    for d in os.listdir(spath):
        if d.find('sess_') == -1: continue;
        filename = spath + '/' + d;
        fsize = os.path.getsize(filename);
        print '|---['+ToSize(fsize)+'] del ' + filename,
        total += fsize
        if os.path.isdir(filename):
            shutil.rmtree(filename)
        else:
            os.remove(filename)
        print '\t\033[1;32m[OK]\033[0m'
        count += 1;
    print '|-已完成php_session的清理，删除['+str(count)+']个文件,共释放磁盘空间['+ToSize(total)+']';
    return total,count

#清空回收站
def ClearRecycle_Bin():
    import files
    f = files.files();
    f.Close_Recycle_bin(None);
    
#清理其它
def ClearOther():
    clearPath = [
                 {'path':'/www/server/panel','find':'testDisk_'},
                 {'path':'/www/wwwlogs','find':'log'},
                 {'path':'/tmp','find':'panelBoot.pl'},
                 {'path':'/www/server/panel/install','find':'.rpm'}
                 ]
    
    total = count = 0;
    print '|-正在清理临时文件及网站日志 ...';
    for c in clearPath:
        for d in os.listdir(c['path']):
            if d.find(c['find']) == -1: continue;
            filename = c['path'] + '/' + d;
            fsize = os.path.getsize(filename);
            print '|---['+ToSize(fsize)+'] del ' + filename,
            total += fsize
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)
            print '\t\033[1;32m[OK]\033[0m'
            count += 1;
    public.serviceReload();
    os.system('/etc/init.d/bt restart > /dev/null');
    print '|-已完成临时文件及网站日志的清理，删除['+str(count)+']个文件,共释放磁盘空间['+ToSize(total)+']';
    return total,count

#字节单位转换
def ToSize(size):
    ds = ['b','KB','MB','GB','TB']
    for d in ds:
        if size < 1024: return str(size)+d;
        size = size / 1024;
    return '0b';
            

if __name__ == "__main__":
    type = sys.argv[1];
    if type == 'root':
        set_mysql_root(sys.argv[2])
    elif type == 'panel':
        set_panel_pwd(sys.argv[2])
    elif type == 'mysql_dir':
        set_mysql_dir(sys.argv[2])
    elif type == 'to':
        panel2To3()
    elif type == 'package':
        PackagePanel();
    elif type == 'ssl':
        CreateSSL();
    elif type == 'port':
        CheckPort();
    elif type == 'clear':
        ClearSystem();
    else:
        print 'ERROR: Parameter error'
