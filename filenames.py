#coding:cp936

import os
import os.path
import msvcrt
from config import *
from functions import *


def GenerateFileTags(dirs):
	for d in dirs:
		_d = d+"/.idea"
		if not os.path.exists(_d):
			os.mkdir(_d)
		if not os.path.isdir(_d):
			continue
		fname = _d+"/filenametags"
		cmd = "%s %s %s %s"%(BASH_PATH, GENFILE_PATH, d, fname)
		os.system(cmd)
		print "Generate %s !"%fname

def main():
	dirs = ReadInputDirs("Generate File Names!! Enter Directories: ")
	if dirs is None:
		return
	GenerateFileTags(dirs)
	msvcrt.getch()

if __name__ == "__main__":
	main()
