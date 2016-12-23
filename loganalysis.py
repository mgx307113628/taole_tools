#coding:cp936

import os
import shutil
import time
import datetime

#REMOTE_PATH = "\\\\192.168.1.26\\guest\\yjlog\\"
REMOTE_PATH = "\\\\192.168.1.26\\guest\\th2log\\"
LOCAL_PATH = "E:/log/"

PROGRESS_FILE = "progress.txt"
BUGS_FILE = "bugs.py"

BUG_HEAD = " Object<"	# " object<"]
BUG_CONTENT = [" File 'script/", " <type 'except"]
BUG_TAIL = " etype <type '"

ANALYSIS_INTERVAL = 3600

GEN_WEEK = 4	#星期5
GEN_HOUR = 7	#早上7点

g_Version = ""
g_Progress = {}
g_Bugs = {}
g_AnalysisCount = 0

def SaveProgress():	#保存进度
	global g_Progress,g_Version
	s = "Version: %s\n\n"%g_Version
	for srvid, lineno in g_Progress.iteritems():
		s += "%d : %d\n"%(srvid, lineno)
	fp = open(LOCAL_PATH+PROGRESS_FILE, "w")
	fp.write(s)
	fp.close()
	return 0

def LoadProgress():
	global g_Progress, g_Version
	try:
		fp = open(LOCAL_PATH+PROGRESS_FILE)
	except:
		return
	for s in fp.readlines():
		if s == "\n":
			continue
		if s[:7] == "Version":
			g_Version = s[8:].strip()
			continue
		lst = s.split(":")
		if len(lst) != 2:
			return -1
		try:
			srvid = int(lst[0].strip())
			lineno = int(lst[1].strip())
		except:
			return -1
		if srvid in g_Progress:
			return -1
		if lineno < 0:
			return -1
		g_Progress[srvid] = lineno
	fp.close()

def SaveBugs():
	global g_Bugs
	s = ""
	for bug, dct in g_Bugs.iteritems():
		for srvid, linenolst in dct.iteritems():
			s += "SERVER%d : %s\n"%(srvid, linenolst)
		s += bug
		s += "\n"
	fp = open(LOCAL_PATH+BUGS_FILE, "w")
	fp.write(s)
	fp.close()
	return 0

def LoadBugs():
	global g_Bugs
	try:
		fp = open(LOCAL_PATH+BUGS_FILE)
	except:
		return
	dct = {}
	bug = ""
	for s in fp.readlines():
		if s[0:6] == "SERVER":
			lst = s.split(":")
			if len(lst) != 2:
				return -1
			try:
				srvid = int(lst[0].strip()[6:])
				line_nos = lst[1].strip()[1:-1].split(", ")
				lst = []
				for no in line_nos:
					lst.append(int(no))
				dct[srvid] = lst
			except:
				return -1
		elif s != "\n":
			bug += s
		elif s == "\n":
			g_Bugs[bug] = dct
			dct = {}
			bug = ""
	fp.close()

def CopyLogFile():
	for f in os.listdir(REMOTE_PATH):
		#if f.find("Log_yj") == 0:
		if f.find("Log_tht") == 0:
			print "copyfile... %s"%f
			shutil.copy(REMOTE_PATH+f, LOCAL_PATH)

def AnalysisFile():
	global g_Progress, g_Bugs
	file_modify = False
	bug_modify = False
	for f in os.listdir(LOCAL_PATH):
		#name = "Log_yj"
		name = "Log_tht"
		if f[0:len(name)] != name:
			continue
		print "analysis... %s"%f
		srvid = int(f[len(name):len(name)+4])
		lastline = g_Progress.get(srvid, 0)
		fp = open(LOCAL_PATH+f)
		bug = ""
		bugging = False
		allfile = fp.readlines()
		newcontent = allfile[lastline+1:]
		for idx, line in enumerate(newcontent):
			file_modify = True
			if bugging == False:
				if line[16:24] == BUG_HEAD:
					bugging = True
			else:
				if line[16:30] in BUG_CONTENT:
					if line[-14:] == "'decodemouse'\n":
						bug = ""
						bugging = False
					else:
						bug += line[17:]
				elif line[16:30] == BUG_TAIL:
					bug += line[17:]
					g_Bugs.setdefault(bug, {}).setdefault(srvid, []).append(lastline+idx+2)
					bug_modify = True
					bug = ""
					bugging = False
				else:
					bug = ""
					bugging = False
		g_Progress[srvid] = len(allfile) - 1
		fp.close()
	return file_modify, bug_modify

def DoAnalysis():
	global g_AnalysisCount, g_Version
	newv = GetTimeVersion()
	v_chang = g_Version != newv
	if v_chang:
		g_Version = newv
	g_AnalysisCount += 1
	print "The %dst Analysis Start! Time: %s"%(g_AnalysisCount, time.asctime())
	CopyLogFile()
	file_modify, bug_modify = AnalysisFile()
	if bug_modify:
		SaveBugs()
	if file_modify or v_chang:
		SaveProgress()
	nexttm = time.ctime(time.time() + ANALYSIS_INTERVAL)
	print "The %dst Analysis Complete! Next Time: %s\n"%(g_AnalysisCount, nexttm)
	time.sleep(ANALYSIS_INTERVAL)
	DoAnalysis()

def GetTimeVersion():
	now = datetime.datetime.today()
	w = time.localtime().tm_wday
	h = time.localtime().tm_hour
	if w >= GEN_WEEK and h >= GEN_HOUR:
		day = w-GEN_WEEK
	else:
		day = w-GEN_WEEK+7
	_day = datetime.timedelta(days=day)
	d = (now-_day).replace(hour=GEN_HOUR).replace(minute=0).replace(second=0)
	return d.strftime("%Y-%m-%d %H:%M:%S")

def main():
	print GetTimeVersion()
	LoadProgress()
	print g_Progress
	print g_Version
	LoadBugs()
	DoAnalysis()
	
if __name__ == "__main__":
	main()

