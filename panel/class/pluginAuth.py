#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: hwliang <hwl@bt.cn>
# +-------------------------------------------------------------------

#+--------------------------------------------------------------------
#|   插件认证模块
#+--------------------------------------------------------------------

import sys as plu_sys
import os as plu_os
import json as plu_json
import public as plu_public
import time

from ctypes import cdll as plu_cdll
from ctypes import c_char_p as plu_c_char_p

from types import ModuleType as plu_ModuleType

machine = plu_os.uname().machine
lib_file = "/www/server/panel/class/libAuth.x86-64.so"
if machine in ['aarch64','arm','aarch'] or machine.find('arm') != -1:
    if plu_public.get_sysbit() == 64:
        lib_file = "/www/server/panel/class/libAuth.aarch64.so"
    else:
        lib_file = "/www/server/panel/class/libAuth.aarch.so"
if machine in ['i386','i686']:
    lib_file = "/www/server/panel/class/libAuth.x86.so"

if not plu_os.path.exists(lib_file): raise plu_public.PanelError("不兼容的操作系统架构，推荐使用aarch64/x86-64架构的操作系统!")
_lib_i46L4Znt7sRndnDx = plu_cdll.LoadLibrary(lib_file)

class Plugin:
    __plugin_info = None
    __plugin_name = None
    __plugin_object = None
    __plugin_list = None  
    __panel_path = '/www/server/panel'
    __plugin_path = __panel_path + '/plugin/'
    __plugin_save_file = __panel_path + '/data/plugin_bin.pl'
    __api_root_url = 'https://api.bt.cn'    
    __api_url = __api_root_url+ '/panel/get_plugin_list'
    __plugin_timeout = 3600
    __is_php = False
    __pid = 0
    __dict__ = None
    
    
    def __init__(self,init_plugin_name = None):
        '''
            @name 实例化插件对像
            @author hwliang<2021-06-15>
            @param init_plugin_name<string> 插件名称
            @return Plguin<object>
        '''
        if not init_plugin_name is False:
            if not init_plugin_name:
                raise ValueError('参数错误,plugin_name少需要一个有效参数')

            self.__plugin_info = plu_public.get_plugin_find(init_plugin_name)
            if self.__plugin_info:
                self.__plugin_name = self.__plugin_info['name']
            else:
                self.__plugin_info = {}
                self.__plugin_name = init_plugin_name
            if 'pid' in self.__plugin_info:
                self.__pid = self.__plugin_info['pid']
            self.__plugin_object = self.__compile()


    def get_mac_address(self):
        import uuid
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e+2] for e in range(0,11,2)])
        
    def get_plugin_list(self,upgrade_force = False):
        '''
            @name 获取插件列表
            @author hwliang<2021-06-15>
            @param upgrade_force<bool> 是否强制重新获取列表
            @return dict
        '''
        is_cloud = True
        if (plu_os.path.exists(self.__plugin_save_file) and not upgrade_force) or plu_public.is_local():
            list_body = plu_public.get_plugin_bin(self.__plugin_save_file,self.__plugin_timeout)
            if list_body: is_cloud = False
        if is_cloud:
            if plu_public.is_local(): raise plu_public.PanelError('当前为离线模式，无法从云端获取软件列表，请先获取软件列表后再开启离线模式!')
            pdata = plu_public.get_user_info()
            pdata['mac'] = self.get_mac_address()
            try:
                self.__flush_plugin_auth()
                list_body = plu_public.HttpPost(self.__api_url,pdata).encode()
                plu_public.writeFile(self.__plugin_save_file,list_body,'wb+')
            except:
                try:
                    list_body = plu_public.get_plugin_bin(self.__plugin_save_file,self.__plugin_timeout)
                    if not list_body: raise plu_public.PanelError('无法连接宝塔云端服务器!')
                except:
                    raise plu_public.PanelError('无法连接宝塔云端服务器!')
        try:
            plugin_list_data = self.__data_decode(list_body)
            self.__plugin_list = plu_json.loads(plugin_list_data)
        except:
            if plu_os.path.exists(self.__plugin_save_file): plu_os.remove(self.__plugin_save_file)
            raise plu_public.PanelError("解析软件列表发生错误，已尝试自动修复，请刷新页面重试!")
        return self.__plugin_list


    
    def __check_plugin_auth(self):
        '''
            @name 检测指定插件是否有授权
            @author hwliang<2021-06-17>
            @param pid<int> PID
            @return int
        '''
        if not self.__pid: return False
        if int(self.__pid) >= 600800000: 
            if self.__plugin_info['endtime'] > 0 and self.__plugin_info['endtime'] < time.time():
                return plu_public.returnMsg(False,'插件[{}]未授权或授权已到期!'.format(self.__plugin_info['title']))
            return False
        global _lib_i46L4Znt7sRndnDx
        _lib_i46L4Znt7sRndnDx.check_plugin_auth.argtypes = [plu_c_char_p]
        _lib_i46L4Znt7sRndnDx.check_plugin_auth.restype = plu_c_char_p
        check_pid = str(self.__pid).encode()
        check_rs = _lib_i46L4Znt7sRndnDx.check_plugin_auth(check_pid)
        result =  plu_json.loads(check_rs)
        if result['status']: return False
        return result
    
    def __flush_plugin_auth(self):
        '''
            @name 刷新授权列表
            @author hwliang<2021-06-17>
            @param pid<int> PID
            @return int
        '''
        global _lib_i46L4Znt7sRndnDx
        _lib_i46L4Znt7sRndnDx.flush_plugin_auth.argtypes = [plu_c_char_p]
        _lib_i46L4Znt7sRndnDx.flush_plugin_auth.restype = plu_c_char_p
        result =  plu_json.loads(_lib_i46L4Znt7sRndnDx.flush_plugin_auth(b'1'))
        if result['status']: return True
        raise plu_public.PanelError(result)
    

    
    def __data_decode(self,aes_data_body):
        '''
            @name 解密数据
            @author hwliang<2021-06-17>
            @param data<bytes> 被解密的数据
            @return bytes
        '''
        global _lib_i46L4Znt7sRndnDx
        _lib_i46L4Znt7sRndnDx.lmJooiTOyupKaDzEbjAAHaGmfsDhLakV.argtypes = [plu_c_char_p]
        _lib_i46L4Znt7sRndnDx.lmJooiTOyupKaDzEbjAAHaGmfsDhLakV.restype = plu_c_char_p
        result_data = []
        for d_aes_base_data in aes_data_body.split(b"\n"):
            if not d_aes_base_data: continue
            de_data = _lib_i46L4Znt7sRndnDx.lmJooiTOyupKaDzEbjAAHaGmfsDhLakV(d_aes_base_data)
            if de_data == b'get mac error':
                raise plu_public.PanelError('请先绑定宝塔帐号!')
            result_data.append(de_data)
        return b"".join(result_data)

    def __get_plugin_main_script(self):
        '''
            @name 获取插件主程序脚本
            @author hwliang<2021-06-15>
            @return string
        '''
        plugin_body,is_return = plu_public.get_plugin_script(self.__plugin_name,self.__plugin_path)
        
        if is_return: return plugin_body,is_return
        
        plugin_body = self.__data_decode(plugin_body)
        if plugin_body.find(b'import') == -1:
            plugin_body = plu_public.re_download_main(self.__plugin_name,self.__plugin_path)
            plugin_body = self.__data_decode(plugin_body)
            if plugin_body.find(b'import') == -1:
                raise plu_public.PanelError('插件程序解析失败!')
        return plugin_body,is_return

    
    def __compile(self):
        '''
            @name 编译插件主程序
            @author hwliang<2021-06-16>
            @param plugin_code<string> 主程序代码
            @return object
        '''
        plugin_obj = None
        is_debug = plu_public.is_debug()

        # 是否要求一次性重新加载插件
        reload_file = plu_os.path.join(self.__panel_path,'data/{}.pl'.format(self.__plugin_name))
        if plu_os.path.exists(reload_file):
            is_debug = True
            plu_os.remove(reload_file)

        if not is_debug: # Debug模式每次访问都重新加载
            plugin_obj = plu_sys.modules.get(self.__plugin_name + '_main',None)
        
        if not plugin_obj: #是否需要重新加载
            plugin_code,is_return = self.__get_plugin_main_script()
            
            sys_path = self.__plugin_path + '/' + self.__plugin_name
            if not sys_path in plu_sys.path: plu_sys.path.insert(0,sys_path)
            if plugin_code: # 是否为Python代码
                if not is_debug and is_return:
                    plugin_obj = __import__(self.__plugin_name + '_main')
                else:
                    plugin_obj = plu_sys.modules.setdefault(self.__plugin_name, plu_ModuleType(self.__plugin_name))
                    plugin_code_object = compile(plugin_code,self.__plugin_name, 'exec')
                    plugin_obj.__file__ = self.__plugin_name
                    plugin_obj.__package__ = ''
                    exec(plugin_code_object, plugin_obj.__dict__)
            else:
                plugin_obj,self.__is_php = plu_public.get_plugin_main_object(self.__plugin_name,sys_path)
                if self.__is_php: return plugin_obj

        return getattr(plugin_obj,self.__plugin_name + '_main')()

    def exec_fun(self,get_args,def_name = None):
        '''
            @name 执行指定方法
            @author hwliang<2021-06-16>
            @param def_name<string> 方法名称
            @param get_args<dict_obj> POST/GET参数对像
            @return mixed
        '''
        auth_res = self.__check_plugin_auth()
        if auth_res: return auth_res
        if self.__is_php:
            return self.__plugin_object.exec_php_script(get_args)
        if not def_name: def_name = get_args.s.strip()
        try:
            return getattr(self.__plugin_object,def_name)(get_args)
        except:
            return plu_public.get_error_object(self.__plugin_info['title'])

    def get_fun(self,def_name):
        '''
            @name 获取函对像
            @author hwliang<2021-06-28>
            @param def_name<string> 函数名称
            @return func_object
        '''
        auth_res = self.__check_plugin_auth()
        if auth_res: return auth_res
        access_defs_list =  getattr(self.__plugin_object,'access_defs',[])
        if not def_name in access_defs_list:
            return None
        return getattr(self.__plugin_object,def_name,None)


    def isdef(self,def_name):
        '''
            @name 指定方法是否存在
            @author hwliang<2021-06-16>
            @param def_name<string> 方法名称
            @return bool
        '''
        if self.__is_php: return True
        return hasattr(self.__plugin_object,def_name)
        
    def __dir__(self):
        return ''
        
