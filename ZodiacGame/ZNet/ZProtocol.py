'''提供了所有网络层数据的格式，与其en/decode方式'''
#当前提供的数据交换方式(DEF)
import json
from enum import Enum

'''
# 协议设计
## 一条消息的基本格式(json)
(
    request:
    state: 1 #default
    broadcast: True #default
)
'''

class Protocol():
    '''游戏应用层与传输层之间的协议'''
    #类属性
    ENCODER = "UTF-8"#编码方式
    DECODER = ENCODER#解码方式
    DEF = "json"#数据交换格式（Data Exchange Format）
    SEGREGATION = b'|#|'#封针
    
    @staticmethod
    def __info__():
        '''输出当前类属性的信息'''
        print("编码方式(ENCODER):{}".format(Protocol.ENCODER))
        print("解码方式(DECODER):{}".format(Protocol.DECODER))
        print("数据交换格式方式(DEF):{}".format(Protocol.DEF))

    @staticmethod
    def message(_request,**addition):
        '''构造格式化的字典等待使用toStream发送'''
        mes = {}
        mes['request'] = _request
        mes.update(addition)#合并额外信息
        return mes

    @staticmethod
    def toStream(_dict):
        '''基于数据交换格式（DEF）返回对应对象的字节流'''
        if Protocol.DEF == "json":
            if not isinstance(_dict,dict): #类型检测
                print("{}:ERROR.数据类型错误".format(__name__))
            return (json.dumps(_dict)).encode(Protocol.ENCODER)+Protocol.SEGREGATION

    @staticmethod     
    def fromStream(_stream):
        '''从字节流返回一个与数据交换格式（DEF）一致的对象'''
        if Protocol.DEF == "json":
            if not isinstance(_stream,bytes): #类型检测
                print("{}:ERROR.数据类型错误".format(__name__))
                return False
            return json.loads(_stream.decode(Protocol.DECODER))

if __name__ == "__main__":
    d = {'a':1,'b':2}
    dd = Protocol.toStream(d)
    print(dd)
    ddd = Protocol.fromStream(dd)
    print(ddd)