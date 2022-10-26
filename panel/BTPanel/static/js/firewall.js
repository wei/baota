var firewall = {
  event: function() {
    var that = this, name = bt.get_cookie('firewall_type');
    // 切换主菜单
    $('#cutTab').on('click', '.tabs-item', function () {
      var index = $(this).index(), name = $(this).data('name')
      var parent = $(this).parent().parent().nextAll('.tab-view-box').children('.tab-con').eq(index)
      var parentData = parent.data('name')
      $(this).addClass('active').siblings().removeClass('active');
      parent.addClass('show w-full').removeClass('hide').siblings().removeClass('show w-full').addClass('hide');
      that[name].event();
      bt.set_cookie('firewall_type',name)
      switch (name){
        case 'safety':
          that.safety.getFirewallIfo();
          break;
      }
    })
    $('[data-name="'+ (name || 'safety') +'"]').trigger('click')
  },
  // 系统防护墙
  safety:{
    /**
     * @description 事件绑定
     */
    event: function () {
      var that = this;
      bt.firewall.get_logs_size(function(rdata){
        $("#logSize").text(rdata);
      })


      // 切换系统防火墙菜单事件
      $('#safety').unbind('click').on('click', '.tab-nav-border span', function () {
        var index = $(this).index();
        $(this).addClass('on').siblings().removeClass('on');
        $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on');
        $('.state-content').show().find('.safety-header').show().siblings().hide()
        that.cutFirewallTab(index);
      })
      $('#isFirewall').unbind('click').click(function(){
        var _that = $(this)
        var status = !_that.prop("checked")
        bt.confirm({
          title:(status?'关闭':'启动')+'系统防火墙',
          msg:(status?'关闭系统防火墙，继续操作!':'启动系统防火墙，继续操作!'),
          cancel:function(){
            _that.prop("checked",status);
          }
        },function () {
          bt_tools.send({
            url:'/safe/firewall/firewall_admin',
            data:{data: JSON.stringify({status:!status?'start':'stop'})},
          },function(rdata){
            bt_tools.msg(rdata);
            setTimeout(function(){
              location.reload();
            },2000)
          },'设置防火墙状态')
        },function () {
          _that.prop("checked",status)
        })
      })
      $('#ssh_ping').unbind('click').on('click',function (){
        var _that = $(this), status = _that.prop("checked")?0:1;
        bt.firewall.ping(status,function(rdata){
          if(rdata === -1){
            _that.prop('checked',!!status);
          }else{
            bt.msg(rdata);
          }
        })
      })
      $('#safety .tab-nav-border span').eq(0).trigger('click');
    },
    /**
     * @description 清空日志
     */
    clear_logs_files:function(){
      bt.show_confirm('清空日志', '即将清空Web日志，是否继续？', function () {
        bt.firewall.clear_logs_files(function(rdata){
          $("#logSize").text(rdata);
          bt.msg({msg:lan.firewall.empty,icon:1});
        })
      })
    },

    /**
     * @description 切换系统防火墙菜单
     * @param {number} index 索引
     */
    cutFirewallTab: function (index) {
      switch (index) {
        case 0:
          this.portRuleTable()
          break;
        case 1:
          this.ipRuleTable()
          break;
        case 2:
          this.portForwardTable()
          break;
        case 3:
          this.countryRegionTable()
          break;
      }
    },

    /**
     * @description 获取防火墙信息
     */
    getFirewallIfo:function () {
      bt_tools.send({
        url: '/safe/firewall/get_firewall_info',
      },function (rdata){
        $('#isFirewall').prop("checked",rdata.status);
        $('#ssh_ping').prop('checked',!rdata.ping);
        $('#safety .tab-nav-border span:eq(0) > i').html(rdata.port)
        $('#safety .tab-nav-border span:eq(1) > i').html(rdata.ip)
        $('#safety .tab-nav-border span:eq(2) > i').html(rdata.trans)
        $('#safety .tab-nav-border span:eq(3) > i').html(rdata.country)
      },'获取系统防火墙状态')
    },

    /**
     * @description 渲染系统防火墙端口规则
     */
    portRuleTable: function () {
      var that = this;
      var portsPs = {
        "3306": "MySQL服务默认端口",
        "888": "phpMyAdmin默认端口",
        "22": "SSH远程服务",
        "20": "FTP主动模式数据端口",
        "21": "FTP协议默认端口",
        "39000-40000": "FTP被动模端口范围",
        "30000-40000": "FTP被动模端口范围",
        "11211": "Memcached服务端口",
        "873": "rsync数据同步服务",
        "8888": "宝塔Linux面板默认端口"
      }
      return bt_tools.table({
        el: '#portRules',
        url: '/safe/firewall/get_rules_list',
        load: '获取端口规则列表',
        default: '端口规则列表为空', // 数据为空时的默认提示
        autoHeight: true,
        beforeRequest: 'model',
        tootls: [
          { // 按钮组
            type: 'group',
            list: [{
              title: '添加端口规则',
              active: true,
              event: function (ev) {
                that.editPortRule()
              }
            }, {
              title: '导入规则',
              event: function (ev) {
                that.ruleImport('port_rule')
              }
            }, {
              title: '导出规则',
              event: function (ev) {
                that.ruleExport('port_rule')
              }
            }]
          },
          { // 搜索内容
            type: 'search',
            placeholder: '请输入端口或备注',
            searchParam: 'query', //搜索请求字段，默认为 search
          },
          // { // 批量操作
          //   type: 'batch', //batch_btn
          //   disabledSelectValue: '请选择需要批量操作的站点!',
          //   selectList: [{
          //     title: "删除项目",
          //     url: '/project/nodejs/remove_project',
          //     param: function (row) {
          //       return { data: JSON.stringify({ project_name: row.name }) }
          //     },
          //     refresh: true,
          //     callback: function (that) {
          //
          //     }
          //   }
          //   ],
          // },
          { //分页显示
            type: 'page',
            numberStatus: true, //　是否支持分页数量选择,默认禁用
            jump: true, //是否支持跳转分页,默认禁用
          }],
        column: [
          // {type: 'checkbox', class: '', width: 20},
          {title: '协议', fid: 'protocol', width: 100},
          {title: '端口', fid: 'ports', width: 150},
          {
            field: 'status',
            title: '状态<a href="https://www.bt.cn/bbs/thread-4708-1-1.html" class="bt-ico-ask" target="_blank" title="点击查看说明">?</a>',
            width: 150,
            type: 'text',
            template: function (item) {
              var status = '';
              switch (item.status) {
                case 0:
                  status = lan.firewall.status_not;
                  break;
                case 1:
                  status = lan.firewall.status_net;
                  break;
                default:
                  status = lan.firewall.status_ok;
                  break;
              }
              return status;
            }
          },
          {
            title: '策略',
            fid: 'types',
            width: 80,
            event:function(row){
              var status = !(row.types === 'accept')
              bt.confirm({
                title:(status?'允许':'拒绝')+'端口规则',
                msg:(status?'允许端口规则 [ '+ row.ports +' ]，继续操作!':'拒绝端口规则 [ '+ row.ports +' ]，继续操作!'),
              },function () {
                var param = $.extend(row,{types:row.types === 'accept'?'drop':'accept',source:row.address})
                delete param.addtime
                delete param.address
                bt_tools.send({
                  url: '/safe/firewall/modify_rules',
                  data: {data: JSON.stringify(param)},
                }, function (rdata) {
                  bt_tools.msg(rdata)
                  that.portRuleTable()
                },'修改状态')
              });
            },
            template: function (row) {
              return row.types === 'accept'?'<a href="javascript:;" class="bt_success">允许</a>':'<a href="javascript:;" class="bt_danger">拒绝</a>'
            }
          },
          {
            title: '来源',
            fid: 'address',
            width:100,
            template: function (row) {
              return row.address === ''?'<span>所有IP</span>':'<span title="'+ row.address +'">'+ row.address +'</span>'
            }
          },
          {title: '备注', fid: 'brief', type: 'text', template: function (row) {
              if (row.brief) return  '<span>'+  row.brief +'</span>';
              if (row.ports in portsPs) return '<span>'+ portsPs[row.ports] +'</span>';
              return '<span>'+ row.brief +'</span>';
            }},
          {title: '时间', fid: 'addtime', width:150},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '修改',
              event: function (row, index) {
                that.editPortRule(row)
              }
            }, {
              title: '删除',
              event: function (row, index) {
                that.removePortRule(row)
              }
            }]
          }]
      })
    },

    /**
     * @description 添加/编辑端口规则
     * @param {object} row 数据
     */
    editPortRule: function (row) {
      var isEdit = !!row, that = this;
      row = row || { protocol:'tcp',ports:'',types:'accept',address:'',brief:''}
      layer.open({
        type: 1,
        area:"420px",
        title: (!isEdit?'添加':'修改') + '端口规则',
        closeBtn: 2,
        shift: 5,
        shadeClose: false,
        btn: ['提交','取消'],
        content: '<form id="editPortRuleForm" class="bt-form bt-form pd20" onsubmit="return false"></form>',
        yes:function(index,layers){
          bt_tools.verifyForm('#editPortRuleForm',[
            {name:'ports',validator:function (value){
                if(!value) return '端口不能为空'
              }},
            {name:'address',validator:function (value,row){
                if(!value && row.choose !== 'all') return '指定IP不能为空'
              }},
          ],function(verify,form){
            if(verify){
              if(isEdit) form.address = form.choose === 'all'?'':form.address
              form['source'] = form.address
              // 添加、修改
              bt_tools.send({
                url: '/safe/firewall/' + (isEdit ? 'modify_rules' : 'create_rules'),
                data: {data: JSON.stringify($.extend({id: row.id}, form))}
              }, function (rdata) {
                bt.msg(rdata)
                if (rdata.status) {
                  layer.close(index)
                  that.portRuleTable()
                  that.getFirewallIfo()
                }
              }, (isEdit ? '编辑' : '添加') + '端口规则');
            }
          })
        },
        success:function(layero,index){
          bt_tools.fromGroup('#editPortRuleForm',[
            { label:'协议', width:'200px', name:'protocol', type:'select', options:[{value:'tcp',label:'TCP'},{value:'udp',label:'UDP'},{value:'tcp/udp',label:'TCP/UDP'}]},
            { label:'端口', width:'200px', name:'ports',readonly:(isEdit) , type:'text', placeholder:'请输入端口' },
            { label:'来源', width:'200px', name:'choose', type:'select', options:[{value:'all',label:'所有IP'},{value:'point',label:'指定IP'}], on:{change:function(ev,val,el){
                  $(this).data('line').next().toggle()
                }}},
            { label:'指定IP', width:'200px', name:'address', labelStyle:(row.address !== ''?'':'display:none'), placeholder:'请输入指定IP' },
            { label:'策略', width:'200px', name:'types', type:'select', options:[{value:'accept',label:'允许'},{value:'drop',label:'拒绝'}] },
            { label:'备注', width:'200px', name:'brief', type:'text' },
            { type:'tips', list:['支持添加多个端口，如：80,88','支持添加范围端口，如：90-99'] ,style:'padding-left: 55px;margin-top:5px;' }
          ],$.extend(row,{choose:row.address?'point':'all'}))
          if(isEdit) $('[name="ports"]').css({'background-color':'#eee','cusor':'no-drop'})
          bt_tools.setLayerArea(layero)
        }
      });
    },

    /**
     * @description 删除端口规则
     * @param {object} row 行数据
     */
    removePortRule: function (row){
      var that = this;
      layer.confirm('是否删除当前端口规则,是否继续？',{btn: ['确认','取消'],icon:3,closeBtn: 2,title:'删除规则'},function(index){
        layer.close(index);
        bt_tools.send({ url:'/safe/firewall/remove_rules', data:{data:JSON.stringify(row)}},function (rdata){
          bt.msg(rdata)
          if(rdata.status) {
            that.portRuleTable()
            that.getFirewallIfo()
          }
        },'删除当前端口规则')
      });
    },

    /**
     * @description ip规则列表
     */
    ipRuleTable: function () {
      var that = this;
      return bt_tools.table({
        el: '#ipRule',
        url: '/safe/firewall/get_ip_rules_list',
        load: '获取IP规则列表',
        default: 'IP规则列表为空', // 数据为空时的默认提示
        autoHeight: true,
        beforeRequest: 'model',
        tootls: [
          { // 按钮组
            type: 'group',
            list: [{
              title: '添加IP规则',
              active: true,
              event: function (ev) {
                that.editIpRule()
              }
            }, {
              title: '导入规则',
              event: function (ev) {
                that.ruleImport('ip_rule')
              }
            }, {
              title: '导出规则',
              event: function (ev) {
                that.ruleExport('ip_rule')
              }
            }]
          },
          { // 搜索内容
            type: 'search',
            placeholder: '请输入IP地址或备注',
            searchParam: 'query', //搜索请求字段，默认为 search
          },
          // { // 批量操作
          //   type: 'batch', //batch_btn
          //   disabledSelectValue: '请选择需要批量操作的站点!',
          //   selectList: [{
          //     title: "删除项目",
          //     url: '/project/nodejs/remove_project',
          //     param: function (row) {
          //       return {
          //         data: JSON.stringify({ project_name: row.name })
          //       }
          //     },
          //     refresh: true,
          //     callback: function (that) {
          //
          //     }
          //   }],
          // },
          { //分页显示
            type: 'page',
            numberStatus: true, //　是否支持分页数量选择,默认禁用
            jump: true, //是否支持跳转分页,默认禁用
          }
        ],
        column: [
          // {type: 'checkbox', class: '', width: 20},
          {fid: 'address', title: 'IP地址', width: 150},
          {fid: 'area', title: 'IP归属地&nbsp;' + (parseInt(bt.get_cookie('ltd_end')) < 0?'<a href="javascript:;" class="btlink" onclick="bt.soft.updata_ltd(true)">企业版专享</a>':''), template: function(row){
              var area = row.area;
              return '<span>'+ (area.continent || '') + (area.info || '--') +'</span>'
            }},
          {
            fid: 'types',
            title: '策略',
            width: 100,
            event:function (row){
              var status = !(row.types === 'accept')
              bt.confirm({
                title:(status?'放行':'停用')+'IP规则',
                msg:(status?'放行IP [ '+ row.address +' ]，继续操作!':'屏蔽IP [ '+ row.address +' ]，继续操作!'),
              },function () {
                var param = $.extend(row,{types:row.types === 'accept'?'drop':'accept'})
                bt_tools.send({
                  url: '/safe/firewall/modify_ip_rules',
                  data: {data: JSON.stringify(param)},
                }, function (rdata) {
                  bt_tools.msg(rdata)
                  that.ipRuleTable()
                },'修改状态')
              });
            },
            template: function (row) {
              return row.types === 'accept'?'<span class="bt_success cursor-pointer">放行</span>':'<span class="bt_danger cursor-pointer">屏蔽</span>'
            }
          },
          {fid: 'brief', title: '备注'},
          {fid: 'addtime', title: '时间', width:150},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '修改',
              event: function (row, index) {
                that.editIpRule(row)
              }
            }, {
              title: '删除',
              event: function (row, index) {
                that.removeIpRule(row)
              }
            }]
          }]
      })
    },

    /**
     * @description 编辑ip规则
     * @param { object } row 行数据
     */
    editIpRule: function (row){
      var isEdit = !!row, that = this;
      row = row || {types:'drop',address:'',brief:''}
      layer.open({
        type: 1,
        area:"420px",
        title: (!isEdit?'添加':'修改') + 'IP规则',
        closeBtn: 2,
        shift: 5,
        shadeClose: false,
        btn: ['提交','取消'],
        content: '<form id="editIpRuleForm" class="bt-form bt-form pd20" onsubmit="return false"></form>',
        yes:function(index,layers){
          bt_tools.verifyForm('#editIpRuleForm',[
            {name:'address',validator:function (value,row){
                if(!value) return 'IP地址不能为空'
              }},
          ],function(verify,form){
            if(verify){
              // 添加、修改
              bt_tools.send({
                url:'/safe/firewall/' + (isEdit?'modify_ip_rules':'create_ip_rules'),
                data:{data:JSON.stringify($.extend({id:row.id},form))}
              }, function (rdata) {
                bt.msg(rdata)
                if(rdata.status){
                  layer.close(index)
                  that.ipRuleTable()
                  that.getFirewallIfo()
                }
              },(isEdit?'编辑':'添加') + 'IP规则');
            }
          })
        },
        success:function(layero,index){
          bt_tools.fromGroup('#editIpRuleForm',[
            { label:'IP', width:'200px', name:'address',type:'textarea',readonly:isEdit,style:'height: 80px;width: 200px;line-height: 22px;'+ (isEdit?'background-color: rgb(238, 238, 238);':''), placeholder:'请输入IP地址' },
            { label:'策略', width:'200px', name:'types', type:'select', options:[{value:'accept',label:'放行'},{value:'drop',label:'屏蔽'}] },
            { label:'备注', width:'200px', name:'brief' },
            !isEdit?{ type:'tips', list:['支持添加IP：如果添加多个IP请用","隔开','支持添加IP段,如：192.168.0.0/24','支持添加IP范围,格式如：192.168.1.xx-192.168.1.xx，暂不支持跨网段范围'] ,style:'padding-left: 55px; margin-top:5px;' }:{type:'tips',list:[]}
          ],row)
          bt_tools.setLayerArea(layero)
        }
      })
    },

    /**
     * @description 删除端口规则
     */
    removeIpRule:function(row){
      var that = this;
      layer.confirm('是否删除当前IP规则,是否继续？',{btn:['确认','取消'],icon:3,closeBtn: 2,title:'删除规则'},function(index){
        layer.close(index);
        bt_tools.send({ url:'/safe/firewall/remove_ip_rules', data:{data:JSON.stringify(row)}},function (rdata){
          bt.msg(rdata)
          if(rdata.status) {
            that.ipRuleTable()
            that.getFirewallIfo()
          }
        },'删除规则')
      });
    },

    /**
     * @description 端口转发列表
     */
    portForwardTable: function () {
      var that = this;
      return bt_tools.table({
        el: '#portForward',
        url: '/safe/firewall/get_forward_list',
        load: '获取端口转发列表',
        default: '端口转发列表为空', // 数据为空时的默认提示
        autoHeight: true,
        beforeRequest: 'model',
        tootls: [
          { // 按钮组
            type: 'group',
            list: [{
              title: '添加端口转发',
              active: true,
              event: function (ev) {
                that.editPortForward()
              }
            }, {
              title: '导入规则',
              event: function (ev) {
                that.ruleImport('trans_rule')
              }
            }, {
              title: '导出规则',
              event: function (ev) {
                that.ruleExport('trans_rule')
              }
            }]
          },
          { // 搜索内容
            type: 'search',
            placeholder: '请输入端口号',
            searchParam: 'query', //搜索请求字段，默认为 search
          },
          // { // 批量操作
          //   type: 'batch', //batch_btn
          //   disabledSelectValue: '请选择需要批量操作的站点!',
          //   selectList: [{
          //     title: "删除项目",
          //     url: '/project/nodejs/remove_project',
          //     param: function (row) {
          //       return {
          //         data: JSON.stringify({ project_name: row.name })
          //       }
          //     },
          //     refresh: true,
          //     callback: function (that) {
          //
          //     }
          //   }],
          // },
          { //分页显示
            type: 'page',
            numberStatus: true, //　是否支持分页数量选择,默认禁用
            jump: true, //是否支持跳转分页,默认禁用
          }
        ],
        column: [
          // {type: 'checkbox',  width: 20},
          {title: '协议',fid: 'protocol',  width: 100},
          {title: '源端口', fid: 'start_port'},
          {title: '目标IP', fid: 'ended_ip', template: function (row) {
              return '<span>'+ (row.ended_ip?row.ended_ip:'127.0.0.1') +'</span>'
            }
          },
          {title: '目标端口', fid: 'ended_port'},
          {title: '添加时间', fid: 'addtime', width: 150},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '修改',
              event: function (row, index) {
                that.editPortForward(row)
              }
            }, {
              title: '删除',
              event: function (row, index) {
                that.removePortForward(row)
              }
            }]
          }],
      })
    },

    /**
     * @description 添加/修改端口转发
     * @param row
     */
    editPortForward: function (row) {
      var isEdit = !!row, that = this;
      row = row || { protocol:'tcp', s_ports:'',d_address:'',d_ports:'' }
      layer.open({
        type: 1,
        area:"420px",
        title: (!isEdit?'添加':'修改') + '端口转发规则',
        closeBtn: 2,
        shift: 5,
        shadeClose: false,
        btn: ['提交','取消'],
        content: '<form id="editIpRuleForm" class="bt-form bt-form pd20" onsubmit="return false"></form>',
        yes:function(index,layers){
          bt_tools.verifyForm('#editIpRuleForm',[
            {name:'s_ports',validator:function (value,row){
                if(!value) return '源端口不能为空'
                if(!bt.check_port(value)) return '源端口格式错误，可用范围：1-65535'
              }},
            {name:'d_ports',validator:function (value,row){
                if(!value) return '目标端口不能为空'
                if(!bt.check_port(value)) return '目标端口格式错误，可用范围：1-65535'
              }},
          ],function(verify,form){
            if(verify){
              // 添加、修改
              if(form['d_address'] === '') form['d_address'] = '127.0.0.1'
              bt_tools.send({
                url:'/safe/firewall/' + (isEdit?'modify_forward':'create_forward'),
                data:{data:JSON.stringify($.extend({id:row.id},form))}
              }, function (rdata) {
                bt.msg(rdata)
                if(rdata.status){
                  layer.close(index)
                  that.portForwardTable()
                  that.getFirewallIfo()
                }
              },(isEdit?'编辑':'添加') + '端口转发');
            }
          })
        },
        success:function(layero,index){
          if(typeof row.id !== 'undefined') row = {s_ports:row.start_port,d_address:row.ended_ip,d_ports:row.ended_port,protocol:row.protocol,id:row.id}
          bt_tools.fromGroup('#editIpRuleForm',[
            { label:'协议', width:'200px', name:'protocol', type:'select', options:[{value:'tcp',label:'TCP'},{value:'udp',label:'UDP'},{value:'tcp/udp',label:'TCP/UDP'}]},
            { label:'源端口', width:'200px', name:'s_ports', type:'text', placeholder:'请输入源端口' },
            { label:'目标IP', width:'200px', name:'d_address', placeholder:'请输入目标IP地址' },
            { label:'目标端口', width:'200px', name:'d_ports', type:'text', placeholder:'请输入目标端口' },
            { type:'tips', list:['如果是本机端口转发，目标IP为：127.0.0.1','如果目标IP不填写，默认则为本机端口转发!'] ,style:'padding-left: 55px; margin-top:5px;' }
          ],row)
          bt_tools.setLayerArea(layero)
        }
      })

    },

    /**
     * @description 删除端口转发
     * @param {object} row 当前行数据
     */
    removePortForward: function (row) {
      var that = this;
      layer.confirm('是否删除当前规则,是否继续？',{btn:['确认','取消'],icon:3,closeBtn: 2,title:'删除规则'},function(index){
        layer.close(index);
        bt_tools.send({
          url:'/safe/firewall/remove_forward',
          data:{data:JSON.stringify({id:row.id,protocol:row.protocol,s_port:row.start_port,d_ip:row.ended_ip,d_port:row.ended_port})}
        }, function (rdata) {
          bt.msg(rdata)
          if(rdata.status) {
            that.portForwardTable()
            that.getFirewallIfo()
          }
        },'删除规则')
      });
    },

    /**
     * @description 国家区域
     */
    countryRegionTable: function () {
      var that = this;
      return bt_tools.table({
        el: '#countryRegion',
        url: '/safe/firewall/get_country_list',
        load: '获取区域规则列表',
        default: '区域规则为空', // 数据为空时的默认提示
        autoHeight: true,
        beforeRequest: 'model',
        column: [
          // {type: 'checkbox', class: '', width: 20},
          {fid: 'country', title: '地区', width: 180,
            template:function (row){
              return '<span>'+ row.country + '(' + row.brief + ')</span>'
            }
          },
          {
            fid: 'types',
            title: '策略',
            width: 100,
            template: function (row) {
              return row.types === 'accept'?'<span class="bt_success">放行</span>':'<span class="bt_danger">屏蔽</span>'
            }
          },
          {fid: 'ports', title: '端口',template:function (row){
              return '<span>' + (!row.ports?'全部':row.ports) + '</span>'
            }},
          {fid: 'addtime', title: '时间', width:150},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '修改',
              event: function (row, index) {
                that.editCountryRegion(row);
              }
            }, {
              title: '删除',
              event: function (row, index) {
                that.removeCountryRegion(row);
              }
            }]
          }],
        tootls: [
          { // 按钮组
            type: 'group',
            list: [{
              title: '添加地区规则',
              active: true,
              event: function (ev) {
                that.editCountryRegion()
              }
            }, {
              title: '导入规则',
              event: function (ev) {
                that.ruleImport('country_rule')
              }
            }, {
              title: '导出规则',
              event: function (ev) {
                that.ruleExport('country_rule')
              }
            }]
          },
          { // 搜索内容
            type: 'search',
            placeholder: '请输入区域',
            searchParam: 'query', //搜索请求字段，默认为 search
          },
          // { // 批量操作
          //   type: 'batch', //batch_btn
          //   disabledSelectValue: '请选择需要批量操作的站点!',
          //   selectList: [{
          //     title: "删除项目",
          //     url: '/project/nodejs/remove_project',
          //     param: function (row) {
          //       return {
          //         data: JSON.stringify({ project_name: row.name })
          //       }
          //     },
          //     refresh: true,
          //     callback: function (that) {
          //
          //     }
          //   }],
          // },
          { //分页显示
            type: 'page',
            numberStatus: true, //　是否支持分页数量选择,默认禁用
            jump: true, //是否支持跳转分页,默认禁用
          }
        ]
      })
    },

    /**
     * @description 添加/修改端口转发
     * @param row
     */
    editCountryRegion:function (row) {
      var isEdit = !!row, that = this;
      row = row || { country:'美国', types:'drop',brief:'US',ports:'' }
      bt_tools.send({
        url:'/safe/firewall/get_countrys',
      },  function (rdata) {
        layer.open({
          type: 1,
          area:"420px",
          title: (!isEdit?'添加':'修改') + '区域规则',
          closeBtn: 2,
          shift: 5,
          shadeClose: false,
          btn: ['提交','取消'],
          content: '<form id="editCountryRegionForm" class="bt-form bt-form pd20" onsubmit="return false"></form>',
          yes:function(index,layers){
            bt_tools.verifyForm('#editCountryRegionForm',[
              {name:'ports',validator:function (value,row){
                  if(!value && row.choose !== 'all') return '指定端口不能为空'
                }},
            ],function(verify,form){
              if(verify){
                // 添加、修改
                form['brief'] = form.country
                form['country'] = $('[name="country"]').find(':selected').text()
                bt_tools.send({
                  url:'/safe/firewall/' + (isEdit?'modify_country':'create_country'),
                  data:{data:JSON.stringify($.extend({id:row.id},form))}
                }, function (rdata) {
                  bt.msg(rdata)
                  if(rdata.status){
                    layer.close(index)
                    that.countryRegionTable()
                    that.getFirewallIfo()
                  }
                },(isEdit?'编辑':'添加') + '区域规则');
              }
            })
          },
          success:function(layero,index){
            var options = []
            for (var i = 0; i < rdata.length; i++) {
              var item = rdata[i]
              options.push({
                label: item.CH,
                value: item.brief
              })
            }
            bt_tools.fromGroup('#editCountryRegionForm',[
              { label:'地区', width:'200px', name:'country', type:'select', options:options },
              { label:'策略', width:'200px', name:'types', type:'select', options:[{value:'drop',label:'屏蔽'}]},
              { label:'端口', width:'200px', name:'choose', type:'select', options:[{value:'all',label:'所有端口'},{value:'point',label:'指定端口'}], on:{change:function(ev,val,el){
                    $(this).data('line').next().toggle()
                  }}},
              { label:'指定端口', width:'200px', name:'ports', labelStyle:'display:none',type:'text', placeholder:'请输入指定端口' },
              { type:'tips', list:['暂只支持输入单个地区名称！','请注意：如果屏蔽了本地区,本地区就访问不了！','指定端口既可以输入单个端口,也可以输入多个端口,多个端口之间用","隔开！'] ,style:'padding-left: 55px; margin-top:5px;' }
            ])
            bt_tools.setLayerArea(layero)
          }
        })
      },'获取国家区域列表')
    },

    /**
     * @description 删除端口转发
     * @param {object} row 当前行数据
     */
    removeCountryRegion: function (row) {
      var that = this;
      layer.confirm('是否删除当前区域规则,是否继续？',{btn:['确认','取消'],icon:3,closeBtn: 2,title:'删除规则'},function(index){
        layer.close(index);
        bt_tools.send({
          url:'/safe/firewall/remove_country',
          data:{data:JSON.stringify(row)}
        }, function (rdata) {
          bt.msg(rdata)
          if(rdata.status) {
            that.countryRegionTable()
            that.getFirewallIfo()
          }
        },'删除规则')
      });
    },

    /**
     * @description 规则导入
     * @param
     */
    ruleImport: function (name){
      var _this = this;
      layer.open({
        type: 1,
        area:"400px",
        title: '导入规则',
        closeBtn: 2,
        shift: 5,
        shadeClose: false,
        btn:['导入','取消'],
        content:'<div class="bt-form bt-form" style="padding:15px 0px">\
								<div class="line" style="text-align: center;">\
                          <div class="info-r c4" style="margin-left:70px;">\
                              <div class="detect_input">\
                                  <input type="text" class="input_file" placeholder="请选择文件" style="width:170px;">\
                                  <input type="file" class="file_input" name="点我上传" id="fileInput" style="display:none;"/>\
                                  <button type="button" class="select_file" onclick="$(\'#fileInput\').click()">选择文件</button>\
                              </div>\
                          </div>\
                      </div>\
							</div>',
        yes:function(index,layers){
          if (!$("#fileInput")[0].files[0]){
            layer.msg('请选择要导入的文件!',{icon:2});
            return false;
          }
          _this.upload({name:name, _fd:$("#fileInput")[0].files[0]}, 0, index);
        },
        success:function(){
          $("#fileInput").on('change',function(){
            if(!$("#fileInput")[0].files[0]){
              $(".input_file").val("");
            }
            var filename = $("#fileInput")[0].files[0].name;
            $(".input_file").val(filename)
          });
        },
      });
    },

    /**
     * @description 规则导出
     */
    ruleExport: function (type){
      bt_tools.send({
        url: '/safe/firewall/export_rules',
        data:{data:JSON.stringify({rule_name:type})},
      },function (rdata){
        if(rdata.status){
          window.open('/download?filename='+rdata.msg);
        }else{
          bt_tools.msg(rdata);
        }
      },'导出规则')
    },

    /**
     * @description 规则导入请求
     * @param s_data
     * @param start
     * @param index
     */
    upload: function (s_data, start, index) {
      var _this = this;
      var fd = s_data._fd;
      var end = Math.min(fd.size, start + 1024*1024*2);
      var form = new FormData();
      form.append("f_path", "/www/server/panel/data/firewall");
      form.append("f_name", fd.name);
      form.append("f_size", fd.size);
      form.append("f_start", start);
      form.append("blob", fd.slice(start, end));
      $.ajax({
        url: '/files?action=upload',
        type: "POST",
        data: form,
        async: true,
        processData: false,
        contentType: false,
        success: function (data) {
          if (typeof (data) === "number") {
            _this.upload(s_data, data, index)
          } else {
            if (data.status) {
              bt_tools.send({
                url:'/safe/firewall/import_rules',
                data:{data:JSON.stringify({rule_name:s_data.name, file_name:fd.name})}
              },function(res){
                bt_tools.msg(res);
                if(res.status){
                  layer.close(index);
                  if(s_data.name === 'port_rule'){ _this.portRuleTable() }
                  else if(s_data.name === 'ip_rule'){ _this.ipRuleTable() }
                  else if(s_data.name === 'country_rule'){ _this.countryRegionTable() }
                  else{ _this.portForwardTable() }
                }
              },'导入规则')
            }
          }
        },
        error: function (e) {
          console.log("上传规则文件出问题喽!")
        }
      })
    },
  },
  // SSH管理
  ssh:{
    /**
     * @description SSH管理列表
     */
    event:function (){
      var that = this;
      // 切换系统防火墙菜单事件
      $('#sshView').unbind('click').on('click', '.tab-nav-border span', function () {
        var index = $(this).index();
        $(this).addClass('on').siblings().removeClass('on');
        $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on');
        $('.state-content').show().find('.ssh-header').show().siblings().hide();
        that.cutSshTab(index);
      })

      $('#sshView .tab-nav-border span').eq(0).trigger('click');

      // SSH开关
      $('#isSsh').unbind('click').on('click',function(){
        var _that = $(this), status = _that.prop("checked")?0:1;
        bt.firewall.set_mstsc_status(status,function(rdata){
          if(rdata === -1){
            _that.prop("checked",!!status);
          }else{
            bt.msg(rdata);
            that.getSshInfo();
          }
        });
      })

      // 保存SSH端口
      $('.save_ssh_port').unbind('click').on('click',function (){
        var port = $(this).prev().val();
        if(port === '') return bt.msg({msg:'端口不能为空！',icon:2});
        if(!bt.check_port(port)) return bt.msg({msg:'端口格式正确！',icon:2});
        bt.firewall.set_mstsc(port);
      })

      // root登录
      $('[name="root_login"]').unbind('change').on('change',function(){
        // var _that = $(this), status = _that.prop("checked");
        var root_type = $(this).val();
        bt_tools.send({
          url:'/ssh_security?action=set_root',
          data:{p_type:root_type}
        },function (rdata){
          bt_tools.msg(rdata)
        },'设置SSH设置')
      })

      // SSH密码登录
      $('[name="ssh_paw"]').unbind('click').on('click',function (){
        var _that = $(this), start = _that.prop("checked");
        bt_tools.send({
          url:'/ssh_security?action=' + (start?'set_password':'stop_password')
        },function (rdata){
          bt_tools.msg(rdata)
        },'设置SSH密码登录状态')
      })

      // SSH密钥登录
      $('[name="ssh_pubkey"]').unbind('click').on('click',function(){
        var _that = $(this);
        var start = _that.prop("checked");
        if(start){
          that.setTemplateSshkey();
        }else{
          bt_tools.send({
            url:'/ssh_security?action=stop_key'
          },function (rdata){
            that.getSeniorSshInfo();
            bt_tools.msg(rdata);
          },'关闭SSH密钥登录')
        }
      })

      // 登录告警
      $('[name="ssh_login_give"]').unbind('click').on('click',function(){
        var _that = $(this), status = _that.prop("checked");
        bt_tools.send({
          url:'/ssh_security?action=' + (status?'start_jian':'stop_jian')
        },function (rdata){
          bt_tools.msg(rdata)
        },'设置SSH登录告警')
      })

      // 查看密钥
      $('.checkKey').unbind('click').on('click',function (){
        that.setSshKeyView()
      })

      // 设置登录告警
      $('.setSshLoginAlarm').unbind('click').on('click',function (){
        that.setSshLoginAlarmView();
      });

      // 下载密钥
      $('.downloadKey').unbind('click').on('click',function (){
        bt_tools.send({
          url:'/ssh_security?action=get_key'
        },function (rdata){
          if(!rdata.msg) return layer.msg('请重新开启SSH密钥登录再下载密钥！');
          window.open('/ssh_security?action=download_key')
        })
      })

      // 登录详情
      $('#sshDetailed').unbind('click').on('click','a',function (){
        var index = $(this).data('index');
        $('#sshView .tab-nav-border>span').eq(1).trigger('click');
        $('.cutLoginLogsType button').eq(index).trigger('click');
      })

      // 防爆破
      $('#fail2ban').unbind('click').on('click','a',function(){
        var type = $(this).data('type');
        switch (type){
          case 'install':
            bt.soft.install('fail2ban')
            break;
          case 'open':
            bt.soft.set_lib_config('fail2ban','Fail2ban防爆破')
            break;
        }
      })

      // 切换登录日志类型
      $('#loginLogsContent').unbind('click').on('click','.cutLoginLogsType button',function(){
        var type = $(this).data('type');
        $(this).addClass('btn-success').removeClass('btn-default').siblings().addClass('btn-default').removeClass('btn-success');
        $('#loginLogsContent>div:eq('+ type +')').show().siblings().hide();
        that.loginLogsTable({p:1,type: Number(type)});
      })

      // 刷新登录日志
      $('#refreshLoginLogs').unbind('click').on('click',function(){
        var type = $('#cutLoginLogsType button.btn-success').data('type');
        that.loginLogsTable({type:type });
      });
    },

    /**
     * @description 切换SSH菜单
     * @param {number} index 索引
     */
    cutSshTab:function (index){
      switch (index){
        case 0:
          this.getSshInfo();
          this.getLoginAlarmInfo();
          this.getSeniorSshInfo();
          this.getSshLoginAlarmInfo();
          break;
        case 1:
          this.loginLogsTable();
          break;
      }
    },
    /**
     * @description 获取登录告警信息
     */
    getLoginAlarmInfo:function(){
      bt_tools.send({
        url:'/ssh_security?action=get_jian'
      },function (rdata){
        $('#ssh_login_give').prop('checked',rdata.status);
      }, {load:'获取登录告警状态',verify:false})
    },

    /**
     * @description 设置密钥登录
     */
    setTemplateSshkey:function(){
      var _this = this;
      layer.open({
        title:'开启SSH密钥登录',
        area:'400px',
        type:1,
        closeBtn: 2,
        btn:['提交','关闭'],
        content:'<div class="bt-form bt-form pd20">'+
            '<div class="line "><span class="tname">SSH密码登录</span><div class="info-r "><select class="bt-input-text mr5 ssh_select_login" style="width:200px"><option value="yes">开启</option><option value="no">关闭</option></select></div></div>'+
            '<div class="line "><span class="tname">密钥加密方式</span><div class="info-r "><select class="bt-input-text mr5 ssh_select_encryption" style="width:200px"><option value="ed25519">ED25519(推荐)</option><option value="ecdsa">ECDSA</option><option value="rsa">RSA</option><option value="dsa">DSA</option></select></div></div>'+
            '</div>',
        yes:function(indexs){
          var ssh_select_login = $('.ssh_select_login').val();
          var ssh_select_encryption = $('.ssh_select_encryption').val();
          bt_tools.send({
            url:'/ssh_security?action=set_sshkey',
            data:{ ssh:ssh_select_login, type:ssh_select_encryption }
          },function (rdata){
            bt_tools.msg(rdata)
            layer.close(indexs)
            _this.getSeniorSshInfo()
          },'开启SSH密钥登录')
        },
        cancel:function(index){
          $('[name="ssh_pubkey"]').prop('checked',false);
        },
        btn2:function(index){
          $('[name="ssh_pubkey"]').prop('checked',false);
        }
      })
    },

    /**
     * @description 设置SSH登录告警
     */
    setSshLoginAlarmView:function(){
      var that = this;
      layer.open({
        title:'SSH登录告警',
        area: '1010px',
        type: 1,
        closeBtn: 2,
        content: '\
				<div class="bt-w-main">\
					<div class="bt-w-menu">\
						<p class="bgw">登录日志</p>\
						<p>IP白名单</p>\
					</div>\
					<div class="bt-w-con pd15">\
						<div class="plugin_body">\
							<div class="content_box news-channel active">\
								<div class="bt-form-new inline"></div>\
								<div id="login_logs_table" class="divtable mt10">\
									<div style="width: 100%; border: 1px solid #ddd; overflow: auto;">\
										<table class="table table-hover" style="border: none;">\
											<thead>\
												<tr>\
													<th>详情</th>\
													<th class="text-right">添加时间</th>\
												</tr>\
											</thead>\
											<tbody>\
												<tr>\
													<td colspan="2" class="text-center">暂无数据</td>\
												</tr>\
											</tbody>\
										</table>\
									</div>\
									<div class="page"></div>\
								</div>\
								<ul class="help-info-text c7">\
									<li></li>\
								</ul>\
							</div>\
							<div class="content_box hide">\
								<div class="bt-form">\
									<div class="box" style="display:inline-block;">\
										<input name="ipAddress" class="bt-input-text mr5" type="text" style="width: 220px;" placeholder="请输入IP" />\
										<button class="btn btn-success btn-sm addAddressIp">添加</button>\
									</div>\
								</div>\
								<div id="whiteIpTable"></div>\
								<ul class="help-info-text c7">\
									<li style="list-style:inside disc">只允许设置ipv4白名单</li>\
								</ul>\
							</div>\
						</div>\
					</div>\
				</div>',
        success: function ($layer, indexs) {
          // layer
          var _that = this;

          // 切换菜单
          $layer.find('.bt-w-menu p').click(function () {
            var index = $(this).index();
            $(this).addClass('bgw').siblings('.bgw').removeClass('bgw');
            $layer.find('.content_box').addClass('hide');
            $layer.find('.content_box').eq(index).removeClass('hide');
            switch (index) {
                // 登录日志
              case 0:
                _that.renderAlarm();
                _that.renderLogsTable(1, false);
                break;
                // IP白名单
              case 1:
                _that.renderWhiteIpTable()
                break;
            }
          });

          // 设置告警通知
          $('.news-channel .bt-form-new').on('change', 'input[type="checkbox"]', function () {
            var $this = $(this);
            var name = $this.attr('name');
            var checked = $this.is(':checked');
            var action = checked ? 'set_login_send' : 'clear_login_send'
            bt_tools.send({
              url: '/ssh_security?action=' + action,
              data:{ type: name }
            }, function (rdata) {
              bt_tools.msg(rdata);
              if (rdata.status) {
                if (checked) {
                  $('.news-channel .bt-form-new input[type="checkbox"]').prop('checked', false);
                  $this.prop('checked', true);
                }
                that.getSshLoginAlarmInfo();
              }
            }, '配置告警通知');
          });

          // 登录日志分页操作
          $('#login_logs_table .page').on('click', 'a', function (e) {
            e.stopPropagation();
            e.preventDefault();
            var page = $(this)
                .attr('href')
                .match(/p=([0-9]*)/)[1];
            _that.renderLogsTable(page);
          });

          // 添加ip
          $('.addAddressIp').click(function () {
            var address = $('[name="ipAddress"]');
            var ip = address.val();
            address.val('');
            if (!ip) {
              bt_tools.msg({ msg:'请输入IP地址', status: false });
              return;
            }
            bt_tools.send({
              url:'/ssh_security?action=add_return_ip',
              data:{ ip: ip }
            }, function (rdata) {
              bt_tools.msg(rdata);
              _that.renderWhiteIpTable();
            },'添加白名单')
          });

          $layer.find('.bt-w-menu p').eq(0).click();
        },
        // 生成告警
        renderAlarm: function () {
          var load = bt_tools.load('获取SSH登录告警配置，请稍候...');
          // 获取告警列表
          bt_tools.send({
            url: '/ssh_security?action=get_msg_push_list',
          }, function (alarms) {
            // 获取选中告警
            bt_tools.send({
              url: '/ssh_security?action=get_login_send',
            }, function (send) {
              load.close();
              var html = '';
              var tits = [];
              // 当前选中的告警key
              var cKey = send.msg;
              // 渲染生成告警列表
              $.each(alarms, function (key, item) {
                if (item.name === 'sms') return;
                var checked = cKey === item.name ? 'checked="checked"' : '';
                html += '\
								<div class="form-item">\
									<div class="form-label">通知' + item.title + '</div>\
									<div class="form-content">\
										<input type="checkbox" id="' + item.name + '_alarm" class="btswitch btswitch-ios" ' + checked + ' name="' + item.name + '" />\
										<label class="btswitch-btn" for="' + item.name + '_alarm"></label>\
									</div>\
								</div>';
                tits.push(item.title);
              });
              $('.news-channel .bt-form-new').html(html);
              $('.news-channel .help-info-text li').eq(0).text(tits.join('/') + '只能同时开启一个');
            });
          });
        },
        // 生成日志表格
        renderLogsTable: function (p, load) {
          p = p || 1;
          load = load !== undefined ? load : true;
          if (load) var loadT = bt_tools.load('正在获取登录日志，请稍候...');
          bt_tools.send({
            url: '/ssh_security?action=get_logs',
            data: { p: p, p_size: 8, }
          }, function (rdata) {
            if (load) loadT.close();
            var html = '';
            if (rdata.data) {
              for (var i = 0; i < rdata.data.length; i++) {
                var item = rdata.data[i];
                html += '<tr><td style="white-space: nowrap;" title="' + item.log + '">' + item.log + '</td><td class="text-right">' + item.addtime + '</td></tr>';
              }
            }
            html = html || '<tr><td class="text-center">暂无数据</td></tr>';
            $('#login_logs_table table tbody').html(html);
            $('#login_logs_table .page').html(rdata.page || '');
          });
        },
        // 生成IP白名单表格
        renderWhiteIpTable: function () {
          var _that = this;
          if (this.ipTable) {
            this.ipTable.$refresh_table_list();
            return;
          }
          this.ipTable = bt_tools.table({
            el: '#whiteIpTable',
            url: '/ssh_security?action=return_ip',
            load: '获取SSH登录白名单',
            autoHeight: true,
            height: '425px',
            default: "SSH登录白名单为空",
            dataFilter: function (data) {
              return { data: data.msg };
            },
            column: [
              {
                title: 'IP地址',
                template: function (item) {
                  return '<span>'+ item + '</span>';
                }
              },
              {
                title: '操作',
                type: 'group',
                width: 150,
                align: 'right',
                group: [
                  {
                    title: '删除',
                    event: function (row, index) {
                      bt_tools.send({
                        url: '/ssh_security?action=del_return_ip',
                        data: { ip: row }
                      },function (rdata){
                        bt_tools.msg(rdata)
                        _that.renderWhiteIpTable();
                      }, '删除IP白名单');
                    }
                  }
                ]
              }
            ]
          })
        }
      })
    },

    /**
     * @description 设置SSH密钥视图
     */
    setSshKeyView:function(){
      bt_tools.send({
        url:'/ssh_security?action=get_key'
      },function (rdata){
        if(!rdata.msg) return layer.msg('请重新开启SSH密钥登录再查看密钥！');
        layer.open({
          title:'SSH登录密钥',
          area:'400px',
          type:1,
          closeBtn: 2,
          content:'<div class="bt-form pd20">\
            <textarea id="ssh_text_key" class="bt-input-text mb10" style="height:220px;width:360px;line-height: 22px;">'+ rdata.msg +'</textarea>\
            <div class="btn-sshkey-group">\
              <button type="button" class="btn btn-success btn-sm mr5 btn-copy-sshkey">复制</button>\
              <button type="button" class="btn btn-success btn-sm btn-download-sshkey">下载</button>\
            </div>\
          </div>',
          success:function (layers,indexs){
            $('.btn-copy-sshkey').on('click',function(){
              bt.pub.copy_pass($('#ssh_text_key').val());
            })
            $('.btn-download-sshkey').on('click',function(){
              window.open('/ssh_security?action=download_key')
            })
          }
        })
      },'获取SSH登录密钥')
    },

    /**
     * @description 获取SSH信息
     */
    getSshInfo:function (){
      bt_tools.send({
        url: '/safe/ssh/GetSshInfo',
        verify: false
      },function (rdata){
        var error = rdata.error;
        $('#fail2ban').html(rdata.fail2ban?'<a href="javascript:;" class="btlink" data-type="open">已安装，查看详情</a>':'<a href="javascript:;" style="color: red;" data-type="install">未安装，点击安装</a>');
        $('#sshDetailed').html('<a href="javascript:;" class="btlink" data-index="1">成功：'+ error.success +'</a><span style="margin: 0 8px">/</span><a href="javascript:;" style="color: red;" data-index="2">失败：'+ error.error +'</a>');
        $('#isSsh').prop("checked",rdata.status);
        $('[name="ssh_port"]').val(rdata.port);
      },'SSH配置信息');
    },
    /**
     * @description 获取高级SSH信息
     */
     getSeniorSshInfo:function (){
        bt_tools.send({
          url: '/ssh_security?action=get_config',
          verify: false
        },function (rdata){
          $('[name="ssh_paw"]').prop("checked",rdata.password === 'yes');
          $('[name="ssh_pubkey"]').prop("checked",rdata.pubkey === 'yes');

          var root_option = '';
          $.each(rdata.root_login_types,function(k,v){
              root_option += '<option value="'+ k +'" '+(rdata.root_login_type == k?'selected':'')+'>'+ v +'</option>';
          })
          $('[name="root_login"]').html(root_option);
          // $('[name="root_login"]').prop("checked",rdata.root_is_login === 'yes')
        },'SSH高级配置信息');
      },
    /**
     * @description 获取SSH登录告警
     */
    getSshLoginAlarmInfo: function () {
      var that = this;
      bt_tools.send({
        url: '/ssh_security?action=get_login_send',
        verify: false
      }, function (send) {
        var data = that.msgPushData;
        if (!data || $.isEmptyObject(data)) {
          bt_tools.send({
            url: '/ssh_security?action=get_msg_push_list',
            verify: false
          }, function (msgData) {
            that.msgPushData = msgData
            that.renderLoginAlarmInfo(send);
          });
        } else {
          that.renderLoginAlarmInfo(send);
        }

      },'SSH登录告警配置');
    },
    /**
     * @description 渲染SSH登录告警配置
     */
    renderLoginAlarmInfo: function (send) {
      var data = this.msgPushData || {};
      var map = {}
      $.each(data, function (key, item) {
        if (key === 'sms') return
        map[key] = item.title
      });
      var key = send.msg;
      var title = map[key];
      if (send.status && title) {
        $('a.setSshLoginAlarm').removeClass('bt_warning').addClass('btlink');
        $('a.setSshLoginAlarm').text(title + '已配置');
      } else {
        $('a.setSshLoginAlarm').addClass('bt_warning').removeClass('btlink');
        $('a.setSshLoginAlarm').text('告警通知未配置');
      }
    },

    /**
     * @description 登录日志
     */
    loginLogsTable:function(param){
      if(!param) param = { p:1, type:0 };
      var logs = [['All','日志','get_ssh_list'],['Success','成功日志','get_ssh_success'],['Error','失败日志','get_ssh_error']];
      var type = logs[param.type][0] , tips = logs[param.type][1];
      var that = this;
      $('#login'+ type +'Logs').empty();
      var arry = ['全部','登录成功','登录失败'];
      var html = $('<div class="btn-group mr10 cutLoginLogsType"></div>');
      $.each(arry,function (i,v){
        html.append('<button type="button" class="btn btn-sm btn-'+ (i === param.type ?'success':'default') +'" data-type="'+ i +'">'+ v +'</button>')
      })
      return bt_tools.table({
        el: '#login'+ type +'Logs',
        url: '/safe/syslog/' + logs[param.type][2],
        load: '获取SSH登录' + tips,
        default: 'SSH登录'+ tips +'为空', // 数据为空时的默认提示
        autoHeight: true,
        dataVerify:false,
        tootls: [
          { // 按钮组
            type: 'group',
            list: [{
              title: '刷新列表',
              active: true,
              event: function (ev,that) {
                that.$refresh_table_list(true)
              }
            }]
          },
          { // 搜索内容
            type: 'search',
            placeholder: '请输入登录IP/用户名',
            searchParam: 'search', //搜索请求字段，默认为 search
          },
          { //分页显示
            type: 'page',
            number: 20
          }
        ],
        dataFilter: function (data) {
          if(typeof data.status === "boolean" && !data.status){
            $('#loginLogsContent').hide().next().show();
            return { data: [] }
          }
          return {data:data}
        },
        beforeRequest: function (data) {
          if(typeof data.data === "string"){
            delete data.data
            return {data: JSON.stringify(data)}
          }
          return {data: JSON.stringify(data)}
        },
        column: [
          {title: 'IP地址:端口',fid: 'address',width:'150px', template:function (row){
              return '<span>'+ row.address +':' + row.port + '</span>';
            }},
          // {title: '登录端口',fid: 'port'},
          {title: '归属地',template:function (row){
              return '<span>'+ (row.area?'' + row.area.info + '':'-') +'</span>';
            }},
          {title: '用户',fid: 'user'},
          {title: '状态', template: function (item) {
              var status = Boolean(item.status);
              return '<span style="color:'+ (status?'#20a53a;':'red') +'">'+ (status ? '登录成功' : '登录失败') +'</span>';
            }},
          {title: '操作时间', fid: 'time', width:150}
        ],
        success:function (config){
          $(config.config.el + ' .tootls_top .pull-right').prepend(html)
          $('#login'+ type +'Page').html(firewall.renderLogsPages(20,param.p,config.data.length))
        }
      })
    },

    /**
     * @description ssh白名单
     */
    sshWhiteList:function(){
      var that = this;
      return bt_tools.table({
        el: '#loginWhiteList',
        url: '/ssh_security?action=return_ip',
        load: '获取SSH登录白名单',
        default: 'SSH登录白名单为空', // 数据为空时的默认提示
        autoHeight: true,
        height: '250px',
        dataFilter: function (data) {
          return { data:data.msg };
        },
        column: [
          {title: 'IP地址',template: function (item) {
              return '<span>'+ item + '</span>';
            }},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '删除',
              event: function (row, index) {
                console.log(row, index)
                bt_tools.send({
                  url: '/ssh_security?action=del_return_ip',
                  data:{ip:row}
                },function (rdata){
                  bt_tools.msg(rdata)
                  that.sshWhiteList()
                },'删除IP白名单');
              }
            }]
          }
        ]
      })
    },
  },
  // 入侵防御
  intrusion:{
    /**
     * @description SSH管理列表
     */
    event:function (){
      var that = this;
      bt.soft.get_soft_find('bt_security', function (rdata) {
        // 判断插件未安装 && 插件是否过期
        if (!rdata.setup && rdata.endtime > -1) {
          $('.buyIntrusion').hide();
        }
        // 判断插件已安装 && 插件是否过期
        if((rdata.setup && rdata.endtime > -1)) {
          $('#intrusion .tab-nav-border,#intrusion .tab-con').show()
          $('#intrusion .installSoft').hide()
          // 切换系统防火墙菜单事件
          $('#intrusion').unbind('click').on('click', '.tab-nav-border span', function () {
            var index = $(this).index()
            $(this).addClass('on').siblings().removeClass('on')
            $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on')
            $('.state-content').show().find('.intrusion-header').show().siblings().hide()
            that.cutSshTab(index)
          })
          $('#intrusion .tab-nav-border span').eq(0).trigger('click')
          $('#isIntrusion').unbind('click').on('click', function () {
            var status = $(this).prop('checked');
            that.setIntrusionSwitch(status)
          })
        }else{
          $('#intrusion .tab-nav-border,#intrusion .tab-con').hide()
          $('#intrusion .installSoft').show()
          $('.state-content').hide()
          $('.installSoft .thumbnail-tab li').unbind('click').on('click',function(){
            var index = $(this).index()
            $(this).addClass('on').siblings().removeClass('on')
            $('.installSoft .thumbnail-item').eq(index).addClass('show').siblings().removeClass('show')
          })
          if(rdata.endtime > -1){
            $('.purchaseIntrusion').hide()
          }else{
            $('.installIntrusion').hide()
          }

          $('.installIntrusion ').unbind('click').on('click',function (){
            bt.soft.install('bt_security',function (rdata) {
              location.reload()
            })
          })
          $('.purchaseIntrusion').unbind('click').on('click',function (){
            bt.soft.updata_ltd(true);
          })
        }
      })
    },

    /**
     * @description 切换SSH管理页面
     */
    cutSshTab:function (index){
      switch (index){
        case 0:
          this.overviewList();
          break;
        case 1:
          this.processWhiteList();
          break;
        case 2:
          this.interceptLog();
          break;
        case 3:
          this.operationLog();
          break;
      }
    },

    /**
     * @description 设置防入侵开关
     */
    setIntrusionSwitch:function (status){
      bt_tools.send({
        url:'/plugin?action=a&name=bt_security&s='+ (status?'start_bt_security':'stop_bt_security'),
      },function(rdata){
        bt_tools.msg(rdata);
      },'设置防入侵状态');
    },

    /**
     * @description 概览列表
     */
    overviewList:function (){
      var _that = this;
      return bt_tools.table({
        el: '#antiOverviewList',
        url: '/plugin?action=a&name=bt_security&s=get_total_all',
        load: '获取防入侵防御列表',
        default: '防入侵防御列表为空', // 数据为空时的默认提示
        autoHeight: true,
        height: '450px',
        dataFilter: function (data) {
          console.log(data)
          $('#isIntrusion').prop('checked',data.open)
          $('.totlaDays').html(data.totla_times).css(data.totla_times?{'color':'#d9534f','font-weight':'bold'}:{})
          $('.totlaTimes').html(data.totla_days).css(data.totla_days?{'color':'#d9534f','font-weight':'bold'}:{})
          return {data:data.system_user};
        },
        column: [
          {title: '用户',fid:'0'},
          {title: '总次数',align: 'center', template:function (row){
              var total = row[4].totla;
              return '<span class="'+ (total > 0?'bt_danger':'') +'">'+ total + '</span>';
            }},
          {title: '当日次数',align: 'center', template:function (row){
              var today = row[4].day_totla;
              return '<span class="'+ (today > 0?'bt_danger':'') +'">'+ today + '</span>';
            }},
          {
            title: '防入侵',
            fid:'3',
            type: 'switch',
            event: function (row, index, ev, key, that) {
              bt_tools.send({
                url:'/plugin?action=a&name=bt_security&s='+(row[3]?'stop_user_security':'start_user_security'),
                data:{ user: row[0] }
              },function (rdata){
                bt_tools.msg(rdata);
                that.$refresh_table_list();
              }, function (rdata) {
                bt_tools.msg(rdata);
                $(ev.currentTarget).prop('checked', row[3]);
              }, '设置防入侵状态');
            }
          },
          {
            title: '日志状态',
            fid:'5',
            type: 'switch',
            event: function (row, index, ev, key, that) {
              bt_tools.send({
                url:'/plugin?action=a&name=bt_security&s='+(row[5]?'stop_user_log':'start_user_log'),
                data:{ uid:row[1] }
              },function (rdata){
                bt_tools.msg(rdata);
                that.$refresh_table_list();
              },'设置日志状态');
            }
          },
          {title: '备注',fid:'6'},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '命令日志',
              event: function (row, index) {
                _that.getCmdLogs(row)
              }
            }]
          }
        ]
      })
    },

    /**
     * @description 获取命令日志
     * @param {Object} row 当前行数据
     */
    getCmdLogs:function (row){
      var that = this;
      bt_tools.send({
        url:'/plugin?action=a&name=bt_security&s=get_logs_list',
        data:{ user:row[0] }
      },function (rdata){
        if(rdata.length > 0){
          that.openLogsView(rdata,row[0])
        }else{
          layer.msg('暂无命令日志',{icon:6})
        }
      })
    },

    /**
     * @description 打开日志视图
     */
    openLogsView:function (arr,user){
      var that = this;
      layer.open({
        type: 1,
        title: "【"+ user +"】- 命令日志",
        area: ['840px', '570px'],
        closeBtn: 2,
        shadeClose: false,
        content: '<div class="logs-list-box pd15">\
        <div class="logs-data-select">\
            <div class="logs-title">选择日期: </div>\
            <div class="logs-unselect">\
              <div class="logs-inputs"><div class="logs-inputs-tips">'+ arr[0] +'</div></div>\
              <dl class="logs-input-list" data-val="'+ arr[0] +'"></dl>\
            </div>\
        </div>\
        <div class="logs-table bt-table">\
            <div id="logsTable"></div>\
            <div class="logs-page page-style pull-right"></div>\
            </div>\
        </div>',
        success:function(layers,index){
          var _html = '';
          for(var i = 0;i<arr.length;i++){
            _html += '<dd logs-data="'+ arr[i] +'" '+ ( i === 0?'class="logs_checked"':'' ) +'>'+ arr[i] +'</dd>';
          }
          $('.logs-list-box .logs-input-list').html(_html);
          $('.logs-list-box .logs-inputs').on('click',function(e){
            if(!$(this).parent().hasClass('active')){
              $(this).parent().addClass('active');
            }else{
              $(this).parent().removeClass('active');
            }
            $(document).unbind('click').click(function(e){
              $('.logs-unselect').removeClass('active');
              $(this).unbind('click');
            });
            e.stopPropagation();
            e.preventDefault();
          });

          $('.logs-input-list dd').on('click',function(e){
            var _val = $(this).attr('logs-data');
            $(this).addClass('logs_checked').siblings().removeClass('logs_checked');
            $(this).parent().attr('data-val',_val);
            $(this).parent().prev().find('.logs-inputs-tips').html(_val);
            that.renderLogsTable({ page:1, day:_val, user:user});
          });

          $('.logs-page').unbind().on('click','a.nextPage',function(e){
            var _page = parseInt($(this).attr('data-page'));
            var _day = $('.logs-input-list dd').attr('logs-data');
            that.renderLogsTable({ page:_page, day:_day, user:user});
          });

          $('.logs-input-list dd:eq(0)').click();

        }
      })
    },

    /**
     * @description 渲染日志视图
     * @param {object} data 日志数据
     */
    renderLogsTable:function (data){
      var _that = this, table = $('#logsTable'), dataTable = table.data('table');
      table.empty();
      return bt_tools.table({
        el: '#logsTable',
        url: '/plugin?action=a&name=bt_security&s=get_user_log',
        load: '获取命令日志列表',
        default: '命令日志列表为空', // 数据为空时的默认提示
        autoHeight: true,
        column: [
          {title: '用户', template:function (row) { return '<span>'+ data.user +'</span>' }},
          {title: '运行目录', fid: 'cwd'},
          {title: '执行的命令', fid: 'cmd'},
          {title: '命令的路径', fid: 'filename'},
          {title: '时间',align:'right', template: function (row) {
              return '<span>'+ bt.format_data(row.timestamp) +'</span>';
            }}
        ],
        beforeRequest: function (param) {
          return $.extend(param,{ p:data.page, day:data.day, user:data.user, num:11});
        },
        success: function (rdata) {
          $('.logs-page').html(firewall.renderLogsPages(10,data.page,rdata.data.length));
        }
      });
    },

    /**
     * @description 进程白名单
     */
    processWhiteList:function (){
      var _that = this;
      return bt_tools.table({
        el: '#antiProcessWhiteList',
        url: '/plugin?action=a&name=bt_security&s=porcess_set_up_log',
        load: '获取进程白名单列表',
        default: '进程白名单为空', // 数据为空时的默认提示
        autoHeight: true,
        dataFilter: function (data) {
          return {data:data};
        },
        tootls: [
          { // 按钮组
            type: 'group',
            list: [{
              title: '添加进程白名单',
              active: true,
              event: function (ev) {
                bt.open({
                  title:'添加进程白名单',
                  area:'400px',
                  btn:['添加','取消'],
                  content:'<div class="bt-form">\
                      <div class="line">\
                      <span class="tname" style="font-size: 12px;">进程名称</span>\
                        <div class="info-r"><input type="text" name="cmd" placeholder="例:/bin/bash" class="bt-input-text mr10 " style="width:220px;" value="" /></div>\
                      </div>\
                    </div>\
                    <ul class="help-info-text c7" style="margin: 5px 0 0 35px;font-size: 12px;"><li style="color:red">命令需要填写全路径例如:/usr/bin/curl</li></ul>',
                  yes:function (){
                    var cmd = $('[name="cmd"]').val();
                    bt_tools.send({
                      url: '/plugin?action=a&name=bt_security&s=add_porcess_log',
                      data: { cmd:cmd }
                    },function (rdata){
                      bt_tools.msg(rdata);
                      _that.processWhiteList()
                    })
                  }
                })
              }
            }]
          },
          // { // 批量操作
          //   type: 'batch', //batch_btn
          //   disabledSelectValue: '请选择需要批量操作的站点!',
          //   selectList: [{
          //     title: "删除项目",
          //     url: '/project/nodejs/remove_project',
          //     param: function (row) {
          //       return { data: JSON.stringify({ project_name: row.name }) }
          //     },
          //     refresh: true,
          //     callback: function (that) {
          //
          //     }
          //   }
          //   ],
          // },
        ],
        column: [
          {title: '进程白名单', template:function (row){
              return '<span>'+ row + '</span>';
            }},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '删除',
              event: function (row, index) {
                console.log(arguments);
                bt.confirm({title:'删除进程白名单-['+ row +']', msg:'是否删除进程白名单-['+ row +']，继续操作！'},function (){
                  bt_tools.send({
                    url:'/plugin?action=a&name=bt_security&s=del_porcess_log',
                    data:{ cmd: row }
                  },function (rdata){
                    _that.processWhiteList()
                    bt_tools.msg(rdata)
                  })
                })
              }
            }]
          }
        ]
      })
    },

    /**
     * @description 拦截日志
     */
    interceptLog:function (){
      var _that = this;
      return bt_tools.table({
        el: '#antiInterceptLog',
        url: '/plugin?action=a&name=bt_security&s=get_log_send',
        load: '获取拦截日志列表',
        default: '拦截日志为空', // 数据为空时的默认提示
        autoHeight: true,
        dataFilter: function (res) {
          return { data: res.data };
        },
        column: [
          {title: '拦截内容', template:function (row){
              return '<span>'+ row.log + '</span>';
            }},
          {title: '触发时间', width:'170px', template:function (row){
              return '<span>'+ row.addtime + '</span>';
            }}
        ]
      })
    },

    /**
     * @description 操作日志
     */
    operationLog:function (){
      var _that = this;
      return bt_tools.table({
        el: '#antiOperationLog',
        url: '/plugin?action=a&name=bt_security&s=get_log',
        load: '获取操作日志列表',
        default: '操作日志为空', // 数据为空时的默认提示
        autoHeight: true,
        tootls:[{ //分页显示
          type: 'page',
          jump: true, //是否支持跳转分页,默认禁用
        }],
        column: [
          {title: '操作', template:function (row){
              return '<span title="'+ row.log +'">'+ row.log + '</span>';
            }},
          {title: '日期', fid:'addtime', width:'170px'},
        ]
      })
    }
  },
  // 系统加固
  system:{
    ipTable: null,

    /**
     * @description SSH管理列表
     */
    event:function (){
      var that = this;

      bt.soft.get_soft_find('syssafe', function (rdata) {
        // 判断插件未安装 && 插件是否过期
        if (!rdata.setup && rdata.endtime > -1) {
          $('.buySystem').hide();
        }
        // 判断插件已安装 && 插件是否过期
        if((rdata.setup && rdata.endtime > -1)){
          $('#system .tab-nav-border,#system .tab-con').show()
          $('#system .installSoft').hide()

          // 切换系统防火墙菜单事件
          $('#system').unbind('click').on('click', '.tab-nav-border span', function () {
            var index = $(this).index()
            $(this).addClass('on').siblings().removeClass('on')
            $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on')
            $('.state-content').show().find('.system-header').show().siblings().hide()
            that.cutSshTab(index)
          });

          // 系统加固开关
          $('#isReinforcement').unbind('change').change(function () {
            var $this = $(this)
            bt_tools.send({
              url: '/plugin?name=syssafe&action=a&s=set_open',
            }, function (rdata) {
              bt_tools.msg(rdata);
            }, function (rdata) {
              bt_tools.msg(rdata);
              var checked = $this.prop('checked');
              $this.prop('checked', !checked);
            }, '保存配置')
          });

          $('#system .tab-nav-border span').eq(0).trigger('click')

          // 添加封锁ip地址
          $('.system_add_ip').click(function () {
            var $ip = $('input[name="system_address"]')
            var ip = $ip.val().trim();
            if (!ip) {
              $ip.focus();
              return layer.msg('请输入IP地址', { icon: 2 });
            }
            if (!bt.check_ip(ip)) {
              $ip.focus();
              return layer.msg('IP地址格式不正确!', { icon: 2 });
            }
            bt_tools.send({
              url: '/plugin?name=syssafe&action=a&s=add_ssh_limit',
              data: { ip: ip }
            }, function (rdata) {
              bt_tools.msg(rdata);
              if (rdata.status) $ip.val('');
              that.getBlockIp();
            }, '提交IP地址')
          })
        }else{
          $('#system .tab-nav-border,#system .tab-con').hide()
          $('#system .installSoft').show()
          $('.state-content').hide()
          $('#system .installSoft .thumbnail-tab li').unbind('click').on('click',function(){
            var index = $(this).index()
            $(this).addClass('on').siblings().removeClass('on')
            $('#system .installSoft .thumbnail-item').eq(index).addClass('show').siblings().removeClass('show')
          })
          if(rdata.endtime > - 1){
            $('.purchaseSystem').hide()
          }else{
            $('.installSystem').hide()

          }
          $('.installSystem ').unbind('click').on('click',function (){
            bt.soft.install('syssafe',function (rdata) {
              location.reload()
            })
          })
          $('.purchaseSystem').unbind('click').on('click',function (){
            bt.soft.updata_ltd(true);
          })
        }
      })

    },

    /**
     * @description 切换SSH管理页面
     */
    cutSshTab:function (index){
      switch (index){
        case 0:
          this.reinforceSystem();
          break;
        case 1:
          this.reinforceBlockIp();
          break;
        case 2:
          this.reinforceLog();
          break;
      }
    },

    /**
     * @description 渲染系统加固配置
     */
    renderSafeConfig:function (){
      if (s_key === 'process') {
        system_reinforcement.process_config()
        return;
      }

      if (s_key === 'ssh') {
        system_reinforcement.ssh_config()
        return;
      }
      var loadT = layer.msg('正在获取数据...', { icon: 16, time: 0 });
      bt_tools.send({
        url: '/plugin?name=syssafe&action=a&s=get_safe_config',
        data: { s_key: s_key }
      },function (rdata){
        var chattrs = { "a": "追加", "i": "只读" }
        var states = { true: "<a style=\"color:green;\">已保护</a>", false:"<a style=\"color:red;\">未保护</a>" }
        var tbody = '';
        for (var i = 0; i < rdata.paths.length; i++) {
          tbody += '<tr>\
            <td>' + rdata.paths[i].path + '</td>\
            <td>' + chattrs[rdata.paths[i].chattr] + '</td>\
            <td>' + (rdata.paths[i].s_mode === rdata.paths[i].d_mode ? rdata.paths[i].s_mode:(rdata.paths[i].s_mode + ' >> ' + rdata.paths[i].d_mode)) + '</td>\
            <td>' + states[rdata.paths[i].state] + '</td>\
            <td style="text-align: right;"><a class="btlink" onclick="system_reinforcement.remove_safe_config(\''+ s_key + '\',\'' + rdata.paths[i].path + '\')">删除</a></td>\
          </tr>'
        }
        if (system_reinforcement.message_box_noe) {
          layer.close(system_reinforcement.message_box_noe);
          system_reinforcement.message_box_noe = null;
        }

        system_reinforcement.message_box_noe = layer.open({
          type: 1,
          title: "配置【" + rdata.name + "】",
          area: ['700px', '550px'],
          closeBtn: 2,
          shadeClose: false,
          content: '<div class="pd15">\
              <div style="border-bottom:#ccc 1px solid;margin-bottom:10px;padding-bottom:10px">\
              <input class="bt-input-text" name="s_path" id="s_path" type="text" value="" style="width:250px;margin-right:5px;" placeholder="被保护的文件或目录完整路径"><a class="glyphicon cursor glyphicon-folder-open" onclick="bt.select_path(\'s_path\')" style="color:#edca5c;margin-right:20px;font-size:16px"></a>\
              <select class="bt-input-text" name="chattr"><option value="i">只读</option><option value="a">追加</option></select>\
              <input class="bt-input-text mr5" name="d_mode" type="text" style="width:120px;" placeholder="权限">\
              <button class="btn btn-success btn-sm va0 pull-right" onclick="system_reinforcement.add_safe_config(\''+ s_key + '\');">添加</button>\</div>\
              <div class="divtable">\
              <div id="jc-file-table" class="table_head_fix" style="max-height:300px;overflow:auto;border:#ddd 1px solid">\
              <table class="table table-hover" style="border:none">\
                <thead>\
                  <tr>\
                    <th width="360">路径</th>\
                    <th>模式</th>\
                    <th>权限</th>\
                    <th>状态</th>\
                    <th style="text-align: right;">操作</th>\
                  </tr>\
                </thead>\
                <tbody class="gztr">'+ tbody+'</tbody>\
              </table>\
              </div>\
            </div>\
            <ul class="help-info-text c7 ptb10" style="margin-top: 5px;">\
              <li>【只读】无法修改、创建、删除文件和目录</li>\
              <li>【追加】只能追加内容，不能删除或修改原有内容</li>\
              <li>【权限】设置文件或目录在受保护状态下的权限(非继承),关闭保护后权限自动还原</li>\
              <li>【如何填写权限】请填写Linux权限代号,如:644、755、600、555等,如果不填写,则使用文件原来的权限</li>\
            </ul>\
          </div>',
          success:function (){

          }
        })
      },'获取系统加固配置');
    },

    /**
     * @description 防护配置
     */
    reinforceSystem:function (){
      var _that = this;
      return bt_tools.table({
        el: '#reinforceSystem',
        url: '/plugin?name=syssafe&action=a&s=get_safe_status',
        load: '获取系统加固配置',
        default: '系统加固配置为空', // 数据为空时的默认提示
        autoHeight: true,
        dataFilter: function (data) {
          $('#isReinforcement').prop('checked', data.open);
          return { data: data.list };
        },
        column: [
          {title: '名称', fid:'name'},
          {title: '描述', fid:'ps'},
          {
            title: '状态',
            fid:'open',
            type: 'switch',
            event: function (row, index, ev, key, that) {
              bt_tools.send({
                url:'/plugin?action=a&name=syssafe&s=set_safe_status',
                data:{ s_key: row.key }
              },function (rdata){
                bt_tools.msg(rdata);
                that.$refresh_table_list();
              }, function (rdata) {
                bt_tools.msg(rdata);
                $(ev.currentTarget).prop('checked', row[3]);
              }, '正在保存配置');
            }
          },
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '配置',
              event: function (row, index) {
                switch (row.key) {
                  case 'ssh':
                    _that.renderReinforceSSHView(row);
                    break;
                  case 'process':
                    _that.renderReinforceAbnormalProcess(row);
                    break;
                  default:
                    _that.renderReinforceSystemView(row);
                    break;
                }
              }
            }]
          }
        ]
      })
    },

    /**
     * @description 渲染防护配置 服务加固、环境变量加固、用户加固、关键目录加固、计划任务加固
     */
    renderReinforceSystemView:function (row){
      var that = this;
      bt_tools.open({
        title: "配置【" + row.name + "】",
        area: ['700px', '600px'],
        btn:false,
        content:'<div class="pd20">\
					<div id="ReinforceSystemTable"></div>\
          <ul class="help-info-text c7 ptb10" style="margin-top: 5px;font-size: 12px;">\
            <li>【只读】无法修改、创建、删除文件和目录</li>\
            <li>【追加】只能追加内容，不能删除或修改原有内容</li>\
            <li>【权限】设置文件或目录在受保护状态下的权限(非继承),关闭保护后权限自动还原</li>\
            <li>【如何填写权限】请填写Linux权限代号,如:644、755、600、555等,如果不填写,则使用文件原来的权限</li>\
				  </ul>\
				</div>',
        success:function (){
          that.reinforceSystemFind(row.key);
        }
      })
    },


    /**
     * @description 渲染指定系统加固配置列表信息
     * @param {String} s_key 系统加固配置key
     */
    reinforceSystemFind: function (s_key) {
      var _that = this;
      var chattrs = { "a": "追加", "i": "只读" }
      return bt_tools.table({
        el: '#ReinforceSystemTable',
        url: '/plugin?name=syssafe&action=a&s=get_safe_config',
        load: '获取系统加固配置',
        default: '系统加固配置为空', // 数据为空时的默认提示
        height: 350,
        beforeRequest: function (data) {
          return $.extend(data, { s_key: s_key });
        },
        dataFilter: function (data) {
          return { data: data.paths };
        },
        column: [
          {title: '路径', fid:'path'},
          {title: '模式', fid:'chattr', template: function (row) {
              return '<span>'+ chattrs[row.chattr] +'</span>';
            }},
          {title: '权限', fid:'ps', template: function (row) {
              return '<span>'+ (row.s_mode === row.d_mode?row.s_mode:(row.s_mode + ' >> ' + row.d_mode)) +'</span>';
            }},
          {title: '状态', fid:'state', template: function (row) {
              return '<span class="'+ (row.state?'bt_success':'bt_danger') +'">'+ (row.state?'已保护':'未保护') +'</span>';
            }},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '删除',
              event: function (row, index, ev, id, that) {
                bt_tools.send({
                  url: '/plugin?name=syssafe&action=a&s=remove_safe_path',
                  data: { s_key: s_key, path: row.path }
                }, function (rdata) {
                  bt_tools.msg(rdata);
                  that.$refresh_table_list();
                }, '删除对象');
              }
            }]
          }
        ],
        tootls:[{ // 按钮组
          type: 'group',
          list: [{
            title: '添加保护文件/目录',
            active: true,
            event: function (ev, that) {
              _that.reinforceAddProtectFile(s_key, that);
            }
          }]
        }]
      })
    },

    /**
     * @description 渲染添加保护文件/目录
     * @param {String} s_key 系统加固配置key
     */
    reinforceAddProtectFile: function (s_key, table) {
      bt_tools.open({
        title: '添加保护文件/目录',
        area: '450px',
        btn: ['保存','取消'],
        skin:'addProtectFile',
        content: {
          class: 'pd20',
          form: [
            {
              label: '路径',
              group:{
                type: 'text',
                name: 'path',
                width: '260px',
                icon: { type: 'glyphicon-folder-open', event: function (ev) { }, select: 'dir' },
                placeholder: '被保护的文件或目录完整路径',
              }
            },
            {
              label: '模式',
              group:{
                type: 'select',
                name: 'chattr',
                width: '260px',
                list: [
                  { title: '只读', value: 'i' },
                  { title: '追加', value: 'a' },
                ]
              }
            },
            {
              label: '权限',
              group:{
                type: 'text',
                name: 'd_mode',
                width: '260px',
                placeholder: '请输入权限',
              }
            }
          ]
        },
        yes: function (form, indexs) {
          if (form.s_path === '') return layer.msg('请选择路径', { icon: 2 });
          if (form.chattr === '') return layer.msg('请选择模式', { icon: 2 });
          if (form.d_mode === '') return layer.msg('请输入权限', { icon: 2 });
          form.s_key = s_key;
          bt_tools.send({
            url: '/plugin?name=syssafe&action=a&s=add_safe_path',
            data: form
          }, function (rdata) {
            bt_tools.msg(rdata);
            layer.close(indexs);
            table.$refresh_table_list();
          }, '添加对象')
        }
      })
    },

    /**
     * @description 渲染配置SSH加固策略
     * @param {object} row 表格单行数据
     */
    renderReinforceSSHView: function (row) {
      bt_tools.open({
        title: "配置【" + row.name + "】",
        area: ['700px'],
        btn:false,
        content:'<div class="pd15">\
					<div style="border-bottom:#ccc 1px solid;padding-bottom:15px">\
						在(检测周期)\
						<input class="bt-input-text" min="30" max="1800" name="s_cycle" type="number" value="0" style="width:80px;margin-right:8px;">秒内,\
						登录错误(检测阈值)\
						<input min="3" max="100" class="bt-input-text" name="s_limit_count" type="number" value="0" style="width:80px;margin-right:8px;">次,\
						封锁(封锁时间)\
						<input min="60" class="bt-input-text" name="s_limit" type="number" value="0" style="width:80px;margin-right:8px;">秒\
						<button class="btn btn-success btn-sm va0 pull-right" id="saveSshConfig">保存</button>\
					</div>\
					<ul class="help-info-text c7 ptb10" style="margin-top: 5px;">\
						<li>触发以上策略后，客户端IP将被封锁一段时间</li>\
						<li>请在面板日志或操作日志中查看封锁记录</li>\
						<li>请在面板日志或操作日志中查看SSH成功登录的记录</li>\
					</ul>\
				</div>',
        success: function () {
          bt_tools.send({
            url: '/plugin?name=syssafe&action=a&s=get_ssh_config',
          }, function (rdata) {
            $('input[name="s_cycle"]').val(rdata.cycle);
            $('input[name="s_limit"]').val(rdata.limit);
            $('input[name="s_limit_count"]').val(rdata.limit_count);
          }, '获取数据');

          // 保存配置
          $('#saveSshConfig').click(function () {
            var data = {
              cycle: $("input[name='s_cycle']").val(),
              limit: $("input[name='s_limit']").val(),
              limit_count: $("input[name='s_limit_count']").val()
            }
            if (data.cycle === '') return layer.msg('请输入检测周期', { icon: 2 });
            if (data.limit === '') return layer.msg('请输入检测阈值', { icon: 2 });
            if (data.limit_count === '') return layer.msg('请输入封锁时间', { icon: 2 });

            bt_tools.send({
              url: '/plugin?name=syssafe&action=a&s=save_ssh_config',
              data: data
            }, function (rdata) {
              bt_tools.msg(rdata);
            }, '保存配置');
          })
        }
      })
    },

    /**
     * @description 渲染异常进程监控配置
     * @param {object} row 表格单行数据
     */
    renderReinforceAbnormalProcess: function (row) {
      var that = this;
      bt_tools.open({
        title: "配置【" + row.name + "】",
        area: ['700px', '600px'],
        btn:false,
        content:'<div class="pd20">\
					<div id="AbnormalProcessTable"></div>\
          <ul class="help-info-text c7 ptb10" style="margin-top: 5px;font-size: 12px;">\
            <li>【进程名称】请填写完整的进程名称,如: mysqld</li>\
            <li>【说明】在白名单列表中的进程将不再检测范围,建议将常用软件的进程添加进白名单</li>\
				  </ul>\
				</div>',
        success: function () {
          bt_tools.table({
            el: '#AbnormalProcessTable',
            url: '/plugin?name=syssafe&action=a&s=get_process_white',
            load: '获取数据',
            height: 350,
            dataFilter: function (rdata) {
              var data = []
              $.each(rdata, function (index, item) {
                data.push({ name: item })
              })
              return { data: data }
            },
            column: [
              {
                title: '进程名称',
                fid: 'name'
              },
              {
                title: '操作',
                type: 'group',
                width: 150,
                align: 'right',
                group: [{
                  title: '删除',
                  event: function (row, index, ev, id, that) {
                    bt_tools.send({
                      url: '/plugin?name=syssafe&action=a&s=remove_process_white',
                      data: { process_name: row.name }
                    }, function (rdata) {
                      bt_tools.msg(rdata);
                      that.$refresh_table_list();
                    }, '删除对象');
                  }
                }]
              }
            ],
            tootls:[{ // 按钮组
              type: 'group',
              list: [{
                title: '添加进程',
                active: true,
                event: function (ev, that) {
                  bt_tools.open({
                    title: '添加进程',
                    area: '450px',
                    btn: ['保存','取消'],
                    skin:'addProtectFile',
                    content: {
                      class: 'pd20',
                      form: [
                        {
                          label: '进程名称',
                          group:{
                            type: 'text',
                            name: 'process_name',
                            width: '260px',
                            placeholder: '完整的进程名称',
                          }
                        }
                      ]
                    },
                    yes: function (form, indexs) {
                      if (form.process_name === '') return layer.msg('请输入完整的进程名称', { icon: 2 });
                      bt_tools.send({
                        url: '/plugin?name=syssafe&action=a&s=add_process_white',
                        data: form
                      }, function (rdata) {
                        bt_tools.msg(rdata);
                        layer.close(indexs);
                        that.$refresh_table_list();
                      }, '添加对象')
                    }
                  })
                }
              }]
            }]
          })
        }
      })
    },

    /**
     * @description 封锁IP
     */
    reinforceBlockIp: function () {
      var _that = this;
      var table = bt_tools.table({
        el: '#reinforceBlockIp',
        url: '/plugin?name=syssafe&action=a&s=get_ssh_limit_info',
        load: '封锁IP列表',
        default: '封锁IP列表为空', // 数据为空时的默认提示
        autoHeight: true,
        dataFilter: function (data) {
          return {data:data};
        },
        column: [
          {title: 'IP地址', fid: 'address'},
          {title: '解封时间', fid:'end', width: 100, template:function (row){
              return '<span>'+ (row.end?bt.format_data(row.end):'手动解封') + '</span>';
            }},
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [{
              title: '立即解封',
              event: function (row, index) {
                bt_tools.send({
                  url: '/plugin?name=syssafe&action=a&s=remove_ssh_limit',
                  data: { ip: row.address }
                }, function (rdata) {
                  bt_tools.msg(rdata);
                  _that.getBlockIp();
                }, '解封IP地址')
              }
            }]
          }
        ]
      });
      this.ipTable = table
      return table
    },

    /**
     * @description 表格重新生成封锁IP
     */
    getBlockIp: function () {
      if (this.ipTable) this.ipTable.$refresh_table_list()
    },

    /**
     * @description 操作日志
     */
    reinforceLog:function (){
      var _that = this;
      $('#reinforceLog').empty()
      return bt_tools.table({
        el: '#reinforceLog',
        url: '/data?action=getData',
        load: '获取系统加固操作日志',
        default: '操作日志为空', // 数据为空时的默认提示
        autoHeight: true,
        beforeRequest: function (param) {
          return $.extend(param,{ search:'系统加固', table:'logs', order:'id desc'});
        },
        tootls: [
          { //分页显示
            type: 'page',
            numberStatus: true, //　是否支持分页数量选择,默认禁用
            jump: true, //是否支持跳转分页,默认禁用
          }],
        column: [
          {title: '时间',fid:'addtime'},
          {title: '详情',fid:'log'},
        ],
      })
    }

  },
  // 日志审计
  logAudit:{

    data:{},
    /**
     * @description SSH管理列表
     */
    event:function (){
      var that = this;
      $('#logAudit .logAuditTab').empty()
      this.getLogFiles()
      $('.state-content').hide()
      $('#logAudit').height($(window).height() - 180)
      $(window).unbind('resize').on('resize', function () {
        var height = $(window).height() - 180;
        $('#logAudit').height(height)
        $('#logAuditTable .divtable').css('max-height', height - 150)
      })
      $('.logAuditTab').unbind('click').on('click', '.logAuditItem',function (){
        var data = $(this).data(), list = []
        $.each(data.list, function (key, val){
          list.push(val.log_file)
        })
        $(this).addClass('active').siblings().removeClass('active')
        that.getSysLogs({log_name: data.log_file, list: list, p:1})
      })

      $('#logAuditPages').unbind('click').on('click', 'a', function (){
        var page = $(this).data('page')
        that.getSysLogs({log_name: that.data.log_name, list: that.data.list, p: page})
        return false
      })
    },

    /**
     * @description 获取日志审计类型
     */
    getLogFiles: function () {
      var that = this;
      bt_tools.send({
        url: '/safe/syslog/get_sys_logfiles'
      }, function (rdata) {
        if(rdata.hasOwnProperty('status') ){
          if(!rdata.status && rdata.msg.indexOf('企业版用户') > -1){
            $('.logAuditTabContent').hide();
            $('#logAudit .installSoft').show()
            return false
          }
        }
        var initData = rdata[0], list = []
        $.each(rdata, function (i, v) {
          var logSize = 0;
          $.each(v.list,function (key, val){
            logSize += val.size;
          })
          $('#logAudit .logAuditTab').append($('<div class="logAuditItem" title="'+ (v.name + ' - '+ v.title +'('+ ToSize(v.size)) +'" data-file="'+ v.log_file +'">' + v.name + ' - '+ v.title +'('+ ToSize(v.size + logSize) +')</div>').data(v))
        })
        $('#logAudit .logAuditTab .logAuditItem:eq(0)').trigger('click')
      }, '获取日志审计类型')
    },

    /**
     * @description 获取日志审计类型列表
     */
    getSysLogs: function (param) {
      var that = this;
      var page = param.p || 1;
      that.data = { log_name: param.log_name, list: param.list, limit: 20, p: page }
      bt_tools.send({
        url: '/safe/syslog/get_sys_log',
        data: {data:JSON.stringify(that.data)}
      }, function (rdata) {
        if(typeof rdata[0] === 'string'){
          $('#logAuditPre').show().siblings().hide()
          that.renderLogsAuditCommand(rdata)
        }else{
          $('#logAuditTable,#logAuditPages').show()
          $('#logAuditPre').hide()
          that.renderLogsAuditTable({ p:page }, rdata)
        }
      }, {
        load: '获取日志审计类型列表',
        verify: false
      })
    },

    /**
     * @description 渲染日志审计命令
     * @param {Object} rdata 参数
     */
    renderLogsAuditCommand: function (rdata) {
      var logAuditLogs = $('#logAuditPre');
      var str = rdata.join('\r').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
      logAuditLogs.html('<pre style="height: 600px; background-color: #333; color: #fff; overflow-x: hidden; word-wrap:break-word; white-space:pre-wrap;">' + str + '</pre>');
      logAuditLogs.find('pre').scrollTop(9999999999999).css({height: $(window).height() - 180})
    },

    /**
     * @description 渲染日志审计表格
     * @param {object} param 参数
     */
    renderLogsAuditTable: function (param, rdata){
      var that = this;
      var column = [], data = rdata[0] ? rdata[0] : { 时间: '--', '角色': '--', '事件': '--' }, i = 0;
      $.each(data, function (key) {
        // console.log(key === '时间',i)
        column.push({ title: key, fid: key,width: (key === '时间' &&  i === 0) ? '200px' : (key === '时间'?'300px':'') })
        i++;
      })
      $('#logAuditTable').empty()
      return bt_tools.table({
        el: '#logAuditTable',
        url:'/safe/syslog/get_sys_log',
        load: '获取日志审计内容',
        default: '日志为空', // 数据为空时的默认提示
        column: column,
        dataFilter: function (data) {
          if(typeof data.status === "boolean" && !data.status){
            $('.logAuditTabContent').hide().next().show();
            return { data: [] }
          }
          if(typeof data[0] === 'string'){
            $('#logAuditPre').show().siblings().hide()
            that.renderLogsAuditCommand(rdata)
          }else{
            $('#logAuditTable,#logAuditPages').show()
            $('#logAuditPre').hide()
            return {data:data}
          }
        },
        beforeRequest: function (param) {
          delete  param.data
          return {data:JSON.stringify($.extend(that.data,param))}
        },
        tootls: [{ // 按钮组
          type: 'group',
          list: [{
            title: '刷新列表',
            active: true,
            event: function (ev) {
              that.getSysLogs(that.data)
            }
          }]
        },{ // 搜索内容
          type: 'search',
          placeholder: '请输入来源/端口/角色/事件',
          searchParam: 'search', //搜索请求字段，默认为 search
        },{
          type:'page',
          number:20
        }],
        success:function (config){
          $('#logAuditTable .divtable').css('max-height', $(window).height()  - 280)
        }
      })
    }
  },
  // 面板日志
  logs:{
    /**
     * @description 事件绑定
     */
    event:function (){
      var that = this;
      $('#logsBody').unbind('click').on('click','.tab-nav-border span',function(){
        var index = $(this).index();
        $(this).addClass('on').siblings().removeClass('on');
        $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on');
        that.cutLogsTab(index)
        $('.state-content').hide()
      })
      $(window).unbind('resize').resize(function (){
        $('#runningLog .crontab-log').height((window.innerHeight - 310) +'px')
      })
      $('#logsBody .tab-nav-border span').eq(0).trigger('click');
    },

    /**
     * @description 切换日志菜单
     * @param {number} index 索引
     */
    cutLogsTab:function(index){
      switch (index) {
        case 0:
          this.operationLogTable()
          break;
        case 1:
          this.runningLog()
          break;
      }
    },

    /**
     * @description 日志表格
     */
    operationLogTable:function(){
      var that = this;
      return bt_tools.table({
        el: '#operationLog',
        url: '/data?action=getData',
        load: '获取面板操作日志',
        default: '面板操作日志为空', // 数据为空时的默认提示
        autoHeight: true,
        beforeRequest: function (data) {
          return $.extend(data, {table: 'logs',order: 'id desc'})
        },
        tootls: [
          { // 按钮组
            type: 'group',
            list: [{
              title: '刷新日志',
              active:true,
              event: function (ev, _that) {
                _that.$refresh_table_list(true)
              }
            },{
              title: '清空日志',
              event: function (ev) {
                bt.firewall.clear_logs(function(){
                  that.operationLogTable()
                });
              }
            }]
          },
          { // 搜索内容
            type: 'search',
            placeholder: '请输入操作日志描述',
            searchParam: 'search', //搜索请求字段，默认为 search
          },
          { //分页显示
            type: 'page',
            numberStatus: true, //　是否支持分页数量选择,默认禁用
            jump: true, //是否支持跳转分页,默认禁用
          }],
        column: [
          {title: '用户', fid: 'username', width: 60},
          {title: '操作类型', fid: 'type', width: 100},
          {title: '详情',fid: 'log'},
          {title: '操作时间', fid: 'addtime', width:150}
        ]
      })
    },

    /**
     * @description 运行日志
     */
    runningLog:function (){
      var that = this;
      bt_tools.send({
        url:'/config?action=get_panel_error_logs'
      },function (rdata){
        $('#runningLog').html('<div style="font-size: 0;">\
          <button type="button" title="刷新日志" class="btn btn-success btn-sm mr5 refreshRunLogs" ><span>刷新日志</span></button>\
          <button type="button" title="清空日志" class="btn btn-default btn-sm mr5 clearRunningLog" ><span>清空日志</span></button>\
          <pre class="crontab-log">'+ (rdata.msg || '日志为空') +'</pre>\
        </div>');
        $('.refreshRunLogs').click(function (){
          that.runningLog()
        })
        $('.clearRunningLog').click(function (){
          that.clearRunningLog()

        })

        $('#runningLog .crontab-log').height((window.innerHeight - 310) +'px')
        var div = document.getElementsByClassName('crontab-log')[0]
        div.scrollTop = div.scrollHeight;
      },'面板运行日志')
    },

    /**
     * @description 清除日志
     */
    clearRunningLog:function (){
      var that = this;
      bt.confirm({
        title:'清空日志',
        msg:'确定清空面板运行日志吗，继续操作？',
      },function (){
        bt_tools.send({
          url:'/config?action=clean_panel_error_logs'
        },function (rdata){
          bt.msg(rdata)
          that.runningLog()
        },'清空日志')
      })
    }
  },

  /**
   * @description 渲染日志分页
   * @param pages
   * @param p
   * @param num
   * @returns {string}
   */
  renderLogsPages:function(pages,p,num){
    return (num >= pages?'<a class="nextPage" data-page="1">首页</a>':'') + (p !== 1?'<a class="nextPage" data-page="'+ (p-1) +'">上一页</a>':'') + (pages <= num?'<a class="nextPage" data-page="'+ (p+1) +'">下一页</a>':'')+'<span class="Pcount">第 '+ p +' 页</span>';
  }
}

firewall.event();

