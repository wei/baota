//软件管理
function phpSoftMain(name,key){
	if(!isNaN(name)){
		var nametext = "php"+name;
	}
	
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/system?action=GetConcifInfo',function(rdata){
		layer.close(loadT);
		nameA = rdata.php[key];
		layer.open({
			type: 1,
			area: '640px',
			title: nametext+'管理',
			closeBtn: 2,
			shift: 0,
			content: '<div class="webEdit" style="width:640px;">\
				<div class="webEdit-menu">\
					<p class="active" onclick="service(\''+name+'\','+nameA.status+')">php服务</p>\
					<p onclick="phpUploadLimit(\''+name+'\','+nameA.max+')">上传限制</p>\
					<p class="phphide" onclick="phpTimeLimit(\''+name+'\','+nameA.maxTime+')">超时限制</p>\
					<p onclick="configChange(\''+name+'\')">配置修改</p>\
					<p onclick="SetPHPConfig(\''+name+'\','+nameA.pathinfo+')">扩展配置</p>\
					<p onclick="disFun(\''+name+'\')">禁用函数</p>\
					<p class="phphide" onclick="SetFpmConfig(\''+name+'\')">性能调整</p>\
					<p class="phphide" onclick="GetPHPStatus(\''+name+'\')">负载状态</p>\
					<p onclick="BtPhpinfo(\''+name+'\')">phpinfo</p>\
				</div>\
				<div id="webEdit-con" class="webEdit-box webEdit-con">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
		})
		if(name== "52"){
			$(".phphide").hide();
		}
		service(name,nameA.status);
		$(".webEdit-menu p").click(function(){
			//var i = $(this).index();
			var txt = $(this).text();
			$(this).addClass("active").siblings().removeClass("active");
			if(txt != "扩展配置") $(".soft-man-con").removeAttr("style");
		})
	});
}

//服务
function service(name,status){
	
	var serviceCon ='<p class="status">当前状态：<span>'+(status?'开启':'关闭')+'</span><span style="color: '+(status?'#20a53a;':'red;')+' margin-left: 3px;" class="glyphicon '+(status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p>\
					<div class="sfm-opt">\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\''+(status?'stop':'start')+'\')">'+(status?'停止':'启动')+'</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'restart\')">重启</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'reload\')">重载配置</button>\
					</div>'; 
	$(".soft-man-con").html(serviceCon);
}


function neice(act){
	if(act == 1){
		var bbs_name = $("#ename").val();
		var qq = $("#qq").val();
		var email = $("#email").val();
		
		if(bbs_name == '' || qq == '' || email == ''){
			layer.msg('论坛用户名/QQ/邮箱不能为空!',{icon:2});
			return;
		}
		
		var data = 'bbs_name=' + bbs_name + '&qq=' + qq + '&email=' + email;
		var loadT = layer.msg("正在提交,请稍候...",{icon:16,time:0,shade:[0.3,'#000']});
		$.post('/ajax?action=SetBeta',data,function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
		
		return;
	}
	$.get('/ajax?action=GetBetaStatus',function(rdata){
		if(rdata != 'False'){
			var user = rdata.split("|")[0];
			//layer.msg('您当前已经是内测用户!',{icon:1});
			layer.open({
				type: 1,
				area: '500px',
				title: '申请内测',
				closeBtn: 2,
				shift: 5,
				shadeClose: false,
				content:'<div class="nc-tips">\
						<p style="font-size: 16px; margin-bottom: 10px;">恭喜您，成为内测组的一员！</p>\
						<p>您的宝塔论坛认证用户为：<span>'+user+'</span></p>\
						<p>您可以用这个账号在内测专用版块反馈交流，<a href="http://www.bt.cn/bbs/forum.php?mod=forumdisplay&fid=39" target="_blank">宝塔论坛内测专用版块</a></p>\
						<p>如果您想返回正式版，则直接SSH里再执行安装代码即可</p>\
				</div>'
			})
			return;
		}
	
		layer.open({
			type: 1,
			area: '560px',
			title: '申请内测',
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content:'<div class="zun-form-new" style="padding-top:0"><div class="neice_con">\
						<div class="tit">注意事项</div>\
						<div class="nc_con">\
							<p style="color:red">1、注意，请不要在正式商用网站及自己生产环境的面板申请测试版。</p>\
							<p>2、所有新功能做完内部初审后都会第一时间向所有内测用户推送。</p>\
							<p>3、内测版会有诸多小Bug，如遇到，可以论坛或QQ找我们，我们一定负责到底。</p>\
							<p>4、内测意义在于为广大宝塔用户找Bug，宝塔团队再一次感谢您的积极参与。</p>\
							<p>5、如果你不是愿意付出及肯折腾学习的人，我们不建议申请内测。</p>\
						</div>\
						<div class="nc_opt"><label><input type="checkbox" name="yes" value="yes" />以上5句我已阅读并知晓</label></div>\
						<div class="tit">联系方式</div>\
						<div class="nc_con nc_con_user">\
							<p><span>论坛用户名</span><input id="ename" name="name" value=""></p>\
							<p style="line-height: 10px; margin-left: 80px; position: relative; top: -5px;">请如实填写宝塔论坛账号，提交后我们会审核，如未有，<a style="color:#20a53a" href="http://www.bt.cn/bbs/member.php?mod=register" target="_blank">去注册宝塔论坛账户</a></p>\
							<p><span>QQ号码</span><input id="qq" name="qq" value=""></p>\
							<p><span>邮箱</span><input id="email" name="email" value=""></p>\
						</div>\
					</div>\
					<div class="submit-btn"><button type="button" class="btn btn-danger btn-sm" onclick="layer.closeAll()">取消</button>\
					<button type="button" class="btn btn-success btn-sm" onclick="neice(1)">提交</button></div></div>'
		})
		$(".nc_con_user input").addClass("disabled").attr({"disabled":"disabled","placeholder":"阅读注意事项并确认"});
		$(".nc_opt label").click(function(){
			var check = $(".nc_opt input").prop("checked");
			if(!check){
				$(".nc_con_user input").addClass("disabled").attr({"disabled":"disabled","placeholder":"阅读注意事项并确认"});
			}
			else{
				$(".nc_con_user input").removeClass("disabled").removeAttr("disabled").removeAttr("placeholder");
			}
		});
		$('#qq').on('input', function() {
			var str = $(this).val();
			$("#email").val(str+"@qq.com");
		})
	})
}

//php上传限制
function phpUploadLimit(version,max){
	var LimitCon = '<p class="conf_p"><input class="phpUploadLimit" type="number" value="'+max+'" name="max">MB</p><button class="btn btn-success btn-sm" onclick="SetPHPMaxSize(\''+version+'\')">保存</button>';
	$(".soft-man-con").html(LimitCon);
}
//php超时限制
function phpTimeLimit(version,max){
	var LimitCon = '<p class="conf_p"><input class="phpTimeLimit" type="number" value="'+max+'">秒</p><button class="btn btn-success btn-sm" onclick="SetPHPMaxTime(\''+version+'\')">保存</button>';
	$(".soft-man-con").html(LimitCon);
}
//设置超时限制
function SetPHPMaxTime(version){
	var max = $(".phpTimeLimit").val();
	var loadT = layer.msg('正在保存数据...',{icon:16,time:0});
	$.post('/config?action=setPHPMaxTime','version='+version+'&time='+max,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	})
}
//设置PHP上传限制
function SetPHPMaxSize(version){
	max = $(".phpUploadLimit").val();
	if(max < 2){
		alert(max);
		layer.msg('上传大小限制不能小于2M',{icon:2});
		return;
	}
	var loadT = layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPHPMaxSize','&version='+version+'&max='+max,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	})
}
//配置修改
function configChange(type){
	var con = '<textarea style="height: 320px; line-height:18px;" id="textBody"></textarea>\
					<button id="OnlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
					<ul class="help-info-text">\
						<li>此处为'+type+'主配置文件,若您不了解配置规则,请勿随意修改。</li>\
					</ul>';
	$(".soft-man-con").html(con);
	var fileName = '';
	switch(type){
		case 'mysqld':
			fileName = '/etc/my.cnf';
			break;
		case 'nginx':
			fileName = '/www/server/nginx/conf/nginx.conf';
			break;
		case 'pure-ftpd':
			fileName = '/www/server/pure-ftpd/etc/pure-ftpd.conf';
			break;
		case 'apache':
			fileName = '/www/server/apache/conf/httpd.conf';
			break;
		default:
			fileName = '/www/server/php/'+type+'/etc/php.ini';
			break;
	}
	var loadT = layer.msg("读取中...",{icon:16,time:0});
	$.post('/files?action=GetFileBody', 'path=' + fileName, function(rdata) {
		layer.close(loadT);
		$("#textBody").empty().text(rdata.data);
		$(".CodeMirror").remove();
		var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
			extraKeys: {"Ctrl-Space": "autocomplete"},
			lineNumbers: true,
			matchBrackets:true,
		});
		editor.focus();
		$(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
		$("#OnlineEditFileBtn").click(function(){
			$("#textBody").text(editor.getValue());
			confSafe(fileName);
		})
	})
}
//配置保存
function confSafe(fileName){
	var data = encodeURIComponent($("#textBody").val());
	var encoding = 'utf-8';
	var loadT = layer.msg('正在保存...', {
		icon: 16,
		time: 0
	});
	$.post('/files?action=SaveFileBody', 'data=' + data + '&path=' + fileName+'&encoding='+encoding, function(rdata) {
		layer.close(loadT);
		layer.msg(rdata.msg, {
			icon: rdata.status ? 1 : 2
		});
	});
}


//设置PATHINFO
function SetPathInfo(version,type){
	var loadT = layer.msg('正在处理..',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPathInfo','version='+version+'&type='+type,function(rdata){
		var pathinfo = (type == 'on')?true:false;
		var pathinfoOpt = '<a style="color:red;" href="javascript:SetPathInfo(\''+version+'\',\'off\');">关闭</a>'
		if(!pathinfo){
			pathinfoOpt = '<a class="link" href="javascript:SetPathInfo(\''+version+'\',\'on\');">开启</a>'
		}
		var pathinfo1 = '<td>PATH_INFO</td><td>扩展配置</td><td>MVC架构的程序需要开启,如typecho</td><td><span class="ico-'+(pathinfo?'start':'stop')+' glyphicon glyphicon-'+(pathinfo?'ok':'remove')+'"></span></td><td style="text-align: right;" width="50">'+pathinfoOpt+'</td>';
		$("#pathInfo").html(pathinfo1);
		$(".webEdit-menu .active").attr('onclick',"SetPHPConfig('71',"+pathinfo+")");
		layer.msg(rdata.msg,{icon:1});
	})
}

//PHP扩展配置
function SetPHPConfig(version,pathinfo){
	$.get('/ajax?action=GetPHPConfig&version='+version,function(rdata){
		var body  = ""
		var opt = ""
		for(var i=0;i<rdata.libs.length;i++){
			if(rdata.libs[i].versions.indexOf(version) == -1) continue;
			
			if(rdata.libs[i]['task'] == '-1' && rdata.libs[i].phpversions.indexOf(version) != -1){
				opt = '<a style="color:green;" href="javascript:task();">正在安装..</a>'
			}else if(rdata.libs[i]['task'] == '0' && rdata.libs[i].phpversions.indexOf(version) != -1){
				opt = '<a style="color:#C0C0C0;" href="javascript:task();">等待安装..</a>'
			}else if(rdata.libs[i].status){
				opt = '<a style="color:red;" href="javascript:UninstallPHPLib(\''+version+'\',\''+rdata.libs[i].name+'\');">卸载</a>'
			}else{
				opt = '<a class="link" href="javascript:InstallPHPLib(\''+version+'\',\''+rdata.libs[i].name+'\');">安装</a>'
			}
			
			body += '<tr>'
						+'<td>'+rdata.libs[i].name+'</td>'
						+'<td>'+rdata.libs[i].type+'</td>'
						+'<td>'+rdata.libs[i].msg+'</td>'
						+'<td><span class="ico-'+(rdata.libs[i].status?'start':'stop')+' glyphicon glyphicon-'+(rdata.libs[i].status?'ok':'remove')+'"></span></td>'
						+'<td style="text-align: right;">'+opt+'</td>'
				   +'</tr>'
		}
		
		var pathinfoOpt = '<a style="color:red;" href="javascript:SetPathInfo(\''+version+'\',\'off\');">关闭</a>'
		if(!pathinfo){
			pathinfoOpt = '<a class="link" href="javascript:SetPathInfo(\''+version+'\',\'on\');">开启</a>'
		}
		var pathinfo1 = '<tr id="pathInfo"><td>PATH_INFO</td><td>扩展配置</td><td>MVC架构的程序需要开启,如typecho</td><td><span class="ico-'+(pathinfo?'start':'stop')+' glyphicon glyphicon-'+(pathinfo?'ok':'remove')+'"></span></td><td style="text-align: right;" width="50">'+pathinfoOpt+'</td></tr>';
		var con='<div class="divtable" style="margin-right:10px">'
					+'<table class="table table-hover" width="100%" cellspacing="0" cellpadding="0" border="0">'
						+'<thead>'
							+'<tr>'
								+'<th>名称</th>'
								+'<th>类型</th>'
								+'<th>说明</th>'
								+'<th width="40">状态</th>'
								+'<th style="text-align: right;" width="50">操作</th>'
							+'</tr>'
						+'</thead>'
						+'<tbody>'+pathinfo1+body+'</tbody>'
					+'</table>'
				+'</div>';
		$(".soft-man-con").html(con).css({"height":"420px","overflow":"auto","margin-right":0});
	});
}

//安装扩展
function InstallPHPLib(version,name){
	layer.confirm('您真的要安装'+name+'吗?',{closeBtn:2},function(){
		name = name.toLowerCase();
		var data = "name="+name+"&version="+version+"&type=1";
		var loadT = layer.msg('正在添加到安装器...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/files?action=InstallSoft', data, function(rdata)
		{
			setTimeout(function(){
				layer.close(loadT);
				SetPHPConfig(version);
				setTimeout(function(){
					layer.msg(rdata.msg,{icon:rdata.status?1:2});
				},1000);
			},1000);
		});
		
		fly("bi-btn");
		InstallTips();
		GetTaskCount();
	});
}

//卸载扩展
function UninstallPHPLib(version,name){
	layer.confirm('您真的要卸载'+name+'吗?',{closeBtn:2},function(){
		name = name.toLowerCase();
		var data = 'name='+name+'&version='+version;
		var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/files?action=UninstallSoft',data,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			SetPHPConfig(version);
		});
	});
}
//禁用函数
function disFun(version){
	$.get('/ajax?action=GetPHPConfig&version='+version,function(rdata){
	var con = '<textarea name="disable_functions" class="funarea">'+rdata.disable_functions+'</textarea>\
	<button class="btn btn-success btn-sm" onclick="disable_functions(\''+version+'\');">保存</button>\
	<ul class="help-info-text">\
		<li>在此处可以禁用指定函数的调用,以增强环境安全性!</li>\
		<li>强烈建议禁用如exec,system等危险函数,函数之间以英文分号隔开!</li>\
	</ul>';
	$(".soft-man-con").html(con);
	})
}
//设置禁用函数
function disable_functions(version){
	var functions = $("textarea[name='disable_functions']").val();
	var data = 'version='+version+'&disable_functions='+functions;
	var loadT = layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPHPDisable',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}
//性能调整
function SetFpmConfig(version,action){
	if(action == 1){
		var max_children = Number($("input[name='max_children']").val());
		var start_servers = Number($("input[name='start_servers']").val());
		var min_spare_servers = Number($("input[name='min_spare_servers']").val());
		var max_spare_servers = Number($("input[name='max_spare_servers']").val());
		if(max_children < max_spare_servers){
			layer.msg('max_spare_servers 不能大于 max_children',{icon:2});
			return;
		}
		
		if(min_spare_servers > start_servers) {
			layer.msg('min_spare_servers 不能大于 start_servers',{icon:2});
			return;
		}
		
		if(max_spare_servers < min_spare_servers){
			layer.msg('min_spare_servers 不能大于 max_spare_servers',{icon:2});
			return;
		}
		
		if(max_children < start_servers){
			layer.msg('start_servers 不能大于 max_children',{icon:2});
			return;
		}
		
		if(max_children < 1 || start_servers < 1 || min_spare_servers < 1 || max_spare_servers < 1){
			layer.msg('配置值不能小于1',{icon:2});
			return;
		}
		
		var data = 'version='+version+'&max_children='+max_children+'&start_servers='+start_servers+'&min_spare_servers='+min_spare_servers+'&max_spare_servers='+max_spare_servers;
		var loadT = layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/config?action=setFpmConfig',data,function(rdata){
			layer.close(loadT);
			var loadT = layer.msg(rdata.msg,{icon:rdata.status?1:2});				
		}).error(function(){
			layer.close(loadT);
			layer.msg('设置成功!',{icon:1});
		});
		return;
	}
	
	$.post('/config?action=getFpmConfig','version='+version,function(rdata){
		
		var limitList = "<option value='0'>自定义</option>"
						+"<option value='1' "+(rdata.max_children==30?'selected':'')+">30并发</option>"
						+"<option value='2' "+(rdata.max_children==50?'selected':'')+">50并发</option>"
						+"<option value='3' "+(rdata.max_children==100?'selected':'')+">100并发</option>"
						+"<option value='4' "+(rdata.max_children==200?'selected':'')+">200并发</option>"
						+"<option value='5' "+(rdata.max_children==300?'selected':'')+">300并发</option>"
						+"<option value='6' "+(rdata.max_children==500?'selected':'')+">500并发</option>"
						+"<option value='7' "+(rdata.max_children==1000?'selected':'')+">1000并发</option>"
		var body="<div class='bingfa'>"
						+"<p><span class='span_tit'>并发方案：</span><select name='limit' style='width:90px; margin-left:6px;'>"+limitList+"</select></p>"
						+"<p><span class='span_tit'>max_children：</span><input type='number' name='max_children' value='"+rdata.max_children+"' />  *允许创建的最大子进程数</p>"
						+"<p><span class='span_tit'>start_servers：</span><input type='number' name='start_servers' value='"+rdata.start_servers+"' />  *起始进程数（服务启动后初始进程数量）</p>"
						+"<p><span class='span_tit'>min_spare_servers：</span><input type='number' name='min_spare_servers' value='"+rdata.min_spare_servers+"' />   *最小空闲进程数（清理空闲进程后的保留进程数量）</p>"
						+"<p><span class='span_tit'>max_spare_servers：</span><input type='number' name='max_spare_servers' value='"+rdata.max_spare_servers+"' />   *最大空闲进程数（当空闲进程达到此值时开始清理）</p>"
						+"<div><button class='btn btn-success btn-sm' onclick='SetFpmConfig(\""+version+"\",1)'>保存</button></div>"
				+"</div>"
		
		$(".soft-man-con").html(body);
		$("select[name='limit']").change(function(){
					var type = $(this).val();
					var max_children = rdata.max_children;
					var start_servers = rdata.start_servers;
					var min_spare_servers = rdata.min_spare_servers;
					var max_spare_servers = rdata.max_spare_servers;
					switch(type){
						case '1':
							max_children = 30;
							start_servers = 5;
							min_spare_servers = 5;
							max_spare_servers = 20;
							break;
						case '2':
							max_children = 50;
							start_servers = 15;
							min_spare_servers = 15;
							max_spare_servers = 35;
							break;
						case '3':
							max_children = 100;
							start_servers = 20;
							min_spare_servers = 20;
							max_spare_servers = 70;
							break;
						case '4':
							max_children = 200;
							start_servers = 25;
							min_spare_servers = 25;
							max_spare_servers = 150;
							break;
						case '5':
							max_children = 300;
							start_servers = 30;
							min_spare_servers = 30;
							max_spare_servers = 180;
							break;
						case '6':
							max_children = 500;
							start_servers = 35;
							min_spare_servers = 35;
							max_spare_servers = 250;
							break;
						case '7':
							max_children = 1000;
							start_servers = 40;
							min_spare_servers = 40;
							max_spare_servers = 300;
							break;
					}
					
					$("input[name='max_children']").val(max_children);
					$("input[name='start_servers']").val(start_servers);
					$("input[name='min_spare_servers']").val(min_spare_servers);
					$("input[name='max_spare_servers']").val(max_spare_servers);
				});
	});
}

//phpinfo
function BtPhpinfo(version){
	var con = '<button class="btn btn-default btn-sm" onclick="GetPHPInfo(\''+version+'\')">查看phpinfo()</button>';
	$(".soft-man-con").html(con);
}
//获取PHPInfo
function GetPHPInfo(version){
	var loadT = layer.msg('正在获取...',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=GetPHPInfo&version='+version,function(rdata){
		layer.close(loadT);
		layer.open({
			type: 1,
		    title: "PHP-"+version+"-PHPINFO",
		    area: ['70%','90%'],
		    closeBtn: 2,
		    shadeClose: true,
		    content:rdata.replace('a:link {color: #009; text-decoration: none; background-color: #fff;}','').replace('a:link {color: #000099; text-decoration: none; background-color: #ffffff;}','')
		});
	});
}
//nginx
function nginxSoftMain(name){
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/system?action=GetConcifInfo',function(rdata){
		layer.close(loadT);
		nameA = rdata['web'];
		var status = name=='nginx'?'<p onclick="GetNginxStatus()">负载状态</p>':'';
		layer.open({
			type: 1,
			area: '640px',
			title: name+'管理',
			closeBtn: 2,
			shift: 0,
			content: '<div class="webEdit" style="width:640px;">\
				<div class="webEdit-menu">\
					<p class="active" onclick="service(\''+name+'\','+nameA.status+')">Web服务</p>\
					<p onclick="configChange(\''+name+'\')">配置修改</p>\
					'+status+'\
				</div>\
				<div id="webEdit-con" class="webEdit-box webEdit-con">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
		})
		service(name,nameA.status);
		$(".webEdit-menu p").click(function(){
			//var i = $(this).index();
			$(this).addClass("active").siblings().removeClass("active");
		})
	});
}
//查看Nginx负载状态
function GetNginxStatus(){
	$.post('/ajax?action=GetNginxStatus','',function(rdata){
		var con = "<div><table class='table table-hover table-bordered'>\
						<tr><th>活动连接(Active connections)</th><td>"+rdata.active+"</td></tr>\
						<tr><th>总连接次数(accepts)</th><td>"+rdata.accepts+"</td></tr>\
						<tr><th>总握手次数(handled)</th><td>"+rdata.handled+"</td></tr>\
						<tr><th>总请求数(requests)</th><td>"+rdata.requests+"</td></tr>\
						<tr><th>请求数(Reading)</th><td>"+rdata.Reading+"</td></tr>\
						<tr><th>响应数(Writing)</th><td>"+rdata.Writing+"</td></tr>\
						<tr><th>驻留进程(Waiting)</th><td>"+rdata.Waiting+"</td></tr>\
					 </table></div>";
		$(".soft-man-con").html(con);
	})
}
//查看PHP负载状态
function GetPHPStatus(version){
	$.post('/ajax?action=GetPHPStatus','version='+version,function(rdata){
		var con = "<div style='height:420px;overflow:hidden;'><table class='table table-hover table-bordered GetPHPStatus' style='margin:0;padding:0'>\
						<tr><th>应用池(pool)</th><td>"+rdata.pool+"</td></tr>\
						<tr><th>进程管理方式(process manager)</th><td>"+((rdata['process manager'] == 'dynamic')?'活动':'静态')+"</td></tr>\
						<tr><th>启动日期(start time)</th><td>"+rdata['start time']+"</td></tr>\
						<tr><th>请求数(accepted conn)</th><td>"+rdata['accepted conn']+"</td></tr>\
						<tr><th>请求队列(listen queue)</th><td>"+rdata['listen queue']+"</td></tr>\
						<tr><th>最大等待队列(max listen queue)</th><td>"+rdata['max listen queue']+"</td></tr>\
						<tr><th>socket队列长度(listen queue len)</th><td>"+rdata['listen queue len']+"</td></tr>\
						<tr><th>空闲进程数量(idle processes)</th><td>"+rdata['idle processes']+"</td></tr>\
						<tr><th>活跃进程数量(active processes)</th><td>"+rdata['active processes']+"</td></tr>\
						<tr><th>总进程数量(total processes)</th><td>"+rdata['total processes']+"</td></tr>\
						<tr><th>最大活跃进程数量(max active processes)</th><td>"+rdata['max active processes']+"</td></tr>\
						<tr><th>到达进程上限次数(max children reached)</th><td>"+rdata['max children reached']+"</td></tr>\
						<tr><th>慢请求数量(slow requests)</th><td>"+rdata['slow requests']+"</td></tr>\
					 </table></div>";
		$(".soft-man-con").html(con);
		$(".GetPHPStatus td,.GetPHPStatus th").css("padding","7px");
	})
}

//软件管理窗口
function SoftMan(name){
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/system?action=GetConcifInfo',function(rdata){
		layer.close(loadT);
		var nameA = rdata[name.replace('mysqld','mysql')];
		var menu = '<p onclick="configChange(\''+name+'\')">配置修改</p>';
		if(name == "phpmyadmin"){
			menu = '<p onclick="phpVer(\''+name+'\',\''+nameA.phpversion+'\')">php版本</p><p onclick="safeConf(\''+name+'\','+nameA.port+','+nameA.auth+')">安全设置</p>';
		}
		
		layer.open({
			type: 1,
			area: '640px',
			title: name+'管理',
			closeBtn: 2,
			shift: 0,
			content: '<div class="webEdit" style="width:640px;">\
				<div class="webEdit-menu">\
					<p class="active" onclick="service(\''+name+'\',\''+nameA.status+'\')">服务</p>'
					+menu+
				'</div>\
				<div id="webEdit-con" class="webEdit-box webEdit-con">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
		})		
		service(name,nameA.status);
		$(".webEdit-menu p").click(function(){
			//var i = $(this).index();
			$(this).addClass("active").siblings().removeClass("active");
		})
	})
}
//phpmyadmin切换php版本
function phpVer(name,version){
	$.post('/site?action=GetPHPVersion',function(rdata){
		var body = "<div class='ver'><span style='margin-right:10px'>选择PHP版本</span><select id='get' name='phpVersion' style='width:110px'>";
		var optionSelect = '';
		for(var i=0;i<rdata.length;i++){
			optionSelect = rdata[i].version == version?'selected':'';
			body += "<option value='"+ rdata[i].version +"' "+ optionSelect +">"+ rdata[i].name +"</option>"
		}
		body += '</select></div><button class="btn btn-success btn-sm" style="margin-top:10px;" onclick="phpVerChange(\'phpversion\',\'get\')">保存</button>';
		$(".soft-man-con").html(body);
	})
}
function phpVerChange(type,msg){
	var data = type + '=' + $("#" + msg).val();
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status){
			setTimeout(function(){
				window.location.reload();
			},3000);
		}
	})
}
//phpmyadmin安全设置
function safeConf(name,port,auth){
	var con = '<div class="ver">\
						<span style="margin-right:10px">访问端口</span>\
						<input class="form-control phpmyadmindk" name="Name" id="pmport" value="'+port+'" placeholder="phpmyadmin访问端口" maxlength="5" type="number">\
						<button class="btn btn-success btn-sm" onclick="phpmyadminport()">保存</button>\
					</div>\
					<div class="user_pw_tit">\
						<span class="tit">密码访问</span>\
						<span class="btswitch-p"><input class="btswitch btswitch-ios" id="phpmyadminsafe" type="checkbox" '+(auth?'checked':'')+'>\
						<label class="btswitch-btn phpmyadmin-btn" for="phpmyadminsafe" onclick="phpmyadminSafe()"></label>\
						</span>\
					</div>\
					<div class="user_pw">\
						<p><span>授权账号</span><input id="username_get" name="username_get" value="" type="text" placeholder="不修改请留空"></p>\
						<p><span>授权密码</span><input id="password_get_1" name="password_get_1" value="" type="password" placeholder="不修改请留空"></p>\
						<p><span>重复密码</span><input id="password_get_2" name="password_get_1" value="" type="password" placeholder="不修改请留空"></p>\
						<p><button class="btn btn-success btn-sm" onclick="phpmyadmin(\'get\')">保存</button></p>\
					</div>';
	$(".soft-man-con").html(con);
	if(auth){
		$(".user_pw").show();
	}
}


//修改phpmyadmin端口
function phpmyadminport(){
	var pmport = $("#pmport").val();
	if(pmport < 80 || pmport > 65535){
		layer.msg('端口范围不合法，请重新输入!',{icon:2});
		return;
	}
	var data = 'port=' + pmport;
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}
//phpmyadmin二级密码
function phpmyadminSafe(){
	var stat = $("#phpmyadminsafe").prop("checked");
	if(stat) {
		$(".user_pw").hide();
		phpmyadmin('close');
	}else{
		 $(".user_pw").show();
	}
	
}


//设置phpmyadmin二级密码
function phpmyadmin(msg){
	type = 'password';
	if(msg == 'close'){
		password_1 = msg;
		username = msg;
		layer.confirm('您真的要关闭访问认证吗?',{closeBtn:2,icon:3},function(){
			var data = type + '=' + msg + '&siteName=phpmyadmin';
			var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0});
			$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
				layer.close(loadT);
				layer.msg(rdata.msg,{icon:rdata.status?1:5});
			});
		});
		return;
	}else{
		username = $("#username_get").val()
		password_1 = $("#password_get_1").val()
		password_2 = $("#password_get_2").val()
		if(username.length < 1 || password_1.length < 1){
			layer.msg('授权用户或密码不能为空!',{icon:5});
			return;
		}
		if(password_1 != password_2){
			layer.msg('两次输入的密码不一致，请重新输入!',{icon:5});
			return;
		}
	}
	msg = password_1 + '&username='+username + '&siteName=phpmyadmin';
	var data = type + '=' + msg;
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
	});
}
