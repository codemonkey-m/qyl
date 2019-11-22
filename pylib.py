# -*- coding:utf-8 -*-
#py公共库,ming@2017-05-31 21:37:25
#2017-06-20 14:52:15 增加下载,暂停功能
#2017-09-28 12:43:03 增加日志线程安全
import datetime
import sys
import os
import requests
import threading

g_DirName = "logs/"

#日志
class logs:
    #log文件路径及名字
    logfile = None
    #是否保存到log文件
    save2file = True
    #线程锁
    mutex = threading.Lock()
    #clearlog 是否清空原有内容
    def __init__(self, save = True, filepath = None, clearlog = False):
        if not os.path.isdir(g_DirName):
            os.mkdir(g_DirName)
        if filepath == None:
            filepath = g_DirName+datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')+".txt"
        else:
            filepath = g_DirName+filepath

        self.save2file = save
        if self.save2file == False:
            return
        mode = 'a'
        if clearlog == True:
            mode = 'w'
        self.logfile = open(filepath, mode)

    # string显示的文字
    # write2file是否写入到日志文件(初始化时设置为保存到文件才生效)
    # percent标记为进度
    # num当前进度,浮点数,函数内*100
    def Msg(self, string, percent = False, num = 0.0, write2file=True,):
        if self.mutex.acquire():
            sys.stdout.write('\r                                       ')
            stime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if percent:
                sys.stdout.write('\033[4;36;40m\r' + stime + '\t%2.2f%%  ' % (num*100) + string + '\033[0m')
            else:
                text = '\r' + stime +'\t%s\r\n' % string
                sys.stdout.write(text)
                if self.save2file == True and write2file == True:
                    self.logfile.write(text)
                    self.logfile.flush()
            sys.stdout.flush()
            self.mutex.release()

#下载接口
# url 下载的链接
# dir 保存的目录
# retry 失败重试的次数
# timeout 链接超时,读取超时
def Download(url, dir="", retry=5, logs=None, timeout=(30,30)):
    curnum = 0
    while curnum < retry:
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            refilename = re.search("([a-zA-Z0-9\.\-]*)$", response.url)
            filename = None
            if refilename == None:
                filename = "NoName%d.file"%int(time.time())
            else:
                filename = refilename.group(1).encode('utf8')
            filelen = int(response.headers.get("Content-Length"))
            if logs != None:
                logs.Msg("下载文件：%s"%filename.encode('utf8') + ",长度:%d"%filelen)
                logs.Msg("下载链接：%s"%response.url.encode('utf8'))
            downloadfile = open(selfdir + dir + "/" + filename, 'w')
            readlen = 0
            timerecord = int(time.time())
            downrecord = 0
            speed = 0.0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    nowtime = int(time.time()) - timerecord
                    if nowtime > 1:
                        speed = (downrecord/float(1024)) / float(nowtime)
                        downrecord = 0
                        timerecord = int(time.time())
                    else:
                        downrecord += len(chunk)
                    readlen += len(chunk)
                    downloadfile.write(chunk)
                    if logs != None:
                        logs.Msg(filename + "\t%2.1fKB/s"%speed, True, (readlen / float(filelen)), False)
            downloadfile.flush()
            downloadfile.close()
        except Exception as e:
            if logs != None:
                logs.Msg(e)
                logs.Msg(url + " 下载失败,重试!")
            curnum += 1
            continue
        if logs != None:
            logs.Msg(dir + "/" + filename + " 下载完成.")
        return
    if logs != None:
        logs.Msg(dir + "/" + filename + " 重试超过指定次数,下载失败.")

#类似 os.system("pause") 通用于win+linux
def pause():
    strText = '按回车键继续...'
    print(strText.decode('utf8'))
    try:
        input()
    except Exception:
        pass
