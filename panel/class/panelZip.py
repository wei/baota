#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板 x3
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http:#bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------
import sys,os,public,re
reload(sys)
sys.setdefaultencoding('utf-8')

class panelZip():
    def zip_dir(self,dirname,zipfilename):
        filelist = []
        if os.path.isfile(dirname):
            filelist.append(dirname)
        else :
            for root, dirs, files in os.walk(dirname):
                for name in files:
                    filelist.append(os.path.join(root, name))
     
        zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
        for tar in filelist:
            arcname = tar[len(dirname):]
            zf.write(tar,arcname)
        zf.close()
        
    def unzip_file(self,zipfilename, unziptodir):
        if not os.path.exists(unziptodir):
            os.mkdir(unziptodir, 0777)
        zfobj = zipfile.ZipFile(zipfilename)
        for name in zfobj.namelist():
            name = name.replace('\\','/')
     
            if name.endswith('/'):
                p = os.path.join(unziptodir, name[:-1])
                if os.path.exists(p):
                    shutil.rmtree(p)
                os.mkdir(p)
            else:
                ext_filename = os.path.join(unziptodir, name)
                ext_dir= os.path.dirname(ext_filename)
                if not os.path.exists(ext_dir):
                    os.mkdir(ext_dir,0777)
                outfile = open(ext_filename, 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
