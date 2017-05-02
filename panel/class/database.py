#coding: utf-8
#-------------------------------------------------------------------
# 宝塔Linux面板
#-------------------------------------------------------------------
# Copyright (c) 2015-2016 宝塔软件(http:#bt.cn) All rights reserved.
#-------------------------------------------------------------------
# Author: 黄文良 <2879625666@qq.com>
#-------------------------------------------------------------------

#------------------------------
# 数据库管理类
#------------------------------
import public,db,web,re,time,os,sys,mysql
reload(sys)
sys.setdefaultencoding('utf-8')
class database:
    
    #添加数据库
    def AddDatabase(self,get):
        try:
            data_name = get['name'].strip()
            if data_name == 'root' or data_name == 'mysql' or data_name == 'test' or len(data_name) < 3:
                return public.returnMsg(False,'数据库名称不合法,或少于3个字符!')
            
            if len(data_name) > 16: return public.returnMsg(False, '数据库名不能大于16位')
            
            reg = "^[a-zA-Z]{1}\w+$"
            if not re.match(reg, data_name): return public.returnMsg(False,'数据库名不能带有特殊符号，且首位必需为字母')
            
            data_pwd = get['password']
            if len(data_pwd)<1:
                data_pwd = public.md5(time.time())[0:8]
            
            sql = public.M('databases')
            if sql.where("name=?",(data_name,)).count(): return public.returnMsg(False,'数据库已存在!')
            address = get['address'].strip()
            user = '是'
            username = data_name
            password = data_pwd
            
            codeing = get['codeing']
            
            wheres={
                    'utf8'      :   'utf8_general_ci',
                    'utf8mb4'   :   'utf8mb4_general_ci',
                    'gbk'       :   'gbk_chinese_ci',
                    'big5'      :   'big5_chinese_ci'
                    }
            codeStr=wheres[codeing]
            #添加MYSQL
            result = mysql.mysql().execute("create database " + data_name + " DEFAULT CHARACTER SET " + codeing + " COLLATE " + codeStr)
            isError=self.IsSqlError(result)
            if  isError != None: return isError
            mysql.mysql().execute("drop user '" + username + "'@'localhost'")
            mysql.mysql().execute("drop user '" + username + "'@'" + address + "'")
            mysql.mysql().execute("grant all privileges on " + data_name + ".* to '" + username + "'@'localhost' identified by '" + data_pwd + "'")
            mysql.mysql().execute("grant all privileges on " + data_name + ".* to '" + username + "'@'" + address + "' identified by '" + data_pwd + "'")
            mysql.mysql().execute("flush privileges")
            
            
            if get['ps'] == '': get['ps']='填写备注'
            addTime = time.strftime('%Y-%m-%d %X',time.localtime())
            
            pid = 0
            if hasattr(get,'pid'): pid = get.pid
            #添加入SQLITE
            sql.add('pid,name,username,password,accept,ps,addtime',(pid,data_name,username,password,address,get['ps'],addTime))
            public.WriteLog("数据库管理", "添加数据库[" + data_name + "]成功!")
            return public.returnMsg(True,'添加成功')
        except Exception,ex:
            public.WriteLog("数据库管理", "添加数据库[" + data_name + "]失败 => "  +  str(ex))
            return public.returnMsg(False,'添加失败')
    
    #检测数据库执行错误
    def IsSqlError(self,mysqlMsg):
        mysqlMsg=str(mysqlMsg)
        if "using password:" in mysqlMsg: return public.returnMsg(False,'数据库管理密码错误!')
        if "Connection refused" in mysqlMsg: return public.returnMsg(False,'数据库连接失败,请检查数据库服务是否启动!')
        if "1133" in mysqlMsg: return public.returnMsg(False,'数据库用户不存在!')
        return None
    
    #删除数据库
    def DeleteDatabase(self,get):
        try:
            id=get['id']
            name = get['name']
            if name == 'bt_default': return public.returnMsg(False,'不能删除宝塔默认数据库!')
            accept = public.M('databases').where("id=?",(id,)).getField('accept')
            #删除MYSQL
            result = mysql.mysql().execute("drop database " + name)
            isError=self.IsSqlError(result)
            if  isError != None: return isError
            mysql.mysql().execute("drop user '" + name + "'@'localhost'")
            mysql.mysql().execute("drop user '" + name + "'@'" + accept + "'")
            mysql.mysql().execute("flush privileges")
            #删除SQLITE
            public.M('databases').where("id=?",(id,)).delete()
            public.WriteLog("数据库管理", "删除数据库[" + name + "]成功!")
            return public.returnMsg(True, '删除数据库成功!')
        except Exception,ex:
            public.WriteLog("数据库管理", "删除数据库[" + data_name + "]失败 => "  +  str(ex))
            return public.returnMsg(False,'删除数据库失败')
    
    #设置ROOT密码
    def SetupPassword(self,get):
        password = get['password'].strip()
        try:
            rep = "^[\w#@%\.]+$"
            if not re.match(rep, password): return public.returnMsg(False, '密码中请不要带有特殊字符!')
            mysql_root = public.M('config').where("id=?",(1,)).getField('mysql_root')
            #修改MYSQL
            result = mysql.mysql().query("show databases")
            isError=self.IsSqlError(result)
            if  isError != None: 
                #尝试使用新密码
                public.M('config').where("id=?",(1,)).setField('mysql_root',password)
                result = mysql.mysql().query("show databases")
                isError=self.IsSqlError(result)
                if  isError != None: 
                    root_mysql = '''#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
pwd=$1
/etc/init.d/mysqld stop
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
/etc/init.d/mysqld start

echo '==========================================='
echo "root密码成功修改为: ${pwd}"
echo "The root password set ${pwd}  successuful"''';
            
                public.writeFile('mysql_root.sh',root_mysql)
                os.system("sh mysql_root.sh " + password)
                os.system("rm -f mysql_root.sh")
                
                
            else:
                if '5.7' in public.readFile(web.ctx.session.setupPath + '/mysql/version.pl'):
                    result = mysql.mysql().execute("update mysql.user set authentication_string=password('" + password + "') where User='root'")
                else:
                    result = mysql.mysql().execute("update mysql.user set Password=password('" + password + "') where User='root'")
                mysql.mysql().execute("flush privileges")

            msg = 'ROOT密码修改成功!'
            #修改SQLITE
            public.M('config').where("id=?",(1,)).setField('mysql_root',password)  
            public.WriteLog("数据库管理", "设置root密码成功!")
            web.ctx.session.config['mysql_root']=password
            return public.returnMsg(True,msg)
        except Exception,ex:
            return public.returnMsg(False,'修改密码失败!');
    
    #修改用户密码
    def ResDatabasePassword(self,get):
        try:
            newpassword = get['password']
            username = get['username']
            id = get['id']
            if username == 'bt_default': return public.returnMsg(False,'不能修改宝塔数据库的密码!')
            rep = "^[\w#@%\.]+$"
            if len(re.search(rep, newpassword).groups()) >0: return public.returnMsg(False, '密码中请不要带有特殊字符!')
            #修改MYSQL
            if '5.7' in public.readFile(web.ctx.session.setupPath + '/mysql/version.pl'):
                result = mysql.mysql().execute("update mysql.user set authentication_string=password('" + newpassword + "') where User='" + username + "'")
            else:
                result = mysql.mysql().execute("update mysql.user set Password=password('" + newpassword + "') where User='" + username + "'")
            
            isError=self.IsSqlError(result)
            if  isError != None: return isError
            mysql.mysql().execute("flush privileges")
            
            if result==False: return public.returnMsg(False,'修改失败,数据库用户不存在!')
            #修改SQLITE
            if int(id) > 0:
                public.M('databases').where("id=?",(id,)).setField('password',newpassword)
            else:
                public.M('config').where("id=?",(id,)).setField('mysql_root',newpassword)
                web.ctx.session.config['mysql_root'] = newpassword
            
            public.WriteLog("数据库管理", "修改数据库用户[" + username + "]密码成功!")
            return public.returnMsg(True,'修改数据库[' + username + ']密码成功!')
        except Exception,ex:
            public.WriteLog("数据库管理", "修改数据库用户[" + username + "]密码失败 => "  +  str(ex))
            return public.returnMsg(False,'修改数据库[' + username + ']密码失败!')
    
    def setMyCnf(self,action = True):
        myFile = '/etc/my.cnf'
        mycnf = public.readFile(myFile)
        root = web.ctx.session.config['mysql_root']
        pwdConfig = "\n[mysqldump]\nuser=root\npassword=root"
        rep = "\n\[mysqldump\]\nuser=root\npassword=.+"
        if action:
            if mycnf.find(pwdConfig) > -1: return
            if mycnf.find("\n[mysqldump]\nuser=root\n") > -1:
                mycnf = mycnf.replace(rep, pwdConfig)
            else:
                mycnf  += "\n[mysqldump]\nuser=root\npassword=root"
            
        else:
            mycnf = mycnf.replace(rep, '')
        
        
        public.writeFile(myFile,mycnf)
    
    
    #备份
    def ToBackup(self,get):
        #try:
        id = get['id']
        name = public.M('databases').where("id=?",(id,)).getField('name')
        root = web.ctx.session.config['mysql_root']
        if not os.path.exists(web.ctx.session.config['backup_path'] + '/database'): os.system('mkdir -p ' + web.ctx.session.config['backup_path'] + '/database');
        mycnf = public.readFile('/etc/my.cnf');
        rep = "\[mysqldump\]\nuser=root"
        sea = '[mysqldump]\n'
        subStr = sea + "user=root\npassword=" + root+"\n";
        mycnf = mycnf.replace(sea,subStr)
        if len(mycnf) > 100:
            public.writeFile('/etc/my.cnf',mycnf);
        
        fileName = name + '_' + time.strftime('%Y%m%d_%H%M%S',time.localtime()) + '.sql.gz'
        backupName = web.ctx.session.config['backup_path'] + '/database/' + fileName
        public.ExecShell("/www/server/mysql/bin/mysqldump --opt --default-character-set=utf8 " + name + " | gzip > " + backupName)
        if not os.path.exists(backupName): return public.returnMsg(False,'备份失败!');
        
        mycnf = public.readFile('/etc/my.cnf');
        mycnf = mycnf.replace(subStr,sea)
        if len(mycnf) > 100:
            public.writeFile('/etc/my.cnf',mycnf);
        
        sql = public.M('backup')
        addTime = time.strftime('%Y-%m-%d %X',time.localtime())
        sql.add('type,name,pid,filename,size,addtime',(1,fileName,id,backupName,0,addTime))
        public.WriteLog("数据库管理", "备份数据库[" + name + "]成功!")
        return public.returnMsg(True, '备份成功!')
        #except Exception,ex:
            #public.WriteLog("数据库管理", "备份数据库[" + name + "]失败 => "  +  str(ex))
            #return public.returnMsg(False,'备份失败!')
    
    #删除备份文件
    def DelBackup(self,get):
        try:
            id = get.id
            where = "id=?"
            filename = public.M('backup').where(where,(id,)).getField('filename')
            if os.path.exists(filename): os.remove(filename)
            
            if filename == 'qiniu':
                name = public.M('backup').where(where,(id,)).getField('name');
                public.ExecShell("python "+web.ctx.session.setupPath + '/panel/script/backup_qiniu.py delete_file ' + name)
            
            public.M('backup').where(where,(id,)).delete()
            public.WriteLog("数据库管理", "删除备份文件[" + filename + "]成功!")
            return public.returnMsg(True, '删除备份文件成功!');
        except Exception,ex:
            public.WriteLog("数据库管理", "删除备份文件[" + filename + "]失败 => "  +  str(ex))
            return public.returnMsg(False,'删除备份文件失败!')
    
    #导入
    def InputSql(self,get):
        try:
            name = get['name']
            file = get['file']
            root = web.ctx.session.config['mysql_root']
            tmp = file.split('.')
            exts = ['sql','gz','zip']
            ext = tmp[len(tmp) -1]
            if ext not in exts:
                return public.returnMsg(False, '请选择sql、gz、zip文件格式!')
            
            if ext != 'sql':
                tmp = file.split('/')
                tmpFile = tmp[len(tmp)-1]
                tmpFile = tmpFile.replace('.sql.' + ext, '.sql')
                tmpFile = tmpFile.replace('.' + ext, '.sql')
                tmpFile = tmpFile.replace('tar.', '')
                backupPath = web.ctx.session.config['backup_path'] + '/database'
                
                if ext == 'zip':
                    public.ExecShell("cd "  +  backupPath  +  " && unzip " +  file)
                else:
                    public.ExecShell("cd "  +  backupPath  +  " && tar zxf " +  file)
                    if not os.path.exists(backupPath  +  "/"  +  tmpFile): public.ExecShell("cd "  +  backupPath  +  " && gunzip -q " +  file)
                 
                if not os.path.exists(backupPath + '/' + tmpFile) or tmpFile == '': return public.returnMsg(False, '文件[' + tmpFile + ']不存在!')
                public.ExecShell("cd "  +  backupPath  +  " && "  +  web.ctx.session.setupPath + "/mysql/bin/mysql -uroot -p" + root + " --default-character-set=utf-8 " + name + " < " + tmpFile + " && rm -f " +  tmpFile)
            else:
                public.ExecShell(web.ctx.session.setupPath + "/mysql/bin/mysql -uroot -p" + root + " " + name + " < " +  file)
            
            public.WriteLog("数据库管理", "导入数据库[" + name + "]成功!")
            return public.returnMsg(True, '导入数据库成功!');
        except Exception,ex:
            public.WriteLog("数据库管理", "导入数据库[" + name + "]失败 => "  +  str(ex))
            return public.returnMsg(False,'导入数据库失败!')
    
    #同步数据库到服务器
    def SyncToDatabases(self,get):
        type = int(get['type'])
        n = 0
        sql = public.M('databases')
        if type == 0:
            data = sql.field('id,name,username,password,accept').select()
            for value in data:
                result = self.ToDataBase(value)
                if result == 1: n +=1
            
        else:
            data = get.data
            for value in data:
                find = sql.where("id=?",(value,)).field('id,name,username,password,accept').find()   
                result = self.ToDataBase(find)
                if result == 1: n +=1
        
        return public.returnMsg(True,"本次共同步了:" + str(n) + "数据库")
    
    
    #添加到服务器
    def ToDataBase(self,find):
        if find['username'] == 'bt_default': return 0
        if len(find['password']) < 3 :
            find['username'] = find['name']
            find['password'] = public.md5(str(time.time()) + find['name'])[0:10]
            public.M('databases').where("id=?",(find['id'],)).save('password,username',(find['password'],find['username']))
        
        result = mysql.mysql().execute("create database " + find['name'])
        if "using password:" in str(result): return -1
        if "Connection refused" in str(result): return -1
        mysql.mysql().execute("drop user '" + find['username'] + "'@'localhost'")
        mysql.mysql().execute("drop user '" + find['username'] + "'@'" + find['accept'] + "'")
        password = find['password']
        if find['password']!="" and len(find['password']) > 20:
            password = find['password']
        
        mysql.mysql().execute("grant all privileges on " + find['name'] + ".* to '" + find['username'] + "'@'localhost' identified by '" + password + "'")
        mysql.mysql().execute("grant all privileges on " + find['name'] + ".* to '" + find['username'] + "'@'" + find['accept'] + "' identified by '" + password + "'")
        mysql.mysql().execute("flush privileges")
        return 1
    
    
    #从服务器获取数据库
    def SyncGetDatabases(self,get):
        data = mysql.mysql().query("show databases")
        isError = self.IsSqlError(data)
        if isError != None: return isError
        users = mysql.mysql().query("select User,Host from mysql.user where User!='root' AND Host!='localhost' AND Host!=''")
        sql = public.M('databases')
        nameArr = ['information_schema','performance_schema','mysql']
        n = 0
        for  value in data:
            b = False
            for key in nameArr:
                if value[0] == key:
                    b = True 
                    break
            if b:continue
            if sql.where("name=?",(value[0],)).count(): continue
            host = '127.0.0.1'
            for user in users:
                if value[0] == user[0]:
                    host = user[1]
                    break
                
            ps = '填写备注'
            if value[0] == 'test':
                    ps = '测试数据库'
            addTime = time.strftime('%Y-%m-%d %X',time.localtime())
            if sql.table('databases').add('name,username,password,accept,ps,addtime',(value[0],value[0],'',host,ps,addTime)): n +=1
        
        return public.returnMsg(True,'本次共从服务器获取' + str(n) + '个数据库!')
    
    
    #获取数据库权限
    def GetDatabaseAccess(self,get):
        name = get['name']
        users = mysql.mysql().query("select User,Host from mysql.user where User='" + name + "' AND Host!='localhost'")
        isError = self.IsSqlError(users)
        if isError != None: return isError
        if len(users)<1:
            return public.returnMsg(True,['',''])
        
        return public.returnMsg(True,users[0])
    
    #设置数据库权限
    def SetDatabaseAccess(self,get):
        try:
            name = get['name']
            access = get['access']
            #if access != '%' and filter_var(access, FILTER_VALIDATE_IP) == False: return public.returnMsg(False, '权限格式不合法')
            password = public.M('databases').where("name=?",(name,)).getField('password')
            mysql.mysql().execute("delete from mysql.user where User='" + name + "' AND Host!='localhost'")
            mysql.mysql().execute("grant all privileges on " + name + ".* to '" + name + "'@'" + access + "' identified by '" + password + "'")
            mysql.mysql().execute("flush privileges")
            return public.returnMsg(True, '设置成功!')
        except Exception,ex:
            public.WriteLog("数据库管理", "设置数据库权限[" + name + "]失败 => "  +  str(ex))
            return public.returnMsg(False,'设置数据库权限失败!')
        