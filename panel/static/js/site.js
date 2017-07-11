/**
 * 取回网站数据列表
 * @param {Number} page   当前页
 * @param {String} search 搜索条件
 */
function getWeb(page, search) {
	//search = search == undefined ? '':search;
	search = $("#SearchValue").prop("value");
	page = page == undefined ? '1':page;
	var sUrl = '/data?action=getData'
	var pdata = 'tojs=getWeb&table=sites&limit=15&p=' + page + '&search=' + search;
	var loadT = layer.load();
	//取回数据
	$.post(sUrl,pdata, function(data) {
		layer.close(loadT);
		//构造数据列表
		var Body = '';
		for (var i = 0; i < data.data.length; i++) {
			//当前站点状态
			if (data.data[i].status == '正在运行' || data.data[i].status == '1') {
				var status = "<a href='javascript:;' title='停用这个站点' onclick=\"webStop(" + data.data[i].id + ",'" + data.data[i].name + "')\" class='btn-defsult'><span style='color:rgb(92, 184, 92)'>运行中    </span><span style='color:rgb(92, 184, 92)' class='glyphicon glyphicon-play'></span></a>";
			} else {
				var status = "<a href='javascript:;' title='启用这个站点' onclick=\"webStart(" + data.data[i].id + ",'" + data.data[i].name + "')\" class='btn-defsult'><span style='color:red'>已停止    </span><span style='color:rgb(255, 0, 0);' class='glyphicon glyphicon-pause'></span></a>";
			}

			//是否有备份
			if (data.data[i].backup_count > 0) {
				var backup = "<a href='javascript:;' class='btlink' onclick=\"getBackup(" + data.data[i].id + ",'" + data.data[i].name + "')\">有备份</a>";
			} else {
				var backup = "<a href='javascript:;' class='btlink' onclick=\"getBackup(" + data.data[i].id + ",'" + data.data[i].name + "')\">无备份</a>";
			}
			//是否设置有效期
			var web_end_time = (data.data[i].due_date == "0000-00-00") ? '永久' : data.data[i].due_date;
			//表格主体
			Body += "<tr><td style='display:none'><input type='checkbox' name='id' value='" + data.data[i].id + "'></td>\
					<td><a class='btlink webtips' href='javascript:;' onclick=\"webEdit(" + data.data[i].id + ",'" + data.data[i].name + "','" + data.data[i].due_date + "','" + data.data[i].addtime + "')\">" + data.data[i].name + "</td>\
					<td>" + status + "</td>\
					<td>" + backup + "</td>\
					<td><a class='btlink' title='打开目录' href=\"javascript:openPath('"+data.data[i].path+"');\">" + data.data[i].path + "</a></td>\
					<td><a class='btlinkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
					<td style='text-align:right; color:#bbb'>\
					<a href='javascript:;' class='btlink' onclick=\"webEdit(" + data.data[i].id + ",'" + data.data[i].name + "','" + data.data[i].due_date + "','" + data.data[i].addtime + "')\">设置 </a>\
                        | <a href='javascript:;' class='btlink' onclick=\"webDelete('" + data.data[i].id + "','" + data.data[i].name + "')\" title='删除站点'>删除</a>\
					</td></tr>"
		}
		
		if(Body.length < 10){
			Body = "<tr><td colspan='6'>当前没有站点数据</td></tr>";
			$(".dataTables_paginate").hide()
		}
		//输出数据列表
		$("#webBody").html(Body);
		$(".btn-more").hover(function(){
			$(this).addClass("open");
		},function(){
			$(this).removeClass("open");
		});
		//输出分页
		$("#webPage").html(data.page);
		
		$(".btlinkbed").click(function(){
			var dataid = $(this).attr("data-id");
			var databak = $(this).text();
			if(databak=="空"){
				databak='';
			}
			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' name='bak' value='" + databak + "' placeholder='备注信息' onblur='GetBakPost(\"sites\")' />");
			$(".baktext").focus();
		});
	});
}

//添加站点
function webAdd(type) {
	if (type == 1) {
		var array;
		var str="";
		var domainlist='';
		var domain = array = $("#mainDomain").val().split("\n");
		var Webport=[];
		var checkDomain = domain[0].split('.');
		if(checkDomain.length < 1){
			layer.msg('域名格式不正确，请重新输入!',{icon:2});
			return;
		}
		for(var i=1; i<domain.length; i++){
			domainlist += '"'+domain[i]+'",';
		}
		Webport = domain[0].split(":")[1];//主域名端口
		if(Webport==undefined){
			Webport="80";
		}
		domainlist = domainlist.substring(0,domainlist.length-1);//子域名json
		domain ='{"domain":"'+domain[0]+'","domainlist":['+domainlist+'],"count":'+domain.length+'}';//拼接joson
		var loadT = layer.msg('正在处理...',{icon:16,time:0})
		var data = $("#addweb").serialize()+"&port="+Webport+"&webname="+domain;
		$.post('/site?action=AddSite', data, function(ret) {
			if(ret.status === false){
				layer.msg(ret.msg,{icon:ret.status?1:2})
				return
			}
			
			var ftpData = '';
			if (ret.ftpStatus) {
				ftpData = "<p class='p1'>FTP账号资料</p>\
					 		<p><span>用户：</span><strong>" + ret.ftpUser + "</strong></p>\
					 		<p><span>密码：</span><strong>" + ret.ftpPass + "</strong></p>\
					 		<p style='margin-bottom: 19px; margin-top: 11px; color: #666'>只要将网站上传至以上FTP即可访问!</p>"
			}
			var sqlData = '';
			if (ret.databaseStatus) {
				sqlData = "<p class='p1'>数据库账号资料</p>\
					 		<p><span>数据库名：</span><strong>" + ret.databaseUser + "</strong></p>\
					 		<p><span>用户：</span><strong>" + ret.databaseUser + "</strong></p>\
					 		<p><span>密码：</span><strong>" + ret.databasePass + "</strong></p>"
			}
			if (ret.siteStatus == true) {
				getWeb(1);
				layer.closeAll();
				if(ftpData == '' && sqlData == ''){
					layer.msg("成功创建站点",{icon:1})
				}
				else{
					layer.open({
						type: 1,
						area: '600px',
						title: '成功创建站点',
						closeBtn:2,
						shadeClose: false,
						content: "<div class='success-msg'>\
							<div class='pic'><img src='/static/img/success-pic.png'></div>\
							<div class='suc-con'>\
								" + ftpData + sqlData + "\
							</div>\
						 </div>",
					});
					if ($(".success-msg").height() < 150) {
						$(".success-msg").find("img").css({
							"width": "150px",
							"margin-top": "30px"
						});
					}
				}

			} else {
				layer.msg(ret.msg, {
					icon: 2
				});
			}
			layer.close(loadT);
		});
		return;
	}
	
	$.post('/site?action=GetPHPVersion',function(rdata){
		var defaultPath = $("#defaultPath").html();
		var php_version = "<div class='line'><span class='tname'>PHP版本</span><select class='bt-input-text' name='version' id='c_k3' style='width:100px'>";
		for(var i=rdata.length-1;i>=0;i--){
            php_version += "<option value='"+rdata[i].version+"'>"+rdata[i].name+"</option>";
        }
		php_version += "</select></div>";
		layer.open({
			type: 1,
			skin: 'demo-class',
			area: '560px',
			title: '添加网站',
			closeBtn: 2,
			shift: 0,
			shadeClose: false,
			content: "<form class='bt-form pd20 pb70' id='addweb'>\
						<div class='line'>\
		                    <span class='tname'>域名</span>\
		                    <div class='info-r c4'>\
								<textarea id='mainDomain' class='bt-input-text' name='webname' style='width:398px;height:100px;line-height:22px' /></textarea>\
								<a href='#' class='btn btn-default btn-xs btn-zhm'>中文转码</a>\
							</div>\
						</div>\
	                    <div class='line'>\
	                    <span class='tname'>备注</span>\
	                    <div class='info-r c4'>\
	                    	<input id='Wbeizhu' class='bt-input-text' type='text' name='ps' placeholder='网站备注' style='width:398px' />\
	                    </div>\
	                    </div>\
	                    <div class='line'>\
	                    <span class='tname'>根目录</span>\
	                    <div class='info-r c4'>\
	                    	<input id='inputPath' class='bt-input-text mr5' type='text' name='path' value='"+defaultPath+"/' placeholder='网站根目录' style='width:398px' /><span class='glyphicon glyphicon-folder-open cursor' onclick='ChangePath(\"inputPath\")'></span>\
	                    </div>\
	                    </div>\
	                    <div class='line'>\
	                    	<span class='tname'>FTP</span>\
	                    	<div class='info-r'>\
	                    	<select class='bt-input-text' name='ftp' id='c_k1' style='width:100px'>\
		                    	<option value='true'>创建</option>\
		                    	<option value='false' selected>不创建</option>\
		                    </select>\
		                    </div>\
	                    </div>\
	                    <div class='line' id='ftpss'>\
	                    <span class='tname'>FTP设置</span>\
	                    <div class='info-r c4'>\
		                    <div class='userpassword'><span class='mr5'>用户名：<input id='ftp-user' class='bt-input-text' type='text' name='ftp_username' value='' style='width:150px' /></span>\
		                    <span class='last'>密码：<input id='ftp-password' class='bt-input-text' type='text' name='ftp_password' value=''  style='width:150px' /></span></div>\
		                    <p class='c9 mt10'>创建站点的同时，为站点创建一个对应FTP帐户，并且FTP目录指向站点所在目录。</p>\
	                    </div>\
	                    </div>\
	                    <div class='line'>\
	                    <span class='tname'>数据库</span>\
							<div class='info-r c4'>\
								<select class='bt-input-text mr5' name='sql' id='c_k2' style='width:100px'>\
									<option value='true'>MySQL</option>\
									<option value='false' selected>不创建</option>\
								</select>\
								<select class='bt-input-text' name='codeing' id='c_codeing' style='width:100px'>\
									<option value='utf8'>utf-8</option>\
									<option value='utf8mb4'>utf8mb4</option>\
									<option value='gbk'>gbk</option>\
									<option value='big5'>big5</option>\
								</select>\
							</div>\
	                    </div>\
	                    <div class='line' id='datass'>\
	                    <span class='tname'>数据库设置</span>\
	                    <div class='info-r c4'>\
		                    <div class='userpassword'><span class='mr5'>用户名：<input id='data-user' class='bt-input-text' type='text' name='datauser' value=''  style='width:150px' /></span>\
		                    <span class='last'>密码：<input id='data-password' class='bt-input-text' type='text' name='datapassword' value=''  style='width:150px' /></span></div>\
		                    <p class='c9 mt10'>创建站点的同时，为站点创建一个对应的数据库帐户，方便不同站点使用不同数据库。</p>\
	                    </div>\
	                    </div>\
						"+php_version+"\
	                    <div class='bt-form-submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
							<button type='button' class='btn btn-success btn-sm btn-title' onclick=\"webAdd(1)\">提交</button>\
						</div>\
	                  </form>",
		});
		$(function() {
			var placeholder = "<div class='placeholder c9' style='top:10px;left:10px'>每行填写一个域名，默认为80端口<br>泛解析添加方法 *.domain.com<br>如另加端口格式为 www.domain.com:88</div>";
			$('#mainDomain').after(placeholder);
			$(".placeholder").click(function(){
				$(this).hide();
				$('#mainDomain').focus();
			})
			$('#mainDomain').focus(function() {
			    $(".placeholder").hide();
			});
			
			$('#mainDomain').blur(function() {
				if($(this).val().length==0){
					$(".placeholder").show();
				}  
			});
			
			
			//FTP账号数据绑定域名
			$('#mainDomain').on('input', function() {
				var array;
				var res,ress;
				var str = $(this).val();
				var len = str.replace(/[^\x00-\xff]/g, "**").length;
				array = str.split("\n");
				ress =array[0].split(":")[0];
				res = ress.replace(new RegExp(/([-.])/g), '_');
				if(res.length > 15) res = res.substr(0,15);
				if($("#inputPath").val().substr(0,defaultPath.length) == defaultPath) $("#inputPath").val(defaultPath+'/'+ress);
				if(!isNaN(res.substr(0,1))) res = "sql"+res;
				if(res.length > 15) res = res.substr(0,15);
				$("#Wbeizhu").val(ress);
				$("#ftp-user").val(res);
				$("#data-user").val(res);
				if(isChineseChar(str)) $('.btn-zhm').show();
				else $('.btn-zhm').hide();
			})
			$('#Wbeizhu').on('input', function() {
				var str = $(this).val();
				var len = str.replace(/[^\x00-\xff]/g, "**").length;
				if (len > 20) {
					str = str.substring(0, 20);
					$(this).val(str);
					layer.msg('不要超出20个字符', {
						icon: 0
					});
				}
			})
			//获取当前时间时间戳，截取后6位
			var timestamp = new Date().getTime().toString();
			var dtpw = timestamp.substring(7);
			$("#data-user").val("sql" + dtpw);
	
			//生成n位随机密码
			function _getRandomString(len) {
				len = len || 32;
				var $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'; // 默认去掉了容易混淆的字符oOLl,9gq,Vv,Uu,I1  
				var maxPos = $chars.length;
				var pwd = '';
				for (i = 0; i < len; i++) {
					pwd += $chars.charAt(Math.floor(Math.random() * maxPos));
				}
				return pwd;
			}
			$("#ftp-password").val(_getRandomString(10));
			$("#data-password").val(_getRandomString(10));
	
	
			$("#ftpss,#datass").hide();
			//不创建
			$("#c_k1").change(function() {
					var val = $("#c_k1").val();
					if (val == 'false') {
						$("#ftp-user").attr("disabled", true);
						$("#ftp-password").attr("disabled", true);
						$("#ftpss").hide();
					} else {
						$("#ftp-user").attr("disabled", false);
						$("#ftp-password").attr("disabled", false);
						$("#ftpss").show();
					}
				})
				//不创建
			$("#c_k2").change(function() {
				var val = $("#c_k2").val();
				if (val == 'false') {
					$("#data-user").attr("disabled", true);
					$("#data-password").attr("disabled", true);
					$("#datass").hide();
				} else {
					$("#data-user").attr("disabled", false);
					$("#data-password").attr("disabled", false);
					$("#datass").show();
				}
			});
		});
	});
}

//修改网站目录
function webPathEdit(id){
	$.post("/data?action=getKey","table=sites&key=path&id="+id,function(rdata){
		$.post('/site?action=GetDirUserINI','path='+rdata+'&id='+id,function(userini){
			var userinicheckeds = userini.userini?'checked':'';
			var logscheckeds = userini.logs?'checked':'';
			var opt = ''
			var selected = '';
			for(var i=0;i<userini.runPath.dirs.length;i++){
				selected = '';
				if(userini.runPath.dirs[i] == userini.runPath.runPath) selected = 'selected';
				opt += '<option value="'+ userini.runPath.dirs[i] +'" '+selected+'>'+ userini.runPath.dirs[i] +'</option>'
			}
			var webPathHtml = "<div class='webedit-box'>\
						<div class='label-input-group ptb10'>\
							<input type='checkbox' name='userini' id='userini'"+userinicheckeds+" /><label class='mr20' for='userini' style='font-weight:normal'>防跨站攻击</label>\
							<input type='checkbox' name='logs' id='logs'"+logscheckeds+" /><label for='logs' style='font-weight:normal'>写访问日志</label>\
						</div>\
						<div class='line mt10'>\
							<span class='mr5'>网站目录</span>\
							<input class='bt-input-text mr5' type='text' style='width:50%' placeholder='网站根目录' value='"+rdata+"' name='webdir' id='inputPath'>\
							<span onclick='ChangePath(&quot;inputPath&quot;)' class='glyphicon glyphicon-folder-open cursor mr20'></span>\
							<button class='btn btn-success btn-sm' onclick='SetSitePath("+id+")'>保存</button>\
						</div>\
						<div class='line mtb15'>\
							<span class='mr5'>运行目录</span>\
							<select class='bt-input-text' type='text' style='width:50%; margin-right:41px' name='runPath' id='runPath'>"+opt+"</select>\
							<button class='btn btn-success btn-sm' onclick='SetSiteRunPath("+id+")' style='margin-top: -1px;'>保存</button>\
						</div>\
						<ul class='help-info-text c7 ptb10'>\
							<li>部分程序的运行目录不在根目录，需要指定二级目录作为运行目录，如ThinkPHP5，Laravel</li>\
							<li>选择您的运行目录，点保存即可</li>\
						</ul>\
					</div>";
			$("#webedit-con").html(webPathHtml);
			
			$("#userini").change(function(){
				$.post('/site?action=SetDirUserINI','path='+rdata,function(userini){
					layer.msg(userini.msg,{icon:userini.status?1:2});
				});
			});
			
			$("#logs").change(function(){
				$.post('/site?action=logsOpen','id='+id,function(userini){
					layer.msg(userini.msg,{icon:userini.status?1:2});
				});
			});
			
		});
	});
}

//提交运行目录
function SetSiteRunPath(id){
	var NewPath = $("#runPath").val();
	var loadT = layer.msg('正在执行,请稍候...',{icon:16,time:10000,shade: [0.3, '#000']});
	$.post('/site?action=SetSiteRunPath','id='+id+'&runPath='+NewPath,function(rdata){
		layer.close(loadT);
		var ico = rdata.status?1:2;
		layer.msg(rdata.msg,{icon:ico});
	});
}

//提交网站目录
function SetSitePath(id){
	var NewPath = $("#inputPath").val();
	var loadT = layer.msg('正在执行,请稍候...',{icon:16,time:10000,shade: [0.3, '#000']});
	$.post('/site?action=SetPath','id='+id+'&path='+NewPath,function(rdata){
		layer.close(loadT);
		var ico = rdata.status?1:2;
		layer.msg(rdata.msg,{icon:ico});
	});
}

//修改网站备注
function webBakEdit(id){
	$.post("/data?action=getKey','table=sites&key=ps&id="+id,function(rdata){
		var webBakHtml = "<div class='webEdit-box padding-10'>\
					<div class='line'>\
					<label><span>网站备注</span></label>\
					<div class='info-r'>\
					<textarea name='beizhu' id='webbeizhu' col='5' style='width:96%'>"+rdata+"</textarea>\
					<br><br><button class='btn btn-success btn-sm' onclick='SetSitePs("+id+")'>保存</button>\
					</div>\
					</div>";
		$("#webedit-con").html(webBakHtml)
	});
}

//提交网站备注
function SetSitePs(id){
	var myPs = $("#webbeizhu").val();
	$.post('/data?action=setPs','table=sites&id='+id+'&ps='+myPs,function(rdata){
		layer.msg(rdata?"修改成功":"无需修改",{icon:rdata?1:2});
	});
}


//设置默认文档
function SetIndexEdit(id){
	$.post('/site?action=GetIndex','id='+id,function(rdata){
		rdata= rdata.replace(new RegExp(/(,)/g), "\n");
		var setIndexHtml = "<div id='SetIndex'><div class='SetIndex'>\
				<div class='line'>\
						<textarea class='bt-input-text' id='Dindex' name='files' style='height: 180px; width:50%; line-height:20px'>"+rdata+"</textarea>\
						<button type='button' class='btn btn-success btn-sm pull-right' onclick='SetIndexList("+id+")' style='margin: 70px 130px 0px 0px;'>保存</button>\
				</div>\
				<ul class='help-info-text c7 ptb10'>\
					<li>默认文档，每行一个，优先级由上至下。</li>\
				</ul>\
				</div></div>";
		$("#webedit-con").html(setIndexHtml);
	});
	
}


/**
 * 停止一个站点
 * @param {Int} wid  网站ID
 * @param {String} wname 网站名称
 */
function webStop(wid, wname) {
	layer.confirm('站点停用后将无法访问，您真的要停用这个站点吗？', {closeBtn:2},function(index) {
		if (index > 0) {
			var loadT = layer.load()
			$.post("/site?action=SiteStop","id=" + wid + "&name=" + wname, function(ret) {
				layer.msg(ret.msg,{icon:ret.status?1:2})
				layer.close(loadT);
				getWeb(1);
				
			});
		}
	});
}

/**
 * 启动一个网站
 * @param {Number} wid 网站ID
 * @param {String} wname 网站名称
 */
function webStart(wid, wname) {
	layer.confirm('即将启动站点，您真的要启用这个站点吗？',{closeBtn:2}, function(index) {
		if (index > 0) {
			var loadT = layer.load()
			$.post("/site?action=SiteStart","id=" + wid + "&name=" + wname, function(ret) {
				layer.msg(ret.msg,{icon:ret.status?1:2})
				layer.close(loadT);
				getWeb(1);
			});
		}
	});
}

/**
 * 删除一个网站
 * @param {Number} wid 网站ID
 * @param {String} wname 网站名称
 */
function webDelete(wid, wname){
	var thtml = "<div class='options'>\
	    	<label><input type='checkbox' id='delftp' name='ftp'><span>FTP</span></label>\
	    	<label><input type='checkbox' id='deldata' name='data'><span>数据库</span></label>\
	    	<label><input type='checkbox' id='delpath' name='path'><span>根目录</span></label>\
	    	</div>";
	SafeMessage("删除站点["+wname+"]","是否要删除的同名FTP、数据库、根目录",function(){
		var ftp='',data='',path='';
		if($("#delftp").is(":checked")){
			ftp='&ftp=1';
		}
		if($("#deldata").is(":checked")){
			data='&data=1';
		}
		if($("#delpath").is(":checked")){
			path='&path=1';
		}
		var loadT = layer.msg('正在执行,请稍候...',{icon:16,time:10000,shade: [0.3, '#000']});
		$.post("/site?action=DeleteSite","id=" + wid + "&webname=" + wname+ftp+data+path, function(ret){
			layer.closeAll();
			layer.msg(ret.msg,{icon:ret.status?1:2})
			getWeb(1);
		});
	},thtml);
}


/**
 * 域名管理
 * @param {Int} id 网站ID
 */
function DomainEdit(id, name,msg,status) {
	$.get('/data?action=getData&table=domain&list=True&search=' + id, function(domain) {
		var echoHtml = "";
		for (var i = 0; i < domain.length; i++) {
			echoHtml += "<tr><td><a title='点击访问' target='_blank' href='http://" + domain[i].name + ":" + domain[i].port + "' class='btlinkbed'>" + domain[i].name + "</a></td><td><a class='btlinkbed'>" + domain[i].port + "</a></td><td class='text-center'><a class='table-btn-del' href='javascript:;' onclick=\"delDomain(" + id + ",'" + name + "','" + domain[i].name + "','" + domain[i].port + "',1)\"><span class='glyphicon glyphicon-trash'></span></a></td></tr>";
		}
		var bodyHtml = "<textarea id='newdomain' class='bt-input-text' style='height: 100px; width: 340px;padding:5px 10px;line-height:20px'></textarea>\
								<a href='#' class='btn btn-default btn-xs btn-zhm' style='top:15px;right:145px'>中文转码</a>\
								<input type='hidden' id='newport' value='80' />\
								<button type='button' class='btn btn-success btn-sm pull-right' style='margin:30px 35px 0 0' onclick=\"DomainAdd(" + id + ",'" + name + "',1)\">添加</button>\
							<div class='divtable mtb15' style='height:350px;overflow:auto'>\
								<table class='table table-hover' width='100%'>\
								<thead><tr><th>域名</th><th width='70px'>端口</th><th width='50px' class='text-center'>操作</th></tr></thead>\
								<tbody id='checkDomain'>" + echoHtml + "</tbody>\
								</table>\
							</div>";
		$("#webedit-con").html(bodyHtml);
		if(msg != undefined){
			layer.msg(msg,{icon:status?1:5});
		}
		var placeholder = "<div class='placeholder c9' style='left:28px'>每行填写一个域名，默认为80端口<br>泛解析添加方法 *.domain.com<br>如另加端口格式为 www.domain.com:88</div>";
		$('#newdomain').after(placeholder);
		$(".placeholder").click(function(){
			$(this).hide();
			$('#newdomain').focus();
		})
		$('#newdomain').focus(function() {
		    $(".placeholder").hide();
		});
		
		$('#newdomain').blur(function() {
			if($(this).val().length==0){
				$(".placeholder").show();
			}  
		});
		$("#newdomain").on("input",function(){
			var str = $(this).val();
			if(isChineseChar(str)) $('.btn-zhm').show();
			else $('.btn-zhm').hide();
		})
		//checkDomain();
	});
}

function DomainRoot(id, name,msg) {
	$.get('/data?action=getData&table=domain&list=True&search=' + id, function(domain) {
		var echoHtml = "";
		for (var i = 0; i < domain.length; i++) {
			echoHtml += "<tr><td><a title='点击访问' target='_blank' href='http://" + domain[i].name + ":" + domain[i].port + "' class='btlinkbed'>" + domain[i].name + "</a></td><td><a class='btlinkbed'>" + domain[i].port + "</a></td><td class='text-center'><a class='table-btn-del' href='javascript:;' onclick=\"delDomain(" + id + ",'" + name + "','" + domain[i].name + "','" + domain[i].port + "',1)\"><span class='glyphicon glyphicon-trash'></span></a></td></tr>";
		}
		var index = layer.open({
			type: 1,
			skin: 'demo-class',
			area: '450px',
			title: '域名管理',
			closeBtn: 2,
			shift: 0,
			shadeClose: true,
			content: "<div class='divtable padding-10'>\
						<textarea id='newdomain'></textarea>\
						<a href='#' class='btn btn-default btn-xs btn-zhm' style='top:22px;right:154px'>中文转码</a>\
						<input type='hidden' id='newport' value='80' />\
						<button type='button' class='btn btn-success btn-sm pull-right' style='margin:30px 35px 0 0' onclick=\"DomainAdd(" + id + ",'" + name + "')\">添加</button>\
						<table class='table table-hover' width='100%' style='margin-bottom:0'>\
						<thead><tr><th>域名</th><th width='70px'>端口</th><th width='50px' class='text-center'>操作</th></tr></thead>\
						<tbody id='checkDomain'>" + echoHtml + "</tbody>\
						</table></div>"
		});
		if(msg != undefined){
			layer.msg(msg,{icon:1});
		}
		var placeholder = "<div class='placeholder'>每行填写一个域名，默认为80端口<br>泛解析添加方法 *.domain.com<br>如另加端口格式为 www.domain.com:88</div>";
		$('#newdomain').after(placeholder);
		$(".placeholder").click(function(){
			$(this).hide();
			$('#newdomain').focus();
		})
		$('#newdomain').focus(function() {
		    $(".placeholder").hide();
		});
		
		$('#newdomain').blur(function() {
			if($(this).val().length==0){
				$(".placeholder").show();
			}  
		});
		$("#newdomain").on("input",function(){
			var str = $(this).val();
			if(isChineseChar(str)) $('.btn-zhm').show();
			else $('.btn-zhm').hide();
		})
		//checkDomain();
	});
}
//编辑域名/端口
function cancelSend(){
	$(".changeDomain,.changePort").hide().prev().show();
	$(".changeDomain,.changePort").remove();
}
//遍历域名
function checkDomain() {
	$("#checkDomain tr").each(function() {
		var $this = $(this);
		var domain = $(this).find("td:first-child").text();
		$(this).find("td:first-child").append("<i class='lading'></i>");
		checkDomainWebsize($this,domain);
	})
}
//检查域名是否解析备案
function checkDomainWebsize(obj,domain){
	var gurl = "http://api.zun.gd/ipaddess"
	var ip = getCookie('iplist');
	var data = "domain=" + domain+"&ip="+ip;
	$.ajax({ url: gurl,data:data,type:"get",dataType:"jsonp",async:true ,success: function(rdata){
		obj.find("td:first-child").find(".lading").remove();
		if (rdata.code == -1) {
			obj.find("td:first-child").append("<i class='yf' data-title='该域名未解析'>未解析</i>");
		} else {
			obj.find("td:first-child").append("<i class='f' data-title='域名解析IP为：" + rdata.data.ip + "<br>当前服务器IP：" + rdata.data.main_ip + "(仅供参考,使用CDN的用户请无视)'>已解析</i>");
		}

		obj.find("i").mouseover(function() {
			var tipsTitle = $(this).attr("data-title");
			layer.tips(tipsTitle, this, {
				tips: [1, '#3c8dbc'],
				time: 0
			})
		})
		obj.find("i").mouseout(function() {
			$(".layui-layer-tips").remove();
		})
	}})
}

/**
 * 添加域名
 * @param {Int} id  网站ID
 * @param {String} webname 主域名
 */
function DomainAdd(id, webname,type) {
	var Domain = $("#newdomain").val().split("\n");
	
	var domainlist="";
	for(var i=0; i<Domain.length; i++){
		domainlist += Domain[i]+",";
	}
	
	if(domainlist.length < 3){
		layer.msg('域名不能为空!',{icon:5});
		return;
	}
	domainlist = domainlist.substring(0,domainlist.length-1);
	var loadT = layer.load();
	var data = "domain=" + domainlist + "&webname=" + webname + "&id=" + id;
	$.post('/site?action=AddDomain', data, function(retuls) {
		layer.close(loadT);
		DomainEdit(id,webname,retuls.msg,retuls.status);
	});
}

/**
 * 删除域名
 * @param {Number} wid 网站ID
 * @param {String} wname 主域名
 * @param {String} domain 欲删除的域名
 * @param {Number} port 对应的端口
 */
function delDomain(wid, wname, domain, port,type) {
	var num = $("#checkDomain").find("tr").length;
	if(num==1){
		layer.msg('最后一个域名不能删除！');
	}
	layer.confirm('您真的要从站点中删除这个域名吗？',{closeBtn:2}, function(index) {
			var url = "/site?action=DelDomain"
			var data = "id=" + wid + "&webname=" + wname + "&domain=" + domain + "&port=" + port;
			var loadT = layer.msg('正在删除...',{time:0,icon:16});
			$.post(url,data, function(ret) {
				layer.close(loadT);
				layer.msg(ret.msg,{icon:ret.status?1:2})
				if(type == 1){
					layer.close(loadT);
					DomainEdit(wid,wname)
				}else{
					layer.closeAll();
					DomainRoot(wid, wname);
				}
			});
	});
}

/**
 * 判断IP/域名格式
 * @param {String} domain  源文本
 * @return bool
 */
function IsDomain(domain) {
		//domain = 'http://'+domain;
		var re = new RegExp();
		re.compile("^[A-Za-z0-9-_]+\\.[A-Za-z0-9-_%&\?\/.=]+$");
		if (re.test(domain)) {
			return (true);
		} else {
			return (false);
		}
	}



/**
 *设置数据库备份
 * @param {Number} sign	操作标识
 * @param {Number} id	编号
 * @param {String} name	主域名
 */
function WebBackup(id, name) {
		var loadT =layer.msg('正在打包，请稍候...', {icon:16,time:0,shade: [0.3, '#000']});
		var data = "id="+id;
		$.post('/site?action=ToBackup', data, function(rdata) {
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2})
			getBackup(id);
		});
}

/**
 *删除网站备份
 * @param {Number} webid	网站编号
 * @param {Number} id	文件编号
 * @param {String} name	主域名
 */
function WebBackupDelete(id,pid){
	layer.confirm('真的要删除备份包吗?',{title:'删除备份文件',closeBtn:2},function(index){
		var loadT =layer.msg('正在删除，请稍候...', {icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site?action=DelBackup','id='+id, function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			getBackup(pid);
		});
	})
}

function getBackup(id,name,page) {
	if(page == undefined){
		page = '1';
	} 
	$.post('/data?action=getFind','table=sites&id=' + id, function(rdata) {
		$.post('/data?action=getData','table=backup&search=' + id + '&limit=5&p='+page+'&type=0&tojs=getBackup',function(frdata){
			
			var body = '';
				for (var i = 0; i < frdata.data.length; i++) {
					if(frdata.data[i].type == '1') continue;
					if(frdata.data[i].filename.length < 15){
						var ftpdown = "<a class='btlink' href='/cloud?filename="+frdata.data[i].filename+"&name="+ frdata.data[i].name+"' target='_blank'>下载</a> | ";
					}else{
						var ftpdown = "<a class='btlink' href='/download?filename="+frdata.data[i].filename+"&name="+frdata.data[i].name+"' target='_blank'>下载</a> | ";
					}
					body += "<tr><td><span class='glyphicon glyphicon-file'></span>"+frdata.data[i].name+"</td>\
							<td>" + (ToSize(frdata.data[i].size)) + "</td>\
							<td>" + frdata.data[i].addtime + "</td>\
							<td class='text-right' style='color:#ccc'>"+ ftpdown + "<a class='btlink' href='javascript:;' onclick=\"WebBackupDelete('" + frdata.data[i].id + "',"+id+")\">删除</a></td>\
						</tr>"
				}
			var ftpdown = '';
			frdata.page = frdata.page.replace(/'/g,'"').replace(/getBackup\(/g,"getBackup(" + id + ",0,");
			
			if(name == 0){
				var sBody = "<table width='100%' id='WebBackupList' class='table table-hover'>\
							<thead><tr><th>文件名称</th><th>文件大小</th><th>打包时间</th><th width='140px' class='text-right'>操作</th></tr></thead>\
							<tbody id='WebBackupBody' class='list-list'>"+body+"</tbody>\
							</table>"
				$("#WebBackupList").html(sBody);
				$(".page").html(frdata.page);
				return;
			}
			layer.closeAll();
			layer.open({
				type: 1,
				skin: 'demo-class',
				area: '700px',
				title: '打包备份',
				closeBtn: 2,
				shift: 0,
				shadeClose: false,
				content: "<div class='bt-form ptb15 mlr15' id='WebBackup'>\
							<button class='btn btn-default btn-sm' style='margin-right:10px' type='button' onclick=\"WebBackup('" + rdata.id + "','" + rdata.name + "')\">打包备份</button>\
							<div class='divtable mtb15' style='margin-bottom:0'><table width='100%' id='WebBackupList' class='table table-hover'>\
							<thead><tr><th>文件名称</th><th>文件大小</th><th>打包时间</th><th width='140px' class='text-right'>操作</th></tr></thead>\
							<tbody id='WebBackupBody' class='list-list'>"+body+"</tbody>\
							</table><div class='page'>"+frdata.page+"</div></div></div>"
			});
		});
		
	});

}

function goSet(num) {
	//取选中对象
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data = '';
	var a = '';
	var count = 0;
	//构造POST数据
	for (var i = 0; i < len; i++) {
		if (el[i].checked == true && el[i].value != 'on') {
			data += a + count + '=' + el[i].value;
			a = '&';
			count++;
		}
	}
	//判断操作类别
	if(num==1){
		reAdd(data);
	}
	else if(num==2){
		shift(data);
	}
}





//设置默认文档
function SetIndex(id){
	var quanju = (id==undefined)?"全局设置":"本站";
	var data=id==undefined?"":"id="+id;
	$.post('/site?action=GetIndex',data,function(rdata){
		rdata= rdata.replace(new RegExp(/(,)/g), "\n");
		layer.open({
				type: 1,
				area: '500px',
				title: '设置网站默认文档',
				closeBtn: 2,
				shift: 5,
				shadeClose: true,
				content:"<form class='bt-form' id='SetIndex'><div class='SetIndex'>"
				+"<div class='line'>"
				+"	<span class='tname' style='padding-right:2px'>默认文档</span>"
				+"	<div class='info-r'>"
				+"		<textarea id='Dindex' name='files' style='line-height:20px'>"+rdata+"</textarea>"
				+"		<p>"+quanju+"默认文档，每行一个，优先级由上至下。</p>"
				+"	</div>"
				+"</div>"
				+"<div class='bt-form-submit-btn'>"
				+"	<button type='button' id='web_end_time' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>"
			    +"    <button type='button' class='btn btn-success btn-sm btn-title' onclick='SetIndexList("+id+")'>确定</button>"
		        +"</div>"
				+"</div></form>"
		});
	});
}

//设置默认站点
function SetDefaultSite(){
	var name = $("#defaultSite").val();
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site?action=SetDefaultSite','name='+name,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
	});
}


//默认站点
function GetDefaultSite(){
	$.post('/site?action=GetDefaultSite','',function(rdata){
		var opt = '<option value="off">未设置默认站点</option>';
		var selected = '';
		for(var i=0;i<rdata.sites.length;i++){
			selected = '';
			if(rdata.defaultSite == rdata.sites[i].name) selected = 'selected';
			opt += '<option value="' + rdata.sites[i].name + '" ' + selected + '>' + rdata.sites[i].name + '</option>';
		}
		
		layer.open({
				type: 1,
				area: '430px',
				title: '设置默认站点',
				closeBtn: 2,
				shift: 5,
				shadeClose: true,
				content:'<div class="bt-form ptb15 pb70">\
							<p class="line">\
								<span class="tname text-right mr5">默认站点：</span>\
								<select id="defaultSite" class="bt-input-text" style="width: 300px;">'+opt+'</select>\
							</p>\
							<ul class="help-info-text c6 plr20">\
							    <li>设置默认站点后,所有未绑定的域名和IP都被定向到默认站点</li>\
							    <li>可有效防止恶意解析</li>\
						    </ul>\
							<div class="bt-form-submit-btn">\
								<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">取消</button>\
								<button class="btn btn-success btn-sm btn-title" onclick="SetDefaultSite()">保存</button>\
							</div>\
						</div>'
		});
	});
}

function SetIndexList(id){
	var Dindex = $("#Dindex").val().replace(new RegExp(/(\n)/g), ",");
	if(id==undefined){
		var data="id=&Index="+Dindex;
	}
	else{
		var data="id="+id+"&Index="+Dindex;
	}
	var loadT= layer.load(2);
	$.post('/site?action=SetIndex',data,function(rdata){
		layer.close(loadT);
		var ico = rdata.status? 1:5;
		layer.msg(rdata.msg,{icon:ico});
	});
}



/*站点修改*/
function webEdit(id,website,endTime,addtime){
	var system = "{$Think.session.system}";
	var eMenu = '';
	eMenu = "<p onclick='DirBinding("+id+")'>子目录绑定</p>"
	+"<p onclick='webPathEdit("+id+")'>网站目录</p>"
	+"<p onclick='limitNet("+id+")'>流量限制</p>"
	+"<p onclick=\"Rewrite('"+website+"')\">伪静态</p>"
	+"<p onclick='SetIndexEdit("+id+")'>默认文档</p>"
	+"<p onclick=\"ConfigFile('"+website+"')\">配置文件</p>"
	+"<p onclick=\"SetSSL("+id+",'"+website+"')\">SSL</p>"
	+"<p onclick=\"PHPVersion('"+website+"')\">PHP版本</p>"
	+"<p onclick=\"toTomcat('"+website+"')\">Tomcat</p>"
	+"<p onclick=\"To301('"+website+"')\">301重定向</p>"
	+"<p onclick=\"Proxy('"+website+"')\">反向代理</p>"
	+"<p id='site_"+id+"' onclick=\"CheckSafe('"+id+"')\">风险扫描</p>";
	layer.open({
		type: 1,
		area: '600px',
		title: '站点修改['+website+']  --  添加时间['+addtime+']',
		closeBtn: 2,
		shift: 0,
		content: "<div class='bt-form'>"
			+"<div class='bt-w-menu pull-left'>"
			+"	<p class='bgw'  onclick=\"DomainEdit(" + id + ",'" + website + "')\">域名管理</p>"
			+"	"+eMenu+""
			+"</div>"
			+"<div id='webedit-con' class='bt-w-con webedit-con pd15'></div>"
			+"</div>"
	});
	DomainEdit(id,website);
	//域名输入提示
	var placeholder = "<div class='placeholder'>每行填写一个域名<br>默认为80端口<br>如另加端口格式为 www.zun.com:88</div>";
	$('#newdomain').after(placeholder);
	$(".placeholder").click(function(){
		$(this).hide();
		$('#newdomain').focus();
	});
	$('#newdomain').focus(function() {
	    $(".placeholder").hide();
	});
	
	$('#newdomain').blur(function() {
		if($(this).val().length==0){
			$(".placeholder").show();
		}  
	});
	//切换
	var $p = $(".bt-w-menu p");
	$p.click(function(){
		$(this).addClass("bgw").siblings().removeClass("bgw");
	});
}


//木马扫描
function CheckSafe(id,act){
	if(act != undefined){
		var loadT = layer.msg('正在提交任务...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site?action=CheckSafe','id='+id,function(rdata){
			$(".btnStart").hide()
			setTimeout(function(){
				CheckSafe(id);
			},3000);
			GetTaskCount();
			layer.close(loadT)
			layer.msg(rdata.msg,{icon:rdata.status?1:5});
		});
		
		return;
	}
	
	
	
   $.post('/site?action=GetCheckSafe','id='+id,function(rdata){
   		var done = "<button type='button' class='btn btn-success btn-sm btnStart mr5'  onclick=\"CheckSafe("+id+",1)\">开始扫描</button>\
   					<button type='button' class='btn btn-default btn-sm btnStart mr20'  onclick=\"UpdateRulelist()\">更新特征库</button>\
   					<a class='f14 mr20' style='color:green;'>已扫描："+rdata.count+"</a><a class='f14' style='color:red;'>风险数量："+rdata.error+"</a>";
   		
   		if(rdata['scan']) done = "<a class='f14 mr20' style='color:green;'>已扫描："+rdata.count+"</a><a class='f14' style='color:red;'>风险数量："+rdata.error+"</a>";
		var echoHtml = "<div class='mtb15'>"
					   + done
					   +"</div>"
		for(var i=0;i<rdata.phpini.length;i++){
			echoHtml += "<tr><td>危险函数</td><td>危险</td><td>未禁用危险函数："+rdata.phpini[i].function+"<br>文件：<a style='color: red;' href='javascript:;' onclick=\"OnlineEditFile(0,'/www/server/php/"+rdata.phpini[i].version+"/etc/php.ini')\">/www/server/php/"+rdata.phpini[i].version+"/etc/php.ini</a></td></tr>";
		}
		
		if(!rdata.sshd){
			echoHtml += "<tr><td>SSH端口</td><td>高危</td><td>sshd文件被篡改</td></tr>";
		}
		
		if(!rdata.userini){
			echoHtml += "<tr><td>跨站攻击</td><td>危险</td><td>站点未开启防跨站攻击!</td></tr>";
		}
		
		for(var i=0;i<rdata.data.length;i++){
			echoHtml += "<tr><td>"+rdata.data[i].msg+"</td><td>"+rdata.data[i].level+"</td><td>文件：<a style='color: red;' href='javascript:;' onclick=\"OnlineEditFile(0,'"+rdata.data[i].filename+"')\">"+rdata.data[i].filename+"</a><br>修改时间："+rdata.data[i].etime+"<br>代码："+rdata.data[i].code+"</td></tr>";
		}

		var body = "<div>"
					+"<div class='divtable mtb15'><table class='table table-hover' width='100%' style='margin-bottom:0'>"
				  	+"<thead><tr><th width='100px'>行为</th><th width='70px'>风险</th><th>详情</th></tr></thead>"
				   	+"<tbody id='checkDomain'>" + echoHtml + "</tbody>"
				   	+"</table></div>"
		
		$("#webedit-con").html(body);
		$(".btnStart").click(function(){
			fly('btnStart');	
		});
		if(rdata['scan']){
			c = $("#site_"+id).attr('class');
			if(c != 'active') return;
			setTimeout(function(){
				CheckSafe(id);
			},1000);
		}
	});
}

function UpdateRulelist(){
	var loadT = layer.msg('正在更新，请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site?action=UpdateRulelist','',function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
	});
	
}


//流量限制
function limitNet(id){
	$.post('site?action=GetLimitNet&id='+id,function(rdata){
		var status_selected = rdata.perserver != 0?'checked':'';
		if(rdata.perserver == 0){
			rdata.perserver = 200;
			rdata.perip = 20;
			rdata.limit_rate = 512;
		}
		var limitList = "<option value='1'>论坛/博客</option>"
						+"<option value='2'>图片站</option>"
						+"<option value='3'>下载站</option>"
						+"<option value='4'>商城</option>"
						+"<option value='5'>门户</option>"
						+"<option value='6'>企业站</option>"
						+"<option value='7'>视频站</option>"
		var body = "<div class='dirBinding flow c4'>"
				+'<p class="label-input-group ptb10"><label style="font-weight:normal"><input type="checkbox" name="status" '+status_selected+' onclick="SaveLimitNet('+id+')" style="width:15px;height:15px;margin-right:5px" />启用流量控制</label></p>'
				+"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>限制方案：</span><select class='bt-input-text mr20' name='limit' style='width:90px'>"+limitList+"</select></p>"
			    +"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>并发限制：</span><input class='bt-input-text mr20' style='width: 90px;' type='number' name='perserver' value='"+rdata.perserver+"' /><span class='c9'>*限制当前站点最大并发数</span></p>"
			    +"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>单IP限制：</span><input class='bt-input-text mr20' style='width: 90px;' type='number' name='perip' value='"+rdata.perip+"' /><span class='c9'>*限制单个IP访问最大并发数</span></p>"
			    +"<p class='line' style='padding:10px 0'><span class='span_tit mr5'>流量限制：</span><input class='bt-input-text mr20' style='width: 90px;' type='number' name='limit_rate' value='"+rdata.limit_rate+"' /><span class='c9'>*限制每个请求的流量上限（单位：KB）</span></p>"
			    +"<button class='btn btn-success btn-sm mt10' onclick='SaveLimitNet("+id+",1)'>保存</button>"
			    +"</div>"
			$("#webedit-con").html(body);
			
			$("select[name='limit']").change(function(){
				var type = $(this).val();
				var perserver = 200;
				var perip = 20;
				var limit_rate = 512;
				switch(type){
					case '1':
						perserver = 300;
						perip = 25;
						limit_rate = 320;
						break;
					case '2':
						perserver = 200;
						perip = 10;
						limit_rate = 1024;
						break;
					case '3':
						perserver = 50;
						perip = 3;
						limit_rate = 2048;
						break;
					case '4':
						perserver = 500;
						perip = 10;
						limit_rate = 2048;
						break;
					case '5':
						perserver = 400;
						perip = 15;
						limit_rate = 1024;
						break;
					case '6':
						perserver = 50;
						perip = 10;
						limit_rate = 512;
						break;
					case '7':
						perserver = 150;
						perip = 4;
						limit_rate = 1024;
						break;
				}
				
				$("input[name='perserver']").val(perserver);
				$("input[name='perip']").val(perip);
				$("input[name='limit_rate']").val(limit_rate);
			});
	});
}


//保存流量限制配置
function SaveLimitNet(id,type){
	var isChecked = $("input[name='status']").attr('checked');
	if(isChecked == undefined || type == 1){
		var data = 'id='+id+'&perserver='+$("input[name='perserver']").val()+'&perip='+$("input[name='perip']").val()+'&limit_rate='+$("input[name='limit_rate']").val();
		var loadT = layer.msg('正在设置...',{icon:16,time:10000})
		$.post('site?action=SetLimitNet',data,function(rdata){
			layer.close(loadT);
			limitNet(id);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	}else{
		var loadT = layer.msg('正在设置...',{icon:16,time:10000})
		$.post('site?action=CloseLimitNet&id='+id,function(rdata){
			layer.close(loadT);
			limitNet(id);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	}
}


//子目录绑定
function DirBinding(id){
	$.post('/site?action=GetDirBinding&id='+id,function(rdata){
		var echoHtml = '';
		for(var i=0;i<rdata.binding.length;i++){
			echoHtml += "<tr><td>"+rdata.binding[i].domain+"</td><td>"+rdata.binding[i].port+"</td><td>"+rdata.binding[i].path+"</td><td class='text-right'><a class='btlink' href='javascript:SetDirRewrite("+rdata.binding[i].id+");'>伪静态</a> | <a class='btlink' href='javascript:DelBinding("+rdata.binding[i].id+","+id+");'>删除</a></td></tr>";
		}
		
		var dirList = '';
		for(var n=0;n<rdata.dirs.length;n++){
			dirList += "<option value='"+rdata.dirs[n]+"'>"+rdata.dirs[n]+"</option>";
		}
		
		var body = "<div class='dirBinding c5'>"
			   +"域名：<input class='bt-input-text mr20' type='text' name='domain' />"
			   +"子目录：<select class='bt-input-text mr20' name='dirName'>"+dirList+"</select>"
			   +"<button class='btn btn-success btn-sm' onclick='AddDirBinding("+id+")'>添加</button>"
			   +"</div>"
			   +"<div class='divtable mtb15'><table class='table table-hover' width='100%' style='margin-bottom:0'>"
			   +"<thead><tr><th>域名</th><th width='70'>端口</th><th width='100'>子目录</th><th width='100' class='text-right'>操作</th></tr></thead>"
			   +"<tbody id='checkDomain'>" + echoHtml + "</tbody>"
			   +"</table></div>"
		
		$("#webedit-con").html(body);
	})
	
}

//子目录伪静态
function SetDirRewrite(id){
	$.post('/site?action=GetDirRewrite&id='+id,function(rdata){
		if(!rdata.status){
			var confirmObj = layer.confirm('你真的要为这个子目录创建独立的伪静态规则吗？',{closeBtn:2},function(){
				$.post('/site?action=GetDirRewrite&id='+id+'&add=1',function(rdata){
					layer.close(confirmObj);
					ShowRewrite(rdata);
				});
			});
			return;
		}
		ShowRewrite(rdata);
	});
}

//显示伪静态
function ShowRewrite(rdata){
	var rList = ''; 
	for(var i=0;i<rdata.rlist.length;i++){
		rList += "<option value='"+rdata.rlist[i]+"'>"+rdata.rlist[i]+"</option>";
	}
	var webBakHtml = "<div class='c5 plr15'>\
						<div class='line'>\
						<select class='bt-input-text mr20' id='myRewrite' name='rewrite' style='width:30%;'>"+rList+"</select>\
						<span>规则转换工具：<a href='http://www.bt.cn/Tools' target='_blank' style='color:#20a53a'>Apache转Nginx</a>\</span>\
						<textarea class='bt-input-text mtb15' style='height: 260px; width: 470px; line-height:18px;padding:5px;' id='rewriteBody'>"+rdata.data+"</textarea></div>\
						<button id='SetRewriteBtn' class='btn btn-success btn-sm' onclick=\"SetRewrite('"+rdata.filename+"')\">保存</button>\
						<ul class='help-info-text c7 ptb10'>\
							<li>请选择您的应用，若设置伪静态后，网站无法正常访问，请尝试设置回default</li>\
							<li>您可以对伪静态规则进行修改，修改完后保存即可。</li>\
						</ul>\
						</div>";
	layer.open({
		type: 1,
		area: '500px',
		title: '配置伪静态规则',
		closeBtn: 2,
		shift: 5,
		shadeClose: true,
		content:webBakHtml
	});
	
	$("#myRewrite").change(function(){
		var rewriteName = $(this).val();
		$.post('/files?action=GetFileBody','path=/www/server/panel/rewrite/'+getCookie('serverType')+'/'+rewriteName+'.conf',function(fileBody){
			 $("#rewriteBody").val(fileBody.data);
		});
	});
}

//添加子目录绑定
function AddDirBinding(id){
	var domain = $("input[name='domain']").val();
	var dirName = $("select[name='dirName']").val();
	if(domain == '' || dirName == '' || dirName == null){
		layer.msg('域名和子目录名称不能为空!',{icon:2});
		return;
	}
	
	var data = 'id='+id+'&domain='+domain+'&dirName='+dirName
	$.post('site?action=AddDirBinding',data,function(rdata){
		DirBinding(id);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
	
}

//删除子目录绑定
function DelBinding(id,siteId){
	layer.confirm('您真的要删除这个子目录绑定吗？',{closeBtn:2},function(){
		$.post('site?action=DelDirBinding','id='+id,function(rdata){
			DirBinding(siteId);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}


//反向代理
function Proxy(siteName,type){
	if(type == 1){
		type = $("input[name='status']").attr('checked')?'0':'1';
		toUrl = $("input[name='toUrl']").val();
		toDomain = $("input[name='toDomain']").val();
		var sub1 = $("input[name='sub1']").val();
		var sub2 = $("input[name='sub2']").val();
		var data = 'name='+siteName+'&type='+type+'&proxyUrl='+toUrl+'&toDomain=' + toDomain + '&sub1=' + sub1 + '&sub2=' + sub2;
		var loadT = layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site?action=SetProxy',data,function(rdata){
			layer.close(loadT);
			if(rdata.status) {
				Proxy(siteName);
			}else{
				$("input[name='status']").attr('checked',false)
			}
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
		return;
	}
	$.post('/site?action=GetProxy','name='+siteName,function(rdata){
		if(rdata.proxyUrl == null) rdata.proxyUrl = '';
		var status_selected = rdata.status?'checked':'';
		var body = "<div>"
			   +"<p style='margin-bottom:8px'><span>目标URL</span><input class='bt-input-text' type='text' name='toUrl' value='"+rdata.proxyUrl+"' style='margin-left: 5px;width: 380px;height: 30px;margin-right:10px;' placeholder='请填写完整URL,例：http://www.test.com' /></p>"
			   +"<p style='margin-bottom:8px'><span>发送域名</span><input class='bt-input-text' type='text' name='toDomain' value='"+rdata.toDomain+"' style='margin-left: 5px;width: 380px;height: 30px;margin-right:10px;' placeholder='发送到目标服务器的域名,例：www.test.com' /></p>"
			   +"<p style='margin-bottom:8px'><span>内容替换</span><input class='bt-input-text' type='text' name='sub1' value='"+rdata.sub1+"' style='margin-left: 5px;width: 182px;height: 30px;margin-right:10px;' placeholder='被替换的文本,可留空' />"
			   +"<input class='bt-input-text' type='text' name='sub2' value='"+rdata.sub2+"' style='margin-left: 5px;width: 183px;height: 30px;margin-right:10px;' placeholder='替换为,可留空' /></p>"
			   +'<div class="label-input-group ptb10"><label style="font-weight:normal"><input type="checkbox" name="status" '+status_selected+' onclick="Proxy(\''+siteName+'\',1)" />启用反向代理</label></div>'
			   +'<ul class="help-info-text c7 ptb10">'
			   +'<li>目标Url必需是可以访问的，否则将直接502</li>'
			   +'<li>默认本站点所有域名访问将被传递到目标服务器，请确保目标服务器已绑定域名</li>'
			   +'<li>若您是被动代理，请在发送域名处填写上目标站点的域名</li>'
			   +'<li>若您不需要内容替换功能，请直接留空</li>'
			   +'</ul>'
			   +"</div>";
			$("#webedit-con").html(body);
	});
}
		
//301重定向
function To301(siteName,type){
	if(type == 1){
		type = $("input[name='status']").attr('checked')?'0':'1';
		toUrl = $("input[name='toUrl']").val();
		srcDomain = $("select[name='srcDomain']").val();
		var data = 'siteName='+siteName+'&type='+type+'&toDomain='+toUrl+'&srcDomain='+srcDomain;
		$.post('site?action=Set301Status',data,function(rdata){
			To301(siteName);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
		return;
	}
	$.post('/site?action=Get301Status','siteName='+siteName,function(rdata){
		var domain_tmp = rdata.domain.split(',');
		var domains = '';
		var selected = '';
		for(var i=0;i<domain_tmp.length;i++){
			selected = '';
			if(domain_tmp[i] == rdata.src) selected = 'selected';
			domains += "<option value='"+domain_tmp[i]+"' "+selected+">"+domain_tmp[i]+"</option>";
		}
		
		if(rdata.url == null) rdata.url = '';
		var status_selected = rdata.status?'checked':'';
		var body = "<div>"
			   +"<p style='margin-bottom:8px'><span>访问域名</span><select class='bt-input-text' name='srcDomain' style='margin-left: 5px;width: 380px;height: 30px;margin-right:10px;'><option value='all'>整站</option>"+domains+"</select></p>"
			   +"<p style='margin-bottom:8px'><span>目标URL</span><input class='bt-input-text' type='text' name='toUrl' value='"+rdata.url+"' style='margin-left: 5px;width: 380px;height: 30px;margin-right:10px;' placeholder='请填写完整URL,例：http://www.test.com' /></p>"
			   +'<div class="label-input-group ptb10"><label style="font-weight:normal"><input type="checkbox" name="status" '+status_selected+' onclick="To301(\''+siteName+'\',1)" />启用301</label></div>'
			   +'<ul class="help-info-text c7 ptb10">'
			   +'<li>选择[整站]时请不要将目标URL设为同一站点下的域名.</li>'
			   +'<li>取消301重定向后，需清空浏览器缓存才能看到生效结果.</li>'
			   +'</ul>'
			   +"</div>";
			$("#webedit-con").html(body);
	});
}

//验证IP地址
function isValidIP(ip) {
    var reg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/
    return reg.test(ip);
}
function isContains(str, substr) {
    return str.indexOf(substr) >= 0;
}
//宝塔ssl
function SetSSL(id,siteName){
	var mBody = '<div class="tab-nav"><span class="on" onclick="BTssl(\'a\','+id+',\''+siteName+'\')">宝塔SSL</span><span onclick="BTssl(\'lets\','+id+',\''+siteName+'\')">Let\'s Encrypt</span><span onclick="BTssl(\'other\','+id+',\''+siteName+'\')">其他证书</span><span class="sslclose" onclick="closeSSL(\''+siteName+'\')">关闭</span></div>'
			  + '<div class="tab-con"></div>';
	$("#webedit-con").html(mBody);
	//BTssl('a',id,siteName);
	$(".tab-nav span").click(function(){
		$(this).addClass("on").siblings().removeClass("on");
	});
	$.post('site?action=GetSSL','siteName='+siteName,function(rdata){
		switch(rdata.type){
			case -1:
				$(".tab-nav span").eq(3).addClass("on").siblings().removeClass("on");
				var txt = "<div class='mtb15'>本站点未设置SSL，如需设置SSL，请选择切换类目申请开启SSL</div>";
				$(".tab-con").html(txt);
				break;
			case 1:
				$(".tab-nav span").eq(1).addClass("on").siblings().removeClass("on");
				setCookie('letssl',1);
				var lets = '<div class="myKeyCon ptb15"><div class="ssl-con-key pull-left mr20">密钥(KEY)<br><textarea id="key" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.key+'</textarea></div>'
					+ '<div class="ssl-con-key pull-left">证书(CRT/PEM)<br><textarea id="csr" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.csr+'</textarea></div>'
					+ '</div>'
					+ '<ul class="help-info-text c7 pull-left"><li>已为您自动生成Let\'s Encrypt免费证书；</li><li>如需使用其他SSL,请切换其他证书后粘贴您的KEY以及CRT内容，然后保存即可。</li></ul>';
				$(".tab-con").html(lets);
				break;
			case 0:
				$(".tab-nav span").eq(2).addClass("on").siblings().removeClass("on");
				BTssl('other',id,siteName);
				break;
			case 2:
				$(".tab-nav span").eq(0).addClass("on").siblings().removeClass("on");
				BTssl('a',id,siteName);
				break;
		}
	})
}
//关闭SSL
function closeSSL(siteName){
	$.post('site?action=GetSSL','siteName='+siteName,function(rdata){
		switch(rdata.type){
			case -1:
				var txt = "<div class='mtb15'>本站点未设置SSL，如需设置SSL，请选择切换类目申请开启SSL</div>";
				setCookie('letssl',0);
				$(".tab-con").html(txt);
				break;
			case 1:
				var txt = "Let's Encrypt";
				closeSSLHTML(txt,siteName);
				break;
			case 0:
				var txt = "其它";
				closeSSLHTML(txt,siteName);
				break;
			case 2:
				var txt = "宝塔SSL";
				closeSSLHTML(txt,siteName);
				break;
		}
	})
}
//关闭SSL内容
function closeSSLHTML(txt,siteName){
	$(".tab-con").html("<div class='line mtb15'>您已启用"+txt+"证书，如需关闭，请点击\"关闭SSL\"按钮。</div><div class='line mtb15'><button class='btn btn-success btn-sm' onclick=\"OcSSL('CloseSSLConf','"+siteName+"')\">关闭SSL</button></div>");
}

//宝塔SSL
function BTssl(type,id,siteName){
	var a = '<div class="btssl"><div class="alert alert-warning" style="padding:10px">未绑定宝塔账号，请注册绑定，绑定宝塔账号(非论坛账号)可实现一键部署SSL</div>'
			+ '<div class="line mtb10"><span class="tname text-right mr20">宝塔账号</span><input id="btusername" class="bt-input-text" type="text" name="bt_panel_username" maxlength="11" style="width:200px" ><i style="font-style:normal;margin-left:10px;color:#999"></i></div>'
			+ '<div class="line mtb10"><span class="tname text-right mr20">密码</span><input id="btpassword" class="bt-input-text" type="password" name="bt_panel_password" style="width:200px" ></div>'
			+ '<div class="line mtb15" style="margin-left:100px"><button class="btn btn-success btn-sm mr20 btlogin">登录</button><button class="btn btn-success btn-sm" onclick="javascript:window.open(\'http://new.bt.cn/register.html\')">注册宝塔账号</button></div>'
			+ '<ul class="help-info-text c7 ptb15"><li>证书申请需要注册宝塔账号并通过实名认证方可使用</li><li>已有宝塔账号请登录绑定</li><li>宝塔SSL申请的是TrustAsia DV SSL CA - G5 原价：1900元/1年，宝塔用户免费！</li><li>一年满期后免费重新颁发</li></ul>'
			+ '</div>';
	var b = '<div class="btssl"><div class="line mtb15"><span class="tname text-center">域名</span><select id="domainlist" class="bt-input-text" style="width:220px"></select></div>'
		  + '<div class="line mtb15" style="margin-left:80px"><button class="btn btn-success btn-sm btsslApply">申请</button></div>'
		  + '<div class="btssllist mtb15" style="height:171px;overflow:auto"><div class="divtable"><table class="table table-hover"><thead><tr><th>域名</th><th>到期时间</th><th>状态</th><th class="text-right" width="80">操作</th></tr></thead><tbody id="ssllist"></tbody></table></div></div>'
		  + '<ul class="help-info-text c7 ptb15"><li>申请之前，请确保域名已解析，如未解析会导致审核失败</li><li>宝塔SSL申请的是免费版TrustAsia DV SSL CA - G5证书，仅支持单个域名申请</li><li>有效期1年，不支持续签，到期后需要重新申请</li></ul>'
		  + '</div>';
	
	var lets =  '<div class="btssl"><div class="line mtb15"><span class="tname text-center">域名</span><ul id="ymlist" style="padding: 5px 10px;max-height:200px;overflow:auto; width:240px;border:#ccc 1px solid;border-radius:3px"></ul></div>'
			  + '<div class="line mtb15" style="margin-left:80px"><button class="btn btn-success btn-sm letsApply">申请</button></div>'
			  + '<ul class="help-info-text c7 ptb15"><li>申请之前，请确保域名已解析，如未解析会导致审核失败。</li><li>本证书国内服务器或国内dns存在一定失败率，如多次还失败请使用其他证书</li><li>Let\'s Encrypt免费证书，有效期3个月，支持多域名。默认会自动续签</li></ul>'
			  + '</div>';
	
	var other = '<div class="myKeyCon ptb15"><div class="ssl-con-key pull-left mr20">密钥(KEY)<br><textarea id="key" class="bt-input-text"></textarea></div>'
					+ '<div class="ssl-con-key pull-left">证书(CRT/PEM)<br><textarea id="csr" class="bt-input-text"></textarea></div>'
					+ '<div class="ssl-btn pull-left mtb15" style="width:100%"><button class="btn btn-success btn-sm" onclick="SaveSSL(\''+siteName+'\')">保存</button></div></div>'
					+ '<ul class="help-info-text c7 pull-left"><li>粘贴您的KEY以及CRT内容，然后保存即可<a href="http://www.bt.cn/bbs/thread-704-1-1.html" target="_blank" style="color:green;">[帮助]</a>。</li></ul>';
					
	switch(type){
		case 'a':
			$.get("/ssl?action=GetUserInfo",function(rdata){
				if(rdata.status){
					BTssl('b',id,siteName);
				}
				else{
					$(".tab-con").html(a);
					$("#btusername").blur(function(){
						if(!(/^1(3|4|5|7|8)\d{9}$/.test($(this).val()))){ 
							$("#btusername").css("border","1px solid #e53451");
							$("#btusername").next("i").html("请输入手机号码");
						}
						else{
							$("#btusername").removeAttr("style").css("width","200px");
							$("#btusername").next("i").empty();
						}
					});
					$(".btlogin").click(function(){
						var data = "username="+$("#btusername").val()+"&password="+$("#btpassword").val();
						$.post("/ssl?action=GetToken",data,function(tdata){
							if(tdata.status){
								layer.msg(tdata.msg,{icon:1});
								BTssl('b',id,siteName);
							}
							else{
								layer.msg(tdata.msg,{icon:2})
							}
						})
					})
				}
			});
			break;
		case 'b':
			$(".tab-con").html(b);
			var opt = '';
			$.get('/data?action=getData&table=domain&list=True&search=' + id, function(rdata) {
				for(var i=0;i<rdata.length;i++){
					var isIP = isValidIP(rdata[i].name);
					var x = isContains(rdata[i].name, '*');
					if(!isIP && !x){
						opt+='<option>'+rdata[i].name+'</option>'
					}
				}
				$("#domainlist").html(opt);
			})
			getSSLlist(siteName);
			$(".btsslApply").click(function(){
				var ym = $("#domainlist").val();
				
				$.post("/data?action=getKey","table=sites&key=path&id="+id,function(rdata){
					//第一步
					var loadT = layer.msg("正在提交订单，请稍后..",{icon:16,time:0,shade:0.3});
					$.post("/ssl?action=GetDVSSL","domain="+ym+"&path="+rdata,function(tdata){
						layer.close(loadT);
						if(tdata.status){
							layer.msg(tdata.msg,{icon:1});
							var partnerOrderId = tdata.data.partnerOrderId;
							//第二步
							var loadT = layer.msg("正在校验域名，请稍后..",{icon:16,time:0,shade:0.3});
							$.post("/ssl?action=Completed","partnerOrderId="+partnerOrderId+"&siteName="+siteName,function(ydata){
								layer.close(loadT);
								if(!ydata.status){
									layer.msg(ydata.msg,{icon:2});
									getSSLlist(siteName);
									return;
								}
								//第三步
								var loadT = layer.msg("正在部署证书，请稍后..",{icon:16,time:0,shade:0.3});
								$.post("/ssl?action=GetSSLInfo","partnerOrderId="+partnerOrderId+"&siteName="+siteName,function(zdata){
									layer.close(loadT);
									layer.msg(zdata.msg,{icon:zdata.status?1:2});
									getSSLlist(siteName);
								});
							})
							
						}
						else{
							layer.msg(tdata.msg,{icon:2})
						}
					})
				})
			});
			break;
		case 'lets':
			$.get("/ssl?action=GetUserInfo",function(sdata){
				if(!sdata.status){
					$(".tab-con").html(a);
					$("#btusername").blur(function(){
						if(!(/^1(3|4|5|7|8)\d{9}$/.test($(this).val()))){ 
							$("#btusername").css("border","1px solid #e53451");
							$("#btusername").next("i").html("请输入手机号码");
						}
						else{
							$("#btusername").removeAttr("style").css("width","200px");
							$("#btusername").next("i").empty();
						}
					});
					$(".btlogin").click(function(){
						var data = "username="+$("#btusername").val()+"&password="+$("#btpassword").val();
						$.post("/ssl?action=GetToken",data,function(tdata){
							if(tdata.status){
								layer.msg(tdata.msg,{icon:1});
								BTssl('lets',id,siteName);
							}
							else{
								layer.msg(tdata.msg,{icon:2})
							}
						})
					})
				}
				else{
					if(getCookie('letssl') == 1){
						$.post('site?action=GetSSL','siteName='+siteName,function(rdata){
							var lets = '<div class="myKeyCon ptb15"><div class="ssl-con-key pull-left mr20">密钥(KEY)<br><textarea id="key" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.key+'</textarea></div>'
								+ '<div class="ssl-con-key pull-left">证书(CRT/PEM)<br><textarea id="csr" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.csr+'</textarea></div>'
								+ '</div>'
								+ '<ul class="help-info-text c7 pull-left"><li>已为您自动生成Let\'s Encrypt免费证书；</li><li>如需使用其他SSL,请切换其他证书后粘贴您的KEY以及CRT内容，然后保存即可。</li></ul>';
							$(".tab-con").html(lets);
						});
						return;
					}
					$(".tab-con").html(lets);
					var opt='';
					$.get('/data?action=getData&table=domain&list=True&search=' + id, function(rdata) {
						for(var i=0;i<rdata.length;i++){
							var isIP = isValidIP(rdata[i].name);
							var x = isContains(rdata[i].name, '*');
							if(!isIP && !x){
								opt+='<li style="line-height:26px"><input type="checkbox" style="margin-right:5px; vertical-align:-2px" value="'+rdata[i].name+'">'+rdata[i].name+'</li>'
							}
						}
						$("#ymlist").html(opt);
						$("#ymlist li input").click(function(e){
							e.stopPropagation();
						})
						$("#ymlist li").click(function(){
							var o = $(this).find("input");
							if(o.prop("checked")){
								o.prop("checked",false)
							}
							else{
								o.prop("checked",true);
							}
						})
						$(".letsApply").click(function(){
							var c = $("#ymlist input[type='checkbox']");
							var str = [];
							var domains = '';
							for(var i=0; i<c.length; i++){
								if(c[i].checked){
									str.push(c[i].value);
								}
							}
							domains = JSON.stringify(str);
							newSSL(siteName,domains);
							
						})
					});
				}
			});
			
			break;
		case 'other':
			$(".tab-con").html(other);
			var key = '';
			var csr = '';
			$.post('site?action=GetSSL','siteName='+siteName,function(rdata){
				if(rdata.key == false) rdata.key = '';
				if(rdata.csr == false) rdata.csr = '';
				$("#key").val(rdata.key);
				$("#csr").val(rdata.csr);
			});
			break;
	}
}

//取证书列表
function getSSLlist(siteName){
	var tr='';
	var loadT = layer.msg("正在获取证书列表，请稍后..",{icon:16,time:0,shade:0.3});
	$.get("/ssl?action=GetOrderList&siteName="+siteName,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			for(var i=0;i<rdata.data.length;i++){
				var txt = '';
				var tips = '';
				var icoask = '';
				txt = (rdata.data[i].stateName == "订单完成") ? '<a href="javascript:onekeySSl(\''+rdata.data[i].partnerOrderId+'\',\''+siteName+'\');" class="btlink">部署</a>' : '';
				if(rdata.data[i].stateName == "待域名确认") {
					txt = '<a href="javascript:VerifyDomain(\''+rdata.data[i].partnerOrderId+'\',\''+siteName+'\');" class="btlink">验证域名</a>';
					tips = '请检查域名是否解析到本服务器';
					icoask = '<i class="ico-font-ask" title="'+tips+'">?</i>';
				}
				if(rdata.data[i].setup){
					txt = '已部署';
				}
				
				tr += '<tr><td>'+rdata.data[i].commonName+'</td><td>'+getLocalTime(rdata.data[i].endtime).split(" ")[0]+'</td><td title='+tips+'>'+rdata.data[i].stateName+icoask+'</td><td class="text-right">'+txt+'</td></tr>'
			}
			$("#ssllist").html(tr);
		}
	});
}

//一键部署证书
function onekeySSl(partnerOrderId,siteName){
	var loadT = layer.msg("正在部署证书，请稍后..",{icon:16,time:0,shade:0.3});
	$.post("/ssl?action=GetSSLInfo","partnerOrderId="+partnerOrderId+"&siteName="+siteName,function(zdata){
		layer.close(loadT);
		layer.msg(zdata.msg,{icon:zdata.status?1:2});
		getSSLlist(siteName);
	})
}

//验证域名
function VerifyDomain(partnerOrderId,siteName){
	var loadT = layer.msg("正在校验域名，请稍后..",{icon:16,time:0,shade:0.3});
	$.post("/ssl?action=Completed","partnerOrderId="+partnerOrderId+'&siteName='+siteName,function(ydata){
		layer.close(loadT);
		if(!ydata.status){
			layer.msg(ydata.msg,{icon:2});
			return;
		}
		//第三步
		var loadT = layer.msg("正在部署证书，请稍后..",{icon:16,time:0,shade:0.3});
		$.post("/ssl?action=GetSSLInfo","partnerOrderId="+partnerOrderId+"&siteName="+siteName,function(zdata){
			layer.close(loadT);
			if(zdata.status) getSSLlist();
			layer.msg(zdata.msg,{icon:zdata.status?1:2});
		});
	});
}

//旧的设置SSL
function SetSSL_old(siteName){
	$.post('site?action=GetSSL','siteName='+siteName,function(rdata){
		var status_selecteda ="";
		var status_selectedb ="";
		var status_selectedc ="";
		if(rdata.key == false) rdata.key = '';
		if(rdata.csr == false) rdata.csr = '';
		switch(rdata.type){
			case -1:
				status_selecteda = "checked='checked'";
				break;
			case 1:
				status_selectedb = "checked='checked'";
				break
			case 0:
				status_selectedc = "checked='checked'";
			default:
				status_selecteda = "checked='checked'";
		}

		var mBody = '<div class="ssl-con c4">'
				  + '<div class="ssl-type label-input-group ptb10"><label class="mr20"><input type="radio" name="type" value="0" '+status_selecteda+'/>关闭SSL</label><label class="mr20"><input type="radio" name="type" value="1" '+status_selectedb+'/>Let\'s Encrypt免费证书</label><label><input class="otherssl" name="type" type="radio" value="2" '+status_selectedc+'>使用其他证书</label></div>'
				  + '<div class="ssl-type-con"></div>'
				  + '</div>';
		var mykeyhtml = '<div class="myKeyCon ptb15"><div class="ssl-con-key pull-left mr20">密钥(KEY)<br><textarea id="key" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.key+'</textarea></div>'
					+ '<div class="ssl-con-key pull-left">证书(CRT/PEM)<br><textarea id="csr" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.csr+'</textarea></div>'
					+ '<div class="ssl-btn pull-left mtb15" style="width:100%"><button class="btn btn-success btn-sm" onclick="ChangeSaveSSL(\''+siteName+'\')">更新证书</button></div></div>'
					+ '<ul class="help-info-text c7 pull-left"><li>已为您自动生成Let\'s Encrypt免费证书；</li><li>如需使用其他SSL,请切换其他证书后粘贴您的KEY以及CRT内容，然后保存即可。</li></ul>';
		
		var othersslhtml = '<div class="myKeyCon ptb15"><div class="ssl-con-key pull-left mr20">密钥(KEY)<br><textarea id="key" class="bt-input-text">'+rdata.key+'</textarea></div>'
					+ '<div class="ssl-con-key pull-left">证书(CRT/PEM)<br><textarea id="csr" class="bt-input-text">'+rdata.csr+'</textarea></div>'
					+ '<div class="ssl-btn pull-left mtb15" style="width:100%"><button class="btn btn-success btn-sm" onclick="SaveSSL(\''+siteName+'\')">保存</button></div></div>'
					+ '<ul class="help-info-text c7 pull-left"><li>粘贴您的KEY以及CRT内容，然后保存即可<a href="http://www.bt.cn/bbs/thread-704-1-1.html" target="_blank" style="color:green;">[帮助]</a>。</li></ul>';
		$("#webedit-con").html(mBody);
		if(rdata.type == 1){
			$(".ssl-type-con").html(mykeyhtml);
		}
		if(rdata.type == 0){
			$(".ssl-type-con").html(othersslhtml);
		}
		$("input[type='radio']").click(function(){
			var val = $(this).val();
			if(val == 0){
				OcSSL('CloseSSLConf',siteName)
			}
			if(val == 1){
				OcSSL("CreateLet",siteName);
			}
			if(val == 2){
				//OcSSL("CreateLet",siteName);
				$(".ssl-type-con").html(othersslhtml);
			}
		});
	});

}
//开启与关闭SSL
function OcSSL(action,siteName){
	var loadT = layer.msg('正在获取证书,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post("site?action="+action,'siteName='+siteName+'&updateOf=1',function(rdata){
		layer.close(loadT)
		
		if(!rdata.status){
			if(!rdata.out){
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				//SetSSL(siteName);
				return;
			}
			
			data = "<p>证书获取失败：</p><hr />"
			for(var i=0;i<rdata.out.length;i++){
				data += "<p>域名: "+rdata.out[i].Domain+"</p>"
					  + "<p>错误类型: "+rdata.out[i].Type+"</p>"
					  + "<p>详情: "+rdata.out[i].Detail+"</p>"
					  + "<hr />"
			}
			
			layer.msg(data,{icon:2,time:0,shade:0.3,shadeClose:true});
			return;
		}
		
		setCookie('letssl',0);
		$.post('/system?action=ServiceAdmin','name='+getCookie('serverType')+'&type=reload',function(result){
			//SetSSL(siteName);
			if(!result.status) layer.msg(result.msg,{icon:2});
		});
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		$(".bt-w-menu .bgw").click();
	})
}

//生成SSL
function newSSL(siteName,domains){
	var loadT = layer.msg('正在获取证书,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('site?action=CreateLet','siteName='+siteName+'&domains='+domains+'&updateOf=1',function(rdata){
		layer.close(loadT)
		if(rdata.status){
			var mykeyhtml = '<div class="myKeyCon ptb15"><div class="ssl-con-key pull-left mr20">密钥(KEY)<br><textarea id="key" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.key+'</textarea></div>'
					+ '<div class="ssl-con-key pull-left">证书(CRT/PEM)<br><textarea id="csr" class="bt-input-text" readonly="" style="background-color:#f6f6f6">'+rdata.csr+'</textarea></div>'
					+ '</div>'
					+ '<ul class="help-info-text c7 pull-left"><li>已为您自动生成Let\'s Encrypt免费证书；</li><li>如需使用其他SSL,请切换其他证书后粘贴您的KEY以及CRT内容，然后保存即可。</li></ul>';
			$(".btssl").html(mykeyhtml);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			return;
		}
		
		if(!rdata.out){
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			//SetSSL(siteName);
			return;
		}
		
		data = "<p>证书获取失败，返回如下错误信息：</p><hr />"
		for(var i=0;i<rdata.out.length;i++){
			data += "<p>域名:"+rdata.out[i].Domain+"</p>"
				  + "<p>错误类型:"+rdata.out[i].Type+"</p>"
				  + "<p>详情:"+rdata.out[i].Detail+"</p>"
				  + "<hr />"
		}
		if(rdata.err[0].length > 10) data += '<p style="color:red;">' + rdata.err[0].replace(/\n/g,'<br>') + '</p>';
		if(rdata.err[1].length > 10) data += '<p style="color:red;">' + rdata.err[1].replace(/\n/g,'<br>') + '</p>';
		setCookie('letssl',1);
		layer.msg(data,{icon:2,time:0,shade:0.3,shadeClose:true});
		
	});
}

//保存SSL
function SaveSSL(siteName){
	var data = 'type=1&siteName='+siteName+'&key='+encodeURIComponent($("#key").val())+'&csr='+encodeURIComponent($("#csr").val());
	var loadT = layer.msg('正在保存...',{icon:16,time:20000,shade: [0.3, '#000']})
	$.post('site?action=SetSSL',data,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1});
		}else{
			layer.msg(rdata.msg,{icon:2,time:0,shade:0.3,shadeClose:true});
		}
	});
}

//更新SSL
function ChangeSaveSSL(siteName){
	var loadT = layer.msg('正在更新证书,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('site?action=CreateLet','siteName='+siteName+'&updateOf=2',function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

//PHP版本
function PHPVersion(siteName){
	$.post('/site?action=GetSitePHPVersion','siteName='+siteName,function(version){
		if(version.status === false){
			layer.msg(version.msg,{icon:5});
			return;
		}
		$.post('/site?action=GetPHPVersion',function(rdata){
			var versionSelect = "<div class='webEdit-box'>\
									<div class='line'>\
										<span class='tname'>选择PHP版本</span>\
										<div class='info-r'>\
											<select id='phpVersion' class='bt-input-text mr5' name='phpVersion' style='width:110px'>";
			var optionSelect = '';
			for(var i=0;i<rdata.length;i++){
				optionSelect = version.phpversion == rdata[i].version?'selected':'';
				versionSelect += "<option value='"+ rdata[i].version +"' "+ optionSelect +">"+ rdata[i].name +"</option>"
			}
			versionSelect += "</select>\
							<button class='btn btn-success btn-sm' onclick=\"SetPHPVersion('"+siteName+"')\">切换</button>\
							</div>\
						</div>\
							<ul class='help-info-text c7 ptb10'>\
								<li>请根据您的程序需求选择版本，切换版本可能导致您的程序无法正常使用；</li>\
								<li>若非必要,请尽量不要使用PHP5.2,这会降低您的服务器安全性；</li>\
								<li>PHP7不支持mysql扩展，默认安装mysqli以及mysql-pdo。</li>\
							</ul>\
						</div>\
					</div>";
			if(version.nodejsversion){
				var nodejs_checked = '';
				if(version.nodejs != -1) nodejs_checked = 'checked';
				versionSelect += '<div class="webEdit-box padding-10">\
									<div class="linex">\
										<label style="font-weight:normal">\
											<input type="checkbox" name="status"  onclick="Nodejs(\''+siteName+'\')" style="width:15px;height:15px;" '+nodejs_checked+' />启用Node.js\
										</label>\
									</div>\
									<ul class="help-info-text c7 ptb10">\
									<li>当前版本为Node.js '+version.nodejsversion+'；</li>\
									<li>Node.js可以与PHP共存,但无法与Tomcat共存；</li>\
									<li>若您的Node.js应用中有php脚本,访问时请添加.php扩展名</li>\
								</ul>\
								</div>'
			}
			$("#webedit-con").html(versionSelect);
		});
	});
}

//tomcat
function toTomcat(siteName){
	$.post('/site?action=GetSitePHPVersion','siteName='+siteName,function(version){
		if(version.status === false){
			layer.msg('apache2.2暂不支持Tomcat!',{icon:5});
			return;
		}
		$.post('/site?action=GetPHPVersion',function(rdata){
			var versionSelect ='';
			if(version.tomcatversion){
				var tomcat_checked = '';
				if(version.tomcat != -1) tomcat_checked = 'checked';
				versionSelect += '<div class="webEdit-box padding-10">\
									<div class="linex">\
										<label style="font-weight:normal">\
											<input type="checkbox" name="status"  onclick="Tomcat(\''+siteName+'\')" style="width:15px;height:15px;" '+tomcat_checked+' />启用Tomcat\
										</label>\
									</div>\
									<ul class="help-info-text c7 ptb10">\
									<li>当前版本为Tomcat '+version.tomcatversion+',若您需要其它版本,请到软件管理 - 所有软件 中切换；</li>\
									<li>Tomcat可以与PHP共存,但无法与Node.js共存；</li>\
									<li>若您的tomcat应用中有php脚本,访问时请添加.php扩展名</li>\
									<li>开启成功后,大概需要1分钟时间生效!</li>\
								</ul>\
								</div>'
			}else{
				layer.msg('您没有安装Tomcat，请先安装!',{icon:2});
				versionSelect = '<font>请先安装Tomcat!</font>'
			}
			
			$("#webedit-con").html(versionSelect);
		});
	});
}
//设置Tomcat
function Tomcat(siteName){
	var data = 'siteName='+siteName;
	var loadT = layer.msg('正在配置,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site?action=SetTomcat',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//设置PHP版本
function SetPHPVersion(siteName){
	var data = 'version='+$("#phpVersion").val()+'&siteName='+siteName;
	var loadT = layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/site?action=SetPHPVersion',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

//配置文件
function ConfigFile(webSite){
	$.post('/files?action=GetFileBody','path=/www/server/panel/vhost/'+getCookie('serverType')+'/'+webSite+'.conf',function(rdata){
		var mBody = "<div class='webEdit-box padding-10'>\
		<textarea style='height: 320px; width: 445px; margin-left: 20px;line-height:18px' id='configBody'>"+rdata.data+"</textarea>\
			<div class='info-r'>\
				<button id='SaveConfigFileBtn' class='btn btn-success btn-sm' style='margin-top:15px;'>保存</button>\
				<ul class='help-info-text c7 ptb10'>\
					<li>此处为站点主配置文件,若您不了解配置规则,请勿随意修改.</li>\
				</ul>\
			</div>\
		</div>";
		$("#webedit-con").html(mBody);
		var editor = CodeMirror.fromTextArea(document.getElementById("configBody"), {
			extraKeys: {"Ctrl-Space": "autocomplete"},
			lineNumbers: true,
			matchBrackets:true,
		});
		$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
		$("#SaveConfigFileBtn").click(function(){
			$("#configBody").empty();
			$("#configBody").text(editor.getValue());
			SaveConfigFile(webSite,rdata.encoding);
		})
	});
}

//保存配置文件
function SaveConfigFile(webSite,encoding){
	var data = 'encoding='+encoding+'&data='+encodeURIComponent($("#configBody").val())+'&path=/www/server/panel/vhost/'+getCookie('serverType')+'/'+webSite+'.conf';
	var loadT = layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/files?action=SaveFileBody',data,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1});
		}else{
			layer.msg(rdata.msg,{icon:2,time:0,shade:0.3,shadeClose:true});
		}
	});
}

//伪静态
function Rewrite(siteName){
	$.post("/site?action=GetRewriteList&siteName="+siteName,function(rdata){
		var filename = '/www/server/panel/vhost/rewrite/'+siteName+'.conf';
		if(getCookie('serverType') == 'apache')	filename = rdata.sitePath+'/.htaccess';
		$.post('/files?action=GetFileBody','path='+filename,function(fileBody){
			var rList = ''; 
			for(var i=0;i<rdata.rewrite.length;i++){
				rList += "<option value='"+rdata.rewrite[i]+"'>"+rdata.rewrite[i]+"</option>";
			}
			var webBakHtml = "<div class='bt-form'>\
						<div class='line'>\
						<select id='myRewrite' class='bt-input-text mr20' name='rewrite' style='width:30%;'>"+rList+"</select>\
						<span>规则转换工具：<a href='http://www.bt.cn/Tools' target='_blank' style='color:#20a53a'>Apache转Nginx</a>\</span>\
						<textarea class='bt-input-text' style='height: 260px; width: 480px; line-height:18px;margin-top:10px;padding:5px;' id='rewriteBody'>"+fileBody.data+"</textarea></div>\
						<button id='SetRewriteBtn' class='btn btn-success btn-sm'>保存</button>\
						<button id='SetRewriteBtnTel' class='btn btn-success btn-sm'>另存为模板</button>\
						<ul class='help-info-text c7 ptb15'>\
							<li>请选择您的应用,若设置伪静态后,网站无法正常访问,请尝试设置回default或清空规则</li>\
							<li>您可以对伪静态规则进行修改,修改完后保存即可!</li>\
						</ul>\
						</div>";
			$("#webedit-con").html(webBakHtml);
			
			var editor = CodeMirror.fromTextArea(document.getElementById("rewriteBody"), {
	            extraKeys: {"Ctrl-Space": "autocomplete"},
				lineNumbers: true,
				matchBrackets:true,
			});
			
			$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
			$("#SetRewriteBtn").click(function(){
				$("#rewriteBody").empty();
				$("#rewriteBody").text(editor.getValue());
				SetRewrite(filename);
			});
			$("#SetRewriteBtnTel").click(function(){
				$("#rewriteBody").empty();
				$("#rewriteBody").text(editor.getValue());
				SetRewriteTel();
			});
			
			$("#myRewrite").change(function(){
				var rewriteName = $(this).val();
				if(rewriteName == '0.当前'){
					rpath = '/www/server/panel/vhost/rewrite/'+siteName+'.conf';
					if(getCookie('serverType') == 'apache')	filename = rdata.sitePath+'/.htaccess';
				}else{
					rpath = '/www/server/panel/rewrite/' + getCookie('serverType')+'/' + rewriteName + '.conf';
				}
				
				$.post('/files?action=GetFileBody','path='+rpath,function(fileBody){
					 $("#rewriteBody").val(fileBody.data);
					 editor.setValue(fileBody.data);
				});
			});
		});
	});
}


//设置伪静态
function SetRewrite(filename){
	var data = 'data='+encodeURIComponent($("#rewriteBody").val())+'&path='+filename+'&encoding=utf-8';
	var loadT = layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/files?action=SaveFileBody',data,function(rdata){
		layer.close(loadT);
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1});
		}else{
			layer.msg(rdata.msg,{icon:2,time:0,shade:0.3,shadeClose:true});
		}
	});
}
var aindex = null;
//保存为模板
function SetRewriteTel(act){
	if(act != undefined){
		name = $("#rewriteName").val();
		if(name == ''){
			layer.msg("模板名称不能为空!",{icon:5});
			return;
		}
		var data = 'data='+encodeURIComponent($("#rewriteBody").val())+'&name='+name;
		var loadT = layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/site?action=SetRewriteTel',data,function(rdata){
			layer.close(loadT);
			layer.close(aindex);
			
			layer.msg(rdata.msg,{icon:rdata.status?1:5});
		});
		return;
	}
	
	aindex = layer.open({
		type: 1,
		shift: 5,
		closeBtn: 2,
		area: '320px', //宽高
		title: '保存为Rewrite模板',
		content: '<div class="bt-form pd20 pb70">\
					<div class="line">\
						<input type="text" class="bt-input-text" name="rewriteName" id="rewriteName" value="" placeholder="模板名称" style="width:100%" />\
					</div>\
					<div class="bt-form-submit-btn">\
					<button type="button" class="btn btn-danger btn-sm">取消</button>\
					<button type="button" id="rewriteNameBtn" class="btn btn-success btn-sm" onclick="SetRewriteTel(1)">确定</button>\
					</div>\
				</div>'
	});
	$(".btn-danger").click(function(){
		layer.close(aindex);
	});
	$("#rewriteName").focus().keyup(function(e){
		if(e.keyCode == 13) $("#rewriteNameBtn").click();
	});
}
//修改默认页
function SiteDefaultPage(){
	stype = getCookie('serverType');
	layer.open({
		type: 1,
		area: '360px',
		title: '修改默认页',
		closeBtn: 2,
		shift: 0,
		content: '<div class="changeDefault pd20">\
						<button class="btn btn-default btn-sm mg10" style="width:138px" onclick="changeDefault(1)">默认文档</button>\
						<button class="btn btn-default btn-sm mg10" style="width:138px" onclick="changeDefault(2)">404错误页</button>\
							<button class="btn btn-default btn-sm mg10" style="width:138px" onclick="changeDefault('+(stype=='nginx'?3:4)+')">'+(stype=='nginx'?'Nginx':'Apache')+'空白页</button>\
						<button class="btn btn-default btn-sm mg10" style="width:138px" onclick="changeDefault(5)">默认站点停止页</button>\
				</div>'
	});
}
function changeDefault(type){
	var vhref='';
	switch(type){
		case 1:
			vhref = '/www/server/panel/data/defaultDoc.html';
			break;
		case 2:
			vhref = '/www/server/panel/data/404.html';
			break;
		case 3:
			vhref = '/www/server/nginx/html/index.html';
			break;
		case 4:
			vhref = '/www/server/apache/htdocs/index.html';
			break;
		case 5:
			vhref = '/www/server/stop/index.html';
			break;
	}
	OnlineEditFile(0,vhref);
}