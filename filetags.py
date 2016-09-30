#coding:cp936

import os
import threading
from config import *
from functions import *


class CGenTags(threading.Thread):
	def __init__(self, d):
		threading.Thread.__init__(self)
		self.path = d
		
	def run(self):
		os.chdir(self.path)
		os.system("D:/mengguoxian/ctags58/ctags.exe -R")

def DoGenTags(dset):
	for d in dset:
		print d+"/tags......"
	threadlist = []
	for d in dset:
		trd = CGenTags(d)
		trd.start()
		threadlist.append(trd)
	for trd in threadlist:
		trd.join()

def main():
	dirs = ReadInputDirs("tags file !!Enter Directories: ")
	if dirs is None:
		return
	DoGenTags(dirs)
	print "success !!!!!"
	os.system("pause")

if __name__ == "__main__":
	main()
