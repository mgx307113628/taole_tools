#coding:cp936

import sys
import os
import os.path
import traceback
import msvcrt
from config import *
from functions import *


def main():
	print "御剑自动导表:"
	lst = []
	for i, d in enumerate(MAKEPY_DIRS):
		lst.append("%d.御剑%s"%(i+1, d.split("/")[-1]))
	hint = "\t".join(lst)+"\nChose Work Directory: "
	while True:
		input_s = raw_input(hint)
		input_s = input_s.strip()
		if input_s == "exit" or input_s == "quit":
			return
		try:
			idx = int(input_s)
		except:
			print "Wrong input!!!!!"
			continue
		if idx > len(MAKEPY_DIRS) or idx <= 0:
			print "Wrong input!!!!!"
			continue
		break
	workdir = MAKEPY_DIRS[idx-1]
	dst = AUTO_MAKE_DIRS[workdir]
	os.chdir(workdir)
	
	SVNUpdate(workdir)
	clst,alst,rlst,dlst,mlst = SVNStatus(workdir)
	rvts = clst+rlst+dlst+mlst
	if rvts and SVNRevert(rvts) != 0:
		print "%s revert error !!!"%workdir
		msvcrt.getch()
		return
	
	SVNUpdate(dst)
	if SVNIsModified(dst):
		print "%s NOT Equal Repository !!!"%dst
		msvcrt.getch()
		return
	
	try:
		f = open("config.ini", "w")
		if f:
			f.write("script_path=%s"%dst)
			f.close()
	except:
		print "config.ini wrong !!!"
		msvcrt.getch()
		return
	
	sys.path.append(workdir)
	import makepyfile
	try:
		makepyfile.MakePyfile("server")
	except:
		traceback.print_exc()
		print "=====================================\npress any key to revert:"
		msvcrt.getch()
		print "reverting ..."
		clst,alst,rlst,dlst,mlst = SVNStatus(dst)
		rvts = rlst+dlst+mlst
		if rvts and SVNRevert(rvts) != 0:
			print "%s Revert ERROR !!!"%dst
			msvcrt.getch()
			return
		try:
			for f in alst:
				os.remove(f)
		except:
			print "%s Revert NOT Clear !!!"%dst
			msvcrt.getch()
			return
		if SVNIsModified(dst):
			print "%s Revert NOT Clear !!!"%dst
			msvcrt.getch()
		return
	
	if SVNCommitAll(dst, "导表") != 0:
		print "%s Commit ERROR !!!"%dst
		msvcrt.getch()
		return
	
	print "auto makepyfile Done : %s -> %s"%(workdir, dst)
	msvcrt.getch()

if __name__ == "__main__":
	main()
