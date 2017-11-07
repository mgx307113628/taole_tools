#coding:cp936

import sys
import os
import os.path
import traceback
import msvcrt
import subprocess
import time
from config import *
from functions import *


TEMP_BAT_FILE = "E:/temp/run_db.bat"

class SVNException(Exception):  
	def __init__(self, errmsg):  
		Exception.__init__(self)
		self.m_ErrMsg = errmsg

class MakePyException(Exception):  
	def __init__(self, errmsg):  
		Exception.__init__(self)
		self.m_ErrMsg = errmsg

class DaoBiao(object):
	def __init__(self, name, workdir, destdir):
		self.name = name
		self.workdir = workdir
		self.destdir = destdir
		self.retcode = None
		self.run()
	
	def run(self):
		try:
			self.checkdirsvn()
		except SVNException, e:
			print e.m_ErrMsg
			return
		try:
			self.run_make()
		except:
			traceback.print_exc()
			return
		try:
			self.result()
		except SVNException, e:
			print e.m_ErrMsg
			return
	
	def checkdirsvn(self):
		print "checking svn %s"%self.workdir
		SVNUpdate(self.workdir)
		clst,alst,rlst,dlst,mlst = SVNStatus(self.workdir)
		rvts = clst+rlst+dlst+mlst
		if rvts:
			raise SVNException("%s SVN workdir Modified !!!"%self.workdir)
		
		print "checking svn %s"%self.destdir
		SVNUpdate(self.destdir)
		if SVNIsModified(self.destdir):
			raise SVNException("%s SVN workdir Modified !!!"%self.destdir)
	
	def run_make(self):
		print "running %s/makepyfile.py -o %s server"%(self.workdir, self.destdir)
		print "-"*33+"makepyfile.py"+"-"*33
		self.retcode = subprocess.call(["python", "makepyfile.py", "-o", self.destdir, "server"])
		print "-"*79
		print "%s makepyfile %s：%s => %s"%(self.name, "成功" if self.retcode == 0 else "失败", self.workdir, self.destdir)
	
	def result(self):
		conclusion = "*"*79+"\n"+"*"*35+" RESULT "+"*"*36+"\n"+"%s导表%s：%s => %s"%(self.name, "成功" if self.retcode == 0 else "失败", self.workdir, self.destdir)
		if self.retcode == 0:
			print "commiting..."
			if SVNCommitAll(self.destdir, "导表") != 0:
				raise SVNException("%s\n%s Commit ERROR !!!"%(conclusion, self.destdir))
		else:
			print "reverting..."
			if SVNRevertAll(self.destdir) != 0:
				raise SVNException("%s\n%s Revert ERROR !!!"%(conclusion, self.destdir))
		print conclusion


def main():
	try:
		_, name, workdir, dst = sys.argv
		DaoBiao(name, workdir, dst)
	except:
		traceback.print_exc()
	msvcrt.getch()

if __name__ == "__main__":
	main()
