#coding: utf-8
import psutil,time,os

class checkCpu:
    __limit = 35;   #Cpu使用率触发上限
    __time = 1;     #循环同期
    
    def checkMain(self):
        pids = psutil.pids()
        for pid in pids:
            try:
                p = psutil.Process(pid);
                if p.exe() == "": continue;
                name = p.name()
                if self.whiteList(name): continue;
                cputimes = p.cpu_times()
                if cputimes.user < 0.1: continue;
                percent = p.cpu_percent(interval = 1); 
                if percent > self.__limit:
                    log = "[" + time.strftime('%Y-%m-%d %X',time.localtime()) + "]kill pid=" + str(pid) + ", name=" + name + ", percent=" + str(percent) + "%";
                    os.system( "echo '" + log + "' >> /tmp/check.log");
                    p.kill();
            except:
                pass
    
    #检查白名单
    def whiteList(self,name):
        wlist = ['sparse_dd','stunnel','squeezed','vncterm','mpathalert','vncterm','multipathd','fe','elasticsyslog','syslogd','v6d','xapi','screen','java','udevd','ntpd','irqbalance','qmgr','wpa_supplicant','mysqld_safe','sftp-server','lvmetad','pure-ftpd','auditd','master','dbus-daemon','tapdisk','sshd','init','ksoftirqd','kworker','kmpathd','kmpath_handlerd','python','kdmflush','bioset','crond','kthreadd','migration','rcu_sched','kjournald','gcc','gcc++','nginx','mysqld','php-cgi','login','firewalld','iptables','systemd','network','dhclient','systemd-journald','NetworkManager','systemd-logind','systemd-udevd','polkitd','tuned','rsyslogd']
        wslist = ['vif','qemu','scsi_eh','xcp','xen']
        
        for key in wlist:
            if key == name: return True
        
        for key in wslist:
            if name.find(key) != -1: return True
            
        return False
    
    
    #开始处理
    def start(self):
        while True:
            self.checkMain();
            time.sleep(self.__time);
            
            
            
if __name__ == "__main__":
    print "checkCPU running.."
    c = checkCpu();
    c.start();
    