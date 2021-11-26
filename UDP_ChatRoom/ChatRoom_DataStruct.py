''''定义了客户端和服务端所有的数据结构，主要包括用户、消息'''
import json
import datetime
from enum import Enum

class User():#本质上就是个字典
    def __init__(self,nickname,userid,password):
        #Attribute
        self.user={}
        self.user["NickName"] = nickname
        self.user["UserID"] = userid
        self.user["Password"]  = password
        #Status
        #self.user["online"]  = online
    def wrap(self):#打包为json
        return json.dumps(self.user)

class UserInfo():#简化版User类用于存储当前在线用户信息
    def __init__(self,nickname,userid,address):
        self.info = {}
        self.info["NickName"] = nickname
        self.info["UserID"] = userid
        self.info["Address"] = address
    def wrap(self):#打包为json
        return json.dumps(self.info)

class TypeMessage(Enum):
    Normal = 0 #普通的广播消息，mes内为信息
    #Request(Clint)
    Request = 1 #通用请求
    Login = 2 #此时mes内为(uid,password)
    Register = 3 #此时mes内为(nickname,uid,password)
    Exit = 4 #此时mes内应该为用户的UID
    PrivateChat = 5 #此时mes内为信息，在attach内为对方的user信息
    #Response(Server)
    Response = 100 #通用回复
    OK = 101
    NO = 102
    #Error
    Error = 200 #通用错误
    error_mesType = 201 #构造消息的数据类型错误

    @staticmethod
    def isMessage(num):
        num = int(num)
        return num==TypeMessage.Normal.value
    @staticmethod
    def isRequest(num):
        num = int(num)
        return TypeMessage.Request.value<=num<TypeMessage.Response.value
    @staticmethod
    def isResponse(num):
        num = int(num)
        return TypeMessage.Response.value<=num<TypeMessage.Error.value
    @staticmethod
    def isError(num):
        num = int(num)
        return num>=TypeMessage.Error.value

class Message():
    def __init__(self,mes,type=TypeMessage.Normal.value,attach=None):
        self.content=dict()
        self.content["Type"] = type
        self.content["Time"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.content["Content"] = mes
        if attach:#如果有额外信息
            self.content["Attach"] = str(attach)
    def wrap(self):  # 打包为json
        return json.dumps(self.content)
        #if self.content["Type"] >= TypeMessage.Request:#将请求解析出来（服务端逻辑）

if __name__=="__main__":
    user = User("xiaoming","nxljyc","123321",False)
    print(user.wrap())
    mes = Message("12355",TypeMessage.PrivateChat.value)
   # print(mes.wrap())