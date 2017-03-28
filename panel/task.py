#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

#------------------------------
# 计划任务
#------------------------------
import sys,os,json
sys.path.append("class/")
import db
global pre,timeoutCount,logPath,isTask
pre = 0
timeoutCount = 0
logPath = '/tmp/panelExec.log'
isTask = '/tmp/panelTask.pl'

def ExecShell(cmdstring, cwd=None, timeout=None, shell=True):
    global logPath
    import shlex
    import datetime
    import subprocess
    import time

    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    
    sub = subprocess.Popen(cmdstring+' > '+logPath+' 2>&1', cwd=cwd, stdin=subprocess.PIPE,shell=shell,bufsize=4096)
    
    while sub.poll() is None:
        time.sleep(0.1)
            
    return sub.returncode

#下载文件
def DownloadFile(url,filename):
    try:
        import urllib,socket
        socket.setdefaulttimeout(10)
        urllib.urlretrieve(url,filename=filename ,reporthook= DownloadHook)
        WriteLogs('done')
    except:
        global timeoutCount
        if timeoutCount > 5:
            return
        timeoutCount += 1
        DownloadFile(url,filename)
        


#下载文件进度回调  
def DownloadHook(count, blockSize, totalSize):
    global pre
    used = count * blockSize
    pre1 = int((100.0 * used / totalSize))
    if pre == pre1:
        return
    speed = {'total':totalSize,'used':used,'pre':pre}
    WriteLogs(json.dumps(speed))
    pre = pre1

#写输出日志
def WriteLogs(logMsg):
    global logPath
    fp = open(logPath,'w+');
    fp.write(logMsg)
    fp.close()

#计划任务  
def startTask():
    global isTask
    import time,public
    while True:
        taskTo = 'False'
        if os.path.exists(isTask): taskTo = public.readFile(isTask)
        if taskTo.strip() == 'True':
            sql = db.Sql()
            sql.table('tasks').where("status=?",('-1',)).setField('status','0')
            taskArr = sql.table('tasks').where("status=?",('0',)).field('id,type,execstr').order("id asc").select()
            for value in taskArr:
                start = int(time.time())
                sql.table('tasks').where("id=?",(value['id'],)).save('status,start',('-1',start))
                if value['type'] == 'download':
                    argv = value['execstr'].split('|bt|')
                    DownloadFile(argv[0],argv[1])
                elif value['type'] == 'execshell':
                    ExecShell(value['execstr'])
                end = int(time.time())
                sql.table('tasks').where("id=?",(value['id'],)).save('status,end',('1',end))
                if(sql.table('tasks').where("status=?",('0')).count() < 1): public.writeFile(isTask,'False')
        time.sleep(2)

#系统监控任务
def systemTask():
    import system,psutil,time
    filename = 'data/control.conf';
    sql = db.Sql().dbfile('system')
    cpuIo = cpu = {}
    cpuCount = psutil.cpu_count()
    used = count = 0
    network_up = network_down = diskio_1 = diskio_2 = networkInfo = cpuInfo = diskInfo = None
    while True:
        if not os.path.exists(filename):
            time.sleep(10);
            continue;
        
        day = 30;
        try:
            day = int(public.readFile(filename));
            if day < 1:
                time.sleep(10)
                continue;
        except:
            day  = 30
        
        
        tmp = {}
        #取当前CPU Io     
        tmp['used'] = psutil.cpu_percent(interval=1)
        
        if not cpuInfo:
            tmp['mem'] = GetMemUsed()
            cpuInfo = tmp 
        
        if cpuInfo['used'] < tmp['used']:
            tmp['mem'] = GetMemUsed()
            cpuInfo = tmp 
        
        
        
        #取当前网络Io
        networkIo = psutil.net_io_counters()[:4]
        if not network_up:
            network_up   =  networkIo[0]
            network_down =  networkIo[1]
        tmp = {}
        tmp['upTotal']      = networkIo[0]
        tmp['downTotal']    = networkIo[1]
        tmp['up']           = round(float((networkIo[0] - network_up) / 1024),2)
        tmp['down']         = round(float((networkIo[1] - network_down) / 1024),2)
        tmp['downPackets']  = networkIo[3]
        tmp['upPackets']    = networkIo[2]
        
        network_up   =  networkIo[0]
        network_down =  networkIo[1]
        
        if not networkInfo: networkInfo = tmp
        if (tmp['up'] + tmp['down']) > (networkInfo['up'] + networkInfo['down']): networkInfo = tmp
        
        #取磁盘Io
        diskio_2 = psutil.disk_io_counters()
        if not diskio_1: diskio_1 = diskio_2
        tmp = {}
        tmp['read_count']   = diskio_2.read_count - diskio_1.read_count
        tmp['write_count']  = diskio_2.write_count - diskio_1.write_count
        tmp['read_bytes']   = diskio_2.read_bytes - diskio_1.read_bytes
        tmp['write_bytes']  = diskio_2.write_bytes - diskio_1.write_bytes
        tmp['read_time']    = diskio_2.read_time - diskio_1.read_time
        tmp['write_time']   = diskio_2.write_time - diskio_1.write_time
        
        if not diskInfo: 
            diskInfo = tmp
        else:
            diskInfo['read_count']   += tmp['read_count']
            diskInfo['write_count']  += tmp['write_count']
            diskInfo['read_bytes']   += tmp['read_bytes']
            diskInfo['write_bytes']  += tmp['write_bytes']
            diskInfo['read_time']    += tmp['read_time']
            diskInfo['write_time']   += tmp['write_time']
        
        diskio_1 = diskio_2
        
        #print diskInfo
        
        if count >= 12:
            try:
                addtime = int(time.time())
                deltime = addtime - (day * 86400)
                
                data = (cpuInfo['used'],cpuInfo['mem'],addtime)
                sql.table('cpuio').add('pro,mem,addtime',data)
                sql.table('cpuio').where("addtime<?",(deltime,)).delete();
                
                data = (networkInfo['up'] / 5,networkInfo['down'] / 5,networkInfo['upTotal'],networkInfo['downTotal'],networkInfo['downPackets'],networkInfo['upPackets'],addtime)
                sql.table('network').add('up,down,total_up,total_down,down_packets,up_packets,addtime',data)
                sql.table('network').where("addtime<?",(deltime,)).delete();
                
                data = (diskInfo['read_count'],diskInfo['write_count'],diskInfo['read_bytes'],diskInfo['write_bytes'],diskInfo['read_time'],diskInfo['write_time'],addtime)
                sql.table('diskio').add('read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime',data)
                sql.table('diskio').where("addtime<?",(deltime,)).delete();
                
                cpuInfo = None
                networkInfo = None
                diskInfo = None
                count = 0
            except:
                pass;
        del(tmp)
        
        time.sleep(5)
        count +=1
            

#取内存使用率
def GetMemUsed():
    import psutil
    mem = psutil.virtual_memory()
    memInfo = {'memTotal':mem.total/1024/1024,'memFree':mem.free/1024/1024,'memBuffers':mem.buffers/1024/1024,'memCached':mem.cached/1024/1024}
    tmp = memInfo['memTotal'] - memInfo['memFree'] - memInfo['memBuffers'] - memInfo['memCached']
    tmp1 = memInfo['memTotal'] / 100
    return (tmp / tmp1)

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=systemTask)
    t.setDaemon(True)
    t.start()
    startTask()
    

