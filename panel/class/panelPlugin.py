#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2017 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------
import public,web,os,sys
class mget: pass;
class panelPlugin:
    __isTable = None;
    __install_path = None;
    __tasks = None;
    
    def __init__(self):
        self.__install_path = web.ctx.session.setupPath + '/panel/plugin'
        self.__isTable = public.M('plugin_list').dbfile('plugin').select();
        if type(self.__isTable) == str:
            self.__isTable = 'str'
            public.M('plugin_list').dbfile('plugin').fofile('data/plugin.sql');
            self.getCloudPlugin(mget());
    
    
    #安装插件
    def install(self,get):
        pluginInfo = public.M('plugin_list').dbfile('plugin').where('name=?',(get.name,)).field('title,tip,name,checks,shell,versions').find();
        if pluginInfo['tip'] == 'lib':
            if not os.path.exists(self.__install_path + '/' + pluginInfo['name']): os.system('mkdir -p ' + self.__install_path + '/' + pluginInfo['name']);
            if not hasattr(web.ctx.session,'downloadUrl'): web.ctx.session.downloadUrl = 'http://download.bt.cn';
            downloadUrl = web.ctx.session.downloadUrl + '/install/lib/plugin/' + pluginInfo['name'] + '/install.sh';
            toFile = self.__install_path + '/' + pluginInfo['name'] + '/install.sh';
            public.downloadFile(downloadUrl,toFile)
            os.system('/bin/bash ' + toFile + ' install')
            if self.checksSetup(pluginInfo['name'],pluginInfo['checks'],pluginInfo['versions'])[0]['status'] or os.path.exists(self.__install_path + '/' + get.name): 
                public.WriteLog('安装器','安装插件['+pluginInfo['title']+']成功！');
                os.system('rm -f ' + toFile);
                return public.returnMsg(True,'安装成功!');
            return public.returnMsg(False,'安装失败!');
        else:
            import db,time
            path = web.ctx.session.setupPath + '/php'
            if not os.path.exists(path): os.system("mkdir -p " + path);
            issue = public.readFile('/etc/issue')
            if web.ctx.session.server_os['x'] != 'RHEL': get.type = '3'
            
            apacheVersion='false';
            if web.ctx.session.webserver == 'apache':
                apacheVersion = public.readFile(web.ctx.session.setupPath+'/apache/version.pl');
            public.writeFile('/var/bt_apacheVersion.pl',apacheVersion)
            public.writeFile('/var/bt_setupPath.conf',web.ctx.session.rootPath)
            isTask = '/tmp/panelTask.pl'
            execstr = "cd " + web.ctx.session.setupPath + "/panel/install && /bin/bash install_soft.sh " + get.type + " install " + get.name + " "+ get.version;
            sql = db.Sql()
            if hasattr(get,'id'):
                id = get.id;
            else:
                id = None;
            sql.table('tasks').add('id,name,type,status,addtime,execstr',(None,'安装['+get.name+'-'+get.version+']','execshell','0',time.strftime('%Y-%m-%d %H:%M:%S'),execstr))
            public.writeFile(isTask,'True')
            public.WriteLog('安装器','添加安装任务['+get.name+'-'+get.version+']成功！');
            return public.returnMsg(True,'已将安装任务添加到队列');
        
    #卸载插件
    def unInstall(self,get):
        pluginInfo = public.M('plugin_list').dbfile('plugin').where('name=?',(get.name,)).field('title,tip,name,checks,shell').find();
        if pluginInfo['tip'] == 'lib':
            if not os.path.exists(self.__install_path+ '/' + pluginInfo['name']): os.system('mkdir -p ' + self.__install_path + '/' + pluginInfo['name']);
            downloadUrl = web.ctx.session.downloadUrl + '/install/lib/plugin/' + pluginInfo['name'] + '/install.sh';
            toFile = self.__install_path + '/' + pluginInfo['name'] + '/install.sh';
            public.downloadFile(downloadUrl,toFile)
            os.system('/bin/bash ' + toFile + ' uninstall')
            os.system('rm -rf ' + web.ctx.session.downloadUrl + '/install/lib/plugin/' + pluginInfo['name'])
            public.M('plugin_list').dbfile('plugin').execute('drop table plugin_' + get.name,());
            public.WriteLog('安装器','卸载软件['+pluginInfo['title']+']成功！');
            return public.returnMsg(True,'卸载成功!');
        else:
            get.type = '0'
            issue = public.readFile('/etc/issue')
            if web.ctx.session.server_os['x'] != 'RHEL': get.type = '3'
            public.writeFile('/var/bt_setupPath.conf',web.ctx.session.rootPath)
            execstr = "cd " + web.ctx.session.setupPath + "/panel/install && /bin/bash install_soft.sh "+get.type+" uninstall " + get.name.lower() + " "+ get.version.replace('.','');
            os.system(execstr);
            public.WriteLog('安装器','卸载软件['+get.name+'-'+get.version+']成功！');
            return public.returnMsg(True,"卸载成功!");
    
    #取插件列表
    def getPluginList(self,get):
        import json    
        arr = public.M('plugin_list').dbfile('plugin').field('pid,title,tip,name,type,status,versions,ps,checks,author,home,shell,addtime,ssort').order('ssort asc').select();
        apacheVersion = ""
        try:
            apavFile = '/www/server/apache/version.pl';
            if os.path.exists(apavFile):
                apacheVersion = public.readFile(apavFile).strip();
        except:
            pass;
            
        n = 0;
        for dirinfo in os.listdir(self.__install_path):
            path = self.__install_path + '/' + dirinfo
            if os.path.isdir(path):
                jsonFile = path + '/info.json'
                if os.path.exists(jsonFile):
                    try:
                        tmp = json.loads(public.readFile(jsonFile))
                        tmp['pid'] = len(arr) + 1000 + n
                        isTrue = True
                        for tm in arr:
                            if tmp['name'] == tm['name']: isTrue = False
                        if isTrue:
                            iconFile = web.ctx.session.setupPath + '/panel/static/img/soft_ico/ico-' + dirinfo + '.png' 
                            if not os.path.exists(iconFile): os.system('\cp -a -r ' + self.__install_path + '/' + dirinfo + '/icon.png ' + iconFile)
                            tmp['status'] = tmp['display'];
                            del(tmp['display'])
                            arr.append(tmp)
                    except:
                        pass
        for i in range(len(arr)):
            if arr[i]['name'] == 'php':
                if apacheVersion == '2.2':
                    arr[i]['versions'] = '5.2,5.3,5.4';
                elif apacheVersion == '2.4':
                    arr[i]['versions'] = '5.3,5.4,5.5,5.6,7.0,7.1';
                arr[i]['apache'] = apacheVersion;
                    
            arr[i]['versions'] = self.checksSetup(arr[i]['name'],arr[i]['checks'],arr[i]['versions'])
            if arr[i]['tip'] == 'lib': 
                arr[i]['path'] = self.__install_path + '/' + arr[i]['name']
                arr[i]['config'] = os.path.exists(arr[i]['path'] + '/index.html');
            else:
                arr[i]['path'] = '/www/server/' + arr[i]['name'];
        arr.append(public.M('tasks').where("status!=?",('1',)).count());
        return arr;
    
    #保存插件排序
    def savePluginSort(self,get):
        ssort = get.ssort.split('|');
        sql = public.M('plugin_list').dbfile('plugin');
        for i in range(len(ssort)):
            if int(ssort[i]) > 1000: continue;
            sql.where('pid=?',(ssort[i],)).setField('ssort',i);
        return public.returnMsg(True,'排序已保存!');
    
    #检查是否安装
    def checksSetup(self,name,checks,vers = ''):
        tmp = checks.split(',');
        versions = [];
        path = '/www/server/' + name + '/version.pl';
        v1 = '';
        if os.path.exists(path): v1 = public.readFile(path)
        if name == 'nginx': v1 = v1.replace('1.10', '1.12');
        if not self.__tasks:
            self.__tasks = public.M('tasks').where("status!=?",('1',)).field('status,name').select()
        isStatus = 0;
        versArr = vers.split(',');
        for v in versArr:
            version = {}
            
            v2 = v;
            if name == 'php': v2 = v2.replace('.','');
            status = False;
            for tm in tmp:
                if name == 'php':
                    if os.path.exists(tm.replace('VERSION',v2)): status = True;
                else:
                    if os.path.exists(tm) and isStatus == 0: 
                        if len(versArr) > 1:
                            if v1.find(v) != -1:
                                status = True
                                isStatus += 1;
                        else:
                            status = True
                            isStatus += 1;
            #处理任务标记
            isTask = '1';
            for task in self.__tasks:
                tmpt = public.getStrBetween('[',']',task['name'])
                if not tmpt:continue;
                tmp1 = tmpt.split('-');
                name1 = tmp1[0].lower();
                if name == 'php':
                    if name1 == name and tmp1[1] == v: isTask = task['status'];
                else:
                    if name1 == 'pure': name1 = 'pure-ftpd';
                    if name1 == name: isTask = task['status']; 
            
            version['status'] = status 
            version['version'] = v;
            version['task'] = isTask;
            versions.append(version);
        return self.checkRun(name,versions);
    
    #检查是否启动
    def checkRun(self,name,versions):
        if name == 'php':
            path = web.ctx.session.setupPath + '/php' 
            for i in range(len(versions)):
                if versions[i]['status']:
                    v4 = versions[i]['version'].replace('.','')
                    versions[i]['run'] = os.path.exists('/tmp/php-cgi-' + v4 + '.sock');
                    versions[i]['fpm'] = versions[i]['run'];
                    phpConfig = self.GetPHPConfig(v4);
                    versions[i]['max'] = phpConfig['max']
                    versions[i]['maxTime'] = phpConfig['maxTime']
                    versions[i]['pathinfo'] = phpConfig['pathinfo']
                    versions[i]['display'] = os.path.exists(path + '/' + v4 + '/display.pl');
                    if len(versions) < 5: versions[i]['run'] = True;
                
        elif name == 'nginx':
            status = False
            if os.path.exists('/etc/init.d/nginx'):
                pidf = '/www/server/nginx/logs/nginx.pid';
                if os.path.exists(pidf):
                    try:
                        pid = public.readFile(pidf)
                        pname = self.checkProcess(int(pid));
                        if pname == 'nginx': status = True;
                    except:
                        status = False
            for i in range(len(versions)):
                versions[i]['run'] = False
                if versions[i]['status']: versions[i]['run'] = status
        elif name == 'apache':
            status = False
            if os.path.exists('/etc/init.d/httpd'):
                pidf = '/www/server/apache/logs/httpd.pid';
                if os.path.exists(pidf):
                    try:
                        pid = public.readFile(pidf)
                        pname = self.checkProcess(int(pid));
                        if pname == 'httpd': status = True;
                    except:
                        status = False
            for i in range(len(versions)):
                versions[i]['run'] = False
                if versions[i]['status']: versions[i]['run'] = status
        elif name == 'mysql':
            status = os.path.exists('/tmp/mysql.sock')
            for i in range(len(versions)):
                versions[i]['run'] = False
                if versions[i]['status']: versions[i]['run'] = status
        elif name == 'tomcat':
            status = False
            if os.path.exists('/etc/init.d/tomcat'):
                if self.getPid('java'): status = True
            for i in range(len(versions)):
                versions[i]['run'] = False
                if versions[i]['status']: versions[i]['run'] = status
        elif name == 'pure-ftpd':
             for i in range(len(versions)):
                versions[i]['run'] = os.path.exists('/var/run/pure-ftpd.pid')
        elif name == 'phpmyadmin':
            for i in range(len(versions)):
                if versions[i]['status']: versions[i] = self.getPHPMyAdminStatus();
        else:
            for i in range(len(versions)):
                if versions[i]['status']: versions[i]['run'] = True;
        
        return versions
    
    #取PHPMyAdmin状态
    def getPHPMyAdminStatus(self):
        import re
        tmp = {}
        setupPath = web.ctx.session.setupPath;
        configFile = setupPath + '/nginx/conf/nginx.conf';
        pauth = False
        pstatus = False
        if os.path.exists(configFile):
            conf = public.readFile(configFile);
            rep = "listen\s+([0-9]+)\s*;";
            rtmp = re.search(rep,conf);
            if rtmp:
                phpport = rtmp.groups()[0];
            
            if conf.find('AUTH_START') != -1: pauth = True;
            if conf.find(setupPath + '/stop') == -1: pstatus = True;
            configFile = setupPath + '/nginx/conf/enable-php.conf';
            if not os.path.exists(configFile): public.writeFile(configFile,public.readFile(setupPath + '/nginx/conf/enable-php-54.conf'));
            conf = public.readFile(configFile);
            rep = "php-cgi-([0-9]+)\.sock";
            rtmp = re.search(rep,conf);
            if rtmp:
                phpversion = rtmp.groups()[0];
            else:
                rep = "php-cgi.*\.sock";
                public.writeFile(configFile,conf);
                phpversion = '54';
        
        configFile = setupPath + '/apache/conf/extra/httpd-vhosts.conf';
        if os.path.exists(configFile):
            conf = public.readFile(configFile);
            rep = "php-cgi-([0-9]+)\.sock";
            rtmp = re.search(rep,conf);
            if rtmp:
                phpversion = rtmp.groups()[0];
            rep = "Listen\s+([0-9]+)\s*\n";
            rtmp = re.search(rep,conf);
            if rtmp:
                phpport = rtmp.groups()[0];
            if conf.find('AUTH_START') != -1: pauth = True;
            if conf.find(web.ctx.session.setupPath + '/stop') == -1: pstatus = True;
        
        try:
            vfile = setupPath + '/phpmyadmin/version.pl';
            if os.path.exists(vfile):
                tmp['version'] = public.readFile(vfile).strip();
                tmp['status'] = True;
            else:
                tmp['version'] = "";
                tmp['status'] = False;
            
            tmp['run'] = pstatus;
            tmp['phpversion'] = phpversion;
            tmp['port'] = phpport;
            tmp['auth'] = pauth;
        except:
            tmp['status'] = False;
        return tmp;
        
    #取PHP配置
    def GetPHPConfig(self,version):
        import re
        setupPath = web.ctx.session.setupPath;
        file = setupPath + "/php/"+version+"/etc/php.ini"
        phpini = public.readFile(file)
        file = setupPath + "/php/"+version+"/etc/php-fpm.conf"
        phpfpm = public.readFile(file)
        data = {}
        try:
            rep = "upload_max_filesize\s*=\s*([0-9]+)M"
            tmp = re.search(rep,phpini).groups()
            data['max'] = tmp[0]
        except:
            data['max'] = '50'
        try:
            rep = "request_terminate_timeout\s*=\s*([0-9]+)\n"
            tmp = re.search(rep,phpfpm).groups()
            data['maxTime'] = tmp[0]
        except:
            data['maxTime'] = 0
        
        try:
            rep = ur"\n;*\s*cgi\.fix_pathinfo\s*=\s*([0-9]+)\s*\n"
            tmp = re.search(rep,phpini).groups()
            
            if tmp[0] == '1':
                data['pathinfo'] = True
            else:
                data['pathinfo'] = False
        except:
            data['pathinfo'] = False
        
        return data
    
    #名取PID
    def getPid(self,pname):
        try:
            import psutil
            pids = psutil.pids()
            for pid in pids:
                if psutil.Process(pid).name() == pname: return True;
            return None
        except:
            return None
    
    #检测指定进程是否存活
    def checkProcess(self,pid):
        try:
            import psutil
            proce = psutil.Process(pid)
            pname = proce.name()
            return pname;
        except:
            return None
    
    #获取配置模板
    def getConfigHtml(self,get):
        filename = self.__install_path + '/' + get.name + '/index.html';
        if not os.path.exists(filename): return public.returnMsg(False,'该插件没有配置模板!');
        
        srcBody = public.readFile(filename)
        
        data = {}
        if srcBody:
            import chardet
            char=chardet.detect(srcBody)
            data['encoding'] = char['encoding']
            if char['encoding'] == 'ascii':data['encoding'] = 'utf-8'
            data['data'] = srcBody.decode(char['encoding']).encode('utf-8')
        else:
            data['data'] = srcBody
            data['encoding'] = 'utf-8'
        
        data['status'] = True
        return data['data']
    
    #取插件信息
    def getPluginInfo(self,get):
        try:
            pluginInfo = public.M('plugin_list').dbfile('plugin').where('name=?',(get.name,)).field('pid,name,type,status,versions,ps,checks,author,home,shell,addtime').find();
            apacheVersion = ""
            try:
                apavFile = '/www/server/apache/version.pl';
                if os.path.exists(apavFile):
                    apacheVersion = public.readFile(apavFile).strip();
            except:
                pass;
            if pluginInfo['name'] == 'php':
                if apacheVersion == '2.2':
                    pluginInfo['versions'] = '5.2,5.3,5.4';
                elif apacheVersion == '2.4':
                    pluginInfo['versions'] = '5.3,5.4,5.5,5.6,7.0,7.1';
            
            pluginInfo['versions'] = self.checksSetup(pluginInfo['name'],pluginInfo['checks'],pluginInfo['versions'])
            if get.name == 'php':
                pluginInfo['phpSort'] = public.readFile('/www/server/php/sort.pl');
            return pluginInfo
        except:
            return False
    
    #取插件状态
    def getPluginStatus(self,get):
        find =  public.M('plugin_list').dbfile('plugin').where('name=?',(get.name,)).field('status,versions').find();
        versions = [];
        path = web.ctx.session.setupPath + '/php';
        for version in find['versions'].split(','):
            tmp = {}
            tmp['version'] = version
            if get.name == 'php':
                tmp['status'] = os.path.exists(path + '/' + version.replace(',','') + '/display.pl')
            else:
                tmp['status'] = find['status'];
            versions.append(tmp);
        return versions
    
    #设置插件状态
    def setPluginStatus(self,get):
        if get.name == 'php':
            isRemove = True
            path = web.ctx.session.setupPath + '/php';
            if get.status == '0':
                versions = public.M('plugin_list').dbfile('plugin').where('name=?',(get.name,)).getField('versions');
                os.system('rm -f ' + path + '/' + get.version.replace('.','') + '/display.pl');
                for version in versions.split(','):
                    if os.path.exists(path + '/' + version.replace('.','') + '/display.pl'):
                        isRemove = False;
                        break;
            else:
                public.writeFile(path + '/' + get.version.replace('.','') + '/display.pl','True');
            
            if isRemove:
                public.M('plugin_list').dbfile('plugin').where('name=?',(get.name,)).setField('status',get.status);
        else:
            public.M('plugin_list').dbfile('plugin').where('name=?',(get.name,)).setField('status',get.status);
        return public.returnMsg(True,'设置成功!');
    
    #从云端获取插件列表
    def getCloudPlugin(self,get):
        import json
        if not hasattr(web.ctx.session,'downloadUrl'): web.ctx.session.downloadUrl = 'http://download.bt.cn';
        
        downloadUrl = web.ctx.session.downloadUrl + '/install/lib/listTest.json'
        data = json.loads(public.httpGet(downloadUrl))
        
        n = i = j = 0;
        for pluginInfo in data:
            find = public.M('plugin_list').dbfile('plugin').where('name=?',(pluginInfo['name'],)).field('pid,name,versions').find();
            if find:
                if find['versions'] != pluginInfo['versions']:
                    result = public.M('plugin_list').dbfile('plugin').where('name=?',(pluginInfo['name'],)).save('title,tip,name,type,versions,ps,checks,author,home,shell,addtime',(pluginInfo['title'],pluginInfo['tip'],pluginInfo['name'],pluginInfo['type'],pluginInfo['versions'],pluginInfo['ps'],pluginInfo['checks'],pluginInfo['author'],pluginInfo['home'],pluginInfo['shell'],pluginInfo['date']));
                    j += 1
            else:
                public.M('plugin_list').dbfile('plugin').add('ssort,title,tip,name,type,status,versions,ps,checks,author,home,shell,addtime',(i,pluginInfo['title'],pluginInfo['tip'],pluginInfo['name'],pluginInfo['type'],pluginInfo['display'],pluginInfo['versions'],pluginInfo['ps'],pluginInfo['checks'],pluginInfo['author'],pluginInfo['home'],pluginInfo['shell'],pluginInfo['date']));
                
                n += 1
            i += 1;
            if pluginInfo['default']: 
                get.name = pluginInfo['name'];
                self.install(get);
        
        if not n and not j: return public.returnMsg(False,'您的插件列表已经是最新版本!');
        return public.returnMsg(True,'成功从云端获取['+str(n)+']个新插件,['+str(j)+']个插件更新!');
    
    #请求插件事件
    def a(self,get):
        if not hasattr(get,'name'): return public.returnMsg(False,'请传入插件名称!');
        path = self.__install_path + '/' + get.name
        if not os.path.exists(path + '/'+get.name+'_main.py'): return public.returnMsg(False,'该插件没有扩展方法!');
        sys.path.append(path);
        plugin_main = __import__(get.name+'_main');
        reload(plugin_main)
        pluginObject = eval('plugin_main.' + get.name + '_main()');
        if not hasattr(pluginObject,get.s): return public.returnMsg(False,'指定方法['+get.s+']不存在!');
        execStr = 'pluginObject.' + get.s + '(get)'
        return eval(execStr);
        
            
    
    
    