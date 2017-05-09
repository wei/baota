#coding: utf-8
#  + -------------------------------------------------------------------
# | 宝塔Linux面板
#  + -------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http:#bt.cn) All rights reserved.
#  + -------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
#  + -------------------------------------------------------------------
import public,db,re,os,web,firewalls
class ftp:
    __runPath = None
    
    def __init__(self):
        self.__runPath = web.ctx.session.setupPath + '/pure-ftpd/bin'
        
    
    #添加FTP
    def AddUser(self,get):
        try:
            import files,time
            fileObj=files.files()
            if re.search("\W + ",get['ftp_username']): return {'status':False,'code':501,'msg':'用户名不合法,不能带有特殊符号'}
            if len(get['ftp_username']) < 3: return {'status':False,'code':501,'msg':'用户名不合法,不能少于3个字符'}
            if not fileObj.CheckDir(get['path']): return {'status':False,'code':501,'msg':'不能以系统关键目录作为FTP目录'}
            if public.M('ftps').where('name=?',(get.ftp_username.strip(),)).count(): return public.returnMsg(False,'用户[' + get.ftp_username + ']已存在')
            username = get['ftp_username'].replace(' ','')
            password = get['ftp_password']
            get.path = get['path'].replace(' ','')
            get.path = get.path.replace("\\", "/")
            fileObj.CreateDir(get)
            os.system('chown www.www ' + get.path)
            public.ExecShell(self.__runPath + '/pure-pw useradd ' + username + ' -u www -d ' + get.path + '<<EOF \n' + password + '\n' + password + '\nEOF')
            self.FtpReload()
            ps=get['ps']
            if get['ps']=='': ps='填写备注'
            addtime=time.strftime('%Y-%m-%d %X',time.localtime())
            
            pid = 0
            if hasattr(get,'pid'): pid = get.pid
            public.M('ftps').add('pid,name,password,path,status,ps,addtime',(pid,username,password,get.path,1,ps,addtime))
            public.WriteLog('FTP管理', '添加FTP用户[' + username + ']成功!')
            return public.returnMsg(True,'添加成功')
        except Exception,ex:
            public.WriteLog('FTP管理', '添加FTP用户[' + username + ']失败 => ' + str(ex))
            return public.returnMsg(False,'添加失败')
    
    #删除用户
    def DeleteUser(self,get):
        try:
            username = get['username']
            id = get['id']
            public.ExecShell(self.__runPath + '/pure-pw userdel ' + username)
            self.FtpReload()
            public.M('ftps').where("id=?",(id,)).delete()
            public.WriteLog('FTP管理', '删除FTP用户[' + username + ']成功!')
            return public.returnMsg(True, "删除用户成功!")
        except Exception,ex:
            public.WriteLog('FTP管理', '删除FTP用户[' + username + ']失败 => ' + str(ex))
            return public.returnMsg(False,'删除失败')
    
    
    #修改用户密码
    def SetUserPassword(self,get):
        try:
            id = get['id']
            username = get['ftp_username']
            password = get['new_password']
            public.ExecShell(self.__runPath + '/pure-pw passwd ' + username + '<<EOF \n' + password + '\n' + password + '\nEOF')
            self.FtpReload()
            public.M('ftps').where("id=?",(id,)).setField('password',password)
            public.WriteLog('FTP管理', 'FTP用户[' + username + ']，修改密码成功!')
            return(True)
        except Exception,ex:
            public.WriteLog('FTP管理', 'FTP用户[' + username + ']，修改密码失败 => ' + str(ex))
            return public.returnMsg(False,'修改密码失败')
    
    
    #设置用户状态
    def SetStatus(self,get):
        try:
            id = get['id']
            username = get['username']
            status = get['status']
            if int(status)==0:
                public.ExecShell(self.__runPath + '/pure-pw usermod ' + username + ' -r 1')
            else:
                public.ExecShell(self.__runPath + '/pure-pw usermod ' + username + " -r ''")
            self.FtpReload()
            public.M('ftps').where("id=?",(id,)).setField('status',status)
            public.WriteLog('FTP管理', "停用FTP用户[" + username + "]成功!")
            return public.returnMsg(True, '操作成功')
        except Exception,ex:
            public.WriteLog('FTP管理', '停用FTP用户[' + username + ']失败 => ' + str(ex))
            return public.returnMsg(False,'停用FTP用户失败')
    
    '''
     * 设置FTP端口
     * @param Int _GET['port'] 端口号 
     * @return bool
     '''
    def setPort(self,get):
        try:
            port = get['port']
            if int(port) < 1 or int(port) > 65535: return public.returnMsg(False,'端口格式错误,范围:1-65535')
            file = web.ctx.session.setupPath + '/pure-ftpd/etc/pure-ftpd.conf'
            conf = public.readFile(file)
            rep = u"\n#?\s*Bind\s+[0-9]+\.[0-9]+\.[0-9]+\.+[0-9]+,([0-9]+)"
            #preg_match(rep,conf,tmp)
            conf = re.sub(rep,"\nBind        0.0.0.0," + port,conf)
            public.writeFile(file,conf)
            public.ExecShell('/etc/init.d/pure-ftpd restart')
            public.WriteLog('FTP管理', "修改FTP端口为[port]成功!")
            #添加防火墙
            #data = ftpinfo(port=port,ps = 'FTP端口')
            get.port=port
            get.ps = 'FTP端口'
            firewalls.firewalls().AddAcceptPort(get)
            web.ctx.session.port=port
            return public.returnMsg(True, '修改成功')
        except Exception,ex:
            public.WriteLog('FTP管理', '设置FTP端口失败 => ' + str(ex))
            return public.returnMsg(False,'修改失败')
    
    #重载配置
    def FtpReload(self):
        public.ExecShell(self.__runPath + '/pure-pw mkdb '  +  web.ctx.session.setupPath + '/pure-ftpd/etc/pureftpd.pdb')
