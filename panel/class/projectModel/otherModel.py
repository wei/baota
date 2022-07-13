# coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: lkq <lkq@bt.cn>
# -------------------------------------------------------------------

# ------------------------------
# 其他模型
# ------------------------------

import os, sys, re, json, shutil, psutil, time
from projectModel.base import projectBase
import public, firewalls

try:
    from BTPanel import cache
except:
    pass


class mobj:
    port = ps = ''


class main(projectBase):
    _panel_path = public.get_panel_path()
    _go_path = '/www/server/other_project'
    _log_name = '项目管理'
    _go_pid_path = '/var/tmp/other_project'
    _go_logs_path = '{}/logs'.format(_go_path)
    _go_run_scripts = '{}/scripts'.format(_go_path)
    _vhost_path = '{}/vhost'.format(_panel_path)
    _pids = None
    setupPath = '/www/server'

    def __init__(self):
        if not os.path.exists(self._go_path):
            os.makedirs(self._go_path, 493)

        if not os.path.exists(self._go_pid_path):
            public.ExecShell("mkdir -p /var/tmp/other_project/ && chmod 777 /var/tmp/other_project/")

        if not os.path.exists(self._go_logs_path):
            os.makedirs(self._go_logs_path, 493)

        if not os.path.exists(self._go_run_scripts):
            os.makedirs(self._go_run_scripts, 493)

    def get_system_user(self, get):
        '''
        @name 获取系统所有的用户
        @Author:lkq 2021-09-06
        @return list
        '''
        path = '/etc/passwd'
        user_list = public.ReadFile(path)
        resutl = []
        result2 = ["root", "www", "mysql"]
        if isinstance(user_list, str):
            user_list = user_list.split('\n')
            [resutl.append(x.split(":")[0]) for x in user_list if x.split(":")[0] != '']
            return resutl
        else:
            return result2

    # 取当前可用PHP版本
    def GetPHPVersion(self, get):
        phpVersions = ('00', 'other', '52', '53', '54', '55', '56', '70', '71', '72', '73', '74', '80')
        httpdVersion = ""
        filename = self.setupPath + '/apache/version.pl'
        if os.path.exists(filename): httpdVersion = public.readFile(filename).strip()

        if httpdVersion == '2.2': phpVersions = ('00', '52', '53', '54')
        if httpdVersion == '2.4': phpVersions = (
        '00', 'other', '53', '54', '55', '56', '70', '71', '72', '73', '74', '80')
        if os.path.exists('/www/server/nginx/sbin/nginx'):
            cfile = '/www/server/nginx/conf/enable-php-00.conf'
            if not os.path.exists(cfile): public.writeFile(cfile, '')

        s_type = getattr(get, 's_type', 0)
        data = []
        for val in phpVersions:
            tmp = {}
            checkPath = self.setupPath + '/php/' + val + '/bin/php'
            if val in ['00', 'other']: checkPath = '/etc/init.d/bt'
            if httpdVersion == '2.2': checkPath = self.setupPath + '/php/' + val + '/libphp5.so'
            if os.path.exists(checkPath):
                tmp['version'] = val
                tmp['name'] = 'PHP-' + val
                if val == '00':
                    tmp['name'] = '纯静态'

                if val == 'other':
                    if s_type:
                        tmp['name'] = '自定义'
                    else:
                        continue
                data.append(tmp)
        return data

    def get_project_find(self, project_name):
        '''
            @name 获取指定项目配置
            @author hwliang<2021-08-09>
            @param project_name<string> 项目名称
            @return dict
        '''
        project_info = public.M('sites').where('project_type=? AND name=?', ('Other', project_name)).find()
        if not project_info: return False
        project_info['project_config'] = json.loads(project_info['project_config'])
        return project_info

    def get_other_pids(self, pid):
        '''
            @name 获取其他进程pid列表
            @author hwliang<2021-08-10>
            @param pid: string<项目pid>
            @return list
        '''
        plugin_name = None
        for pid_name in os.listdir(self._go_pid_path):
            pid_file = '{}/{}'.format(self._go_pid_path, pid_name)
            s_pid = int(public.readFile(pid_file))
            if pid == s_pid:
                plugin_name = pid_name[:-4]
                break
        project_find = self.get_project_find(plugin_name)
        if not project_find: return []
        if not self._pids: self._pids = psutil.pids()
        all_pids = []
        for i in self._pids:
            try:
                p = psutil.Process(i)
                if p.cwd() == project_find['path'] and p.username() == project_find['project_config']['run_user']:
                    # if p.name() in ['node','npm','pm2']:
                    all_pids.append(i)
            except:
                continue
        return all_pids

    def get_project_pids(self, get=None, pid=None):
        '''
            @name 获取项目进程pid列表
            @author hwliang<2021-08-10>
            @param pid: string<项目pid>
            @return list
        '''
        if get: pid = int(get.pid)
        if not self._pids: self._pids = psutil.pids()
        project_pids = []

        for i in self._pids:
            try:
                p = psutil.Process(i)
            except:
                continue
            if p.ppid() == pid:
                if i in project_pids: continue
                project_pids.append(i)

        other_pids = []
        for i in project_pids:
            other_pids += self.get_project_pids(pid=i)
        if os.path.exists('/proc/{}'.format(pid)):
            project_pids.append(pid)

        all_pids = list(set(project_pids + other_pids))
        if not all_pids:
            all_pids = self.get_other_pids(pid)
        return sorted(all_pids)

    def get_project_run_state(self, get=None, project_name=None):
        '''
            @name 获取项目运行状态
            @author hwliang<2021-08-12>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @param project_name<string> 项目名称
            @return bool
        '''
        if get: project_name = get.project_name.strip()
        pid_file = "{}/{}.pid".format(self._go_pid_path, project_name)
        if not os.path.exists(pid_file): return False
        pid = int(public.readFile(pid_file))
        pids = self.get_project_pids(pid=pid)
        if not pids: return False
        return True

    def get_process_cpu_time(self, cpu_times):
        cpu_time = 0.00
        for s in cpu_times: cpu_time += s
        return cpu_time

    def get_cpu_precent(self, p):
        '''
            @name 获取进程cpu使用率
            @author hwliang<2021-08-09>
            @param p: Process<进程对像>
            @return dict
        '''
        skey = "cpu_pre_{}".format(p.pid)
        old_cpu_times = cache.get(skey)

        process_cpu_time = self.get_process_cpu_time(p.cpu_times())
        if not old_cpu_times:
            cache.set(skey, [process_cpu_time, time.time()], 3600)
            # time.sleep(0.1)
            old_cpu_times = cache.get(skey)
            process_cpu_time = self.get_process_cpu_time(p.cpu_times())

        old_process_cpu_time = old_cpu_times[0]
        old_time = old_cpu_times[1]
        new_time = time.time()
        cache.set(skey, [process_cpu_time, new_time], 3600)
        percent = round(100.00 * (process_cpu_time - old_process_cpu_time) / (new_time - old_time) / psutil.cpu_count(),
                        2)
        return percent

    def format_connections(self, connects):
        '''
            @name 获取进程网络连接信息
            @author hwliang<2021-08-09>
            @param connects<pconn>
            @return list
        '''
        result = []
        for i in connects:
            raddr = i.raddr
            if not i.raddr:
                raddr = ('', 0)
            laddr = i.laddr
            if not i.laddr:
                laddr = ('', 0)
            result.append({
                "fd": i.fd,
                "family": i.family,
                "local_addr": laddr[0],
                "local_port": laddr[1],
                "client_addr": raddr[0],
                "client_rport": raddr[1],
                "status": i.status
            })
        return result

    def get_connects(self, pid):
        '''
            @name 获取进程连接信息
            @author hwliang<2021-08-09>
            @param pid<int>
            @return dict
        '''
        connects = 0
        try:
            if pid == 1: return connects
            tp = '/proc/' + str(pid) + '/fd/'
            if not os.path.exists(tp): return connects
            for d in os.listdir(tp):
                fname = tp + d
                if os.path.islink(fname):
                    l = os.readlink(fname)
                    if l.find('socket:') != -1: connects += 1
        except:
            pass
        return connects

    def object_to_dict(self, obj):
        '''
            @name 将对象转换为字典
            @author hwliang<2021-08-09>
            @param obj<object>
            @return dict
        '''
        result = {}
        for name in dir(obj):
            value = getattr(obj, name)
            if not name.startswith('__') and not callable(value) and not name.startswith('_'): result[name] = value
        return result

    def list_to_dict(self, data):
        '''
            @name 将列表转换为字典
            @author hwliang<2021-08-09>
            @param data<list>
            @return dict
        '''
        result = []
        for s in data:
            result.append(self.object_to_dict(s))
        return result

    def get_process_info_by_pid(self, pid):
        '''
            @name 获取进程信息
            @author hwliang<2021-08-12>
            @param pid: int<进程id>
            @return dict
        '''
        process_info = {}
        try:
            if not os.path.exists('/proc/{}'.format(pid)): return process_info
            p = psutil.Process(pid)
            status_ps = {'sleeping': '睡眠', 'running': '活动'}
            with p.oneshot():
                p_mem = p.memory_full_info()
                if p_mem.uss + p_mem.rss + p_mem.pss + p_mem.data == 0: return process_info
                p_state = p.status()
                if p_state in status_ps: p_state = status_ps[p_state]
                # process_info['exe'] = p.exe()
                process_info['name'] = p.name()
                process_info['pid'] = pid
                process_info['ppid'] = p.ppid()
                process_info['create_time'] = int(p.create_time())
                process_info['status'] = p_state
                process_info['user'] = p.username()
                process_info['memory_used'] = p_mem.uss
                process_info['cpu_percent'] = self.get_cpu_precent(p)
                process_info['io_write_bytes'], process_info['io_read_bytes'] = self.get_io_speed(p)
                process_info['connections'] = self.format_connections(p.connections())
                process_info['connects'] = self.get_connects(pid)
                process_info['open_files'] = self.list_to_dict(p.open_files())
                process_info['threads'] = p.num_threads()
                process_info['exe'] = ' '.join(p.cmdline())
                return process_info
        except:
            return process_info

    def get_io_speed(self, p):
        '''
            @name 获取磁盘IO速度
            @author hwliang<2021-08-12>
            @param p: Process<进程对像>
            @return list
        '''
        skey = "io_speed_{}".format(p.pid)
        old_pio = cache.get(skey)
        if not hasattr(p,'io_counters'): return 0,0
        pio = p.io_counters()
        if not old_pio:
            cache.set(skey, [pio, time.time()], 3600)
            # time.sleep(0.1)
            old_pio = cache.get(skey)
            pio = p.io_counters()

        old_write_bytes = old_pio[0].write_bytes
        old_read_bytes = old_pio[0].read_bytes
        old_time = old_pio[1]

        new_time = time.time()
        write_bytes = pio.write_bytes
        read_bytes = pio.read_bytes

        cache.set(skey, [pio, new_time], 3600)

        write_speed = int((write_bytes - old_write_bytes) / (new_time - old_time))
        read_speed = int((read_bytes - old_read_bytes) / (new_time - old_time))

        return write_speed, read_speed

    def get_project_load_info(self, get=None, project_name=None):
        '''
            @name 获取项目负载信息
            @author hwliang<2021-08-12>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        if get: project_name = get.project_name.strip()
        load_info = {}
        pid_file = "{}/{}.pid".format(self._go_pid_path, project_name)
        if not os.path.exists(pid_file): return load_info
        pid = int(public.readFile(pid_file))
        pids = self.get_project_pids(pid=pid)
        if not pids: return load_info
        for i in pids:
            process_info = self.get_process_info_by_pid(i)
            if process_info: load_info[i] = process_info
        return load_info

    def get_ssl_end_date(self, project_name):
        '''
            @name 获取SSL信息
            @author hwliang<2021-08-09>
            @param project_name <string> 项目名称
            @return dict
        '''
        import data
        return data.data().get_site_ssl_info('other_{}'.format(project_name))

    def get_project_stat(self, project_info):
        '''
            @name 获取项目状态信息
            @author hwliang<2021-08-09>
            @param project_info<dict> 项目信息
            @return list
        '''
        project_info['project_config'] = json.loads(project_info['project_config'])
        project_info['run'] = self.get_project_run_state(project_name=project_info['name'])
        project_info['load_info'] = self.get_project_load_info(project_name=project_info['name'])
        project_info['ssl'] = self.get_ssl_end_date(project_name=project_info['name'])
        project_info['listen'] = []
        project_info['listen_ok'] = True
        if project_info['load_info']:
            for pid in project_info['load_info'].keys():
                for conn in project_info['load_info'][pid]['connections']:
                    if not conn['status'] == 'LISTEN': continue
                    if not conn['local_port'] in project_info['listen']:
                        project_info['listen'].append(conn['local_port'])
            if project_info['listen']:
                project_info['listen_ok'] = project_info['project_config']['port'] in project_info['listen']
        return project_info

    def exists_nginx_ssl(self, project_name):
        '''
            @name 判断项目是否配置Nginx SSL配置
            @author hwliang<2021-08-09>
            @param project_name: string<项目名称>
            @return tuple
        '''
        config_file = "{}/nginx/other_{}.conf".format(public.get_vhost_path(), project_name)
        if not os.path.exists(config_file):
            return False, False

        config_body = public.readFile(config_file)
        if not config_body:
            return False, False

        is_ssl, is_force_ssl = False, False
        if config_body.find('ssl_certificate') != -1:
            is_ssl = True
        if config_body.find('HTTP_TO_HTTPS_START') != -1:
            is_force_ssl = True
        return is_ssl, is_force_ssl

    def check_port_is_used(self, port, sock=False):
        '''
            @name 检查端口是否被占用
            @author hwliang<2021-08-09>
            @param port: int<端口>
            @return bool
        '''
        if not isinstance(port, int): port = int(port)
        if port == 0: return False
        project_list = public.M('sites').where('status=? AND project_type=?', (1, 'Other')).field(
            'name,path,project_config').select()
        for project_find in project_list:
            project_config = json.loads(project_find['project_config'])
            if not 'port' in project_config: continue
            if int(project_config['port']) == port: return True
        if sock: return False
        return public.check_tcp('127.0.0.1', port)

    def exists_apache_ssl(self, project_name):
        '''
            @name 判断项目是否配置Apache SSL配置
            @author hwliang<2021-08-09>
            @param project_name: string<项目名称>
            @return bool
        '''
        config_file = "{}/apache/other_{}.conf".format(public.get_vhost_path(), project_name)
        if not os.path.exists(config_file):
            return False, False

        config_body = public.readFile(config_file)
        if not config_body:
            return False, False

        is_ssl, is_force_ssl = False, False
        if config_body.find('SSLCertificateFile') != -1:
            is_ssl = True
        if config_body.find('HTTP_TO_HTTPS_START') != -1:
            is_force_ssl = True
        return is_ssl, is_force_ssl

    def set_apache_config(self, project_find):
        '''
            @name 设置Apache配置
            @author hwliang<2021-08-09>
            @param project_find: dict<项目信息>
            @return bool
        '''
        project_name = project_find['name']

        # 处理域名和端口
        ports = []
        domains = []
        for d in project_find['project_config']['domains']:
            domain_tmp = d.split(':')
            if len(domain_tmp) == 1: domain_tmp.append(80)
            if not int(domain_tmp[1]) in ports:
                ports.append(int(domain_tmp[1]))
            if not domain_tmp[0] in domains:
                domains.append(domain_tmp[0])

        config_file = "{}/apache/other_{}.conf".format(self._vhost_path, project_name)
        template_file = "{}/template/apache/other_http.conf".format(self._vhost_path)
        config_body = public.readFile(template_file)
        apache_config_body = ''

        # 旧的配置文件是否配置SSL
        is_ssl, is_force_ssl = self.exists_apache_ssl(project_name)
        if is_ssl:
            if not 443 in ports: ports.append(443)

        from panelSite import panelSite
        s = panelSite()

        # 根据端口列表生成配置
        for p in ports:
            # 生成SSL配置
            ssl_config = ''
            if p == 443 and is_ssl:
                ssl_key_file = "{vhost_path}/cert/{project_name}/privkey.pem".format(project_name=project_name,
                                                                                     vhost_path=public.get_vhost_path())
                if not os.path.exists(ssl_key_file): continue  # 不存在证书文件则跳过
                ssl_config = '''#SSL
    SSLEngine On
    SSLCertificateFile {vhost_path}/cert/{project_name}/fullchain.pem
    SSLCertificateKeyFile {vhost_path}/cert/{project_name}/privkey.pem
    SSLCipherSuite EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5
    SSLProtocol All -SSLv2 -SSLv3 -TLSv1
    SSLHonorCipherOrder On'''.format(project_name=project_name, vhost_path=public.get_vhost_path())
            else:
                if is_force_ssl:
                    ssl_config = '''#HTTP_TO_HTTPS_START
    <IfModule mod_rewrite.c>
        RewriteEngine on
        RewriteCond %{SERVER_PORT} !^443$
        RewriteRule (.*) https://%{SERVER_NAME}$1 [L,R=301]
    </IfModule>
    #HTTP_TO_HTTPS_END'''

            # 生成vhost主体配置
            apache_config_body += config_body.format(
                site_path=project_find['path'],
                server_name='{}.{}'.format(p, project_name),
                domains=' '.join(domains),
                log_path=public.get_logs_path(),
                server_admin='admin@{}'.format(project_name),
                url='http://127.0.0.1:{}'.format(project_find['project_config']['port']),
                port=p,
                ssl_config=ssl_config,
                project_name=project_name
            )
            apache_config_body += "\n"

            # 添加端口到主配置文件
            if not p in [80]:
                s.apacheAddPort(p)

        # 写.htaccess
        rewrite_file = "{}/.htaccess".format(project_find['path'])
        if not os.path.exists(rewrite_file): public.writeFile(rewrite_file, '# 请将伪静态规则或自定义Apache配置填写到此处\n')

        # 写配置文件
        public.writeFile(config_file, apache_config_body)
        return True

    def set_nginx_config(self, project_find):
        '''
            @name 设置Nginx配置
            @author hwliang<2021-08-09>
            @param project_find: dict<项目信息>
            @return bool
        '''
        project_name = project_find['name']
        ports = []
        domains = []

        for d in project_find['project_config']['domains']:
            domain_tmp = d.split(':')
            if len(domain_tmp) == 1: domain_tmp.append(80)
            if not int(domain_tmp[1]) in ports:
                ports.append(int(domain_tmp[1]))
            if not domain_tmp[0] in domains:
                domains.append(domain_tmp[0])
        listen_ipv6 = public.listen_ipv6()
        listen_ports = ''
        for p in ports:
            listen_ports += "    listen {};\n".format(p)
            if listen_ipv6:
                listen_ports += "    listen [::]:{};\n".format(p)
        listen_ports = listen_ports.strip()

        is_ssl, is_force_ssl = self.exists_nginx_ssl(project_name)
        ssl_config = ''
        if is_ssl:
            listen_ports += "\n    listen 443 ssl http2;"
            if listen_ipv6: listen_ports += "\n    listen [::]:443 ssl http2;"

            ssl_config = '''ssl_certificate    {vhost_path}/cert/{priject_name}/fullchain.pem;
    ssl_certificate_key    {vhost_path}/cert/{priject_name}/privkey.pem;
    ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    add_header Strict-Transport-Security "max-age=31536000";
    error_page 497  https://$host$request_uri;'''.format(vhost_path=self._vhost_path, priject_name=project_name)

            if is_force_ssl:
                ssl_config += '''
    #HTTP_TO_HTTPS_START
    if ($server_port !~ 443){
        rewrite ^(/.*)$ https://$host$1 permanent;
    }
    #HTTP_TO_HTTPS_END'''

        config_file = "{}/nginx/other_{}.conf".format(self._vhost_path, project_name)
        template_file = "{}/template/nginx/other_http.conf".format(self._vhost_path)

        config_body = public.readFile(template_file)
        config_body = config_body.format(
            site_path=project_find['path'],
            domains=' '.join(domains),
            project_name=project_name,
            panel_path=self._panel_path,
            log_path=public.get_logs_path(),
            url='http://127.0.0.1:{}'.format(project_find['project_config']['port']),
            host='127.0.0.1',
            listen_ports=listen_ports,
            ssl_config=ssl_config
        )

        # # 恢复旧的SSL配置
        # ssl_config = self.get_nginx_ssl_config(project_name)
        # if ssl_config:
        #     config_body.replace('#error_page 404/404.html;',ssl_config)

        rewrite_file = "{panel_path}/vhost/rewrite/other_{project_name}.conf".format(panel_path=self._panel_path,
                                                                                     project_name=project_name)
        if not os.path.exists(rewrite_file): public.writeFile(rewrite_file, '# 请将伪静态规则或自定义NGINX配置填写到此处\n')
        public.writeFile(config_file, config_body)
        return True

    def clear_nginx_config(self, project_find):
        '''
            @name 清除nginx配置
            @author hwliang<2021-08-09>
            @param project_find: dict<项目信息>
            @return bool
        '''
        project_name = project_find['name']
        config_file = "{}/nginx/other_{}.conf".format(self._vhost_path, project_name)
        if os.path.exists(config_file):
            os.remove(config_file)
        rewrite_file = "{panel_path}/vhost/rewrite/other_{project_name}.conf".format(panel_path=self._panel_path,
                                                                                     project_name=project_name)
        if os.path.exists(rewrite_file):
            os.remove(rewrite_file)
        return True

    def clear_apache_config(self, project_find):
        '''
            @name 清除apache配置
            @author hwliang<2021-08-09>
            @param project_find: dict<项目信息>
            @return bool
        '''
        project_name = project_find['name']
        config_file = "{}/apache/other_{}.conf".format(self._vhost_path, project_name)
        if os.path.exists(config_file):
            os.remove(config_file)
        return True

    def clear_config(self, project_name):
        '''
            @name 清除项目配置
            @author hwliang<2021-08-09>
            @param project_name: string<项目名称>
            @return bool
        '''
        project_find = self.get_project_find(project_name)
        if not project_find: return False
        self.clear_nginx_config(project_find)
        self.clear_apache_config(project_find)
        public.serviceReload()
        return True

    def set_config(self, project_name):
        '''
            @name 设置项目配置
            @author hwliang<2021-08-09>
            @param project_name: string<项目名称>
            @return bool
        '''
        project_find = self.get_project_find(project_name)
        if not project_find: return False
        if not project_find['project_config']: return False
        if not project_find['project_config']['bind_extranet']: return False
        if not project_find['project_config']['domains']: return False
        self.set_nginx_config(project_find)
        self.set_apache_config(project_find)
        public.serviceReload()
        return True

    def kill_pids(self, get=None, pids=None):
        '''
            @name 结束进程列表
            @author hwliang<2021-08-10>
            @param pids: string<进程pid列表>
            @return dict
        '''
        if get: pids = get.pids
        if not pids: return public.return_data(True, '没有进程')
        pids = sorted(pids, reverse=True)
        for i in pids:
            try:
                p = psutil.Process(i)
                p.kill()
            except:
                pass
        return public.return_data(True, '进程已全部结束')

    def bind_extranet(self, get):
        '''
            @name 绑定外网
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        project_name = get.project_name.strip()
        project_find = self.get_project_find(project_name)
        if not project_find: return public.return_error('项目不存在')
        if not project_find['project_config']['domains']: return public.return_error('请先到【域名管理】选项中至少添加一个域名')
        project_find['project_config']['bind_extranet'] = 1
        public.M('sites').where("id=?", (project_find['id'],)).setField('project_config',
                                                                        json.dumps(project_find['project_config']))
        self.set_config(project_name)
        public.WriteLog(self._log_name, '其他项目{}, 开启外网映射'.format(project_name))
        return public.return_data(True, '开启外网映射成功')

    def unbind_extranet(self, get):
        '''
            @name 解绑外网
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        project_name = get.project_name.strip()
        self.clear_config(project_name)
        public.serviceReload()
        project_find = self.get_project_find(project_name)
        project_find['project_config']['bind_extranet'] = 0
        public.M('sites').where("id=?", (project_find['id'],)).setField('project_config',
                                                                        json.dumps(project_find['project_config']))
        public.WriteLog(self._log_name, '其他项目{}, 关闭外网映射'.format(project_name))
        return public.return_data(True, '关闭成功')

    def restart_project(self, get):
        '''
            @name 重启项目
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        res = self.stop_project(get)
        if not res['status']: return res
        res = self.start_project(get)
        if not res['status']: return res
        return public.return_data(True, '重启成功')

    def stop_project(self, get):
        '''
            @name 停止项目
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        pid_file = "{}/{}.pid".format(self._go_pid_path, get.project_name)
        if not os.path.exists(pid_file): return public.return_error('项目未启动')
        pid = int(public.readFile(pid_file))
        pids = self.get_project_pids(pid=pid)
        if not pids: return public.return_error('项目未启动')
        self.kill_pids(pids=pids)
        if os.path.exists(pid_file): os.remove(pid_file)
        return public.return_data(True, '停止成功')

    def start_project(self, get):
        '''
            @name 启动项目
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        if not os.path.exists(self._go_pid_path):
            public.ExecShell("mkdir -p /var/tmp/gopids/ && chmod 777 /var/tmp/gopids/")
        else:
            ret = public.get_mode_and_user("/var/tmp/other_project/")
            if isinstance(ret, dict):
                if ret['mode'] != 777:
                    public.ExecShell("chmod 777 /var/tmp/other_project/")
        project_find = self.get_project_find(get.project_name)
        if not project_find: return public.returnMsg(False, '项目不存在')
        log_file = "{}/{}.log".format(self._go_logs_path, get.project_name)
        pid_file = "{}/{}.pid".format(self._go_pid_path, get.project_name)
        public.writeFile(log_file, "")
        public.set_own(log_file, project_find['project_config']['run_user'])
        project_cmd = project_find["project_config"]['project_cmd']
        if 'project_path' in project_find['project_config']:
            jar_path = project_find['project_config']['project_path']
        else:
            jar_path = '/root'
        # 启动脚本
        start_cmd = '''#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
 cd {jar_path}
nohup {project_cmd} 2>&1 >> {log_file} &
echo $! > {pid_file}'''.format(
            jar_path=jar_path,
            project_cmd=project_cmd,
            pid_file=pid_file,
            log_file=log_file,
        )
        script_file = "{}/{}.sh".format(self._go_run_scripts, get.project_name)
        # 写入启动脚本
        public.writeFile(script_file, start_cmd)
        if os.path.exists(pid_file): os.remove(pid_file)
        public.ExecShell("chown -R {}:{} {}".format(project_find['project_config']['run_user'],
                                                    project_find['project_config']['run_user'], jar_path))
        public.set_mode(script_file, 755)
        public.set_own(script_file, project_find['project_config']['run_user'])
        # 执行脚本文件
        p = public.ExecShell("bash {}".format(script_file), user=project_find['project_config']['run_user'])
        time.sleep(1)
        if not os.path.exists(pid_file):
            return public.returnMsg(False, '启动失败{}'.format(p))
        # 获取PID
        pid = int(public.readFile(pid_file))
        pids = self.get_project_pids(pid=pid)
        if not pids:
            if os.path.exists(pid_file): os.remove(pid_file)
            return public.returnMsg(False, '启动失败<br>{}'.format(public.GetNumLines(log_file, 20)))

        return public.return_data(True, '启动成功')

    def get_project_list(self, get):
        '''
            @name 获取项目列表
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''

        if not 'p' in get:  get.p = 1
        if not 'limit' in get: get.limit = 20
        if not 'callback' in get: get.callback = ''
        if not 'order' in get: get.order = 'id desc'

        if 'search' in get:
            get.project_name = get.search.strip()
            search = "%{}%".format(get.project_name)
            count = public.M('sites').where('project_type=? AND (name LIKE ? OR ps LIKE ?)',
                                            ('Other', search, search)).count()
            data = public.get_page(count, int(get.p), int(get.limit), get.callback)
            data['data'] = public.M('sites').where('project_type=? AND (name LIKE ? OR ps LIKE ?)',
                                                   ('Other', search, search)).limit(
                data['shift'] + ',' + data['row']).order(get.order).select()
        else:
            count = public.M('sites').where('project_type=?', 'Other').count()
            data = public.get_page(count, int(get.p), int(get.limit), get.callback)
            data['data'] = public.M('sites').where('project_type=?', 'Other').limit(
                data['shift'] + ',' + data['row']).order(get.order).select()

        for i in range(len(data['data'])):
            data['data'][i] = self.get_project_stat(data['data'][i])
        return data

    def project_get_domain(self, get):
        '''
            @name 获取指定项目的域名列表
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        project_id = public.M('sites').where('name=?', (get.project_name,)).getField('id')
        domains = public.M('domain').where('pid=?', (project_id,)).order('id desc').select()
        project_find = self.get_project_find(get.project_name)
        if len(domains) != len(project_find['project_config']['domains']):
            public.M('domain').where('pid=?', (project_id,)).delete()
            if not project_find: return []
            for d in project_find['project_config']['domains']:
                domain = {}
                arr = d.split(':')
                if len(arr) < 2: arr.append(80)
                domain['name'] = arr[0]
                domain['port'] = int(arr[1])
                domain['pid'] = project_id
                domain['addtime'] = public.getDate()
                public.M('domain').insert(domain)
            if project_find['project_config']['domains']:
                domains = public.M('domain').where('pid=?', (project_id,)).select()
        return domains

    def project_remove_domain(self, get):
        '''
            @name 为指定项目删除域名
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
                domain: string<域名>
            }
            @return dict
        '''
        project_find = self.get_project_find(get.project_name)
        if not project_find:
            return public.return_error('指定项目不存在')
        last_domain = get.domain
        domain_arr = get.domain.split(':')
        if len(domain_arr) == 1:
            domain_arr.append(80)

        project_id = public.M('sites').where('name=?', (get.project_name,)).getField('id')
        if len(project_find['project_config']['domains']) == 1: return public.return_error('项目至少需要一个域名')
        domain_id = public.M('domain').where('name=? AND pid=?', (domain_arr[0], project_id)).getField('id')
        if not domain_id:
            return public.return_error('指定域名不存在')
        public.M('domain').where('id=?', (domain_id,)).delete()

        if get.domain in project_find['project_config']['domains']:
            project_find['project_config']['domains'].remove(get.domain)
        if get.domain + ":80" in project_find['project_config']['domains']:
            project_find['project_config']['domains'].remove(get.domain + ":80")

        public.M('sites').where('id=?', (project_id,)).save('project_config',
                                                            json.dumps(project_find['project_config']))
        public.WriteLog(self._log_name, '从项目：{}，删除域名{}'.format(get.project_name, get.domain))
        self.set_config(get.project_name)
        return public.return_data(True, '删除域名成功')

    def project_add_domain(self, get):
        '''
            @name 为指定项目添加域名
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
                domains: list<域名列表>
            }
            @return dict
        '''
        project_find = self.get_project_find(get.project_name)
        if not project_find:
            return public.return_error('指定项目不存在')
        project_id = project_find['id']
        domains = get.domains
        success_list = []
        error_list = []
        for domain in domains:
            domain = domain.strip()
            domain_arr = domain.split(':')
            if len(domain_arr) == 1:
                domain_arr.append(80)
                domain += ':80'
            if not public.M('domain').where('name=?', (domain_arr[0],)).count():
                public.M('domain').add('name,pid,port,addtime',
                                       (domain_arr[0], project_id, domain_arr[1], public.getDate()))
                if not domain in project_find['project_config']['domains']:
                    project_find['project_config']['domains'].append(domain)
                public.WriteLog(self._log_name, '成功添加域名{}到项目{}'.format(domain, get.project_name))
                success_list.append(domain)
            else:
                public.WriteLog(self._log_name, '添加域名错误，域名{}已存在'.format(domain))
                error_list.append(domain)

        if success_list:
            public.M('sites').where('id=?', (project_id,)).save('project_config',
                                                                json.dumps(project_find['project_config']))
            self.set_config(get.project_name)

        if success_list:
            public.M('sites').where('id=?',(project_id,)).save('project_config',json.dumps(project_find['project_config']))
            self.set_config(get.project_name)
            return public.returnMsg(True,"成功添加{}个域名，失败{}个!".format(len(success_list),len(error_list)))
        return public.returnMsg(False,"成功添加{}个域名，失败{}个!".format(len(success_list),len(error_list)))

    def get_project_info(self, get):
        '''
            @name 获取指定项目信息
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        project_info = public.M('sites').where('project_type=? AND name=?', ('Other', get.project_name)).find()
        if not project_info: return public.return_error('指定项目不存在!')
        project_info = self.get_project_stat(project_info)
        return project_info

    def create_project(self, get):
        '''
            @name 创建新的项目
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
            project_name: string<项目名称>
            project_path: string<项目目录>
            project_ps: string<项目备注信息>
            bind_extranet: int<是否绑定外网> 1:是 0:否
            domains: list<域名列表> ["domain1:80","domain2:80"]  // 在bind_extranet=1时，需要填写
            is_power_on: int<是否开机启动> 1:是 0:否
            run_user: string<运行用户>
            project_cmd: string<项目执行的命令>
            port 端口号
            }
            @return dict
        '''

        project_name = get.project_name.strip()
        if not re.match("^\w+$", project_name):
            return public.return_error('项目名称格式不正确，支持字母、数字、下划线，表达式: ^[0-9A-Za-z_]$')

        if public.M('sites').where('name=? and project_type=?', (get.project_name,)).count():
            return public.return_error('指定项目名称已存在: {}'.format(get.project_name))
        # if 'project_exe' in get:get.project_path=get.project_exe
        # get.project_path = get.project_path.strip()
        if not os.path.exists(get.project_exe):
            return public.return_error('项目目录不存在: {}'.format(get.project_exe))

        # 端口占用检测
        if get.port=="":return public.return_error("请填写好端口")
        if self.check_port_is_used(get.port):
            return public.return_error('指定端口已被其它应用占用，请修改您的项目配置使用其它端口, 端口: {}'.format(get.port))
        domains = []
        if get.bind_extranet == 1:
            domains = get.domains
        for domain in domains:
            domain_arr = domain.split(':')
            if public.M('domain').where('name=?', domain_arr[0]).count():
                return public.return_error('指定域名已存在: {}'.format(domain))

        # 获取可执行文件的的根目录
        pdata = {
            'name': get.project_name,
            'path': get.project_exe,
            'ps': get.project_ps,
            'status': 1,
            'type_id': 0,
            'project_type': 'Other',
            'project_config': json.dumps(
                {
                    'ssl_path': '/www/wwwroot/java_node_ssl',
                    'project_name': get.project_name,
                    'bind_extranet': get.bind_extranet,
                    'domains': [],
                    'project_cmd': get.project_cmd,
                    'is_power_on': get.is_power_on,
                    'run_user': get.run_user,
                    'port': int(get.port),
                    'project_exe': get.project_exe
                }
            ),
            'addtime': public.getDate()
        }
        project_id = public.M('sites').insert(pdata)
        if get.bind_extranet == 1:
            format_domains = []
            for domain in domains:
                if domain.find(':') == -1: domain += ':80'
                format_domains.append(domain)
            get.domains = format_domains
            self.project_add_domain(get)
        self.set_config(get.project_name)
        public.WriteLog(self._log_name, '添加其他项目{}'.format(get.project_name))
        self.start_project(get)
        return public.return_data(True, '添加项目成功', project_id)

    def modify_project(self, get):
        '''
            @name 修改指定项目
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
            project_name: string<项目名称>
            project_path: string<项目执行目录>
            project_ps: string<项目备注信息>  可以修改
            is_power_on: int<是否开机启动> 1:是 0:否  可以修改
            run_user: string<运行用户>   可以修改
            project_cmd: string<项目执行的命令>  可以修改
            port 端口号   可以修改端口
            }
            @return dict
        '''
        project_find = self.get_project_find(get.project_name)
        if not project_find:
            return public.return_error('指定项目不存在: {}'.format(get.project_name))

        if not os.path.exists(get.project_exe):
            return public.return_error('项目目录不存在: {}'.format(get.project_exe))

        if hasattr(get, 'port'):
            if int(project_find['project_config']['port']) != int(get.port):
                if self.check_port_is_used(get.get('port/port'), True):
                    return public.return_error('指定端口已被其它应用占用，请修改您的项目配置使用其它端口, 端口: {}'.format(get.port))
                project_find['project_config']['port'] = int(get.port)
        # if hasattr(get,'project_cwd'): project_find['project_config']['project_cwd'] = get.project_cwd.strip()
        if hasattr(get, 'project_path'): project_find['project_config']['project_path'] = get.project_path.strip()
        if hasattr(get, 'is_power_on'): project_find['project_config']['is_power_on'] = get.is_power_on
        if hasattr(get, 'run_user'): project_find['project_config']['run_user'] = get.run_user.strip()
        if hasattr(get, 'project_cmd'): project_find['project_config']['project_cmd'] = get.project_cmd.strip()

        pdata = {
            'path': get.project_exe,
            'ps': get.project_ps,
            'project_config': json.dumps(project_find['project_config'])
        }

        public.M('sites').where('name=?', (get.project_name,)).update(pdata)
        self.set_config(get.project_name)
        public.WriteLog(self._log_name, '修改其他项目{}'.format(get.project_name))
        # 重启项目
        self.stop_project(get)
        self.start_project(get)
        return public.return_data(True, '修改项目成功,并重启')

    def remove_project(self, get):
        '''
            @name 删除指定项目
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                project_name: string<项目名称>
            }
            @return dict
        '''
        project_find = self.get_project_find(get.project_name)
        if not project_find:
            return public.return_error('指定项目不存在: {}'.format(get.project_name))

        self.stop_project(get)
        self.clear_config(get.project_name)
        public.M('domain').where('pid=?', (project_find['id'],)).delete()
        public.M('sites').where('name=?', (get.project_name,)).delete()
        pid_file = "{}/{}.pid".format(self._go_pid_path, get.project_name)
        if os.path.exists(pid_file): os.remove(pid_file)
        script_file = '{}/{}.sh'.format(self._go_run_scripts, get.project_name)
        if os.path.exists(script_file): os.remove(script_file)
        log_file = '{}/{}.log'.format(self._go_logs_path, get.project_name)
        if os.path.exists(log_file): os.remove(log_file)
        public.WriteLog(self._log_name, '删除其他项目{}'.format(get.project_name))
        return public.return_data(True, '删除项目成功')

    # xss 防御
    def xsssec(self,text):
        return text.replace('<', '&lt;').replace('>', '&gt;')


    def get_project_log(self, get):
        '''
        @name 取项目日志
        @author lkq<2021-08-27>
        @param  domain 域名
        @param  project_name 项目名称
        @return string
        '''
        project_info = self.get_project_find(get.project_name.strip())
        if not project_info: return public.returnMsg(False, '项目不存在')
        log_file = "{}/{}.log".format(self._go_logs_path, get.project_name)
        if not os.path.exists(log_file): return public.returnMsg(False, '日志文件不存在')
        return public.returnMsg(True, self.xsssec(public.GetNumLines(log_file,1000)))

    def auto_run(self):
        '''
        @name 开机自动启动
        '''
        # 获取数据库信息
        project_list = public.M('sites').where('project_type=?', ('Other',)).field('name,path,project_config').select()
        get = public.dict_obj()
        success_count = 0
        error_count = 0
        for project_find in project_list:
            project_config = json.loads(project_find['project_config'])
            if project_config['is_power_on'] in [0, False, '0', None]: continue
            project_name = project_find['name']
            project_state = self.get_project_run_state(project_name=project_name)
            if not project_state:
                get.project_name = project_name
                result = self.start_project(get)
                if not result['status']:
                    error_count += 1
                    error_msg = '自动启动其他项目[' + project_name + ']失败!'
                    public.WriteLog(self._log_name, error_msg)
                    public.print_log(error_msg, 'ERROR')
                else:
                    success_count += 1
                    success_msg = '自动启动其他项目[' + project_name + ']成功!'
                    public.WriteLog(self._log_name, success_msg)
                    public.print_log(success_msg, 'INFO')
        if (success_count + error_count) < 1: return False
        dene_msg = '共需要启动{}个其他项目，成功{}个，失败{}个'.format(success_count + error_count, success_count, error_count)
        public.WriteLog(self._log_name, dene_msg)
        public.print_log(dene_msg, 'INFO')
        return True