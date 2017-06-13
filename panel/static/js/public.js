function PageData(c, h, j) {
	var e = h + 1;
	var a = h - 1;
	var b = "";
	var g = "";
	if(h <= 1) {
		b = "disabled";
		a = 1
	}
	if(h >= c.page) {
		g = "disabled";
		e = c.page
	}
	if(h < 4) {
		var d = 1
	} else {
		var d = h - 1
	}
	var f = d + 3;
	if((c.page - h) < 2) {
		f = c.page + 1
	}
	var k = "<li class='" + b + "'><a href='javascript:;' onclick='" + j + "(1)'>&lt;&lt;</a></li><li class='prev " + b + "'><a href='javascript:;' onclick='" + j + "(" + a + ")'>&lt;</a></li>";
	for(d; d < f; d++) {
		if(d == h) {
			k += "<li class='active'><a href='javascript:;' onclick='" + j + "(" + d + ")'>" + d + "</a></li>"
		} else {
			k += "<li><a href='javascript:;' onclick='" + j + "(" + d + ")'>" + d + "</a></li>"
		}
	}
	k += "<li class='next " + g + "'><a href='javascript:;' onclick='" + j + "(" + e + ")'>&gt;</a></li>	<li class='" + g + "'><a href='javascript:;' onclick='" + j + "(" + c.page + ")'>&gt;&gt;</a></li>	<li class='disabled'><a href='javascript:;'>共 " + c.page + " 页  " + c.count + " 条记录</a></li>";
	return k
}
$(document).ready(function() {
	$(".sub-menu a.sub-menu-a").click(function() {
		$(this).next(".sub").slideToggle("slow").siblings(".sub:visible").slideUp("slow")
	})
});

function thenew(b, d, a, c) {
	if(b == null) {
		layer.confirm("初始化数据可能需要几分钟时间，继续吗？", {
			title: "初始化",
			closeBtn: 2
		}, function(e) {
			if(e > 0) {
				var f = layer.load({
					shade: true,
					shadeClose: false
				});
				$.get("/Server/there?id=" + d + "&ssid=" + a + "&ip=" + c, function(g) {
					if(g == true) {
						layer.msg("初始化成功", {
							icon: 1
						});
						location.reload()
					} else {
						layer.msg("初始化失败，没有安装服务", {
							icon: 2
						});
						layer.close(f)
					}
				})
			}
		})
	} else {
		window.location.href = "/Server?ssid=" + a
	}
}

function RandomStrPwd(b) {
	b = b || 32;
	var c = "AaBbCcDdEeFfGHhiJjKkLMmNnPpRSrTsWtXwYxZyz2345678";
	var a = c.length;
	var d = "";
	for(i = 0; i < b; i++) {
		d += c.charAt(Math.floor(Math.random() * a))
	}
	return d
}

function repeatPwd(a) {
	$("#MyPassword").val(RandomStrPwd(a))
}

function refresh() {
	window.location.reload()
}

function GetBakPost(b) {
	$(".baktext").hide().prev().show();
	var c = $(".baktext").attr("data-id");
	var a = $(".baktext").val();
	if(a == "") {
		a = "空"
	}
	setWebPs(b, c, a);
	$("a[data-id='" + c + "']").html(a);
	$(".baktext").remove()
}

function setWebPs(b, e, a) {
	var d = layer.load({
		shade: true,
		shadeClose: false
	});
	var c = "ps=" + a;
	$.post("/data?action=setPs", "table=" + b + "&id=" + e + "&" + c, function(f) {
		if(f == true) {
			if(b == "sites") {
				getWeb(1)
			} else {
				if(b == "ftps") {
					getFtp(1)
				} else {
					getData(1)
				}
			}
			layer.closeAll();
			layer.msg("修改成功", {
				icon: 1
			})
		} else {
			layer.msg("失败，没有权限", {
				icon: 2
			});
			layer.closeAll()
		}
	})
}
$("#setBox").click(function() {
	if($(this).prop("checked")) {
		$("input[name=id]").prop("checked", true)
	} else {
		$("input[name=id]").prop("checked", false)
	}
});
$(".menu-icon").click(function() {
	$(".sidebar-scroll").toggleClass("sidebar-close");
	$(".main-content").toggleClass("main-content-open");
	if($(".sidebar-close")) {
		$(".sub-menu").find(".sub").css("display", "none")
	}
});
var Upload, percentage;

function UsersSetup(a) {
	$.get("/Client/GetClient?id=" + a, function(c) {
		var b = layer.open({
			type: 1,
			skin: "demo-class",
			area: "540px",
			title: "用户设置",
			closeBtn: 2,
			shift: 5,
			shadeClose: false,
			content: '<div class="user-shezhi"><ul class="nav nav-tabs" role="tablist"><li role="presentation" class="active"><a href="#home" aria-controls="home" role="tab" data-toggle="tab">基本</a></li><li role="presentation"><a href="#binding" aria-controls="binding" role="tab" data-toggle="tab">绑定</a></li><li role="presentation"><a href="#messages" aria-controls="messages" role="tab" data-toggle="tab">通知</a></li></ul><div class="tab-content"><div role="tabpanel" class="tab-pane active" id="home"><form id="tabHome" class="zun-form-new"><div class="line"><label><span>新密码</span></label><div class="info-r"><input type="password" name="password1" id="password1" placeholder="请输入新密码"></div></div><div class="line"><label><span>重复密码</span></label><div class="info-r"><input type="password" name="password2" id="password2" placeholder="再输一遍"></div></div><div class="submit-btn"><button type="button" onclick="layer.closeAll()" class="btn btn-danger btn-sm btn-title">取消</button><button type="button" class="btn btn-success btn-sm btn-title">提交</button></div></form></div><div role="tabpanel" class="tab-pane" id="binding"><form id="tabBinding" class="zun-form-new"><div class="line"><label><span>手机</span></label><div class="info-r"><input type="number" name="phone" id="phone" placeholder="11位手机号码"></div></div><div class="line"><label><span>邮箱</span></label><div class="info-r"><input type="email" name="email" id="email" placeholder="abc@qq.com"></div></div></form></div><div role="tabpanel" class="tab-pane" id="messages"><form id="tabMessage" class="zun-form-new"><div class="line"><select name="body" style="width:40%"><option value="异地登陆通知">异地登陆通知</option><option value="站点异常通知">站点异常通知</option><option value="备份通知">备份通知</option><option value="服务器异常通知">服务器异常通知</option></select><select name="type"  style="width:20%"><option value="邮件">邮件</option><option value="短信">短信</option></select><a class="btn btn-default">添加</a></div></form></div></div></div>'
		})
	})
}
Date.prototype.format = function(b) {
	var c = {
		"M+": this.getMonth() + 1,
		"d+": this.getDate(),
		"h+": this.getHours(),
		"m+": this.getMinutes(),
		"s+": this.getSeconds(),
		"q+": Math.floor((this.getMonth() + 3) / 3),
		S: this.getMilliseconds()
	};
	if(/(y+)/.test(b)) {
		b = b.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length))
	}
	for(var a in c) {
		if(new RegExp("(" + a + ")").test(b)) {
			b = b.replace(RegExp.$1, RegExp.$1.length == 1 ? c[a] : ("00" + c[a]).substr(("" + c[a]).length))
		}
	}
	return b
};

function getLocalTime(a) {
	a = a.toString();
	if(a.length > 10) {
		a = a.substring(0, 10)
	}
	return new Date(parseInt(a) * 1000).format("yyyy/MM/dd hh:mm:ss")
}

function ToSize(a) {
	var d = [" B", " KB", " MB", " GB"];
	var e = 1024;
	for(var b = 0; b < d.length; b++) {
		if(a < e) {
			return(b == 0 ? a : a.toFixed(2)) + d[b]
		}
		a /= e
	}
}

function getHelp(a) {
	layer.open({
		type: 2,
		area: ["60%", "95%"],
		skin: "demo-class",
		title: "帮助信息",
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "/Help/helpFind?id=" + a
	})
}

function ChangePath(d) {
	setCookie("SetId", d);
	setCookie("SetName", "");
	var c = layer.open({
		type: 1,
		area: "650px",
		title: "选择目录",
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='changepath'><div class='path-top'><button type='button' class='btn btn-default btn-sm' onclick='BackFile()'><span class='glyphicon glyphicon-share-alt'></span> 返回</button><div class='place' id='PathPlace'>当前路径：<span></span></div></div><div class='path-con'><div class='path-con-left'><dl><dt id='changecomlist' onclick='BackMyComputer()'>计算机</dt></dl></div><div class='path-con-right'><ul class='default' id='computerDefautl'></ul><div class='file-list divtable'><table class='table table-hover' style='border:0 none'><thead><tr class='file-list-head'><th width='40%'>文件名</th><th width='20%'>修改时间</th><th width='10%'>权限</th><th width='10%'>所有者</th><th width='10%'></th></tr></thead><tbody id='tbody' class='list-list'></tbody></table></div></div></div></div><div class='getfile-btn' style='margin-top:0'><button type='button' class='btn btn-default btn-sm pull-left' onclick='CreateFolder()'>新建文件夹</button><button type='button' class='btn btn-danger btn-sm mr5' onclick=\"layer.close(getCookie('ChangePath'))\">关闭</button> <button type='button' class='btn btn-success btn-sm' onclick='GetfilePath()'>选择</button></div>"
	});
	setCookie("ChangePath", c);
	var b = $("#" + d).val();
	tmp = b.split(".");
	if(tmp[tmp.length - 1] == "gz") {
		tmp = b.split("/");
		b = "";
		for(var a = 0; a < tmp.length - 1; a++) {
			b += "/" + tmp[a]
		}
		setCookie("SetName", tmp[tmp.length - 1])
	}
	b = b.replace(/\/\//g, "/");
	GetDiskList(b);
	ActiveDisk()
}

function GetDiskList(b) {
	var d = "";
	var a = "";
	var c = "path=" + b + "&disk=True";
	$.post("/files?action=GetDir", c, function(h) {
		if(h.DISK != undefined) {
			for(var f = 0; f < h.DISK.length; f++) {
				a += "<dd onclick=\"GetDiskList('" + h.DISK[f].path + "')\"><span class='glyphicon glyphicon-hdd'></span>&nbsp;" + h.DISK[f].path + "</dd>"
			}
			$("#changecomlist").html(a)
		}
		for(var f = 0; f < h.DIR.length; f++) {
			var g = h.DIR[f].split(";");
			var e = g[0];
			if(e.length > 20) {
				e = e.substring(0, 20) + "..."
			}
			if(isChineseChar(e)) {
				if(e.length > 10) {
					e = e.substring(0, 10) + "..."
				}
			}
			d += "<tr><td onclick=\"GetDiskList('" + h.PATH + "/" + g[0] + "')\" title='" + g[0] + "'><span class='glyphicon glyphicon-folder-open'></span>" + e + "</td><td>" + getLocalTime(g[2]) + "</td><td>" + g[3] + "</td><td>" + g[4] + "</td><td><span class='delfile-btn' onclick=\"NewDelFile('" + h.PATH + "/" + g[0] + "')\">X</span></td></tr>"
		}
		if(h.FILES != null && h.FILES != "") {
			for(var f = 0; f < h.FILES.length; f++) {
				var g = h.FILES[f].split(";");
				var e = g[0];
				if(e.length > 20) {
					e = e.substring(0, 20) + "..."
				}
				if(isChineseChar(e)) {
					if(e.length > 10) {
						e = e.substring(0, 10) + "..."
					}
				}
				d += "<tr><td title='" + g[0] + "'><span class='glyphicon glyphicon-file'></span>" + e + "</td><td>" + getLocalTime(g[2]) + "</td><td>" + g[3] + "</td><td>" + g[4] + "</td><td></td></tr>"
			}
		}
		$(".default").hide();
		$(".file-list").show();
		$("#tbody").html(d);
		if(h.PATH.substr(h.PATH.length - 1, 1) != "/") {
			h.PATH += "/"
		}
		$("#PathPlace").find("span").html(h.PATH);
		ActiveDisk();
		return
	})
}

function CreateFolder() {
	var a = "<tr><td colspan='2'><span class='glyphicon glyphicon-folder-open'></span> <input id='newFolderName' class='newFolderName' type='text' value=''></td><td colspan='3'><button id='nameOk' type='button' class='btn btn-success btn-sm'>确定</button>&nbsp;&nbsp;<button id='nameNOk' type='button' class='btn btn-default btn-sm'>取消</button></td></tr>";
	if($("#tbody tr").length == 0) {
		$("#tbody").append(a)
	} else {
		$("#tbody tr:first-child").before(a)
	}
	$(".newFolderName").focus();
	$("#nameOk").click(function() {
		var c = $("#newFolderName").val();
		var b = $("#PathPlace").find("span").text();
		newTxt = b.replace(new RegExp(/(\/\/)/g), "/") + c;
		var d = "path=" + newTxt;
		$.post("/files?action=CreateDir", d, function(e) {
			if(e.status == true) {
				layer.msg(e.msg, {
					icon: 1
				})
			} else {
				layer.msg(e.msg, {
					icon: 2
				})
			}
			GetDiskList(b)
		})
	});
	$("#nameNOk").click(function() {
		$(this).parents("tr").remove()
	})
}

function NewDelFile(c) {
	var a = $("#PathPlace").find("span").text();
	newTxt = c.replace(new RegExp(/(\/\/)/g), "/");
	var b = "path=" + newTxt + "&empty=True";
	$.post("/files?action=DeleteDir", b, function(d) {
		if(d.status == true) {
			layer.msg(d.msg, {
				icon: 1
			})
		} else {
			layer.msg(d.msg, {
				icon: 2
			})
		}
		GetDiskList(a)
	})
}

function ActiveDisk() {
	var a = $("#PathPlace").find("span").text().substring(0, 1);
	switch(a) {
		case "C":
			$(".path-con-left dd:nth-of-type(1)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "D":
			$(".path-con-left dd:nth-of-type(2)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "E":
			$(".path-con-left dd:nth-of-type(3)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "F":
			$(".path-con-left dd:nth-of-type(4)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "G":
			$(".path-con-left dd:nth-of-type(5)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "H":
			$(".path-con-left dd:nth-of-type(6)").css("background", "#eee").siblings().removeAttr("style");
			break;
		default:
			$(".path-con-left dd").removeAttr("style")
	}
}

function BackMyComputer() {
	$(".default").show();
	$(".file-list").hide();
	$("#PathPlace").find("span").html("");
	ActiveDisk()
}

function BackFile() {
	var c = $("#PathPlace").find("span").text();
	if(c.substr(c.length - 1, 1) == "/") {
		c = c.substr(0, c.length - 1)
	}
	var d = c.split("/");
	var a = "";
	if(d.length > 1) {
		var e = d.length - 1;
		for(var b = 0; b < e; b++) {
			a += d[b] + "/"
		}
		GetDiskList(a.replace("//", "/"))
	} else {
		a = d[0]
	}
	if(d.length == 1) {}
}

function GetfilePath() {
	var a = $("#PathPlace").find("span").text();
	a = a.replace(new RegExp(/(\\)/g), "/");
	$("#" + getCookie("SetId")).val(a + getCookie("SetName"));
	layer.close(getCookie("ChangePath"))
}

function VirtualDirectories(b, a) {
	layer.open({
		type: 1,
		area: "620px",
		title: "查看目录",
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='changepath'>			<div class='path-top'>				<button id='backPath' type='button' class='btn btn-default btn-sm' ><span class='glyphicon glyphicon-share-alt'></span> 返回</button>				<div class='place' id='xuniPathPlace'>当前路径：<span></span></div>			</div>			<div class='path-con'>				<div class='path-con-right' style='width:100%'>					<table class='table table-hover'>						<thead>							<tr class='file-list-head'>								<th width='60%'>名称</th>								<th width='15%'>大小</th>								<th width='25%'>修改时间</th>							</tr>						</thead>						<tbody id='xunitbody' class='list-list'>						</tbody>					</table>				</div>			</div>		</div>"
	});
	GetVirtualDirectories(b, a);
	$("#backPath").click(function() {
		var c = $("#xuniPathPlace").find("span").text();
		GetVirtualDirectories(-1, c)
	})
}

function GetVirtualDirectories(d, c) {
	if(c == undefined) {
		c = ""
	}
	var b = "";
	var a = "id=" + d + "&path=" + c;
	$.get("/Api/GetDirFormat", a, function(f) {
		for(var e = 0; e < f.DIR.length; e++) {
			b += '<tr><td onclick="GetVirtualDirectories(' + f.DIR[e].id + ",'" + f.PATH + "')\"><span class='glyphicon glyphicon-folder-open'></span>" + f.DIR[e].name + "</td><td>--</td><td>" + f.DIR[e].addtime + "</td></tr>"
		}
		for(var e = 0; e < f.FILES.length; e++) {
			b += "<tr><td><span class='glyphicon glyphicon-file'></span>" + f.FILES[e].filename + "</td><td>" + (ToSize(f.FILES[e].filesize)) + "</td><td>" + f.FILES[e].uptime + "</td></tr>"
		}
		$("#xunitbody").html(b);
		$("#xuniPathPlace").find("span").text(f.PATH)
	})
}

function setCookie(a, c) {
	var b = 30;
	var d = new Date();
	d.setTime(d.getTime() + b * 24 * 60 * 60 * 1000);
	document.cookie = a + "=" + escape(c) + ";expires=" + d.toGMTString()
}

function getCookie(b) {
	var a, c = new RegExp("(^| )" + b + "=([^;]*)(;|$)");
	if(a = document.cookie.match(c)) {
		return unescape(a[2])
	} else {
		return null
	}
}

function aotuHeight() {
	var a = $("body").height() - 40;
	$(".main-content").css("min-height", a)
}
$(function() {
	aotuHeight()
});
$(window).resize(function() {
	aotuHeight()
});

function showHidePwd() {
	var a = "glyphicon-eye-open",
		b = "glyphicon-eye-close";
	$(".pw-ico").click(function() {
		var g = $(this).attr("class"),
			e = $(this).prev();
		if(g.indexOf(a) > 0) {
			var h = e.attr("data-pw");
			$(this).removeClass(a).addClass(b);
			e.text(h)
		} else {
			$(this).removeClass(b).addClass(a);
			e.text("**********")
		}
		var d = $(this).next().position().left;
		var f = $(this).next().position().top;
		var c = $(this).next().width();
		$(this).next().next().css({
			left: d + c + "px",
			top: f + "px"
		})
	})
}

function openPath(a) {
	setCookie("Path", a);
	window.location.href = "/files"
}

function OnlineEditFile(k, f) {
	if(k != 0) {
		var l = $("#PathPlace input").val();
		var h = encodeURIComponent($("#textBody").val());
		var a = $("select[name=encoding]").val();
		layer.msg("正在保存...", {
			icon: 16,
			time: 0
		});
		$.post("/files?action=SaveFileBody", "data=" + h + "&path=" + f + "&encoding=" + a, function(m) {
			if(k == 1) {
				layer.closeAll()
			}
			layer.msg(m.msg, {
				icon: m.status ? 1 : 2
			})
		});
		return
	}
	var e = layer.msg("正在读取文件...", {
		icon: 16,
		time: 0
	});
	var g = f.split(".");
	var b = g[g.length - 1];
	var c = "在线编辑只支持文本与脚本文件，默认UTF8编码，是否尝试打开？";
	if(b == "conf" || b == "cnf" || b == "ini") {
		c = "您正在打开的是一个配置文件，若您不了解配置规则可能导致该配置的程序无法正常使用，继续吗？"
	}
	var d;
	switch(b) {
		case "html":
			var j = {
				name: "htmlmixed",
				scriptTypes: [{
					matches: /\/x-handlebars-template|\/x-mustache/i,
					mode: null
				}, {
					matches: /(text|application)\/(x-)?vb(a|script)/i,
					mode: "vbscript"
				}]
			};
			d = j;
			break;
		case "htm":
			var j = {
				name: "htmlmixed",
				scriptTypes: [{
					matches: /\/x-handlebars-template|\/x-mustache/i,
					mode: null
				}, {
					matches: /(text|application)\/(x-)?vb(a|script)/i,
					mode: "vbscript"
				}]
			};
			d = j;
			break;
		case "js":
			d = "text/javascript";
			break;
		case "json":
			d = "application/ld+json";
			break;
		case "css":
			d = "text/css";
			break;
		case "php":
			d = "application/x-httpd-php";
			break;
		case "tpl":
			d = "application/x-httpd-php";
			break;
		case "xml":
			d = "application/xml";
			break;
		case "sql":
			d = "text/x-sql";
			break;
		case "conf":
			d = "text/x-nginx-conf";
			break;
		default:
			var j = {
				name: "htmlmixed",
				scriptTypes: [{
					matches: /\/x-handlebars-template|\/x-mustache/i,
					mode: null
				}, {
					matches: /(text|application)\/(x-)?vb(a|script)/i,
					mode: "vbscript"
				}]
			};
			d = j
	}
	$.post("/files?action=GetFileBody", "path=" + f, function(s) {
		layer.close(e);
		var u = ["utf-8", "GBK", "GB2312", "BIG5"];
		var n = "";
		var m = "";
		var o = "";
		for(var p = 0; p < u.length; p++) {
			m = s.encoding == u[p] ? "selected" : "";
			n += '<option value="' + u[p] + '" ' + m + ">" + u[p] + "</option>"
		}
		var r = layer.open({
			type: 1,
			shift: 5,
			closeBtn: 2,
			area: ["90%", "90%"],
			title: "在线编辑[" + f + "]",
			content: '<form class="bt-form pd20 pb70"><div class="line"><p style="color:red;margin-bottom:10px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换!			<select class="bt-input-text" name="encoding" style="width: 74px;position: absolute;top: 31px;right: 19px;height: 22px;z-index: 9999;border-radius: 0;">' + n + '</select></p><textarea class="mCustomScrollbar bt-input-text" id="textBody" style="width:100%;margin:0 auto;line-height: 1.8;position: relative;top: 10px;" value="" />			</div>			<div class="bt-form-submit-btn" style="position:absolute; bottom:0; width:100%">			<button type="button" class="btn btn-danger btn-sm btn-editor-close">关闭</button>			<button id="OnlineEditFileBtn" type="button" class="btn btn-success btn-sm">保存</button>			</div>			</form>'
		});
		$("#textBody").text(s.data);
		var q = $(window).height() * 0.9;
		$("#textBody").height(q - 160);
		var t = CodeMirror.fromTextArea(document.getElementById("textBody"), {
			extraKeys: {
				"Ctrl-F": "findPersistent",
				"Ctrl-H": "replaceAll",
				"Ctrl-S": function() {
					$("#textBody").text(t.getValue());
					OnlineEditFile(2, f)
				}
			},
			mode: d,
			lineNumbers: true,
			matchBrackets: true,
			matchtags: true,
			autoMatchParens: true
		});
		t.focus();
		t.setSize("auto", q - 150);
		$("#OnlineEditFileBtn").click(function() {
			$("#textBody").text(t.getValue());
			OnlineEditFile(1, f)
		});
		$(".btn-editor-close").click(function() {
			layer.close(r)
		})
	})
}

function ServiceAdmin(a, b) {
	if(!isNaN(a)) {
		a = "php-fpm-" + a
	}
	var c = "name=" + a + "&type=" + b;
	var d = "";
	switch(b) {
		case "stop":
			d = "停止";
			break;
		case "start":
			d = "启动";
			break;
		case "restart":
			d = "重启";
			break;
		case "reload":
			d = "重载";
			break
	}
	layer.confirm("您真的要" + d + a + "服务吗？", {
		closeBtn: 2
	}, function() {
		var e = layer.msg("正在" + d + a + "服务...", {
			icon: 16,
			time: 0
		});
		$.post("/system?action=ServiceAdmin", c, function(g) {
			layer.close(e);
			var f = g.status ? a + "服务已" + d : a + "服务" + d + "失败!";
			layer.msg(f, {
				icon: g.status ? 1 : 2
			});
			if(b != "reload" && g.status == true) {
				setTimeout(function() {
					window.location.reload()
				}, 1000)
			}
			if(!g.status) {
				layer.msg(g.msg, {
					icon: 2,
					time: 0,
					shade: 0.3,
					shadeClose: true
				})
			}
		}).error(function() {
			layer.close(e);
			layer.msg("操作成功!", {
				icon: 1
			})
		})
	})
}

function GetConfigFile(a) {
	var b = "";
	switch(a) {
		case "mysql":
			b = "/etc/my.cnf";
			break;
		case "nginx":
			b = "/www/server/nginx/conf/nginx.conf";
			break;
		case "pure-ftpd":
			b = "/www/server/pure-ftpd/etc/pure-ftpd.conf";
			break;
		case "apache":
			b = "/www/server/apache/conf/httpd.conf";
			break;
		case "tomcat":
			b = "/www/server/tomcat/conf/server.xml";
			break;
		default:
			b = "/www/server/php/" + a + "/etc/php.ini";
			break
	}
	OnlineEditFile(0, b)
}

function GetPHPStatus(a) {
	if(a == "52") {
		layer.msg("抱歉,不支持PHP5.2", {
			icon: 2
		});
		return
	}
	$.post("/ajax?action=GetPHPStatus", "version=" + a, function(b) {
		layer.open({
			type: 1,
			area: "400",
			title: "PHP负载状态",
			closeBtn: 2,
			shift: 5,
			shadeClose: true,
			content: "<div style='margin:15px;'><table class='table table-hover table-bordered'>						<tr><th>应用池(pool)</th><td>" + b.pool + "</td></tr>						<tr><th>进程管理方式(process manager)</th><td>" + ((b["process manager"] == "dynamic") ? "活动" : "静态") + "</td></tr>						<tr><th>启动日期(start time)</th><td>" + b["start time"] + "</td></tr>						<tr><th>请求数(accepted conn)</th><td>" + b["accepted conn"] + "</td></tr>						<tr><th>请求队列(listen queue)</th><td>" + b["listen queue"] + "</td></tr>						<tr><th>最大等待队列(max listen queue)</th><td>" + b["max listen queue"] + "</td></tr>						<tr><th>socket队列长度(listen queue len)</th><td>" + b["listen queue len"] + "</td></tr>						<tr><th>空闲进程数量(idle processes)</th><td>" + b["idle processes"] + "</td></tr>						<tr><th>活跃进程数量(active processes)</th><td>" + b["active processes"] + "</td></tr>						<tr><th>总进程数量(total processes)</th><td>" + b["total processes"] + "</td></tr>						<tr><th>最大活跃进程数量(max active processes)</th><td>" + b["max active processes"] + "</td></tr>						<tr><th>到达进程上限次数(max children reached)</th><td>" + b["max children reached"] + "</td></tr>						<tr><th>慢请求数量(slow requests)</th><td>" + b["slow requests"] + "</td></tr>					 </table></div>"
		})
	})
}

function GetNginxStatus() {
	$.post("/ajax?action=GetNginxStatus", "", function(a) {
		layer.open({
			type: 1,
			area: "400",
			title: "Nginx负载状态",
			closeBtn: 2,
			shift: 5,
			shadeClose: true,
			content: "<div style='margin:15px;'><table class='table table-hover table-bordered'>						<tr><th>活动连接(Active connections)</th><td>" + a.active + "</td></tr>						<tr><th>总连接次数(accepts)</th><td>" + a.accepts + "</td></tr>						<tr><th>总握手次数(handled)</th><td>" + a.handled + "</td></tr>						<tr><th>总请求数(requests)</th><td>" + a.requests + "</td></tr>						<tr><th>请求数(Reading)</th><td>" + a.Reading + "</td></tr>						<tr><th>响应数(Writing)</th><td>" + a.Writing + "</td></tr>						<tr><th>驻留进程(Waiting)</th><td>" + a.Waiting + "</td></tr>					 </table></div>"
		})
	})
}

function GetNetWorkList() {
	var a = layer.msg("正在获取...", {
		icon: 16,
		time: 0,
		shade: [0.3, "#000"]
	});
	$.post("/ajax?action=GetNetWorkList", "", function(d) {
		layer.close(a);
		var b = "";
		for(var c = 0; c < d.length; c++) {
			b += "<tr><td>" + d[c].type + "</td><td>" + d[c].laddr[0] + ":" + d[c].laddr[1] + "</td><td>" + (d[c].raddr.length > 1 ? "<a style='color:blue;' title='屏蔽此IP' href=\"javascript:dropAddress('" + d[c].raddr[0] + "');\">" + d[c].raddr[0] + "</a>:" + d[c].raddr[1] : "NONE") + "</td><td>" + d[c].status + "</td><td>" + d[c].process + "</td><td>" + d[c].pid + "</td></tr>"
		}
		layer.open({
			type: 1,
			area: ["650px", "600px"],
			title: "网络状态",
			closeBtn: 2,
			shift: 5,
			shadeClose: true,
			content: "<div style='margin:15px;'><table class='table table-hover table-bordered'>						<tr>							<th>协议</th>							<th>本地地址</th>							<th>远程地址</th>							<th>状态</th>							<th>进程</th>							<th>PID</th>						</tr>						<tbody>" + b + "</tbody>					 </table></div>"
		})
	})
}

function GetProcessList() {
	var a = layer.msg("正在分析...", {
		icon: 16,
		time: 0,
		shade: [0.3, "#000"]
	});
	$.post("/ajax?action=GetProcessList", "", function(d) {
		layer.close(a);
		var b = "";
		for(var c = 0; c < d.length; c++) {
			b += "<tr><td>" + d[c].pid + "</td><td>" + d[c].name + "</td><td>" + d[c].cpu_percent + "%</td><td>" + d[c].memory_percent + "%</td><td>" + ToSize(d[c].io_read_bytes) + "/" + ToSize(d[c].io_write_bytes) + "</td><td>" + d[c].status + "</td><td>" + d[c].threads + "</td><td>" + d[c].user + "</td><td><a title='结束此进程' style='color:red;' href=\"javascript:killProcess(" + d[c].pid + ",'" + d[c].name + "');\">结束</a></td></tr>"
		}
		layer.open({
			type: 1,
			area: ["70%", "600px"],
			title: "进程管理",
			closeBtn: 2,
			shift: 5,
			shadeClose: true,
			content: "<div style='margin:15px;'><table class='table table-hover table-bordered'>						<tr>							<th>PID</th>							<th>名称</th>							<th>CPU</th>							<th>内存</th>							<th>读/写</th>							<th>状态</th>							<th>线程</th>							<th>用户</th>							<th>操作</th>						</tr>						<tbody>" + b + "</tbody>					 </table></div>"
		})
	})
}

function killProcess(a, b) {
	layer.confirm("结束进程[" + a + "][" + b + "]后可能会影响服务器的正常运行，继续吗？", {
		closeBtn: 2
	}, function() {
		loadT = layer.msg("正在结束进程...", {
			icon: 16,
			time: 0,
			shade: [0.3, "#000"]
		});
		$.post("/ajax?action=KillProcess", "pid=" + a, function(c) {
			layer.close(loadT);
			layer.msg(c.msg, {
				icon: c.status ? 1 : 2
			})
		})
	})
}

function dropAddress(a) {
	layer.confirm("屏蔽此IP后，对方将无法访问本服务器，你可以在【安全】中删除，继续吗？", {
		closeBtn: 2
	}, function() {
		loadT = layer.msg("正在屏蔽IP...", {
			icon: 16,
			time: 0,
			shade: [0.3, "#000"]
		});
		$.post("/firewall?action=AddDropAddress", "port=" + a + "&ps=手动屏蔽", function(b) {
			layer.close(loadT);
			layer.msg(b.msg, {
				icon: b.status ? 1 : 2
			})
		})
	})
}

function divcenter() {
	$(".layui-layer").css("position", "absolute");
	var c = $(window).width();
	var b = $(".layui-layer").outerWidth();
	var g = $(window).height();
	var f = $(".layui-layer").outerHeight();
	var a = (c - b) / 2;
	var e = (g - f) / 2 > 0 ? (g - f) / 2 : 10;
	var d = $(".layui-layer").offset().left - $(".layui-layer").position().left;
	var h = $(".layui-layer").offset().top - $(".layui-layer").position().top;
	a = a + $(window).scrollLeft() - d;
	e = e + $(window).scrollTop() - h;
	$(".layui-layer").css("left", a + "px");
	$(".layui-layer").css("top", e + "px")
}

function btcopy() {
	$(".btcopy").zclip({
		path: "/static/js/ZeroClipboard.swf",
		copy: function() {
			return $(this).attr("data-pw")
		},
		afterCopy: function() {
			if($(this).attr("data-pw") == "") {
				layer.msg("密码为空", {
					icon: 7,
					time: 1500
				})
			} else {
				layer.msg("复制成功", {
					icon: 1,
					time: 1500
				})
			}
		}
	})
}

function isChineseChar(b) {
	var a = /[\u4E00-\u9FA5\uF900-\uFA2D]/;
	return a.test(b)
}

function SafeMessage(j, h, g, f) {
	if(f == undefined) {
		f = ""
	}
	var d = Math.round(Math.random() * 9 + 1);
	var c = Math.round(Math.random() * 9 + 1);
	var e = "";
	e = d + c;
	sumtext = d + " + " + c;
	setCookie("vcodesum", e);
	layer.open({
		type: 1,
		title: j,
		area: "350px",
		closeBtn: 2,
		shadeClose: true,
		content: "<div class='bt-form webDelete pd20 pb70'><p>" + h + "</p>" + f + "<div class='vcode'>计算结果：<span class='text'>" + sumtext + "</span>=<input type='number' id='vcodeResult' value=''></div><div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm btn-title' onclick='layer.closeAll()'>取消</button> <button type='button' id='toSubmit' class='btn btn-success btn-sm btn-title' >提交</button></div></div>"
	});
	$("#vcodeResult").focus().keyup(function(a) {
		if(a.keyCode == 13) {
			$("#toSubmit").click()
		}
	});
	$("#toSubmit").click(function() {
		var a = $("#vcodeResult").val().replace(/ /g, "");
		if(a == undefined || a == "") {
			layer.msg("输入计算结果，否则无法删除");
			return
		}
		if(a != getCookie("vcodesum")) {
			layer.msg("计算错误，请重新计算");
			return
		}
		g()
	})
}
isAction();

function isAction() {
	hrefs = window.location.href.split("/");
	name = hrefs[hrefs.length - 1];
	if(!name) {
		$("#memuA").addClass("current");
		return
	}
	$("#memuA" + name).addClass("current")
}
var W_window = $(window).width();
if(W_window <= 980) {
	$(window).scroll(function() {
		var a = $(window).scrollTop();
		$(".sidebar-scroll").css({
			position: "absolute",
			top: a
		})
	})
} else {
	$(".sidebar-scroll").css({
		position: "fixed",
		top: "0"
	})
}
$(function() {
	$(".fb-ico").hover(function() {
		$(".fb-text").css({
			left: "36px",
			top: 0,
			width: "80px"
		})
	}, function() {
		$(".fb-text").css({
			left: 0,
			width: "36px"
		})
	}).click(function() {
		$(".fb-text").css({
			left: 0,
			width: "36px"
		});
		$(".zun-feedback-suggestion").show()
	});
	$(".fb-close").click(function() {
		$(".zun-feedback-suggestion").hide()
	});
	$(".fb-attitudes li").click(function() {
		$(this).addClass("fb-selected").siblings().removeClass("fb-selected")
	})
});
$("#dologin").click(function() {
	layer.confirm("您真的要退出面板吗?", {
		closeBtn: 2
	}, function() {
		window.location.href = "/login?dologin=True"
	});
	return false
});

function setPassword(a) {
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		if(p1 == "" || p1.length < 8) {
			layer.msg("面板密码不能少于8位!", {
				icon: 2
			});
			return
		}
		
		//准备弱口令匹配元素
		var checks = ['admin','root','123','456','789','123456','456789','654321','qweasd','asdfghjkl','zxcvbnm','user','password','passwd','panel','linux','centos','ubuntu','abc','xyz'];
		pchecks = 'abcdefghijklmnopqrstuvwxyz1234567890';
		for(var i=0;i<pchecks.length;i++){
			checks.push(pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]);
		}
		
		//检查弱口令
		cps = p1.toLowerCase();
		var isError = "";
		for(var i=0;i<checks.length;i++){
			if(cps.indexOf(checks[i]) != -1){
				isError += '['+checks[i]+'] ';
			}
		}
		
		if(isError != ""){
			layer.msg('面板密码中不能包括弱口令'+isError,{icon:5});
			return;
		}
		
		
		if(p1 != p2) {
			layer.msg("两次输入的密码不一致", {
				icon: 2
			});
			return
		}
		$.post("/config?action=setPassword", "password1=" + p1 + "&password2=" + p2, function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {
					icon: 1
				})
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
		title: "修改密码",
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'><div class='line'><span class='tname' style='width: 25px;'>密码</span><div class='info-r' style='margin-left: 44px;'><input class='bt-input-text' type='text' name='password1' id='p1' value='' placeholder='新的密码' style='width:100%'/></div></div><div class='line'><span class='tname' style='width: 25px;'>重复</span><div class='info-r' style='margin-left: 44px;'><input class='bt-input-text' type='text' name='password2' id='p2' value='' placeholder='再输一次' style='width:100%' /></div></div><div class='bt-form-submit-btn'><span style='float: left;' title='随机密码' class='btn btn-default btn-sm' onclick='randPwd(10)'>随机</span><button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">取消</button> <button type='button' class='btn btn-success btn-sm' onclick=\"setPassword(1)\">修改</button></div></div>"
	});
}


function randPwd(){
	var pwd = RandomStrPwd(12);
	$("#p1").val(pwd);
	$("#p2").val(pwd);
	layer.msg('请在修改前记录好您的新密码!',{time:2000})
}

function setUserName(a) {
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		if(p1 == "" || p1.length < 3) {
			layer.msg("用户名为空或少于3位!", {
				icon: 2
			});
			return
		}
		if(p1 != p2) {
			layer.msg("两次输入的用户名不一致", {
				icon: 2
			});
			return
		}
		$.post("/config?action=setUsername", "username1=" + p1 + "&username2=" + p2, function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {
					icon: 1
				});
				$("input[name='username_']").val(p1)
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
		title: "修改面板用户名",
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'><div class='line'><span class='tname'>用户名</span><div class='info-r'><input class='bt-input-text' type='text' name='password1' id='p1' value='' placeholder='新的用户名' style='width:100%'/></div></div><div class='line'><span class='tname'>重复</span><div class='info-r'><input class='bt-input-text' type='text' name='password2' id='p2' value='' placeholder='再输一次' style='width:100%'/></div></div><div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">取消</button> <button type='button' class='btn btn-success btn-sm' onclick=\"setUserName(1)\">修改</button></div></div>"
	})
}
var openWindow = null;
var downLoad = null;
var speed = null;

function GetReloads() {
	var a = 0;
	speed = setInterval(function() {
		if($("#taskList").html() != "任务列表") {
			clearInterval(speed);
			a = 0;
			return
		}
		a++;
		$.post("/files?action=GetTaskSpeed", "", function(h) {
			if(h.task == undefined) {
				$("#srunning").html("当前没有任务!");
				divcenter();
				return
			}
			var b = "";
			var d = "";
			for(var g = 0; g < h.task.length; g++) {
				if(h.task[g].status == "-1") {
					if(h.task[g].type != "download") {
						var c = "";
						var f = h.msg.split("\n");
						for(var e = 0; e < f.length; e++) {
							c += f[e] + "<br>"
						}
						if(h.task[g].name.indexOf("扫描") != -1) {
							b = "<li><span class='titlename'>" + h.task[g].name + "</span><span class='state'>正在扫描 <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + h.task[g].id + ")\">删除</a></span><span class='opencmd'></span><div class='cmd'>" + c + "</div></li>"
						} else {
							b = "<li><span class='titlename'>" + h.task[g].name + "</span><span class='state'>正在安装 <img src='/static/img/ing.gif'></span><div class='cmd'>" + c + "</div></li>"
						}
					} else {
						b = "<li><div class='line-progress' style='width:" + h.msg.pre + "%'></div><span class='titlename'>" + h.task[g].name + "<a style='margin-left:130px;'>" + (ToSize(h.msg.used) + "/" + ToSize(h.msg.total)) + "</a></span><span class='com-progress'>" + h.msg.pre + "%</span><span class='state'>下载中 <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + h.task[g].id + ")\">删除</a></span></li>"
					}
				} else {
					d += "<li><span class='titlename'>" + h.task[g].name + "</span><span class='state'>等待 | <a style='color:green' href=\"javascript:RemoveTask(" + h.task[g].id + ')">删除</a></span></li>'
				}
			}
			$("#srunning").html(b + d);
			divcenter();
			$(".cmd").scrollTop($(".cmd")[0].scrollHeight)
		}).error(function() {})
	}, 1000)
}

function task() {
	layer.open({
		type: 1,
		title: "<a id='taskList'>任务列表</a>",
		area: "600px",
		closeBtn: 2,
		shadeClose: false,
		content: "<div class='tasklist'><div class='tab-nav'><span class='on'>正在处理</span><span>已完成</span><a href='javascript:ActionTask();' class='btn btn-default btn-sm' style='float: right;margin-top: -3px;' title='若您的任务长时间没有继续，请尝试点此按钮!'>激活队列</a></div><div class='tab-con'><ul id='srunning'></ul><ul id='sbody' style='display:none'></ul></div></div>"
	});
	GetTaskList();
	GetReloads();
	$(".tab-nav span").click(function() {
		var a = $(this).index();
		$(this).addClass("on").siblings().removeClass("on");
		$(".tab-con ul").hide().eq(a).show();
		GetTaskList();
		divcenter()
	})
}

function ActionTask() {
	var a = layer.msg("正在删除...", {
		icon: 16,
		time: 0,
		shade: [0.3, "#000"]
	});
	$.post("/files?action=ActionTask", "", function(b) {
		layer.close(a);
		layer.msg(b.msg, {
			icon: b.status ? 1 : 5
		})
	})
}

function RemoveTask(b) {
	var a = layer.msg("正在删除...", {
		icon: 16,
		time: 0,
		shade: [0.3, "#000"]
	});
	$.post("/files?action=RemoveTask", "id=" + b, function(c) {
		layer.close(a);
		layer.msg(c.msg, {
			icon: c.status ? 1 : 5
		})
	})
}

function GetTaskList(a) {
	a = a == undefined ? 1 : a;
	$.post("/data?action=getData", "tojs=GetTaskList&table=tasks&limit=10&p=" + a, function(g) {
		var e = "";
		var b = "";
		var c = "";
		var f = false;
		for(var d = 0; d < g.data.length; d++) {
			switch(g.data[d].status) {
				case "-1":
					f = true;
					if(g.data[d].type != "download") {
						b = "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state'>正在安装 <img src='/static/img/ing.gif'></span><span class='opencmd'></span><pre class='cmd'></pre></li>"
					} else {
						b = "<li><div class='line-progress' style='width:0%'></div><span class='titlename'>" + g.data[d].name + "<a id='speed' style='margin-left:130px;'>0.0M/12.5M</a></span><span class='com-progress'>0%</span><span class='state'>下载中 <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + g.data[d].id + ")\">删除</a></span></li>"
					}
					break;
				case "0":
					c += "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state'>等待</span> | <a href=\"javascript:RemoveTask(" + g.data[d].id + ")\">删除</a></li>";
					break;
				case "1":
					e += "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state'>" + g.data[d].addtime + "  已完成  耗时" + (g.data[d].end - g.data[d].start) + "秒</span></li>"
			}
		}
		$("#srunning").html(b + c);
		$("#sbody").html(e);
		return f
	})
}

function GetTaskCount() {
	$.post("/ajax?action=GetTaskCount", "", function(a) {
		$(".task").text(a)
	})
}

function setSelectChecked(c, d) {
	var a = document.getElementById(c);
	for(var b = 0; b < a.options.length; b++) {
		if(a.options[b].innerHTML == d) {
			a.options[b].selected = true;
			break
		}
	}
}
GetTaskCount();

function ShowSoftList(){
	layer.open({
		type: 1,
		title: "软件管家",
		area: "70%",
		offset: "100px",
		shadeClose: false,
		content: '<div class="divtable" style="margin: 10px;"><table width="100%" cellspacing="0" cellpadding="0" border="0" class="table table-hover"><thead><tr><th>软件名称</th><th>类型</th><th>版本</th><th>状态</th><th width="90" style="text-align: right;">操作</th></tr></thead><tbody id="softList"></tbody></table></div>'
	});
	GetSoftList()
}

function RecInstall() {
	$.post("/ajax?action=GetSoftList", "", function(l) {
		var c = "";
		var g = "";
		var e = "";
		for(var h = 0; h < l.length; h++) {
			if(l[h].name == "Tomcat") {
				continue
			}
			var o = "";
			var m = "<input id='data_" + l[h].name + "' data-info='" + l[h].name + " " + l[h].versions[0].version + "' type='checkbox' checked>";
			for(var b = 0; b < l[h].versions.length; b++) {
				var d = "";
				if((l[h].name == "PHP" && (l[h].versions[b].version == "5.4" || l[h].versions[b].version == "54")) || (l[h].name == "MySQL" && l[h].versions[b].version == "5.5") || (l[h].name == "phpMyAdmin" && l[h].versions[b].version == "4.4")) {
					d = "selected";
					m = "<input id='data_" + l[h].name + "' data-info='" + l[h].name + " " + l[h].versions[b].version + "' type='checkbox' checked>"
				}
				o += "<option value='" + l[h].versions[b].version + "' " + d + ">" + l[h].name + " " + l[h].versions[b].version + "</option>"
			}
			var f = "<li><span class='ico'><img src='/static/img/" + l[h].name.toLowerCase() + ".png'></span><span class='name'><select id='select_" + l[h].name + "' class='sl-s-info'>" + o + "</select></span><span class='pull-right'>" + m + "</span></li>";
			if(l[h].name == "Nginx") {
				c = f
			} else {
				if(l[h].name == "Apache") {
					g = f
				} else {
					e += f
				}
			}
		}
		c += e;
		g += e;
		g = g.replace(new RegExp(/(data_)/g), "apache_").replace(new RegExp(/(select_)/g), "apache_select_");
		var k = layer.open({
			type: 1,
			title: "推荐安装套件",
			area: ["658px", "423px"],
			closeBtn: 2,
			shadeClose: false,
			content: "<div class='rec-install'><div class='important-title'><p><span class='glyphicon glyphicon-alert' style='color: #f39c12; margin-right: 10px;'></span>我们为您推荐以下一键套件，请按需选择或在 <a href='javascript:jump()' style='color:#20a53a'>所有软件</a> 栏自行选择，如你不懂，请安装LNMP。</p></div><div class='rec-box'><h3>LNMP(推荐)</h3><div class='rec-box-con'><ul class='rec-list'>" + c + "</ul><p class='fangshi'>安装方式：<label data-title='即rpm，安装时间极快（5~10分钟），性能与稳定性略低于编译安装' style='margin-right:0'>极速安装<input type='checkbox' checked></label><label data-title='安装时间长（30分钟到3小时），适合高并发高性能应用'>编译安装<input type='checkbox'></label></p><div class='onekey'>一键安装</div></div></div><div class='rec-box' style='margin-left:16px'><h3>LAMP</h3><div class='rec-box-con'><ul class='rec-list'>" + g + "</ul><p class='fangshi'>安装方式：<label data-title='即rpm，安装时间极快（5~10分钟），性能与稳定性略低于编译安装' style='margin-right:0'>极速安装<input type='checkbox' checked></label><label data-title='安装时间长（30分钟到3小时），适合高并发高性能应用'>编译安装<input type='checkbox'></label></p><div class='onekey'>一键安装</div></div></div></div>"
		});
		$(".fangshi input").click(function() {
			$(this).attr("checked", "checked").parent().siblings().find("input").removeAttr("checked")
		});
		$(".sl-s-info").change(function() {
			var p = $(this).find("option:selected").text();
			var n = $(this).attr("id");
			p = p.toLowerCase();
			$(this).parents("li").find("input").attr("data-info", p)
		});
		$("#apache_select_PHP").change(function() {
			var n = $(this).val();
			j(n, "apache_select_", "apache_")
		});
		$("#select_PHP").change(function() {
			var n = $(this).val();
			j(n, "select_", "data_")
		});

		function j(p, r, q) {
			var n = "4.4";
			switch(p) {
				case "5.2":
					n = "4.0";
					break;
				case "5.3":
					n = "4.0";
					break;
				case "5.4":
					n = "4.4";
					break;
				default:
					n = "4.7"
			}
			$("#" + r + "phpMyAdmin option[value='" + n + "']").attr("selected", "selected").siblings().removeAttr("selected");
			$("#" + r + "_phpMyAdmin").attr("data-info", "phpmyadmin " + n)
		}
		$("#select_MySQL,#apache_select_MySQL").change(function() {
			var n = $(this).val();
			a(n)
		});
		
		$("#apache_select_Apache").change(function(){
			var apacheVersion = $(this).val();
			if(apacheVersion == '2.2'){
				layer.msg('您选择的是Apache2.2,PHP将会以php5_module模式运行!');
			}else{
				layer.msg('您选择的是Apache2.4,PHP将会以php-fpm模式运行!');
			}
		});
		
		$("#apache_select_PHP").change(function(){
			var apacheVersion = $("#apache_select_Apache").val();
			var phpVersion = $(this).val();
			if(apacheVersion == '2.2'){
				if(phpVersion != '5.2' && phpVersion != '5.3' && phpVersion != '5.4'){
					layer.msg('Apache2.2不支持PHP-' + phpVersion,{icon:5});
					$(this).val("5.4");
					$("#apache_PHP").attr('data-info','php 5.4');
					return false;
				}
			}else{
				if(phpVersion == '5.2'){
					layer.msg('Apache2.4不支持PHP-' + phpVersion,{icon:5});
					$(this).val("5.4");
					$("#apache_PHP").attr('data-info','php 5.4');
					return false;
				}
			}
		});

		function a(n) {
			memSize = getCookie("memSize");
			max = 64;
			msg = "64M";
			switch(n) {
				case "5.1":
					max = 256;
					msg = "256M";
					break;
				case "5.7":
					max = 1500;
					msg = "2GB";
					break;
				case "5.6":
					max = 800;
					msg = "1GB";
					break;
				case "AliSQL":
					max = 800;
					msg = "1GB";
					break;
				case "mariadb_10.0":
					max = 800;
					msg = "1GB";
					break;
				case "mariadb_10.1":
					max = 1500;
					msg = "2GB";
					break
			}
			if(memSize < max) {
				layer.msg("您 的内存小于" + msg + "，不建议安装MySQL-" + n, {
					icon: 5
				})
			}
		}
		$(".onekey").click(function() {
			var v = $(this).prev().find("input").eq(0).prop("checked") ? "1" : "0";
			var r = $(this).parents(".rec-box-con").find(".rec-list li").length;
			var n = "";
			var q = "";
			var p = "";
			var x = "";
			var s = "";
			for(var t = 0; t < r; t++) {
				var w = $(this).parents(".rec-box-con").find("ul li").eq(t);
				var u = w.find("input");
				if(u.prop("checked")) {
					n += u.attr("data-info") + ","
				}
			}
			q = n.split(",");
			loadT = layer.msg("正在添加到安装器...", {
				icon: 16,
				time: 0,
				shade: [0.3, "#000"]
			});
			for(var t = 0; t < q.length - 1; t++) {
				p = q[t].split(" ")[0].toLowerCase();
				x = q[t].split(" ")[1];
				s = "name=" + p + "&version=" + x + "&type=" + v + "&id=" + (t + 1);
				$.ajax({
					url: "/files?action=InstallSoft",
					data: s,
					type: "POST",
					async: false,
					success: function(y) {}
				})
			}
			layer.close(loadT);
			layer.close(k);
			setTimeout(function() {
				GetTaskCount()
			}, 2000);
			layer.msg("已将安装请求添加到安装器..", {
				icon: 1
			});
			setTimeout(function() {
				task()
			}, 1000)
		});
		InstallTips();
		fly("onekey")
	})
}

function jump() {
	layer.closeAll();
	window.location.href = "/soft"
}

function InstallTips() {
	$(".fangshi label").mouseover(function() {
		var a = $(this).attr("data-title");
		layer.tips(a, this, {
			tips: [1, "#787878"],
			time: 0
		})
	}).mouseout(function() {
		$(".layui-layer-tips").remove()
	})
}

function fly(a) {
	var b = $("#task").offset();
	$("." + a).click(function(d) {
		var e = $(this);
		var c = $('<span class="yuandian"></span>');
		c.fly({
			start: {
				left: d.pageX,
				top: d.pageY
			},
			end: {
				left: b.left + 10,
				top: b.top + 10,
				width: 0,
				height: 0
			},
			onEnd: function() {
				layer.closeAll();
				layer.msg("已添加到队列", {
					icon: 1
				});
				GetTaskCount()
			}
		})
	})
};