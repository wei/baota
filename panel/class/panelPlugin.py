#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2017 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------
import public,web,os,sys,json
class mget: pass;
class panelPlugin:
    __isTable = None;
    __install_path = None;
    __tasks = None;
    __list = 'data/list.json'
    __type = 'data/type.json'
    
    def __init__(self):
        self.__install_path = '/www/server/panel/plugin'
        if not os.path.exists(self.__list): self.getCloudPlugin(None);
    
    #取列表
    def GetList(self,get = None):
        try:
            if not os.path.exists(self.__list): return [];
            data = json.loads(public.readFile(self.__list));
            #排序
            data = sorted(data, key= lambda b:b['sort'],reverse=False);
            
            #获取非划分列表
            n = 0;
            for dirinfo in os.listdir(self.__install_path):
                isTrue = True
                for tm in data:
                    if tm['name'] == dirinfo: isTrue = False
                if not isTrue: continue;
                
                path = self.__install_path + '/' + dirinfo
                if os.path.isdir(path):
                    jsonFile = path + '/info.json'
                    if os.path.exists(jsonFile):
                        try:
                            tmp = json.loads(public.readFile(jsonFile))
                            
                            if not hasattr(get,'type'): 
                                get.type = 0;
                            else:
                                get.type = int(get.type)
                            
                            if get.type > 0:
                                try:
                                    if get.type != tmp['id']: continue;
                                except:
                                    continue;
                            
                            tmp['pid'] = len(data) + 1000 + n
                            
                            #处理图标
                            iconFile = web.ctx.session.setupPath + '/panel/static/img/soft_ico/ico-' + dirinfo + '.png' 
                            if not os.path.exists(iconFile): os.system('\cp -a -r ' + self.__install_path + '/' + dirinfo + '/icon.png ' + iconFile)
                            tmp['status'] = tmp['display'];
                            tmp['display'] = 0;
                            data.append(tmp)
                        except:
                            pass
            #索引列表
            if get:
                display = None
                if hasattr(get,'display'): display = True;
                if not hasattr(get,'type'): 
                    get.type = 0;
                else:
                    get.type = int(get.type)
                if not hasattr(get,'search'): 
                    search = None
                    m = 0
                else:
                    search = get.search.encode('utf-8').lower();
                    m = 1
                    
                tmp = [];
                for d in data:
                    if display:
                        if d['display'] == 0: continue;
                    i=0;
                    if get.type > 0:
                        if get.type == d['id']: i+=1
                    else:
                        i+=1
                    if search:
                        if d['name'].lower().find(search) != -1: i+=1;
                        if d['name'].find(search) != -1: i+=1;
                        if d['title'].lower().find(search) != -1: i+=1;
                        if d['title'].find(search) != -1: i+=1;
                        if get.type > 0 and get.type != d['type']: i -= 1;
                    if i>m:tmp.append(d);
                data = tmp;
            return data
        except:
            return [];
    
    #取分页
    def GetPage(self,data,get):
        #包含分页类
        import page
        #实例化分页类
        page = page.Page();
        info = {}
        info['count'] = len(data)
        info['row']   = 15
        info['p'] = 1
        if hasattr(get,'p'):
            info['p']     = int(get['p'])
        info['uri']   = {}
        info['return_js'] = ''
        if hasattr(get,'tojs'):
            info['return_js']   = get.tojs
        
        #获取分页数据
        result = {}
        result['page'] = page.GetPage(info)
        n = 0;
        result['data'] = [];
        for i in range(info['count']):
            if n > page.ROW: break;
            if i < page.SHIFT: continue;
            n += 1;
            result['data'].append(data[i]);
        return result;
    
    #取分类
    def GetType(self,get = None):
        try:
            if not os.path.exists(self.__type): return False;
            data = json.loads(public.readFile(self.__type));
            return data
        except:
            return False;
        
    #取单个
    def GetFind(self,name):
        try:
            data = self.GetList(None);
            for d in data:
                if d['name'] == name: return d;
            return None
        except:
            return None;
    
    #设置
    def SetField(self,name,key,value):
        data = self.GetList(None);
        for i in range(len(data)):
            if data[i]['name'] != name: continue;
            data[i][key] = value;
        
        public.writeFile(self.__list,json.dumps(data));
        return True;
    
    
    
    #安装插件
    def install(self,get):
        pluginInfo = self.GetFind(get.name);
        if not pluginInfo:
            import json
            pluginInfo = json.loads(public.readFile(self.__install_path + '/' + get.name + '/info.json'));
        
        if pluginInfo['tip'] == 'lib':
            if not os.path.exists(self.__install_path + '/' + pluginInfo['name']): os.system('mkdir -p ' + self.__install_path + '/' + pluginInfo['name']);
            if not hasattr(web.ctx.session,'downloadUrl'): web.ctx.session.downloadUrl = 'http://download.bt.cn';
            downloadUrl = web.ctx.session.downloadUrl + '/install/lib/plugin/' + pluginInfo['name'] + '/install.sh';
            toFile = self.__install_path + '/' + pluginInfo['name'] + '/install.sh';
            public.downloadFile(downloadUrl,toFile)
            os.system('/bin/bash ' + toFile + ' install')
            if self.checksSetup(pluginInfo['name'],pluginInfo['checks'],pluginInfo['versions'])[0]['status'] or os.path.exists(self.__install_path + '/' + get.name): 
                public.WriteLog('TYPE_SETUP','PLUGIN_INSTALL_LIB',(pluginInfo['title'],));
                os.system('rm -f ' + toFile);
                return public.returnMsg(True,'PLUGIN_INSTALL_SUCCESS');
            return public.returnMsg(False,'PLUGIN_INSTALL_ERR');
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
            public.WriteLog('TYPE_SETUP','PLUGIN_ADD',(get.name,get.version));
            return public.returnMsg(True,'PLUGIN_INSTALL');
        
    #卸载插件
    def unInstall(self,get):
        pluginInfo = self.GetFind(get.name);
        if not pluginInfo:
            import json
            pluginInfo = json.loads(public.readFile(self.__install_path + '/' + get.name + '/info.json'));
        
        if pluginInfo['tip'] == 'lib':
            if not os.path.exists(self.__install_path+ '/' + pluginInfo['name']): os.system('mkdir -p ' + self.__install_path + '/' + pluginInfo['name']);
            downloadUrl = web.ctx.session.downloadUrl + '/install/lib/plugin/' + pluginInfo['name'] + '/install.sh';
            toFile = self.__install_path + '/' + pluginInfo['name'] + '/install.sh';
            public.downloadFile(downloadUrl,toFile)
            os.system('/bin/bash ' + toFile + ' uninstall')
            os.system('rm -rf ' + web.ctx.session.downloadUrl + '/install/lib/plugin/' + pluginInfo['name'])
            public.WriteLog('TYPE_SETUP','PLUGIN_UNINSTALL_SOFT',(pluginInfo['title'],));
            return public.returnMsg(True,'PLUGIN_UNINSTALL');
        else:
            get.type = '0'
            issue = public.readFile('/etc/issue')
            if web.ctx.session.server_os['x'] != 'RHEL': get.type = '3'
            public.writeFile('/var/bt_setupPath.conf',web.ctx.session.rootPath)
            execstr = "cd " + web.ctx.session.setupPath + "/panel/install && /bin/bash install_soft.sh "+get.type+" uninstall " + get.name.lower() + " "+ get.version.replace('.','');
            os.system(execstr);
            public.WriteLog('TYPE_SETUP','PLUGIN_UNINSTALL',(get.name,get.version));
            return public.returnMsg(True,"PLUGIN_UNINSTALL");
    
    #取插件列表
    def getPluginList(self,get):
        import json
        arr = self.GetList(get);
        result = {}
        if not arr: 
            result['data'] = arr;
            result['type'] = self.GetType(None);
            return result;
        apacheVersion = ""
        try:
            apavFile = '/www/server/apache/version.pl';
            if os.path.exists(apavFile):
                apacheVersion = public.readFile(apavFile).strip();
        except:
            pass;
        
        result = self.GetPage(arr,get);
        arr = result['data'];
            
        for i in range(len(arr)):
            if arr[i]['name'] == 'php':
                if apacheVersion == '2.2':
                    arr[i]['versions'] = '5.2,5.3,5.4';
                elif apacheVersion == '2.4':
                    arr[i]['versions'] = '5.3,5.4,5.5,5.6,7.0,7.1';
                arr[i]['apache'] = apacheVersion;
                    
            arr[i]['versions'] = self.checksSetup(arr[i]['name'].replace('_soft',''),arr[i]['checks'],arr[i]['versions'])
            
            #是否强制使用插件模板 LIB_TEMPLATE
            if os.path.exists(self.__install_path+'/'+arr[i]['name']): arr[i]['tip'] = 'lib';
            
            if arr[i]['tip'] == 'lib': 
                arr[i]['path'] = self.__install_path + '/' + arr[i]['name'].replace('_soft','');
                arr[i]['config'] = os.path.exists(arr[i]['path'] + '/index.html');
            else:
                arr[i]['path'] = '/www/server/' + arr[i]['name'].replace('_soft','');
        arr.append(public.M('tasks').where("status!=?",('1',)).count());
        
        
        result['data'] = arr;
        result['type'] = self.GetType(None);
        return result;
    
    #保存插件排序
    def savePluginSort(self,get):
        ssort = get.ssort.split('|');
        data = self.GetList(None)
        l = len(data);
        for i in range(len(ssort)):
            if int(ssort[i]) > 1000: continue;
            for n in range(l):
                if data[n]['pid'] == int(ssort[i]): data[n]['sort'] = i;
        public.writeFile(self.__list,json.dumps(data));
        return public.returnMsg(True,'PLUGIN_SORT');
    
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
                    versions[i]['fpm'] = os.path.exists('/etc/init.d/php-fpm-'+v4);
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
                        pname = self.checkProcess(pid,'nginx');
                        if pname: status = True;
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
                    pid = public.readFile(pidf)
                    status = self.checkProcess(pid,'httpd');
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
            if os.path.exists('/www/server/tomcat/logs/catalina-daemon.pid'):
                if self.getPid('jsvc'): status = True
            if not status:
                if self.getPid('java'): status = True
            for i in range(len(versions)):
                versions[i]['run'] = False
                if versions[i]['status']: versions[i]['run'] = status
        elif name == 'pure-ftpd':
             for i in range(len(versions)):
                pidf = '/var/run/pure-ftpd.pid'
                if os.path.exists(pidf):
                    pid = public.readFile(pidf)
                    versions[i]['run'] = self.checkProcess(pid,'pure-ftpd')
                    if not versions[i]['run']: os.system('rm -f ' + pidf)
        elif name == 'phpmyadmin':
            for i in range(len(versions)):
                if versions[i]['status']: versions[i] = self.getPHPMyAdminStatus();
        elif name == 'redis':
            for i in range(len(versions)):
                pidf = '/var/run/redis_6379.pid'
                if os.path.exists(pidf):
                    pid = public.readFile(pidf)
                    versions[i]['run'] = self.checkProcess(pid,'redis-server')
                    if not versions[i]['run']: os.system('rm -f ' + pidf)
        elif name == 'memcached':
            for i in range(len(versions)):
                pidf = '/var/run/memcached.pid'
                if os.path.exists(pidf):
                    pid = public.readFile(pidf)
                    versions[i]['run'] = self.checkProcess(pid,'memcached')
                    if not versions[i]['run']: os.system('rm -f ' + pidf)
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
        phpversion = "54";
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
        except Exception,ex:
            tmp['status'] = False;
            tmp['error'] = str(ex);
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
    def checkProcess(self,pid,name):
        try:
            pids = public.ExecShell('pidof ' + name)[0].split()
            if pid.strip() in pids: return True
            return False;
        except:
            return False
    
    #获取配置模板
    def getConfigHtml(self,get):
        filename = self.__install_path + '/' + get.name + '/index.html';
        if not os.path.exists(filename): return public.returnMsg(False,'PLUGIN_GET_HTML');
        
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
            pluginInfo = self.GetFind(get.name)
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
        find = self.GetFind(get.name);
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
                versions = self.GetFind(get.name)['versions']
                os.system('rm -f ' + path + '/' + get.version.replace('.','') + '/display.pl');
                for version in versions.split(','):
                    if os.path.exists(path + '/' + version.replace('.','') + '/display.pl'):
                        isRemove = False;
                        break;
            else:
                public.writeFile(path + '/' + get.version.replace('.','') + '/display.pl','True');
            
            if isRemove:
                self.SetField(get.name, 'display', int(get.status))
        else:
            self.SetField(get.name, 'display', int(get.status))
        return public.returnMsg(True,'SET_SUCCESS');
    
    #从云端获取插件列表
    def getCloudPlugin(self,get):
        if hasattr(web.ctx.session,'getCloudPlugin') and get != None: return public.returnMsg(True,'您的插件列表已经是最新版本-1!');
        import json
        if not hasattr(web.ctx.session,'downloadUrl'): web.ctx.session.downloadUrl = 'http://download.bt.cn';
        
        #获取列表
        try:
            newUrl = public.get_url();
            downloadUrl = newUrl + '/install/list.json'
            data = json.loads(public.httpGet(downloadUrl))
            web.ctx.session.downloadUrl = newUrl;
        except:
            downloadUrl = web.ctx.session.downloadUrl + '/install/list.json'
            data = json.loads(public.httpGet(downloadUrl))
        
        n = i = j = 0;
        
        lists = self.GetList(None);
        
        for i in range(len(data)):
            for pinfo in lists:
                if data[i]['name'] != pinfo['name']: continue;
                data[i]['display'] = pinfo['display'];
            if data[i]['default']: 
                get.name = data[i]['name'];
                self.install(get);
        
        public.writeFile(self.__list,json.dumps(data));
        
        #获取分类
        try:
            downloadUrl = web.ctx.session.downloadUrl + '/install/type.json'
            types = json.loads(public.httpGet(downloadUrl))
            public.writeFile(self.__type,json.dumps(types));
        except:
            pass;
        
        self.getCloudPHPExt(get);
        web.ctx.session.getCloudPlugin = True;
        return public.returnMsg(True,'PLUGIN_UPDATE');
    
    #获取PHP扩展
    def getCloudPHPExt(self,get):
        import json
        try:
            if not hasattr(web.ctx.session,'downloadUrl'): web.ctx.session.downloadUrl = 'http://download.bt.cn';
            downloadUrl = web.ctx.session.downloadUrl + '/install/lib/phplib.json'
            tstr = public.httpGet(downloadUrl)
            data = json.loads(tstr);
            if not data: return False;
            public.writeFile('data/phplib.conf',json.dumps(data));
            return True;
        except:
            return False;
    
    #请求插件事件
    def a(self,get):
        if not hasattr(get,'name'): return public.returnMsg(False,'PLUGIN_INPUT_A');
        path = self.__install_path + '/' + get.name
        if not os.path.exists(path + '/'+get.name+'_main.py'): return public.returnMsg(False,'PLUGIN_INPUT_B');
        sys.path.append(path);
        plugin_main = __import__(get.name+'_main');
        reload(plugin_main)
        pluginObject = eval('plugin_main.' + get.name + '_main()');
        if not hasattr(pluginObject,get.s): return public.returnMsg(False,'PLUGIN_INPUT_C',(get.s,));
        execStr = 'pluginObject.' + get.s + '(get)'
        return eval(execStr);
        
            
    
    
    