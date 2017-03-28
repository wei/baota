/**
 * 取回FTP数据列表
 * @param {Number} page   当前页
 */
function getFtp(page,search) {
	search = search == undefined ? '':search;
	var sUrl = '/data?action=getData'
	var data = 'tojs=getFtp&tab=ftps&limit=10&p='+page+'&search='+search;
	var loadT = layer.load();
	$.post(sUrl,data, function(data){
		layer.close(loadT);
		//构造数据列表
		var Body = '';
		for (var i = 0; i < data.data.length; i++) {
			if(data.data[i].status == '1'){
				var ftp_status = "<a href='javascript:;' title='停止这个帐号' onclick=\"ftpStop("+data.data[i].id+",'"+data.data[i].name+"')\"><span style='color:#5CB85C'>已启用 </span> <span style='color:#5CB85C' class='glyphicon glyphicon-pause'></span></a>";
			}else{
				var ftp_status = "<a href='javascript:;' title='启用这个帐号' onclick=\"ftpStart("+data.data[i].id+",'"+data.data[i].name+"')\"><span style='color:red'>已停用 </span> <span style='color:red;' class='glyphicon glyphicon-play'></span></a>";;
			}
			Body +="<tr><td style='display:none'><input type='checkbox' name='id' value='"+data.data[i].id+"'></td>\
					<td>"+data.data[i].name+"</td>\
					<td class='relative'><span class='password' data-pw='"+data.data[i].password+"'>**********</span><span class='glyphicon glyphicon-eye-open cursor pw-ico' style='margin-left:10px'></span><span class='ico-copy cursor btcopy' style='margin-left:10px' title='复制密码' data-pw='"+data.data[i].password+"'></span></td>\
					<td>"+ftp_status+"</td>\
					<td><a class='link' title='打开目录' href=\"javascript:openPath('"+data.data[i].path+"');\">"+data.data[i].path+"</a></td>\
					<td><a class='linkbed' href='javascript:;' data-id='"+data.data[i].id+"'>" + data.data[i].ps + "</a></td>\
					<td style='text-align:right; color:#bbb'>\
                       <a href='javascript:;' class='link' onClick=\"ftpEditSet("+data.data[i].id+",'"+data.data[i].name+"','"+data.data[i].password+"')\">改密 </a>\
                        | <a href='javascript:;' class='link' onclick=\"ftpDelete('"+data.data[i].id+"','"+data.data[i].name+"')\" title='删除FTP'>删除</a>\
                    </td></tr>"                 			
		}
		//输出数据列表
		$("#ftpBody").html(Body);
		//输出分页
		$("#ftpPage").html(data.page);
		//备注
		$(".linkbed").click(function(){
			var dataid = $(this).attr("data-id");
			var databak = $(this).text();
			$(this).hide().after("<input class='baktext' type='text' data-id='"+dataid+"' name='bak' value='" + databak + "' placeholder='备注信息' onblur='GetBakPost(\"ftps\")' />");
			$(".baktext").focus();
		});
		//复制密码
		btcopy();
		showHidePwd();
	});
}

/**
 *添加FTP帐户
 * @param {Number} type	添加类型
 */
function ftpAdd(type) {
	if (type == 1) {
		var loadT = layer.load({
			shade: true,
			shadeClose: false
		});
		var data = $("#ftpAdd").serialize();
		$.post('/ftp?action=AddUser', data, function(rdata) {
			if (rdata.status) {
				getFtp(1);
				layer.closeAll();
				layer.msg(rdata.msg, {
					icon: 1
				});
			} else {
				getFtp(1);
				layer.closeAll();
				layer.msg(rdata.msg, {
					icon: 5
				});
			}
		});
		return true;
	}
	var defaultPath = $("#defaultPath").html();
	var index = layer.open({
		type: 1,
		skin: 'demo-class',
		area: '500px',
		title: '添加FTP帐户',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<form class='zun-form-new' id='ftpAdd'>\
					<div class='line'>\
					<label><span>用户名</span></label>\
					<div class='info-r'><input type='text' id='ftpUser' name='ftp_username' style='width:340px' /></div>\
					</div>\
					<div class='line'>\
					<label><span>密码</span></label>\
					<div class='info-r'><input type='text' name='ftp_password' id='MyPassword' style='width:340px' value='"+(RandomStrPwd(10))+"' /><span title='随机密码' class='glyphicon glyphicon-repeat cursor' onclick='repeatPwd(10)'></span></div>\
					</div>\
					<div class='line'>\
					<label><span>根目录</span></label>\
					<div class='info-r'><input id='inputPath' type='text' name='path' value='"+defaultPath+"/' placeholder='帐户根目录，会自动创建同名目录'  style='width:340px' /><span class='glyphicon glyphicon-folder-open cursor' onclick='ChangePath(\"inputPath\")'></span><p>FTP所指向的目录</p></div>\
					</div>\
                    <div class='line' style='display:none'>\
					<label><span>备注</span></label>\
					<div class='info-r'>\
					<input type='text' name='ps' value='' placeholder='备注信息(小于255个字符)' />\
					</div></div>\
					<div class='submit-btn'>\
						<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
				        <button type='button' class='btn btn-success btn-sm btn-title' onclick=\"ftpAdd(1)\" >提交</button>\
			        </div>\
			      </form>"
	});
	
	
	$("#ftpUser").keyup(function()
	{
		var ftpName = $(this).val();
		if($("#inputPath").val().substr(0,11) == '/www/wwwroo' )
		{
			$("#inputPath").val('/www/wwwroot/'+ftpName);
		}
	});
}


/**
 * 删除FTP帐户
 * @param {Number} id 
 * @param {String} ftp_username  欲被删除的用户名
 * @return {bool}
 */
function ftpDelete(id,ftp_username){
	layer.open({
		type: 1,
	    title: "删除["+ftp_username+"]",
	    area: '350px',
	    closeBtn: 2,
	    shadeClose: true,
	    content:"<div class='zun-form-new webDelete'>\
	    	<p>您真的要删除吗？</p>\
			<div class='vcode'>计算结果：<span class='text'></span>=<input type='text' id='vcodeResult' value=''></div>\
	    	<div class='submit-btn' style='margin-top:15px'>\
				<button type='button' id='web_end_time' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
		        <button type='button' id='web_del_send' class='btn btn-success btn-sm btn-title'  onclick=\"ftpall('"+id+"','"+ftp_username+"')\">提交</button>\
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
function ftpall(id,ftp_username){
	var sum = $("#vcodeResult").val();
	if(sum == undefined || sum ==''){
		layer.msg("输入计算结果，否则无法删除");
		return;
	}
	else{
		if(sum == getCookie("vcodesum")){
			var loadT = layer.load();
			$.get('/ftp.php?action=DeleteUser&id='+id+'&username='+ftp_username,function(rdata){
				layer.closeAll();
				if(rdata['status'] == true){
					getFtp(1);
					layer.msg(rdata.msg,{icon:1});
				}else{
					layer.msg(rdata.msg,{icon:2});
				}
			});
		}
		else{
			layer.msg("计算错误，请重新计算");
			return;
		}
	}
}

//同步
function SyncTo()
{
	var index = layer.open({
			type: 1,
			skin: 'demo-class',
			area: '300px',
			title: '同步FTP',
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: "<br><button class='btn btn-default' onclick='goSet(1)'>同步选中用户</button><br><br>\
						<button class='btn btn-default' onclick='FtpToLocal()'>同步所有用户</button><br><br>\
						<button class='btn btn-default' onclick='FtpToCloud()'>获取服务器上的用户</button><br><br>"
		});
}

//同步到服务器
function FtpToLocal(){
	layer.confirm('将FTP列表同步到服务器？', {
		title:false,
		closeBtn:2,
	    time: 0, 
	    btn: ['确定', '取消']  
    },function(){
		var loadT =layer.msg('正在连接服务器，请稍候...', {icon: 16,time:20000});
		$.get('/Api/SyncData?arg=FtpToLocal',function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		})
	 },function(){
    	layer.closeAll();
    });
}

//从服务器上获取
function FtpToCloud(){
	layer.confirm('您确定要获取么？', {
		title:false,
		closeBtn:2,
        time: 0, 
        btn: ['确定', '取消']   
    },function(){
    	var loadT =layer.msg('正在连接服务器，请稍候...', {icon: 16,time:20000});
		$.get('/Api/SyncData?arg=FtpToCloud',function(rdata){
			layer.closeAll();
			layer.msg(rdata.msg,{icon:rdata.status?1:2});
		})
    },function(){
    	layer.closeAll();
    });
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

function reAdd(data,type){
	if(data == ''){
		layer.msg('请选择至少一个FTP帐户作为操作对象',{icon:2});
		return;
	}
	if(type == 1){
		var ssid = $("#server").prop('value');
		data = data+'&ssid='+ssid;
		var str = '转移FTP帐户操作不可逆，您真的要转移选定FTP帐户到目标服务器吗？';
	}else{
		var str = '即将把您选定的FTP帐户进行重新添加，若FTP帐户在服务器上已存在，此操作将会失败！您真的要同步吗？';
	}
	layer.confirm(str,{closeBtn:2},function(index) {
		if(index <= 0){
			layer.closeAll();
			return;
		}
		var loadT=layer.load({shade:true,shadeClose:false});
		$.post('/Ftp/reAdd',data,function(retuls){
			if(retuls > 0){
				layer.closeAll();
				layer.msg('成功处理 '+retuls+'个FTP帐户',{icon:1});
			}else{
				layer.closeAll();
				layer.msg('操作失败，该FTP已存在!',{icon:2});
			}
			
		});
	});
}

/**
 * 停止FTP帐号
 * @param {Number} id	FTP的ID
 * @param {String} username	FTP用户名
 */
function ftpStop(id, username) {
	layer.confirm("您真的要停止" + username + "的FTP吗?", {
		title: 'FTP服务',
		closeBtn:2
	}, function(index) {
		if (index > 0) {
			var loadT = layer.load({shade: true,shadeClose: false});
			$.get('/ftp.php?action=SetStatus&id=' + id + '&username=' + username + '&status=0', function(rdata) {
				layer.close(loadT);
				if (rdata.status == true) {
					layer.msg(rdata.msg, {icon: 1});
					getFtp(1);
				} else {
					layer.msg(rdata.msg, {icon:2});
				}
			});
		} else {
			layer.closeAll();
		}
	});
}
/**
 * 启动FTP帐号
 * @param {Number} id	FTP的ID
 * @param {String} username	FTP用户名
 */
function ftpStart(id, username) {
	var loadT = layer.load({shade: true,shadeClose: false});
	$.get('/ftp.php?action=SetStatus&id=' + id + '&username=' + username + '&status=1', function(rdata) {
		layer.close(loadT);
		if (rdata.status == true) {
			layer.msg(rdata.msg, {icon: 1});
			getFtp(1);
		} else {
			layer.msg(rdata.msg, {icon:2});
		}
	});
}

/**
 * 修改FTP帐户信息
 * @param {Number} type 修改类型
 * @param {Number} id	FTP编号
 * @param {String} username	FTP用户名
 * @param {String} statu	FTP状态
 * @param {String} group	FTP权限
 * @param {String} passwd	FTP密码
 */
function ftpEditSet(id, username, passwd) {
	if (id != undefined) {
		var index = layer.open({
			type: 1,
			skin: 'demo-class',
			area: '300px',
			title: '修改FTP用户密码',
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: "<form class='zun-form-new' id='ftpEditSet'>\
						<div class='line'>\
						<input type='hidden' name='id' value='" + id + "'/>\
						<input type='hidden' name='ftp_username' value='" + username + "'/>\
						<label><span>用户名:</span></label><div class='info-r'><input  type='text' name='myusername' value='" + username + "' disabled /></div></div>\
						<div class='line'>\
						<label><span>新密码:</span></label><div class='info-r'><input  type='text' name='new_password' value='" + passwd + "' /></div>\
						</div>\
				        <div class='submit-btn'>\
							<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
					        <button type='button' class='btn btn-success btn-sm btn-title' onclick='ftpEditSet()' >提交</button>\
				        </div>\
				      </form>"
		});
	} else {
		layer.confirm("您确定要修改该FTP帐户密码吗?", {
			title: 'FTP服务',
			closeBtn:2
		}, function(index) {
			if (index > 0) {
				var loadT = layer.load({
					shade: true,
					shadeClose: false
				});
				var data = $("#ftpEditSet").serialize();
				$.post('/ftp.php?action=SetUserPassword', data, function(rdata) {
					if (rdata == true) {
						getFtp(1);
						layer.closeAll();
						layer.msg('操作成功', {
							icon: 1
						});
					} else {
						getFtp(1);
						layer.closeAll();
						layer.msg('操作失败', {
							icon:2
						});
					}

				});
			}
		});
	}
}

/**
 *修改FTP服务端口
 */
function ftpPortEdit(port) {
	layer.open({
		type: 1,
		skin: 'demo-class',
		area: '300px',
		title: '修改FTP端口',
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<form class='zun-form-new' id='ftpEditSet'>\
					<div class='line'><input id='ftp_port' type='text' name='ftp_port' value='" + port + "' /></div>\
			        <div class='submit-btn'>\
						<button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button>\
				        <button id='poseFtpPort' type='button' class='btn btn-success btn-sm btn-title'>提交</button>\
			        </div>\
			      </form>"
	});
	 $("#poseFtpPort").click(function(){
	 	var NewPort = $("#ftp_port").val();
	 	ftpPortPost(NewPort);
	 })
}
//修改FTP服务端口
function ftpPortPost(port){
	layer.closeAll();
	var loadT = layer.load(2);
	$.get('/ftp.php?action=setPort&port=' + port, function(rdata) {
			if (rdata.status == true) {
				layer.msg(rdata.msg, {
					icon: 1
				});
				refresh();
			} else {
				layer.msg(rdata.msg, {
					icon:2
				});
			}
			layer.close(loadT);
		});
}