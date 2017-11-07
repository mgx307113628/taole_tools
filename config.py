#coding:cp936

#BASH_PATH = "D:/cygwin64/bin/bash"
#FIND_PATH = "D:/cygwin64/bin/find"
#SORT_PATH = "D:/cygwin64/bin/sort"
#GENFILE_PATH = "E:/tools/genfiletags.sh"

PATH_ROOT = "E:/taohua2/"
MASTER_DIRS = ["ready", "trunk", "violet", "yujian"]
PUBLIC_DIRS = ["tifu", "quanfu"]

MAKEPY_DIRS = [
	["开发",	"E:/taohua2/导表/0开发",	"",],
	["策划",	"E:/taohua2/导表/1策划",	"E:/taohua2/master/ready/",],
	["体服",	"E:/taohua2/导表/2体服",	"E:/taohua2/master/trunk/",],
	["全服",	"E:/taohua2/导表/3全服",	"E:/taohua2/master/violet/",],
	["御剑",	"E:/taohua2/导表/4御剑",	"",],#E:/taohua2/master/yujian/
	["手游策划",	"E:/pisces/策划导表",	"",],
	["手游体服",	"E:/pisces/策划体服",	"",],
]

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
