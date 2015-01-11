#!/usr/bin/env python2
# -*- coding:utf-8 -*-

#rom flask import g
from gevent import socket
from time import time, sleep
from . import app
from flask import g
import threading
import string 
import redis
import re

class dmrobot(): 
    def __init__(self):  
        #threading.Thread.__init__(self)  
        self.HOST = None  
        self.PORT = None  
        self.NICK = "gdanmakubot"
        self.IDENT="gdanmakubot"
        self.REALNAME="DANMAKU"
        self.channel = None
        self.timeout = 180
        self.dmch = None
        self.dmpw = None
        self.pingout = 5
        self.thread_stop = True
        self.ss = socket.socket()
        self.checked = False
        self.method = "MSG" #CHANNEL OR MSG
        self.commands = {"PING":0,"PONG":1,"JOIN":2,"LEAVE":3,"QUIT":4,"PRIVMSG":5}
        self.online = False

    def run(self): #Overwrite run() method, put what you want the thread do here  
        self.thread_stop = False
        if not self.checked or not self.online:
            return None
        last_ping = time()

        matchuser = re.compile(ur'^\:(\S+)\!')
        while not self.thread_stop: 
            #判断是否存活
            pinging = False;
            if time()-last_ping > self.timeout :
                ss.send("PING :TIMEOUTCHECK\r\n")
                pinging = True
            #获得buffer并分离buffer的每一行
            readbuffer=""
            readbuffer = self.ss.recv(1024)
            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop()
            
            #对每一行处理
            for line in temp:
                print line
                line = string.rstrip(line)
                line = string.split(line)
                cmdfound = False
                for i in range(0,len(line)):
                    if self.commands.has_key(line[i]):
                        cmdfound = True
                        break
                if cmdfound is False:
                    continue
                if line[i] == 'PING':
                    self.ss.send(''.join(["PONG ",line[i+1],'\r\n']))
                    pinging = False
                    last_ping = time();
                elif line[i] == 'PONG':
                    pinging = False
                    last_ping = time();
                elif line[i] == 'JOIN':
                    if not line[i+1] == self.channel :
                        online = False
                elif line[i] == 'PRIVMSG':
                    match = matchuser.split(line[i-1])
                    user = match[1]
                    content = ""
                    for j in range(i+2,len(line)):
                        content = ''.join([content,' ', line[j]])
                    content = string.strip(content)
                    content = content.strip(':')
                    if line[i+1][0] == '#':
                        if self.method == 'CHANNEL':
                            if self.shoot(content):
                                self.ss.send(''.join(["PRIVMSG ", line[i+1], ' ', 'Shoot!','\r\n' ]))
                            else:
                                self.ss.send(''.join(["PRIVMSG ", line[i+1], ' ', 'Server Config Error.','\r\n' ]))
                        else : self.ss.send(''.join(["PRIVMSG ", line[i+1], ' ', 'Please msg me privately','\r\n' ]))
                    else :
                        if self.shoot(content):
                            self.ss.send(''.join(["PRIVMSG ", user, ' ', 'Shoot!','\r\n' ]))
                        else:
                            self.ss.send(''.join(["PRIVMSG ", user, ' ', 'Server Config Error.','\r\n' ]))   
            if pinging is True:
                if(time() - last_ping > (self.timeout + self.pingout)):
                    print "TimeOut,Stop"
                    self.stop()
    
    def shoot(self, content):
        with app.app_context():
            if not self.dmch.is_open:
                key = self.dmpw
                if key is None or (not self.dmch.verify_pub_passwd(key)):
                    return False
            
            danmaku = {
                "text": content,
                "style": "white",
                "position": "fly"
            }
            self.dmch.new_danmaku(danmaku)
            return True

    def check(self):
        if self.HOST is None or self.PORT is None or self.dmch is None:
            return False

        self.ss.connect((self.HOST,self.PORT))
        self.ss.send("NICK %s\r\n" % self.NICK)
        self.ss.send("USER %s %s * :%s\r\n" % (self.IDENT, self.HOST, self.REALNAME))
        
        if self.channel is None:
            self.method = "MSG"
        else:
            self.ss.send("JOIN %s\r\n" % self.channel)
            self.ss.send("PRIVMSG %s Hello\r\n" % self.channel)

        self.checked = True
        self.online = True
        return True

    def stop(self):  
        self.thread_stop = True
        ss.send("QUIT")
        self.ss.close()
        self.online = False
        self.checked = False
         
   
def test():  
    thread1 = dmrobot()
    thread1.HOST = "card.freenode.net"
    thread1.PORT = 6666
    thread1.channel = "#tuna"
    thread1.method = "CHANNEL"
    thread1.check()
    thread1.start()
    while(1):
        sleep(1000)
    return  
   
if __name__ == '__main__':  
    test()  