var backupListAll = [], siteListAll = [], databaseListAll = [], allDatabases = [],allTables = [],
    backuptolist = [{ title: '服务器磁盘', value: 'localhost' },
      { title: '阿里云OSS', value: 'alioss' },
      { title: '腾讯云COS', value: 'txcos' },
      { title: '七牛云存储', value: 'qiniu' },
      { title: '华为云存储', value: 'obs' },
      { title: '百度云存储', value: 'bos' }];
var crontab = {
  typeTips: { site: '备份网站', database: '备份数据库', logs: '切割日志', path: '备份目录', webshell: '查杀站点' },
  crontabForm: { name: '', type: '', where1: '', hour: '', minute: '', week: '', sType: '', sBody: '', sName: '', backupTo: '', save: '', sBody: '', urladdress: '', save_local: '', notice: '', notice_channel: '' , datab_name : '',tables_name :'' },
  editForm: false,
  crontabFormConfig: [{
    label: '任务类型',
    group: {
      type: 'select',
      name: 'sType',
      width: '140px',
      value: 'toShell',
      list: [
        { title: 'Shell脚本', value: 'toShell' },
        { title: '备份网站', value: 'site' },
        { title: '备份数据库', value: 'database' },
        { title: '数据库增量备份', value: 'enterpriseBackup' },
        { title: '日志切割', value: 'logs' },
        { title: '备份目录', value: 'path' },
        { title: '木马查杀', value: 'webshell' },
        { title: '同步时间', value: 'syncTime' },
        { title: '释放内存', value: 'rememory' },
        { title: '访问URL', value: 'toUrl' }
      ],
      unit: '<span style="margin-top: 9px; display: inline-block;"><i style="color: red;font-style: initial;font-size: 12px;margin-right: 5px">*</i>任务类型包含以下部分：Shell脚本、备份网站、备份数据库、日志切割、释放内存、访问URL、备份目录、木马查杀、同步时间</span>',
      change: function (formData, element, that) {
        that.data.type = 'week'   //默认类型为每星期
        var config = crontab.crontabsType(arryCopy(crontab.crontabFormConfig), formData, that)
        that.$again_render_form(config)
        var arry = ['site', 'database', 'logs', 'webshell', 'enterpriseBackup'];
        if (arry.indexOf(formData.sType) > -1) {
          that.$replace_render_content(3)
          setTimeout(function () {
            $('[data-name="sName"] li:eq(0)').click()
          }, 100)
        }
        if (formData.sType === 'enterpriseBackup') {
          console.log('---')
          $('.glyphicon-repeat').on('click',function(){
            that.config.form[6].group.value = bt.get_random(bt.get_random_num(6,10))
            that.$local_refresh('urladdress', that.config.form[6].group)
            $('input[name=urladdress]').click()
          })
        }
      }
    }
  }, {
    label: '任务名称',
    group: {
      type: 'text',
      name: 'name',
      width: '350px',
      placeholder: '请输入计划任务名称'
    }
  }, {
    label: '执行周期',
    group: [{
      type: 'select',
      name: 'type',
      value: 'week',
      list: [
        { title: '每天', value: 'day' },
        { title: 'N天', value: 'day-n' },
        { title: '每小时', value: 'hour' },
        { title: 'N小时', value: 'hour-n' },
        { title: 'N分钟', value: 'minute-n' },
        { title: '每星期', value: 'week' },
        { title: '每月', value: 'month' }
      ],
      change: function (formData, element, that) {
        crontab.crontabType(that.config.form, formData)
        that.$replace_render_content(2)
      }
    }, {
      type: 'select',
      name: 'week',
      value: '1',
      list: [
        { title: '周一', value: '1' },
        { title: '周二', value: '2' },
        { title: '周三', value: '3' },
        { title: '周四', value: '4' },
        { title: '周五', value: '5' },
        { title: '周六', value: '6' },
        { title: '周日', value: '0' }
      ]
    }, {
      type: 'number',
      display: false,
      name: 'where1',
      'class': 'group',
      width: '70px',
      value: '3',
      unit: '日',
      min: 1,
      max: 31
    }, {
      type: 'number',
      name: 'hour',
      'class': 'group',
      width: '70px',
      value: '1',
      unit: '小时',
      min: 0,
      max: 23
    }, {
      type: 'number',
      name: 'minute',
      'class': 'group',
      width: '70px',
      min: 0,
      max: 59,
      value: '30',
      unit: '分钟'
    }]
  }, {
    label: '备份网站',
    display: false,
    group: [{
      type: 'select',
      name: 'sName',
      width: '150px',
      placeholder: '无站点数据',
      list: siteListAll,
      change: function (formData, element, that) {
        var nameForm = that.config.form[1]
        if (formData.sType === 'enterpriseBackup') {
          crontab.getAllTables(formData.datab_name,function(res) {
            that.config.form[3].group[3].list = res
            that.config.form[3].group[3].display = formData.sName === 'tables'
            that.$replace_render_content(3)
            nameForm.group.value = '[勿删]数据库增量备份[ ' + (formData.sName === 'databases' ? formData.datab_name : (formData.datab_name+'---'+ res[0].value)) + ' ]'
            that.$local_refresh('name', nameForm.group)
          })
        }else{
          nameForm.group.value = crontab.typeTips[formData.sType] + '[ ' + (formData.sName === 'ALL' ? '所有' : formData.sName) + ' ]'
        }
        that.$local_refresh('name', nameForm.group)
      }
    }, {
      type: 'text',
      width: '200px',
      name: 'path',
      display: false,
      icon: {
        type: 'glyphicon-folder-open',
        event: function (formData, element, that) {
          $("#bt_select").one('click', function () {
            that.config.form[1].group.value = '备份目录[' + element['path'].val() + ']'
            that.$local_refresh('name', that.config.form[1].group)
          })
        }
      },
      value: bt.get_cookie('sites_path') ? bt.get_cookie('sites_path') : '/www/wwwroot',
      placeholder: '请选择文件目录'
    },{
      label: '数据库',
      display: false,
      type: 'select',
      name: 'datab_name',
      width: '150px',
      list: allDatabases,
      change: function (formData, element, that) {
        var nameForm = that.config.form[1]
        crontab.getAllTables(formData.datab_name,function (res) {
          that.config.form[3].group[3].list = res
          that.$replace_render_content(3)
          nameForm.group.value = '[勿删]数据库增量备份[ ' + (formData.sName === 'databases' ? formData.datab_name : formData.datab_name+'---'+res[0].value) + ' ]'
          that.$local_refresh('name', nameForm.group)
        })
      }
    },{
      type: 'select',
      display: false,
      label: '表',
      name: 'tables_name',
      width: '150px',
      list: allTables,
      change: function (formData, element, that) {
        var nameForm = that.config.form[1]
        if (formData.sType === 'enterpriseBackup') {
          nameForm.group.value = '[勿删]数据库增量备份[ ' + (formData.sName === 'databases' ? formData.datab_name : formData.datab_name+'---'+formData.tables_name) + ' ]'
        }
        that.$local_refresh('name', nameForm.group)
      }
    } ,{
      type: 'select',
      name: 'backupTo',
      label: '备份到',
      width: '150px',
      placeholder: '无存储信息',
      value: 'localhost',
      list: backupListAll,
      change: function (formData, element, that) {
        if (that.data.sType!=='enterpriseBackup' && formData.sType !== 'enterpriseBackup') {
          that.config.form[3].group[4].value = formData.backupTo;
          that.config.form[3].group[5].value = formData.save;
          that.config.form[3].group[6].display = formData.backupTo !== "localhost" ? true : false;
          switch(formData.sType){
            case 'site':
            case 'database':
              that.config.form[3].group[0].value = formData.sName
              break;
            case 'path':
              that.config.form[3].group[1].value = formData.path
              break;
          }
          that.$replace_render_content(3)
        }
      }
    }, {
      label: '保留最新',
      type: 'number',
      name: 'save',
      'class': 'group',
      width: '70px',
      value: '3',
      unit: '份'

    }, {
      type: 'checkbox',
      name: 'save_local',
      display: false,
      style: { "margin-top": "7px" },
      value: 1,
      title: '同时保留本地备份（和云存储保留份数一致）',
      event: function (formData, element, that) {
        that.config.form[3].group[6].value = !formData.save_local ? '0' : '1';
      }
    }]
  }, {
    label: '备份提醒',
    display: false,
    group: [{
      type: 'select',
      name: 'notice',
      value: 0,
      list: [
        { title: '不接收任何消息通知', value: 0 },
        { title: '任务执行失败接收通知', value: 1 }
      ],
      change: function (formData, element, that) {
        var notice_channel_form = that.config.form[4], notice = parseInt(formData.notice)
        notice_channel_form.group[1].display = !!notice
        notice_channel_form.group[0].value = notice
        that.$replace_render_content(4)

        var flag = false;
        if (formData.notice !== '0') {
          flag = that.config.form[4].group[1].list.length == 0;
        }
        that.config.form[8].group.disabled = flag;
        that.$local_refresh('submitForm', that.config.form[8].group);
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
          return crontab.pushChannelMessage.getChannelSwitch(res,that.config.form[0].group.value)
        },
        success: function (res, that, config, list) {
          if(!config.group[1].value && config.group[0].value == 1){
            config.group[1].value = list.length > 0 ? list[0].value : []
          }
          if (list.length === 0) {
            that.config.form[8].group.disabled = true
            that.$local_refresh('submitForm', that.config.form[8].group)
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
  }, {
    label: '脚本内容',
    group: {
      type: 'textarea',
      name: 'sBody',
      style: {
        'width': '500px',
        'min-width': '500px',
        'min-height': '130px',
        'line-height': '22px',
        'padding-top': '10px',
        'resize': 'both'
      },
      placeholder: '请输入脚本内容'
    }
  }, {
    label: 'URL地址',
    display: false,
    group: {
      type: 'text',
      width: '500px',
      name: 'urladdress',
      value: 'http://',
      event: function (formData, element, that) {
        if (formData.sType === 'enterpriseBackup') {
          $('.glyphicon-repeat').on('click',function(){
            that.config.form[6].group.value = bt.get_random(bt.get_random_num(6,10))
            that.$local_refresh('urladdress', that.config.form[6].group)
            $('input[name=urladdress]').click()
          })
        }
      }
    }
  }, {
    label: '温馨提示',
    display: false,
    group: {
      type: 'help',
      name: 'webshellTips',
      style: { 'margin-top': '6px' },
      list: ['释放PHP、MYSQL、PURE-FTPD、APACHE、NGINX的内存占用,建议在每天半夜执行!']
    }
  }, {
    label: '',
    group: {
      type: 'button',
      size: '',
      name: 'submitForm',
      title: '添加任务',
      event: function (formData, element, that) {
        formData['save_local'] = that.config.form[3].group[6].value.toString();
        that.submit(formData)
      }
    }
  }],
  /**
   * @description 计划任务类型解构调整
   * @param {}
   * @param {}
   * @param {Add} 是否是添加
   */

  crontabsType: function (config, formData, Add) {
    config[4].group[1].name = 'notice_channel';
    config[3].group[4].list = backupListAll;
    // config[2].group[0].value = 'week';
    switch (formData.sType) {
      case 'toShell':
        break;
      case 'enterpriseBackup':
        config[2].label = '备份周期'
        config[2].group[0].display = false
        config[2].group[1].display = false
        config[2].group[2].display = false
        config[2].group[3].display = true
        config[2].group[4].display = false
        config[6].display = false;
        config[3].group[0].list = [{title: '数据库', value: 'databases'},{title: '表', value: 'tables'}];
        config[3].label = '备份类型'
        config[3].group[0].placeholder = ''
        config[3].group[4].placeholder = ''
        config[3].group[4].value = ['localhost']
        config[3].group[4].width = '300px'
        config[3].group[2].list = allDatabases
        config[3].group[4].list = backuptolist
        config[3].group[4].type = 'multipleSelect'
        config[3].group[2].display = true;
        config[3].group[5].display = false;
        config[3].display = true;
        config[6].display = true;
        config[6].label = '压缩密码'
        config[6].group.width = '250px'
        config[6].group.unit = '<span class="glyphicon glyphicon-repeat cursor mr5"></span><span style="margin-left:5px;color:red;">注意：请牢记压缩密码，以免因压缩密码导致无法恢复和下载数据</span>'
        config[6].group.placeholder = '请输入压缩密码，可为空'
        config[6].group.value = ''
        config[1].group.disabled = true // 禁用任务名称，不允许修改
        config[5].display = false;
        config[4].display = true;
        config[7].display = true;
        config[7].group.list = ''
        config[7].group.unit = '<span class="alertMsg"><span class="glyphicon glyphicon-alert" style="color: #f39c12; margin-right: 10px;"></span>【使用提醒】此功能为企业版专享功能，目前处于公测阶段，将于2023年1月16日后转为收费功能。当前数据库暂不支持SQLServer、MongoDB、Redis、PgSQL备份</span>'
        if (Add) {
          config[2].group[0].value = 'hour-n'
          config[2].group[3].value = '3'
        }

        break;
      case 'database':
        config[3].group[0].placeholder = '无数据库数据';
        config[5].display = false;
        config[7].display = true;
        config[7].group.list = ''
        config[7].group.unit = '<span class="alertMsg">当前数据库暂不支持SQLServer、MongoDB、Redis、PgSQL备份</span>'
        if (Add) {
          config[2].group[0].value = 'day'
          config[2].group[1].display = false
          config[2].group[3].value = '2'
          config[2].group[4].value = '30'
        }
      case 'logs':
        if (formData.sType === 'logs') {
          if(Add){
            config[2].group[3].value = '0'
            config[2].group[4].value = '1'
            config[2].group[0].value = 'day'
          }
          config[2].group[1].display = false
          config[3].group[4].display = false
          config[3].group[5].value = 180
        }
      case 'path':
        if (formData.sType === 'path') {
          config[1].group.value = '备份目录[' + config[3].group[1].value + ']'
          if(Add) {
            config[2].group[0].value = 'day'
            config[2].group[1].display = false
          }
          config[3].group[0].display = false
          config[3].group[1].display = true
          config[3].group[4].list = backupListAll
        }
      case 'webshell':
        if (formData.sType === 'webshell') {
          config[3].group[0].unit = '<span style="margin-top: 9px; display: inline-block;">*本次查杀由长亭牧云强力驱动</span>';
          config[3].group[4].display = false
          config[3].group[5].display = false
          config[3].group[6].display = false
          config[4].display = true
          config[4].label = '消息通道'
          config[4].group[1].name = 'urladdress'
          config[4].group[0].display = false
          delete config[4].group[1].label
          config[4].group[1].display = true
          config[5].display = false
        }
      case 'site':
        config[3].group[0].list = siteListAll;
        config[3].label = crontab.typeTips[formData.sType]
        if (formData.sType !== 'path') config[1].group.disabled = true // 禁用任务名称，不允许修改
        config[3].display = true // 显示备份网站操作模块
        if (formData.sType === 'database' || formData.sType === 'site' || formData.sType === 'path') config[4].display = true
        config[5].label = '排除规则'
        config[5].group.placeholder = '每行一条规则,目录不能以/结尾，示例：\ndata/config.php\nstatic/upload\n *.log\n'
        break;
      case 'syncTime':
        config[1].group.value = '定期同步服务器时间'
        config[5].group.value = 'echo "|-检查ntpdate命令是否就绪.."\n'
        +'is_ntpdate=$(which ntpdate)\n'
        +'if [ "$is_ntpdate" = "" ];then\n'
        +'   if [ -f /usr/bin/apt ];then\n'
        +'       apt install ntpdate -y\n'
        +'   else\n'
        +'       is_dnf=$(which dnf)\n'
        +'       if [ "$is_dnf" = "" ];then\n'
        +'                yum install ntpdate -y\n'
        +'       fi\n'
        +'   fi\n'
        +'fi\n'
        +'is_ntpdate=$(which ntpdate)\n'
        +'is_http=0\n'
        +'if [ "$is_ntpdate" != "" ];then\n'
        +'    echo "|-正在尝试从1.pool.bt.cn同步时间..";\n'
        +'    ntpdate -u 1.pool.bt.cn\n'
        +'    if [ $? = 1 ];then\n'
        +'       echo "|-正在尝试从0.asia.pool.ntp.org同步时间..";\n'
        +'       ntpdate -u 0.asia.pool.ntp.org\n'
        +'   fi\n'
        +'else\n'
        +'    is_http=1\n'
        +'fi\n'
        +'if [ $? = 1 ] || [ $is_http = 1 ];then\n'
        +'    echo "|-正在尝试从www.bt.cn同步时间..";\n'
        +'    getBtTime=$(curl -sS --connect-timeout 3 -m 60 http://www.bt.cn/api/index/get_time)\n'
        +'    if [ "${getBtTime}" ];then\n'
        +'        echo "|-设置时间: "$(date -s "$(date -d @$getBtTime +"%Y-%m-%d %H:%M:%S")")\n'
        +'    fi\n'
        +'fi\n'
        +'echo "|-正在尝试将当前系统时间写入硬件..";\n'
        +'hwclock -w\n'
        +'echo "|-当前时间为：$(date)"\n'
        +'echo "|-时间同步完成!";\n'
        break;
      case 'rememory':
        config[1].group.value = '释放内存'
        config[5].display = false
        config[7].display = true
        break;
      case 'toUrl':
        config[5].display = false
        config[6].display = true
        break;
    }
    if (formData.sType === 'database') config[3].group[0].list = databaseListAll;
    if (Add && (formData.sType === 'database' || formData.sType === 'logs' || formData.sType === 'site')) {
      config[3].group[0].value = 'ALL';
    }
    config[0].group.value = formData.sType
    return config
  },

  /**
   * @description 计划任务类型解构调整
   */
  crontabType: function (config, formData) {
    var formConfig = config[2];
    switch (formData.type) {
      case 'day-n':
      case 'month':
      case 'day':
        formConfig.group[1].display = false
        $.extend(formConfig.group[2], {
          display: formData.type !== 'day',
          unit: formData.type === 'day-n' ? '天' : '日'
        })
        formConfig.group[3].display = true
        break;
      case 'hour-n':
      case 'hour':
      case 'minute-n':
        formConfig.group[1].display = false
        formConfig.group[2].display = false
        formConfig.group[3].display = formData.type === 'hour-n'
        formConfig.group[4].value = formData.type === 'minute-n' ? 3 : 30
        break;
      case 'week':
        formConfig.group[1].display = true
        formConfig.group[2].display = false
        formConfig.group[3].display = true
        break;

    }
    var num = formData.sType == 'logs' ? 0 : 1;
    var hour = formData.hour ? formData.hour : num;
    var minute = formData.minute ? formData.minute : 30;
    formConfig.group[3].value = parseInt(hour).toString();
    formConfig.group[4].value = parseInt(minute).toString()
    formConfig.group[0].value = formData.type;
    return config;
  },
  /**
   * @description 添加计划任务表单
   */
  addCrontabForm: function () {
    var _that = this
    return bt_tools.form({
      el: '#crontabForm',
      'class': 'crontab_form',
      form: arryCopy(crontab.crontabFormConfig),
      submit: function (formData) {
        var form = $.extend(true, {}, _that.crontabForm), _where1 = $('input[name=where1]'), _hour = $('input[name=hour]'), _minute = $('input[name=minute]');
        $.extend(form, formData)
        if (form.name === '') {
          bt.msg({ status: false, msg: '计划任务名称不能为空！' })
          return false
        }
        if (_where1.length > 0) {
          if (_where1.val() > 31 || _where1.val() < 1 || _where1.val() == '') {
            _where1.focus();
            layer.msg('请输入正确的周期范围[1-31]', { icon: 2 });
            return false;
          }
        }
        if (_hour.length > 0) {
          if (_hour.val() > 23 || _hour.val() < 0 || _hour.val() == '') {
            _hour.focus();
            layer.msg('请输入正确的周期范围[0-23]', { icon: 2 });
            return false;
          }
        }
        if (_minute.length > 0) {
          if (_minute.val() > 59 || _minute.val() < 0 || _minute.val() == '') {
            _minute.focus();
            layer.msg('请输入正确的周期范围[0-59]', { icon: 2 });
            return false;
          }
        }
        switch (form.type) {
          case "minute-n":
            form.where1 = form.minute;
            form.minute = '';
            if(form.where1 < 1) return bt.msg({ status: false, msg: '分钟不能小于1！' })
            break;
          case "hour-n":
            form.where1 = form.hour;
            form.hour = '';
            if(form.minute <= 0 && form.where1 <= 0) return bt.msg({ status: false, msg: '小时、分钟不能同时小于1！' })
            break;
            // 天/日默认最小为1
        }
        switch (form.sType) {
          case 'syncTime':
            if (form.sType === 'syncTime') form.sType = 'toShell'
          case 'toShell':
            if (form.sBody === '') {
              bt.msg({ status: false, msg: '脚本内容不能为空！' })
              return false
            }
            break;
          case 'path':
            form.sName = form.path
            delete form.path
            if (form.sName === '') {
              bt.msg({ status: false, msg: '备份目录不能为空！' })
              return false
            }
            break;
          case 'toUrl':
            if (!bt.check_url(form.urladdress)) {
              layer.msg(lan.crontab.input_url_err, { icon: 2 });
              $('#crontabForm input[name=urladdress]').focus();
              return false;
            }
            break;
          case 'enterpriseBackup':
            if (form.hour < 1) {
              layer.msg('备份周期应大于0', { icon: 2 });
              $('#crontabForm input[name=hour]').focus();
              return false;
            }
            break;
        }
        if (form.sType == "site" || form.sType == "database" || form.sType == "path" || form.sType == "logs") {
          if (Number(form.save) < 1 || form.save == '') {
            return bt.msg({status: false, msg: '保留最新不能小于1！'});
          }
        }
        var url = '/crontab?action=AddCrontab',params = form
        if (form.sType == "enterpriseBackup") {
          var multipleValues = $('select[name=backupTo').val()
          if(multipleValues == null) return layer.msg('请最少选择一个备份类型')
          url = 'project/binlog/add_mysqlbinlog_backup_setting'
          params = {
            datab_name : form.datab_name,
            backup_type : form.sName,
            zip_password : form.urladdress,
            cron_type : 'hour-n',
            backup_cycle : form.hour,
            upload_localhost : multipleValues.indexOf('localhost') > -1 ? 'localhost' : '',
            upload_alioss : multipleValues.indexOf('alioss') > -1 ? 'alioss' : '',
            upload_txcos : multipleValues.indexOf('txcos') > -1 ? 'txcos' : '',
            upload_qiniu : multipleValues.indexOf('qiniu') > -1 ? 'qiniu' : '',
            upload_obs : multipleValues.indexOf('obs') > -1 ? 'obs' : '',
            upload_bos : multipleValues.indexOf('bos') > -1 ? 'bos' : '',
            notice : form.notice,
            notice_channel : form.notice_channel,
          }
          if(params.backup_type == 'tables') {
            params['table_name'] = form.tables_name
            if(form.tables_name == '') return layer.msg("当前数据库下没有表，不能添加")
          }
        }
        bt_tools.send({
          url: url,
          data: params
        }, function (res) {
          _that.addCrontabForm.data = {}
          _that.addCrontabForm.$again_render_form(_that.crontabFormConfig)
          _that.crontabTabel.$refresh_table_list(true)
          bt_tools.msg(res)
        }, '添加计划任务');
      }
    })
  },
  /**
   * @description 获取所有数据库名
   */
  getAllDatabases: function (callback){
    $.post('project/binlog/get_databases', function (res) {
      allDatabases = []
      if (res.length == 0) {
        allDatabases = [{title:'当前没有数据库',value:''}]
      }else{
        for (let i = 0; i < res.length; i++) {
          allDatabases.push({title:res[i].name,value:res[i].name})
        }
      }
      if (callback) callback(res)
    })
  },
  /**
   * @description 取指定数据库的所有表名
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  getAllTables: function (param, callback) {
    $.post('project/binlog/get_tables', {db_name: param} , function (res) {
      var data = [],allTables = []
      for (let i = 0; i < res.length; i++) {
        data.push({title:res[i].name,value:res[i].name})
      }
      if (data.length == 0) {
        allTables = [{title:'当前数据库下没有表',value:''}]
      }else{
        allTables = data
      }
      if (callback) callback(allTables)
    })
  },
  /**
   * @description 获取计划任务存储列表
   * @param {function} callback 回调函数
   */
  getDataList: function (type, callback) {
    if ($.type(type) === 'function') callback = type, type = 'sites'
    bt_tools.send({
      url: '/crontab?action=GetDataList',
      data: { type: type }
    }, function (res) {
      var backupList = [{ title: '服务器磁盘', value: 'localhost' }];
      for (var i = 0; i < res.orderOpt.length; i++) {
        var item = res.orderOpt[i]
        backupList.push({ title: item.name, value: item.value })
      }
      backupListAll = backupList
      var siteList = [{ title: '所有', value: 'ALL' }];
      for (var i = 0; i < res.data.length; i++) {
        var item = res.data[i]
        siteList.push({ title: item.name + ' [ ' + item.ps + ' ]', value: item.name });
      }
      if (siteList.length === 1) siteList = []
      if (type === 'sites') {
        siteListAll = siteList
      } else {
        databaseListAll = siteList
      }
      if (callback) callback(res)
    }, '获取存储配置');
  },
  /**
   * @description 删除计划任务
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  delCrontab: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=DelCrontab',
      data: { id: param.id }
    }, function (res) {
      bt.msg(res)
      if (res.status && callback) callback(res)
    }, '删除计划任务');
  },
  /**
   * @description 执行计划任务
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  startCrontabTask: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=StartTask',
      data: { id: param.id }
    }, function (res) {
      bt.msg(res)
      if (res.status && callback) callback(res)
    }, '执行计划任务');
  },
  /**
   * @description 获取计划任务执行日志
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  getCrontabLogs: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=GetLogs',
      data: { id: param.id }
    }, function (res) {
      if (res.status) {
        if (callback) callback(res)
      } else {
        bt.msg(res)
      }
    }, '获取执行日志');
  },
  /**
   * @description 获取计划任务执行日志
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  clearCrontabLogs: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=DelLogs',
      data: { id: param.id }
    }, function (res) {
      bt.msg(res)
      if (res.status && callback) callback(res)
    }, '清空执行日志');
  },
  /**
   * @description 获取计划任务执行状态
   * @param {object} param 参数对象
   * @param {function} callback 回调函数
   */
  setCrontabStatus: function (param, callback) {
    bt_tools.send({
      url: '/crontab?action=set_cron_status',
      data: { id: param.id }
    }, function (res) {
      bt.msg(res)
      if (res.status && callback) callback(res)
    }, '设置任务状态');
  },
  /**
   * @description 计划任务表格
   */
  crontabTabel: function () {
    var _that = this
    return bt_tools.table({
      el: '#crontabTabel',
      url: '/crontab?action=GetCrontab',
      minWidth: '1000px',
      autoHeight: true,
      'default': "计划任务列表为空", //数据为空时的默认提示
      height: 300,
      dataFilter: function (res) {
        return { data: res };
      },
      column: [
        { type: 'checkbox', 'class': '', width: 20 },
        {
          fid: 'name',
          title: "任务名称"
        },
        {
          fid: 'status',
          title: "状态",
          width: 80,
          config: {
            icon: true,
            list: [
              [1, '正常', 'bt_success', 'glyphicon-play'],
              [0, '停用', 'bt_danger', 'glyphicon-pause']
            ]
          },
          type: 'status',
          event: function (row, index, ev, key, that) {
            bt.confirm({
              title: '设置计划任务状态',
              msg: parseInt(row.status) ? '计划任务暂停后将无法继续运行，您真的要停用这个计划任务吗？' : '该计划任务已停用，是否要启用这个计划任务'
            }, function () {
              _that.setCrontabStatus(row, function () {
                that.$refresh_table_list(true)
              })
            })
          }
        },
        // {
        //   fid: 'type',
        //   title: "周期",
        //   width: 120
        // },
        {
          fid: 'cycle',
          title: "执行周期",
          template: function (row, index) {
            if (row.sType == "enterpriseBackup") {
              return '<span>每隔'+ row.where1 +'小时执行</span>'
            }
            return '<span>'+ row.cycle +'</span>'
          }
        }, {
          fid: 'save',
          title: "保存数量",
          template: function (row) {
            return '<span>' + (row.save > 0 ? +row.save + '份' : '-') + '</span>'
          }
        }, {
          fid: 'backupTo',
          title: "备份到",
          width: 170,
          template: function (row, index) {
            if (row.sType == "enterpriseBackup") {
              var arry = [],arry1 = []
              arry = row.backupTo.split("|")
              for (var i = 0; i < arry.length; i++) {
                for (var j = 0; j < backuptolist.length; j++) {
                  if (arry[i] == backuptolist[j].value) {
                    arry1.push(backuptolist[j].title)
                  }
                }
              }
              return '<span>' + arry1 + '</span>'
            } else {
              for (var i = 0; i < backupListAll.length; i++) {
                var item = backupListAll[i]
                if (item.value === row.backupTo) {
                  if (row.sType === 'toShell') return '<span>--</span>';
                  return '<span>' + item.title + '</span>'
                }
              }
              return '<span>--</span>'
            }
          }
        }, {
          fid: 'addtime',
          title: '上次执行时间',
        },
        {
          title: "操作",

          type: 'group',
          align: 'right',
          group: [{
            title: '执行',
            event: function (row, index, ev, key, that) {
              _that.startCrontabTask(row, function (res) {
                that.$refresh_table_list(true);
                if(res.status) {
                  setTimeout(function () {
                    layer.closeAll()
                    $('#crontabTabel .table tbody tr:eq('+ index +')').find('[title="日志"]').click()
                  }, 1000)
                }
              })
            }
          }, {
            title: '编辑',
            event: function (row, index, ev, key, that) {
              var arry = [],db_result,t_result
              arry = row.urladdress.split("|")
              if(row.sType === 'enterpriseBackup'){
                crontab.getAllDatabases(function (rdata) {
                  crontab.getAllTables(arry[0],function(res) {
                    db_result = rdata.some(function(item){
                      if (item.name === arry[0]) {
                        return true
                      }
                    })
                    if(arry[1] !== ''){
                      t_result = res.some(function(item){
                        if (item.value === arry[1]) {
                          return true
                        }
                      })
                    }
                    edit(res)
                  })
                })
              }else{
                edit()
              }
              function edit(table_list) {
                layer.open({
                  type: 1,
                  title: '编辑计划任务-[' + row.name + ']',
                  area: row.sType != "enterpriseBackup" ? '990px':'1140px',
                  skin: 'layer-create-content',
                  shadeClose: false,
                  closeBtn: 2,
                  content: '<div class="ptb20" id="editCrontabForm" style="min-height: 400px"></div>',
                  success: function (layers, indexs) {
                    bt_tools.send({
                      url: '/crontab?action=get_crond_find',
                      data: { id: row.id }
                    }, function (rdata) {
                      var formConfig = arryCopy(crontab.crontabFormConfig),
                          form = $.extend(true, {}, _that.crontabForm),
                          cycle = {};
                      for (var keys in form) {
                        if (form.hasOwnProperty.call(form, keys)) {
                          form[keys] = typeof rdata[keys] === "undefined" ? '' : rdata[keys]
                        }
                      }
                      crontab.crontabType(formConfig, form)
                      crontab.crontabsType(formConfig, form)
                      switch (rdata.type) {
                        case 'day':
                          cycle = { where1: '', hour: rdata.where_hour, minute: rdata.where_minute }
                          break;
                        case 'day-n':
                          cycle = { where1: rdata.where1, hour: rdata.where_hour, minute: rdata.where_minute }
                          break;
                        case 'hour':
                          cycle = { where1: rdata.where1, hour: rdata.where_hour, minute: rdata.where_minute }
                          break;
                        case 'hour-n':
                          cycle = { where1: rdata.where1, hour: rdata.where1, minute: rdata.where_minute }
                          break;
                        case 'minute-n':
                          cycle = { where1: rdata.where1, hour: '', minute: rdata.where1 }
                          break;
                        case 'week':
                          formConfig[2].group[1].value = rdata.where1
                          cycle = { where1: '', week: rdata.where1, hour: rdata.where_hour, minute: rdata.where_minute }
                          break;
                        case 'month':
                          cycle = { where1: rdata.where1, where: '', hour: rdata.where_hour, minute: rdata.where_minute }
                          break;
                      }

                      if (rdata.sType !== 'enterpriseBackup') {
                        formConfig[3].group[4].value = rdata.backupTo;
                        formConfig[3].group[6].display = (rdata.backupTo != "" && rdata.backupTo != 'localhost');
                        formConfig[3].group[6].value = rdata.save_local;
                      }
                      formConfig[4].group[0].value = rdata.notice;
                      formConfig[4].group[1].display = rdata.sType == 'webshell' ? true : !!rdata.notice;    //单独判断是否为木马查杀
                      if (formConfig[4].group[1].display) {
                        formConfig[4].group[1].display = true;
                        formConfig[4].group[1].value = (rdata.sType == 'webshell' ? rdata.urladdress : (rdata.notice_channel === '' ? first : rdata.notice_channel))
                      }
                      $.extend(form, cycle, { id: rdata.id })



                      switch (rdata.sType) {
                        case 'logs':
                        case 'path':
                          form.path = rdata.sName
                          formConfig[3].group[1].disabled = true
                          break
                        case 'enterpriseBackup':
                          formConfig[3].group[2].value = arry[0]
                          formConfig[3].group[2].disabled = true
                          if(arry[1] !== ''){
                            // formConfig[3].group[3].list = [{title:arry[1],value:arry[1]}]
                            formConfig[3].group[3].list = table_list
                            formConfig[3].group[3].value = arry[1]
                            formConfig[3].group[3].disabled = true
                            formConfig[3].group[3].display = true
                          }
                          if (!t_result) {
                            formConfig[3].group[3].placeholder = '表不存在'
                            var none_db = formConfig[3].group[3].list.some(function(item){
                              if (item.value === '') {
                                return true
                              }
                            })
                            if (none_db) formConfig[3].group[3].list = []
                          }
                          if (!db_result) {
                            formConfig[3].group[2].placeholder = '数据库不存在'
                            formConfig[3].group[3].placeholder = '表不存在'
                            formConfig[3].group[3].list = []
                          }
                          formConfig[3].group[1].disabled = true
                          formConfig[6].display = false
                          var backT = rdata.backupTo.split('|'), backupTolist = []
                          for (var i = 0; i < backT.length; i++) {
                            if (backT[i] != '') {
                              backupTolist.push(backT[i])
                            }
                          }
                          formConfig[3].group[4].value = backupTolist
                          break;
                      }
                      formConfig[0].group.disabled = true
                      formConfig[1].group.disabled = true
                      formConfig[3].group[0].disabled = true
                      formConfig[8].group.title = '保存编辑'
                      var screen = ['site','database','logs','path','webshell']
                      if(screen.indexOf(form.sType) > -1){
                        if (form.sName === 'ALL') {
                          form.name = form.name.replace(/\[(.*)]/, '[ 所有 ]');
                        } else {
                          form.name = form.name.replace(/\[(.*)]/, '[ ' + form.sName + ' ]');
                        }
                      }

                      delete formConfig[0].group.unit

                      bt_tools.form({
                        el: '#editCrontabForm',
                        'class': 'crontab_form',
                        form: formConfig,
                        data: form,
                        submit: function (formData) {
                          var submitForm = $.extend(true, {}, _that.crontabForm, formData, {
                            id: rdata.id,
                            sType: rdata.sType
                          })
                          if (submitForm.name === '') {
                            bt.msg({ status: false, msg: '计划任务名称不能为空！' })
                            return false
                          }
                          switch (submitForm.sType) {
                            case 'syncTime':
                              if (submitForm.sType === 'syncTime') submitForm.sType = 'toShell'
                            case 'toShell':
                              if (submitForm.sBody === '') {
                                bt.msg({ status: false, msg: '脚本内容不能为空！' })
                                return false
                              }
                              break;
                            case 'path':
                              submitForm.sName = submitForm.path
                              delete submitForm.path
                              if (submitForm.sName === '') {
                                bt.msg({ status: false, msg: '备份目录不能为空！' })
                                return false
                              }
                              break;
                            case 'toUrl':
                              if (!bt.check_url(submitForm.urladdress)) {
                                layer.msg(lan.crontab.input_url_err, { icon: 2 });
                                $('#editCrontabForm input[name=urladdress]').focus();
                                return false;
                              }
                              break;
                            case 'enterpriseBackup':
                              if (submitForm.hour == '')  return bt.msg({ status: false, msg: '备份周期不能为空！' })
                              if (submitForm.hour < 0)  return
                              break;
                          }

                          var hour = parseInt(submitForm.hour), minute = parseInt(submitForm.minute), where1 = parseInt(submitForm.where1)

                          switch (submitForm.type) {
                            case 'hour':
                            case 'minute-n':
                              if (minute < 0 || minute > 59 || isNaN(minute)) return bt.msg({ status: false, msg: '请输入正确分钟范围0-59分' })
                              if (submitForm.type === 'minute-n') {
                                submitForm.where1 = submitForm.minute
                                submitForm.minute = ''
                                if(submitForm.where1 < 1) return bt.msg({ status: false, msg: '分钟不能小于1！' })
                              }
                              break;
                            case 'day-n':
                            case 'month':
                              if (where1 < 1 || where1 > 31 || isNaN(where1)) return bt.msg({ status: false, msg: '请输入正确天数1-31天' })
                            case 'week':
                            case 'day':
                            case 'hour-n':
                              if (hour < 0 || hour > 23 || isNaN(hour)) return bt.msg({ status: false, msg: '请输入小时范围0-23时' })
                              if (minute < 0 || minute > 59 || isNaN(minute)) return bt.msg({ status: false, msg: '请输入正确分钟范围0-59分' })
                              if (submitForm.type === 'hour-n') {
                                submitForm.where1 = submitForm.hour
                                submitForm.hour = ''
                                if(submitForm.minute <= 0 && submitForm.where1 <= 0) return bt.msg({ status: false, msg: '小时、分钟不能同时小于1！' })
                              }
                              break;
                          }
                          if (submitForm.sType == "site" || submitForm.sType == "database" || submitForm.sType == "path" || submitForm.sType == "logs") {
                            if (Number(submitForm.save) < 1 || submitForm.save == '') {
                              return bt.msg({ status: false, msg: '保留最新不能小于1！'});
                            }
                          }

                          var url = '/crontab?action=modify_crond', params = submitForm
                          if (submitForm.sType == 'enterpriseBackup') {
                            var multipleValues = $('select[name=backupTo').val()
                            if(multipleValues == null) return layer.msg('请最少选择一个备份类型')
                            url = 'project/binlog/modify_mysqlbinlog_backup_setting'
                            params = {
                              datab_name : arry[0],
                              cron_type : 'hour-n',
                              backup_cycle : submitForm.hour,
                              upload_localhost : multipleValues.indexOf('localhost') > -1 ? 'localhost' : '',
                              upload_alioss : multipleValues.indexOf('alioss') > -1 ? 'alioss' : '',
                              upload_txcos : multipleValues.indexOf('txcos') > -1 ? 'txcos' : '',
                              upload_qiniu : multipleValues.indexOf('qiniu') > -1 ? 'qiniu' : '',
                              upload_obs : multipleValues.indexOf('obs') > -1 ? 'obs' : '',
                              upload_bos : multipleValues.indexOf('bos') > -1 ? 'bos' : '',
                              notice : submitForm.notice,
                              notice_channel : submitForm.notice_channel,
                              cron_id : row.id,
                              backup_id : arry[2]
                            }
                            if($('select[name=datab_name').parent().find('.bt_select_content').text().indexOf('不存在') > -1) return layer.msg('数据库['+ arry[0] +']不存在',{icon:2})
                            if($('select[name=tables_name').length) if($('select[name=tables_name').parent().find('.bt_select_content').text().indexOf('不存在') > -1) return layer.msg('表['+ arry[1] +']不存在',{icon:2})
                          }else{
                            if($('select[name=sName').length){
                              params.name.match(/\[(.*)]/)
                              var sName_result = formConfig[3].group[0].list.some(function(item){
                                if (item.value === (RegExp.$1.trim() === '所有'?'ALL':RegExp.$1.trim())) {
                                  return true
                                }
                              })
                              if(!sName_result) return layer.msg(formConfig[3].group[0].placeholder,{icon:2})
                            }
                          }
                          bt_tools.send({
                            url: url,
                            data: params
                          }, function (res) {
                            bt_tools.msg(res)
                            layer.close(indexs)
                            _that.crontabTabel.$refresh_table_list(true);
                          }, '编辑计划任务')
                        }
                      })
                    }, '获取计划配置信息')
                  }
                })
              }
            }
          }, {
            title: '日志',
            event: function (row, index, ev, key, that) {
              var log_interval = null
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
												<button type="button" class="btn btn-success btn-sm btn-title" id="closeLogs">'+ lan['public']['close'] + '</button>\
											</div>\
										</div>',
                  success: function () {
                    var nScrollHight = 0;  //滚动距离总长(注意不是滚动条的长度)
                    var nScrollTop = 0;   //滚动到的当前位置
                    var nDivHight = $(".crontab-log").height();
                    var isDb = true
                    $(".crontab-log").scroll(function(){
                      nScrollHight = $(this)[0].scrollHeight;
                      nScrollTop = $(this)[0].scrollTop;
                      var paddingBottom = parseInt( $(this).css('padding-bottom') ),paddingTop = parseInt( $(this).css('padding-top') );
                      isDb = false
                      //判断是否滚动到底部
                      if(nScrollTop + paddingBottom + paddingTop + nDivHight >= nScrollHight){
                        isDb = true
                      }
                    });
                    var data_text = ''
                    log_interval = setInterval(function () {
                      bt_tools.send({
                        url: '/crontab?action=GetLogs',
                        data: { id: row.id }
                      }, function (res) {
                        if (res.status) {
                          var arr = res.msg.split('\n')
                          if(data_text === res.msg && arr[arr.length - 1].indexOf('-------') > -1) {
                            clearInterval(log_interval)
                            return
                          }
                          if(isDb) render_content(res)
                        }
                      })
                    }, 2000)
                    render_content(rdata)
                    function render_content(data) {
                      data_text = data.msg
                      var log_body = data.msg === '' ? '当前日志为空' : data.msg,setchmod = $(".setchmod pre"),crontab_log = $('.crontab-log')[0]
                      setchmod.text(log_body);
                      crontab_log.scrollTop = crontab_log.scrollHeight;
                    }
                    $('#clearLogs').on('click', function () {
                      clearInterval(log_interval)
                      _that.clearCrontabLogs(row, function () {
                        $(".setchmod pre").text('')
                      })
                    })
                    $('#closeLogs').on('click', function () {
                      clearInterval(log_interval)
                      layer.closeAll()
                    })
                  },
                  cancel: function(indexs){
                    clearInterval(log_interval)
                    layer.close(indexs)
                  }
                })
              })
            }
          }, {
            title: '删除',
            event: function (row, index, ev, key, that) {
              bt.confirm({
                title: '删除计划任务',
                msg: '您确定要删除计划任务【' + row.name + '】，是否继续？'
              }, function () {
                if (row.sType == 'enterpriseBackup') {
                  var arry = []
                  arry = row.urladdress.split("|")
                  bt_tools.send({url: 'project/binlog/delete_mysql_binlog_setting',data: {cron_id:row.id,backup_id:arry[2],type:'cron'} },function (res) {
                    layer.msg(res.msg, {icon: res.status ? 1:2})
                    that.$refresh_table_list(true);
                  })
                }else{
                  _that.delCrontab(row, function () {
                    that.$refresh_table_list(true);
                  })
                }
              })
            }
          }]
        }
      ],
      // 渲染完成
      tootls: [{ // 批量操作
        type: 'batch', //batch_btn
        positon: ['left', 'bottom'],
        placeholder: '请选择批量操作',
        buttonValue: '批量操作',
        disabledSelectValue: '请选择需要批量操作的计划任务!',
        selectList: [{
          title: "执行任务",
          url: '/crontab?action=StartTask',
          load: true,
          param: function (row) {
            return { id: row.id }
          },
          callback: function (that) { // 手动执行,data参数包含所有选中的站点
            bt.confirm({
              title: '批量执行任务',
              msg: '您确定要批量执行选中的计划任务吗，是否继续？'
            }, function () {
              var param = {};
              that.start_batch(param, function (list) {
                var html = '';
                for (var i = 0; i < list.length; i++) {
                  var item = list[i];
                  html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + item.request.msg + '</span></div></td></tr>';
                }
                _that.crontabTabel.$batch_success_table({
                  title: '批量执行',
                  th: '任务名称',
                  html: html
                });
                _that.crontabTabel.$refresh_table_list(true);
              });
            })
          }
        }, {
          title: "删除任务",
          url: function (row) {
            if (row.sType == 'enterpriseBackup') {
              var arry = []
              arry = row.urladdress.split("|")
              return 'project/binlog/delete_mysql_binlog_setting?cron_id='+row.id+'&backup_id='+arry[2]+'&type=cron'
            } else {
              return '/crontab?action=DelCrontab&id='+ row.id
            }
          },
          load: true,
          // param: function (row) {
          //   return { id: row.id }
          // },
          callback: function (that) { // 手动执行,data参数包含所有选中的站点
            bt.show_confirm("批量删除计划任务", "<span style='color:red'>同时删除选中的计划任务，是否继续？</span>", function () {
              var param = {};
              that.start_batch(param, function (list) {
                var html = '';
                for (var i = 0; i < list.length; i++) {
                  var item = list[i];
                  html += '<tr><td>' + item.name + '</td><td><div style="float:right;"><span style="color:' + (item.request.status ? '#20a53a' : 'red') + '">' + item.request.msg + '</span></div></td></tr>';
                }
                _that.crontabTabel.$batch_success_table({
                  title: '批量删除',
                  th: '任务名称',
                  html: html
                });
                _that.crontabTabel.$refresh_table_list(true);
              });
            });
          }
        }],
      }]
    })
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
  /**
   * @description 初始化
   */
  init: function () {
    var that = this;
    this.getAllDatabases()
    this.getDataList(function () {
      that.addCrontabForm = that.addCrontabForm()
      that.crontabTabel = that.crontabTabel()
      that.getDataList('databases');
    })
    function resizeTable () {
      var height = window.innerHeight - 795, table = $('#crontabTabel .divtable');
      table.css({ maxHeight: height < 400 ? '400px' : (height + 'px') })
    }
    $(window).on('resize', resizeTable)
    setTimeout(function () {
      resizeTable()
    }, 500)
  }
}
