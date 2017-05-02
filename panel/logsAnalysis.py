#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

#------------------------------
# 日志分析器
#------------------------------
import sys
sys.path.append("class/")
import time,public,db,os
class logsAnalysis:
    
    def openLogs(self,filename):
        fp = open(filename,'r');
        fp.readline()
    
    def GetNginxLogs(self):
        fp = open('e:\\www.bt.cn.log_2017-04-19_120101.log','r')
        line = fp.readline()
        sql = public.M('site_logs').dbfile('siteLogs');
        while line:
            line = line.replace('"','').replace("(",'').replace(")",'').replace(';','');
            tmp = {}
            arr = line.split();
            try:
                tmp['address'] = arr[0];
                tmp['mtime'] = int(time.mktime(time.strptime(arr[3],'[%d/%b/%Y:%H:%M:%S')));
                tmp['type'] = arr[5]
                tmp['uri'] = arr[6];
                tmp['http_version'] = arr[7];
                tmp['status'] = arr[8];
                tmp['size'] = int(arr[9]);
                tmp['referer'] = arr[10];
                tmp['os'] = arr[12] + ' ' + arr[13] + ' ' +  arr[14].replace(';','') + ' ' + arr[15].replace('WOW','X')
                tmp['browser'] = arr[20]
            except:
                try:
                    if not hasattr(tmp, 'size'): tmp['size'] = 0;
                    tmp['referer'] = '_'
                    tmp['os'] = '_'
                    tmp['browser'] = arr[11]
                except:
                    line = fp.readline()
                    continue
            
            sql.addAll('address,mtime,type,uri,http_version,status,size,referer,os,browser',(tmp['address'],tmp['mtime'],tmp['type'],tmp['uri'],tmp['http_version'],tmp['status'],tmp['size'],tmp['referer'],tmp['os'],tmp['browser']))
            line = fp.readline()
        sql.commit();
            #break;
    def checkDB(self):
        if os.path.exists('data/siteLogs.db'): return self
        dbobj = db.Sql();
        print dbobj.dbfile('siteLogs').create('siteLogs');
        return self;
        
        
        


logsAnalysis().checkDB().GetNginxLogs();