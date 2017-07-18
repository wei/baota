#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板 x3
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------
import os, sys, time
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

#文件的MD5值
def GetFileMd5(filename):
    if not os.path.isfile(filename): return False;
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest();

#取随机字符串
def GetRandomString(length):
    from random import Random
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    chrlen = len(chars) - 1
    random = Random()
    for i in range(length):
        str+=chars[random.randint(0, chrlen)]
    return str

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
    #重载Web服务配置
    if os.path.exists('/www/server/nginx/sbin/nginx'):
        result = ExecShell('/etc/init.d/nginx reload')
        if result[1].find('nginx.pid') != -1:
            ExecShell('pkill -9 nginx && sleep 1');
            ExecShell('/etc/init.d/nginx start');
    else:
        result = ExecShell('/etc/init.d/httpd reload')
    return result;

def phpReload(version):
    #重载PHP配置
    import os
    if os.path.exists('/www/server/php/' + version + '/libphp5.so'):
        ExecShell('/etc/init.d/httpd reload');
    else:
        ExecShell('/etc/init.d/php-fpm-'+version+' reload');
        
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
        import re;
        filename = 'data/iplist.txt'
        ipaddress = readFile(filename)
        if not ipaddress:
            import urllib2
            url = 'http://pv.sohu.com/cityjson?ie=utf-8'
            opener = urllib2.urlopen(url)
            str = opener.read()
            ipaddress = re.search('\d+.\d+.\d+.\d+',str).group(0)
            writeFile(filename,ipaddress)
        
        ipaddress = re.search('\d+.\d+.\d+.\d+',ipaddress).group(0);
        return ipaddress
    except:
        try:
            url = 'http://www.bt.cn/Api/getIpAddress';
            opener = urllib2.urlopen(url)
            return opener.read()
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


#处理MySQL配置文件
def CheckMyCnf():
    import os;
    confFile = '/etc/my.cnf'
    if not os.path.exists(confFile): return False;
    conf = readFile(confFile)
    if len(conf) > 100: return True;
    versionFile = '/www/server/mysql/version.pl';
    if not os.path.exists(versionFile): return False;
    
    versions = ['5.1','5.5','5.6','5.7','AliSQL']
    version = readFile(versionFile);
    for key in versions:
        if key in version:
            version = key;
            break;
    
    shellStr = '''
#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

CN='125.88.182.172'
HK='103.224.251.79'
HK2='103.224.251.67'
US='174.139.221.74'
sleep 0.5;
CN_PING=`ping -c 1 -w 1 $CN|grep time=|awk '{print $7}'|sed "s/time=//"`
HK_PING=`ping -c 1 -w 1 $HK|grep time=|awk '{print $7}'|sed "s/time=//"`
HK2_PING=`ping -c 1 -w 1 $HK2|grep time=|awk '{print $7}'|sed "s/time=//"`
US_PING=`ping -c 1 -w 1 $US|grep time=|awk '{print $7}'|sed "s/time=//"`

echo "$HK_PING $HK" > ping.pl
echo "$HK2_PING $HK2" >> ping.pl
echo "$US_PING $US" >> ping.pl
echo "$CN_PING $CN" >> ping.pl
nodeAddr=`sort -n -b ping.pl|sed -n '1p'|awk '{print $2}'`
if [ "$nodeAddr" == "" ];then
    nodeAddr=$HK
fi

Download_Url=http://$nodeAddr:5880


MySQL_Opt()
{
    MemTotal=`free -m | grep Mem | awk '{print  $2}'`
    if [[ ${MemTotal} -gt 1024 && ${MemTotal} -lt 2048 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 32M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 128#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 768K#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 768K#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 16#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 16M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 32M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 128M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 32M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 2048 && ${MemTotal} -lt 4096 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 64M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 256#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 1M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 1M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 32#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 32M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 64M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 256M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 64M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 4096 && ${MemTotal} -lt 8192 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 128M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 512#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 2M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 2M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 32M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 64#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 64M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 64M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 512M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 128M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 8192 && ${MemTotal} -lt 16384 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 256M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 1024#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 4M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 4M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 64M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 128#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 128M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 128M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 1024M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 256M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 16384 && ${MemTotal} -lt 32768 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 512M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 2048#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 8M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 128M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 256#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 256M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 256M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 2048M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 512M#" /etc/my.cnf
    elif [[ ${MemTotal} -ge 32768 ]]; then
        sed -i "s#^key_buffer_size.*#key_buffer_size = 1024M#" /etc/my.cnf
        sed -i "s#^table_open_cache.*#table_open_cache = 4096#" /etc/my.cnf
        sed -i "s#^sort_buffer_size.*#sort_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^read_buffer_size.*#read_buffer_size = 16M#" /etc/my.cnf
        sed -i "s#^myisam_sort_buffer_size.*#myisam_sort_buffer_size = 256M#" /etc/my.cnf
        sed -i "s#^thread_cache_size.*#thread_cache_size = 512#" /etc/my.cnf
        sed -i "s#^query_cache_size.*#query_cache_size = 512M#" /etc/my.cnf
        sed -i "s#^tmp_table_size.*#tmp_table_size = 512M#" /etc/my.cnf
        sed -i "s#^innodb_buffer_pool_size.*#innodb_buffer_pool_size = 4096M#" /etc/my.cnf
        sed -i "s#^innodb_log_file_size.*#innodb_log_file_size = 1024M#" /etc/my.cnf
    fi
}

wget -O /etc/my.cnf $Download_Url/install/conf/mysql-%s.conf -T 5
MySQL_Opt
''' % (version,)
    #判断是否迁移目录
    if os.path.exists('data/datadir.pl'):
        newPath = public.readFile('data/datadir.pl');
        mycnf = public.readFile('/etc/my.cnf');
        mycnf = mycnf.replace('/www/server/data',newPath);
        public.writeFile('/etc/my.cnf',mycnf);
        
    os.system(shellStr);
    WriteLog('守护程序', '检测到MySQL配置文件异常,可能导致mysqld服务无法正常启动,已自动修复!');
    return True;


def checksum(source_string):
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receive_one_ping(my_socket, ID, timeout):
    import struct,select
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: return
        timeReceived = time.time()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0: return

def send_one_ping(my_socket, dest_addr, ID):
    import socket,struct
    dest_addr = socket.gethostbyname(dest_addr)
    my_checksum = 0
    ICMP_ECHO_REQUEST = 8
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1) #压包
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + data
    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1

def do_one(dest_addr, timeout):
    import socket
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            msg = msg + (
            " - Note that ICMP messages can only be sent from processes"
            " running as root."
          )
            raise socket.error(msg)
        raise # raise the original error
    
    my_ID = os.getpid() & 0xFFFF
    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)
    my_socket.close()
    return delay

def get_url(timeout = 0.5):
    import json
    try:
        nodeFile = '/www/server/panel/data/node.json';
        node_list = json.loads(readFile(nodeFile));
        mnode = None
        for node in node_list:
            node['ping'] = do_one(node['address'], timeout)
            if not node['ping']: continue;
            if not mnode: mnode = node;
            if node['ping'] < mnode['ping']: mnode = node;
        return mnode['protocol'] + mnode['address'] + ':' + mnode['port'];
    except:
        return False
