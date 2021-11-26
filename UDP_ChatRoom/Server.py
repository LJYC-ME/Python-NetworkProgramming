'''Server这里由于时间不足只能随便乱写了'''
import threading
from socket import *
from ChatRoom_DataStruct import *
import json
import random
import time

ServerBook = {"local":("127.0.0.1",5122),"online":("服务器内网IP","服务端口号")}
ServerSwitch = "local"

reg_users = []#注册过的用户（内容为User字典）
cur_users = []#当前所有用户（内容为UserInfo字典）
AddrRefNickName = {}#地址到昵称的反射

def NPC_haidaogou(serverSocket):
    '''一个简单欢乐的群发线程，也可以改造为心跳维活'''
    while True:
        len = random.randint(1, 5)
        mes = "汪~" * len
        res = Message("{} ({})\n{}".format("聒噪の海盗狗", datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), mes))
        for alluser in cur_users:
            server.sendto(res.wrap().encode("UTF-8"), alluser.info["Address"])
        timer = random.randint(5,10)
        time.sleep(timer)

def addDefaultUsers():
    '''默认用户，方便调试'''
    frozen = User("Frozen","frozen","123321")
    jerry = User("Jerry", "jerry", "123321")
    reg_users.append(frozen)
    reg_users.append(jerry)

if __name__=="__main__":
    addDefaultUsers()#测试需要
    #一个最简单的UDP Server
    server=socket(AF_INET,SOCK_DGRAM)
    server.bind(ServerBook[ServerSwitch])#绑定在(IP,Port)组成的端口
    #UDP每一个recvfrom对应一个sendto
    #NPC
    haidaogou=threading.Thread(target=NPC_haidaogou, args=(server,))
    haidaogou.start()
    while True:
        datagram,sender=server.recvfrom(2048)#接受2048Bytes的Datagram
        mes = json.loads(datagram.decode('UTF-8'))
        print(mes)
        type  = mes["Type"]
        if TypeMessage.isMessage(type):#普通信息
            res = Message("{} ({})\n{}".format(AddrRefNickName[sender],mes["Time"],mes["Content"]))
            for alluser in cur_users:
                if alluser.info["Address"] != sender:
                    server.sendto(res.wrap().encode("UTF-8"), alluser.info["Address"])
        elif TypeMessage.isRequest(type):#用户请求
            if type is TypeMessage.Login.value:#登录请求
                info = tuple(mes["Content"])
                #print("Login:"+str(info))
                res = Message(TypeMessage.NO.value, type=TypeMessage.Response.value)
                #检查是否注册
                nickname = None
                for tracer in reg_users:#如果存在且账号密码相同就承认
                    #print(tracer.user["UserID"])
                    if tracer.user["UserID"] == info[0] and tracer.user["Password"] == info[1]:
                        nickname = tracer.user["NickName"]
                        res.content["Content"]=TypeMessage.OK.value
                        break
                # 检查是否在线
                for tracer in cur_users:
                    if tracer.info["UserID"] == info[0]:
                        res.content["Content"] = TypeMessage.NO.value
                        break
                if res.content["Content"] == TypeMessage.OK.value:#登录成功则加入当前用户组
                    adduser = UserInfo(nickname,info[0],sender)
                    cur_users.append(adduser)
                    AddrRefNickName[sender]=nickname#建立反射
                server.sendto(res.wrap().encode("UTF-8"),sender)#将回复值返回
            elif type is TypeMessage.Register.value:#注册请求
                info = tuple(mes["Content"])
                res = Message(TypeMessage.OK.value, type=TypeMessage.Response.value)
                for tracer in reg_users:#检查是否注册
                    if tracer.user["UserID"] == info[1]:
                        res.content["Content"]=TypeMessage.NO.value
                        break
                if res.content["Content"] == TypeMessage.OK.value:#保存该用户
                    adduser = User(info[0],info[1],info[2])
                    reg_users.append(adduser)
                server.sendto(res.wrap().encode("UTF-8"), sender)
            elif type is TypeMessage.Exit.value:#退出请求
                for i in cur_users:
                    #print(i.info["Address"])
                    #print(tuple(mes["Content"]))
                    if i.info["UserID"]==mes["Content"]:
                        print("{}-{}({}) exit".format(mes["Time"],i.info["UserID"],i.info["Address"]))
                        cur_users.remove(i)
                        break
            elif type is TypeMessage.PrivateChat.value:#私聊请求
                #此时需要在attach中添加私聊对象的数组
                friends = mes["Attach"].split(';')
                for name in friends:
                    print(name)
                    for friend in cur_users:
                        if friend.info["NickName"] == name:
                            res = Message("---------------私聊信息---------------\nFrom:{} ({})\n{}\n".format(AddrRefNickName[sender], mes["Time"], mes["Content"]))
                            server.sendto(res.wrap().encode("UTF-8"), friend.info["Address"])
        #print(mes)
        #server.sendto(("Reply:"+mes).encode("UTF-8"),sender)#将接受的消息返回
