'''使用协程风格的异步Server'''
from socket import *
from users import authenticate
from FrozenToolKit import FrozenFile
import settings
import protocol
import json
import os
import asyncio

class User:
    '''用于管理接入用户的数据'''
    def __init__(self,addr,_reader,_writer,_MAX_RECV):
        #socket parameter
        self.MAX_RECV = _MAX_RECV #单次最大接收字节
        #user attribute
        self.clientAddr = addr #IP Port二元标识
        self.buffer_recv = '' #接受消息的缓存
        self.buffer_sticky = '' #粘包分包剩余数据缓存
        self.buffer_send = '' #发送区（大文件需要trunk）
        self.USER_HOME = None
        self.reader = _reader #传入一个reader
        self.writer = _writer #传入一个writer

    def __del__(self):
        self.writer.close()

    async def handle(self):
        '''处理用户数据（入口程序）'''
        while True:
            try:
                await self.recvall_bySuffix(protocol.suffix)
                print(self.buffer_recv)
                mes = json.loads(self.buffer_recv)
                self.buffer_recv = ''#清空
                state = int(mes['state'])#解析STATECODE
                if state == 1:#RPC
                    request = str(mes['message']).split(' ')
                    cmd = '_CIL_' + request[0]#防止调用其他方法
                    if hasattr(self,cmd):
                        #self.session.sendall(protocol.FTPMes('{} is operating'.format(request[0]),200))
                        func = getattr(self,cmd)
                        #len_para = len(request)-1
                        await func(request[1:])#传入参数
                    else:
                        res = "No command {}, typing 'help/man' ask for more commands, Format: [cmd] [para1] [para2] ...".format(request[0])
                        await self.sendall(protocol.FTPMes(res,201))
                elif state == 100:#login
                    if authenticate(mes['uid'],mes['pwd']):
                        self.USER_HOME = os.path.join(settings.SERVER_ROOT,"home",mes['uid'])#为用户生成目录
                        if not os.path.exists(self.USER_HOME):
                            print("Makedir: {}".format(self.USER_HOME))
                            os.makedirs(self.USER_HOME)
                        await self.sendall(protocol.FTPMes('OK',100))
                    else:
                        await self.sendall(protocol.FTPMes('NO',101))  
                elif state == 999:#Exit
                    print("connection {} Exit".format(self.clientAddr))
                    return 'end'
            except EOFError:
                #print("connection {} is lost……".format(self.clientAddr))#这里有个退出BUG，实在不知道怎么解决了！
                return 'end'

    async def sendall(self,mes):
        '''自制版本的sendall'''
        self.writer.write(mes)
        await self.writer.drain()#等待写完毕
        pass

    async def recvall_bySuffix(self,suffix):
        '''根据suffix不断接受数据并保存在buffer_recv剩余数据缓存在buffer_sticky'''
        self.buffer_recv = ''#清空
        if self.buffer_sticky:
            #print("REST")
            self.buffer_recv += self.buffer_sticky #载入剩余数据
            self.buffer_sticky = ''
        pos_suffix = self.buffer_recv.find(suffix)
        while pos_suffix == -1:
            inflow = await self.reader.read(self.MAX_RECV)
            if not inflow:
                raise EOFError('socket closed [Received: {} bytes]'.format(len(self.buffer_recv)))
            self.buffer_recv += inflow.decode(protocol.coder)
            #print(len(self.buffer_recv))
            pos_suffix = self.buffer_recv.find(suffix)
        self.buffer_sticky = self.buffer_recv[len(suffix)+pos_suffix:]#剩余数据缓存
        self.buffer_recv = self.buffer_recv[:pos_suffix]#分包完成
        print(self.buffer_recv)
        return True
    
    #各类处理方法 ↓（private）
    async def _CIL_help(self,*para):#para用于制造通用接口
        await self.sendall(protocol.FTPMes("help/man: 帮助文档'\nls: 当前目录文件\nget [filename]： 下载文件"))
    
    async def _CIL_man(self,*para):
        self._CIL_help()
    
    async def _CIL_ls(self,*para):
        files = ''
        cnt = 0
        for file in os.listdir(self.USER_HOME):
            filePath = os.path.join(self.USER_HOME,file)
            if os.path.isfile(filePath):
                cnt += 1
                suffix = 'B'
                size = os.path.getsize(filePath)
                if size >= 1024:
                     size = int(size/1024)
                     suffix = 'KB'
                if size >= 1024:
                     size = int(size/1024)
                     suffix = 'MB'
                if size >= 1024:
                     size = int(size/1024)
                     suffix = 'GB'
                files += "[{}] {}{} {}\n".format(cnt,file.ljust(30),size,suffix)
                #files += "".format(cnt) + file.ljust(30) + str(os.path.getsize(filePath)) + ' KB\n'
        await self.sendall(protocol.FTPMes(files))

    async def _CIL_get(self,*para):
        if not para[0]:#必须传入文件名参数才能下载
            await self.sendall(protocol.FTPMes("Sorry please type 'get [filename]'",201))
        else:
            filePath = os.path.join(self.USER_HOME,str(para[0][0]))
            print(filePath)
            if not os.path.exists(filePath):#文件不存在
                await self.sendall(protocol.FTPMes("Sorry this file is not existed",201))
            else:
                Coder = FrozenFile.get_encoding(filePath)
                Size = os.path.getsize(filePath)
                #对Size进行判断，如果过大需要结合protocol.FTPMes_NoSuffix分批发送
                if Size < settings.METRIC_SIZE_FILE:
                    with open(filePath,'rb') as fp:
                        mes = fp.read()
                    await self.sendall(protocol.FTPMes(str(mes),200,coder=Coder,size=Size))
                else:#大文件
                    totalSize = Size
                    await self.sendall(protocol.FTPMes('',202,coder=Coder,size=Size))
                    await self.recvall_bySuffix(protocol.suffix)
                    mes = json.loads(self.buffer_recv)
                    self.buffer_recv = ''#清空
                    res = int(mes['state'])#202接受203拒绝
                    if res == 202:
                        print("Big File is Sending")
                        clientSize = int(mes['buffsize'])
                        with open(filePath,'rb') as fp:
                            while True:
                                data = fp.read(clientSize)
                                totalSize -= len(data)
                                if totalSize <= clientSize:#最后一块
                                    await self.sendall(protocol.FTPMes(str(data),203))
                                    break
                                else:
                                    await self.sendall(protocol.FTPMes(str(data),202))
                    elif res == 203: await self.sendall(protocol.FTPMes('Get Cancel Successfully!'))#应付一下

class Server:
    '''FTP Server'''
    def __init__(self):
        #Server
        self.socket = None
        self.MAX_RECV = 4096 #单次最大接收字节
        self.users = {} #保存所有用户（静态方法）
        #Client
        self.clientAddr = None

    def start(self):
        '''开启TCP FTP服务'''
        asyncio.run(self.main())
    
    async def main(self):
        '''主循环，建议通过start启动'''
        server = await asyncio.start_server(self.handle,settings.HOST_IP,settings.HOST_PORT)
        addr = server.sockets[0].getsockname()
        print("Server on {}".format(addr))
        async with server:
            await server.serve_forever()

    async def handle(self,reader,writer):
        '''处理每一个连接进来的Client的请求'''
        while True:
            peer = writer.get_extra_info('peername')#可以标识唯一用户 
            if peer not in self.users.keys(): #载入新用户
                self.users[peer] = User(peer,reader,writer,self.MAX_RECV)
            res = await self.users[peer].handle()
            if res == 'end':
                self.users.pop(peer)


if __name__ == "__main__":
    server = Server()
    server.start()