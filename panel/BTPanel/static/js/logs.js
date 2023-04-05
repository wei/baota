var logs = {
	event: function() {
	  var that = this, name = bt.get_cookie('logs_type');
	  that.get_logs_info();
	  // 切换主菜单
	  $('#cutTab').unbind().on('click', '.tabs-item', function () {
		var index = $(this).index(), name = $(this).data('name')
		var parent = $(this).parent().parent().nextAll('.tab-view-box').children('.tab-con').eq(index)
		$(this).addClass('active').siblings().removeClass('active');
		parent.addClass('show w-full').removeClass('hide').siblings().removeClass('show w-full').addClass('hide');
		that[name].event();
		bt.set_cookie('logs_type',name)
	  })
	  $('[data-name="'+ (name || 'panelLogs') +'"]').trigger('click')
	},
	get_logs_info: function () {
		bt_tools.send({url: '/logs/panel/get_logs_info'}, function (rdata) {
			
		})
	},
    // 面板日志
	panelLogs:{
		crontabId: '',
		crontabName: '',
        /**
		 * @description 事件绑定
		 */
		event:function (){
			var that = this;
			$('.state-content').hide()
			$('#panelLogs').unbind('click').on('click','.tab-nav-border span',function(){
			  var index = $(this).index();
			  $(this).addClass('on').siblings().removeClass('on');
			  $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on');
			  that.cutLogsTab(index)
			})
			$(window).unbind('resize').resize(function (){
				that.heightResize()
			})
			$('#panelLogs .tab-nav-border span').eq(0).trigger('click');
			$('.refresh_log').unbind('click').on('click',function (){
				that.getLogs(1)
			})
			$('.close_log').unbind('click').on('click',function (){
				that.delLogs()
			})
			$('#panelCrontab .Tab').on('click','.Item',function(){
				var id = $(this).data('id')
				$(this).addClass('active').siblings().removeClass('active')
				that.crontabId = id
				that.crontabName = $(this).prop('title')
				that.get_crontab_logs(id)
			})
			//计划任务日志刷新
			$('.refreshCrontabLogs').unbind('click').click(function (){
				if(!that.crontabId) return layer.msg('暂无计划任务，不支持刷新日志',{icon:2})
				that.get_crontab_logs(that.crontabId)
			})
			//计划任务搜索
			$('#panelLogs .search-input').keyup(function (e) {
				var value = $(this).val()
				if(e.keyCode == 13) that.crontabLogs(value)
			})
			$('#panelLogs').on('click','.glyphicon-search',function(){
				var value = $('#panelLogs .search-input').val()
				that.crontabLogs(value)
			})
		},
		heightResize: function(){
			$('#errorLog .crontab-log').height((window.innerHeight - 310) +'px')
			$('#panelCrontab .crontab-log').height((window.innerHeight - 310) +'px')
			$('#panelCrontab .Tab').css('max-height',(window.innerHeight - 290) +'px')
			$('#panelCrontab').height((window.innerHeight - 240) +'px')
		},
		/**
		 * @description 切换日志菜单
		 * @param {number} index 索引
		 */
		cutLogsTab:function(index){
			switch (index) {
				case 0:
					this.getLogs(1)
					break;
				case 1:
					this.errorLog()
					break;
				case 2:
					this.heightResize()
					this.crontabLogs('',function() {
						$('#panelCrontab .Tab .Item').eq(0).trigger('click');
					})
					break;
			}
		},
		/**
		* @description 获取计划任务执行日志
		* @param {object} id 参数
		*/
		get_crontab_logs: function (id){
			var that = this
			that.getCrontabLogs({id: id}, function (rdata) {
				$('#panelCrontab .crontab-log').html('<code>'+ bt.htmlEncode.htmlEncodeByRegExp(rdata.msg) + '</code>')
				var div = $('#panelCrontab .crontab-log')
				div.height((window.innerHeight - 310) +'px')
				div.scrollTop(div.prop('scrollHeight'))
			})
		},
		/**
		 * @description 计划任务日志
		*/
		crontabLogs:function (search,callback){
			var _that = this
			$('#panelCrontab .Tab').empty()
			bt_tools.send({url: '/data?action=getData&table=crontab',data: {search: search ? search : '',p: 1,limit: 9999}}, function (rdata) {
				$.each(rdata.data, function (index, item) {
					$('#panelCrontab .Tab').append($('<div class="Item '+ (_that.crontabId && _that.crontabId === item.id ? 'active' : '' ) +'" title="'+ bt.htmlEncode.htmlEncodeByRegExp(item.name) + '" data-id="'+ item.id +'">'+ item.name +'</div>'))
				})
				if(callback) callback(rdata)
			})
		},
		/**
		* @description 获取计划任务执行日志
		* @param {object} param 参数对象
		* @param {function} callback 回调函数
		*/
		getCrontabLogs:function (param,callback){
			var loadT = bt.load('正在获取执行日志，请稍后...')
			$.post('/crontab?action=GetLogs', { id: param.id }, function (res) {
				loadT.close()
				if (callback) callback(res)
			})
		},
		/**
		 * @description 错误日志
		 */
		errorLog:function (){
			var that = this;
			bt_tools.send({
				url:'/config?action=get_panel_error_logs'},{},function(res){
				log = res.msg
				if(res.data == '') log = '当前没有日志'
				$('#errorLog').html('<div style="font-size: 0;">\
					<button type="button" title="刷新日志" class="btn btn-success btn-sm mr5 refreshRunLogs" ><span>刷新日志</span></button>\
					<pre class="crontab-log"><code>'+ bt.htmlEncode.htmlEncodeByRegExp(log) +'</code></pre>\
				</div>');
				$('.refreshRunLogs').click(function (){
					that.errorLog()
				})
				var div = $('#errorLog .crontab-log')
				div.height((window.innerHeight - 310) +'px')
				div.scrollTop(div.prop('scrollHeight'))
			},'面板错误日志')
		},
		/**
		* 取回数据
		* @param {Int} page  分页号
		*/
		getLogs:function(page,search) {
			var that = this
			search = search == undefined ? '':search;
			bt_tools.send({url:'/data?action=getData&table=logs&tojs=getLogs&limit=20&p=' + page+"&search="+search}, function(data) {
				$('#operationLog').empty()
				bt_tools.table({
					el:'#operationLog',
					data: data.data,
                    height: $(window).height() - 330+'px',
                    default: '操作列表为空', // 数据为空时的默认提示
					tootls: [
						{ // 按钮组
							type: 'group',
							positon: ['left', 'top'],
							list: [{
								title: '刷新日志',
								active: true,
								event: function (ev,_that) {
									that.getLogs(1)
								}
							}, {
								title: '清空日志',
								event: function (ev,_that) {
									that.delLogs()
								}
							}]
						}
					],
					column:[
						{ fid: 'username', title: "用户",width: 100 },
						{ fid: 'type', title: "操作类型",width: 100 },
						{ fid: 'log', title: "详情"},
						{ fid: 'addtime', title: "操作时间",width: 150}
					],
					success: function () {
						if(!$('#operationLog .search_input').length){
							$('#operationLog .tootls_top').append('<div class="pull-right">\
								<div class="bt_search">\
									<input type="text" class="search_input" style="" placeholder="搜索日志" value="'+ search +'">\
									<span class="glyphicon glyphicon-search" aria-hidden="true"></span>\
								</div>\
							</div>')
							$('#operationLog .search_input').keydown(function (e) {
								var value = $(this).val()
								if(e.keyCode == 13) that.getLogs(1,value)
							})
							$('#operationLog .glyphicon-search').click(function () {
								var value = $('#operationLog .search_input').val()
								that.getLogs(1,value)
							})
						}
					}
				})
				$('.operationLog').html(data.page);
			},'获取面板操作日志')
		},
		//清理面板日志
		delLogs: function(){
			var that = this
			bt.firewall.clear_logs(function(rdata){
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				that.getLogs(1);
			})
		},
    },
    // 网站日志
	siteLogs:{
		siteName: '',
        event: function() {
			var that = this
			this.getSiteList('',function(rdata){
				$('#siteLogs .Tab .Item').eq(0).trigger('click');
			})
			that.heightResize()

			$(window).unbind('resize').resize(function (){
				that.heightResize()
			})

			$('#siteLogs .Tab').unbind().on('click','.Item',function(){
				that.siteName = $(this).data('name')
				$(this).addClass('active').siblings().removeClass('active')
				var index = $('#siteLogs .tab-nav-border span.on').index()
				$('#siteLogs .tab-nav-border span').eq(index).trigger('click');
			})

			$('#siteLogs').unbind().on('click','.tab-nav-border span',function(){
				var index = $(this).index();
				$(this).addClass('on').siblings().removeClass('on');
				$(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on');
				that.cutLogsTab(index)
			})
			$('#siteLogs .TabGroup .search-input').keyup(function (e) {
				var value = $(this).val()
				if(e.keyCode == 13) that.getSiteList(value)
			})
			$('#siteLogs .TabGroup').on('click','.glyphicon-search',function(){
				var value = $('#siteLogs .search-input').val()
				that.getSiteList(value)
			})
        },
		heightResize: function(){
			$('#siteLogs .Tab').css('max-height',(window.innerHeight - 290) +'px')
			$('#siteLogs').height((window.innerHeight - 200) +'px')
			$('#siteOnesite .divtable').css('max-height',($(window).height() - 350) +'px')
			$('#siteRun .crontab-log').height((window.innerHeight - 330) +'px')
			$('#siteError .crontab-log').height((window.innerHeight - 330) +'px')
		},
		/**
		 * @description 获取网站列表
		*/
		getSiteList:function(search,callback){
			var that = this
			$('#siteLogs .Tab').empty()
			bt_tools.send('/data?action=getData&table=sites',{limit: 999999,p:1,search: search ? search : '',type: -1},function(rdata){
				var _html = ''
				$.each(rdata.data,function(index,item){
					_html += '<div class="Item '+ (that.siteName && that.siteName === item.name ? 'active' : '' ) +'" title="'+ item.name+'（'+ item.ps +'）' +'" data-name="'+ item.name +'">'+ item.name+(item.ps ? '（'+ item.ps +'）' : '') +'</div>'
				})
				$('#siteLogs .Tab').html(_html)
				if(callback) callback(rdata)
			})
		},
		/**
		 * @description 切换日志菜单
		 * @param {number} index 索引
		*/
		cutLogsTab:function(index){
			var that = this;
			switch (index) {
				case 0://网站操作日志 
					that.getSiteOnesite();
					break;
				case 1://网站运行日志
					that.getSiteRun()
					break;
				case 2://网站错误日志
					that.getSiteError()
					break;
				case 3://WEB日志分析
					that.getSiteWeb()
					break;
			}
		},
		/**
		 * @description 获取网站操作日志
		*/
		getSiteOnesite: function(p) {
			var that = this;
			$('#siteOnesite').empty()
			bt_tools.table({
				el: '#siteOnesite',
				url: '/logs/panel/get_logs_bytype',
				param: { 
					data: JSON.stringify({
						stype: '网站管理',
						search: that.siteName,
						limit: 20,
						p: p || 1
				})
				},
				height: $(window).height() - 350,
				dataFilter: function(res) {
					$('#siteOnesite .tootls_bottom').remove()
					$('#siteOnesite').append('<div class="tootls_group tootls_bottom"><div class="pull-right"></div></div>')
					$('#siteOnesite .tootls_bottom .pull-right').append($(res.page).addClass('page'))
					$('#siteOnesite .tootls_bottom .pull-right .page').on('click','a',function(e){
						var num = $(this).prop('href').split('p=')[1]
						that.getSiteOnesite(num)
						e.preventDefault();
					})
					return {data: res.data}
				},
				tootls: [
					{ // 按钮组
					  type: 'group',
					  positon: ['left', 'top'],
					  list: [{
						title: '刷新日志',
						active: true,
						event: function (ev,_that) {
							_that.$refresh_table_list(true)
						}
					  }]
					}
				],
				column: [
					{fid: 'username', title: '用户', type: 'text', width: 150},
					{fid: 'type', title: '操作类型', type: 'text', width: 150},
					{fid: 'log', title: '日志', type: 'text', width: 300},
					{fid: 'addtime', title: '操作时间', type: 'text', width: 150},
				]
			})
		},
		/**
		 * @description 网站运行日志
		*/
		getSiteRun: function(search,p) {
			var that = this;
			var loadT = bt.load('正在获取日志,请稍候...')
			$.post({url: '/site?action=GetSiteLogs'}, { siteName: that.siteName}, function (rdata) {
				loadT.close();
				$('#siteRun').html('<div style="margin-bottom: 5px; position: relative; height:30px;line-height:30px;display: flex;justify-content: space-between;"><button type="button" title="刷新日志" class="btn btn-success btn-sm mr15 refreshSiteSunLogs" >\
					<span>刷新日志</span></button>\
				</div>\
				<div style="font-size: 0;">\
					<pre class="crontab-log"><code>'+ bt.htmlEncode.htmlEncodeByRegExp(rdata.msg === "" ? '当前没有日志.' : rdata.msg) +'</code></pre>\
				</div>');

				$('.refreshSiteSunLogs').click(function (){
					that.getSiteRun()
				})
				var div = $('#siteRun .crontab-log')
				div.height((window.innerHeight - 330) +'px')
				div.scrollTop(div.prop('scrollHeight'))
			})
		},
		/**
		 * @description 网站错误日志
		*/
		getSiteError: function() {
			var that = this;
			bt.site.get_site_error_logs(that.siteName, function (rdata) {
				$('#siteError').html('<div style="font-size: 0;">\
					<button type="button" title="刷新日志" class="btn btn-success btn-sm mr5 refreshSiteErrorLogs" ><span>刷新日志</span></button>\
					<pre class="crontab-log"><code>'+ bt.htmlEncode.htmlEncodeByRegExp(rdata.msg) +'</code></pre>\
				</div>');

				$('.refreshSiteErrorLogs').click(function (){
					that.getSiteError()
				})

				var div = $('#siteError .crontab-log')
				div.height((window.innerHeight - 330) +'px')
				div.scrollTop(div.prop('scrollHeight'))
			})
		},
		/**
		 * @description WEB日志分析
		*/
		getSiteWeb: function() {
			var that = this,robj = $('#siteWeb');
			var progress = '';  //扫描进度
			robj.empty()
			var loadT = bt.load('正在获取日志分析数据，请稍候...');
			$.post('/ajax?action=get_result&path=/www/wwwlogs/' + that.siteName+'.log', function (rdata) {
				loadT.close();
				//1.扫描按钮
				var analyes_log_btn = '<button type="button" title="日志扫描" class="btn btn-success analyes_log btn-sm mr5"><span>日志扫描</span></button>'

				//2.功能介绍
				var analyse_help = '<ul class="help-info-text c7">\
					<li>日志安全分析：扫描网站(.log)日志中含有攻击类型的请求(类型包含：<em style="color:red">xss,sql,san,php</em>)</li>\
					<li>分析的日志数据包含已拦截的请求</li>\
					<li>默认展示上一次扫描数据(如果没有请点击日志扫描）</li>\
					<li>如日志文件过大，扫描可能等待时间较长，请耐心等待</li>\
					</ul>'

				robj.append(analyes_log_btn+'<div class="analyse_log_table"></div>'+analyse_help)
				render_analyse_list(rdata);

				//事件
				$(robj).find('.analyes_log').click(function(){
					bt.confirm({
						title:'扫描网站日志',
						msg:'建议在服务器负载较低时进行安全分析，本次将对【'+that.siteName+'.log】文件进行扫描，可能等待时间较长，是否继续？'
					}, function(index){
						layer.close(index)
						progress = layer.open({
							type: 1,
							closeBtn: 2,
							title: false,
							shade: 0,
							area: '400px',
							content: '<div class="pro_style" style="padding: 20px;"><div class="progress-head" style="padding-bottom: 10px;">正在扫描中，扫描进度...</div>\
									<div class="progress">\
										<div class="progress-bar progress-bar-success progress-bar-striped" role="progressbar" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style="width: 0%">0%</div>\
									</div>\
								</div>',
							success:function(){
								// 开启扫描并且持续获取进度
								$.post('/ajax?action=log_analysis&path=/www/wwwlogs/' + that.siteName+'.log', function (rdata) {
									if(rdata.status){
										detect_progress();
									}else{
										layer.close(progress);
										layer.msg(rdata.msg, { icon: 2, time: 0, shade: 0.3, shadeClose: true });
									}
								})
							}
						})
					})
				})
			})
			// 渲染分析日志列表
			function render_analyse_list(rdata){
				var numTotal = rdata.xss+rdata.sql+rdata.san+rdata.php+rdata.ip+rdata.url
				var analyse_list = '<div class="divtable" style="margin-top: 10px;"><table class="table table-hover">\
					<thead><tr><th width="142">扫描时间</th><th>耗时</th><th>XSS</th><th>SQL</th><th>扫描</th><th>PHP攻击</th><th>IP(top100)</th><th>URL(top100)</th><th>合计</th></tr></thead>\
					<tbody class="analyse_body">'
				if(rdata.is_status){   //检测是否有扫描数据
					analyse_list +='<tr>\
							<td>'+rdata.start_time+'</td>\
							<td>'+rdata.time.substring(0,4)+'秒</td>\
							<td class="onChangeLogDatail" '+(rdata.xss>0?'style="color:red"':'')+' name="xss">'+rdata.xss+'</td>\
							<td class="onChangeLogDatail" '+(rdata.sql>0?'style="color:red"':'')+' name="sql">'+rdata.sql+'</td>\
							<td class="onChangeLogDatail" '+(rdata.san>0?'style="color:red"':'')+' name="san">'+rdata.san+'</td>\
							<td class="onChangeLogDatail" '+(rdata.php>0?'style="color:red"':'')+' name="php">'+rdata.php+'</td>\
							<td class="onChangeLogDatail" '+(rdata.ip>0?'style="color:#20a53a"':'')+' name="ip">'+rdata.ip+'</td>\
							<td class="onChangeLogDatail" '+(rdata.url>0?'style="color:#20a53a"':'')+' name="url">'+rdata.url+'</td>\
							<td>'+numTotal+'</td>\
						</tr>'
				}else{
					analyse_list+='<tr><td colspan="9" style="text-align: center;">没有扫描数据</td></tr>'
				}
				analyse_list += '</tbody></table></div>'
				$('.analyse_log_table').html(analyse_list)
				$('.onChangeLogDatail').css('cursor','pointer').attr('title','点击查看详情')
				//查看详情
				$('.onChangeLogDatail').on('click',function(){
					get_analysis_data_datail($(this).attr('name'))
				})
			}
			// 扫描进度
			function detect_progress(){
				$.post('/ajax?action=speed_log&path=/www/wwwlogs/' + that.siteName+'.log', function (res) {
					var pro = res.msg
					if(pro !== 100){
						if (pro > 100) pro = 100;
						if (pro !== NaN) {
							$('.pro_style .progress-bar').css('width', pro + '%').html(pro + '%');
						}
						setTimeout(function () {
							detect_progress();
						}, 1000);
					}else{
						layer.msg('扫描完成',{icon:1,timeout:4000})
						layer.close(progress);
						get_analysis_data();
					}
				})
			}
			// 获取扫描结果
			function get_analysis_data(){
				var loadTGA = bt.load('正在获取日志分析数据，请稍候...');
				$.post('/ajax?action=get_result&path=/www/wwwlogs/' + that.siteName+'.log', function (rdata) {
					loadTGA.close();
					render_analyse_list(rdata,true)
				})
			}
			// 获取扫描结果详情日志
			function get_analysis_data_datail(name){
				layer.open({
					type: 1,
					closeBtn: 2,
					shadeClose: false,
					title: '【'+name+'】日志详情',
					area: '650px',
					content:'<pre id="analysis_pre" style="background-color: #333;color: #fff;height: 545px;margin: 0;white-space: pre-wrap;border-radius: 0;"></pre>',
					success: function () {
						var loadTGD = bt.load('正在获取日志详情数据，请稍候...');
						$.post('/ajax?action=get_detailed&path=/www/wwwlogs/' + that.siteName+'.log&type='+name+'', function (logs) {
							loadTGD.close();
							$('#analysis_pre').text((name == 'ip' || name == 'url'?'&nbsp;&nbsp;[次数]&nbsp;&nbsp;['+name+']</br>':'')+logs)
						})
					}
				})
			}
		},
		check_log_time: function () {
            bt.confirm({
                msg: "是否立即校对IIS日志时间，校对后日志统一使用北京时间记录？",
                title: '提示'
            }, function () {
                var loading = bt.load()
                bt.send("check_log_time", 'site/check_log_time', {}, function (rdata) {
                    loading.close();
                    if (rdata.status) {
                        site.reload();
                    }
                    bt.msg(rdata);
                })
            })
        },
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
			var ltd = parseInt(bt.get_cookie('ltd_end'))
			if(ltd < 0) {
				$('#logAudit .installSoft').show().prevAll().hide()
			}
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
      logAuditLogs.html('<pre style="height: 600px; background-color: #333; color: #fff; overflow-x: hidden; word-wrap:break-word; white-space:pre-wrap;"><code>' + str + '</code></pre>');
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
	// SSH登录日志
	loginLogs:{
    event: function() {
			var that = this;
			var ltd = parseInt(bt.get_cookie('ltd_end'))
			if(ltd < 0) {
        return $('#loginLogsContent').hide().next().show();
      }
			var type = $('.cutLoginLogsType button.btn-success').data('type')
			this.loginLogsTable({p:1, type: type? type : 0});
			 // 切换登录日志类型
			$('#loginLogsContent').unbind('click').on('click','.cutLoginLogsType button',function(){
				var type = $(this).data('type');
				$(this).addClass('btn-success').removeClass('btn-default').siblings().addClass('btn-default').removeClass('btn-success');
				// $('#loginLogsContent>div:eq('+ type +')').show().siblings().hide();
				that.loginLogsTable({p:1,type: Number(type)});
			})
        },
		/**
     * @description 登录日志
     */
    loginLogsTable:function(param){
      if(!param) param = { p:1, type:0 };
      var logsArr = [['All','日志','get_ssh_list'],['Success','成功日志','get_ssh_success'],['Error','失败日志','get_ssh_error']];
      var type = logsArr[param.type][0] , tips = logsArr[param.type][1];
      var that = this;
			var search = $('#loginAllLogs .search_input').val() || '';
      $('#loginAllLogs').empty();
      var arry = ['全部','登录成功','登录失败'];
      var html = $('<div class="btn-group mr10 cutLoginLogsType" style="top: -2px;"></div>');
      $.each(arry,function (i,v){
        html.append('<button type="button" class="btn btn-sm btn-'+ (i === param.type ?'success':'default') +'" data-type="'+ i +'">'+ v +'</button>')
      })
      return bt_tools.table({
        el: '#loginAllLogs',
        url: '/safe/syslog/' + logsArr[param.type][2],
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
          { //分页显示
            type: 'page',
            number: 20,
						page: param.p,
          }
        ],
        dataFilter: function (data) {
          if(typeof data.status === "boolean" && !data.status){
            $('#loginLogsContent').hide().next().show();
            return { data: [] }
          }
					$('#loginAllLogs .tootls_top .pull-right').prepend(html)
					$('#loginAllLogs .tootls_top .pull-right .bt_search').remove()
               search = search.replace(/(^\s*)|(\s*$)/g, "");//xss
					$('#loginAllLogs .tootls_top .pull-right').append('<div class="bt_search">\
						<input type="text" class="search_input" style="" placeholder="请输入登录IP/用户名">\
						<span class="glyphicon glyphicon-search" aria-hidden="true"></span>\
					</div>')
               $('#loginAllLogs .search_input').val(search)
					$('#loginAllLogs .tootls_top .pull-right .search_input').keyup(function(e){
						if(e.keyCode === 13){
							that.loginLogsTable({p:1,type:param.type})
						}
					})
					$('#loginAllLogs .tootls_top .pull-right .glyphicon-search').click(function(){
						that.loginLogsTable({p:1,type:param.type})
					})
          $('#loginAllLogs .tootls_bottom .pull-right').html('<div class="page">'+logs.renderLogsPages(20,param.p,data.length)+'</div>')
					$('#loginAllLogs .tootls_bottom .pull-right .page a').click(function(){
						var p = $(this).data('p');
						that.loginLogsTable({p:p,type:param.type})
					})
          return {data:data}
        },
        beforeRequest: function (data) {
          if(typeof data.data === "string"){
            delete data.data
            return {data: JSON.stringify(data)}
          }
					data.search = search;
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
        }
      })
    },
  },
	//软件日志
	softwareLogs: {
		username: '',
		/**
		 * @description 事件绑定
		 */
		 event:function (){
			var that = this;
			$('#softwareLogs').unbind('click').on('click','.tab-nav-border span',function(){
			  var index = $(this).index();
			  $(this).addClass('on').siblings().removeClass('on');
			  $(this).parent().next().find('.tab-block').eq(index).addClass('on').siblings().removeClass('on');
			  that.cutLogsTab(index)
			})
			$('#softwareLogs .tab-nav-border span').eq(0).trigger('click');

			$('#softwareLogs .TabGroup .search-input').keyup(function (e) {
				var value = $(this).val()
				if(e.keyCode == 13) that.getFtpList(value)
			})
			$('#softwareLogs .TabGroup').on('click','.glyphicon-search',function(){
				var value = $('#softwareLogs .search-input').val()
				that.getFtpList(value)
			})
			$('#softwareLogs .Content .search-input').keyup(function (e) {
				var value = $(this).val()
				if(e.keyCode == 13) that.getFtpLogs(value)
			})
			$('#softwareLogs .Content').on('click','.glyphicon-search',function(){
				var value = $('#softwareLogs .Content .search-input').val()
				that.getFtpLogs(value)
			})
			$('#softwareLogs .Tab').unbind().on('click','.Item',function(){
				that.username = $(this).data('username')
				$(this).addClass('active').siblings().removeClass('active')
				that.getFtpLogs()
			})
			$('.refreshFtpLogs').click(function (){
				that.getFtpLogs()
			})
			$('#softwareMysqlSlow .search-input').keyup(function (e) {
				var value = $(this).val()
				if(e.keyCode == 13) that.getMysqlSlowLogs(value)
			})
			$('#softwareMysqlSlow').on('click','.glyphicon-search',function(){
				var value = $('#softwareMysqlSlow .search-input').val()
				that.getMysqlSlowLogs(value)
			})
			$('.refreshMysqlSlow').click(function (){
				that.getMysqlSlowLogs()
			})
			$('.refreshMysqlError').click(function (){
				that.getMysqlErrorLogs()
			})
			$(window).unbind('resize').resize(function (){
				that.heightResize()
			})
			that.heightResize()
			// 切换日志类型
			$('#ftpLogsTable').unbind('click').on('click','.cutFtpLogsType button',function(){
				var type = $(this).data('type');
				$(this).addClass('btn-success').removeClass('btn-default').siblings().addClass('btn-default').removeClass('btn-success');
				that.getFtpLogs({p:1,type: Number(type)});
			})
		},
		heightResize: function(){
			$('#softwareFtp .Tab').css('max-height',(window.innerHeight - 300) +'px')
			$('#softwareLogs').height((window.innerHeight - 200) +'px')
			$('#softwareLogs .crontab-log').height((window.innerHeight - 330) +'px')
		},
		/**
		 * @description 切换日志菜单
		 * @param {number} index 索引
		 */
		cutLogsTab:function(index){
			var that = this;
			switch (index) {
				case 0://FTP日志
					var ltd = parseInt(bt.get_cookie('ltd_end'))
					if(ltd < 0){
						return $('#softwareFtp .daily-thumbnail').show().prev().hide()
					}
					that.getFtpList('',function(rdata){
						$('#softwareLogs .Tab .Item').eq(0).trigger('click');
					})
					break;
				case 1://MySql慢日志
					that.getMysqlSlowLogs()
					break;
				case 2://MySql错误日志
					that.getMysqlErrorLogs()
					break;
			}
		},
		/**
		 * @description MySql慢日志
		*/
		getMysqlSlowLogs:function(search,limit){
			limit = limit || 5000;
			var loadT = bt.load('正在获取MySql慢日志，请稍后...')
			$.post('/logs/panel/get_slow_logs',{data:JSON.stringify({search:search,limit: limit})},function (rdata) {
				loadT.close()
				$('#softwareMysqlSlow .crontab-log').html('<code>'+ bt.htmlEncode.htmlEncodeByRegExp(rdata['msg'] ? rdata.msg : (rdata.length ? rdata.join('\n') : '当前没有日志.') + '</code>'))
				var div = $('#softwareMysqlSlow .crontab-log')
				div.height((window.innerHeight - 330) +'px')
				div.scrollTop(div.prop('scrollHeight'))
			})
		},
		/**
		 * @description MySql错误日志
		*/
		getMysqlErrorLogs:function(){
			var loadT = bt.load('正在获取MySql慢日志,请稍候...')
			$.post('/database?action=GetErrorLog', function (rdata) {
				loadT.close()
				$('#softwareMysqlError .crontab-log').html('<code>'+ bt.htmlEncode.htmlEncodeByRegExp(rdata ? rdata : '当前没有日志.') +'</code>')
				var div = $('#softwareMysqlError .crontab-log') 
				div.height((window.innerHeight - 330) +'px')
				div.scrollTop(div.prop('scrollHeight'))
			}) 
		},
		/**
		 * @description 获取FTP日志
		 * @param {string} param 搜索内容
		 */
		getFtpLogs:function(param){
			var that = this;
			console.log(param)
			if(!param) param = { p:1, type:0 };
      var logsArr = [['登录日志','get_login_logs'],['操作日志','get_action_logs']];
      $('#ftpLogsTable').empty();
      var arry = ['登录日志','操作日志'];
			var span = $('<span style="border-left: 1px solid #ccc;margin: 0 15px;"></span><span class="mr5">日志类型：</span>');
      var html = $('<div class="btn-group mr10 cutFtpLogsType" style="top: -2px;"></div>');
      $.each(arry,function (i,v){
        html.append('<button type="button" class="btn btn-sm btn-'+ (i === param.type ?'success':'default') +'" data-type="'+ i +'">'+ v +'</button>')
      })
			if(param.type == 0){
				return bt_tools.table({
					el: '#ftpLogsTable',
					url: '/ftp?action='+ logsArr[param.type][1],
					default: '暂无日志信息',
					height: 390,
					param: {
						user_name: that.username
					},
					column: [
						{ title: '用户名', type: 'text', width: 100,template:function() {
							return '<span>' + that.username + '</span>';
						}},
						{ fid: 'ip', title: '登录IP', type: 'text', width: 110},
						{ fid: 'status', title: '状态', type: 'text', width: 75,
						template: function (rowc, index, ev) {
								var status = rowc.status.indexOf('登录成功') > -1 
							return '<span class="' + (status ?  'btlink' : 'bterror' ) + '">' + (status ?  '登录成功' : '登录失败' ) + '<span>';
						}},
						{ fid: 'in_time', title: '登录时间', type: 'text', width: 150 },
						{ fid: 'out_time', title: '登出时间', type: 'text', width: 200},
					],
					tootls: [
						{
							type:'group',
							positon:['left','top'],
							list:[
								{title:'刷新日志',active:true,event:function(ev,ethat){
										$('#bt_ftp_Login_logs .search_input').val('')
										ethat.config.search.value = ''
									ethat.$refresh_table_list(true)
								}},
							]
						},
						{
							type: 'search',
							positon: ['right', 'top'],
							placeholder: '请输入登录IP/状态/时间',
							searchParam: 'search', //搜索请求字段，默认为 search
							value: '',// 当前内容,默认为空
						},
						{
							type: 'page',
							positon: ['right', 'bottom'], // 默认在右下角
							pageParam: 'p', //分页请求字段,默认为 : p
							page: 1, //当前分页 默认：1
						}
					],
					success:function(){
						$('#ftpLogsTable .tootls_top .pull-left').append(span).append(html)
					}
				})
			}else{
				var typeList = [
					{ title: '全部', value: 'all' },
					{ title: '上传', value: 'upload' },
					{ title: '下载', value: 'download' },
					{ title: '删除', value: 'delete' },
					{ title: '重命名', value: 'rename' }]
				table_logsOperation('all')
				function table_logsOperation(type) {
					$('#ftpLogsTable').empty()
					bt_tools.table({
						el: '#ftpLogsTable',
						default: '暂无日志信息',
						height: 350,
						url: '/ftp?action='+ logsArr[param.type][1],
						param: {
							user_name: that.username,
							type: type
						},
						column: [
							{ title: '用户名', type: 'text', width: 100,template:function() {
								return '<span>' + that.username + '</span>';
							}},
							{ fid: 'ip', title: '操作IP', type: 'text', width: 110},
							{ fid: 'file', title: '文件', type: 'text', width: 240,fixed: true },
							{ fid: 'type', title: '操作类型', type: 'text', width: 75},
							{ fid: 'time', title: '操作时间', type: 'text', width: 100 },
						],
						tootls: [{
								type:'group',
								positon:['left','top'],
								list:[
									{title:'刷新日志',active:true,event:function(){
										table_logsOperation(type)
									}},
								]
							},
							{
								type: 'search',
								positon: ['right', 'top'],
								placeholder: '请输入操作IP/文件/类型/时间',
								searchParam: 'search', //搜索请求字段，默认为 search
								value: '',// 当前内容,默认为空
							},
							{
								type: 'page',
								positon: ['right', 'bottom'], // 默认在右下角
								pageParam: 'p', //分页请求字段,默认为 : p
								page: 1, //当前分页 默认：1
							}
						],
						success: function () {
							if(!$('#ftpLogsTable .log_type').length){
								var _html = ''
								$.each(typeList, function (index, item) {
									_html += '<option value="' + item.value + '">' + item.title + '</option>'
								})
								$('#ftpLogsTable .bt_search').before('<select class="bt-input-text mr5 log_type" style="width:110px" name="log_type">'+ _html +'</select>')
								$('#ftpLogsTable .tootls_top .pull-left').append(span).append(html)
								$('#ftpLogsTable .log_type').val(type)
								$('#ftpLogsTable .log_type').change(function () {
									table_logsOperation($(this).val())
								})
							}
						}
					})
				}
			}
		},
		/**
		 * @description 获取网站列表
		*/
		getFtpList:function(search,callback){
			var that = this
			$('#softwareFtp .Tab').empty()
			bt_tools.send('/data?action=getData&table=ftps',{limit: 999999,p:1,search: search ? search : ''},function(rdata){
				var _html = ''
				$.each(rdata.data,function(index,item){
					_html += '<div class="Item '+ (that.username && that.username === item.name ? 'active' : '' ) +'" title="'+ item.name+'（'+ item.ps +'）' +'" data-username="'+ item.name +'">'+ item.name+'（'+ item.ps +'）' +'</div>'
				})
				$('#softwareFtp .Tab').html(_html)
				if(callback) callback(rdata)
			})
		},
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
logs.event();

//面板操作日志分页切换
function getLogs(page) {
	logs.panelLogs.getLogs(page,$('#operationLog .search_input').val())
}