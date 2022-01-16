'''Client入口'''

from socket import *
import json
import protocol
from FrozenToolKit.FrozenWiget import processBar #引入进度条

class Client:
    '''FTP Client'''
    def __init__(self):
        self.socket = None
        self.MAX_RECV = 4096
        self.user = {}
        self.buffer_recv = ''#接受消息的缓存
        self.buffer_sticky = ''#粘包分包剩余数据缓存
        #Appendix
        #self.prcBar = None

    def __del__(self):
        self.socket.sendall(protocol.FTPMes('',999))#Exit
        self.socket.close()

    def start(self):
        '''启动FTP服务'''
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.connect(("127.0.0.1",9968))
        #用户认证与处理
        if self.login():
            print("Login Successfully! typing 'help/man' ask for more commands")
            while self.handle():
                pass

    def login(self):
        '''登录FTP服务器'''
        while True:
            self.user['UID'] = input("User ID: ").strip()
            password = input("Password: ").strip()
            self.socket.sendall(protocol.FTPMes('',100,uid=self.user['UID'],pwd=password))
            self.recvall_bySuffix(protocol.suffix)
            mes = json.loads(self.buffer_recv)
            self.buffer_recv = ''#清空
            if mes['state'] == 100:
                break
            else: print("Authenticate Failed!")
        return True

    def handle(self):
        '''处理用户各种FTP请求'''
        request = input("[{}]>>".format(self.user['UID'])).strip()
        if request == 'exit':
            return False
        self.socket.sendall(protocol.FTPMes(request))#还未解决粘包
        self.recvall_bySuffix(protocol.suffix)
        mes = json.loads(self.buffer_recv)
        self.buffer_recv = ''#清空
        if int(mes['state'])==200:#下载请求且成功请求
            #简单起见就默认下载到当前路径的downloads目录下
            with open("./downloads/{}".format(request.split(' ')[1]),"w",encoding=protocol.coder) as file:
                file.write(mes['message'])
            print("Download Successfully!")
            print("可能的编码方式:{}".format(mes['coder']))
        elif int(mes['state'])==202:#大文件传输请求
            request2 = '1'#默认接受
            if int(mes['size']) >= 268435456:#256MB
                request2 = input("文件较大（>=256MB）传输可能需要一段时间，请再次确认是否需要GET(0:NO Others:YES) >>").strip()
            if request2 != '0':
                self.socket.sendall(protocol.FTPMes('ACCEPT',202,buffsize=self.MAX_RECV))#接受
                with open("./downloads/{}".format(request.split(' ')[1]),"w",encoding=protocol.coder) as file:
                    self.recvall_bySuffix_BigFile(file,protocol.suffix,int(mes['size']))
                print("文件下载完成")
                print("可能的编码方式:{}".format(mes['coder']))
            else:
                self.socket.sendall(protocol.FTPMes('CANCEL',203))#拒绝
            pass
        else:
            print(mes['message'])
        return True

    def recvall_bySuffix(self,suffix):
        '''根据suffix不断接受数据并保存在buffer_recv剩余数据缓存在buffer_sticky（这个函数由于类设计问题没有做分包）'''
        self.buffer_recv=''#清空
        if self.buffer_sticky:
            print("REST")
            self.buffer_recv += self.buffer_sticky #载入剩余数据
            self.buffer_sticky = ''
        pos_suffix = self.buffer_recv.find(suffix)
        while pos_suffix == -1:
            inflow = self.socket.recv(self.MAX_RECV)
            if not inflow:
                raise EOFError('socket closed [Received: {} bytes]'.format(len(self.buffer_recv)))
            self.buffer_recv += inflow.decode(protocol.coder)
            pos_suffix = self.buffer_recv.find(suffix)
        self.buffer_sticky = self.buffer_recv[len(suffix)+pos_suffix:]#剩余数据缓存
        self.buffer_recv = self.buffer_recv[:pos_suffix]#分包完成

    def recvall_bySuffix_BigFile(self,file,suffix,fileSize):
        '''大文件接受self.buffer_recv直接就是文件内容，第一个参数file是文件指针'''
        self.buffer_recv=''#清空
        curlength = 0
        prcBar = processBar(fileSize)
        prcBar.__next__()
        while True:
            if self.buffer_sticky:
                #print("REST")
                self.buffer_recv += self.buffer_sticky #载入剩余数据
                self.buffer_sticky = ''
            pos_suffix = self.buffer_recv.find(suffix)
            while pos_suffix == -1:
                inflow = self.socket.recv(self.MAX_RECV)
                if not inflow:
                    raise EOFError('socket closed [Received: {} bytes]'.format(len(self.buffer_recv)))
                self.buffer_recv += inflow.decode(protocol.coder)
                pos_suffix = self.buffer_recv.find(suffix)
            self.buffer_sticky = self.buffer_recv[len(suffix)+pos_suffix:]#剩余数据缓存
            self.buffer_recv = self.buffer_recv[:pos_suffix]#分包完成
            self.buffer_recv  = json.loads(self.buffer_recv)
            curlength += len(self.buffer_recv['message'])
            file.write(str(self.buffer_recv['message']))
            prcBar.send(curlength)
            if int(self.buffer_recv['state']) == 203:
                break
            self.buffer_recv = ''#清空
        
    #各类处理方法 ↓（private）
    def _func(self):
        pass

if __name__ == "__main__":
    client = Client()
    client.start()