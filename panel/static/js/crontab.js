var num = 0;
//查看任务日志
function GetLogs(id){
	layer.msg('正在获取...',{icon:16,time:0,shade: [0.3, '#000']});
	var data='&id='+id
	$.post('/crontab?action=GetLogs',data,function(rdata){
		layer.closeAll();
		if(!rdata.status) {
			layer.msg(rdata.msg,{icon:2});
			return;
		};
		layer.open({
			type:1,
			title:'任务执行日志',
			area: ['60%','500px'], 
			shadeClose:false,
			closeBtn:2,
			content:'<div class="setchmod bt-form pd20 pb70">'
					+'<pre style="overflow: auto; border: 0px none; padding: 15px; margin: 0px; height: 410px; background-color: rgb(255, 255, 255);">'+rdata.msg+'</pre>'
					+'<div class="bt-form-submit-btn" style="margin-top: 0px;">'
					+'<button type="button" class="btn btn-success btn-sm" onclick="CloseLogs('+id+')">清空</button>'
					+'<button type="button" class="btn btn-danger btn-sm" onclick="layer.closeAll()">关闭</button>'
				    +'</div>'
					+'</div>'
		});
	});
}

function getCronData(){
	var laid=layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/crontab?action=GetCrontab',"",function(rdata){
		layer.close(laid);
		var cbody="";
		if(rdata == ""){
			cbody="<tr><td colspan='5'>当前没有计划任务</td></tr>"
		}
		else{
			for(var i=0;i<rdata.length;i++){
				cbody += "<tr>\
							<td>"+rdata[i].name+"</td>\
							<td>"+rdata[i].type+"</td>\
							<td>"+rdata[i].cycle+"</td>\
							<td>"+rdata[i].addtime+"</td>\
							<td>\
								<a href=\"javascript:StartTask("+rdata[i].id+");\" class='btlink'>执行</a> | \
								<a href=\"javascript:OnlineEditFile(0,'/www/server/cron/"+rdata[i].echo+"');\" class='btlink'>脚本</a> | \
								<a href=\"javascript:GetLogs("+rdata[i].id+");\" class='btlink'>日志</a> | \
								<a href=\"javascript:planDel("+rdata[i].id+" ,'"+rdata[i].name.replace('\\','\\\\')+"');\" class='btlink'>删除</a>\
							</td>\
						</tr>"
			}
		}
		$('#cronbody').html(cbody);
	});
}

//执行任务脚本
function StartTask(id){
	layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
	var data='id='+id;
	$.post('/crontab?action=StartTask',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//清空日志
function CloseLogs(id){
	layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
	var data='id='+id;
	$.post('/crontab?action=DelLogs',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


//删除
function planDel(id,name){
	SafeMessage("删除["+name+"]","您确定要该任务吗?",function(){
			layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
			var data='id='+id;
			$.post('/crontab?action=DelCrontab',data,function(rdata){
				layer.closeAll();
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				getCronData();
			});
	});
}

	
function IsURL(str_url){
	var strRegex = '^(https|http|ftp|rtsp|mms)?://.+';
	var re=new RegExp(strRegex);
	if (re.test(str_url)){
		return (true);
	}else{
		return (false);
	}
}


//提交
function planAdd(){
	var name = $(".planname input[name='name']").val();
	if(name == ''){
		$(".planname input[name='name']").focus();
		layer.msg('任务名称不能为空!',{icon:2});
		return;
	}
	$("#set-Config input[name='name']").val(name);
	
	var type = $(".plancycle").find("b").attr("val");
	$("#set-Config input[name='type']").val(type);
	
	var where1 = $("#ptime input[name='where1']").val();
	var is1;
	var is2 = 1;
	switch(type){
		case 'day-n':
			is1=31;
			break;
		case 'hour-n':
			is1=23;
			break;
		case 'minute-n':
			is1=59;
			break;
		case 'month':
			is1=31;
			break;
		
	}
	
	if(where1 > is1 || where1 < is2){
		$("#ptime input[name='where1']").focus();
		layer.msg('表单不合法,请重新输入!',{icon:2});
		return;
	}
	
	$("#set-Config input[name='where1']").val(where1);
	
	var hour = $("#ptime input[name='hour']").val();
	if(hour > 23 || hour < 0){
		$("#ptime input[name='hour']").focus();
		layer.msg('小时值不合法!',{icon:2});
		return;
	}
	$("#set-Config input[name='hour']").val(hour);
	var minute = $("#ptime input[name='minute']").val();
	if(minute > 59 || minute < 0){
		$("#ptime input[name='minute']").focus();
		layer.msg('分钟值不合法!',{icon:2});
		return;
	}
	$("#set-Config input[name='minute']").val(minute);
	
	var save = $("#save").val();
	
	if(save < 0){
		layer.msg('不能有负数!',{icon:2});
		return;
	}
	
	$("#set-Config input[name='save']").val(save);
	
	
	$("#set-Config input[name='week']").val($(".planweek").find("b").attr("val"));
	var sType = $(".planjs").find("b").attr("val");
	var sBody = encodeURIComponent($("#implement textarea[name='sBody']").val());
	
	if(sType == 'toFile'){
		if($("#viewfile").val() == ''){
			layer.msg('请选择脚本文件!',{icon:2});
			return;
		}
	}else{
		if(sBody == ''){
			$("#implement textarea[name='sBody']").focus();
			layer.msg('脚本代码不能为空!',{icon:2});
			return;
		}
	}
	
	var urladdress = $("#urladdress").val();
	if(sType == 'toUrl'){
		if(!IsURL(urladdress)){
			layer.msg('URL地址不正确!',{icon:2});
			$("implement textarea[name='urladdress']").focus();
			return;
		}
	}
	urladdress = encodeURIComponent(urladdress);
	$("#set-Config input[name='urladdress']").val(urladdress);
	$("#set-Config input[name='sType']").val(sType);
	$("#set-Config textarea[name='sBody']").val(decodeURIComponent(sBody));
	
	var sName = $("#sName").attr("val");
	
	if(sType == 'site' || sType == 'database'){
		var backupTo = $(".planBackupTo").find("b").attr("val");
		$("#backupTo").val(backupTo);
	}
	
	$("#set-Config input[name='sName']").val(sName);
	
	layer.msg('正在添加...',{icon:16,time:0,shade: [0.3, '#000']});
	var data= $("#set-Config").serialize() + '&sBody='+sBody + '&urladdress=' + urladdress;
	$.post('/crontab?action=AddCrontab',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		getCronData();
	});
}

$(".dropdown ul li a").click(function(){
	var txt = $(this).text();
	var type = $(this).attr("value");
	$(this).parents(".dropdown").find("button b").text(txt).attr("val",type);
	switch(type){
		case 'day':
			closeOpt();
			toHour();
			toMinute();
			break;
		case 'day-n':
			closeOpt();
			toWhere1('天');
			toHour();
			toMinute();
			break;
		case 'hour':
			closeOpt();
			toMinute();
			break;
		case 'hour-n':
			closeOpt();
			toWhere1('小时');
			toMinute();
			break;
		case 'minute-n':
			closeOpt();
			toWhere1('分钟');
			break;
		case 'week':
			closeOpt();
			toWeek();
			toHour();
			toMinute();
			break;
		case 'month':
			closeOpt();
			toWhere1('日');
			toHour();
			toMinute();
			break;
		case 'toFile':
			toFile();
			break;
		case 'toShell':
			toShell();
			$(".controls").html('脚本内容');
			break;
		case 'rememory':
			rememory();
			$(".controls").html('提示');
			break;
		case 'site':
			toBackup('sites');
			$(".controls").html('备份站点');
			break;
		case 'database':
			toBackup('databases');
			$(".controls").html('备份数据库');
			break;
		case 'logs':
			toBackup('logs');
			$(".controls").html('切割网址');
			break;
		case 'toUrl':
			toUrl();
			$(".controls").html('URL地址');
			break;
	}
})


//备份
function toBackup(type){
	var sMsg = "";
	switch(type){
		case 'sites':
			sMsg = '备份网站';
			sType = "sites";
			break;
		case 'databases':
			sMsg = '备份数据库';
			sType = "databases";
			break;
		case 'logs':
			sMsg = '切割日志';
			sType = "sites";
			break;
	}
	var data='type='+sType
	$.post('/crontab?action=GetDataList',data,function(rdata){
		$(".planname input[name='name']").attr('readonly','true').css({"background-color":"#f6f6f6","color":"#666"});
		var sOpt = "";
		if(rdata.data.length == 0){
			layer.msg('列表为空!',{icon:2})
			return
		}
		for(var i=0;i<rdata.data.length;i++){
			if(i==0){
				$(".planname input[name='name']").val(sMsg+'['+rdata.data[i].name+']');
			}
			sOpt += '<li><a role="menuitem" tabindex="-1" href="javascript:;" value="'+rdata.data[i].name+'">'+rdata.data[i].name+'['+rdata.data[i].ps+']</a></li>';			
		}
		
		var orderOpt = ''
		for (var i=0;i<rdata.orderOpt.length;i++){
			orderOpt += '<li><a role="menuitem" tabindex="-1" href="javascript:;" value="'+rdata.orderOpt[i].value+'">'+rdata.orderOpt[i].name+'</a></li>'
		}
		
		

		var sBody = '<div class="dropdown pull-left mr20">\
					  <button class="btn btn-default dropdown-toggle" type="button" id="backdata" data-toggle="dropdown" style="width:auto">\
						<b id="sName" val="'+rdata.data[0].name+'">'+rdata.data[0].name+'['+rdata.data[0].ps+']</b> <span class="caret"></span>\
					  </button>\
					  <ul class="dropdown-menu" role="menu" aria-labelledby="backdata">'+sOpt+'</ul>\
					</div>\
					<div class="textname pull-left mr20">备份到</div>\
					<div class="dropdown planBackupTo pull-left mr20">\
					  <button class="btn btn-default dropdown-toggle" type="button" id="excode" data-toggle="dropdown" style="width:auto;">\
						<b val="localhost">服务器磁盘</b> <span class="caret"></span>\
					  </button>\
					  <ul class="dropdown-menu" role="menu" aria-labelledby="excode">\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="localhost">服务器磁盘</a></li>\
						'+ orderOpt +'\
					  </ul>\
					</div>\
					<div class="textname pull-left mr20">保留最新</div><div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="save" id="save" value="3" maxlength="4" max="100" min="1"></span>\
					<span class="name">份</span>\
					</div>';
		$("#implement").html(sBody);
		getselectname();
		$(".dropdown ul li a").click(function(){
			var sName = $("#sName").attr("val");
			if(!sName) return;
			$(".planname input[name='name']").val(sMsg+'['+sName+']');
		});
	});
}


//下拉菜单名称
function getselectname(){
	$(".dropdown ul li a").click(function(){
		var txt = $(this).text();
		var type = $(this).attr("value");
		$(this).parents(".dropdown").find("button b").text(txt).attr("val",type);
	});
}
//清理
function closeOpt(){
	$("#ptime").html('');
}
//星期
function toWeek(){
	var mBody = '<div class="dropdown planweek pull-left mr20">\
					  <button class="btn btn-default dropdown-toggle" type="button" id="excode" data-toggle="dropdown">\
						<b val="1">周一</b> <span class="caret"></span>\
					  </button>\
					  <ul class="dropdown-menu" role="menu" aria-labelledby="excode">\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="1">周一</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="2">周二</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="3">周三</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="4">周四</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="5">周五</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="6">周六</a></li>\
						<li><a role="menuitem" tabindex="-1" href="javascript:;" value="0">周日</a></li>\
					  </ul>\
					</div>';
	$("#ptime").html(mBody);
	getselectname()
}
//指定1
function toWhere1(ix){
	var mBody ='<div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="where1" value="3" maxlength="2" max="31" min="0"></span>\
					<span class="name">'+ix+'</span>\
					</div>';
	$("#ptime").append(mBody);
}
//小时
function toHour(){
	var mBody = '<div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="hour" value="1" maxlength="2" max="23" min="0"></span>\
					<span class="name">时</span>\
					</div>';
	$("#ptime").append(mBody);
}

//分钟
function toMinute(){
	var mBody = '<div class="plan_hms pull-left mr20 bt-input-text">\
					<span><input type="number" name="minute" value="30" maxlength="2" max="59" min="0"></span>\
					<span class="name">分</span>\
					</div>';
	$("#ptime").append(mBody);
	
}

//从文件
function toFile(){
	var tBody = '<input type="text" value="" name="file" id="viewfile" onclick="fileupload()" readonly="true">\
				<button class="btn btn-default" onclick="fileupload()">上传</button>';
	$("#implement").html(tBody);
	$(".planname input[name='name']").removeAttr('readonly style').val("");
}

//从脚本
function toShell(){
	var tBody = "<textarea class='txtsjs bt-input-text' name='sBody'></textarea>";
	$("#implement").html(tBody);
	$(".planname input[name='name']").removeAttr('readonly style').val("");
}

//从脚本
function toUrl(){
	var tBody = "<input type='text' style='width:400px; height:34px' class='bt-input-text' name='urladdress' id='urladdress' placeholder='URL地址' value='http://' />";
	$("#implement").html(tBody);
	$(".planname input[name='name']").removeAttr('readonly style').val("");
}

//释放内存
function rememory(){
	$(".planname input[name='name']").removeAttr('readonly style').val("");
	$(".planname input[name='name']").val('释放内存');
	$("#implement").html('释放PHP、MYSQL、PURE-FTPD、APACHE、NGINX的内存占用,建议在每天半夜执行!');
	return;
}
//上传
function fileupload(){
	$("#sFile").change(function(){
		$("#viewfile").val($("#sFile").val());
	});
	$("#sFile").click();
}