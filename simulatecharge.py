#coding:cp936

import random
import hashlib
import urllib
import time
import msvcrt
import urllib
import urllib2
import json

CHARGEKEY_360 = "2cdd61e5d4cf21edd22843020b52cf30"
CHARGEKEY_YY = "bGVCQSlfggRAtVqLc3zJOpYYkghxGxw1"

def RandomGet(lst):
	n = len(lst)
	if n > 0:
		return lst[random.randint(0, n-1)]
	return None

def RandomPasswd(n = 8):
	chs = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
	chs += [chr(i) for i in xrange(ord('A'), ord('Z')+1)]
	chs += [chr(i) for i in xrange(ord('0'), ord('9')+1)]
	pwd = ""
	for i in xrange(n):
		pwd += RandomGet(chs)
	return pwd

def main():
	try:
		iput = raw_input("选择账号来源（360:1,多玩:2）: ")
		source = int(iput.strip())
		if source not in (1, 2):
			raise
		iput = raw_input("服务器ID（比如1001,1027）: ")
		sid = int(iput.strip())
		iput = raw_input("角色ID: ")
		rid = int(iput.strip())
		iput = raw_input("第三方账号ID（指令$p who.m_OpenAccount的结果）: ")
		uid = iput.strip()
		iput = raw_input("充值人民币（单位元）: ")
		money = int(iput.strip())
		amount = money*45
	except:
		print "输入错误"
		msvcrt.getch()
		return
	stype = "virtual"
	pno = RandomPasswd(15)
	tm = int(time.time())
	if source == 1:
		gkey = "thyj2"
		world = 111
		sign = hashlib.md5("%d%s%d%s%d%d%d%s%s%s%s"%(amount, gkey, money, pno, rid, sid, tm, stype, uid, world, CHARGEKEY_360)).hexdigest()
		args = {
			"gkey" : gkey,
			"world": world,
			"skey" : sid,
			"roleid" : rid,
			"uid" : uid,
			"type" : stype,
			"money" : money,
			"amount" : amount,
			"orderid" : pno,
			"time" : tm,
			"sign" : sign,
		}
		path = "/delivermechant.php"
	else:
		gkey = "THYJ2"
		itemid = ""
		price = ""
		cparam = ""
		sign = hashlib.md5("%s%s%d%d%s%d%s%d%d%s%s%s%s"%(uid,pno,money,amount,stype,tm,gkey,sid,rid,itemid,price,cparam,CHARGEKEY_YY)).hexdigest().lower()
		args = {
			"game" : gkey,
			"server" : sid,
			"role" : rid,
			"account" : uid,
			"type" : stype,
			"rmb" : money,
			"num" : amount,
			"orderid" : pno,
			"time" : tm,
			"itemid" : itemid,
			"price" : price,
			"cparam" : cparam,
			"sign" : sign,
		}
		path = "/delivermechantyy.php"
	path = "http://192.168.8.133:6962"+path
	args = urllib.urlencode(args)
	print "REQUEST:", path+"?"+args
	print "..."
	req = urllib2.Request(path, args)
	res = urllib2.urlopen(req)
	r = res.read()
	m = json.loads(r)
	print "RECEIVE: %s"%m
	print "="*80
	if source == 1:
		if m.get("errno") == 0:
			print "充值成功!!"
		else:
			print "充值失败!!!"
			errmsg = m.get("errmsg", "")
			if errmsg:
				print errmsg
	elif source == 2:
		if m.get("code") == 1:
			print "充值成功!!"
		else:
			print "充值失败!!"
	msvcrt.getch()

if __name__ == "__main__":
	try:
		main()
	except:
		msvcrt.getch()
