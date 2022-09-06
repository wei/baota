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

import os, sys, public, base64, json, re,requests
import sys, os
panelPath = "/www/server/panel"
os.chdir(panelPath)
sys.path.insert(0,panelPath + "/class/")
from requests.packages import urllib3
# 关闭警告
urllib3.disable_warnings()

class dingding_msg:

    conf_path = 'data/dingding.json'
    __dingding_info = None
    __module_name = None
    __default_pl = "{}/data/default_msg_channel.pl".format(panelPath)
    def __init__(self):
        try:
            self.__dingding_info = json.loads(public.readFile(self.conf_path))
            if not 'dingding_url' in self.__dingding_info or not 'isAtAll' in self.__dingding_info or not 'user' in self.__dingding_info:
                self.__dingding_info = None
        except :
            self.__dingding_info = None
        self.__module_name = self.__class__.__name__.replace('_msg','')

    def get_version_info(self,get):
        """
        获取版本信息
        """
        data = {}
        data['ps'] = '宝塔钉钉消息通道，用于接收面板消息推送'
        data['version'] = '1.2'
        data['date'] = '2022-08-10'
        data['author'] = '宝塔'
        data['title'] = '钉钉'
        data['help'] = 'http://www.bt.cn'
        return data

    def get_config(self,get):
        """
        获取钉钉配置
        """
        data = {}
        if self.__dingding_info :
            data = self.__dingding_info

            if not 'list' in data: data['list'] = {}

            data['list']['default'] = {'title':'默认','data':data['dingding_url']}
            data['default'] = self.__get_default_channel()

        return data

    def set_config(self,get):
        """
        设置钉钉配置
        @url 钉钉URL
        @atall 默认@全体成员
        @user
        """

        if not hasattr(get, 'url') or not hasattr(get, 'atall'):
            return public.returnMsg(False, '请填写完整信息')

        user = []
        status = 1
        atall = False
        if 'status' in get:  status = int(get.status)
        if 'user' in get: user = get.user.split('\n')

        if 'atall' in get and get.atall == 'True':
            atall = True

        self.__dingding_info  = {"dingding_url": get.url.strip(),"isAtAll": atall, "user":user}

        try:
            info = public.get_push_info('消息通道配置提醒',['>配置状态：<font color=#20a53a>成功</font>\n\n'])
            ret = self.send_msg(info['msg'])
        except:
            ret = self.send_msg('宝塔告警测试')

        if ret['status']:
            if 'default' in get and get['default']:
                public.writeFile(self.__default_pl, self.__module_name)

            public.writeFile(self.conf_path, json.dumps(self.__dingding_info))
            return public.returnMsg(True, '钉钉消息通道设置成功')
        else:
            return ret


    def get_send_msg(self,msg):
        """
        @name 处理md格式
        """
        try:
            title = '宝塔告警通知'
            if msg.find("####") >= 0:
                try:
                    title = re.search(r"####(.+)", msg).groups()[0]
                except:pass

        except:pass
        return msg,title

    def send_msg(self,msg,to_user = 'default'):
        """
        钉钉发送信息
        @msg 消息正文
        """

        if not self.__dingding_info :
            return public.returnMsg(False,'未正确配置钉钉信息。')

        at_info = ''
        for user in self.__dingding_info['user']:
            if re.match("^[0-9]{11,11}$",str(user)): at_info += '@'+user+' '

        msg,title = self.get_send_msg(msg)

        if at_info: msg = msg + '\n\n>' + at_info

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "服务器通知",
                "text": msg
            },
            "at": {
                "atMobiles": self.__dingding_info['user'],
                "isAtAll": self.__dingding_info['isAtAll']
            }
        }

        headers = {'Content-Type': 'application/json'}
        try:
            error,success = 0,0
            conf = self.get_config(None)['list']

            res = {}
            for to_key in to_user.split(','):
                if not to_key in conf: continue

                x = requests.post(url = conf[to_key]['data'], data=json.dumps(data), headers=headers,verify=False,timeout=10)
                if x.json()["errcode"] == 0:
                    success += 1
                    res[conf[to_key]['title']] = 1
                else:
                    error += 1
                    res[conf[to_key]['title']] = 0
                try:
                    public.write_push_log(self.__module_name,title,res)
                except:pass
            return public.returnMsg(True,'发送完成,发送成功{},发送失败{}.'.format(success,error))
        except:
            return public.returnMsg(False,'钉钉消息发送失败。 --> {}'.format(public.get_error_info()))


    def push_data(self,data):
        """
        @name 统一发送接口
        @data 消息内容
            {"module":"mail","title":"标题","msg":"内容","to_email":"xx@qq.com","sm_type":"","sm_args":{}}
        """
        return self.send_msg(data['msg'])

    def __get_default_channel(self):
        """
        @获取默认消息通道
        """
        try:
            if public.readFile(self.__default_pl) == self.__module_name:
                return True
        except:pass
        return False


    def uninstall(self):
        if os.path.exists(self.conf_path):
            os.remove(self.conf_path)