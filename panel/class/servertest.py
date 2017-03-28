#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板 x3
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <2879625666@qq.com>
# +-------------------------------------------------------------------

#+--------------------------------------------------------------------
#|   服务器测试
#+--------------------------------------------------------------------

import time,psutil;
class serverTest:
    
    #测试CPU
    def testCpu(self,n = 1):
        data = {}
        data['cpuCount'] = psutil.cpu_count();
        data['testFloat'] = int(self.testFloat());
        data['testInt'] = int(self.testInt());
        data['testBubble'] = int(self.testBubble());
        data['testTree'] = int(self.testTree());
        
        import re;
        cpuinfo = open('/proc/cpuinfo','r').read();
        rep = "model\s+name\s+:\s+(.+)"
        tmp = re.search(rep,cpuinfo);
        data['cpuType'] = ""
        if tmp:
            data['cpuType'] = tmp.groups()[0];
        
        data['system'] = open('/etc/redhat-release','r').read().replace('release ','').strip()
        data['score'] = (data['testBubble'] + data['testTree'] + data['testInt'] + data['testFloat']) * data['cpuCount'];
        return data;
        pass
    
    #测试整数运算
    def testInt(self):
        return self.testIntOrFloat(1);
    
    #测试浮点运行
    def testFloat(self):
        return self.testIntOrFloat(1.01);
        
    #CPU测试体
    def testIntOrFloat(self,n=1):
        start = time.time();
        num  = 10000 * 1000;
        for i in range(num):
            if i == 0: continue;
            a = n + i;
            b = n - i;
            c = n * i;
            d = n / i;
            n = n + 1;
            
        end = time.time();
        usetime = end - start;
        return num / 1000 / usetime;
    
    #冒泡算法测试
    def testBubble(self):
        start = time.time();
        num  = 10000 * 5;
        for c in xrange(num):
            lst = [0,1,2,3,4,5,6,7,8,9]
            lst = self.bubbleSort(lst)
        end = time.time();
        usetime = end - start;
        return num / 5 / usetime;
    
    #冒泡排序
    def bubbleSort(self,lst):
        length = len(lst)
        for i in xrange(0, length, 1):
            for j in xrange(0, length-1-i, 1):
                if lst[j] < lst[j+1]:
                    temp = lst[j]
                    lst[j] = lst[j+1]
                    lst[j+1] = temp
        return lst
    
    #二叉树算法测试
    def testTree(self):
        import testTree
        
        start = time.time();
        elems = range(3000)              #生成树节点
        tree = testTree.Tree()           #新建一个树对象
        for elem in elems:                  
            tree.add(elem)               #逐个加入树的节点
    
        tree.level_queue(tree.root)
        tree.front_digui(tree.root)
        tree.middle_digui(tree.root)
        tree.later_digui(tree.root)
        tree.front_stack(tree.root)
        tree.middle_stack(tree.root)
        tree.later_stack(tree.root)
        
        end = time.time();
        usetime = end - start;
        return 3000 / usetime;
    
    
    
    #测试内存
    def testMem(self):
        mem = psutil.virtual_memory()
        return mem.total/1024/1024;
        pass
    
    #测试磁盘
    def testDisk(self):
        import os
        data = {}
        filename = "testDisk_" + time.strftime('%Y%m%d%H%M%S',time.localtime());
        data['write'] =  self.testDiskWrite(filename);
        import shutil
        filename2 = "testDisk_" + time.strftime('%Y%m%d%H%M%S',time.localtime());
        shutil.move(filename,filename2);
        data['read'] =  self.testDiskRead(filename2);
        diskIo = psutil.disk_partitions()
        diskInfo = []
        for disk in diskIo:
            tmp = {}
            tmp['path'] = disk[1]
            tmp['size'] = psutil.disk_usage(disk[1])[0]
            diskInfo.append(tmp)
        data['diskInfo'] = diskInfo;
        data['score'] = data['write'] * 12 + data['read'] * 24
        os.remove(filename2);
        return data;
        pass
    
    #测试磁盘写入速度
    def testDiskWrite(self,filename):
        import random
        start = time.time();
        fp = open(filename,'w+');
        strTest = "";
        strTmp = "";
        for n in range(4):
            strTmp += chr(random.randint(97, 122))
        for n in range(1024):
            strTest += strTmp;
    
        for i in range(1024 * 256):
            fp.write(strTest);
            
        del(strTest);
        del(strTmp);
        fp.close()
        end = time.time();
        usetime = end - start;
        return int(1024/usetime);
        
    #测试磁盘读取速度    
    def testDiskRead(self,filename):
        import random
        start = time.time();
        fp = open(filename,'r');
        size = 4096;
        while True:
            tmp = fp.read(size);
            if not tmp: break;
            del(tmp);
        fp.close()
        end = time.time();
        usetime = end - start;
        return int(1024/usetime);
    
    def testWorkNet(self):
        pass
    