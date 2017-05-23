/**
 * 取回数据库列表
 * @param {Number} page	页码
 */
function getData(page,search) {
	//search = search == undefined ? '':search;
	search = $("#SearchValue").prop("value");
	var sUrl = '/data?action=getData';
	var sUrlData='tojs=getData&table=databases&limit=15&p='+page+'&search='+search;
	var loadT = layer.load();
	$.post(sUrl, sUrlData,function(data) {
		layer.close(loadT);
		//构造数据列表
		var Body = '';
		if(data.data == ""){
			Body="<tr><td colspan='7'>当前没有数据库数据</td></tr>";
			$("#DataPage").hide()
		}
		else{
			$("#DataPage").show();
			for (var i = 0; i < data.data.length; i++) {
				if(data.data[i].backup_count==0){
					var isback = "<a href='javascript:;' class='link' onclick=\"DataDetails('"+data.data[i].id+"','"+data.data[i].name+"')\">无打包</a>"
				}else{
					var isback = "<a href='javascript:;' class='link' onclick=\"DataDetails('"+data.data[i].id+"','"+data.data[i].name+"')\">有打包</a>"
				}
				Body += "<tr><td><input type='checkbox' name='id' value='"+data.data[i].id+"'>\
						<td>" + data.data[i].name + "</td>\
						<td>" + data.data[i].name + "</td>\
						<td class='relative'><span class='password' data-pw='"+data.data[i].password+"'>**********</span><span class='glyphicon glyphicon-eye-open cursor pw-ico' style='margin-left:10px'></span><span class='ico-copy cursor btcopy' style='margin-left:10px' title='复制密码' data-pw='"+data.data[i].password+"'></span></td>\
						<td>"+isback+" | <a class='link' href=\"javascript:InputDatabase('"+data.data[i].name+"');\" title='导入数据库'>导入</a></td>\
						<td><a class='linkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
						<td style='text-align:right;'>\
						<a href='javascript:;' class='link' onclick=\"AdminDatabase('"+data.data[i].name+"','"+data.data[i].name+"','"+data.data[i].password+"')\" title='管理数据库'>管理</a> | \
						<a href='javascript:;' class='link' onclick=\"SetDatabaseAccess('"+data.data[i].name+"')\" title='设置访问权限'>权限</a> | \
						<a href='javascript:;' class='link' onclick=\"DataRespwd(0,'"+data.data[i].id+"','"+data.data[i].name+"')\" title='修改数据库密码'>改密</a> | \
						<a href='javascript:;' class='link' onclick=\"DataDelete("+data.data[i].id+",'"+data.data[i].name+"')\" title='删除数据库'>删除</a>\
						</td></tr>"
			}
		}
		//输出数据列表
		$("#DataBody").html(Body);
		//输出分页
		$("#DataPage").html(data.page);
		//备注
		$(".linkbed").click(function(){
			var dataid = $(this).attr("data-id");
			var databak = $(this).text();
			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' name='bak' value='" + databak + "' placeholder='备注信息' onblur='GetBakPost(\"databases\")' />");
			$(".baktext").focus();
		});
		//复制密码
		btcopy();
		showHidePwd();
	});
}

/**
 *添加数据库 
 * @param {Number} sign	操作标识
 * @param {String} name	数据库名
 * @param {String} type	数据库类型
 * @param {Boolean} adduser	是否添加新用户
 * @param {String} bak	备注
 */
function DataAdd(sign){
	if(sign==0){
		var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '480px',
		title: '添加数据库',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<form class='zun-form-new' id='DataAdd'>\
						<div class='line'>\
							<label><span>数据库名</span></label><div class='info-r'><input  type='text' name='name' placeholder='新的数据库名' style='width:70%' />\
							<select name='codeing' style='width:22%'>\
								<option value='utf8'>utf-8</option>\
								<option value='utf8mb4'>utf8mb4</option>\
								<option value='gbk'>gbk</option>\
								<option value='big5'>big5</option>\
							</select>\
							</div>\
						</div>\
						<div class='line'>\
						<label><span>密码</span></label><div class='info-r'><input  type='text' name='password' id='MyPassword' style='width:340px' placeholder='数据库密码' value='"+(RandomStrPwd(10))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(10)'></span></div>\
						</div>\
                        <div class='line'>\
						<label><span>访问权限</span></label>\
						<div class='info-r'>\
						<select id='dataAccess' style='width:100px;'>\
							<option value='127.0.0.1'>本地服务器</option>\
							<option value='%'>所有人</option>\
							<option value='ip'>指定IP</option>\
						</select>\
						<input type='text' name='address' placeholder='请输入允许访问的IP地址' style='width:230px;display:none;' />\
						</div>\
						</div>\
						<div class='line' style='display:none'>\
						<label><span>备注</span></label><div class='info-r'><input type='text' name='ps' placeholder='数据库备注' /></div>\
						</div>\
                        <div class='submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
					        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"DataAdd(1)\" >提交</button>\
				        </div>\
				      </form>"
		});
		
		$("#dataAccess").change(function(){
			var access = $(this).val();
			if(access == 'ip'){
				$("input[name=address]").show().val('');
			}else{
				$("input[name=address]").hide();
			}
		});
	}else{
		var loadT=layer.load({shade:true,shadeClose:false});
		var access = $("#dataAccess").val();
		if(access != 'ip') $("input[name=address]").val(access);
		var data = $("#DataAdd").serialize();
		$.post('/database?action=AddDatabase',data,function(rdata){
			if(rdata.status){
				getData(1);
				layer.closeAll();
				layer.msg(rdata.msg,{icon:1});
			}else{
				layer.closeAll();
				layer.msg(rdata.msg,{icon:2});
			}
		});
	}
}
/**
 *设置数据库密码 
 * @param {Number} sign	操作标识
 * @param {String} passwd	数据库新密码
 */
function DataSetuppwd(sign, passwd) {
		if (sign == 0) {
			$.post('/data?action=getKey','table=config&key=mysql_root&id=1',function(rdata){
				var mypasswd=rdata;
				var index = layer.open({
				type: 1,
				skin: 'demo-class',
				area: '500px',
				title: '设置数据库密码',
				closeBtn: 2,
				shift: 5,
				shadeClose: false,
				content: "<div class='zun-form-new'' id='DataSetuppwd'>\
						<div class='line'>\
						<label style='width:14%'><span>root密码:</span></label><div class='info-r'><input id='MyPassword' type='text' name='password' value='"+mypasswd+"' style='width:350px' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(16)'></span>\
						</div></div>\
				        <div class='submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
					        <button type='button' id='PostPwBtn' class='btn btn-success btn-sm btn-title' onclick='DataSetuppwd(1)' >提交</button>\
				        </div>\
				      </div>"
			});
			RandomStrPwd(16);
			$("#MyPassword").focus().keyup(function(e){
				if(e.keyCode == 13) $("#PostPwBtn").click();
			});
		});			
		} else {
			var loadT=layer.msg('正在处理,请稍候...',{icon:16,time:0});
			var newPassword = $("#MyPassword").val();
			var data = 'password='+newPassword;
			$.post('/database?action=SetupPassword',data,function(rdata){
				if(rdata.status){
					getData(1);
					layer.closeAll();
					layer.msg(rdata.msg,{icon:1});
					setTimeout(function(){window.location.reload();},3000);
				}else{
					layer.close(loadT);
					layer.msg(rdata.msg,{icon:2});
				}
			});
		}
}
/**
 * 重置数据库密码
 * @param {Number} sign	操作标识
 * @param {String} passwd	数据库密码
 */
function DataRespwd(sign,id,username){
	if(sign==0){
		layer.open({
			type:1,
			skin:'demo-class',
			area:'500px',
			title:'修改数据库密码',
			closeBtn:2,
			shift:5,
			shadeClose:false,
			content:"<form class='zun-form-new' id='DataRespwd'>\
						<div class='line'>\
						<input type='text' name='id' value='"+id+"' hidden />\
						<label><span>用户名:</span></label><div class='info-r'><input type='text' name='username' value='"+username+"' readonly='readonly'/>\
						</div></div>\
						<div class='line'>\
						<label><span>新密码:</span></label><div class='info-r'><input type='text' name='password' placeholder='新的数据库密码' />\
						</div></div>\
				        <div class='submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
					        <button type='button' class='btn btn-success btn-sm btn-title' onclick='DataRespwd(1)' >提交</button>\
				        </div>\
				      </form>"
		});
		return;
	}
	layer.confirm("您确定要修改数据库的密码吗?",{title:'数据库管理',closeBtn:2},function(index){
			if(index>0){
				var loadT=layer.load({shade:true,shadeClose:false});
				var data = $("#DataRespwd").serialize();
				$.post('/database?action=ResDatabasePassword',data,function(rdata){
					getData(1);
					layer.closeAll();
					layer.msg(rdata.msg,{icon:rdata.status?1:2});
				});
			}
		});
	
}
/**
 *数据库管理详细信息 
 * @param {Number} id	数据库编号
 * @param {String} dataname	数据库名称
 */
function DataDetails(id,dataname,page){
	if(page == undefined){
		page = '1';
	}
	var loadT = layer.msg('获取中...',{icon:16,time:0});
	$.post('/data?action=getFind','table=databases&id='+id,function(rdata){
		$.post('/data?action=getData','table=backup&search='+id+'&limit=5&p=1&type=1&tojs=DataDetails&p='+page,function(frdata){
			layer.close(loadT);
			var ftpdown = '';
			var body='';
			var port;
			
			frdata.page = frdata.page.replace(/'/g,'"').replace(/DataDetails\(/g,"DataDetails(" + id + ",0,");
			for(var i=0;i<frdata.data.length;i++){
				if(frdata.data[i].type == '0') continue;
				if(frdata.data[i].filename.length < 12){
					var ftpdown = "<a class='link' href='/cloud?filename="+frdata.data[i].filename+"&name="+ frdata.data[i].name+"' target='_blank'>下载</a>";
				}else{
					var ftpdown = "<a class='link' herf='javascrpit:;' onclick=\"RecoveryData('"+frdata.data[i].filename+"','"+dataname+"')\">恢复</a> | <a class='link' href='/download?filename="+frdata.data[i].filename+"&name="+ frdata.data[i].name+"' target='_blank'>下载</a>";
				}
				
				 body += "<tr><td><span class='glyphicon glyphicon-file'></span>"+frdata.data[i].name+"</td>\
								<td>"+(ToSize(frdata.data[i].size))+"</td>\
								<td>"+frdata.data[i].addtime+"</td>\
								<td style='color:#bbb;text-align:right'>\
								"+ftpdown+" | <a class='link' herf='javascrpit:;' onclick=\"DataBackupDelete('"+id+"','"+frdata.data[i].id+"')\">删除</a>\
								</td>\
							</tr>"
			}
			
			
			if(dataname == 0){
				var sBody = "<table width='100%' id='DataBackupList' class='table table-hover'>\
							<thead><tr><th>文件名称</th><th>文件大小</th><th>打包时间</th><th width='140px' class='text-right'>操作</th></tr></thead>\
							<tbody id='DataBackupBody' class='list-list'>"+body+"</tbody>\
							</table>"
				$("#DataBackupList").html(sBody);
				$(".page").html(frdata.page);
				return;
			}
			layer.closeAll();
			layer.open({
					type: 1,
					skin: 'demo-class',
					area: '700px',
					title: '数据库备份详情',
					closeBtn: 2,
					shift: 5,
					shadeClose: false,
					content:"<form class='zun-form' id='DataBackup' style='max-width:98%'>\
							<button class='btn btn-success btn-sm' style='margin-right:10px' type='button' onclick=\"DataBackup(" + rdata.id + ",'" + dataname + "')\">打包</button>\
							</form>\
							<div class='divtable' style='margin:10px 17px 17px'><table width='100%' id='DataBackupList' class='table table-hover' style='margin-bottom:0'>\
							<thead><tr><th>备份名称</th><th>文件大小</th><th>备份时间</th><th class='text-right'>操作</th></tr></thead>\
							<tbody id='DataBackupBody' class='list-list'>"+body+"</tbody>\
							</table><div class='page'>"+frdata.page+"</div></div>"
			});
		});
	});
}
//恢复数据库备份
function RecoveryData(fileName,dataName){
	layer.confirm("数据库将被覆盖,继续吗?",{title:'导入数据',closeBtn:2},function(index){
		var loadT =layer.msg('正在导入，请稍候...', {icon:16,time:0,shade: [0.3, '#000']});
		$.post('/database?action=InputSql','file='+fileName+'&name='+dataName,function(rdata){
			layer.close(loadT);
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
	});
}
/**
 *设置数据库备份 
 * @param {Number} id	数据库编号
 * @param {String} dataname	数据库名称
 */
function DataBackup(id,dataname){
	var loadT =layer.msg('正在备份，请稍候...', {icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=ToBackup', "id="+id, function(rdata) {
		if (rdata.status == true) {
			layer.closeAll();
			DataDetails(id,dataname);
			layer.msg('操作成功', {
				icon: 1
			});
		} else {
			layer.closeAll();
			DataDetails(id,dataname);
			layer.msg('操作失败', {
				icon:2
			});
		}
	});
}

/**
 *删除数据库备份 
 * @param {Number} id	数据库编号
 * @param {String} dataname	数据库名称
 */
function DataBackupDelete(typeid,id,dataname){
	layer.confirm("真的要删除备份文件吗?",{title:'删除备份',closeBtn:2},function(index){
		var loadT=layer.load({shade:true,shadeClose:false});
		$.post('/database?action=DelBackup','id='+id,function(frdata){
			layer.closeAll();
			layer.msg(frdata.msg,{icon:frdata.status?1:2});
			DataDetails(typeid,dataname);
		});
	});
}
/**
 *删除数据库 
 * @param {Number} id	数据编号
 */

function DataDelete(id,name){
	layer.open({
		type: 1,
	    title: "删除数据库["+name+"]",
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='zun-form-new webDelete'>\
	    	<p>一旦删除将无法恢复！您确定要删除该数据库吗？</p>\
			<div class='vcode'>计算结果：<span class='text'></span>=<input type='text' id='vcodeResult' value=''></div>\
	    	<div class='submit-btn' style='margin-top:15px'>\
				<button type='button' id='web_end_time' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
		        <button type='button' id='web_del_send' class='btn btn-success btn-sm btn-title'  onclick=\"ftpall('"+id+"','"+name+"')\">提交</button>\
	        </div>\
	    </div>"
	})
	randomSum();
}
//随机生成验证计算
function randomSum(){
	var a = Math.round(Math.random()*9+1);
	var b = Math.round(Math.random()*9+1);
	var sum = '';
	sum = a + b;
	$(".vcode .text").text(a+' + '+b);
	setCookie("vcodesum",sum);
	$("#vcodeResult").focus().keyup(function(e){
		if(e.keyCode == 13) $("#web_del_send").click();
	});
}
//删除操作
function ftpall(id,name){
	var sum = $("#vcodeResult").val();
	if(sum == undefined || sum ==''){
		layer.msg("输入计算结果，否则无法删除");
		return;
	}
	else{
		if(sum == getCookie("vcodesum")){
			var loadT = layer.load();
			//'/database?action=DelLiteTable','table=databases'
			$.post('/database?action=DeleteDatabase','id='+id+'&name='+name,function(frdata){
				getData(1);
				layer.closeAll();
				layer.msg(frdata.msg,{icon:frdata.status?1:2});
			});
		}
		else{
			layer.msg("计算错误，请重新计算");
			return;
		}
	}
}

/**
 * 选中项操作
 */
function goSet(num){
	//取选中对象
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data='';
	var a = '';
	var count = 0;
	//构造POST数据
	for(var i=0;i<len;i++){
		if(el[i].checked == true && el[i].value != 'on'){
			data += a+count+'='+el[i].value;
			a = '&';
			count++;
		}
	}
	//判断操作类别
	if(num==1){
		reAdd(data);
	}
	else if(num==2){
		shift(data);
	}
}



//重载MySQL配置
function ReloadMySQL(){
	layer.msg('已重载MySQL配置!',{icon:1});
	$.post('/database?action=ReloadMySQL','',function(rdata){});
}

Date.prototype.format = function(format)
{
	 var o = {
	 "M+" : this.getMonth()+1, //month
	 "d+" : this.getDate(),    //day
	 "h+" : this.getHours(),   //hour
	 "m+" : this.getMinutes(), //minute
	 "s+" : this.getSeconds(), //second
	 "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
	 "S" : this.getMilliseconds() //millisecond
	 }
	 if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
	 (this.getFullYear()+"").substr(4 - RegExp.$1.length));
	 for(var k in o)if(new RegExp("("+ k +")").test(format))
	 format = format.replace(RegExp.$1,
	 RegExp.$1.length==1 ? o[k] :
	 ("00"+ o[k]).substr((""+ o[k]).length));
	 return format;
}
//时间戳到格式日期
function getLocalTime(tm) {
	return new Date(parseInt(tm) * 1000).format("yyyy/MM/dd hh:mm:ss");
}


//取扩展名
function GetExtName(fileName,oext){
	var extArr = fileName.split(".");
	var exts = ['conf','sh','cnf','pl','so','passwd','cshrc','deny','cache','init','po','ext2','ext3','ext4','i686','img','gz','efi','old','pid','lock','frm','opt','err','MYI','MYD','CSM'];
	var extLastName = extArr[extArr.length - 1];
	if(oext) return extLastName;
	if(extArr.length<2 || extLastName.length>5 || extLastName.length < 2){
		return "file";
	}
	for(var i=0; i<exts.length; i++){
		if(exts[i]==extLastName){
			return "file";
		}
	}
	return extLastName;
}

//导入数据库
function InputDatabase(name){
	var path = getCookie('backup_path') + "/database";
	$.post('/files?action=GetDir','path='+path,function(rdata){
		var Body = '';
		for (var i = 0; i < rdata.FILES.length; i++) {
			if(rdata.FILES[i] == null) continue;
			var fmp = rdata.FILES[i].split(";");
			var ext = GetExtName(fmp[0],true);
			
			if(ext != 'sql' && ext != 'zip' && ext != 'gz' && ext != 'tgz') continue;
			Body += "<tr>\
						<td class='column-name'><span class='ico ico-"+ext+"'></span><a class='text'>" + fmp[0] + "</a></td>\
						<td>" + ((fmp[2].length > 11)?fmp[2]:getLocalTime(fmp[2])) + "</td>\
						<td>" + (ToSize(fmp[1])) + "</td>\
						<td class='editmenu'>\
							<a class='link' href='javascript:;' onclick=\"RecoveryData('" + rdata.PATH +"/"+ fmp[0] + "','"+name+"')\">导入</a>\
						</span></td>\
					</tr>";
		}
		layer.open({
				type: 1,
				skin: 'demo-class',
				area: '600px',
				title: '从文件导入数据',
				closeBtn: 2,
				shift: 5,
				shadeClose: false,
				content: '<div style="padding:10px">'
							+'<button class="btn btn-default btn-sm" onclick="UploadFiles(\''+name+'\')">从本地上传</button>'
							+'<div class="divtable" style="max-height:300px; overflow:auto">'
								+'<table class="table table-hover">'
									+'<thead>'
										+'<tr>'
											+'<th>文件名</th>'
											+'<th>修改时间</th>'
											+'<th>大小</th>'
											+'<th>操作</th>'
										+'</tr>'
									+'</thead>'
									+'<tbody>'+Body+'</tbody>'
								+'</table>'
							+'</div>'
							+'<ul class="help-info-text">'
							   +'<li>仅支持sql、zip、(tar.gz|gz|tgz)</li>'
							   +'<li>zip、tar.gz压缩包结构：test.zip或test.tar.gz压缩包内，必需包含test.sql</li>'
							   +'<li>若文件过大，您还可以使用SFTP工具，将数据库文件上传到'+getCookie('backup_path')+'/database</li>'
							+'</ul>'
						+'</div>'
		});
	});
}


//上传文件
function UploadFiles(name){
	var path = getCookie('backup_path') + "/database/";
	var index = layer.open({
		type:1,
		closeBtn: 2,
		title:'上传文件 --- <span style="color:red;">请上传sql或zip或tar.gz压缩包</span>',
		area: ['500px','500px'], 
		shadeClose:false,
		content:'<div class="fileUploadDiv"><input type="hidden" id="input-val" value="'+path+'" />\
				<input type="file" id="file_input"  multiple="true" autocomplete="off" />\
				<button type="button"  id="opt" autocomplete="off">添加文件</button>\
				<button type="button" id="up" autocomplete="off" >开始上传</button>\
				<span id="totalProgress" style="position: absolute;top: 7px;right: 147px;"></span>\
				<span style="float:right;margin-top: 9px;">\
				<font>文件编码:</font>\
				<select id="fileCodeing" >\
					<option value="byte">二进制</option>\
					<option value="utf-8">UTF-8</option>\
					<option value="gb18030">GB2312</option>\
				</select>\
				</span>\
				<button type="button" id="filesClose" autocomplete="off">关闭</button>\
				<ul id="up_box"></ul></div>'
	});
	$("#filesClose").click(function(){
		layer.closeAll();
		InputDatabase(name);
	});
	UploadStart(true);
}


//设置访问权限
function SetDatabaseAccess(dataName,action){
	if(action == 1){
		var access = $("#dataAccess").val();
		if(access == 'ip') access = $("input[name=address]").val();
		layer.msg('正在处理...',{icon:16,time:0,shade: [0.3, '#000']});
		$.post('/database?action=SetDatabaseAccess','name='+dataName+'&access='+access,function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		});
		return;
	}
	
	
	$.post('/database?action=GetDatabaseAccess','name='+dataName,function(rdata){
		if(rdata == null){
			layer.msg('此数据库不能修改访问权限!',{icon:2});
			return;
		}
		layer.open({
			type: 1,
			skin: 'demo-class',
			area: '480px',
			title: '设置数据库权限['+dataName+']',
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: "<form class='zun-form-new' id='DatabaseAccess'>\
	                        <div class='line'>\
							<label><span>访问权限</span></label>\
							<div class='info-r'>\
							<select id='dataAccess' style='width:100px;'>\
								<option value='127.0.0.1' "+(rdata.msg[1] == '127.0.0.1'?'selected':'')+">本地服务器</option>\
								<option value='%' "+(rdata.msg[1] == '%'?'selected':'')+">所有人</option>\
								<option value='ip' "+((rdata.msg[1] != '127.0.0.1' && rdata.msg[1] != '%')?'selected':'')+">指定IP</option>\
							</select>\
							<input type='text' name='address' placeholder='请输入允许访问的IP地址' value='"+rdata.msg[1]+"' style='width:230px;"+((rdata.msg[1] != '127.0.0.1' && rdata.msg[1] != '%')?'':'display:none;')+"' />\
							</div>\
							</div>\
	                        <div class='submit-btn'>\
								<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
						        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"SetDatabaseAccess('"+dataName+"',1)\" >确定</button>\
					        </div>\
					      </form>"
		});
		
		$("#dataAccess").change(function(){
			var access = $(this).val();
			if(access == 'ip'){
				$("input[name=address]").show().val('');
			}else{
				$("input[name=address]").hide();
			}
		});
	});
}

//同步到数据库
function SyncToDatabases(type){
	//取选中对象
	var el = document.getElementsByTagName('input');
	var len = el.length;
	var data='';
	var a = '';
	var count = 0;
	//构造POST数据
	for(var i=0;i<len;i++){
		if(el[i].checked == true && el[i].value != 'on'){
			data += a+count+'='+el[i].value;
			a = '&';
			count++;
		}
	}
	
	var loadT = layer.msg('正在同步...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=SyncToDatabases&type='+type,data,function(rdata){
		layer.close(loadT);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

//从数据库中获取
function SyncGetDatabases(){
	var loadT = layer.msg('正在同步...',{icon:16,time:0,shade: [0.3, '#000']});
	$.post('/database?action=SyncGetDatabases',function(rdata){
		layer.close(loadT);
		getData(1);
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
	});
}

/**
 * 全选/反选
 */
$("#setBox").click(function() {
	if ($(this).prop("checked")) {
		$("input[name=id]").prop("checked", true);
	} else {
		$("input[name=id]").prop("checked", false);
	}
});


//管理数据库
function AdminDatabase(name,username,password){
	if($("#toPHPMyAdmin").attr('action').indexOf('phpmyadmin') == -1){
		layer.msg('请选安装phpMyAdmin',{icon:2,shade: [0.3, '#000']})
		setTimeout(function(){ window.location.href = '/soft'; },3000);
		return;
	}
	
	$("#db").val(name);
	$("#pma_username").val(username);
	$("#pma_password").val(password);
	$("#toPHPMyAdmin").submit();
}

$(".safe .tipstitle").mouseover(function(){
var title = $(this).attr("data-title");
layer.tips(title, this, {
    tips: [1, '#3c8dbc'],
    time:0
})
}).mouseout(function(){
	$(".layui-layer-tips").remove();
})
$(".btn-more").hover(function(){
	$(this).addClass("open");
},function(){
	$(this).removeClass("open");
});
