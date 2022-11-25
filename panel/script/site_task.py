#coding: utf-8
import os,sys,time,re,json
os.chdir('/www/server/panel/')
sys.path.insert(0,"class/")
import public

#设置用户状态
def SetStatus(get):
    msg = public.getMsg('OFF')
    if get.status != '0': msg = public.getMsg('ON')
    try:
        id = get['id']
        username = get['username']
        status = get['status']
        runPath = '/www/server/pure-ftpd/bin'
        if int(status)==0:
            public.ExecShell(runPath + '/pure-pw usermod ' + username + ' -r 1')
        else:
            public.ExecShell(runPath + '/pure-pw usermod ' + username + " -r ''")
        FtpReload()
        public.M('ftps').where("id=?",(id,)).setField('status',status)
        public.WriteLog('TYPE_FTP','FTP_STATUS', (msg,username))
        return public.returnMsg(True, 'SUCCESS')
    except Exception as ex:
        public.WriteLog('TYPE_FTP','FTP_STATUS_ERR', (msg,username,str(ex)))
        return public.returnMsg(False,'FTP_STATUS_ERR',(msg,))

def FtpReload():
    runPath = '/www/server/pure-ftpd/bin'
    public.ExecShell(runPath + '/pure-pw mkdb /www/server/pure-ftpd/etc/pureftpd.pdb')


def flush_ssh_log():
    """
    @name 更新ssh日志
    """
    try:
        import PluginLoader
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

oldEdate = public.readFile('data/edate.pl')
if not oldEdate: oldEdate = '0000-00-00'
mEdate = time.strftime('%Y-%m-%d',time.localtime())
edateSites = public.M('sites').where('edate>? AND edate<? AND (status=? OR status=?)',('0000-00-00',mEdate,1,u'正在运行')).field('id,name').select()
import panelSite
siteObject = panelSite.panelSite()
for site in edateSites:
    get = public.dict_obj()
    get.id = site['id']
    get.name = site['name']
    siteObject.SiteStop(get)

    bind_ftp = public.M('ftps').where('pid=?',get.id).find()
    if bind_ftp:
        get = public.dict_obj()
        get.id = bind_ftp['id']
        get.username = bind_ftp['name']
        get.status = '0'
        SetStatus(get)
oldEdate = mEdate
public.writeFile('/www/server/panel/data/edate.pl',mEdate)

# 更新ssh日志
flush_ssh_log()


#未参加用户体验改进计划的不提交统计信息
if public.get_improvement():
    import PluginLoader
    PluginLoader.start_total()

