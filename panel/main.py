#!/usr/bin/env python
#coding:utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2017 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

#------------------------------
# Panel 入口
#------------------------------
from tools import CloseLogs
CloseLogs();
import sys,web,io,os
sys.path.append("class/")
os.chdir('/www/server/panel')
import common,public,data,page,db,time

#关闭调试模式
web.config.debug = False

#启用SSL
if os.path.exists('data/ssl.pl'):
    try:
        import OpenSSL
        from web.wsgiserver import CherryPyWSGIServer
        CherryPyWSGIServer.ssl_certificate = "ssl/certificate.pem";
        CherryPyWSGIServer.ssl_private_key = "ssl/privateKey.pem";
        if os.path.exists("ssl/root.pem"): CherryPyWSGIServer.ssl_certificate_chain = "ssl/root.pem";
    except Exception,ex:
        print ex;



#URL配置
urls = (
    '/'        , 'panelIndex',
    '/site'    , 'panelSite',
    '/data'    , 'panelData',
    '/files'   , 'panelFiles',
    '/ftp'     , 'panelFtp',
    '/database', 'panelDatabase',
    '/firewall', 'panelFirewall',
    '/config'  , 'panelConfig',
    '/crontab' , 'panelCrontab',
    '/login'   , 'panelLogin',
    '/code'    , 'panelCode',
    '/system'  , 'panelSystem',
    '/ajax'    , 'panelAjax',
    '/install' , 'panelInstall',
    '/download', 'panelDownload',
    '/control' , 'panelControl',
    '/soft'    , 'panelSoft',
    '/cloud'   , 'panelCloud',
    '/test'    , 'panelTest',
    '/close'   , 'panelClose',
    '/plugin'  , 'panelPlugin',
    '/waf'     , 'panelWaf',
    '/ssl'     , 'panelSSL',
    '/api'     , 'panelApi',
    '/hook'    , 'panelHook',
    '/pluginApi','panelPluginApi',
    '/downloadApi' , 'panelDownloadApi',
    '/safe'     , 'panelSafe',
    '/public'   , 'panelPublic',
    '/auth'     , 'panelAuth',
    '/wxapp'    , 'panelWxapp',
    '/vpro'     , 'panelVpro',
    '/robots.txt','panelRobots'
)


app = web.application(urls, globals(),autoreload = False)

#初始化SESSION
web.config.session_parameters['cookie_name'] = 'BT_PANEL'
web.config.session_parameters['cookie_domain'] = None
web.config.session_parameters['timeout'] = 3600
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = not os.path.exists('data/auth_login_ip.pl')
web.config.session_parameters['secret_key'] = 'www.bt.cn'
web.config.session_parameters['expired_message'] = 'Session expired'
dbfile = '/dev/shm/session.db';
src_sessiondb = 'data/session.db';
if not os.path.exists(src_sessiondb): 
    print db.Sql().dbfile('session').create('session');
if not os.path.exists(dbfile): os.system("\\cp -a -r "+src_sessiondb+" " + dbfile);
sessionDB = web.database(dbn='sqlite', db=dbfile)
session = web.session.Session(app, web.session.DBStore(sessionDB,'sessions'), initializer={'login': False});
def session_hook():
    session.panelPath = os.path.dirname(__file__);
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))

#获取当前模板
templatesConf = 'data/templates.pl';
if os.path.exists('templates/index.html'): os.system('rm -f templates/*.html');
if not os.path.exists(templatesConf): public.writeFile(templatesConf,'default');
templateName = public.readFile(templatesConf);

#初始化模板引擎
render = web.template.render('templates/' + templateName + '/',base='template',globals={'session': session,'web':web})

class panelIndex(common.panelAdmin):
    def GET(self):
        import system
        data = system.system().GetConcifInfo()
        data['siteCount'] = public.M('sites').count()
        data['ftpCount'] = public.M('ftps').count()
        data['databaseCount'] = public.M('databases').count()
        data['lan'] = public.getLan('index')
        data['endtime'] = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        if 'vip' in web.ctx.session:
            data['endtime'] = '<span>'+time.strftime('%Y-%m-%d',time.localtime(web.ctx.session.vip['msg']['endtime']))+'</span><a href="/vpro" class="btlink xufei"> 续费</a>';
            if not web.ctx.session.vip['msg']['endtime']: data['endtime'] = '<span style="color: #fc6d26;font-weight: bold;">永久授权</span>';
        return render.index(data)
    
class panelLogin(common.panelSetup):
    def GET(self):
        if os.path.exists('/www/server/panel/install.pl'): raise web.seeother('/install');
        web.ctx.session.lan = public.get_language();
        if not hasattr(session,'webname'): session.webname = public.getMsg('NAME');
        tmp = web.ctx.host.split(':')
        domain = public.readFile('data/domain.conf')
        if domain:
            if(tmp[0].strip() != domain.strip()): 
                errorStr = '''
<meta charset="utf-8">
<title>%s</title>
</head><body>
<h1>%s</h1>
    <p>%s</p>
    <p>%s</p>
    <p>%s</p>
<hr>
<address>%s 5.x <a href="http://www.bt.cn/bbs" target="_blank">%s</a></address>
</body></html>
    ''' % (public.getMsg('PAGE_ERR_TITLE'),public.getMsg('PAGE_ERR_DOMAIN_H1'),public.getMsg('PAGE_ERR_DOMAIN_P1'),public.getMsg('PAGE_ERR_DOMAIN_P2'),public.getMsg('PAGE_ERR_DOMAIN_P3'),public.getMsg('NAME'),public.getMsg('PAGE_ERR_HELP'))
                web.header('Content-Type','text/html; charset=utf-8', unique=True)
                return errorStr
        if os.path.exists('data/limitip.conf'):
            iplist = public.readFile('data/limitip.conf')
            if iplist:
                iplist = iplist.strip();
                if not web.ctx.ip in iplist.split(','):
                    errorStr = '''
<meta charset="utf-8">
<title>%s</title>
</head><body>
<h1>%s</h1>
    <p>%s</p>
    <p>%s</p>
    <p>%s</p>
<hr>
<address>%s 5.x <a href="http://www.bt.cn/bbs" target="_blank">%s</a></address>
</body></html>
''' % (public.getMsg('PAGE_ERR_TITLE'),public.getMsg('PAGE_ERR_IP_H1'),public.getMsg('PAGE_ERR_IP_P1',(web.ctx.ip,)),public.getMsg('PAGE_ERR_IP_P2'),public.getMsg('PAGE_ERR_IP_P3'),public.getMsg('NAME'),public.getMsg('PAGE_ERR_HELP'))
                    web.header('Content-Type','text/html; charset=utf-8', unique=True)
                    return errorStr;
        
        get = web.input()
        sql = db.Sql()
        if hasattr(get,'dologin'):
            if web.ctx.session.login != False:
                web.ctx.session.login = False;
                web.ctx.session.kill();
            import time
            time.sleep(0.2);
            raise web.seeother('/login')
        
        if hasattr(web.ctx.session,'login'):
            if web.ctx.session.login == True:
                raise web.seeother('/')
        
        if not hasattr(web.ctx.session,'code'):
            web.ctx.session.code = False
        data = {}
        data['lan'] = public.getLan('login')
        self.errorNum(False)
        render = web.template.render('templates/' + templateName + '/',globals={'session': session,'web':web})
        return render.login(data)
        
    
    def POST(self):
        post = web.input()
        web.ctx.session.lan = public.get_language();
        if not (hasattr(post, 'username') or hasattr(post, 'password') or hasattr(post, 'code')):
            return public.returnJson(False,'LOGIN_USER_EMPTY');
        
        self.errorNum(False)
        if self.limitAddress('?') < 1: return public.returnJson(False,'LOGIN_ERR_LIMIT');
        
        post.username = post.username.strip();
        password = public.md5(post.password.strip());
        sql = db.Sql();
        userInfo = sql.table('users').where("id=?",(1,)).field('id,username,password').find()
        if hasattr(web.ctx.session,'code'):
            if web.ctx.session.code:
                if not public.checkCode(post.code):
                    public.WriteLog('TYPE_LOGIN','LOGIN_ERR_CODE',('****',web.ctx.session.code,web.ctx.ip));
                    return public.returnJson(False,'CODE_ERR');
        try:
            if userInfo['username'] != post.username or userInfo['password'] != password:
                public.WriteLog('TYPE_LOGIN','LOGIN_ERR_PASS',('****','******',web.ctx.ip));
                num = self.limitAddress('+');
                return public.returnJson(False,'LOGIN_USER_ERR',(str(num),));
            
            import time;
            login_temp = 'data/login.temp'
            if not os.path.exists(login_temp): public.writeFile(login_temp,'');
            login_logs = public.readFile(login_temp);
            public.writeFile(login_temp,login_logs + web.ctx.ip + '|' + str(int(time.time())) + ',');
            web.ctx.session.login = True;
            web.ctx.session.username = userInfo['username'];
            public.WriteLog('TYPE_LOGIN','LOGIN_SUCCESS',(userInfo['username'],web.ctx.ip));
            self.limitAddress('-');
            numFile = '/tmp/panelNum.pl';
            timeFile = '/tmp/panelNime.pl';
            if os.path.exists(numFile): os.remove(numFile);
            if os.path.exists(timeFile): os.remove(timeFile);
            return public.returnJson(True,'LOGIN_SUCCESS');
        except Exception,ex:
            stringEx = str(ex)
            if stringEx.find('unsupported') != -1 or stringEx.find('-1') != -1: 
                btClear();
                return public.returnJson(False,'磁盘Inode已用完,面板已尝试释放Inode,请重试...');
            public.WriteLog('TYPE_LOGIN','LOGIN_ERR_PASS',('****','******',web.ctx.ip));
            num = self.limitAddress('+');
            return public.returnJson(False,'LOGIN_USER_ERR',(str(num),));
    
    
    #防暴破
    def errorNum(self,s = True):
        numFile = '/tmp/panelNum.pl';        
        if not os.path.exists(numFile): 
            public.writeFile(numFile,'0');
            public.ExecShell('chmod 600 ' + numFile);
        
        ntmp = public.readFile(numFile);
        if ntmp.strip() == '':ntmp = '0';
        num = int(ntmp);

        if s:
            num +=1;
            public.writeFile(numFile,str(num));
        
        if num > 6:
            web.ctx.session.code = True;
    
    #IP限制
    def limitAddress(self,type):
        import time
        logFile = 'data/'+web.ctx.ip+'.login';
        timeFile = 'data/'+web.ctx.ip+'_time.login';
        limit = 6;
        outtime = 600;
        try:
            #初始化
            if not os.path.exists(timeFile): public.writeFile(timeFile,str(time.time()));
            if not os.path.exists(logFile): public.writeFile(logFile,'0');
            
            #判断是否解除登陆限制
            time1 = float(public.readFile(timeFile));
            if (time.time() - time1) > outtime: 
                public.writeFile(logFile,'0');
                public.writeFile(timeFile,str(time.time()));
            
            #计数
            num1 = int(public.readFile(logFile));
            if type == '+':
                num1 += 1;
                public.writeFile(logFile,str(num1));
                self.errorNum();
                web.ctx.session.code = True;
                return limit - num1;
            
            #清空
            if type == '-':
                public.ExecShell('rm -f data/*.login');
                web.ctx.session.code = False;
                return 1;
            return limit - num1;
        except:
            return limit;
        

class panelSite(common.panelAdmin):
    def GET(self):
        data = {}
        data['isSetup'] = True;
        data['lan'] = public.getLan('site');
        if os.path.exists(web.ctx.session.setupPath+'/nginx') == False and os.path.exists(web.ctx.session.setupPath+'/apache') == False: data['isSetup'] = False;
        return render.site(data);
        
    def POST(self):
        get = web.input()
        import panelSite
        siteObject = panelSite.panelSite()
        
        defs = ('GetSiteLogs','GetSiteDomains','GetSecurity','SetSecurity','ProxyCache','CloseToHttps','HttpToHttps','SetEdate','SetRewriteTel','GetCheckSafe','CheckSafe','GetDefaultSite','SetDefaultSite','CloseTomcat','SetTomcat','apacheAddPort','AddSite','GetPHPVersion','SetPHPVersion','DeleteSite','AddDomain','DelDomain','GetDirBinding','AddDirBinding','GetDirRewrite','DelDirBinding'
                ,'UpdateRulelist','SetSiteRunPath','GetSiteRunPath','SetPath','SetIndex','GetIndex','GetDirUserINI','SetDirUserINI','GetRewriteList','SetSSL','SetSSLConf','CreateLet','CloseSSLConf','GetSSL','SiteStart','SiteStop','GetDnsApi','SetDnsApi'
                ,'Set301Status','Get301Status','CloseLimitNet','SetLimitNet','GetLimitNet','SetProxy','GetProxy','ToBackup','DelBackup','GetSitePHPVersion','logsOpen','GetLogsStatus','CloseHasPwd','SetHasPwd','GetHasPwd')
        return publicObject(siteObject,defs);

class panelConfig(common.panelAdmin):
    def GET(self):
        import system,wxapp
        data = system.system().GetConcifInfo();
        data['lan'] = public.getLan('config');
        data['wx'] = wxapp.wxapp().get_user_info(None)['msg'];
        return render.config(data);
    
    def POST(self):
        import config
        configObject = config.config()
        defs = ('SavePanelSSL','GetPanelSSL','GetPHPConf','SetPHPConf','GetPanelList','AddPanelInfo','SetPanelInfo','DelPanelInfo','ClickPanelInfo','SetPanelSSL','SetTemplates','Set502','setPassword','setUsername','setPanel','setPathInfo','setPHPMaxSize','getFpmConfig','setFpmConfig','setPHPMaxTime','syncDate','setPHPDisable','SetControl','ClosePanel','AutoUpdatePanel','SetPanelLock')
        return publicObject(configObject,defs);
    
class panelDownload(common.panelAdmin):
    def GET(self):
        get = web.input()
        try:
            get.filename = get.filename.encode('utf-8');
            import os        
            fp = open(get.filename,'rb')
            size = os.path.getsize(get.filename)
            filename = os.path.basename(get.filename)
            
            #输出文件头
            web.header("Content-Disposition", "attachment; filename=" +filename);
            web.header("Content-Length", size);
            web.header('Content-Type','application/octet-stream');
            buff = 4096
            while True:
                fBody = fp.read(buff)
                if fBody:
                    yield fBody
                else:
                    return
        except Exception, e:
            yield 'Error'
        finally:
            if fp:
                fp.close()

class panelCloud(common.panelAdmin):
    def GET(self):
        import json
        get = web.input()
        result = public.ExecShell("python "+web.ctx.session.setupPath + '/panel/script/backup_'+get.filename+'.py download ' + get.name)
        raise web.seeother(json.loads(result[0]));
        

class panelFiles(common.panelAdmin):
    def GET(self):
        data = {}
        data['lan'] = public.getLan('files')
        return render.files(data)

    def POST(self):
        import files
        filesObject = files.files()
        defs = ('CheckExistsFiles','GetExecLog','GetSearch','ExecShell','GetExecShellMsg','UploadFile','GetDir','CreateFile','CreateDir','DeleteDir','DeleteFile',
                'CopyFile','CopyDir','MvFile','GetFileBody','SaveFileBody','Zip','UnZip',
                'GetFileAccess','SetFileAccess','GetDirSize','SetBatchData','BatchPaste',
                'DownloadFile','GetTaskSpeed','CloseLogs','InstallSoft','UninstallSoft',
                'RemoveTask','ActionTask','Re_Recycle_bin','Get_Recycle_bin','Del_Recycle_bin','Close_Recycle_bin','Recycle_bin')
        return publicObject(filesObject,defs);

class panelDatabase(common.panelAdmin):
    def GET(self):
        pmd = self.get_phpmyadmin_dir();
        web.ctx.session.phpmyadminDir = False
        if pmd: 
            web.ctx.session.phpmyadminDir = 'http://' + web.ctx.host.split(':')[0] + ':'+ pmd[1] + '/' + pmd[0];
        
        data = {}
        data['isSetup'] = True;
        data['mysql_root'] = public.M('config').where('id=?',(1,)).getField('mysql_root');
        data['lan'] = public.getLan('database')
        if os.path.exists(web.ctx.session.setupPath+'/mysql') == False: data['isSetup'] = False;
        return render.database(data)
    
    def POST(self):
        import database
        databaseObject = database.database()
        defs = ('GetSlowLogs','GetRunStatus','SetDbConf','GetDbStatus','BinLog','GetErrorLog','GetMySQLInfo','SetDataDir','SetMySQLPort','AddDatabase','DeleteDatabase','SetupPassword','ResDatabasePassword','ToBackup','DelBackup','InputSql','SyncToDatabases','SyncGetDatabases','GetDatabaseAccess','SetDatabaseAccess')
        return publicObject(databaseObject,defs);
    
    def get_phpmyadmin_dir(self):
        path = web.ctx.session.setupPath + '/phpmyadmin'
        if not os.path.exists(path): return None
        
        phpport = '888';
        try:
            import re;
            if web.ctx.session.webserver == 'nginx':
                filename = web.ctx.session.setupPath + '/nginx/conf/nginx.conf';
                conf = public.readFile(filename);
                rep = "listen\s+([0-9]+)\s*;";
                rtmp = re.search(rep,conf);
                if rtmp:
                    phpport = rtmp.groups()[0];
            else:
                filename = web.ctx.session.setupPath + '/apache/conf/extra/httpd-vhosts.conf';
                conf = public.readFile(filename);
                rep = "Listen\s+([0-9]+)\s*\n";
                rtmp = re.search(rep,conf);
                if rtmp:
                    phpport = rtmp.groups()[0];
        except:
            pass
            
        for filename in os.listdir(path):
            print filename
            filepath = path + '/' + filename
            if os.path.isdir(filepath):
                if filename[0:10] == 'phpmyadmin':
                    return str(filename),phpport
        
        return None
            

class panelFtp(common.panelAdmin):
    def GET(self):
        self.FtpPort()
        data = {}
        data['isSetup'] = True;
        if os.path.exists(web.ctx.session.setupPath+'/pure-ftpd') == False: data['isSetup'] = False;
        data['lan'] = public.getLan('ftp')
        return render.ftp(data)
        
    def POST(self):
        import ftp
        ftpObject = ftp.ftp()
        defs = ('AddUser','DeleteUser','SetUserPassword','SetStatus','setPort')
        return publicObject(ftpObject,defs);
    
    #取端口
    def FtpPort(self):
        if hasattr(web.ctx.session,'port'):return
        import re
        try:
            file = web.ctx.session.setupPath+'/pure-ftpd/etc/pure-ftpd.conf'
            conf = public.readFile(file)
            rep = "\n#?\s*Bind\s+[0-9]+\.[0-9]+\.[0-9]+\.+[0-9]+,([0-9]+)"
            port = re.search(rep,conf).groups()[0]
        except:
            port='21'
        web.ctx.session.port = port
    
class panelFirewall(common.panelAdmin):
    def GET(self):
        data = {}
        data['lan'] = public.getLan('firewall')
        return render.firewall(data)
    
    def POST(self):
        import firewalls
        firewallObject = firewalls.firewalls()
        defs = ('GetList','AddDropAddress','DelDropAddress','FirewallReload','SetFirewallStatus','AddAcceptPort','DelAcceptPort','SetSshStatus','SetPing','SetSshPort','GetSshInfo')
        return publicObject(firewallObject,defs);
        
    
class panelCrontab(common.panelAdmin):
    def GET(self):
        import crontab
        data = {}
        data['lan'] = public.getLan('crontab')
        return render.crontab(data)
    
    def POST(self):       
        import crontab
        crontabObject = crontab.crontab()
        defs = ('GetCrontab','AddCrontab','GetDataList','GetLogs','DelLogs','DelCrontab','StartTask')
        return publicObject(crontabObject,defs);

class panelCode:
    def GET(self):
        import vilidate,time
        if hasattr(web.ctx.session,'codeTime'):
            if (time.time() - web.ctx.session.codeTime) < 0.1:
                return public.getMsg('CODE_BOOM');
        vie = vilidate.vieCode();
        codeImage = vie.GetCodeImage(80,4);
        try:
            from cStringIO import StringIO
        except:
            from StringIO import StringIO
        out = StringIO();
        codeImage[0].save(out, "png")
        web.ctx.session.codeStr  = public.md5("".join(codeImage[1]).lower())
        web.ctx.session.codeTime = time.time()
        web.header('Cache-Control', 'private, max-age=0, no-store, no-cache, must-revalidate, post-check=0, pre-check=0');
        web.header('Pragma', 'no-cache');
        web.header('Content-Type','image/png');
        return out.getvalue();

class panelSystem(common.panelAdmin):
    def GET(self):
        return self.funObj()
    
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import system
        sysObject = system.system()
        defs = ('UpdatePro','GetAllInfo','GetNetWorkApi','GetLoadAverage','ClearSystem','GetNetWorkOld','GetNetWork','GetDiskInfo','GetCpuInfo','GetBootTime','GetSystemVersion','GetMemInfo','GetSystemTotal','GetConcifInfo','ServiceAdmin','ReWeb','RestartServer','ReMemory','RepPanel')
        return publicObject(sysObject,defs);

class panelAjax(common.panelAdmin):
    def GET(self):
        return self.funObj()
    
    def POST(self):
        return self.funObj()
        
    def funObj(self):
        import ajax
        ajaxObject = ajax.ajax()
        defs = ('GetCloudHtml','get_load_average','GetOpeLogs','GetFpmLogs','GetFpmSlowLogs','SetMemcachedCache','GetMemcachedStatus','GetRedisStatus','GetWarning','SetWarning','CheckLogin','GetSpeed','GetAd','phpSort','ToPunycode','GetBetaStatus','SetBeta','setPHPMyAdmin','delClose','KillProcess','GetPHPInfo','GetQiniuFileList','UninstallLib','InstallLib','SetQiniuAS','GetQiniuAS','GetLibList','GetProcessList','GetNetWorkList','GetNginxStatus','GetPHPStatus','GetTaskCount','GetSoftList','GetNetWorkIo','GetDiskIo','GetCpuIo','CheckInstalled','UpdatePanel','GetInstalled','GetPHPConfig','SetPHPConfig')
        return publicObject(ajaxObject,defs);

class panelInstall:
    def GET(self):
        if not os.path.exists('install.pl'): raise web.seeother('/login');
        data = {}
        data['status'] = os.path.exists('install.pl');
        data['username'] = public.M('users').where('id=?',(1,)).getField('username');
        data['brand'] = public.getMsg('BRAND');
        data['product'] = public.getMsg('PRODUCT');
        render = web.template.render('templates/' + templateName + '/',globals={'session': session})
        return render.install(data);
    
    def POST(self):
        if not os.path.exists('install.pl'): raise web.seeother('/login');
        get = web.input();
        if not hasattr(get,'bt_username'): return '用户名不能为空!';
        if not get.bt_username: return '用户名不能为空!'
        if not hasattr(get,'bt_password1'): return '密码不能为空!';
        if not get.bt_password1: return '密码不能为空!';
        if get.bt_password1 != get.bt_password2: return '两次输入的密码不一致，请重新输入!';
        public.M('users').where("id=?",(1,)).save('username,password',(get.bt_username,public.md5(get.bt_password1.strip())))
        os.remove('install.pl');
        data = {}
        data['status'] = os.path.exists('install.pl');
        data['username'] = get.bt_username;
        render = web.template.render( 'templates/' + templateName + '/',globals={'session': session});
        return render.install(data);
    

class panelData(common.panelAdmin):
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        dataObject = data.data()
        defs = ('setPs','getData','getFind','getKey')
        return publicObject(dataObject,defs);

class panelControl(common.panelAdmin):
    def GET(self):
        data = {}
        data['lan'] = public.getLan('control')
        return render.control(data)
    
class panelSoft(common.panelAdmin):
    def GET(self):
        import system
        data = system.system().GetConcifInfo()
        data['lan'] = public.getLan('soft')
        return render.soft(data)

class panelTest(common.panelAdmin):
    
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import servertest;
        testObject = servertest.serverTest()
        defs = ('testCpu','testInt','testFloat','testBubble','testTree','testMem','testDisk','testWorkNet')
        return publicObject(testObject,defs);

class panelPlugin(common.panelAdmin):
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import panelPlugin
        pluginObject = panelPlugin.panelPlugin()
        defs = ('flush_cache','GetCloudWarning','install','unInstall','getPluginList','getPluginInfo','getPluginStatus','setPluginStatus','a','getCloudPlugin','getConfigHtml','savePluginSort')
        return publicObject(pluginObject,defs);
    
class panelWaf(common.panelAdmin):
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import panelWaf
        toObject = panelWaf.panelWaf()
        defs = ('GetConfig','SetConfigString','SetConfigList','GetWafConf','SetWafConf','SetStatus','updateWaf')
        return publicObject(toObject,defs);
    
class panelSSL(common.panelAdmin):
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import panelSSL
        toObject = panelSSL.panelSSL()
        defs = ('RemoveCert','SetCertToSite','GetCertList','SaveCert','GetCert','GetCertName','DelToken','GetToken','GetUserInfo','GetOrderList','GetDVSSL','Completed','SyncOrder','GetSSLInfo','downloadCRT','GetSSLProduct')
        result = publicObject(toObject,defs);
        return result;

class panelAuth(common.panelAdmin):
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import panelAuth
        toObject = panelAuth.panelAuth()
        defs = ('get_re_order_status_plugin','get_voucher_plugin','create_order_voucher_plugin','get_product_discount_by','get_re_order_status','create_order_voucher','create_order','get_order_status','get_voucher','flush_pay_status','create_serverid','check_serverid','get_plugin_list','check_plugin','get_buy_code','check_pay_status','get_renew_code','check_renew_code','get_business_plugin','get_ad_list','check_plugin_end','get_plugin_price')
        result = publicObject(toObject,defs);
        return result;
    
class panelApi(common.panelAdmin):
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import panelApi
        toObject = panelApi.panelApi()
        defs = ('GetToken','SetToken','CreateToken','SetTokenStatus')
        result = publicObject(toObject,defs);
        return result;

class panelWxapp(common.panelAdmin):
    def GET(self):
        return self.funObj()
        
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import wxapp
        toObject = wxapp.wxapp()
        defs = ('blind','get_safe_log','blind_result','get_user_info','blind_del','blind_qrcode')
        result = publicObject(toObject,defs);
        return result;

class panelHook:
    def GET(self):
        return self.pobject();
    def POST(self):
        return self.pobject();
    
    def pobject(self):
        get = web.input()
        if not os.path.exists('/www/server/panel/plugin/webhook'): return public.getJson(public.returnMsg(False,'请先安装WebHook组件!'));
        sys.path.append('/www/server/panel/plugin/webhook');
        import webhook_main
        return public.getJson(webhook_main.webhook_main().RunHook(get));

#安全登陆接口
class panelSafe(common.panelSetup):
    def GET(self):
        return self.pobject();
    
    def POST(self):
        return self.pobject();
    
    def pobject(self):
        get = web.input()
        pluginPath = '/www/server/panel/plugin/safelogin';
        if hasattr(get,'check'):
            if os.path.exists(pluginPath + '/safelogin_main.py'): return 'True';
            return 'False';
        get.data = self.check_token(get.data);
        if not get.data: return public.returnJson(False,'验证失败');
        sys.path.append(pluginPath);
        import safelogin_main;
        reload(safelogin_main);
        s = safelogin_main.safelogin_main();
        if not hasattr(s,get.data['action']): return public.returnJson(False,'方法不存在');
        defs = ('GetServerInfo','add_ssh_limit','remove_ssh_limit','get_ssh_limit','get_login_log','get_panel_limit','add_panel_limit','remove_panel_limit','close_ssh_limit','close_panel_limit','get_system_info','get_service_info','get_ssh_errorlogin')
        if not get.data['action'] in defs: return 'False';
        return public.getJson(eval('s.' + get.data['action'] + '(get)'));
    
    #检查Token
    def check_token(self,data):
        pluginPath = '/www/server/panel/plugin/safelogin/token.pl';
        if not os.path.exists(pluginPath): return False;
        from urllib import unquote;
        from binascii import unhexlify;
        from json import loads;
        
        result = unquote(unhexlify(data));
        token = public.readFile(pluginPath).strip();
        
        result = loads(result);
        if not result: return False;
        if result['token'] != token: return False;
        return result;    
    
class panelPluginApi(common.panelSetup):
    def GET(self):
        get = web.input();
        if not get.name in ['psync']: return "Error!"
        if not public.path_safe_check(get.name): return "Error"
        if not public.checkToken(get): return public.returnJson(False,'无效的Token!');
        if not self.CheckPlugin(get.name): return public.returnJson(False,'您没有权限访问当前插件!');
        return self.funObj();
    
    def POST(self):
        get = web.input(backupfile={},data=[]);
        if not get.name in ['psync']: return "Error!"
        if not public.path_safe_check(get.name): return "Error"
        if not public.checkToken(get): return public.returnJson(False,'无效的Token!');
        if not self.CheckPlugin(get.name): return public.returnJson(False,'您没有权限访问当前插件!');
        return self.funObj();
    
    def CheckPlugin(self,name):
        try:
            infoFile = '/www/server/panel/plugin/' + name + '/info.json';
            if not os.path.exists(infoFile): return False;
            import json
            info = json.loads(public.readFile(infoFile));
            if not info['api']: return False;
            return True;
        except:
            return False
    
    def funObj(self):
        import panelPlugin
        pluginObject = panelPlugin.panelPlugin();
        defs = ('install','unInstall','getPluginList','getPluginInfo','getPluginStatus','setPluginStatus','a','getCloudPlugin','getConfigHtml','savePluginSort')
        return publicObject(pluginObject,defs);
    
class panelDownloadApi(common.panelSetup):
    def GET(self):
        get = web.input()
        if not public.checkToken(get): get.filename = str(time.time());
        try:

            get.filename = '/www/server/panel/plugin/psync/backup/' + get.filename.encode('utf-8');
            if public.path_safe_check(get.filename): 
                import os
                fp = open(get.filename,'rb')
                size = os.path.getsize(get.filename)
                filename = os.path.basename(get.filename)
                
                #输出文件头
                web.header("Content-Disposition", "attachment; filename=" + filename);
                web.header("Content-Length", size);
                web.header('Content-Type','application/octet-stream')
                buff = 4096
                while True:
                    fBody = fp.read(buff)
                    if fBody:
                        yield fBody
                    else:
                        return
        except Exception, e:
            yield 'Error'
        finally:
            if fp:
                fp.close()

class panelToken(common.panelSetup):
    def GET(self):
        import json,time
        get = web.input();
        tokenFile = 'data/token.json'
        if not os.path.exists(self.tokenFile): return json.dumps(public.returnMsg(False,'错误：当前未开启API接口服务!'));
        token = json.loads(public.readFile(tokenFile));
        if get.access_key != token['access_key'] or get.secret_key != token['secret_key']:
            return json.dumps(public.returnMsg(False,'密钥验证失败!'));
        
        tempToken = {}
        tempToken['token'] = public.GetRandomString(32);
        tempToken['timeout'] = time.time() + 86400;
        
        public.writeFile('data/tempToken.json',json.dumps(tempToken));
        tempToken['status'] = True;
        return json.dumps(tempToken);
    

class panelClose:
    def GET(self):
        if not os.path.exists('data/close.pl'): raise web.seeother('/');
        render = web.template.render('templates/' + templateName + '/',globals={'session': session})
        data = {}
        data['lan'] = public.getLan('close');
        return render.close(data)

class panelVpro(common.panelAdmin):
    def GET(self):
        render = web.template.render('templates/' + templateName + '/',globals={'session': session})
        data = {}
        return render.vpro(data)

class panelPublic(common.panelSetup):
    def GET(self):
        return self.RequestFun();
    
    def POST(self):
        return self.RequestFun();
    
    def RequestFun(self):
        get = web.input();
        get.client_ip = web.ctx.ip;
        if get.fun in ['scan_login','login_qrcode','set_login','is_scan_ok','blind']:
            import wxapp
            pluwx = wxapp.wxapp()
            checks = pluwx._check(get)
            if type(checks) != bool or not checks: return public.getJson(checks)
            data = public.getJson(eval('pluwx.'+get.fun+'(get)'))
            return data
        
        if not get.name in ['app']: return "Error!"
        if not public.path_safe_check(get.name + '/' + get.fun): return "Error"
        import panelPlugin
        plu = panelPlugin.panelPlugin();
        get.s = '_check';
        
        checks = plu.a(get)
        if type(checks) != bool or not checks: return public.getJson(checks)
        get.s = get.fun
        self.SetSession();
        result = plu.a(get)
        return public.getJson(result)
    
    def SetSession(self):
        if not hasattr(web.ctx.session,'brand'):
            web.ctx.session.brand = public.getMsg('BRAND');
            web.ctx.session.product = public.getMsg('PRODUCT');
            web.ctx.session.rootPath = '/www'
            web.ctx.session.webname = public.getMsg('NAME');
            web.ctx.session.downloadUrl = 'http://download.bt.cn';
            if os.path.exists('data/title.pl'):
                web.ctx.session.webname = public.readFile('data/title.pl'); 
            web.ctx.session.setupPath = '/www/server';
            web.ctx.session.logsPath = '/www/wwwlogs';
        if not hasattr(web.ctx.session,'menu'):
            web.ctx.session.menu = public.getLan('menu');
        if not hasattr(web.ctx.session,'lan'):
            web.ctx.session.lan = public.get_language();
        if not hasattr(web.ctx.session,'home'):
            web.ctx.session.home = 'https://www.bt.cn';
        if not hasattr(web.ctx.session,'webserver'):
            if os.path.exists('/www/server/nginx'):
                web.ctx.session.webserver = 'nginx'
            else:
                web.ctx.session.webserver = 'apache'
            if os.path.exists('/www/server/'+web.ctx.session.webserver+'/version.pl'):
                web.ctx.session.webversion = public.readFile('/www/server/'+web.ctx.session.webserver+'/version.pl').strip()
        if not hasattr(web.ctx.session,'phpmyadminDir'):
            filename = '/www/server/data/phpmyadminDirName.pl'
            if os.path.exists(filename):
                web.ctx.session.phpmyadminDir = public.readFile(filename).strip()
        if not hasattr(web.ctx.session,'server_os'):
            tmp = {}
            if os.path.exists('/etc/redhat-release'):
                tmp['x'] = 'RHEL';
                tmp['osname'] = public.readFile('/etc/redhat-release').split()[0];
            elif os.path.exists('/usr/bin/yum'):
                tmp['x'] = 'RHEL';
                tmp['osname'] = public.readFile('/etc/issue').split()[0];
            elif os.path.exists('/etc/issue'): 
                tmp['x'] = 'Debian';
                tmp['osname'] = public.readFile('/etc/issue').split()[0];
            web.ctx.session.server_os = tmp


class panelRobots:
    def GET(self):
        return self.get_robots();
    
    def POST(self):
        return self.get_robots();
    
    def get_robots(self):
        robots = '''User-agent: *
Disallow: /'''
        return robots;
        

def publicObject(toObject,defs):
    get = web.input(zunfile = {},data = []);
    if hasattr(get,'path'):
            get.path = get.path.replace('//','/').replace('\\','/');
            if get.path.find('->') != -1:
                get.path = get.path.split('->')[0].strip();
    for key in defs:
        if key == get.action:
            fun = 'toObject.'+key+'(get)'
            if hasattr(get,'html'):
                return eval(fun)
            else:
                return public.getJson(eval(fun))
    return public.returnJson(False,'ARGS_ERR')


#强制清理垃圾
def btClear():
    try:
        import tools
        count = total = 0;
        tmp_total,tmp_count = tools.ClearMail();
        count += tmp_count;
        total += tmp_total;
        tmp_total,tmp_count = tools.ClearSession();
        count += tmp_count;
        total += tmp_total;
        tmp_total,tmp_count = tools.ClearOther();
        count += tmp_count;
        total += tmp_total;
        public.WriteLog('系统工具','<spen style="color:red;">检测到[磁盘空间]或[Inode]已用完，面板无法正常运行,正在尝试清理系统垃圾...</span>');
        public.WriteLog('系统工具','<spen style="color:red;">系统垃圾清理完成，共删除['+str(count)+']个文件,释放磁盘空间['+tools.ToSize(total)+']</span>');
    except:pass;
    
#定义404错误
def notfound():
    errorStr = '''
    <meta charset="utf-8">
    <title>%s</title>
    </head><body>
    <h1>%s</h1>
        <p>%s</p>
    <hr>
    <address>%s 5.x <a href="https://www.bt.cn/bbs" target="_blank">%s</a></address>
    </body></html>
    ''' % (public.getMsg('PAGE_ERR_404_TITLE'),public.getMsg('PAGE_ERR_404_H1'),public.getMsg('PAGE_ERR_404_P1'),public.getMsg('NAME'),public.getMsg('PAGE_ERR_HELP'))
    return web.notfound(errorStr);
  
#定义500错误 
def internalerror():
    errorStr = '''
    <meta charset="utf-8">
    <title>%s</title>
    </head><body>
    <h1>%s</h1>
        <p>%s</p>
    <hr>
    <address>%s 5.x <a href="https://www.bt.cn/bbs" target="_blank">%s</a></address>
    </body></html>
    '''  % (public.getMsg('PAGE_ERR_500_TITLE'),public.getMsg('PAGE_ERR_500_H1'),public.getMsg('PAGE_ERR_500_P1'),public.getMsg('NAME'),public.getMsg('PAGE_ERR_HELP'))
    #os.system('sleep 1 && /etc/init.d/bt reload &')
    return web.internalerror(errorStr)

#检查环境
def check_system():
    import panelSite
    sql = db.Sql();
    sql.execute("alter TABLE sites add edate integer DEFAULT '0000-00-00'",());
    filename = '/www/server/panel/static/js/ZeroClipboard.swf'
    if os.path.exists(filename): os.remove(filename)
    panelSite.panelSite().set_mt_conf()
    

if __name__ == "__main__":
    check_system();
    app.notfound = notfound  
    app.internalerror = internalerror
    reload(sys)
    sys.setdefaultencoding("utf-8")
    app.run()
