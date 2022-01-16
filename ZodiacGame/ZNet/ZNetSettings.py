'''游戏网络模块的配置文件'''

class ZNetSettings():
    '''游戏的网络服务配置'''
    #General
    SIZE_RECV = 4096 #一次recv的接收量
    SEGREGATION = '|#|'
    #Server
    HOST_IP = '127.0.0.1'
    HOST_PORT = 19219
    MAX_LISTEN = 10 #最大挂起连接
    OPT_PORTREUSE = True #是否端口复用

NET_SETTING = ZNetSettings()#Singleton