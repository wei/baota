#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板 x3
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2017 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

import public,web,re,sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
class config:
    
    def setPassword(self,get):
        #return public.returnMsg(False,'体验服务器，禁止修改!')
        if get.password1 != get.password2: return public.returnMsg(False,'两次输入的密码不一致，请重新输入!')
        if len(get.password1) < 5: return public.returnMsg(False,'用户密码不能小于5位!')
        public.M('users').where("username=?",(web.ctx.session.username,)).setField('password',public.md5(get.password1))
        public.WriteLog('面板配置','修改用户['+web.ctx.session.username+']密码成功!')
        return public.returnMsg(True,'密码修改成功!')
    
    def setUsername(self,get):
        #return public.returnMsg(False,'体验服务器，禁止修改!')
        if get.username1 != get.username2: return public.returnMsg(False,'两次输入的用户名不一致，请重新输入!')
        if len(get.username1) < 3: return public.returnMsg(False,'用户名不能小于3位!')
        public.M('users').where("username=?",(web.ctx.session.username,)).setField('username',get.username1)
        web.ctx.session.username = get.username1
        public.WriteLog('面板配置','修改用户['+get.username2+']的用户名为['+get.username1+']!')
        return public.returnMsg(True,'用户名修改成功!')
    
    def setPanel(self,get):
        #return public.returnMsg(False,'体验服务器，禁止修改!')
        if not public.IsRestart(): return public.returnMsg(False,'请等待所有安装任务完成再执行!');
        if get.domain:
            reg = "^([\w\-\*]{1,100}\.){1,4}(\w{1,10}|\w{1,10}\.\w{1,10})$";
            if not re.match(reg, get.domain): return public.returnMsg(False,'域名格式不正确!');
        isReWeb = False
        oldPort = web.ctx.host.split(':')[1];
        newPort = get.port;
        if oldPort != get.port:
            if self.IsOpen(get.port):
                return public.returnMsg(False,'端口['+get.port+']已被占用!')
            if int(get.port) >= 65535 or  int(get.port) < 100: return public.returnMsg(False,'端口范围不正确!');
            public.writeFile('data/port.pl',get.port)
            import firewalls
            get.ps = '新的面板端口';
            fw = firewalls.firewalls();
            fw.AddAcceptPort(get);
            get.port = oldPort;
            get.id = public.M('firewall').where("port=?",(oldPort,)).getField('id');
            fw.DelAcceptPort(get);
            isReWeb = True
        
        if get.webname != web.ctx.session.webname: 
            web.ctx.session.webname = get.webname
            public.writeFile('data/title.pl',get.webname);
        
        limitip = public.readFile('data/limitip.conf');
        if get.limitip != limitip: public.writeFile('data/limitip.conf',get.limitip);
        
        public.writeFile('data/domain.conf',get.domain.strip())
        public.writeFile('data/iplist.txt',get.address)
        
        public.M('config').where("id=?",('1',)).save('backup_path,sites_path',(get.backup_path,get.sites_path))
        web.ctx.session.config['backup_path'] = get.backup_path
        web.ctx.session.config['sites_path'] = get.sites_path
        
        data = {'uri':web.ctx.fullpath,'host':web.ctx.host.split(':')[0]+':'+newPort,'status':True,'isReWeb':isReWeb,'msg':'配置已保存!'}
        public.WriteLog('面板配置','设置面板端口['+newPort+'],域名['+get.domain+'],默认备份路径['+get.backup_path+'],默认网站路径['+get.sites_path+'],服务器IP['+get.address+'],授权IP['+get.limitip+']!')
        return data
    
    def setPathInfo(self,get):
        #设置PATH_INFO
        version = get.version
        type = get.type
        if web.ctx.session.webserver == 'nginx':
            path = web.ctx.session.setupPath+'/nginx/conf/enable-php-'+version+'.conf';
            conf = public.readFile(path);
            rep = "\s+#*include\s+pathinfo.conf;";
            if type == 'on':
                conf = re.sub(rep,'\n\t\t\tinclude pathinfo.conf;',conf)
            else:
                conf = re.sub(rep,'\n\t\t\t#include pathinfo.conf;',conf)
            public.writeFile(path,conf)
            public.serviceReload();
        
        path = web.ctx.session.setupPath+'/php/'+version+'/etc/php.ini';
        conf = public.readFile(path);
        rep = "\n*\s*cgi\.fix_pathinfo\s*=\s*([0-9]+)\s*\n";
        status = '0'
        if type == 'on':status = '1'
        conf = re.sub(rep,"\ncgi.fix_pathinfo = "+status+"\n",conf)
        public.writeFile(path,conf)
        public.WriteLog("PHP配置", "设置PHP-"+version+" PATH_INFO模块为["+type+"]!");
        public.phpReload(version);
        return public.returnMsg(True,type+'设置成功!');
    
    
    #设置文件上传大小限制
    def setPHPMaxSize(self,get):
        version = get.version
        max = get.max
        
        if int(max) < 2: return public.returnMsg(False,'上传大小限制不能小于2M!')
        
        #设置PHP
        path = web.ctx.session.setupPath+'/php/'+version+'/etc/php.ini'
        conf = public.readFile(path)
        rep = u"\nupload_max_filesize\s*=\s*[0-9]+M"
        conf = re.sub(rep,u'\nupload_max_filesize = '+max+'M',conf)
        rep = u"\npost_max_size\s*=\s*[0-9]+M"
        conf = re.sub(rep,u'\npost_max_size = '+max+'M',conf)
        public.writeFile(path,conf)
        
        if web.ctx.session.webserver == 'nginx':
            #设置Nginx
            path = web.ctx.session.setupPath+'/nginx/conf/nginx.conf'
            conf = public.readFile(path)
            rep = "client_max_body_size\s+([0-9]+)m"
            tmp = re.search(rep,conf).groups()
            if int(tmp[0]) < int(max):
                conf = re.sub(rep,'client_max_body_size '+max+'m',conf)
                public.writeFile(path,conf)
            
        public.serviceReload()
        public.phpReload(version);
        public.WriteLog("PHP配置", "设置PHP-"+version+"最大上传大小为["+max+"MB]!")
        return public.returnMsg(True,'设置成功!')
    
    #设置禁用函数
    def setPHPDisable(self,get):
        filename = web.ctx.session.setupPath + '/php/' + get.version + '/etc/php.ini'
        if not os.path.exists(filename): return public.returnMsg(False,'指定PHP版本不存在!');
        phpini = public.readFile(filename);
        rep = "disable_functions\s*=\s*.*\n"
        phpini = re.sub(rep, 'disable_functions = ' + get.disable_functions + "\n", phpini);
        public.WriteLog('PHP配置','修改PHP-'+get.version+'的禁用函数为['+get.disable_functions+']')
        public.writeFile(filename,phpini);
        public.phpReload(get.version);
        return public.returnMsg(True,'修改成功!');
    
    #设置PHP超时时间
    def setPHPMaxTime(self,get):
        time = get.time
        version = get.version;
        if int(time) < 30 or int(time) > 86400: return public.returnMsg(False,'请填写30-86400间的值!');
        file = web.ctx.session.setupPath+'/php/'+version+'/etc/php-fpm.conf';
        conf = public.readFile(file);
        rep = "request_terminate_timeout\s*=\s*([0-9]+)\n";
        conf = re.sub(rep,"request_terminate_timeout = "+time+"\n",conf);    
        public.writeFile(file,conf)
        
        if web.ctx.session.webserver == 'nginx':
            #设置Nginx
            path = web.ctx.session.setupPath+'/nginx/conf/nginx.conf';
            conf = public.readFile(path);
            rep = "fastcgi_connect_timeout\s+([0-9]+);";
            tmp = re.search(rep, conf).groups();
            if int(tmp[0]) < time:
                conf = re.sub(rep,'fastcgi_connect_timeout '+time+';',conf);
                rep = "fastcgi_send_timeout\s+([0-9]+);";
                conf = re.sub(rep,'fastcgi_send_timeout '+time+';',conf);
                rep = "fastcgi_read_timeout\s+([0-9]+);";
                conf = re.sub(rep,'fastcgi_read_timeout '+time+';',conf);
                public.writeFile(path,conf)
                
        public.WriteLog("PHP配置", "设置PHP-"+version+"最大脚本超时时间为["+time+"秒]!");
        public.serviceReload()
        public.phpReload(version);
        return public.returnMsg(True, '保存成功!');
    
    
    #取FPM设置
    def getFpmConfig(self,get):
        version = get.version;
        file = web.ctx.session.setupPath+"/php/"+version+"/etc/php-fpm.conf";
        conf = public.readFile(file);
        data = {}
        rep = "\s*pm.max_children\s*=\s*([0-9]+)\s*";
        tmp = re.search(rep, conf).groups();
        data['max_children'] = tmp[0];
        
        rep = "\s*pm.start_servers\s*=\s*([0-9]+)\s*";
        tmp = re.search(rep, conf).groups();
        data['start_servers'] = tmp[0];
        
        rep = "\s*pm.min_spare_servers\s*=\s*([0-9]+)\s*";
        tmp = re.search(rep, conf).groups();
        data['min_spare_servers'] = tmp[0];
        
        rep = "\s*pm.max_spare_servers \s*=\s*([0-9]+)\s*";
        tmp = re.search(rep, conf).groups();
        data['max_spare_servers'] = tmp[0];
        
        return data


    #设置
    def setFpmConfig(self,get):
        version = get.version
        max_children = get.max_children
        start_servers = get.start_servers
        min_spare_servers = get.min_spare_servers
        max_spare_servers = get.max_spare_servers
        
        file = web.ctx.session.setupPath+"/php/"+version+"/etc/php-fpm.conf";
        conf = public.readFile(file);
        
        rep = "\s*pm.max_children\s*=\s*([0-9]+)\s*";
        conf = re.sub(rep, "\npm.max_children = "+max_children, conf);
        
        rep = "\s*pm.start_servers\s*=\s*([0-9]+)\s*";
        conf = re.sub(rep, "\npm.start_servers = "+start_servers, conf);
        
        rep = "\s*pm.min_spare_servers\s*=\s*([0-9]+)\s*";
        conf = re.sub(rep, "\npm.min_spare_servers = "+min_spare_servers, conf);
        
        rep = "\s*pm.max_spare_servers \s*=\s*([0-9]+)\s*";
        conf = re.sub(rep, "\npm.max_spare_servers = "+max_spare_servers+"\n", conf);
        public.writeFile(file,conf)
        public.phpReload(version);
        public.WriteLog("PHP配置", "设置PHP-"+version+"并发设置,max_children="+max_children+",start_servers="+start_servers+",min_spare_servers="+min_spare_servers+",max_spare_servers="+max_spare_servers);
        return public.returnMsg(True, '设置成功');
    
    #同步时间
    def syncDate(self,get):
        result = public.ExecShell("ntpdate 0.asia.pool.ntp.org");
        public.WriteLog("环境设置", "同步服务器时间成功!");
        return public.returnMsg(True,"同步成功!");
        
    def IsOpen(self,port):
        #检查端口是否占用
        import socket
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.connect(('127.0.0.1',int(port)))
            s.shutdown(2)
            return True
        except:
            return False
    
    #设置是否开启监控
    def SetControl(self,get):
        try:
            if hasattr(get,'day'): 
                get.day = int(get.day);
                get.day = str(get.day);
                if(get.day < 1): return public.returnMsg(False,"保存天数不合法!");
        except:
            pass
        
        filename = 'data/control.conf';
        if get.type == '1':
            public.writeFile(filename,get.day);
            public.WriteLog("监控设置", "开启监控服务,记录保存["+get.day+"]天!");
        elif get.type == '0':
            public.ExecShell("rm -f " + filename);
            public.WriteLog("监控设置", "关闭监控服务!");
        elif get.type == 'del':
            if not public.IsRestart(): return public.returnMsg(False,'请等待所有安装任务完成再执行!');
            os.remove("data/system.db")
            import db;
            sql = db.Sql()
            result = sql.dbfile('system').create('system');
            public.WriteLog("监控设置", "监控记录已清空!");
            return public.returnMsg(True,"清理成功!");
            
        else:
            data = {}
            if os.path.exists(filename):
                try:
                    data['day'] = int(public.readFile(filename));
                except:
                    data['day'] = 30;
                data['status'] = True
            else:
                data['day'] = 30;
                data['status'] = False
            return data
        
        
        return public.returnMsg(True,"设置成功!");
    
    #关闭面板
    def ClosePanel(self,get):
        #return public.returnMsg(False,'体验服务器，禁止修改!')
        filename = 'data/close.pl'
        public.writeFile(filename,'True');
        public.ExecShell("chmod 600 " + filename);
        public.ExecShell("chown root.root " + filename);
        return public.returnMsg(True,'面板已关闭!');
    
    
    #设置自动更新
    def AutoUpdatePanel(self,get):
        #return public.returnMsg(False,'体验服务器，禁止修改!')
        filename = 'data/autoUpdate.pl'
        if os.path.exists(filename):
            os.remove(filename);
        else:
            public.writeFile(filename,'True');
            public.ExecShell("chmod 600 " + filename);
            public.ExecShell("chown root.root " + filename);
        return public.returnMsg(True,'设置成功!');
    
    #设置二级密码
    def SetPanelLock(self,get):
        path = 'data/lock';
        if not os.path.exists(path):
            public.ExecShell('mkdir ' + path);
            public.ExecShell("chmod 600 " + path);
            public.ExecShell("chown root.root " + path);
        
        keys = ['files','tasks','config'];
        for name in keys:
            filename = path + '/' + name + '.pl';
            if hasattr(get,name):
                public.writeFile(filename,'True');
            else:
                if os.path.exists(filename): os.remove(filename);
                
    #设置PHP守护程序
    def Set502(self,get):
        try:
            filename = 'data/502Task.pl';
            if os.path.exists(filename):
                os.system('rm -f ' + filename)
            else:
                public.writeFile(filename,'True')
            
            return public.returnMsg(True,'设置成功!');
        except:
            return public.returnMsg(True,'失败,磁盘不可写!');
        
        
        
        
            
       
        