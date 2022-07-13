$('.database-pos .tabs-item').click(function () {
  var type = $(this).data('type');
  var index = $(this).index();
  bt.set_cookie('db_page_model', type);
  bt.data.db_tab_name = type
  $(this).addClass('active').siblings().removeClass('active');
  $('.db_table_view .tab-con .tab-con-block').eq(index).removeClass('hide').siblings().addClass('hide');
  if(type == 'redis'){
    $('.info-title-tips').hide()
  }else{
    $('.info-title-tips').show()
  }
  var loadT = layer.msg('正在获取远程服务器列表,请稍候...', {
    icon: 16,
    time: 0,
    shade: [0.3, '#000']
  });

  var requestParam = {url:'database/'+bt.data.db_tab_name+'/GetCloudServer',data:{data:JSON.stringify({type:bt.data.db_tab_name})}}
  if(bt.data.db_tab_name == 'mysql') requestParam = {url:'database?action=GetCloudServer',data:{type:bt.data.db_tab_name}}
  bt_tools.send(requestParam,function(cloudData){
    layer.close(loadT);
    cloudDatabaseList = cloudData
    //是否安装本地或远程服务器
    if(cloudData.length <= 0){
      var tips = '当前未安装本地服务器/远程服务器,<a class="btlink install_server">点击安装</a> | <a class="btlink" onclick="db_public_fn.get_cloud_server_list()">添加远程服务器</a>'
      if(bt.data.db_tab_name == 'sqlserver')tips = '当前未配置远程服务器,<a class="btlink" onclick="db_public_fn.get_cloud_server_list()">添加远程服务器</a>'
      $('.mask_layer').removeAttr('style');
      $('.prompt_description').html(tips)

      //安装docker
      $('.install_server').click(function(){
        bt.soft.install(bt.data.db_tab_name)
      })
    }else{
      $('.mask_layer').hide()
    }
    switch (type) {
      case 'mysql':
        database.database_table_view();
        break;
      case 'sqlserver':
        sql_server.database_table_view();
        break;
      case 'mongodb':
        bt_tools.send({url:'database/'+bt.data.db_tab_name+'/get_root_pwd'},function(_status){
          mongoDBAccessStatus = _status.authorization == 'enabled'?true:false
          mongodb.database_table_view();
        },'获取访问状态')
        break;
      case 'redis':
        redis.database_table_view();
        break;
    }

  })
});


var database_table = null,
    dbCloudServerTable = null,  //远程服务器视图
    cloudDatabaseList = [],     //远程服务器列表
    mongoDBAccessStatus = false;

var database = {
  backuptoList: [{ title: '本地服务器', value: 'localhost' },
  { title: '阿里云OSS', value: 'alioss' },
  { title: '腾讯云COS', value: 'txcos' },
  { title: '七牛云存储', value: 'qiniu' },
  { title: '华为云存储', value: 'obs' },
  { title: '百度云存储', value: 'bos' }],
  database_table_view: function (search) {
    var param = {
      table: 'databases',
      search: search || ''
    }
    $('#bt_database_table').empty();
    database_table = bt_tools.table({
      el: '#bt_database_table',
      url: '/data?action=getData',
      param: param, //参数
      minWidth: '1000px',
      autoHeight: true,
      default: "数据库列表为空", // 数据为空时的默认提示
      pageName: 'database',
      beforeRequest: function(){
        var db_type_val = $('.database_type_select_filter').val()
        switch(db_type_val){
          case 'all':
            delete param['db_type']
            delete param['sid']
            break;
          case 0:
            param['db_type'] = 0;
            break;
          default:
            delete param['db_type'];
            param['sid'] = db_type_val
        }
        return param
      },
      column: [{
        type: 'checkbox',
        width: 20
      },
        {
          fid: 'name',
          title: '数据库名',
          type: 'text'
        },
        {
          fid: 'username',
          title: '用户名',
          type: 'text',
          sort: true
        },
        {
          fid: 'password',
          title: '密码',
          type: 'password',
          copy: true,
          eye_open: true,
          template: function (row) {
            if (row.password === '') return '<span class="c9 cursor" onclick="database.set_data_pass(\'' + row.id + '\',\'' + row.username + '\',\'' + row.password + '\')">无法获取密码，请点击<span style="color:red">改密</span>重置密码!</span>'
            return true
          }
        },
        bt.public.get_quota_config('database'),
        {
          fid: 'backup',
          title: '备份',
          width: 130,
          template: function (row) {
            var backup = '点击备份',
                _class = "bt_warning";
            if (row.backup_count > 0) backup = lan.database.backup_ok, _class = "bt_success";
            return '<span><a href="javascript:;" class="btlink ' + _class + '" onclick="database.database_detail(' + row.id + ',\'' + row.name + '\',\'' + row.db_type + '\')">' + backup + (row.backup_count > 0 ? ('(' + row.backup_count + ')') : '') + '</a> | ' +
                '<a href="javascript:database.input_database(\'' + row.name + '\')" class="btlink">' + lan.database.input + '</a></span>';
          }
        },
        {
          title:'数据库位置',
          type: 'text',
          width: 116,
          template: function (row) {
            var type_column = '-'
            switch(row.db_type){
              case 0:
                type_column = '本地数据库'
                break;
              case 1:
                type_column = ('远程库('+row.conn_config.db_host+':'+row.conn_config.db_port+')').toString()
                break;
              case 2:
                $.each(cloudDatabaseList,function(index,item){
                  if(row.sid == item.id){
                    if(item.ps !== ''){ // 默认显示备注
                      type_column = item.ps
                    }else{
                      type_column = ('远程服务器('+item.db_host+':'+item.db_port+')').toString()
                    }
                  }
                })
                break;
            }
            return '<span class="flex" style="width:100px" title="'+type_column+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+type_column+'</span></span>'
          }
        },
        {
          fid: 'ps',
          title: '备注',
          type: 'input',
          blur: function (row, index, ev) {
            bt.pub.set_data_ps({
              id: row.id,
              table: 'databases',
              ps: ev.target.value
            }, function (res) {
              layer.msg(res.msg, { icon: res.status ? 1 : 2 });
            });
          },
          keyup: function (row, index, ev) {
            if (ev.keyCode === 13) {
              $(this).blur();
            }
          }
        },
        {
          type: 'group',
          title: '操作',
          width: 220,
          align: 'right',
          group: [{
            title: '管理',
            tips: '数据库管理',
            hide:function(rows){return rows.db_type != 0},  // 远程数据库和远程服务器
            event: function (row) {
              bt.database.open_phpmyadmin(row.name, row.username, row.password);
            }
          }, {
            title: '权限',
            tips: '设置数据库权限',
            hide:function(rows){return rows.db_type == 1}, //远程数据库
            event: function (row) {
              bt.database.set_data_access(row.username);
            }
          }, {
            title: '工具',
            tips: 'MySQL优化修复工具',
            event: function (row) {
              database.rep_tools(row.name);
            }
          }, {
            title: '改密',
            tips: '修改数据库密码',
            hide:function(rows){return rows.db_type == 1},
            event: function (row) {
              database.set_data_pass(row.id, row.username, row.password);
            }
          }, {
            title: '删除',
            tips: '删除数据库',
            event: function (row) {
              database.del_database(row.id, row.name,row, function (res) {
                if (res.status) database_table.$refresh_table_list(true);
                layer.msg(res.msg, {
                  icon: res.status ? 1 : 2
                })
              });
            }
          }]
        }
      ],
      sortParam: function (data) {
        return {
          'order': data.name + ' ' + data.sort
        };
      },
      tootls: [{ // 按钮组
        type: 'group',
        positon: ['left', 'top'],
        list: [{
          title: '添加数据库',
          active: true,
          event: function () {
            var cloudList = []
            $.each(cloudDatabaseList,function(index,item){
              var _tips = item.ps != ''?(item.ps+' ('+item.db_host+')'):item.db_host
              cloudList.push({title:_tips,value:item.id})
            })
            bt.database.add_database(cloudList,function (res) {
              if (res.status) database_table.$refresh_table_list(true);
            })
          }
        }, {
          title: 'root密码',
          event: function () {
            bt.database.set_root('root')
          }
        }, {
          title: 'phpMyAdmin',
          event: function () {
            var url = $('#phpMyAdminUrl').data('url'),
                isEnable = url !== 'False';
            bt.open({
              type: 1,
              title:'phpMyAdmin访问安全提示',
              area:'450px',
              btn:false,
              content:'<div class="bt-form pd25">\
                <div class="rebt-con" style="width:100%;display: flex;padding:0;height:auto;justify-content: space-around;">\
                  <div class="rebt-li panel_visit" style="position:relative;width: 150px;height: 50px;line-height: 50px;">\
                    <a href="javascript:;" style="font-size:13px;border-radius:2px;">通过面板访问</a>\
                    <span class="recommend-pay-icon" style="height: 30px;width: 30px;background-size: contain;"></span>\
                  </div>\
                  <div class="rebt-li public_visit" style="position:relative;width: 150px;height: 50px;line-height: 50px;">\
                    <a href="javascript:;"  style="font-size:13px;border-radius:2px;">通过公共访问</a>\
                  </div>\
                </div>\
                <ul class="help-info-text c7"><li>面板访问需要登录面板后，才能通过面板访问phpMyAdmin</li>'+ (isEnable?
                      '<li class="color-red">关闭公共访问权限可提升安全性，可到软件商店-&gt;phpMyAdmin中关闭</li>':
                      '<li>未开启公共访问权限，可到软件商店-&gt;phpMyAdmin中开启</li><li class="color-red">注意：开启公共访问权限存在安全风险，建议非必要不启用</li>'
              ) + '</ul>\
              </div>',
              success:function (layers,indexs) {
                $('.close_layer').click(function () {
                  layer.close(indexs)
                })
                $('.panel_visit').click(function () {
                  bt.database.open_phpmyadmin('', 'root', bt.config.mysql_root)
                })
                $('.public_visit').click(function () {
                  if(isEnable){
                    window.open(url)
                  }else{
                    layer.msg('未开启公共访问权限')
                  }
                })
              }
            })
          }
        },
          {
            title:'远程服务器',
            event:function(){
              db_public_fn.get_cloud_server_list();
            }
          },{
            title:'企业增量备份',
            event:function(){
              database.get_backup();
            }
          },{
            title: '同步所有',
            style: {
              'margin-left': '30px'
            },
            event: function () {
              database.sync_to_database({
                type: 0,
                data: []
              }, function (res) {
                if (res.status) database_table.$refresh_table_list(true);
              })
            }
          }, {
            title: '从服务器获取',
            event: function () {
              var _list = [];
              $.each(cloudDatabaseList,function (index,item){
                var _tips = item.ps != ''?(item.ps+' (服务器地址:'+item.db_host+')'):item.db_host
                _list.push({title:_tips,value:item.id})
              })
              bt_tools.open({
                title:'选择数据库位置',
                area:'450px',
                btn: ['确认','取消'],
                skin: 'databaseCloudServer',
                content: {
                  'class':'pd20',
                  form:[{
                    label:'数据库位置',
                    group:{
                      type:'select',
                      name:'sid',
                      width:'260px',
                      list:_list
                    }
                  }]
                },
                success:function(layers){
                  $(layers).find('.layui-layer-content').css('overflow','inherit')
                },
                yes:function (form,layers,index){
                  bt.database.sync_database(form.sid,function (rdata) {
                    if (rdata.status){
                      database_table.$refresh_table_list(true);
                      layer.close(layers)
                    }
                  })
                }
              })
            }
          }, {
            title: '回收站',
            icon: 'trash',
            event: function () {
              bt.recycle_bin.open_recycle_bin(6)
            }
          }]
      }, {
        type: 'batch', //batch_btn
        positon: ['left', 'bottom'],
        placeholder: '请选择批量操作',
        buttonValue: '批量操作',
        disabledSelectValue: '请选择需要批量操作的数据库!',
        selectList: [{
          title: '同步选中',
          url: '/database?action=SyncToDatabases&type=1',
          paramName: 'ids', //列表参数名,可以为空
          paramId: 'id', // 需要传入批量的id
          th: '数据库名称',
          beforeRequest: function (list) {
            var arry = [];
            $.each(list, function (index, item) {
              arry.push(item.id);
            });
            return JSON.stringify(arry)
          },
          success: function (res, list, that) {
            layer.closeAll();
            var html = '';
            $.each(list, function (index, item) {
              html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (res.status ? '#20a53a' : 'red') + '">' + res.msg + '</span></div></td></tr>';
            });
            that.$batch_success_table({
              title: '批量同步选中',
              th: '数据库名称',
              html: html
            });
          }
        }, {
          title: "删除数据库",
          url: '/database?action=DeleteDatabase',
          load: true,
          param: function (row) {
            return {
              id: row.id,
              name: row.name
            }
          },
          callback: function (config) { // 手动执行,data参数包含所有选中的站点
            var ids = [];
            for (var i = 0; i < config.check_list.length; i++) {
              ids.push(config.check_list[i].id);
            }
            database.del_database(ids, function (param) {
              config.start_batch(param, function (list) {
                layer.closeAll()
                var html = '';
                for (var i = 0; i < list.length; i++) {
                  var item = list[i];
                  html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + item.request.msg + '</span></div></td></tr>';
                }
                database_table.$batch_success_table({
                  title: '批量删除',
                  th: '数据库名称',
                  html: html
                });
                database_table.$refresh_table_list(true);
              });
            })
          }
        }]
      }, {
        type: 'search',
        positon: ['right', 'top'],
        placeholder: '请输入数据库名称/备注',
        searchParam: 'search', //搜索请求字段，默认为 search
        value: '',// 当前内容,默认为空
      }, { //分页显示
        type: 'page',
        positon: ['right', 'bottom'], // 默认在右下角
        pageParam: 'p', //分页请求字段,默认为 : p
        page: 1, //当前分页 默认：1
        numberParam: 'limit', //分页数量请求字段默认为 : limit
        number: 20, //分页数量默认 : 20条
        numberList: [10, 20, 50, 100, 200], // 分页显示数量列表
        numberStatus: true, //　是否支持分页数量选择,默认禁用
        jump: true, //是否支持跳转分页,默认禁用
      }],
      success:function(config){
        //搜索前面新增数据库位置下拉
        if($('.database_type_select_filter').length == 0){
          var _option = '<option value="all">全部</option>'
          $.each(cloudDatabaseList,function(index,item){
            var _tips = item.ps != ''?item.ps:item.db_host
            _option +='<option value="'+item.id+'">'+_tips+'</option>'
          })
          $('#bt_database_table .bt_search').before('<select class="bt-input-text mr5 database_type_select_filter" style="width:110px" name="db_type_filter">'+_option+'</select>')

          //事件
          $('.database_type_select_filter').change(function(){
            database_table.$refresh_table_list(true);
          })
        }
      }
    });
  },
  // 同步所有
  sync_to_database: function (obj, callback) {
    bt.database.sync_to_database({
      type: obj.type,
      ids: JSON.stringify(obj.data)
    }, function (rdata) {
      if (callback) callback(rdata);
    });
  },
  // 同步数据库
  database_detail: function (id, dataname,db_type) {
    if(bt.data.db_tab_name == 'mysql'){
      var cloud_list = { //云存储列表名
        alioss: '阿里云OSS',
        ftp: 'FTP',
        sftp: 'SFTP',
        msonedrive: '微软OneDrive',
        qiniu: '七牛云',
        txcos: '腾讯COS',
        upyun: '又拍云',
        'Google Cloud': '谷歌云',
        'Google Drive': '谷歌网盘',
        bos: '百度云',
        obs: '华为云'
      };
      var web_tab = bt_tools.tab({
        class: 'pd20',
        type: 0,
        theme: { nav: 'ml0'},
        active: 1, //激活TAB下标
        list: [{
          title: '常规备份',
          name: 'conventionalBackup',
          content: '<div id="bt_backup_table"></div>',
          success: function () {
            var bt_backup_table = $('#bt_backup_table')
            bt_backup_table.html('')
            var backup_table = bt_tools.table({
              el: '#bt_backup_table',
              url: '/data?action=getData',
              param: { table: 'backup', search: id, type: '1', limit:5 },
              default: "[" + dataname + "] 数据库备份列表为空", //数据为空时的默认提示
              column: [
                { type: 'checkbox', class: '', width: 20 },
                { fid: 'name', title: '文件名称', width: 220, fixed: true },
                {
                  fid: 'storage_type',
                  title: '存储对象',
                  type: 'text',
                  width: 70,
                  template: function (row) {
                    var is_cloud = false, cloud_name = '' //当前云存储类型
                    if (row.filename.indexOf('|') != -1) {
                      var _path = row.filename;
                      is_cloud = true;
                      cloud_name = _path.match(/\|(.+)\|/, "$1")
                    } else {
                      is_cloud = false;
                    }
                    return is_cloud ? cloud_list[cloud_name[1]] : '本地'
                  }
                },
                {
                  fid: 'size',
                  title: '文件大小',
                  width: 80,
                  type: 'text',
                  template: function (row, index) {
                    return bt.format_size(row.size)
                  }
                },
                { fid: 'addtime', width: 150, title: '备份时间' },
                { fid: 'ps',
                  title: '备注',
                  type: 'input',
                  blur: function (row, index, ev, key, that) {
                    if (row.ps == ev.target.value) return false
                    bt.pub.set_data_ps({ id: row.id, table: 'backup', ps: ev.target.value }, function (res) {
                      bt_tools.msg(res, { is_dynamic: true })
                    })
                  },
                  keyup: function (row, index, ev) {
                    if (ev.keyCode === 13)  $(this).blur()
                  }
                },
                {
                  title: '操作',
                  type: 'group',
                  width: 140,
                  align: 'right',
                  group: [{
                    title: '恢复',
                    event: function (row, index, ev, key, that) {
                      var _id = row.id
                      num1 = bt.get_random_num(3, 15),
                          num2 = bt.get_random_num(5, 9),
                          taskID = 0,
                          taskStatus = 0, //0未开始  1正在下载   2下载完成
                          intervalTask = null;
                      // 根据id获取对象数据
                      var obj = that.data.filter(function (x) {
                        return x.id === _id
                      })
                      obj = obj[0] //由于filter返回数组所以取第一位
                      var _path = obj.filename,
                          cloud_name = _path.match(/\|(.+)\|/, "$1"),
                          isYun = _path.indexOf('|') != -1;
                      if (!isYun) {
                        bt.database.input_sql(_path, dataname)
                        return
                      }
                      layer.open({
                        type: 1,
                        title: "从云存储恢复",
                        area: ['500px', '350px'],
                        closeBtn: 2,
                        shadeClose: false,
                        skin: 'db_export_restore',
                        content: "<div style='padding: 20px 20px 0 20px;'>" +
                            "<div class='db_export_content'><ul>" +
                            "<li>此备份文件存储在云存储，需要通过以下步骤才能完成恢复：</li>" +
                            "<li class='db_export_txt'>" +
                            "<span>1</span>" +
                            "<div>" +
                            "<p>从[" + cloud_list[cloud_name[1]] + "]下载备份文件到服务器。</p>" +
                            "<p class='btlink'></p>" +
                            "</div>" +
                            "</li>" +
                            "<li class='db_export_txt2'>" +
                            "<span>2</span>" +
                            "<div>" +
                            "<p>恢复备份</p>" +
                            "<p class='btlink'></p>" +
                            "</div>" +
                            "</li>" +
                            "</ul>" +
                            "<p class='db_confirm_txt'style='color:red;margin-bottom: 10px;'>数据库将被覆盖，是否继续？</p>" +
                            "</div>" +
                            "<div class='db_export_vcode db_two_step' style='margin:0'>" + lan.bt.cal_msg + "" +
                            "<span class='text'>" + num1 + " + " + num2 + "</span>=<input type='number' id='vcodeResult' value=''>" +
                            "</div>" +
                            "<div class='bt-form-submit-btn'>" +
                            "<button type='button' class='btn btn-danger btn-sm db_cloud_close'>取消</button>" +
                            "<button type='button' class='btn btn-success btn-sm db_cloud_confirm'>确认</button></div>" +
                            "</div>",
                        success: function (layers, indexs) {
                          // 确认按钮
                          $('.db_export_restore').on('click', '.db_cloud_confirm', function () {
                            var vcodeResult = $('#vcodeResult');
                            if (vcodeResult.val() === '') {
                              layer.tips('计算结果不能为空', vcodeResult, {
                                tips: [1, 'red'],
                                time: 3000
                              })
                              vcodeResult.focus()
                              return false;
                            } else if (parseInt(vcodeResult.val()) !== (num1 + num2)) {
                              layer.tips('计算结果不正确', vcodeResult, {
                                tips: [1, 'red'],
                                time: 3000
                              })
                              vcodeResult.focus()
                              return false;
                            }
                            $('.db_two_step,.db_confirm_txt').remove(); //删除计算
                            $('.db_export_restore .db_export_content li:first').animate({
                              'margin-bottom': '35px'
                            }, 600);
                            $('.db_export_restore .db_cloud_confirm').addClass('hide'); //隐藏确认按钮
                            //请求云储存链接
                            $.post('/cloud', {
                              toserver: true,
                              filename: obj.filename,
                              name: obj.name
                            }, function (res) {
                              taskID = res.task_id
                              if (res.status === false) {
                                layer.msg(res.msg, {
                                  icon: 2
                                });
                                return false;
                              } else {
                                // 获取下载进度
                                function downloadDBFile () {
                                  $.post('/task?action=get_task_log_by_id', {
                                    id: res.task_id,
                                    task_type: 1
                                  }, function (task) {
                                    if (task.status == 1) {
                                      clearInterval(intervalTask)
                                      taskStatus = 2
                                      $('.db_export_txt p:eq(1)').html('下载完成!');
                                      $('.db_export_txt2 p:eq(1)').html('请稍等，正在恢复数据库 <img src="/static/img/ing.gif">');
                                      bt.send('InputSql', 'database/InputSql', {
                                        file: res.local_file,
                                        name: dataname
                                      }, function (rdata) {
                                        layer.close(indexs)
                                        bt.msg(rdata);
                                        console.log('11')
                                      })
                                    } else {
                                      taskStatus = 1;
                                      //更新下载进度
                                      $('.db_export_txt p:eq(1)').html('正在下载文件:已下载 ' + task.used + '/' + ToSize(task.total))
                                    }
                                  })
                                }
                                downloadDBFile();
                                intervalTask = setInterval(function () {
                                  downloadDBFile();
                                }, 1500);
                              }
                            })
                          })
                          // 取消按钮
                          $('.db_export_restore').on('click', '.db_cloud_close', function () {
                            switch (taskStatus) {
                              case 1:
                                layer.confirm('正在执行从云存储中下载，是否取消', {
                                  title: '下载取消'
                                }, function () {
                                  clearInterval(intervalTask) //取消轮询下载进度
                                  layer.close(indexs)
                                  database.cancel_cloud_restore(taskID)
                                })
                                break;
                              case 2:
                                layer.msg('数据正在恢复中，无法取消', {
                                  icon: 2
                                })
                                return false;
                            }
                          })
                        },
                        cancel: function (layers) {
                          switch (taskStatus) {
                            case 0:
                              layer.close(layers);
                              break;
                            case 1:
                              layer.confirm('正在执行从云存储中下载，是否取消', {
                                title: '下载取消'
                              }, function () {
                                clearInterval(intervalTask) //取消轮询下载进度
                                layer.close(layers)
                                database.cancel_cloud_restore(taskID)
                              }, function () {
                                return false;
                              })
                              break;
                            case 2:
                              layer.msg('数据正在恢复中，无法取消', {
                                icon: 2
                              })
                              return false;
                          }
                          return false;
                        }
                      })
                    }
                  },{
                    title: '下载',
                    template: function (row, index, ev, key, that) {
                      return '<a target="_blank" class="btlink" href="/download?filename=' + row.filename + '&amp;name=' + row.name + '">下载</a>'
                    }
                  }, {
                    title: '删除',
                    event: function (row, index, ev, key, that) {
                      that.del_site_backup({ name: row.name, id: row.id }, function (rdata) {
                        bt_tools.msg(rdata);
                        if (rdata.status) {
                          that.$refresh_table_list();
                          database_table.$refresh_table_list(true)
                        }
                      });
                    }
                  }]
                }
              ],
              methods: {
                /**
                 * @description 删除站点备份
                 * @param {object} config
                 * @param {function} callback
                 */
                del_site_backup: function (config, callback) {
                  bt.confirm({ title: '删除数据库备份', msg: '删除数据库备份[' + config.name + '],是否继续？' }, function () {
                    bt_tools.send('database/DelBackup', { id: config.id }, function (rdata) {
                      if (callback) callback(rdata)
                    }, true)
                  });
                }
              },
              success: function () {
                $('.bt_backup_table').css('top', (($(window).height() - $('.bt_backup_table').height()) / 2) + 'px')
              },
              tootls: [{ // 按钮组
                type: 'group',
                positon: ['left', 'top'],
                list: [{
                  title: '备份数据库',
                  active: true,
                  event: function (ev, that) {
                    bt.database.backup_data(id, function (rdata) {
                      bt_tools.msg(rdata);
                      if (rdata.status) {
                        that.$refresh_table_list();
                        database_table.$refresh_table_list(true)
                      }
                    });
                  }
                }]
              }, {
                type: 'batch',
                positon: ['left', 'bottom'],
                config: {
                  title: '删除',
                  url: '/site?action=DelBackup',
                  paramId: 'id',
                  load: true,
                  callback: function (that) {
                    bt.confirm({ title: '批量删除数据库备份', msg: '是否批量删除选中的数据库备份，是否继续？', icon: 0 }, function (index) {
                      layer.close(index);
                      that.start_batch({}, function (list) {
                        var html = '';
                        for (var i = 0; i < list.length; i++) {
                          var item = list[i];
                          html += '<tr><td><span class="text-overflow" title="' + item.name + '">' + item.name + '</span></td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + item.request.msg + '</span></div></td></tr>';
                        }
                        backup_table.$batch_success_table({ title: '批量删除数据库备份', th: '文件名', html: html })
                        backup_table.$refresh_table_list(true)
                        database_table.$refresh_table_list(true)
                      });
                    });
                  }
                } //分页显示
              }, {
                type: 'page',
                positon: ['right', 'bottom'], // 默认在右下角
                pageParam: 'p', //分页请求字段,默认为 : p
                page: 1, //当前分页 默认：1
                numberParam: 'limit',
                //分页数量请求字段默认为 : limit
                defaultNumber: 10
                //分页数量默认 : 20条
              }]
            })
          }
        }, {
          title: '增量备份',
          name: 'incrementalBackup',
          content: '<div id="bt_incbackup_table"></div>',
          success: function () {
            $('.bt_backup_table .tab-block.on').css('width','100%')
            bt_tools.send({url:'project/binlog/get_binlog_status'}, function (res) {
              if (res.status) {
                var bt_incbackup_table = $('#bt_incbackup_table')
                bt_incbackup_table.html('')
                var alltablesname = [], arry = []
                getTables(dataname,true)
                function getTables(res,flag){
                  alltablesname = [],arry = []
                  //获取指定数据库表名
                  bt_tools.send({url:'project/binlog/get_tables',data: {db_name:res}}, function (res) {
                    if (res.length == 0) {
                      alltablesname = [{title:'当前数据库下没有表',value:''}]
                      arry = alltablesname
                    }else{
                      for (var i = 0; i < res.length; i++) {
                          alltablesname.push(res[i])
                      }
                      $.each(alltablesname,function(index,item){
                        arry.push({ title: item.name+(item.cron_id == null || item.cron_id.length == 0 ? ' [无备份任务]':''), value: item.name })
                      })
                    }
                    if (flag) {
                      table('all')
                    }
                  })
                }
                function table(typename) {
                  var backup_table = bt_tools.table({
                    el: '#bt_incbackup_table',
                    url: 'project/binlog/get_specified_database_info',
                    param: { datab_name : dataname,type : typename },
                    load: true,
                    default: "[" + dataname + "] 数据库增量备份列表为空", //数据为空时的默认提示
                    column: [
                      { fid: 'excute_time', title: '备份时间', type: 'text',width: '150px' },
                      { fid: 'type', title: '类型', type: 'text',width: '75px',
                        template: function (row) {
                          if (row.type === "databases") return '<span>数据库<span>';
                          return '<span>表</span>'
                        }
                      },
                      { fid: 'name', title: '名称', type: 'text' },
                      { fid: 'full_size', title: '备份大小', type: 'text',width: '120px' },
                      { 
                        title: '备份计划任务', 
                        width: 100, 
                        type: 'text',
                        template: function (row){
                          return (row.cron_id == [] || row.cron_id.length == 0 ? '<span class="color-red cursor-pointer">丢失</span>' : '<span>正常</span>')
                        },
                        event: function (row, index, ev, key, that) {
                          if(row.cron_id == [] || row.cron_id.length == 0){
                            bt.confirm({
                              title: '恢复备份计划任务',
                              msg: '该备份计划任务不存在，是否恢复备份计划任务'
                            }, function () {
                              var params = {
                                cron_type : 'hour-n',
                                backup_type : row.type,
                                backup_cycle: row.backup_cycle,
                                datab_name : dataname,
                                backup_id : row.backup_id,
                                notice: row.notice,
                                notice_channel : row.notice_channel,
                                upload_localhost : row.upload_localhost,
                                upload_alioss : row.upload_alioss,
                                upload_txcos : row.upload_txcos,
                                upload_qiniu : row.upload_qiniu,
                                upload_obs : row.upload_obs,
                                upload_bos : row.upload_bos
                              }
                              bt_tools.send({url:'project/binlog/modify_mysqlbinlog_backup_setting',data: params}, function (res) {
                                bt_tools.msg(res)
                                if (res.status) {
                                  that.$refresh_table_list();
                                  database_table.$refresh_table_list(true)
                                }
                              },'恢复计划任务')
                            })
                          }
                        } 
                      },
                      {
                        title: '操作',
                        type: 'group',
                        align: 'right',
                        width: 270,
                        group: [
                          {
                            title: '执行',
                            hide: function (row) {
                              return (row.cron_id == [] || row.cron_id.length == 0 ? true : false)
                            },
                            event: function (row, index, ev, key, that) {
                              database.startCrontabTask({ id: row.cron_id }, function () {
                                that.$refresh_table_list();
                                database_table.$refresh_table_list(true)
                              })
                            }
                          },
                          {
                            title: '编辑',
                            hide: function (row) {
                              return (row.cron_id == [] || row.cron_id.length == 0 ? true : false)
                            },
                            event: function (row, index, ev, key, that) {
                              var editBackup = null;
                              layer.open({
                                type: 1,
                                title:'编辑'+(row.type === 'databases' ? '数据库' : '表')+'['+row.name+']增量备份',
                                closeBtn: 2,
                                shadeClose: false,
                                area:'550px',
                                btn: ['提交','取消'],
                                skin: 'addDbbackup',
                                content: '<div id="addDbbackup"></div>',
                                success: function (layers, indexs) {
                                  var mulpValues = [],mulpTitles = []
                                  for (var i = 0; i < database.backuptoList.length; i++) {
                                    if(row['upload_'+database.backuptoList[i].value] == "") continue
                                    mulpValues.push(row['upload_'+database.backuptoList[i].value])
                                    mulpTitles.push(database.backuptoList[i].title)
                                  }
                                  editBackup = bt_tools.form({
                                    el: '#addDbbackup',
                                    data: row,
                                    class: 'pd15',
                                    form: [
                                      {
                                        label: '数据备份到',
                                        group: {
                                          type: 'multipleSelect',
                                          name: 'upload_alioss',
                                          width: '390px',
                                          value: mulpValues,
                                          list: database.backuptoList
                                        }
                                      },
                                      {
                                        label: '压缩密码',
                                        group: {
                                          type: 'text',
                                          disabled: true,
                                          name: 'zip_password',
                                          width: '390px',
                                          value: row.zip_password,
                                        }
                                      },
                                      {
                                        label: '备份周期',
                                        group: [
                                          {
                                            type: 'number',
                                            name: 'backup_cycle',
                                            'class': 'group_span',
                                            width: '346px',
                                            value: row.backup_cycle,
                                            unit: '小时',
                                            min: 0,
                                            max: 23
                                          }
                                        ]
                                      },
                                      {
                                        label: '备份提醒',
                                        group: [{
                                          type: 'select',
                                          name: 'notice',
                                          value: parseInt(row.notice),
                                          list: [
                                            { title: '不接收任何消息通知', value: 0 },
                                            { title: '任务执行失败接收通知', value: 1 }
                                          ],
                                          change: function (formData, element, that) {
                                            that.config.form[3].group[1].display = formData.notice == 0 ? false : true
                                            that.config.form[3].group[0].value = parseInt(formData.notice)
                                            that.$replace_render_content(3)
                                          }
                                        }, {
                                          label: '消息通道',
                                          type: 'select',
                                          name: 'notice_channel',
                                          display: parseInt(row.notice) == 0 ? false : true,
                                          value: row.notice_channel,
                                          width: '100px',
                                          placeholder: '未配置消息通道',
                                          list: {
                                            url: '/config?action=get_msg_configs',
                                            dataFilter: function (res, that) {
                                              return database.pushChannelMessage.getChannelSwitch(res, 'enterpriseBackup')
                                            },success: function (res, that, config, list) {
                                              if(!config.group[1].value && config.group[0].value == 1){
                                                config.group[1].value = list[0].value
                                              }
                                            }
                                          }
                                        }, {
                                          type: 'link',
                                          'class': 'mr5',
                                          title: '设置消息通道',
                                          event: function (formData, element, that) {
                                            open_three_channel_auth();
                                          }
                                        }]
                                      }
                                    ]
                                  })
                                },
                                yes: function (indexs) {
                                  var formData = editBackup.$get_form_value()
                                  if(formData.backup_cycle == '') return layer.msg("备份周期不能为空！")
                                  if(formData.backup_cycle < 0) return layer.msg("备份周期不能小于0！")
                                  if(formData.notice == 1) {
                                    if (formData.notice_channel == undefined) return layer.msg("请设置消息通道")
                                  }
                                  formData['cron_type'] = 'hour-n'
                                  formData['backup_type'] = row.type
                                  formData['datab_name'] = dataname
                                  formData['cron_id'] = row.cron_id
                                  formData['backup_id'] = row.backup_id
                                  formData['notice_channel'] = formData.notice == 0 ? '' : formData.notice_channel
                                  var multipleValues = $('select[name=upload_alioss]').val()
                                  if(multipleValues == null) return layer.msg('请最少选择一个备份类型')
                                  formData['upload_localhost'] = multipleValues.indexOf('localhost') > -1 ? 'localhost' : ''
                                  formData['upload_alioss'] = multipleValues.indexOf('alioss') > -1 ? 'alioss' : '',
                                  formData['upload_txcos'] = multipleValues.indexOf('txcos') > -1 ? 'txcos' : '',
                                  formData['upload_qiniu'] = multipleValues.indexOf('qiniu') > -1 ? 'qiniu' : '',
                                  formData['upload_obs'] = multipleValues.indexOf('obs') > -1 ? 'obs' : '',
                                  formData['upload_bos'] = multipleValues.indexOf('bos') > -1 ? 'bos' : '',
                                  delete formData['zip_password']
                                  //编辑
                                  bt_tools.send({url:'project/binlog/modify_mysqlbinlog_backup_setting',data: formData}, function (res) {
                                    bt_tools.msg(res)
                                    if (res.status) {
                                      layer.close(indexs)
                                      that.$refresh_table_list();
                                      database_table.$refresh_table_list(true)
                                    }
                                  },'编辑备份任务')
                                }
                              })
                            }
                          },{
                            title: '日志',
                            hide: function (row) {
                              return (row.cron_id == [] || row.cron_id.length == 0 ? true : false)
                            },
                            event: function (row, index, ev, key, that) {
                              database.backupLogs({ id: row.cron_id }, index, ev, key, that)
                            }
                          },
                          {
                            title: '恢复',
                            event: function (row, index, ev, key, that) {
                              that.resume_download_backup({ gp_type : 0,type : row.type,title:'恢复',backup_id: row.backup_id,datab_name: row.name,start_time: row.start_time,end_time: row.end_time})
                            }
                          },{
                            title: '下载',
                            event: function (row, index, ev, key, that) {
                              that.resume_download_backup({ gp_type : 1,type : row.type,title:'下载',backup_id: row.backup_id,datab_name: row.name,start_time: row.start_time,end_time: row.end_time})
                            }
                          }, {
                            title: '删除',
                            event: function (row, index, ev, key, that) {
                              that.del_database_backup({ name: row.name, cron_id: row.cron_id,backup_id: row.backup_id }, function (rdata) {
                                bt_tools.msg(rdata);
                                if (rdata.status) {
                                  that.$refresh_table_list();
                                  database_table.$refresh_table_list(true)
                                  getTables(dataname,false)
                                }
                              });
                            }
                          }]
                      }
                    ],
                    methods: {
                      /**
                       * @description 恢复 下载
                       * @param {object} config
                       */
                      resume_download_backup: function (config) {
                        layer.open({
                          type: 1,
                          title:config.title+(config.type === "databases" ? '数据库':'表' )+'【'+config.datab_name+'】数据',
                          closeBtn: 2,
                          shadeClose: false,
                          area:['350px',config.backup_id == null ? '220px':'170px'],
                          skin: 'restore',
                          content: '<div id="restore" class="bt-form pd15">\
                          <div class="line" style="display: '+(config.backup_id == null ? "block":"none")+'">\
                            <span class="tname">解压密码</span>\
                            <div class="info-r">\
                              <input type="text" placeholder="请输入压缩密码" class="bt-input-text mr5 showPwd" name="zip_password" />\
                            </div>\
                          </div>\
                          <div class="line">\
                            <span class="tname">'+ config.title +'截止时间</span>\
                            <div class="info-r">\
                              <input id="calendar" type="text" class="bt-input-text mr5" name="calendar" placeholder="请输入'+ config.title +'截止时间" readOnly />\
                            </div>\
                          </div>\
                        </div>',
                          btn: ['确定'+config.title, '关闭'],
                          success: function (){
                            laydate.render({
                              elem: '#calendar'
                              ,show: true //直接显示
                              ,closeStop: '#test1'
                              ,theme: '#20a53a'
                              ,trigger: 'click' //采用click弹出
                              ,min: config.start_time,
                              max: config.end_time,
                              vlue: bt.get_date(365),
                              type: 'datetime',
                              format: 'yyyy-MM-dd HH:mm:ss',
                              btns: ['clear','confirm']
                            });
                          },
                          yes: function (indexs) {
                            var url = '',title = ''
                            var params = {
                              end_time : $('input[name=calendar]').val()
                            }
                            if(params.end_time == '') return layer.msg("截止时间不能为空")
                            if(config.backup_id == null){
                              if($('input[name=zip_password]').val() == ''){
                                return layer.msg("解压密码不能为空")
                              }else{
                                params['zip_password'] = $('input[name=zip_password]').val()
                              }
                            }
                            params['datab_name'] = dataname
                            if (config.type == 'tables') {
                              params['table_name'] = config.datab_name
                            }
                            if (config.gp_type == 0){//恢复
                              url = 'project/binlog/restore_to_database'
                              params['backup_id'] = config.backup_id
                              title = '恢复备份任务'
                            }else {//下载
                              params['backup_type'] =  config.type == 'databases' ? 'databases' : 'tables'
                              url = 'project/binlog/export_data'
                              title = '下载备份任务'
                            }
                            bt_tools.send({url:url ,data:  params}, function (res) {
                              if (config.gp_type == 0) {
                                layer.msg(res.msg, {icon: res.status ? 1:2})
                                if(res.status) layer.close(indexs)
                              }else{
                                if (typeof res.name == "undefined") {
                                  if (!res.status) {
                                    layer.msg(res.msg, {icon: 2})
                                  }
                                }else{
                                  layer.close(indexs)
                                  window.location.href = '/download?filename='+res.name
                                }
                              }
                            },title)
                          }
                        })
                      },
                      /**
                       * @description 删除站点备份
                       * @param {object} config
                       * @param {function} callback
                       */
                      del_database_backup: function (config, callback) {
                        bt.prompt_confirm("删除备份任务","删除备份任务[" + config.name + "]，删除此任务会连备份数据一起删除,是否继续？",function () {
                          bt_tools.send({url:'project/binlog/delete_mysql_binlog_setting',data: {cron_id:config.cron_id,backup_id:config.backup_id,type:'manager'}}, function (rdata) {
                            if (callback) callback(rdata)
                          }, '删除备份任务')
                        })
                      }
                    },
                    tootls: [{ // 按钮组
                      type: 'group',
                      positon: ['left', 'top'],
                      list: [{
                        title: '添加备份任务',
                        active: true,
                        event: function (ev, that) {
                          var addDBbackup = null;
                          layer.open({
                            type: 1,
                            title:'添加备份任务',
                            closeBtn: 2,
                            shadeClose: false,
                            area:'550px',
                            btn: ['提交','取消'],
                            skin: 'addDbbackup',
                            content: '<div id="addDbbackup"></div>',
                            success: function (layers, indexs) {
                              addDBbackup = bt_tools.form({
                                el: '#addDbbackup',
                                class: 'pd15',
                                form: [
                                  {
                                    label: '数据库名称',
                                    group: {
                                      type: 'text',
                                      disabled: true,
                                      name: 'datab_name',
                                      width: '390px',
                                      value: dataname
                                    }
                                  },
                                  {
                                    label: '选择类型',
                                    group: {
                                      type: 'select',
                                      name: 'backup_type',
                                      width: '390px',
                                      list: [
                                        { title:'数据库',value:'databases'},
                                        { title:'表',value:'tables'}
                                      ],
                                      change: function (formData, element, that) {
                                        if (formData.backup_type == 'tables') {
                                          that.config.form[2].hide = false
                                        }else{
                                          that.config.form[2].hide = true
                                        }
                                        that.$replace_render_content(2)
                                      }
                                    }
                                  },
                                  {
                                    label: '选择表',
                                    hide: true,
                                    group: {
                                      type: 'select',
                                      name: 'table_name',
                                      width: '390px',
                                      list: arry,
                                      change: function (formData, element, that) {
                                        that.$replace_render_content(2)
                                      }
                                    }
                                  },
                                  {
                                    label: '数据备份到',
                                    group: {
                                      type: 'multipleSelect',
                                      name: 'upload_alioss',
                                      width: '390px',
                                      list: database.backuptoList
                                    }
                                  },
                                  {
                                    label: '压缩密码',
                                    group: {
                                      type: 'text',
                                      name: 'zip_password',
                                      width: '390px',
                                      placeholder: '请输入压缩密码',
                                      unit: '<span class="glyphicon glyphicon-repeat cursor mr5"></span>'
                                    }
                                  },
                                  {
                                    label: '备份周期',
                                    group: [
                                      {
                                        type: 'number',
                                        name: 'backup_cycle',
                                        'class': 'group_span',
                                        width: '346px',
                                        value: '3',
                                        unit: '小时',
                                        min: 0,
                                        max: 23
                                      }
                                    ]
                                  },
                                  {
                                    label: '备份提醒',
                                    group: [{
                                      type: 'select',
                                      name: 'notice',
                                      value: 0,
                                      list: [
                                        { title: '不接收任何消息通知', value: 0 },
                                        { title: '任务执行失败接收通知', value: 1 }
                                      ],
                                      change: function (formData, element, that) {
                                        that.config.form[6].group[1].display = formData.notice == 0 ? false : true
                                        that.config.form[6].group[0].value = parseInt(formData.notice)
                                        that.$replace_render_content(6)
                                      }
                                    }, {
                                      label: '消息通道',
                                      type: 'select',
                                      name: 'notice_channel',
                                      display: false,
                                      width: '100px',
                                      placeholder: '未配置消息通道',
                                      list: {
                                        url: '/config?action=get_msg_configs',
                                        dataFilter: function (res, that) {
                                          return database.pushChannelMessage.getChannelSwitch(res, 'enterpriseBackup')
                                        }
                                      }
                                    }, {
                                      type: 'link',
                                      'class': 'mr5',
                                      title: '设置消息通道',
                                      event: function (formData, element, that) {
                                        open_three_channel_auth();
                                      }
                                    }]
                                  }
                                ]
                              })
                              $('#addDbbackup .pd15').append("<ul class='help-info-text c7 mlr20'>\
                                <li style='color:red;'>注意：请牢记压缩密码，以免因压缩密码导致无法恢复和下载数据</li>\
                            </ul>");
                              $('#addDbbackup .unit .glyphicon-repeat').click(function (){
                                $('#addDbbackup input[name=zip_password]').val(bt.get_random(bt.get_random_num(6,10)))
                              })
                              $('#addDbbackup .unit .glyphicon-repeat').click()
                            },
                            yes: function (indexs) {
                              var formData = addDBbackup.$get_form_value()
                              if(formData.backup_cycle == '') return layer.msg("备份周期不能为空！")
                              if(formData.backup_cycle < 0) return layer.msg("备份周期不能小于0！")
                              if(formData.backup_type == 'tables'){
                                if(formData.table_name == '0') return layer.msg("当前数据库下没有表，不能添加")
                              }else{
                                delete formData['table_name']
                              }
                              if(formData.notice == 1) {
                                if (formData.notice_channel == undefined) return layer.msg("请设置消息通道")
                              }
                              formData['cron_type'] = 'hour-n'
                              var multipleValues = $('select[name=upload_alioss]').val()
                              if(multipleValues == null) return layer.msg('请最少选择一个备份类型')
                              formData['upload_localhost'] = multipleValues.indexOf('localhost') > -1 ? 'localhost' : ''
                              formData['upload_alioss'] = multipleValues.indexOf('alioss') > -1 ? 'alioss' : '',
                              formData['upload_txcos'] = multipleValues.indexOf('txcos') > -1 ? 'txcos' : '',
                              formData['upload_qiniu'] = multipleValues.indexOf('qiniu') > -1 ? 'qiniu' : '',
                              formData['upload_obs'] = multipleValues.indexOf('obs') > -1 ? 'obs' : '',
                              formData['upload_bos'] = multipleValues.indexOf('bos') > -1 ? 'bos' : '',
                              formData['notice_channel'] = formData.notice == 0 ? '' : formData.notice_channel
                              //添加
                              bt_tools.send({url:'project/binlog/add_mysqlbinlog_backup_setting', data: formData}, function (res) {
                                bt_tools.msg(res)
                                if (res.status) {
                                  layer.close(indexs)
                                  that.$refresh_table_list();
                                  database_table.$refresh_table_list(true)
                                  getTables(dataname,false)
                                }
                              }, '添加备份任务')
                            }
                          })

                        }
                      }]
                    },
                      //分页显示
                      {
                        type: 'page',
                        positon: ['right', 'bottom'], // 默认在右下角
                        pageParam: 'p', //分页请求字段,默认为 : p
                        page: 1, //当前分页 默认：1
                      }]
                  })
                  $('#bt_incbackup_table .tootls_top .pull-right').append('<div class="searchTypeName"><div>')
                  var form_datas = []
                  bt_tools.form({
                    el: '.searchTypeName',
                    form: [
                      {
                        label: ' ',
                        group: {
                          type: 'select',
                          name: 'typeName',
                          width: '110px',
                          value: typename,
                          list: [
                            {
                              title: '全部',
                              value: 'all'
                            }, {
                              title: '数据库',
                              value: 'databases'
                            }, {
                              title: '表',
                              value: 'tables'
                            }
                          ],
                          change: function (formData, element, that) {
                            $('#bt_incbackup_table').html('')
                            table(formData.typeName)
                          }
                        }
                      }
                    ]
                  })
                  var backupType = $('#bt_incbackup_table .select_backup_type'),
                      backupTypeOption = $('#bt_incbackup_table .select_backup_type option')
                  for (var i = 0; i < backupTypeOption.length; i++) {
                    if (backupTypeOption[i].value == typename) {
                      backupTypeOption.eq(i).prop('selected',true)
                    }
                  }
                  backupType.change(function () {
                    $('#bt_incbackup_table').html('')
                    table(backupType.val())
                  })
                  $('#bt_incbackup_table .tootls_group.tootls_top .pull-left').append('<div class="inlineBlock ml5"><span class="glyphicon glyphicon-alert" style="color: #f39c12; margin-right: 10px;"></span>【使用提醒】此功能为企业版专享功能，当前所有用户可免费使用。</div>')
                  $('#bt_incbackup_table').append("<ul class='help-info-text c7'>\
                    <li>备份大小：备份大小包含完全备份数据大小和增量备份数据大小</li>\
                    <li>备份会保留一个星期的备份数据，当备份时，检测到完全备份为一个星期前，会重新完全备份</li>\
                    <li>请勿同一时间添加多个备份任务，否则可能因同一时间执行多个备份任务导致文件句柄数打开过多或者爆内存</li>\
                </ul>");
                }
              }else{
                layer.msg('请检查数据库是否正常运行或二进制日志是否开启！', { time: 0, shadeClose: true, shade: .3 });
              }
            },'检测是否开启二进制日志')
          }
        }]
      });
      bt_tools.open({
        area: '880px',
        title: '备份数据库&nbsp;-&nbsp;[&nbsp;' + dataname + '&nbsp;]',
        btn: false,
        skin: 'bt_backup_table',
        content: web_tab.$reader_content(),
        success:function () {
          web_tab.$init();
          $('.bt_backup_table .tab-nav span').eq(1).click(function () {
            if(db_type != 0){
              $('.bt_backup_table .tab-nav span').eq(0).click()
              layer.msg('不支持远程数据库')
              return false
            }
          })
        }
      });
    }else{
      var loadT = bt.load(lan.public.the_get);
      bt.pub.get_data('table=backup&search=' + id + '&limit=5&type=1&tojs=database.database_detail&p=1', function (frdata) {
        loadT.close();
        frdata.page = frdata.page.replace(/'/g, '"').replace(/database.database_detail\(/g, "database.database_detail(" + id + ",'" + dataname + "',");
        if ($('#DataBackupList').length <= 0) {
          bt.open({
            type: 1,
            skin: 'demo-class',
            area: '700px',
            title: lan.database.backup_title,
            closeBtn: 2,
            shift: 5,
            shadeClose: false,
            content: "<div class='divtable pd15 style='padding-bottom: 0'><button id='btn_data_backup' class='btn btn-success btn-sm' type='button' style='margin-bottom:10px'>" + lan.database.backup + "</button><table width='100%' id='DataBackupList' class='table table-hover'></table><div class='page databackup_page'></div></div>"
          });
        }
        setTimeout(function () {
          $('.databackup_page').html(frdata.page);
          bt.render({
            table: '#DataBackupList',
            columns: [
              { field: 'name', title: '文件名称' , templet: function (item) {
                  var _arry = item.name.split('/');
                  return _arry[_arry.length-1];
                }},
              {
                field: 'size', title: '文件大小', templet: function (item) {
                  return bt.format_size(item.size);
                }
              },
              { field: 'addtime', title: '备份时间' },
              {
                field: 'opt', title: '操作', align: 'right', templet: function (item) {
                  var _opt = '<a class="btlink" herf="javascrpit:;" onclick="bt.database.input_sql(\'' + item.filename + '\',\'' + dataname + '\')">恢复</a> | ';
                  _opt += '<a class="btlink" href="/download?filename=' + item.filename + '&amp;name=' + item.name + '" target="_blank">下载</a> | ';
                  _opt += '<a class="btlink" herf="javascrpit:;" onclick="bt.database.del_backup(\'' + item.id + '\',\'' + id + '\',\'' + dataname + '\')">删除</a>'
                  return _opt;
                }
              },
            ],
            data: frdata.data
          });
          $('#btn_data_backup').unbind('click').click(function () {
            bt.database.backup_data(id, function (rdata) {
              if (rdata.status) {
                database.database_detail(id, dataname);
                database_table.$refresh_table_list(true);
              }
            })
          })
        }, 100)
      });
    }
  },
  /**
 * @description 日志
 * @param {object} 
 */
backupLogs: function (row, index, ev, key, that) {
  var _that = this
  _that.getCrontabLogs(row, function (rdata) {
    layer.open({
      type: 1,
      title: lan.crontab.task_log_title,
      area: ['700px', '490px'],
      shadeClose: false,
      closeBtn: 2,
      content: '<div class="setchmod bt-form">\
          <pre class="crontab-log" style="overflow: auto; border: 0 none; line-height:23px;padding: 15px; margin: 0;white-space: pre-wrap; height: 405px; background-color: rgb(51,51,51);color:#f1f1f1;border-radius:0;"></pre>\
            <div class="bt-form-submit-btn" style="margin-top: 0">\
            <button type="button" class="btn btn-danger btn-sm btn-title" id="clearLogs" style="margin-right:15px;">'+ lan['public']['empty'] + '</button>\
            <button type="button" class="btn btn-success btn-sm btn-title">'+ lan['public']['close'] + '</button>\
          </div>\
        </div>',
      success: function (layers, index) {
        var log_body = rdata.msg === '' ? '当前日志为空' : rdata.msg, setchmod = $(".setchmod pre"), crontab_log = $('.crontab-log')[0]
        setchmod.text(log_body);
        crontab_log.scrollTop = crontab_log.scrollHeight;
        $('#clearLogs').on('click', function () {
          _that.clearCrontabLogs(row, function () {
            setchmod.text('')
          })
        })
        $('.setchmod .bt-form-submit-btn .btn-success').click(function(){
          layer.close(index)
        })
      }
    })
  })
},
  /**
 * @description 执行备份任务
 * @param {object} param 参数对象
 * @param {function} callback 回调函数
 */
   startCrontabTask: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=StartTask',
      data: param
    }, function (res) {
      bt.msg(res)
      if (res.status && callback) callback(res)
    }, '执行备份任务');
  },
  /**
   * @description 获取执行日志
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  getCrontabLogs: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=GetLogs',
      data: param
    }, function (res) {
      if (res.status) {
        if (callback) callback(res)
      } else {
        bt.msg(res)
      }
    }, '获取执行日志');
  },
  /**
   * @description 清空执行日志
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  clearCrontabLogs: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=DelLogs',
      data: param
    }, function (res) {
      bt.msg(res)
      if (res.status && callback) callback(res)
    }, '清空执行日志');
  },
  /**
   * @descripttion 消息推送下拉
   */
  pushChannelMessage:{
    //获取通道状态
    getChannelSwitch:function(data,type) {
      var arry = [{title: '全部通道', value: ''}], info = [];
      for (var resKey in data) {
        if (data.hasOwnProperty(resKey)) {
          var value = resKey, item = data[resKey]
          if (!item['setup'] || $.isEmptyObject(item['data'])) continue
          info.push(value)
          arry.push({title: item.title, value: value})
        }
      }
      arry[0].value = info.join(',');
      if (type === 'webshell') arry.shift();
      if (arry.length === (type === 'webshell' ? 0 : 1)) return []
      return arry
    }
  },
  // 备份导入》本地导入
  upload_files: function (name) {
    var path = bt.get_cookie('backup_path') + "/database/";
    bt_upload_file.open(path, '.sql,.zip,.bak', lan.database.input_up_type, function () {
      database.input_database(name);
    });
  },
  //备份数据库
  backupList: function (type) {
    var _that = this
    $('#webedit-con-database').html('<div id="dbbackup_list"></div>');
    var arry1 = [],arry = [];
    var url = '' ,params = {},alldbname = [],alltablesname = []
    var search = {}
    dataBaseName(true)
    function dataBaseName(flag) {
      database.databaseName = [],alldbname = [],arry1 = []
      bt_tools.send({url:'project/binlog/get_databases'}, function (res) {
        if (res.length == 0) {
          database.databaseName = [{title: '当前没有数据库',value: ''}]
          arry1 = database.databaseName
        }else{
          database.databaseName = res
          for (var i = 0; i < database.databaseName.length; i++) {
            alldbname.push(database.databaseName[i])
          }
          $.each(alldbname,function(index,item){
            arry1.push({ title: item.name + (item.cron_id == null || item.cron_id.length == 0 ? ' [无备份任务]':''), value: item.name })
          })
        }
        if (type === 1 && database.databaseName.length > 0) getTables(database.databaseName[0].name)
        if (flag) {
          if (type === 0) {
            url = 'project/binlog/get_databases_info'
            table()
          } else {
            if(database.databaseName.length == 0) {
              $('.databaseBackup .database-menu p:eq(0)').click()
              return layer.msg('当前没有数据库，不可查看备份表')
            }
            refresh(database.databaseName[0].name)
          }
        }
      })
    }
    function refresh(res) {
      url = 'project/binlog/get_specified_database_info'
      params = { datab_name: res, type: 'tables'}
      if (type == 1) {
        search ={
          type: 'search',
          positon: ['right', 'top'],
          placeholder: '请输入数据库名称',
          searchParam: 'datab_name', //搜索请求字段，默认为 search
          value: res,// 当前内容,默认为空
        }
      }
      table()
      var selectDbList = []
      for (var i = 0; i < database.databaseName.length; i++) {
        selectDbList.push({title: database.databaseName[i].name+' '+ (database.databaseName[i].cron_id == null ? '[无备份任务]':''),value: database.databaseName[i].name})
      }
      $('#dbbackup_list .tootls_group.tootls_top .pull-right').prepend('\
      <div class="selects_conter">\
        <span class="select_text">数据库</span>\
        <div class="select_conter">\
        <span style="display: none;" class="database_hide_value"></span>\
        <input type="text" placeholder="请选择" autocomplete="off" class="inbox_input database_input"\
            name="inbox_input" style="border: none;" value="'+ res +'">\
        <ul class="database_list" id="database_select_list"></ul>\
        <span class="select_down"></span>\
      </div>\
      ')
      $('.select_conter input').on('focus', function (e) {
        var _that = $(this),
            database_list = $(this).next(),
            _list = database_list.find('li'),
            database_default = $(this).prev(),
            html = '';
        _list.siblings().removeClass('active')
        for (var i = 0; i < database.databaseName.length; i++) {
          var item = database.databaseName[i]
          html += '<li '+ (_that.val() == item.name ? 'class="active"': '') + '>'+ item.name + '</li>'
        }
        $('.database_list').html(html)
        database_list.width($(this)[0].clientWidth).show();
        $(document).unbind('click').on('click', function (ev) {
          if (ev.target.className.indexOf('inbox_input') == -1) {
            if (_that.val() == '' || _that.val() != database_default.text()) {
              _that.val(database_default.text())
            }
            database_list.hide();
          }
          ev.stopPropagation();
        });
        return false;
      })
      $('.select_conter input').on('input', function (e) {
        var html = '',_that = $(this)
        for (var i = 0; i < database.databaseName.length; i++) {
          var item = database.databaseName[i]
          if (_that.val() != '') {
            if (item.name.indexOf(_that.val()) > -1) {
              html += '<li '+ (_that.val() == item.name ? 'class="active"': '') + '>'+ item.name + '</li>'
            }else{
              html += ''
            }
          }else{
            html += '<li>' + item.name + '</li>'
          }
          $('.database_list').html(html)
        }
      })
      $('.select_conter input').on('keydown', function (e) {
        if (e.keyCode == 13) {
          $('#dbbackup_list').html('');
          refresh($(this).val())
        }
      })
      $('.select_conter').on('click', 'li', function (e) {
        var item_val = $(this).text(),
            input = $(this).parent().prev();
        $(this).addClass('active').siblings().removeClass('active').parent().hide();
        $(this).parent().siblings(".database_hide_value").html(item_val);
        $(this).parent().siblings(".database_input").text(item_val);
        $('#dbbackup_list').html('');
        refresh(item_val)
        input.val(item_val);
      })
    }
    function getTables(res){
      alltablesname = [],arry = []
      //获取指定数据库表名
      bt_tools.send({url:'project/binlog/get_tables' , data: {db_name:res}}, function (res) {
        if (res.length == 0) {
          alltablesname = [{title:'当前数据库下没有表',value:''}]
          arry = alltablesname
        }else{
          for (var i = 0; i < res.length; i++) {
            alltablesname.push(res[i])
          }
          $.each(alltablesname,function(index,item){
            arry.push({ title: item.name+(item.cron_id == null || item.cron_id.length == 0 ? ' [无备份任务]':''), value: item.name })
          })
        }
      })
    }
    function table() {
      $('#dbbackup_list').html('');
      var backup_databases = bt_tools.table({
        el: '#dbbackup_list',
        url: url,
        param: params,
        load: true,
        default:  type === 0 ? "数据库备份列表为空":"表备份列表为空", //数据为空时的默认提示
        column: [
          { fid: 'excute_time', title: '备份时间', width: 150, type: 'text' },
          { fid: 'name', title: type === 0 ? '数据库名' : '表名', type: 'text' },
          { fid: 'full_size', title: '备份大小', width: 80, type: 'text' },
          { 
            title: '备份计划任务', 
            width: 100, 
            type: 'text',
            template: function (row){
              return (row.cron_id == [] || row.cron_id.length == 0 ? '<span class="color-red cursor-pointer">丢失</span>' : '<span>正常</span>')
            },
            event: function (row, index, ev, key, that) {
              if(row.cron_id == [] || row.cron_id.length == 0){
                bt.confirm({
                  title: '恢复备份计划任务',
                  msg: '该备份计划任务不存在，是否恢复备份计划任务'
                }, function () {
                  var params = {
                    cron_type : 'hour-n',
                    backup_type : row.type,
                    backup_cycle: row.backup_cycle,
                    datab_name : type == 0 ? row.name : $('input[name=inbox_input]').val(),
                    backup_id : row.backup_id,
                    notice: row.notice,
                    notice_channel : row.notice_channel,
                    upload_localhost : row.upload_localhost,
                    upload_alioss : row.upload_alioss,
                    upload_txcos : row.upload_txcos,
                    upload_qiniu : row.upload_qiniu,
                    upload_obs : row.upload_obs,
                    upload_bos : row.upload_bos
                  }
                  bt_tools.send({url:'project/binlog/modify_mysqlbinlog_backup_setting',data: params}, function (res) {
                    bt_tools.msg(res)
                    if (res.status) {
                      that.$refresh_table_list();
                      database_table.$refresh_table_list(true)
                    }
                  },'恢复计划任务')
                })
              }
            } 
         },
          {
            title: '操作',
            type: 'group',
            width: 270,
            align: 'right',
            group: [
              {
                title: '执行',
                hide: function (row) {
                  return (row.cron_id == [] || row.cron_id.length == 0 ? true : false)
                },
                event: function (row, index, ev, key, that) {
                  database.startCrontabTask({ id: row.cron_id }, function () {
                    that.$refresh_table_list();
                    database_table.$refresh_table_list(true)
                  })
                }
              },
              {
                title: '编辑',
                hide: function (row) {
                  return (row.cron_id == [] || row.cron_id.length == 0 ? true : false)
                },
                event: function (row, index, ev, key, that) {
                  var editBackup = null;
                  layer.open({
                    type: 1,
                    title:'编辑'+(type === 0 ? '数据库' : '表')+'['+row.name+']增量备份',
                    closeBtn: 2,
                    shadeClose: false,
                    area: '550px',
                    btn: ['提交','取消'],
                    skin: 'addDbbackup',
                    content: '<div id="addDbbackup"></div>',
                    success: function (layers, indexs) {
                      var mulpValues = [],mulpTitles = []
                      for (var i = 0; i < database.backuptoList.length; i++) {
                        if(row['upload_'+database.backuptoList[i].value] == "") continue
                        mulpValues.push(row['upload_'+database.backuptoList[i].value])
                        mulpTitles.push(database.backuptoList[i].title)
                      }
                      editBackup = bt_tools.form({
                        el: '#addDbbackup',
                        data: row,
                        class: 'pd15',
                        form: [
                          {
                            label: '数据备份到',
                            group: {
                              type: 'multipleSelect',
                              name: 'upload_alioss',
                              width: '390px',
                              value: mulpValues,
                              list: database.backuptoList
                            }
                          },
                          {
                            label: '压缩密码',
                            group: {
                              type: 'text',
                              disabled: true,
                              name: 'zip_password',
                              width: '390px',
                              value: row.zip_password,
                            }
                          },
                          {
                            label: '备份周期',
                            group: [
                              {
                                type: 'number',
                                name: 'backup_cycle',
                                'class': 'group_span',
                                width: '346px',
                                value: row.backup_cycle,
                                unit: '小时',
                                min: 0,
                                max: 23
                              }
                            ]
                          },
                          {
                            label: '备份提醒',
                            group: [{
                              type: 'select',
                              name: 'notice',
                              value: parseInt(row.notice),
                              list: [
                                { title: '不接收任何消息通知', value: 0 },
                                { title: '任务执行失败接收通知', value: 1 }
                              ],
                              change: function (formData, element, that) {
                                that.config.form[3].group[1].display = formData.notice == 0 ? false : true
                                that.config.form[3].group[0].value = parseInt(formData.notice)
                                that.$replace_render_content(3)
                              }
                            }, {
                              label: '消息通道',
                              type: 'select',
                              name: 'notice_channel',
                              display: parseInt(row.notice) == 0 ? false : true,
                              value: row.notice_channel,
                              width: '100px',
                              placeholder: '未配置消息通道',
                              list: {
                                url: '/config?action=get_msg_configs',
                                dataFilter: function (res, that) {
                                  return database.pushChannelMessage.getChannelSwitch(res, 'enterpriseBackup')
                                },success: function (res, that, config, list) {
                                  if(!config.group[1].value && config.group[0].value == 1){
                                    config.group[1].value = list[0].value
                                  }
                                }
                              }
                            }, {
                              type: 'link',
                              'class': 'mr5',
                              title: '设置消息通道',
                              event: function (formData, element, that) {
                                open_three_channel_auth();
                              }
                            }]
                          }
                        ]
                      })
                    },
                    yes: function (indexs) {
                      var formData = editBackup.$get_form_value()
                      if(formData.backup_cycle == '') return layer.msg("备份周期不能为空！")
                      if(formData.backup_cycle < 0) return layer.msg("备份周期不能小于0！")
                      if(formData.notice == 1) {
                        if (formData.notice_channel == undefined) return layer.msg("请设置消息通道")
                      }
                      formData['cron_type'] = 'hour-n'
                      formData['backup_type'] = row.type
                      formData['datab_name'] = type == 0 ? row.name : $('input[name=inbox_input]').val()
                      formData['cron_id'] = row.cron_id
                      formData['backup_id'] = row.backup_id
                      formData['notice_channel'] = formData.notice == 0 ? '' : formData.notice_channel
                      var multipleValues = $('select[name=upload_alioss]').val()
                      if(multipleValues == null) return layer.msg('请最少选择一个备份类型')
                      formData['upload_localhost'] = multipleValues.indexOf('localhost') > -1 ? 'localhost' : ''
                      formData['upload_alioss'] = multipleValues.indexOf('alioss') > -1 ? 'alioss' : '',
                      formData['upload_txcos'] = multipleValues.indexOf('txcos') > -1 ? 'txcos' : '',
                      formData['upload_qiniu'] = multipleValues.indexOf('qiniu') > -1 ? 'qiniu' : '',
                      formData['upload_obs'] = multipleValues.indexOf('obs') > -1 ? 'obs' : '',
                      formData['upload_bos'] = multipleValues.indexOf('bos') > -1 ? 'bos' : '',
                      delete formData['zip_password']
                      //编辑
                      bt_tools.send({url:'project/binlog/modify_mysqlbinlog_backup_setting',data: formData}, function (res) {
                        bt_tools.msg(res)
                        if (res.status) {
                          layer.close(indexs)
                          that.$refresh_table_list();
                          database_table.$refresh_table_list(true)
                        }
                      },'编辑备份任务')
                    }
                  })
                }
              },
              {
                title: '日志',
                hide: function (row) {
                  return (row.cron_id == [] || row.cron_id.length == 0 ? true : false)
                },
                event: function (row, index, ev, key, that) {
                  database.backupLogs({ id: row.cron_id }, index, ev, key, that)
                }
              },
              {
                title: '恢复',
                event: function (row, index, ev, key, that) {
                  that.resume_download_backup({ gp_type : 0,title:'恢复',backup_id: row.backup_id,datab_name: row.name,start_time: row.start_time,end_time: row.end_time})
                }
              },{
                title: '下载',
                event: function (row, index, ev, key, that) {
                  that.resume_download_backup({ gp_type : 1,title:'下载',backup_id: row.backup_id,datab_name: row.name,start_time: row.start_time,end_time: row.end_time})
                }
              }, {
                title: '删除',
                event: function (row, index, ev, key, that) {
                  that.del_database_backup({ name: row.name, cron_id: row.cron_id,backup_id: row.backup_id }, function (rdata) {
                    bt_tools.msg(rdata);
                    if (rdata.status) {
                      that.$refresh_table_list();
                      database_table.$refresh_table_list(true)
                      dataBaseName(false)
                    }
                  });
                }
              }]
          }
        ],
        methods: {
          /**
           * @description 恢复 下载
           * @param {object} config
           */
          resume_download_backup: function (config) {
            layer.open({
              type: 1,
              title:config.title+(type === 0 ? '数据库':'表' )+'【'+config.datab_name+'】数据',
              closeBtn: 2,
              shadeClose: false,
              area:['350px',config.backup_id == null ? '220px':'170px'],
              skin: 'restore',
              content: '<div id="restore" class="bt-form pd15">\
                <div class="line" style="display: '+(config.backup_id == null ? "block":"none")+'">\
                  <span class="tname">解压密码</span>\
                  <div class="info-r">\
                    <input type="text" class="bt-input-text mr5 showPwd" name="zip_password" placeholder="请输入解压密码" />\
                  </div>\
                </div>\
                <div class="line">\
                  <span class="tname">'+ config.title +'截止时间</span>\
                  <div class="info-r">\
                    <input id="calendar" type="text" class="bt-input-text mr5" name="calendar" placeholder="请输入'+ config.title +'截止时间" readOnly />\
                  </div>\
                </div>\
              </div>',
              btn: ['确定'+config.title, '关闭'],
              success: function (){
                laydate.render({
                  elem: '#calendar'
                  ,show: true //直接显示
                  ,closeStop: '#test1'
                  ,theme: '#20a53a'
                  ,trigger: 'click' //采用click弹出
                  ,min: config.start_time,
                  max: config.end_time,
                  vlue: bt.get_date(365),
                  type: 'datetime',
                  format: 'yyyy-MM-dd HH:mm:ss',
                  btns: ['clear','confirm']
                });
              },
              yes: function (indexs) {
                var url = '',title = ''
                var params = {
                  end_time : $('input[name=calendar]').val()
                }
                if(params.end_time == '') return layer.msg("截止时间不能为空")
                if(config.backup_id == null){
                  if($('input[name=zip_password]').val() == ''){
                    return layer.msg("解压密码不能为空")
                  }else{
                    params['zip_password'] = $('input[name=zip_password]').val()
                  }
                }
                if (type == 0) {
                  params['datab_name'] = config.datab_name
                } else {
                  params['datab_name'] = $('input[name=inbox_input]').val()
                  params['table_name'] = config.datab_name
                }
                if (config.gp_type == 0){//恢复
                  url = 'project/binlog/restore_to_database'
                  params['backup_id'] = config.backup_id
                  title = '恢复备份任务'
                }else {//下载
                  params['backup_type'] =  type == 0 ? 'databases' : 'tables'
                  url = 'project/binlog/export_data'
                  title = '下载备份任务'
                }
                bt_tools.send({url:url, data:params } , function (res) {
                  if (config.gp_type == 0) {
                    layer.msg(res.msg, {icon: res.status ? 1:2})
                    if(res.status) layer.close(indexs)
                  }else{
                    if (typeof res.name == "undefined") {
                      if (!res.status) {
                        layer.msg(res.msg, {icon: 2})
                      }
                    }else{
                      layer.close(indexs)
                      window.location.href = '/download?filename='+res.name
                    }
                  }
                },title)
              }
            })
          },
          /**
           * @description 删除站点备份
           * @param {object} config
           * @param {function} callback
           */
          del_database_backup: function (config, callback) {
            bt.prompt_confirm("删除备份任务","删除备份任务[" + config.name + "]，删除此任务会连备份数据一起删除,是否继续？",function () {
              bt_tools.send({url:'project/binlog/delete_mysql_binlog_setting',data: {cron_id:config.cron_id,backup_id:config.backup_id,type:'manager'}}, function (rdata) {
                if (callback) callback(rdata)
              }, '删除备份任务')
            })
          }
        },
        tootls: [{ // 按钮组
          type: 'group',
          positon: ['left', 'top'],
          list: [{
            title: '添加备份任务',
            active: true,
            event: function (ev, that) {
              var addDBbackup = null;
              layer.open({
                type: 1,
                title:'添加备份任务',
                closeBtn: 2,
                shadeClose: false,
                area:'550px',
                btn: ['提交','取消'],
                skin: 'addDbbackup',
                content: '<div id="addDbbackup"></div>',
                success: function (layers, indexs) {
                  addDBbackup = bt_tools.form({
                    el: '#addDbbackup',
                    class: 'pd15',
                    form: [
                      {
                        label: '选择数据库',
                        group: {
                          type: 'select',
                          name: 'datab_name',
                          width: '390px',
                          list: arry1,
                          change: function (formData, element, that) {
                            if (type == 1) {
                              getTables(formData.datab_name)
                              setTimeout(function() {
                                that.config.form[1].group.list = arry
                                that.$replace_render_content(1)
                              },200)
                            }
                          }
                        }
                      },
                      {
                        label: '选择表',
                        hide: type === 1 ? false : true,
                        group: {
                          type: 'select',
                          name: 'table_name',
                          width: '390px',
                          list: arry
                        }
                      },
                      {
                        label: '数据备份到',
                        group: {
                          type: 'multipleSelect',
                          name: 'upload_alioss',
                          width: '390px',
                          list: database.backuptoList
                        }
                      },
                      {
                        label: '压缩密码',
                        group: {
                          type: 'text',
                          name: 'zip_password',
                          width: '390px',
                          placeholder: '请输入压缩密码',
                          unit: '<span class="glyphicon glyphicon-repeat cursor mr5"></span>'
                        }
                      },
                      {
                        label: '备份周期',
                        group: [
                          {
                            type: 'number',
                            name: 'backup_cycle',
                            'class': 'group_span',
                            width: '346px',
                            value: '3',
                            unit: '小时',
                            min: 0,
                            max: 23
                          }
                        ]
                      },
                      {
                        label: '备份提醒',
                        group: [{
                          type: 'select',
                          name: 'notice',
                          value: 0,
                          list: [
                            { title: '不接收任何消息通知', value: 0 },
                            { title: '任务执行失败接收通知', value: 1 }
                          ],
                          change: function (formData, element, that) {
                            that.config.form[5].group[1].display = formData.notice == 0 ? false : true
                            that.config.form[5].group[0].value = parseInt(formData.notice)
                            that.$replace_render_content(5)
                          }
                        }, {
                          label: '消息通道',
                          type: 'select',
                          name: 'notice_channel',
                          display: false,
                          width: '100px',
                          placeholder: '未配置消息通道',
                          list: {
                            url: '/config?action=get_msg_configs',
                            dataFilter: function (res, that) {
                              return database.pushChannelMessage.getChannelSwitch(res, 'enterpriseBackup')
                            }
                          }
                        }, {
                          type: 'link',
                          'class': 'mr5',
                          title: '设置消息通道',
                          event: function (formData, element, that) {
                            open_three_channel_auth();
                          }
                        }]
                      }
                    ]
                  })
                  $('#addDbbackup .pd15').append("<ul class='help-info-text c7 mlr20'>\
                      <li style='color:red;'>注意：请牢记压缩密码，以免因压缩密码导致无法恢复和下载数据</li>\
                  </ul>");
                  $('#addDbbackup .unit .glyphicon-repeat').click(function (){
                    $('#addDbbackup input[name=zip_password]').val(bt.get_random(bt.get_random_num(6,10)))
                  })
                  $('#addDbbackup .unit .glyphicon-repeat').click()
                },
                yes: function (indexs) {
                  var formData = addDBbackup.$get_form_value()
                  if(formData.backup_cycle == '') return layer.msg("备份周期不能为空！")
                  if(formData.backup_cycle < 0) return layer.msg("备份周期不能小于0！")
                  formData['cron_type'] = 'hour-n'
                  formData['backup_type'] = type === 0 ? 'databases' : 'tables'
                  if(formData.backup_type == 'tables'){
                    if(formData.table_name == '0') return layer.msg("当前数据库下没有表，不能添加")
                  }else{
                    delete formData['table_name']
                  }
                  if(formData.notice == 1) {
                    if (formData.notice_channel == undefined) return layer.msg("请设置消息通道")
                  }
                  var multipleValues = $('select[name=upload_alioss]').val()
                  if(multipleValues == null) return layer.msg('请最少选择一个备份类型')
                  formData['upload_localhost'] = multipleValues.indexOf('localhost') > -1 ? 'localhost' : '',
                  formData['upload_alioss'] = multipleValues.indexOf('alioss') > -1 ? 'alioss' : '',
                  formData['upload_txcos'] = multipleValues.indexOf('txcos') > -1 ? 'txcos' : '',
                  formData['upload_qiniu'] = multipleValues.indexOf('qiniu') > -1 ? 'qiniu' : '',
                  formData['upload_obs'] = multipleValues.indexOf('obs') > -1 ? 'obs' : '',
                  formData['upload_bos'] = multipleValues.indexOf('bos') > -1 ? 'bos' : '',
                  formData['notice_channel'] = formData.notice == 0 ? '' : formData.notice_channel
                  //添加
                  bt_tools.send({url:'project/binlog/add_mysqlbinlog_backup_setting',data: formData}, function (res) {
                    bt_tools.msg(res)
                    if (res.status) {
                      layer.close(indexs)
                      that.$refresh_table_list();
                      database_table.$refresh_table_list(true)
                      dataBaseName(false)
                    }
                  })
                }
              })

            }
          }]
        },
          //分页显示
          {
            type: 'page',
            positon: ['right', 'bottom'], // 默认在右下角
            pageParam: 'p', //分页请求字段,默认为 : p
            page: 1, //当前分页 默认：1
            // numberParam: 'limit',
            //分页数量请求字段默认为 : limit
            // defaultNumber: 10
            //分页数量默认 : 20条
          }]
      })
      $('#dbbackup_list .tootls_group.tootls_top .pull-left').append('<div class="inlineBlock ml5"><span class="glyphicon glyphicon-alert" style="color: #f39c12; margin-right: 10px;"></span>【使用提醒】此功能为企业版专享功能，当前所有用户可免费使用。</div>')
      $('#dbbackup_list').append("<ul class='help-info-text c7'>\
          <li>备份大小：备份大小包含完全备份数据大小和增量备份数据大小</li>\
          <li>备份会保留一个星期的备份数据，当备份时，检测到完全备份为一个星期前，会重新完全备份</li>\
          <li>请勿同一时间添加多个备份任务，否则可能因同一时间执行多个备份任务导致文件句柄数打开过多或者爆内存</li>\
      </ul>");
    }
  },
  get_backup: function () {
    var that = this;
    bt_tools.send({url:'project/binlog/get_binlog_status'}, function (res) {
      if (res.status) {
        bt.open({
          type: 1,
          area: ['890px','620px'],
          title: '企业增量备份',
          closeBtn: 2,
          skin: 'databaseBackup',
          shift: 0,
          content: "<div class='bt-tabs'>\
            <div class='bt-w-menu database-menu pull-left' style='height: 100%;'>\
              <p>备份数据库</p><p>备份表</p>\
            </div>\
            <div id='webedit-con-database' class='bt-w-con webedit-con pd15'></div>\
          </div>",
          success:function(){
            $('.database-menu p').css('padding-left','28px')
            $('.database-menu p').click(function () {
              $('#webedit-con-database').html('');
              $(this).addClass('bgw').siblings().removeClass('bgw');
              var index = $(this).index()
              database.backupList(index)
            })
            $('.database-menu p:eq(0)').click()
          }
        })
      } else {
        layer.msg('请检查数据库是否正常运行或二进制日志是否开启！', { time: 0, shadeClose: true, shade: .3 });
      }
    },'检测是否开启二进制日志')
  },
  /**
   * @name 删除导入的文件
   * @author hwliang<2021-09-09>
   * @param {string} filename
   * @param {string} name
   */
  rm_input_file: function (filename, name) {
    bt.files.del_file(filename, function (rdata) {
      bt.msg(rdata);
      database.input_database(name);
    })
  },
  // 备份导入
  input_database: function (name) {
    var path = bt.get_cookie('backup_path') + "/database";

    bt.files.get_files(path, '', function (rdata) {
      var data = [];
      for (var i = 0; i < rdata.FILES.length; i++) {
        if (rdata.FILES[i] == null) continue;
        var fmp = rdata.FILES[i].split(";");
        var ext = bt.get_file_ext(fmp[0]);
        if (ext != 'sql' && ext != 'zip' && ext != 'gz' && ext != 'tgz' && ext != 'bak') continue;
        data.push({
          name: fmp[0],
          size: fmp[1],
          etime: fmp[2],
        })
      }
      if ($('#DataInputList').length <= 0) {
        bt.open({
          type: 1,
          skin: 'demo-class',
          area: ["600px", "478px"],
          title: lan.database.input_title_file,
          closeBtn: 2,
          shift: 5,
          shadeClose: false,
          content: '\
            <div class="pd15">\
              <div class="clearfix">\
                <button class="btn btn-default btn-sm" onclick="database.upload_files(\'' + name + '\')">' + lan.database.input_local_up + '</button>\
                <div class="pull-right">\
                  \
                </div>\
              </div>\
              <div class="divtable mtb15" style="max-height:274px; overflow:auto; border: 1px solid #ddd;">\
                <table id="DataInputList" class="table table-hover" style="border: none;"></table>\
              </div>' +
              bt.render_help([lan.database.input_ps1, lan.database.input_ps2, (bt.os != 'Linux' ? lan.database.input_ps3.replace(/\/www.*\/database/, path) : lan.database.input_ps3)]) +
              '</div>\
            '
        });
      }
      setTimeout(function () {
        bt.fixed_table('DataInputList');
        bt.render({
          table: '#DataInputList',
          columns: [{
            field: 'name',
            title: lan.files.file_name
          },
            {
              field: 'etime',
              title: lan.files.file_etime,
              templet: function (item) {
                return bt.format_data(item.etime);
              }
            },
            {
              field: 'size',
              title: lan.files.file_size,
              templet: function (item) {
                return bt.format_size(item.size)
              }
            },
            {
              field: 'opt',
              title: '操作',
              align: 'right',
              templet: function (item) {
                return '<a class="btlink" herf="javascrpit:;" onclick="bt.database.input_sql(\'' + bt.rtrim(rdata.PATH, '/') + "/" + item.name + '\',\'' + name + '\')">导入</a>  | <a class="btlink" herf="javascrpit:;" onclick="database.rm_input_file(\'' + bt.rtrim(rdata.PATH, '/') + "/" + item.name + '\',\'' + name + '\')">删除</a>';
              }
            },
          ],
          data: data
        });
      }, 100)
    }, 'mtime')
  },
  // 工具
  rep_tools: function (db_name, res) {
    var loadT = layer.msg('正在获取数据,请稍候...', {
      icon: 16,
      time: 0
    });
    bt.send('GetInfo', 'database/GetInfo', {
      db_name: db_name
    }, function (rdata) {
      layer.close(loadT)
      if (rdata.status === false) {
        layer.msg(rdata.msg, {
          icon: 2
        });
        return;
      }
      var types = {
        InnoDB: "MyISAM",
        MyISAM: "InnoDB"
      };
      var tbody = '';
      for (var i = 0; i < rdata.tables.length; i++) {
        if (!types[rdata.tables[i].type]) continue;
        tbody += '<tr>\
                        <td><input value="dbtools_' + rdata.tables[i].table_name + '" class="check" onclick="database.selected_tools(null,\'' + db_name + '\');" type="checkbox"></td>\
                        <td><span style="width:220px;"> ' + rdata.tables[i].table_name + '</span></td>\
                        <td>' + rdata.tables[i].type + '</td>\
                        <td><span style="width:90px;"> ' + rdata.tables[i].collation + '</span></td>\
                        <td>' + rdata.tables[i].rows_count + '</td>\
                        <td>' + rdata.tables[i].data_size + '</td>\
                        <td style="text-align: right;">\
                            <a class="btlink" onclick="database.rep_database(\'' + db_name + '\',\'' + rdata.tables[i].table_name + '\')">修复</a> |\
                            <a class="btlink" onclick="database.op_database(\'' + db_name + '\',\'' + rdata.tables[i].table_name + '\')">优化</a> |\
                            <a class="btlink" onclick="database.to_database_type(\'' + db_name + '\',\'' + rdata.tables[i].table_name + '\',\'' + types[rdata.tables[i].type] + '\')">转为' + types[rdata.tables[i].type] + '</a>\
                        </td>\
                    </tr> '
      }

      if (res) {
        $(".gztr").html(tbody);
        $("#db_tools").html('');
        $("input[type='checkbox']").attr("checked", false);
        $(".tools_size").html('大小：' + rdata.data_size);
        return;
      }

      layer.open({
        type: 1,
        title: "MySQL工具箱【" + db_name + "】",
        area: ['780px', '580px'],
        closeBtn: 2,
        shadeClose: false,
        content: '<div class="pd15">\
                                <div class="db_list">\
                                    <span><a>数据库名称：' + db_name + '</a>\
                                    <a class="tools_size">大小：' + rdata.data_size + '</a></span>\
                                    <span id="db_tools" style="float: right;"></span>\
                                </div >\
                                <div class="divtable">\
                                <div  id="database_fix"  style="height:360px;overflow:auto;border:#ddd 1px solid">\
                                <table class="table table-hover "style="border:none">\
                                    <thead>\
                                        <tr>\
                                            <th><input class="check" onclick="database.selected_tools(this,\'' + db_name + '\');" type="checkbox"></th>\
                                            <th>表名</th>\
                                            <th>引擎</th>\
                                            <th>字符集</th>\
                                            <th>行数</th>\
                                            <th>大小</th>\
                                            <th style="text-align: right;">操作</th>\
                                        </tr>\
                                    </thead>\
                                    <tbody class="gztr">' + tbody + '</tbody>\
                                </table>\
                                </div>\
                            </div>\
                            <ul class="help-info-text c7">\
                                <li>【修复】尝试使用REPAIR命令修复损坏的表，仅能做简单修复，若修复不成功请考虑使用myisamchk工具</li>\
                                <li>【优化】执行OPTIMIZE命令，可回收未释放的磁盘空间，建议每月执行一次</li>\
                                <li>【转为InnoDB/MyISAM】转换数据表引擎，建议将所有表转为InnoDB</li>\
                            </ul></div>'
      });
      tableFixed('database_fix');
      //表格头固定
      function tableFixed (name) {
        var tableName = document.querySelector('#' + name);
        tableName.addEventListener('scroll', scrollHandle);
      }

      function scrollHandle (e) {
        var scrollTop = this.scrollTop;
        //this.querySelector('thead').style.transform = 'translateY(' + scrollTop + 'px)';
        $(this).find("thead").css({
          "transform": "translateY(" + scrollTop + "px)",
          "position": "relative",
          "z-index": "1"
        });
      }
    });
  },
  selected_tools: function (my_obj, db_name) {
    var is_checked = false
    if (my_obj) is_checked = my_obj.checked;
    var db_tools = $("input[value^='dbtools_']");
    var n = 0;
    for (var i = 0; i < db_tools.length; i++) {
      if (my_obj) db_tools[i].checked = is_checked;
      if (db_tools[i].checked) n++;
    }
    if (n > 0) {
      var my_btns = '<button class="btn btn-default btn-sm" onclick="database.rep_database(\'' + db_name + '\',null)">修复</button><button class="btn btn-default btn-sm" onclick="database.op_database(\'' + db_name + '\',null)">优化</button><button class="btn btn-default btn-sm" onclick="database.to_database_type(\'' + db_name + '\',null,\'InnoDB\')">转为InnoDB</button></button><button class="btn btn-default btn-sm" onclick="database.to_database_type(\'' + db_name + '\',null,\'MyISAM\')">转为MyISAM</button>'
      $("#db_tools").html(my_btns);
    } else {
      $("#db_tools").html('');
    }
  },
  rep_database: function (db_name, tables) {
    dbs = database.rep_checkeds(tables)
    var loadT = layer.msg('已送修复指令,请稍候...', {
      icon: 16,
      time: 0
    });
    bt.send('ReTable', 'database/ReTable', {
      db_name: db_name,
      tables: JSON.stringify(dbs)
    }, function (rdata) {
      layer.close(loadT)
      if (rdata.status) {
        database.rep_tools(db_name, true);
      }
      layer.msg(rdata.msg, {
        icon: rdata.status ? 1 : 2
      });
    });
  },
  op_database: function (db_name, tables) {
    dbs = database.rep_checkeds(tables)
    var loadT = layer.msg('已送优化指令,请稍候...', {
      icon: 16,
      time: 0
    });
    bt.send('OpTable', 'database/OpTable', {
      db_name: db_name,
      tables: JSON.stringify(dbs)
    }, function (rdata) {
      layer.close(loadT)
      if (rdata.status) {
        database.rep_tools(db_name, true);
      }
      layer.msg(rdata.msg, {
        icon: rdata.status ? 1 : 2
      });
    });
  },
  to_database_type: function (db_name, tables, type) {
    dbs = database.rep_checkeds(tables)
    var loadT = layer.msg('已送引擎转换指令,请稍候...', {
      icon: 16,
      time: 0,
      shade: [0.3, "#000"]
    });
    bt.send('AlTable', 'database/AlTable', {
      db_name: db_name,
      tables: JSON.stringify(dbs),
      table_type: type
    }, function (rdata) {
      layer.close(loadT);
      if (rdata.status) {
        database.rep_tools(db_name, true);
      }
      layer.msg(rdata.msg, {
        icon: rdata.status ? 1 : 2
      });
    });
  },
  rep_checkeds: function (tables) {
    var dbs = []
    if (tables) {
      dbs.push(tables)
    } else {
      var db_tools = $("input[value^='dbtools_']");
      for (var i = 0; i < db_tools.length; i++) {
        if (db_tools[i].checked) dbs.push(db_tools[i].value.replace('dbtools_', ''));
      }
    }

    if (dbs.length < 1) {
      layer.msg('请至少选择一张表!', {
        icon: 2
      });
      return false;
    }
    return dbs;
  },
  // 改密
  set_data_pass: function (id, username, password) {
    var that = this,
        bs = bt.database.set_data_pass(function (rdata) {
          if (rdata.status) database_table.$refresh_table_list(true);
          bt.msg(rdata);
        })
    $('.name' + bs).val(username);
    $('.id' + bs).val(id);
    $('.password' + bs).val(password);
  },
  // 删除
  del_database: function (wid, dbname,obj, callback) {
    var rendom = bt.get_random_code(),
        num1 = rendom['num1'],
        num2 = rendom['num2'],
        title = '',
        tips = '是否确认【删除数据库】，删除后可能会影响业务使用！';
    if(obj && obj.db_type > 0) tips = '远程数据库不支持数据库回收站，删除后将无法恢复，请谨慎操作';
    title = typeof dbname === "function" ? '批量删除数据库' : '删除数据库 [ ' + dbname + ' ]';
    layer.open({
      type: 1,
      title: title,
      icon: 0,
      skin: 'delete_site_layer',
      area: "530px",
      closeBtn: 2,
      shadeClose: true,
      content: "<div class=\'bt-form webDelete pd30\' id=\'site_delete_form\'>" +
          "<i class=\'layui-layer-ico layui-layer-ico0\'></i>" +
          "<div class=\'f13 check_title\' style=\'margin-bottom: 20px;\'>"+tips+"</div>" +
          "<div style=\'color:red;margin:18px 0 18px 18px;font-size:14px;font-weight: bold;\'>注意：数据无价，请谨慎操作！！！" + (!recycle_bin_db_open ? '<br>风险操作：当前数据库回收站未开启，删除数据库将永久消失！' : '') + "</div>" +
          "<div class=\'vcode\'>" + lan.bt.cal_msg + "<span class=\'text\'>" + num1 + " + " + num2 + "</span>=<input type=\'number\' id=\'vcodeResult\' value=\'\'></div>" +
          "</div>",
      btn: [lan.public.ok, lan.public.cancel],
      yes: function (indexs) {
        var vcodeResult = $('#vcodeResult'),
            data = {
              id: wid,
              name: dbname
            };
        if (vcodeResult.val() === '') {
          layer.tips('计算结果不能为空', vcodeResult, {
            tips: [1, 'red'],
            time: 3000
          })
          vcodeResult.focus()
          return false;
        } else if (parseInt(vcodeResult.val()) !== (num1 + num2)) {
          layer.tips('计算结果不正确', vcodeResult, {
            tips: [1, 'red'],
            time: 3000
          })
          vcodeResult.focus()
          return false;
        }
        if (typeof dbname === "function") {
          delete data.id;
          delete data.name;
        }
        layer.close(indexs)
        var arrs = wid instanceof Array ? wid : [wid]
        var ids = JSON.stringify(arrs),
            countDown = 9;
        if (arrs.length == 1) countDown = 4
        title = typeof dbname === "function" ? '二次验证信息，批量删除数据库' : '二次验证信息，删除数据库 [ ' + dbname + ' ]';
        var loadT = bt.load('正在检测数据库数据信息，请稍候...'),
            param = {url:'database/'+bt.data.db_tab_name+'/check_del_data',data:{data:JSON.stringify({ids: ids})}}
        if(bt.data.db_tab_name == 'mysql') param = {url:'database?action=check_del_data',data:{ids:ids}}
        bt_tools.send(param,function(res){
          loadT.close()
          layer.open({
            type: 1,
            title: title,
            closeBtn: 2,
            skin: 'verify_site_layer_info active',
            area: '740px',
            content: '<div class="check_delete_site_main pd30">' +
                '<i class="layui-layer-ico layui-layer-ico0"></i>' +
                '<div class="check_layer_title">堡塔温馨提示您，请冷静几秒钟，确认以下要删除的数据。</div>' +
                '<div class="check_layer_content">' +
                '<div class="check_layer_item">' +
                '<div class="check_layer_site"></div>' +
                '<div class="check_layer_database"></div>' +
                '</div>' +
                '</div>' +
                '<div class="check_layer_error ' + (recycle_bin_db_open ? 'hide' : '') + '"><span class="glyphicon glyphicon-info-sign"></span>风险事项：当前未开启数据库回收站功能，删除数据库后，数据库将永久消失！</div>' +
                '<div class="check_layer_message">请仔细阅读以上要删除信息，防止数据库被误删，确认删除还有 <span style="color:red;font-weight: bold;">' + countDown + '</span> 秒可以操作。</div>' +
                '</div>',
            btn: ['确认删除(' + countDown + '秒后继续操作)', '取消删除'],
            success: function (layers) {
              var html = '',
                  rdata = res.data;
              var filterData = rdata.filter(function (el) {
                return ids.indexOf(el.id) != -1
              })
              for (var i = 0; i < filterData.length; i++) {
                var item = filterData[i],
                    newTime = parseInt(new Date().getTime() / 1000),
                    t_icon = '<span class="glyphicon glyphicon-info-sign" style="color: red;width:15px;height: 15px;;vertical-align: middle;"></span>';

                database_html = (function (item) {
                  var is_time_rule = (newTime - item.st_time) > (86400 * 30) && (item.total > 1024 * 10),
                      is_database_rule = res.db_size <= item.total,
                      database_time = bt.format_data(item.st_time, 'yyyy-MM-dd'),
                      database_size = bt.format_size(item.total);

                  var f_size = '<i ' + (is_database_rule ? 'class="warning"' : '') + ' style = "vertical-align: middle;" > ' + database_size + '</i> ' + (is_database_rule ? t_icon : '');
                  var t_size = '注意：此数据库较大，可能为重要数据，请谨慎操作.\n数据库：' + database_size;
                  if (item.total < 2048) t_size = '注意事项：当前数据库不为空，可能为重要数据，请谨慎操作.\n数据库：' + database_size;
                  if (item.total === 0) t_size = '';
                  return '<div class="check_layer_database">' +
                      '<span title="数据库：' + item.name + '">数据库：' + item.name + '</span>' +
                      '<span title="' + t_size + '">大小：' + f_size + '</span>' +
                      '<span title="' + (is_time_rule && item.total != 0 ? '重要：此数据库创建时间较早，可能为重要数据，请谨慎操作.' : '') + '时间：' + database_time + '">创建时间：<i ' + (is_time_rule && item.total != 0 ? 'class="warning"' : '') + '>' + database_time + '</i></span>' +
                      '</div>'
                }(item))
                if (database_html !== '') html += '<div class="check_layer_item">' + database_html + '</div>';
              }
              if (html === '') html = '<div style="text-align: center;width: 100%;height: 100%;line-height: 300px;font-size: 15px;">无数据</div>'
              $('.check_layer_content').html(html)
              var interVal = setInterval(function () {
                countDown--;
                $(layers).find('.layui-layer-btn0').text('确认删除(' + countDown + '秒后继续操作)')
                $(layers).find('.check_layer_message span').text(countDown)
              }, 1000);
              setTimeout(function () {
                $(layers).find('.layui-layer-btn0').text('确认删除');
                $(layers).find('.check_layer_message').html('<span style="color:red">注意：请仔细阅读以上要删除信息，防止数据库被误删</span>')
                $(layers).removeClass('active');
                clearInterval(interVal)
              }, countDown * 1000)
            },
            yes: function (indes, layers) {
              // console.log(1);
              if ($(layers).hasClass('active')) {
                layer.tips('请确认信息，稍候再尝试，还剩' + countDown + '秒', $(layers).find('.layui-layer-btn0'), {
                  tips: [1, 'red'],
                  time: 3000
                })
                return;
              }
              if (typeof dbname === "function") {
                dbname(data)
              } else {
                bt.database.del_database(data, function (rdata) {
                  layer.closeAll()
                  if (callback) callback(rdata);
                  bt.msg(rdata);
                })
              }
            }
          })
        })
      }
    })
  },
}

var sql_server ={
  database_table_view :function(search){
    var param = {
      table: 'databases',
      search: search || ''
    }
    $('#bt_sqldatabase_table').empty();
    database_table = bt_tools.table({
      el: '#bt_sqldatabase_table',
      url: 'database/sqlserver/get_list',
      param: param, //参数
      minWidth: '1000px',
      load: true,
      autoHeight: true,
      default: "数据库列表为空", // 数据为空时的默认提示
      pageName: 'database',
      beforeRequest:function(beforeData){
        var db_type_val = $('.sqlserver_type_select_filter').val()
        switch(db_type_val){
          case 'all':
            delete param['db_type']
            delete param['sid']
            break;
          case 0:
            param['db_type'] = 0;
            break;
          default:
            delete param['db_type'];
            param['sid'] = db_type_val
        }
        if (beforeData.hasOwnProperty('data') && typeof beforeData.data === 'string') {
          delete beforeData['data']
          return { data: JSON.stringify($.extend(param,beforeData)) }
        }
        return {data:JSON.stringify(param)}
      },
      column:[
        {type: 'checkbox',width: 20},
        {fid: 'name',title: '数据库名',type:'text'},
        {fid: 'username',title: '用户名',type:'text',sort:true},
        {fid:'password',title:'密码',type:'password',copy:true,eye_open:true},
        {
          title:'数据库位置',
          type: 'text',
          width: 116,
          template: function (row) {
            var type_column = '-'
            switch(row.db_type){
              case 0:
                type_column = '本地数据库'
                break;
              case 1:
                type_column = ('远程库('+row.conn_config.db_host+':'+row.conn_config.db_port+')').toString()
                break;
              case 2:
                $.each(cloudDatabaseList,function(index,item){
                  if(row.sid == item.id){
                    if(item.ps !== ''){ // 默认显示备注
                      type_column = item.ps
                    }else{
                      type_column = ('远程服务器('+item.db_host+':'+item.db_port+')').toString()
                    }
                  }
                })
                break;
            }
            return '<span class="flex" style="width:100px" title="'+type_column+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+type_column+'</span></span>'
          }
        },
        {
          fid: 'ps',
          title: '备注',
          type: 'input',
          blur: function (row, index, ev) {
            bt.pub.set_data_ps({
              id: row.id,
              table: 'databases',
              ps: ev.target.value
            }, function (res) {
              layer.msg(res.msg, (res.status ? {} : {
                icon: 2
              }));
            });
          },
          keyup: function (row, index, ev) {
            if (ev.keyCode === 13) {
              $(this).blur();
            }
          }
        },
        {
          type: 'group',
          title: '操作',
          width: 220,
          align: 'right',
          group: [{
            title: '改密',
            tips: '修改数据库密码',
            hide:function(rows){return rows.db_type == 1},
            event: function (row) {
              database.set_data_pass(row.id, row.username, row.password);
            }
          }, {
            title: '删除',
            tips: '删除数据库',
            event: function (row) {
              database.del_database(row.id, row.name,row, function (res) {
                if (res.status) database_table.$refresh_table_list(true);
                layer.msg(res.msg, {
                  icon: res.status ? 1 : 2
                })
              });
            }
          }]
        }
      ],
      sortParam: function (data) {
        return {
          'order': data.name + ' ' + data.sort
        };
      },
      tootls: [{ // 按钮组
        type: 'group',
        positon: ['left', 'top'],
        list: [{
          title: '添加数据库',
          active: true,
          event: function () {
            var cloudList = []
            $.each(cloudDatabaseList,function(index,item){
              var _tips = item.ps != ''?(item.ps+' ('+item.db_host+')'):item.db_host
              cloudList.push({title:_tips,value:item.id})
            })
            bt.database.add_database(cloudList,function (res) {
              if (res.status) database_table.$refresh_table_list(true);
            })
          }
        },{
          title:'远程服务器',
          event:function(){
            db_public_fn.get_cloud_server_list();
          }
        },{
          title: '同步所有',
          style:{'margin-left':'30px'},
          event: function () {
            database.sync_to_database({type:0,data:[]},function(res){
              if(res.status) database_table.$refresh_table_list(true);
            })
          }
        },{
          title: '从服务器获取',
          event: function () {
            var _list = [];
            $.each(cloudDatabaseList,function (index,item){
              var _tips = item.ps != ''?(item.ps+' (服务器地址:'+item.db_host+')'):item.db_host
              _list.push({title:_tips,value:item.id})
            })
            bt_tools.open({
              title:'选择数据库位置',
              area:'450px',
              btn: ['确认','取消'],
              skin: 'databaseCloudServer',
              content: {
                'class':'pd20',
                form:[{
                  label:'数据库位置',
                  group:{
                    type:'select',
                    name:'sid',
                    width:'260px',
                    list:_list
                  }
                }]
              },
              success:function(layers){
                $(layers).find('.layui-layer-content').css('overflow','inherit')
              },
              yes:function (form,layers,index){
                bt.database.sync_database(form.sid,function (rdata) {
                  if (rdata.status){
                    database_table.$refresh_table_list(true);
                    layer.close(layers)
                  }
                })
              }
            })
          }
        }]
      },{
        type: 'batch', //batch_btn
        positon: ['left', 'bottom'],
        placeholder: '请选择批量操作',
        buttonValue: '批量操作',
        disabledSelectValue: '请选择需要批量操作的数据库!',
        selectList: [{
          title:'同步选中',
          url:'/database/'+bt.data.db_tab_name+'/SyncToDatabases',
          paramName: 'data', //列表参数名,可以为空
          th:'数据库名称',
          beforeRequest: function(list) {
            var arry = [];
            $.each(list, function (index, item) {
              arry.push(item.id);
            });
            return JSON.stringify({ids:JSON.stringify(arry),type:1})
          },
          success: function (res, list, that) {
            layer.closeAll();
            var html = '';
            $.each(list, function (index, item) {
              html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (res.status ? '#20a53a' : 'red') + '">' + res.msg + '</span></div></td></tr>';
            });
            that.$batch_success_table({
              title: '批量同步选中',
              th: '数据库名称',
              html: html
            });
          }
        },{
          title: "删除数据库",
          url: '/database/'+bt.data.db_tab_name+'/DeleteDatabase',
          load: true,
          param: function (row) {
            return {data:JSON.stringify({
                id: row.id,
                name: row.name
              })}
          },
          callback: function (that) { // 手动执行,data参数包含所有选中的站点
            var ids = [];
            for (var i = 0; i < that.check_list.length; i++) {
              ids.push(that.check_list[i].id);
            }
            database.del_database(ids,function(param){
              that.start_batch(param, function (list) {
                layer.closeAll()
                var html = '';
                for (var i = 0; i < list.length; i++) {
                  var item = list[i];
                  html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + item.request.msg + '</span></div></td></tr>';
                }
                database_table.$batch_success_table({
                  title: '批量删除',
                  th: '数据库名称',
                  html: html
                });
                database_table.$refresh_table_list(true);
              });
            })
          }
        }]
      }, {
        type: 'search',
        positon: ['right', 'top'],
        placeholder: '请输入数据库名称/备注',
        searchParam: 'search', //搜索请求字段，默认为 search
        value: '',// 当前内容,默认为空
      }, { //分页显示
        type: 'page',
        positon: ['right', 'bottom'], // 默认在右下角
        pageParam: 'p', //分页请求字段,默认为 : p
        page: 1, //当前分页 默认：1
        numberParam: 'limit', //分页数量请求字段默认为 : limit
        number: 20, //分页数量默认 : 20条
        numberList: [10, 20, 50, 100, 200], // 分页显示数量列表
        numberStatus: true, //　是否支持分页数量选择,默认禁用
        jump: true, //是否支持跳转分页,默认禁用
      }],
      success:function(config){
        //搜索前面新增数据库位置下拉
        if($('.sqlserver_type_select_filter').length == 0){
          var _option = '<option value="all">全部</option>'
          $.each(cloudDatabaseList,function(index,item){
            var _tips = item.ps != ''?item.ps:item.db_host
            _option +='<option value="'+item.id+'">'+_tips+'</option>'
          })
          $('#bt_sqldatabase_table .bt_search').before('<select class="bt-input-text mr5 sqlserver_type_select_filter" style="width:110px" name="db_type_filter">'+_option+'</select>')

          //事件
          $('.sqlserver_type_select_filter').change(function(){
            database_table.$refresh_table_list(true);
          })
        }
      }
    });
  }
}

var mongodb = {
  database_table_view :function(search){
    var param = {
      table: 'databases',
      search: search || ''
    }
    $('#bt_mongodb_table').empty();
    database_table = bt_tools.table({
      el: '#bt_mongodb_table',
      url: 'database/mongodb/get_list',
      param: param, //参数
      minWidth: '1000px',
      load: true,
      autoHeight: true,
      default: "数据库列表为空", // 数据为空时的默认提示
      pageName: 'database',
      beforeRequest:function(beforeData){
        var db_type_val = $('.mongodb_type_select_filter').val()
        switch(db_type_val){
          case 'all':
            delete param['db_type']
            delete param['sid']
            break;
          case 0:
            param['db_type'] = 0;
            break;
          default:
            delete param['db_type'];
            param['sid'] = db_type_val
        }
        if (beforeData.hasOwnProperty('data') && typeof beforeData.data === 'string') {
          delete beforeData['data']
          return { data: JSON.stringify($.extend(param,beforeData)) }
        }
        return {data:JSON.stringify(param)}
      },
      column:[
        {type: 'checkbox',width: 20},
        {fid: 'name',title: '数据库名',type:'text'},
        {fid: 'username',title: '用户名',type:'text',sort:true},
        {fid:'password',title:'密码',type:'password',copy:true,eye_open:true},
        {
          fid:'backup',
          title: '备份',
          width: 130,
          template: function (row) {
            var backup = '点击备份',
                _class = "bt_warning";
            if (row.backup_count > 0) backup = lan.database.backup_ok, _class = "bt_success";
            return '<span><a href="javascript:;" class="btlink ' + _class + '" onclick="database.database_detail('+row.id+',\''+row.name+'\')">' + backup + (row.backup_count > 0 ? ('(' + row.backup_count + ')') : '') + '</a> | ' +
                '<a href="javascript:database.input_database(\''+row.name+'\')" class="btlink">'+lan.database.input+'</a></span>';
          }
        },
        {
          title:'数据库位置',
          type: 'text',
          width: 116,
          template: function (row) {
            var type_column = '-'
            switch(row.db_type){
              case 0:
                type_column = '本地数据库'
                break;
              case 1:
                type_column = ('远程库('+row.conn_config.db_host+':'+row.conn_config.db_port+')').toString()
                break;
              case 2:
                $.each(cloudDatabaseList,function(index,item){
                  if(row.sid == item.id){
                    if(item.ps !== ''){ // 默认显示备注
                      type_column = item.ps
                    }else{
                      type_column = ('远程服务器('+item.db_host+':'+item.db_port+')').toString()
                    }
                  }
                })
                break;
            }
            return '<span class="flex" style="width:100px" title="'+type_column+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+type_column+'</span></span>'
          }
        },
        {
          fid: 'ps',
          title: '备注',
          type: 'input',
          blur: function (row, index, ev) {
            bt.pub.set_data_ps({
              id: row.id,
              table: 'databases',
              ps: ev.target.value
            }, function (res) {
              layer.msg(res.msg, (res.status ? {} : {
                icon: 2
              }));
            });
          },
          keyup: function (row, index, ev) {
            if (ev.keyCode === 13) {
              $(this).blur();
            }
          }
        },
        {
          type: 'group',
          title: '操作',
          width: 220,
          align: 'right',
          group: [{
            title: '改密',
            tips: '修改数据库密码',
            hide:function(rows){return rows.db_type == 1},
            event: function (row) {
              database.set_data_pass(row.id, row.username, row.password);
            }
          }, {
            title: '删除',
            tips: '删除数据库',
            event: function (row) {
              database.del_database(row.id, row.name,row, function (res) {
                if (res.status) database_table.$refresh_table_list(true);
                layer.msg(res.msg, {
                  icon: res.status ? 1 : 2
                })
              });
            }
          }]
        }
      ],
      sortParam: function (data) {
        return {
          'order': data.name + ' ' + data.sort
        };
      },
      tootls: [{ // 按钮组
        type: 'group',
        positon: ['left', 'top'],
        list: [{
          title: '添加数据库',
          active: true,
          event: function () {
            var cloudList = []
            $.each(cloudDatabaseList,function(index,item){
              var _tips = item.ps != ''?(item.ps+' ('+item.db_host+')'):item.db_host
              cloudList.push({title:_tips,value:item.id})
            })
            bt.database.add_database(cloudList,function (res) {
              if (res.status) database_table.$refresh_table_list(true);
            })
          }
        },{
          title: 'root密码',
          event: function () {
            if(mongoDBAccessStatus){
              bt.database.set_root('mongo')
            }else{
              layer.msg('请先开启安全认证',{icon:0})
            }
          }
        },{
          title: '安全认证',
          event: function () {
            layer.open({
              title:'安全认证开关',
              area:'250px',
              btn:false,
              content:'<div class="bt-form">\
								<div class="line">\
									<span class="tname">安全认证</span>\
									<div class="info-r">\
										<div class="inlineBlock mr50" style="margin-top: 5px;vertical-align: -6px;">\
											<input class="btswitch btswitch-ios" id="mongodb_access" type="checkbox" name="monitor">\
											<label class="btswitch-btn" for="mongodb_access" style="margin-bottom: 0;"></label>\
										</div>\
									</div>\
								</div>\
								<div class="line">\
									<div class="">\
									<div class="inlineBlock  ">\
									<ul class="help-info-text c7" style="margin-top:0;">\
										<li>安全认证：开启后访问数据需要使用帐号和密码</li>\
									</ul>\
								</div></div></div>\
							</div>',
              success:function(){
                $('#mongodb_access').attr('checked',mongoDBAccessStatus)

                $('#mongodb_access').click(function(){
                  var _status = $(this).prop('checked')
                  bt_tools.send({url:'database/'+bt.data.db_tab_name+'/set_auth_status',data:{data:JSON.stringify({status:_status?1:0})},verify: true},function(rdata){
                    if(rdata.status){
                      mongoDBAccessStatus = _status
                      layer.msg(rdata.msg,{icon:1})
                    }
                  },'设置密码访问状态')
                })
              }
            })
          }
        },{
          title:'远程服务器',
          event:function(){
            db_public_fn.get_cloud_server_list();
          }
        },{
          title: '同步所有',
          style:{'margin-left':'30px'},
          event: function () {
            database.sync_to_database({type:0,data:[]},function(res){
              if(res.status) database_table.$refresh_table_list(true);
            })
          }
        },{
          title: '从服务器获取',
          event: function () {
            var _list = [];
            $.each(cloudDatabaseList,function (index,item){
              var _tips = item.ps != ''?(item.ps+' (服务器地址:'+item.db_host+')'):item.db_host
              _list.push({title:_tips,value:item.id})
            })
            bt_tools.open({
              title:'选择数据库位置',
              area:'450px',
              btn: ['确认','取消'],
              skin: 'databaseCloudServer',
              content: {
                'class':'pd20',
                form:[{
                  label:'数据库位置',
                  group:{
                    type:'select',
                    name:'sid',
                    width:'260px',
                    list:_list
                  }
                }]
              },
              success:function(layers){
                $(layers).find('.layui-layer-content').css('overflow','inherit')
              },
              yes:function (form,layers,index){
                bt.database.sync_database(form.sid,function (rdata) {
                  if (rdata.status){
                    database_table.$refresh_table_list(true);
                    layer.close(layers)
                  }
                })
              }
            })
          }
        }]
      },{
        type: 'batch', //batch_btn
        positon: ['left', 'bottom'],
        placeholder: '请选择批量操作',
        buttonValue: '批量操作',
        disabledSelectValue: '请选择需要批量操作的数据库!',
        selectList: [{
          title:'同步选中',
          url:'/database/'+bt.data.db_tab_name+'/SyncToDatabases',
          paramName: 'data', //列表参数名,可以为空
          th:'数据库名称',
          beforeRequest: function(list) {
            var arry = [];
            $.each(list, function (index, item) {
              arry.push(item.id);
            });
            return JSON.stringify({ids:JSON.stringify(arry),type:1})
          },
          success: function (res, list, that) {
            layer.closeAll();
            var html = '';
            $.each(list, function (index, item) {
              html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (res.status ? '#20a53a' : 'red') + '">' + res.msg + '</span></div></td></tr>';
            });
            that.$batch_success_table({
              title: '批量同步选中',
              th: '数据库名称',
              html: html
            });
          }
        },{
          title: "删除数据库",
          url: '/database/'+bt.data.db_tab_name+'/DeleteDatabase',
          load: true,
          param: function (row) {
            return {data:JSON.stringify({
                id: row.id,
                name: row.name
              })}
          },
          callback: function (that) { // 手动执行,data参数包含所有选中的站点
            var ids = [];
            for (var i = 0; i < that.check_list.length; i++) {
              ids.push(that.check_list[i].id);
            }
            database.del_database(ids,function(param){
              that.start_batch(param, function (list) {
                layer.closeAll()
                var html = '';
                for (var i = 0; i < list.length; i++) {
                  var item = list[i];
                  html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + item.request.msg + '</span></div></td></tr>';
                }
                database_table.$batch_success_table({
                  title: '批量删除',
                  th: '数据库名称',
                  html: html
                });
                database_table.$refresh_table_list(true);
              });
            })
          }
        }]
      }, {
        type: 'search',
        positon: ['right', 'top'],
        placeholder: '请输入数据库名称/备注',
        searchParam: 'search', //搜索请求字段，默认为 search
        value: '',// 当前内容,默认为空
      }, { //分页显示
        type: 'page',
        positon: ['right', 'bottom'], // 默认在右下角
        pageParam: 'p', //分页请求字段,默认为 : p
        page: 1, //当前分页 默认：1
        numberParam: 'limit', //分页数量请求字段默认为 : limit
        number: 20, //分页数量默认 : 20条
        numberList: [10, 20, 50, 100, 200], // 分页显示数量列表
        numberStatus: true, //　是否支持分页数量选择,默认禁用
        jump: true, //是否支持跳转分页,默认禁用
      }],
      success:function(config){
        //搜索前面新增数据库位置下拉
        if($('.mongodb_type_select_filter').length == 0){
          var _option = '<option value="all">全部</option>'
          $.each(cloudDatabaseList,function(index,item){
            var _tips = item.ps != ''?item.ps:item.db_host
            _option +='<option value="'+item.id+'">'+_tips+'</option>'
          })
          $('#bt_mongodb_table .bt_search').before('<select class="bt-input-text mr5 mongodb_type_select_filter" style="width:110px" name="db_type_filter">'+_option+'</select>')

          //事件
          $('.mongodb_type_select_filter').change(function(){
            database_table.$refresh_table_list(true);
          })
        }
      }
    });
  }
}
var redis = {
  redisDBList:[],
  cloudInfo:{
    sid:0,
    title:'本地服务器'
  },  //当前远程信息
  database_table_view:function(){
    var that = this;
    this.cloudInfo.sid = 0
    $('#bt_redis_view').empty()

    $('#bt_redis_view').html('<div class="pull-right redis_cloud_server"></div>')

    // 远程服务器列表
    var _option = ''
    $.each(cloudDatabaseList,function(index,item){
      var _tips = item.ps != ''?item.ps:item.db_host
      _option +='<option value="'+item.id+'">'+_tips+'</option>'
    })
    $('#bt_redis_view .redis_cloud_server').html('<span class="mr5" style="color:#f0ad4e"><span class="glyphicon glyphicon-info-sign"></span>当前所有操作项都关联至</span><select class="bt-input-text mr5 redis_type_select_filter" style="width:110px" name="db_type_filter">'+_option+'</select>')

    //远程服务器列表点击事件
    $('.redis_type_select_filter').change(function(){
      that.cloudInfo.sid = $(this).val();
      that.cloudInfo.title = $(this).find('option:selected').text();
      that.render_redis_content()
    })


    // 渲染redis列表
    this.render_redis_content()
  },
  render_redis_content:function(id){
    $('.redis_content_view').remove()
    var that = this;
    $('#bt_redis_view').append('<div class="redis_content_view">\
		<button type="button" title="添加Key" class="btn btn-success btn-sm mr5 addRedisDB" style="margin-bottom:10px"><span>添加Key</span></button>\
		<button type="button" title="远程服务器" class="btn btn-default btn-sm mr5 RedisCloudDB" style="margin-bottom:10px"><span>远程服务器</span></button>\
		<button type="button" title="备份列表" class="btn btn-default btn-sm mr5 backupRedis" style="margin-bottom:10px;display:'+(this.cloudInfo.sid == 0?'inline-block':'none')+'"><span>备份列表</span></button>\
		<button type="button" title="清空数据库" class="btn btn-default btn-sm emptyRedisDB" style="margin:0 0 10px 30px"><span>清空数据库</span></button>\
		<div id="redis_content_tab"><div class="tab-nav"></div><div class="tab-con redis_table_content" style="padding:10px 0"></div></div></div>')
    var tabHTML = ''
    bt_tools.send({url:'database/redis/get_list',data:{data:JSON.stringify({sid:that.cloudInfo.sid})}},function(rdata){
      that.redisDBList = rdata;
      $.each(rdata,function(index,item){
        tabHTML +='<span data-id="'+item.id+'">'+item.name+'('+item.keynum+')</span>'
      })
      $('#redis_content_tab .tab-nav').html(tabHTML)


      setTimeout(function(){
        if(id){
          $('#redis_content_tab .tab-nav span:contains(DB'+id+')').click()
        }else{
          if(rdata.length == 0){
            $('#redis_content_tab .tab-nav').remove()
            that.render_redis_table(0)
          }else{
            $('#redis_content_tab .tab-nav span:eq(0)').click()
          }
        }
      },50)

      $('.addRedisDB').click(function(){
        that.set_redis_library()
      })
      $('.backupRedis').click(function(){
        that.backup_redis_list()
      })
      $('.emptyRedisDB').click(function(){
        that.choose_redis_list()
      })
      $('.RedisCloudDB').click(function(){
        db_public_fn.get_cloud_server_list()
      })

      // redis数据库点击事件
      $('#redis_content_tab .tab-nav span').click(function(){
        var _id = $(this).data('id');
        $(this).addClass('on').siblings().removeClass('on')
        that.render_redis_table(_id)
      })
    })
  },
  render_redis_table:function(id){
    var that = this;
    $('.redis_table_content').empty();
    database_table = bt_tools.table({
      el: '.redis_table_content',
      url: 'database/redis/get_db_keylist',
      param: {db_idx:id}, //参数
      minWidth: '1000px',
      autoHeight: true,
      load: true,
      default: "数据库列表为空", // 数据为空时的默认提示
      pageName: 'database',
      beforeRequest:function(beforeData){
        var db_type_val = that.cloudInfo.sid,param = {}
        switch(db_type_val){
          case 0:
            param['db_type'] = 0;
            break;
          default:
            delete param['db_type'];
            param['sid'] = db_type_val
        }
        if (beforeData.hasOwnProperty('data') && typeof beforeData.data === 'string') {
          delete beforeData['data']
          return { data: JSON.stringify($.extend(param,{db_idx:id},beforeData)) }
        }
        return {data:JSON.stringify($.extend(param,{db_idx:id,limit:beforeData.limit}))}
      },
      column:[
        {type: 'checkbox',width: 20},
        {fid: 'name',title: '键',type:'text'},
        {fid: 'val',title: '值',type:'text',template:function(row){
            var _val = $('<div></div>').text(row.val)
            return '<div class="flex" style="width:350px" title="'+_val.html()+'"><span class="size_ellipsis">'+_val.html()+'</span><span class="ico-copy cursor btcopy ml5" title="复制密码"></span></div>'
          },event:function(row,index,ev,key){
            if($(ev.target).hasClass('btcopy')){
              bt.pub.copy_pass(row.val);
            }
          }},
        {fid:'type',title:'数据类型',type:'text'},
        {fid:'len',title:'数据长度',type:'text'},
        {fid:'endtime',title:'有效期',type:'text',template: function (row) {
            return that.reset_time_format(row.endtime)
          }},
        {
          type: 'group',
          title: '操作',
          width: 220,
          align: 'right',
          group: [{
            title: '编辑',
            tips: '编辑数据',
            hide: function(rows){
              return (rows.type == 'string' || rows.type == 'int')?false:true
            },
            event: function (row) {
              that.set_redis_library(row)
            }
          },{
            title: '删除',
            tips: '删除数据',
            event: function (row) {
              layer.confirm('是否删除【'+row.name+'】', {
                title: '删除key值', closeBtn: 2, icon: 0
              }, function (index) {
                bt_tools.send({url:'database/redis/del_redis_val',data:{data:JSON.stringify({db_idx:id,key:row.name,sid:that.cloudInfo.sid})}},function(rdata){
                  if(rdata.status){
                    that.render_redis_table(id);
                  }
                  bt_tools.msg(rdata)
                  layer.close(index)
                })
              });
            }
          }]
        }
      ],
      tootls: [{
        type: 'search',
        positon: ['right', 'top'],
        placeholder: '请输入键名称',
        searchParam: 'search', //搜索请求字段，默认为 search
        value: '',// 当前内容,默认为空
      }, { //分页显示
        type: 'page',
        positon: ['right', 'bottom'], // 默认在右下角
        pageParam: 'p', //分页请求字段,默认为 : p
        page: 1, //当前分页 默认：1
        numberParam: 'limit', //分页数量请求字段默认为 : limit
        number: 20, //分页数量默认 : 20条
        numberList: [10, 20, 50, 100, 200], // 分页显示数量列表
        numberStatus: true, //　是否支持分页数量选择,默认禁用
        jump: true, //是否支持跳转分页,默认禁用
      }],
      success: function () {
        var arry = [],maxWidth = ''
        for (var i = 0; i < $('.size_ellipsis').length; i++) {
          arry.push($('.size_ellipsis').eq(i).width())
        }
        maxWidth = Math.max.apply(null,arry)
        $('.size_ellipsis').width(maxWidth)
      }
    });
  },
  // redis备份列表
  backup_redis_list:function(){
    var that = this,redisBackupTable = null;
    bt_tools.open({
      title:'Redis备份列表',
      area:['927px','633px'],
      btn: false,
      skin: 'redisBackupList',
      content: '<div id="redisBackupTable" class="pd20" style="padding-bottom:40px;"></div>',
      success:function(){
        redisBackupTable = bt_tools.table({
          el:'#redisBackupTable',
          default:'备份列表为空',
          height:478,
          url: 'database/redis/get_backup_list',
          column:[{
            fid:'name',
            title:'名称',
            width: 170,
            template: function (item) {
              return '<span class="flex" style="width:154px" title="'+item.name+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+item.name+'</span></span>'
            }},
            {
              fid:'filepath',
              title:'路径',
              template: function (item) {
                return '<span class="flex" style="width:280px" title="'+item.filepath+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+item.filepath+'</span></span>'
              }},
            {fid:'mtime',width:137,title:'备份时间',template:function(row){
                return '<span>'+bt.format_data(row.mtime)+'</span>'
              }},
            {fid:'size',title:'大小',template:function(row){
                return '<span>'+bt.format_size(row.size)+'</span>'
              }},
            {fid:'sid',width:78,title:'备份位置',template:function(row){
                var type_column = '-'
                switch(row.sid){
                  case "0":
                    type_column = '本地数据库'
                    break;
                  case "1":
                    type_column = ('远程库('+row.conn_config.db_host+':'+row.conn_config.db_port+')').toString()
                    break;
                  case "2":
                    $.each(cloudDatabaseList,function(index,item){
                      if(row.sid == item.id){
                        if(item.ps !== ''){ // 默认显示备注
                          type_column = item.ps
                        }else{
                          type_column = ('远程服务器('+item.db_host+':'+item.db_port+')').toString()
                        }
                      }
                    })
                    break;
                }
                return '<span class="flex" style="width:100px" title="'+type_column+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+type_column+'</span></span>'
              }},
            {
              type: 'group',
              title: '操作',
              align: 'right',
              group: [{
                title:'恢复',
                event:function(row){
                  bt.prompt_confirm('覆盖数据', '即将使用【'+row.name+'】对数据进行覆盖，是否继续?', function () {
                    bt_tools.send({url:'database/redis/InputSql',data:{data:JSON.stringify({file:row.filepath,sid:0})}},function(rdata){
                      if(rdata.status) that.render_redis_content();
                      bt_tools.msg(rdata)
                    },'恢复数据')
                  })
                }
              },{
                title:'删除',
                event:function(row){
                  layer.confirm('是否删除【'+row.name+'】备份', {
                    title: '删除备份', closeBtn: 2, icon: 0
                  }, function (index) {
                    bt_tools.send({url:'database/redis/DelBackup',data:{data:JSON.stringify({file:row.filepath})}},function(rdata){
                      if(rdata.status) redisBackupTable.$refresh_table_list(true);
                      bt_tools.msg(rdata)
                      layer.close(index)
                    },'删除备份')
                  });
                }
              }]
            }
          ],
          tootls:[{
            type:'group',
            positon: ['left','top'],
            list:[{
              title:'立即备份',
              active: true,
              event:function(){
                bt_tools.send({url:'database/redis/ToBackup'},function(rdata){
                  if(rdata.status) redisBackupTable.$refresh_table_list(true);
                  bt_tools.msg(rdata)
                })
              }
            }]
          }]
        })
      }
    })
  },
  // 添加/编辑redis库
  set_redis_library:function(row){
    var that = this,
        redis_form = null,
        cloudList = []
    $.each(cloudDatabaseList,function(index,item){
      var _tips = item.ps != ''?(item.ps+' ('+item.db_host+')'):item.db_host
      cloudList.push({title:_tips,value:item.id})
    })
    bt_tools.open({
      title:(row?('编辑['+row.name+']'):'添加')+'Key'+(!row?('至【'+this.cloudInfo.title+'】'):''),
      area:'400px',
      btn:[(row?'保存':'添加'),'取消'],
      content: '<div class="ptb20" id="redis_library_form"></div>',
      success: function (layers) {
        redis_form = bt_tools.form({
          el:'#redis_library_form',
          form: [{
            label:'数据库',
            group:{
              type:'select',
              name:'db_idx',
              width:'260px',
              list:[
                {title:'DB0',value:0},
                {title:'DB1',value:1},
                {title:'DB2',value:2},
                {title:'DB3',value:3},
                {title:'DB4',value:4},
                {title:'DB5',value:5},
                {title:'DB6',value:6},
                {title:'DB7',value:7},
                {title:'DB8',value:8},
                {title:'DB9',value:9},
                {title:'DB10',value:10},
                {title:'DB11',value:11},
                {title:'DB12',value:12},
                {title:'DB13',value:13},
                {title:'DB14',value:14},
                {title:'DB15',value:15}
              ],
              disabled:row?true:false,
            }
          },{
            label:'键',
            group:{
              type:'text',
              name:'name',
              width:'260px',
              placeholder:'请输入键(key)',
              disabled:row?true:false,
            }
          },{
            label:'值',
            group:{
              type:'text',
              name:'val',
              width:'260px',
              placeholder:'请输入值',
            }
          },{
            label:'有效期',
            group:{
              type:'number',
              name:'endtime',
              width:'235px',
              placeholder:'为空则永不过期',
              unit:'秒'
            }
          },{
            group: {
              type: 'help',
              style: { 'margin-left': '30px' },
              list: ['有效期为0表示永久']
            }
          }],
          data:row?row:{db_idx:$('#redis_content_tab .tab-nav span.on').data('id')}
        })
      },
      yes:function(indexs){
        var formValue = redis_form.$get_form_value()
        if(formValue.name == '') return layer.msg('键不能为空')
        if(formValue.val == '') return layer.msg('值不能为空')
        if(formValue.endtime <= 0) delete formValue.endtime
        if(row){
          formValue['db_idx'] = $('#redis_content_tab .tab-nav span.on').data('id')
        }
        formValue['sid'] = that.cloudInfo.sid
        bt_tools.send({url:'database/redis/set_redis_val',data:{data:JSON.stringify(formValue)}},function(res){
          if(res.status){
            layer.close(indexs);
            that.render_redis_content(formValue.db_idx)
          }
          bt_tools.msg(res)
        },(row?'保存':'添加')+'redis数据中')
      }
    })
  },
  //选择需要清空的redis库
  choose_redis_list:function(){
    var that = this;
    layer.open({
      type:1,
      area:'400px',
      title:'清空【'+this.cloudInfo.title+'】数据库',
      shift: 5,
      closeBtn: 2,
      shadeClose: false,
      btn:['确认','取消'],
      content:'<div class="bt-form pd20" id="choose_redis_from">\
					<div class="line"><span class="tname">选择数据库</span>\
						<div class="info-r">\
							<div class="rule_content_list">\
								<div class="rule_checkbox_group" bt-event-click="checkboxMysql" bt-event-type="active_all"><input name="*" type="checkbox" style="display: none;">\
									<div class="bt_checkbox_groups active"></div>\
									<span class="rule_checkbox_title">全部选中</span></div>\
								<ul class="rule_checkbox_list"></ul>\
							</div>\
						</div>\
					</div>\
				</div>',
      success:function(layers,index){
        var rule_site_list = '';
        $.each(that.redisDBList,function(index,item){
          rule_site_list += '<li>'
              +'<div class="rule_checkbox_group" bt-event-click="checkboxMysql" bt-event-type="active">'
              +'<span class="glyphicon glyphicon-menu-right" style="display:none" aria-hidden="true" bt-event-click="checkboxMysql" bt-event-type="fold"></span>'
              +'<input name="'+ item.name +'" type="checkbox" data-id="'+item.id+'" checked=checked style="display: none;">'
              +'<div class="bt_checkbox_groups active"></div>'
              +'<span class="rule_checkbox_title">'+ item.name +'</span>'
              +'</div>'
              +'</li>'
          $('.rule_checkbox_list').html(rule_site_list);
          that.event_bind()
        });
      },
      yes:function(index,layers){
        var redisIDList = [];
        $('#choose_redis_from .rule_checkbox_list input').each(function(index,el){
          if($(this).prop('checked')){
            redisIDList.push($(this).data('id'))
          }
        });
        if(redisIDList.length == 0)return layer.msg('请选择需要删除的数据库',{icon:2})
        layer.confirm('清空后数据将无法恢复,是否继续?', {
          title: '清空数据库', closeBtn: 2, icon: 0
        }, function (index) {
          bt_tools.send({url:'database/redis/clear_flushdb',data:{data:JSON.stringify({ids:JSON.stringify(redisIDList),sid:that.cloudInfo.sid})}},function(rdata){
            if(rdata.status){
              that.render_redis_content();
              layer.closeAll()
            }
            bt_tools.msg(rdata)
          })
        });

      }
    })
  },

  event_bind:function(){
    $('.rule_checkbox_group').unbind('click').click(function(ev){
      var _type = $(this).attr('bt-event-type'), _checkbox = '.bt_checkbox_groups';
      switch (_type) {
        case 'active_all'://选中全部
          var thatActive = $(this).find(_checkbox), thatList = $(this).next();
          if (thatActive.hasClass('active')) {
            thatActive.removeClass('active').prev().prop('checked', false);
            thatList.find(_checkbox).removeClass('active').prev().prop('checked', false);
          } else {
            thatActive.addClass('active').prev().prop('checked', true);
            thatList.find(_checkbox).addClass('active').prev().prop('checked', true);
          }
          break;
        case 'active': //激活选中和取消
          var thatActive = $(this).find(_checkbox), thatList = $(this).next();
          if (thatActive.hasClass('active')) {
            thatActive.removeClass('active').prev().prop('checked', false);
            $('.mysql_content_list>.mysql_checkbox_group input').prop('checked', false).next().removeClass('active');
            if (thatList.length == 1) {
              thatList.find(_checkbox).removeClass('active').prev().prop('checked', false);
            } else {
              var nodeLength = $(this).parent().siblings().length + 1,
                  nodeList = $(this).parent().parent();
              if (nodeList.find('.bt_checkbox_groups.active').length != nodeLength) {
                nodeList.prev().find(_checkbox).removeClass('active').prev().prop('checked', false);
              }
            }
          } else {
            thatActive.addClass('active').prev().prop('checked', true);
            if (thatList.length == 1) {
              thatList.find(_checkbox).addClass('active').prev().prop('checked', true);
            } else {
              var nodeLength = $(this).parent().siblings().length + 1,
                  nodeList = $(this).parent().parent();
              if (nodeList.find('.bt_checkbox_groups.active').length == nodeLength) {
                nodeList.prev().find(_checkbox).addClass('active').prev().prop('checked', true);
              }
            }
          }
          break;
        case 'fold': //折叠数据库列表
          if ($(this).hasClass('glyphicon-menu-down')) {
            $(this).removeClass('glyphicon-menu-down').addClass('glyphicon-menu-right').parent().next().hide();
          } else {
            $(this).removeClass('glyphicon-menu-rigth').addClass('glyphicon-menu-down').parent().next().show();
          }
          break;
      }
      $('.rule_content_list').removeAttr('style');
      ev.stopPropagation();
    })
  },
  //重置时间格式
  reset_time_format:function(time){
    if(time == 0) return '永久'
    var theTime = parseInt(time);// 秒
    var middle= 0;// 分
    var hour= 0;// 小时

    if(theTime > 60) {
      middle= parseInt(theTime/60);
      theTime = parseInt(theTime%60);
      if(middle> 60) {
        hour= parseInt(middle/60);
        middle= parseInt(middle%60);
      }
    }
    var result = ""+parseInt(theTime)+"秒";
    if(middle > 0) {
      result = ""+parseInt(middle)+"分"+result;
    }
    if(hour> 0) {
      result = ""+parseInt(hour)+"小时"+result;
    }
    return result;
  }
}

var db_public_fn = {
  // 远程服务器列表
  get_cloud_server_list:function(){
    var that = this;
    bt_tools.open({
      title:bt.data.db_tab_name+'远程服务器列表',
      area:'860px',
      btn: false,
      skin: 'databaseCloudServer',
      content: '<div id="db_cloud_server_table" class="pd20" style="padding-bottom:40px;"></div>',
      success:function(){
        var tdHTML = [{
          fid:'db_host',
          title:'服务器地址',
          width: 170,
          template: function (item) {
            return '<span class="flex" style="width:154px" title="'+item.db_host+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+item.db_host+'</span></span>'
          }
        },
          {fid:'db_port',width:80,title:'数据库端口'},
          {fid:'db_type',width:80,title:'数据库类型'},
          {
            fid:'db_user',
            width:100,
            title:'管理员名称'
          },
          {fid:'db_password',type: 'password',title:'管理员密码',copy: true,eye_open: true},
          {fid:'ps',title:'备注',width:160,template: function (item) {
              return '<span class="flex" style="width:144px" title="'+item.ps+'"><span class="size_ellipsis" style="width: 0; flex: 1;">'+item.ps+'</span></span>'
            }},
          {
            type: 'group',
            width: 100,
            title: '操作',
            align: 'right',
            group: [{
              title:'编辑',
              hide:function (row) {
                return row.id == 0
              },
              event:function(row){
                that.render_db_cloud_server_view(row,true);
              }
            },{
              title:'删除',
              hide:function (row) {
                return row.id == 0
              },
              event:function(row){
                that.del_db_cloud_server(row)
              }
            }]
          }
        ]
        if(bt.data.db_tab_name == 'redis') tdHTML.splice(3,1)
        dbCloudServerTable = bt_tools.table({
          el:'#db_cloud_server_table',
          default:'服务器列表为空',
          data: [],
          column:tdHTML,
          tootls:[{
            type:'group',
            positon: ['left','top'],
            list:[{
              title:'添加远程服务器',
              active: true,
              event:function(){that.render_db_cloud_server_view()}
            }]
          }]
        })
        that.render_cloud_server_table();
      }
    })
  },
  // 重新渲染远程服务器
  render_cloud_server_table: function (callback) {
    var param = {url:'database/'+bt.data.db_tab_name+'/GetCloudServer',data:{data:JSON.stringify({type:bt.data.db_tab_name})}}
    if(bt.data.db_tab_name == 'mysql') param = {url:'database?action=GetCloudServer',data:{type:bt.data.db_tab_name}}
    bt_tools.send(param,function(rdata){
      var arry = []
      for (var i = 0; i < rdata.length; i++) {
        var element = rdata[i];
        if(element.id == 0) continue
        arry.push(element)
      }
      dbCloudServerTable.$reader_content(arry);
      if(callback) callback(rdata)
    });
  },
  // 添加/编辑远程服务器视图
  render_db_cloud_server_view:function(config,is_edit){
    var that = this;
    if(!config) config = {db_host:'',db_port:'3306',db_user:'',db_password:'',db_user:'root',ps:''}
    if(bt.data.db_tab_name == 'sqlserver'){
      config['db_port'] = 1433
      config['db_user'] = 'sa'
    }else if(bt.data.db_tab_name == 'redis'){
      config['db_port'] = 6379
      config['db_user'] = ''
    }else if(bt.data.db_tab_name == 'mongodb'){
      config['db_port'] = 27017
    }
    bt_tools.open({
      title: (is_edit?'编辑':'添加')+bt.data.db_tab_name+'远程服务器',
      area:'450px',
      btn:['保存','取消'],
      skin:'addCloudServerProject',
      content:{
        'class':'pd20',
        form:[{
          label:'服务器地址',
          group:{
            type:'text',
            name:'db_host',
            width:'260px',
            value:config.db_host,
            placeholder:'请输入服务器地址',
            event:function(){
              $('[name=db_host]').on('input',function(){
                $('[name=db_ps]').val($(this).val())
              })
            }
          }
        },{
          label:'数据库端口',
          group:{
            type:'number',
            name:'db_port',
            width:'260px',
            value:config.db_port,
            placeholder:'请输入数据库端口'
          }
        },{
          label:'管理员名称',
          hide:bt.data.db_tab_name == 'redis'?true:false,
          group:{
            type:'text',
            name:'db_user',
            width:'260px',
            value:config.db_user,
            placeholder:'请输入管理员名称',
          }
        },{
          label:'管理员密码',
          group:{
            type:'text',
            name:'db_password',
            width:'260px',
            value:config.db_password,
            placeholder:'请输入管理员密码'
          }
        },{
          label:'备注',
          group:{
            type:'text',
            name:'db_ps',
            width:'260px',
            value:config.ps,
            placeholder:'服务器备注'
          }
        },{
          group:{
            type:'help',
            style:{'margin-top':'0'},
            list:[
              '支持MySQL5.5、MariaDB10.1及以上版本',
              '支持阿里云、腾讯云等云厂商的云数据库',
              '注意1：请确保本服务器有访问数据库的权限',
              '注意2：请确保填写的管理员帐号具备足够的权限'
            ]
          }
        }]
      },
      success:function(){
        if(bt.data.db_tab_name != 'mysql') $('.addCloudServerProject .help-info-text li').eq(0).remove();
      },
      yes:function(form,indexs){
        var interface = is_edit?'ModifyCloudServer':'AddCloudServer'
        if(form.db_host == '') return layer.msg('请输入服务器地址',{icon:2})
        if(form.db_port == '') return layer.msg('请输入数据库端口',{icon:2})
        if(form.db_user == '' && bt.data.db_tab_name != 'redis') return layer.msg('请输入管理员名称',{icon:2})
        if(form.db_password == '') return layer.msg('请输入管理员密码',{icon:2})

        if(is_edit) form['id'] = config['id'];
        form['type'] = bt.data.db_tab_name
        that.layerT = bt.load('正在'+(is_edit?'修改':'创建')+'远程服务器,请稍候...');

        var param = {url:'database/'+bt.data.db_tab_name+'/'+interface,data:{data:JSON.stringify(form)}}
        if(bt.data.db_tab_name == 'mysql') param = {url:'database?action='+interface,data:form}
        bt_tools.send(param,function(rdata){
          that.layerT.close();
          if(rdata.status){
            that.reset_server_config()
            layer.close(indexs)
            layer.msg(rdata.msg, {icon:1})
          }else{
            layer.msg(rdata.msg,{time:0,icon:2,closeBtn: 2, shade: .3,area: '650px'})
          }
        })
      }
    })
  },
  // 删除远程服务器管理关系
  del_db_cloud_server: function(row){
    var that = this;
    layer.confirm('仅删除管理关系以及面板中的数据库记录，不会删除远程服务器中的数据', {
      title: '删除【'+row.db_host+'】远程服务器',
      icon: 0,
      closeBtn: 2
    }, function () {
      var param = {url:'database/'+bt.data.db_tab_name+'/RemoveCloudServer',data:{data:JSON.stringify({id:row.id})}}
      if(bt.data.db_tab_name == 'mysql') param = {url:'database?action=RemoveCloudServer',data:{id:row.id}}
      bt_tools.send(param,function(rdata){
        if(rdata.status) that.reset_server_config()
        layer.msg(rdata.msg, {
          icon: rdata.status ? 1 : 2
        })
      })
    })
  },
  // 重新加载服务
  reset_server_config:function(){
    this.render_cloud_server_table(function(){
      if(bt.data.db_tab_name == 'redis') redis.cloudInfo.sid = 0  //redis恢复默认是本地服务器
      $('.database-pos .tabs-item[data-type="' + bt.data.db_tab_name + '"]').trigger('click');
    });
  }
}
$('.database-pos .tabs-item[data-type="' + (bt.get_cookie('db_page_model') || 'mysql') + '"]').trigger('click');