#coding:cp936

import sys
import os
import shutil
import os.path
import traceback
import msvcrt
#import filenames
import filetags
from config import *
from functions import *


def Synchronize():
	#ԴĿ¼
	sset = ReadInputDirs("Synchronize Code\nChose Source Dir: ", maxnum=1)
	if sset is None:
		return
	#Ŀ��Ŀ¼
	dests = ReadInputDirs("Enter Dest Dirs: ")
	if dests is None:
		return
	
	#���ԴĿ¼
	source = list(sset)[0]
	srcname = GetDirName(source)
	print "check %s SVN ..."%source
	SVNUpdate(source)
	if SVNIsModified(source):
		print "%s NOT Equal Repository !!!"%source
		msvcrt.getch()
		return
	rev = SVNRevision(source)
	
	#Ŀ��Ŀ¼����
	for dst in dests:
		dname = GetDirName(dst)
		if dname in MASTER_DIRS + PUBLIC_DIRS:
			print "%s can't be dest"%dname
			msvcrt.getch()
			return
		if dname == srcname:
			print "%s is source"%dname
			msvcrt.getch()
			return
	#Ŀ��Ŀ¼SVN����
	svncomp = set()
	for dst in dests:
		print "check %s SVN ..."%dst
		SVNUpdate(dst)
		if SVNCommitAll(dst, "pre sync") == 0:
			svncomp.add(dst)
	
	#��ʼͬ��
	syncs = set()
	for dst in svncomp:
		#ɾ���ļ�
		for f in os.listdir(dst):
			if f not in EXCLUDE_NAME:
				f = dst+f
				print "remove %s"%f
				if os.path.isdir(f):
					shutil.rmtree(f)
				else:
					os.remove(f)
		#�����ļ�
		for f in os.listdir(source):
			if f not in EXCLUDE_NAME:
				s = source+f
				print "copy %s to %s"%(s, dst)
				if os.path.isdir(s):
					shutil.copytree(s, dst+f)
				else:
					shutil.copyfile(s, dst+f)
		syncs.add(dst)
	
	#SVN�ύ
	success = set()
	log = "sync with %s %s"%(srcname, rev)
	for dst in syncs:
		print "prepare svn commit %s..."%dst
		if SVNCommitAll(dst, log) == 0:
			success.add(dst)
	
	#tags�ļ�
	#filenames.GenerateFileTags(success)
	filetags.DoGenTags(success)
	
	print "================================================================"
	print "synchronize Done: %s -> %s"%(source, dests)
	print "dest svn problem: %s"%(dests-svncomp)
	print "file sync problem: %s"%(svncomp-syncs)
	print "svn commit problem: %s"%(syncs-success)
	print "success: %s"%success
	msvcrt.getch()

def main():
	try:
		Synchronize()
	except:
		traceback.print_exc()
	msvcrt.getch()

if __name__ == "__main__":
	main()
