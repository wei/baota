# coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2017 宝塔软件(http:#bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: zouhw <zhw@bt.cn>
# -------------------------------------------------------------------

# ------------------------------
# 项目管理控制器
# ------------------------------
import os ,public ,json ,re ,time #line:13
class main :#line:15
    def __init__ (OOO000OO00O0OO0O0 ):#line:17
        pass #line:18
    def model (O00O0O0000OOO000O ,OO00OO000OO0O0000 ):#line:20
        ""#line:29
        import panelPlugin #line:30
        O0OOOO000000OO0O0 =public .to_dict_obj ({})#line:31
        O0OOOO000000OO0O0 .focre =1 #line:32
        O00OOO0O0O0O0O00O =panelPlugin .panelPlugin ().get_soft_list (O0OOOO000000OO0O0 )#line:33
        __OOO0000OOO00000O0 =int (O00OOO0O0O0O0O00O ['ltd'])>1 #line:34
        __OO0O00O00O0OOOOOO =public .to_string ([20307 ,39564 ,26102 ,38388 ,32467 ,26463 ,65292 ,32487 ,32493 ,20351 ,29992 ,35831 ,36141 ,20080 ,20225 ,19994 ,29256 ,65281 ])#line:36
        if time .time ()>1665904796 :#line:37
            if not __OOO0000OOO00000O0 :#line:38
                return public .returnMsg (False ,__OO0O00O00O0OOOOOO )#line:39
        try :#line:40
            OO00OO000OO0O0000 .def_name =OO00OO000OO0O0000 .dk_def_name #line:41
            OO00OO000OO0O0000 .mod_name =OO00OO000OO0O0000 .dk_model_name #line:42
            if OO00OO000OO0O0000 ['mod_name']in ['base']:return public .return_status_code (1000 ,'错误的调用!')#line:43
            public .exists_args ('def_name,mod_name',OO00OO000OO0O0000 )#line:44
            if OO00OO000OO0O0000 ['def_name'].find ('__')!=-1 :return public .return_status_code (1000 ,'调用的方法名称中不能包含“__”字符')#line:45
            if not re .match (r"^\w+$",OO00OO000OO0O0000 ['mod_name']):return public .return_status_code (1000 ,'调用的模块名称中不能包含\w以外的字符')#line:46
            if not re .match (r"^\w+$",OO00OO000OO0O0000 ['def_name']):return public .return_status_code (1000 ,'调用的方法名称中不能包含\w以外的字符')#line:47
        except :#line:48
            return public .get_error_object ()#line:49
        O00OO0OO0OO0OOO00 ="dk_{}".format (OO00OO000OO0O0000 ['mod_name'].strip ())#line:51
        O0OOO00OOO0OOO0OO =OO00OO000OO0O0000 ['def_name'].strip ()#line:52
        O0000000OOO0OO000 ="{}/projectModel/bt_docker/{}.py".format (public .get_class_path (),O00OO0OO0OO0OOO00 )#line:55
        if not os .path .exists (O0000000OOO0OO000 ):#line:56
            return public .return_status_code (1003 ,O00OO0OO0OO0OOO00 )#line:57
        OO0OO0O0OO0OO0OOO =public .get_script_object (O0000000OOO0OO000 )#line:59
        if not OO0OO0O0OO0OO0OOO :return public .return_status_code (1000 ,'没有找到{}模型'.format (O00OO0OO0OO0OOO00 ))#line:60
        O0O0OO0OO00OO00OO =getattr (OO0OO0O0OO0OO0OOO .main (),O0OOO00OOO0OOO0OO ,None )#line:61
        if not O0O0OO0OO00OO00OO :return public .return_status_code (1000 ,'没有在{}模型中找到{}方法'.format (O00OO0OO0OO0OOO00 ,O0OOO00OOO0OOO0OO ))#line:62
        O0000OO0000O000OO ='{}_{}_LAST'.format (O00OO0OO0OO0OOO00 .upper (),O0OOO00OOO0OOO0OO .upper ())#line:76
        OOOO00000OOO0O0O0 =public .exec_hook (O0000OO0000O000OO ,OO00OO000OO0O0000 )#line:77
        if isinstance (OOOO00000OOO0O0O0 ,public .dict_obj ):#line:78
            O0O0O00000000O0OO =OOOO00000OOO0O0O0 #line:79
        elif isinstance (OOOO00000OOO0O0O0 ,dict ):#line:80
            return OOOO00000OOO0O0O0 #line:81
        elif isinstance (OOOO00000OOO0O0O0 ,bool ):#line:82
            if not OOOO00000OOO0O0O0 :#line:83
                return public .return_data (False ,{},error_msg ='前置HOOK中断操作')#line:84
        O00O0OO00OO00OO0O =O0O0OO0OO00OO00OO (OO00OO000OO0O0000 )#line:87
        O0000OO0000O000OO ='{}_{}_END'.format (O00OO0OO0OO0OOO00 .upper (),O0OOO00OOO0OOO0OO .upper ())#line:90
        OO000OOO00OOOOO00 =public .to_dict_obj ({'args':OO00OO000OO0O0000 ,'result':O00O0OO00OO00OO0O })#line:94
        OOOO00000OOO0O0O0 =public .exec_hook (O0000OO0000O000OO ,OO000OOO00OOOOO00 )#line:95
        if isinstance (OOOO00000OOO0O0O0 ,dict ):#line:96
            O00O0OO00OO00OO0O =OOOO00000OOO0O0O0 ['result']#line:97
        return O00O0OO00OO00OO0O #line:98
