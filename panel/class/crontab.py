#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http:#bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------
import public,db,os,web,time,re
class crontab:
    #取计划任务列表
    def GetCrontab(self,get):
        self.checkBackup()
        cront = public.M('crontab').order("id desc").field('id,name,type,where1,where_hour,where_minute,echo,addtime').select()
        data=[]
        for i in range(len(cront)):
            tmp=cront[i]
            if cront[i]['type']=="day":
                tmp['type']="每天"
                tmp['cycle']='每天, '+str(cront[i]['where_hour'])+'点'+str(cront[i]['where_minute'])+'分 执行'
            elif cront[i]['type']=="day-n":
                tmp['type']="每"+str(cront[i]['where1'])+'天'
                tmp['cycle']='每隔'+str(cront[i]['where1'])+'天 '+str(cront[i]['where_hour'])+'点'+str(cront[i]['where_minute'])+'分 执行'
            elif cront[i]['type']=="hour":
                tmp['type']="每小时"
                tmp['cycle']='每小时, 第'+str(cront[i]['where_minute'])+'分钟 执行'
            elif cront[i]['type']=="hour-n":
                tmp['type']="每"+str(cront[i]['where1'])+'小时'
                tmp['cycle']='每隔'+str(cront[i]['where1'])+'小时 第'+str(cront[i]['where_minute'])+'分钟 执行'
            elif cront[i]['type']=="minute-n":
                tmp['type']="每"+str(cront[i]['where1'])+'分钟'
                tmp['cycle']='每隔'+str(cront[i]['where1'])+'分钟执行'
            elif cront[i]['type']=="week":
                tmp['type']="每周"
                tmp['cycle']= '每周'+self.toWeek(int(cront[i]['where1']))+', '+str(cront[i]['where_hour'])+'点'+str(cront[i]['where_minute'])+'分执行'
            elif cront[i]['type']=="month":
                tmp['type']="每月"
                tmp['cycle']='每月, '+str(cront[i]['where1'])+'日 '+str(cront[i]['where_hour'])+'点'+str(cront[i]['where_minute'])+'分执行'
            data.append(tmp)
        return data
    
    #转换大写星期
    def toWeek(self,num):
        wheres={
                0   :   '日',
                1   :   '一',
                2   :   '二',
                3   :   '三',
                4   :   '四',
                5   :   '五',
                6   :   '六'
                }
        try:
            return wheres[num]
        except:
            return ''
    
    #检查环境
    def checkBackup(self):
        #检查备份脚本是否存在
        filePath=web.ctx.session.setupPath+'/panel/script/backup'
        if not os.path.exists(filePath):
            public.downloadFile('http://www.bt.cn/linux/backup.sh',filePath)
        #检查日志切割脚本是否存在
        filePath=web.ctx.session.setupPath+'/panel/script/logsBackup'
        if not os.path.exists(filePath):
            public.downloadFile('http://www.bt.cn/linux/logsBackup.py',filePath)
        #检查计划任务服务状态
        if public.ExecShell('/etc/init.d/crond status')[0].find('running') == -1:
            public.ExecShell('/etc/init.d/crond start')
    
    #添加计划任务
    def AddCrontab(self,get):
        #return public.returnMsg(False,'此为演示服务器,禁止添加计划任务!')
        if len(get['name'])<1:
             return public.returnMsg(False,'任务名称不能为空!')
        cuonConfig=""
        if get['type']=="day":
            cuonConfig = self.GetDay(get)
            name = "每天"
        elif get['type']=="day-n":
            cuonConfig = self.GetDay_N(get)
            name = "每"+get['where1']+'天'
        elif get['type']=="hour":
            cuonConfig = self.GetHour(get)
            name = "每小时"
        elif get['type']=="hour-n":
            cuonConfig = self.GetHour_N(get)
            name = "每小时"
        elif get['type']=="minute-n":
            cuonConfig = self.Minute_N(get)
        elif get['type']=="week":
            get['where1']=get['week']
            cuonConfig = self.Week(get)
        elif get['type']=="month":
            cuonConfig = self.Month(get)
        cronPath=web.ctx.session.setupPath+'/cron'
        cronName=self.GetShell(get)
        if type(cronName) == dict: return cronName;
        cuonConfig += ' ' + cronPath+'/'+cronName+' >> '+ cronPath+'/'+cronName+'.log 2>&1'
        self.WriteShell(cuonConfig)
        self.CrondReload()
        addData=public.M('crontab').add('name,type,where1,where_hour,where_minute,echo,addtime',(get['name'],get['type'],get['where1'],get['hour'],get['minute'],cronName,time.strftime('%Y-%m-%d %X',time.localtime())))
        if addData>0:
             return public.returnMsg(True,'添加成功!')
        return public.returnMsg(False,'添加失败!')
        
    #取任务构造Day
    def GetDay(self,param):
        cuonConfig ="{0} {1} * * * ".format(param['minute'],param['hour'])
        return cuonConfig
    #取任务构造Day_n
    def GetDay_N(self,param):
        cuonConfig ="{0} {1} */{2} * * ".format(param['minute'],param['hour'],param['where1'])
        return cuonConfig
    
    #取任务构造Hour
    def GetHour(self,param):
        cuonConfig ="{0} * * * * ".format(param['minute'])
        return cuonConfig
    
    #取任务构造Hour-N
    def GetHour_N(self,param):
        cuonConfig ="{0} */{1} * * * ".format(param['minute'],param['where1'])
        return cuonConfig
    
    #取任务构造Minute-N
    def Minute_N(self,param):
        cuonConfig ="*/{0} * * * * ".format(param['where1'])
        return cuonConfig
    
    #取任务构造week
    def Week(self,param):
        cuonConfig ="{0} {1} * * {2}".format(param['minute'],param['hour'],param['week'])
        return cuonConfig
    
    #取任务构造Month
    def Month(self,param):
        cuonConfig = "{0} {1} {2} * * ".format(param['minute'],param['hour'],param['where1'])
        return cuonConfig
    
    #取数据列表
    def GetDataList(self,get):
        data = {}
        data['data'] = public.M(get['type']).field('name,ps').select()
        data['orderOpt'] = [];
        import json
        tmp = public.readFile('data/libList.conf');
        libs = json.loads(tmp)
        import imp;
        for lib in libs:
            try:
                imp.find_module(lib['module']);
                tmp = {}
                tmp['name'] = lib['name'];
                tmp['value']= lib['opt']
                data['orderOpt'].append(tmp);
            except:
                continue;
        
        return data
    
    #取任务日志
    def GetLogs(self,get):
        id = get['id']
        echo = public.M('crontab').where("id=?",(id,)).field('echo').find()
        logFile = web.ctx.session.setupPath+'/cron/'+echo['echo']+'.log'
        if not os.path.exists(logFile):return public.returnMsg(False, '当前任务日志为空!')
        log = public.readFile(logFile)
        where = "Warning: Using a password on the command line interface can be insecure.\n"
        if  log.find(where)>-1:
            log = log.replace(where, '')
            public.writeFile('/tmp/read.tmp',log)
        return public.returnMsg(True, log)
    
    #清理任务日志
    def DelLogs(self,get):
        try:
            id = get['id']
            echo = public.M('crontab').where("id=?",(id,)).getField('echo')
            logFile = web.ctx.session.setupPath+'/cron/'+echo+'.log'
            os.remove(logFile)
            return public.returnMsg(True, '日志已清空!')
        except:
            return public.returnMsg(False, '清空日志失败!')
    
    #删除计划任务
    def DelCrontab(self,get):
        try:
            id = get['id']
            find = public.M('crontab').where("id=?",(id,)).field('name,echo').find()
            file = '/var/spool/cron/root'
            conf=public.readFile(file)
            rep = ".+" + str(find['echo']) + ".+\n"
            conf = re.sub(rep, "", conf)
            cronPath = web.ctx.session.setupPath + '/cron'
            public.writeFile(file,conf)
            
            sfile = cronPath + '/' + find['echo']
            if os.path.exists(sfile): os.remove(sfile)
            sfile = cronPath + '/' + find['echo'] + '.log'
            if os.path.exists(sfile): os.remove(sfile)
            
            self.CrondReload()
            public.M('crontab').where("id=?",(id,)).delete()
            public.WriteLog('计划任务', '删除计划任务[' + find['name'] + ']成功!')
            return public.returnMsg(True, '删除成功!')
        except:
            return public.returnMsg(False, '写入配置到计划任务失败!')
    
    #取执行脚本
    def GetShell(self,param):
        try:
            type=param['sType']
            if type=='toFile':
                shell=param.sFile
            else :
                head="#!/bin/bash\nPATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin\nexport PATH\n"
                log='-access_log'
                if web.ctx.session.webserver=='nginx':
                    log='.log'
                
                wheres={
                        'site'  :   head + "python " + web.ctx.session.setupPath+"/panel/script/backup.py site "+param['sName']+" "+param['save'],
                        'database': head + "python " + web.ctx.session.setupPath+"/panel/script/backup.py database "+param['sName']+" "+param['save'],
                        'logs'  :   head + web.ctx.session.setupPath+"/panel/script/logsBackup "+param['sName']+log+" "+param['save'],
                        'rememory' : head + "sh " + web.ctx.session.setupPath + '/panel/script/rememory.sh'
                        }
                if param['backupTo'] != 'localhost':
                    wheres={
                        'site'  :   head + "python " + web.ctx.session.setupPath+"/panel/script/backup_"+param['backupTo']+".py site "+param['sName']+" "+param['save'],
                        'database': head + "python " + web.ctx.session.setupPath+"/panel/script/backup_"+param['backupTo']+".py database "+param['sName']+" "+param['save'],
                        'logs'  :   head + web.ctx.session.setupPath+"/panel/script/logsBackup "+param['sName']+log+" "+param['save'],
                        'rememory' : head + "sh " + web.ctx.session.setupPath + '/panel/script/rememory.sh'
                        }              
                
                try:
                    shell=wheres[type]
                except:
                    if type == 'toUrl':
                        shell = head + 'curl -sS --connect-timeout 10 -m 60 ' + param.urladdress; 
                    else:
                        shell=head+param['sBody']
                    
                    shell += '''
echo "----------------------------------------------------------------------------"
endDate=`date +"%Y-%m-%d %H:%M:%S"`
echo "★[$endDate] 任务执行成功"
echo "----------------------------------------------------------------------------"
'''
            cronPath=web.ctx.session.setupPath+'/cron'
            if not os.path.exists(cronPath): public.ExecShell('mkdir -p ' + cronPath);
            cronName=public.md5(public.md5(str(time.time()) + '_bt'))
            file = cronPath+'/' + cronName
            public.writeFile(file,self.CheckScript(shell))
            public.ExecShell('chmod 750 ' + file)
            return cronName
        except Exception,ex:
            return public.returnMsg(False, '文件写入失败!')
        
    #检查脚本
    def CheckScript(self,shell):
        keys = ['shutdown','init 0','mkfs','passwd','chpasswd','--stdin','mkfs.ext','mke2fs']
        for key in keys:
            shell = shell.replace(key,'[***]');
        return shell;
    
    #重载配置
    def CrondReload(self):
        if os.path.exists('/usr/bin/systemctl'): 
            public.ExecShell("systemctl reload crond")
        else:
            public.ExecShell('/etc/rc.d/init.d/crond reload')
        
    #将Shell脚本写到文件
    def WriteShell(self,config):
        file='/var/spool/cron/root'
        if not os.path.exists(file): public.writeFile(file,'')
        conf = public.readFile(file)
        conf += config + "\n"
        if public.writeFile(file,conf):
            public.ExecShell("chmod 600 '" + file + "' && chown root.root " + file)
            return True
        return public.returnMsg(False,'写入配置到计划任务失败!')
    
    #立即执行任务
    def StartTask(self,get):
        echo = public.M('crontab').where('id=?',(get.id,)).getField('echo');
        execstr = web.ctx.session.setupPath + '/cron/' + echo;
        os.system('chmod +x ' + execstr)
        os.system('nohup ' + execstr + ' >> ' + execstr + '.log 2>&1 &');
        return public.returnMsg(True,'任务已执行!')
        
    
        