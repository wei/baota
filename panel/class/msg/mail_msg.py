#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2020 宝塔软件(http://www.bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 沐落 <cjx@bt.cn>
# | Author: lx
# | 消息通道邮箱模块
# +-------------------------------------------------------------------

import os, sys, public, base64, json, re
import sys, os
panelPath = "/www/server/panel"
os.chdir(panelPath)
sys.path.insert(0,panelPath + "/class/")
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

class mail_msg:
    __module_name = None
    __default_pl = "{}/data/default_msg_channel.pl".format(panelPath)

    __mail_send_conf = '/www/server/panel/data/stmp_mail.json'
    __mail_receive_conf = '/www/server/panel/data/mail_list.json'
    __mail_config = None
    def __init__(self):
        self.__mail_config = {}
        if os.path.exists('data/stmp_mail.json'):
            self.__mail_config['send'] = json.loads(public.readFile(self.__mail_send_conf))

        if os.path.exists('data/mail_list.json'):
            self.__mail_config['receive'] = json.loads(public.readFile(self.__mail_receive_conf))

        if not 'send' in self.__mail_config: self.__mail_config['send'] = {}
        if not 'receive' in self.__mail_config: self.__mail_config['receive'] = {}

        if 'qq_mail' not in self.__mail_config['send'] or 'qq_stmp_pwd' not in self.__mail_config['send'] or 'hosts' not in self.__mail_config['send']:  self.__mail_config = None

        self.__module_name = self.__class__.__name__.replace('_msg','')

    def __get_default_channel(self):
        """
        @获取默认消息通道
        """
        try:
            if public.readFile(self.__default_pl) == self.__module_name:
                return True
        except:pass
        return False

    def get_version_info(self,get):
        """
        获取版本信息
        """
        data = {}
        data['ps'] = '宝塔邮箱消息通道，用于接收面板消息推送'
        data['version'] = '1.1'
        data['date'] = '2022-08-10'
        data['author'] = '宝塔'
        data['title'] = '邮箱'
        data['help'] = 'http://www.bt.cn'
        return data

    def get_config(self,get):
        """
        获取QQ邮箱配置
        """
        data = {}
        if self.__mail_config:
            data = self.__mail_config
            if "send" in data:
                if not os.path.exists(self.__mail_send_conf):
                    public.writeFile(self.__mail_send_conf,json.dumps(data["send"]))
            if "receive" in data:
                if not os.path.exists(self.__mail_receive_conf):
                    public.writeFile(self.__mail_receive_conf, json.dumps(data["receive"]))

            data['default'] = self.__get_default_channel()
        return data

    def set_config(self,get):
        """
        设置邮箱配置
        @send 带有此参数表示设置发送者设置
            @qq_mail 发送者邮箱
            @qq_stmp_pwd 发送者密码
            @hosts 发送stmp
            @发送端口port

        @mails 接收者配置，一行一个（如：111@qq.com\n222@qq.com）
        """

        if not self.__mail_config:
            self.__mail_config = {'send':{},'receive':{}}

        if hasattr(get, 'send'):
            if not hasattr(get, 'qq_mail') or not hasattr(get, 'qq_stmp_pwd') or not hasattr(get, 'hosts') or not hasattr(get, 'port'):  return public.returnMsg(False, '请填写完整信息')
            mail_config = {
                "qq_mail": get.qq_mail.strip(),
                "qq_stmp_pwd": get.qq_stmp_pwd.strip(),
                "hosts": get.hosts.strip(),
                "port": get.port
            }
            self.__mail_config['send'] = mail_config
            public.writeFile(self.__mail_send_conf, json.dumps(mail_config))
        else:
            if not hasattr(get, 'mails'):  return public.returnMsg(False, '至少填写一个接收者邮箱.')
            arrs = get.mails.strip().split('\n')
            if len(arrs) == 0 : return public.returnMsg(False, '至少填写一个接收者邮箱.')
            self.__mail_config['receive'] = arrs
            public.writeFile(self.__mail_receive_conf,json.dumps(arrs))

        self.send_msg("宝塔测试邮件")
        return public.returnMsg(True, '邮箱配置成功.')

    def send_test_msg(self):
        pass


    def get_send_msg(self,msg):
        """
        @name 处理md格式
        """
        try:
            title = '宝塔告警通知'
            if msg.find("####") >= 0:
                msg = msg.replace("\n\n","<br>").strip()
                try:
                    title = re.search(r"####(.+)", msg).groups()[0]
                except:pass
        except:pass
        return msg,title

    def send_msg(self,msg , title = '宝塔面板消息推送',to_email = None):
        """
        邮箱发送
        @msg 消息正文
        @title 消息标题
        @to_email 发送给谁，默认发送所有人
        """
        if not self.__mail_config : return public.returnMsg(False,'未正确配置邮箱信息。')

        if not 'port' in self.__mail_config['send']: self.__mail_config['send']['port'] = 465

        receive_list = []
        if to_email:
            for x in to_email.split(','):
                receive_list.append(x)
        else:
            receive_list = self.__mail_config['receive']

        ret_msg = ''
        sucess = 0
        error = 0

        msg,title = self.get_send_msg(msg)
        res = {}
        for email in receive_list:

            try:
                data = MIMEText(msg, 'html', 'utf-8')
                data['From'] = formataddr([self.__mail_config['send']['qq_mail'], self.__mail_config['send']['qq_mail']])
                data['To'] = formataddr([self.__mail_config['send']['qq_mail'], email.strip()])
                data['Subject'] = title
                if int(self.__mail_config['send']['port']) == 465:
                    server = smtplib.SMTP_SSL(str(self.__mail_config['send']['hosts']), str(self.__mail_config['send']['port']))
                else:
                    server = smtplib.SMTP(str(self.__mail_config['send']['hosts']), str(self.__mail_config['send']['port']))
                server.login(self.__mail_config['send']['qq_mail'], self.__mail_config['send']['qq_stmp_pwd'])
                server.sendmail(self.__mail_config['send']['qq_mail'], [email.strip(), ], data.as_string())
                server.quit()
                sucess += 1
                res[email] = 1
            except :
                error += 1
                res[email] = 0
                ret_msg += "{} ->> {}\r\n".format(email,public.get_error_info())

        public.write_push_log(self.__module_name,title,res)
        if ret_msg: ret_msg = '，错误详情 ->> ' + ret_msg
        return public.returnMsg(True,'发送完成，共发送【{}】条，成功【{}】，失败【{}】{}。'.format(len(receive_list),sucess,error,ret_msg))

    def push_data(self,data):
        to_email = data.get("to_email", None)
        if 'to_user' in data:
            to_email = data['to_user']

        return self.send_msg(data['msg'],data['title'],to_email)

    def uninstall(self):
        if os.path.exists(self.__mail_send_conf):
            os.remove(self.__mail_send_conf)
        if os.path.exists(self.__mail_receive_conf):
            os.remove(self.__mail_receive_conf)