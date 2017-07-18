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
			//$(this).prev().text("内存释放");
			$("#memory").text("内存释放");
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
		//$(this).prev().text("内存使用率");
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
		//setTimeout("location.reload()",2000);
	})
})

function rocket(sum,m){
	var n = sum-m;
	$(".mem-release").find(".mask span").text(n);
}
//释放内存
function ReMemory(){
	//var loadT = layer.msg('正在处理,请稍候..',{icon:16,time:0,shade: [0.3, '#000']});
	setTimeout(function(){
		$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px'}).html('<span style="display:none">1</span>释放中 <img src="/static/img/ings.gif">');
		$.post('/system?action=ReMemory','',function(rdata){
			//layer.msg(rdata.msg,{icon:rdata.status?1:5});
			var percent = GetPercent(rdata.memRealUsed,rdata.memTotal);
			var memText = rdata.memRealUsed+"/"+rdata.memTotal + " (MB)";
			percent = Math.round(percent);
			$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px'}).html("<span style='display:none'>"+percent+"</span>释放完成");
			setCookie("mem-before",memText);
			var memNull = getCookie("memRealUsed") - rdata.memRealUsed;
			setTimeout(function(){
				if(memNull > 0){
					$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px','line-height':'22px','padding-top':'22px'}).html("<span style='display:none'>"+percent+"</span>已释放<br>"+memNull+"MB");
				}
				else{
					$(".mem-release").find('.mask').css({'color':'#20a53a','font-size':'14px'}).html("<span style='display:none'>"+percent+"</span>状态最佳");
				}
				$(".mem-release").removeClass("mem-action");
				$("#memory").text(memText);
				//layer.msg("已释放"+memNull+"MB，可用"+rdata.memFree+"MB",{icon:1});
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
					$("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span> 磁盘分区['+rdata[i].path+']的可用容量小于1GB，这可能会导致MySQL自动停止，面板无法访问等问题，请及时清理！</p>')
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

//检查配置
function checkConfig(){
	$.get('/system?action=ServiceAdmin&name='+getCookie('serverType')+'&type=test',function(rdata){
		if(rdata.status) return;
		layer.open({
			type:1,
			title:'检测到配置文件错误!',
			area: '600px', 
			shadeClose:false,
			closeBtn:2,
			content:'<div class="setchmod bt-form pd20 pb70">'
					+'<p style="padding: 0 20px 10px;line-height: 24px;">'+rdata.msg+'</p>'
					+'<p style="font-weight:bold;margin-left: 24px;margin-top: 20px;">注意：</p><ul style="padding: 0 20px 10px;margin-top: 3px;" class="help-info-text">'
					+'============================================================================'
					+'<li>请根据以上错误信息排除配置文件错误！</li>'
					+'<li>配置文件有错误的情况下，您添加的站点、域名将无法生效！</li>'
					+'<li>排除配置错误之前请不要重启服务器或apache/nginx，这会导致您的Web服务无法启动！</li>'
					+'<li>若您无法排除错误，请附上错误信息到我们官方论坛发贴求助;<a href="http://www.bt.cn/bbs" target="_blank" style="color:#20a53a"> >>点击求助</a></li>'
					+'</ul>'
					+'<div class="bt-form-submit-btn">'
					+'<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">知道了</button>'
				    +'</div>'
					+'</div>'
		});
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
		$("#core").html(info.cpuNum + " 核心");
		$("#state").html(info.cpuRealUsed);
		var memFree = info.memTotal - info.memRealUsed;
		
		if(memFree < 64){
			$("#messageError").show();
			$("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span> 当前可用物理内存小于64M，这可能导致MySQL自动停止，站点502等错误，请尝试释放内存！</p>')
		}
		
		if(info.isuser > 0){
			$("#messageError").show();
			$("#messageError").append('<p><span class="glyphicon glyphicon-alert" style="color: #ff4040; margin-right: 10px;"></span> 当前面板用户为admin,这可能为面板安全带来风险！<a class="btlink" href="javascript:setUserName();"> [修改]</a></p>')
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
			$("#InterfaceSpeed").html("接口速率： 1.0Gbps");
			$("#upSpeed").html(net.up+' KB');
			$("#downSpeed").html(net.down+' KB');
			$("#downAll").html(ToSize(net.downTotal));
			$("#downAll").attr('title','报文数量:'+net.downPackets)
			$("#upAll").html(ToSize(net.upTotal));
			$("#upAll").attr('title','报文数量:'+net.upPackets)
			$("#core").html(net.cpu[1] + " 核心");
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
			text: '接口流量实时',
			left: 'center',
			textStyle:{
				color:'#888888',
				fontStyle: 'normal',
				fontFamily: '宋体',
				fontSize: 16,
			}
		},
		tooltip: {
			trigger: 'axis'
		},
		legend: {
			data:['上行','下行'],
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
			name: '单位KB/s',
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
			name: '上行',
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
			name: '下行',
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
				name:'上行',
				data: yData
			},{
				name:'下行',
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
			$("#toUpdate").html('<a class="btlink" href="javascript:updateMsg();">立即更新</a>');
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
	var loadT = layer.msg('正在获取版本信息...',{icon:16,time:0,shade: [0.3, '#000']});
	$.get('/ajax?action=UpdatePanel&check=true',function(rdata){
		layer.close(loadT);
		if(rdata.status === false){
			layer.msg(rdata.msg,{icon:1});
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
			title:'升级到['+rdata.version+']',
			area: '400px', 
			shadeClose:false,
			closeBtn:2,
			content:'<div class="setchmod bt-form pd20 pb70">'
					+'<p style="padding: 0 0 10px;line-height: 24px;">'+rdata.updateMsg+'</p>'
					+'<div class="bt-form-submit-btn">'
					+'<button type="button" class="btn btn-danger btn-sm btn-title" onclick="layer.closeAll()">取消</button>'
					+'<button type="button" class="btn btn-success btn-sm btn-title" onclick="updateVersion(\''+rdata.version+'\')" >立即升级</button>'
				    +'</div>'
					+'</div>'
		});
	});
}

//开始升级
function updateVersion(version){
	var loadT = layer.msg('正在升级面板..',{icon:16,time:0,shade: [0.3, '#000']});
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
		
		layer.msg('升级成功!',{icon:1});
		$.get('/system?action=ReWeb',function(){});
		setTimeout(function(){
			window.location.reload();
		},3000);
	}).error(function(){
		layer.msg('升级成功!',{icon:1});
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
	title: '版本更新',
	closeBtn: 2,
	shift: 5,
	shadeClose: false,
	content: '<div class="DrawRecordCon"></div>'	
	})
	$.get('http://www.bt.cn/Api/getUpdateLogs',function(rdata){
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
		title: "安全重启服务器",
		area: ['500px', '280px'],
		closeBtn: 2,
		shadeClose: false,
		content:"<div class='bt-form bt-window-restart'>\
			<div class='pd15'>\
			<p style='color:red; margin-bottom:10px; font-size:15px;'>注意，若您的服务器是一个容器，请取消。</p>\
			<div class='SafeRestart' style='line-height:26px'>\
				<p>安全重启有利于保障文件安全，将执行以下操作：</p>\
				<p>1.停止"+serverType+"服务</p>\
				<p>2.停止MySQL服务</p>\
				<p>3.开始重启服务器</p>\
				<p>4.等待服务器启动</p>\
			</div>\
			</div>\
			<div class='bt-form-submit-btn'>\
				<button type='button' id='web_end_time' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
				<button type='button' id='web_del_send' class='btn btn-success btn-sm btn-title'  onclick='WSafeRestart()'>确定</button>\
			</div>\
		</div>"
	})
}

//重启服务器
function WSafeRestart(){
	var body = '<div class="SafeRestartCode pd15" style="line-height:26px"></div>';
	$(".bt-window-restart").html(body);
	var data = "name="+serverType+"&type=stop";
	$(".SafeRestartCode").html("<p>正在停止"+serverType+"服务...</p>");
	$.post('/system?action=ServiceAdmin',data,function(r1){
		data = "name=mysqld&type=stop";
		$(".SafeRestartCode").html("<p class='c9'>正在停止"+serverType+"服务</p><p>正在停止MySQL服务...</p>");
		$.post('/system?action=ServiceAdmin',data,function(r2){
			$(".SafeRestartCode").html("<p class='c9'>正在停止"+serverType+"服务</p><p class='c9'>正在停止MySQL服务</p><p>开始重启服务器...</p>");
			$.post('/system?action=RestartServer','',function(rdata){
				$(".SafeRestartCode").html("<p class='c9'>正在停止"+serverType+"服务</p><p class='c9'>正在停止MySQL服务</p><p class='c9'>开始重启服务器</p><p>等待服务器启动...</p>");
				var sEver = setInterval(function(){
					$.get("/system?action=GetSystemTotal", function(info) {
						clearInterval(sEver);
						$(".SafeRestartCode").html("<p class='c9'>正在停止"+serverType+"服务</p><p class='c9'>正在停止MySQL服务</p><p class='c9'>开始重启服务器</p><p class='c9'>等待服务器启动</p><p>服务器重启成功!</p>");
						setTimeout(function(){
							layer.closeAll();
						},3000);
					}).error(function(){
						
					});
				},3000);
			}).error(function(){
				$(".SafeRestartCode").html("<p class='c9'>正在停止"+serverType+"服务</p><p class='c9'>正在停止MySQL服务</p><p class='c9'>开始重启服务器</p><p>等待服务器启动...</p>");
				var sEver = setInterval(function(){
					$.get("/system?action=GetSystemTotal", function(info) {
						clearInterval(sEver);
						$(".SafeRestartCode").html("<p class='c9'>正在停止"+serverType+"服务</p><p class='c9'>正在停止MySQL服务</p><p class='c9'>开始重启服务器</p><p class='c9'>等待服务器启动</p><p>服务器重启成功!</p>");
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
	layer.confirm('即将重启面板服务，继续吗？',{title:'重启面板服务',closeBtn:2,icon:3},function(){
		var loadT = layer.msg('正在重启面板服务,请稍候...',{icon:16,time:0,shade: [0.3, '#000']});
		$.get('/system?action=ReWeb',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:5});
		}).error(function(){
			layer.close(loadT);
			layer.msg('面板服务重启成功!',{icon:1});
			setTimeout(function(){
				window.location.reload();
			},3000)
		});
	});
}


//查看网络状态
function GetNetWorkList(rflush){
	var loadT = layer.msg('正在获取...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/ajax?action=GetNetWorkList','',function(rdata){
		layer.close(loadT);
		var tbody = ""
		for(var i=0;i<rdata.length;i++){
			tbody += "<tr>"
						+"<td>" + rdata[i].type + "</td>"
						+"<td>" + rdata[i].laddr[0]+ ":" + rdata[i].laddr[1] + "</td>"
						+"<td>" + (rdata[i].raddr.length > 1?"<a style='color:blue;' title='屏蔽此IP' href=\"javascript:dropAddress('" + rdata[i].raddr[0] + "');\">"+rdata[i].raddr[0]+"</a>:" + rdata[i].raddr[1]:'NONE') + "</td>"
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
			title:'网络状态',
			closeBtn:2,
			shift:5,
			shadeClose:true,
			content:"<div class='divtable' style='margin:15px;'>\
					<button class='btn btn-default btn-sm pull-right' onclick='GetNetWorkList(true);' style='margin-bottom:5px;'>刷新</button>\
					<table class='table table-hover table-bordered'>\
						<thead>\
						<tr>\
							<th>协议</th>\
							<th>本地地址</th>\
							<th>远程地址</th>\
							<th>状态</th>\
							<th>进程</th>\
							<th>PID</th>\
						</tr>\
						</thead>\
						<tbody id='networkList'>"+tbody+"</tbody>\
					 </table></div>"
		});
	});
}

//进程管理
function GetProcessList(rflush){
	var loadT = layer.msg('正在分析...',{icon:16,time:0,shade: [0.3, '#000']});
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
						+"<td><a title='结束此进程' style='color:red;' href=\"javascript:;\" onclick=\"killProcess(" + rdata[i].pid + ",'"+rdata[i].name+"',this)\">结束</a></td>"
					+"</tr>";
		}
		
		if(rflush){
			$("#processList").html(tbody);
			return;
		}

		layer.open({
			type:1,
			area:['70%','600px'],
			title:'进程管理',
			closeBtn:2,
			shift:5,
			shadeClose:true,
			content:"<div class='divtable' style='margin:15px;'>\
					<button class='btn btn-default btn-sm pull-right' onclick='GetProcessList(true);' style='margin-bottom:5px;'>刷新</button>\
					<table class='table table-hover table-bordered'>\
						<thead>\
						<tr>\
							<th>PID</th>\
							<th>名称</th>\
							<th>CPU</th>\
							<th>内存</th>\
							<th>读/写</th>\
							<th>状态</th>\
							<th>线程</th>\
							<th>用户</th>\
							<th>操作</th>\
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
	layer.confirm('结束进程['+pid+']['+name+']后可能会影响服务器的正常运行，继续吗？',{icon:3,closeBtn:2},function(){
		loadT = layer.msg('正在结束进程...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/ajax?action=KillProcess','pid='+pid,function(rdata){
			that.remove();
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}

//屏蔽指定IP
function dropAddress(address){
	layer.confirm('屏蔽此IP后，对方将无法访问本服务器，你可以在【安全】中删除，继续吗？',{icon:3,closeBtn:2},function(){
		loadT = layer.msg('正在屏蔽IP...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/firewall?action=AddDropAddress','port='+address+'&ps=手动屏蔽',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}