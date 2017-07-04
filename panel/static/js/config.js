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
			content: "<div class='bt-form twoPassword'>\
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

//绑定修改宝塔账号
function bindBTName(a,type){
	var titleName = "绑定宝塔账号";
	if(type == "b"){
		btn = "<button type='button' class='btn btn-success btn-sm' onclick=\"bindBTName(1,'b')\">绑定</button>";
	}
	else{
		titleName = "修改绑定宝塔账号";
		btn = "<button type='button' class='btn btn-success btn-sm' onclick=\"bindBTName(1,'c')\">修改</button>";
	}
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		$.post(" /ssl?action=GetToken", "username=" + p1 + "&password=" + p2, function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {
					icon: 1
				});
			} else {
				layer.msg(b.msg, {
					icon: 2
				})
			}
		});
		return
	}
	layer.open({
		type: 1,
		area: "290px",
		title: titleName,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'><div class='line'><span class='tname'>账号</span><div class='info-r'><input class='bt-input-text' type='text' name='username' id='p1' value='' placeholder='宝塔官网账户' style='width:100%'/></div></div><div class='line'><span class='tname'>密码</span><div class='info-r'><input class='bt-input-text' type='password' name='password' id='p2' value='' placeholder='宝塔官网密码' style='width:100%'/></div></div><div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">取消</button> "+btn+"</div></div>"
	})
}
//解除绑定宝塔账号
function UnboundBt(){
	var name = $("input[name='btusername']").val();
	layer.confirm("您确定要解除绑定："+name+" ？",{closeBtn:2,title:"解除绑定"},function(){
		$.get("/ssl?action=DelToken",function(b){
			layer.msg(b.msg,{icon:b.status? 1:2})
		})
	})
}
$.get("/ssl?action=GetUserInfo",function(b){
	if(b.status){
		$("input[name='btusername']").val(b.data.username);
		$("input[name='btusername']").next().text("修改").attr("onclick","bindBTName(2,'c')").css({"margin-left":"-82px"});
		$("input[name='btusername']").next().after('<span class="btn btn-xs btn-success" onclick="UnboundBt()" style="vertical-align: 0px;">解绑</span>');
	}
	else{
		$("input[name='btusername']").next().text("绑定").attr("onclick","bindBTName(2,'b')").removeAttr("style");
	}
});



//设置API
function apiSetup(){
	var loadT = layer.msg('正在获取Token...',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/api?action=GetToken',function(rdata){
		layer.close(loadT);
		
	});
}
