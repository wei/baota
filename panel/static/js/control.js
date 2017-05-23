//默认显示7天周期图表
setTimeout(function(){
	Wday(0,'cpu');
},500);
setTimeout(function(){
	Wday(0,'mem');
},1000);
setTimeout(function(){
	Wday(0,'disk');
},1500);
setTimeout(function(){
	Wday(0,'network');
},2000);
$(".st").hover(function(){
	$(this).next().show();
},function(){
	$(this).next().hide();
	$(this).next().hover(function(){
		$(this).show();
	},function(){
		$(this).hide();
	})
})
$(".searcTime .gt").click(function(){
	$(this).addClass("on").siblings().removeClass("on");
})
$(".cpubtn").click(function(){
	$(this).parents(".searcTime").find("span").removeClass("on");
	$(this).parents(".searcTime").find(".st").addClass("on");
	var b = (new Date($(this).parent().find(".btime").val()).getTime())/1000;
	var e = (new Date($(this).parent().find(".etime").val()).getTime())/1000;
	b = Math.round(b);
	e = Math.round(e);
	cpu(b,e)
})
$(".membtn").click(function(){
	$(this).parents(".searcTime").find("span").removeClass("on");
	$(this).parents(".searcTime").find(".st").addClass("on");
	var b = (new Date($(this).parent().find(".btime").val()).getTime())/1000;
	var e = (new Date($(this).parent().find(".etime").val()).getTime())/1000;
	b = Math.round(b);
	e = Math.round(e);
	mem(b,e)
})
$(".diskbtn").click(function(){
	$(this).parents(".searcTime").find("span").removeClass("on");
	$(this).parents(".searcTime").find(".st").addClass("on");
	var b = (new Date($(this).parent().find(".btime").val()).getTime())/1000;
	var e = (new Date($(this).parent().find(".etime").val()).getTime())/1000;
	b = Math.round(b);
	e = Math.round(e);
	disk(b,e)
})
$(".networkbtn").click(function(){
	$(this).parents(".searcTime").find("span").removeClass("on");
	$(this).parents(".searcTime").find(".st").addClass("on");
	var b = (new Date($(this).parent().find(".btime").val()).getTime())/1000;
	var e = (new Date($(this).parent().find(".etime").val()).getTime())/1000;
	b = Math.round(b);
	e = Math.round(e);
	network(b,e)
})
//指定天数
function Wday(day,name){
	var now = (new Date().getTime())/1000;
	if(day==0){
		var b = (new Date(GetToday() + " 00:00:01").getTime())/1000;
			b = Math.round(b);
		var e = Math.round(now);
	}
	if(day==1){
		var b = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
		var e = (new Date(getBeforeDate(day) + " 23:59:59").getTime())/1000;
		b = Math.round(b);
		e = Math.round(e);
	}
	else{
		var b = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
			b = Math.round(b);
		var e = Math.round(now);
	}
	switch (name){
		case "cpu":
			cpu(b,e);
			break;
		case "mem":
			mem(b,e);
			break;
		case "disk":
			disk(b,e);
			break;
		case "network":
			network(b,e);
			break;
	}
}

function GetToday(){
   var mydate = new Date();
   var str = "" + mydate.getFullYear() + "/";
   str += (mydate.getMonth()+1) + "/";
   str += mydate.getDate();
   return str;
}



//取监控状态
function GetStatus(){
	loadT = layer.msg('正在读取...',{icon:16,time:0})
	$.post('/config?action=SetControl','type=-1',function(rdata){
		layer.close(loadT);
		if(rdata.status){
			$("#openJK").html("<input class='btswitch btswitch-ios' id='ctswitch' type='checkbox' checked><label class='btswitch-btn' for='ctswitch' onclick='SetControl()'></label>")
		}
		else{
			$("#openJK").html("<input class='btswitch btswitch-ios' id='ctswitch' type='checkbox'><label class='btswitch-btn' for='ctswitch' onclick='SetControl()'></label>")
		}
		$("#saveDay").val(rdata.day)
	})
}

GetStatus()

//设置监控状态
function SetControl(act){
	var day = $("#saveDay").val()
	if(day < 1){
		layer.msg('保存天数不合法!',{icon:2});
		return;
	}
	if(act){
		var type = $("#ctswitch").prop('checked')?'1':'0';
	}else{
		var type = $("#ctswitch").prop('checked')?'0':'1';
	}
	
	loadT = layer.msg('正在处理...',{icon:16,time:0})
	$.post('/config?action=SetControl','type='+type+'&day='+day,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

//清理记录
function CloseControl(){
	layer.confirm('您真的清空所有监控记录吗？',{title:'清空记录',closeBtn:2}, function() {
		loadT = layer.msg('正在处理...',{icon:16,time:0})
		$.post('/config?action=SetControl','type=del',function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}



//字节单位转换MB
function ToSizeG(bytes){
	var c = 1024 * 1024;
	var b = 0;
	if(bytes > 0){
		var b = (bytes/c).toFixed(2);
	}
	return b;
}
//定义周期时间
function getBeforeDate(n){
    var n = n;
    var d = new Date();
    var year = d.getFullYear();
    var mon=d.getMonth()+1;
    var day=d.getDate();
    if(day <= n){
		if(mon>1) {
		   mon=mon-1;
		}
		else {
		 year = year-1;
		 mon = 12;
		}
	}
	d.setDate(d.getDate()-n);
	year = d.getFullYear();
	mon=d.getMonth()+1;
	day=d.getDate();
    s = year+"/"+(mon<10?('0'+mon):mon)+"/"+(day<10?('0'+day):day);
    return s;
}
//cpu
function cpu(b,e){
$.get('/ajax?action=GetCpuIo&start='+b+'&end='+e,function(rdata){
	var myChartCpu = echarts.init(document.getElementById('cupview'));
	var xData = [];
	var yData = [];
	//var zData = [];
	
	for(var i = 0; i < rdata.length; i++){
		xData.push(rdata[i].addtime);
		yData.push(rdata[i].pro);
		//zData.push(rdata[i].mem);
	}
	option = {
		tooltip: {
			trigger: 'axis',
			formatter: '{b}<br />{a}: {c}%'
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
			type: 'value',
			name: '百分比',
			boundaryGap: [0, '100%'],
			min:0,
			max: 100,
			splitLine:{
				lineStyle:{
					color:"#ddd"
				}
			},
			axisLine:{
				lineStyle:{
					color:"#666"
				}
			}
		},
		dataZoom: [{
			type: 'inside',
			start: 0,
			end: 100,
			zoomLock:true
		}, {
			start: 0,
			end: 100,
			handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
			handleSize: '80%',
			handleStyle: {
				color: '#fff',
				shadowBlur: 3,
				shadowColor: 'rgba(0, 0, 0, 0.6)',
				shadowOffsetX: 2,
				shadowOffsetY: 2
			}
		}],
		series: [
			{
				name:'CPU',
				type:'line',
				smooth:true,
				symbol: 'none',
				sampling: 'average',
				itemStyle: {
					normal: {
						color: 'rgb(0, 153, 238)'
					}
				},
				data: yData
			}
		]
	};
	myChartCpu.setOption(option);
    window.addEventListener("resize",function(){
		myChartCpu.resize();
	});
})
}

//内存
function mem(b,e){
$.get('/ajax?action=GetCpuIo&start='+b+'&end='+e,function(rdata){
	var myChartMen = echarts.init(document.getElementById('memview'));
	var xData = [];
	//var yData = [];
	var zData = [];
	
	for(var i = 0; i < rdata.length; i++){
		xData.push(rdata[i].addtime);
		//yData.push(rdata[i].pro);
		zData.push(rdata[i].mem);
	}
	option = {
		tooltip: {
			trigger: 'axis',
			formatter: '{b}<br />{a}: {c}%'
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
			type: 'value',
			name: '百分比',
			boundaryGap: [0, '100%'],
			min:0,
			max: 100,
			splitLine:{
				lineStyle:{
					color:"#ddd"
				}
			},
			axisLine:{
				lineStyle:{
					color:"#666"
				}
			}
		},
		dataZoom: [{
			type: 'inside',
			start: 0,
			end: 100,
			zoomLock:true
		}, {
			start: 0,
			end: 100,
			handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
			handleSize: '80%',
			handleStyle: {
				color: '#fff',
				shadowBlur: 3,
				shadowColor: 'rgba(0, 0, 0, 0.6)',
				shadowOffsetX: 2,
				shadowOffsetY: 2
			}
		}],
		series: [
			{
				name:'内存',
				type:'line',
				smooth:true,
				symbol: 'none',
				sampling: 'average',
				itemStyle: {
					normal: {
						color: 'rgb(0, 153, 238)'
					}
				},
				data: zData
			}
		]
	};
	myChartMen.setOption(option);
	window.addEventListener("resize",function(){
		myChartMen.resize();
	});
})
}

//磁盘io
function disk(b,e){
$.get('/ajax?action=GetDiskIo&start='+b+'&end='+e,function(rdata){
	var myChartDisk = echarts.init(document.getElementById('diskview'));
	var rData = [];
	var wData = [];
	var xData = [];
	var yData = [];
	var zData = [];
	
	for(var i = 0; i < rdata.length; i++){
		rData.push(ToSizeG(rdata[i].read_bytes));
		wData.push(ToSizeG(rdata[i].write_bytes));
		xData.push(rdata[i].addtime);
		yData.push(rdata[i].read_count);
		zData.push(rdata[i].write_count);
	}
	option = {
		tooltip: {
			trigger: 'axis'
		},
		legend: {
			data:['读取次数','写入次数','读取字节数','写入字节数']
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
		yAxis: [
			{
				type: 'value',
				name: '次数',
				splitLine:{
					lineStyle:{
						color:"#ddd"
					}
				},
				axisLine:{
					lineStyle:{
						color:"#666"
					}
				}
			},
			{
				type: 'value',
				name: '字节',
				axisLabel: {
					formatter: '{value}'
				},
				splitLine:{
					lineStyle:{
						color:"#ddd"
					}
				},
				axisLine:{
					lineStyle:{
						color:"#666"
					}
				}
			}
		],
		dataZoom: [{
			type: 'inside',
			start: 0,
			end: 100,
			zoomLock:true
		}, {
			start: 0,
			end: 100,
			handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
			handleSize: '80%',
			handleStyle: {
				color: '#fff',
				shadowBlur: 3,
				shadowColor: 'rgba(0, 0, 0, 0.6)',
				shadowOffsetX: 2,
				shadowOffsetY: 2
			}
		}],
		series: [
			{
				name:'读取次数',
				type:'line',
				smooth:true,
				symbol: 'none',
				sampling: 'average',
				itemStyle: {
					normal: {
						color: 'rgb(255, 70, 131)'
					}
				},
				data: yData
			},
			{
				name:'写入次数',
				type:'line',
				smooth:true,
				symbol: 'none',
				sampling: 'average',
				itemStyle: {
					normal: {
						color: 'rgba(46, 165, 186, .7)'
					}
				},
				data: zData
			},
			{
				name:'读取字节数',
				type:'line',
				yAxisIndex: 1,
				data: rData
			},
			{
				name:'写入字节数',
				type:'line',
				yAxisIndex: 1,
				data: wData
			}
		]
	};
	myChartDisk.setOption(option);
	window.addEventListener("resize",function(){
		myChartDisk.resize();
	});
})
}

//网络Io
function network(b,e){
$.get('/ajax?action=GetNetWorkIo&start='+b+'&end='+e,function(rdata){
	var myChartNetwork = echarts.init(document.getElementById('network'));
	var aData = [];
	var bData = [];
	var cData = [];
	var dData = [];
	var xData = [];
	var yData = [];
	var zData = [];
	
	for(var i = 0; i < rdata.length; i++){
		aData.push(rdata[i].total_up);
		bData.push(rdata[i].total_down);
		cData.push(rdata[i].down_packets);
		dData.push(rdata[i].up_packets);
		xData.push(rdata[i].addtime);
		yData.push(rdata[i].up);
		zData.push(rdata[i].down);
	}
	option = {
		tooltip: {
			trigger: 'axis'
		},
		legend: {
			data:['上行','下行']
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
			type: 'value',
			name: '带宽KB/s',
			boundaryGap: [0, '100%'],
			splitLine:{
				lineStyle:{
					color:"#ddd"
				}
			},
			axisLine:{
				lineStyle:{
					color:"#666"
				}
			}
		},
		dataZoom: [{
			type: 'inside',
			start: 0,
			end: 100,
			zoomLock:true
		}, {
			start: 0,
			end: 100,
			handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
			handleSize: '80%',
			handleStyle: {
				color: '#fff',
				shadowBlur: 3,
				shadowColor: 'rgba(0, 0, 0, 0.6)',
				shadowOffsetX: 2,
				shadowOffsetY: 2
			}
		}],
		series: [
			{
				name:'上行',
				type:'line',
				smooth:true,
				symbol: 'none',
				sampling: 'average',
				itemStyle: {
					normal: {
						color: 'rgb(255, 140, 0)'
					}
				},
				data: yData
			},
			{
				name:'下行',
				type:'line',
				smooth:true,
				symbol: 'none',
				sampling: 'average',
				itemStyle: {
					normal: {
						color: 'rgb(30, 144, 255)'
					}
				},
				data: zData
			}
		]
	};
	myChartNetwork.setOption(option);
	window.addEventListener("resize",function(){
		myChartNetwork.resize();
	});
})
}