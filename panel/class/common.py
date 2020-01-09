#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2017 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <287962566@qq.com>
# +-------------------------------------------------------------------
#
#             ┏┓      ┏┓
#            ┏┛┻━━━━━━┛┻┓
#            ┃               ☃              ┃
#            ┃  ┳┛   ┗┳ ┃
#            ┃     ┻    ┃
#            ┗━┓      ┏━┛
#              ┃      ┗━━━━━┓
#              ┃  神兽保佑              ┣┓
#              ┃ 永无BUG！            ┏┛
#              ┗┓┓┏━┳┓┏━━━━━┛
#               ┃┫┫ ┃┫┫
#               ┗┻┛ ┗┻┛

import web,os,public
class MyBad():
    _msg = None
    def __init__(self,msg):
        self._msg = msg
    def __repr__(self):
        return self._msg

class panelSetup:
    def __init__(self):
        ua = web.ctx.env.get('HTTP_USER_AGENT').lower();
        if ua.find('spider') != -1 or ua.find('bot') != -1: raise web.redirect('https://www.baidu.com');
        web.ctx.session.version = "5.9.2";
        if os.path.exists('data/title.pl'):
            web.ctx.session.webname = public.readFile('data/title.pl');
        
        
        
class panelAdmin(panelSetup):
    setupPath = '/www/server'
    def __init__(self):
        self.local();
    
    #api请求 
    def auth(self):
        self.checkAddressWhite();
        self.setSession();
        self.checkWebType();
        self.checkDomain();
        self.checkConfig();
        self.GetOS();
        
    #本地请求
    def local(self):
        self.checkLimitIp();
        self.setSession();
        self.checkClose();
        self.checkWebType();
        self.checkDomain();
        self.checkConfig();
        self.GetOS();
    
    #检查Token合法性
    def checkToken(self):
        data = public.auth_decode(web.input());
        
    
    #检查api管理权限
    def checkRule(self):
        ruleFile = 'data/rule.json';
        if not os.path.exists(ruleFile): return False;
        toPath = web.ctx.path.replace('/','');
        ruleList = public.readFile(ruleFile).split('|');
        if toPath in ruleList: return True;
        return False;
    
    #检查IP白名单
    def checkAddressWhite(self):
        token = self.GetToken();
        if not token: raise web.seeother('/login');
        if not web.ctx.ip in token['address']: raise web.seeother('/login');
        
    
    #检查IP限制
    def checkLimitIp(self):
        if os.path.exists('data/limitip.conf'):
            iplist = public.readFile('data/limitip.conf')
            if iplist:
                iplist = iplist.strip();
                if not web.ctx.ip in iplist.split(','): raise web.seeother('/login')
    
    #设置基础Session
    def setSession(self):
        if not hasattr(web.ctx.session,'brand'):
            web.ctx.session.brand = public.getMsg('BRAND');
            web.ctx.session.product = public.getMsg('PRODUCT');
            web.ctx.session.rootPath = '/www'
            web.ctx.session.webname = public.getMsg('NAME');
            web.ctx.session.downloadUrl = 'http://download.bt.cn';
            if os.path.exists('data/title.pl'):
                web.ctx.session.webname = public.readFile('data/title.pl'); 
            web.ctx.session.setupPath = self.setupPath;
            web.ctx.session.logsPath = '/www/wwwlogs';
        if not hasattr(web.ctx.session,'menu'):
            web.ctx.session.menu = public.getLan('menu');
        if not hasattr(web.ctx.session,'lan'):
            web.ctx.session.lan = public.get_language();
        if not hasattr(web.ctx.session,'home'):
            web.ctx.session.home = 'http://www.bt.cn';
            
    
    #检查Web服务器类型
    def checkWebType(self):
        if os.path.exists(self.setupPath + '/nginx'):
            web.ctx.session.webserver = 'nginx'
        else:
            web.ctx.session.webserver = 'apache'
        if os.path.exists(self.setupPath+'/'+web.ctx.session.webserver+'/version.pl'):
            web.ctx.session.webversion = public.readFile(self.setupPath+'/'+web.ctx.session.webserver+'/version.pl').strip()
        filename = self.setupPath+'/data/phpmyadminDirName.pl'
        if os.path.exists(filename):
            web.ctx.session.phpmyadminDir = public.readFile(filename).strip()
    
    #检查面板是否关闭
    def checkClose(self):
        if os.path.exists('data/close.pl'):
            raise web.seeother('/close');
        
    #检查域名绑定
    def checkDomain(self):
        try:
            if not web.ctx.session.login:
                raise web.seeother('/login')
            
            tmp = web.ctx.host.split(':')
            domain = public.readFile('data/domain.conf')
            if domain:
                if(tmp[0].strip() != domain.strip()): raise web.seeother('/login')
        except:
            raise web.seeother('/login')
    
    #检查系统配置
    def checkConfig(self):
        if not hasattr(web.ctx.session,'config'):
            web.ctx.session.config = public.M('config').where("id=?",('1',)).field('webserver,sites_path,backup_path,status,mysql_root').find();
            if not hasattr(web.ctx.session.config,'email'):
                web.ctx.session.config['email'] = public.M('users').where("id=?",('1',)).getField('email');
            if not hasattr(web.ctx.session,'address'):
                web.ctx.session.address = public.GetLocalIp()
    
    #获取操作系统类型 
    def GetOS(self):
        if not hasattr(web.ctx.session,'server_os'):
            tmp = {}
            if os.path.exists('/etc/redhat-release'):
                tmp['x'] = 'RHEL';
            elif os.path.exists('/usr/bin/yum'):
                tmp['x'] = 'RHEL';
            elif os.path.exists('/etc/issue'): 
                tmp['x'] = 'Debian';
            web.ctx.session.server_os = tmp
            