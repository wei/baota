#coding: utf-8
#-------------------------------------------------------------------
# 宝塔Linux面板
#-------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
#-------------------------------------------------------------------
# Author: hwliang <hwl@bt.cn>
#-------------------------------------------------------------------

# 系统防火墙
#------------------------------
import sys, os, json, re, time, sqlite3
from xml.etree.ElementTree import ElementTree, Element
from safeModel.base import safeBase
from flask import send_file, abort

os.chdir("/www/server/panel")
sys.path.append("class/")
import public


class main(safeBase):

    __isFirewalld = False
    __isUfw = False
    __Obj = None
    _ip_list = []
    _port_list = []
    _ufw_default = '/etc/default/ufw'
    _ufw_sysctl = '/etc/ufw/sysctl.conf'
    _ufw_before = '/etc/ufw/before.rules'

    _trans_status = "/www/server/panel/plugin/firewall/status.json"
    _rule_path = "/www/server/panel/plugin/firewall/"
    _ips_path = "/www/server/panel/plugin/firewall/ips.txt"
    _country_path = "/www/server/panel/plugin/firewall/country.txt"
    _white_list_file = "/www/server/panel/plugin/firewall/whitelist.txt"  # 证书验证IP

    _white_list = []
    _firewall_create_tip = '{}/data/firewall_sqlite.pl'.format(
        public.get_panel_path())

    def __init__(self):
        if os.path.exists('/usr/sbin/firewalld'): self.__isFirewalld = True
        if os.path.exists('/usr/sbin/ufw'): self.__isUfw = True

        self.get_old_rule()

        if not os.path.exists(self._trans_status):
            ret = {"status": "close"}
            public.writeFile(self._trans_status, json.dumps(ret))

        if not os.path.exists(self._firewall_create_tip):
            Sqlite()
            public.writeFile(self._firewall_create_tip, '')

    def get_old_rule(self):
        """
        @兼容防火墙插件规则
        """

        self._rule_path = self._rule_path.replace('plugin', 'data')
        if not os.path.exists(self._rule_path): os.makedirs(self._rule_path)

        if os.path.exists(self._trans_status):
            n_path = self._trans_status.replace('plugin', 'data')
            if not os.path.exists(n_path):
                public.writeFile(n_path, public.readFile(self._trans_status))

        if os.path.exists(self._ips_path):
            n_path = self._ips_path.replace('plugin', 'data')
            if not os.path.exists(n_path):
                public.writeFile(n_path, public.readFile(self._ips_path))

        if os.path.exists(self._white_list_file):
            n_path = self._white_list_file.replace('plugin', 'data')
            if not os.path.exists(n_path):
                public.writeFile(n_path,
                                 public.readFile(self._white_list_file))

        if os.path.exists(self._country_path):
            n_path = self._country_path.replace('plugin', 'data')
            if not os.path.exists(n_path):
                public.writeFile(n_path, public.readFile(self._country_path))

        self._white_list_file = self._white_list_file.replace('plugin', 'data')
        self._country_path = self._country_path.replace('plugin', 'data')
        self._ips_path = self._ips_path.replace('plugin', 'data')
        self._trans_status = self._trans_status.replace('plugin', 'data')

    def install_sys_firewall(self, get):
        """
        @安装系统防火墙
        """

        res = public.install_sys_firewall()
        if res:
            return public.returnMsg(True, '安装成功')
        return public.returnMsg(False, '安装失败')

    def get_firewall_info(self, get):
        """
        @name 获取防火墙统计
        """
        data = {}
        data['port'] = public.M('firewall_new').count()
        data['ip'] = public.M('firewall_ip').count()
        data['trans'] = public.M('firewall_trans').count()
        data['country'] = public.M('firewall_country').count()

        isPing = True
        try:
            file = '/etc/sysctl.conf'
            conf = public.readFile(file)
            rep = r"#*net\.ipv4\.icmp_echo_ignore_all\s*=\s*([0-9]+)"
            tmp = re.search(rep, conf).groups(0)[0]
            if tmp == '1': isPing = False
        except:
            isPing = True

        data['ping'] = isPing
        data['status'] = public.get_firewall_status()
        return data

    # 服务状态获取
    def get_firewall_status(self, get):
        if self.__isUfw:
            res = public.ExecShell('ufw status verbose')[0]
            if res.find('inactive') != -1: return False
            return True

        if self.__isFirewalld:
            res = public.ExecShell("systemctl status firewalld")[0]
            if res.find('active (running)') != -1: return True
            if res.find('disabled') != -1: return False
            if res.find('inactive (dead)') != -1: return False
        else:
            res = public.ExecShell("/etc/init.d/iptables status")[0]
            if res.find('not running') != -1: return False
            return True
        return False

    # 服务状态控制
    def firewall_admin(self, get):
        order = ['reload', 'restart', 'stop', 'start']
        if not get.status in order:
            return public.returnMsg(False, '未知控制命令!')
        names = ["重载", "重启", "停止", "启动"]
        result = dict(zip(order, names))
        if self.__isUfw:
            if get.status == "stop":
                public.ExecShell('/usr/sbin/ufw disable')
            elif get.status == "start":
                public.ExecShell('/usr/sbin/ufw enable')
            elif get.status == "reload":
                public.ExecShell('/usr/sbin/ufw reload')
            elif get.status == "restart":
                public.ExecShell(
                    '/usr/sbin/ufw disable && /usr/sbin/ufw ufw enable')

            # ufw防火墙启动时重载一次sysctl
            # 解决deian系统启动ufw后禁ping失效 by linxiao/2022-10-26
            if get.status != "stop":
                filename = '/etc/sysctl.conf'
                ctl_content = public.readFile(filename)
                if ctl_content and ctl_content.find(
                        "net.ipv4.icmp_echo") != -1:
                    public.ExecShell("sysctl -p")

            return public.returnMsg(True, '防火墙已{}'.format(result[get.status]))
        if self.__isFirewalld:
            public.ExecShell('systemctl {} firewalld'.format(get.status))
            return public.returnMsg(True, '防火墙已{}'.format(result[get.status]))
        else:
            public.ExecShell('service iptables {}'.format(get.status))
        return public.returnMsg(True, '防火墙已{}'.format(result[get.status]))

    # 重载防火墙配置
    def FirewallReload(self):
        if self.__isUfw:
            public.ExecShell('/usr/sbin/ufw reload')
            return
        if self.__isFirewalld:
            public.ExecShell('firewall-cmd --reload')
        else:
            public.ExecShell('/etc/init.d/iptables save')
            public.ExecShell('/etc/init.d/iptables restart')

    #端口扫描
    def CheckPort(self, port):
        import socket
        localIP = '127.0.0.1'
        temp = {}
        temp['port'] = port
        temp['local'] = True
        try:
            s = socket.socket()
            s.settimeout(0.01)
            s.connect((localIP, port))
            s.close()
        except:
            temp['local'] = False

        result = 0
        if temp['local']: result += 2
        return result

        # 查询入栈规则
    def get_rules_list(self, args):
        if self.__isFirewalld:
            self.__Obj = firewalld()
            self.GetList()
        else:
            self.get_ufw_list()

        p = 1
        limit = 15
        if 'p' in args: p = args.p
        if 'limit' in args: limit = args.limit

        where = '1=1'
        sql = public.M('firewall_new')

        if hasattr(args, 'query'):
            where = " ports like '%{search}%' or brief like '%{search}%' or address like '%{search}%'".format(
                search=args.query)

        count = sql.where(where, ()).count()
        data = public.get_page(count, int(p), int(limit))
        data['data'] = sql.where(where, ()).limit('{},{}'.format(
            data['shift'], data['row'])).order('addtime desc').select()
        res_data = data['data']
        for i in range(len(res_data)):
            if not 'ports' in res_data[i]:
                res_data[i]['status'] = -1
                continue
            d = res_data[i]
            _port = d['ports']
            if _port.find(':') != -1 or _port.find('.') != -1 or _port.find(
                    '-') != -1:
                d['status'] = -1
            else:
                d['status'] = self.CheckPort(int(_port))
        for i in res_data:
            if 'brief' in i:
                i['brief'] = public.xsssec(i['brief'])
        return res_data

    def check_firewall_rule(self, args):
        """
        @检测防火墙规则
        """
        port = args['port']
        find = public.M('firewall_new').where('ports=?', (str(port), )).find()
        if find:
            return True
        return False

    # 端口检查
    def check_port(self, port_list):
        rep1 = "^\d{1,5}(:\d{1,5})?$"
        # rep1 = '^[0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5]$'
        for port in port_list:
            if port.find('-') != -1:
                ports = port.split('-')
                if not re.search(rep1, ports[0]):
                    return public.returnMsg(False, 'PORT_CHECK_RANGE')
                if not re.search(rep1, ports[1]):
                    return public.returnMsg(False, 'PORT_CHECK_RANGE')
            elif port.find(':') != -1:
                ports = port.split(':')
                if not re.search(rep1, ports[0]):
                    return public.returnMsg(False, 'PORT_CHECK_RANGE')
                if not re.search(rep1, ports[1]):
                    return public.returnMsg(False, 'PORT_CHECK_RANGE')
            else:
                if not re.search(rep1, port):
                    return public.returnMsg(False, 'PORT_CHECK_RANGE')

    def parse_ip_interval(self, ip_str):
        """解析区间IP

        author: lx
        date: 2022/10/25

        Returns:
            list : IP列表
        """
        ips = []
        try:
            rep2 = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
            searchor = re.compile(rep2)
            if ip_str.find("-") != -1:
                pre_ip, end_ip = ip_str.split("-")
                if searchor.search(pre_ip) and searchor.search(end_ip):
                    ips.append(pre_ip)
                    pinx = pre_ip.rfind(".") + 1
                    einx = end_ip.rfind(".") + 1
                    pre = pre_ip[0:pinx]
                    end = end_ip[0:einx]
                    if pre == end:
                        start_num = int(pre_ip[pinx:])
                        end_num = min(int(end_ip[einx:]), 255)
                        for i in range(start_num + 1, end_num):
                            new_ip = pre + str(i)
                            if searchor.search(new_ip):
                                ips.append(new_ip)
                        end_ip = end + str(end_num)
                    ips.append(end_ip)
        except:
            pass
        return ips

    def check_add_ports(self, ports):
        """
        @name 检测端口是否已添加
        @auther hezhihong
        @param ports 端口
        """
        all_port = public.M('firewall_new').order('addtime desc').select()
        for i2 in all_port:
            start_port = end_port = ''
            if i2['ports'].find('-') != -1:
                start_port = i2['ports'].split('-')[0]
                end_port = i2['ports'].split('-')[1]
            else:
                start_port = i2['ports']
            if ports.find(',') != -1:
                port_list = ports.split(',')
                for port in port_list:
                    if end_port:
                        if int(port) >= int(start_port) and int(port) <= int(
                                end_port):
                            return public.returnMsg(
                                False, '{}端口已在端口{}中，请勿重复添加！'.format(
                                    port, i2['ports']))
                    else:
                        if port == start_port:
                            return public.returnMsg(
                                False, '{}端口已经添加过，请勿重复添加！'.format(port))
            elif ports.find('-') != -1:
                add_start = ports.split('-')[0]
                add_end = ports.split('-')[1]
                if end_port:
                    if (int(add_start) >= int(start_port)
                            and int(add_start) <= int(end_port)) or (
                                int(add_end) >= int(start_port)
                                and int(add_end) <= int(end_port)):
                        return public.returnMsg(
                            False, '{}端口范围与现有防火墙规则端口{}重叠，请勿重复添加！'.format(
                                ports, i2['ports']))
                else:
                    if int(add_start) <= int(start_port) and int(
                            add_end) >= int(start_port):
                        return public.returnMsg(
                            False, '{}端口范围包含已添加端口{}，请勿重复添加！'.format(
                                ports, i2['ports']))
            else:
                if end_port:
                    if int(ports) >= int(start_port) and int(ports) <= int(
                            end_port):
                        return public.returnMsg(
                            False,
                            '{}端口已在端口{}中，请勿重复添加！'.format(ports, i2['ports']))
                else:
                    if ports == start_port:
                        return public.returnMsg(
                            False, '{}端口已经添加过，请勿重复添加！'.format(ports))
        return {}

    # 添加入栈规则
    def create_rules(self, get):
        '''
        get 里面 有  protocol port type address brief   五个参数
        protocol == ['tcp','udp']
        port = 端口
        types == [accept、drop] # 放行和禁止
        address  地址，允许放行的ip，如果全部就是：0.0.0.0/0;另外可以包含“,"或者"-"
        表示区间IP
        brief   备注说明
        '''
        protocol = get.protocol
        ports = get.ports.strip()
        types = get.types
        address = get.source.strip()
        brief = get.brief.strip()
        port_list = ports.split(',')
        result = self.check_port(port_list)  # 检测端口
        if result: return result
        # 检测端口是否已经添加过 hezhihong
        add_result = self.check_add_ports(ports)
        if 'status' in add_result: return add_result

        allow_ips = []
        if address:
            sources = [
                sip.strip() for sip in address.split(",") if sip.strip()
            ]
            rep2 = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
            _ips = []
            for source_ip in sources:
                if source_ip.find("-") != -1:
                    print("parse:", source_ip)
                    _ips += self.parse_ip_interval(source_ip)
                else:
                    _ips.append(source_ip)

            for source_ip in _ips:
                if not re.search(rep2,
                                 source_ip) and not public.is_ipv6(source_ip):
                    return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
                query_result = public.M('firewall_new').where\
                    ('ports=? and address=? and protocol=? and types=?',
                    (ports, source_ip, protocol, types,)).count()
                if query_result > 0:
                    continue
                allow_ips.append(source_ip)
        if not allow_ips:
            allow_ips.append("")
        for source_ip in allow_ips:
            if self.__isUfw:
                for port in port_list:
                    if port.find('-') != -1:
                        port = port.replace('-', ':')
                    self.add_ufw_rule(source_ip, protocol, port, types)
            else:
                if self.__isFirewalld:
                    for port in port_list:
                        if port.find(':') != -1:
                            port = port.replace(':', '-')
                        self.add_firewall_rule(source_ip, protocol, port,
                                               types)
                else:
                    for port in port_list:
                        self.add_iptables_rule(source_ip, protocol, port,
                                               types)
            addtime = time.strftime('%Y-%m-%d %X', time.localtime())
            for port in port_list:
                result = public.M('firewall_new').add(
                    'ports,brief,protocol,address,types,addtime',
                    (port, public.xsssec(brief), protocol, source_ip, types,
                     addtime))
        if len(allow_ips) > 0:
            self.FirewallReload()
        return public.returnMsg(True, 'ADD_SUCCESS')

    # 删除入栈规则
    def remove_rules(self, get):
        '''
        get 里面有  id protocol port type address    五个参数
        protocol == ['tcp','udp']
        port = 端口
        types == [accept、drop] # 放行和禁止
        address  地址，允许放行的ip
        '''
        id = get.id
        address = get.address
        protocol = get.protocol
        ports = get.ports
        types = get.types
        if self.__isUfw:
            self.del_ufw_rule(address, protocol, ports, types)
        else:
            if self.__isFirewalld:
                self.del_firewall_rule(address, protocol, ports, types)
            else:
                self.del_iptables_rule(address, protocol, ports, types)
        public.M('firewall_new').where("id=?", (id, )).delete()
        self.FirewallReload()
        return public.returnMsg(True, 'DEL_SUCCESS')

    # 修改入栈规则
    def modify_rules(self, get):
        '''
        get 里面有  id protocol port type address    五个参数
        protocol == ['tcp','udp']
        port = 端口
        types==['reject','accept'] # 放行和禁止
        address  地址，允许放行的ip，如果全部就是：0.0.0.0/0
        '''
        id = get.id
        protocol = get.protocol
        ports = get.ports.strip()
        types = get.types
        address = get.source.strip()
        brief = get.brief.strip()
        if address:
            rep = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
            if not re.search(rep, get.source) and not public.is_ipv6(
                    get.source):
                return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
        data = public.M('firewall_new').where('id=?', (id, )).field(
            'id,address,protocol,ports,types,brief,addtime').find()
        _address = data.get("address", "")
        _protocol = data.get("protocol", "")
        _port = data.get("ports", "")
        _type = data.get("types", "")
        if self.__isUfw:
            self.edit_ufw_rule(_address, _protocol, _port, _type, address,
                               protocol, ports, types)
        else:
            if self.__isFirewalld:
                self.edit_firewall_rule(_address, _protocol, _port, _type,
                                        address, protocol, ports, types)
            else:
                self.edit_iptables_rule(_address, _protocol, _port, _type,
                                        address, protocol, ports, types)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        public.M('firewall_new').where('id=?', id).update({
            'address': address,
            'protocol': protocol,
            'ports': ports,
            'types': types,
            'brief': brief,
            'addtime': addtime
        })
        try:
            if int(ports) == 22:
                self.delete_service()
        except:
            pass
        self.FirewallReload()
        return public.returnMsg(True, '操作成功')

    # firewall端口规则添加
    def add_firewall_rule(self, address, protocol, ports, types):
        if not address:
            if protocol.find('/') != -1:
                if types == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --add-port=' +
                        ports + '/tcp')
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --add-port=' +
                        ports + '/udp')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 port protocol="tcp" port="%s" drop"'
                        % (ports))
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 port protocol="udp" port="%s" drop"'
                        % (ports))
            else:
                if types == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --add-port=' +
                        ports + '/' + protocol + '')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 port protocol="%s" port="%s" drop"'
                        % (protocol, ports))
            return True
        if public.is_ipv6(address):
            if protocol.find('/') != -1:
                public.ExecShell(
                    'firewall-cmd --permanent --add-rich-rule="rule family=ipv6 source address="%s" port protocol="tcp" port="%s" %s"'
                    % (address, ports, types))
                public.ExecShell(
                    'firewall-cmd --permanent --add-rich-rule="rule family=ipv6 source address="%s" port protocol="udp" port="%s" %s"'
                    % (address, ports, types))
            else:
                public.ExecShell(
                    'firewall-cmd --permanent --add-rich-rule="rule family=ipv6 source address="%s" port protocol="%s" port="%s" %s"'
                    % (address, protocol, ports, types))
        else:
            if protocol.find('/') != -1:
                public.ExecShell(
                    'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address="%s" port protocol="tcp" port="%s" %s"'
                    % (address, ports, types))
                public.ExecShell(
                    'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address="%s" port protocol="udp" port="%s" %s"'
                    % (address, ports, types))
            else:
                public.ExecShell(
                    'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address="%s" port protocol="%s" port="%s" %s"'
                    % (address, protocol, ports, types))
        return True

    # firewall端口规则删除
    def del_firewall_rule(self, address, protocol, ports, types):
        if not address:
            if protocol.find('/') != -1:
                if types == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-port='
                        + ports + '/tcp')
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-port='
                        + ports + '/udp')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family=ipv4 port protocol="tcp" port="%s" drop"'
                        % (ports))
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family=ipv4 port protocol="udp" port="%s" drop"'
                        % (ports))
            else:
                if types == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-port='
                        + ports + '/' + protocol + '')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family=ipv4 port protocol="%s" port="%s" drop"'
                        % (protocol, ports))
            self.update_panel_data(ports)
            return True
        if public.is_ipv6(address):
            if protocol.find('/') != -1:
                public.ExecShell(
                    'firewall-cmd --permanent --remove-rich-rule="rule family="ipv6" source address="%s" port protocol="tcp" port="%s" %s"'
                    % (address, ports, types))
                public.ExecShell(
                    'firewall-cmd --permanent --remove-rich-rule="rule family="ipv6" source address="%s" port protocol="udp" port="%s" %s"'
                    % (address, ports, types))
            else:
                public.ExecShell(
                    'firewall-cmd --permanent --remove-rich-rule="rule family="ipv6" source address="%s" port protocol="%s" port="%s" %s"'
                    % (address, protocol, ports, types))
        else:
            if protocol.find('/') != -1:
                public.ExecShell(
                    'firewall-cmd --permanent --remove-rich-rule="rule family="ipv4" source address="%s" port protocol="tcp" port="%s" %s"'
                    % (address, ports, types))
                public.ExecShell(
                    'firewall-cmd --permanent --remove-rich-rule="rule family="ipv4" source address="%s" port protocol="udp" port="%s" %s"'
                    % (address, ports, types))
            else:
                public.ExecShell(
                    'firewall-cmd --permanent --remove-rich-rule="rule family="ipv4" source address="%s" port protocol="%s" port="%s" %s"'
                    % (address, protocol, ports, types))
        return True

    # firewall端口规则编辑
    def edit_firewall_rule(self, _address, _protocol, _port, _type, address,
                           protocol, ports, types):
        if not _address:
            if _protocol.find('/') != -1:
                if _type == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-port='
                        + _port + '/tcp')
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-port='
                        + _port + '/udp')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family=ipv4 port protocol="tcp" port="%s" drop"'
                        % (ports))
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family=ipv4 port protocol="udp" port="%s" drop"'
                        % (ports))
            else:
                if _type == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-port='
                        + _port + '/' + _protocol + '')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family=ipv4 port protocol="%s" port="%s" drop"'
                        % (protocol, ports))
        else:
            if public.is_ipv6(_address):
                if _protocol.find('/') != -1:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family="ipv6" source address="%s" port protocol="tcp" port="%s" %s"'
                        % (_address, _port, _type))
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family="ipv6" source address="%s" port protocol="udp" port="%s" %s"'
                        % (_address, _port, _type))
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family="ipv6" source address="%s" port protocol="%s" port="%s" %s"'
                        % (_address, _protocol, _port, _type))
            else:
                if _protocol.find('/') != -1:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family="ipv4" source address="%s" port protocol="tcp" port="%s" %s"'
                        % (_address, _port, _type))
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family="ipv4" source address="%s" port protocol="udp" port="%s" %s"'
                        % (_address, _port, _type))
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-rich-rule="rule family="ipv4" source address="%s" port protocol="%s" port="%s" %s"'
                        % (_address, _protocol, _port, _type))
        if not address:
            if protocol.find('/') != -1:
                if types == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --add-port=' +
                        ports + '/tcp')
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --add-port=' +
                        ports + '/udp')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 port protocol="tcp" port="%s" drop"'
                        % (ports))
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 port protocol="udp" port="%s" drop"'
                        % (ports))
            else:
                if types == "accept":
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --add-port=' +
                        ports + '/' + protocol + '')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 port protocol="%s" port="%s" drop"'
                        % (protocol, ports))
        else:
            if public.is_ipv6(address):
                if protocol.find('/') != -1:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv6 source address="%s" port protocol="tcp" port="%s" %s"'
                        % (address, ports, types))
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv6 source address="%s" port protocol="udp" port="%s" %s"'
                        % (address, ports, types))
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv6 source address="%s" port protocol="%s" port="%s" %s"'
                        % (address, protocol, ports, types))
            else:
                if protocol.find('/') != -1:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address="%s" port protocol="tcp" port="%s" %s"'
                        % (address, ports, types))
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address="%s" port protocol="udp" port="%s" %s"'
                        % (address, ports, types))
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address="%s" port protocol="%s" port="%s" %s"'
                        % (address, protocol, ports, types))
        return True

    # ufw 端口规则添加
    def add_ufw_rule(self, address, protocol, ports, types):
        rule = "allow" if types == "accept" else "deny"
        if address == "":
            if protocol.find('/') != -1:
                public.ExecShell('ufw ' + rule + ' ' + ports + '/tcp')
                public.ExecShell('ufw ' + rule + ' ' + ports + '/udp')
            else:
                public.ExecShell('ufw ' + rule + ' ' + ports + '/' + protocol +
                                 '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell('ufw ' + rule + ' proto tcp from ' + address +
                                 ' to any port ' + ports + '')
                public.ExecShell('ufw ' + rule + ' proto udp from ' + address +
                                 ' to any port ' + ports + '')
            else:
                public.ExecShell('ufw ' + rule + ' proto ' + protocol +
                                 ' from ' + address + ' to any port ' + ports +
                                 '')

    # ufw 端口规则删除
    def del_ufw_rule(self, address, protocol, ports, types):
        rule = "allow" if types == "accept" else "deny"
        if address == "":
            if protocol.find('/') != -1:
                public.ExecShell('ufw delete ' + rule + ' ' + ports + '/tcp')
                public.ExecShell('ufw delete ' + rule + ' ' + ports + '/udp')
            else:
                public.ExecShell('ufw delete ' + rule + ' ' + ports + '/' +
                                 protocol + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell('ufw delete ' + rule + ' proto tcp from ' +
                                 address + ' to any port ' + ports + '')
                public.ExecShell('ufw delete ' + rule + ' proto udp from ' +
                                 address + ' to any port ' + ports + '')
            else:
                public.ExecShell('ufw delete ' + rule + ' proto ' + protocol +
                                 ' from ' + address + ' to any port ' + ports +
                                 '')
        self.update_panel_data(ports)

    # ufw 端口规则修改
    def edit_ufw_rule(self, _address, _protocol, _port, _type, address,
                      protocol, ports, types):
        _rule = "allow" if _type == "accept" else "deny"
        rules = "allow" if types == "accept" else "deny"
        if _address == "":
            if _protocol.find('/') != -1:
                public.ExecShell('ufw delete ' + _rule + ' ' + _port + '/tcp')
                public.ExecShell('ufw delete ' + _rule + ' ' + _port + '/udp')
            else:
                public.ExecShell('ufw delete ' + _rule + ' ' + _port + '/' +
                                 _protocol + '')
        else:
            if _protocol.find('/') != -1:
                public.ExecShell('ufw delete ' + _rule + ' proto tcp from ' +
                                 _address + ' to any port ' + _port + '')
                public.ExecShell('ufw delete ' + _rule + ' proto udp from ' +
                                 _address + ' to any port ' + _port + '')
            else:
                public.ExecShell('ufw delete ' + _rule + ' proto ' +
                                 _protocol + ' from ' + _address +
                                 ' to any port ' + _port + '')
        if address == "":
            if protocol.find('/') != -1:
                public.ExecShell('ufw ' + rules + ' ' + ports + '/tcp')
                public.ExecShell('ufw ' + rules + ' ' + ports + '/udp')
            else:
                public.ExecShell('ufw ' + rules + ' ' + ports + '/' +
                                 protocol + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell('ufw ' + rules + ' proto tcp from ' +
                                 address + ' to any port ' + ports + '')
                public.ExecShell('ufw ' + rules + ' proto udp from ' +
                                 address + ' to any port ' + ports + '')
            else:
                public.ExecShell('ufw ' + rules + ' proto ' + protocol +
                                 ' from ' + address + ' to any port ' + ports +
                                 '')

    # iptables端口规则添加
    def add_iptables_rule(self, address, protocol, ports, types):
        rule = "ACCEPT" if types == "accept" else "DROP"
        if not address:
            if protocol.find('/') != -1:
                public.ExecShell(
                    'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport '
                    + ports + ' -j ' + rule + '')
                public.ExecShell(
                    'iptables -I INPUT -p tcp -m state --state NEW -m udp --dport '
                    + ports + ' -j ' + rule + '')
            else:
                public.ExecShell(
                    'iptables -I INPUT -p tcp -m state --state NEW -m ' +
                    protocol + ' --dport ' + ports + ' -j ' + rule + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell('iptables -I INPUT -s ' + address +
                                 ' -p tcp --dport ' + ports + ' -j ' + rule +
                                 '')
                public.ExecShell('iptables -I INPUT -s ' + address +
                                 ' -p udp --dport ' + ports + ' -j ' + rule +
                                 '')
            else:
                public.ExecShell('iptables -I INPUT -s ' + address + ' -p ' +
                                 protocol + ' --dport ' + ports + ' -j ' +
                                 rule + '')
        return True

    # iptables端口规则删除
    def del_iptables_rule(self, address, protocol, ports, types):
        rule = "ACCEPT" if types == "accept" else "DROP"
        if not address:
            if protocol.find('/') != -1:
                public.ExecShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport '
                    + ports + ' -j ' + rule + '')
                public.ExecShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m udp --dport '
                    + ports + ' -j ' + rule + '')
            else:
                public.ExecShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m ' +
                    protocol + ' --dport ' + ports + ' -j ' + rule + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell('iptables -D INPUT -s ' + address +
                                 ' -p tcp --dport ' + ports + ' -j ' + rule +
                                 '')
                public.ExecShell('iptables -D INPUT -s ' + address +
                                 ' -p udp --dport ' + ports + ' -j ' + rule +
                                 '')
            else:
                public.ExecShell('iptables -D INPUT -s ' + address + ' -p ' +
                                 protocol + ' --dport ' + ports + ' -j ' +
                                 rule + '')
        return True

    # iptables端口规则编辑
    def edit_iptables_rule(self, _address, _protocol, _port, _type, address,
                           protocol, ports, types):
        rule1 = "ACCEPT" if _type == "accept" else "DROP"
        rule2 = "ACCEPT" if types == "accept" else "DROP"
        if not _address:
            if _protocol.find('/') != -1:
                public.ExecShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport '
                    + _port + ' -j ' + rule1 + '')
                public.ExecShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m udp --dport '
                    + _port + ' -j ' + rule1 + '')
            else:
                public.ExecShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m ' +
                    _protocol + ' --dport ' + _port + ' -j ' + rule1 + '')
        else:
            if _protocol.find('/') != -1:
                public.ExecShell('iptables -D INPUT -s ' + _address +
                                 ' -p tcp --dport ' + _port + ' -j ' + rule1 +
                                 '')
                public.ExecShell('iptables -D INPUT -s ' + _address +
                                 ' -p udp --dport ' + _port + ' -j ' + rule1 +
                                 '')
            else:
                public.ExecShell('iptables -D INPUT -s ' + _address + ' -p ' +
                                 _protocol + ' --dport ' + _port + ' -j ' +
                                 rule1 + '')
        if not address:
            if protocol.find('/') != -1:
                public.ExecShell(
                    'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport '
                    + ports + ' -j ' + rule2 + '')
                public.ExecShell(
                    'iptables -I INPUT -p tcp -m state --state NEW -m udp --dport '
                    + ports + ' -j ' + rule2 + '')
            else:
                public.ExecShell(
                    'iptables -I INPUT -p tcp -m state --state NEW -m ' +
                    protocol + ' --dport ' + ports + ' -j ' + rule2 + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell('iptables -I INPUT -s ' + address +
                                 ' -p tcp --dport ' + ports + ' -j ' + rule2 +
                                 '')
                public.ExecShell('iptables -I INPUT -s ' + address +
                                 ' -p udp --dport ' + ports + ' -j ' + rule2 +
                                 '')
            else:
                public.ExecShell('iptables -I INPUT -s ' + address + ' -p ' +
                                 protocol + ' --dport ' + ports + ' -j ' +
                                 rule2 + '')
        return True

    # 修改面板数据
    def update_panel_data(self, ports):
        res = public.M('firewall').where("port=?", (ports, )).delete()

    # 查询IP规则
    def get_ip_rules_list(self, args):
        p = 1
        limit = 15
        if 'p' in args: p = args.p
        if 'limit' in args: limit = args.limit

        where = '1=1'
        sql = public.M('firewall_ip')

        if hasattr(args, 'query'):
            where = " address like '%{search}%' or brief like '%{search}%' ".format(
                search=args.query)

        count = sql.where(where, ()).count()
        data = public.get_page(count, int(p), int(limit))
        data['data'] = sql.where(where, ()).limit('{},{}'.format(
            data['shift'], data['row'])).order('addtime desc').select()

        data['data'] = public.return_area(data['data'], 'address')
        return data

    # IP地址检测
    def check_ip(self, address_list):
        rep = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
        for address in address_list:
            address = address.split('/')[0]
            if address.find('-') != -1:
                addresses = address.split('-')
                if addresses[0] >= addresses[1]:
                    return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
                s_ips = addresses[0].split(".")
                e_ips = addresses[1].split(".")
                head_s_ip = s_ips[0] + "." + s_ips[1] + "." + s_ips[2] + "."
                head_e_ip = e_ips[0] + "." + e_ips[1] + "." + e_ips[2] + "."
                if head_s_ip != head_e_ip:
                    return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
                if not re.search(rep, addresses[0]):
                    return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
                if not re.search(rep, addresses[1]):
                    return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
            else:
                if not re.search(rep, address) and not public.is_ipv6(address):
                    return public.returnMsg(False, 'FIREWALL_IP_FORMAT')

    # 获取IP范围
    def get_ip(self, address):
        result = []
        arrys = address.split("-")
        s_ips = arrys[0].split(".")
        e_ips = arrys[1].split(".")
        head_s_ip = s_ips[0] + "." + s_ips[1] + "." + s_ips[2] + "."
        region = int(e_ips[-1]) - int(s_ips[-1])
        for num in range(0, region + 1):
            result.append(head_s_ip + str(num + int(s_ips[-1])))
        return result

    def handle_firewall_ip(self, address, types):
        ip_list = self.get_ip(address)
        if isinstance(ip_list, dict):
            return
        public.ExecShell(
            'firewall-cmd --permanent --zone=public --new-ipset=' + address +
            ' --type=hash:net')
        xml_path = "/etc/firewalld/ipsets/%s.xml" % address
        tree = ElementTree()
        tree.parse(xml_path)
        root = tree.getroot()
        for ip in ip_list:
            entry = Element("entry")
            entry.text = ip
            root.append(entry)
            # public.ExecShell('firewall-cmd --permanent --zone=public --ipset='+ address + ' --add-entry='+ip)
        self.format(root)
        tree.write(xml_path, 'utf-8', xml_declaration=True)
        # public.ExecShell('firewall-cmd --permanent --zone=public --add-rich-rule=\'rule source ipset="'+ address +'" accept\'')
        public.ExecShell(
            'firewall-cmd --permanent --zone=public --add-rich-rule=\'rule source ipset="'
            + address + '" ' + types + '\'')

    def handle_ufw_ip(self, address, types):
        ip_list = self.get_ip(address)
        if isinstance(ip_list, dict):
            return
        public.ExecShell('ipset create ' + address + ' hash:net')
        for ip in ip_list:
            public.ExecShell('ipset add ' + address + ' ' + ip)
        public.ExecShell('iptables -I INPUT -m set --match-set ' + address +
                         ' src -j ' + types.upper())

    # 添加IP规则
    def create_ip_rules(self, get):
        _address = get.address.strip()
        types = get.types  # types in [accept, drop]
        brief = get.brief
        address_list = _address.split(',')
        result = self.check_ip(address_list)
        if result:
            return result
        for address in address_list:
            if public.M('firewall_ip').where("address=?",
                                             (address, )).count() > 0:
                return public.returnMsg(False, 'FIREWALL_IP_EXISTS')
            if self.__isUfw:
                _rule = "allow" if types == "accept" else "deny"
                if address.find('-') != -1:
                    self.handle_ufw_ip(address, types)
                else:
                    is_debian = True if public.get_os_version().lower().find(
                        "debian") != -1 else False
                    if not is_debian:
                        if _rule == "allow":
                            if public.is_ipv6(address):
                                public.ExecShell('ufw ' + _rule + ' from ' +
                                                 address + ' to any')
                            else:
                                public.ExecShell('ufw insert 1 ' + _rule +
                                                 ' from ' + address +
                                                 ' to any')
                        else:
                            public.ExecShell('ufw ' + _rule + ' from ' +
                                             address + ' to any')
                    else:
                        public.ExecShell('iptables -I INPUT -s ' + address +
                                         ' -j ' + types.upper())
            else:
                if self.__isFirewalld:
                    if address.find('-') != -1:
                        self.handle_firewall_ip(address, types)
                    else:
                        if types == "accept":
                            public.ExecShell(
                                'firewall-cmd --permanent --add-source=' +
                                address + ' --zone=trusted')
                        else:
                            if public.is_ipv6(address):
                                public.ExecShell(
                                    'firewall-cmd --permanent --add-rich-rule=\'rule family=ipv6 source address="'
                                    + address + '" ' + types + '\'')
                            else:
                                public.ExecShell(
                                    'firewall-cmd --permanent --add-rich-rule=\'rule family=ipv4 source address="'
                                    + address + '" ' + types + '\'')
                else:
                    if address.find('-') != -1:
                        self.handle_ufw_ip(address, types)
                    else:
                        public.ExecShell('iptables -I INPUT -s ' + address +
                                         ' -j ' + types.upper())
            addtime = time.strftime('%Y-%m-%d %X', time.localtime())
            public.M('firewall_ip').add(
                'address,types,brief,addtime',
                (address, types, public.xsssec(brief), addtime))
        self.FirewallReload()
        return public.returnMsg(True, 'ADD_SUCCESS')

    # 删除所有IP规则
    def remove_all_ip_rules(self, get):
        ip_list = public.M('firewall_ip').select()
        for ip in ip_list:
            id = ip["id"]
            address = ip["address"]
            types = ip["types"]
            if self.__isUfw:
                _rule = "allow" if types == "accept" else "deny"
                if address.find('-') != -1:
                    public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                     address + ' src -j ' + types.upper())
                    public.ExecShell('ipset destroy ' + address)
                else:
                    is_debian = True if public.get_os_version().lower().find(
                        "debian") != -1 else False
                    if not is_debian:
                        public.ExecShell('ufw delete ' + _rule + ' from ' +
                                         address + ' to any')
                    else:
                        public.ExecShell("iptables -D INPUT -s " + address +
                                         " -j " + types.upper())
            else:
                if self.__isFirewalld:
                    if address.find('-') != -1:
                        public.ExecShell(
                            'firewall-cmd --permanent --zone=public --remove-rich-rule=\'rule source ipset="'
                            + address + '" ' + types + '\'')
                        public.ExecShell(
                            'firewall-cmd --permanent --zone=public --delete-ipset='
                            + address)
                    else:
                        public.ExecShell(
                            'firewall-cmd --permanent --remove-source=' +
                            address + ' --zone=trusted')
                        if public.is_ipv6(address):
                            public.ExecShell(
                                'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv6 source address="'
                                + address + '" ' + types + '\'')
                        else:
                            public.ExecShell(
                                'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv4 source address="'
                                + address + '" ' + types + '\'')
                else:
                    if address.find('-') != -1:
                        public.ExecShell(
                            'iptables -D INPUT -m set --match-set ' + address +
                            ' src -j ' + types.upper())
                        public.ExecShell('ipset destroy ' + address)
                    else:
                        public.ExecShell('iptables -D INPUT -s ' + address +
                                         ' -j ' + types.upper())
            public.M('firewall_ip').where("id=?", (id, )).delete()
            self.update_panel_data(address)  # 删除面板自带防火墙的表数据
        self.FirewallReload()
        return public.returnMsg(True, '所有IP规则已被删除。')

    # 删除IP规则
    def remove_ip_rules(self, get):
        id = get.id
        address = get.address
        types = get.types
        if self.__isUfw:
            _rule = "allow" if types == "accept" else "deny"
            if address.find('-') != -1:
                public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                 address + ' src -j ' + types.upper())
                public.ExecShell('ipset destroy ' + address)
            else:
                is_debian = True if public.get_os_version().lower().find(
                    "debian") != -1 else False
                if not is_debian:
                    public.ExecShell('ufw delete ' + _rule + ' from ' +
                                     address + ' to any')
                else:
                    public.ExecShell('ufw delete ' + _rule + ' from ' +
                                     address + ' to any')
                    public.ExecShell("iptables -D INPUT -s " + address +
                                     " -j " + types.upper())
        else:
            if self.__isFirewalld:
                if address.find('-') != -1:
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-rich-rule=\'rule source ipset="'
                        + address + '" ' + types + '\'')
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --delete-ipset='
                        + address)
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-source=' + address +
                        ' --zone=trusted')
                    if public.is_ipv6(address):
                        public.ExecShell(
                            'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv6 source address="'
                            + address + '" ' + types + '\'')
                    else:
                        public.ExecShell(
                            'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv4 source address="'
                            + address + '" ' + types + '\'')
            else:
                if address.find('-') != -1:
                    public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                     address + ' src -j ' + types.upper())
                    public.ExecShell('ipset destroy ' + address)
                else:
                    public.ExecShell('iptables -D INPUT -s ' + address +
                                     ' -j ' + types.upper())
        public.M('firewall_ip').where("id=?", (id, )).delete()
        self.update_panel_data(address)  # 删除面板自带防火墙的表数据
        self.FirewallReload()
        return public.returnMsg(True, 'DEL_SUCCESS')

    # 修改IP规则
    def modify_ip_rules(self, get):
        id = get.id
        address = get.address.strip()
        types = get.types
        brief = get.brief
        result = self.check_ip([address])
        if result:
            return result
        data = public.M('firewall_ip').where(
            'id=?', (id, )).field('id,address,types,brief,addtime').find()
        _address = data.get("address", "")
        _type = data.get("types", "")
        if self.__isUfw:
            rule1 = "allow" if _type == "accept" else "deny"
            if _address.find('-') != -1:
                public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                 _address + ' src -j ' + _type.upper())
                public.ExecShell('ipset destroy ' + _address)
            else:
                is_debian = True if public.get_os_version().lower().find(
                    "debian") != -1 else False
                if not is_debian:
                    public.ExecShell('ufw delete ' + rule1 + ' from ' +
                                     address + ' to any')
                else:
                    cmd = "iptables -D INPUT -s " + address + " -j " + _type.upper(
                    )
                    public.ExecShell(cmd)
                # public.ExecShell('ufw delete ' + rule1 + ' from ' + _address + ' to any')
            rule2 = "allow" if types == "accept" else "deny"
            if address.find('-') != -1:
                self.handle_ufw_ip(address, types)
            else:
                is_debian = True if public.get_os_version().lower().find(
                    "debian") != -1 else False
                if not is_debian:
                    if rule2 == "allow":
                        if public.is_ipv6(address):
                            public.ExecShell('ufw ' + rule2 + ' from ' +
                                             address + ' to any')
                        else:
                            public.ExecShell('ufw insert 1 ' + rule2 +
                                             ' from ' + address + ' to any')
                    else:
                        public.ExecShell('ufw ' + rule2 + ' from ' + address +
                                         ' to any')
                else:
                    public.ExecShell('iptables -I INPUT -s ' + address +
                                     ' -j ' + types.upper())
        else:
            if self.__isFirewalld:
                if _address.find('-') != -1:
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-rich-rule=\'rule source ipset="'
                        + _address + '" ' + _type + '\'')
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --delete-ipset='
                        + _address)
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --remove-source=' +
                        _address + ' --zone=trusted')
                    if public.is_ipv6(address):
                        public.ExecShell(
                            'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv6 source address="'
                            + _address + '" ' + _type + '\'')
                    else:
                        public.ExecShell(
                            'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv4 source address="'
                            + _address + '" ' + _type + '\'')
                if address.find('-') != -1:
                    brief = address
                    self.handle_firewall_ip(address, types)
                else:
                    if types == "accept":
                        public.ExecShell(
                            'firewall-cmd --permanent --add-source=' +
                            address + ' --zone=trusted')
                    else:
                        if public.is_ipv6(address):
                            public.ExecShell(
                                'firewall-cmd --permanent --add-rich-rule=\'rule family=ipv6 source address="'
                                + address + '" ' + types + '\'')
                        else:
                            public.ExecShell(
                                'firewall-cmd --permanent --add-rich-rule=\'rule family=ipv4 source address="'
                                + address + '" ' + types + '\'')
            else:
                if _address.find('-') != -1:
                    public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                     _address + ' src -j ' + types.upper())
                    public.ExecShell('ipset destroy ' + _address)
                else:
                    public.ExecShell('iptables -D INPUT -s ' + _address +
                                     ' -j ' + _type.upper())
                if address.find('-') != -1:
                    self.handle_ufw_ip(address, types)
                else:
                    public.ExecShell('iptables -I INPUT -s ' + address +
                                     ' -j ' + types.upper())
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        public.M('firewall_ip').where('id=?', id).update({
            'address': address,
            'types': types,
            'brief': brief,
            'addtime': addtime
        })
        self.FirewallReload()
        return public.returnMsg(True, '操作成功')

    # 查看端口转发状态
    def trans_status(self):
        content = dict()
        with open(self._trans_status, 'r') as fr:
            content = json.loads(fr.read())
            if content["status"] == "open":
                return True
            self.open_forward()
            content["status"] = "open"
            with open(self._trans_status, 'w') as fw:
                fw.write(json.dumps(content))
        return True

    # 查询端口转发
    def get_forward_list(self, args):
        result = self.trans_status()

        p = 1
        limit = 15
        if 'p' in args: p = args.p
        if 'limit' in args: limit = args.limit

        where = '1=1'
        sql = public.M('firewall_trans')

        if hasattr(args, 'query'):
            where = " start_port like '%{search}%'".format(search=args.query)

        count = sql.where(where, ()).count()
        data = public.get_page(count, int(p), int(limit))
        data['data'] = sql.where(where, ()).limit('{},{}'.format(
            data['shift'], data['row'])).order('addtime desc').select()
        return data

    # 添加端口转发
    def create_forward(self, get):
        s_port = get.s_ports.strip()  # 起始端口
        d_port = get.d_ports.strip()  # 目的端口
        d_ip = get.d_address.strip()  # 目的ip
        protocol = get.protocol
        rep1 = "^\d{1,5}(:\d{1,5})?$"
        if not re.search(rep1, s_port):
            return public.returnMsg(False, 'PORT_CHECK_RANGE')
        if not re.search(rep1, d_port):
            return public.returnMsg(False, 'PORT_CHECK_RANGE')
        rep = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
        if d_ip:
            if not re.search(rep, get.d_address) and not public.is_ipv6(
                    get.d_address):
                return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
            if d_ip in ["127.0.0.1", "localhost"]:
                d_ip = ""
        if public.M('firewall_trans').where("start_port=?",
                                            (s_port, )).count() > 0:
            return public.returnMsg(False, '该端口已存在，请勿重复添加！')
        if self.__isUfw:
            content = self.ufw_handle_add(s_port, d_port, d_ip, protocol)
            self.save_profile(self._ufw_before, content)
        else:
            if self.__isFirewalld:
                self.firewall_handle_add(s_port, d_port, d_ip, protocol)
            else:
                self.iptables_handle_add(s_port, d_port, d_ip, protocol)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        public.M('firewall_trans').add(
            'start_port, ended_ip, ended_port, protocol, addtime',
            (s_port, d_ip, d_port, protocol, addtime))
        self.FirewallReload()
        return public.returnMsg(True, 'ADD_SUCCESS')

    # 删除端口转发
    def remove_forward(self, get):
        id = get.id
        s_port = get.s_port
        d_port = get.d_port
        d_ip = get.d_ip
        protocol = get.protocol
        if self.__isUfw:
            content = self.ufw_handle_del(s_port, d_port, d_ip, protocol)
            self.save_profile(self._ufw_before, content)
        else:
            if self.__isFirewalld:
                self.firewall_handle_del(s_port, d_port, d_ip, protocol)
            else:
                self.iptables_handle_del(s_port, d_port, d_ip, protocol)
        public.M('firewall_trans').where("id=?", (id, )).delete()
        self.FirewallReload()
        return public.returnMsg(True, 'DEL_SUCCESS')

    # 修改端口转发
    def modify_forward(self, get):
        id = get.id
        s_port = get.s_ports.strip()
        d_port = get.d_ports.strip()
        d_ip = get.d_address.strip()
        pool = get.protocol
        rep1 = "^\d{1,5}(:\d{1,5})?$"
        if not re.search(rep1, s_port):
            return public.returnMsg(False, 'PORT_CHECK_RANGE')
        if not re.search(rep1, d_port):
            return public.returnMsg(False, 'PORT_CHECK_RANGE')
        data = public.M('firewall_trans').where('id=?', (id, )).field(
            'id,start_port,ended_ip,ended_port,protocol,addtime').find()
        start_port = data.get("start_port", "")
        ended_ip = data.get("ended_ip", "")
        ended_port = data.get("ended_port", "")
        protocol = data.get("protocol", "")
        if d_ip:
            rep = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
            if not re.search(rep, get.d_address) and not public.is_ipv6(
                    get.d_address):
                return public.returnMsg(False, 'FIREWALL_IP_FORMAT')
            if d_ip in ["127.0.0.1", "localhost"]:
                d_ip = ""
        if self.__isUfw:
            content = self.ufw_handle_update(start_port, ended_ip, ended_port,
                                             protocol, s_port, d_ip, d_port,
                                             pool)
            self.save_profile(self._ufw_before, content)
        else:
            if self.__isFirewalld:
                self.firewall_handle_update(start_port, ended_ip, ended_port,
                                            protocol, s_port, d_ip, d_port,
                                            pool)
            else:
                self.iptables_handle_update(start_port, ended_ip, ended_port,
                                            protocol, s_port, d_ip, d_port,
                                            pool)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        public.M('firewall_trans').where('id=?', id).update({
            'start_port': s_port,
            "ended_ip": d_ip,
            "ended_port": d_port,
            "protocol": pool
        })
        self.FirewallReload()
        return public.returnMsg(True, '操作成功.')

    # 处理ufw的端口转发添加
    def ufw_handle_add(self, s_port, d_port, d_ip, protocol):
        content = self.get_profile(self._ufw_before)
        if content.find('*nat') == -1:
            content = "*nat\n" + ":PREROUTING ACCEPT [0:0]\n" + ":POSTROUTING ACCEPT [0:0]\n" + "COMMIT\n" + content
        array = content.split('\n')
        result = array.index(":POSTROUTING ACCEPT [0:0]")
        if d_ip == "":
            if protocol.find('/') != -1:
                _string = "-A PREROUTING -p tcp --dport {1} -j REDIRECT --to-port {2}\n".format(
                    s_port, d_port)
                _string = _string + "-A PREROUTING -p udp --dport {1} -j REDIRECT --to-port {2}".format(
                    s_port, d_port)
            else:
                _string = "-A PREROUTING -p {0} --dport {1} -j REDIRECT --to-port {2}".format(
                    protocol, s_port, d_port)
        else:
            _string = "-A PREROUTING -p {0} --dport {1} -j DNAT --to-destination {2}:{3}\n".format(
                protocol, s_port, d_ip,
                d_port) + "-A POSTROUTING -d {0} -j MASQUERADE".format(d_ip)
        array.insert(result + 1, _string)
        return '\n'.join(array)

    # 处理ufw的端口转发删除
    def ufw_handle_del(self, s_port, d_port, d_ip, protocol):
        content = self.get_profile(self._ufw_before)
        if d_ip == "":
            _string = "-A PREROUTING -p {0} --dport {1} -j REDIRECT --to-port {2}\n".format(
                protocol, s_port, d_port)
        else:
            _string = "-A PREROUTING -p {0} --dport {1} -j DNAT --to-destination {2}:{3}\n".format(
                protocol, s_port, d_ip,
                d_port) + "-A POSTROUTING -d {0} -j MASQUERADE\n".format(d_ip)
        content = content.replace(_string, "")
        return content

    # 处理ufw的端口转发修改
    def ufw_handle_update(self, start_port, ended_ip, ended_port, protocol,
                          s_port, d_ip, d_port, pool):
        content = self.get_profile(self._ufw_before)
        if ended_ip == "":
            s_string = "-A PREROUTING -p {0} --dport {1} -j REDIRECT --to-port {2}\n".format(
                protocol, start_port, ended_port)
        else:
            s_string = "-A PREROUTING -p {0} --dport {1} -j DNAT --to-destination {2}:{3}\n".format(
                protocol, start_port, ended_ip, ended_port
            ) + "-A POSTROUTING -d {0} -j MASQUERADE\n".format(ended_ip)
        if d_ip == "":
            d_string = "-A PREROUTING -p {0} --dport {1} -j REDIRECT --to-port {2}\n".format(
                pool, s_port, d_port)
        else:
            d_string = "-A PREROUTING -p {0} --dport {1} -j DNAT --to-destination {2}:{3}\n".format(
                pool, s_port, d_ip,
                d_port) + "-A POSTROUTING -d {0} -j MASQUERADE\n".format(d_ip)
        content = content.replace(s_string, d_string)
        return content

    # 处理firewall的端口转发添加
    def firewall_handle_add(self, s_port, d_port, d_ip, protocol):
        if protocol.find('/') != -1:
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --add-forward-port=port="
                + s_port + ":proto=tcp:toaddr=" + d_ip + ":toport=" + d_port +
                "")
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --add-forward-port=port="
                + s_port + ":proto=udp:toaddr=" + d_ip + ":toport=" + d_port +
                "")
        else:
            cmd = "firewall-cmd --permanent --zone=public --add-forward-port=port=" + s_port + ":proto=" + protocol + ":toaddr=" + d_ip + ":toport=" + d_port + ""
            public.ExecShell(cmd)

    # 处理firewall的端口转发删除
    def firewall_handle_del(self, s_port, d_port, d_ip, protocol):
        if protocol.find('/') != -1:
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --remove-forward-port=port="
                + s_port + ":proto=tcp:toaddr=" + d_ip + ":toport=" + d_port +
                "")
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --remove-forward-port=port="
                + s_port + ":proto=udp:toaddr=" + d_ip + ":toport=" + d_port +
                "")
        else:
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --remove-forward-port=port="
                + s_port + ":proto=" + protocol + ":toaddr=" + d_ip +
                ":toport=" + d_port + "")

    # 处理firewall的端口转发修改
    def firewall_handle_update(self, start_port, ended_ip, ended_port,
                               protocol, s_port, d_ip, d_port, pool):
        if protocol.find('/') != -1:
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --remove-forward-port=port="
                + start_port + ":proto=tcp:toaddr=" + ended_ip + ":toport=" +
                ended_port + "")
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --remove-forward-port=port="
                + start_port + ":proto=udp:toaddr=" + ended_ip + ":toport=" +
                ended_port + "")
        else:
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --remove-forward-port=port="
                + start_port + ":proto=" + protocol + ":toaddr=" + ended_ip +
                ":toport=" + ended_port + "")
        if pool.find('/') != -1:
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --add-forward-port=port="
                + s_port + ":proto=tcp:toaddr=" + d_ip + ":toport=" + d_port +
                "")
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --add-forward-port=port="
                + s_port + ":proto=udp:toaddr=" + d_ip + ":toport=" + d_port +
                "")
        else:
            public.ExecShell(
                "firewall-cmd --permanent --zone=public --add-forward-port=port="
                + s_port + ":proto=" + pool + ":toaddr=" + d_ip + ":toport=" +
                d_port + "")

    # 处理iptables的端口转发添加
    def iptables_handle_add(self, s_port, d_port, d_ip, protocol):
        if d_ip == "":
            if protocol.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p tcp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p udp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
            else:
                public.ExecShell("iptables -t nat -A PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j REDIRECT --to-port " + d_port + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p tcp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p udp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -A POSTROUTING -j MASQUERADE")
            else:
                public.ExecShell("iptables -t nat -A PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j DNAT --to-destination " + d_ip + ":" +
                                 d_port + '')
                public.ExecShell(
                    "iptables -t nat -A POSTROUTING -j MASQUERADE")
        return True

    # 处理iptables的端口转发删除
    def iptables_handle_del(self, s_port, d_port, d_ip, protocol):
        if d_ip == "":
            if protocol.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p tcp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p udp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
            else:
                public.ExecShell("iptables -t nat -D PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j REDIRECT --to-port " + d_port + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p tcp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p udp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -D POSTROUTING -j MASQUERADE")
            else:
                public.ExecShell("iptables -t nat -D PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j DNAT --to-destination " + d_ip + ":" +
                                 d_port + '')
                public.ExecShell(
                    "iptables -t nat -D POSTROUTING -j MASQUERADE")
        return True

    # 处理iptables的端口转发删除
    def iptables_handle_update(self, start_port, ended_ip, ended_port,
                               protocol, s_port, d_ip, d_port, pool):
        if ended_ip == "":
            if protocol.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p tcp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p udp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
            else:
                public.ExecShell("iptables -t nat -D PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j REDIRECT --to-port " + d_port + '')
        else:
            if protocol.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p tcp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -D PREROUTING -p udp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -D POSTROUTING -j MASQUERADE")
            else:
                public.ExecShell("iptables -t nat -D PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j DNAT --to-destination " + d_ip + ":" +
                                 d_port + '')
                public.ExecShell(
                    "iptables -t nat -D POSTROUTING -j MASQUERADE")
        if d_ip == "":
            if pool.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p tcp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p udp --dport " + s_port +
                    " -j REDIRECT --to-port " + d_port + '')
            else:
                public.ExecShell("iptables -t nat -A PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j REDIRECT --to-port " + d_port + '')
        else:
            if pool.find('/') != -1:
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p tcp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -A PREROUTING -p udp --dport " + s_port +
                    " -j DNAT --to-destination " + d_ip + ":" + d_port + '')
                public.ExecShell(
                    "iptables -t nat -A POSTROUTING -j MASQUERADE")
            else:
                public.ExecShell("iptables -t nat -A PREROUTING -p " +
                                 protocol + " --dport " + s_port +
                                 " -j DNAT --to-destination " + d_ip + ":" +
                                 d_port + '')
                public.ExecShell(
                    "iptables -t nat -A POSTROUTING -j MASQUERADE")
        return True

    # 开启端口转发
    def open_forward(self):
        if self.__isUfw:
            content1 = self.get_profile(self._ufw_default)
            content2 = self.get_profile(self._ufw_sysctl)
            content1 = content1.replace('DEFAULT_FORWARD_POLICY="DROP"',
                                        'DEFAULT_FORWARD_POLICY="ACCEPT"')
            content2 = content2.replace('#net/ipv4/ip_forward=1',
                                        'net/ipv4/ip_forward=1')
            self.save_profile(self._ufw_default, content1)
            self.save_profile(self._ufw_sysctl, content2)
            self.FirewallReload()
            return True
        if self.__isFirewalld:
            public.ExecShell(
                'echo "\nnet.ipv4.ip_forward=1" >> /etc/sysctl.conf')
            public.ExecShell('firewall-cmd --add-masquerade --permanent')
            self.FirewallReload()
        else:
            public.ExecShell(
                'echo "\nnet.ipv4.ip_forward=1" >> /etc/sysctl.conf')
            public.ExecShell('sysctl -p /etc/sysctl.conf')
            self.FirewallReload()
        return True

    # 开启或关闭端口转发
    def open_close_forward(self, get):
        if not get.status in ["open", "close"]:
            return public.returnMsg(False, '未知控制命令!')
        if self.__isUfw:
            content1 = self.get_profile(self._ufw_default)
            content2 = self.get_profile(self._ufw_sysctl)
            if get.status == 'open':
                content1 = content1.replace('DEFAULT_FORWARD_POLICY="DROP"',
                                            'DEFAULT_FORWARD_POLICY="ACCEPT"')
                content2 = content2.replace('#net/ipv4/ip_forward=1',
                                            'net/ipv4/ip_forward=1')
            else:
                content1 = content1.replace('DEFAULT_FORWARD_POLICY="ACCEPT"',
                                            'DEFAULT_FORWARD_POLICY="DROP"')
                content2 = content2.replace('net/ipv4/ip_forward=1',
                                            '#net/ipv4/ip_forward=1')
            self.save_profile(self._ufw_default, content1)
            self.save_profile(self._ufw_sysctl, content2)
            self.FirewallReload()
            return public.returnMsg(True,
                                    '开启' if get.status == "open" else "关闭")
        if self.__isFirewalld:
            if get.status == 'open':
                public.ExecShell('firewall-cmd --add-masquerade --permanent')
            else:
                public.ExecShell(
                    'firewall-cmd --remove-masquerade --permanent')
            self.FirewallReload()
        else:
            public.ExecShell(
                'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf')
            public.ExecShell('sysctl -p /etc/sysctl.conf')
        return public.returnMsg(True, "关闭端口转发")

    def get_host_ip(self):
        """
        查询本机ip地址
        :return:
        """
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip

    def load_white_list(self):
        try:
            if not self._white_list:
                ip_data = self.get_profile(self._white_list_file)
                white_list_ips = json.loads(ip_data)
                white_list = []
                for ip_obj in white_list_ips:
                    white_list += ip_obj["ips"]
                self._white_list = white_list
                # public.WriteLog("firewall_debug", str(white_list))
            return self._white_list
        except Exception as e:
            public.WriteLog("firewall", "加载白名单列表失败！")
        return []

    def verify_ip(self, ip_entry):
        """检查规则IP是否和内网IP重叠"""
        try:
            try:
                import IPy
            except:
                ipy_tips = '/tmp/bt_ipy.pl'
                if not os.path.exists(ipy_tips):
                    os.system("nohup btpip install IPy &>/dev/null &")
                    public.WriteFile(ipy_tips, 'True')

            release_ips = [
                IPy.IP("127.0.0.1"),
                IPy.IP("172.16.1.1"),
                IPy.IP("10.0.0.1"),
                IPy.IP("192.168.0.0"),
                IPy.IP(self.get_host_ip())
            ]

            white_list = self.load_white_list()

            release_ips += white_list

            ip = IPy.IP(ip_entry, make_net=True)
            for rip_obj in release_ips:
                overlap = ip.overlaps(rip_obj)
                if overlap > 0:
                    return False
            return True
        except:
            return False

    def handle_firewall_country(self, brief, ip_list, types, port_list):
        try:
            public.ExecShell(
                'firewall-cmd --permanent --zone=public --new-ipset=' + brief +
                ' --type=hash:net')
            xml_path = "/etc/firewalld/ipsets/%s.xml" % brief
            tree = ElementTree()
            tree.parse(xml_path)
            root = tree.getroot()
            for ip in ip_list:
                if self.verify_ip(ip):
                    entry = Element("entry")
                    entry.text = ip
                    root.append(entry)
            self.format(root)
            tree.write(xml_path, 'utf-8', xml_declaration=True)
            if port_list:
                for port in port_list:
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --add-rich-rule=\'rule source ipset="'
                        + brief + '" port port="' + port + '" protocol=tcp ' +
                        types + '\'')
            else:
                public.ExecShell(
                    'firewall-cmd --permanent --zone=public --add-rich-rule=\'rule source ipset="'
                    + brief + '" ' + types + '\'')
        except Exception as e:
            return {"status": "error", "msg": e}

    def handle_ufw_country(self, brief, ip_list, types, port_list):
        tmp_path = '/tmp/firewall_tmp.sh'
        tmp_file = open(tmp_path, 'w')
        _string = "#!/bin/bash\n"
        for ip in ip_list:
            if self.verify_ip(ip):
                _string = _string + 'ipset add ' + brief + ' ' + ip + '\n'
        tmp_file.write(_string)
        tmp_file.close()
        public.ExecShell('ipset create ' + brief +
                         ' hash:net; /bin/bash /tmp/firewall_tmp.sh')
        if port_list:
            for port in port_list:
                public.ExecShell('iptables -I INPUT -m set --match-set ' +
                                 brief + ' src -p tcp --destination-port ' +
                                 port + ' -j ' + types.upper())
        else:
            public.ExecShell('iptables -I INPUT -m set --match-set ' + brief +
                             ' src -j ' + types.upper())

    # 查询区域规则
    def get_country_list(self, args):

        p = 1
        limit = 15
        if 'p' in args: p = args.p
        if 'limit' in args: limit = args.limit

        where = '1=1'
        sql = public.M('firewall_country')

        if hasattr(args, 'query'):
            where = " country like '%{search}%' or brief like '%{search}%'".format(
                search=args.query)

        count = sql.where(where, ()).count()
        data = public.get_page(count, int(p), int(limit))
        data['data'] = sql.where(where, ()).limit('{},{}'.format(
            data['shift'], data['row'])).order('addtime desc').select()
        return data

    # 添加区域规则
    def create_country(self, get):
        brief = get.brief
        types = get.types  # types in [accept, drop]
        ports = get.ports
        country = get.country
        rep = "^\d{1,5}(:\d{1,5})?$"
        port_list = []

        #检测该区域是否已添加过全部端口规则 hezhihong
        add_list = public.M('firewall_country').where(
            "country=?", (country, )).field('ports').select()
        for add in add_list:
            if not add['ports']:
                return public.returnMsg(False, '该区域已添加过，请勿重复添加！')

        if ports:
            port_list = ports.split(',')
            for port in port_list:
                if not re.search(rep, port):
                    return public.returnMsg(False, 'PORT_CHECK_RANGE')
                if public.M('firewall_country').where(
                        "country=? and ports=?", (country, port)).count() > 0:
                    return public.returnMsg(False, '该区域已添加过，请勿重复添加！')
        self.get_os_info()
        content = self.get_profile(self._ips_path)
        result = json.loads(content)
        ip_list = []
        for r in result:
            if brief == r["brief"]:
                ip_list = r["ips"]
                break
        if not ip_list:
            return public.returnMsg(True, "请输入正确的区域名称！")
        if self.__isUfw:
            self.handle_ufw_country(brief, ip_list, types, port_list)
        else:
            if self.__isFirewalld:
                result = self.handle_firewall_country(brief, ip_list, types,
                                                      port_list)
                if result:
                    return result
            else:
                self.handle_ufw_country(brief, ip_list, types, port_list)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        if port_list:
            for port in port_list:
                public.M('firewall_country').add(
                    'country,types,brief,ports,addtime',
                    (country, types, brief, port, addtime))
        else:
            public.M('firewall_country').add(
                'country,types,brief,ports,addtime',
                (country, types, brief, '', addtime))
        self.FirewallReload()
        return public.returnMsg(True, 'ADD_SUCCESS')

    # 删除区域规则
    def remove_country(self, get):
        id = get.id
        types = get.types
        brief = get.brief
        ports = get.ports
        country = get.country
        reload = True
        if "not_reload" in get:
            reload = get.not_reload.lower() == "true"

        public.M('firewall_country').where("id=?", (id, )).delete()
        if self.__isUfw:
            if not ports:
                public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                 brief + ' src -j ' + types.upper())
            else:
                public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                 brief + ' src -p tcp --destination-port ' +
                                 ports + ' -j ' + types.upper())
            if not public.M('firewall_country').where("country=?",
                                                      (country, )).count() > 0:
                public.ExecShell('ipset destroy ' + brief)
        else:
            if self.__isFirewalld:
                if not ports:
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-rich-rule=\'rule source ipset="'
                        + brief + '" ' + types + '\'')
                else:
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --remove-rich-rule=\'rule source ipset="'
                        + brief + '" port port="' + ports + '" protocol=tcp ' +
                        types + '\'')
                if not public.M('firewall_country').where(
                        "country=?", (country, )).count() > 0:
                    public.ExecShell(
                        'firewall-cmd --permanent --zone=public --delete-ipset='
                        + brief)
            else:
                if not ports:
                    public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                     brief + ' src -j ' + types.upper())
                else:
                    public.ExecShell('iptables -D INPUT -m set --match-set ' +
                                     brief +
                                     ' src -p tcp --destination-port ' +
                                     ports + ' -j ' + types.upper())
                if not public.M('firewall_country').where(
                        "country=?", (country, )).count() > 0:
                    public.ExecShell('ipset destroy ' + brief)
        if reload:
            self.FirewallReload()
        return public.returnMsg(True, 'DEL_SUCCESS')

    # 编辑区域规则
    def modify_country(self, get):
        # 2022/11/24 修复编辑地区端口规则问题 lx
        id = get.id
        # types = get.types
        # brief = get.brief
        # country = get.country
        data = public.M('firewall_country').where(
            'id=?',
            (id, )).field('id,country,types,brief,ports,addtime').find()
        ori_get = public.dict_obj()
        ori_get.id = id
        ori_get.types = data.get("types", "")
        ori_get.brief = data.get("brief", "")
        ori_get.country = data.get("country", "")
        ori_get.ports = data.get("ports", "")
        ori_get.not_reload = "true"
        rm_res = self.remove_country(ori_get)
        if rm_res["status"]:
            create_res = self.create_country(get)
            if create_res["status"]:
                return public.returnMsg(True, "操作成功")
        return public.returnMsg(False, "操作失败")

    # 获取服务端列表：centos
    def GetList(self):
        try:
            result, arry = self.__Obj.GetAcceptPortList()
            addtime = time.strftime('%Y-%m-%d %X', time.localtime())
            for i in range(len(result)):
                if "address" not in result[i].keys(): continue
                tmp = self.check_db_exists(result[i]['ports'],
                                           result[i]['address'],
                                           result[i]['types'])
                protocol = result[i]['protocol']
                ports = result[i]['ports']
                types = result[i]['types']
                address = result[i]['address']
                if not tmp:
                    if ports:
                        public.M('firewall_new').add(
                            'ports,protocol,address,types,brief,addtime',
                            (ports, protocol, address, types, '', addtime))
                    else:
                        public.M('firewall_ip').add(
                            'address,types,brief,addtime',
                            (address, types, '', addtime))
            for i in range(len(arry)):
                if arry[i]['port']:
                    tmp = self.check_trans_data(arry[i]['port'])
                    protocol = arry[i]['protocol']
                    s_port = arry[i]['port']
                    d_port = arry[i]['to-port']
                    address = arry[i]['address']
                    if not tmp:
                        public.M('firewall_trans').add(
                            'start_port,ended_ip,ended_port,protocol,addtime',
                            (s_port, address, d_port, protocol, addtime))
        except Exception as e:
            file = open('error.txt', 'w')
            return public.returnMsg(False, e)

    # 获取服务端列表：ufw
    def get_ufw_list(self):
        data = public.M('firewall').field('id,port,ps,addtime').select()
        for dt in data:
            port = dt['port']
            brief = dt['ps']
            addtime = dt['addtime']
            if port.find('.') != -1:
                tmp = self.check_db_exists('', port, 'drop')
                if not tmp:
                    public.M('firewall_ip').add('address,types,brief,addtime',
                                                (port, 'drop', '', addtime))
            else:
                tmp = self.check_db_exists(port, '', 'accept')
                if not tmp:
                    public.M('firewall_new').add(
                        'ports,brief,protocol,address,types,addtime',
                        (port, brief, 'tcp/udp', '', 'accept', addtime))

    # 检查数据库是否存在
    def check_db_exists(self, ports, address, types):
        if ports:
            data = public.M('firewall_new').field(
                'id,ports,protocol,address,types,brief,addtime').select()
            for dt in data:
                if dt['ports'] == ports: return dt
            return False
        else:
            data = public.M('firewall_ip').field(
                'id,address,types,brief,addtime').select()
            for dt in data:
                if dt["address"] == address and dt["types"] == types: return dt
            return False

    def check_trans_data(self, ports):
        data = public.M('firewall_trans').field(
            'id,start_port,ended_ip,ended_port,protocol,addtime').select()
        for dt in data:
            if dt['start_port'] == ports: return dt
        return False

    # 规则导出：服务器
    def export_rules(self, get):
        rule_name = get.rule_name
        arry = []
        if rule_name == "port_rule":
            filename = self._rule_path + "port.json"
            data_list = public.M('firewall_new').order("id desc").select()
        elif rule_name == "ip_rule":
            filename = self._rule_path + "ip.json"
            data_list = public.M('firewall_ip').order("id desc").select()
        elif rule_name == "trans_rule":
            filename = self._rule_path + "forward.json"
            data_list = public.M('firewall_trans').order("id desc").select()
        elif rule_name == "country_rule":
            filename = self._rule_path + "country.json"
            data_list = public.M('firewall_country').order("id desc").select()
        if not data_list:
            data_list = []
        # 将数据换成一行一条 hezhihong
        write_str = ""
        if data_list:
            for i in data_list:
                write_str += json.dumps(i, ensure_ascii=False) + "\n"
        public.writeFile(filename, write_str)
        return public.returnMsg(True, filename)

    # 规则导出：本地
    def get_file(self, args):
        filename = args.filename
        mimetype = "application/octet-stream"
        if not os.path.exists(filename): return abort(404)
        return send_file(filename,
                         mimetype=mimetype,
                         as_attachment=True,
                         attachment_filename=os.path.basename(filename),
                         cache_timeout=0)

    # 规则导入：json
    def import_rules(self, get):
        rule_name = get.rule_name  # 规则名:[port_rule, ip_rule, trans_rule, country_rule]
        file_name = get.file_name  # 文件命:[port.json, ip.json, trans.json, country.json]
        file_path = "{0}{1}".format(self._rule_path, file_name)
        data_list = self.get_profile(file_path)

        # 一行一条规则格式文件导入 hezhihong
        if data_list and isinstance(data_list, str):
            data_list = data_list.strip()
        if isinstance(data_list, str) and data_list.find('\n') != -1:
            data_list = data_list.split('\n')
            try:
                data_list.remove('')
            except:
                pass
        if isinstance(data_list, str):
            try:
                data_list = json.loads(data_list)
            except:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return public.ReturnMsg(False, "文件内容有误！")
        if data_list:
            if isinstance(data_list, dict):
                data_list = [data_list]
            if not isinstance(data_list, list):
                if os.path.exists(file_path):
                    os.remove(file_path)
                return public.ReturnMsg(False, "文件内容有误！")
            if len(data_list) == 0:
                return public.ReturnMsg(False, "文件为空哦！")
            result = self.hand_import_rules(rule_name, data_list)
        os.remove(file_path)
        return public.ReturnMsg(result["status"], result["msg"])

    # 处理规则导入，读取json文件内容
    def hand_import_rules(self, rule_name, data_list):
        table_head = []
        try:
            if rule_name == "port_rule":
                table_head = [
                    "id", "protocol", "ports", "types", "address", "brief",
                    "addtime"
                ]
                for data in data_list:
                    #兼容一行一条规则格式文件导入 hezhihong
                    try:
                        data = json.loads(data)
                    except:
                        pass

                    res = all([field in data.keys() for field in table_head])
                    if not res or len(table_head) != len(data.keys()):
                        return {"status": False, "msg": "数据格式不正确！"}
                    get = public.dict_obj()
                    get.protocol = data["protocol"]
                    get.ports = data["ports"]
                    get.types = data["types"]
                    get.source = data["address"]
                    get.brief = data["brief"]
                    result = self.create_rules(get)
                    if not result["status"]:
                        continue
            elif rule_name == "ip_rule":
                table_head = ["id", "types", "address", "brief", "addtime"]
                for data in data_list:
                    #兼容一行一条规则格式文件导入 hezhihong
                    try:
                        data = json.loads(data)
                    except:
                        pass
                    res = all([field in data.keys() for field in table_head])
                    if not res:
                        return {"status": False, "msg": "数据格式不正确！"}
                    get = public.dict_obj()
                    get.types = data["types"]
                    get.address = data["address"]
                    get.brief = data["brief"]
                    result = self.create_ip_rules(get)
                    if not result["status"]:
                        continue
            elif rule_name == "trans_rule":
                table_head = [
                    "id", "start_port", "ended_ip", "ended_port", "protocol",
                    "addtime"
                ]
                for data in data_list:
                    #兼容一行一条规则格式文件导入 hezhihong
                    try:
                        data = json.loads(data)
                    except:
                        pass
                    res = all([field in data.keys() for field in table_head])
                    if not res:
                        return {"status": False, "msg": "数据格式不正确！"}
                    get = public.dict_obj()
                    get.s_ports = data["start_port"]
                    get.d_address = data["ended_ip"]
                    get.d_ports = data["ended_port"]
                    get.protocol = data["protocol"]
                    result = self.create_forward(get)
                    if not result["status"]:
                        continue
            elif rule_name == "country_rule":
                table_head = ["id", "types", "country", "brief", "addtime"]
                for data in data_list:
                    #兼容一行一条规则格式文件导入 hezhihong
                    try:
                        data = json.loads(data)
                    except:
                        pass
                    res = all([field in data.keys() for field in table_head])
                    if not res:
                        return {"status": False, "msg": "数据格式不正确！"}
                    get = public.dict_obj()
                    get.types = data["types"]
                    get.ports = data["ports"]
                    get.brief = data["brief"]
                    get.country = data["country"]
                    result = self.create_country(get)
                    if not result["status"]:
                        continue
        except:
            return {"status": False, "msg": "导入失败！"}
        return {"status": True, "msg": "导入成功！"}

    def get_countrys(self, get):
        result = []
        content = self.get_profile(self._country_path)
        result = json.loads(content)
        # result = sorted(result, key=lambda x : x['CH'], reverse=True);
        return result

    # 读取配置文件
    def get_profile(self, path):

        if not os.path.exists(path):
            b_path = os.path.dirname(path)
            if not os.path.exists(b_path): os.makedirs(b_path)

            if path in [
                    self._ips_path, self._country_path, self._white_list_file
            ]:
                public.downloadFile(
                    'https://download.bt.cn/install/lib/{}'.format(
                        os.path.basename(path)), path)

        content = ""
        with open(path, "r") as fr:
            content = fr.read()
        return content

    # 保存配置文件
    def save_profile(self, path, data):
        with open(path, "w") as fw:
            fw.write(data)

    # 读取配置文件
    def update_profile(self, path):
        import files
        f = files.files()
        return f.GetFileBody(path)

    # 获取端口规则列表
    def get_port_rules(self, get):
        rule_list = public.M('firewall_new').order("id desc").select()
        return public.returnMsg(True, rule_list)

    # 整理配置文件格式
    def format(self, em, level=0):
        i = "\n" + level * "  "
        if len(em):
            if not em.text or not em.text.strip():
                em.text = i + "  "
            for e in em:
                self.format(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        if level and (not em.tail or not em.tail.strip()):
            em.tail = i

    def check_table(self):
        if public.M('sqlite_master').where('type=? AND name=?',
                                           ('table', 'firewall_new')).count():
            if public.M('sqlite_master').where(
                    'type=? AND name=?', ('table', 'firewall_ip')).count():
                if public.M('sqlite_master').where(
                        'type=? AND name=?',
                    ('table', 'firewall_trans')).count():
                    if public.M('sqlite_master').where(
                            'type=? AND name=?',
                        ('table', 'firewall_country')).count():
                        return True
        return Sqlite()

    def delete_service(self):
        if self.__isUfw:
            public.ExecShell('ufw delete allow ssh')
        else:
            if self.__isFirewalld:
                public.ExecShell(
                    'firewall-cmd --zone=public --remove-service=ssh --permanent'
                )
            else:
                pass
        return True

    # 获取系统类型(具体到哪个版本)
    def get_os_info(self):
        tmp = {}
        if os.path.exists('/etc/redhat-release'):
            sys_info = public.ReadFile('/etc/redhat-release')
        elif os.path.exists('/usr/bin/yum'):
            sys_info = public.ReadFile('/etc/issue')
        elif os.path.exists('/etc/issue'):
            sys_info = public.ReadFile('/etc/issue')
        tmp['osname'] = sys_info.split()[0]
        tmp['version'] = re.search(r'\d+(\.\d*)*', sys_info).group()
        if tmp["osname"] == "CentOS":
            if tmp["version"].startswith("8"):
                content = self.get_profile("/etc/firewalld/firewalld.conf")
                content = content.replace("FirewallBackend=nftables",
                                          "FirewallBackend=iptables")
                self.save_profile("/etc/firewalld/firewalld.conf", content)
                public.ExecShell("systemctl restart firewalld")
        return True


class firewalld:
    __TREE = None
    __ROOT = None
    __CONF_FILE = '/etc/firewalld/zones/public.xml'

    # 初始化配置文件XML对象
    def __init__(self):
        if self.__TREE: return
        if not os.path.exists(self.__CONF_FILE): return
        self.__TREE = ElementTree()
        self.__TREE.parse(self.__CONF_FILE)
        self.__ROOT = self.__TREE.getroot()

    # 获取规则列表
    def GetAcceptPortList(self):
        mlist = self.__ROOT.getchildren()
        data, arry = [], []
        for p in mlist:
            tmp = {}
            if p.tag == 'port':
                tmp["protocol"] = p.attrib['protocol']
                tmp['ports'] = p.attrib['port']
                tmp['types'] = 'accept'
                tmp['address'] = ''
            elif p.tag == 'forward-port':
                tmp["protocol"] = p.attrib['protocol']
                tmp["port"] = p.attrib['port']
                tmp["address"] = p.attrib.get('to-addr', '')
                tmp["to-port"] = p.attrib['to-port']
                arry.append(tmp)
                continue
            elif p.tag == 'rule':
                tmp["types"] = 'accept'
                tmp['ports'] = ''
                tmp['protocol'] = ''
                ch = p.getchildren()
                for c in ch:
                    if c.tag == 'port':
                        tmp['protocol'] = c.attrib['protocol']
                        tmp['ports'] = c.attrib['port']
                    elif c.tag == 'drop':
                        tmp['types'] = 'drop'
                    elif c.tag == 'reject':
                        tmp['types'] = 'reject'
                    elif c.tag == 'source':
                        if "address" in c.attrib.keys():
                            tmp['address'] = c.attrib['address']
            else:
                continue
            if tmp:
                data.append(tmp)
        return data, arry


class Sqlite():
    db_file = None  # 数据库文件
    connection = None  # 数据库连接对象

    def __init__(self):
        self.db_file = "/www/server/panel/data/default.db"
        self.create_table()

    # 获取数据库对象
    def GetConn(self):
        try:
            if self.connection == None:
                self.connection = sqlite3.connect(self.db_file)
                self.connection.text_factory = str
        except Exception as ex:
            import traceback
            traceback.print_exc()
            return "error: " + str(ex)

    def create_table(self):
        # 创建firewall_new表记录端口规则
        if not public.M('sqlite_master').where(
                'type=? AND name=?', ('table', 'firewall_new')).count():
            public.M('').execute('''CREATE TABLE "firewall_new" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "protocol" TEXT DEFAULT '',
                "ports" TEXT,
                "types" TEXT,
                "address" TEXT DEFAULT '',
                "brief" TEXT DEFAULT '',
                "addtime" TEXT DEFAULT '');''')
            public.M('').execute(
                'CREATE INDEX firewall_new_port ON firewall_new (ports);')

        # 创建firewall_ip表记录IP规则（屏蔽或放行）
        if not public.M('sqlite_master').where(
                'type=? AND name=?', ('table', 'firewall_ip')).count():
            public.M('').execute('''CREATE TABLE "firewall_ip" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "types" TEXT,
                "address" TEXT DEFAULT '',
                "brief" TEXT DEFAULT '',
                "addtime" TEXT DEFAULT '');''')
            public.M('').execute(
                'CREATE INDEX firewall_ip_addr ON firewall_ip (address);')

        # 创建firewall_trans表记录端口转发记录
        if not public.M('sqlite_master').where(
                'type=? AND name=?', ('table', 'firewall_trans')).count():
            public.M('').execute('''CREATE TABLE firewall_trans (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "start_port" TEXT,
                "ended_ip" TEXT,
                "ended_port" TEXT,
                "protocol" TEXT DEFAULT '',
                "addtime" TEXT DEFAULT '');''')
            public.M('').execute(
                'CREATE INDEX firewall_trans_port ON firewall_trans (start_port);'
            )

        # 创建firewall_country表记录IP规则（屏蔽或放行）
        if not public.M('sqlite_master').where(
                'type=? AND name=?', ('table', 'firewall_country')).count():
            public.M('').execute('''CREATE TABLE "firewall_country" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "types" TEXT,
                "country" TEXT DEFAULT '',
                "brief" TEXT DEFAULT '',
                "addtime" TEXT DEFAULT '');''')
            public.M('').execute(
                'CREATE INDEX firewall_country_name ON firewall_country (country);'
            )
        # 修复之前已经创建的 firewall_country 表无 ports 字段的问题
        create_table_str = public.M('sqlite_master').where(
            'type=? AND name=?', ('table', 'firewall_country')).getField('sql')
        if 'ports' not in create_table_str:
            public.M('').execute(
                'ALTER TABLE "firewall_country" ADD "ports" TEXT DEFAULT ""')

    def create_trigger(self, sql):
        self.GetConn()
        self.connection.text_factory = str
        try:
            result = self.connection.execute(sql)
            id = result.lastrowid
            self.connection.commit()
            self.rm_lock()
            return id
        except Exception as ex:
            return "error: " + str(ex)


sql = """
        CREATE TRIGGER update_port AFTER DELETE ON firewall
        when old.port!=''
        BEGIN
            delete from firewall_new where ports = old.port;
            delete from firewall_ip where address = old.port;
        END;
      """
s = Sqlite()
s.create_trigger(sql)