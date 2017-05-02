//软件管理
function phpSoftMain(name,key){
	if(!isNaN(name)){
		var nametext = "php"+name;
		name = name.replace(".","");
	}
	
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/plugin?action=getPluginInfo&name=php',function(rdata){
		layer.close(loadT);
		nameA = rdata.versions[key];
		bodys = [
				'<p class="active" data-id="0"><a href="javascript:service(\''+name+'\','+nameA.run+')">php服务</a><span class="spanmove"></span></p>',
				'<p data-id="1"><a href="javascript:phpUploadLimit(\''+name+'\','+nameA.max+')">上传限制</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="2"><a href="javascript:phpTimeLimit(\''+name+'\','+nameA.maxTime+')">超时限制</a><span class="spanmove"></span></p>',
				'<p data-id="3"><a href="javascript:configChange(\''+name+'\')">配置修改</a><span class="spanmove"></span></p>',
				'<p data-id="4"><a href="javascript:SetPHPConfig(\''+name+'\','+nameA.pathinfo+')">扩展配置</a><span class="spanmove"></span></p>',
				'<p data-id="5"><a href="javascript:disFun(\''+name+'\')">禁用函数</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="6"><a href="javascript:SetFpmConfig(\''+name+'\')">性能调整</a><span class="spanmove"></span></p>',
				'<p class="phphide" data-id="7"><a href="javascript:GetPHPStatus(\''+name+'\')">负载状态</a><span class="spanmove"></span></p>',
				'<p data-id="8"><a href="javascript:BtPhpinfo(\''+name+'\')">phpinfo</a><span class="spanmove"></span></p>'
		]
		
		var sdata = '';
		if(rdata.phpSort == false){
			rdata.phpSort = [0,1,2,3,4,5,6,7,8];
		}else{
			rdata.phpSort = rdata.phpSort.split('|');
		}
		for(var i=0;i<rdata.phpSort.length;i++){
			sdata += bodys[rdata.phpSort[i]];
		}
		
		layer.open({
			type: 1,
			area: '640px',
			title: nametext+'管理',
			closeBtn: 2,
			shift: 0,
			content: '<div class="webEdit" style="width:640px;">\
				<input name="softMenuSortOrder" type="hidden" />\
				<div class="webEdit-menu  soft-man-menu">\
					'+sdata+'\
				</div>\
				<div id="webEdit-con" class="webEdit-box webEdit-con">\
					<div class="soft-man-con"></div>\
				</div>\
			</div>'
		})
		if(name== "52"){
			$(".phphide").hide();
		}
		service(name,nameA.run);
		$(".webEdit-menu p a").click(function(){
			var txt = $(this).text();
			$(this).parent().addClass("active").siblings().removeClass("active");
			if(txt != "扩展配置") $(".soft-man-con").removeAttr("style");
		});
		$(".soft-man-menu").dragsort({dragSelector: ".spanmove", dragEnd: MenusaveOrder});
	});
}

function MenusaveOrder() {
	var data = $(".soft-man-menu > p").map(function() { return $(this).attr("data-id"); }).get();
	var ssort = data.join("|");
	$("input[name=softMenuSortOrder]").val(ssort);
	$.post('/ajax?action=phpSort','ssort='+ssort,function(){});
};
//服务
function service(name,status){
	if(status == 'false') status = false;
	if(status == 'true') status = true;
	
	var serviceCon ='<p class="status">当前状态：<span>'+(status?'开启':'关闭')+'</span><span style="color: '+(status?'#20a53a;':'red;')+' margin-left: 3px;" class="glyphicon '+(status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p>\
					<div class="sfm-opt">\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\''+(status?'stop':'start')+'\')">'+(status?'停止':'启动')+'</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'restart\')">重启</button>\
						<button class="btn btn-default btn-sm" onclick="ServiceAdmin(\''+name+'\',\'reload\')">重载配置</button>\
					</div>'; 
	$(".soft-man-con").html(serviceCon);
}


//更新软件列表
function updateSoftList(){
	loadT = layer.msg('正在从云端获取数据，请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/plugin?action=getCloudPlugin',function(rdata){
		layer.close(loadT);
		GetSList();
		layer.msg(rdata.msg,{icon:rdata.status?1:1});
	});
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
	var loadT = layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
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
	var con = '<p style="color: #666; margin-bottom: 7px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换</p><textarea style="height: 320px; line-height:18px;" id="textBody"></textarea>\
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
		case 'tomcat':
			fileName = '/www/server/tomcat/conf/server.xml';
			break;
		default:
			fileName = '/www/server/php/'+type+'/etc/php.ini';
			break;
	}
	var loadT = layer.msg("读取中...",{icon:16,time:0,shade: [0.3, '#000']});
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
function SetPHPConfig(version,pathinfo,go){
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
				opt = '<a style="color:red;" href="javascript:UninstallPHPLib(\''+version+'\',\''+rdata.libs[i].name+'\',\''+rdata.libs[i].title+'\');">卸载</a>'
			}else{
				opt = '<a class="link" href="javascript:InstallPHPLib(\''+version+'\',\''+rdata.libs[i].name+'\',\''+rdata.libs[i].title+'\');">安装</a>'
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
	
	if(go == undefined){
		sindex = setInterval(function(){
			if($(".active a").html() != '扩展配置'){
				clearInterval(sindex);
				return;
			}
			SetPHPConfig(version,pathinfo,true)
		},5000);
	}
	
}

//安装扩展
function InstallPHPLib(version,name,title){
	layer.confirm('您真的要安装['+name+']吗?',{closeBtn:2},function(){
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
function UninstallPHPLib(version,name,title){
	layer.confirm('您真的要卸载['+name+']吗?',{closeBtn:2},function(){
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
		var disable_functions = rdata.disable_functions.split(',');
		var dbody = ''
		for(var i=0;i<disable_functions.length;i++){
			dbody += "<tr><td>"+disable_functions[i]+"</td><td><a style='float:right;' href=\"javascript:disable_functions('"+version+"','"+disable_functions[i]+"','"+rdata.disable_functions+"');\">删除</a></td></tr>";
		}
		
		var con = "<div class='dirBinding'>"
				   +"<input type='text' placeholder='添加要被禁止的函数名,如: exec' id='disable_function_val' style='height: 28px; border-radius: 3px;width: 410px;' />"
				   +"<button class='btn btn-success btn-sm' onclick=\"disable_functions('"+version+"',1,'"+rdata.disable_functions+"')\">添加</button>"
				   +"</div>"
				   +"<div class='divtable' style='width:96%;margin:6px auto;height:350px;overflow:auto'><table class='table table-hover' width='100%' style='margin-bottom:0'>"
				   +"<thead><tr><th>函数名</th><th width='100' class='text-right'>操作</th></tr></thead>"
				   +"<tbody id='blacktable'>" + dbody + "</tbody>"
				   +"</table></div>"
		
		con +='\
		<ul class="help-info-text">\
			<li>在此处可以禁用指定函数的调用,以增强环境安全性!</li>\
			<li>强烈建议禁用如exec,system等危险函数!</li>\
		</ul>';
		
		$(".soft-man-con").html(con);
	});
}
//设置禁用函数
function disable_functions(version,act,fs){
	var fsArr = fs.split(',');
	if(act == 1){
		var functions = $("#disable_function_val").val();
		for(var i=0;i<fsArr.length;i++){
			if(functions == fsArr[i]){
				layer.msg("您要输入的函数已被禁用!",{icon:5});
				return;
			}
		}
		fs += ',' + functions;	
		msg = '添加成功!';
	}else{
		
		fs = '';
		for(var i=0;i<fsArr.length;i++){
			if(act == fsArr[i]) continue;
			fs += fsArr[i] + ','
		}
		msg = '删除成功!';
		fs = fs.substr(0,fs.length -1);
	}

	var data = 'version='+version+'&disable_functions='+fs;
	var loadT = layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPHPDisable',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.status?msg:rdata.msg,{icon:rdata.status?1:2});
		disFun(version);
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
function nginxSoftMain(name,version){
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/system?action=GetConcifInfo',function(rdata){
		layer.close(loadT);
		nameA = rdata['web'];
		var status = name=='nginx'?'<p onclick="GetNginxStatus()">负载状态</p>':'';
		var menu = '';
		if(version != undefined || version !=''){
			var menu = '<p onclick="softChangeVer(\''+name+'\',\''+version+'\')">切换版本</p>';
		}
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
					<p onclick="waf()">WAF防火墙</p>\
					'+menu+'\
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

//WAF防火墙
function waf(){
	var loadT = layer.msg('正在获取,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get("/waf?action=GetConfig",function(rdata){
		layer.close(loadT);
		if(rdata.status == -1){
			layer.msg('您当前Nginx版本不支持waf模块,请重新安装Nginx,重装Nginx不会丢失您的网站配置!',{icon:5,time:5000});
			return;
		}
		
		var whiteList = ""
		for(var i=0;i<rdata.ipWhitelist.length;i++){
			if(rdata.ipWhitelist[i] == "") continue;
			whiteList += "<tr><td>"+rdata.ipWhitelist[i]+"</td><td><a href=\"javascript:deleteWafKey('ipWhitelist','"+rdata.ipWhitelist[i]+"');\">删除</a></td></tr>";
		}
		
		var blackList = ""
		for(var i=0;i<rdata.ipBlocklist.length;i++){
			if(rdata.ipBlocklist[i] == "") continue;
			blackList += "<tr><td>"+rdata.ipBlocklist[i]+"</td><td><a href=\"javascript:deleteWafKey('ipBlocklist','"+rdata.ipBlocklist[i]+"');\">删除</a></td></tr>";
		}
				
		var cc = rdata.CCrate.split('/')
		
		var con = "<div class='wafConf'>\
					<div class='wafConf-btn'>\
						<span>防火墙</span><div class='ssh-item'>\
                            <input class='btswitch btswitch-ios' id='closeWaf' type='checkbox' "+(rdata.status == 1?'checked':'')+">\
                            <label class='btswitch-btn' for='closeWaf' onclick='CloseWaf()'></label>\
                    	</div>\
						<div class='pull-right'>\
                    	<button class='btn btn-default btn-sm' onclick='gzEdit()'>规则编辑</button>\
                    	<button class='btn btn-default btn-sm' onclick='upLimit()'>上传限制</button>\
						</div>\
					</div>\
					<div class='wafConf_checkbox'>\
					<input type='checkbox' id='waf_UrlDeny' "+(rdata['UrlDeny'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('UrlDeny','"+(rdata['UrlDeny'] == 'on'?'off':'on')+"')\" /><label for='waf_UrlDeny'>URL过滤</label>\
					<input type='checkbox' id='waf_CookieMatch' "+(rdata['CookieMatch'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('CookieMatch','"+(rdata['CookieMatch'] == 'on'?'off':'on')+"')\" /><label for='waf_CookieMatch'>Cookie过滤</label>\
					<input type='checkbox' id='waf_postMatch' "+(rdata['postMatch'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('postMatch','"+(rdata['postMatch'] == 'on'?'off':'on')+"')\" /><label for='waf_postMatch'>POST过滤</label>\
					<input type='checkbox' id='waf_CCDeny' "+(rdata['CCDeny'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('CCDeny','"+(rdata['CCDeny'] == 'on'?'off':'on')+"')\" /><label for='waf_CCDeny'>防CC攻击</label>\
					<input type='checkbox' id='waf_attacklog' "+(rdata['attacklog'] == 'on'?'checked':'')+" onclick=\"SetWafConfig('attacklog','"+(rdata['attacklog'] == 'on'?'off':'on')+"')\" /><label for='waf_attacklog'>记录防御信息</label>\
					</div>\
					<div class='wafConf_cc'>\
					<span>CC攻击触发频率(次)</span><input id='CCrate_1' type='number' value='" + cc[0] + "' style='width:80px;margin-right:30px'/>\
					<span>CC攻击触发周期(秒)</span><input id='CCrate_2' type='number' value='" + cc[1] + "' style='width:80px;'/>\
					<button onclick=\"SetWafConfig('CCrate','')\" class='btn btn-default btn-sm'>确定</button>\
					</div>\
					<div class='wafConf_ip'>\
						<fieldset>\
						<legend>IP白名单</legend>\
						<input type='text' id='ipWhitelist_val' placeholder='IP地址' style='width:175px;' /><button onclick=\"addWafKey('ipWhitelist')\" class='btn btn-default btn-sm'>添加</button>\
						<div class='table-overflow'><table class='table table-hover'>"+whiteList+"</table></div>\
						</fieldset>\
						<fieldset>\
						<legend>IP黑名单</legend>\
						<input type='text' id='ipBlocklist_val' placeholder='IP地址' style='width:175px;' /><button onclick=\"addWafKey('ipBlocklist')\" class='btn btn-default btn-sm'>添加</button>\
						<div class='table-overflow'><table class='table table-hover'>"+blackList+"</table></div>\
						</fieldset>\
					</div>\
				</div>"
		$(".soft-man-con").html(con);
	});
}

//上传限制
function upLimit(){
	var loadT = layer.msg('正在获取,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get("/waf?action=GetConfig",function(rdata){
		layer.close(loadT);
		var black_fileExt = ''
		for(var i=0;i<rdata.black_fileExt.length;i++){
			black_fileExt += "<tr><td>"+rdata.black_fileExt[i]+"</td><td><a style='float:right;' href=\"javascript:deleteWafKey('black_fileExt','"+rdata.black_fileExt[i]+"');\">删除</a></td></tr>";
		}
		
		if($("#blacktable").html() != undefined){
			$("#blacktable").html(black_fileExt);
			$("#black_fileExt_val").val('');
			return;
		}
		
		layer.open({
			type: 1,
			area: '300px',
			title: '文件上传后缀黑名单',
			closeBtn: 2,
			shift: 0,
			content:"<div class='dirBinding'>"
				   +"<input type='text' placeholder='添加禁止上传的扩展名,如: zip' id='black_fileExt_val' style='height: 28px; border-radius: 3px;width: 221px;' />"
				   +"<button class='btn btn-success btn-sm' onclick=\"addWafKey('black_fileExt')\">添加</button>"
				   +"</div>"
				   +"<div class='divtable' style='width:96%;margin:6px auto'><table class='table table-hover' width='100%' style='margin-bottom:0'>"
				   +"<thead><tr><th>扩展名</th><th width='100' class='text-right'>操作</th></tr></thead>"
				   +"<tbody id='blacktable'>" + black_fileExt + "</tbody>"
				   +"</table></div>"
		});
	});
}

//设置waf状态
function CloseWaf(){
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetStatus','',function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
	});
}

//取规则文件 
function GetWafFile(name){
	OnlineEditFile(0,'/www/server/panel/vhost/wafconf/' + name);
}
//规则编辑
function gzEdit(){
	layer.open({
		type: 1,
		area: '360px',
		title: '规则编辑',
		closeBtn: 2,
		shift: 0,
		content:"<div class='gzEdit'><button class='btn btn-default btn-sm' onclick=\"GetWafFile('cookie')\">Cookie</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('post')\">POST</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('url')\">URL</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('user-agent')\">User-Agent</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('args')\">Args</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('whiteurl')\">URL白名单</button>\
				<button class='btn btn-default btn-sm' onclick=\"GetWafFile('returnhtml')\">警告内容</button>\
				<button class='btn btn-default btn-sm' onclick=\"updateWaf('returnhtml')\">从云端更新</button></div>"
	});
}

//更新WAF规则
function updateWaf(){
	var loadT = layer.msg('正在更新规则文件,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=updateWaf','',function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
	});
}

//设置WAF配置值
function SetWafConfig(name,value){
	if(name == 'CCrate'){
		value = $("#CCrate_1").val() + '/' + $("#CCrate_2").val();
	}
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetConfigString','name='+name+'&value='+value,function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
		
	});
}


//删除WAF指定值
function deleteWafKey(name,value){
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetConfigList&act=del','name='+name+'&value='+value,function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
		if(name == 'black_fileExt') upLimit();
	});
}

//删除WAF指定值
function addWafKey(name){
	var value = $('#'+name+'_val').val();
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/waf?action=SetConfigList&act=add','name='+name+'&value='+value,function(rdata){
		layer.close(loadT)
		layer.msg(rdata.msg,{icon:rdata.status?1:5});
		if(rdata.status) waf();
		if(name == 'black_fileExt') upLimit();
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
function SoftMan(name,version){
	switch(name){
		case 'nginx':
			nginxSoftMain(name,version);
			return;
			break;
		case 'apache':
			nginxSoftMain(name,version);
			return;
			break;
		case 'mysql':
			name='mysqld';
			break;
	}
	var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/system?action=GetConcifInfo',function(rdata){
		layer.close(loadT);
		var nameA = rdata[name.replace('mysqld','mysql')];
		var menu = '<p onclick="configChange(\''+name+'\')">配置修改</p><p onclick="softChangeVer(\''+name+'\',\''+version+'\')">切换版本</p>';
		if(name == "phpmyadmin"){
			menu = '<p onclick="phpVer(\''+name+'\',\''+nameA.phpversion+'\')">php版本</p><p onclick="safeConf(\''+name+'\','+nameA.port+','+nameA.auth+')">安全设置</p>';
		}
		if(version == undefined || version == ''){
			var menu = '<p onclick="configChange(\''+name+'\')">配置修改</p>';
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
//软件切换版本
function softChangeVer(name,version){
	if(name == "mysqld") name = "mysql";
	var veropt = version.split("|");
	var SelectVersion = '';
	for(var i=0; i<veropt.length; i++){
		SelectVersion += '<option>'+name+' '+veropt[i]+'</option>';
	}
	var body = "<div class='ver'><span style='margin-right:10px'>选择版本</span><select id='selectVer' name='phpVersion' style='width:160px'>";
	body += SelectVersion+'</select></div><button class="btn btn-success btn-sm" style="margin-top:10px;">切换</button>';
	$(".soft-man-con").html(body);
	$(".btn-success").click(function(){
		var ver = $("#selectVer").val();
		oneInstall(name,ver.split(" ")[1]);
	});
	selectChange();
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
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
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
					</div>\
					<ul class="help-info-text"><li>为phpmyadmin增加一道访问安全锁</li></ul>';
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
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
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
			var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
			$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
				layer.close(loadT);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
			});
		});
		return;
	}else{
		username = $("#username_get").val()
		password_1 = $("#password_get_1").val()
		password_2 = $("#password_get_2").val()
		if(username.length < 1 || password_1.length < 1){
			layer.msg('授权用户或密码不能为空!',{icon:2});
			return;
		}
		if(password_1 != password_2){
			layer.msg('两次输入的密码不一致，请重新输入!',{icon:2});
			return;
		}
	}
	msg = password_1 + '&username='+username + '&siteName=phpmyadmin';
	var data = type + '=' + msg;
	var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=setPHPMyAdmin',data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}
//首页软件列表
function indexsoft(){
	var loadT = layer.msg('正在获取列表...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/plugin?action=getPluginList','',function(rdata){
		layer.close(loadT);
		var con = '';
		for(var i=0;i<rdata.length - 1;i++){
			var len = rdata[i].versions.length;
			var version_info = '';
			for(var j=0;j<len;j++){
              	if(rdata[i].versions[j].status) continue;
             	version_info += rdata[i].versions[j].version + '|';
            }
          	if(version_info != ''){
             	 version_info = version_info.substring(0,version_info.length-1);
            }
			if(rdata[i].status == 1){
				var isDisplay = false;
				if(rdata[i].name != 'php'){
					for(var n=0; n<len; n++){
						if(rdata[i].versions[n].status == true){
							isDisplay = true;
							var version = rdata[i].versions[n].version;
							if(rdata[i].versions[n].run == true){
								state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
							}
							else{
								state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
							}
						}
					}
					if(isDisplay){
						var clickName = 'SoftMan';
						if(rdata[i].tip == 'lib') clickName = 'PluginMan';
						
						con += '<div class="col-sm-3 col-md-3 col-lg-3" data-id="'+rdata[i].pid+'">\
									<span class="spanmove"></span>\
									<div onclick="' + clickName + '(\''+rdata[i].name+'\',\''+version_info+'\')">\
									<div class="image"><img src="/static/img/soft_ico/ico-'+rdata[i].name+'.png"></div>\
									<div class="sname">'+rdata[i].title+' '+version+state+'</div>\
									</div>\
								</div>'
					}
				}
				else{
					for(var n=0; n<len; n++){
						if(rdata[i].versions[n].status == true){
							var version = rdata[i].versions[n].version;
							if(rdata[i].versions[n].run == true){
								state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
							}
							else{
								state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
							}
						}
						if(rdata[i].versions[n].display == true ){
							con += '<div class="col-sm-3 col-md-3 col-lg-3" data-id="'+rdata[i].pid+'">\
								<span class="spanmove"></span>\
								<div onclick="phpSoftMain(\''+rdata[i].versions[n].version+'\','+n+')">\
								<div class="image"><img src="/static/img/soft_ico/ico-'+rdata[i].name+'.png"></div>\
								<div class="sname">'+rdata[i].title+' '+rdata[i].versions[n].version+state+'</div>\
								</div>\
							</div>'
						}
					}
				}
			}
		}
		$("#indexsoft").html(con);
		//软件位置移动
		var softboxlen = $("#indexsoft > div").length;
		var softboxsum = 12;
		var softboxcon = '';
		var softboxn =softboxlen;
		if(softboxlen <= softboxsum){
			for(var i=0;i<softboxsum-softboxlen;i++){
				softboxn +=1000;
				softboxcon +='<div class="col-sm-3 col-md-3 col-lg-3 no-bg" data-id="'+softboxn+'"></div>'
			}
			$("#indexsoft").append(softboxcon);
		}
		$("#indexsoft").dragsort({ dragSelector: ".spanmove", dragBetween: true, dragEnd: saveOrder, placeHolderTemplate: "<div class='col-sm-3 col-md-3 col-lg-3 dashed-border'></div>" });

		function saveOrder() {
			var data = $("#indexsoft > div").map(function() { return $(this).attr("data-id"); }).get();
			var ssort = data.join("|");
			$("input[name=list1SortOrder]").val(ssort);
			$.post("/plugin?action=savePluginSort",'ssort=' + ssort,function(rdata){});
		};
	})
}

//插件设置菜单
function PluginMan(name,title){
	loadT = layer.msg('正在获取模板...',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/plugin?action=getConfigHtml&name=' + name,function(rhtml){
		layer.close(loadT);
		if(rhtml.status === false){
			if(name == "phpguard"){
				layer.msg("php守护已启动，无需设置",{icon:1})
			}
			else{
				layer.msg(rhtml.msg,{icon:2});
			}
			return;
		}
		layer.open({
			type: 1,
			shift: 5,
			closeBtn: 2,
			area: '700px', //宽高
			title: '配置'+ title,
			content: rhtml
		});
		rcode = rhtml.split('<script type="javascript/text">')[1].replace('</script>','');
		setTimeout(function(){
			if(!!(window.attachEvent && !window.opera)){ 
				execScript(rcode); 
			}else{
				window.eval(rcode);
			}
		},200)
		
	});
}


//设置插件
function SetPluginConfig(name,param,def){
	if(def == undefined) def = 'SetConfig';
	loadT = layer.msg('正在保存配置...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/plugin?action=a&name='+name+'&s=' + def,param,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//取七牛文件列表
function GetFileList(name){
	var loadT = layer.msg('正在从云端获取...',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=GetQiniuFileList&name='+name,function(rdata){
		layer.close(loadT);
		if(rdata.status === false){
			layer.msg(rdata.msg,{icon:2});
			return;
		}
		
		var tBody = ''
		for(var i=0;i<rdata.length;i++){
			tBody += "<tr>\
						<td>"+rdata[i].key+"</td>\
						<td>"+rdata[i].mimeType+"</td>\
						<td>"+ToSize(rdata[i].fsize)+"</td>\
						<td>"+getLocalTime(rdata[i].putTime)+"</td>\
					</tr>"
		}
		
		layer.open({
			type: 1,
			skin: 'demo-class',
			area: '700px',
			title: '文件列表',
			closeBtn: 2,
			shift: 0,
			content: "<div class='divtable' style='margin:17px'>\
						<table width='100%' class='table table-hover'>\
							<thead>\
								<tr>\
									<th>名称</th>\
									<th>类型</th>\
									<th>大小</th>\
									<th>更新时间</th>\
								</tr>\
							</thead>\
							<tbody class='list-list'>"+tBody+"</tbody>\
						</table>\
					</div>"
		});
	});
}

//取软件列表
function GetSList(isdisplay){
	if(isdisplay == undefined){
		var loadT = layer.msg('正在获取列表...',{icon:16,time:0,shade: [0.3, '#000']})
	}
	$.post('/plugin?action=getPluginList','',function(rdata){
		layer.close(loadT);
		var sBody = '';
		var pBody = '';
		$(".task").text(rdata[rdata.length - 1]);
		for(var i=0;i<rdata.length - 1;i++){
			var len = rdata[i].versions.length;
          	var version_info = '';
			var version = '';
			var softPath ='';
			var titleClick = '';
			var state = '';
			var indexshow = '';
			var checked = '';
			checked = rdata[i].status==0 ? '':'checked';
          	for(var j=0;j<len;j++){
              	if(rdata[i].versions[j].status) continue;
             	version_info += rdata[i].versions[j].version + '|';
            }
          	if(version_info != ''){
             	 version_info = version_info.substring(0,version_info.length-1);
            }
			
			var handle = '<a class="link" onclick="AddVersion(\''+rdata[i].name+'\',\''+version_info+'\',\''+rdata[i].tip+'\',this,\''+rdata[i].title+'\')">安装</a>';
			if(rdata[i].name != 'php'){
				for(var n=0; n<len; n++){
					if(rdata[i].versions[n].status == true){
						if(rdata[i].tip == 'lib'){
							handle = '<a class="link" onclick="PluginMan(\''+rdata[i].name+'\',\''+rdata[i].title+'\')">设置</a> | <a class="link" onclick="UninstallVersion(\''+rdata[i].name+'\',\''+rdata[i].versions[n].version+'\',\''+rdata[i].title+'\')">卸载</a>';
							titleClick = 'onclick="PluginMan(\''+rdata[i].name+'\',\''+rdata[i].title+'\')" style="cursor:pointer"';
						}else{
							handle = '<a class="link" onclick="SoftMan(\''+rdata[i].name+'\',\''+version_info+'\')">设置</a> | <a class="link" onclick="UninstallVersion(\''+rdata[i].name+'\',\''+rdata[i].versions[n].version+'\',\''+rdata[i].title+'\')">卸载</a>';
							titleClick = 'onclick="SoftMan(\''+rdata[i].name+'\',\''+version_info+'\')" style="cursor:pointer"';
						}
						
						version = rdata[i].versions[n].version;
						softPath = '<span class="glyphicon glyphicon-folder-open" title="'+rdata[i].path+'" onclick="openPath(\''+rdata[i].path+'\')"></span>';
						indexshow = '<div class="index-item"><input class="btswitch btswitch-ios" id="index_'+rdata[i].name+'" type="checkbox" '+checked+'><label class="btswitch-btn" for="index_'+rdata[i].name+'" onclick="toIndexDisplay(\''+rdata[i].name+'\',\''+version+'\')"></label></div>';
						if(rdata[i].versions[n].run == true){
							state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
						}
						else{
							state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
						}
					}
					var isTask = rdata[i].versions[n].task;
					if(isTask == '-1'){
						handle = '<a style="color:green;" href="javascript:task();">正在安装..</a>'
					}else if(isTask == '0'){
						handle = '<a style="color:#C0C0C0;" href="javascript:task();">等待安装..</a>'
					}
				}
				sBody += '<tr>'
						+'<td><span '+titleClick+'><img src="/static/img/soft_ico/ico-'+rdata[i].name+'.png">'+rdata[i].title+' '+version+'</span></td>'
						+'<td>'+rdata[i].type+'</td>'
						+'<td>'+rdata[i].ps+'</td>'
						+'<td>'+softPath+'</td>'
						+'<td>'+state+'</td>'
						+'<td>'+indexshow+'</td>'
						+'<td style="text-align: right;">'+handle+'</td>'
					+'</tr>'
			}
			else{
				for(var n=0; n<len; n++){
					if(rdata[i].versions[n].status == true){
						checked = rdata[i].versions[n]['display'] ? "checked":"";
						handle = '<a class="link" onclick="phpSoftMain(\''+rdata[i].versions[n].version+'\','+n+')">设置</a> | <a class="link" onclick="UninstallVersion(\''+rdata[i].name+'\',\''+rdata[i].versions[n].version+'\',\''+rdata[i].title+'\')">卸载</a>';
						softPath = '<span class="glyphicon glyphicon-folder-open" title="'+rdata[i].path+'" onclick="openPath(\''+rdata[i].path+"/"+rdata[i].versions[n].version.replace(/\./,"")+'\')"></span>';
						titleClick = 'onclick="phpSoftMain(\''+rdata[i].versions[n].version+'\','+n+')" style="cursor:pointer"';
						indexshow = '<div class="index-item"><input class="btswitch btswitch-ios" id="index_'+rdata[i].name+rdata[i].versions[n].version.replace(/\./,"")+'" type="checkbox" '+checked+'><label class="btswitch-btn" for="index_'+rdata[i].name+rdata[i].versions[n].version.replace(/\./,"")+'" onclick="toIndexDisplay(\''+rdata[i].name+'\',\''+rdata[i].versions[n].version+'\')"></label></div>';
						if(rdata[i].versions[n].run == true){
							state='<span style="color:#20a53a" class="glyphicon glyphicon-play"></span>'
						}
						else{
							state='<span style="color:red" class="glyphicon glyphicon-pause"></span>'
						}
						
					}
					else{
						handle = '<a class="link" onclick="oneInstall(\''+rdata[i].name+'\',\''+rdata[i].versions[n].version+'\')">安装</a>';
						softPath ='';
						checked = '';
						indexshow = '';
						titleClick ='';
						state = '';
					}
					var isTask = rdata[i].versions[n].task;
					if(isTask == '-1'){
						handle = '<a style="color:green;" href="javascript:task();">正在安装..</a>'
					}else if(isTask == '0'){
						handle = '<a style="color:#C0C0C0;" href="javascript:task();">等待安装..</a>'
					}
					pBody += '<tr>'
							+'<td><span '+titleClick+'><img src="/static/img/soft_ico/ico-'+rdata[i].name+'.png">'+rdata[i].title+'-'+rdata[i].versions[n].version+'</span></td>'
							+'<td>'+rdata[i].type+'</td>'
							+'<td>'+rdata[i].ps+'</td>'
							+'<td>'+softPath+'</td>'
							+'<td>'+state+'</td>'
							+'<td>'+indexshow+'</td>'
							+'<td style="text-align: right;">'+handle+'</td>'
						+'</tr>'
				}
			}
		}
		sBody += pBody;
		$("#softList").html(sBody);
	})
}

//独立安装
function oneInstall(name,version){
	if (name == 'pure') name += '-'+version.toLowerCase();
	
	if (name == 'apache' || name == 'nginx'){
		var isError = false
		$.ajax({
			url:'/ajax?action=GetInstalled',
			type:'get',
			async:false,
			success:function(rdata){
				if(rdata.webserver != name && rdata.webserver != false){
					layer.msg('请先卸载Nginx',{icon:2})
					isError = true;
					return;
				}
			}
		});
	}
	
	if(getCookie('serverType') == 'apache' && name == 'php' && version == '5.2'){
		layer.msg("抱歉,Apache2.4不支持PHP-5.2!",{icon:5});
		return;
	}
	
	
	if (isError) return;
	var one = layer.open({
		type: 1,
	    title: '选择安装方式',
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='zun-form-new'>\
			<div class='version'>安装版本：<span style='margin-left:30px'>"+name+" "+version+"</span></div>\
	    	<div class='fangshi'>安装方式：<label data-title='即rpm，安装时间极快（5~10分钟），性能与稳定性略低于编译安装'>极速安装<input type='checkbox' checked></label><label data-title='安装时间长（30分钟到3小时），适合高并发高性能应用'>编译安装<input type='checkbox'></label></div>\
	    	<div class='submit-btn' style='margin-top:15px'>\
				<button type='button' class='btn btn-danger btn-sm btn-title one-close'>取消</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>提交</button>\
	        </div>\
	    </div>"
	})
	$('.fangshi input').click(function(){
		$(this).attr('checked','checked').parent().siblings().find("input").removeAttr('checked');
	});
	$("#bi-btn").click(function(){
		var type = $('.fangshi input').prop("checked") ? '1':'0';
		var data = "name="+name+"&version="+version+"&type="+type;
		var loadT = layer.msg('正在添加到安装器...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/files?action=InstallSoft', data, function(rdata) {
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			GetSList();
		})
		
	});
	$(".one-close").click(function(){
		layer.close(one);
	})
	InstallTips();
	fly("bi-btn");
}

function AddVersion(name,ver,type,obj,title){
	if(type == "lib"){
		layer.confirm('您真的要安装['+title+'-'+ver+']吗?',{closeBtn:2},function(){
			$(obj).text("安装中..");
			var data = "name="+name;
			var loadT = layer.msg('正在安装，请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
			$.post("/plugin?action=install",data,function(rdata){
				layer.close(loadT);
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				setTimeout(function(){GetSList()},2000)
			});
		});
		return;
	}
	
	
	var titlename = name;
	var veropt = ver.split("|");
	var SelectVersion = '';
	for(var i=0; i<veropt.length; i++){
		SelectVersion += '<option>'+name+' '+veropt[i]+'</option>';
	}
	if(name == 'phpmyadmin' || name == 'nginx' || name == 'apache'){
		var isError = false
		$.ajax({
			url:'/ajax?action=GetInstalled',
			type:'get',
			async:false,
			success:function(rdata){
				if(name == 'nginx'){
					if(rdata.webserver != name.toLowerCase() && rdata.webserver != false){
						layer.msg('请先卸载Apache',{icon:2})
						isError = true;
						return;
					}
				}
				if(name == 'apache'){
					if(rdata.webserver != name.toLowerCase() && rdata.webserver != false){
						layer.msg('请先卸载Nginx',{icon:2})
						isError = true;
						return;
					}
				}
				if(name == 'phpmyadmin'){
					if (rdata.php.length < 1){
						layer.msg('请先安装php',{icon:2})
						isError = true;
						return;
					}
					if (!rdata.mysql.setup){
						layer.msg('请先安装MySQL',{icon:2})
						isError = true;
						return;
					}
					
				}
			}
		});
		if(isError) return;
	}
	
	layer.open({
		type: 1,
	    title: titlename+"软件安装",
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='zun-form-new'>\
			<div class='version'>安装版本：<select id='SelectVersion'>"+SelectVersion+"</select></div>\
	    	<div class='fangshi'>安装方式：<label data-title='即rpm，安装时间极快（5~10分钟），性能与稳定性略低于编译安装'>极速安装<input type='checkbox' checked></label><label data-title='安装时间长（30分钟到3小时），适合高并发高性能应用'>编译安装<input type='checkbox'></label></div>\
	    	<div class='submit-btn' style='margin-top:15px'>\
				<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
		        <button type='button' id='bi-btn' class='btn btn-success btn-sm btn-title bi-btn'>提交</button>\
	        </div>\
	    </div>"
	})
	selectChange();
	$('.fangshi input').click(function(){
		$(this).attr('checked','checked').parent().siblings().find("input").removeAttr('checked');
	});
	$("#bi-btn").click(function(){
		var info = $("#SelectVersion").val().toLowerCase();
		var name = info.split(" ")[0];
		var version = info.split(" ")[1];
		var type = $('.fangshi input').prop("checked") ? '1':'0';
		var data = "name="+name+"&version="+version+"&type="+type;

		var loadT = layer.msg('正在添加到安装器...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post("/plugin?action=install",data,function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			GetSList();
		});
	});
	InstallTips();
	fly("bi-btn");
}

function selectChange(){
	$("#SelectVersion,#selectVer").change(function(){
		var info = $(this).val();
		var name = info.split(" ")[0];
		var version = info.split(" ")[1];
		max=64
		msg="64M"
		if(name == 'mysql'){
			memSize = getCookie('memSize');
			switch(version){
				case '5.1':
					max = 256;
					msg = '256M';
					break;
				case '5.7':
					max = 1500;
					msg = '2GB';
					break;
				case '5.6':
					max = 800;
					msg = '1GB';
					break;
				case 'AliSQL':
					max = 800;
					msg = '1GB';
					break;
				case 'mariadb_10.0':
					max = 800;
					msg = '1GB';
					break;
				case 'mariadb_10.1':
					max = 1500;
					msg = '2GB';
					break;
			}
			if(memSize < max){
				layer.msg('您 的内存小于' + msg + '，不建议安装MySQL-' + version,{icon:5});
			}
		}
	});
}


//卸载软件
function UninstallVersion(name,version,title){
	layer.confirm('您真的要卸载['+title+'-'+version+']吗?',{closeBtn:2},function(){
		var data = 'name='+name+'&version='+version;
		var loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/plugin?action=unInstall',data,function(rdata){
			layer.close(loadT)
			GetSList();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		})
	});
}


//获取插件列表
function GetLibList(){
	var loadT = layer.msg('正在获取列表...',{icon:16,time:0,shade: [0.3, '#000']})
	$.post('/ajax?action=GetLibList','',function(rdata){
		layer.close(loadT)
		var tBody = ''
		for(var i=0;i<rdata.length;i++){
			tBody += "<tr>\
						<td>"+rdata[i].name+"</td>\
						<td>"+rdata[i].type+"</td>\
						<td>"+rdata[i].ps+"</td>\
						<td>--</td>\
						<td>"+rdata[i].status+"</td>\
						<td style='text-align: right;'>"+rdata[i].optstr+"</td>\
					</tr>"
		}
		$("#softList").append(tBody);
	});
}


//设置插件
function SetLibConfig(name,action){
	if(action == 1){
		var access_key = $("input[name='access_key']").val();
		var secret_key = $("input[name='secret_key']").val();
		var bucket_name = $("input[name='bucket_name']").val();
		if(access_key.length < 1 || secret_key.length < 1 || bucket_name.length < 1){
			layer.msg('表单错误！',{icon:2});
			return;
		}
		
		var bucket_domain = $("input[name='bucket_domain']").val();
		var data = 'name='+name+'&access_key='+access_key+'&secret_key='+secret_key+'&bucket_name='+bucket_name+'&bucket_domain='+bucket_domain;
		
		var loadT = layer.msg('正在提交...',{icon:16,time:0,shade:[0.3,'#000']});
		$.post('/ajax?action=SetQiniuAS',data,function(rdata){
			layer.close(loadT);
			if(rdata.status) layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		}).error(function(){
			layer.close(loadT);
			layer.msg('操作失败!',{icon:2});
		});
		return;
	}
	
	if(name == 'beta'){
		neice();
		return;
	}
	
	$.post('/ajax?action=GetQiniuAS','name='+name,function(rdata){
		var keyMsg = rdata.info.key.split('|');
		var secretMsg = rdata.info.secret.split('|');
		var bucketMsg = rdata.info.bucket.split('|');
		var domainMsg = rdata.info.domain.split('|');
		
		var body="<div class='zun-form-new bingfa'>"
				+"<p><span class='span_tit'>"+keyMsg[0]+"：</span><input placeholder='"+keyMsg[1]+"' style='width: 300px;' type='text' name='access_key' value='"+rdata.AS[0]+"' />  *"+keyMsg[2]+" "+'<a href="'+rdata.info.help+'" style="color:green" target="_blank"> [帮助]</a>'+"</p>"
				+"<p><span class='span_tit'>"+secretMsg[0]+"：</span><input placeholder='"+secretMsg[1]+"' style='width: 300px;' type='text' name='secret_key' value='"+rdata.AS[1]+"' />  *"+secretMsg[2]+"</p>"
				+"<p><span class='span_tit'>"+bucketMsg[0]+"：</span><input placeholder='"+bucketMsg[1]+"' style='width: 300px;' type='text' name='bucket_name' value='"+rdata.AS[2]+"' />   *"+bucketMsg[2]+"</p>"
				+"<p><span class='span_tit'>"+domainMsg[0]+"：</span><input placeholder='"+domainMsg[1]+"' style='width: 300px;' type='text' name='bucket_domain' value='"+rdata.AS[3]+"' />   *"+domainMsg[2]+"</p>"
			+'<div class="submit-btn">'
				+'<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">取消</button>'
				+'<button type="button" class="btn btn-success btn-sm btn-title" onclick="GetQiniuFileList(\''+name+'\')" style="margin-right: 4px;">列表</button>'
				+"<button class='btn btn-success btn-sm btn-title' onclick=\"SetLibConfig('"+name+"',1)\">保存</button>"
			+'</div>'
		+"</div>"
		
		layer.open({
			type: 1,
			shift: 5,
			closeBtn: 2,
			area: '700px', //宽高
			title: '配置'+rdata.info.name,
			content: body
			});
	});
}


//安装插件
function InstallLib(name){
	layer.confirm('您真的要安装['+name+']插件吗？',{title:'安装插件',closeBtn:2}, function() {
		var loadT = layer.msg('正在安装,请稍候...',{icon:16,time:0,shade:[0.3,'#000']});
		$.post('/ajax?action=InstallLib','name='+name,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			if(rdata.status){
				GetSList();
				SetLibConfig(name);
			}
		});
	});
}

//卸载插件
function UninstallLib(name){
	layer.confirm('您真的要卸载['+name+']插件吗？',{title:'卸载插件',closeBtn:2}, function() {
		var loadT = layer.msg('正在卸载...',{icon:16,time:0,shade:[0.3,'#000']});
		$.post('/ajax?action=UninstallLib','name='+name,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			if(rdata.status){
				GetSList();
			}
		});
	});
}

//首页显示
function toIndexDisplay(name,version){
	var status = $("#index_"+name).prop("checked")?"0":"1";
	if(name == "php"){
		var verinfo = version.replace(/\./,"");
		status = $("#index_"+name+verinfo).prop("checked")?"0":"1";
	}
	var data= "name="+name+"&status="+status+"&version="+version;
	$.post("plugin?action=setPluginStatus",data,function(rdata){
		if(rdata.status){
			layer.msg(rdata.msg,{icon:1})
		}
	})
}


$(function(){
	setInterval(function(){GetSList(true);},5000);
});
