setTimeout(function(){
		GetSshInfo();
	},500);
	
	setTimeout(function(){
		ShowAccept(1);
	},1000);
	
	setTimeout(function(){
		getLogs(1);
	},1500);
	
	function CloseLogs(){
		$.post('/files?action=CloseLogs','',function(rdata){
		$("#logSize").html(rdata);
		layer.msg('已清理!',{icon:1});
	});
}
	
$(function(){
	$.post('/files?action=GetDirSize','path=/www/wwwlogs',function(rdata){
		$("#logSize").html(rdata);
	});
})

$("#firewalldType").change(function(){
	var type = $(this).val();
	var w = '120px';
	var p = '端口';
	var t = '放行';
	var m = '说明: 支持放行端口范围，如: 3000:3500';
	if(type == 'address'){
		w = '150px';
		p = '欲屏蔽的IP地址';
		t = '屏蔽';
		m = '说明: 支持放行IP段，如: 192.168.0.0/24';
	}
	$("#AcceptPort").css("width",w);
	$("#AcceptPort").attr('placeholder',p);
	$("#toAccept").html(t);
	$("#f-ps").html(m);
	 
});


function GetSshInfo(){
	$.post('/firewall?action=GetSshInfo','',function(rdata){
		var SSHchecked = ''
		if(rdata.status){
			SSHchecked = "<input class='btswitch btswitch-ios' id='sshswitch' type='checkbox' checked><label class='btswitch-btn' for='sshswitch' onclick='SetMstscStatus()'></label>"
		}else{
			SSHchecked = "<input class='btswitch btswitch-ios' id='sshswitch' type='checkbox'><label class='btswitch-btn' for='sshswitch' onclick='SetMstscStatus()'></label>"
			$("#mstscSubmit").attr('disabled','disabled')
			$("#mstscPort").attr('disabled','disabled')
		}
		
		$("#in_safe").html(SSHchecked)
		$("#mstscPort").val(rdata.port)
		var isPint = ""
		if(rdata.ping){
			isPing = "<input class='btswitch btswitch-ios' id='noping' type='checkbox'><label class='btswitch-btn' for='noping' onclick='ping(0)'></label>"
		}else{
			isPing = "<input class='btswitch btswitch-ios' id='noping' type='checkbox' checked><label class='btswitch-btn' for='noping' onclick='ping(1)'></label>"
		}
		
		$("#isPing").html(isPing)
		
	});
}


	/**
 * 修改远程端口
 */

function mstsc(port) {
		layer.confirm('更改远程端口时，将会注消所有已登陆帐户，您真的要更改远程端口吗？', {
		title: '远程端口'
	}, function(index) {
		var data = "port=" + port;
		var loadT = layer.load({
			shade: true,
			shadeClose: false
		});
		$.post('/firewall?action=SetSshPort', data, function(ret) {
			layer.msg(ret.msg,{icon:ret.status?1:2})
			layer.close(loadT)
			GetSshInfo()
		});
	});
}
/**
 * 更改禁ping状态
 * @param {Int} state 0.禁ping 1.可ping
 */
function ping(status){
	var msg = status==0?'禁PING后不影响服务器正常使用，但无法ping通服务器，您真的要禁PING吗？':'解除禁PING状态可能会被黑客发现您的服务器，您真的要解禁吗？';
layer.confirm(msg,{title:'是否禁ping',closeBtn:2},function(){
	layer.msg('正在处理……',{icon:16,time:20000});
	$.post('/firewall?action=SetPing','status='+status, function(ret) {
		layer.closeAll();
		if (ret.status == true) {
			if(status == 0){
				layer.msg('已禁Ping', {icon: 1});
			}
			else{
				layer.msg('已解除禁Ping', {icon: 1});
			}
			setTimeout(function(){window.location.reload();},3000);
			
			
		} else {
			layer.msg('连接服务器失败', {icon: 2});
		}
	})
},function(){
	if(status == 1){
		$("#noping").prop("checked",true);
	}
	else{
		$("#noping").prop("checked",false);
		}
	})
}

	
	
	/**
 * 设置远程服务状态
 * @param {Int} state 0.启用 1.关闭
 */
function SetMstscStatus(){
	status = $("#sshswitch").prop("checked")==true?1:0;
	
	var msg = status==1?'停用SSH服务的同时也将注销所有已登陆用户,继续吗？':'确定启用SSH服务吗？';
	layer.confirm(msg,{title:'警告',closeBtn:2},function(index){
		if(index > 0){
			layer.msg('正在处理……',{icon:16,time:20000});
			$.post('/firewall?action=SetSshStatus','status='+status,function(rdata){
				layer.closeAll();
				layer.msg(rdata.msg,{icon:rdata.status?1:2});
				refresh();
			})
		}
	},function(){
		if(status == 0){
			$("#sshswitch").prop("checked",false);
		}
		else{
			$("#sshswitch").prop("checked",true);
		}
	})
}

/**
 * 取回数据
 * @param {Int} page  分页号
 */
function ShowAccept(page,search) {
	search = search == undefined ? '':search;
	var loadT = layer.load();
	$.post('/data?action=getData','table=firewall&tojs=ShowAccept&limit=10&p=' + page+"&search="+search, function(data) {
		layer.close(loadT);
		var Body = '';
		for (var i = 0; i < data.data.length; i++) {
			var status = '';
			switch(data.data[i].status){
				case 0:
					status = '未使用';
					break;
				case 1:
					status = '外网不通';
					break;
				default:
					status = '正常';
					break;
			}
			Body += "<tr>\
						<td><em class='dlt-num'>" + data.data[i].id + "</em></td>\
						<td>" + (data.data[i].port.indexOf('.') == -1?'放行端口:['+data.data[i].port+']':'屏蔽IP:['+data.data[i].port+']') + "</td>\
						<td>" + status + "</td>\
						<td>" + data.data[i].addtime + "</td>\
						<td>" + data.data[i].ps + "</td>\
						<td class='text-right'><a href='javascript:;' class='btlink' onclick=\"DelAcceptPort(" + data.data[i].id + ",'" + data.data[i].port + "')\">删除</a></td>\
					</tr>";
		}
		$("#firewallBody").html(Body);
		$("#firewallPage").html(data.page);
	})
}

//添加放行
function AddAcceptPort(){
	var type = $("#firewalldType").val();
	var port = $("#AcceptPort").val();
	var ps = $("#Ps").val();
	var action = "AddDropAddress";
	if(type == 'port'){
		ports = port.split(':');
		for(var i=0;i<ports.length;i++){
			if(isNaN(ports[i]) || ports[i] < 1 || ports[i] > 65535 ){
				layer.msg('端口范围不合法!',{icon:5});
				return;
			}
		}
		action = "AddAcceptPort";
	}
	
	
	if(ps.length < 1){
		layer.msg("备注/说明 不能为空!",{icon:2});
		$("#Ps").focus();
		return;
	}
	var loadT = layer.msg('正在添加...',{icon:16,time:0,shade: [0.3, '#000']})
	$.post('/firewall?action='+action,'port='+port+"&ps="+ps+'&type='+type,function(rdata){
		layer.close(loadT);
		if(rdata.status == true || rdata.status == 'true'){
			layer.msg(rdata.msg,{icon:1});
			ShowAccept(1);
			$("#AcceptPort").val('');
			$("#Ps").val('');
		}else{
			layer.msg('防火墙连接失败,请检查是否启用 Fiewalld',{icon:2});
		}
		
		$("#AcceptPort").attr('value',"");
		$("#Ps").attr('value',"");
	})
	
}

//删除放行
function DelAcceptPort(id, port) {
	var action = "DelDropAddress";
	if(port.indexOf('.') == -1){
		action = "DelAcceptPort";
	}
	
	layer.confirm("您真的要删除"+port+"吗？", {title: '删除防火墙规则',closeBtn:2}, function(index) {
		var loadT = layer.msg('正在删除...',{icon:16,time:0,shade: [0.3, '#000']})
		$.post("/firewall?action="+action,"id=" + id + "&port=" + port, function(ret) {
			layer.close(loadT);
			layer.msg(ret.msg,{icon:ret.status?1:2})
			ShowAccept(1);
		});
	});
}


/**
 * 取回数据
 * @param {Int} page  分页号
 */
function getLogs(page,search) {
	search = search == undefined ? '':search;
	var loadT = layer.load();
	$.post('/data?action=getData','table=logs&tojs=getLogs&limit=10&p=' + page+"&search="+search, function(data) {
		layer.close(loadT);
		var Body = '';
		for (var i = 0; i < data.data.length; i++) {
			Body += "<tr>\
							<td><em class='dlt-num'>" + data.data[i].id + "</em></td>\
							<td>" + data.data[i].type + "</td>\
							<td>" + data.data[i].log + "</td>\
							<td>" + data.data[i].addtime + "</td>\
						</tr>";
		}
		$("#logsBody").html(Body);
		$("#logsPage").html(data.page);
	})
}

//清理面板日志
function delLogs(){
	layer.confirm('即将清空面板日志，继续吗？',{title:'清空日志',closeBtn:2},function(){
		var loadT = layer.msg('正在清理...',{icon:16});
		$.post('/ajax?action=delClose','',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
			getLogs(1);
		});
	});
}