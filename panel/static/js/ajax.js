//初始化上传组件
function UploadStart(isBackup) {

	var upload = function(config) {
		this.uptype = config.UpType;
		this.url = config.url
		this.oldurl = config.url
		this.filessize = config.FilesSize, this.MaxUpNum = config.MaxUpNum, this.str = new MyAjax();
		this.file_input = document.getElementById("file_input");
		this.opt = document.getElementById("opt");
		this.up = document.getElementById("up");
		this.up_box = document.getElementById("up_box");
		this.filesalllength = this.FilesArrayLength = this.up_box_li = FileProgress = 0;
		this.FilesArray = new Array();
		this.num = 0;
	};

	upload.prototype = {
		SelectFile: function() {
			if(this.FilesArrayLength === 0) {
				this.up_box.innerHTML = "";
				this.un();
			}
			var filesall = this.file_input.files,
				files, filestype, fl = filesall.length;
			if(this.filesalllength + fl > this.MaxUpNum) {
				fl = this.MaxUpNum - this.filesalllength;
				layer.msg("一次只能选择" + this.MaxUpNum + "个文件上传，剩下的不作处理！", {
					icon: 5
				});
			}
			
			for(var i = 0; i < fl; i++) {
				files = filesall[i];
				filestype = files.name.split(".");
				filestype = Object.prototype.toString.call(filestype) === "[object Array]" ? filestype[filestype.length - 1] : "";
				if(isBackup){
					if(filestype !="sql" && filestype !="zip" && filestype !="gz" && filestype !="tgz"){
						layer.msg("文件类型不符合",{icon:5});
						return;
					}
				}
				if(!files) {
					this.up_box.insertAdjacentHTML("beforeEnd", "<li>" + files.name + "<em style='color: red;'>错误的文件</em></li>");
				} else if(this.uptype.length > 0 && this.uptype.indexOf(filestype.toLowerCase()) === -1) {
					this.up_box.insertAdjacentHTML("beforeEnd", "<li>" + files.name + "<em style='color: red;'>不允许上传的类型文件</em></li>");
				} else if(files.size <= 0) {
					this.up_box.insertAdjacentHTML("beforeEnd", "<li>" + files.name + "<em style='color: red;'>不能为空字节文件</em></li>");
				} else {
					this.up_box.insertAdjacentHTML("beforeEnd", "<li><span class='filename'>" + files.name + "</span><span class='filesize'>" + (ToSize(files.size)) + "</span><span class='cancel' title='取消' onclick='this.parentNode.remove();'>X</span><em>正在等待</em></li>");
					this.FilesArray.push([files, (this.filesalllength - 1 < 0 ? 0 : this.filesalllength) + i]);
				}
			}
			this.filesalllength += fl;
			this.FilesArrayLength = this.FilesArray.length;
		},
		read: function() {
			if(this.filesalllength == 0) {
				layer.msg("请选择文件!", {
					icon: 5
				});
				return;
			}
			
			this.url = this.oldurl+'&codeing='+document.getElementById("fileCodeing").value
			
			if(this.FilesArrayLength > 0) {
				this.opt.disabled = true;
				this.up.disabled = true;
				this.file_input.disabled = true;
				this.up_box_li = this.up_box.getElementsByTagName("li");
				this.ready(this.FilesArray, 0, this.FilesArrayLength - 1);
			} else layer.msg("没有可用文件上传，重新选择文件", {
				icon: 5
			});
		},
		un: function() {
			this.opt.disabled = this.up.disabled = this.file_input.disabled;
			this.filesalllength = this.FilesArrayLength = this.up_box_li = 0;
			this.FilesArray = new Array();
		},
		ready: function(FilesArray, n, l) { //上传前，为上传作准备
			if(n > l) {
				this.un();
				return;
			}
			try {
				var reader = new FormData();
				reader.append("zunfile", FilesArray[n][0]);
			} catch(e) {
				this.opt.disabled = true;
				this.up.disabled = true;
				this.file_input.disabled = true;
				layer.msg("抱歉,IE 6/7/8 不支持请更换浏览器再上传", {
					icon: 5
				});
			}

			if(FilesArray.length > 1) {
				$("#totalProgress").html("<p>已上传" + this.num + "/" + FilesArray.length + "</p><progress value='" + this.num + "' max='" + FilesArray.length + "' ></progress>");
				$(".cancel").css("visibility", "hidden");
			}
			
			this.send(reader, FilesArray, n, l);
		},
		SetTxt: function(n, txt, color) {
			var em = this.up_box_li[n].getElementsByTagName("em")[0];
			em.style.color = color;
			em.innerHTML = txt;
		},
		send: function(ResultData, FilesArray, n, l) { //上传逻辑
			if(!this.up_box_li[n].getElementsByTagName("em")[0]){
				this.ready(FilesArray, n + 1, l);
				this.num++;
				return;
			}
			
			var self = this;
			this.FileProgress = 0;
			this.str.carry({
				url: this.url,
				data: ResultData,
				type: "get",
				timeout: 86400000,
				async: true,
				lock: true,
				complete: false,
				progress: function(evt) { //进度条事件
					self.FileProgress = Math.floor(evt.loaded / evt.total * 100) + "%";
					if(self.FileProgress == '100%') self.FileProgress = '正在保存..'
					self.SetTxt(FilesArray[n][1], "上传进度：" + self.FileProgress, "#005100");
				},
				success: function(serverdata) { //上传成功事件
					self.str.serverdata = false;
					self.SetTxt(FilesArray[n][1], "已上传成功", "#005100");
					self.ready(FilesArray, n + 1, l);
					self.num++;
					if(FilesArray.length > 1) {
						var msg = (self.num == FilesArray.length) ? '上传完成' : '已上传';
						$("#totalProgress").html("<p>" + msg + self.num + "/" + FilesArray.length + "</p><progress value='" + self.num + "' max='" + FilesArray.length + "' ></progress>");
					}

					if(self.num == FilesArray.length) {
						uploads.opt.disabled = false;
						uploads.up.disabled = false;
						uploads.file_input.disabled = false;
						self.num = 0;
					}
					if(!isBackup){
						GetFiles(getCookie('Path'));
					}
						
				},
				error: function(ErroMsg) {
					self.SetTxt(FilesArray[n][1], " 上传错误", "red");
					self.str.serverdata = false;
					self.ready(FilesArray, n + 1, l);
				},
				cache: false
			});
		}
	};

	try {
		var uploads = new upload({
			UpType: new Array(),
			FilesSize: 5242880000,
			MaxUpNum: 100,
			url: "/files?action=UploadFile&path=" + document.getElementById("input-val").value
		});
		uploads.opt.addEventListener("click", function() {
			uploads.file_input.click();
		}, false);
		uploads.up.addEventListener("click", function() {
			uploads.read();
		}, false);
		uploads.file_input.addEventListener("change", function() {
			uploads.SelectFile();
		}, false);
	} catch(e) {
		uploads.opt.disabled = true;
		uploads.up.disabled = true;
		uploads.file_input.disabled = true;
		layer.msg("抱歉,IE 6/7/8 不支持请更换浏览器再上传", {
			icon: 5
		});
	}
}