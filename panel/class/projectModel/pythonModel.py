# coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: baozi <lkq@bt.cn>
# -------------------------------------------------------------------

# ------------------------------
# Python模型
# ------------------------------

import os, re, json, time, shutil, psutil
from typing import Union, Dict, TextIO, Optional, Tuple, List
import ssh_terminal
from projectModel.base import projectBase
import public

try:
    from BTPanel import cache
except:
    pass


class main(projectBase):
    _panel_path = public.get_panel_path()
    _project_path = '/www/server/python_project'
    _log_name = '项目管理'
    _pyv_path = '/www/server/pyporject_evn'
    _tmp_path = '/var/tmp'
    _logs_path = '{}/vhost/logs'.format(_project_path)
    _project_logs = '/www/wwwlogs/python'
    _vhost_path = '{}/vhost'.format(_panel_path)
    _pip_source = "https://mirrors.aliyun.com/pypi/simple/"
    __log_split_script_py = public.get_panel_path() + '/script/run_log_split.py'
    _project_conf = {}
    _pids = None

    def __init__(self):
        if not os.path.exists(self._project_path):
            os.makedirs(self._project_path, mode=0o755)

        if not os.path.exists(self._logs_path):
            os.makedirs(self._logs_path, mode=0o777)

        if not os.path.exists(self._project_logs):
            os.makedirs(self._project_logs, mode=0o777)

        if not os.path.exists(self._pyv_path):
            os.makedirs(self._pyv_path, mode=0o755)

    def get_cloud_version(self, get=None) -> Union[list, dict]:
        """从云端获取Python版本
        @author baozi <202-02-22>
        @param:
        @return  list[str] : 可用python版本列表
        """
        res = public.httpGet(public.get_url() + '/install/plugin/pythonmamager/pyv.txt')
        if not res:
            return {"status": False, "msg": "请求不到官方python版本数据，请切换节点试一试"}
        text = res.split('\n')
        pyv_data = {"v": text, "time": int(time.time())}
        public.writeFile('{}/pyproject_v.txt'.format(self._tmp_path), json.dumps(pyv_data))
        return text

    def get_pyv_can_install(self):
        """获取那些版本的python能安装
        @author baozi <202-02-22>
        @param:
        @return  list[str] : 可用python版本列表
        """
        pyv_data = public.readFile('{}/pyproject_v.txt'.format(self._tmp_path))
        if not pyv_data:
            return self.get_cloud_version()
        try:
            res: dict = json.loads(pyv_data)
            if time.time() - res["time"] > 60 * 60 * 24 * 30:
                return self.get_cloud_version()
            else:
                return res["v"]
        except:
            return self.get_cloud_version()
    
    def __get_python_v(self, get):
        """获取已安装的Python版本
        @author baozi <202-02-22>
        @param:
            get  (dict ):  无请求信息
        @return  list[str] : 已安装python版本列表
        """
        path = '{}/versions'.format(self._pyv_path)
        if not os.path.exists(path):
            return []
        data = os.listdir(path)
        return data

    def GetCloudPython(self, get):
        """显示可以安装的python版本

        @author baozi <202-02-22>
        @param:
            get  (dict ):  无请求信息
        @return  msg : 返回Python版本的安装情况
        """
        data = self.get_pyv_can_install()
        existpy = self.__get_python_v(get)
        if "status" in data:
            error = '<br>错误：连接宝塔官网异常，请按照以下方法排除问题后重试：<br>解决方法：<a target="_blank" class="btlink" href="https://www.bt.cn/bbs/thread-87257-1-1.html">https://www.bt.cn/bbs/thread-87257-1-1.html</a><br>'
            raise public.PanelError(error)
        v = []
        l = {}
        for i in data:
            i = i.strip()
            if re.match(r"[\d\.]+", i):
                v.append(i)
        for i in v:
            if i.split()[0] in existpy:
                l[i] = "1"
            else:
                l[i] = "0"

        l = sorted(l.items(), key=lambda d: [int(i) for i in d[0].split('.')], reverse=True)
        for i, v in enumerate(l):
            l[i] = {"version": v[0], "installed": v[1]}
        return public.return_data(True, l)
    
    def GetPythonVersion(self, get):
        """获取已安装的Python版本
        @author baozi <202-02-22>
        @param:
            get  (dict ):  无请求信息
        @return  list[str] : 已安装python版本列表
        """
        return self.__get_python_v(get)

    def InstallPythonV(self, get):
        """安装新的Python
        @author baozi <202-02-22>
        @param:
            get  (dict): 请求信息,包含版本号
        @return  msg :  是否安装成功
        """
        can_install = self.get_pyv_can_install()
        if get.version not in can_install:
            return public.returnMsg(False, '该版本尚未支持，请到论坛反馈。')
        if get.version in self.__get_python_v(None):
            return public.returnMsg(False, "该版本已安装过，无需重复安装")
        _sh = f"bash {self._panel_path}/script/get_python.sh {get.version} {public.get_url()}&> {self._logs_path}/py.log"
        public.ExecShell(_sh)
        path = f'{self._pyv_path}/versions/{get.version}/bin/'
        if "2.7" in get.version:
            path = path + "python"
        else:
            path = path + "python3"
        if os.path.exists(path):
            # public.writeFile(f"{self._logs_path}/py.log", "")
            return public.returnMsg(True, "安装成功！")
        return public.returnMsg(False, "安装失败！{}".format(path))

    def install_pip(self, vpath, pyv):
        """安装包管理工具pip
        @author baozi <202-02-22>
        @param:
            vpath  (str):  Python环境地址
            pyv  (str):  Python版本
        @return
        """
        if [int(i) for i in pyv.split('.')] > [3, 6]:
            pyv = "3.6"

        _sh = f'bash {self._panel_path}/script/get_python.sh {pyv} {public.get_url()} {vpath} &>> {self._logs_path}/py.log'
        public.ExecShell(_sh)

    def copy_pyv(self, get):
        """复制python环境到指定项目
        @author baozi <202-02-22>
        @param:
            get  ( dict ):   请求信息
        @return
        """
        import files
        if not os.path.exists(get.vpath):
            self.__write_log(get.pjname.strip(), "开始复制环境 {}".format(get.vpath))

        get.sfile = f"{self._pyv_path}/versions/{get.version}"
        get.dfile = get.vpath
        self.__write_log(get.pjname.strip(), (files.files().CopyFile(get))["msg"])
        import pwd
        res = pwd.getpwnam('www')
        uid = res.pw_uid
        gid = res.pw_gid
        os.chown(get.dfile, uid, gid)
        self.install_pip(get.vpath, get.version)
        if not os.path.exists(get.vpath):
            return False
        else:
            self.__write_log(get.pjname.strip(), "环境制作成功")
            return True

    def __write_log(self, pjname, msg):
        """写日志
        @author baozi <202-02-22>
        @param:
            pjname ( str ) : 项目名称
            msg  ( dict ):  需要写入的日志信息
        @return
        """
        path = f"{self._logs_path}/{pjname}.log"
        localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        if not os.path.exists(path):
            public.ExecShell("touch %s" % path)
        public.writeFile(path, localtime + "\n" + msg + "\n", "a+")

    def RemovePythonV(self, get):
        """卸载虚拟环境的Python
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息，包含要删除的版本信息
        @return  msg : 是否删除成功
        """
        v = get.version.split()[0]
        # projects = public.M('sites').where("project_type=?", ("Python",)).field('name,project_config').select()
        exist_pv = self.__get_python_v(get)
        if v not in exist_pv:
            return public.returnMsg(False, "没有安装该Python版本")
        # use_p= []
        # for project in projects:
        #     if json.loads(project["project_config"])["version"] == v:
        #         use_p.append(project["name"])
        # if use_p:
        #     return public.returnMsg(False, "该版本正在被项目[{}]使用，请先删除项目后再卸载".format(project["name"]))

        self.remove_python(v)
        insatalled = os.listdir(f'{self._pyv_path}/versions')
        if v in insatalled:
            return public.returnMsg(False, "卸载Python失败，请再试一次")
        return public.returnMsg(True, "卸载Python成功")

    def remove_python(self, pyv):
        """删除安装目录
        @author baozi <202-02-22>
        @param:
            pyv  ( str ):  版本号
        @return
        """
        py_path = f'{self._pyv_path}/versions/{pyv}'
        if os.path.exists(py_path):
            import shutil
            shutil.rmtree(py_path)

    def __get_project_conf(self, name_id):
        """获取项目的配置信息
        @author baozi <202-02-22>
        @param:
            name_id  ( str|id ):  项目名称或者项目id
        @return dict_onj: 项目信息
        """
        if isinstance(name_id, int):
            _id = name_id
            _name = None
        else:
            _id = None
            _name = name_id
        data = public.M('sites').where('project_type=? AND (name = ? OR id = ?)', ('Python', _name, _id)).field(
            'name,path,status,project_config').find()
        if not data: return False
        project_conf = json.loads(data['project_config'])
        if not os.path.exists(data["path"]):
            self.__stop_project(project_conf)
        project_conf["status"] = data["status"]
        return project_conf

        # 获取已经安装的模块

    def GetPackages(self, get):
        conf = self.__get_project_conf(get.name.strip())
        if not conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")

        piplist = []
        l = public.ExecShell("%s list" % self._get_vp_pip(conf["vpath"]))[0].split("\n")
        public.print_log(l)
        for d in l[2:]:
            try:
                p, v = d.split()
                piplist.append((p, v))
            except:
                pass
        return piplist

    def MamgerPackage(self, get):
        """安装与卸载虚拟环境模块
        @author baozi <202-02-22>
        @param:
            get  ( 请求信息 ):  包含操作act,pjname,p,v
        @return  msg : 操作成功与否
        """
        conf = self.__get_project_conf(get.name.strip())
        if not conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")
        vp = conf["vpath"]
        if get.act == "install":
            _sh = f"%s install -i {self._pip_source} %s"
            pkg = get.p if not get.v else f"{get.p}=={get.v}"
            public.ExecShell(_sh % (self._get_vp_pip(vp), pkg))
            pkgs = public.ExecShell("%s list" % self._get_vp_pip(vp))[0]
            _pkg = get.p.lower()
            if '_' in _pkg:
                _pkg = _pkg.replace("_", "-")
            if get.p.lower() in pkgs.lower() or _pkg in pkgs.lower():
                return public.returnMsg(True, "安装成功")
            else:
                return public.returnMsg(False, "安装失败")
        else:
            if get.p == "pip":
                return public.returnMsg(False, "PIP不能卸载。。。。")
            _sh = "echo 'y' | %s uninstall %s"
            public.ExecShell(_sh % (self._get_vp_pip(vp), get.p))
            packages = public.ExecShell("%s list" % self._get_vp_pip(vp))[0]
            if get.p not in packages.lower():
                return public.returnMsg(True, "卸载成功")
            else:
                return public.returnMsg(False, "卸载失败")

    def _get_vp_pip(self, vpath):
        """获取虚拟环境下的pip
        @author baozi <202-02-22>
        @param:
            vpath  ( str ):  虚拟环境位置
        @return  str : pip 位置
        """
        if os.path.exists('{}/bin/pip'.format(vpath)):
            return '{}/bin/pip'.format(vpath)
        else:
            return '{}/bin/pip3'.format(vpath)

    def _get_vp_python(self, vpath):
        """获取虚拟环境下的python解释器
        @author baozi <202-02-22>
        @param:
            vpath  ( str ):  虚拟环境位置
        @return  str : python解释器 位置
        """
        if os.path.exists('{}/bin/python'.format(vpath)):
            return '{}/bin/python'.format(vpath)
        else:
            return '{}/bin/python3'.format(vpath)

        # 检查输入参数

    def __check_args(self, get):
        """检查输入的参数
        @author baozi <202-02-22>
        @param:
            get  ( dict ):   创建Python项目时的请求
        @return  dict : 规范化的请求参数
        """
        test_rule = {
            "pjname": lambda x: (3 < len(x.encode("utf-8")) < 15, '项目名称必须大于3小于15个字符串'),
            "port": self.__check_port,
            "path": lambda x: (os.path.exists(x), "项目路径不存在"),
            "version": lambda x: (x in self.__get_python_v(None), 'Python版本未安装'),
            "xsgi": lambda x: (x in ("asgi", "wsgi"), "网络协议版本选择错误"),
            "framework": lambda x: (x in ("django", "flask", "sanic", "python"), '框架选择错误'),
            "stype": lambda x: (x in ("uwsgi", "gunicorn", "python"), '运行方式选择错误'),
            "rfile": lambda x: (True, ''),
            # "auto_run": lambda x: (x in ("1", "0", True, False, 1, 0), '自动运行选择错误'),
            "parm": lambda x: (True, ''),
            # "logpath": lambda x: (True, ''),
        }
        values = {}
        errormsg, error_idx = '', 1
        if get.get("stype") == "python":
            get.xsgi = "wsgi"
        for k, r in test_rule.items():
            v = get.get(k).strip()
            flag, msg = r(v)
            if not flag:
                errormsg += f"{msg}<br>"
                error_idx += 1
            else:
                values[k] = v
        if errormsg:
            return False, public.returnMsg(False, errormsg[:-4])

        # values["auto_run"] = True if values["auto_run"] in (1, "1", True) else False
        values["auto_run"] = False
        values["path"] = values["path"] if values["path"][-1] != '/' else values["path"][:-1]
        if "logpath" not in values:
            values["logpath"] = os.path.join(self._project_logs, values["pjname"])
            # else:
        #     values["logpath"] = values["logpath"] if values["logpath"][-1] != '/' else values["logpath"][:-1]
        #     if os.path.isfile(values["logpath"]):
        #         return False, public.returnMsg(False, "日志路径不应当是一个文件")

        # 对run_file 进行检查
        if "user" not in get:
            values["user"] = "www"
        if not values["rfile"].startswith(values["path"]):
            return False, public.returnMsg(False, "启动文件不在项目目录下")
        if not (values["rfile"][-3:] == ".py" and os.path.isfile(values["rfile"])):
            return False, public.returnMsg(False, "启动文件不是python扩展文件")
        if values["framework"] == "djnago":
            if not (values["rfile"][-7:] == "wsgi.py" and values["xsgi"] == "wsgi") or \
                    (values["rfile"][-7:] == "asgi.py" and values["xsgi"] == "asgi") or values["stype"] == "python":
                return False, public.returnMsg(False,
                                               "在django框架下，您选择的启动文件可能有问题。django官方推荐使用wsgi.py 或 asgi.py 作为部署时的启动文件")
        if "requirement_path" in get:
            requirement_path = get.requirement_path.strip()
            if not os.path.isfile(requirement_path):
                return False, public.returnMsg(False, "未找到指定依赖包文件-requirement.txt")
            else:
                values["requirement_path"] = requirement_path
        else:
            values["requirement_path"] = None

        return True, values

    def __check_port(self, port):
        """检查端口是否合格
        @author baozi <202-02-22>
        @param:
            port  ( str ):  端口号
        @return   [bool,msg]: 结果 + 错误信息
        """
        try:
            if int(port) < 65535 and int(port) > 0:
                data = public.ExecShell("ss  -nultp|grep ':%s '" % port)[0]
                if data:
                    return False, "该端口已经被占用"
            else:
                return False, "请输入正确的端口范围 1 < 端口 < 65535"
        except ValueError:
            return False, "端口请输入整数"
        else:
            return True, None

    def __check_project_exist(self, pjname=None):
        """检查项目是否存在
        @author baozi <202-02-22>
        @param:
            pjname  ( str ):  项目名称
            path  ( str ):  项目路径
        @return  bool : 返回验证结果
        """
        data = public.M('sites').where('name=?', (pjname,)).field('id').find()
        return bool(data)

    def __check_project_path_exist(self, path=None):
        """检查项目地址是否存在
        @author baozi <202-02-22>
        @param:
            pjname  ( str ):  项目名称
            path  ( str ):  项目路径
        @return  bool : 返回验证结果
        """
        data = public.M('sites').where('project_type=? AND path=? ', ('Python', path)).field('id').find()
        return bool(data)

    def __check_feasibility(self, values):
        """检查用户部署方式的可行性
        @author baozi <202-02-22>
        @param:
            values  ( dict ):  用户输入参数的规范化数据
        @return  msg
        """
        version: str = values["version"]
        xsgi = values["xsgi"]
        framework = values["framework"]
        stype = values["stype"]
        if framework == "sanic" and [int(i) for i in version.split('.')[:2]] < [3, 7]:
            return "sanic框架不支持python3.7以下的版本"
        if xsgi == "asgi" and stype == "uwsgi":
            return "uWsgi服务框架不支持asgi协议"

    def __install_module(self, project_conf, log_path):
        """批量安装模块
        @author baozi <202-02-22>
        @param:
            vpath  ( str ):  虚拟环境位置
            requirement_path  ( str ):   requirement文件位置
        @return
        """
        self.__write_log(project_conf["pjname"], "安装依赖包")
        # _sh = f"{self._get_vp_pip(project_conf['vpath'])} install -i {self._pip_source} -r {project_conf['requirement_path']}"
        # res = public.ExecShell(_sh)[0]
        # self.__write_log(project_conf["pjname"], res)

        _sh = f"nohup {self._get_vp_python(project_conf['vpath'])} -m pip install -i {self._pip_source} -r {project_conf['requirement_path']} &>> {log_path}"
        public.ExecShell(_sh)

    def __install_run_server(self, values):
        """安装服务器部署应用
        @author baozi <202-02-22>
        @param:
            values  ( dict ):  用户输入信息
        @return bool : 返回是否安装成功
        """
        self.__write_log(values["pjname"], "开始安装服务器应用")
        _sh = f"{self._get_vp_pip(values['vpath'])} install -i {self._pip_source} %s"
        _log = ''
        res = public.ExecShell(_sh % ("uwsgi",))
        _log += res[0]
        res = public.ExecShell(_sh % ("gunicorn",))
        _log += res[0]
        res = public.ExecShell(_sh % ("uvicorn",))
        _log += res[0]

        self.__write_log(values["pjname"], _log)

    def CreateProject(self, get):
        """创建Python项目
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息
        @return  test : 创建情况
        """
        # 检查输入参数
        flag, values = self.__check_args(get)
        if not flag:
            return values
        if self.__check_project_exist(values["pjname"]):
            return public.returnMsg(False, "项目已经存在")
        if self.__check_project_path_exist(values["path"]):
            return public.returnMsg(False, "该路径已存在其他项目")
        # 检查服务器部署的可行性
        msg = self.__check_feasibility(values)
        if msg: return public.returnMsg(False, msg)
        # 制作虚拟环境
        vpath = self._pyv_path + '/' + public.md5(values["pjname"]) + "_venv"
        vpath = vpath.replace("//", "/")
        get.vpath, values["vpath"] = vpath, vpath
        flag = self.copy_pyv(get)
        if not flag:
            logfile = f"{self._logs_path}/{values['pjname']}.log"
            if os.path.exists(logfile):
                os.remove(logfile)
            return public.returnMsg(False, "虚拟环境部署失败，请检查Python版本")

        self.__write_log(values["pjname"], "站点创建成功")
        # 安装服务器部署应用
        self.__install_run_server(values, )
        # 安装依赖包
        if values["requirement_path"] is not None:
            self.__install_module(values, f"{self._logs_path}/{values['pjname']}.log")
        # 准备启动的配置文件
        self.__write_log(values["pjname"], "开始制作配置文件")
        self.__prepare_start_conf(values)
        self.__write_log(values["pjname"], "配置文件已输出")
        # 尝试启动
        flag = self.__start_project(values)
        # 将站点记录下来
        for i in ("install_module", "requirement_path"):
            if i in values: values.pop(i)
        # 默认不开启映射，不绑定外网
        values["domains"], values["bind_extranet"] = [], 0
        p_data = {
            "name": values["pjname"],
            "path": values["path"],
            "ps": values["pjname"],
            "status": int(values["status"]),
            'type_id': 0,
            "project_type": "Python",
            "addtime": public.getDate(),
            "project_config": json.dumps(values)
        }
        res = public.M("sites").insert(p_data)
        if isinstance(res, str) and res.startswith("error"):
            return public.returnMsg(False, "项目记录失败，请联系官方")
        # 返回信息
        public.WriteLog(self._log_name, "添加Python项目{}".format(values["pjname"]))
        if flag:
            self.__write_log(values["pjname"], "项目启动成功!")
            # logfile = f"{self._logs_path}/{values['pjname']}.log"
            # if os.path.exists(logfile):
            #     os.remove(logfile)
            return public.returnMsg(True, "项目启动成功!")
        else:
            msg = "项目启动失败，但我们已经配置好了环境，您可以通过站点设置、日志文件了解更多详情。"
            self.__write_log(values["pjname"], msg)
            return public.returnMsg(True, msg)

    def __prepare_start_conf(self, values):
        """准备启动的配置文件,python运行不需要,uwsgi和gunicorn需要
        @author baozi <202-02-22>
        @param:
            values  ( dict ):  用户传入的参数
        @return   :
        """
        # 加入默认配置
        values["user"] = values['user'] if 'user' in values else 'root'
        values["processes"] = values['processes'] if 'processes' in values else 4
        values["threads"] = values['threads'] if 'threads' in values else 2
        if not os.path.exists(values['logpath']):
            os.makedirs(values['logpath'], mode=0o777)
        self.__prepare_uwsgi_start_conf(values)
        self.__prepare_gunicorn_start_conf(values)

    def __prepare_uwsgi_start_conf(self, values):
        # uwsgi
        template_file = "{}/template/python_project/uwsgi_conf.conf".format(self._vhost_path)
        config_body: str = public.readFile(template_file)
        values["is_http"] = values["is_http"] if "is_http" in values else True
        config_body = config_body.format(
            path=values["path"],
            rfile=values["rfile"],
            processes=values["processes"],
            threads=values["threads"],
            is_http="" if values["is_http"] else "#",
            is_socket="#" if values["is_http"] else "",
            port=values["port"],
            user=values["user"],
            logpath=values['logpath']
        )
        uwsgi_file = f"{values['path']}/uwsgi.ini"
        public.writeFile(uwsgi_file, config_body)

    def __prepare_gunicorn_start_conf(self, values):
        # gunicorn
        worker_class = "sync" if values["xsgi"] == "wsgi" else 'uvicorn.workers.UvicornWorker'
        template_file = "{}/template/python_project/gunicorn_conf.conf".format(self._vhost_path)
        values["loglevel"] = values["loglevel"] if "loglevel" in values else "info"
        config_body: str = public.readFile(template_file)
        config_body = config_body.format(
            path=values["path"],
            processes=values["processes"],
            threads=values["threads"],
            user=values["user"],
            worker_class=worker_class,
            port=values["port"],
            logpath=values['logpath'],
            loglevel=values["loglevel"]
        )
        gconf_file = f"{values['path']}/gunicorn_conf.py"
        public.writeFile(gconf_file, config_body)

    def __start_project(self, project_conf, reconstruction=False):
        """启动项目
        @author baozi <202-02-22>
        @param:
            project_conf  ( dict ):  站点配置
            reconstruction  ( bool ):  是否重写启动指令
        @return  bool : 是否启动成功
        """
        if project_conf["stype"] == "python":
            log_file = project_conf['logpath'] + "/error.log".replace("//", "/")
            if not os.path.exists(log_file):
                public.ExecShell("mkdir %s" % os.path.dirname(log_file), user="www")
                public.ExecShell("touch %s" % log_file)
            v_python = self._get_vp_python(project_conf['vpath'])
            _sh = "nohup {vpath} -u {run_file} {parm} >> {log} 2>&1 &".format(
                vpath=v_python,
                run_file=project_conf['rfile'],
                log=log_file,
                parm=project_conf['parm']
            )
            _check_sh = f"ps aux|grep '{v_python}'|grep -v 'grep'|wc -l"
        elif project_conf["stype"] == "uwsgi":
            if not os.path.exists(project_conf['path'] + "/uwsgi.ini"):
                self.__prepare_uwsgi_start_conf(project_conf)
            _sh = "%s/bin/uwsgi -d --ini %s/uwsgi.ini" % (
                project_conf['vpath'], project_conf['path'])
            _check_sh = f"ps aux|grep '{project_conf['vpath']}/bin/uwsgi'|grep -v 'grep'|wc -l"
        else:
            if not os.path.exists(project_conf['path'] + "/gunicorn_conf.py"):
                self.__prepare_gunicorn_start_conf(project_conf)
            _app = project_conf['rfile'].replace((project_conf['path'] + "/"), "")[:-3]
            _app = _app.replace("/", ".")
            if project_conf['framework'] == "django":
                _app += ":application"
            else:
                _app += ":app"
            _sh = "nohup %s/bin/gunicorn -c %s/gunicorn_conf.py %s &>> %s &" % (
                project_conf['vpath'], project_conf['path'], _app, f'{project_conf["logpath"]}/gunicorn_error.log')
            _check_sh = f"ps aux|grep '{project_conf['vpath']}/bin/gunicorn' |grep -v 'grep'|wc -l"

        project_conf["start_sh"], project_conf["check_sh"] = _sh, _check_sh

        pid_cnt = public.ExecShell(_check_sh)[0].strip("\n")
        if pid_cnt != "0":
            return True
        res = public.ExecShell(_sh)
        for _ in range(10):
            time.sleep(0.1)
            pid_cnt = public.ExecShell(_check_sh)[0].strip("\n")
            if pid_cnt != "0":
                # 再次检查是否开启
                time.sleep(0.8)
                pid_cnt = public.ExecShell(_check_sh)[0].strip("\n")
                if pid_cnt != "0":
                    project_conf["status"] = 1
                    return True

        project_conf["status"] = 0
        return False

    def StartProject(self, get):
        """启动项目api接口
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息，包含name
        @return   msg: 启动情况信息
        """
        name = get.name.strip()
        project_conf = self.__get_project_conf(name_id=name)
        if not project_conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")
        if "port" in project_conf and project_conf["port"]:
            flag, msg = self.__check_port(project_conf["port"])
            if not flag:
                return public.returnMsg(False, msg)
        if not os.path.exists(project_conf["path"]):
            return public.returnMsg(False, "项目文件丢失，无法启动")
        flag = self.__start_project(project_conf)
        if flag:
            pdata = {
                "status": 1,
                "project_config": json.dumps(project_conf)
            }
            public.M('sites').where('name=?', (name,)).update(pdata)
            return public.returnMsg(True, "项目启动成功")
        else:
            pdata = {
                "status": 0,
                "project_config": json.dumps(project_conf)
            }
            public.M('sites').where('name=?', (name,)).update(pdata)
            return public.returnMsg(False, "项目启动失败")

    def __stop_project(self, project_conf, reconstruction=False):
        """停止项目
        @author baozi <202-02-22>
        @param:
            project_conf  ( dict ):  站点配置
        @return  bool : 是否停止成功
        """
        if "stop_sh" in project_conf and not reconstruction:
            _sh = project_conf["stop_sh"]
            _check_sh = project_conf["check_sh"]
        elif project_conf["stype"] == "python":
            v_python = self._get_vp_python(project_conf['vpath'])
            _sh = "kill -s 15 `ps aux|grep '%s' |grep -v 'grep' |awk '{print $2}'`" % v_python
            _check_sh = f"ps aux|grep '{v_python}'|grep -v 'grep'|wc -l"
        elif project_conf["stype"] == "uwsgi":
            _sh = "%s/bin/uwsgi --stop %s/uwsgi.pid" % (
                project_conf['vpath'], project_conf['path'])
            _check_sh = f"ps aux|grep '{project_conf['vpath']}/bin/uwsgi'|grep -v 'grep'|wc -l"
        else:
            gunicorn_pid = f"{project_conf['path']}/gunicorn.pid"
            _sh = "kill -15  `cat %s`" % gunicorn_pid
            _check_sh = f"ps aux|grep '{project_conf['vpath']}/bin/gunicorn' |grep -v 'grep'|wc -l"

        project_conf["stop_sh"], project_conf["check_sh"] = _sh, _check_sh
        pid_cnt = public.ExecShell(_check_sh)[0].strip("\n")
        if pid_cnt == "0":
            return True
        err = public.ExecShell(_sh)[1]
        if not err:
            for _ in range(20):
                time.sleep(0.1)
                pid_cnt = public.ExecShell(_check_sh)[0].strip("\n")
                if pid_cnt == "0":
                    project_conf["status"] = 0
                    return True

        if self._error_stop(project_conf):
            return True
        project_conf["status"] = 1
        return False

    def _error_stop(self, project_conf):
        """
        @param project_conf: 站点配置
        @return:
        """
        if project_conf["stype"] == "uwsgi":
            pid_file = project_conf['path'] + "/uwsgi.pid"
            if os.path.exists(pid_file):
                return False
            _sh = "ps aux|grep '%s/bin/uwsgi' |grep -v 'grep' |awk '{print $2}'" % project_conf['vpath']
            tmp = public.ExecShell(_sh)[0]
        elif project_conf["stype"] == "gunicorn":
            gunicorn_pid = f"{project_conf['path']}/gunicorn.pid"
            if os.path.exists(gunicorn_pid):
                return False
            _sh = "ps aux|grep '%s/bin/gunicorn' |grep -v 'grep' |awk '{print $2}'" % project_conf['vpath']
            tmp = public.ExecShell(_sh)[0]
        else:
            return False
        for i in tmp.split("\n"):
            try:
                pid = int(i)
            except ValueError:
                continue
            # 根据 PID 查找进程
            process = psutil.Process(pid)
            # 杀死进程
            process.terminate()

        for _ in range(20):
            time.sleep(0.1)
            pid_cnt = public.ExecShell(project_conf["check_sh"])[0].strip("\n")
            if pid_cnt == "0":
                project_conf["status"] = 0
                return True
        return False

    def StopProject(self, get):
        """停止项目的api接口
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息
        @return  msg : 返回停止操作的结果
        """
        name = get.name.strip()
        project_conf = self.__get_project_conf(name_id=name)
        if not project_conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")

        if self.__stop_project(project_conf):
            pdata = {
                "status": 0,
                "project_config": json.dumps(project_conf)
            }
            public.M('sites').where('name=?', (name,)).update(pdata)
            return public.returnMsg(True, "项目停止成功")
        else:
            pdata = {
                "status": 1,
                "project_config": json.dumps(project_conf)
            }
            public.M('sites').where('name=?', (name,)).update(pdata)
            return public.returnMsg(False, "项目停止失败")

    def RestartProject(self, get):
        name = get.name.strip()
        conf = self.__get_project_conf(name)
        if not conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")
        if not self.__stop_project(conf):
            return public.returnMsg(False, "项目停止失败")
        if not self.__start_project(conf):
            return public.returnMsg(False, "项目启动失败")
        return public.returnMsg(True, "项目重启成功")

    def RemoveProject(self, get):
        """删除项目接口
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息对象
        @return  msg : 是否删除成功
        """
        name = get.name.strip()
        project = self.get_project_find(name)
        conf = project["project_config"]
        if not conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")
        pid_cnt = public.ExecShell(conf["check_sh"])[0].strip("\n")
        if pid_cnt != "0" and (not self.__stop_project(conf)):
            return public.returnMsg(False, "项目未停止成功，请尝试手动停止并重试")

        self.del_crontab(name)
        self.clear_config(get.name)
        logfile = self._logs_path + "/%s.log" % conf["pjname"]
        if os.path.exists(conf["vpath"]): shutil.rmtree(conf["vpath"])
        if os.path.exists(logfile): os.remove(logfile)
        if os.path.exists(conf["path"] + "/uwsgi.ini"): os.remove(conf["path"] + "/uwsgi.ini")
        if os.path.exists(conf["path"] + "/gunicorn_conf.py"): os.remove(conf["path"] + "/gunicorn_conf.py")

        public.M('domain').where('pid=?', (project['id'],)).delete()
        public.M('sites').where('name=?', (name,)).delete()
        public.WriteLog(self._log_name, '删除Python项目{}'.format(name))
        return public.returnMsg(True, "删除成功")

    def xsssec(self, text):
        return text.replace('<', '&lt;').replace('>', '&gt;')

    def last_lines(self, filename, lines=1):
        block_size = 3145928
        block = ''
        nl_count = 0
        start = 0
        fsock = open(filename, 'rU')
        try:
            fsock.seek(0, 2)
            curpos = fsock.tell()
            while (curpos > 0):
                curpos -= (block_size + len(block))
                if curpos < 0: curpos = 0
                fsock.seek(curpos)
                try:
                    block = fsock.read()
                except:
                    continue
                nl_count = block.count('\n')
                if nl_count >= lines: break
            for n in range(nl_count - lines + 1):
                start = block.find('\n', start) + 1
        finally:
            fsock.close()
        return block[start:]

    def GetProjectLog(self, get):
        """获取项目日志api
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息，需要包含项目名称
        @return  msg : 日志信息
        """
        project_conf = self.__get_project_conf(get.name.strip())
        if not project_conf: return public.returnMsg(False, '项目不存在')
        if project_conf["stype"] == "python":
            log_file = project_conf["logpath"] + "/error.log"
        elif project_conf["stype"] == "gunicorn":
            log_file = project_conf["logpath"] + "/gunicorn_error.log"
        else:
            log_file = project_conf["logpath"] + "/uwsgi.log"
        if not os.path.exists(log_file): return public.returnMsg(False, '日志文件不存在')
        log_file_size = os.path.getsize(log_file)
        if log_file_size > 3145928:
            return {"status": True, "path": log_file, "data": self.xsssec(self.last_lines(log_file, 3000)),
                    "size": public.to_size(log_file_size)}
        return {"status": True, "path": log_file, "data": self.xsssec(public.GetNumLines(log_file, 3000)),
                "size": public.to_size(log_file_size)}

    def GetPythonInstallLog(self, get):
        log_file = f"{self._logs_path}/py.log"
        if not os.path.exists(log_file): return public.returnMsg(False, '日志文件不存在')
        if os.path.getsize(log_file) > 3145928:
            return public.returnMsg(True, self.xsssec(self.last_lines(log_file, 3000)))
        return public.returnMsg(True, self.xsssec(public.GetNumLines(log_file, 3000)))

    def GetProjectCreateLog(self, get):
        name = get.name.strip()
        log_file = f"{self._logs_path}/{name}.log"
        if not os.path.exists(log_file): return public.returnMsg(False, '日志文件不存在')
        if os.path.getsize(log_file) > 3145928:
            return public.returnMsg(True, self.xsssec(self.last_lines(log_file, 3000)))
        return public.returnMsg(True, self.xsssec(public.GetNumLines(log_file, 3000)))

    def GetProjectList(self, get):
        """获取项目列表
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息
        @return  msg : _description_
        """
        if not 'p' in get:  get.p = 1
        if not 'limit' in get: get.limit = 20
        if not 'callback' in get: get.callback = ''
        if not 'order' in get: get.order = 'id desc'

        if 'search' in get:
            get.project_name = get.search.strip()
            search = "%{}%".format(get.project_name)
            count = public.M('sites').where('project_type=? AND (name LIKE ? OR ps LIKE ?)',
                                            ('Python', search, search)).count()
            data = public.get_page(count, int(get.p), int(get.limit), get.callback)
            data['data'] = public.M('sites').where('project_type=? AND (name LIKE ? OR ps LIKE ?)',
                                                   ('Python', search, search)).limit(
                data['shift'] + ',' + data['row']).order(get.order).select()
        else:
            count = public.M('sites').where('project_type=?', 'Python').count()
            data = public.get_page(count, int(get.p), int(get.limit), get.callback)
            data['data'] = public.M('sites').where('project_type=?', 'Python').limit(
                data['shift'] + ',' + data['row']).order(get.order).select()

        for i in range(len(data['data'])):
            self._get_project_state(data['data'][i])
        return data

    def _get_project_state(self, project_info):
        """获取项目详情信息
        @author baozi <202-02-22>
        @param:
            project_info  ( dict ):  项目详情
        @return   : 项目详情的列表
        """
        if not isinstance(project_info['project_config'], dict):
            project_info['project_config'] = json.loads(project_info['project_config'])
        if project_info["project_config"]["stype"] == "python":
            project_info["config_file"] = None
        elif project_info["project_config"]["stype"] == "uwsgi":
            project_info["config_file"] = f'{project_info["project_config"]["path"]}/uwsgi.ini'
        else:
            project_info["config_file"] = f'{project_info["project_config"]["path"]}/gunicorn_conf.py'

        pid_cnt = public.ExecShell(project_info["project_config"]["check_sh"])[0].strip("\n")
        if pid_cnt == "0":
            project_info['run'], project_info['status'], project_info["project_config"]["status"] = False, 0, 0
        else:
            project_info['run'], project_info['status'], project_info["project_config"]["status"] = True, 1, 1
            mem, cpu = self.get_mem_and_cpu(project_info["project_config"])
            project_info.update({"cpu": cpu, "mem": mem})
        for i in ("start_sh", "stop_sh", "check_sh"):
            if i in project_info["project_config"]: project_info["project_config"].pop(i)

    def GetProjectConf(self, get):
        """获取项目配置信息
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  请求信息，站点名称name
        @return  可修改项目  uwsgi: rfile, processes, threads, is_http, port, user, logpath, other
                            gunicorn: rfile, processes, threads, port, user, logpath, loglevel, other
        """
        project_conf = self.__get_project_conf(get.name.strip())
        if not project_conf: return public.return_error('项目不存在')
        res_data = {
            "rfile": project_conf["rfile"],
            "xsgi": project_conf["xsgi"],
            "processes": project_conf["processes"] if "processes" in project_conf else 4,
            "threads": project_conf["threads"] if "threads" in project_conf else 2,
            "port": project_conf["port"],
            "user": project_conf["user"],
            "logpath": project_conf["logpath"],
            "stype": project_conf["stype"],
            "is_http": project_conf["is_http"] if "is_http" in project_conf else True,
            "loglevel": project_conf["loglevel"] if "loglevel" in project_conf else 'info'
        }
        return res_data

    def ChangeProjectConf(self, get):
        """修改项目配置信息
        @author baozi <202-02-22>
        @param:
            get  ( dict ):  用户请求信息 包含name，data
        @return
        """
        conf = self.__get_project_conf(get.name.strip())
        if not conf: return public.returnMsg("没有该项目")
        if not os.path.exists(conf["path"]):
            return public.returnMsg(False, "项目文件丢失，请尝试移除本项目，重新建立")
        data: dict = get.data

        change_values = {}
        # stype
        if "stype" in data and data["stype"] != conf["stype"]:
            if data["stype"] not in ("uwsgi", "gunicorn", "python"):
                return public.returnMsg(False, "启动方式选择错误")
            else:
                self.__stop_project(conf)
                self.__prepare_start_conf(conf)
                conf["stype"] = data["stype"]
        if "xsgi" in data and data["xsgi"] != conf["xsgi"]:
            if data["xsgi"] not in ("wsgi", "asgi"):
                return public.returnMsg(False, "网络协议选择错误")
            else:
                conf["xsgi"] = data["xsgi"]
                change_values["xsgi"] = data["xsgi"]
        # 检查服务器部署的可行性
        msg = self.__check_feasibility(conf)
        if msg: return public.returnMsg(False, msg)
        # rfile
        if "rfile" in data and data["rfile"] != conf["rfile"]:
            if not data["rfile"].startswith(conf["path"]):
                return public.returnMsg(False, "启动文件不在项目目录下？。。。")
            if not (data["rfile"][-3:] == ".py" and os.path.isfile(data["rfile"])):
                return public.returnMsg(False, "启动文件不是python扩展文件？。。。")
            change_values["rfile"] = data["rfile"]
            conf["rfile"] = data["rfile"]
        # parm
        if conf["stype"] == "python":
            conf["parm"] = data["parm"] if "parm" in data else conf["parm"]

        # processes and threads
        try:
            if "processes" in data and int(data["processes"]) != int(conf["processes"]):
                change_values["processes"], conf["processes"] = int(data["processes"]), int(data["processes"])
            if "threads" in data and int(data["threads"]) != int(conf["threads"]):
                change_values["threads"], conf["threads"] = int(data["threads"]), int(data["threads"])
        except ValueError:
            return public.returnMsg(False, "线程或进程数设置有误")

        # port 某些情况下可以关闭
        if "port" in data and data["port"] != conf["port"] and data["port"]:
            flag, msg = self.__check_port(data["port"])
            if not flag:
                return public.returnMsg(False, msg)
            change_values["port"] = data["port"]
            conf["port"] = data["port"]

        # user
        if "user" in data and data["user"] != conf["user"]:
            if data["user"] in ("root", "www"):
                change_values["user"] = data["user"]
                conf["user"] = data["user"]

        # auto_run
        if "auto_run" in data and data["auto_run"] != conf["auto_run"]:
            if isinstance(data["auto_run"], bool):
                conf["auto_run"] = data["auto_run"]
        # logpath
        if "logpath" in data and data["logpath"] != conf["logpath"]:
            data["logpath"] = data["logpath"] if data["logpath"][-1] != '/' else data["logpath"][:-1]
            if os.path.isfile(data["logpath"]):
                return public.returnMsg(False, "日志路径不应当是一个文件")
            if '\n' in data["logpath"].strip():
                return public.returnMsg(False, "日志路径不能包含换行")
            change_values["logpath"] = data["logpath"]
            conf["logpath"] = data["logpath"]

        # 特殊
        if conf["stype"] == "gunicorn":
            if "loglevel" in data and data["loglevel"] != conf["loglevel"]:
                if data["loglevel"] in ("debug", "info", "warning", "error", "critical"):
                    change_values["loglevel"] = data["loglevel"]
                    conf["loglevel"] = data["loglevel"]
            config_file = public.readFile(conf["path"] + "/gunicorn_conf.py")
            config_file = self.__change_gunicorn_config_to_file(change_values, config_file)
            public.writeFile(conf["path"] + "/gunicorn_conf.py", config_file)

        if conf["stype"] == "uwsgi":
            if "is_http" in data and isinstance(data["is_http"], bool):
                change_values["is_http"] = data["is_http"]
                conf["is_http"] = data["is_http"]
            config_file = public.readFile(conf["path"] + "/uwsgi.ini")
            if "port" not in change_values:
                change_values["port"] = conf["port"]
            config_file = self.__change_uwsgi_config_to_file(change_values, config_file)
            public.writeFile(conf["path"] + "/uwsgi.ini", config_file)

        # 尝试重启项目
        msg = ''
        if not self.__stop_project(conf, reconstruction=True):
            msg = "修改成功，但尝试重启时，项目停止失败"
        if not self.__start_project(conf, reconstruction=True):
            msg = "修改成功，但尝试重启时，项目启动失败"

        pdata = {
            "project_config": json.dumps(conf)
        }
        public.M('sites').where('name=?', (get.name.strip(),)).update(pdata)
        public.WriteLog(self._log_name, 'Python项目{}, 修改了启动配置项'.format(get.name.strip()))

        if msg:
            return public.returnMsg(False, msg)

        return public.returnMsg(True, "修改成功")

    def __change_uwsgi_config_to_file(self, changes, config_file):
        """修改配置信息
        @author baozi <202-03-08>
        @param:
            changes  ( dict ):  改变的项和值
            config_file  ( string ):  需要改变的文件
        @return
        """
        reps = {
            "rfile": (r'wsgi-file\s{0,3}=\s{0,3}[^#\n]*\n', lambda x: f"wsgi-file={x.strip()}\n"),
            "processes": (r'processes\s{0,3}=\s{0,3}[\d]*\n', lambda x: f"processes={x.strip()}\n"),
            "threads": (r'threads\s{0,3}=\s{0,3}[\d]*\n', lambda x: f"threads={x.strip()}\n"),
            "user": (
            r'uid\s{0,3}=\s{0,3}[^\n]*\ngid\s{0,3}=\s{0,3}[^\n]*\n', lambda x: f"uid={x.strip()}\ngid={x.strip()}\n"),
            "logpath": (r'daemonize\s{0,3}=\s{0,3}[^\n]*\n', lambda x: f"daemonize={x.strip()}/uwsgi.log\n")
        }
        if "logpath" in changes and not os.path.exists(changes['logpath']):
            os.makedirs(changes['logpath'], mode=0o777)
        for k, (rep, fun) in reps.items():
            if k not in changes: continue
            config_file = re.sub(rep, fun(str(changes[k])), config_file)

        if "port" in changes:
            # 被用户关闭了预设的通信方式
            if config_file.find("\n#http") != -1 and config_file.find("\n#socket") != -1:
                pass
            elif "is_http" in changes:
                # 按照预设的方式修改
                rep = r"\n#?http\s{0,3}=\s{0,3}((\d{0,3}\.){3}\d{0,3})?:\d{2,5}\n#?socket\s{0,3}=\s{0,3}((\d{0,3}\.){3}\d{0,3})?:\d{2,5}\n"
                is_http, is_socket = ("", "#") if changes["is_http"] else ("#", "")
                new = "\n{is_http}http=0.0.0.0:{port}\n{is_socket}socket=0.0.0.0:{port}\n".format(is_http=is_http,
                                                                                                  port=changes["port"],
                                                                                                  is_socket=is_socket)
                config_file = re.sub(rep, new, config_file)
            else:
                rpe_h = r'http\s{0,3}=\s{0,3}((\d{0,3}\.){3}\d{0,3})?:\d{2,5}\n'
                config_file = re.sub(rpe_h, f"http=0.0.0.0:{changes['port']}\n", config_file)
                rpe_s = r'socket\s{0,3}=\s{0,3}((\d{0,3}\.){3}\d{0,3})?:\d{2,5}\n'
                config_file = re.sub(rpe_s, f"socket=0.0.0.0:{changes['port']}\n", config_file)

        return config_file

    def __prevent_re(self, test_str):
        # 防正则转译
        re_char = ['$', '(', ')', '*', '+', '.', '[', ']', '{', '}', '?', '^', '|', '\\']
        res = ""
        for i in test_str:
            if i in re_char:
                res += "\\" + i
            else:
                res += i
        return res

    def __get_uwsgi_config_from_file(self, config_file, conf):
        """检查并从修改的配置信息获取必要信息
        @author baozi <202-03-08>
        @param:
            changes  ( dict ):  改变的项和值
            config_file  ( string ):  需要改变的文件
        @return
        """
        # 检查必要项目
        check_reps = [
            (r"\n\s?chdir\s{0,3}=\s{0,3}" + self.__prevent_re(conf["path"]) + r"[^\n]*\n", "不能修改项目路径"),
            (r"\n\s?pidfile\s{0,3}=\s{0,3}" + self.__prevent_re(conf["path"] + "/uwsgi.pid") + r"[^\n]*\n",
             "不能修改项目的pidfile文件位置"),
            (r"\n\s?master\s{0,3}=\s{0,3}true[^\n]*\n", "不能修改主进程相关配置"),
        ]
        for rep, msg in check_reps:
            if not re.search(rep, config_file):
                return False, msg

        get_reps = {
            "rfile": (r'\n\s?wsgi-file\s{0,3}=\s{0,3}(?P<target>[^#\n]*)\n', None),
            "module": (r'\n\s?module\s{0,3}=\s{0,3}(?P<target>[^\n/:])*:[^\n]*\n', None),
            "processes": (r'\n\s?processes\s{0,3}=\s{0,3}(?P<target>[\d]*)\n', None),
            "threads": (r'\n\s?threads\s{0,3}=\s{0,3}(?P<target>[\d]*)\n', None),
            "logpath": (
            r'\n\s?daemonize\s{0,3}=\s{0,3}(?P<target>[^\n]*)\n', "没有检查到。配置项：日志路径，请注意您的修改")
        }
        changes = {}
        for k, (rep, msg) in get_reps.items():
            res = re.search(rep, config_file)
            if not res and msg:
                return False, msg
            elif res:
                changes[k] = res.group("target").strip()
        if "module" in changes:
            _rfile = conf["path"] + changes["module"].replace(".", "/") + ".py"
            if os.path.isfile(_rfile):
                changes["rfile"] = _rfile
            changes.pop("module")

        if "logpath" in changes:
            if not os.path.exists(changes['logpath']):
                os.makedirs(changes['logpath'], mode=0o777)
            if "/" in changes["logpath"]:
                _path, filename = changes["logpath"].rsplit("/", 1)
                if filename != "uwsgi.log":
                    return False, "为方便日志管理，日志文件名称请使用 uwsgi.log "
                else:
                    changes["logpath"] = _path
            else:
                if changes["logpath"] != "uwsgi.log":
                    return False, "为方便日志管理，日志文件名称请使用 uwsgi.log"
                else:
                    changes["logpath"] = conf["path"]

        # port 相关查询
        rep_h = r'\n\s{0,3}http\s{0,3}=\s{0,3}((\d{0,3}\.){3}\d{0,3})?:(?P<target>\d{2,5})[^\n]*\n'
        rep_s = r'\n\s{0,3}socket\s{0,3}=\s{0,3}((\d{0,3}\.){3}\d{0,3})?:(?P<target>\d{2,5})[^\n]*\n'
        res_http = re.search(rep_h, config_file)
        res_socket = re.search(rep_s, config_file)
        if res_http:
            changes["port"] = res_http.group("target").strip()
        elif res_socket:
            changes["port"] = res_socket.group("target").strip()
        else:
            # 被用户关闭了预设的通信方式
            changes["port"] = ""

        return True, changes

    def __change_gunicorn_config_to_file(self, changes, config_file):
        """修改配置信息
        @author baozi <202-03-08>
        @param:
            changes  ( dict ):  改变的项和值
            config_file  ( string ):  需要改变的文件
        @return
        """
        reps = {
            "processes": (r'workers\s{0,3}=\s{0,3}[^\n]*\n', lambda x: f"workers = {x.strip()}\n"),
            "threads": (r'threads\s{0,3}=\s{0,3}[\d]*\n', lambda x: f"threads = {x.strip()}\n"),
            "user": (r'user\s{0,3}=\s{0,3}[^\n]*\n', lambda x: f"user = '{x.strip()}'\n"),
            "loglevel": (r'loglevel\s{0,3}=\s{0,3}[^\n]*\n', lambda x: f"loglevel = '{x.strip()}'\n"),
            "port": (r'bind\s{0,3}=\s{0,3}[^\n]*\n', lambda x: f"bind = '0.0.0.0:{x.strip()}'\n"),
        }
        for k, (rep, fun) in reps.items():
            if k not in changes: continue
            config_file = re.sub(rep, fun(str(changes[k])), config_file)
        if "logpath" in changes:
            if not os.path.exists(changes['logpath']):
                os.makedirs(changes['logpath'], mode=0o777)
            rpe_accesslog = r'''accesslog\s{0,3}=\s{0,3}['"](/[^/\n]*)*['"]\n'''
            config_file = re.sub(rpe_accesslog, f"accesslog = '{changes['logpath']}/gunicorn_acess.log'\n", config_file)
            rpe_errorlog = r'''errorlog\s{0,3}=\s{0,3}['"](/[^/\n]*)*['"]\n'''
            config_file = re.sub(rpe_errorlog, f"errorlog = '{changes['logpath']}/gunicorn_error.log\n", config_file)

        return config_file

    def __get_gunicorn_config_from_file(self, config_file, conf):
        """修改配置信息
        @author baozi <202-03-08>
        @param:
            config_file  ( dict ):  被改变的文件
            conf  ( string ):  项目原配置
        @return
        """
        # 检查必要项目
        check_reps = [
            (r'''\n\s?chdir ?= ?["']''' + self.__prevent_re(conf["path"]) + '''["']\n''', "请不要修改项目路径"),
            (r'''\n\s?pidfile\s{0,3}=\s{0,3}['"]''' + self.__prevent_re(
                conf["path"] + "/gunicorn.pid") + r'''['"][^\n]*\n''',
             "不能修改项目的pidfile文件位置,这将导致我们无法准确监控项目运行情况"),
            (r'''\n\s?worker_class\s{0,3}=\s{0,3}((['"]sync['"])|(['"]uvicorn\.workers\.UvicornWorker['"]))[^\n]*\n''',
             "请不要修改worker_class相关配置"),
        ]
        for rep, msg in check_reps:
            if not re.findall(rep, config_file):
                return False, msg

        get_reps = {
            "port": (r'''\n\s?bind\s{0,3}=\s{0,3}['"]((\d{0,3}\.){3}\d{0,3})?:(?P<target>\d{2,5})['"][^\n]*\n''',
                     "没有检查到。配置项：bind，请注意您的修改"),
            "processes": (r'\n\s?workers\s{0,3}=\s{0,3}(?P<target>[^\n]*)[^\n]*\n', None),
            "threads": (r'\n\s?threads\s{0,3}=\s{0,3}(?P<target>[\d]*)[^\n]*\n', None),
            "logpath": (r'''\n\s?errorlog\s{0,3}=\s{0,3}['"](?P<target>[^"'\n]*)['"][^\n]*\n''',
                        "没有检查到。配置项：日志路径，请注意您的修改"),
            "loglevel": (r'''\n\s?loglevel\s{0,3}=\s{0,3}['"](?P<target>[^'"\n]*)['"][^\n]*\n''',
                         "没有检查到。配置项：日志等级，请注意您的修改")
        }
        changes = {}
        for k, (rep, msg) in get_reps.items():
            res = re.search(rep, config_file)
            if not res and msg:
                return False, msg
            elif res:
                changes[k] = res.group("target").strip()

        if "logpath" in changes:
            if not os.path.exists(changes['logpath']):
                os.makedirs(changes['logpath'], mode=0o777)
            if "/" in changes["logpath"]:
                _path, filename = changes["logpath"].rsplit("/", 1)
                if filename != "gunicorn_error.log":
                    return False, "为方便日志管理，日志文件名称请使用 gunicorn_error.log"
                else:
                    changes["logpath"] = _path
            else:
                if changes["logpath"] != "gunicorn_error.log":
                    return False, "为方便日志管理，日志文件名称请使用 gunicorn_error.log"
                else:
                    changes["logpath"] = conf["path"]
            rep_accesslog = r'''\n\s?accesslog\s{0,3}=\s{0,3}['"]''' + self.__prevent_re(
                changes["logpath"] + "/gunicorn_acess.log") + r'''['"][^\n]*\n'''
            if not re.search(rep_accesslog, config_file):
                return False, "为方便日志管理, 请将错误日志(errorlog) 与 访问日志(accesslog) 放到同一文件路径下"

        if "loglevel" in changes:
            if not changes["loglevel"] in ("debug", "info", "warning", "error", "critical"):
                return False, "日志等级配置错误"
        return True, changes

    def get_ssl_end_date(self, project_name):
        '''
            @name 获取SSL信息
            @author hwliang<2021-08-09>
            @param project_name <string> 项目名称
            @return dict
        '''
        import data
        return data.data().get_site_ssl_info('python_{}'.format(project_name))

    def GetProjectInfo(self, get):
        """获取项目所有信息
        @author baozi <202-03-08>
        @param:
            get  ( dict ):  请求信息，站点名称name
        @return
        """
        project = self.get_project_find(get.name.strip())
        if not project: return public.returnMsg(False, "没该项目")
        self._get_project_state(project)
        project_conf = project["project_config"]
        if project_conf["stype"] == "python":
            return project
        project_conf["processes"] = project_conf["processes"] if "processes" in project_conf else 4
        project_conf["threads"] = project_conf["threads"] if "threads" in project_conf else 2

        if project_conf["stype"] == "uwsgi":
            project_conf["is_http"] = bool(project_conf["is_http"])

        project["ssl"] = self.get_ssl_end_date(get.name.strip())
        return project

    # 取文件配置
    def GetConfFile(self, get):
        """获取项目配置文件信息
        @author baozi <202-03-08>
        @param:
            get  ( dict ):  用户请求信息 包含name
        @return 文件信息
        """
        project_conf = self.__get_project_conf(get.name.strip())
        if not project_conf: return public.return_error('项目不存在')

        import files
        if project_conf["stype"] == "python":
            return public.returnMsg(False, "Python启动方式没有配置文件可修改")
        elif project_conf["stype"] == "gunicorn":
            get.path = project_conf["path"] + "/gunicorn_conf.py"
        else:
            get.path = project_conf["path"] + "/uwsgi.ini"
        public.print_log(get.path)
        f = files.files()
        return f.GetFileBody(get)

    # 保存文件配置
    def SaveConfFile(self, get):
        """修改项目配置文件信息
        @author baozi <202-03-08>
        @param:
            get  ( dict ):  用户请求信息 包含name,data,encoding
        @return 文件信息
        """
        project_conf = self.__get_project_conf(get.name.strip())
        if not project_conf: return public.return_error('项目不存在')

        import files

        data = get.data
        if project_conf["stype"] == "python":
            return public.returnMsg(False, "Python启动方式没有配置文件可修改")
        elif project_conf["stype"] == "gunicorn":
            get.path = project_conf["path"] + "/gunicorn_conf.py"
            flag, changes = self.__get_gunicorn_config_from_file(data, project_conf)
            if not flag:
                return public.returnMsg(False, changes)
        else:
            get.path = project_conf["path"] + "/uwsgi.ini"
            flag, changes = self.__get_uwsgi_config_from_file(data, project_conf)
            if not flag:
                return public.returnMsg(False, changes)

        project_conf.update(changes)

        f = files.files()
        get.encoding = "utf-8"
        result = f.SaveFileBody(get)
        if not result["status"]:
            return public.returnMsg(False, "保存失败")

        # 尝试重启项目
        msg = ''
        if not self.__stop_project(project_conf, reconstruction=True):
            msg = "修改成功，但尝试重启时，项目停止失败"
        if not self.__start_project(project_conf, reconstruction=True):
            msg = "修改成功，但尝试重启时，项目启动失败"

        pdata = {
            "project_config": json.dumps(project_conf)
        }
        public.M('sites').where('name=?', (get.name.strip(),)).update(pdata)
        public.WriteLog(self._log_name, 'Python项目{}, 修改了启动配置项'.format(get.name.strip()))

        if msg:
            return public.returnMsg(False, msg)

        return public.returnMsg(True, "修改成功")

    # ———————————————————————————————————————————
    #   Nginx 与 Apache 相关的设置内容(包含SSL)  |
    # ———————————————————————————————————————————

    def exists_nginx_ssl(self, project_name):
        '''
            @name 判断项目是否配置Nginx SSL配置
            @author hwliang<2021-08-09>
            @param project_name: string<项目名称>
            @return tuple
        '''
        config_file = "{}/nginx/python_{}.conf".format(public.get_vhost_path(), project_name)
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

    def exists_apache_ssl(self, project_name):
        '''
            @name 判断项目是否配置Apache SSL配置
            @author hwliang<2021-08-09>
            @param project_name: string<项目名称>
            @return bool
        '''
        config_file = "{}/apache/python_{}.conf".format(public.get_vhost_path(), project_name)
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

    def set_apache_config(self, project):
        '''
            @name 设置Apache配置
            @author hwliang<2021-08-09>
            @param project: dict<项目信息>
            @return bool
        '''
        project_name = project['name']

        # 处理域名和端口
        ports = []
        domains = []
        for d in project['project_config']['domains']:
            domain_tmp = d.split(':')
            if len(domain_tmp) == 1: domain_tmp.append(80)
            if not int(domain_tmp[1]) in ports:
                ports.append(int(domain_tmp[1]))
            if not domain_tmp[0] in domains:
                domains.append(domain_tmp[0])

        config_file = "{}/apache/python_{}.conf".format(self._vhost_path, project_name)
        template_file = "{}/template/apache/python_http.conf".format(self._vhost_path)
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
                site_path=project['path'],
                server_name='{}.{}'.format(p, project_name),
                domains=' '.join(domains),
                log_path=public.get_logs_path(),
                server_admin='admin@{}'.format(project_name),
                url='http://127.0.0.1:{}'.format(project['project_config']['port']),
                port=p,
                ssl_config=ssl_config,
                project_name=project_name
            )
            apache_config_body += "\n"

            # 添加端口到主配置文件
            if not p in [80]:
                s.apacheAddPort(p)

        # 写.htaccess
        rewrite_file = "{}/.htaccess".format(project['path'])
        if not os.path.exists(rewrite_file): public.writeFile(rewrite_file,
                                                              '# 请将伪静态规则或自定义Apache配置填写到此处\n')

        # 写配置文件
        public.writeFile(config_file, apache_config_body)
        return True

    def set_nginx_config(self, project):
        '''
            @name 设置Nginx配置
            @author hwliang<2021-08-09>
            @param project: dict<项目信息>
            @return bool
        '''
        project_name = project['name']
        ports = []
        domains = []

        for d in project['project_config']['domains']:
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

        config_file = "{}/nginx/python_{}.conf".format(self._vhost_path, project_name)
        template_file = "{}/template/nginx/python_http.conf".format(self._vhost_path)

        config_body = public.readFile(template_file)
        config_body = config_body.format(
            site_path=project['path'],
            domains=' '.join(domains),
            project_name=project_name,
            panel_path=self._panel_path,
            log_path=public.get_logs_path(),
            url='http://127.0.0.1:{}'.format(project['project_config']['port']),
            host='127.0.0.1',
            listen_ports=listen_ports,
            ssl_config=ssl_config
        )

        # # 恢复旧的SSL配置
        # ssl_config = self.get_nginx_ssl_config(project_name)
        # if ssl_config:
        #     config_body.replace('#error_page 404/404.html;',ssl_config)

        rewrite_file = "{panel_path}/vhost/rewrite/python_{project_name}.conf".format(panel_path=self._panel_path,
                                                                                      project_name=project_name)
        if not os.path.exists(rewrite_file): public.writeFile(rewrite_file,
                                                              '# 请将伪静态规则或自定义NGINX配置填写到此处\n')
        public.writeFile(config_file, config_body)
        return True

    def clear_nginx_config(self, project):
        '''
            @name 清除nginx配置
            @author hwliang<2021-08-09>
            @param project: dict<项目信息>
            @return bool
        '''
        project_name = project['name']
        config_file = "{}/nginx/python_{}.conf".format(self._vhost_path, project_name)
        if os.path.exists(config_file):
            os.remove(config_file)
        rewrite_file = "{panel_path}/vhost/rewrite/python_{project_name}.conf".format(panel_path=self._panel_path,
                                                                                      project_name=project_name)
        if os.path.exists(rewrite_file):
            os.remove(rewrite_file)
        return True

    def clear_apache_config(self, project):
        '''
            @name 清除apache配置
            @author hwliang<2021-08-09>
            @param project_find: dict<项目信息>
            @return bool
        '''
        project_name = project['name']
        config_file = "{}/apache/python_{}.conf".format(self._vhost_path, project_name)
        if os.path.exists(config_file):
            os.remove(config_file)
        return True

    def get_project_find(self, project_name):
        '''
            @name 获取指定项目配置
            @author hwliang<2021-08-09>
            @param project_name<string> 项目名称
            @return dict
        '''
        project_info = public.M('sites').where('project_type=? AND name=?', ('Python', project_name)).find()
        if not project_info: return False
        project_info['project_config'] = json.loads(project_info['project_config'])
        return project_info

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

    def BindExtranet(self, get):
        '''
            @name 绑定外网
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                name: string<项目名称>
            }
            @return dict
        '''
        project_name = get.name.strip()
        project_find = self.get_project_find(project_name)
        if not project_find: return public.return_error('项目不存在')
        if not project_find['project_config']['domains']: return public.return_error(
            '请先到【域名管理】选项中至少添加一个域名')
        project_find['project_config']['bind_extranet'] = 1
        public.M('sites').where("id=?", (project_find['id'],)).setField('project_config',
                                                                        json.dumps(project_find['project_config']))
        self.set_config(project_name)
        public.WriteLog(self._log_name, 'Python项目{}, 开启外网映射'.format(project_name))
        return public.returnMsg(True, '开启外网映射成功')

    def unBindExtranet(self, get):
        '''
            @name 解绑外网
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                name: string<项目名称>
            }
            @return dict
        '''
        project_name = get.name.strip()
        self.clear_config(project_name)
        public.serviceReload()
        project_find = self.get_project_find(project_name)
        project_find['project_config']['bind_extranet'] = 0
        public.M('sites').where("id=?", (project_find['id'],)).setField('project_config',
                                                                        json.dumps(project_find['project_config']))
        public.WriteLog(self._log_name, 'Python项目{}, 关闭外网映射'.format(project_name))
        return public.returnMsg(True, '关闭成功')

    def GetProjectDomain(self, get):
        '''
            @name 获取指定项目的域名列表
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                name: string<项目名称>
            }
            @return dict
        '''
        project_name = get.name.strip()
        project_id = public.M('sites').where('name=?', (project_name,)).getField('id')
        domains = public.M('domain').where('pid=?', (project_id,)).order('id desc').select()
        project_find = self.get_project_find(project_name)
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

    def RemoveProjectDomain(self, get):
        '''
            @name 为指定项目删除域名
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                name: string<项目名称>
                domain: string<域名>
            }
            @return dict
        '''
        project_name = get.name.strip()
        project_find = self.get_project_find(project_name)
        if not project_find:
            return public.return_error('指定项目不存在')
        domain_arr = get.domain.split(':')
        if len(domain_arr) == 1:
            domain_arr.append(80)

        # 从域名配置表中删除
        project_id = public.M('sites').where('name=?', (project_name,)).getField('id')
        if len(project_find['project_config']['domains']) == 1: return public.return_error('项目至少需要一个域名')
        domain_id = public.M('domain').where('name=? AND pid=?', (domain_arr[0], project_id)).getField('id')
        if not domain_id:
            return public.returnMsg(False, '指定域名不存在')
        public.M('domain').where('id=?', (domain_id,)).delete()

        # 从 project_config 中删除
        if get.domain in project_find['project_config']['domains']:
            project_find['project_config']['domains'].remove(get.domain)
        if get.domain + ":80" in project_find['project_config']['domains']:
            project_find['project_config']['domains'].remove(get.domain + ":80")

        public.M('sites').where('id=?', (project_id,)).save('project_config',
                                                            json.dumps(project_find['project_config']))
        public.WriteLog(self._log_name, '从项目：{}，删除域名{}'.format(project_name, get.domain))
        self.set_config(project_name)
        return public.returnMsg(True, '删除域名成功')

    def MultiRemoveProjectDomain(self, get):
        '''
            @name 为指定项目删除域名
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                name: string<项目名称>
                domain: string<域名>
            }
            @return dict
        '''
        project_name = get.name.strip()
        project_find = self.get_project_find(project_name)
        if not project_find:
            return public.return_error('指定项目不存在')
        domain_ids: list = get.domain_ids

        try:
            if isinstance(domain_ids, str):
                domain_ids = json.loads(domain_ids)
            for i in range(len(domain_ids)):
                domain_ids[i] = int(domain_ids[i])
        except:
            return public.returnMsg(False, '域名id参数错误')

        # 获取正确的IDS
        project_id = public.M('sites').where('name=?', (project_name,)).getField('id')
        _all_id = public.M('domain').where('pid=?', (project_id,)).field("id,name,port").select()
        if not isinstance(_all_id, list):
            return public.returnMsg(False, '网站数据错误')
        all_id = {i["id"]: (i["name"], i["port"]) for i in _all_id}
        # 从域名配置表中删除
        for i in domain_ids:
            if i not in all_id:
                return public.returnMsg(False, '域名id参数不来自本站点')
        is_all = len(domain_ids) == len(all_id)
        not_del = None
        if is_all:
            domain_ids.sort(reverse=True)
            domain_ids, not_del = domain_ids[:-1], domain_ids[-1]
        if not_del:
            not_del = {"id": not_del, "name": all_id[not_del][0], "port": all_id[not_del][1]}

        public.M('domain').where(f'id IN ({",".join(["?"] * len(domain_ids))})', domain_ids).delete()

        del_domains = []
        for i in domain_ids:
            # 从 project_config 中删除
            d_n, d_p = all_id[i]
            del_domains.append(d_n + ':' + str(d_p))
            if d_n in project_find['project_config']['domains']:
                project_find['project_config']['domains'].remove(d_n)
            if d_n + ':' + str(d_p) in project_find['project_config']['domains']:
                project_find['project_config']['domains'].remove(d_n + ':' + str(d_p))

        public.M('sites').where('id=?', (project_id,)).save('project_config',
                                                            json.dumps(project_find['project_config']))
        public.WriteLog(self._log_name, '从项目：{}，批量删除域名:'.format(project_name, del_domains))
        self.set_config(project_name)

        return {
            "status": True,
            "msg": f"删除成功 :{del_domains}",
            "error": {
                not_del["name"]: "项目至少需要一个域名"
            } if not_del is not None else {},
            "success": del_domains
        }
    
    def AddProjectDomain(self, get):
        '''
            @name 为指定项目添加域名
            @author hwliang<2021-08-09>
            @param get<dict_obj>{
                name: string<项目名称>
                domains: list<域名列表>
            }
            @return dict
        '''
        project_name = get.name.strip()
        project_find = self.get_project_find(project_name)
        if not project_find:
            return public.return_error('指定项目不存在')
        project_id = project_find['id']
        domains = get.domains
        flag = False
        res_domains = []
        for domain in domains:
            domain = domain.strip()
            if not domain: continue
            domain_arr = domain.split(':')
            if len(domain_arr) == 1:
                domain_arr.append(80)
                domain += ':80'
            if not public.M('domain').where('name=?', (domain_arr[0],)).count():
                public.M('domain').add('name,pid,port,addtime',
                                       (domain_arr[0], project_id, domain_arr[1], public.getDate()))
                if not domain in project_find['project_config']['domains']:
                    project_find['project_config']['domains'].append(domain)
                public.WriteLog(self._log_name, '成功添加域名{}到项目{}'.format(domain, project_name))
                res_domains.append({"name": domain_arr[0], "status": True, "msg": '添加成功'})
                flag = True
            else:
                public.WriteLog(self._log_name, '添加域名错误，域名{}已存在'.format(domain))
                res_domains.append(
                    {"name": domain_arr[0], "status": False, "msg": '添加失败，域名{}已存在'.format(domain)})
        if flag:
            public.M('sites').where('id=?', (project_id,)).save('project_config', json.dumps(project_find['project_config']))
            self.set_config(project_name)

        return self._ckeck_add_domain(project_name, res_domains)

    def get_project_run_state(self, conf):
        pid_cnt = public.ExecShell(conf["check_sh"])[0].strip("\n")
        if pid_cnt != "0":
            return True
        else:
            return False

    def auto_run(self):
        '''
        @name 开机自动启动
        '''
        # 获取数据库信息
        project_list = public.M('sites').where('project_type=?', ('Python',)).field('name,path,project_config').select()
        get = public.dict_obj()
        success_count = 0
        error_count = 0
        for project in project_list:
            project_config = json.loads(project['project_config'])
            if project_config['auto_run'] in [0, False, '0', None]: continue
            project_name = project['name']
            project_state = self.get_project_run_state(project_config)
            if not project_state:
                get.name = project_name
                result = self.StartProject(get)
                if not result['status']:
                    error_count += 1
                    error_msg = '自动启动Python项目[' + project_name + ']失败!'
                    public.WriteLog(self._log_name, error_msg)
                    public.print_log(error_msg, 'ERROR')
                else:
                    success_count += 1
                    success_msg = '自动启动Python项目[' + project_name + ']成功!'
                    public.WriteLog(self._log_name, success_msg)
                    public.print_log(success_msg, 'INFO')
        if (success_count + error_count) < 1: return False
        dene_msg = '共需要启动{}个Python项目，成功{}个，失败{}个'.format(success_count + error_count, success_count,
                                                                       error_count)
        public.WriteLog(self._log_name, dene_msg)
        public.print_log(dene_msg, 'INFO')
        return True

    # —————————————
    #  日志切割   |
    # —————————————
    def del_crontab(self, name):
        """
        @name 删除项目日志切割任务
        @auther hezhihong<2022-10-31>
        @return
        """
        cron_name = f'[勿删]Python项目[{name}]运行日志切割'
        cron_path = public.GetConfigValue('setup_path') + '/cron/'
        cron_list = public.M('crontab').where("name=?", (cron_name,)).select()
        if cron_list:
            for i in cron_list:
                if not i: continue
                cron_echo = public.M('crontab').where("id=?", (i['id'],)).getField('echo')
                args = {"id": i['id']}
                import crontab
                crontab.crontab().DelCrontab(args)
                del_cron_file = cron_path + cron_echo
                public.ExecShell("crontab -u root -l| grep -v '{}'|crontab -u root -".format(del_cron_file))

    def add_crontab(self, name, log_conf, python_path):
        """
        @name 构造站点运行日志切割任务
        """
        cron_name = f'[勿删]Python项目[{name}]运行日志切割'
        if not public.M('crontab').where('name=?', (cron_name,)).count():
            cmd = '{pyenv} {script_path} {name}'.format(
                pyenv=python_path,
                script_path=self.__log_split_script_py,
                name=name
            )
            args = {
                "name": cron_name,
                "type": 'day' if log_conf["log_size"] == 0 else "minute-n",
                "where1": "" if log_conf["log_size"] == 0 else log_conf["minute"],
                "hour": log_conf["hour"],
                "minute": log_conf["minute"],
                "sName": name,
                "sType": 'toShell',
                "notice": '0',
                "notice_channel": '',
                "save": str(log_conf["num"]),
                "save_local": '1',
                "backupTo": '',
                "sBody": cmd,
                "urladdress": ''
            }
            import crontab
            res = crontab.crontab().AddCrontab(args)
            if res and "id" in res.keys():
                return True, "新建任务成功"
            return False, res["msg"]
        return True

    def _get_python_path(self):
        python_path = ''
        try:
            python_path = public.ExecShell('which btpython')[0].strip("\n")
        except:
            try:
                python_path = public.ExecShell('which python')[0].strip("\n")
            except:
                pass
        return python_path

    def change_cronta(self, name, log_conf):
        """
        @name 更改站点运行日志切割任务
        """
        python_path = self._get_python_path()
        if not python_path: return False
        cronInfo = public.M('crontab').where('name=?', (f'[勿删]Python项目[{name}]运行日志切割',)).find()
        if not cronInfo:
            return self.add_crontab(name, log_conf, python_path)
        import crontab
        recrontabMode = crontab.crontab()
        id = cronInfo['id']
        del (cronInfo['id'])
        del (cronInfo['addtime'])
        cronInfo['sBody'] = '{pyenv} {script_path} {name}'.format(
            pyenv=python_path,
            script_path=self.__log_split_script_py,
            name=name
        )
        cronInfo['where_hour'] = log_conf['hour']
        cronInfo['where_minute'] = log_conf['minute']
        cronInfo['save'] = log_conf['num']
        cronInfo['type'] = 'day' if log_conf["log_size"] == 0 else "minute-n"
        cronInfo['where1'] = '' if log_conf["log_size"] == 0 else log_conf['minute']

        columns = 'where_hour,where_minute,sBody,save,type,where1'
        values = (
        cronInfo['where_hour'], cronInfo['where_minute'], cronInfo['sBody'], cronInfo['save'], cronInfo['type'],
        cronInfo['where1'])
        recrontabMode.remove_for_crond(cronInfo['echo'])
        if cronInfo['status'] == 0: return False, '当前任务处于停止状态,请开启任务后再修改!'
        if not recrontabMode.sync_to_crond(cronInfo):
            return False, '写入计划任务失败,请检查磁盘是否可写或是否开启了系统加固!'
        public.M('crontab').where('id=?', (id,)).save(columns, values)
        public.WriteLog('计划任务', '修改计划任务[' + cronInfo['name'] + ']成功')
        return True, '修改成功'

    def mamger_log_split(self, get):
        """管理日志切割任务
        @author baozi <202-02-27>
        @param:
            get  ( dict ):  包含name, mode, hour, minute
        @return
        """
        name = get.name.strip()
        project_conf = self.__get_project_conf(name_id=name)
        if not project_conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")
        try:
            _log_size = float(get.log_size) if float(get.log_size) >= 0 else 0
            _hour = get.hour.strip() if 0 <= int(get.hour) < 24 else "2"
            _minute = get.minute.strip() if 0 <= int(get.minute) < 60 else '0'
            _num = int(get.num) if 0 < int(get.num) <= 1800 else 180
        except (ValueError, AttributeError):
            _log_size = 0
            _hour = "2"
            _minute = "0"
            _num = 180

        if _log_size != 0:
            _log_size = _log_size * 1024 * 1024
            _hour = 0
            _minute = 5

        log_conf = {
            "log_size": _log_size,
            "hour": _hour,
            "minute": _minute,
            "num": _num
        }
        flag, msg = self.change_cronta(name, log_conf)
        if flag:
            conf_path = '{}/data/run_log_split.conf'.format(public.get_panel_path())
            if os.path.exists(conf_path):
                data = json.loads(public.readFile(conf_path))
            else:
                data = {}
            data[name] = {
                "stype": "size" if bool(_log_size) else "day",
                "log_size": _log_size,
                "limit": _num,
            }
            public.writeFile(conf_path, json.dumps(data))
            project_conf["log_conf"] = log_conf
            pdata = {
                "project_config": json.dumps(project_conf)
            }
            public.M('sites').where('name=?', (name,)).update(pdata)
        return public.returnMsg(flag, msg)

    def set_log_split(self, get):
        """设置日志计划任务状态
        @author baozi <202-02-27>
        @param:
            get  ( dict ):  包含项目名称name
        @return  msg : 操作结果
        """
        name = get.name.strip()
        project_conf = self.__get_project_conf(name_id=name)
        if not project_conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")
        cronInfo = public.M('crontab').where('name=?', (f'[勿删]Python项目[{name}]运行日志切割',)).find()
        if not cronInfo:
            return public.returnMsg(False, "该项目没有设置运行日志的切割任务")

        status_msg = ['停用', '启用']
        status = 1
        import crontab
        recrontabMode = crontab.crontab()

        if cronInfo['status'] == status:
            status = 0
            recrontabMode.remove_for_crond(cronInfo['echo'])
        else:
            cronInfo['status'] = 1
            if not recrontabMode.sync_to_crond(cronInfo):
                return public.returnMsg(False, '写入计划任务失败,请检查磁盘是否可写或是否开启了系统加固!')

        public.M('crontab').where('id=?', (cronInfo["id"],)).setField('status', status)
        public.WriteLog('计划任务', '修改计划任务[' + cronInfo['name'] + ']状态为[' + status_msg[status] + ']')
        return public.returnMsg(True, '设置成功')

    def get_log_split(self, get):
        """获取站点的日志切割任务
        @author baozi <202-02-27>
        @param:
            get  ( dict ):   name
        @return msg : 操作结果
        """

        name = get.name.strip()
        project_conf = self.__get_project_conf(name_id=name)
        if not project_conf:
            return public.returnMsg(False, "没有该项目，请尝试刷新页面")
        cronInfo = public.M('crontab').where('name=?', (f'[勿删]Python项目[{name}]运行日志切割',)).find()
        if not cronInfo:
            return public.returnMsg(False, "该项目没有设置运行日志的切割任务")

        res = project_conf["log_conf"]
        res["status"] = cronInfo["status"]
        return {"status": True, "data": res}

    # ——————————————————————————————————————————————
    #   对用户的项目目录进行预先读取， 获取有效信息   |
    # ——————————————————————————————————————————————

    def _get_requirements_by_readme_file(self, path):
        readme_rep = r"^[Rr][Ee][Aa][Dd][Mm][Ee]"
        readme_files = self.__search_file(readme_rep, path, this_type="file")
        if not readme_files: return None

        # 从readfile找安装依赖包文件
        target_path = None
        requirements_rep = r'pip\s{0,3}install\s{0,3}-r\s{0,3}(?P<target>[A-z0-9_/]*\.txt)'
        for i in readme_files:
            file = public.readFile(i)
            target = re.search(requirements_rep, file)
            if target:
                requirements_path = os.path.join(path, target.group("target"))
                if os.path.exists(requirements_path) and os.path.isfile(requirements_path):
                    target_path = requirements_path
                    break
        if not target_path:
            return None
        return target_path

    def _get_requirements_file(self, path):
        requirements_rep = r"^requirements\.txt$"
        requirements_path = self.__search_file(requirements_rep, path, this_type="file")
        if not requirements_path:
            requirements_rep2 = r"^[Rr]equirements?"
            requirements_dir = self.__search_file(requirements_rep2, path, this_type="dir")
            if requirements_dir:
                return self._get_requirements_file(self, requirements_dir)
            return None
        return requirements_path[0]

    def _get_framework_from_requirements(self, requirements_path):
        file_body = public.readFile(requirements_path)
        dj_rep = r"[Dd]jango\s{0,3}"
        flask_rep = r"[Ff]lask\s{0,3}"
        sanic_rep = r"[Ss]anic\s{0,3}"
        if re.search(dj_rep, file_body):
            return "django"
        if re.search(flask_rep, file_body):
            return "flask"
        if re.search(sanic_rep, file_body):
            return "sanic"
        return "python"

    def _get_run_file(self, path, sub=0):
        runfile_rep = r"^wsgi\.py$|^asgi\.py$|^app\.py$"
        runfile = self.__search_file(runfile_rep, path, this_type="file")

        for i in runfile:
            if i.endswith("wsgi.py"):
                return i, "wsgi"

        for i in runfile:
            if i.endswith("asgi.py"):
                return i, "asgi"
        if runfile:
            return runfile[0], "wsgi"
        if not sub:
            return None, None

        sub_rep = r'.*'
        sub_dir = self.__search_file(sub_rep, path, this_type="dir")
        for i in sub_dir:
            a, b = self._get_run_file(i, sub - 1)
            if a and b:
                return a, b

        return None, None

    def __get_runfile(self, path, is_sanic, sub=0):
        py_rep = r".*\.py$"
        sanic_rep = r"\n[A-Za-z0-9_]*\s{0,3}=\s{0,3}Sanic\s{0,3}\([^\n\(\)]*(\([^\n\(\)]*\)[^\n\(\)]*)*\)[^\n]*\n"
        flask_rep = r"\n[A-Za-z0-9_]*\s{0,3}=\s{0,3}(create|make)_app\s{0,3}\([^\n\(\)]*(\([^\n\(\)]*\)[^\n\(\)]*)*\)[^\n]*\n"
        runfile = self.__search_file(py_rep, path, this_type="file", exclude="test")

        for i in runfile:
            file = public.readFile(i)
            if re.search(sanic_rep if is_sanic else flask_rep, file):
                return i

        if not sub:
            return None

        sub_rep = r'.*'
        sub_dir = self.__search_file(sub_rep, path, this_type="dir", exclude="test")
        for i in sub_dir:
            a = self.__get_runfile(i, is_sanic, sub - 1)
            if a:
                return a

        return None

    def get_info(self, get):
        """ 对用户的项目目录进行预先读取， 获取有效信息
        @author baozi <202-03-10>
        @param:
            get  ( dict ):  请求信息，包含path，路径
        @return  _type_ : _description_
        """
        if "path" not in get:
            return public.returnMsg(False, "没有选择项目路径信息")
        else:
            path = get.path.strip()
        if path[-1] == "/": path = path[:-1]
        if not os.path.exists(path):
            return False, "项目目录错误"

        # 找requirement文件
        requirement_path = self._get_requirements_file(path)
        if not requirement_path:
            requirement_path = self._get_requirements_by_readme_file(path)

        runfile, xsgi = self._get_run_file(path, 1)

        if not requirement_path:
            return {
                "doubt": True,
                "framework": None,
                "requirement_path": None,
                "runfile": runfile,
                "xsgi": xsgi,
                "stype": None
            }

        framework = self._get_framework_from_requirements(requirement_path)
        doubt = False
        if framework == "django":
            pass
        elif framework == "python":
            doubt = True
        elif framework == "sanic":
            xsgi = "asgi"
            if not runfile:
                runfile = self.__get_runfile(path, is_sanic=True, sub=1)
            if not runfile:
                doubt = True
                runfile = self.__get_Sanic_file(path, sub=1)
        else:
            if not runfile:
                runfile = self.__get_runfile(path, is_sanic=False, sub=1)
            if not runfile:
                doubt = True
                runfile = self.__build_flask_runfile(path)
            if not xsgi:
                xsgi = "wsgi"

        return {
            "doubt": doubt,
            "framework": framework,
            "requirement_path": requirement_path,
            "runfile": runfile,
            "xsgi": xsgi,
            "stype": "gunicorn" if framework != "python" else None
        }

    def __get_Sanic_file(self, path, sub=0):
        py_rep = r".*\.py$"
        sanic_rep = r"\nfrom\s{1,3}sanic\s{1,3}import\s{1,3}([A-Za-z]*,\s{0,3}){0,12}Sanic,? {0,3}([A-Za-z]*,\s{0,3}){0,12}[^\n]*\n"
        runfile = self.__search_file(py_rep, path, this_type="file", exclude="test")

        for i in runfile:
            file = public.readFile(i)
            if re.search(sanic_rep, file):
                return i

        if not sub:
            return None

        sub_rep = r'.*'
        sub_dir = self.__search_file(sub_rep, path, this_type="dir", exclude="test")
        for i in sub_dir:
            a = self.__get_Sanic_file(i, sub - 1)
            if a:
                return a

        return None

    def __build_flask_runfile(self, path):
        app_module, app_func = self.__find_flask_app_func(path, 1)
        if not app_module:
            return None
        name = path.rsplit(os.sep, 1)[1]
        app_module = app_module.replace(path + os.sep, "").strip()
        app_module = app_module.replace(os.sep, ".")
        app_file = """# 文件生成时间：{date}
# 文件生产者:bt.python_project
# 由于未找到启动文件,故调用create_app自动生成入口文件

from {app_module} import {app_func}

app = {app_func}('{name}')\n"""
        app_file = app_file.format(
            app_module=app_module,
            app_func=app_func,
            name=name,
            date=public.format_date()
        )
        run_file = os.path.join(path, "app.py")
        public.writeFile(run_file, app_file)

        return run_file

    def __find_flask_app_func(self, path, sub):
        py_rep = r".*\.py$"
        create_rep = r"\n\s{0,3}def\s{0,3}create_app\s{0,3}\([^\n\(\)]*(\([^\n\(\)]*\)[^\n\(\)]*)*\)[^\n]*\n"
        make_rep = r"\n\s{0,3}def\s{0,3}make_app\s{0,3}\([^\n\(\)]*(\([^\n\(\)]*\)[^\n\(\)]*)*\)[^\n]*\n"
        runfile = self.__search_file(py_rep, path, this_type="file")

        for i in runfile:
            file = public.readFile(i)
            if re.search(create_rep, file):
                if i.endswith("__init__.py"):
                    return path, "create_app"
                else:
                    return i, "create_app"
            if re.search(make_rep, file):
                if i.endswith("__init__.py"):
                    return path, "make_app"
                else:
                    return i, "make_app"

        if not sub:
            return None, None

        sub_rep = r'.*'
        sub_dir = self.__search_file(sub_rep, path, this_type="dir", exclude="test")
        for i in sub_dir:
            a, b = self.__find_flask_app_func(i, sub - 1)
            if a:
                return a, b

        return None, None

    def __search_file(self, name_rep, path, this_type="file", exclude=None) -> str:
        target_names = []
        for f_name in os.listdir(path):
            f_name.encode('utf-8')
            target_name = re.search(name_rep, f_name)
            if target_name:
                target_names.append(f_name)

        res = []
        for i in target_names:
            if exclude and i.find(exclude) != -1:
                continue
            _path = os.path.join(path, i)
            if this_type == "file" and os.path.isfile(_path):
                res.append(_path)
                continue
            if this_type == "dir" and not os.path.isfile(_path):
                res.append(_path)
                continue

        return res

    def for_split(self, logsplit, project):
        """日志切割方法调用
        @author baozi <202-03-20>
        @param:
            logsplit  ( LogSplit ):  日志切割方法，传入 pjanme:项目名称 sfile:日志文件路径 log_prefix:产生的日志文件前缀
            project  ( dict ):  项目内容
        @return
        """
        if project['project_config']["stype"] == "python":
            log_file = project['project_config']["logpath"] + "/error.log"
            logsplit(project["name"], log_file, project["name"])
        elif project['project_config']["stype"] == "gunicorn":
            log_file = project['project_config']["logpath"] + "/gunicorn_error.log"
            logsplit(project["name"], log_file, project["name"] + "_error")
            log_file2 = project['project_config']["logpath"] + "/gunicorn_acess.log"
            logsplit(project["name"], log_file2, project["name"] + "_acess")
        else:
            log_file = project['project_config']["logpath"] + "/uwsgi.log"
            logsplit(project["name"], log_file, project["name"])

    def _ckeck_add_domain(self, site_name, domains):
        from panelSite import panelSite
        ssl_data = panelSite().GetSSL(type("get", tuple(), {"siteName": site_name})())
        if not ssl_data["status"]: return {"domains": domains}
        domain_rep = []
        for i in ssl_data["cert_data"]["dns"]:
            if i.startswith("*"):
                _rep = "^[^\.]+\." + i[2:].replace(".", "\.")
            else:
                _rep = "^" + i.replace(".", "\.")
            domain_rep.append(_rep)
        no_ssl = []
        for domain in domains:
            if not domain["status"]: continue
            for _rep in domain_rep:
                if re.search(_rep, domain["name"]):
                    break
            else:
                no_ssl.append(domain["name"])
        if no_ssl:
            return {
                "domains": domains,
                "not_ssl": no_ssl,
                "tip": "本站点已启用SSL证书,但本次添加的域名：{}，无法匹配当前证书，如有需求，请重新申请证书。".format(
                    str(no_ssl))
            }
        return {"domains": domains}

    # ————————————————————————————————————
    #              虚拟终端               |
    # ————————————————————————————————————

    def set_export(self, project_name):
        conf = self.__get_project_conf(project_name)
        if not conf:
            return False, "没有该项目\r\n"

        v_path_bin = conf["vpath"] + "/bin"
        if not os.path.exists(conf["path"]):
            return False, "项目文件丢失\r\n"
        if not os.path.exists(v_path_bin):
            return False, "没有该虚拟环境\r\n"
        pre_v_path_bin = self.__prevent_re(v_path_bin)
        msg = "虚拟环境已就绪！"  # 使用中文的感叹号
        _cd_sh = "clear\ncd %s\n" % conf["path"]
        _sh = 'if [[ "$PATH" =~ "^%s:.*" ]]; then { echo "%s"; } else { export PATH="%s:${PATH}"; echo "%s"; } fi\n' % (
            pre_v_path_bin, msg, v_path_bin, msg
        )
        return True, _sh + _cd_sh
    
    @staticmethod
    def _get_pid_by_ps(check_sh: str) -> List[int]:
        _check_sh = check_sh.rsplit("|", 1)[0]
        _check_sh += "| awk '{print $2}'"
        s, e = public.ExecShell(_check_sh)
        pids = [int(i) for i in s.split("\n") if bool(i.strip())]
        return pids

    def get_mem_and_cpu(self, conf):
        pids = self._get_pid_by_ps(conf["check_sh"])
        mem, cpusum = 0, 0
        for pid in pids:
            res = self.get_process_info_by_pid(pid)
            if "memory_used" in res:
                mem += res["memory_used"]
            if "cpu_percent" in res:
                cpusum += res["cpu_percent"]
        public.print_log([mem, cpusum])
        return mem, cpusum

    def get_process_info_by_pid(self, pid):
        process_info = {}
        try:
            if not os.path.exists('/proc/{}'.format(pid)): return process_info
            p = psutil.Process(pid)
            status_ps = {'sleeping':'睡眠','running':'活动'}
            with p.oneshot():
                p_mem = p.memory_full_info()
                if p_mem.uss + p_mem.rss + p_mem.pss + p_mem.data == 0: return process_info
                p_state = p.status()
                if p_state in status_ps:
                    p_state = status_ps[p_state]
                # process_info['exe'] = p.exe()
                process_info['name'] = p.name()
                process_info['pid'] = pid
                process_info['ppid'] = p.ppid()
                process_info['create_time'] = int(p.create_time())
                process_info['status'] = p_state
                process_info['user'] = p.username()
                process_info['memory_used'] = p_mem.uss
                process_info['cpu_percent'] = self.get_cpu_precent(p)
                # process_info['io_write_bytes'], process_info['io_read_bytes'] = self.get_io_speed(p)
                # process_info['connections'] = self.format_connections(p.connections())
                # process_info['connects'] = self.get_connects(pid)
                # process_info['open_files'] = self.list_to_dict(p.open_files())
                process_info['threads'] = p.num_threads()
                process_info['exe'] = ' '.join(p.cmdline())
                return process_info
        except:
            return process_info

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
            cache.set(skey,[process_cpu_time,time.time()],3600)
            old_cpu_times = cache.get(skey)
            process_cpu_time = self.get_process_cpu_time(p.cpu_times())

        old_process_cpu_time = old_cpu_times[0]
        old_time = old_cpu_times[1]
        new_time = time.time()
        cache.set(skey,[process_cpu_time,new_time],3600)
        percent = round(100.00 * (process_cpu_time - old_process_cpu_time) / (new_time - old_time) / psutil.cpu_count(),2)
        return percent

    @staticmethod
    def get_process_cpu_time(cpu_times):
        cpu_time = 0.00
        for s in cpu_times: cpu_time += s
        return cpu_time


class PyenvSshTerminal(ssh_terminal.ssh_terminal):
    _set_python_export = None

    def send(self):
        '''
            @name 写入数据到缓冲区
            @author hwliang<2020-08-07>
            @return void
        '''
        try:
            while self._ws.connected:
                if self._s_code:
                    time.sleep(0.1)
                    continue
                client_data = self._ws.receive()
                if not client_data: continue
                if client_data == '{}': continue
                if len(client_data) > 10:
                    if client_data.find('{"host":"') != -1:
                        continue
                    if client_data.find('"resize":1') != -1:
                        self.resize(client_data)
                        continue
                    if client_data.find('{"pj_name"') != -1:
                        client_data = self.__set_export(client_data)
                        if not client_data:
                            continue

                public.print_log("传入：" + client_data)
                self._ssh.send(client_data)
        except Exception as ex:
            ex = str(ex)

            if ex.find('_io.BufferedReader') != -1:
                self.debug('从websocket读取数据发生错误，正在重新试')
                self.send()
                return
            elif ex.find('closed') != -1:
                self.debug('会话已中断')
            else:
                self.debug('写入数据到缓冲区发生错误: {}'.format(ex))

        if not self._ws.connected:
            self.debug('客户端已主动断开连接')
        public.print_log("close7")
        self.close()

    def __set_export(self, client_data):
        _data = json.loads(client_data)
        flag, msg = main().set_export(_data["pj_name"])
        if not flag:
            self._ws.send(msg)
            return None
        return msg
