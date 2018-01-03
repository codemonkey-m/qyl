# -*- coding:utf-8 -*-
import os
import pylib
import pickle
import requests
import re

rootpath = "./qyl/"
try:
	os.mkdir(rootpath)
except Exception as e:
	pass

log = pylib.logs(True, rootpath+"logs.txt")

webroot = "http://www.qyl88.com/"
mainpage = "recent/"

sop = None
try:
	sopfile = open(rootpath+"sop.txt", 'r+')
	sop = pickle.load(sopfile)
	sopfile.close()
except Exception as e:
	pass

if sop == None:
	sop = {'page' : '1', 'url' : '0'}
log.Msg(sop)

def SaveSop(data):
	#重新打开用以保存
	sopfile = open(rootpath+"sop.txt", 'w+')
	pickle.dump(data, sopfile)
	sopfile.close()

urltxt = open(rootpath+"urls.txt", 'w+')
while True:
	log.Msg("读取第"+sop['page']+"页")
	menupage = webroot+mainpage
	if sop['page'] != '1':
		menupage = menupage + sop['page']
	log.Msg("当前目录页链接:"+menupage)

	menupagedata = ""
	try:
		menupagedata = pylib.ReadUrl(menupage)
	except Exception as e:
		log.Msg(e)
		continue

	#查找页面上的视频页链接
	menupagelinks = []
	while True:
		reLink = re.search("a href\=\"\/(\d+\/.*\/)\"", menupagedata)
		if reLink == None:
			break

		menupagedata = menupagedata[reLink.span()[1]:len(menupagedata)]
		menupagelinks.append(reLink.group(1))

	log.Msg("共读取到视频页面数:%d"%len(menupagelinks))
	for index in range(int(sop['url']), len(menupagelinks)):
		log.Msg("当前第%d"%(index+1)+"/%d条"%len(menupagelinks))
		log.Msg("读取页面信息:"+webroot+menupagelinks[index])
		videopagedata = pylib.ReadUrl(webroot+menupagelinks[index])

		reVideo = re.search("<source src\=\"(.*\.mp4)\"", videopagedata)
		if reVideo == None:
			log.Msg("视频链接查找失败！")
			continue
		else:
			log.Msg("视频链接:"+reVideo.group(1))

		reName = re.search("\d*/(.*)/", menupagelinks[index])
		if reName != None:
			log.Msg("视频名字:"+reName.group(1))

		urltxt.write(reName.group(1) + "\t" + reVideo.group(1) + "\r\n")

		#pylib.Download(url = reVideo.group(1), filename = reName.group(1)+".mp4", dir = rootpath, logs = log)

		sop['url'] = "%d"%index
		SaveSop(sop)
	urltxt.flush()
	sop['url'] = "0"
	sop['page'] = "%d"%(int(sop['page'])+1)
pylib.pause()