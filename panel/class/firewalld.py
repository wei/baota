#!/usr/bin/env python
#coding:utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2017 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

#------------------------------
# Firewalld管理类
#------------------------------
from xml.etree.ElementTree import ElementTree,Element
import os,public
class firewalld:
    __TREE = None
    __ROOT = None
    __CONF_FILE = '/etc/firewalld/zones/public.xml';

    #初始化配置文件XML对象
    def __init__(self):
        if self.__TREE: return;
        self.__TREE = ElementTree();
        self.__TREE.parse(self.__CONF_FILE);
        self.__ROOT = self.__TREE.getroot();
    
    
    #获取端口列表
    def GetAcceptPortList(self):
        mlist = self.__ROOT.getchildren();
        data = []
        for p in mlist:
            if p.tag != 'port': continue;
            tmp = p.attrib
            port = p.attrib['port'];
            data.append(tmp);
        return data;
    
    #添加端口放行
    def AddAcceptPort(self,port,pool = 'tcp'):
        #检查是否存在
        if self.CheckPortAccept(pool, port): return True;
        attr = {"protocol":pool,"port":port}
        Port = Element("port", attr);
        self.__ROOT.append(Port);
        self.Save();
        return True;
    
    #删除端口放行
    def DelAcceptPort(self,port,pool = 'tcp'):
        #检查是否存在
        if not self.CheckPortAccept(pool, port): return True;
        mlist = self.__ROOT.getchildren();
        for p in mlist:
            if p.tag != 'port': continue;
            if p.attrib['port'] == port and p.attrib['protocol'] == pool: 
                self.__ROOT.remove(p);
                self.Save();
                return True;
        return False
    
    #检查端口是否已放行
    def CheckPortAccept(self,pool,port):
        for p in self.GetAcceptPortList():
            if p['port'] == port and p['protocol'] == pool: return True;
        return False;
    
    #获取屏蔽IP列表
    def GetDropAddressList(self):
        mlist = self.__ROOT.getchildren();
        data = []
        for ip in mlist:
            if ip.tag != 'rule': continue;
            tmp = {}
            ch = ip.getchildren();
            for c in ch:
                if c.tag == 'source':
                    tmp['address'] = c.attrib['address'];
                if c.tag == 'drop': tmp['type'] = 'drop';
            data.append(tmp);
        return data;
    
    #添加IP屏蔽
    def AddDropAddress(self,address):
        #检查是否存在
        if self.CheckIpDrop(address): return True;
        attr = {"family":'ipv4'}
        rule = Element("rule", attr);
        attr = {"address":address};
        source = Element("source", attr);
        drop = Element("drop", {});
        rule.append(source);
        rule.append(drop);
        self.__ROOT.append(rule);
        self.Save();
        return True;
    
    #删除IP屏蔽
    def DelDropAddress(self,address):
        #检查是否存在
        if not self.CheckIpDrop(address): return True;
        mlist = self.__ROOT.getchildren();
        for ip in mlist:
            if ip.tag != 'rule': continue;
            ch = ip.getchildren();
            for c in ch:
                if c.tag != 'source': continue;
                if c.attrib['address'] == address: 
                    self.__ROOT.remove(ip);
                    self.Save();
                    return True;
        return False
    
    #检查IP是否已经屏蔽
    def CheckIpDrop(self,address):
        for ip in self.GetDropAddressList():
            if ip['address'] == address: return True;
        return False;
    
    #取服务状态
    def GetServiceStatus(self):
        result = public.ExecShell("systemctl status firewalld|grep '(running)'")
        if len(result) > 10: return True;
        return False;
    
    #服务控制
    def FirewalldService(self,type):
        os.system('systemctl '+type+' firewalld.service');
        return public.returnMsg(True,'SUCCESS');
    
    #保存配置
    def Save(self):
        self.format(self.__ROOT);
        self.__TREE.write(self.__CONF_FILE,'utf-8');
        os.system('firewall-cmd --reload');
        
    #整理配置文件格式
    def format(self,em,level = 0):
        i = "\n" + level*"  "
        if len(em):
            if not em.text or not em.text.strip():
                em.text = i + "  "
            for e in em:
                self.format(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        if level and (not em.tail or not em.tail.strip()):
            em.tail = i
    
if __name__ == "__main__":
    p = firewalld();
    #print p.GetAcceptPortList();
    print p.GetDropAddressList();
    