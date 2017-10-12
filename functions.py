#coding:cp936

import os
import os.path
from config import *

def ReadInputDirs(hint="", root=PATH_ROOT, maxnum=None):
	while True:
		iput = raw_input(hint)
		iput = iput.strip()
		if iput == "exit" or iput == "quit":
			return None
		fail = False
		dirs = set()
		cnt = 0
		for s in iput.split(","):
			s = s.strip()
			if s:
				cnt += 1
				if maxnum is not None and cnt > maxnum:
					fail = True
					print "ERROR, Too Much Directories"
					break
				if s[0] in ["c","d","e","f","g","C","D","E","F","G",] and s[1] == ":" and s[2] in ["\\", "/"]:
					_path = s+"/"
				elif s in MASTER_DIRS:
					_path = root+"master/"+s+"/"
				elif s in PUBLIC_DIRS:
					_path = root+"public/"+s+"/"
				else:
					_path = root+"branch/"+s+"/"
				if not os.path.isdir(_path):
					fail = True
					print "ERROR, No Such Directory: %s !!!"%_path
					break
				dirs.add(_path)
		if dirs and not fail:
			return dirs

def GetDirName(d):
	lst = d.split("/")
	lst.reverse()
	for s in lst:
		if s:
			return s

def SVNIsModified(d):
	cmd = "svn status %s"%d
	s = os.popen(cmd).read()
	if s:
		return True
	return False

def SVNStatus(d):
	cmd = "svn status %s"%d
	strlst = os.popen(cmd).readlines()
	clst = []	#冲突
	alst = []	#增加
	rlst = []	#删除
	dlst = []	#删除
	mlst = []	#更改
	status_to_lst = {
		"C" : clst,
		"?" : alst,
		"!" : rlst,
		"M" : mlst,
		"D" : dlst,
	}
	for s in strlst:
		sts = s.split()
		if len(sts) == 2:
			status, filename = s.split()
			lst = status_to_lst.get(status)
			if lst is not None:
				lst.append(filename)
	return clst, alst, rlst, dlst, mlst

def SVNUpdate(d):
	cmd = "svn up %s"%d
	os.popen(cmd)

FILE_NAME_CNT = 150

def SVNAdd(files):
	i = 0
	while i < len(files):
		e = i + FILE_NAME_CNT
		cmd = "svn add %s"%" ".join(files[i:e])
		if os.system(cmd) != 0:
			return 1
		i = e
	return 0

def SVNDelete(files):
	i = 0
	while i < len(files):
		e = i + FILE_NAME_CNT
		cmd = "svn delete %s"%" ".join(files[i:e])
		if os.system(cmd) != 0:
			return 1
		i = e
	return 0

def SVNRevert(files):
	i = 0
	while i < len(files):
		e = i + FILE_NAME_CNT
		cmd = "svn revert %s"%" ".join(files[i:e])
		if os.system(cmd) != 0:
			return 1
		i = e
	return 0

def SVNRevertAll(d):
	clst,alst,rlst,dlst,mlst = SVNStatus(workdir)
	rvts = clst+rlst+dlst+mlst
	if rvts and SVNRevert(rvts) != 0:
		print "%s revert error !!!"%workdir
		return

def SVNCommit(d, log):
	cmd = 'svn ci %s -m "%s"'%(d,log)
	return os.system(cmd)

def SVNCommitAll(d, log):
	clst, alst, rlst, dlst, mlst = SVNStatus(d)
	if clst:
		return 1
	if alst:
		if SVNAdd(alst) != 0:
			return 2
	if rlst:
		if SVNDelete(rlst) != 0:
			return 3
	if SVNCommit(d, log) != 0:
		return 4
	return 0

def SVNRevision(d):
	cmd = "svn info %s"%d
	strlst = os.popen(cmd).readlines()
	for s in strlst:
		lst = s.split(": ")
		if lst and lst[0] == "Last Changed Rev":
			return lst[1]
