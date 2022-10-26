function CreateWebsiteModel(config) {
	this.type = config.type;
	this.tips = config.tips;
	this.methods = {
		createProject: ['create_project', '创建' + config.tips + '项目'],
		modifyProject: ['modify_project', '修改' + config.tips + '项目'],
		removeProject: ['remove_project', '删除' + config.tips + '项目'],
		startProject: ['start_project', '启动' + config.tips + '项目'],
		stopProject: ['stop_project', '停止' + config.tips + '项目'],
		restartProject: ['restart_project', '重启' + config.tips + '项目'],
		getProjectInfo: ['get_project_info', '获取' + config.tips + '项目信息'],
		getProjectDomain: ['project_get_domain', '获取' + config.tips + '项目域名'],
		addProjectDomain: ['project_add_domain', '添加' + config.tips + '项目域名'],
		removeProjectDomain: [
			'project_remove_domain',
			'删除' + config.tips + '项目域名',
		],
		getProjectLog: ['get_project_log', '获取' + config.tips + '项目日志'],
		bindExtranet: ['bind_extranet', '开启外网映射'],
		unbindExtranet: ['unbind_extranet', '关闭外网映射'],
	};
	this.bindHttp(); //将请求映射到对象
	this.reanderProjectList(); // 渲染列表
}
/**
 * @description 渲染获取项目列表
 */
CreateWebsiteModel.prototype.reanderProjectList = function () {
	var _that = this;
	$('#bt_' + this.type + '_table').empty();
	site.model_table = bt_tools.table({
		el: '#bt_' + this.type + '_table',
		url: '/project/' + _that.type + '/get_project_list',
		minWidth: '1000px',
		autoHeight: true,
		default: '项目列表为空', //数据为空时的默认提示\
		load: '正在获取' + _that.tips + '项目列表，请稍候...',
		pageName: 'nodejs',
		beforeRequest: function (params) {
			if (params.hasOwnProperty('data') && typeof params.data === 'string') {
				var oldParams = JSON.parse(params['data']);
				delete params['data'];
				return { data: JSON.stringify($.extend(oldParams, params)) };
			}
			return { data: JSON.stringify(params) };
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
					_that.reanderProjectInfoView(row);
				},
			},
			{
				fid: 'run',
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
					var status = row.run;
					bt.confirm(
						{
							title: status ? '停止项目' : '启动项目',
							msg: status
								? '停止项目后，当前项目服务将停止运行，继续吗？'
								: '启用' + _that.tips + '项目[' + row.name + '],继续操作?',
						},
						function (index) {
							layer.close(index);
							_that[status ? 'stopProject' : 'startProject'](
								{ project_name: row.name },
								function (res) {
									bt.msg({
										status: res.status,
										msg: res.data || res.error_msg,
									});
									that.$refresh_table_list(true);
								}
							);
						}
					);
				},
			},
			{
				fid: 'run_port',
				title: '运行端口',
				template: function (row) {
					return '<span>' + (row.listen.join('、') || '--') + '<span>';
				},
			},
			{
				fid: 'path',
				title: '根目录',
				tips: '打开目录',
				type: 'link',
				event: function (row, index, ev) {
					openPath(row.path);
				},
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
				fid: 'ssl',
				title: 'SSL证书',
				tips: '部署证书',
				width: 100,
				type: 'text',
				template: function (row, index) {
					var _ssl = row.ssl,
						_info = '',
						_arry = [
							['issuer', '证书品牌'],
							['notAfter', '到期日期'],
							['notBefore', '申请日期'],
							['dns', '可用域名'],
						];
					try {
						if (typeof row.ssl.endtime != 'undefined') {
							if (row.ssl.endtime < 1) {
								return '<a class="btlink bt_danger" href="javascript:;">已过期</a>';
							}
						}
					} catch (error) {}
					for (var i = 0; i < _arry.length; i++) {
						var item = _ssl[_arry[i][0]];
						_info +=
							_arry[i][1] + ':' + item + (_arry.length - 1 != i ? '\n' : '');
					}
					return row.ssl === -1
						? '<a class="btlink bt_warning" href="javascript:;">未部署</a>'
						: '<a class="btlink ' +
								(row.ssl.endtime < 7 ? 'bt_danger' : '') +
								'" href="javascript:;" title="' +
								_info +
								'">剩余' +
								row.ssl.endtime +
								'天</a>';
				},
				event: function (row) {
					_that.reanderProjectInfoView(row);
					setTimeout(function () {
						$('.site-menu p:eq(5)').click();
					}, 500);
				},
			},
			{
				title: '操作',
				type: 'group',
				width: 100,
				align: 'right',
				group: [
					{
						title: '设置',
						event: function (row, index, ev, key, that) {
							_that.reanderProjectInfoView(row);
						},
					},
					{
						title: '删除',
						event: function (row, index, ev, key, that) {
							bt.prompt_confirm(
								'删除项目',
								'您正在删除' + _that.tips + '项目-[' + row.name + ']，继续吗？',
								function () {
									_that.removeProject(
										{ project_name: row.name },
										function (res) {
											bt.msg({
												status: res.status,
												msg: res.data || res.error_msg,
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
							_that.reanderAddProject(function () {
								site.model_table.$refresh_table_list(true);
							});
						},
					},
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
						url: '/project/' + _that.type + '/remove_project',
						param: function (row) {
							return {
								data: JSON.stringify({ project_name: row.name }),
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
												'">' +
												(item.requests.status
													? item.requests.data
													: item.requests.error_msg) +
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
					},
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
				label: '项目执行文件',
				formLabelWidth: '110px',
				must: '*',
				group: {
					type: 'text',
					width: '400px',
					value: '',
					name: 'project_exe',
					placeholder: '请选择项目可执行文件',
					icon: {
						type: 'glyphicon-folder-open',
						select: 'file',
						event: function (ev) {},
						callback: function (path) {
							var pathList = path.split('/');
							var filename = pathList[pathList.length - 2];
							var project_command_config = this.config.form[3],
								project_name_config = this.config.form[1],
								project_ps_config = this.config.form[6];
							project_name_config.group.value = filename;
							project_command_config.group.value = path;
							if (data.type != 'edit') {
								project_ps_config.group.value = filename;
								this.$replace_render_content(6);
							}
							this.$replace_render_content(3);
							this.$replace_render_content(1);
						},
					},
					verify: function (val) {
						if (val === '') {
							bt.msg({ msg: '请选择项目可执行文件', status: false });
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
					name: 'project_name',
					width: '400px',
					placeholder: '请输' + that.tips + '项目名称',
					disabled: data.type != 'edit' ? false : true,
					input: function (formData, formElement, formConfig) {
						var project_ps_config = formConfig.config.form[6];
						project_ps_config.group.value = formData.project_name;
						formConfig.$replace_render_content(6);
					},
					verify: function (val) {
						if (val === '') {
							bt.msg({ msg: '请输入项目名称', status: false });
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
				label: '执行命令',
				formLabelWidth: '110px',
				must: '*',
				group: {
					type: 'text',
					name: 'project_cmd',
					width: '400px',
					placeholder: '请输入项目执行的命令',
					value: '',
					verify: function (val) {
						if (val === '') {
							bt.msg({ msg: '请输入执行命令', status: false });
							return false;
						}
					},
				},
			},
			{
				label: '运行用户',
				formLabelWidth: '110px',
				group: {
					type: 'select',
					name: 'run_user',
					width: '150px',
					unit: '* 无特殊需求请选择www用户',
					list: [
						{ title: 'www', value: 'www' },
						{ title: 'root', value: 'root' },
					],
					tips: '',
				},
			},
			{
				label: '开机启动',
				formLabelWidth: '110px',
				group: {
					type: 'checkbox',
					name: 'is_power_on',
					title: '是否开启启动项目'+(this.tips === 'Go' ? '（默认自带守护进程每120秒检测一次）':''),
				},
			},
			{
				label: '备注',
				formLabelWidth: '110px',
				group: {
					type: 'text',
					name: 'project_ps',
					width: '400px',
					placeholder: '请输入项目备注',
					value: '',
				},
			},
			{
				label: '绑定域名',
				formLabelWidth: '110px',
				group: {
					type: 'textarea', //当前表单的类型 支持所有常规表单元素、和复合型的组合表单元素
					name: 'domains', //当前表单的name
					style: { width: '400px', height: '120px', 'line-height': '22px' },
					tips: {
						//使用hover的方式显示提示
						text: '<span>如果需要绑定外网，请输入需要绑定的域名，该选项可为空</span><br>如需填写多个域名，请换行填写，每行一个域名，默认为80端口<br>泛解析添加方法 *.domain.com<br>如另加端口格式为 www.domain.com:88',
						style: { top: '10px', left: '15px' },
					},
				},
			},
			{
				formLabelWidth: '25px',
				group: {
					type: 'help',
					list: [
						'执行命令：请输入项目需要携带的参数，默认请输入执行文件名',
						'项目教程：<a href="https://www.bt.cn/bbs/thread-93034-1-1.html" target="_blank" class="btlink">https://www.bt.cn/bbs/thread-93034-1-1.html</a>',
					],
				},
			},
		];

	if (data.type == 'edit') {
		config.splice(7, 2);
		config.push({
			formLabelWidth: '110px',
			group: {
				type: 'button',
				name: 'submitForm',
				title: '保存配置',
				event: function (fromData) {
					// 编辑项目
					fromData.is_power_on = fromData.is_power_on ? 1 : 0;
					if (parseInt(fromData.port) < 0 || parseInt(fromData.port) > 65535) return layer.msg('项目端口号应为[0-65535]',{icon:2})
					that.modifyProject(fromData, function (res) {
						bt.msg({ status: res.status, msg: res.data });
						that.simulatedClick(0);
					});
					console.log(arguments, 'event');
				},
			},
		});
	}
	return config;
};

/**
 * @description 渲染添加项目表单
 */
CreateWebsiteModel.prototype.reanderAddProject = function (callback) {
	var that = this;
	var modelForm = bt_tools.open({
		title: '添加' + this.tips + '项目',
		area: '620px',
		btn: ['提交', '取消'],
		content: {
			class: 'pd30',
			formLabelWidth: '120px',
			form: (function () {
				return that.getAddProjectConfig();
			})(),
		},
		yes: function (formData, indexs, layero) {
			console.log(formData, arguments);
			if (formData.domains !== '') {
				var arry = formData.domains.replace('\n', '').split('\r'),
					newArry = [];
				for (var i = 0; i < arry.length; i++) {
					var item = arry[i];
					if (bt.check_domain_port(item)) {
						newArry.push(item.indexOf(':') > -1 ? item : item + ':80');
					} else {
						bt.msg({ status: false, msg: '【' + item + '】 绑定域名格式错误' });
						return false;
					}
				}
				formData.bind_extranet = 1;
				formData.domains = newArry;
			} else {
				formData.bind_extranet = 0;
				delete formData.domains;
			}
			formData.is_power_on = formData.is_power_on ? 1 : 0;
			if (parseInt(formData.port) < 0 || parseInt(formData.port) > 65535) return layer.msg('项目端口号应为[0-65535]',{icon:2})
			that.createProject(formData, function (res) {
				if (res.status) {
					layer.close(indexs);
					if (callback) callback(res);
				}
				bt.msg({ msg: res.data, status: res.status });
			});
		},
	});
	return modelForm;
};

/**
 * @description 模拟点击
 */
CreateWebsiteModel.prototype.simulatedClick = function (num) {
	$('.bt-w-menu p:eq(' + num + ')').click();
};

/**
 * @description
 * @param {string} name 站点名称
 */
CreateWebsiteModel.prototype.reanderProjectInfoView = function (row) {
	var that = this;
	bt.open({
		type: 1,
		title:
			this.tips + '项目管理-[' + row.name + ']，添加时间[' + row.addtime + ']',
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

			function reander_tab_list(config) {
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
								that.getProjectInfo({ project_name: row.name }, function (res) {
									config.list[i].event.call(that, $content, res, ev);
								});
							}
						});
						if (item.active) tab.click();
					})(i, item);
				}
			}
			reander_tab_list(
				{
					el: $layers.find('.bt-w-menu'),
					list: [
						{
							title: '项目配置',
							active: true,
							event: that.reanderProjectConfigView,
						},
						{
							title: '域名管理',
							event: that.reanderDomainManageView,
						},
						{
							title: '外网映射',
							event: that.reanderProjectMapView,
						},
						{
							title: '伪静态',
							event: that.reanderProjectRewriteView,
						},
						{
							title: '配置文件',
							event: that.reanderFileConfigView,
						},
						{
							title: 'SSL',
							event: that.reanderProjectSslView,
						},
						{
							title: '负载状态',
							event: that.reanderServiceCondition,
						},
						{
							title: '服务状态',
							event: that.reanderServiceStatusView,
						},
						{
							title: '项目日志',
							event: that.reanderProjectLogsView,
						},
						{
							title: '网站日志',
							event: that.reanderSiteLogsView,
						},
					],
				},
				function (config, i, ev) {}
			);
		},
	});
};

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
						{ load: element[1] }
					);
				};
			})(element);
		}
	}
};

/**
 * @description 项目配置
 * @param {object} row 项目信息
 */
CreateWebsiteModel.prototype.reanderProjectConfigView = function (el, row) {
	var that = this,
		projectConfig = row.project_config,
		param = $.extend(projectConfig, { project_ps: row.ps, listen:row.listen });
	bt_tools.form({
		el: '#webedit-con',
		data: param,
		class: 'ptb15',
		form: that.getAddProjectConfig({ type: 'edit' }),
	});
	setTimeout(function () {
		$('[name="project_cmd"]').val(param.project_cmd);
	},50)
	if (row.listen.length && !(row.listen.indexOf(parseInt($('input[name=port]').val())) > -1)) {
		$('.error_port').remove()
		$('input[name=port]').next().after('<div class="error_port" style="margin-top: 10px;color: red;">项目端口可能有误，检测到当前项目监听了以下端口'+ row.listen +'</div>')
	}
};

/**
 * @description 域名管理
 * @param {object} row 项目信息
 */
CreateWebsiteModel.prototype.reanderDomainManageView = function (el, row) {
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
								{ project_name: row.name, domains: domins },
								function (res) {
									bt.msg({
										status: res.status,
										msg: res.data || res.msg || res.error_msg,
									});
									if (res.status) {
										$('[name=modeldomain]').val('');
										$('.placeholder').css('display', 'block');
										project_domian.$refresh_table_list(true);
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
		url: '/project/' + that.type + '/project_get_domain',
		default: '暂无域名列表',
		param: { project_name: row.name },
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
								{ project_name: row.name, domain: rowc.name + ':' + rowc.port },
								function (res) {
									bt.msg({
										status: res.status,
										msg: res.data || res.error_msg,
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
						url: '/project/' + that.type + '/project_remove_domain',
						param: function (crow) {
							return {
								data: JSON.stringify({
									project_name: row.name,
									domain: crow.name + ':' + crow.port,
								}),
							};
						},
						callback: function (that) {
							// 手动执行,data参数包含所有选中的站点
							bt.show_confirm(
								'批量删除域名',
								"<span style='color:red'>同时删除选中的域名，是否继续？</span>",
								function () {
									var param = {};
									that.start_batch(param, function (list) {
										var html = '';
										for (var i = 0; i < list.length; i++) {
											var item = list[i];
											html +=
												'<tr><td>' +
												item.name +
												'</td><td><div style="float:right;"><span style="color:' +
												(item.request.status ? '#20a53a' : 'red') +
												'">' +
												(item.request.status ? '成功' : '失败') +
												'</span></div></td></tr>';
										}
										project_domian.$batch_success_table({
											title: '批量删除',
											th: '删除域名',
											html: html,
										});
										project_domian.$refresh_table_list(true);
									});
								}
							);
						},
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
CreateWebsiteModel.prototype.reanderProjectMapView = function (el, row) {
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
			param = { project_name: row.name };
		if (!_check) param['domains'] = row['project_config']['domains'];
		layer.confirm(
			'是否确认' + (!_check ? '开启' : '关闭') + '外网映射！,是否继续',
			{
				title: '外网映射',
				icon: 0,
				closeBtn: 2,
				cancel: function () {
					$('#model_project_map').attr('checked', _check);
				},
			},
			function () {
				that[_check ? 'unbindExtranet' : 'bindExtranet'](param, function (res) {
					if (!res.status) $('#model_project_map').attr('checked', _check);
					bt.msg({
						status: res.status,
						msg: typeof res.data != 'string' ? res.error_msg : res.data,
					});
					row['project_config']['bind_extranet'] = _check ? 0 : 1;
				});
			},
			function () {
				$('#model_project_map').attr('checked', _check);
			}
		);
	});
};

/**
 * @description 渲染项目伪静态视图
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.reanderProjectRewriteView = function (el, row) {
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
	site.edit.get_rewrite_list({ name: this.type + '_' + row.name }, function () {
		$('.webedit-box .line:first').remove();
		$('[name=btn_save_to]').remove();
		$('.webedit-box .help-info-text li:first').remove();
	});
};

/**
 * @description 渲染项目配置文件
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.reanderFileConfigView = function (el, row) {
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
 * @description 渲染项目使用情况
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.reanderServiceCondition = function (el, row) {
	if (!row.run) {
		el.html('').next().removeClass('hide');
		if (el.next().find('.node_mask_module_text').length === 1) {
			el.next()
				.find('.node_mask_module_text')
				.hide()
				.parent()
				.append(
					'<div class="node_mask_module_text">请先启动服务后重新尝试，<a href="javascript:;" class="btlink" onclick="site.node.simulated_click(7)">设置服务状态</a></div'
				);
		} else {
			el.next().find('.node_mask_module_text:eq(1)').show().prev().hide();
		}
		return false;
	}
	el.html(
		'<div class="line" style="padding-top: 0;"><span class="tname" style="width: 30px;text-align:left;padding-right: 5px;">PID</span><div class="info-r"><select class="bt-input-text mr5" name="node_project_pid"></select></div></div><div class="node_project_pid_datail"></div>'
	);
	var _option = '',
		tabelCon = '';
	for (var load in row.load_info) {
		if (row.load_info.hasOwnProperty(load)) {
			_option += '<option value="' + load + '">' + load + '</option>';
		}
	}
	var node_pid = $('[name=node_project_pid]');
	node_pid.html(_option);
	node_pid
		.change(function () {
			var _pid = $(this).val(),
				rdata = row['load_info'][_pid],
				fileBody = '',
				connectionsBody = '';
			for (var i = 0; i < rdata.open_files.length; i++) {
				var itemi = rdata.open_files[i];
				fileBody +=
					'<tr>' +
					'<td>' +
					itemi['path'] +
					'</td>' +
					'<td>' +
					itemi['mode'] +
					'</td>' +
					'<td>' +
					itemi['position'] +
					'</td>' +
					'<td>' +
					itemi['flags'] +
					'</td>' +
					'<td>' +
					itemi['fd'] +
					'</td>' +
					'</tr>';
			}
			for (var k = 0; k < rdata.connections.length; k++) {
				var itemk = rdata.connections[k];
				connectionsBody +=
					'<tr>' +
					'<td>' +
					itemk['client_addr'] +
					'</td>' +
					'<td>' +
					itemk['client_rport'] +
					'</td>' +
					'<td>' +
					itemk['family'] +
					'</td>' +
					'<td>' +
					itemk['fd'] +
					'</td>' +
					'<td>' +
					itemk['local_addr'] +
					'</td>' +
					'<td>' +
					itemk['local_port'] +
					'</td>' +
					'<td>' +
					itemk['status'] +
					'</td>' +
					'</tr>';
			}

			//     tabelCon = reand_table_config([
			//         [{"名称":rdata.name},{"PID":rdata.pid},{"状态":rdata.status},{"父进程":rdata.ppid}],
			//         [{"用户":rdata.user},{"Socket":rdata.connects},{"CPU":rdata.cpu_percent},{"线程":rdata.threads}],
			//         [{"内存":rdata.user},{"io读":rdata.connects},{"io写":rdata.cpu_percent},{"启动时间":rdata.threads}],
			//         [{"启动命令":rdata.user}],
			//     ])
			//
			// console.log(tabelCon)
			//
			//
			//     function reand_table_config(conifg){
			//         var html = '';
			//         for (var i = 0; i < conifg.length; i++) {
			//             var item = conifg[i];
			//             html += '<tr>';
			//             for (var j = 0; j < item; j++) {
			//                 var items = config[j],name = Object.keys(items)[0];
			//                 console.log(items,name)
			//                 html += '<td>'+  name +'</td><td>'+ items[name] +'</td>'
			//             }
			//             console.log(html)
			//             html += '</tr>'
			//         }
			//         return '<div class="divtable"><table class="table"><tbody>'+ html  +'</tbody></tbody></table></div>';
			//     }

			tabelCon =
				'<div class="divtable">' +
				'<table class="table">' +
				'<tbody>' +
				'<tr>' +
				'<th width="50">名称</th><td  width="100">' +
				rdata.name +
				'</td>' +
				'<th width="50">状态</th><td  width="90">' +
				rdata.status +
				'</td>' +
				'<th width="60">用户</th><td width="100">' +
				rdata.user +
				'</td>' +
				'<th width="80">启动时间</th><td width="150">' +
				getLocalTime(rdata.create_time) +
				'</td>' +
				'</tr>' +
				'<tr>' +
				'<th>PID</th><td  >' +
				rdata.pid +
				'</td>' +
				'<th>PPID</th><td >' +
				rdata.ppid +
				'</td>' +
				'<th>线程</th><td>' +
				rdata.threads +
				'</td>' +
				'<th>Socket</th><td>' +
				rdata.connects +
				'</td>' +
				'</tr>' +
				'<tr>' +
				'<th>CPU</th><td>' +
				rdata.cpu_percent +
				'%</td>' +
				'<th>内存</th><td>' +
				ToSize(rdata.memory_used) +
				'</td>' +
				'<th>io读</th><td>' +
				ToSize(rdata.io_read_bytes) +
				'</td>' +
				'<th>io写</th><td>' +
				ToSize(rdata.io_write_bytes) +
				'</td>' +
				'</tr>' +
				'<tr>' +
				'</tr>' +
				'<tr>' +
				'<th width="50">命令</th><td colspan="7" style="word-break: break-word;width: 570px">' +
				rdata.exe +
				'</td>' +
				'</tr>' +
				'</tbody>' +
				'</table>' +
				'</div>' +
				'<h3 class="tname">网络</h3>' +
				'<div class="divtable" >' +
				'<div style="height:160px;overflow:auto;border:#ddd 1px solid" id="nodeNetworkList">' +
				'<table class="table table-hover" style="border:none">' +
				'<thead>' +
				'<tr>' +
				'<th>客户端地址</th>' +
				'<th>客户端端口</th>' +
				'<th>协议</th>' +
				'<th>FD</th>' +
				'<th>本地地址</th>' +
				'<th>本地端口</th>' +
				'<th>状态</th>' +
				'</tr>' +
				'</thead>' +
				'<tbody>' +
				connectionsBody +
				'</tbody>' +
				'</table>' +
				'</div>' +
				'</div>' +
				'<h3 class="tname">打开的文件列表</h3>' +
				'<div class="divtable" >' +
				'<div style="height:160px;overflow:auto;border:#ddd 1px solid" id="nodeFileList">' +
				'<table class="table table-hover" style="border:none">' +
				'<thead>' +
				'<tr>' +
				'<th>文件</th>' +
				'<th>mode</th>' +
				'<th>position</th>' +
				'<th>flags</th>' +
				'<th>fd</th>' +
				'</tr>' +
				'</thead>' +
				'<tbody>' +
				fileBody +
				'</tbody>' +
				'</table>' +
				'</div>' +
				'</div>';
			$('.node_project_pid_datail').html(tabelCon);
			bt_tools.$fixed_table_thead('#nodeNetworkList');
			bt_tools.$fixed_table_thead('#nodeFileList');
		})
		.change()
		.html(_option);
};

/**
 * @description 项目SSL
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.reanderProjectSslView = function (el, row) {
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
	site.set_ssl({ name: row.name, ele: el, id: row.id });
	site.ssl.reload();
};

/**
 * @description 渲染项目服务状态
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.reanderServiceStatusView = function (el, row) {
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
					bt.confirm(
						{
							title: item.title + '项目-[' + row.name + ']',
							msg:
								'您确定要' +
								item.title +
								'项目吗，' +
								(row.run ? '当前项目可能会受到影响，' : '') +
								'是否继续?',
						},
						function (index) {
							layer.close(index);
							item.event.call(that, { project_name: row.name }, function (res) {
								row.run = indexs === 0 ? true : indexs === 1 ? false : row.run;
								html.find('.status').html(reander_service(row.run));
								$('.sfm-opt button').eq(0).addClass('hide');
								$('.sfm-opt button').eq(1).addClass('hide');
								$('.sfm-opt button')
									.eq(row.run ? 1 : 0)
									.removeClass('hide');
								bt.msg({ status: res.status, msg: res.data || res.error_msg });
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
CreateWebsiteModel.prototype.reanderProjectLogsView = function (el, row) {
	el.html('<div class="model_project_log"></div>');
	this.getProjectLog({ project_name: row.name }, function (res) {
		$('#webedit-con .model_project_log').html(
			'<pre class="command_output_pre" style="height:640px;">' +
				(typeof res == 'object' ? res.msg : res) +
				'</pre>'
		);
		$('.command_output_pre').scrollTop(
			$('.command_output_pre').prop('scrollHeight')
		);
	});
};

/**
 * @description 渲染项目日志
 * @param el {object} 当前element节点
 * @param row {object} 当前项目数据
 */
CreateWebsiteModel.prototype.reanderSiteLogsView = function (el, row) {
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
	site.edit.get_site_logs({ name: row.name });
};
