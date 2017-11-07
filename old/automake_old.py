#coding:cp936

import sys
import os
import os.path
import traceback
import msvcrt
from config import *
from functions import *

class SVNException(Exception):  
	def __init__(self, errmsg):  
		Exception.__init__(self)
		self.m_ErrMsg = errmsg

class MakePyException(Exception):  
	def __init__(self, errmsg):  
		Exception.__init__(self)
		self.m_ErrMsg = errmsg


def main():
	print "桃花2自动导表:"
	options = {}
	notify = []
	for i, d in enumerate(MAKEPY_DIRS):
		name, _, dest = d
		if dest:
			options[i] = d
			notify.append("%d.%s"%(i, name))
	hint = "\t".join(notify)+"\nChose Work Directory: "
	while True:
		input_s = raw_input(hint)
		input_s = input_s.strip()
		if input_s == "exit" or input_s == "quit":
			return
		if len(input_s) > len(options):
			print "Wrong input!!!!!"
			continue
		idxes = []
		try:
			for i in input_s:
				idx = int(i)
				if idx not in options:
					raise
				if idx not in idxes:
					idxes.append(idx)
		except:
			print "Wrong input !!!!!"
			continue
		break
	
	errors = {}
	for idx in idxes:
		name, workdir, dst = options[idx]
		try:
			DoDaoBiao(workdir, dst)
			print "============> SUCCESS : %s -> %s\n"%(workdir, dst)
		except SVNException, e:
			errors.setdefault(name, []).append(e.m_ErrMsg)
		except MakePyException, e:
			errors.setdefault(name, []).append(e.m_ErrMsg)
			clst,alst,rlst,dlst,mlst = SVNStatus(dst)
			rvts = rlst+dlst+mlst
			if rvts and SVNRevert(rvts) != 0:
				errors[name].append("%s Revert ERROR !!!"%dst)
				continue
			try:
				for f in alst:
					os.remove(f)
			except:
				errors[name].append("%s Revert NOT Clear !!!"%dst)
				continue
			if SVNIsModified(dst):
				errors[name].append("%s Revert NOT Clear !!!"%dst)
				continue
		except:
			errors.setdefault(name, []).append(traceback.format_exc())

	for idx in idxes:
		name, workdir, dst = options[idx]
		print "==================================================="
		print name+" RESULT:\n"
		msglst = errors.get(name)
		if msglst:
			for msg in msglst:
				print msg+"\n"
		else:
			print "SUCCESS : %s -> %s\n"%(workdir, dst)
	
	msvcrt.getch()

def DoDaoBiao(workdir, dst):
	os.chdir(workdir)
	SVNUpdate(workdir)
	clst,alst,rlst,dlst,mlst = SVNStatus(workdir)
	rvts = clst+rlst+dlst+mlst
	if rvts:
		raise SVNException("%s NOT Equal Repository !!!"%workdir)
	#if rvts and SVNRevert(rvts) != 0:
	#	raise SVNException("%s revert error !!!"%workdir)
	
	SVNUpdate(dst)
	if SVNIsModified(dst):
		raise SVNException("%s NOT Equal Repository !!!"%dst)
	
	f = open("config.ini", "w")
	f.write("script_path=%s"%dst)
	f.close()
	
	print "%s --> %s......"%(workdir, dst)
	
	sys.path.append(workdir)
	import makepyfile
	reload(makepyfile)
	savedstd = sys.stdout
	tmp = open("e:/temp/tmp.txt", "w")
	sys.stdout = tmp
	try:
		makepyfile.MakePyfile("server")
	except:
		raise MakePyException(traceback.format_exc())
	finally:
		sys.stdout = savedstd
		sys.path.remove(workdir)
	
	if SVNCommitAll(dst, "导表") != 0:
		raise SVNException("%s Commit ERROR !!!"%dst)
	

if __name__ == "__main__":
	main()
