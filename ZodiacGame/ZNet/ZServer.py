'''基于多线程的TCP游戏服务端'''

from os import stat
from queue import Queue
from socket import *
from ZNetSettings import NET_SETTING
import json
import gc #垃圾回收
import threading
from ZProtocol import *
from Users import Account

class User():
    '''连入服务端的客户'''
    def __init__(self,_session,_address):
        self.state = 'offline'#{online,offline,zombie}
        self.session = _session
        self.address = _address
        self.connecting = True
        #Data Buffer
        self.buffer_recv = b''
        #Game Data(游戏数据，登录成功后等待载入)
        self.ID = None #登录后获取，可以用于判定重复登录
        self.charactor = None #玩家角色的属性
    
    def handle(self):
        '''处理与客户端的通信'''
        while self.connecting:
            #print("dealing")
            try:
                self.recv_all()
            except:
                pass
        print("{} is closing".format(self.address))
        self.session.close()
        me = Server.clients.pop(self.address)
        del me
        gc.collect()

    def recv_all(self):
        more = self.session.recv(NET_SETTING.SIZE_RECV)
        if not more:  # 无新数据，客户端关闭，关闭套接字，下一轮套接字事件为关闭或异常，处理后续清理
            self.connecting = False
        else: 
            #print(more)
            data = self.buffer_recv + more
            #print('server recv',data)
            if Protocol.SEGREGATION in data:
                # 可能接受多个完整的数据，将完整的数据存入self.push_to_top,剩余数据（若还有）不构成完整的数据包放回
                data = data.split(Protocol.SEGREGATION)
                if data[-1] != b'':  # 不是完整的数据包
                    self.buffer_recv[self.session] = data[-1]
                data = data[:-1]
                for d in data:
                    #数据包处理
                    event = Protocol.fromStream(d)
                    if (event['request']=='exit'):#退出事件
                        self.connecting = False 
                    elif (event['request']=='login'):#登录事件
                        if Account.Authenticate(event['account'],event['password']):
                            reA = True
                            for user in Server.clients.values():
                                if user.ID == event['account']:#重复登录
                                    self.session.sendall(Protocol.toStream(Protocol.message('login',state = 'NO',prompt='该用户已经在线')))
                                    reA = False
                                    break
                            if reA:#登录成功
                                self.session.sendall(Protocol.toStream(Protocol.message('login',state = 'OK')))
                                self.state = 'online'
                                self.ID = event['account'] #更改状态
                                self.charactor = event['charactor']
                                self.charactor['Name'] = self.ID #用ID标识角色
                                Server.getOnlineUsers(self)
                                Server.broadCastToOthers(self,Protocol.message('addplayer',player=self.charactor))
                        else:#登录失败
                            self.session.sendall(Protocol.toStream(Protocol.message('login',state = 'NO',prompt='账号或密码错误')))
                    else:#其他事件交给Server的事件列表
                        Server.events.put(event)
            else:  # 无完整数据包
                self.buffer_recv[self.session] = data


class Server():
    '''Server'''
    events = Queue() #处理来自所有客户端的完整包
    clients = {} #维持所有Active Sockets

    def __init__(self):
        self.listener = None 

    def start(self):
        self.listener = socket(AF_INET,SOCK_STREAM)
        self.listener.setblocking(False)#设置非阻塞
        self.listener.setsockopt(SOL_SOCKET,SO_REUSEADDR,NET_SETTING.OPT_PORTREUSE)
        self.listener.bind((NET_SETTING.HOST_IP,NET_SETTING.HOST_PORT))
        print("Server start at {} successfully".format((NET_SETTING.HOST_IP,NET_SETTING.HOST_PORT)))
        self.listener.listen(NET_SETTING.MAX_LISTEN)
        helper = threading.Thread(target=self.handle)#处理来自客户端的事件
        helper.setDaemon(True)
        helper.start()
        while self.handle():
            try:
                session,clientAddr = self.listener.accept()
                print("Start a new session with {}".format(clientAddr))
                client = User(session,clientAddr)
                Server.clients[clientAddr] = client #地址-><class>User
                thr_user = threading.Thread(target=client.handle)
                thr_user.setDaemon(True)
                thr_user.start()
            except:
                print("\rCurrent Users:{} ".format(len(self.clients)),end='')

    def handle(self):
        '''处理Server.events中的事项（为了同步因此多为广播事件）'''
        while not Server.events.empty():
            #print(Server.events)#Debug
            event = Server.events.get()#(0执行者,1事件)
            #print(event)
            request = event['request'] 
            if request == 'setattr':#更新某单位的全部属性（由于设计问题暂不考虑效率）通过Name在GAME.PlayerManager中快速修改
                #self.broadCast(Protocol.message(request,attr=event['attr']))
                self.syn(Protocol.message(request,attr=event['attr']))
            #处理之后需要广播给所有人（可以考虑处理一定数量级后再广播）
        return True

    @staticmethod
    def syn(attr,state='online'):
        for each in Server.clients.values():
            if each.state != state:
                continue
            if each.ID == attr['attr']['Name']:#更新列表状态
                each.charactor = attr['attr']
            each.session.sendall(Protocol.toStream(attr))  

    @staticmethod
    def broadCast(message,state='online'):
        for each in Server.clients.values():
            if each.state != state:
                continue
            each.session.sendall(Protocol.toStream(message))  
            

    @staticmethod
    def broadCastToOthers(announcer,message,state='online'):
        '''默认向其他状态为online人广播一条消息'''
        #assert isinstance(message,Protocol.message)
        for each in Server.clients.values():
            if each == announcer or each.state != state:
                continue
            each.session.sendall(Protocol.toStream(message))

    @staticmethod
    def getOnlineUsers(announcer):
        '''想announcer发送所有在线用户'''
        for each in Server.clients.values():
            if each == announcer or each.state != 'online':
                continue
            else:
                announcer.session.sendall(Protocol.toStream(Protocol.message('addplayer',player=each.charactor)))

if __name__ == "__main__":
    server = Server()
    server.start()