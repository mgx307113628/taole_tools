#coding:cp936

import sys
import os
import os.path
import traceback
import msvcrt
from config import *
from functions import *


def main():
	print "手动导表:"
	lst = []
	for i, d in enumerate(MAKEPY_DIRS):
		lst.append("%d.%s"%(i+1, d[0]))
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
		name, workdir, _ = MAKEPY_DIRS[idx-1]
		break
	os.chdir(workdir)
	
	cmd = raw_input("Enter SVN Command for %s { svnup, revert, [empty] } : "%workdir)
	cmd = cmd.strip()
	if cmd == "exit" or cmd == "quit":
		return
	elif cmd == "revert":
		SVNUpdate(workdir)
		clst,alst,rlst,dlst,mlst = SVNStatus(workdir)
		rvts = clst+rlst+dlst+mlst
		print rvts
		if rvts and SVNRevert(rvts) != 0:
			print "%s revert error !!!"%workdir
			msvcrt.getch()
			return
	elif cmd == "svnup":
		SVNUpdate(workdir)
		clst,alst,rlst,dlst,mlst = SVNStatus(workdir)
		if clst:
			print "%s SVN conflict !!!"%(workdir)
			msvcrt.getch()
			return
	
	dset = ReadInputDirs("Enter Dest Directory: ",maxnum=1)
	if dset is None:
		return
	dst = list(dset)[0]
	#SVNUpdate(dst)
	#if SVNIsModified(dst):
	#	print "%s NOT Equal Repository !!!"%dst
	#	msvcrt.getch()
	#	return
	
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
	
	
	while True:
		args = set()
		input_s = raw_input("Enter MakeArgs: ")
		input_s = input_s.strip()
		if input_s == "exit" or input_s == "quit":
			return
		dest = input_s.split(",")
		for s in dest:
			s = s.strip()
			if s:
				args.add(s)
		if not args:
			continue
		break
	
	success = []
	errors = {}
	for arg in args:
		print "%s......"%arg
		try:
			makepyfile.MakePyfile(arg)
			success.append(arg)
		except:
			errors[arg] = traceback.format_exc()
	
	print "%s -> %s\nsuccess: %s"%(workdir, dst, success)
	if errors:
		for arg, tb in errors.iteritems():
			print "failed %s:\n%s"%(arg, tb)
	else:
		print "failed None"
	msvcrt.getch()

if __name__ == "__main__":
	main()
