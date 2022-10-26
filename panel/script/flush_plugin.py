#coding: utf-8
import sys,os
os.chdir('/www/server/panel/')
sys.path.insert(0,"class/")
import PluginLoader
import public
import time


def flush_cache():
    '''
        @name 更新缓存
        @author hwliang
        @return void
    '''
    try:
        start_time = time.time()
        res = PluginLoader.get_plugin_list(1)
        spath = '{}/data/pay_type.json'.format(public.get_panel_path())
        public.downloadFile(public.get_url() + '/install/lib/pay_type.json',spath)
        import plugin_deployment
        plugin_deployment.plugin_deployment().GetCloudList(None)

        timeout = time.time() - start_time
        if 'ip' in res and res['ip']:
            public.print_log("缓存更新成功,耗时: %.2f 秒" % timeout)
        else:
            if isinstance(res,dict) and not 'msg' in res: res['msg'] = '连接服务器失败!'
            public.print_log("缓存更新失败: {}".format(res['msg']))
    except:
        public.print_log("缓存更新失败: {}".format(public.get_error_info()))


def flush_ssh_log():
    """
    @name 更新ssh日志
    """

    try:

        c_time = 0
        c_file ='{}/data/ssh/time.day'.format(public.get_panel_path())
        try:
            c_time = int(public.readFile(c_file))
        except:pass

        public.print_log("开始更新SSH登录日志...")
        if c_time:
            public.print_log("上次更新时间:{}".format(public.format_date(times = c_time)))

        if time.time() - c_time > 86400:
            #登录成功日志
            args = public.dict_obj()
            args.model_index = 'safe'
            args.count = 100
            args.p = 1000000
            res = PluginLoader.module_run("syslog","get_ssh_success",args)

            #登录所有登录日志
            res = PluginLoader.module_run("syslog","get_ssh_list",args)

            #登录失败日志
            res = PluginLoader.module_run("syslog","get_ssh_error",args)

            public.print_log("更新ssh日志成功")
            public.writeFile(c_file,str(int(time.time())))
        else:
            public.print_log("未超过一天,不更新ssh日志")
    except:
        public.print_log("更新ssh日志失败: {}".format(public.get_error_info()))


def flush_msg_json():
    """
    @name 更新消息json
    """
    try:
        public.print_log("开始更新消息json...")
        spath = '{}/data/msg.json'.format(public.get_panel_path())
        public.downloadFile(public.get_url() + '/linux/panel/msg/msg.json',spath)
        public.print_log("更新消息json成功")
    except:
        public.print_log("更新消息json失败: {}".format(public.get_error_info()))

if __name__ == '__main__':
    tip_date_tie = '/tmp/.fluah_time'
    if os.path.exists(tip_date_tie):
        last_time = int(public.readFile(tip_date_tie))
        timeout = time.time() - last_time
        if timeout < 600:
            print("执行间隔过短，退出 - {}!".format(timeout))
            sys.exit()
    flush_cache()
    flush_msg_json()


    flush_ssh_log()  #耗时较长，建议放到最后执行

    public.writeFile(tip_date_tie,str(int(time.time())))
