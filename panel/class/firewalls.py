#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板 x3
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http:#bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------
import sys,os,web,public,re
reload(sys)
sys.setdefaultencoding('utf-8')
class firewalls:
    __isFirewalld = False
    
    def __init__(self):
        if os.path.exists('/usr/sbin/firewalld'): self.__isFirewalld = True
        print self.__isFirewalld
        
    #重载防火墙配置
    def FirewallReload(self):
        if self.__isFirewalld:
            public.ExecShell('firewall-cmd --reload')
        else:
            public.ExecShell('/etc/init.d/iptables save')
            public.ExecShell('/etc/init.d/iptables restart')
    
    #设置防火墙状态
    def SetFirewallStatus(self,get):
        status = status
        result = SendSocket("Firewall|status|".status)
        return (result)
    
    
    #添加屏蔽IP
    def AddDropAddress(self,get):
        import time
        #return public.returnMsg(False,'体验服务器，禁止操作!')
        address = get.port
        if public.M('firewall').where("port=?",(address,)).count() > 0: return public.returnMsg(False,'您要放屏蔽的IP已存在屏蔽列表，无需重复处理!')
        if self.__isFirewalld:
            public.ExecShell('firewall-cmd --permanent --add-rich-rule=\'rule family=ipv4 source address="'+ address +'" drop\'')
        else:
            public.ExecShell('iptables -I INPUT -s '+address+' -j DROP')
        
        public.WriteLog("防火墙管理", '屏蔽IP['+address+']成功!')
        addtime = time.strftime('%Y-%m-%d %X',time.localtime())
        public.M('firewall').add('port,ps,addtime',(address,get.ps,addtime))
        
        self.FirewallReload();
        return public.returnMsg(True,'添加成功!')
    
    
    #删除IP屏蔽
    def DelDropAddress(self,get):
        #return public.returnMsg(False,'体验服务器，禁止操作!')
        address = get.port
        id = get.id
        if self.__isFirewalld:
            public.ExecShell('firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv4 source address="'+ address +'" drop\'')
        else:
            public.ExecShell('iptables -t filte -D INPUT -s '+address+' -j DROP')
        
        public.WriteLog("防火墙管理", '解除屏蔽IP['+address+']成功!')
        public.M('firewall').where("id=?",(id,)).delete()
        
        self.FirewallReload();
        return public.returnMsg(True,'删除成功!')
    
    
    #添加放行端口
    def AddAcceptPort(self,get):
        #return public.returnMsg(False,'体验服务器，禁止操作!')
        import time
        port = get.port
        ps = get.ps
        if public.M('firewall').where("port=?",(port,)).count() > 0: return public.returnMsg(False,'您要放行的端口已存在，无需重复放行!')
        if self.__isFirewalld:
            public.ExecShell('firewall-cmd --permanent --zone=public --add-port='+port+'/tcp')
        else:
            public.ExecShell('iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport '+port+' -j ACCEPT')
        public.WriteLog("防火墙管理", '放行端口['+port+']成功!')
        addtime = time.strftime('%Y-%m-%d %X',time.localtime())
        public.M('firewall').add('port,ps,addtime',(port,ps,addtime))
        
        self.FirewallReload()
        return public.returnMsg(True,'添加成功!')
    
    
    #删除放行端口
    def DelAcceptPort(self,get):
        #return public.returnMsg(False,'体验服务器，禁止操作!')
        port = get.port
        id = get.id
        try:
            if(port == web.ctx.host.split(':')[1]): return public.returnMsg(False,'失败，不能删除当前面板端口!')
            
            if self.__isFirewalld:
                public.ExecShell('firewall-cmd --permanent --zone=public --remove-port='+port+'/tcp')
            else:
                public.ExecShell('iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport '+port+' -j ACCEPT')
            public.WriteLog("防火墙管理", '删除防火墙放行端口['+port+']成功!')
            public.M('firewall').where("id=?",(id,)).delete()
            
            self.FirewallReload()
            return public.returnMsg(True,'删除成功!')
        except:
            return public.returnMsg(False,'失败，程序给跪了!')
    
    #设置远程端口状态
    def SetSshStatus(self,get):
        #return public.returnMsg(False,'体验服务器，禁止操作!')
        version = public.readFile('/etc/redhat-release')
        if int(get['status'])==1:
            msg = 'SSH服务已停用'
            act = 'stop'
        else:
            msg = 'SSH服务已启动'
            act = 'start'
        
        
        if version.find(' 7.') != -1:
            public.ExecShell("systemctl "+act+" sshd.service")
        else:
            public.ExecShell("/etc/init.d/sshd "+act)
        
        public.WriteLog("防火墙管理", msg)
        return public.returnMsg(True,'操作成功!')

        
    
    
    #设置ping
    def SetPing(self,get):
        if get.status == '1':
            get.status = '0';
        else:
            get.status = '1';
        filename = '/etc/sysctl.conf'
        conf = public.readFile(filename)
        if conf.find('net.ipv4.icmp_echo') != -1:
            rep = u"net\.ipv4\.icmp_echo.*"
            conf = re.sub(rep,'net.ipv4.icmp_echo_ignore_all='+get.status,conf)
        else:
            conf += "\nnet.ipv4.icmp_echo_ignore_all="+get.status
            
        
        public.writeFile(filename,conf)
        public.ExecShell('sysctl -p')
        return public.returnMsg(True,'操作成功!') 
        
    
    
    #改远程端口
    def SetSshPort(self,get):
        #return public.returnMsg(False,'体验服务器，禁止操作!')
        port = get.port
        if int(port) < 22 or int(port) > 65535: return public.returnMsg(False,'端口范围必需在22-65535之间!');
        ports = ['21','25','80','443','8080','888','8888'];
        if port in ports: return public.returnMsg(False,'指定端口为常用端口，请换一个试试!');
        
        file = '/etc/ssh/sshd_config'
        conf = public.readFile(file)
        
        rep = "#*Port\s+([0-9]+)\s*\n"
        conf = re.sub(rep, "Port "+port+"\n", conf)
        public.writeFile(file,conf)
        
        if self.__isFirewalld:
            public.ExecShell('firewall-cmd --permanent --zone=public --add-port='+port+'/tcp')
            public.ExecShell('setenforce 0');
            public.ExecShell('sed -i "s#SELINUX=enforcing#SELINUX=disabled#" /etc/selinux/config');
            public.ExecShell("systemctl restart sshd.service")
        else:
            public.ExecShell('iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport '+port+' -j ACCEPT')
            public.ExecShell("/etc/init.d/sshd restart")
        
        self.FirewallReload()
        public.M('firewall').where("ps=?",('SSH远程管理服务',)).setField('port',port)
        public.WriteLog("防火墙管理", "改SSH端口为["+port+"]成功!")
        return public.returnMsg(True,'修改成功!') 
    
    #取SSH信息
    def GetSshInfo(self,get):
        file = '/etc/ssh/sshd_config'
        conf = public.readFile(file)
        rep = "#*Port\s+([0-9]+)\s*\n"
        port = re.search(rep,conf).groups(0)[0]
        version = public.readFile('/etc/redhat-release')
        if version.find(' 7.') != -1:
            status = public.ExecShell("systemctl status sshd.service | grep 'dead'")
        else:
            status = public.ExecShell("/etc/init.d/sshd status | grep 'stopped'")
            
#        return status;
        if len(status[0]) > 3: 
            status = False
        else:
            status = True
        isPing = True
        try:
            file = '/etc/sysctl.conf'
            conf = public.readFile(file)
            rep = "net\.ipv4\.icmp_echo_ignore_all\s*=\s*([0-9]+)"
            tmp = re.search(rep,conf).groups(0)[0]
            if tmp == '1': isPing = False
        except:
            isPing = True
        
        
        
        data = {}
        data['port'] = port
        data['status'] = status
        data['ping'] = isPing
        return data
        
    