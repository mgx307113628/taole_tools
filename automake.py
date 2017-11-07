#coding:cp936

import sys
import os
import os.path
import traceback
import msvcrt
import subprocess
import datetime
from config import *
from functions import *


def GetChoise(hint, options):
	while True:
		try:
			input_s = raw_input(hint)
		except KeyboardInterrupt:
			continue
		input_s = input_s.strip()
		if input_s == "exit" or input_s == "quit":
			exit(0)
		if len(input_s) == 0:
			continue
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
		return idxes

def DaoBiao():
	options = {}
	notify = []
	for i, d in enumerate(MAKEPY_DIRS):
		name, _, dest = d
		if dest:
			options[i] = d
			notify.append("%d.%s"%(i, name))
	hint = "\n桃花2自动导表:\t"+"\t".join(notify)+"\nChose Work Directory: "
	idxes = GetChoise(hint, options)
	
	print "="*79
	#t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	t = datetime.datetime.now().strftime('%m月%d日%H时%M分')
	for name, workdir, dst in [options[idx] for idx in idxes]:
		si = subprocess.STARTUPINFO()
		si.dwFlags = subprocess.STARTF_USESHOWWINDOW
		si.wShowWindow = 4
		try:
			child = subprocess.Popen(["python", os.getcwd()+"\\submake.py", name, workdir, dst], cwd=workdir, creationflags=subprocess.CREATE_NEW_CONSOLE, startupinfo=si)
		except:
			traceback.print_exc()
		print "%s  %s  %s=>%s"%(name, t, workdir, dst)
	print "="*79
	return True

def main():
	while True:
		DaoBiao()

if __name__ == "__main__":
	main()
