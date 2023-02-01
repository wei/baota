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
			if (name === 'contDetect') {
				contDetect.event();
			} else {
				that[name].event();
			}
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
          title:(status?'停用':'启用')+'系统防火墙',
          msg:(status?'停用系统防火墙，服务器将失去安全防护，是否继续操作？':'推荐启用，启用系统防火墙后，可以更好的防护当前的服务器安全，是否继续操作？'),
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
            placeholder: '请输入端口',
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
            placeholder: '请输入源端口',
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
          yes: function (index, layers) {
            bt_tools.verifyForm('#editCountryRegionForm', [
              {
								name: 'ports',
								validator: function (value, row) {
                  if (!value && row.choose !== 'all') return '指定端口不能为空';
                }
							},
            ], function (verify, form) {
              if (verify) {
                // 添加、修改
                form['brief'] = form.country;
                form['country'] = $('[name="country"]').find(':selected').text();
								if (form.choose === 'all') form.ports = '';
                bt_tools.send({
                  url: '/safe/firewall/' + (isEdit ? 'modify_country' : 'create_country'),
                  data: { data: JSON.stringify($.extend({ id: row.id }, form)) }
                }, function (rdata) {
                  bt.msg(rdata)
                  if(rdata.status){
                    layer.close(index)
                    that.countryRegionTable()
                    that.getFirewallIfo()
                  }
                }, (isEdit ? '编辑' : '添加') + '区域规则');
              }
            })
          },
          success: function (layero, index) {
            var options = [];
            for (var i = 0; i < rdata.length; i++) {
              var item = rdata[i]
              options.push({
                label: item.CH,
                value: item.brief
              })
            }
            bt_tools.fromGroup('#editCountryRegionForm', [
              { label: '地区', width: '200px', name: 'country', type: 'select', options: options },
              { label: '策略', width: '200px', name: 'types', type: 'select', options: [{ value:'drop', label:'屏蔽' }] },
              {
								label: '端口',
								width: '200px',
								name: 'choose',
								type: 'select',
								options:[
									{ value: 'all', label: '所有端口' },
									{ value: 'point', label: '指定端口' }
								], 
								on: {
									change: function (ev, val) {
                    $(this).data('line').next().toggle()
                	}
								}
							},
              { label: '指定端口', width: '200px', name: 'ports', labelStyle: 'display:none', type: 'text', placeholder: '请输入指定端口' },
              {
								type:'tips',
								list:['暂只支持输入单个地区名称！','请注意：如果屏蔽了本地区,本地区就访问不了！','指定端口既可以输入单个端口,也可以输入多个端口,多个端口之间用","隔开！'],
								style:'padding-left: 55px; margin-top:5px;'
							}
            ], {
							country: row.brief,
							types: 'drop',
							choose: 'all'
						});
						if (row.ports) {
							$('select[name="choose"]').val('point');
							$('select[name="choose"]').change();
							$('input[name="ports"]').val(row.ports);
						}
            bt_tools.setLayerArea(layero);
          }
        });
      },'获取国家区域列表')
    },

    /**
     * @description 删除地区规则
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
        },'删除地区规则')
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
        if(!bt.check_port(port)) return bt.msg({msg:'端口格式错误，可用范围：1-65535，<br />请避免使用以下端口<br />【80,443,8080,8443,8888】',icon:2});
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
      var _this = this
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
              <button type="button" class="btn btn-default btn-sm btn-rebuild-sshkey">重新生成</button>\
            </div>\
          </div>',
          success:function (layers,indexs){
            $('.btn-copy-sshkey').on('click',function(){
              bt.pub.copy_pass($('#ssh_text_key').val());
            })
            $('.btn-download-sshkey').on('click',function(){
              window.open('/ssh_security?action=download_key')
            })
            $('.btn-rebuild-sshkey').on('click',function(){
              bt_tools.send({
                url:'/ssh_security?action=set_sshkey',
                data:{ ssh:'yes', type:'ed25519' }
              },function (res){
                bt_tools.send({
                  url:'/ssh_security?action=get_key'
                },function (rdata){
                  if(!rdata.msg) return layer.msg('请重新开启SSH密钥登录再查看密钥！');
                  $('#ssh_text_key').val(rdata.msg)
                  if(res.status) bt_tools.msg({msg:'重新生成密钥成功！',status:true})
                  _this.getSeniorSshInfo()
                })
              },'重新生成密钥')
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
  //安全检测
  safeDetect:{
    scan_list:[],//漏洞扫描
    scan_num:0,
    span_time:'',
    is_pay:true,
    is_recycle: bt.get_cookie('file_recycle_status') || false, // 是否开启回收站
    /**
     * @description 安全检测列表
     */
     event:function (){
      var that = this;
      $.post('/project/safe_detect/check_auth',function (res){
        if(res === false || res['status'] === false){
          $('#safeDetect .tab-nav-border,#safeDetect .tab-con').hide()
          $('#safeDetect .installSoft').show()
          $('.state-content').hide()
          $('.installSoft .thumbnail-tab li').unbind('click').on('click',function(){
            var index = $(this).index()
            $(this).addClass('on').siblings().removeClass('on')
            $('.installSoft .thumbnail-item').eq(index).addClass('show').siblings().removeClass('show')
          })
        }else{
          $('#safeDetect .tab-nav-border,#safeDetect .tab-con').show()
          $('#safeDetect .installSoft').hide()
          $('#safeDetect').unbind('click').on('click','.tab-nav-border span',function(){
            var index = $(this).index();
            $(this).addClass('on').siblings().removeClass('on');
            $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on');
            that.cutSafeDetectTab(index)
            $('.state-content').hide()
          })
          $('#safeDetect .tab-nav-border span').eq(0).trigger('click');
          // 木马查杀开关
          $('#isSpywareDetection').unbind('change').change(function () {
            var $this = $(this),checked = $this.prop('checked'), url = '/project/safe_detect/stop_service'
            if (checked) url = '/project/safe_detect/start_service'
            bt_tools.send({
              url: url,
            }, function (rdata) {
              bt_tools.msg(rdata);
            }, function (rdata) {
              bt_tools.msg(rdata);
              $this.prop('checked', !checked);
            }, '保存配置')
          });
        }
      })
    },
    /**
     * @description 切换安全检测菜单
     * @param {number} index 索引
     */
    cutSafeDetectTab:function(index){
      switch (index) {
        case 0://木马查杀
          this.get_service_status()
          this.spywareDetectionList()
          break;
        case 1://安全检测
          this.safeDetectList()
          break;
        case 2://漏洞扫描
          var that = this
          bt_tools.send({
            url:'project/scanning/list'
          },function (res){
            if (res.status !== false) {
              that.scan_list = []
              that.scan_num = 0
              that.scan_list = res
              for (var i = 0; i < res.info.length; i++) {
                if (res.info[i].cms.length > 0) {
                  that.scan_num += res.info[i].cms.length
                }
              }
              that.is_pay = res.is_pay
              that.span_time = that.get_simplify_time(res.time)
            }
            that.getScanList()
          })
          break;
      }
    },
    /**
    * @description 木马查杀全局状态
    */
    get_service_status:function (){
      $.post({
        url: '/project/safe_detect/get_service_status',
      }, function (rdata) {
        $('#isSpywareDetection').prop('checked',rdata.status)
      })
    },
    /**
    * @description 木马查杀
    */
    spywareDetectionList:function (){
      var _this = this;
      var spywareDetectionTable = bt_tools.table({
        el: '#spywareDetectionList',
        url: '/project/safe_detect/get_monitor_dir',
        load: '获取目录列表',
        default: '目录列表为空', // 数据为空时的默认提示
        autoHeight: true,
        height: $(window).height() - 380,
        column: [
          {
            type: 'checkbox',
            class: '',
            width: 20
          },
          {
            title: '目录',
            fid:'path',
            tips: '打开目录',
            type: 'link',
            event: function (row, index, ev) {
              openPath(row.path);
            }
          },
          {
            width: 80,
            title: '监控状态',
            fid: 'open',
            config: {
              icon: true,
              list: [
                [true, '运行中', 'bt_success', 'glyphicon-play'],
                [false, '已停止', 'bt_danger', 'glyphicon-pause']
              ]
            },
            type: 'status',
            event: function (row, index, ev, key, that) {
              var url = '/project/safe_detect/stop_monitor_dir'
              if (!row.open) url = '/project/safe_detect/start_monitor_dir'
              var param = {
                path: row.path
              }
              bt_tools.send({
                url: url,
                data: {data : JSON.stringify(param)}
              },function (rdata) {
                bt_tools.msg(rdata);
                that.$refresh_table_list(false)
              }, '保存配置')
            }
          },
          {
            fid: 'ps',
            title: '备注',
            type: 'input',
            blur: function (row, index, ev, key, that) {
              if (row.ps == ev.target.value) return false;
              bt_tools.send({
                url: '/project/safe_detect/edit_monitor_dir',
                data: {
                  path: row.path,
                  ps: ev.target.value
                }
              }, function (res) {
                bt_tools.msg(res, { is_dynamic: true });
              })
            },
            keyup: function (row, index, ev) {
              if (ev.keyCode === 13) {
                $(this).blur();
              }
            }
          },
          {
            title: '操作',
            type: 'group',
            width: 150,
            align: 'right',
            group: [
              {
                title: '扫描',
                event: function (row, index, ev, key, that) {
                  _this.set_dir_kill({path:row.path})
                }
              },
              {
                title: '删除',
                event: function (row, index, ev, key, that) {
                  bt.simple_confirm({title:'删除监听目录【'+ row.path +'】', msg:'删除选中目录后，该目录将不在自动进行木马查杀和病毒文件隔离，是否继续操作？'},function (){
                    bt_tools.send({
                      url: '/project/safe_detect/del_monitor_dir',
                      data: {
                        path: row.path,
                      }
                    }, function (res) {
                      if (res.status) {
                        layer.close(index)
                        that.$refresh_table_list(true);
                      }
                      bt_tools.msg(res);
                    },'删除监听目录')
                  })
              }
            }]
          }
        ],
        tootls: [{ // 按钮组
          type: 'group',
          positon: ['left', 'top'],
          list: [{
            title: '添加目录',
            active: true,
            event: function (ev, that) {
              _this.add_monitor_dir_form(function (res, index) {
                if (res.status) {
                  layer.close(index)
                  that.$refresh_table_list(true);
                }
                bt_tools.msg(res);
              })
            }
          }, {
            title: '白名单',
            event: function (ev) {
              _this.get_white_path()
            }
          }, {
            title: '隔离文件',
            event: function (ev) {
              _this.webshell_file()
            }
          }]
        }, { // 批量操作
          type: 'batch',
          positon: ['left', 'bottom'],
          placeholder: '请选择批量操作',
          buttonValue: '批量操作',
          disabledSelectValue: '请选择需要批量操作的站点!',
          selectList: [{
            title: "开启监听目录",
            load: true,
            url: '/project/safe_detect/start_monitor_dir',
            param: function (crow) {
              return { path: crow.path }
            },
            callback: function (that) { // 手动执行,data参数包含所有选中的站点
              bt.simple_confirm({title:'批量开启监听目录', msg:'批量开启监听选中的目录，开启后目录将会对自动的进行木马查杀并进行隔离，是否继续操作？'},function (){
                var param = {};
                that.start_batch(param, function (list) {
                  var html = ''
                  for (var i = 0; i < list.length; i++) {
                    var item = list[i];
                    html += '<tr><td>' + item.path + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + (item.request.status ? '成功' : '失败') + '</span></div></td></tr>';
                  }
                  spywareDetectionTable.$batch_success_table({
                    title: '批量开启监听目录',
                    th: '目录',
                    html: html
                  });
                  spywareDetectionTable.$refresh_table_list(true);
                });
              });
            }
          },{
            title: "关闭监听目录",
            load: true,
            url: '/project/safe_detect/stop_monitor_dir',
            param: function (crow) {
              return { path: crow.path }
            },
            callback: function (that) { // 手动执行,data参数包含所有选中的站点
              bt.confirm({title:'批量关闭监听目录', msg:'批量关闭监听选中的目录，关闭后目录将停止自动进行木马查杀，是否继续操作？'},function (){
                var param = {};
                that.start_batch(param, function (list) {
                  var html = ''
                  for (var i = 0; i < list.length; i++) {
                    var item = list[i];
                    html += '<tr><td>' + item.path + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + (item.request.status ? '成功' : '失败') + '</span></div></td></tr>';
                  }
                  spywareDetectionTable.$batch_success_table({
                    title: '批量关闭监听目录',
                    th: '目录',
                    html: html
                  });
                  spywareDetectionTable.$refresh_table_list(true);
                });
              });
            }
          },{
            title: "删除监听目录",
            load: true,
            url: '/project/safe_detect/del_monitor_dir',
            param: function (crow) {
              return { path: crow.path }
            },
            callback: function (that) { // 手动执行,data参数包含所有选中的站点
              bt.confirm({title:'批量删除监听目录', msg:'批量关闭监听选中的目录，该目录将不在自动进行木马查杀和病毒文件隔离，是否继续操作？'},function (){
                var param = {};
                that.start_batch(param, function (list) {
                  var html = ''
                  for (var i = 0; i < list.length; i++) {
                    var item = list[i];
                    html += '<tr><td>' + item.path + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + (item.request.status ? '成功' : '失败') + '</span></div></td></tr>';
                  }
                  spywareDetectionTable.$batch_success_table({
                    title: '批量删除监听目录',
                    th: '目录',
                    html: html
                  });
                  spywareDetectionTable.$refresh_table_list(true);
                });
              });
            }
          }],
        }],
        success: function (layers,indexs) {
          if(!$('#spywareDetectionList .help-info-text').length){
            $('#spywareDetectionList').append('<ul class="help-info-text c7" style="margin-top:5px;">\
              <li>注意：隔离文件后的数字表示隔离文件总数</li>\
              <li style="color: #fc6d26;">动态查杀开启后，当查杀目录中的文件发生修改就会自动的进行木马查杀并进行隔离</li>\
            </ul>')
            $('#spywareDetectionList .tootls_top .pull-left').append('<div class="inlineBlock mlr15 dividing-line"></div><div class="inlineBlock mb10" style="height: 30px;">\
                <span style="vertical-align: middle;">动态查杀开关</span>\
                <div class="ssh-item" style="float: inherit;display: inline-block;vertical-align: middle;padding-top: 1px;">\
                    <input class="btswitch btswitch-ios" id="isSpywareDetection" type="checkbox" />\
                    <label class="btswitch-btn 4/5000 isSpywareDetection" for="isSpywareDetection"></label>\
                </div> \
            </div>')
          }
          $('#spywareDetectionList.bt_table .divtable').css({'clear':'both'})
          bt_tools.send({
            url: '/project/safe_detect/get_webshell_total',
          }, function (rdata) {
            $('#spywareDetectionList .tootls_top .pull-left button:eq(2)').html('<span>隔离文件</span><span class="'+ (rdata > 0 ? 'btn_red':'btn_normal') +'">'+ rdata +'</span>')
          })
        }
      })
      return spywareDetectionTable
    },
    /**
     * @description 添加目录
     * @param callback {function} 回调函数
     */
    add_monitor_dir_form:function (callback) {
      var that = this
      var add_monitor_dir = bt_tools.open({
        title: "添加目录",
        area: '490px',
        btn: ['提交', '取消'],
        content:'<form id="addMonitorDirForm" class="bt-form bt-form pd20" onsubmit="return false">'+
          '<div class="line">\
            <span class="tname" style="width: 50px;">目录</span>\
            <div class="info-r" style="margin-left: 50px;">\
              <textarea class="bt-input-text mr5 dir" style="width: 393px;height: 120px;line-height: 22px;" name="dir" placeholder="如需填写多个目录请换行填写，例：\n/www/aaa\n/www/bbb"></textarea>\
            </div>\
          </div>\
          <div class="line">\
            <span class="tname" style="width: 50px;"></span>\
            <div class="info-r" style="margin-left: 50px;">\
              <button type="button" class="btn btn-default btn-sm mr5">添加指定目录</button>\
              <button type="button" class="btn btn-default btn-sm mr5">添加网站目录</button>\
            </div>\
          </div>'+
        '</form>',
        success: function (layero,index) {
          var btn = $('.line button'), dir = $('[name=dir]')
          btn.click(function () {
            var index = $(this).index()
            switch (index) {
              case 1:
                bt_tools.send({
                  url: '/project/safe_detect/add_all_site',
                },function (res) {
                  var data = []
                  for (var i = 0; i < res.length; i++) {
                    data.push({path:res[i]})
                  }
                  bt_tools.open({
                    title: '选择网站目录',
                    area: '500px',
                    btn: ['提交', '取消'],
                    content:'<div id="all_site" style="padding: 15px 20px;"></div>',
                    success: function (layero,index) {
                      bt_tools.table({
                        el: '#all_site',
                        load: false,
                        default: '网站目录列表为空', // 数据为空时的默认提示
                        autoHeight: true,
                        height: '250px',
                        data: data,
                        column: [
                          {
                            type: 'checkbox',
                            class: '',
                            width: 20,
                          },
                          {
                            title: '网站目录',
                            fid:'path'
                          },
                        ]
                      })
                      for (var i = 0; i < $('#all_site tbody tr').length; i++) {
                        $('#all_site tbody tr:eq('+ i +') td:eq(1)').click(function () {
                          var cust_checkbox =  $(this).prev().find('.cust—checkbox')
                          cust_checkbox.click()
                        })
                      }
                      var dir_value = dir.val().split(/[(\r\n\s)\r\n\s]+/).filter(function (s) { return $.trim(s).length > 0})
                      for (var i = 0; i < res.length; i++) {
                        if(dir_value.indexOf(res[i]) > -1) {
                          $('#all_site tbody tr:eq('+ i +') .cust—checkbox').click()
                        }
                      }
                    },
                    yes: function (index, layers) {
                      console.log()
                      var idx = $('#all_site tbody .cust—checkbox.active')
                      var rdata = []
                      for (var i = 0; i < idx.length; i++) {
                        rdata.push(res[idx.eq(i).parent().parent().parent().parent().index()])
                      }
                      layer.close(index)
                      dir.val(rdata.join("\n"))
                    }
                  })
                }, '获取所有网站目录')
                break;
              case 0:
                bt.select_path('dir','dir','multi',function (rdata) {
                  var arr = dir.val() != '' ? dir.val().split(/[(\r\n\s)\r\n\s]+/).filter(function (s) { return $.trim(s).length > 0}) : []
                  arr.push(rdata)
                  dir.val(arr.join("\n"))
                });
                break;
            }
          })
        },
        yes: function (index, layers) {
          var dir = $('[name=dir]'), param = {}
          if(dir.val() === '') return layer.msg('目录不能为空!',{icon:2});
          param = {
            dirs: dir.val().split(/[(\r\n\s)\r\n\s]+/).filter(function (s) { return $.trim(s).length > 0})
          }
          bt_tools.send({
            url: '/project/safe_detect/add_monitor_dir',
            data: {data : JSON.stringify(param)}
          },function (rdata) {
            if(callback) callback(rdata,index)
          }, '添加目录')
        }
      })
      return add_monitor_dir
    },
    /**
     * @description 白名单
     */
    get_white_path:function (){
      bt_tools.open({
        title: "白名单",
        area: ['700px','550px'],
        btn: false,
        content:'<div id="whitePathList" class="pd20"></div>',
        success: function (layero,index) {
          whitePathTable = bt_tools.table({
            el: '#whitePathList',
            url: '/project/safe_detect/get_white_path',
            height: '350',
            load: true,
            default: "暂无白名单目录",
            dataFilter: function (res) {
                var data = []
                if(res['dir']) {
                  for (var i = 0; i < res.dir.length; i++) {
                    data.push({path:res.dir[i],type:'dir'})
                  }
                }
                if(res['file']){
                  for (var i = 0; i < res.file.length; i++) {
                    data.push({path:res.file[i],type:'file'})
                  }
                }
                return { data: data };
            },
            column: [
              {
                type: 'checkbox',
                class: '',
                width: 20
              },
              {
                  fid: 'path',
                  title: '路径',
              },{
                fid: 'type',
                title: '类型',
                width: '100px',
                template:function (row){
                  return '<span>'+ (row.type === 'dir' ? '目录' : '文件') + '</span>';
                }
              },{
                  title: '操作',
                  type: 'group',
                  width: '100px',
                  align: 'right',
                  group: [{
                      title: '删除',
                      event: function (rowc, index, ev, key, rthat) {
                        var param = {
                          path: rowc.path,
                          type: rowc.type
                        }
                        bt.confirm({ title: '删除白名单目录', msg: '删除白名单目录-[' + rowc.path + ']，是否继续？' }, function () {
                          bt_tools.send({
                            url: '/project/safe_detect/del_white_path',
                            data: {data : JSON.stringify(param)}
                          },function (rdata) {
                            bt_tools.msg(rdata);
                            if (rdata.status) {
                              whitePathTable.$refresh_table_list()
                            }
                          }, '删除白名单目录')
                        })
                      }
                  }]
              }
            ],
            tootls: [{ // 按钮组
              type: 'group',
              positon: ['left', 'top'],
              list: [{
                  title: '添加',
                  active: true,
                  event: function (ev, that) {
                    var path = $('input[name=path]').val(),
                        type = $('input[name=path]').data('type')
                    if(path == '') return layer.msg('请选择目录/文件全路径', {icon:2})
                    // if (path.substr(path.length-1,1) != '/') path = path + '/'
                    var param = {
                      path: path,
                      type: type
                    }
                    bt_tools.send({url:'/project/safe_detect/add_white_path', data: {data : JSON.stringify(param)} }, function (rdata) {
                      bt_tools.msg(rdata);
                      if (rdata.status) {
                        whitePathTable.$refresh_table_list()
                        $('input[name=path]').val('')
                      }
                    },'添加白名单目录')
                  }
              }]
            }, { // 批量操作
              type: 'batch',
              positon: ['left', 'bottom'],
              placeholder: '请选择批量操作',
              buttonValue: '批量操作',
              disabledSelectValue: '请选择需要批量操作的站点!',
              selectList: [{
                title: "删除白名单目录",
                load: true,
                url: '/project/safe_detect/del_white_path',
                param: function (crow) {
                  return { path: crow.path,type: crow.type }
                },
                callback: function (that) { // 手动执行,data参数包含所有选中的站点
                  bt.confirm({title:'删除白名单目录', msg:'批量删除，该操作可能会存在风险，是否继续？'},function (){
                    var param = {};
                    that.start_batch(param, function (list) {
                      var html = ''
                      for (var i = 0; i < list.length; i++) {
                        var item = list[i];
                        html += '<tr><td>' + item.path + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + (item.request.status ? '成功' : '失败') + '</span></div></td></tr>';
                      }
                      whitePathTable.$batch_success_table({
                        title: '批量删除白名单目录',
                        th: '白名单目录 ',
                        html: html
                      });
                      whitePathTable.$refresh_table_list(true);
                    });
                  });
                }
              }],
            }],
            success: function () {
              if($('input[name=path]').length == 0){
                $('#whitePathList .tootls_top .pull-left .btn').before('<input type="text" name="path" placeholder="选择目录/文件全路径" class="bt-input-text mr10 add_path" value="" style="width: 250px;"><span data-id="path" class="glyphicon cursor ml5 glyphicon-folder-open"></span>')
                $('#whitePathList').append('<ul class="help-info-text c7" style="margin-top:5px;"><li>注意：添加白名单目录要已<code>/</code>结尾</li></ul>')
                //文件选择
                $('.glyphicon-folder-open').click(function () {
                  bt.select_path('add_path','all',function (rdata,type) {
                    $('[name=path]').val(rdata + (type === 'dir' ? '/':'') )
                    $('[name=path]').data('type',type === 'files' ? 'file' : type)
                  });
                })
              }
              $('#whitePathList.bt_table .divtable .table').css({'margin-bottom':'0.1px'})
            }
          })
        }
      })
    },
    /**
     * @description 隔离文件
     */
    webshell_file: function(){
      bt_tools.open({
        title: "隔离文件",
        area: ['700px','550px'],
        btn: false,
        content:'<div id="webshellFileList" style="padding: 10px 20px;"></div>',
        success: function (layero,index) {
          $('.layui-layer-page').css('z-index','2000')
          $('.layui-layer-page').prev().css('z-index','1999')
          refresh()
          function refresh(day) {
            var param = { day: day }
            var url = day ? '?data='+JSON.stringify(param) : ''
            whitePathTable = bt_tools.table({
              el: '#webshellFileList',
              url: '/project/safe_detect/webshell_file'+url,
              height: '420px',
              load: true,
              default: "暂无隔离文件",
              column: [
                {
                  fid: 'time',
                  title: '隔离时间',
                  width: '150px',
                  type: 'text',
                },
                {
                    fid: 'path',
                    title: '文件',
                    type: 'link',
                    event: function (row, index, ev, key, rthat) {
                      bt.pub.on_edit_file(0,row.path)
                    }
                },{
                  title: '操作',
                  type: 'group',
                  width: '200px',
                  align: 'right',
                  group: [{
                      title: '样本文件',
                      event: function (row, index, ev, key, rthat) {
                        bt.pub.on_edit_file(0,'/www/server/panel/data/bt_security/webshell/'+row.md5_file)
                      }
                  },{
                    title: '删除',
                    event: function (row, index, ev, key, rthat) {
                      var num1 = bt.get_random_num(1, 9), num2 = bt.get_random_num(1, 9)
                      layer.open({
                        type: 1,
                        title: '删除文件',
                        icon: 0,
                        skin: 'delete_site_layer',
                        area: "370px",
                        closeBtn: 2,
                        shadeClose: true,
                        content: "<div class=\'bt-form webDelete pd30\' id=\'webshell_delete_form\'>" +
                          '<i class="layui-layer-ico layui-layer-ico0"></i>' +
                          "<div class=\'f13 check_title\'>是否要删除关联的源文件！</div>" +
                          "<div class=\"check_type_group\">" +
                          "<label><input type=\"checkbox\" name=\"source_file\"><span>源文件</span></label>" +
                          "</div>" +
                          "<div class=\'vcode\'>" + lan.bt.cal_msg + "<span class=\'text\'>" + num1 + " + " + num2 + "</span>=<input type=\'number\' id=\'vcodeResult\' value=\'\'></div>" +
                          "</div>",
                        btn: [lan.public.ok, lan.public.cancel],
                        success: function (layers, indexs) {
                          var _this = this;
                          layers.find('#vcodeResult').keyup(function (e) {
                            if (e.keyCode == 13) {
                              _this.yes(indexs);
                            }
                          });
                        },
                        yes: function (indexs) {
                          var vcodeResult = $('#vcodeResult'),
                              param = {
                                md5: row.md5,
                                path: row.path
                              }
                          $('#webshell_delete_form input[type=checkbox]').each(function (index, item) {
                            if ($(item).is(':checked')) param['type'] = 'delete'
                          })
                          if (vcodeResult.val() === '') {
                            layer.tips('计算结果不能为空', vcodeResult, { tips: [1, 'red'], time: 3000 })
                            vcodeResult.focus()
                            return false;
                          } else if (parseInt(vcodeResult.val()) !== (num1 + num2)) {
                            layer.tips('计算结果不正确', vcodeResult, { tips: [1, 'red'], time: 3000 })
                            vcodeResult.focus()
                            return false;
                          }
                          bt_tools.send({
                            url: 'project/safe_detect/set_handle_file',
                            data: {data : JSON.stringify(param)}
                          },function (res) {
                            if (res.status) {
                              layer.close(indexs)
                              rthat.$refresh_table_list(true);
                            }
                            bt_tools.msg(res);
                          }, '删除文件')
                        }
                      })
                    }
                }]
              }
              ],
              success: function () {
                if(!$('#webshellFileList .help-info-text').length){
                  $('#webshellFileList').append('<ul class="help-info-text c7" style="margin-top:5px;"><li>样本文件：查杀时的文件内容被记录形成的样本文件</li></ul>')
                }
              }
            })
          }
        }
      })
    },
    /**
     * @description 安全检测
     */
    safeDetectList:function (){
      var _this = this
      $.post('/project/safe_detect/get_safe_count',function (res) {
        var progressType = {system_account:'系统账户',sshd_service:'SSHD远程服务',file_mode:'重要文件权限及属性',software:'重点软件检测',website_permissions:'网站权限检测',other:'其他项目检测'}
        var progressTypeImg = {}
        var itemList = '',desList = ''
        for (var key in progressType) {
          var item = progressType[key]
          itemList += itemDiv(1)
          desList += itemDiv(0)
        }
        function itemDiv(index) {
          return '<div class="progress_item '+ key +'_item">\
            <div class="progress_item_header">\
              <div class="progress_type"><img src="/static/img/icon-'+ key +'.svg" /><span>' + item + '</span></div>\
              <div class="progress_status">'+ (index ? '等待扫描...':'') +'</div>\
              <div class="progress_fold"><img src="/static/img/arrow-down.svg"></div>\
            </div>\
            <div class="progress_item_body"></div>\
          </div>'
        }
        function safeCount(score) {
          return '<span>'+ score +'</span> <span>分</span><svg viewBox="0 0 100 100"><path d="\
          M 50 50\
          m 0 -46\
          a 46 46 0 1 1 0 92\
          a 46 46 0 1 1 0 -92\
          " stroke="#e5e9f2" stroke-width="5" fill="none" class="el-progress-circle__track" style="stroke-dasharray: 289.027px, 289.027px; stroke-dashoffset: 0px;"></path><path d="\
          M 50 50\
          m 0 -46\
          a 46 46 0 1 1 0 92\
          a 46 46 0 1 1 0 -92\
          " stroke="'+(score === 100 ? '#20a53a' : '#fc6d26')+'" fill="none" stroke-linecap="round" stroke-width="5" class="el-progress-circle__path" style="stroke-dasharray: '+ (289.027*score/100) +'px, 289.027px; stroke-dashoffset: 0px; transition: stroke-dasharray 0.6s ease 0s, stroke 0.6s ease 0s;"></path></svg>'
        }
        var html = '<div class="progress-header">\
          <div class="progress-header-cot">\
            <div class="progresscircle hide">\
              <p><img src="/static/images/icon-safe-detect.svg" /></p><p>安全检测</p>\
            </div>\
            <div class="progresscirclebar hide">\
              <svg viewBox="0 0 100 100"><path d="\
              M 50 50\
              m 0 -46\
              a 46 46 0 1 1 0 92\
              a 46 46 0 1 1 0 -92\
              " stroke="#20a53a" fill="none" stroke-linecap="round" stroke-width="4" class="el-progress-circle__path" style="stroke-dasharray: 180px, 289.027px; stroke-dashoffset: 0px; transition: stroke-dasharray 0.6s ease 0s, stroke 0.6s ease 0s;"></path></svg>\
            </div>\
            <div class="progresscirclebar '+ (!res.status ? '' : 'security')+'" style="color:'+(res.msg.security_count === 100 ? '#20a53a' : '#fc6d26')+';">'+
              (!res.status ? '<img src="/static/images/icon-safe-detect.svg" style="width: 120px;" />' : safeCount(res.msg.security_count))
              +
            '</div>\
          </div>\
          <div class="progress-header-cot">\
            <div class="scanning-progress-title">'+ (!res.status ? '当前未进行安全检测':'上次检测时间 '+ (bt.get_simplify_time(res.msg.time) === '刚刚' ? '一分钟内' : bt.get_simplify_time(res.msg.time)))  +'</div>\
            <div class="scanning-progress-bar hide"><div class="progress-bar"><div class="progressbar"></div></div><div class="progressbar_text">0%</div></div>\
            <div class="scanning-progress-cont">'+ (!res.status ? '当前安全风险未知，请立即检测':'若长时间未检测，服务器可能存在安全风险，建议立即检测') +'</div>\
          </div>\
          <div class="progress-header-cot">\
            <button type="button" class="btn btn-success btn-sm pro_detection im_detect">立即检测</button>\
            <button class="btn btn-sm btn-default detect_repair_scan ml10 hide">立即修复</button>\
          </div>\
        </div>\
        <div class="progress-cont-list">'+desList+'</div>\
        <div class="progress-cont-list hide">'+ itemList +'</div>'
        $('#safeDetectList').empty().append(html)//<div class="prog_desc_title">支持以下安全检测项：</div>

        var progBtn = $('.pro_detection'),
        repairBtn = $('.detect_repair_scan'),
        progItem = $('.progress_item'),
        progTitle = $('.scanning-progress-title'),
        progBar = $('.progressbar'),
        progBarText = $('.progressbar_text'),
        progCircleBar = $('.progresscirclebar'),
        progCont = $('.scanning-progress-cont'),
        imgSrc = $('.progresscircle img'),
        progressList = ['system_account','sshd_service','file_mode','software','website_permissions','other']// 类型
        statusType = [{ color: '#888' ,text: '未安装'},{color: '#20a53a',text: '良好'},{color: '#ff5e03', text: '警告'},{color: 'red', text: '危险'}]
        progressConfig = {system_account:[],sshd_service:[],file_mode:[],software:[],website_permissions:[],other:[]}
        statusTotal = {}

        function setProInfo(config) {
          if($('.progress-cont-list:eq(1)').hasClass('hide')) return
          if(config.progCont) progCont.html(config.progCont)
          if(config.progEnd) {
            progTitle.html(config.progTitle)
            var statusNum = statusTotal['other']
            var status_html = statusNum['3'] || statusNum['2'] ? (statusNum['3'] ? '<span class="color-red">发现'+ statusNum['3'] + '项危险</span> ' : '')
            + (statusNum['2'] ? '<span class="color-org">'+ (statusNum['3'] ? '': '发现') +statusNum['2'] + '项警告</span>' : '') :'<span class="color-green">无风险项</span>'
            $('.other_item').find('.progress_status').html(status_html)
            progBtn.removeClass('btn-default cancel_detect').addClass('btn-success').text('重新检测')
            progCircleBar.removeClass('active')
            progCircleBar.eq(1).addClass('security').css('color',(100-config.total_score === 100 ? '#20a53a' : '#fc6d26')).html(safeCount(100-config.total_score)).removeClass('hide').prevAll().addClass('hide')
            $('.scanning-progress-bar').addClass('hide')
            repairBtn.removeClass('hide')
          }
          if (config.progress) {
            var typeElm = $('.'+ config.topic + '_item'), itemBodys = typeElm.find('.progress_item_body')
            progressConfig[config.topic].push(config)
            progBar.css('width', config.progress + '%')
            progBarText.html(config.progress + '%')
            typeElm.find('.progress_status').html('<span class="color-green">正在扫描...</span>')
            if(config.status === 3 || config.status === 2){
              progCircleBar.eq(0).find('.el-progress-circle__path').attr('stroke','#fc6d26')
              imgSrc.attr('src','/static/images/icon-safe-detect_org.svg')
              progBar.css('background-color','#fc6d26')
            }
            statusTotal[config.topic] = getArrNum(progressConfig[config.topic])
            if(progressList.indexOf(config.topic) > -1 && config.topic != 'system_account'){
              var statusNum = statusTotal[progressList[typeElm.index()-1]],status_html = ''
              if(statusNum !== undefined){
                status_html = statusNum['3'] || statusNum['2'] ? (statusNum['3'] ? '<span class="color-red">发现'+ statusNum['3'] + '项危险</span> ' : '')
                + (statusNum['2'] ? '<span class="color-org">'+ (statusNum['3'] ? '': '发现') +statusNum['2'] + '项警告</span>' : '') :'<span class="color-green">无风险项</span>'
              }
              typeElm.prev().find('.progress_status').html(status_html)
            }
            progBtn.removeClass('btn-success').addClass('btn-default cancel_detect').text('取消检测')
            var html = '<div class="progress_item_info '+ (config.info ? 'active' : '') +'">\
              <div class="info_cont">\
                <div>'+ config.name.replace('分析网站','') +'</div>\
                <div style="color: '+ statusType[config.status < 0 ? 0 : config.status].color +';">'+ statusType[config.status < 0 ? 0 : config.status].text +'</div>\
              </div>'+
              '<div class="info_cont_desc">'+ config.info +'</div>'+
            '</div>'
            itemBodys.append(html)
            if(!typeElm.hasClass('active')) typeElm.find('.progress_item_header').click()
          }
        }
        //某值出现次数
        function getArrNum(arr) {
          var obj = {}
          arr.forEach(function (element) {
            if (obj[element.status]) {
              obj[element.status]++
            } else {
              obj[element.status] = 1
            }
          })
          return obj
        }
        // 重置检测视图，恢复默认状态
        function resetView(){
          $('.scanning-progress-bar').removeClass('hide')
          progCircleBar.eq(0).find('.el-progress-circle__path').attr('stroke','#20a53a')
          imgSrc.attr('src','/static/images/icon-safe-detect.svg')
          progBar.css('background-color','#20a53a')
          progressConfig = {system_account:[],sshd_service:[],file_mode:[],software:[],website_permissions:[],other:[]}
          statusTotal = {}
          progTitle.html('正在检测中...')
          progCont.html('正在检测：')
          progBar.css('width', '0')
          progBarText.html('0%')
          progBtn.addClass('btn-success').removeClass('btn-default')
          $('.progress_status').html('等待扫描...')
          $('.progress_item_body').empty()
          progCircleBar.addClass('active')
          progCircleBar.eq(1).addClass('hide').prevAll().removeClass('hide')
        }
        var connect = new CreateConnect({ // 创建持久化链接
          onmessage: function (data) { // 消息监听的回调
            var config = {};
            if(!!data.isEnd){
              var img_end = ''//<img src="/static/img/ico-success.svg" />
              if(data.error > 0 || data.warn > 0){
                config.progTitle = img_end+'检测已完成，一共发现 <span class="color-org">'+(data.error+data.warn)+'</span> 项风险项'+(data.error > 0 ? '（包含 <span class="color-red">' + data.error + '</span> 项危险项，请立即处理）' : '');
              }else{
                config.progTitle = img_end+'检测已完成';
              }
              config.progCont = '检测时间：'+ bt.format_data(data.time / 1000,'yyyy/MM/dd');
              config.total_score = data.total_score
              config.progEnd = true //扫描结束
              connect.cancel();
            }
            if(data.progress) {
              config = data
              config['progCont'] = '正在检测：'+data.name;
            }
            setProInfo(config)
          }
        })
        repairBtn.click(function () {
          _this.repair_scheme()
        })
        //重新检测
        progBtn.click(function () {
          repairBtn.addClass('hide')
          if($(this).hasClass('cancel_detect')){
            $('#safeDetect .tab-nav-border span:eq(1)').click()
            connect.close();
          }else if($(this).hasClass('im_detect')){
            $('.scanning-progress-bar,.progresscircle,.progresscirclebar:eq(0),.progress-cont-list:eq(1)').removeClass('hide')
            $('.progresscirclebar:eq(1),.progress-cont-list:eq(0)').addClass('hide')
            $(this).removeClass('btn-success im_detect').addClass('btn-default cancel_detect').text('取消检测')
            resetView()
            connect.start();
          }else{
            resetView()
            connect.start();
          }


        })
        //展开收起
        progItem.on('click','.progress_item_header',function () {
          var _this = $(this),parent = $(this).parent(),foldImg = _this.find('.progress_fold img')
          if(!parent.hasClass('active')){
            parent.addClass('active')
            foldImg.css('transform','rotate(180deg)');
          }else{
            parent.removeClass('active')
            foldImg.removeAttr('style');
          }
        })
        var setTimes = setInterval(function () {
          if($('#safeDetectList').length == 0){
            connect.close();
            clearInterval(setTimes)
          }
        },3000)
      })
    },
    /**
     * @description 漏洞扫描
     */
    getScanList:function (){
      var that = this
      //降序
      function sortDesc(a,b){
        return b.cms.length - a.cms.length
      }
      function sortDanDesc(a,b){
        return parseInt(b.dangerous) - parseInt(a.dangerous)
      }
      var thumbnail = '<div class="webedit-con" style="display: flex;padding-top: 20px;align-items: center;justify-content: space-evenly;">\
        <div class="thumbnail-introduce" style="margin-top: 0;">\
          <span style="font-size: 18px;">漏洞扫描工具介绍：</span>\
          <ul style="display: block;font-size: 16px;">\
            <li>\
              可识别多款开源CMS程序，支持如下：<br>\
              迅睿CMS、pbootcms、苹果CMS、eyoucms、<br>\
              海洋CMS、ThinkCMF、zfaka、dedecms、<br>\
              MetInfo、emlog、帝国CMS、discuz、<br>\
              Thinkphp、Wordpress\
            </li>\
            <li style="margin-left:0;">可扫描网站中存在的漏洞</li>\
            <li style="margin-left:0;">提供修复/提供付费解决方案</li>\
          </ul>\
        </div>\
        <div class="thumbnail-box1" style="text-align: center;">\
          <img src="/static/img/safe_detect_scanning.png" style="width: 70%;" />\
        </div>\
      </div>'
      function reader_scan_list (res) {
        var data = {
          info : res.info.sort(sortDesc),
          time : res.time,
          is_pay: res.is_pay
        }
        that.span_time = that.get_simplify_time(data.time)
        var html = '', scan_time = '', arry = [], level = [['低危', '#e8d544'], ['中危', '#E6A23C'], ['高危', '#ff5722'], ['严重', 'red']]
        if (!data.is_pay) {
          html += thumbnail
        }else{
          if (data.info.length > 0) {
            for(var i = 0;i < data.info.length; i++){
              arry[i] = data.info[i].name
            }
            bt.each(arry, function (index, item) {
              var data_item = [], n = 0 , infoName = [],arr
              var re=/(http[s]?:\/\/([\w-]+.)+([:\d+])?(\/[\w-\.\/\?%&=]*)?)/gi;
              var info = data.info[index]
              if (info.cms.length >0) {
                arr = info.cms.sort(sortDanDesc)
                for (var i = 0; i < arr.length; i++) {
                  data_item[i] = arr[i].name
                }
                for (var i = 0; i < data.info.length; i++) {
                  if (data.info[i].cms.length >0) {
                    infoName[n++] = data.info[i].name
                  }
                }
                html += '<li class="module_item">' +
                  '<div class="module_head" style="background: transparent;' + (item === infoName[0] && info.cms.length > 0 ? 'border-bottom: 1px solid rgb(232, 232, 232);':'') +'">' +
                  '<div class="module_title">网站：' + item + '</div>' +
                  '<div class="module_num">风险项：<span>' + info.cms.length + '</span></div>' +
                  '<div class="module_type">类型：' + info.cms_name + '（'+ info.version_info +'）</div>' +
                  '<span class="module_cut_show">' + (item === infoName[0] && info.cms.length > 0 ? '<i style="color: #555;">收起</i><span style="color: #555;" class="glyphicon glyphicon-menu-up" aria-hidden="false"></span>' : '<i style="color: #555;">展开</i><span style="color: #555;" class="glyphicon glyphicon-menu-down" aria-hidden="false"></span>') + '</span>' +
                  '</div>'
                html += '<ul class="module_details_list ' + (item === infoName[0] && info.cms.length > 0 ? 'active' : '') + '">'
                bt.each(data_item, function (indexs, items) {
                  var cms = arr[indexs]
                  html += '<li class="module_details_item">' +
                    '<div class="module_details_head cursor">' +
                    '<span class="module_details_title">\
                      <span title="' + items + '">' + items + '</span>\
                      <i>（&nbsp;等级：' + (function (level) {
                        var level_html = '';
                        switch (level) {
                          case 4:
                            level_html += '<span style="color:red">严重</span>';
                            break;
                          case 3:
                            level_html += '<span style="color:#ff5722">高危</span>';
                            break;
                          case 2:
                            level_html += '<span style="color:#E6A23C">中危</span>';
                            break;
                          case 1:
                            level_html += '<span style="color:#e8d544">低危</span>';
                            break;
                        }
                        return level_html;
                      }(parseInt(cms.dangerous))) + '）</i>\
                    </span>' +
                    '<span class="operate_tools">\
                      <a href="javascript:;" class="btlink" data-name="' + info.name + '" ">检测</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href="javascript:;" class="btlink cut_details">详情</a>\
                    </span>'+
                    '</div>' +
                    '<div class="module_details_body">' +
                      '<div class="module_details_line">\
                        <div class="line_title">修复建议：</div>\
                        <div class="line_content" style="width: 600px;">' + cms.repair.replace(re,function(a){ return '<a href="'+ a +'" class="btlink" rel="noreferrer noopener" target="_blank">'+ a +'</a>'; }).replace(/(\r\n)|(\n)/g,'<br>') + '</div>\
                      </div>' +
                    '</div>' +
                    '</li>';
                })
                html += '</ul>'
                html += '</li>'
              }
            })
          } else {
            html += '<li class="safe_state">当前处于安全状态，请继续保持！</li>'
          }
          scan_time = Date.now() / 1000;
          $('.scan-header-cont .scan-subtitle').html('检测时间：&nbsp;' + bt.format_data(scan_time));
        }
        $('.warning_scan_body').html(html);
      }
      var _html = '<div class="scan-header">\
        <div class="scan-header-cont"><div class="safaty_load"></div><img src="'+ ( that.scan_num > 0 ? '/static/img/scanning-danger.svg' : '/static/img/scanning-success.svg')+'" style="height: 75px;width: 75px;"></div>\
        <div class="scan-header-cont">\
          <div class="scan-title">'+ ((that.scan_num > 0 ? ' 当前存在风险项 <span class="color-red">'+that.scan_num+'</span> 项，请尽快修复漏洞' : ' 未扫描到漏洞，请持续保持哦')) +'</div>\
          <div class="scan-subtitle">'+ (!that.is_pay ? '未开通，此功能为企业版专享功能' : (that.scan_num > 0 ? '扫描时间：'+ bt.format_data(Date.now() / 1000,'yyyy/MM/dd') : '当前处于安全状态，请继续保持！')) +'</div>\
        </div>\
        <div class="scan-header-cont" '+ (!that.is_pay ? 'style="justify-content: end;"':'' )+'>'+
          ( !that.is_pay ? '<button class="btn btn-sm btn-success" style="border-radius: 5px;" onclick=\"product_recommend.pay_product_sign(\'ltd\',50,\'ltd\')\"">立即查看</button>' : '<button class="warn-look hide btn btn-sm btn-success" style="margin-right:10px">重新检测</button><button class="btn btn-sm btn-success warn-again-scan">立即查看</button>' ) +
        '</div>\
      </div>\
      <ol class="warning_scan_body">'+thumbnail+'</ol>'+
      '<ul class="c7 help_info_text mt15">'+
        '<li>如需支持其他cms程序，请发帖反馈：<a class="btlink" target="_blank" href="https://www.bt.cn/bbs/thread-89149-1-1.html">https://www.bt.cn/bbs/thread-89149-1-1.html</a></li>'+
      '</ul>'
      $('#getScanList').empty().append(_html)
      // if(that.scan_list.info.length > 0) setTimeout(function(){$('.warn-again-scan').click()},50)
      var scanTitle = $('.scan-header-cont .scan-title'),
      scanSubtitle = $('.scan-header-cont .scan-subtitle'),
      safaty_load = $('.safaty_load'),
      scan_body = $('.warning_scan_body'),
      img = $('.scan-header-cont img'),
      scan_interval = null
      //预览图片
      scan_body.on('click', '.thumbnail-box' ,function(){
        layer.open({
          title:false,
          btn:false,
          shadeClose:true,
          closeBtn: 1,
          area:['700px','700px'],
          content:'<img src="/static/img/safe_detect_scanning.png" style="width:700px"/>',
          success:function(layero){
            $(layero).find('.layui-layer-content').css('padding','0')
          }
        })
      });
      //扫描
      $('.warn-again-scan').click(function () {
        if ($(this).hasClass('warning_cancel_scan')) {
          $('.scan-header-cont .warning_cancel_scan').html('立即查看').addClass('warn-again-scan btn-success').removeClass('warning_cancel_scan btn-default')
          img.attr("src",( that.scan_num > 0 ? '/static/img/scanning-danger.svg' : '/static/img/scanning-success.svg')).css({"height":"75px","width":"75px"})
          safaty_load.css('display','none')
          scanTitle.html((that.scan_num > 0 ? ' 漏洞数为'+that.scan_num+'个,请尽快修复漏洞' : ' 未扫描到漏洞，请持续保持哦') + ' <i style="font-style:normal;font-size:16px;"> 扫描时间：'+ bt.format_data(Date.now() / 1000,'yyyy/MM/dd')+'</i>')
          scanSubtitle.html(!that.is_pay ? '未开通，此功能为企业版专享功能' : (that.scan_num > 0 ? '请点击立即查看' : '当前处于安全状态，请继续保持！'));
          scan_body.html(thumbnail)
          clearInterval(scan_interval)
        }else if($(this).hasClass('warn_repair_scan')){
          that.repair_scheme()
        } else {
          $('.scan-header-cont .warn-again-scan').html('取消扫描').addClass('warning_cancel_scan btn-default').removeClass('warn-again-scan btn-success')
          img.attr("src","/static/img/scanning-scan.svg").css({"height":"60px","width":"60px"})
          safaty_load.css('display','block')
          scanTitle.html('正在扫描网站漏洞，请稍后...')
          scanSubtitle.html('检测程序类型，是否支持')
          scan_body.html('<li style="height: 200px;border: 1px solid #ddd;\
          border-radius: 2px;\
          align-items: center;\
          display: grid;\
          text-align: center;\
          font-size: 18px;\
          color: #888;"><span>请稍后 <img src="data:image/gif;base64,R0lGODlhDgACAIAAAHNzcwAAACH/C05FVFNDQVBFMi4wAwEAAAAh+QQFDgABACwAAAAAAgACAAACAoRRACH5BAUOAAEALAQAAAACAAIAAAIChFEAIfkEBQ4AAQAsCAAAAAIAAgAAAgKEUQAh+QQJDgABACwAAAAADgACAAACBoyPBpu9BQA7"></spam></li>')
          scan_interval = setInterval(function () {
            bt_tools.send({url:'/project/safe_detect/get_scan'}, function (res) {
              that.scan_num = 0
              that.scan_list = res
              that.is_pay = res.is_pay
              for (var i = 0; i < res.info.length; i++) {
                if (res.info[i].cms.length > 0) {
                  that.scan_num += res.info[i].cms.length
                }
              }
              if (that.scan_num > 0) {
                img.attr("src","/static/img/scanning-danger.svg").css({"height":"60px","width":"60px"})
                safaty_load.css('display','none')
                scanTitle.html('当前存在风险项 <i style="color:red;">' + that.scan_num + '</i> 项，请立即处理')
              } else {
                img.attr("src","/static/img/scanning-success.svg")
                img.css({"height":"60px","width":"60px"})
                safaty_load.css('display','none')
                scanTitle.html('当前网站没有风险项')
              }
              $('.scan-header-cont .warning_cancel_scan').html('立即修复').addClass('warn_repair_scan').removeClass('warning_cancel_scan')
              $('.warn-look').removeClass('hide');
              reader_scan_list(that.scan_list);
              clearInterval(scan_interval)
            })
          },500)
        }
      });
      //重新检测
      $('.warn-look').click(function(){
        $('.warn_repair_scan').addClass('warn-again-scan').removeClass('warn_repair_scan')
        $('.warn-again-scan').click();
        $('.warn-look').addClass('hide');
      })
      //展开收起
      scan_body.on('click', '.module_item .module_head', function () {
        var _parent = $(this).parent(), _parent_index = _parent.index(), _list = $(this).next();
        if (parseInt($(this).find('.module_num span').text()) > 0) {
          if (_list.hasClass('active')) {
            _list.css('height', 0);
            $(this).find('.module_cut_show i').text('展开').next().removeClass('glyphicon-menu-up').addClass('glyphicon-menu-down');
            _list.removeClass('active').removeAttr('style');
            $(this).css('border-bottom','none')
          } else {
            $(this).parent().parent().scrollTop(_parent_index * 45);
            $(this).find('.module_cut_show i').text('收起').next().removeClass('glyphicon-menu-down').addClass('glyphicon-menu-up');
            _list.addClass('active');
            var details_list = _list.parent().siblings().find('.module_details_list');
            details_list.removeClass('active');
            details_list.prev().find('.module_cut_show i').text('展开').next().removeClass('glyphicon-menu-up').addClass('glyphicon-menu-down')
            details_list.prev().css('border-bottom','none')
            $(this).css('border-bottom','1px solid rgb(232, 232, 232)')
          }
        }
      });
      //详情收起
      scan_body.on('click', '.module_details_head', function () {
        if ($(this).children().eq(1).children('.cut_details').hasClass('active')) {
          $(this).siblings().hide();
          $(this).children().eq(1).children('.cut_details').removeClass('active').text('详情');
          $(this).parents('.module_details_item').css({"background": "transparent"})
        }else {
          var item = $(this).parents('.module_details_item'), indexs = item.index();
          $(this).children().eq(1).children('.cut_details').addClass('active').text('收起');
          // item.css({"background": "#f8fffd"})
          // item.siblings().find('.module_details_body').hide();
          // item.siblings().find('.operate_tools a:eq(1)').removeClass('active').text('详情');
          $(this).siblings().show();
          $('.module_details_list').scrollTop(indexs * 41);
        }
      })
      //单个检测
      scan_body.on('click', '.operate_tools a', function () {
        var index = $(this).index(), data = $(this).data();
        var obj = JSON.stringify({"name" : data.name})
        if(index==1) return
        var loadT = layer.msg('正在检测指定模块，请稍候...', { icon: 16, time: 0 });
        $.post('project/scanning/startAweb', {data : obj}, function (res) {
          layer.close(loadT)
          that.scan_num = 0
          that.scan_list = res
          for (var i = 0; i < res.info.length; i++) {
            if (res.info[i].cms.length > 0) {
              that.scan_num += res.info[i].cms.length
            }
          }
          layer.msg('检测成功', { icon: 1 });
          reader_scan_list(that.scan_list);
        })
        return false;
      });
    },
    /**
     * @description 立即修复
    */
    repair_scheme: function () {
      bt.open({
        title:false,
        area:'330px',
        btn:false,
        closeBtn: 1,
        content:'<div class="repair-scheme">\
          <div class="repair-scheme-box">\
            <div class="repair-scheme-title">修复方案一：</div>\
            <div class="repair-scheme-content">请根据当前风险项提供的解决方案手动修复</div>\
          </div>\
          <div class="repair-scheme-box">\
            <div class="repair-scheme-title">修复方案二（<span>推荐，简单快捷</span>）：</div>\
            <div class="repair-scheme-content">\
              <span>使用微信扫描二维码，联系客服，付费修复</span>\
              <div class="qrcode">\
                <div id="wechatQrcode"><img src="/static/images/customer-qrcode.png" alt="qrcode" style="width:90px;height:90px;" /></div>\
              </div>\
            </div>\
          </div>\
        </div>',
        success:function(layero){
          // $('#wechatQrcode').qrcode({
          //   render: "canvas",
          //   width: 90,
          //   height: 90,
          //   foreground:'#222',
          //   text: 'https://work.weixin.qq.com/kfid/kfc72fcbde93e26a6f3'
          // })
        }
      })
    },
    /**
     * @description 获取时间简化缩写
     * @param {number} dateTimeStamp 需要转换的时间戳
     * @return {String} 简化后的时间格式
    */
    get_simplify_time: function (dateTimeStamp) {
      if (dateTimeStamp.toString().length === 10) dateTimeStamp = dateTimeStamp * 1000;
      var minute = 1000 * 60, hour = minute * 60, day = hour * 24,now = new Date().getTime(), diffValue = now - dateTimeStamp;
      var dayC = diffValue / day
      if (dayC >= 1) {
        result = "" + parseInt(dayC);
      }else{
        result = "0";
      }
      return result;
    },
    /**
     * @description 目录木马查杀
     * @param {Object} data 当前文件的数据对象
     * @returns void
     */
    set_dir_kill: function(data) {
      var that = this;
      var socket = null;
      var $layer = $('spyware_detection_view');
      var that_layer = null;
      var tableList = [];
      var path = data.path;
      var onece = true //扫描开始的信息状态
      bt.open({
        type: '1',
        title: '木马扫描 【' + path + '】',
        area: ['840px', '650px'],
        content: '\
        <div class="spyware_detection_view">\
          <div class="spyware_detection_head">\
            <div class="head_icon">\
              <div class="scanning" style="display: none;">\
                <img class="start_icon" src="/static/img/scanning-scan.svg" />\
                <div class="status_loading"></div>\
              </div>\
              <div class="scanning_danger" style="display: none;">\
                <img class="start_icon" src="/static/img/scanning-dangerous.svg" />\
                <div class="status_loading danger"></div>\
              </div>\
              <div class="done" style="display: none;">\
                <img class="icon success" src="/static/img/scanning-success.svg" />\
                <img class="icon danger" src="/static/img/scanning-danger.svg" style="display: none;" />\
              </div>\
            </div>\
            <div class="head_left">\
              <div class="info">当前未进行木马查杀</div>\
              <div class="file"></div>\
            </div>\
            <div class="head_right">\
              <button type="button" class="btn btn-default cancel-detection-btn" style="display: none;">取消查杀</button>\
              <button type="button" class="btn btn-default reset-detection-btn" style="display: none; margin-right: 6px">重新查杀</button>\
              <button type="button" class="btn btn-success done-detection-btn" style="display: none; width: 70px;">完成</button>\
            </div>\
          </div>\
          <!-- <div class="spyware_detection_progress">\
            <div class="progress_bar">\
              <div class="inner"></div>\
            </div>\
            <div class="text">0%</div>\
          </div> -->\
          <div class="spyware_detection_body">\
            <div id="spyware_detection_table"></div>\
          </div>\
        </div>',
        success: function (layero, index) {
          that_layer = this;
          $layer = layero;

          this.init_table();
          that_layer.reset_detection();

          // 重新查杀
          $('.reset-detection-btn').click(function () {
            that_layer.reset_detection();
          });

          // 取消
          $('.cancel-detection-btn').click(function () {
            bt.confirm({
              title: '取消木马查杀',
              msg: '当前正在进行木马查杀，确定取消查杀？'
            }, function (indexs) {
              that_layer.stop_detection();
              that_layer.detection_status = 'done'
              layer.close(indexs);
            });
          });

          // 完成
          $('.done-detection-btn').click(function () {
            layer.close(index);
          });

          $layer.prev().css({ 'z-index': 19999 })
          $layer.css({ 'z-index': 20000 })
        },
        cancel: function (index) {
          if (that_layer.detection_status != 'done') {
            bt.confirm({
              msg: '当前正在进行木马查杀，确定关闭查杀？',
              title: '关闭木马查杀'
            }, function (indexs) {
              that_layer.stop_detection();
              layer.close(indexs);
              layer.close(index);
            });
          }
          return that_layer.detection_status == 'done'
        },
        init_table: function () {
          var that_layer = this;
          this.spyTable = bt_tools.table({
            el: '#spyware_detection_table',
            default: "暂无数据",
            height: '376',
            data: [],
            column: [
              {
                type: 'checkbox',
                width: 20
              },
              {
                fid: 'filename',
                title: '文件名',
                width: 140,
                type: 'text',
                template: function (row) {
                  return '<span class="flex" title="' + row.filename + '"><span style="flex: 1; width: 0;" class="text_ellipsis">' + row.filename + '</span></span>';
                }
              },
              {
                fid: 'path',
                title: '文件路径',
                type: 'text',
                template: function (row) {
                  return '<span class="flex" title="' + row.path + '"><span style="flex: 1; width: 0;" class="text_ellipsis">' + row.path + '</span></span>';
                }
              },
              {
                type: 'group',
                title: '操作',
                width: 160,
                align: 'right',
                group: [
                  {
                    title: '误报',
                    event: function (row) {
                      bt.show_confirm('误报反馈', '<span class="red">是否确定提交误报反馈</br></span>', function () {
                        var loadT = bt.load('正在添加URL白名单，请稍候...');
                        bt.send('send_baota', 'files/send_baota', { filename: row.path }, function (res) {
                          loadT.close();
                          bt.msg(res);
                        });
                      });
                    }
                  },
                  {
                    title: '打开文件',
                    event: function (row) {
                      bt.pub.on_edit_file(0, row.path);
                    }
                  },
                  {
                    title: '删除',
                    event: function (row, index) {
                      that.del_file_or_dir(row, function (res) {
                        if (res.status) {
                          tableList.splice(index, 1);
                          that_layer.set_table_list();
                        }
                      });
                    }
                  }
                ]
              }
            ],
            tootls: [
              { // 批量操作
                type: 'batch',
                positon: ['left', 'bottom'],
                config: {
                  title: '删除',
                  callback:function (data) {
                    bt.confirm({
                      title: '批量删除',
                      msg: '确认删除选中内容,删除后将移至回收站，是否继续操作?'
                    }, function (indexs) {
                      var layerT = bt.load('正在批量删除文件，请稍候...');
                      var list = [];
                      var i = 0;
                      var checkList = data.check_list;

                      function delFile (data, callback) {
                        bt.send('DeleteFile', 'files/DeleteFile', { path: data.path }, function(res) {
                          list.push({
                            filename: data.filename,
                            status: res.status,
                            result: res.status ? '删除成功' : '删除失败'
                          });
                          if (res.status) {
                            var fileIndex = -1;
                            for (var i = 0; i < tableList.length; i++) {
                              if(tableList[i].path == data.path) {
                                fileIndex = i;
                              }
                            }
                            if (fileIndex != -1) {
                              tableList.splice(fileIndex, 1);
                            }
                          }
                          callback && callback(res);
                        });
                      }
                      function callback () {
                        i++;
                        if (i >= checkList.length) {
                          that_layer.set_table_list();
                          layerT.close();
                          bt.open({
                            type: '1',
                            title: '批量删除',
                            area: '350px',
                            content: '\
                              <div class="batch_title">\
                                <span class="batch_icon"></span>\
                                <span class="batch_text">批量删除操作完成！</span>\
                              </div>\
                              <div id="batch_table" style="margin: 15px 30px 15px 30px;"></div>\
                            ',
                            success: function ($layers) {
                              bt_tools.table({
                                el: '#batch_table',
                                height: '200px',
                                data: list,
                                column: [
                                  {
                                    fid: 'filename',
                                    title: '文件名',
                                    type: 'text',
                                    template: function (row) {
                                      return '<span class="flex" title="' + row.filename + '"><span style="flex: 1; width: 0;" class="text_ellipsis">' + row.filename + '</span></span>';
                                    }
                                  },
                                  {
                                    fid: 'result',
                                    title: '操作结果',
                                    type: 'text',
                                    width: 90,
                                    align: 'right',
                                    template: function (row) {
                                      return '<span style="color: ' + (row.status ? '#20a53a' : 'red') + '">' + row.result + '</span>';
                                    }
                                  }
                                ]
                              });

                              var top = ($(window).height() - $layers.height()) / 2;
                              $layers.css('top', top + 'px');
                            }
                          });
                        } else {
                          delFile(checkList[i], callback);
                        }
                      }
                      delFile(checkList[i], callback);
                    });
                  }
                }
              }
            ]
          });
        },
        reset_detection: function () {
          that_layer.detection_status = 'start'
          $layer.find('.spyware_detection_head .file').text('开始文件查杀');
          this.show_cancel_btn();
          this.init_info();
          this.reset_table();
          this.reset_tq_num();
          this.set_progress(0);
          this.set_stop_status(false);
          this.set_search_file_num(0);
          this.set_icon_status('scanning');
          // this.set_progress_color('success');
          this.start_detection();
        },
        // 显示取消按钮
        show_cancel_btn: function () {
          $('.done-detection-btn').hide();
          $('.start-detection-btn').hide();
          $('.reset-detection-btn').hide();
          $('.cancel-detection-btn').show();
        },
        // 显示完成按钮
        show_done_btn: function () {
          $('.start-detection-btn').hide();
          $('.cancel-detection-btn').hide();
          $('.done-detection-btn').show();
          $('.reset-detection-btn').show();
        },
        // 初始化信息
        init_info: function () {
          $layer.find('.spyware_detection_head .info').html('<span class="status">正在查杀</span>，扫描文件中...')
        },
        // 变化后信息
        change_info: function () {
          $layer.find('.spyware_detection_head .info').html('<span class="status">正在查杀</span>，已扫描文件<span class="scanned_num">0</span>/<span class="total_num">0</span>个；发现木马文件<span class="tqnum">0</span>个')
        },
        // 改变完成状态
        change_status_done: function () {
          if($layer.find('.spyware_detection_head .info .scanned_num').length){
            $layer.find('.spyware_detection_head .info .status').text('查杀完成');
          }else{
            $layer.find('.spyware_detection_head .info').text('查杀完成');
          }
        },
        // 设置进度条进度
        set_progress: function (val) {
          if (val == 0) {
            $layer.find('.progress_bar .inner').remove();
            $layer.find('.progress_bar').html('<div class="inner"></div>');
          } else {
            $layer.find('.progress_bar .inner').css('width', val + '%');
            $layer.find('.spyware_detection_progress .text').text(val + '%');
          }
        },
        // 设置进度条颜色
        set_progress_color: function (status) {
          switch (status) {
            case 'success':
              $layer.find('.progress_bar .inner').css('background-color', '#20a53a');
              break;
            case 'danger':
              $layer.find('.progress_bar .inner').css('background-color', 'red');
              break;
          }
        },
        // 设置木马扫描进度条
        set_search_progress: function (scanned, total) {
          if (total == 0) return;
          var range = ((scanned / total) * 100).toFixed(1);
          this.set_progress(range);
        },
        // 设置图标状态
        set_icon_status: function (state) {
          $layer.find('.spyware_detection_head .head_icon>div').hide();
          var $icon = $layer.find('.spyware_detection_head .head_icon .' + state);
          $icon.show();
          switch (state) {
            case 'done':
              var img = $layer.find('.spyware_detection_head .tqnum').text() <= 0 ? 'success' : 'danger';
              $icon.find('.icon').hide();
              $icon.find('.icon.' + img).show();
              break;
          }
        },
        // 设置搜索文件数量
        set_search_file_num: function (scanned, total) {
          $layer.find('.spyware_detection_head .scanned_num').text(scanned);
          if (total) $layer.find('.spyware_detection_head .total_num').text(total);
        },
        // 设置搜索文件信息
        set_search_file_text: function (text) {
          $layer.find('.spyware_detection_head .file').text(text);
          if(text === '当前文件夹不存在木马文件') $layer.find('.spyware_detection_head .info').html('<span class="status">正在查杀</span>')
        },
        // 重置木马数量
        reset_tq_num: function () {
          $layer.find('.tqnum').text(0);
        },
        // 设置停止状态
        set_stop_status: function (val) {
          this.stop_status = val;
          if (val) this.on_close();
        },
        // 添加木马数量
        add_tq_num: function () {
          var num = $layer.find('.tqnum').text() || 0;
          num++;
          $layer.find('.tqnum').text(num);
        },
        // 开始查杀
        start_detection: function () {
          onece = true
          this.connect();
        },
        // 停止查杀
        stop_detection: function () {
          this.set_stop_status(true);
          this.set_progress(100.0);
          this.show_done_btn();
          this.set_icon_status('done');
          this.change_status_done();
          $layer.find('.spyware_detection_head .info .status').text('查杀已取消');
          $layer.find('.spyware_detection_head .file').text('扫描已完成');
        },
        // 重置表格数据
        reset_table: function () {
          tableList = [];
          this.set_table_list();
        },
        // 设置表格数据
        set_table_data: function (data) {
          var path = data.path;
          if (!path) return;
          var filename = path.substring(path.lastIndexOf('/') + 1, path.length);
          that.$http('get_file_attribute', { filename: path }, function (res) {
            tableList.push({
              type: res.is_dir ? 'dir' : 'file',
              type_tips: res.is_dir ? '文件夹' : '文件',
              filename: filename,
              path: path
            });
            that_layer.set_table_list();
          });
        },
        set_table_list: function () {
          this.spyTable.$reader_content(tableList);
        },
        connect: function () {
          // 连接
          var url = (window.location.protocol === 'http:' ? 'ws://' : 'wss://') + window.location.host + '/ws_panel';
          socket = new WebSocket(url);
          // 绑定事件
          socket.addEventListener('open', this.on_open);
          socket.addEventListener('error', this.on_error);
          socket.addEventListener('message', this.on_message);
        },
        send: function (data, success) {
          // 判断当前连接状态，如果 != 1，则100ms后尝试重新发送
          if (socket.readyState === 1) {
            socket.send(JSON.stringify(data));
            if (success) success();
          } else {
            setTimeout(function () { that_layer.send(data); }, 100);
          }
        },
        on_open: function (e) {
          var token = $("#request_token_head").attr('token');
          that_layer.send({ mod_name: 'files', 'x-http-token': token });
          that_layer.send({ mod_name: 'files', def_name: 'ws_webshell_check', ws_callback: 1, path: path });
        },
        on_close: function () {
          if (socket) {
            socket.close();
            socket = null;
          }
        },
        on_error: function (e) {
          console.log(e);
        },
        on_message: function (e) {
          var dataStr = e.data;
          if (!dataStr) return;
          if (that_layer.stop_status === true) return;
          var data = JSON.parse(dataStr);
          if (data.is_count && onece) {
            that_layer.change_info()
            onece = false
          }
          that_layer.set_search_file_text(data.info);
          if (data.end === false) {
            that_layer.set_search_file_num(data.is_count, data.count);
          }
          if (data.end === false && data.status === false) {
            that_layer.set_search_progress(data.is_count, data.count);
          }
          if (data.end === false && data.status === true) {
            that_layer.set_icon_status('scanning_danger');
            // that_layer.set_progress_color('danger');
            that_layer.add_tq_num();
            that_layer.set_table_data(data);
          }
          if (data.end === true && data.is_max !== true) {
            that_layer.detection_status = 'done'
            that_layer.set_progress(100.0);
            that_layer.change_status_done();
            that_layer.show_done_btn();
            that_layer.set_icon_status('done');
          } else if (data.end === true && data.is_max === true) {
            that_layer.detection_status = 'done'
            that_layer.set_icon_status('done');
            that_layer.set_progress(100.0);
            that_layer.show_done_btn();
            $layer.find('.head_left .info').text('查杀失败')
            $layer.find('.head_icon .done .icon.success').hide()
            $layer.find('.head_icon .done .icon.danger').show()
            $layer.find('.reset-detection-btn').hide()
          }
        }
      });
    },
    /**
     * @description 删除文件和目录
     * @param {Object} data 当前文件的数据对象
     * @return void
     */
    del_file_or_dir: function (data,callback) {
      var that = this;
      if (that.is_recycle == 'true' || (typeof that.is_recycle == 'boolean' && that.is_recycle)) {
        bt.confirm({
          title: '删除' + data.type_tips + '[&nbsp;' + data.filename + '&nbsp;]',
          msg: '<span>您确定要删除该' + data.type_tips + '[&nbsp;' + data.path + '&nbsp;]吗，删除后将移至回收站，是否继续操作?</span>'
        }, function () {
          that.del_file_req(data, function (res) {
            layer.msg(res.msg, { icon: res.status ? 1 : 2 })
            if (callback) callback(res);
          });
        });
      } else {
        bt.show_confirm('删除' + data.type_tips + '[&nbsp;' + data.filename + '&nbsp;]', '<i style="font-size: 15px;font-style: initial;color: red;">当前未开启回收站，删除该' + (data.type == 'dir' ? '文件夹' : '文件') + '后将无法恢复，是否继续删除？</i></span>', function () {
          that.del_file_req(data, function (res) {
            layer.msg(res.msg, { icon: res.status ? 1 : 2 })
            if (callback) callback(res);
          });
        })
      }
    },
    /**
   * @description 删除文件（文件和文件夹）
   * @param {Object} data 文件目录参数
   * @param {Function} callback 回调函数
   * @return void
   */
  del_file_req: function (data, callback) {
    var _req = (data.type === 'dir' ? 'DeleteDir' : 'DeleteFile')
    var layerT = bt.load('正在删除文件，请稍候...');
    bt.send(_req, 'files/' + _req, { path: data.path }, function (res) {
      layerT.close();
      layer.msg(res.msg, { icon: res.status ? 1 : 2 })
      if (callback) callback(res);
    });
  },
    method_list: {},
    /**
     * @description 文件管理请求方法
     * @param {*} data
     * @param {*} parem
     * @param {*} callback
     */
    $http: function (data, parem, callback) {
      var that = this,
        loadT = '';
      if (typeof data == "string") {
        if (typeof parem != "object") callback = parem, parem = {};
        if (!Array.isArray(that.method_list[data])) that.method_list[data] = ['files', that.method_list[data]];
        that.$http({ method: data, tips: (that.method_list[data][1] ? '正在' + that.method_list[data][1] + '，请稍候...' : false), module: that.method_list[data][0], data: parem, msg: true }, callback);
      } else {
        if (typeof data.tips != 'undefined' && data.tips) loadT = bt.load(data.tips);
        bt.send(data.method, (data.module || 'files') + '/' + data.method, data.data || {}, function (res) {
          if (loadT != '') loadT.close();
          if (typeof res == "string") res = JSON.parse(res);
          if (res.status === false && res.msg) {
            bt.msg(res);
            return false;
          }
          if (parem) parem(res)
        });
      }
    }
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
      }, {load:'获取日志审计类型',verify:false})
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

/**
 * 内容检测
 */
var contDetect = {
	// 网站内容检测表格
	siteDetectTable: null,
	// 风险动态表格
	riskDynamicTable: null,
	// 监控表格
	monitorTable: null,
	/**
	 * @description 事件
	 */
	event: function () {
		var that = this;

		// todo
		$('.state-content').hide();

		$('#contDetect .tab-nav-border span').click(function () {
			var index = $(this).index();
			$(this).addClass('on').siblings().removeClass('on');
			$('#contDetect .tab-block').hide();
			$('#contDetect .tab-block').eq(index).show();
			switch (index) {
				case 0:
					that.initOverview();
					break;
				case 1:
					that.initMonitorList();
					break;
				case 2:
					that.initDetectHistory();
					break;
				case 3:
					that.initRiskList();
					break;
			}
		});

		$('.crontab-btn').click(function () {
			$('#contDetect .tab-nav-border span').eq(1).click();
		});

		$('.not-crontab-btn').click(function () {
			$('#contDetect .tab-nav-border span').eq(1).click();
		});

		$('.today-risk-num').click(function () {
			$('#contDetect .tab-nav-border span').eq(3).click();
		});

		this.init();
	},

	/**
	 * @description 初始化
	 */
	init: function () {	
		bt_tools.send({
			url: '/project/content/check_auth'
		}, function (rdata) {
			$('#contDetect .tab-nav-border span').eq(0).click();
		}, function () {
			$('#contDetect .tab-nav-border').hide();
			$('#contDetect .tab-con').hide();
			$('.cont-detect-soft').show();

			$('.cont-detect-soft .thumbnail-tab li').unbind('click').on('click',function(){
				var index = $(this).index()
				$(this).addClass('on').siblings().removeClass('on')
				$('.cont-detect-soft .thumbnail-item').eq(index).addClass('show').siblings().removeClass('show')
			});
		});
	},

	/**
	 * @description 初始化概览
	 */
	initOverview: function () {
		var that = this;
		bt_tools.send({
			url: '/project/content/get_content_monitor_overview',
		}, function (rdata) {
			that.renderOverviewInfo(rdata);
			that.renderSiteDetect(rdata.site_info);
			that.renderDynamicRisk(rdata.risk_info);
			that.renderDetectStatistics(rdata.site_info);
			that.renderWeekRisk(rdata['7day_risk']);
			that.renderSensitiveWord(rdata.sensitive_word);
		}, '处理')
	},
	/**
	 * @description 渲染概览信息
	 * @param {*} res 
	 */
	renderOverviewInfo: function (res) {
		$('.monitor-site-num').text(res.site_count);
		$('.today-risk-num').text(res.day_risk);
		$('.today-inspection-num').text(res.today_count);
		if (res.today_count > 0) {
			$('.risk-total-num').addClass('red').removeClass('cbt');
		} else {
			$('.risk-total-num').addClass('cbt').removeClass('red');
		}
		$('.risk-total-num').text(res.risk_count);
		if (res.risk_count > 0) {
			$('.today-risk-num').addClass('red').removeClass('cbt');
		} else {
			$('.today-risk-num').addClass('cbt').removeClass('red');
		}
	},
	/**
	 * @description 初始化站点检测
	 * @param {*} site_info 
	 */
	renderSiteDetect: function (site_info) {
		var that = this;
		var methodMap = {
			1: '全站扫描',
			2: '快速扫描',
			3: '单URL'
		}
		that.siteDetectTable = bt_tools.table({
			el: '#site-cont-table',
			autoHeight: true,
			height: '340px',
			default: '<div class="no-data">网站内容检测为空</div>',
			data: site_info,
			url: undefined,
			column: [
				{
					fid: 'time',
					type: 'text',
					title: '巡检时间',
					template: function (row) {
						return '<span>' + bt.format_data(row.time) + '</span>';
					}
				},
				{
					fid: 'site_name',
					title: '检测域名'
				},
				{
					fid: 'method',
					title: '检测方式',
					template: function (row) {
						return '<span>' + methodMap[row.method] + '</span>';
					}
				},
				{
					fid: 'scans',
					title: '检测页面数'
				},
				{
					fid: 'result',
					type: 'text',
					title: '巡检结果',
					template: function (row) {
						if (row.risks == 0) return '<span class="cbt">无风险</span>'
						return '<a class="bterror" href="javascript:;">' + row.risks + '</a>'
					},
					event: function (row) {
						if (row.risks === 0) return;
						that.showRiskDetails(row);
					}
				}
			]
		});
	},
	/**
	 * @description 初始化检测统计
	 * @param {*} sensitive_word 
	 */
	renderDetectStatistics: function (site_info) {
		if (site_info.length <= 0) return
		var that = this;
		var times = [];
		var names = [];
		var counts = [];
		for (var i = 0; i < site_info.length; i++) {
			if (i >= 5) break;
			var items = site_info[i];
			names.push(items.site_name);
			times.push(items.end_time - items.start_time);
			counts.push(items.scans);
		}
		var charts = echarts.init(document.getElementById('detect-statistics'));
		var option = {
			legend: {
				left: 'left',
				data: ['耗时', '检测页面']
			},
			grid: {
				left: 45,
				top: 50,
				right: 15,
				bottom: 20,
				backgroundColor: "#888"
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: {
					type: 'cross'
				},
				formatter: function (params) {
          var value = !params.length ? '' : ('检测网站: ' +  params[0].name + (params.length === 2 ? ("</br>耗时: " + that.getDuration(params[0].value) + "</br>检测页面数量: " + params[1].value) : (!params[0].seriesIndex ? "</br>耗时: " + that.getDuration(params[0].value) : "</br>检测页面数量: " + params[0].value)))
					return value;  
				}
			},
			xAxis: {
				type: 'category',
				data: names,
				scale: true,
				triggerEvent: true,
				axisLabel: {
					formatter: function (params) {
						var val = "";
						if (params.length > 6) {
							val = params.substr(0, 6) + '...';
							return val;
						} else {
							return params;
						}
					}
				},
			},
			yAxis: {
				type: 'value'
			},
			series: [
				{
					type: 'bar',
					name: '耗时',
					barWidth: 24,
					data: times,
					itemStyle: {
						color: '#fcc858'
					}
				},
				{
					type: 'bar',
					name: '检测页面',
					barWidth: 24,
					data: counts,
					itemStyle: {
						color: '#8dcf6e'
					}
				}
			]
		}
		charts.setOption(option);
		window.addEventListener("resize", function () {
			charts.resize();
		});
	},
	/**
	 * @description 初始化动态风险
	 * @param {*} risk_info 
	 */
	renderDynamicRisk: function (risk_info) {
		var typeMap = {
			title: '标题',
			body: '网页内',
			keywords: '关键词',
			descriptions: '描述',
			title_update: '标题更新',
			keywords_update: '关键词更新',
			description_update: '描述更新',
			tail_hash_update: '尾部script代码块更新',
			title_hash_update: '头部head代码块更新',
		}

		var that = this;

		this.riskDynamicTable = bt_tools.table({
			el: '#risk-dynamic-table',
			height: '340px',
			default: '<div class="no-data">风险动态为空</div>',
			data: risk_info,
			url: undefined,
			column: [
				{
					fid: 'time',
					type: 'text',
					width: '140px',
					title: '巡检时间',
					template: function (row) {
						return '<span>' + bt.format_data(row.time) + '</span>';
					}
				},
				{
					fid: 'url',
					title: 'URL',
					template: function (row) {
						return '<span class="flex"><a class="ellipsis_text btlink" href="' + row.url + '" target="_blank" style="min-width: 120px; flex: 1; width: 0;" title="' + row.url + '">' + row.url + '</a></span>';
					}
				},
				{
					fid: 'content',
					type: 'text',
					title: '关键词',
					template: function (row) {
						return '<span class="flex"><span class="ellipsis_text" style="min-width: 130px; flex: 1; width: 0;" title="' + row.content + '">' + row.content + '</span></span>';
					}
				},
				{
					fid: 'risk_content',
					title: '类型',
					template: function (row) {
						return '<span class="inlineBlock" style="width: 50px;">' + row.risk_content + '</span>';
					}
				},
				{
					fid: 'risk_type',
					type: 'text',
					title: '风险位置',
					template: function (row) {
						return '<span class="inlineBlock" style="width: 60px;">' + typeMap[row.risk_type] + '</span>';
					}
				},
				{
					fid: 'result',
					type: 'group',
					align: 'right',
					title: '操作',
					width: '60px',
					group: [
						{
							title: '详情',
							event: function (row) {
								var baseUrl = '/www/server/panel/class/projectModel/content/source/';
								var url = baseUrl + row.source_file;
								if (row.risk_type.indexOf('_update') > -1) {
									that.showBothFile(row, baseUrl);
								} else {
									that.showFile(url, row.content);
								}
							}
						}
					]
				}
			]
		});
	},
	/**
	 * @description 初始化近7天风险趋势
	 * @param {*} week_risk 
	 */
	renderWeekRisk: function (week_risk) {
		var days = [];
		var counts = [];
		for (var key in week_risk) {
			days.push(key);
		}
		days = days.sort(function (a, b) {
			return new Date(a).getTime() < new Date(b).getTime() ? -1 : 1;
		});
		for (var i = 0; i < days.length; i++) {
			counts.push(week_risk[days[i]]);
		}
		var charts = echarts.init(document.getElementById('week-risk'));
		var option = {
			grid: {
				left: 45,
				right: 15,
				top: 40,
				bottom: 20,
				backgroundColor: "#888"
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: {
					type: 'cross'
				},
				formatter: function (params) {
					var value = params[0].name + "</br>" + "风险次数: " + params[0].value;
					return value;  
				}
			},
			xAxis: {
				type: 'category',
				boundaryGap: false,
				data: days,
				axisLabel: {
					fontSize: 10,
					color: '#666',
					formatter: function (value) {
						return bt.format_data(new Date(value).getTime() / 1000, 'MM-dd')
					} 
				}
			},
			axisLabel: {
				fontSize: 10,
				color: '#666'
			},
			axisLine: {
				show: false
			},
			axisTick: {
				show: false
			},
			yAxis: {
				type: 'value',
				splitNumber: 5,
				name:'风险次数/次',
				min: 0,
				axisLine: {
					show: false
				},
				axisTick: {
					show: false
				},
				axisLabel: {
					fontSize: 10,
					color: '#666'
				},
			},
			series: [
				{
					type: 'line',
					smooth: 0.6,
					data: counts,
					areaStyle: {
						normal: {
							color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
								offset: 0,
								color: '#FF9E9E'
							}, {
								offset: 1,
								color: '#FFF6F6'
							}], false)
						},
					},
					itemStyle: {
						normal: {
							color: '#FF8585', // 改变折线点的颜色
							lineStyle: {
								color: '#FF8585', // 改变折线颜色
								type:'solid',
							}
						}
					},
				}
			]
		}
		charts.setOption(option);
		window.addEventListener("resize", function () {
			charts.resize();
		});
	},
	/**
	 * @description 初始化敏感词排行
	 * @param {*} sensitive_word 
	 */
	renderSensitiveWord: function (sensitive_word) {
		if (sensitive_word.length <= 0) return;
		var words = [];
		var counts = [];
		for (var i = 0; i < sensitive_word.length; i++) {
			if (i >= 6) break;
			var item = sensitive_word[i];
			words.push(item.words);
			counts.push(item.count);
		}
		var chart = echarts.init(document.getElementById('sensitive-word'));
		var option = {
			grid: {
				top: 10,
				left: 60,
				right: 15,
				bottom: 20,
				backgroundColor: "#888"
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: {
					type: 'cross'
				},
				formatter: function (params) {
					var value = '敏感词: ' + params[0].name + "</br>" + "次数: " + params[0].value;
					return value;  
				}
			},
			xAxis: {
				type: 'value'
			},
			yAxis: {
				type: 'category',
				data: words,
				scale: true,
				triggerEvent: true,
				axisLabel: {
					formatter: function (params) {
						var val = "";
						if (params.length > 4) {
							val = params.substr(0, 4) + '...';
							return val;
						} else {
							return params;
						}
					}
				}
			},
			series: [
				{
					type: 'bar',
					data: counts,
					barWidth: 20,
					itemStyle: {
						color: function (params) {
							var colorList = ['#ffa688', '#ffc87d', '#98caa5', '#acce9b', '#cad48f'];
							return colorList[params.dataIndex];
						}
					}
				}
			]
		};
		chart.setOption(option);
		window.addEventListener("resize", function () {
			chart.resize();
		});
	},
	/**
	 * @description 初始化监控列表
	 */
	initMonitorList: function () {
		var that = this;
		var methodMap = {
			1: '全站扫描',
			2: '快速扫描',
			3: '单URL'
		}
		this.monitorTable = bt_tools.table({
			el: '#cont-monitor-table',
			default: "暂无数据",
			url: '/project/content/get_content_monitor_list',
      load: '获取目录列表',
			autoHeight: true,
			height: '980',
			column: [
				{
					fid: 'name',
					title: '监控名',
				},
				{
					fid: 'url',
					title: '网站/URL',
				},
				{
					fid: 'method',
					type: 'text',
					title: '监控方式',
					template: function (row) {
						return '<span>' + methodMap[row.method] + '</span>'
					}
				},
				{
					fid: 'last_scan_time',
					type: 'text',
					title: '上一次检测时间',
					template: function (row) {
						if (isNaN(parseInt(row.last_scan_time))) return '<span>未检测</span>'
						return '<span>' + that.get_simplify_time(row.last_scan_time) + '</span>'
					}
				},
				{
					fid: 'last_risk_count',
					title: '上一次风险',
					template: function (row) {
						if (row.last_risk_count == 0) return '<span class="cbt">无风险</span>';
						return '<a class="bterror" href="javascript:;">' + row.last_risk_count + '</a>'
					},
					event: function (row) {
						if (row.risks === 0) return;
						that.showRiskDetails(row);
					}
				},
				{
					fid: 'crontab_status',
					title: '计划任务状态',
					template: function (row) {
						if (row.crontab_status === 1) return '<span class="cbt">正常</span>'
						return '<a class="bt_warning" href="javascript:;" title="点击修复">未设置</a>'
					},
					event: function (row) {
						if (row.crontab_status === 1) return

						that.repairCron(row);
					}
				},
				{
					fid: 'send_msg',
					title: '发送告警',
					template: function (row) {
						if (row.send_msg === 1) return '<a class="btlink" href="javascript:;" >已开启</a>'
						return '<a class="bt_warning" href="javascript:;" >未开启</a>'
					},
					event: function (row) {
						that.getMonitorForm(true, row);
					}
				},
				{
					fid: 'opt',
					title: '操作',
					align: 'right',
					type: 'group',
					group: [
						{
							title: '立即检测',
							event: function (row) {
								bt_tools.send({
									url: '/project/content/scanning',
									data: { data: JSON.stringify({ id: row.id }) },
								}, function (res) {
									that.checkMontior(row, res);
								}, '检测中');
							}
						},
						{
							title: '编辑',
							event: function (row) {
								that.getMonitorForm(true, row);
							}
						},
						{
							title: '删除',
							event: function (row) {
								bt.confirm({
									title: '删除监控 - [' + row.name + ']',
									msg: '删除后无法继续监控该网站，是否继续？'
								}, function (index) {
									bt_tools.send({
										url: '/project/content/del_content_monitor_info',
										data: { data: JSON.stringify({ id: row.id }) },
									}, function (rdata) {
										bt.msg(rdata);
										that.initMonitorList();
									}, '删除监控')
								});
							}
						}
					]
				}
			],
			tootls: [
				{
					type: 'group',
					positon: ['left', 'top'],
					list: [
						{
							title: '添加监控',
							active: true,
							event: function () {
								that.getMonitorForm();
							}
						},
						{
							title: '自定义词库',
							event: function () {
								that.getThesaurus();
							}
						}
					]
				}
			]
		});
	},
	/**
   * @description 获取时间简化缩写
   * @param {Numbre} dateTimeStamp 需要转换的时间戳
   * @return {String} 简化后的时间格式
   */
	get_simplify_time: function (dateTimeStamp) {
    if (dateTimeStamp === 0) return '刚刚';
    if (dateTimeStamp.toString().length == 10) dateTimeStamp = dateTimeStamp * 1000
    var minute = 1000 * 60, hour = minute * 60, day = hour * 24, halfamonth = day * 15, month = day * 30, now = new Date().getTime(), diffValue = now - dateTimeStamp;
    if (diffValue < 0) return '刚刚';
    var monthC = diffValue / month, weekC = diffValue / (7 * day), dayC = diffValue / day, hourC = diffValue / hour, minC = diffValue / minute;
    if (monthC >= 1) {
      result = "" + parseInt(monthC) + "月前";
    } else if (weekC >= 1) {
      result = "" + parseInt(weekC) + "周前";
    } else if (dayC >= 1) {
      result = "" + parseInt(dayC) + "天前";
    } else if (hourC >= 1) {
      result = "" + parseInt(hourC) + "小时前";
    } else if (minC >= 1) {
      result = "" + parseInt(minC) + "分钟前";
    } else {
      result = "刚刚";
    }
    return result;
  },
	/**
	 * @description 获取监控表单
	 */
	getMonitorForm: function (isEdit, row) {
		var that = this;
		isEdit = isEdit || false;
		var title = isEdit ? '编辑监控 [' + row.name + ']' : '添加监控';
		layer.open({
			type: 1,
			closeBtn: 2,
    	shadeClose: false,
			title: title,
			area: '620px',
			btn: ['提交','取消'],
			content: '\
			<div class="monitor-form bt-form-new pd20" style="max-height: 600px;">\
				<div class="form-item">\
					<span class="form-label">监控名</span>\
					<div class="form-content">\
						<input type="text" class="bt-input-text" name="name" style="width: 200px;" placeholder="请输入监控名" />\
					</div>\
				</div>\
				<div class="form-item">\
					<span class="form-label">检测方式</span>\
					<div class="form-content">\
						<select class="bt-input-text" style="width:200px" name="method">\
							<option value="1">全站扫描</option>\
							<option value="2" selected>快速扫描</option>\
							<option value="3">单URL</option>\
						</select>\
					</div>\
				</div>\
				<div class="form-item">\
					<span class="form-label">检测网站</span>\
					<div class="form-content">\
						<select class="bt-input-text" ' + (isEdit ? 'disabled="disabled"' : '') + ' style="width: 200px; margin-right: 8px;" name="site_name">\
							<option value="auto">自定义网站</option>\
						</select>\
						<input type="text" class="bt-input-text" ' + (isEdit ? 'disabled="disabled"' : '') + ' name="site_url" style="width: 197px;" placeholder="请输入网站域名" />\
					</div>\
				</div>\
				<div class="form-item access-form-item">\
					<span class="form-label">访问网站方式</span>\
					<div class="form-content">\
						<div class="form-radio">\
							<input type="radio" id="access_https" name="access" value="https://">\
							<label for="access_https">HTTPS</label>\
						</div>\
						<div class="form-radio">\
							<input type="radio" id="access_http" name="access" checked="checked" value="http://">\
							<label for="access_http">HTTP</label>\
						</div>\
					</div>\
				</div>\
				<div class="form-item">\
					<span class="form-label">发送告警</span>\
					<div class="form-content">\
						<input type="checkbox" id="sendMsg" class="btswitch btswitch-ios" name="send_msg"  />\
						<label class="btswitch-btn" for="sendMsg"></label>\
					</div>\
				</div>\
				<div class="form-item form-item-push" style="display: none;">\
					<span class="form-label">通知方式</span>\
					<div class="form-content push-method" style="align-items: flex-top; flex-wrap: wrap;"></div>\
				</div>\
				<div class="form-item">\
					<span class="form-label">检测频率</span>\
					<div class="form-content">\
						<div style="margin-right: 8px">\
							<select class="bt-input-text" style="width: 70px" name="type">\
								<option value="day">每天</option>\
								<option value="day-n">N天</option>\
								<option value="week">每星期</option>\
								<option value="month">每月</option>\
							</select>\
						</div>\
						<div class="week-select" style="display: none; margin-right: 8px">\
							<select class="bt-input-text" style="width: 80px" name="week">\
								<option value="1">周一</option>\
								<option value="2">周二</option>\
								<option value="3">周三</option>\
								<option value="4">周四</option>\
								<option value="5">周五</option>\
								<option value="6">周六</option>\
								<option value="7">周日</option>\
							</select>\
						</div>\
						<div class="flex group-input where-input" style="display: none; margin-right: 8px">\
							<input type="number" name="where1" min="0" max="31" class="bt-input-text" style="width: 60px;" />\
							<span class="unit">天</span>\
						</div>\
						<div class="flex group-input" style="margin-right: 8px">\
							<input type="number" name="hour" min="0" max="23" class="bt-input-text" style="width: 60px;" />\
							<span class="unit">小时</span>\
						</div>\
						<div class="flex group-input">\
							<input type="number" name="minute" min="0" max="59" class="bt-input-text" style="width: 60px;" />\
							<span class="unit">分钟</span>\
						</div>\
					</div>\
				</div>\
				<div class="form-item">\
					<span class="form-label"></span>\
					<div class="form-content">\
						<div class="form-checkbox">\
							<input type="checkbox" name="switch_config" />\
							<div class="checkbox-label">高级配置</div>\
						</div>\
					</div>\
				</div>\
				<div class="form-config" style="display: none;">\
					<div class="form-item">\
						<span class="form-label">敏感词库</span>\
						<div class="form-content">\
							<ul class="domain-ul-list">\
								<li>\
									<input class="checkbox-text word-checkall" type="checkbox" checked="checked" />\
									<span>全选</span>\
								</li>\
								<li>\
									<input class="checkbox-text word-check" type="checkbox" checked="checked">\
									<span>自定义词库</span>\
								</li>\
								<li>\
									<input class="checkbox-text word-check" type="checkbox" checked="checked">\
									<span>默认词库</span>\
								</li>\
							</ul>\
						</div>\
					</div>\
					<div class="form-item">\
						<span class="form-label">检测带参数的URL</span>\
						<div class="form-content" style="align-items: flex-start;">\
							<div class="flex" style="align-items: center; height: 32px;">\
								<input type="checkbox" id="scanArgs" class="btswitch btswitch-ios" name="scan_args" />\
								<label class="btswitch-btn" for="scanArgs"></label>\
							</div>\
							<div class="desc c9" style="line-height: 22px;">\
								<p>扫描时检测带参数的URL，如URL: https://bt.cn?a=b</p>\
								<p>\
									<span style="margin-right: 20px;">开启前</span>\
									<span>不检测</span>\
								</p>\
								<p>\
									<span style="margin-right: 20px;">开启后</span>\
									<span>检测</span>\
								</p>\
								<p>注意，开启后检测页面将成倍增长，可能会导致检测时间大量增加</p>\
							</div>\
						</div>\
					</div>\
					<div class="form-item">\
						<span class="form-label">头部JS检测</span>\
						<div class="form-content">\
							<input type="checkbox" id="titleHash" class="btswitch btswitch-ios" name="title_hash" />\
							<label class="btswitch-btn" for="titleHash"></label>\
							<span class="desc c9">监控页面源码中的title_hash标签是否有修改</span>\
						</div>\
					</div>\
					<div class="form-item">\
						<span class="form-label">尾部JS检测</span>\
						<div class="form-content">\
							<input type="checkbox" id="tailHash" class="btswitch btswitch-ios" name="tail_hash" />\
							<label class="btswitch-btn" for="tailHash"></label>\
							<span class="desc c9">监控页面源码中的tail_hash标签是否有修改</span>\
						</div>\
					</div>\
					<div class="form-item">\
						<span class="form-label">关键词检测</span>\
						<div class="form-content">\
							<input type="checkbox" id="keywords" class="btswitch btswitch-ios" name="keywords" />\
							<label class="btswitch-btn" for="keywords"></label>\
							<span class="desc c9">监控页面源码中的keywords标签是否有修改</span>\
						</div>\
					</div>\
					<div class="form-item">\
						<span class="form-label">描述检测</span>\
						<div class="form-content">\
							<input type="checkbox" id="descriptions" class="btswitch btswitch-ios" name="descriptions" />\
							<label class="btswitch-btn" for="descriptions"></label>\
							<span class="desc c9">监控页面源码中的descriptions标签是否有修改</span>\
						</div>\
					</div>\
					<div class="form-item">\
						<span class="form-label">标题检测</span>\
						<div class="form-content">\
							<input type="checkbox" id="title" class="btswitch btswitch-ios" name="title" />\
							<label class="btswitch-btn" for="title"></label>\
							<span class="desc c9">监控页面源码中的title标签是否有修改</span>\
						</div>\
					</div>\
					<div class="form-item">\
						<span class="form-label">搜索引擎收录监控</span>\
						<div class="form-content">\
							<input type="checkbox" id="searchMonitor" class="btswitch btswitch-ios" name="search_monitor" />\
							<label class="btswitch-btn" for="searchMonitor"></label>\
							<span class="desc c9">监控搜索引擎是否存在风险关键词</span>\
						</div>\
					</div>\
					<div class="form-item" style="padding-bottom: 20px;">\
						<span class="form-label">自定义访问UA</span>\
						<div class="form-content">\
							<textarea class="bt-input-text" name="scan_ua" style="width: 370px; height: 100px; line-height: 22px;" placeholder="请输入自定义访问UA">Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)</textarea>\
						</div>\
					</div>\
				</div>\
			</div>',
			success: function ($layer) {
				var _that = this;
				// layer居中
				function setLayerCenter() {
					var height = $(window).height();
					var layerHeight = $layer.height();
					var top = (height - layerHeight) / 2;
					$layer.css('top', top);
				}
				var methodMap = {
					1: '全站扫描',
					2: '快速扫描',
					3: '单URL扫描'
				}
				// 检测频率
				$('select[name="type"]').change(function () {
					var type = $(this).val();
					$('.week-select').hide();
					$('.where-input').hide();
					$('select[name="week"]').val(1);
					$('input[name="where1"]').val(3);
					var hour = Math.round(Math.random() * 5);
					$('input[name="hour"]').val(hour);
					var minute = Math.round(Math.random() * 59);
					$('input[name="minute"]').val(minute);
					switch (type) {
						case 'day-n':
							$('.where-input').show();
							$('.where-input .unit').text('天');
							break;
						case 'week':
							$('.week-select').show();
							break;
						case 'month':
							$('.where-input').show();
							$('.where-input .unit').text('日');
							break;
					}
				});
				// 检测网站
				$('select[name="site_name"]').change(function () {
					var site_name = $(this).val();
					switch (site_name) {
						case 'auto':
							$(this).next().show();
							break;
						default:
							var method = $('select[name="method"]').val();
							$('input[name="name"]').val(site_name + methodMap[method]);
							$(this).next().hide();
							break;
					}
				});
				$('input[name="site_url"]').keyup(function () {
					var method = $('select[name="method"]').val();
					$('input[name="name"]').val($(this).val() + methodMap[method]);
				});
				// 检测方式
				$('select[name="method"]').change(function () {
					var method = $(this).val();
					var site_name = $('select[name="site_name"]').val();
					$('input[name="name"]').val(site_name + methodMap[method]);
					if (method == 3) {
						$('select[name="site_name"]').val('auto');
						$('select[name="site_name"]').change();
						$('select[name="site_name"]').attr('disabled', 'disabled');
						$('.access-form-item').hide();
            $('input[name="name"]').val($('input[name="site_url"]').val() + methodMap[method]);
					} else {
            $('.access-form-item').show();
						if (!isEdit) $('select[name="site_name"]').removeAttr('disabled');
					}
				});
				// 表单单选框
				$('.form-checkbox .checkbox-label').click(function () {
					$(this).prev().click();
				});

				// 高级配置
				$('input[name="switch_config"]').change(function () {
					var checked = $(this).is(':checked');
					if (checked) {
						$('.form-config').show();
					} else {
						$('.form-config').hide();
					}
					setLayerCenter();
				});

				// 发送告警
				$('input[name="send_msg"]').change(function () {
					var checked = $(this).is(':checked');
					if (checked) {
						$('.form-item-push').show();
					} else {
						$('.form-item-push').hide();
					}
				});

				// 安装通知方式
				$('.push-method').on('click','.install-notice',function(){
					var type = $(this).data('type')
					open_three_channel_auth(type)
				});

				// 敏感词库
				$('.domain-ul-list .word-checkall').change(function () {
					var checked = $(this).is(':checked');
					$('.domain-ul-list .word-check').prop('checked', checked);
				});
				
				$('.domain-ul-list .word-check').change(function () {
					var all = true;
					for (var i = 0; i < $('.domain-ul-list .word-check').length; i++) {
						$('.domain-ul-list .word-check').eq(i).is(':checked') ? '' : all = false;
						if (!all) break;
					}
					$('.domain-ul-list .word-checkall').prop('checked', all);
				});

				$('.domain-ul-list li span').click(function () {
					$(this).prev().click();
				});

				$('select[name="type"]').change();
				$('input[name="send_msg"]').change();

				this.initNotice();
				this.initSiteList(function (sites) {
					if (isEdit) {
						// 检测网站
						var isAuto = true
						for (var i = 0; i < sites.length; i++) {
							if (sites[i].name === row.site_name) {
								isAuto = false
								break;
							}
						}
						if (!isAuto) {
							$('select[name="site_name"]').val(row.site_name);
							$('select[name="site_name"]').change();
						} else {
							$('input[name="site_url"]').val(row.site_name);
						}
						_that.initForm();
					} else {
						$('select[name="method"]').change();
						if (sites.length > 0) $('select[name="site_name"]').val(sites[0].name);
						$('select[name="site_name"]').change();
					}
				});
			},
			// 初始化网站列表
			initSiteList: function (callback) {
				bt_tools.send({
					url: '/crontab?action=GetDataList',
					data: { type: 'sites' }
				}, function (rdata) {
					var sites = rdata.data;
					var options = '';
					for (var i = 0; i < sites.length; i++) {
						options += '<option value="' + sites[i].name + '">' + sites[i].name + ' [' + sites[i].ps + ']' + '</option>';
					}
					$('select[name="site_name"]').append(options);
					callback(sites);
				});
			},
			// 初始化通知方式
			initNotice: function () {
				bt.site.get_msg_configs(function (rdata) {
					var html = '', unInstall = '', pushList = [];
					for (var key in rdata) {
						if (key === 'sms') continue;
						var item = rdata[key];
						var module = '';
						var id = 'radio_' + item.name
						var checked = key === module ? 'checked' : '';
						var disabled = item.setup ? '' : 'disabled="disabled"';
						var _html = '\
						<div class="form-radio' + (!item.setup ? ' check_disabled' : '') + '">\
							<input type="radio" id="' + id + '" name="push_method" value="' + item.name + '" ' + checked + disabled + ' />\
							<label class="cursor" for="' + id + '" title="' + item.ps + '">' + item.title + '</label>\
							' + (!item.setup ? '[<a target="_blank" class="bterror install-notice" data-type="'+ item.name +'">点击安装</a>]' : '') + '\
						</div>';
						if(!item.setup){
							unInstall += _html;
						}else{
							html += _html;
						}
					}
					$('.push-method').html(html + unInstall)
				});
			},
			// 初始化表单
			initForm: function () {
				$('input[name="name"]').val(row.name);
				// 检测方式
				if (row.method == 3) {
					$('select[name="method"]').attr('disabled', 'disabled');
				} else {
					$('select[name="method"]').find('option[value="3"]').remove();
				}
				$('select[name="method"]').val(row.method);
				// 访问网站方式
				var header = row.url.split('://')[0];
				$('#access_' + header).prop('checked', true);
				// 发送告警
				$('input[name="send_msg"]').prop('checked', row.send_msg === 1);
				$('input[name="send_msg"]').change();
				// 通知方式
				setTimeout(function () {
					if (row.send_type) $('#radio_' + row.send_type).prop('checked', true);
				}, 0);
				
				// 检测频率
				if (row.crontab_info) {
					bt_tools.send({
						url: '/crontab?action=get_crond_find',
						data: { id: row.crontab_info.id }
					}, function (rdata) {
						$('select[name="type"]').val(rdata.type);
						$('select[name="type"]').change();
						$('input[name="hour"]').val(rdata.where_hour);
						$('input[name="minute"]').val(rdata.where_minute);
						if (rdata.type === 'week') $('select[name="week"]').val(rdata.where1);
						if (rdata.type === 'day-n' || rdata.type === 'month') $('input[name="where1"]').val(rdata.where1);
					});
				}
				// 高级配置
				if (row.scan_config) {
					var config = row.scan_config;
					$('input[name="switch_config"]').prop('checked', true);
					$('input[name="switch_config"]').change();
					$('input[name="scan_args"]').prop('checked', config.scan_args === 1);
					$('input[name="title_hash"]').prop('checked', config.title_hash === 1);
					$('input[name="tail_hash"]').prop('checked', config.tail_hash === 1);
					$('input[name="keywords"]').prop('checked', config.keywords === 1);
					$('input[name="descriptions"]').prop('checked', config.descriptions === 1);
					$('input[name="title"]').prop('checked', config.title === 1);
					$('input[name="search_monitor"]').prop('checked', config.search_monitor === 1);
					$('textarea[name="scan_ua"]').val(config.scan_ua);
					$('.word-checkall').prop('checked', false);
					$('.word-checkall').change();
					if (config.thesaurus === 1) {
						$('.word-checkall').prop('checked', true);
						$('.word-checkall').change();
					} else if (config.thesaurus === 2) {
						$('.word-check').eq(0).prop('checked', true);
					} else if (config.thesaurus === 3) {
						$('.word-check').eq(1).prop('checked', true);
					}
				}
			},
			yes: function (index) {
				var data = this.getFormData();
				if (data.name === '') {
					layer.msg('请输入监控名称', { icon: 2 });
					return;
				}
				if (data.site_name === '') {
					layer.msg('请输入检测网站域名', { icon: 2 });
					return;
				}
				if (data.method !== 3) {
					var siteName = $('select[name="site_name"]').val();
					if (siteName === 'auto' && bt.check_domain(data.site_name) === false) {
						layer.msg('检测网站域名格式不正确', { icon: 2 });
						return;
					}
				}
				if (data.send_msg === 1 && !data.send_type) {
					layer.msg('请选择通知方式', { icon: 2 });
					return
				}
				var tips = isEdit ? '编辑监控' : '添加监控';
				var url = isEdit ? 'set_content_monitor_info' : 'add_content_monitor_info'
				if (isEdit) {
					data.id = row.id;
				}
				bt_tools.send({
					url: '/project/content/' + url,
					data: {
						data: JSON.stringify(data)
					}
				}, function (rdata) {
					bt.msg(rdata);
					layer.close(index);
					that.initMonitorList();
				}, tips);
			},
			getFormData: function () {
				var method = parseInt($('select[name="method"]').val());
				var siteName = $('select[name="site_name"]').val();
				siteName = siteName === 'auto' ? $('input[name="site_url"]').val() : siteName;
				var url = method != 3 ? $('input[name="access"]:checked').val() + siteName : siteName;
				var isSend = $('input[name="send_msg"]').is(':checked');
				var data = {
					name: $('input[name="name"]').val(),
					method: parseInt($('select[name="method"]').val()),
					site_name: siteName,
					url: url,
					send_msg: isSend ? 1 : 0,
					type: $('select[name="type"]').val(),
					hour: $('input[name="hour"]').val(),
					minute: $('input[name="minute"]').val()
				};
				if (isSend) data.send_type = $('input[name="push_method"]:checked').val();
				if (!$('.week-select').is(':hidden')) data.week = $('select[name="week"]').val();
				if (!$('.where-input').is(':hidden')) data.where1 = $('input[name="where1"]').val();
				if ($('input[name="switch_config"]').is(':checked')) data.scan_config = this.getScanConfig();
				return data;
			},
			getScanConfig: function () {
				var data = {
					scan_args: $('input[name="scan_args"]').is(':checked') ? 1 : 0,
					title: $('input[name="title"]').is(':checked') ? 1 : 0,
					keywords: $('input[name="keywords"]').is(':checked') ? 1 : 0,
					descriptions: $('input[name="descriptions"]').is(':checked') ? 1 : 0,
					title_hash: $('input[name="title_hash"]').is(':checked') ? 1 : 0,
					tail_hash: $('input[name="tail_hash"]').is(':checked') ? 1 : 0,
					search_monitor: $('input[name="search_monitor"]').is(':checked') ? 1 : 0,
					scan_ua: $('textarea[name="scan_ua"]').val(),
				};
				if ($('.word-checkall').is(':checked')) {
					data.thesaurus = 1;
				} else if ($('.word-check').eq(0).is(':checked')) {
					data.thesaurus = 2;
				} else if ($('.word-check').eq(1).is(':checked')) {
					data.thesaurus = 3;
				} else {
					data.thesaurus = 4;
				}
				return data;
			}
		})
	},
	/**
	 * @description 检测监控
	 */
	checkMontior: function (row, res) {
		var timer = null;
		function clearTimer () {
			if (timer) clearTimeout(timer);
		}
		layer.open({
      title: '检测监控 [' + row.name + ']',
      type: 1,
      closeBtn: 2,
    	shadeClose: false,
      area: ['630px', '410px'],
			btn: ['停止检测', '关闭'],
      content: '<pre id="create_lst" class="crontab-log" style="height: 100%; margin-top: 0; border-radius: 0;"></pre>',
      success: function (layers, index) {
				this.isScan = true;
				this.getLog();
      },
			btn2: function () {
				clearTimer();
			},
			cancel: function () {
				clearTimer();
			},
			yes: function (index) {
				var that = this;
				bt.confirm({ msg: '当前正在进行检测网站，确定停止检测网站吗？', title: '停止检测网站' }, function (cIndex) {
					bt_tools.send({
						url: '/project/content/kill_scanning',
						data: { data: JSON.stringify({ id: row.id }) }
					}, function (res) {
						bt.msg(res);
						that.isScan = false;
						layer.close(cIndex);
						layer.close(index);
					});
				});
			},
			getLog: function () {
				var that = this;
				bt_tools.send({
					url: '/ajax?action=get_lines&num=20&filename=' + res.path_info
				}, function (rdata) {
					$("#create_lst").text(rdata.msg);
					$("#create_lst").scrollTop($("#create_lst")[0] ? $("#create_lst")[0].scrollHeight : 0);
					// 扫描已结束
					if (rdata.msg.indexOf('扫描结束') !== -1) {
						that.isScan = false;
						layer.msg('扫描已结束', { icon: 1 });
						clearTimer();
						return;
					}
					// 扫描未结束
					if (rdata.msg.indexOf('扫描结束') === -1 && that.isScan) {
						timer = setTimeout(function () {
							that.getLog();
						}, 1000);
					}
				}, function (rdata) {
					bt.msg(rdata);
					that.isScan = false;
				});
			}
    });
	},
	/**
	 * @description 修复计划任务
	 * @param {*} row 
	 */
	repairCron: function (row) {
		var that = this;
		layer.open({
			type: 1,
			closeBtn: 2,
    	shadeClose: false,
			title: '修复计划任务 [' + row.name + ']',
			area: '560px',
			btn: ['提交','取消'],
			content: '\
			<div class="bt-form-new pd20" style="padding: 30px 20px;">\
				<div class="form-item">\
					<span class="form-label">检测频率</span>\
					<div class="form-content">\
						<div style="margin-right: 8px">\
							<select class="bt-input-text" style="width: 70px" name="type">\
								<option value="day">每天</option>\
								<option value="day-n">N天</option>\
								<option value="week">每星期</option>\
								<option value="month">每月</option>\
							</select>\
						</div>\
						<div class="week-select" style="display: none; margin-right: 8px">\
							<select class="bt-input-text" style="width: 80px" name="week">\
								<option value="1">周一</option>\
								<option value="2">周二</option>\
								<option value="3">周三</option>\
								<option value="4">周四</option>\
								<option value="5">周五</option>\
								<option value="6">周六</option>\
								<option value="7">周日</option>\
							</select>\
						</div>\
						<div class="flex group-input where-input" style="display: none; margin-right: 8px">\
							<input type="number" name="where1" min="0" max="31" class="bt-input-text" style="width: 60px;" />\
							<span class="unit">天</span>\
						</div>\
						<div class="flex group-input" style="margin-right: 8px">\
							<input type="number" name="hour" min="0" max="23" class="bt-input-text" style="width: 60px;" />\
							<span class="unit">小时</span>\
						</div>\
						<div class="flex group-input">\
							<input type="number" name="minute" min="0" max="59" class="bt-input-text" style="width: 60px;" />\
							<span class="unit">分钟</span>\
						</div>\
					</div>\
				</div>\
			</div>',
			success: function () {
				// 检测频率
				$('select[name="type"]').change(function () {
					var type = $(this).val();
					$('.week-select').hide();
					$('.where-input').hide();
					$('select[name="week"]').val(1);
					$('input[name="where1"]').val(3);
					var hour = Math.round(Math.random() * 5);
					$('input[name="hour"]').val(hour);
					var minute = Math.round(Math.random() * 59);
					$('input[name="minute"]').val(minute);
					switch (type) {
						case 'day-n':
							$('.where-input').show();
							$('.where-input .unit').text('天');
							break;
						case 'week':
							$('.week-select').show();
							break;
						case 'month':
							$('.where-input').show();
							$('.where-input .unit').text('日');
							break;
					}
				});

				$('select[name="type"]').change();
			},
			yes: function (index) {
				var data = {
					id: row.id,
					type: $('select[name="type"]').val(),
					hour: $('input[name="hour"]').val(),
					minute: $('input[name="minute"]').val()
				}
				if (!$('.week-select').is(':hidden')) data.week = $('select[name="week"]').val();
				if (!$('.where-input').is(':hidden')) data.where1 = $('input[name="where1"]').val();
				bt_tools.send({
					url: '/project/content/repair_cron',
					data: { data: JSON.stringify(data) }
				}, function (res) {
					layer.close(index);
					that.initMonitorList();
					bt.msg(res);
				});
			}
		});
	},
	/**
	 * @description 自定义词库
	 */
	getThesaurus: function () {
		var table = null;
		layer.open({
			type: 1,
			closeBtn: 2,
    	shadeClose: false,
			area: '440px',
			title: '自定义词库',
			content: '<div class="pd15"><div id="thesaurus-table" style="padding-bottom: 2px;"></div></div>',
			success: function ($layer) {
				function setLayerCenter () {
					if (!$layer) return;
					var height = $(window).height();
					var layerHeight = $layer.height();
					var top = (height - layerHeight) / 2;
					$layer.css('top', top);
				}

				table = bt_tools.table({
					el: '#thesaurus-table',
					url: '/project/content/get_thesaurus',
					height: '400',
					load: '获取自定义词库',
					default: "暂无数据",
					autoHeight: true,
					dataFilter: function (res) {
						var data = [];
						$.each(res, function (i, item) {
							data.push({ name: item });
						});
						setTimeout(function () {
							setLayerCenter();
						}, 0);
						return { data: data }
					},
					column: [
						{ fid: 'name', title: '关键词' },
						{
							fid: 'opt',
							title: '操作',
							align: 'right',
							type: 'group',
							width: 80,
							group: [
								{
									title: '删除',
									event: function (row) {
										bt_tools.send({
											url: '/project/content/del_thesaurus',
											data: { data: JSON.stringify({ key: row.name }) }
										}, function (res) {
											table.$refresh_table_list();
											bt.msg(res);
										}, '删除自定义词库');
									}
								}
							]
						}
					],
					tootls: [
						{
							type: 'group',
							positon: ['left', 'top'],
							list: [
								{
									title: '添加',
									active: true,
									event: function () {
										var form = null;
										bt_tools.open({
											title: '添加自定义词库',
											area: '400px',
											btn: ['添加', '取消'],
											content: '<div class="pd20" id="thesaurus-form"></div>',
											success: function () {
												form = bt_tools.form({
													el: '#thesaurus-form',
													form: [
														{
															label: '关键词',
															group: {
																type: 'text',
																name: 'key',
																width: '220px',
																placeholder: '请输入你需要扫描的关键词'
															}
														}
													]
												});
												$('#thesaurus-form').append(bt.render_help(['关键字小于3时会引起大量误报，请设置大于等于3个关键字！']));
											},
											yes: function (index) {
												var data = form.$get_form_value()
												if (data.key === '') {
													layer.msg('关键词不能为空', { icon: 2 });
													return
												}
												bt_tools.send({
													url: '/project/content/add_thesaurus',
													data: { data: JSON.stringify(data) }
												}, function (res) {
													layer.close(index);
													table.$refresh_table_list();
													bt.msg(res);
												}, '添加自定义词库');
											}
										});
									}
								},
								{
									title: '导入',
									event: function () {
										bt_tools.open({
											title: '导入自定义词库',
											area: ['400px', '370px'],
											btn: ['确定', '取消'],
											content: '\
											<div class="pd20">\
												<textarea name="key" class="bt-input-text" style="width: 100%; height: 230px; line-height: 22px;" placeholder="导入格式如下：一行一个，如果在同一行输入则视为一个"></textarea>\
											</div>',
											yes: function (index) {
												var key = $('textarea[name="key"]').val();
												if (key === '') {
													layer.msg('导入数据不能为空', { icon: 2 })
													return
												}
												bt_tools.send({
													url: '/project/content/import_thesaurus',
													data: { data: JSON.stringify({ key: key }) }
												}, function (res) {
													layer.close(index);
													table.$refresh_table_list();
													bt.msg(res);
												}, '导入自定义词库');
											}
										})
									}
								},
								{
									title: '清空',
									event: function () {
										bt.confirm({
											title: '清空自定义词库',
											msg: '是否清空列表数据？'
										}, function (index) {
											layer.close(index);
											bt_tools.send({
												url: '/project/content/clear_thesaurus',
											}, function (res) {
												bt.msg(res);
												table.$refresh_table_list();
											}, '清空自定义词库');
										});
									}
								}
							]
						}
					]
				});
			}
		})
	},
	/**
	 * @description 检测历史
	 */
	initDetectHistory: function () {
		var that = this;
		bt_tools.table({
			el: '#detect-history-table',
			url: '/project/content/get_risk',
			default: '暂无数据',
			load: '获取检测历史',
			autoHeight: true,
			height: '980px',
			column: [
				{
					fid: 'site_name',
					title: '网站列表'
				},
				{
					fid: 'scans',
					title: '扫描URL总数'
				},
				{
					fid: 'start_time',
					type: 'text',
					title: '扫描耗时',
					template: function (row) {
						if (row.end_time <= 1) return '0秒';
						if (row.end_time - row.start_time <= 0) return '0秒';
						return '<span>' + that.getDuration(row.end_time - row.start_time) + '</span>';
					}
				},
				{
					fid: 'risks',
					title: '风险次数',
					template: function (row) {
						if (row.risks > 0) return '<a class="bterror" href="javascript:;">' + row.risks + '</a>'
						return '<span class="cbt">无风险</span>'
					},
					event: function (row) {
						if (row.risks === 0) return;
						that.showRiskDetails(row);
					}
				},
				{
					fid: 'status',
					type: 'text',
					title: '状态',
					template: function (row) {
						if ((row.is_status === 0 && row.end_time === 0) || row.end_time === 1) {
							return '<span class="red">扫描未完成</span>'
						}
						if (row.is_status === 1 && row.end_time === 0) {
							return '<span class="bt_warning">扫描中</span>'
						}
						return '<span class="cbt">扫描完成</span>'
					}
				},
				{
					fid: 'start_time',
					type: 'text',
					title: '扫描时间',
					template: function (row) {
						return '<span>' + bt.format_data(row.start_time) + '</span>'
					}
				},
				{
					fid: 'group',
					type: 'group',
					align: 'right',
					title: '操作',
					group: [
						{
							title: '查看报告',
							template: function (row) {
								if ((row.is_status === 0 && row.end_time === 0) || row.end_time === 1) {
									return '<span style="color: #c8c9cc; cursor: not-allowed;">查看报告</span>'
								}
								if (row.is_status === 1 && row.end_time === 0) {
									return '<span style="color: #c8c9cc; cursor: not-allowed;">查看报告</span>'
								}
								return '<span class="btlink">查看报告</span>'
							},
							event: function (row) {
								if ((row.is_status === 0 && row.end_time === 0) || row.end_time === 1) return;
								if (row.is_status === 1 && row.end_time === 0) return;
								
								window.open('/project/content/report/html?id=' + row.testing_id);
							}
						}
					]
				}
			],
			tootls: [
				{ 
					type: 'page', // 分页显示
					jump: true, // 是否支持跳转分页,默认禁用
				}
			]
		})
	},
	/**
	 * @description 秒转成天时分秒
	 * @param {*} second 
	 * @returns 
	 */
	getDuration: function (second) {
		var duration
		var days = Math.floor(second / 86400);
		var hours = Math.floor((second % 86400) / 3600);
		var minutes = Math.floor(((second % 86400) % 3600) / 60);
		var seconds = Math.floor(((second % 86400) % 3600) % 60);
		if(days>0)  duration = days + "天" + hours + "小时" + minutes + "分" + seconds + "秒";
		else if(hours>0)  duration = hours + "小时" + minutes + "分" + seconds + "秒";
		else if(minutes>0) duration = minutes + "分" + seconds + "秒";
		else if(seconds>=0) duration = seconds + "秒";
		return duration;
	},
	/**
	 * @description 风险详情
	 * @param {*} row 
	 */
	showRiskDetails: function (row) {
		var that = this;
		layer.open({
			type: 1,
			closeBtn: 2,
			shadeClose: false,
			title: '风险详情 [' + row.site_name + ']',
			area: '850px',
			zIndex: 2000,
			content: '<div class="pd20"><div class="new-table" id="risk-details-table"></div></div>',
			success: function ($layer) {
				function setLayerCenter () {
					if (!$layer) return;
					var height = $(window).height();
					var layerHeight = $layer.height();
					var top = (height - layerHeight) / 2;
					$layer.css('top', top);
				}

				var typeMap = {
					title: '标题',
					body: '网页内',
					keywords: '关键词',
					descriptions: '描述',
					title_update: '标题更新',
					keywords_update: '关键词更新',
					description_update: '描述更新',
					tail_hash_update: '尾部script代码块更新',
					title_hash_update: '头部head代码块更新',
				}
				bt_tools.table({
					el: '#risk-details-table',
					url: '/project/content/get_risk_info',
					default: '暂无数据',
					height: 470,
					beforeRequest: function (param) {
						param.data = JSON.stringify({ testing_id: row.testing_id, p: param.p, limit: param.limit })
						return param
					},
					dataFilter: function (res) {
						setTimeout(function () {
							setLayerCenter();
						}, 0);
						return res
					},
					column: [
						{
							fid: 'time',
							type: 'text',
							width: '140px',
							title: '巡检时间',
							template: function (row) {
								return '<span>' + bt.format_data(row.time) + '</span>';
							}
						},
						{
							fid: 'url',
							title: 'URL',
							width: '196px',
							template: function (row) {
								return '<a class="ellipsis_text btlink" href="' + row.url + '" target="_blank" style="max-width: 180px; width: auto;" title="' + row.url + '">' + row.url + '</a>'
							}
						},
						{
							fid: 'content',
							type: 'text',
							title: '关键词',
							template: function (row) {
								return '<span class="ellipsis_text" style="max-width: 240px; width: 100%;" title="' + row.content + '">' + row.content + '</span>'
							}
						},
						{
							fid: 'risk_content',
							title: '类型',
						},
						{
							fid: 'risk_type',
							type: 'text',
							title: '风险位置',
							template: function (row) {
								return '<span>' + typeMap[row.risk_type] + '</span>';
							}
						},
						{
							fid: 'result',
							type: 'group',
							align: 'right',
							title: '操作',
							width: '60px',
							group: [
								{
									title: '详情',
									event: function (row) {
										var baseUrl = '/www/server/panel/class/projectModel/content/source/';
										var url = baseUrl + row.source_file;
										if (row.risk_type.indexOf('_update') > -1) {
											that.showBothFile(row, baseUrl);
										} else {
											that.showFile(url, row.content);
										}
									}
								}
							]
						}
					],
					tootls: [
						{ 
							type: 'page', // 分页显示
							jump: true, // 是否支持跳转分页,默认禁用
						}
					]
				})
			}
		});
	},
	/**
	 * @description 获取风险列表
	 */
	initRiskList: function () {
		var that = this;

		var typeMap = {
			title: '标题',
			body: '网页内',
			keywords: '关键词',
			descriptions: '描述',
			title_update: '标题更新',
			keywords_update: '关键词更新',
			description_update: '描述更新',
			tail_hash_update: '尾部script代码块更新',
			title_hash_update: '头部head代码块更新',
		}

		bt_tools.table({
			el: '#risk-table',
			url: '/project/content/get_risk_list',
			height: '980px',
			default: "风险列表为空",
			autoHeight: true,
			column: [
				{
					fid: 'time',
					type: 'text',
					width: '160px',
					title: '巡检时间',
					template: function (row) {
						return '<span>' + bt.format_data(row.time) + '</span>';
					}
				},
				{
					fid: 'url',
					title: 'URL',
					template: function (row) {
						return '<span class="flex"><a class="ellipsis_text btlink" href="' + row.url + '" target="_blank" style="min-width: 120px; flex: 1; width: 0;" title="' + row.url + '">' + row.url + '</a></span>';
					}
				},
				{
					fid: 'content',
					type: 'text',
					title: '关键词',
					template: function (row) {
						return '<span class="flex"><span class="ellipsis_text" style="min-width: 130px; flex: 1; width: 0;" title="' + row.content + '">' + row.content + '</span></span>';
					}
				},
				{
					fid: 'risk_content',
					title: '类型',
					template: function (row) {
						return '<span class="inlineBlock">' + row.risk_content + '</span>';
					}
				},
				{
					fid: 'risk_type',
					type: 'text',
					title: '风险位置',
					template: function (row) {
						return '<span class="inlineBlock">' + typeMap[row.risk_type] + '</span>';
					}
				},
				{
					fid: 'result',
					type: 'group',
					align: 'right',
					title: '操作',
					width: '60px',
					group: [
						{
							title: '详情',
							event: function (row) {
								var baseUrl = '/www/server/panel/class/projectModel/content/source/';
								var url = baseUrl + row.source_file;
								if (row.risk_type.indexOf('_update') > -1) {
									that.showBothFile(row, baseUrl);
								} else {
									that.showFile(url, row.content);
								}
							}
						}
					]
				}
			],
			tootls: [
				{ 
					type: 'page', // 分页显示
					jump: true, // 是否支持跳转分页,默认禁用
				}
			]
		});
	},
	/**
	 * @description 显示文件详情
	 */
	showFile: function (path, content, callback, close) {
		var editor = null;
		var html = document.getElementById("aceTmplate").innerHTML;
		var _aceTmplate = html.replace(/\<\\\/script\>/g, '</script>');
		var config = {
			id: '',
			type: '',
		}
		layer.open({
			type: 1,
			maxmin: true,
			shade: false,
			anim:-1,
			area: ['80%', '80%'],
			title: '文件详情',
			skin: 'aceEditors',
			zIndex: 19999,
			content: _aceTmplate,
			end: function () {
				editor && editor.destroy();
				editor && editor.container.remove();
				close && close();
			},
			success: function (layero, index) {
				var _this = this;
				var _icon = '<span class="icon"><i class="glyphicon glyphicon-ok" aria-hidden="true"></i></span>';

				$('.ace_editor_main').on('click', function () {
					$('.ace_toolbar_menu').hide();
				});

				$(document).click(function (e) {
					$('.ace_toolbar_menu').hide();
				});

				// 最大化、最小化
        layero.find('.layui-layer-max').click(function (e) {
					aceEditor.setEditorView();
        });

				// 顶部状态栏
				$('.ace_header>span').click(function (e) {
					var type = $(this).attr('class');
					if (_this.ace_active == '' && type != 'helps') {
						return false;
					}
					switch (type) {
						// 刷新文件
						case 'refreshs': 
							aceEditor.getFileBody({ path: path }, function (res) {
								$('.item_tab_' + config.id + ' .icon-tool').attr('data-file-state', '0').removeClass('glyphicon-exclamation-sign').addClass('glyphicon-remove');
								_this.setEditorVal(res.data);
								if (content) {
									editor.find(content);
									editor.execCommand('find');
								}
								layer.msg('刷新成功', { icon: 1 });
							});
							break;
						// 搜索
						case 'searchs':
							editor.execCommand('find');
							break;
						// 跳转行
						case 'jumpLine':
							$('.ace_toolbar_menu').show().find('.menu-jumpLine').show().siblings().hide();
							$('.set_jump_line input').val('').focus();
							var _cursor = editor.selection.getCursor();
							$('.set_jump_line .jump_tips span:eq(0)').text(_cursor.row);
							$('.set_jump_line .jump_tips span:eq(1)').text(_cursor.column);
							$('.set_jump_line .jump_tips span:eq(2)').text(editor.session.getLength());
							$('.set_jump_line input').unbind('keyup').on('keyup', function (e) {
								var _val = $(this).val();
								if ((e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 96 && e.keyCode <= 105)) {
									if (_val != '' && typeof parseInt(_val) == 'number') {
										editor.gotoLine(_val);
									};
								}
							});
							break;
						case 'helps':
							if (!$('[data-type=shortcutKeys]').length != 0) {
								aceEditor.addEditorView(1, { title: '快捷键提示', html: aceShortcutKeys.innerHTML });
							} else {
								$('[data-type=shortcutKeys]').click();
							}
							break;
					}
		
					e.stopPropagation();
					e.preventDefault();
				});

				// 切换TAB视图
				$('.ace_conter_menu').on('click', '.item', function (e) {
					var _id = $(this).attr('data-id')
					$('.item_tab_' + _id).addClass('active').siblings().removeClass('active');
					$('#ace_editor_' + _id).addClass('active').siblings().removeClass('active');
					_this.currentStatusBar(_id);
				});

				// 关闭编辑视图
				$('.ace_conter_menu').on('click', '.item .icon-tool', function (e) {
					var file_type = $(this).attr('data-file-state');
					var id = $(this).parent().parent().attr('data-id');
					switch (file_type) {
						// 直接关闭
						case '0':
							$('.item_tab_' + id).remove();
							$('#ace_editor_' + id).remove();
							$('.ace_conter_menu .item').eq(0).click();
							_this.currentStatusBar(id);
							break;
					}
					$('.ace_toolbar_menu').hide();
					e.stopPropagation();
					e.preventDefault();
				});

				// 显示工具条
				$('.ace_header .pull-down').click(function () {
					if ($(this).find('i').hasClass('glyphicon-menu-down')) {
						$('.ace_header').css({ 'top': '-30px' });
						$('.ace_overall').css({ 'top': '0' });
						$(this).css({ 'top': '30px', 'height': '30px', 'line-height': '30px' });
						$(this).find('i').addClass('glyphicon-menu-up').removeClass('glyphicon-menu-down');
					} else {
						$('.ace_header').css({ 'top': '0' });
						$('.ace_overall').css({ 'top': '30px' });
						$(this).removeAttr('style');
						$(this).find('i').addClass('glyphicon-menu-down').removeClass('glyphicon-menu-up');
					}
					aceEditor.setEditorView();
				});

				// 底部状态栏功能按钮
				$('.ace_conter_toolbar .pull-right span').click(function (e) {
					var _type = $(this).attr('data-type');
					switch (_type) {
						case 'cursor':
							$('.ace_header .jumpLine').click();
							break;
						case 'lang':
							layer.msg('暂不支持切换语言模式，敬请期待!', { icon: 6 });
							break;
					}
					e.stopPropagation();
					e.preventDefault();
				});

				_this.getFileBody();
			},
			// 获取文件内容
			getFileBody: function () {
				var _this = this;
				aceEditor.getFileBody({ path: path }, function (res) {
					var _id = bt.get_random(8);
					var paths = path.split('/');
					var _fileName = paths[paths.length - 1];
					var _fileType = aceEditor.getFileType(_fileName);
					var _type = _fileType.name;
					var _mode = _fileType.mode;
					config.type = _type;
					$('.ace_conter_menu').append('\
						<li class="item active item_tab_' + _id + '" title="' + path + '" data-type="' + _type + '" data-mode="' + _mode + '" data-id="' + _id + '" data-fileName="' + _fileName + '">\
							<div class="ace_item_box" style="padding-right: 10px;">\
            		<span class="icon_file"><i class="' + _mode + '-icon"></i></span>\
								<span class="tab_text" title="' + path + '">' + _fileName + '</span>\
            	</div>\
            </li>\
					');
					$('.ace_conter_editor').append('<div id="ace_editor_' + _id + '" class="ace_editors active"></div>');
					if (res.only_read && res.size > 3145928) {
						layer.msg('文件大小超过3MB，仅显示最新的10000行数据', { icon: 0, area: '380px' });
					}
					_this.createEditor(_id);
					_this.setEditorVal(res.data);
					if (content) {
						editor.find(content);
						editor.execCommand('find');
					}
					callback && callback(res.data, editor);
				});
			},
			// 创建编辑器
			createEditor: function (id) {
				if (editor) return;

				var element = document.getElementById('ace_editor_' + id);
				config.id = id;
				ace.require("/ace/ext/language_tools");
				editor = ace.edit(element, {
					mode: 'ace/mode/html',
					theme: 'ace/theme/monokai',
					wrap: true, // 是否换行
					readOnly: true, // 是否只读
					showInvisibles: true,  // 是否显示不可见字符
					showPrintMargin: false,	// 是否显示打印边距
				});
				editor.selection.on('changeCursor', function (e) {
					var _cursor = editor.selection.getCursor();
					$('[data-type="cursor"]').html('行<i class="cursor-row">' + (_cursor.row + 1) + '</i>,列<i class="cursor-line">' + _cursor.column + '</i>');
				});
				this.currentStatusBar(id);
			},
			// 设置编辑器的值
			setEditorVal: function (data) {
				editor.setValue(data);
				editor.resize();
				editor.focus();
				editor.moveCursorTo(0, 0);
			},
			// 更新状态栏
			currentStatusBar: function (id) {
				if (config.id !== id) {
					aceEditor.removerStatusBar();
					return;
				}

				$('.ace_conter_toolbar [data-type="tab"]').remove();
				$('.ace_conter_toolbar [data-type="history"]').remove();
				$('.ace_conter_toolbar [data-type="encoding"]').remove();
				$('.ace_conter_toolbar [data-type="cursor"]').html('行<i class="cursor-row">1</i>,列<i class="cursor-line">0</i>');
				$('.ace_conter_toolbar [data-type="path"]').html('文件位置：<i title="' + path + '">' + path + '</i>');
				var readOnly = $('.ace_conter_toolbar [data-type="readOnly"]');
				readOnly.show().text('只读模式').css('background','#ff9200');
				$('.ace_conter_toolbar [data-type="lang"]').html('语言：<i>HTML</i>');
				$('.ace_conter_toolbar span').attr('data-id', id);
				$('.file_fold').removeClass('bg');
				$('[data-menu-path="' + path + '"]').find('.file_fold').addClass('bg');
				
				editor.resize();
			}
		});
	},
	/**
	 * @description 显示两个文件的对比
	 * @param {*} row 
	 * @param {*} baseUrl 
	 */
	 showBothFile: function (row, baseUrl) {
		if (row.risk_type === 'title_hash_update' || row.risk_type === 'tail_hash_update') {
			baseUrl = '/www/server/panel/class/projectModel/content/hash/' + row.site_name + '/';
		}
		var sPath = baseUrl + row.source_content_file;
		var aceDiff = null;
		this.showFile(sPath, '', function (sData, ace) {
			var nPath = baseUrl + row.new_content_file;
			aceEditor.getFileBody({ path: nPath }, function (nData) {
				var $item = $('.ace_conter_menu .item.active');
				$item.find('.icon_file').html('<img src="/static/img/ico-history.png">');
				$item.find('.icon_file').next().text('原内容 <-> 新内容').attr('title', sPath + ' <-> ' + nPath);
				$('.ace_scroller').remove();
				console.log();
				aceDiff = new AceDiff({
					element: '#' + ace.container.id,
					theme: 'ace/theme/monokai',
					mode: 'ace/mode/html',
					showConnectors: false,
					left: {
						content: html_beautify(sData),
						editable: false,
						copyLinkEnabled: false
					},
					right: {
						content: html_beautify(nData.data),
						editable: false,
						copyLinkEnabled: false
					},
				});
				aceDiff.editors.left.ace.session.setUseWrapMode(true);
				aceDiff.editors.left.ace.setShowPrintMargin(false);
				aceDiff.editors.right.ace.session.setUseWrapMode(true);
				aceDiff.editors.right.ace.setShowPrintMargin(false);

				// 滚动同步
				var left = aceDiff.editors.left.ace;
				var right = aceDiff.editors.right.ace;
				$('.acediff__left .ace_scrollbar-v').scroll(function () {
					right.session.setScrollTop(left.session.getScrollTop())
				})
				$('.acediff__right .ace_scrollbar-v').scroll(function () {
					left.session.setScrollTop(right.session.getScrollTop())
				});
			}, function () {
				aceDiff && aceDiff.destroy();
			});
		});
	}
}

firewall.event();

function CreateConnect(config,callback) {
  this.progressList = ['system_account','sshd_service','file_mode','software','website_permissions','other'],// 类型
  this.execution = 0; // 执行位置
  this.connectStatus = false; // 连接状态
  this.isHandle = false; // 是否处理
  this.config = { // 配置
    mod_name:"safe_detect",
    def_name:"get_safe_scan",
    ws_callback:'',
  }
  this.init();
  this.onmessage = config.onmessage
  if(callback){
    callback.call(this);
  }
}

/**
 * @description 初始化链接
 * @param {*} data
 */
 CreateConnect.prototype.init = function(callback){
  var that = this;
  var http_token = $("#request_token_head").attr('token');
  this.send()
  this.connect.onopen = function(){
    that.connectStatus = true;
    this.send(JSON.stringify({ 'x-http-token': http_token }))
    this.send(JSON.stringify({
      mod_name:'safe_detect'
    }));
    if(callback) callback()
  }
}

/**
 * @description 开始执行扫描
 * @param {*} data
 */
 CreateConnect.prototype.start = function(error){
  var that = this, index = 0,isEnd = false, errorNum = 0,errorWarnNum = 0,score = 0;
  this.isHandle = true;
  if(this.connectStatus){
    var ws = this.connect;
    var execution = this.execution;
    this.config.ws_callback = new Date().getTime();
    ws.send(JSON.stringify(this.config));
    ws.onmessage = function(wsData){
      if(isEnd){
        that.execution ++;
        that.start(errorNum);
        return false;
      }
      var data = JSON.parse(wsData.data.replace(/'/g,'"'))
      if(data.status === 3) errorNum += 1
      if(data.status === 2) errorWarnNum += 1
      if(data.points) score += data.points
      if(!that.isHandle) return false;
      that.onmessage(data.callback ? {isEnd:true, error:errorNum, warn:errorWarnNum, total_score:score,time: data.callback} : data); // 监听返回内容
    }
  }else{
    that.init(function () {
      that.start()
    })
  }
}

/**
 * @description 取消扫描
*/
CreateConnect.prototype.cancel = function(){
  this.isHandle = false;
  this.execution = 0;
}

/**
 * @description 发送请求
 */
CreateConnect.prototype.send = function(){
  var protocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
  this.connect = new WebSocket(protocol + location.host +'/ws_project');
}

/**
 * @description 关闭ws链接
 */
CreateConnect.prototype.close = function(){
  this.connect.close();
  this.connectStatus = false;
  this.cancel();
}