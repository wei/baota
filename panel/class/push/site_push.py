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
os.chdir(panelPath)
sys.path.append("class/")
import public,db,time,html,panelPush
import config

try:
    from BTPanel import cache
except :
    from cachelib import SimpleCache
    cache = SimpleCache()

class site_push:

    __push = None
    __push_model = ['dingding','weixin','mail','sms','wx_account','feishu']
    __conf_path =  "{}/class/push/push.json".format(panelPath)
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
        #证书到期提醒
        item = self.__push.format_push_data()
        item['cycle'] = 30
        item['type'] = 'ssl'
        item['push'] = self.__push_model
        item['title'] = '网站SSL到期提醒'
        item['helps'] = ['SSL到期提醒一天只发送一次']
        data.append(item)

        #网站到期提醒
        item = self.__push.format_push_data(push = ['dingding','weixin','mail'])
        item['cycle'] = 15
        item['type'] = 'site_endtime'
        item['title'] = '网站到期提醒'
        item['helps'] = ['网站到期提醒一天只发送一次']
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
            if m_type in ['endtime','ssl','site_endtime']:
                m_cycle.append('剩余{}天时，每天1次'.format(data[skey]['cycle']))

            if len(m_cycle) > 0:
                result[skey]['m_cycle'] = ''.join(m_cycle)
        return result



    def set_push_config(self,get):
        """
        @name 设置推送配置
        """
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
        elif pdata['type'] in ['panel_login']:
            p_module = pdata['module'].split(',')
            if len(p_module) > 1:
                return public.returnMsg(False,'面板登录告警只支持配置一个告警方式.')

            if not pdata['status']:
                return public.returnMsg(False,'不支持暂停面板登录告警，如需暂停请直接删除.')

            import config
            c_obj = config.config()

            args = public.dict_obj()
            args.type = pdata['module'].strip()

            res = c_obj.set_login_send(args)
            if not res['status']: return res

        elif pdata['type'] in ['ssh_login']:

            p_module = pdata['module'].split(',')
            if len(p_module) > 1:
                return public.returnMsg(False,'SSH登录告警只支持配置一个告警方式.')

            if not pdata['status']:
                return public.returnMsg(False,'不支持暂停SSH登录告警，如需暂停请直接删除.')

            import ssh_security
            c_obj = ssh_security.ssh_security()

            args = public.dict_obj()
            args.type = pdata['module'].strip()

            res = c_obj.set_login_send(args)
            if not res['status']: return res

        elif pdata['type'] in ['ssh_login_error']:

            res = public.get_ips_area(['127.0.0.1'])
            if 'status' in res:
                return res

        elif pdata['type'] in ['panel_safe_push']:
            pdata['interval'] = 30

        if is_create: data[module][id] = pdata
        public.set_module_logs('site_push_ssl','set_push_config',1)
        return data

    def del_push_config(self,get):
        """
        @name 删除推送记录
        @param get
            id = 告警记录标识
            module = 告警模块, site_push,panel_push
        """
        id = get.id
        module = get.name

        data = self.__push.get_push_list(get)
        info = data[module][id]
        if id in ['panel_login']:

            c_obj = config.config()
            args = public.dict_obj()
            args.type = info['module'].strip()
            res = c_obj.clear_login_send(args)
            public.print_log(json.dumps(res))
            if not res['status']: return res
        elif id in ['ssh_login']:

            import ssh_security
            c_obj = ssh_security.ssh_security()
            res = c_obj.clear_login_send(None)

            if not res['status']: return res

        try:
            data = self.__push._get_conf()
            del data[module][id]
            public.writeFile(self.__conf_path,json.dumps(data))
        except: pass
        return public.returnMsg(True, '删除成功.')


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
        stime = time.time()
        result = {'index': stime}

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
        elif data['type'] in ['site_endtime']:

            if stime < data['index'] + 86400:
                return public.returnMsg(False,"一天推送一次，跳过.")

            mEdate = public.format_date(format='%Y-%m-%d',times = stime + 86400 * int(data['cycle']))
            web_list = public.M('sites').where('edate>? AND edate<? AND (status=? OR status=?)',('0000-00-00',mEdate,1,u'正在运行')).field('id,name,edate').select()

            if len(web_list) > 0:
                for m_module in data['module'].split(','):
                    if m_module == 'sms': continue

                    s_list = ['>即将到期：<font color=#ff0000>{} 个站点</font>'.format(len(web_list))]
                    for x in web_list:
                        s_list.append(">网站：{}  到期：{}".format(x['name'],x['edate']))

                    sdata = public.get_push_info('宝塔面板网站到期提醒',s_list)
                    result[m_module] = sdata
                return result

        elif data['type'] in ['panel_pwd_endtime']:
            if stime < data['index'] + 86400:
                return public.returnMsg(False,"一天推送一次，跳过.")

            import config
            c_obj = config.config()
            res = c_obj.get_password_config(None)

            if res['expire'] > 0 and res['expire_day'] < data['cycle']:
                for m_module in data['module'].split(','):
                    if m_module == 'sms': continue

                    s_list = [">告警类型：登录密码即将过期",">剩余天数：<font color=#ff0000>{}  天</font>".format(res['expire_day'])]
                    sdata = public.get_push_info('宝塔面板密码到期提醒',s_list)
                    result[m_module] = sdata
                return result
        elif data['type'] in ['clear_bash_history']:
            stime = time.time()

            result = {'index': stime}

        elif data['type'] in ['panel_bind_user_change']:
            #面板绑定帐号发生变更
            uinfo = public.get_user_info()

            user_str = public.md5(uinfo['username'])
            old_str = public.get_cache_func(data['type'])['data']
            if not old_str:
                public.set_cache_func(data['type'],user_str)
            else:
                if user_str != old_str:

                    for m_module in data['module'].split(','):
                        if m_module == 'sms': continue

                        s_list = [">告警类型：面板绑定帐号变更",">当前绑定帐号：{}****{}".format(uinfo['username'][:3],uinfo['username'][-4:])]
                        sdata = public.get_push_info('面板绑定帐号变更提醒',s_list)
                        result[m_module] = sdata

                    public.set_cache_func(data['type'],user_str)
                    return result

        elif data['type'] in ['panel_safe_push']:
            #面板安全告警

            s_list = []
            #面板登录用户安全
            t_add,t_del,total = self.get_records_calc('login_user_safe',public.M('users'))
            if t_add > 0 or t_del > 0:
                s_list.append(">登录用户变更：<font color=#ff0000>总 {} 个，新增 {} 个 ，删除 {} 个</font>.".format(total,t_add,t_del))

            #面板日志发生删除
            t_add,t_del,total = self.get_records_calc('panel_logs_safe',public.M('logs'),1)
            if t_del > 0:
                s_list.append(">面板日志发生删除，删除条数：<font color=#ff0000>{} 条</font>".format(t_del))

            debug_str = '关闭'
            debug_status = 'False'
            #面板开启开发者模式告警
            if os.path.exists('{}/data/debug.pl'.format(public.get_panel_path())):
                debug_status = 'True'
                debug_str = '开启'

            skey = 'panel_debug_safe'
            tmp = public.get_cache_func(skey)['data']
            if not tmp:
                public.set_cache_func(skey,debug_status)
            else:
                if str(debug_status) != tmp:
                    s_list.append(">面板开发者模式发生变更，当前状态：{}".format(debug_str))
                    public.set_cache_func(skey,debug_status)

            #面板开启api告警
            api_str = 'False'
            s_path = '{}/config/api.json'.format(public.get_panel_path())
            if os.path.exists(s_path):
                api_str = public.readFile(s_path).strip()
                if not api_str: api_str = 'False'

            api_str = public.md5(api_str)
            skey = 'panel_api_safe'
            tmp = public.get_cache_func(skey)['data']
            if not tmp:
                public.set_cache_func(skey,api_str)
            else:
                if api_str != tmp:
                    s_list.append(">面板API配置发生改变，请及时确认是否本人操作.")
                    public.set_cache_func(skey,api_str)


            #面板用户名和密码发生变更
            find = public.M('users').where('id=?',(1,)).find()

            if find:
                skey = 'panel_user_change_safe'
                user_str = public.md5(find['username']) + '|' + public.md5(find['password'])
                tmp = public.get_cache_func(skey)['data']
                if not tmp:
                    public.set_cache_func(skey,user_str)
                else:
                    if user_str != tmp:
                        s_list.append(">面板登录帐号或密码发生变更")
                        public.set_cache_func(skey,user_str)


            if len(s_list) > 0:
                sdata = public.get_push_info('宝塔面板安全告警',s_list)
                for m_module in data['module'].split(','):
                    if m_module == 'sms': continue
                    result[m_module] = sdata

                return result

        elif data['type'] in ['panel_oneav_push']:
            #微步在线木马扫描提醒
            sfile = '{}/plugin/oneav/oneav_main.py'.format(public.get_panel_path())
            if not os.path.exists(sfile): return

            _obj = public.get_script_object(sfile)
            _main = getattr(_obj,'oneav_main',None)
            if not _main: return

            args = public.dict_obj()
            args.p = 1
            args.count = 1000

            f_list = []
            s_day = public.getDate(format='%Y-%m-%d')

            for line in _main().get_logs(args):

                #未检测到当天日志，跳出
                if public.format_date(times=line['time']).find(s_day) == -1:
                    break
                if line['file'] in f_list: continue

                f_list.append(line['file'])

            if not f_list: return

            for m_module in data['module'].split(','):
                if m_module == 'sms': continue

                s_list = [">告警类型：木马检测告警",">通知内容：<font color=#ff0000>发现疑似木马文件 {} 个</font>".format(len(f_list)),">文件列表：[{}]".format('、'.join(f_list))]
                sdata = public.get_push_info('宝塔面板木马检测告警',s_list)
                result[m_module] = sdata
            return result

        elif data['type'] in ['panel_update']:

            #面板更新提醒
            if stime < data['index'] + 86400:
                return public.returnMsg(False,"一天推送一次，跳过.")

            s_url = '{}/api/panel/updateLinux'
            if public.get_os('windows'): s_url = '{}/api/wpanel/updateWindows'
            s_url = s_url.format('https://www.bt.cn')

            try:
                res = json.loads(public.httpPost(s_url,{}))
                if not res: return public.returnMsg(False,"获取更新信息失败.")
            except:pass

            n_ver = res['version']
            if res['is_beta']:
                n_ver = res['beta']['version']

            if public.version() != n_ver:
                for m_module in data['module'].split(','):
                    if m_module == 'sms': continue

                    s_list = [">通知类型：面板版本更新",">当前版本：{} ".format(public.version()),">最新版本：{}".format(n_ver)]
                    sdata = public.get_push_info('面板更新提醒',s_list)
                    result[m_module] = sdata
                return result
        elif data['type'] in ['ssh_login_error']:

            #登录失败次数
            import PluginLoader

            args = public.dict_obj()
            args.model_index = 'safe'
            args.count = data['count']
            args.p = 1
            res = PluginLoader.module_run("syslog","get_ssh_error",args)
            if 'status' in res:
                return

            if type(res) == list:
                last_info = res[data['count'] -1]
                if public.to_date(times=last_info['time']) >= time.time() - data['cycle'] * 60:
                    for m_module in data['module'].split(','):
                        if m_module == 'sms': continue

                        s_list = [">通知类型：SSH登录失败告警",">告警内容：<font color=#ff0000>{} 分钟内登录失败超过 {} 次</font> ".format(data['cycle'],data['count'])]
                        sdata = public.get_push_info('SSH登录失败告警',s_list)
                        result[m_module] = sdata
                    return result

        return public.returnMsg(False,"未达到阈值，跳过.")


    def get_records_calc(self,skey,table,stype = 0):
        '''
            @name 获取指定表数据是否发生改变
            @param skey string 缓存key
            @param table db 表对象
            @param stype int 0:计算总条数 1:只计算删除
            @return array
                total int 总数

        '''
        total_add = 0
        total_del = 0

        #获取当前总数和最大索引值
        u_count = table.count()
        u_max =  table.order('id desc').getField('id')

        n_data = {'count': u_count,'max': u_max}
        tmp = public.get_cache_func(skey)['data']
        if not tmp:
            public.set_cache_func(skey,n_data)
        else:
            n_data = tmp

            #检测上一次记录条数是否被删除
            pre_count =  table.where('id<=?',(n_data['max'])).count()
            if stype == 1:
                if pre_count < n_data['count']: #有数据被删除，记录被删条数
                    total_del += n_data['count'] - pre_count

                n_count =  u_max - pre_count  #上次记录后新增的条数
                n_idx = u_max - n_data['max']  #上次记录后新增的索引差
                if n_count < n_idx:
                    total_del += n_idx - n_count
            else:

                if pre_count < n_data['count']: #有数据被删除，记录被删条数
                    total_del += n_data['count'] - pre_count
                elif pre_count > n_data['count']:
                    total_add += pre_count - n_data['count']

                t1_del = 0
                t1_add = 0
                n_count =  u_count - pre_count  #上次记录后新增的条数

                if u_max > n_data['max']:
                    n_idx = u_max - n_data['max']  #上次记录后新增的索引差
                    if n_count < n_idx: t1_del = n_idx - n_count

                #新纪录除开删除，全部计算为新增
                t1_add = n_count - t1_del
                if t1_add > 0: total_add += t1_add

                total_del += t1_del

            public.set_cache_func(skey,{'count': u_count,'max': u_max})
        return total_add,total_del,u_count

    def __check_endtime(self,siteName,cycle,project_type = ''):
        """
        @name 检测到期时间
        @param siteName str 网站名称
        @param cycle int 提前提醒天数
        @param project_type str 网站类型
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

                    sdata['sm_type'] = 'ssl_end|宝塔面板SSL到期提醒'
                    sdata['sm_args'] = public.check_sms_argv({
                        'name':public.get_push_address(),
                        'website':public.push_argv(clist[0]["siteName"]),
                        'time':clist[0]["notAfter"],
                        'total':len(clist)
                    })
                else:
                    s_list = ['>即将到期：<font color=#ff0000>{} 张</font>'.format(len(clist))]
                    for x in clist:
                        s_list.append(">网站：{}  到期：{}".format(x['siteName'],x['notAfter']))

                    sdata = public.get_push_info('宝塔面板SSL到期提醒',s_list)

                result[m_module] = sdata
        return result



