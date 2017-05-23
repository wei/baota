//校验端口格式
$(function(){
	$("#banport").keyup(function(){
		var text = $(this).val();
		if(isNaN(text)){
			text = text.substring(0,text.length-1);
			$(this).val(text);
		}
		if($(this).val()>65535){
			$(this).val(65535);
		}
	});
	$("#twoPassword").click(function(){
		layer.open({
			type: 1,
			area: '500px',
			title: '模块加锁设置',
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: "<div class='zun-form-new twoPassword'>\
				<div class='tp-tit'>设置加锁模块</div>\
				<div class='tp-con' style='margin-bottom:30px'>\
					<label><input type='checkbox'>文件管理</label>\
					<label><input type='checkbox'>计划任务</label>\
					<label><input type='checkbox'>面板设置</label>\
				</div>\
				<div class='tp-tit'>设置加锁密码</div>\
				<div class='tp-con'>\
					<div class='line'><label><span>校验面板密码</span></label><div class='info-r'><input type='password' name='btpw' value=''></div></div>\
					<div class='line'><label><span>设置二级密码</span></label><div class='info-r'><input type='password' name='bttpw' value=''></div></div>\
					<div class='line'><label><span>重复输入</span></label><div class='info-r'><input type='password' name='bttpw' value=''></div></div>\
				</div>\
				<div class='submit-btn'><button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">取消</button>\
				<button type='button' class='btn btn-success btn-sm' onclick=\"setPassword(1)\">提交</button></div>\
			</div>"
		});
	});
});


//关闭面板
function ClosePanel(){
	layer.confirm('关闭面板会导致您无法访问面板 ,您真的要关闭宝塔Linux面板吗？',{title:'关闭面板',closeBtn:2,icon:13}, function() {
		$.post('/config?action=ClosePanel','',function(rdata){
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			setTimeout(function(){window.location.reload();},1000);
		});
	},function(){
		$("#closePl").prop("checked",false);
	});
}

//设置自动更新
function SetPanelAutoUpload(){
	loadT = layer.msg('正在设置...',{icon:16,time:0});
	$.post('/config?action=AutoUpdatePanel','',function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}


$(".set-submit").click(function(){
	var data = $("#set-Config").serialize();
	layer.msg('正在保存数据...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=setPanel',data,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		if(rdata.status){
			if(rdata.isReWeb) $.get('/system?action=ReWeb',function(){});
			setTimeout(function(){
				window.location.href = 'http://'+rdata.host+rdata.uri;
			},3000);
		}
	});
	
});


function syncDate(){
	var loadT = layer.msg('正在同步时间...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=syncDate','',function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:1});
		setTimeout(function(){
				window.location.reload();
			},3000);
	});
}

//PHP守护程序
function Set502(){
	var loadT = layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/config?action=Set502','',function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});	
}