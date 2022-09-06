#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Windows面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2020 宝塔软件(https://www.bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 沐落 <cjx@bt.cn>
# +-------------------------------------------------------------------
import sys,os,time,json,re
panelPath = "/www/server/panel"
os.chdir(panelPath);
sys.path.append("class/")
import public,db,time,html,panelPush

try:
    from BTPanel import cache
except :
    from cachelib import SimpleCache
    cache = SimpleCache()


class site_push:

    __push = None
    __push_model = ['dingding','weixin','mail','sms']
    def __init__(self):
        self.__push = panelPush.panelPush()

    #-----------------------------------------------------------start 添加推送 ------------------------------------------------------
    def get_version_info(self,get):
        """
        获取版本信息
        """
        data = {}
        data['ps'] = ''
        data['version'] = '1.0'
        data['date'] = '2020-08-10'
        data['author'] = '宝塔'
        data['help'] = 'http://www.bt.cn/bbs'
        return data

    """
    @获取推送模块配置
    """
    def get_module_config(self,get):

        stype =  None
        if 'type' in get:
            stype = get.type

        data = []
        item = self.__push.format_push_data()
        item['cycle'] = 30
        item['type'] = 'ssl'
        item['push'] = self.__push_model
        item['title'] = '网站SSL到期提醒'
        item['helps'] = ['SSL到期提醒一天只发送一次']
        data.append(item)

        for data_item in data:
            if stype == data_item['type']:
                return data_item
        return data


    def get_push_cycle(self,data):
        """
        @获取执行周期
        """
        result = {}
        for skey in data:
            result[skey] = data[skey]

            m_cycle =[]
            m_type = data[skey]['type']
            if m_type in ['endtime','ssl']:
                m_cycle.append('剩余{}天时，每天1次'.format(data[skey]['cycle']))

            if len(m_cycle) > 0:
                result[skey]['m_cycle'] = ''.join(m_cycle)
        return result

    def set_push_config(self,get):
        id = get.id
        module = get.name
        pdata = json.loads(get.data)

        data = self.__push._get_conf()
        if not module in data:data[module] = {}

        is_create = True
        if pdata['type'] in ['ssl']:
            for x in data[module]:
                item = data[module][x]
                if item['type'] == pdata['type'] and item['project'] == pdata['project']:
                    is_create = False
                    data[module][x] = pdata

        if is_create: data[module][id] = pdata
        public.set_module_logs('site_push_ssl','set_push_config',1)
        return data
    #-----------------------------------------------------------end 添加推送 ------------------------------------------------------
    def get_unixtime(self,data,format = "%Y-%m-%d %H:%M:%S"):
        import time
        timeArray = time.strptime(data,format )
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    def get_site_ssl_info(self,webType,siteName,project_type = ''):
        """
        @获取SSL详细信息
        @webType string web类型 /nginx /apache /iis
        @siteName string 站点名称
        """
        result = False
        if webType in ['nginx','apache']:
            path = public.get_setup_path()
            if public.get_os('windows'):
                conf_file = '{}/{}/conf/vhost/{}.conf'.format(path,webType,siteName)
                ssl_file = '{}/{}/conf/ssl/{}/fullchain.pem'.format(path,webType,siteName)
            else:
                conf_file ='{}/vhost/{}/{}{}.conf'.format(public.get_panel_path(),webType,project_type,siteName)
                ssl_file = '{}/vhost/cert/{}/fullchain.pem'.format(public.get_panel_path(),siteName)

            conf = public.readFile(conf_file)

            if not conf:
                return result

            if conf.find('SSLCertificateFile') >=0  or conf.find('ssl_certificate') >= 0:

                if os.path.exists(ssl_file):
                    cert_data = public.get_cert_data(ssl_file)
                    return cert_data
        return result



    def get_total(self):
        return True

    def get_push_data(self,data,total):
        """
        @检测推送数据
        @data dict 推送数据
            title:标题
            project:项目
            type:类型 ssl:证书提醒
            cycle:周期 天、小时
            keys:检测键值
        """

        if data['type'] in ['ssl']:
            if time.time() < data['index'] + 86400:
                return public.returnMsg(False,"SSL一天推送一次，跳过.")

            ssl_list = []

            sql = public.M('sites')
            if data['project'] == 'all':

                #过滤单独设置提醒的网站
                n_list = []
                try:
                    push_list = self.__push._get_conf()['site_push']
                    for skey in push_list:
                        p_name = push_list[skey]['project']
                        if p_name != 'all': n_list.append(p_name)
                except : pass

                #所有正常网站
                web_list =  sql.where('status=1',()).select()
                for web in web_list:
                    project_type = ''
                    if web in n_list: continue

                    if not web['project_type'] in ['PHP']:
                        project_type = web['project_type'].lower() + '_'

                    info = self.__check_endtime(web['name'],data['cycle'],project_type)
                    if info:
                        info['siteName'] = web['name']
                        ssl_list.append(info)
            else:
                project_type = ''
                find = sql.where('name=? and status=1',(data['project'],)).find()
                if not find: return public.returnMsg(False,"没有可用的站点.")

                if not find['project_type'] in ['PHP']:
                    project_type = find['project_type'].lower() + '_'

                info = self.__check_endtime(find['name'],data['cycle'],project_type)
                if info:
                    info['siteName'] = find['name']
                    ssl_list.append(info)

            return self.__get_ssl_result(data,ssl_list)

        return public.returnMsg(False,"未达到阈值，跳过.")


    def __check_endtime(self,siteName,cycle,project_type = ''):
        """
        @检测到期时间
        """
        info = self.get_site_ssl_info(public.get_webserver(),siteName,project_type)
        if info:
            endtime = self.get_unixtime(info['notAfter'],'%Y-%m-%d')
            day = int((endtime - time.time()) / 86400)
            if day <= cycle: return info

        return False

    def __get_ssl_result(self,data,clist):
        """
        @ssl到期返回
        @data dict 推送数据
        @clist list 证书列表
        @return dict
        """
        if len(clist) == 0:
            return public.returnMsg(False,"未找到到期证书，跳过.")

        result = {'index':time.time() }
        for m_module in data['module'].split(','):
            if m_module in self.__push_model:

                sdata = self.__push.format_msg_data()
                if m_module in ['sms']:
                    sdata['sm_type'] = 'ssl_end'
                    sdata['sm_args'] = public.check_sms_argv({
                        'name':public.get_push_address(),
                        'website':public.push_argv(clist[0]["siteName"]),
                        'time':clist[0]["notAfter"],
                        'total':len(clist)
                    })
                else:
                    s_list = ['>即将到期：<font color=#ff0000>{} 张</font>'.format(len(clist))]
                    for x in clist:
                        s_list.append(">网站：{}  到期：{}  \n\n".format(x['siteName'],x['notAfter']))

                    sdata = public.get_push_info('宝塔面板SSL到期提醒',s_list)

                result[m_module] = sdata
        return result



