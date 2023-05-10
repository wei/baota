function CreateWebsiteModel(config) {
    this.type = config.type;
    this.tips = config.tips;
    this.pyVersionList = []; // python版本列表
    this.pyVindexOf = 0;  // python版本索引
    this.addModelForm = null; // 添加项目表单
    this.methods = {
        createProject: ['CreateProject', false,false],  // 第一个参数是否采用需要加载load，第一个是否跳过msg直接返回数据
        getConfFile: ['GetConfFile', '获取项目配置文件信息'],
        saveConfFile: ['SaveConfFile', '修改项目配置文件信息'],
        getinfo: ['get_info', '获取' + config.tips + '项目信息'],
        modifyProject: ['ChangeProjectConf', '修改' + config.tips + '项目'],
        stopProject: ['StopProject', '停止' + config.tips + '项目'],
        startProject: ['StartProject', '启动' + config.tips + '项目'],
        restartProject: ['RestartProject', '重启' + config.tips + '项目'],
        getCloudPython: ['GetCloudPython', '获取' + config.tips + '版本'],
        installPythonV: ['InstallPythonV', false,false],
        removePythonV: ['RemovePythonV', '卸载' + config.tips + '版本'],
        removeProject: ['RemoveProject', '删除' + config.tips + '项目'],
        getProjectInfo: ['GetProjectInfo', '获取' + config.tips + '项目信息'],
        addProjectDomain: ['AddProjectDomain', '添加' + config.tips + '项目域名'],
        removeProjectDomain: ['RemoveProjectDomain','删除' + config.tips + '项目域名',],
        getProjectLog: ['GetProjectLog', '获取' + config.tips + '项目日志'],
        bindExtranet: ['BindExtranet', '开启外网映射'],
        unbindExtranet: ['unBindExtranet', '关闭外网映射'],
        get_log_split: ['get_log_split', '获取' + config.tips + '项目日志切割任务'],
        mamger_log_split: ['mamger_log_split', '设置' + config.tips + '项目日志切割任务'],
        set_log_split: ['set_log_split', '设置' + config.tips + '项目日志切割状态'],
    };
    this.bindHttp(); //将请求映射到对象
    this.renderProjectList(); // 渲染列表
    this.getPythonVersion(); // 获取python版本
}

/**
 * @description 渲染获取项目列表
 */
CreateWebsiteModel.prototype.renderProjectList = function () {
    var _that = this;
    $('#bt_' + this.type + '_table').empty();
		$('#bt_' + this.type + '_table').append('<div class="mask_layer hide"><div class="prompt_description python-model"></div></div>')
    site.model_table = bt_tools.table({
        el: '#bt_' + this.type + '_table',
        url: '/project/' + _that.type + '/GetProjectList',
        minWidth: '1000px',
        autoHeight: true,
        default: '项目列表为空', //数据为空时的默认提示
        load: '正在获取' + _that.tips + '项目列表，请稍候...',
        beforeRequest: function (params) {
            if (params.hasOwnProperty('data') && typeof params.data === 'string') {
                var oldParams = JSON.parse(params['data']);
                delete params['data'];
                return { data: JSON.stringify($.extend(oldParams, params)) };
            }
            return { data: JSON.stringify(params) };
        },
        dataFilter:function(data){
            data['data'].forEach(function(element) {
                element.status = element.status == 1 ? true : false;
            });
            return data
        },
        sortParam: function (data) {
            return { order: data.name + ' ' + data.sort };
        },
        column: [
            { type: 'checkbox', class: '', width: 20 },
            {
                fid: 'name',
                title: '项目名称',
                type: 'link',
                event: function (row, index, ev) {
                    _that.renderProjectInfoView(row);
                },
            },
            {
                fid: 'status',
                title: '服务状态',
                width: 80,
                config: {
                    icon: true,
                    list: [
                        [true, '运行中', 'bt_success', 'glyphicon-play'],
                        [false, '未启动', 'bt_danger', 'glyphicon-pause'],
                    ],
                },
                type: 'status',
                event: function (row, index, ev, key, that) {
                    var status = row.status;
                    bt.simple_confirm(
                        {
                            title: (status ? '停止项目' : '启动项目')+'【' + row.name + '】',
                            msg: status
                                ? '停用项目后将无法正常访问项目，是否继续操作？'
                                : '启用项目后，用户可以正常访问项目内容，是否继续操作？',
                        },
                        function (index) {
                            layer.close(index);
                            _that[status ? 'stopProject' : 'startProject'](
                                { name: row.name },
                                function (res) {
                                    bt.msg({
                                        status: res.status,
                                        msg: res.msg || res.error_msg,
                                    });
                                    that.$refresh_table_list(true);
                                }
                            );
                        }
                    );
                },
            },
            {
                title: 'CPU',
                width: 60,
                type: 'text',
                template: function (row) {
                    if (typeof row['cpu'] == 'undefined') return '<span>-</span>'
                    return '<span>' + row['cpu'].toFixed(2) + '%</span>'
                }
            },
            {
                title: '内存',
                width: 80,
                type: 'text',
                template: function (row) {
                    if (typeof row['mem'] == 'undefined') return '<span>-</span>'
                    return '<span>' + bt.format_size(row['mem']) + '</span>'
                }
            },
            {
                fid: 'path',
                title: '根目录',
                tips: '打开目录',
                type: 'link',
                event: function (row, index, ev) {
					openPath(row.path);
				},
				// template:function(row,index,ev){
                //     return bt.files.dir_details_span(row.path);
                // },
            },
            {
                fid: 'ps',
                title: '备注',
                type: 'input',
                blur: function (row, index, ev, key, that) {
                    if (row.ps == ev.target.value) return false;
                    bt.pub.set_data_ps(
                        { id: row.id, table: 'sites', ps: ev.target.value },
                        function (res) {
                            bt_tools.msg(res, { is_dynamic: true });
                        }
                    );
                },
                keyup: function (row, index, ev) {
                    if (ev.keyCode === 13) {
                        $(this).blur();
                    }
                },
            },
            {
                title: '操作',
                type: 'group',
                width: 168,
                align: 'right',
                group: [
                    {
                        title: '终端',
                        event: function (row){
                            bt.clear_cookie('Path')
                            Term.route = '/pyenv_webssh'
                            Term.ssh_info = {pj_name:row.name}
                            Term.run()
                        }
                    },
                    {
                        title: '设置',
                        event: function (row, index, ev, key, that) {
                            _that.renderProjectInfoView(row);
                        },
                    },
                    {
                        title:'模块',
                        event:function(row){
                            _that.renderProjectModuleView(row);
                        }
                    },
                    {
                        title: '删除',
                        event: function (row, index, ev, key, that) {
                            bt.input_confirm({
                                    title: '删除项目 - [' + row.name + ']',
                                    value: '删除项目',
                                    msg: '<span class="color-org">风险操作，此操作不可逆</span>，删除' + _that.tips + '项目后您将无法管理该项目，是否继续操作？'},
                                function () {
                                    _that.removeProject(
                                        { name: row.name },
                                        function (res) {
                                            bt.msg({
                                                status: res.status,
                                                msg: res.msg,
                                            });
                                            site.model_table.$refresh_table_list(true);
                                        }
                                    );
                                }
                            );
                        },
                    },
                ],
            },
        ],
        // 渲染完成
        tootls: [
            {
                // 按钮组
                type: 'group',
                positon: ['left', 'top'],
                list: [
                    {
                        title: '添加' + _that.tips + '项目',
                        active: true,
                        event: function (ev) {
                            _that.renderAddProject(function () {
                                site.model_table.$refresh_table_list(true);
                            });
                        },
                    },
                    {
                        title: 'Python版本管理',
                        event: function(){
                            _that.getVersionManagement()
                        }
                    }
                ],
            },
            {
                // 搜索内容
                type: 'search',
                positon: ['right', 'top'],
                placeholder: '请输入项目名称或备注',
                searchParam: 'search', //搜索请求字段，默认为 search
                value: '', // 当前内容,默认为空
            },
            {
                // 批量操作
                type: 'batch', //batch_btn
                positon: ['left', 'bottom'],
                placeholder: '请选择批量操作',
                buttonValue: '批量操作',
                disabledSelectValue: '请选择需要批量操作的站点!',
                selectList: [
                    {
                        title: '删除项目',
                        url: '/project/' + _that.type + '/RemoveProject',
                        param: function (row) {
                            return {
                                data: JSON.stringify({ name: row.name }),
                            };
                        },
                        refresh: true,
                        callback: function (that) {
                            bt.prompt_confirm(
                                '批量删除项目',
                                '您正在删除选中的' + _that.tips + '项目，继续吗？',
                                function () {
                                    that.start_batch({}, function (list) {
                                        var html = '';
                                        for (var i = 0; i < list.length; i++) {
                                            var item = list[i];
                                            html +=
                                                '<tr><td><span>' +
                                                item.name +
                                                '</span></td><td><div style="float:right;"><span style="color:' +
                                                (item.requests.status ? '#20a53a' : 'red') +
                                                '">' + item.requests.msg +
                                                '</span></div></td></tr>';
                                        }
                                        site.model_table.$batch_success_table({
                                            title: '批量删除项目',
                                            th: '项目名称',
                                            html: html,
                                        });
                                        site.model_table.$refresh_table_list(true);
                                    });
                                }
                            );
                        },
                    }
                ],
            },
            {
                //分页显示
                type: 'page',
                positon: ['right', 'bottom'], // 默认在右下角
                pageParam: 'p', //分页请求字段,默认为 : p
                page: 1, //当前分页 默认：1
                numberParam: 'limit',
                //分页数量请求字段默认为 : limit
                number: 20,
                //分页数量默认 : 20条
                numberList: [10, 20, 50, 100, 200], // 分页显示数量列表
                numberStatus: true, //　是否支持分页数量选择,默认禁用
                jump: true, //是否支持跳转分页,默认禁用
            },
        ],
        success: function () {
			// 详情事件
			// bt.files.dir_details()
		}
    });
};

/**
 * @description 获取添加项目配置
 */
CreateWebsiteModel.prototype.getAddProjectConfig = function (data) {
    var that = this,
        data = data || {},
        config = [
            {
                label: '项目路径',
                formLabelWidth: '110px',
                must: '*',
                group: {
                    type: 'text',
                    width: '400px',
                    value: '',
                    name: 'path',
                    placeholder: '项目的根路径',
                    disabled: data.type != 'edit' ? false : true,
                    icon: {
                        type: 'glyphicon-folder-open',
                        select: 'dir',
                        event: function (ev) {},
                        callback: function (path) {
                            var pathList = path.split('/');
                            var fileName = pathList[pathList.length - 1] == '' ? pathList[pathList.length - 2] : pathList[pathList.length - 1];
                            this.config.form[0].group.value = path;
                            this.config.form[1].group.value = fileName;
                            this.$replace_render_content(0);
                            this.$replace_render_content(1);
                            var cThis = this;
                            // 尝试获取运行文件等信息
                            that.getinfo({path:path},function(res){
                                if(res.framework) cThis.config.form[5].group.value = res.framework;cThis.$replace_render_content(5);
                                if(res.requirement_path) cThis.config.form[8].group.value = res.requirement_path;cThis.$replace_render_content(8);
                                if(res.runfile) cThis.config.form[2].group.value = res.runfile;cThis.$replace_render_content(2);
                                if(res.stype || res.xsgi){
                                    cThis.config.form[6].group[0].value = res.stype;
                                    cThis.config.form[6].group[1].value = res.xsgi;
                                    if(res.stype == 'python'){
                                        cThis.config.form[7].display = true;
                                    }else{
                                        cThis.config.form[7].display = false;
                                        cThis.config.form[6].group[1].display = true;
                                    }
                                    cThis.$replace_render_content(6);
                                    cThis.$replace_render_content(7);
                                }
                            })
                        },
                    },
                    verify: function (val) {
                        if (val === '') {
                            bt.msg({ msg: '请选择项目运行文件', status: false });
                            return false;
                        }
                    },
                },
            },
            {
                label: '项目名称',
                formLabelWidth: '110px',
                must: '*',
                group: {
                    type: 'text',
                    name: 'pjname',
                    width: '400px',
                    placeholder: '请输' + that.tips + '项目名称',
                    disabled: data.type != 'edit' ? false : true,
                    verify: function (val) {
                        if (val === '') {
                            bt.msg({ msg: '请输入项目名称', status: false });
                            return false;
                        }
                    },
                },
            },
            {
                label: '运行文件',
                formLabelWidth: '110px',
                must: '*',
                group: {
                    type: 'text',
                    width: '400px',
                    value: '',
                    name: 'rfile',
                    placeholder: '项目的运行文件',
                    icon: {
                        type: 'glyphicon-folder-open',
                        select: 'file',
                        event: function (ev) {},
                        callback: function (path) {
                            this.config.form[2].group.value = path;
                            this.$replace_render_content(2);
                        },
                    },
                    verify: function (val) {
                        if (val === '') {
                            bt.msg({ msg: '请选择项目运行文件', status: false });
                            return false;
                        }
                    },
                },
            },
            {
                label: '项目端口',
                formLabelWidth: '110px',
                must: '*',
                group: {
                    type: 'number',
                    name: 'port',
                    width: '220px',
                    placeholder: '请输入项目的真实端口',
                    unit: '* 请输入项目的真实端口',
                    verify: function (val) {
                        if (val === '') {
                            bt.msg({ msg: '请输入项目端口', status: false });
                            return false;
                        }
                    },
                },
            },
            {
                label: that.tips+'版本',
                formLabelWidth: '110px',
                group: [{
                    type: 'select',
                    name: 'version',
                    width: '150px',
                    disabled: data.type != 'edit' ? false : true,
                    value: that.pyVindexOf != undefined ? that.pyVindexOf.version : '',
                    list: (function(){
                        var list = [];
                        for(var i=0;i<that.pyVersionList.length;i++){
                            var _isInstall = that.pyVersionList[i].installed == '1'?true:false;
                            list.push({title:(that.pyVersionList[i].version+ (data.type !== 'edit' ? ' ['+(_isInstall?'已安装':'未安装')+']' : '')),value:that.pyVersionList[i].version,disabled:!_isInstall});
                        }
                        return list;
                    })(),
                    tips: '',
                },{
                    type:'link',
                    'class': 'mr5',
                    title:'版本管理',
                    event:function(){
                        that.getVersionManagement()
                    }
                }]
            },
            {
                label: '框架',
                formLabelWidth: '110px',
                group: {
                    type: 'select',
                    name: 'framework',
                    width: '150px',
                    disabled: data.type != 'edit' ? false : true,
                    unit: '* 未使用框架请选择python',
                    list: [
                        { title: 'django', value: 'django' },
                        { title: 'flask', value: 'flask' },
                        { title: 'sanic', value: 'sanic' },
                        { title: 'python', value: 'python' },
                    ],
                    tips: '',
                    change:function(value,form,that){
                        that.config.form[6].display = true
                        that.config.form[7].display = false
                        switch(value['framework']){
                            case 'django':
                            case 'flask':
                                that.config.form[6].group[0].value = 'uwsgi'
                                that.config.form[6].group[1].value = 'wsgi';
                                that.config.form[6].group[1].display = true
                                break;
                            case 'sanic':
                                that.config.form[6].group[0].value = 'gunicorn'
                                that.config.form[6].group[1].value = 'asgi';
                                that.config.form[6].group[1].display = true
                                break;
                            case 'python':
                                that.config.form[6].display = false
                                that.config.form[7].display = true
                                that.config.form[6].group[1].display = false
                                break;
                        }
                        that.$replace_render_content(6)
                        that.$replace_render_content(7)
                    }
                },
            },
            {
                label: '运行方式',
                formLabelWidth: '110px',
                group: [{
                    type: 'select',
                    name: 'stype',
                    width: '150px',
                    list: [
                        { title: 'uwsgi', value: 'uwsgi' },
                        { title: 'gunicorn', value: 'gunicorn' },
                        { title: 'python', value: 'python' },
                    ],
                    tips: '',
                    change:function(value,form,that){
                        that.config.form[6].group[0].value = value.stype
                        that.config.form[7].display = value['stype'] == 'python' ?true :false;
                        that.config.form[6].group[1].display = value['stype'] == 'python' ? false : true;
                        if(data.type == 'edit') that.config.form[8].display = value['stype'] == 'python' ? false : true;
                        that.$replace_render_content(6)
                        that.$replace_render_content(7)
                        that.$replace_render_content(8)
                    }
                },{
                    label: '网络协议',
                    type: 'select',
                    name: 'xsgi',
                    width: '150px',
                    display: (data.type == 'edit' && data.stype == 'python') ? false : true,
                    list: [
                        { title: 'wsgi', value: 'wsgi' },
                        { title: 'asgi', value: 'asgi' },
                    ],
                    tips: '',
                }]
            },
            {
                label: '启动方式',
                formLabelWidth: '110px',
                display:false,
                group: {
                    type: 'text',
                    name: 'parm',
                    width: '400px',
                    placeholder: '自定义的启动参数',
                }
            },
            {
                label: '安装依赖包',
                formLabelWidth: '110px',
                group: {
                    type: 'text',
                    width: '400px',
                    value: '',
                    disabled: data.type != 'edit' ? false : true,
                    name: 'requirement_path',
                    placeholder: '如需安装依赖包,请填写依赖包的文件地址[为空则不安装依赖包]',
                    icon: {
                        type: 'glyphicon-folder-open',
                        select: 'file',
                        event: function (ev) {},
                        callback: function (path) {
                            this.config.form[8].group.value = path;
                            this.$replace_render_content(8);
                        },
                    },
                }
            },
            {
                formLabelWidth: '25px',
                group: {
                    type: 'help',
                    list: [
                        '执行命令：请输入项目需要携带的参数，默认请输入执行文件名',
                    ],
                },
            }
        ];
    if (data.type == 'edit') {
        config.splice(8, 2);
        config[4].group[0].value = data.version //版本
        if(data.stype == 'python') config[7].display = true
        config = $.merge(config,[{
            label: '进程数',
            formLabelWidth: '110px',
            must: '*',
            display:data.type != 'edit' || (data.type == 'edit' && data.stype === 'python') ? false : true,
            group: [{
                type: 'number',
                name: 'processes',
                width: '150px',
                placeholder: '进程数',
            },{
                label: '<span class="color-red mr5">*</span>线程数',
                style:{'vertical-align':'inherit'},
                type: 'number',
                name: 'threads',
                width: '150px',
                placeholder: '线程数',
            }]
        },{
            label: '启动用户',
            formLabelWidth: '110px',
            group: {
                type: 'select',
                name: 'user',
                width: '150px',
                list: [
                    { title: 'www', value: 'www' },
                    { title: 'root', value: 'root' },
                ],
                disabled: (data.type == 'edit' && data.stype != 'gunicorn') ? false : true,
            }
        },{
            label: '通信方式',
            formLabelWidth: '110px',
            group: {
                type: 'select',
                name: 'is_http',
                width: '150px',
                list: [
                    { title: 'http', value: true },
                    { title: 'socket', value: false },
                ]
            }
        },{
            formLabelWidth: '110px',
            group: {
                type: 'button',
                name: 'submitForm',
                title: '保存配置',
                event: function (fromData, ev,thatC) {
                    if(data.stype == 'uwsgi' || data.stype == 'gunicorn'){
                        fromData['logpath'] = thatC['data']['logpath'];
                        fromData['loglevel'] = thatC['data']['loglevel'];
                    }
                    if(fromData.rfile == '') return bt.msg({ msg: '请选择项目运行文件', status: false });
                    switch(thatC['data']['stype']){
                        case 'uwsgi':
                            fromData.is_http = fromData.is_http == 'true' ? true : false;
                        case 'python':
                            if (parseInt(fromData.port) < 0 || parseInt(fromData.port) > 65535) return layer.msg('项目端口格式错误，可用范围：1-65535',{icon:2})
                            if(fromData.processes == '') return bt.msg({ msg: '请输入进程数', status: false });
                            if(fromData.threads == '') return bt.msg({ msg: '请输入线程数', status: false });
                            break;
                        case 'gunicorn':
                            if(fromData.parm == '') return bt.msg({ msg: '请输入启动参数', status: false });
                            break;
                    }
                    // 编辑项目
                    that.modifyProject({name:data.pjname,data:fromData}, function (res) {
                        site.model_table.$refresh_table_list()
                        bt.msg({ status: res.status, msg: res.msg });
                        that.simulatedClick(0);
                    });
                },
            },
        }])
        if(data.stype != 'uwsgi') config.splice(10,1)
    }
    return config;
};

/**
 * @description 渲染添加项目表单
 */
CreateWebsiteModel.prototype.renderAddProject = function (callback) {
    var that = this;
    this.addModelForm = bt_tools.open({
        title: '添加' + this.tips + '项目',
        area: '620px',
        btn: ['提交', '取消'],
        content: {
            class: 'pd30 bt-model-create-view',
            formLabelWidth: '120px',
            form: (function () {
                return that.getAddProjectConfig();
            })(),
        },
        yes: function (formData, indexs, layero) {
            if (parseInt(formData.port) < 0 || parseInt(formData.port) > 65535) return layer.msg('项目端口格式错误，可用范围：1-65535',{icon:2})
            var _command = null;
            var loadT = bt.load('正在加载，请稍后...')
            that.createProject(formData, function (res) {
                if (res.status) {
                    layer.close(indexs);
                    if (_command > 0) layer.close(_command);
                    if (callback) callback(res);
                }else{
                    _command = -1
                }
                bt.msg({ msg: res.msg, status: res.status });
            });
            setTimeout(function () {
                if (_command < 0) return false;
                loadT.close()
                _command = that.installVersionLog({ shell: 'tail -f  /www/server/python_project/vhost/logs/'+formData.pjname+'.log' })
            }, 1000);
        },
    });
    return this.addModelForm;
};
/**
 * @description 获取python版本安装情况
 */
CreateWebsiteModel.prototype.getVersionManagement = function () {
    var _that = this;
    bt_tools.open({
        type: 1,
        title: _that.tips +'版本管理',
        area: ['460px', '470px'],
        btn: false,
        content: '<div class="pd15"><div id="versionManagement"></div></div>',
        success: function () {
            var versionTable = bt_tools.table({
                el: '#versionManagement',
                url:'/project/python/GetCloudPython',
                height: '390px',
                load:'正在获取版本信息...',
                dataFilter: function (res) {
                    _that.pyVersionList = res.data;
                    return {data:res.data}
                },
                column: [
                    { type:'text',fid: 'version', title: '版本号' },
                    { type:'text',title:'安装状态',template:function(row){
                            return row.installed == '1' ? '<span style="color:#20a53a">已安装</span>' : '<span style="color:#d9534f">未安装</span>'
                        }},
                    {type:'text',align: 'right',title:'操作',template:function(row){
                            return row.installed == '1' ? '<a class="bterror">卸载</a>' : '<a class="btlink">安装</a>'
                        },event:function(row){
                            var is_installed = row.installed == '1' ? true : false;
                            bt.confirm({
                                title: (is_installed?'卸载':'安装')+'Python版本',
                                msg: is_installed?'卸载['+row.version+']版本后，相关项目将无法启动，是否继续？':'是否安装['+row.version+']版本？'
                            }, function () {
                                var _command = null;
                                if(!is_installed){
                                    setTimeout(function () {
                                        if (_command < 0) return false;
                                        _command = _that.installVersionLog({ shell: 'tail -f /www/server/python_project/vhost/logs/py.log' })
                                    }, 500);
                                }
                                _that[(is_installed ? 'removePythonV' : 'installPythonV')](
                                    {version:row.version},
                                    function(res){
                                        if(res.status){
                                            versionTable.$refresh_table_list(true);
                                            if (_command > 0) layer.close(_command)
                                        }
                                        bt.msg(res)
                                    })
                            });
                        }}
                ]
            })
            $('#versionManagement').find('.mtb10').css('margin','0')
        },
        cancel: function () {
            if(_that.addModelForm != null && $('.bt-model-create-view').length > 0){
                var versionIndex = _that.pyVersionList.find(function (item) {
                    return item.installed == '1';
                })
                var _addModel = _that.addModelForm.form
                _addModel.config.form[4]['group'][0].value = versionIndex != undefined ? versionIndex.version : ''
                _addModel.config.form[4]['group'][0].list = (function(){
                    var list = [];
                    for(var i=0;i<_that.pyVersionList.length;i++){
                        var _isInstall = _that.pyVersionList[i].installed == '1'?true:false;
                        list.push({title:(_that.pyVersionList[i].version+' ['+(_isInstall?'已安装':'未安装')+']'),value:_that.pyVersionList[i].version,disabled:!_isInstall});
                    }
                    return list;
                })()
                _that.addModelForm.form.$replace_render_content(4)
            }
        }
    })
};
/**
 * @description 获取python版本安装情况
 */
CreateWebsiteModel.prototype.getPythonVersion = function (callback) {
    var _this = this;
    this.getCloudPython({},function (res) {
        _this.pyVersionList = res.data;
        _this.pyVindexOf = res.data.find(function (item) {
            return item.installed == '1';
        })
        if(callback) callback(res)
    })
}
/**
 * @description
 * @param {string} name 站点名称
 */
CreateWebsiteModel.prototype.renderProjectInfoView = function (row) {
    var that = this;
    bt.open({
        type: 1,
        title:this.tips + '项目管理-[' + row.name + ']，添加时间[' + row.addtime + ']',
        skin: 'model_project_dialog',
        area: ['780px', '720px'],
        content:
            '<div class="bt-tabs">' +
            '<div class="bt-w-menu site-menu pull-left"></div>' +
            '<div id="webedit-con" class="bt-w-con pd15" style="height:100%">' +
            '</div>' +
            '<div class="mask_module hide" style="left:110px;"><div class="node_mask_module_text">请开启<a href="javascript:;" class="btlink mapExtranet" onclick="site.node.simulated_click(2)"> 外网映射 </a>后查看配置信息</div></div>' +
            '</div>',
        btn: false,
        success: function (layers) {
            var $layers = $(layers),
                $content = $layers.find('#webedit-con');

            function render_tab_list(config) {
                for (var i = 0; i < config.list.length; i++) {
                    var item = config.list[i],
                        tab = $(
                            '<p class="' + (i === 0 ? 'bgw' : '') + '">' + item.title + '</p>'
                        );
                    $(config.el).append(tab);
                    (function (i, item) {
                        tab.on('click', function (ev) {
                            $('.mask_module').addClass('hide');
                            $(this).addClass('bgw').siblings().removeClass('bgw');
                            if ($(this).hasClass('bgw')) {
                                that.getProjectInfo({ name: row.name }, function (res) {
                                    config.list[i].event.call(that, $content, res, ev);
                                });
                            }
                        });
                        if (item.active) tab.click();
                    })(i, item);
                }
            }
            render_tab_list(
                {
                    el: $layers.find('.bt-w-menu'),
                    list: [
                        {
                            title: '项目配置',
                            active: true,
                            event: that.renderProjectConfigView,
                        },
                        {
                            title: '域名管理',
                            event: that.renderDomainManageView,
                        },
                        {
                            title: '外网映射',
                            event: that.renderProjectMapView,
                        },
                        {
                            title: '配置文件',
                            event: that.renderFileConfigView,
                        },
                        {
                            title: '运行配置',
                            event: that.renderFrameworkConfigView,
                        },
                        {
                            title: '服务状态',
                            event: that.renderServiceStatusView,
                        },
                        {
                            title: '项目日志',
                            event: that.renderProjectLogsView,
                        },
                    ],
                },
                function (config, i, ev) {}
            );
        },
    });
};
/**
 * @description 项目配置
 * @param {object} row 项目信息
 */
CreateWebsiteModel.prototype.renderProjectConfigView = function (el, row) {
    var that = this,
        projectConfig = row.project_config,
        _config = that.getAddProjectConfig( $.extend(projectConfig,{ type: 'edit' }) );
    bt_tools.form({
        el: '#webedit-con',
        data: projectConfig,
        class: 'ptb15',
        form: _config
    });
};
/**
 * @description 域名管理
 * @param {object} row 项目信息
 */
CreateWebsiteModel.prototype.renderDomainManageView = function (el, row,ev) {
    var that = this,
        list = [
            {
                class: 'mb0',
                items: [
                    {
                        name: 'modeldomain',
                        width: '340px',
                        type: 'textarea',
                        placeholder:
                            '如果需要绑定外网，请输入需要映射的域名，该选项可为空<br>多个域名，请换行填写，每行一个域名，默认为80端口<br>泛解析添加方法 *.domain.com<br>如另加端口格式为 www.domain.com:88',
                    },
                    {
                        name: 'btn_model_submit_domain',
                        text: '添加',
                        type: 'button',
                        callback: function (sdata) {
                            var arrs = sdata.modeldomain.split('\n');
                            var domins = [];
                            for (var i = 0; i < arrs.length; i++) domins.push(arrs[i]);
                            if (domins[0] == '')
                                return layer.msg('域名不能为空', { icon: 0 });
                            that.addProjectDomain(
                                { name: row.name, domains: domins },
                                function (res) {
                                    if (typeof res.status == 'undefined') {
                                        $('[name=modeldomain]').val('');
                                        $('.placeholder').css('display', 'block');
                                        site.render_domain_result_table(res)
                                        project_domian.$refresh_table_list(true);
                                    }else{
                                        bt.msg({ status: res.status, msg: res.error_msg });
                                    }
                                }
                            );
                        },
                    },
                ],
            },
        ];
    var _form_data = bt.render_form_line(list[0]),
        loadT = null,
        placeholder = null;
    el.html(_form_data.html + '<div id="project_domian_list"></div>');
    bt.render_clicks(_form_data.clicks);
    // domain样式
    $('.btn_model_submit_domain')
        .addClass('pull-right')
        .css('margin', '30px 35px 0 0');
    $('textarea[name=modeldomain]').css('height', '120px');
    placeholder = $('.placeholder');
    placeholder
        .click(function () {
            $(this).hide();
            $('.modeldomain').focus();
        })
        .css({
            width: '340px',
            heigth: '120px',
            left: '0px',
            top: '0px',
            'padding-top': '10px',
            'padding-left': '15px',
        });
    $('.modeldomain')
        .focus(function () {
            placeholder.hide();
            loadT = layer.tips(placeholder.html(), $(this), {
                tips: [1, '#20a53a'],
                time: 0,
                area: $(this).width(),
            });
        })
        .blur(function () {
            if ($(this).val().length == 0) placeholder.show();
            layer.close(loadT);
        });
    var project_domian = bt_tools.table({
        el: '#project_domian_list',
        url: '/project/' + that.type + '/GetProjectDomain',
        default: '暂无域名列表',
        param: { name: row.name },
        height: 375,
        beforeRequest: function (params) {
            if (params.hasOwnProperty('data') && typeof params.data === 'string')
                return params;
            return { data: JSON.stringify(params) };
        },
        column: [
            { type: 'checkbox', class: '', width: 20 },
            {
                fid: 'name',
                title: '域名',
                type: 'text',
                template: function (row) {
                    return (
                        '<a href="http://' +
                        row.name +
                        ':' +
                        row.port +
                        '" target="_blank" class="btlink">' +
                        row.name +
                        '</a>'
                    );
                },
            },
            {
                fid: 'port',
                title: '端口',
                type: 'text',
            },
            {
                title: '操作',
                type: 'group',
                width: '100px',
                align: 'right',
                group: [
                    {
                        title: '删除',
                        template: function (row, that) {
                            return that.data.length === 1 ? '<span>不可操作</span>' : '删除';
                        },
                        event: function (rowc, index, ev, key, rthat) {
                            if (ev.target.tagName == 'SPAN') return;
                            if (rthat.data.length === 1) {
                                return bt.msg({ status: false, msg: '最后一个域名不能删除!' });
                            }
                            that.removeProjectDomain(
                                { name: row.name, domain: rowc.name },
                                function (res) {
                                    bt.msg({
                                        status: res.status,
                                        msg: res.msg,
                                    });
                                    rthat.$refresh_table_list(true);
                                }
                            );
                        },
                    },
                ],
            },
        ],
        tootls: [
            {
                // 批量操作
                type: 'batch',
                positon: ['left', 'bottom'],
                placeholder: '请选择批量操作',
                buttonValue: '批量操作',
                disabledSelectValue: '请选择需要批量操作的站点!',
                selectList: [
                    {
                        title: '删除域名',
                        load: true,
                        url: '/project/' + that.type + '/MultiRemoveProjectDomain',
                        param: {name:row.name},
                        paramId: 'id',
                        paramName: 'domain_ids',
                        theadName: '域名',
                        confirmVerify: false, //是否提示验证方式
                        refresh: true,
                        beforeRequest: function (list) {
                            var arry = [];
                            $.each(list, function (index, item) {
                                arry.push(item.id);
                            });
                            return JSON.stringify(arry);
                        }
                        // callback: function (that) {
                        // 	// 手动执行,data参数包含所有选中的站点
                        // 	bt.show_confirm(
                        // 		'批量删除域名',
                        // 		"<span style='color:red'>同时删除选中的域名，是否继续？</span>",
                        // 		function () {
                        // 			var param = {};
                        // 			that.start_batch(param, function (list) {
                        // 				var html = '';
                        // 				for (var i = 0; i < list.length; i++) {
                        // 					var item = list[i];
                        // 					html +=
                        // 						'<tr><td>' +
                        // 						item.name +
                        // 						'</td><td><div style="float:right;"><span style="color:' +
                        // 						(item.request.status ? '#20a53a' : 'red') +
                        // 						'">' +
                        // 						(item.request.status ? '成功' : '失败') +
                        // 						'</span></div></td></tr>';
                        // 				}
                        // 				project_domian.$batch_success_table({
                        // 					title: '批量删除',
                        // 					th: '删除域名',
                        // 					html: html,
                        // 				});
                        // 				project_domian.$refresh_table_list(true);
                        // 			});
                        // 		}
                        // 	);
                        // },
                    },
                ],
            },
        ],
    });
    setTimeout(function () {
        $(el).append(
            '<ul class="help-info-text c7">' +
            '<li>如果您的是HTTP项目，且需要映射到外网，请至少绑定一个域名</li>' +
            '<li>建议所有域名都使用默认的80端口</li>' +
            '</ul>'
        );
    }, 100);
};

/**
 * @description 渲染项目外网映射
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.renderProjectMapView = function (el, row) {
    var that = this;
    el.html(
        '<div class="pd15"><div class="ss-text mr50" style="display: block;height: 35px;">' +
        '   <em title="外网映射">外网映射</em>' +
        '       <div class="ssh-item">' +
        '           <input class="btswitch btswitch-ios" id="model_project_map" type="checkbox">' +
        '           <label class="btswitch-btn" for="model_project_map" name="model_project_map"></label>' +
        '       </div>' +
        '</div><ul class="help-info-text c7"><li>如果您的是HTTP项目，且需要外网通过80/443访问，请开启外网映射</li><li>开启外网映射前，请到【域名管理】中至少添加1个域名</li></ul></div>'
    );
    $('#model_project_map').attr(
        'checked',
        row['project_config']['bind_extranet'] ? true : false
    );
    $('[name=model_project_map]').click(function () {
        var _check = $('#model_project_map').prop('checked'),
            param = { name: row.name };
        if (!_check) param['domains'] = row['project_config']['domains'];
        layer.confirm(
            (!_check ? '开启外网映射后，可以通过绑定域名进行访问' : '关闭外网映射后，已绑定域名将取消关联访问') + '，是否继续操作？',
            {
                title: '外网映射',
                icon: 0,
                closeBtn: 2,
                cancel: function () {
                    $('#model_project_map').prop('checked', _check);
                },
            },
            function () {
                that[_check ? 'unbindExtranet' : 'bindExtranet'](param, function (res) {
                    if (!res.status) $('#model_project_map').prop('checked', _check);
                    bt.msg({
                        status: res.status,
                        msg: res.msg,
                    });
                    row['project_config']['bind_extranet'] = _check ? 0 : 1;
                });
            },
            function () {
                $('#model_project_map').prop('checked', _check);
            }
        );
    });
};

/**
 * @description 渲染项目服务状态
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.renderServiceStatusView = function (el, row) {
    var _this = this
    var arry = [
            { title: '启动', event: this.startProject },
            { title: '停止', event: this.stopProject },
            { title: '重启', event: this.restartProject },
        ],
        that = this,
        html = $(
            '<div class="soft-man-con bt-form"><p class="status"></p><div class="sfm-opt"></div></div>'
        );
    function reander_service(status) {
        var status_info = status
            ? ['开启', '#20a53a', 'play']
            : ['停止', 'red', 'pause'];
        return (
            '当前状态：<span>' +
            status_info[0] +
            '</span><span style="color:' +
            status_info[1] +
            '; margin-left: 3px;" class="glyphicon glyphicon glyphicon-' +
            status_info[2] +
            '"></span>'
        );
    }
    html.find('.status').html(reander_service(row.run));
    el.html(html);
    for (var i = 0; i < arry.length; i++) {
        var item = arry[i],
            btn = $('<button class="btn btn-default btn-sm"></button>');
        (function (btn, item, indexs) {
            !(row.run && indexs === 0) || btn.addClass('hide');
            !(!row.run && indexs === 1) || btn.addClass('hide');
            btn
                .on('click', function () {
                    bt.simple_confirm(
                        {
                            title: item.title +_this.tips+ '项目【' + row.name + '】',
                            msg: item.title + '项目后'+ (item.title === '停止' ? '将无法正常访问项目' : (item.title === '启动' ? '，用户可以正常访问项目内容' : '将重新加载项目')) + '，是否继续操作？',
                        },
                        function (index) {
                            layer.close(index);
                            item.event.call(that, { name: row.name }, function (res) {
                                row.run = indexs === 0 ? true : indexs === 1 ? false : row.run;
                                html.find('.status').html(reander_service(row.run));
                                $('.sfm-opt button').eq(0).addClass('hide');
                                $('.sfm-opt button').eq(1).addClass('hide');
                                $('.sfm-opt button')
                                    .eq(row.run ? 1 : 0)
                                    .removeClass('hide');
                                bt.msg({ status: res.status, msg: res.msg });
                            });
                        }
                    );
                })
                .text(item.title);
        })(btn, item, i);
        el.find('.sfm-opt').append(btn);
    }
};

/**
 * @description 渲染项目日志
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.renderProjectLogsView = function (el, row) {
    var that = this,
        _config = row.project_config,
        log_config = '<div class="model_project_log_config" style="margin-bottom: 15px;">\
		'+(_config.stype == 'gunicorn'?'日志级别 <select class="bt-input-text mr5" name="model_log_level">\
				<option>debug</option>\
				<option>info</option>\
				<option>warning</option>\
				<option>error</option>\
				<option>critical</option>\
			</select>':'')+'\
		日志路径 <input type="text" name="model_log_path" id="model_log_path" value="'+_config.logpath+'" placeholder="日志路径" class="bt-input-text mr10" style="width:350px" />\
		<span class="glyphicon glyphicon-folder-open cursor mr10" onclick="bt.select_path(\'model_log_path\',\'dir\')"></span>\
		<button class="btn btn-success btn-sm" name="submitLogConfig">保存</button>\
		</div>'
    el.html(log_config+'<div class="model_project_log"></div>');
    $('[name=model_log_level]').val(_config.loglevel);
    this.getProjectLog({ name: row.name }, function (res) {
        $('#webedit-con .model_project_log').html(
            '<pre class="command_output_pre" style="height:580px;">' +
            (typeof res == 'object' ? res.data : res) +
            '</pre>'
        );
        // $('#webedit-con .model_project_log').html(
        //     '<div class="mb15">日志大小<span class="ml10">'+ res.size +'</span></div><pre class="command_output_pre" style="height:500px;">' +
        //     (typeof res == 'object' ? res.data : res) +
        //     '</pre>'
        // );
		// $.post({url: '/project/python/get_log_split', data: { name: row.name }}, function (rdata) {
        //   var html = '',configInfo = {}
        //   if(rdata.status) configInfo = rdata.data
		// 	    html = '开启后' + (rdata.status ? rdata.data.log_size ? '日志文件大小超过'+ bt.format_size(rdata.data.log_size,true,2,'MB') +'时进行切割日志文件' : '每天'+ rdata.data.hour +'点' + rdata.data.minute + '分进行切割日志文件' : '默认每天2点0分进行切割日志文件')
        //   $('#webedit-con .model_project_log .command_output_pre').before('<div class="inlineBlock log-split mb20" style="line-height: 32px;">\
        //   <label>\
        //     <div class="bt-checkbox '+ (rdata.status && rdata.data.status ? 'active':'') +'"></div>\
        //     <span>日志切割</span>\
        //   </label>\
        //   <span class="unit">'+html+'，如需修改请点击<a href="javascript:;" class="btlink mamger_log_split">编辑配置</a></span>\
        //   </div>')
		// 			$('#webedit-con .model_project_log .log-split').hover(function(){
        //     layer.tips('当日志文件过大时，读取和搜索时间会增加，同时也会占用存储空间，因此需要对日志进行切割以方便管理和维护。', $(this), {tips: [3, '#20a53a'], time: 0});
        //   },function(){
        //     layer.closeAll('tips');
        //   })
        //   $('#webedit-con .model_project_log label').click(function(){
        //     if(rdata['is_old']){
        //         bt_tools.msg(rdata)
        //         return;
        //     }
        //     bt.confirm({title:'设置日志切割任务',msg: !rdata.status || (rdata.status && !rdata.data.status) ? '开启后对该项目日志进行切割，是否继续操作？' : '关闭后将无法对该项目日志进行切割，是否继续操作？'},function(){
        //       if(rdata.status){
        //         bt_tools.send({url:'/project/python/set_log_split',data:{name: row.name}},function(res){
        //           bt_tools.msg(res)
        //           if(res.status) {
        //             that.simulatedClick(6);
        //           }
        //         })
        //       }else{
        //         bt_tools.send({url:'/project/python/mamger_log_split',data:{name: row.name}},function(res){
        //           bt_tools.msg(res)
        //           if(res.status) {
        //             that.simulatedClick(6);
        //             layer.close(indexs)
        //           }
        //         })
        //       }
        //     })
        //   })
        //   $('.mamger_log_split').click(function(){
        //     if(rdata['is_old']){
        //         bt_tools.msg(rdata)
        //         return;
        //     }
        //     bt_tools.open({
        //       type: 1,
        //       area: '460px',
        //       title: '配置日志切割任务',
        //       closeBtn: 2,
        //       btn: ['提交', '取消'],
        //       content: {
        //         'class': 'pd20 mamger_log_split_box',
        //         form: [{
        //           label: '执行时间',
        //           group: [{
		// 								type: 'text',
		// 								name: 'day',
		// 								width: '44px',
		// 								value: '每天',
		// 								disabled: true
		// 							},{
        //             type: 'number',
        //             name: 'hour',
        //             'class': 'group',
        //             width: '70px',
        //             value: configInfo.hour || '2',
        //             unit: '时',
        //             min: 0,
        //             max: 23
        //           }, {
        //             type: 'number',
        //             name: 'minute',
        //             'class': 'group',
        //             width: '70px',
        //             min: 0,
        //             max: 59,
        //             value: configInfo.minute || '0',
        //             unit: '分'
        //           }]
        //         },{
        //           label: '日志大小',
        //           group:{
        //             type: 'text',
        //             name: 'log_size',
        //             width: '210px',
        //             value: configInfo.log_size ? bt.format_size(configInfo.log_size,true,2,'MB').replace(' MB','') : '',
        //             unit: 'MB',
        //             placeholder: '请输入日志大小',
        //           }
        //         }, {
        //           label: '保留最新',
        //           group:{
        //             type: 'number',
        //             name: 'num',
        //             'class': 'group',
        //             width: '70px',
        //             value: configInfo.num || '180',
        //             unit: '份'
        //           }
        //         }]
        //       },
        //       success: function (layero, index) {
        //         $(layero).find('.mamger_log_split_box .bt-form').prepend('<div class="line">\
        //         <span class="tname">切割方式</span>\
        //         <div class="info-r">\
        //           <div class="replace_content_view" style="line-height: 32px;">\
        //             <div class="checkbox_config">\
		// 									<i class="file_find_radio '+ (configInfo.log_size ? 'active' : '') +'"></i>\
        //               <span class="laberText" style="font-size: 12px;">按日志大小</span>\
        //             </div>\
        //             <div class="checkbox_config">\
        //               <i class="file_find_radio '+ (configInfo.log_size > 0 ? '' : 'active') +'"></i>\
        //               <span class="laberText" style="font-size: 12px;">按执行时间</span>\
        //             </div>\
        //           </div>\
        //         </div>')
        //         $(layero).find('.mamger_log_split_box .bt-form').append('<div class="line"><div class=""><div class="inlineBlock  "><ul class="help-info-text c7"><li>每5分钟执行一次</li><li>【日志大小】：日志文件大小超过指定大小时进行切割日志文件</li><li>【保留最新】：保留最新的日志文件，超过指定数量时，将自动删除旧的日志文件</li></ul></div></div></div>')
        //         $(layero).find('.replace_content_view .checkbox_config').click(function(){
        //           var index = $(this).index()
        //           $(this).find('i').addClass('active').parent().siblings().find('i').removeClass('active')
        //           if(index){
        //             $(layero).find('[name=hour]').parent().parent().parent().show()
        //             $(layero).find('[name=log_size]').parent().parent().parent().hide()
        //             $(layero).find('.help-info-text li').eq(0).hide().next().hide()
        //           }else{
        //             $(layero).find('[name=hour]').parent().parent().parent().hide()
        //             $(layero).find('[name=log_size]').parent().parent().parent().show()
        //             $(layero).find('.help-info-text li').eq(0).show().next().show()
        //           }
        //         })
        //         if(configInfo.log_size) {
        //           $(layero).find('[name=hour]').parent().parent().parent().hide()
        //         }else{
        //           $(layero).find('[name=log_size]').parent().parent().parent().hide()
        //           $(layero).find('.help-info-text li').eq(0).hide().next().hide()
        //         }
        //         $(layero).find('[name=log_size]').on('input', function(){
        //           if($(this).val() < 1 || !bt.isInteger(parseFloat($(this).val()))) {
        //             layer.tips('请输入日志大小大于0的的整数', $(this), { tips: [1, 'red'], time: 2000 })
        //           }
        //         })
        //         $(layero).find('[name=hour]').on('input', function(){
        //           if($(this).val() > 23 || $(this).val() < 0 || !bt.isInteger(parseFloat($(this).val()))) {
        //             layer.tips('请输入小时范围0-23的整数时', $(this), { tips: [1, 'red'], time: 2000 })
        //           }
        //           $(layero).find('.hour').text($(this).val())
        //         })
        //         $(layero).find('[name=minute]').on('input', function(){
        //           if($(this).val() > 59 || $(this).val() < 0 || !bt.isInteger(parseFloat($(this).val()))) {
        //             layer.tips('请输入正确分钟范围0-59分的整数', $(this), { tips: [1, 'red'], time: 2000 })
        //           }
        //           $(layero).find('.minute').text($(this).val())
        //         })
        //         $(layero).find('[name=num]').on('input', function(){
        //           if($(this).val() < 1 || $(this).val() > 1800 || !bt.isInteger(parseFloat($(this).val()))) {
        //             layer.tips('请输入保留最新范围1-1800的整数', $(this), { tips: [1, 'red'], time: 2000 })
        //           }
        //         })
        //       },
        //       yes: function (formD,indexs) {
        //         formD['name'] = row.name
		// 						delete formD['day']
        //         if($('.mamger_log_split_box .file_find_radio.active').parent().index()) {
		// 							if (formD.hour < 0 || formD.hour > 23 || isNaN(formD.hour) || formD.hour === '' || !bt.isInteger(parseFloat(formD.hour))) return layer.msg('请输入小时范围0-23时的整数')
		// 							if (formD.minute < 0 || formD.minute > 59 || isNaN(formD.minute) || formD.minute === '' || !bt.isInteger(parseFloat(formD.minute))) return layer.msg('请输入正确分钟范围0-59分的整数')
		// 							formD['log_size'] = 0
		// 						}else{
		// 							if(formD.log_size == '' || !bt.isInteger(parseFloat(formD.log_size))) return layer.msg('请输入日志大小大于0的的整数')
		// 						}
		// 						if(formD.num < 1 || formD.num > 1800 || !bt.isInteger(parseFloat(formD.num))) return layer.msg('请输入保留最新范围1-1800的整数')
        //         if(!rdata.status || (rdata.status && !rdata.data.status)) {
		// 							if(rdata.status){
		// 								that.set_log_split({name: row.name},function(res){
		// 									if(res.status) {
		// 										pub_open()
		// 									}
		// 								})
		// 							}else{
		// 								pub_open()
		// 							}
		// 						}else{
		// 							pub_open()
		// 						}
		// 						function pub_open() {
		// 							that.mamger_log_split(formD,function(res){
		// 								bt.msg(res)
		// 								if(res.status) {
		// 									that.renderProjectLogsView(el, row);
		// 									layer.close(indexs)
		// 								}
		// 							})
		// 						}
        //       }
        //     })
        //   })
        // })
        $('.command_output_pre').scrollTop(
            $('.command_output_pre').prop('scrollHeight')
        );
    });
    // 保存按钮
    $('[name=submitLogConfig]').click(function () {
        var logpath = $('[name=model_log_path]').val(),
            loglevel = $('[name=model_log_level]').val(),
            param  = { name: row.name, data:{logpath: logpath} };
        if (!logpath) {
            bt.msg({ status: false, msg: '日志路径不能为空' });
            return;
        }
        //gunicorn时才有日志级别
        if(_config.stype == 'gunicorn'){
            param.data.loglevel = loglevel;
        }
        // 编辑项目
        that.modifyProject(param, function (res) {
            bt.msg({ status: res.status, msg: res.msg });
            that.simulatedClick(5);
        });
    })
};

/**
 * @description 渲染项目配置文件
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.renderFileConfigView = function (el, row) {
    el.empty();
    if (row.project_config.bind_extranet === 0) {
        $('.mask_module')
            .removeClass('hide')
            .find('.node_mask_module_text:eq(1)')
            .hide()
            .prev()
            .show();
        return false;
    }
    site.edit.set_config({ name: this.type + '_' + row.name });
};
/**
 * @description 渲染运行配置文件
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.renderFrameworkConfigView = function(el,row){
    var that = this,_aceEditor = null;
    var con = '<div class="bt-input-text ace_config_editor_scroll" style="height: 400px; line-height:18px;font-size:12px" id="siteConfigBody"></div>\
	<button id="OnlineProjectSubmit" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
	<ul class="c7 ptb15">\
		<li>此处为运行配置文件,若您不了解配置规则,请勿随意修改.</li>\
	</ul>';
    $("#webedit-con").html(con);
    this.getConfFile({ name: row.name }, function (res) {
        _aceEditor = ace.edit('siteConfigBody', {
            theme: "ace/theme/chrome", //主题
            mode: "ace/mode/python", // 语言类型
            wrap: true,
            showInvisibles: false,
            showPrintMargin: false,
            showFoldWidgets: false,
            useSoftTabs: true,
            tabSize: 2,
            showPrintMargin: false,
            readOnly: false
        })

        _aceEditor.setValue(res.data)
    })
    $("#OnlineProjectSubmit").click(function (e) {
        that.saveConfFile({ name: row.name, data: _aceEditor.getValue()  }, function (res) {
            if(res.status) bt.msg({ status: res.status, msg: res.msg });
        })
    });
}
/**
 * @description 渲染项目模块
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.renderProjectModuleView = function(row){
    var that = this;
    bt_tools.open({
        type: 1,
        title: '项目【' + row.name + '】模块管理',
        area: ['600px', '430px'],
        closeBtn: 2,
        btn:false,
        content: '<div class="project_module_title" style="padding: 15px 15px 0 15px;">\
				<input type="text" name="project_module_name" placeholder="虚拟环境模块名称" class="bt-input-text mr10" style="width:270px" />\
				<input type="text" name="project_module_version" placeholder="模块版本" class="bt-input-text mr10" style="width:160px" />\
				<button class="btn btn-success btn-sm" name="project_module_install">安装模块</button>\
			</div>\
			<div class="project_module_table plr15"></div>',
        success:function(){
            var project_model = bt_tools.table({
                el: '.project_module_table',
                url: '/project/' + that.type + '/GetPackages',
                param: { name: row.name },
                load:'正在获取模块列表...',
                height:'317px',
                column:[
                    { fid: '0',title: '模块名',type: 'text',template:function(row){return row[0]} },
                    { fid: '1',title: '版本',type: 'text',width:60,template:function(row){return row[1]} },
                    { title: '操作',type: 'group',width: 70,align: 'right',group: [
                            {
                                title: '卸载',
                                event: function (rowc) {
                                    bt.confirm({
                                        title: '卸载项目环境模块',
                                        msg: '卸载['+rowc[0]+']后，模块相关的全局变量将无法调用，是否继续？'
                                    }, function () {
                                        bt_tools.send({url: '/project/' + that.type + '/MamgerPackage',data: { name:row.name,act:'uninstall',p:rowc[0],v:rowc[1]}},function (res) {
                                            bt.msg(res);
                                            if(res.status)project_model.$refresh_table_list(true);
                                        },{ load: '正在卸载项目模块' });
                                    });
                                }
                            }
                        ]}
                ]
            })

            //安装模块
            $('[name=project_module_install]').click(function(){
                var name = $('[name=project_module_name]').val(),
                    version = $('[name=project_module_version]').val();
                if(!name){
                    bt.msg({status:false,msg:'虚拟环境模块名称不能为空'});
                    return;
                }
                bt_tools.send({url: '/project/' + that.type + '/MamgerPackage',data: { name:row.name,act:'install',p:name,v:version}},function (res) {
                    bt.msg(res);
                    if(res.status){
                        $('[name=project_module_name],[name=project_module_version]').val('')
                        project_model.$refresh_table_list(true);
                    }
                },{ load: '正在安装项目模块' });
            })
        }
    })
};
/**
 * @description 模拟点击
 */
CreateWebsiteModel.prototype.simulatedClick = function (num) {
    console.log(num)
    $('.bt-w-menu p:eq(' + num + ')').click();
};
/**
 * @description 获取python版本安装情况
 */
CreateWebsiteModel.prototype.installVersionLog = function (config) {
    var r_command = layer.open({
        type: 1,
        title: config.name || '正在安装python版本，请稍候...',
        closeBtn: 0,
        area: ['500px', '342px'],
        skin: config.class || 'module_commmand',
        shadeClose: false,
        content: '<div class="python_module_command"></div>',
        success: function () {
            bt_tools.command_line_output({ el: '.python_module_command', shell: config.shell, area: config.area || ['100%', '300px'] })
        }
    })
    return r_command;
}
/**
 * @description 绑定请求
 */
CreateWebsiteModel.prototype.bindHttp = function () {
    var that = this;
    for (const item in this.methods) {
        if (Object.hasOwnProperty.call(this.methods, item)) {
            const element = that.methods[item];
            (function (element) {
                CreateWebsiteModel.prototype[item] = function (param, callback) {
                    bt_tools.send(
                        {
                            url: '/project/' + that.type + '/' + element[0],
                            data: { data: JSON.stringify(param) },
                        },
                        function (data) {
                            if (callback) callback(data);
                        },
                        { load: element[1],verify:element[2] }
                    );
                };
            })(element);
        }
    }
};