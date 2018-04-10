#coding:cp936

import sys
import os
import re
import shutil
import time
import datetime
import optparse
import traceback


def log_message(msg, *args):
    print >> sys.stdout, "[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg%args)
    sys.stdout.flush()

class NameList(list):
    def __init__(self, name, unit):
        list.__init__([])
        self.name = name
        self.unit = unit

class Analysor(object):
    pattern_time = re.compile(r"^\[(\d{4})-(\d{2})-(\d{2}).*")

    pattern_trade = re.compile(r"^\[.{19}\] (TRADE|STALL|GIVE) (\d+)\|money:(\d+)\|.* <<< (\d+)\|money:(\d+)\|.*")
    pattern_studio = re.compile(r"^\[.{19}\] STUDIOMONEY who:(\d+) total:(\d+) money:(\d+) studio:(\d+) .*")
    pattern_forbid = re.compile(r"^\[.{19}\] STUDIOFORBID who:(\d+) .*studio:(\d+) .*")

    def __init__(self, srvid, logfile, archivedir, reportdir):
        self.serverid = srvid
        self.logfile = logfile
        self.archivedir = os.path.join(archivedir, str(srvid))
        if not os.path.exists(self.archivedir):
            os.mkdir(self.archivedir)
        self.reportdir = reportdir

        self.logtime = ""

        self.data_trade = {}
        self.data_studio = {}
        self.data_forbid = {}

        self.rank_money_recv = NameList('收入总金额', '银子')
        self.rank_money_recvcnt = NameList('收入总次数', '次数')
        self.rank_money_give = NameList('支出总金额', '银子')
        self.rank_money_givecnt = NameList('支出总次数', '次数')
        self.rank_money_total = NameList('交易总金额(收入+支出)', '银子')
        self.rank_studio_recvcnt = NameList('"低于12小时玩家银子"收入总次数', '次数')
        self.rank_studio_givecnt = NameList('"低于12小时玩家银子"支出总次数', '次数')
        self.rank_forbid = NameList('被拦截交易次数', '次数')

        self.all_rank = [
            self.rank_money_recv,
            self.rank_money_recvcnt,
            self.rank_money_give,
            self.rank_money_givecnt,
            self.rank_money_total,
            self.rank_studio_recvcnt,
            self.rank_studio_givecnt,
            self.rank_forbid,
        ]


    def Analysis(self):
        self.Ready()
        self.GatherStatistics()
        self.Rank()
        self.WriteReport()

    def Ready(self):
        for line in open(self.logfile):
            m = self.pattern_time.match(line)
            if m:
                log_message("Analysis logfile... server: %s, time: %s-%s-%s", self.serverid, *m.groups())
                break
        else:
            raise RunTimeError
        self.logtime = "%s%s%s"%m.groups()
        shutil.copy(self.logfile, os.path.join(self.archivedir, "r_moneymonitor_%s_%s_%s.log"%m.groups()))

    def GatherStatistics(self):
        for line in open(self.logfile):
            match_trade = self.pattern_trade.match(line)
            if match_trade:
                _, recver, recv_money, giver, give_money = match_trade.groups()
                recver      =int(recver)
                recv_money  =int(recv_money)
                giver       =int(giver)
                give_money  =int(give_money)
                lst = self.data_trade.setdefault(recver, [0,0,0,0])
                lst[0] += 1
                lst[1] += recv_money
                lst = self.data_trade.setdefault(giver, [0,0,0,0])
                lst[2] += 1
                lst[3] += give_money
            match_studio = self.pattern_studio.match(line)
            if match_studio:
                recver, total, money, giver = match_studio.groups()
                recver  = int(recver)
                total   = int(total)
                money   = int(money)
                giver   = int(giver)
                lst = self.data_studio.setdefault(recver, [0, 0, 0, 0])
                lst[0] += 1
                lst[1] = total
                lst = self.data_studio.setdefault(giver, [0, 0, 0, 0])
                lst[2] += 1
                lst[3] += money
            match_forbid = self.pattern_forbid.match(line)
            if match_forbid:
                recver, giver = match_forbid.groups()
                recver  = int(recver)
                giver   = int(giver)
                for pid in [recver, giver]:
                    self.data_forbid[pid] = self.data_forbid.get(pid, 0) + 1

    def Rank(self):
        log_message("Work Done! Analysis trade %d players"%(len(self.data_trade)))
        for pid, [recv_cnt, recv_money, give_cnt, give_money] in self.data_trade.iteritems():
            if recv_cnt > 0:
                self.rank_money_recvcnt.append((recv_cnt, pid))
            if recv_money > 0:
                self.rank_money_recv.append((recv_money, pid))
            if give_cnt > 0:
                self.rank_money_givecnt.append((give_cnt, pid))
            if give_money > 0:
                self.rank_money_give.append((give_money, pid))
            _sum = sum([recv_money, give_money])
            if _sum > 0:
                self.rank_money_total.append((_sum, pid))
        for pid, [recv_cnt, recv_money, give_cnt, give_money] in self.data_studio.iteritems():
            if recv_cnt > 0:
                self.rank_studio_recvcnt.append((recv_cnt, pid))
            if give_cnt > 0:
                self.rank_studio_givecnt.append((give_cnt, pid))
        for pid, cnt in self.data_forbid.iteritems():
            if cnt > 0:
                self.rank_forbid.append((cnt, pid))

        for rank in self.all_rank:
            rank.sort(reverse=True)

    def WriteReport(self):
        f = open(os.path.join(self.reportdir, "report_%s_%d.txt"%(self.logtime, self.serverid)), "w")
        for rank in self.all_rank:
            rank.sort(reverse=True)
            f.write('====%s====\r\n'%(rank.name))
            f.write('排名  玩家ID     %s\r\n'%(rank.unit))
            for idx, (num, pid) in enumerate(rank): 
                if idx >= 100:
                    break
                f.write('{0:<6}{1:<11}{2}\r\n'.format(idx+1, pid, num))
            f.write('\r\n')
        f.close()


class Manager(object):
    REMOTE_LOG_DIR = "/mnt/th2_today/"
    LOG_DIR_HEAD = "tht"
    LOG_FILE_NAME = "r_moneymonitor.log"
    REPORT_FILE_FORMAT = "moneyreport_%s.txt"

    def __init__(self, logdir, outdir, archdir):
        self.logdir = logdir
        self.outdir = outdir
        self.archive = archdir
        self.analysors = {}
        

    def StartAnalyse(self):
        while True:
            self.CopyLogFiles()
            for srvid, analysor in self.analysors.iteritems():
                try:
                    analysor.Analysis()
                except:
                    log_message("server%d log run error !!\n%s"%(srvid, traceback.format_exc()))
            log_message("sleeping....")
            time.sleep(3600)

    def CopyLogFiles(self):
        dirlst = os.listdir(self.REMOTE_LOG_DIR)
        if not dirlst:
            log_message("NO REMOTE LOG FILES !!")
            #msvcrt.getch()
            exit(1)
        allsrvlst = []
        for d in dirlst:
            if d.find(self.LOG_DIR_HEAD) == 0:
                try:
                    allsrvlst.append(int(d[len(self.LOG_DIR_HEAD):]))
                except:
                    pass
        serverids = sorted(allsrvlst, reverse=True)[:20]
        if len(serverids) == 0:
            log_message("NO REMOTE LOG FILES !!")
            #msvcrt.getch()
            exit(1)
        if os.path.exists(self.logdir):
            shutil.rmtree(self.logdir)
        os.mkdir(self.logdir)
        for srvid in serverids:
            remotefile = self.REMOTE_LOG_DIR+self.LOG_DIR_HEAD+str(srvid)+"/"+self.LOG_FILE_NAME
            localdir = os.path.join(self.logdir, str(srvid))
            os.mkdir(localdir)
            localfile = os.path.join(localdir, self.LOG_FILE_NAME)
            log_message("copyfile... %s to %s"%(remotefile, localfile))
            shutil.copy(remotefile, localfile)
            self.analysors[srvid] = Analysor(srvid, localfile, self.archive, self.outdir)


def main():
    root = os.path.split(os.path.abspath(__file__))[0]
    
    parser = optparse.OptionParser(usage = '%prog [--outdir=outdir]', version='%prog 0.1' )
    parser.add_option('-o', '--outdir', dest='out', type=str, default='', help='output directory', metavar='outdir')
    parser.add_option('-a', '--archdir', dest='arch', type=str, default='', help='archive directory', metavar='archdir')
    opts, args = parser.parse_args()
    
    if opts.out:
        out_dir = os.path.abspath(opts.out)
        if not os.path.isdir(out_dir):
            log_message("ERROR! not this dir:%s"%out_dir)
            return
    else:
        out_dir = os.getcwd()

    if opts.arch:
        arch_dir = os.path.abspath(opts.arch)
        if not os.path.isdir(arch_dir):
            log_message("ERROR! not this dir:%s"%arch_dir)
            return
    else:
        arch_dir = os.path.join(root, "archievelog")
        if not os.path.exists(arch_dir):
            os.mkdir(arch_dir)
    
    log_dir = os.path.join(root, "currentlog")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    log_message("Start ! log:%s arch:%s out:%s"%(log_dir, arch_dir, out_dir))
    analysor = Manager(log_dir, out_dir, arch_dir)
    analysor.StartAnalyse()

if __name__ == "__main__":
    main()
