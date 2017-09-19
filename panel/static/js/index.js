//检测是否安装环境
$.post("/ajax?action=CheckInstalled",function(rdata){
	if(rdata == false){
		RecInstall();
	}
})

$(function(){
	$(".mem-release").hover(function(){
		$(this).addClass("shine_green");
		if(!($(this).hasClass("mem-action"))){
			$(this).find(".mem-re-min").hide();
			$(this).find(".mask").css({"color":"#d2edd8"});
			$(this).find(".mem-re-con").css({"display":"block"});
			$(this).find(".mem-re-con").animate({"top":"0",opacity:1});
			$("#memory").text(lan.index.memre);
		}
	},function(){
		if(!($(this).hasClass("mem-action"))){
			$(this).find(".mem-re-min").show();
		}
		else{
			$(this).find(".mem-re-min").hide();
		}
		$(this).removeClass("shine_green");
		$(this).find(".mask").css({"color":"#20a53a"});
		$(this).find(".mem-re-con").css({"top":"15px",opacity:1,"display":"none"});
		$("#memory").text(getCookie("mem-before"));
	}).click(function(){
		$(this).find(".mem-re-min").hide();
		if(!($(this).hasClass("mem-action"))){
			ReMemory();
			var btlen = $(".mem-release").find(".mask span").text();
			$(this).addClass("mem-action");
			$(this).find(".mask").css({"color":"#20a53a"});
			$(this).find(".mem-re-con").animate({"top":"-400px",opacity:0});
			$(this).find(".pie_right .right").css({"transform":"rotate(3deg)"});
			for(var i=0;i<btlen;i++){
				setTimeout("rocket("+btlen+","+i+")",i*30);
			}
		}
	})
})

function rocket(sum,m){
	var n = sum-m;
	$(".mem-release").find(".mask span").text(n);
}
//释放内存
function ReMemory(){
	setTimeout(function(){
		$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px'}).html('<span style="display:none">1</span>'+lan.index.memre_ok_0+' <img src="/static/img/ings.gif">');
		$.post('/system?action=ReMemory','',function(rdata){
			var percent = GetPercent(rdata.memRealUsed,rdata.memTotal);
			var memText = rdata.memRealUsed+"/"+rdata.memTotal + " (MB)";
			percent = Math.round(percent);
			$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px'}).html("<span style='display:none'>"+percent+"</span>"+lan.index.memre_ok);
			setCookie("mem-before",memText);
			var memNull = getCookie("memRealUsed") - rdata.memRealUsed;
			setTimeout(function(){
				if(memNull > 0){
					$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px','line-height':'22px','padding-top':'22px'}).html("<span style='display:none'>"+percent+"</span>"+lan.index.memre_ok_1+"<br>"+memNull+"MB");
				}
				else{
					$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px'}).html("<span style='display:none'>"+percent+"</span>"+lan.index.memre_ok_2);
				}
				$(".mem-release").removeClass("mem-action");
				$("#memory").text(memText);
				setCookie("memRealUsed",rdata.memRealUsed);
			},1000);
			setTimeout(function(){
				$(".mem-release").find('.mask').removeAttr("style").html("<span>"+percent+"</span>%");
				$(".mem-release").find(".mem-re-min").show();
			},2000)
		});
	},2000);
}
function GetPercent(num, total){
	num = parseFloat(num);
	total = parseFloat(total);
	if (isNaN(num) || isNaN(total)) {
		return "-";
	}
	return total <= 0 ? "0%" : (Math.round(num / total * 10000) / 100.00);
}
function GetDiskInfo(){
	$.get('/system?action=GetDiskInfo',function(rdata){
		var dBody
		for(var i=0;i<rdata.length;i++){
			if(rdata[i].path == '/' || rdata[i].path == '/www'){
				if(rdata[i].size[2].indexOf('M') != -1){
					$("#messageError").show();
					$("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span> '+lan.get('diskinfo_span_1',[rdata[i].path])+'</p>');
				}
			}
			dBody = '<li class="col-xs-6 col-sm-3 col-md-3 col-lg-2 mtb20 circle-box text-center">'
						+'<h3 class="c5 f15">'+rdata[i].path+'</h3>'
						+'<div class="circle">'
							+'<div class="pie_left">'
								+'<div class="left"></div>'
							+'</div>'
							+'<div class="pie_right">'
								+'<div class="right"></div>'
							+'</div>'
							+'<div class="mask"><span>'+rdata[i].size[3].replace('%','')+'</span>%</div>'
						+'</div>'
						+'<h4 class="c5 f15">'+rdata[i].size[1]+'/'+rdata[i].size[0]+'</h4>'
					+'</li>'
			$("#systemInfoList").append(dBody)
			setImg();
		}
		
	});

}

function getInfo() {
	$.get("/system?action=GetSystemTotal", function(info) {
		setCookie("memRealUsed",parseInt((info.memRealUsed)));
		$("#memory").html(parseInt((info.memRealUsed))+'/'+info.memTotal+' (MB)');
		setCookie("mem-before",$("#memory").text());
		if(!getCookie('memSize')) setCookie('memSize',parseInt(info.memTotal));
		$("#left").html(Math.floor(info.memRealUsed / (info.memTotal / 100)));
		$("#info").html(info.system);
		$("#running").html(info.time);
		$("#core").html(info.cpuNum + " "+lan.index.cpu_core);
		$("#state").html(info.cpuRealUsed);
		var memFree = info.memTotal - info.memRealUsed;
		
		if(memFree < 64){
			$("#messageError").show();
			$("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;">'+lan.index.mem_warning+'</span> </p>')
		}
		
		if(info.isuser > 0){
			$("#messageError").show();
			$("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span> '+lan.index.user_warning+'<a class="btlink" href="javascript:setUserName();"> ['+lan.public.edit+']</a></p>')
		}
		setImg();
	});
}


function getNet(){
	var up;
	var down;
	$.ajax({
		type:"get",
		url:"/system?action=GetNetWork",
		async:true,
		success:function(net){
			$("#InterfaceSpeed").html(lan.index.interfacespeed+"： 1.0Gbps");
			$("#upSpeed").html(net.up+' KB');
			$("#downSpeed").html(net.down+' KB');
			$("#downAll").html(ToSize(net.downTotal));
			$("#downAll").attr('title',lan.index.package+':'+net.downPackets)
			$("#upAll").html(ToSize(net.upTotal));
			$("#upAll").attr('title',lan.index.package+':'+net.upPackets)
			$("#core").html(net.cpu[1] + " "+lan.index.cpu_core);
			$("#state").html(net.cpu[0]);
			setCookie("upNet",net.up);
			setCookie("downNet",net.down);
			setImg();
		}
	});
	//var result = Number(getCookie("upNet"));
	//return result;
}
//网络Io
function NetImg(){
	var myChartNetwork = echarts.init(document.getElementById('NetImg'));
	var xData = [];
	var yData = [];
	var zData = [];
	function getTime(){
		var now = new Date();
		var hour=now.getHours();
		var minute=now.getMinutes();
		var second=now.getSeconds();
		if(minute<10){
			minute = "0"+minute;
		}
		if(second<10){
			second = "0"+second;
		}
		var nowdate = hour+":"+minute+":"+second;
		return nowdate;
	}
	function ts(m){return m<10?'0'+m:m }
	function format(sjc){
		var time = new Date(sjc);
		var h = time.getHours();
		var mm = time.getMinutes();
		var s = time.getSeconds();
		return ts(h)+':'+ts(mm)+':'+ts(s);
	}
	function addData(shift) {
		xData.push(getTime());
		yData.push(getCookie("upNet"));
		zData.push(getCookie("downNet"));
		if (shift) {
			xData.shift();
			yData.shift();
			zData.shift();
		}
	}
	for (var i = 8; i >= 0; i--){
		var time = (new Date()).getTime();
		xData.push(format(time - (i * 3 * 1000)));
		yData.push(0);
		zData.push(0);                                                       
	}
	// 指定图表的配置项和数据
	var option = {
		title: {
			text: lan.index.interface_net,
			left: 'center',
			textStyle:{
				color:'#888888',
				fontStyle: 'normal',
				fontFamily: lan.index.net_font,
				fontSize: 16,
			}
		},
		tooltip: {
			trigger: 'axis'
		},
		legend: {
			data:[lan.index.net_up,lan.index.net_down],
			bottom:'2%'
		},
		xAxis: {
			type: 'category',
			boundaryGap: false,
			data: xData,
			axisLine:{
				lineStyle:{
					color:"#666"
				}
			}
		},
		yAxis: {
			name: lan.index.unit+'KB/s',
			splitLine:{
				lineStyle:{
					color:"#eee"
				}
			},
			axisLine:{
				lineStyle:{
					color:"#666"
				}
			}
		},
		series: [{
			name: lan.index.net_up,
			type: 'line',
			data: yData,
			smooth:true,
			symbol: 'none',
			stack: 'a',
			areaStyle: {
				normal: {}
			},
			itemStyle: {
				normal: {
					color: 'rgba(255, 140, 0, 0.7)'
				}
			}
		},{
			name: lan.index.net_down,
			type: 'line',
			data: zData,
			smooth:true,
			symbol: 'none',
			stack: 'a',
			areaStyle: {
				normal: {}
			},
			itemStyle: {
				normal: {
					color: 'rgba(30, 144, 255, 0.7)'
				}
			}
		}]
	};
	setInterval(function () {
		getNet();
		addData(true);
		myChartNetwork.setOption({
			xAxis: {
				data: xData
			},
			series: [{
				name:lan.index.net_up,
				data: yData
			},{
				name:lan.index.net_down,
				data: zData
			}]
		});
	}, 3000);
	// 使用刚指定的配置项和数据显示图表。
	myChartNetwork.setOption(option);
	window.addEventListener("resize",function(){
		myChartNetwork.resize();
	});
}
NetImg();
function setImg() {
	$('.circle').each(function(index, el) {
		var num = $(this).find('span').text() * 3.6;
		if (num <= 180) {
			$(this).find('.left').css('transform', "rotate(0deg)");
			$(this).find('.right').css('transform', "rotate(" + num + "deg)");
		} else {
			$(this).find('.right').css('transform', "rotate(180deg)");
			$(this).find('.left').css('transform', "rotate(" + (num - 180) + "deg)");
		};
	});

}
setImg();

//检查更新
setTimeout(function(){
	$.get('/ajax?action=UpdatePanel',function(rdata){
		if(rdata.status == false) return;
		if(rdata.version != undefined){
			$("#toUpdate").html('<a class="btlink" href="javascript:updateMsg();">'+lan.index.update_go+'</a>');
			return;
		}
		$.get('/system?action=ReWeb',function(){});
		layer.msg(rdata.msg,{icon:1});
		setTimeout(function(){
			window.location.reload();
		},3000);
	}).error(function(){
		$.get('/system?action=ReWeb',function(){});
		setTimeout(function(){
			window.location.reload();
		},3000);
	});
},3000);


//检查更新
function checkUpdate(){
	var loadT = layer.msg(lan.index.update_get,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=UpdatePanel&check=true',function(rdata){
		layer.close(loadT);
		if(rdata.status === false){
			layer.confirm(rdata.msg,{title:lan.index.update_check,icon:1,closeBtn: 2,btn: [lan.public.know,lan.public.close]});
			return;
		}
		layer.msg(rdata.msg,{icon:1});
		if(rdata.version != undefined) updateMsg();
	});
}


function updateMsg(){
	window.open("http://www.bt.cn/bbs/thread-1186-1-1.html");
	$.get('/ajax?action=UpdatePanel',function(rdata){
		layer.open({
			type:1,
			title:lan.index.update_to+'['+rdata.version+']',
			area: '400px', 
			shadeClose:false,
			closeBtn:2,
			content:'<div class="setchmod bt-form pd20 pb70">'
					+'<p style="padding: 0 0 10px;line-height: 24px;">'+rdata.updateMsg+'</p>'
					+'<div class="bt-form-submit-btn">'
					+'<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">'+lan.public.cancel+'</button>'
					+'<button type="button" class="btn btn-success btn-sm btn-title" onclick="updateVersion(\''+rdata.version+'\')" >'+lan.index.update_go+'</button>'
				    +'</div>'
					+'</div>'
		});
	});
}

//开始升级
function updateVersion(version){
	var loadT = layer.msg(lan.index.update_the,{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=UpdatePanel','toUpdate=yes',function(rdata){
		layer.closeAll();
		if(rdata.status === false){
			layer.msg(rdata.msg,{icon:5,time:5000});
			return;
		}
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		if(rdata.status){
			$("#btversion").html(version);
			$("#toUpdate").html('');
		}
		
		layer.msg(lan.index.update_ok,{icon:1});
		$.get('/system?action=ReWeb',function(){});
		setTimeout(function(){
			window.location.reload();
		},3000);
	}).error(function(){
		layer.msg(lan.index.update_ok,{icon:1});
		$.get('/system?action=ReWeb',function(){});
		setTimeout(function(){
			window.location.reload();
		},3000);
	});
}

//更新日志
function openLog(){
	layer.open({
		type: 1,
		area: '640px',
		title: lan.index.update_log,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: '<div class="DrawRecordCon"></div>'	
	});
	$.get('https://www.bt.cn/Api/getUpdateLogs',function(rdata){
		var body = '';
		for(var i=0;i<rdata.length;i++){
			body += '<div class="DrawRecord DrawRecordlist">\
					<div class="DrawRecordL">'+rdata[i].addtime+'<i></i></div>\
					<div class="DrawRecordR">\
						<h3>'+rdata[i].title+'</h3>\
						<p>'+rdata[i].body+'</p>\
					</div>\
				</div>'
		}
		$(".DrawRecordCon").html(body);
	},'jsonp');
}


//重启服务器
function ReBoot(){
	layer.open({
		type: 1,
		title: lan.index.reboot_title,
		area: ['500px', '280px'],
		closeBtn: 2,
		shadeClose: false,
		content:"<div class='bt-form bt-window-restart'>\
			<div class='pd15'>\
			<p style='color:red; margin-bottom:10px; font-size:15px;'>"+lan.index.reboot_warning+"</p>\
			<div class='SafeRestart' style='line-height:26px'>\
				<p>"+lan.index.reboot_ps+"</p>\
				<p>"+lan.index.reboot_ps_1+"</p>\
				<p>"+lan.index.reboot_ps_2+"</p>\
				<p>"+lan.index.reboot_ps_3+"</p>\
				<p>"+lan.index.reboot_ps_4+"</p>\
			</div>\
			</div>\
			<div class='bt-form-submit-btn'>\
				<button type='button' id='web_end_time' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>"+lan.public.cancel+"</button>\
				<button type='button' id='web_del_send' class='btn btn-success btn-sm btn-title'  onclick='WSafeRestart()'>"+lan.public.ok+"</button>\
			</div>\
		</div>"
	})
}

//重启服务器
function WSafeRestart(){
	var body = '<div class="SafeRestartCode pd15" style="line-height:26px"></div>';
	$(".bt-window-restart").html(body);
	var data = "name="+serverType+"&type=stop";
	$(".SafeRestartCode").html("<p>"+lan.index.reboot_msg_1+"</p>");
	$.post('/system?action=ServiceAdmin',data,function(r1){
		data = "name=mysqld&type=stop";
		$(".SafeRestartCode").html("<p class='c9'>"+lan.index.reboot_msg_1+"</p><p>"+lan.index.reboot_msg_2+"...</p>");
		$.post('/system?action=ServiceAdmin',data,function(r2){
			$(".SafeRestartCode").html("<p class='c9'>正在停止"+serverType+"服务</p><p class='c9'>"+lan.index.reboot_msg_2+"</p><p>"+lan.index.reboot_msg_3+"...</p>");
			$.post('/system?action=RestartServer','',function(rdata){
				$(".SafeRestartCode").html("<p class='c9'>"+lan.index.reboot_msg_1+"</p><p class='c9'>"+lan.index.reboot_msg_2+"</p><p class='c9'>"+lan.index.reboot_msg_3+"</p><p>"+lan.index.reboot_msg_4+"...</p>");
				var sEver = setInterval(function(){
					$.get("/system?action=GetSystemTotal", function(info) {
						clearInterval(sEver);
						$(".SafeRestartCode").html("<p class='c9'>"+lan.index.reboot_msg_1+"</p><p class='c9'>"+lan.index.reboot_msg_2+"</p><p class='c9'>"+lan.index.reboot_msg_3+"</p><p class='c9'>"+lan.index.reboot_msg_4+"</p><p>"+lan.index.reboot_msg_5+"</p>");
						setTimeout(function(){
							layer.closeAll();
						},3000);
					}).error(function(){
						
					});
				},3000);
			}).error(function(){
				$(".SafeRestartCode").html("<p class='c9'>"+lan.index.reboot_msg_1+"</p><p class='c9'>"+lan.index.reboot_msg_2+"</p><p class='c9'>"+lan.index.reboot_msg_3+"</p><p>"+lan.index.reboot_msg_4+"...</p>");
				var sEver = setInterval(function(){
					$.get("/system?action=GetSystemTotal", function(info) {
						clearInterval(sEver);
						$(".SafeRestartCode").html("<p class='c9'>"+lan.index.reboot_msg_1+"</p><p class='c9'>"+lan.index.reboot_msg_2+"</p><p class='c9'>"+lan.index.reboot_msg_3+"</p><p class='c9'>"+lan.index.reboot_msg_4+"</p><p>"+lan.index.reboot_msg_5+"</p>");
						setTimeout(function(){
							layer.closeAll();
							window.location.reload();
						},3000);
						
					}).error(function(){
						
					});
				},3000);
			});
		});
	});
	$(".layui-layer-close").unbind("click");
}

function reWeb(){
	layer.confirm(lan.index.panel_reboot_msg,{title:lan.index.panel_reboot_title,closeBtn:2,icon:3},function(){
		var loadT = layer.msg(lan.index.panel_reboot_to,{icon:16,time:0,shade: [0.3, '#000']});
		$.get('/system?action=ReWeb',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:5});
		}).error(function(){
			layer.close(loadT);
			layer.msg(lan.index.panel_reboot_ok,{icon:1});
			setTimeout(function(){
				window.location.reload();
			},3000)
		});
	});
}


//查看网络状态
function GetNetWorkList(rflush){
	var loadT = layer.msg(lan.public.the_get,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=GetNetWorkList','',function(rdata){
		layer.close(loadT);
		var tbody = ""
		for(var i=0;i<rdata.length;i++){
			tbody += "<tr>"
						+"<td>" + rdata[i].type + "</td>"
						+"<td>" + rdata[i].laddr[0]+ ":" + rdata[i].laddr[1] + "</td>"
						+"<td>" + (rdata[i].raddr.length > 1?"<a style='color:blue;' title='"+lan.index.net_dorp_ip+"' href=\"javascript:dropAddress('" + rdata[i].raddr[0] + "');\">"+rdata[i].raddr[0]+"</a>:" + rdata[i].raddr[1]:'NONE') + "</td>"
						+"<td>" + rdata[i].status + "</td>"
						+"<td>" + rdata[i].process + "</td>"
						+"<td>" + rdata[i].pid + "</td>"
					+"</tr>"
		}
		
		if(rflush){
			$("#networkList").html(tbody);
			return;
		}

		layer.open({
			type:1,
			area:['650px','600px'],
			title:lan.index.net_status_title,
			closeBtn:2,
			shift:5,
			shadeClose:true,
			content:"<div class='divtable' style='margin:15px;'>\
					<button class='btn btn-default btn-sm pull-right' onclick='GetNetWorkList(true);' style='margin-bottom:5px;'>"+lan.public.fresh+"</button>\
					<table class='table table-hover table-bordered'>\
						<thead>\
						<tr>\
							<th>"+lan.index.net_protocol+"</th>\
							<th>"+lan.index.net_address_dst+"</th>\
							<th>"+lan.index.net_address_src+"</th>\
							<th>"+lan.index.net_address_status+"</th>\
							<th>"+lan.index.net_process+"</th>\
							<th>"+lan.index.net_process_pid+"</th>\
						</tr>\
						</thead>\
						<tbody id='networkList'>"+tbody+"</tbody>\
					 </table></div>"
		});
	});
}

//进程管理
function GetProcessList(rflush){
	var loadT = layer.msg(lan.index.process_check,{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=GetProcessList','',function(rdata){
		layer.close(loadT);
		var tbody = "";
		for(var i=0;i<rdata.length;i++){
			tbody += "<tr>"
						+"<td>" + rdata[i].pid + "</td>"
						+"<td>" + rdata[i].name + "</td>"
						+"<td>" + rdata[i].cpu_percent + "%</td>"
						+"<td>" + rdata[i].memory_percent + "%</td>"
						+"<td>" + ToSize(rdata[i].io_read_bytes) + '/' + ToSize(rdata[i].io_write_bytes) + "</td>"
						+"<td>" + rdata[i].status + "</td>"
						+"<td>" + rdata[i].threads + "</td>"
						+"<td>" + rdata[i].user + "</td>"
						+"<td><a title='"+lan.index.process_kill_title+"' style='color:red;' href=\"javascript:;\" onclick=\"killProcess(" + rdata[i].pid + ",'"+rdata[i].name+"',this)\">"+lan.index.process_kill+"</a></td>"
					+"</tr>";
		}
		
		if(rflush){
			$("#processList").html(tbody);
			return;
		}

		layer.open({
			type:1,
			area:['70%','600px'],
			title:lan.index.process_title,
			closeBtn:2,
			shift:5,
			shadeClose:true,
			content:"<div class='divtable' style='margin:15px;'>\
					<button class='btn btn-default btn-sm pull-right' onclick='GetProcessList(true);' style='margin-bottom:5px;'>"+lan.public.fresh+"</button>\
					<table class='table table-hover table-bordered'>\
						<thead>\
						<tr>\
							<th>"+lan.index.process_pid+"</th>\
							<th>"+lan.index.process_name+"</th>\
							<th>"+lan.index.process_cpu+"</th>\
							<th>"+lan.index.process_mem+"</th>\
							<th>"+lan.index.process_disk+"</th>\
							<th>"+lan.index.process_status+"</th>\
							<th>"+lan.index.process_thread+"</th>\
							<th>"+lan.index.process_user+"</th>\
							<th>"+lan.index.process_act+"</th>\
						</tr>\
						</thead>\
						<tbody id='processList'>"+tbody+"</tbody>\
					 </table></div>"
		});
	});
}
//结束指定进程
function killProcess(pid,name,obj){
	var that= $(obj).parents('tr');
	layer.confirm(lan.get('process_kill_confirm',[name,pid]),{icon:3,closeBtn:2},function(){
		loadT = layer.msg(lan.index.kill_msg,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/ajax?action=KillProcess','pid='+pid,function(rdata){
			that.remove();
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}

//屏蔽指定IP
function dropAddress(address){
	layer.confirm(lan.index.net_doup_ip_msg,{icon:3,closeBtn:2},function(){
		loadT = layer.msg(lan.index.net_doup_ip_to,{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/firewall?action=AddDropAddress','port='+address+'&ps='+lan.index.net_doup_ip_ps,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}

//修复面板
function repPanel(){
	layer.confirm(lan.index.rep_panel_msg,{title:lan.index.rep_panel_title,closeBtn:2,icon:3},function(){
		var loadT = layer.msg(lan.index.rep_panel_the,{icon:16,time:0,shade: [0.3, '#000']});
		$.get('/system?action=RepPanel',function(rdata){
			layer.close(loadT);
			layer.msg(lan.index.rep_panel_ok,{icon:1});
		}).error(function(){
			layer.close(loadT);
			layer.msg(lan.index.rep_panel_ok,{icon:1});
		});
	});
}
