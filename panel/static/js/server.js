//扫描系统垃圾
function junk() {
		var gurl = "/Clear/getSize?type=all";
		var body = "";
		$(".junk .box-con").html("<span class='loading'></span>");
		$.ajax({ url: gurl,type:"get",async:true ,success: function(rdata){
			body = "<p>系统临时文件：<span id='systemsize'>" + rdata.System_temp + " MB</span><span class='btn btn-del btn-xs' onclick=\"delTemp('system')\">清除</span></p>\
						<p>用户临时文件：<span id='usersize'>" + rdata.User_temp + " MB</span><span class='btn btn-del btn-xs' onclick=\"delTemp('user')\">清除</span></p>\
						<p>IE临时文件：<span id='iesize'>" + rdata.Ie_temp + " MB</span><span class='btn btn-del btn-xs' onclick=\"delTemp('ie')\">清除</span></p>\
						<p>cookie：<span id='cookiesize'>" + rdata.Cookie_temp + " MB</span><span class='btn btn-del btn-xs' onclick=\"delTemp('cookie')\">清除</span></p>";
			$(".junk .box-con").html(body);
			$(".junk .box-con p").hide();
			var num = $(".junk p").size();
			for (var i = 0; i < num; i++) {
				setTimeout("$('.junk p').eq(" + i + ").fadeIn(1000);", i * 100);
			}

		}});
	}


//清除
function delTemp(type) {
		var data = "type=" + type;
		$.get('/Clear/delTemp', data, function(rdata) {
			if (rdata.status == "true") {
				layer.msg("清除成功", {
					icon: 1
				});
			}
		});
		junk();
	}


//取系统巡检数据-用户安全检测
function userSafe() {
	var gurl = "/clear/testIng?type=user";
	var body = "";
	$(".system-check .user-safe .box-con").html("<i class='loading'></i>");
	$.ajax({ url: gurl,type:"get",async:true ,success: function(rdata){
		var userlist = "";
		for (var i = 0; i < rdata.user.length; i++) {
			if (rdata.user[i].UserName == "Administrator" || rdata.user[i].UserName == "administrator") {
				if(rdata.user[i].Disable==false){
					userlist += "<p class='yellow'><a class='name' data-title='默认管理员名称没有修改，容易受到黑客暴力破解！点击改名修改。'>" + rdata.user[i].UserName + "</a><span class='btn btn-info btn-xs' onclick=\"changeAdminName('"+rdata.user[i].UserName+"')\">改名</span><span class='btn btn-success btn-xs' onclick=\"disabledAdmin('"+rdata.user[i].UserName+"')\">禁用</span><span class='btn btn-del btn-xs' onclick=\"delAdmin('"+rdata.user[i].UserName+"')\">删除</span></p>";
				}
				else{
					userlist += "<p class='yellow'><a class='name' data-title='默认管理员名称没有修改，容易受到黑客暴力破解！点击改名修改。'>" + rdata.user[i].UserName + "</a><span class='btn btn-success btn-xs' onclick=\"enableAdmin('"+rdata.user[i].UserName+"')\">启用</span></p>";
				}
			} else {
				if(rdata.user[i].Disable==false){
					userlist += "<p><a class='name'>" + rdata.user[i].UserName + "</a><span class='btn btn-info btn-xs' onclick=\"changeAdminName('"+rdata.user[i].UserName+"')\">改名</span><span class='btn btn-success btn-xs' onclick=\"disabledAdmin('"+rdata.user[i].UserName+"')\">禁用</span><span class='btn btn-del btn-xs' onclick=\"delAdmin('"+rdata.user[i].UserName+"')\">删除</span></p>";
				}
				else{
					userlist += "<p><a class='name' data-title='该账户已禁用'>" + rdata.user[i].UserName + "</a><span class='btn btn-success btn-xs' onclick=\"enableAdmin('"+rdata.user[i].UserName+"')\">启用</span></p>";
				}
			}
		}
		body = "<p>管理员数量：" + rdata.count + "</p>" + userlist;
		$(".system-check .user-safe .box-con").html(body).hide().fadeIn(1000);
		$('.user-safe .box-con p a').mouseover(function(){
			var tipstitle = $(this).attr("data-title");
		    layer.tips(tipstitle, this, {
			    tips: [1, '#3c8dbc'],
			    time:0
			});
		});
		$('.user-safe .box-con p a').mouseout(function(){
			$(".layui-layer-tips").remove();
		});
	}});
}
//更改管理员用户名称
function changeAdminNameGo(name){
	var newName = $(".usernewName").val();
	var gurl = "/clear/testIng?type=userName&name="+name+"&newName="+newName;
	$.get(gurl,function(rdata){
		if(rdata.status == true){
			userSafe();
			layer.msg('用户名更改成功', {icon: 1});
		}
		else{
			layer.msg(rdata.msg, {icon: 5});
		}
	});
	layer.closeAll();
}
//更改名称弹出层
function changeAdminName(name){
	var index = layer.open({
		type: 1,
		area: '350px',
		title: '更改管理员用户名称',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='zun-form-new changename'>\
			<div class='line'>\
				<input class='usernewName' type='text' value='"+name+"'>\
			</div>\
			<div class='submit-btn'>\
				<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
		        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"changeAdminNameGo('"+name+"')\" >提交</button>\
	        </div>\
			</div>"
	});
}
//删除管理员
function delAdmin(name){
	layer.confirm('您是否真的要删除: '+name, {
		icon:3,
	    btn: ['删除','取消'], //按钮
	    closeBtn: 2,
	    title:false
	}, function(){
	    var gurl = "/clear/testIng?type=userDelete&name="+name;
		$.get(gurl,function(rdata){
			if(rdata.status == true){
				userSafe();
				layer.msg('用户删除成功', {icon: 1});
			}
			else{
				layer.msg(rdata.msg, {icon: 5});
			}
		});
	}, function(){
	    layer.closeAll();
	});
}
//禁用管理员
function disabledAdmin(name){
	var gurl = "/clear/testIng?type=userStatus&status=0&name="+name;
	$.get(gurl,function(rdata){
		if(rdata.status == true){
			userSafe();
			layer.msg('用户已禁用', {icon: 1});
		}
		else{
			layer.msg(rdata.msg, {icon: 5});
		}
	});
}

//启用管理员
function enableAdmin(name){
	var gurl = "/clear/testIng?type=userStatus&status=1&name="+name;
	$.get(gurl,function(rdata){
		if(rdata.status == true){
			userSafe();
			layer.msg('用户已启用', {icon: 1});
		}
		else{
			layer.msg(rdata.msg, {icon: 5});
		}
	});
}

//危险端口检测
function dangerPort() {
	var gurl="/clear/testIng?type=danger";
	var body="";
	$(".system-check .danger").html("<i class='loading'></i>");
	$.ajax({ url: gurl,type:"get",async:true ,success: function(rdata){
	        var dangerPortList = "";
			for (var i = 0; i < rdata.length; i++) {
				if (rdata[i].status == true) {
					dangerPortList +=rdata[i].port+" ";
				}
			}
			body = "<p>已开启端口："+dangerPortList+"</p>";
			$(".system-check .danger").html(body).hide().fadeIn(1000);
	}});
}

//防火墙状态检查
function firewall(){
	var gurl = "/clear/testIng?type=firewall";
	var body = "";
	//$(".system-check .firewall").html("<i class='loading'></i>");
	$.ajax({ url: gurl,type:"get",async:true ,success: function(rdata){
		if(rdata.status==false){
			body="<p>防火墙未开启：<span class='btn btn-success btn-xs' onclick='FirewallStatus(1)'>开启</span></p>";
		}
		else{
			body="<p>防火墙已开启：<span class='btn btn-del btn-xs' onclick='FirewallStatus(0)'>关闭</span></p>";
		}
		$(".system-check .firewall").html(body).hide().fadeIn(1000);
	}});
}
//远程端口
function mstsc(){
	var gurl = "/clear/testIng?type=mstsc";
	var body = "";
	//$(".system-check .mstsc").html("<i class='loading'></i>");
	$.ajax({ url: gurl,type:"get",async:true ,success: function(rdata){
		if(rdata.status==false){
			body="<p>远程端口："+rdata.port+"，未开启，<span class='btn btn-success btn-xs' onclick='mstscStatus(0)'>开启</span></p>";
		}
		else{
			body="<p>远程端口："+rdata.port+"，已启用，<span class='btn btn-del btn-xs' onclick='mstscStatus(1)'>关闭</span></p>";
		}
		$(".system-check .mstsc").html(body).hide().fadeIn(1000);
	}});
}
//防护软件检测
function safe(){
	var gurl = "/clear/testIng?type=safe";
	var body = "";
	//$(".system-check .safeinfo").html("<i class='loading'></i>");
	$.ajax({ url: gurl,type:"get",async:true ,success: function(rdata){
		body="<p>防护软件："+rdata.safes+"</p>";
		$(".system-check .safeinfo").html(body).hide().fadeIn(1000);
	}});
}

//网络速度检测
function ping() {
	var gurl = "/clear/testIng?type=ping";
	var body = "";
	$("#pings-box").html("<i class='loading'></i>");
	$.ajax({ url: gurl,type:"get",async:true ,success: function(rdata){
		var pingList = "";
		for (var i = 0; i < rdata.length; i++) {
			pingList += "<span>"+rdata[i].addr+"<em> <b>"+rdata[i].ping+"</b> ms</em></span>";
		}
		body = pingList;
		$("#pings-box").html(body).hide().fadeIn(1000);
		$("#pings-box span").each(function(){
			var that = $(this).find("em");
			var s = $(this).find("b").text();
			if(s<50){
				that.css("color","#5cb85c");
			}
			else if(s<80){
				that.css("color","#3c8dbc");
			}
			else{
				that.css("color","#fdab02");
			}
		})
	}});
}
//禁用危险端口
function NodangerPort(){
	var index = layer.open({
		type: 1,
		area: '500px',
		title: '端口禁用',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='zun-form-new systemSafeCheck' style='text-align:left'>\
			<div class='line'>危险端口135：存在被远程电脑写入恶意代码的风险。</div>\
			<div class='line'>危险端口137：允许获取系统信息，被黑客利用的风险。</div>\
			<div class='line'>危险端口138：容易泄露主机所处的局域网信息。</div>\
			<div class='line'>危险端口139：存在被利用空会话，破解管理员密码的风险。</div>\
			<div class='line'>危险端口445：存在通过共享文件夹入侵主机硬盘的风险。</div>\
			<div class='line'>危险端口593：存在远程执行代码的风险。</div>\
			<div class='line'>危险端口4489：存在远程入侵的风险。</div>\
			<div class='line'>危险端口1025：动态端口扫描风险。</div>\
			<div class='line'>危险端口2475：存在安全隐患。</div>\
			<div class='line'>危险端口3127：存在安全隐患。</div>\
			<div class='line'>危险端口6129：存在安全隐患。</div>\
		</div>"
		});
		$(".systemSafeCheck .line").hide();
		var num = $(".systemSafeCheck .line").size();
		for (var i = 0; i < num; i++) {
			setTimeout("$('.systemSafeCheck .line').eq(" + i + ").append(\"<span style='color:#00be43;float:right;'>已关闭</span>\").fadeIn();", i * 100);
		}
	var gurl = "/clear/testIng?type=dangerSet";
	$.get(gurl,function(rdata){
		setTimeout("layer.msg('危险端口已禁用', {icon: 1})",1000);
	});
}

//设置防火墙状态
function FirewallStatus(status){
	var gurl = "/clear/testIng?type=FirewallStatus&status="+status;
	$.get(gurl,function(rdata){
		if(status==1){
			if(rdata.status==true){
				layer.msg('防火墙开启成功', {icon: 1});
			}
			else{
				layer.msg('防火墙开启失败', {icon: 5});
			}
		}
		if(status==0){
			if(rdata.status==true){
				layer.msg('防火墙关闭成功', {icon: 1});
			}
			else{
				layer.msg('防火墙关闭失败', {icon: 5});
			}
		}
		firewall();
	});
}
//设置远程端口状态
function mstscStatus(status){
	var gurl = "/clear/testIng?type=mstscStatus&status="+status;
	$.get(gurl,function(rdata){
		if(status==0){
			if(rdata.status==true){
				layer.msg('远程服务开启成功', {icon: 1});
			}
			else{
				layer.msg('远程服务开启失败', {icon: 5});
			}
		}
		if(status==1){
			if(rdata.status==true){
				layer.msg('远程服务关闭成功', {icon: 1});
			}
			else{
				layer.msg('远程服务关闭失败', {icon: 5});
			}
		}
		mstsc();
	});
}
//安全检测
function systemSafeCheck(){
	setTimeout("dangerPort()", 50);
	setTimeout("firewall()", 2000);
	setTimeout("mstsc()", 4000);
	setTimeout("safe()", 6000);
}
function systemCheckUpDown(){
	$(".system-check .con").hide().show();
}
function systemCheck(info){
	if(info < 1.8){
		layer.msg('云管家版本过低，请更新版本!',{icon:5});
		return;
	}
	systemCheckUpDown();
	setTimeout("junk()", 10);
	setTimeout("userSafe()", 2000);
	setTimeout("dangerPort()", 4000);
	setTimeout("firewall()", 6000);
	setTimeout("mstsc()", 8000);
	setTimeout("safe()", 10000);
	setTimeout("ping()", 12000);
}
var boxcon = $(".system-check .con > ul > li .box-right .box-con");
boxcon.click(function(){
	boxcon.removeAttr("onclick").unbind("click");
	boxcon.css({"background":"none","opacity":"1"});
	boxcon.next().remove();
})
$(".system-check .s-title a").click(function(){
	boxcon.removeAttr("onclick").unbind("click");
	boxcon.css({"background":"none","opacity":"1"});
	boxcon.next().remove();
})
boxcon.css("opacity","0.4").after("<div class='icon-shuaxin'></div>");
$(".box-right .gongju").find(".btn-info").click(function(){
	$(this).parent().next().removeAttr("onclick").unbind("click");
	$(this).parent().next().css({"background":"none","opacity":"1"});
	$(this).parent().next().next().remove();
})
