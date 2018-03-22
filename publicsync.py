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
	dests = ReadInputDirs("Enter Dest Dirs: ", maxnum=1)
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
	
	#���Ŀ��Ŀ¼
	dst = list(dests)[0]
	dname = GetDirName(dst)
	if dname == srcname:
		print "%s is source"%dname
		msvcrt.getch()
		return
	print "check %s SVN ..."%dst
	SVNUpdate(dst)
	if SVNIsModified(dst):
		print "%s NOT Equal Repository !!!"%dst
		msvcrt.getch()
		return
	
	#��ʼͬ��
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
	
	#SVN�ύ
	log = "sync with %s %s"%(srcname, rev)
	print "prepare svn commit %s..."%dst
	if SVNCommitAll(dst, log) != 0:
		print "%s commint WRONG !!!"%dst
		msvcrt.getch()
		return
	
	print "================================================================"
	print "SUCCESS synchronize Done: %s -> %s"%(source, dst)
	msvcrt.getch()

def main():
	try:
		Synchronize()
	except:
		traceback.print_exc()
	msvcrt.getch()

if __name__ == "__main__":
	main()
