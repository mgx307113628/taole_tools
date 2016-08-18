#coding:cp936

BASH_PATH = "D:/cygwin64/bin/bash"
FIND_PATH = "D:/cygwin64/bin/find"
SORT_PATH = "D:/cygwin64/bin/sort"
GENFILE_PATH = "E:/tools/genfiletags.sh"

PATH_ROOT = "E:/yujian/"


MAKEPY_DIRS = [
	"E:/yujian/a导表/策划导表",
	"E:/yujian/a导表/体服导表",
	"E:/yujian/a导表/全服导表",
]

AUTO_MAKE_DIRS = {
	"E:/yujian/a导表/策划导表" : "E:/yujian/ready/",
	"E:/yujian/a导表/体服导表" : "E:/yujian/trunk/",
	"E:/yujian/a导表/全服导表" : "E:/yujian/trial/",
}

EXCLUDE_NAME = [		#排除的文件
	"tags",
	#"filenametags",
	#"game.kpf",
	#"game6.komodoproject",
	#".komodotools",
	".settings",
	".idea",
	".svn",
	".project",
	".pydevproject",
	".git",
	".gitignore",
]
