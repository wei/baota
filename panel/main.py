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
import sys,web,io,os
sys.path.append("class/")
import common,public,data,page,db

#关闭调试模式
web.config.debug = False

#启用SSL
if os.path.exists('data/ssl.pl'):
    try:
        from web.wsgiserver import CherryPyWSGIServer
        CherryPyWSGIServer.ssl_certificate = "ssl/certificate.pem"
        CherryPyWSGIServer.ssl_private_key = "ssl/privateKey.pem"
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
    '/hook'    , 'panelHook'
)


app = web.application(urls, globals(),autoreload = False)

#初始化SESSION
web.config.session_parameters['cookie_name'] = 'BT_PANEL'
web.config.session_parameters['cookie_domain'] = None
web.config.session_parameters['timeout'] = 3600
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = True
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
        return render.index(data)
    
class panelLogin(common.panelSetup):
    def GET(self):
        if not hasattr(session,'webname'): session.webname = '宝塔Linux面板';
        tmp = web.ctx.host.split(':')
        domain = public.readFile('data/domain.conf')
        if domain:
            if(tmp[0].strip() != domain.strip()): 
                errorStr = '''
<meta charset="utf-8">
<title>拒绝访问</title>
</head><body>
<h1>抱歉,您没有访问权限</h1>
    <p>请使用正确的域名访问!</p>
    <p>查看许可域名: cat /www/server/panel/data/domain.conf</p>
    <p>关闭访问限制: rm -f /www/server/panel/data/domain.conf</p>
<hr>
<address>宝塔Linux面板 5.x <a href="http://www.bt.cn/bbs" target="_blank">请求帮助</a></address>
</body></html>
    '''
                web.header('Content-Type','text/html; charset=utf-8', unique=True)
                return errorStr
        if os.path.exists('data/limitip.conf'):
            iplist = public.readFile('data/limitip.conf')
            if iplist:
                if not web.ctx.ip in iplist.split(','):
                    errorStr = '''
<meta charset="utf-8">
<title>拒绝访问</title>
</head><body>
<h1>抱歉,您的IP没有被授权</h1>
    <p>您当前的IP为[%s]，请使用正确的IP访问!</p>
    <p>查看授权IP: cat /www/server/panel/data/limitip.conf</p>
    <p>关闭访问限制: rm -f /www/server/panel/data/limitip.conf</p>
<hr>
<address>宝塔Linux面板 5.x <a href="http://www.bt.cn/bbs" target="_blank">请求帮助</a></address>
</body></html>
''' % (web.ctx.ip,)
                    web.header('Content-Type','text/html; charset=utf-8', unique=True)
                    return errorStr;
        
        get = web.input()
        sql = db.Sql()
        if hasattr(get,'dologin'):
            if session.login != False:
                session.login = False;
                session.kill();
            import time
            time.sleep(0.2);
            raise web.seeother('/login')
        
        if hasattr(session,'login'):
            if session.login == True:
                raise web.seeother('/')
        
        if not hasattr(session,'code'):
            session.code = False
            
        data = sql.table('users').getField('username')
        render = web.template.render('templates/' + templateName + '/',globals={'session': session})
        return render.login(data)
        
    
    def POST(self):
        post = web.input()
        if not (hasattr(post, 'username') or hasattr(post, 'password') or hasattr(post, 'code')):
            return public.returnJson(False,'用户名或密码不能为空');
        
        if self.limitAddress('?') < 1: return public.returnJson(False,'您多次登陆失败,暂时禁止登陆!');
        post.username = post.username.strip();
        password = public.md5(post.password.strip());
        if session.code:
            if not public.checkCode(post.code):
                public.WriteLog('登陆','<a style="color:red;">验证码错误</a>,帐号:'+post.username+',验证码:'+post.code+',登陆IP:'+ web.ctx.ip);
                return public.returnJson(False,'验证码不正确,请重新输入!');
        
        sql = db.Sql()
        userInfo = sql.table('users').where("username=? AND password=?",(post.username,password)).field('id,username,password').find()
        try:
            if userInfo['username'] != post.username or userInfo['password'] != password:
                public.WriteLog('登陆','<a style="color:red;">密码错误</a>,帐号:'+post.username+',密码:'+post.password+',登陆IP:'+ web.ctx.ip);
                num = self.limitAddress('+');
                return public.returnJson(False,'用户名或密码错误,您还可以尝试['+str(num)+']次.');
            
            import time;
            login_temp = 'data/login.temp'
            if not os.path.exists(login_temp): public.writeFile(login_temp,'');
            login_logs = public.readFile(login_temp);
            public.writeFile(login_temp,login_logs+web.ctx.ip+'|'+str(int(time.time()))+',');
            session.login = True
            session.username = post.username
            public.WriteLog('登陆','<a style="color:green;">登陆成功</a>,帐号:'+post.username+',登陆IP:'+ web.ctx.ip);
            self.limitAddress('-');
            return public.returnJson(True,'登陆成功,正在跳转!');
        except:
            public.WriteLog('登陆','<a style="color:red;">密码错误</a>,帐号:'+post.username+',密码:'+post.password+',登陆IP:'+ web.ctx.ip);
            num = self.limitAddress('+');
            return public.returnJson(False,'用户名或密码错误,您还可以尝试['+str(num)+']次.');
    
    #IP限制
    def limitAddress(self,type):
        import time
        logFile = 'data/'+web.ctx.ip+'.login';
        timeFile = 'data/'+web.ctx.ip+'_time.login';
        limit = 6;
        outtime = 1800;
        try:
            #初始化
            if not os.path.exists(timeFile): public.writeFile(timeFile,str(time.time()));
            if not os.path.exists(logFile): public.writeFile(logFile,'0');
            
            #判断是否解除登陆限制
            time1 = long(public.readFile(timeFile).split('.')[0]);
            if (time.time() - time1) > outtime: 
                public.writeFile(logFile,'0');
                public.writeFile(timeFile,str(time.time()));
            
            #计数
            num1 = int(public.readFile(logFile));
            if type == '+':
                num1 += 1;
                public.writeFile(logFile,str(num1));
                if num1 > 1:
                    session.code = True;
                return limit - num1;
            
            #清空
            if type == '-':
                public.ExecShell('rm -f data/*.login');
                session.code = False;
                return 1;
            
            return limit - num1;
        except:
            return limit;
        

class panelSite(common.panelAdmin):
    def GET(self):
        data = {}
        data['isSetup'] = True;
        if os.path.exists(web.ctx.session.setupPath+'/nginx') == False and os.path.exists(web.ctx.session.setupPath+'/apache') == False: data['isSetup'] = False;
        return render.site(data);
        
    def POST(self):
        get = web.input()
        import panelSite
        siteObject = panelSite.panelSite()
        
        defs = ('SetRewriteTel','GetCheckSafe','CheckSafe','GetDefaultSite','SetDefaultSite','CloseTomcat','SetTomcat','apacheAddPort','AddSite','GetPHPVersion','SetPHPVersion','DeleteSite','AddDomain','DelDomain','GetDirBinding','AddDirBinding','GetDirRewrite','DelDirBinding'
                ,'UpdateRulelist','SetSiteRunPath','GetSiteRunPath','SetPath','SetIndex','GetIndex','GetDirUserINI','SetDirUserINI','GetRewriteList','SetSSL','SetSSLConf','CreateLet','CloseSSLConf','GetSSL','SiteStart','SiteStop'
                ,'Set301Status','Get301Status','CloseLimitNet','SetLimitNet','GetLimitNet','SetProxy','GetProxy','ToBackup','DelBackup','GetSitePHPVersion','logsOpen','GetLogsStatus','CloseHasPwd','SetHasPwd','GetHasPwd')
        return publicObject(siteObject,defs);

class panelConfig(common.panelAdmin):
    def GET(self):
        import system
        data = system.system().GetConcifInfo()
        return render.config(data)
    
    def POST(self):
        import config
        configObject = config.config()
        defs = ('SetPanelSSL','SetTemplates','Set502','setPassword','setUsername','setPanel','setPathInfo','setPHPMaxSize','getFpmConfig','setFpmConfig','setPHPMaxTime','syncDate','setPHPDisable','SetControl','ClosePanel','AutoUpdatePanel','SetPanelLock')
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

class panelCloud(common.panelAdmin):
    def GET(self):
        import json
        get = web.input()
        result = public.ExecShell("python "+web.ctx.session.setupPath + '/panel/script/backup_'+get.filename+'.py download ' + get.name)
        raise web.seeother(json.loads(result[0]));
        

class panelFiles(common.panelAdmin):
    def GET(self):
        return render.files('test')

    def POST(self):
        import files
        filesObject = files.files()
        defs = ('UploadFile','GetDir','CreateFile','CreateDir','DeleteDir','DeleteFile',
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
        if os.path.exists(web.ctx.session.setupPath+'/mysql') == False: data['isSetup'] = False;
        return render.database(data)
    
    def POST(self):
        import database
        databaseObject = database.database()
        defs = ('BinLog','GetErrorLog','GetMySQLInfo','SetDataDir','SetMySQLPort','AddDatabase','DeleteDatabase','SetupPassword','ResDatabasePassword','ToBackup','DelBackup','InputSql','SyncToDatabases','SyncGetDatabases','GetDatabaseAccess','SetDatabaseAccess')
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
        return render.firewall("test")
    
    def POST(self):
        import firewalls
        firewallObject = firewalls.firewalls()
        defs = ('AddDropAddress','DelDropAddress','FirewallReload','SetFirewallStatus','AddAcceptPort','DelAcceptPort','SetSshStatus','SetPing','SetSshPort','GetSshInfo')
        return publicObject(firewallObject,defs);
        
    
class panelCrontab(common.panelAdmin):
    def GET(self):
        import crontab
        get = web.input()
        data = crontab.crontab().GetCrontab(get)
        return render.crontab(data)
    
    def POST(self):       
        import crontab
        crontabObject = crontab.crontab()
        defs = ('GetCrontab','AddCrontab','GetDataList','GetLogs','DelLogs','DelCrontab','StartTask')
        return publicObject(crontabObject,defs);

class panelCode:
    def GET(self):
        import vilidate,time
        if hasattr(session,'codeTime'):
            if (time.time() - session.codeTime) < 0.2:
                return '请不要频繁刷新验证码!'
        vie = vilidate.vieCode()
        codeImage = vie.GetCodeImage(80,4)
        try:
            from cStringIO import StringIO
        except:
            from StringIO import StringIO
        out = StringIO()
        codeImage[0].save(out, "png")
        session.codeStr  = public.md5("".join(codeImage[1]).lower())
        session.codeTime = time.time()
        web.header('Cache-Control', 'private, max-age=0, no-store, no-cache, must-revalidate, post-check=0, pre-check=0');
        web.header('Pragma', 'no-cache');
        web.header('Content-Type','image/png')
        return out.getvalue()

class panelSystem(common.panelAdmin):
    def GET(self):
        return self.funObj()
    
    def POST(self):
        return self.funObj()
    
    def funObj(self):
        import system
        sysObject = system.system()
        defs = ('GetNetWorkOld','GetNetWork','GetDiskInfo','GetCpuInfo','GetBootTime','GetSystemVersion','GetMemInfo','GetSystemTotal','GetConcifInfo','ServiceAdmin','ReWeb','RestartServer','ReMemory')
        return publicObject(sysObject,defs);

class panelAjax(common.panelAdmin):
    def GET(self):
        return self.funObj()
    
    def POST(self):
        return self.funObj()
        
    def funObj(self):
        import ajax
        ajaxObject = ajax.ajax()
        defs = ('GetAd','phpSort','ToPunycode','GetBetaStatus','SetBeta','setPHPMyAdmin','delClose','KillProcess','GetPHPInfo','GetQiniuFileList','UninstallLib','InstallLib','SetQiniuAS','GetQiniuAS','GetLibList','GetProcessList','GetNetWorkList','GetNginxStatus','GetPHPStatus','GetTaskCount','GetSoftList','GetNetWorkIo','GetDiskIo','GetCpuIo','CheckInstalled','UpdatePanel','GetInstalled','GetPHPConfig','SetPHPConfig')
        return publicObject(ajaxObject,defs);

class panelInstall:
    def GET(self):
        if not os.path.exists('install.pl'): raise web.seeother('/login');
        data = {}
        data['status'] = os.path.exists('install.pl');
        data['username'] = public.M('users').where('id=?',(1,)).getField('username');
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
        data['username'] = get.bt_username
        render = web.template.render( 'templates/' + templateName + '/',globals={'session': session})
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
        data = web.input()
        return render.control(data)
    
class panelSoft(common.panelAdmin):
    def GET(self):
        import system
        data = system.system().GetConcifInfo()
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
        defs = ('install','unInstall','getPluginList','getPluginInfo','getPluginStatus','setPluginStatus','a','getCloudPlugin','getConfigHtml','savePluginSort')
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
        defs = ('DelToken','GetToken','GetUserInfo','GetOrderList','GetDVSSL','Completed','SyncOrder','GetSSLInfo','downloadCRT','GetSSLProduct')
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

class panelClose:
    def GET(self):
        if not os.path.exists('data/close.pl'): raise web.seeother('/');
        render = web.template.render('templates/' + templateName + '/',globals={'session': session})
        return render.close(web.ctx.session.version)


def publicObject(toObject,defs):
    get = web.input(zunfile = {},data = []);
    if hasattr(get,'path'):
            get.path = get.path.replace('//','/').replace('\\','/');
            if get.path.find('->') != -1:
                get.path = get.path.split('->')[0].strip();
    for key in defs:
        if key == get.action:
            fun = 'toObject.'+key+'(get)'
            return public.getJson(eval(fun))
    return public.returnJson(False,'指定参数无效!')

#定义404错误
def notfound():  
    errorStr = '''
    <meta charset="utf-8">
    <title>404 Not Found</title>
    </head><body>
    <h1>抱歉,页面不存在</h1>
        <p>您请求的页面不存在,请检查URL地址是否正确!</p>
    <hr>
    <address>宝塔Linux面板 5.x <a href="https://www.bt.cn/bbs" target="_blank">请求帮助</a></address>
    </body></html>
    '''
    return web.notfound(errorStr);
  
#定义500错误 
def internalerror():
    errorStr = '''
    <meta charset="utf-8">
    <title>500 Internal Server Error</title>
    </head><body>
    <h1>抱歉,程序异常</h1>
        <p>您请求的页面因发生异常而中断!</p>
    <hr>
    <address>宝塔Linux面板 5.x <a href="https://www.bt.cn/bbs" target="_blank">请求帮助</a></address>
    </body></html>
    '''
    return web.internalerror(errorStr)

if __name__ == "__main__":
    app.notfound = notfound  
    app.internalerror = internalerror
    reload(sys)
    sys.setdefaultencoding("utf-8")
    app.run()
