'''基于多线程的TCP游戏客户端'''

from queue import Queue
from socket import *
from ZNet.ZProtocol import Protocol
import threading
import ZGame
import json
import os
import time
from ZObject.ZAttribution import ZAttribution

class Client():
    events = Queue() #处理来自Server的信息
    session = None
    def __init__(self,server_ip,server_port):
        Client.session = None
        self.SIZE_RECV = 4096
        self.buffer_recv = b''
        #Server的信息
        self.serverIP = server_ip
        self.serverPort = server_port
        Client.session = socket(AF_INET,SOCK_STREAM)
        self.session.setblocking(False) #非阻塞
        try:
            Client.session.connect((self.serverIP,self.serverPort))
            ZGame.GAME.Client = self #共享
        except:
            pass

    def __del__(self):
        print("{} is closing".format(self.serverIP))
        Client.session.sendall(Protocol.toStream(Protocol.message('exit')))
        Client.session.close()
        
    def start(self):
        if Client.session: 
            #用户登录
            while not self.login():
                pass
            #开启一个接受信息的线程
            thr_client = threading.Thread(target=self.helper_recv)
            thr_client.setDaemon(True)
            thr_client.start()
            while True:
                self.handle()
        else:
            print("start failed! please ensure a explicit server(IP,Port)")
        self.exit()

    def login(self):
        '''用户登录'''
        account = input("[Account]:")
        password = input("[Password]:")
        Client.session.sendall(Protocol.toStream(Protocol.message('login',account=account,password=password,charactor=ZGame.GAME.ME.getAttr())))
        time.sleep(1)
        try:  
            self.recv_all()
            event = Client.events.get()#取出登录事件
            if event['state'] == 'OK':
                ZGame.GAME.Login = True
                ZGame.GAME.ME.attribution['Name'] = account
                ZGame.GAME.PlayerManager[account] = ZGame.GAME.ME #因为有可能服务端直接影响玩家，所以对自身也要映射
                return True
            else:
                print(event['prompt'])
                return False
        except:
            pass

    def exit(self):
        print("{} is closing".format(self.serverIP))
        Client.session.sendall(Protocol.toStream(Protocol.message('exit')))
        Client.session.close()

    def handle(self):
        '''处理来自Server的各类事件'''
        while not Client.events.empty():
            event = Client.events.get()#取出事件
            #print(event)
            request = event['request']
            if request == 'addplayer':
                player = event['player']
                ZGame.GAME.PlayerManager[player['Name']] = ZGame.GAME.addCreature(ZAttribution(player),ZGame.GAME.players)
            elif request == 'setattr':
                #print(event['attr'])
                ZGame.GAME.PlayerManager[event['attr']['Name']].updateAttr(event['attr'])
                #print(ZGame.GAME.PlayerManager)
        #self.session.sendall(Protocol.toStream(Protocol.message(i)))
        return True

    def syn(self):
        '''发送Client的游戏对象的属性字典'''
        Client.session.sendall(Protocol.toStream(Protocol.message('setattr',attr=ZGame.GAME.ME.getAttr())))

    def helper_recv(self):
        '''接受信息的线程'''
        while True:
            try:
                self.recv_all()
            except:
                pass

    def recv_all(self):
        '''接受所有信息'''
        more = Client.session.recv(self.SIZE_RECV)
        if not more:  # 无新数据，客户端关闭
            self.exit()
        else: 
            data = self.buffer_recv + more
            #print('client recv',data)
            if Protocol.SEGREGATION in data:
                # 可能接受多个完整的数据，将完整的数据存入self.push_to_top,剩余数据（若还有）不构成完整的数据包放回
                data = data.split(Protocol.SEGREGATION)
                if data[-1] != b'':  # 不是完整的数据包
                    self.buffer_recv = data[-1]
                data = data[:-1]
                for d in data:
                    Client.events.put(Protocol.fromStream(d))#交给Client的事件列表
            else:  # 无完整数据包
                self.buffer_recv = data

if __name__ == "__main__":
    client = Client('127.0.0.1',19219)
    client.start()