#coding: utf-8
#-------------------------------------------------------------------
# 宝塔Linux面板
#-------------------------------------------------------------------
# Copyright (c) 2015-2016 宝塔软件(http:#bt.cn) All rights reserved.
#-------------------------------------------------------------------
# Author: 黄文良 <2879625666@qq.com>
#-------------------------------------------------------------------

#------------------------------
# SSL接口
#------------------------------
import public,os,web,sys,binascii,urllib,json,time,datetime
reload(sys)
sys.setdefaultencoding('utf-8')
class panelSSL:
    
    __APIURL = 'https://www.bt.cn/api/Auth';
    __UPATH = 'data/userInfo.json';
    __userInfo = None;
    __PDATA = None;
    
    #构造方法
    def __init__(self):
        pdata = {}
        data = {}
        if os.path.exists(self.__UPATH):
            self.__userInfo = json.loads(public.readFile(self.__UPATH));
            if self.__userInfo:
                pdata['access_key'] = self.__userInfo['access_key'];
                data['secret_key'] = self.__userInfo['secret_key'];
        else:
            pdata['access_key'] = 'test';
            data['secret_key'] = '123456';
        pdata['data'] = data;
        self.__PDATA = pdata;
    
    #获取Token
    def GetToken(self,get):
        data = {}
        data['username'] = get.username;
        data['password'] = public.md5(get.password);
        pdata = {}
        pdata['data'] = self.De_Code(data);
        result = json.loads(public.httpPost(self.__APIURL+'/GetToken',pdata));
        result['data'] = self.En_Code(result['data']);
        if result['data']: public.writeFile(self.__UPATH,json.dumps(result['data']));
        del(result['data']);
        return result;
    
    #删除Token
    def DelToken(self,get):
        os.system("rm -f " + self.__UPATH);
        return public.returnMsg(True,"已解除绑定!");
    
    #获取用户信息
    def GetUserInfo(self,get):
        result = {}
        if self.__userInfo:
            userTmp = {}
            userTmp['username'] = self.__userInfo['username'][0:3]+'****'+self.__userInfo['username'][-4:];
            result['status'] = True;
            result['msg'] = '获取成功!';
            result['data'] = userTmp;
        else:
            userTmp = {}
            userTmp['username'] = '未绑定宝塔帐号';
            result['status'] = False;
            result['msg'] = '请绑定宝塔帐户!';
            result['data'] = userTmp;
        return result;
    
    #获取订单列表
    def GetOrderList(self,get):
        if hasattr(get,'siteName'):
            path =   '/etc/letsencrypt/live/'+ get.siteName + '/partnerOrderId';
            if os.path.exists(path):
                self.__PDATA['data']['partnerOrderId'] = public.readFile(path);
        
        self.__PDATA['data'] = self.De_Code(self.__PDATA['data']);
        result = json.loads(public.httpPost(self.__APIURL + '/GetSSLList',self.__PDATA));
        result['data'] = self.En_Code(result['data']);
        for i in range(len(result['data'])):
            result['data'][i]['endtime'] =   self.add_months(result['data'][i]['createTime'],result['data'][i]['validityPeriod'])
        return result;
    
    #计算日期增加(月)
    def add_months(self,dt,months):
        import calendar
        dt = datetime.datetime.fromtimestamp(dt/1000);
        month = dt.month - 1 + months
        year = dt.year + month / 12
        month = month % 12 + 1
        day = min(dt.day,calendar.monthrange(year,month)[1])
        return (time.mktime(dt.replace(year=year, month=month, day=day).timetuple()) + 86400) * 1000
    
    #申请证书
    def GetDVSSL(self,get):
        if not self.CheckDomain(get): return public.returnMsg(False,'以下域名解析不正确，或解析未生效!<li style="color:red;">'+get.domain+'</li>');
        self.__PDATA['data']['domain'] = get.domain;
        self.__PDATA['data'] = self.De_Code(self.__PDATA['data']);
        result = json.loads(public.httpPost(self.__APIURL + '/GetDVSSL',self.__PDATA));
        result['data'] = self.En_Code(result['data']);
        if hasattr(result['data'],'authValue'):
            public.writeFile(get.path + '/.well-known/pki-validation/fileauth.txt',result['data']['authValue']);
        return result;
    
    #检查域名是否解析
    def CheckDomain(self,get):
        try:
            epass = public.GetRandomString(32);
            spath = get.path + '/.well-known/pki-validation';
            if not os.path.exists(spath): os.system("mkdir -p '" + spath + "'");
            public.writeFile(spath + '/fileauth.txt',epass);
            result = public.httpGet('http://' + get.domain + '/.well-known/pki-validation/fileauth.txt');
            if result == epass: return True
            return False
        except:
            return False
    
    #确认域名
    def Completed(self,get):
        self.__PDATA['data']['partnerOrderId'] = get.partnerOrderId;
        self.__PDATA['data'] = self.De_Code(self.__PDATA['data']);
        if hasattr(get,'siteName'):
            get.path = public.M('sites').where('name=?',(get.siteName,)).getField('path');
            sslInfo = json.loads(public.httpPost(self.__APIURL + '/SyncOrder',self.__PDATA));
            sslInfo['data'] = self.En_Code(sslInfo['data']);
            try:
                public.writeFile(get.path + '/.well-known/pki-validation/fileauth.txt',sslInfo['data']['authValue']);
            except:
                return public.returnMsg(False,'验证信息写入失败!');
        result = json.loads(public.httpPost(self.__APIURL + '/Completed',self.__PDATA));
        result['data'] = self.En_Code(result['data']);
        return result;
    
    #同步指定订单
    def SyncOrder(self,get):
        self.__PDATA['data']['partnerOrderId'] = get.partnerOrderId;
        self.__PDATA['data'] = self.De_Code(self.__PDATA['data']);
        result = json.loads(public.httpPost(self.__APIURL + '/SyncOrder',self.__PDATA));
        result['data'] = self.En_Code(result['data']);
        return result;
    
    #获取证书
    def GetSSLInfo(self,get):
        self.__PDATA['data']['partnerOrderId'] = get.partnerOrderId;
        self.__PDATA['data'] = self.De_Code(self.__PDATA['data']);
        result = json.loads(public.httpPost(self.__APIURL + '/GetSSLInfo',self.__PDATA));
        result['data'] = self.En_Code(result['data']);
        
        #写配置到站点
        if hasattr(get,'siteName'):
            try:
                siteName = get.siteName;
                path =   '/etc/letsencrypt/live/'+ siteName;
                if not os.path.exists(path):
                    public.ExecShell('mkdir -p ' + path)
                csrpath = path+"/fullchain.pem";
                keypath = path+"/privkey.pem";
                pidpath = path+"/partnerOrderId";
                #清理旧的证书链
                public.ExecShell('rm -rf ' + path + '-00*')
                public.ExecShell('rm -rf /etc/letsencrypt/archive/' + get.siteName)
                public.ExecShell('rm -rf /etc/letsencrypt/archive/' + get.siteName + '-00*')
                public.ExecShell('rm -f /etc/letsencrypt/renewal/'+ get.siteName + '.conf')
                public.ExecShell('rm -f /etc/letsencrypt/renewal/'+ get.siteName + '-00*.conf')
                public.ExecShell('rm -f ' + path + '/README');
                
                public.writeFile(keypath,result['data']['privateKey']);
                public.writeFile(csrpath,result['data']['cert']+result['data']['certCa']);
                public.writeFile(pidpath,get.partnerOrderId);
                import panelSite
                panelSite.panelSite().SetSSLConf(get);
                public.serviceReload();
                return public.returnMsg(True,'设置成功!');
            except Exception,ex:
                return public.returnMsg(False,'设置失败!,' + str(ex));
        result['data'] = self.En_Code(result['data']);
        return result;
    
    #获取产品列表
    def GetSSLProduct(self,get):
        self.__PDATA['data'] = self.De_Code(self.__PDATA['data']);
        result = json.loads(public.httpPost(self.__APIURL + '/GetSSLProduct',self.__PDATA));
        result['data'] = self.En_Code(result['data']);
        return result;
    
    #加密数据
    def De_Code(self,data):
        pdata = urllib.urlencode(data);
        return binascii.hexlify(pdata);
    
    #解密数据
    def En_Code(self,data):
        result = urllib.unquote(binascii.unhexlify(data));
        return json.loads(result);
    
    
    
    