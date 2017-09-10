#coding:utf8

import os
import shutil
import time
import datetime


BUG_TYPE_ERROR = 1
BUG_TYPE_TRACE = 2


def GetTimeVersion():
    GEN_WEEK = 4#星期5
    GEN_HOUR = 6#早上6点
    now = datetime.datetime.today()
    w = time.localtime().tm_wday
    h = time.localtime().tm_hour
    if w >= GEN_WEEK and h >= GEN_HOUR:
        day = w-GEN_WEEK
    else:
        day = w-GEN_WEEK+7
    _day = datetime.timedelta(days=day)
    d = (now-_day).replace(hour=GEN_HOUR).replace(minute=0).replace(second=0)
    #return d.strftime("%Y-%m-%d %H:%M:%S")
    return d.strftime("%Y%m%d")

class Bug(object):
    def __init__(self, bugid, btype, markstr):
        self.ID = bugid
        self.BugType = btype
        self.Mark = markstr
        self.Appearances = {}
        self.Resolved = False

    def Appear(self, errstr, srvid, linenum):
        self.Appearances.setdefault(errstr, {}).setdefault(srvid, []).append(linenum)

class LogAnalyseTaohua2(object):
    REMOTE_LOG_DIR = "\\\\192.168.1.26\\guest\\th2log\\"
    LOG_FILE_HEAD = "Log_tht"
    REPORT_FILE_FORMAT = "bugreport_%s.txt"
    LOG_LINE_HEAD_NUM = 17
    ERROR_HEAD = "File 'script/"
    ERROR_TAIL = "etype <type 'exceptions"
    TRACE_HEAD = "Traceback (most recent call last):\n"
    TRACE_TAIL = "\n"

    def __init__(self, logdir, reportdir):
        self.TimeStr = GetTimeVersion()
        self.LogDir = logdir+self.TimeStr+"/"
        self.ReportFile = reportdir+self.REPORT_FILE_FORMAT%self.TimeStr
        self.MaxBugID = 0
        self.Errors = {}    #str2id
        self.Traces = {}    #str2id
        self.Bugs = {}      #id2object

    def StartAnalyse(self):
        self.CopyLogFiles()
        self.ReadReport()
        self.DoAnalyse()
        self.WriteReport()

    def CheckLogName(self, filename):
        lst = filename.split(".")
        if len(lst)==2 and lst[0][:len(self.LOG_FILE_HEAD)]==self.LOG_FILE_HEAD and lst[1] == "txt":
            try:
                return int(lst[0][len(self.LOG_FILE_HEAD):])
            except:
                return 0
        return 0

    def CopyLogFiles(self):
        if os.path.exists(self.LogDir):
            shutil.rmtree(self.LogDir)
        os.mkdir(self.LogDir)
        for f in os.listdir(self.REMOTE_LOG_DIR):
            if self.CheckLogName(f) != 0:
                print "copyfile... %s"%f
                shutil.copy(self.REMOTE_LOG_DIR+f, self.LogDir)

    def CreateBug(self, btype, mark):
        self.MaxBugID += 1
        bug = Bug(self.MaxBugID, btype, mark)
        self.Bugs[self.MaxBugID] = bug
        return bug

    def AddBug(self, btype, srvid, linenum, linelst):
        linenum -= len(linelst)
        for i in xrange(len(linelst)-1, -1, -1):
            if linelst[i] == "\n":
                linelst.pop(i)
        if btype == BUG_TYPE_ERROR:
            mark = linelst[-3]
            dct = self.Errors
        elif btype == BUG_TYPE_TRACE:
            TRACE_EXCLUSION_NORECORD = "OSError: [Errno 2] No such file or directory: 'warrec/Exorcism_"
            if linelst[-1][:len(TRACE_EXCLUSION_NORECORD)]==TRACE_EXCLUSION_NORECORD:
                return
            mark = linelst[-1]
            dct = self.Traces
        bugid = dct.get(mark)
        if bugid is None:
            bug = self.CreateBug(btype, mark)
            self.Errors[mark] = bug.ID
        else:
            bug = self.Bugs[bugid]
        bug.Appear("".join(linelst), srvid, linenum)

    def DoAnalyse(self):
        for f in os.listdir(self.LogDir):
            srvid = self.CheckLogName(f)
            if srvid == 0:
                continue
            errlines = []
            tracelines = []
            linenum = 0
            for line in open(self.LogDir+f):
                linenum += 1
                if linenum == 1:#[08-24
                    month, day = self.TimeStr[4:6], self.TimeStr[6:8]
                    if line[1:3] != month or line[4:6] != day:
                        print srvid
                        continue
                #check error
                text = line[self.LOG_LINE_HEAD_NUM:]
                if len(errlines)==0:
                    if text[:len(self.ERROR_HEAD)] == self.ERROR_HEAD:
                        errlines.append(text)
                else:
                    errlines.append(text)
                    if text[:len(self.ERROR_TAIL)] == self.ERROR_TAIL:
                        self.AddBug(BUG_TYPE_ERROR, srvid, linenum, errlines)
                        errlines = []
                #check trace
                if len(tracelines) == 0:
                    if line == self.TRACE_HEAD:
                        tracelines.append(line)
                else:
                    tracelines.append(line)
                    if line == self.TRACE_TAIL:
                        self.AddBug(BUG_TYPE_TRACE, srvid, linenum, tracelines)
                        tracelines = []

    def ReadReport(self):
        try:
            f = open(self.ReportFile)
        except:
            return
        bug = None
        for line in f:
            if line[:3] == "BUG":
                if bug != None:
                    print "read report error 1 !"
                    return
                k = line.find(")")
                i = line.find(":")
                btype = int(line[4:k])
                bugid = int(line[k+1:i-1])
                mark = line[i+2:]
                bug = Bug(bugid, btype, mark)
            elif line[:8] == "RESOLVED":
                if bug == None:
                    print "read report error 2 !"
                    return
                resolved = False
                if line[11:] == "True\n":
                    resolved = True
                bug.Resolved = resolved
                self.Bugs[bug.ID] = bug
                if bug.BugType == BUG_TYPE_ERROR:
                    self.Errors[bug.Mark] = bug.ID
                elif bug.BugType == BUG_TYPE_TRACE:
                    self.Traces[bug.Mark] = bug.ID
                bug = None
        self.MaxBugID = max(self.Bugs)
        f.close()

    def WriteReport(self):
        sepline = "#"*80+"\n"
        f = open(self.ReportFile, "w")
        bugs = sorted(self.Bugs.values(), key=lambda x:(x.Resolved, x.BugType, x.ID))
        for bug in bugs:
            f.write("BUG(%d) %d : %s"%(bug.BugType, bug.ID, bug.Mark))
            f.write("RESOLVED : %s\n"%(bug.Resolved))
            if bug.Resolved == True:
                continue
            f.write(sepline)
            for errstr, dct in bug.Appearances.iteritems():
                for srvid, linenums in dct.iteritems():
                    f.write("SERVER %d : %s\n"%(srvid, str(linenums)))
                f.write("%s"%errstr)
            f.write(sepline)
            f.write("\n")
        f.close()


if __name__ == "__main__":
    LOCAL_PATH = "E:/log/"
    analysor = LogAnalyseTaohua2(LOCAL_PATH, LOCAL_PATH)
    analysor.StartAnalyse()
