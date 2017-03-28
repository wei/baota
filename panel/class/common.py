#coding: utf-8
import web,os,public
class panelSetup:
    def __init__(self):
        web.header("Server",'Bt-Panel Server')
        web.header("Token-auth",'http://www.bt.cn')
        web.ctx.session.webname = '宝塔Linux面板'
        if os.path.exists('data/title.pl'):
            web.ctx.session.webname = public.readFile('data/title.pl');
        pass
        
class panelAdmin(panelSetup):
    def __init__(self):
        web.ctx.session.brand = '宝塔'
        web.ctx.session.product = 'Linux面板'
        web.ctx.session.version = "3.5.0"
        web.ctx.session.rootPath = '/www'
        web.ctx.session.webname = '宝塔Linux面板'
        if os.path.exists('data/title.pl'):
            web.ctx.session.webname = public.readFile('data/title.pl');
        web.ctx.session.setupPath = web.ctx.session.rootPath+'/server'
        web.ctx.session.logsPath = web.ctx.session.rootPath+'/wwwlogs'
        setupPath = web.ctx.session.setupPath
        
        if os.path.exists('data/close.pl'):
            raise web.seeother('/close');
        
        if os.path.exists(setupPath + '/nginx'):
            web.ctx.session.webserver = 'nginx'
        else:
            web.ctx.session.webserver = 'apache'
        if os.path.exists(setupPath+'/'+web.ctx.session.webserver+'/version.pl'):
            web.ctx.session.webversion = public.readFile(setupPath+'/'+web.ctx.session.webserver+'/version.pl').strip()
        
        filename = setupPath+'/data/phpmyadminDirName.pl'
        if os.path.exists(filename):
            web.ctx.session.phpmyadminDir = public.readFile(filename).strip()
            
        try:
            if not web.ctx.session.login:
                raise web.seeother('/login')
            
            tmp = web.ctx.host.split(':')
            domain = public.readFile('data/domain.conf')
            if domain:
                if(tmp[0].strip() != domain.strip()): raise web.seeother('/login')
        except:
            raise web.seeother('/login')
        
        web.ctx.session.config = public.M('config').where("id=?",('1',)).field('webserver,sites_path,backup_path,status,mysql_root').find();
        if not hasattr(web.ctx.session.config,'email'):
            web.ctx.session.config['email'] = public.M('users').where("id=?",('1',)).getField('email');
        if not hasattr(web.ctx.session,'address'):
            web.ctx.session.address = public.GetLocalIp()