#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 宝塔软件(http:#bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: hwliang <hwl@bt.cn>
# +-------------------------------------------------------------------

import public,os,sys,db,time,json,re
from BTPanel import session,cache,json_header
from flask import request,redirect,g

class userlogin:
    limit_expire_time = 0
    def request_post(self,post):
        if not hasattr(post, 'username') or not hasattr(post, 'password'):
            return public.returnJson(False,'LOGIN_USER_EMPTY'),json_header

        self.error_num(False)
        if self.limit_address('?') < 1: return public.returnJson(False,'您多次登录失败,暂时禁止登录,请等待{}秒后重试!'.format(int(self.limit_expire_time - time.time()))),json_header
        post.username = post.username.strip()
        format_error = '参数格式错误'
        # 核验用户名密码格式
        post.username = public.rsa_decrypt(post.username)
        if len(post.username) != 32:
            return public.returnMsg(False,format_error),json_header

        post.password = public.rsa_decrypt(post.password)
        if len(post.password) != 32:
            return public.returnMsg(False,format_error),json_header

        if not re.match(r"^\w+$",post.username): return public.returnMsg(False,format_error),json_header
        if not re.match(r"^\w+$",post.password): return public.returnMsg(False,format_error),json_header
        last_login_token = session.get('last_login_token',None)
        if not last_login_token:
            public.WriteLog('TYPE_LOGIN','LOGIN_ERR_CODE',('****','****',public.GetClientIp()))
            return public.returnJson(False,"验证失败，请刷新页面重新登录!"),json_header

        public.chdck_salt()
        sql = db.Sql()
        userInfo = None
        user_plugin_file = '{}/users_main.py'.format(public.get_plugin_path('users'))
        if os.path.exists(user_plugin_file):
            user_list = sql.table('users').field('id,username,password,salt').select()
            for u_info in user_list:
                if public.md5(public.md5(u_info['username'] + last_login_token)) == post.username:
                    userInfo = u_info
        else:
            userInfo = sql.table('users').where('id=?',1).field('id,username,password,salt').find()


        if 'code' in session:
            if session['code'] and not 'is_verify_password' in session:
                if not hasattr(post, 'code'): return public.returnJson(False,'验证码不能为空!'),json_header
                if not re.match(r"^\w+$",post.code): return public.returnJson(False,'CODE_ERR'),json_header
                if not public.checkCode(post.code):
                    public.WriteLog('TYPE_LOGIN','LOGIN_ERR_CODE',('****','****',public.GetClientIp()))
                    return public.returnJson(False,'CODE_ERR'),json_header
        try:
            if not userInfo:
                public.WriteLog('TYPE_LOGIN','LOGIN_ERR_PASS',('****','******',public.GetClientIp()))
                num = self.limit_address('+')
                if not num: return public.returnJson(False,'您多次登录失败,暂时禁止登录,请等待{}秒后重试!'.format(int(self.limit_expire_time - time.time()))),json_header
                return public.returnJson(False,'用户名或密码错误，<span style="color:red;">请刷新页面重试</span>，您还可以重试[{}]次'.format(num)),json_header

            if userInfo and not userInfo['salt']:
                public.chdck_salt()
                userInfo = sql.table('users').where('id=?',(userInfo['id'],)).field('id,username,password,salt').find()

            password = public.md5(post.password.strip() + userInfo['salt'])
            s_username = public.md5(public.md5(userInfo['username'] + last_login_token))
            if s_username != post.username or userInfo['password'] != password:
                public.WriteLog('TYPE_LOGIN','LOGIN_ERR_PASS',('****','******',public.GetClientIp()))
                num = self.limit_address('+')
                if not num: return public.returnJson(False,'您多次登录失败,暂时禁止登录,请等待{}秒后重试!'.format(int(self.limit_expire_time - time.time()))),json_header
                return public.returnJson(False,'LOGIN_USER_ERR',(str(num),)),json_header
            _key_file = "/www/server/panel/data/two_step_auth.txt"

            # 密码过期检测
            if sys.path[0] != 'class/': sys.path.insert(0,'class/')
            if not public.password_expire_check():
                session['password_expire'] = True

            #登陆告警
            #public.run_thread(public.login_send_body,("账号密码",userInfo['username'],public.GetClientIp(),str(int(request.environ.get('REMOTE_PORT')))))
            # public.login_send_body("账号密码",userInfo['username'],public.GetClientIp(),str(request.environ.get('REMOTE_PORT')))
            if hasattr(post,'vcode'):
                if not re.match(r"^\d+$",post.vcode): return public.returnJson(False,'验证码格式错误'),json_header
                if self.limit_address('?',v="vcode") < 1: return public.returnJson(False,'您多次验证失败，禁止10分钟'),json_header
                import pyotp
                secret_key = public.readFile(_key_file)
                if not secret_key:
                    return public.returnJson(False, "没有找到key,请尝试在命令行关闭谷歌验证后在开启"),json_header
                t = pyotp.TOTP(secret_key)
                result = t.verify(post.vcode)
                if not result:
                    if public.sync_date(): result = t.verify(post.vcode)
                    if not result:
                        num = self.limit_address('++',v="vcode")
                        return public.returnJson(False, '验证失败，您还可以尝试[{}]次!'.format(num)), json_header
                now = int(time.time())
                public.run_thread(public.login_send_body,("账号密码",userInfo['username'],public.GetClientIp(),str(int(request.environ.get('REMOTE_PORT')))))
                public.writeFile("/www/server/panel/data/dont_vcode_ip.txt",json.dumps({"client_ip":public.GetClientIp(),"add_time":now}))
                self.limit_address('--',v="vcode")
                self.set_cdn_host(post)
                return self._set_login_session(userInfo)

            acc_client_ip = self.check_two_step_auth()

            if not os.path.exists(_key_file) or acc_client_ip:
                public.run_thread(public.login_send_body,("账号密码",userInfo['username'],public.GetClientIp(),str(int(request.environ.get('REMOTE_PORT')))))
                self.set_cdn_host(post)
                return self._set_login_session(userInfo)
            self.limit_address('-')
            session['is_verify_password'] = True
            return "1"
        except Exception as ex:
            stringEx = str(ex)
            if stringEx.find('unsupported') != -1 or stringEx.find('-1') != -1:
                public.ExecShell("rm -f /tmp/sess_*")
                public.ExecShell("rm -f /www/wwwlogs/*log")
                public.ServiceReload()
                return public.returnJson(False,'USER_INODE_ERR'),json_header
            public.WriteLog('TYPE_LOGIN','LOGIN_ERR_PASS',('****','******',public.GetClientIp()))
            num = self.limit_address('+')
            if not num: return public.returnJson(False,'您多次登录失败,暂时禁止登录,请等待{}秒后重试!'.format(int(self.limit_expire_time - time.time()))),json_header
            return public.returnJson(False,'LOGIN_USER_ERR',(str(num),)),json_header

    def request_tmp(self,get):
        try:
            if not hasattr(get,'tmp_token'): return public.returnJson(False,'错误的参数!'),json_header
            if len(get.tmp_token) == 48:
                return self.request_temp(get)
            if len(get.tmp_token) != 64: return public.returnJson(False,'错误的参数!'),json_header
            if not re.match(r"^\w+$",get.tmp_token):return public.returnJson(False,'错误的参数!'),json_header

            save_path = '/www/server/panel/config/api.json'
            data = json.loads(public.ReadFile(save_path))
            if not 'tmp_token' in data or not 'tmp_time' in data: return public.returnJson(False,'验证失败!'),json_header
            if (time.time() - data['tmp_time']) > 120: return public.returnJson(False,'过期的Token'),json_header
            if get.tmp_token != data['tmp_token']: return public.returnJson(False,'错误的Token'),json_header
            userInfo = public.M('users').where("id=?",(1,)).field('id,username').find()
            session['login'] = True
            session['username'] = userInfo['username']
            session['tmp_login'] = True
            session['uid'] = userInfo['id']
            ids=public.WriteLog('TYPE_LOGIN','LOGIN_SUCCESS',(userInfo['username'],public.GetClientIp()+ ":" + str(request.environ.get('REMOTE_PORT'))))
            public.cache_set(public.GetClientIp() + ":" + str(request.environ.get('REMOTE_PORT')), ids)
            self.limit_address('-')
            cache.delete('panelNum')
            cache.delete('dologin')
            session['session_timeout'] = time.time() + public.get_session_timeout()
            del(data['tmp_token'])
            del(data['tmp_time'])
            public.writeFile(save_path,json.dumps(data))
            self.set_request_token()
            self.login_token()
            self.set_cdn_host(get)
            return redirect('/')
        except:
            return public.returnJson(False,'登录失败,' + public.get_error_info()),json_header


    def request_temp(self,get):
        try:
            if len(get.__dict__.keys()) > 2: return '存在无意义参数!'
            if not hasattr(get,'tmp_token'): return '错误的参数!'
            if len(get.tmp_token) != 48: return '错误的参数!'
            if not re.match(r"^\w+$",get.tmp_token):return '错误的参数!'
            skey = public.GetClientIp() + '_temp_login'
            if not public.get_error_num(skey,10): return '连续10次验证失败，禁止1小时'

            s_time = int(time.time())
            if public.M('temp_login').where('state=? and expire>?',(0,s_time)).field('id,token,salt,expire').count()==0:
                public.set_error_num(skey)
                return '验证失败2!'

            data = public.M('temp_login').where('state=? and expire>?',(0,s_time)).field('id,token,salt,expire').find()
            if not data:
                public.set_error_num(skey)
                return '验证失败!'
            if not isinstance(data,dict):
                public.set_error_num(skey)
                return '验证失败!'
            r_token = public.md5(get.tmp_token + data['salt'])
            if r_token != data['token']:
                public.set_error_num(skey)
                return '验证失败!'
            public.set_error_num(skey,True)
            userInfo = public.M('users').where("id=?",(1,)).field('id,username').find()
            session['login'] = True
            session['username'] = '临时({})'.format(data['id'])
            session['tmp_login'] = True
            session['tmp_login_id'] = str(data['id'])
            session['tmp_login_expire'] = time.time() + 3600
            session['uid'] = data['id']
            sess_path = 'data/session'
            if not os.path.exists(sess_path):
                os.makedirs(sess_path,384)
            public.writeFile(sess_path + '/' + str(data['id']),'')
            login_addr = public.GetClientIp()+ ":" + str(request.environ.get('REMOTE_PORT'))
            ids=public.WriteLog('TYPE_LOGIN','LOGIN_SUCCESS',(userInfo['username'],login_addr))
            public.cache_set(public.GetClientIp()+ ":" + str(request.environ.get('REMOTE_PORT')),ids)
            public.M('temp_login').where('id=?',(data['id'],)).update({"login_time":s_time,'state':1,'login_addr':login_addr})
            self.limit_address('-')
            cache.delete('panelNum')
            cache.delete('dologin')
            session['session_timeout'] = time.time() + public.get_session_timeout()
            self.set_request_token()
            self.login_token()
            self.set_cdn_host(get)
            public.run_thread(public.login_send_body("临时授权",userInfo['username'],public.GetClientIp(),str(request.environ.get('REMOTE_PORT'))))
            return redirect('/')
        except:
            public.print_log(public.get_error_info(),'ERROR')
            return '登录失败，登录过程发生错误'


    def login_token(self):
        import config
        config.config().reload_session()

    def request_get(self,get):
        '''
            @name 验证登录页面请求权限
            @author hwliang
            @return False | Response
        '''
        # 获取标题
        if not 'title' in session: session['title'] = public.getMsg('NAME')

        # 验证是否使用限制的域名访问
        domain_check = public.check_domain_panel()
        if domain_check: return domain_check

        # 验证是否使用限制的IP地址访问
        ip_check = public.check_ip_panel()
        if ip_check: return ip_check

        # 验证是否已经登录
        if 'login' in session:
            if session['login'] == True:
                return redirect('/')

        # 复位验证码
        if not 'code' in session:
            session['code'] = False

        # 记录错误次数
        self.error_num(False)

    #生成request_token
    def set_request_token(self):
        html_token_key = public.get_csrf_html_token_key()
        session[html_token_key] = public.GetRandomString(48)
        session[html_token_key.replace("https_","")] = public.GetRandomString(48)
        #session['client_hash'] = public.get_client_hash()


    def set_cdn_host(self,get):
        try:
            if not 'cdn_url' in get: return True
            plugin_path = 'plugin/static_cdn'
            if not os.path.exists(plugin_path): return True
            cdn_url = public.get_cdn_url()
            if not cdn_url or cdn_url == get.cdn_url: return True
            public.set_cdn_url(get.cdn_url)
        except:
            return False

    #防暴破
    def error_num(self,s = True):
        nKey = 'panelNum'
        num = cache.get(nKey)
        if not num:
            cache.set(nKey,1)
            num = 1
        if s: cache.inc(nKey,1)
        if num > 6: session['code'] = True

    #IP限制
    def limit_address(self,type,v=""):
        clientIp = public.GetClientIp()
        numKey = 'limitIpNum_' + v + clientIp
        limit = 5
        outTime = 300
        try:
            #初始化
            num1 = cache.get(numKey)
            if not num1:
                cache.set(numKey,0,outTime)
                num1 = 0

            self.limit_expire_time = cache.get_expire_time(numKey)

            #计数
            if type == '+':
                cache.inc(numKey,1)
                self.error_num()
                session['code'] = True
                return limit - (num1+1)

            #计数验证器
            if type == '++':
                cache.inc(numKey,1)
                self.error_num()
                session['code'] = False
                return limit - (num1+1)

            #清空
            if type == '-':
                cache.delete(numKey)
                session['code'] = False
                return 1

            #清空验证器
            if type == '--':
                cache.delete(numKey)
                session['code'] = False
                return 1
            return limit - num1
        except:
            return limit

    # 登录成功设置session
    def _set_login_session(self,userInfo):
        try:
            session['login'] = True
            session['username'] = userInfo['username']
            session['uid'] = userInfo['id']
            session['login_user_agent'] = public.md5(request.headers.get('User-Agent',''))
            ids=public.WriteLog('TYPE_LOGIN','LOGIN_SUCCESS',(userInfo['username'],public.GetClientIp()+ ":" + str(request.environ.get('REMOTE_PORT'))))
            public.cache_set(public.GetClientIp()+ ":" + str(request.environ.get('REMOTE_PORT')),ids)
            self.limit_address('-')
            cache.delete('panelNum')
            cache.delete('dologin')
            session['session_timeout'] = time.time() + public.get_session_timeout()
            if 'last_login_token' in session: del(session['last_login_token'])
            self.set_request_token()
            self.login_token()
            login_type = 'data/app_login.pl'
            if os.path.exists(login_type):
                os.remove(login_type)
            try:
                default_pl = "{}/default.pl".format(public.get_panel_path())
                public.writeFile(default_pl,"********")
            except:
                pass
            return public.returnJson(True,'LOGIN_SUCCESS'),json_header
        except Exception as ex:
            stringEx = str(ex)
            if stringEx.find('unsupported') != -1 or stringEx.find('-1') != -1:
                public.ExecShell("rm -f /tmp/sess_*")
                public.ExecShell("rm -f /www/wwwlogs/*log")
                public.ServiceReload()
                return public.returnJson(False,'USER_INODE_ERR'),json_header
            public.WriteLog('TYPE_LOGIN','LOGIN_ERR_PASS',('****','******',public.GetClientIp()))
            num = self.limit_address('+')
            return public.returnJson(False,'LOGIN_USER_ERR',(str(num),)),json_header


    # 检查是否需要进行二次验证
    def check_two_step_auth(self):
        dont_vcode_ip_info = public.readFile("/www/server/panel/data/dont_vcode_ip.txt")
        acc_client_ip = False
        if dont_vcode_ip_info:
            dont_vcode_ip_info = json.loads(dont_vcode_ip_info)
            ip = dont_vcode_ip_info["client_ip"] == public.GetClientIp()
            now = int(time.time())
            v_time = now - int(dont_vcode_ip_info["add_time"])
            if ip and v_time < 86400:
                acc_client_ip = True
        return acc_client_ip

    # 清理多余SESSION数据
    def clear_session(self):
        try:
            session_file = '/dev/shm/session.db'
            if not os.path.exists(session_file): return False
            s_size = os.path.getsize(session_file)
            if s_size < 1024 * 512: return False
            if s_size > 1024 * 1024 * 10:
                from BTPanel import sdb
                if os.path.exists(session_file): os.remove(session_file)
                sdb.create_all()
                if not os.path.exists(session_file):
                    public.writeFile('/www/server/panel/data/reload.pl','True')
                    return False
            return True
        except:
            return False

