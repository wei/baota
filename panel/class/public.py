#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板 x3
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

def M(table):
    import db
    sql = db.Sql()
    return sql.table(table);

def md5(str):
    #生成MD5
    try:
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    except:
        return False

def checkCode(code,outime = 120):
    #校验验证码
    import time,web
    try:
        if md5(code.lower()) != web.ctx.session.codeStr:
            web.ctx.session.login_error = '验证码错误,请重新输入!'
            return False
        if time.time() - web.ctx.session.codeTime > outime:
            web.ctx.session.login_error = '验证码已过期,请点验证码图片重新获取!'
            return False
        return True
    except:
        web.ctx.session.login_error = '验证码不存在!'
        return False

def returnJson(status,msg):
    #取通用Json返回
    return getJson({'status':status,'msg':msg})

def returnMsg(status,msg):
    #取通用字曲返回
    return {'status':status,'msg':msg}

def getJson(data):
    import json,web
    web.header('Content-Type','application/json; charset=utf-8')
    return json.dumps(data)

def readFile(filename):
    #读文件内容
    try:
        fp = open(filename, 'r');
        fBody = fp.read()
        fp.close()
        return fBody
    except:
        return False

def getDate():
    #取格式时间
    import time
    return time.strftime('%Y-%m-%d %X',time.localtime())

def WriteLog(type,logMsg):
    #写日志
    try:
        import time
        import db
        sql = db.Sql()
        mDate = time.strftime('%Y-%m-%d %X',time.localtime())
        data = (type,logMsg,mDate)
        result = sql.table('logs').add('type,log,addtime',data)
        writeFile('/tmp/test.pl', str(data))
    except:
        pass
    
def writeFile(filename,str):
    #写文件内容
    try:
        fp = open(filename, 'w+');
        fp.write(str)
        fp.close()
        return True
    except:
        return False
    
def httpGet(url):
    #发送GET请求
    try:
        import urllib2 
        response = urllib2.urlopen(url) 
        return response.read()
    except Exception,ex:
        return str(ex);

def httpPost(url,data):
    #发送POST请求
    try:
        import urllib 
        import urllib2 
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read()
    except Exception,ex:
        return str(ex);


def ExecShell(cmdstring, cwd=None, timeout=None, shell=True):
    import shlex
    import datetime
    import subprocess
    import time

    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    
    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,shell=shell,bufsize=4096,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout：%s"%cmdstring)
            
    return sub.communicate()


def serviceReload():
    import web
    #重载Web服务配置
    if web.ctx.session.webserver == 'nginx':
        result = ExecShell('/etc/init.d/nginx reload')
        if result[1].find('nginx.pid') != -1:
            ExecShell('pkill -9 nginx && sleep 1');
            ExecShell('/etc/init.d/nginx start');
    else:
        result = ExecShell('/etc/init.d/httpd reload')
    return result;

def phpReload(version):
    #重载PHP配置
    ExecShell('/etc/init.d/php-fpm-'+version+' reload')
        
def downloadFile(url,filename):
    import urllib
    urllib.urlretrieve(url,filename=filename ,reporthook= downloadHook)
    
def downloadHook(count, blockSize, totalSize):
    speed = {'total':totalSize,'block':blockSize,'count':count}
    print speed
    print '%02d%%'%(100.0 * count * blockSize / totalSize)
    
    
def GetLocalIp():
    #取本地外网IP
    try:
        filename = 'data/iplist.txt'
        ipaddress = readFile(filename)
        if not ipaddress:
            import re,urllib2
            url = 'http://pv.sohu.com/cityjson?ie=utf-8'
            opener = urllib2.urlopen(url)
            str = opener.read()
            ipaddress = re.search('\d+.\d+.\d+.\d+',str).group(0)
            writeFile(filename,ipaddress)
        return ipaddress
    except:
        import web
        return web.ctx.host.split(':')[0];

#搜索数据中是否存在
def inArray(arrays,searchStr):
    for key in arrays:
        if key == searchStr: return True
    
    return False

#检查Web服务器配置文件是否有错误
def checkWebConfig():
    import web
    if web.ctx.session.webserver == 'nginx':
        result = ExecShell(web.ctx.session.setupPath+"/nginx/sbin/nginx -t -c "+web.ctx.session.setupPath+"/nginx/conf/nginx.conf");
        searchStr = 'successful'
    else:
        result = ExecShell(web.ctx.session.setupPath+"/apache/bin/apachectl -t");
        searchStr = 'Syntax OK'
    
    if result[1].find(searchStr) == -1:
        WriteLog("检查配置", "配置文件错误: "+result[1]);
        return result[1];
    return True;

#检查是否为IPv4地址
def checkIp(ip):
    import re
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')  
    if p.match(ip):  
        return True  
    else:  
        return False
    
#检查端口是否合法
def checkPort(port):
    ports = ['21','25','443','8080','888','8888','8443'];
    if port in ports: return False;
    intport = int(port);
    if intport < 1 or intport > 65535: return False;
    return True;

#字符串取中间
def getStrBetween(startStr,endStr,srcStr):
    start = srcStr.find(startStr)
    if start == -1: return None
    end = srcStr.find(endStr)
    if end == -1: return None
    return srcStr[start+1:end]

#取CPU类型
def getCpuType():
    import re;
    cpuinfo = open('/proc/cpuinfo','r').read();
    rep = "model\s+name\s+:\s+(.+)"
    tmp = re.search(rep,cpuinfo);
    cpuType = None
    if tmp:
        cpuType = tmp.groups()[0];
    return cpuType;


#检查是否允许重启
def IsRestart():
    num  = M('tasks').where('status!=?',('1',)).count();
    if num > 0: return False;
    return True;

#加密密码字符
def hasPwd(password):
    import crypt;
    return crypt.crypt(password,password);    
    
    
    
    
        