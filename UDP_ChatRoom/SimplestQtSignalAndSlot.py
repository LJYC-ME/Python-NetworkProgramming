from PyQt5.QtCore import *

class MySignal(QObject):
    # 定义信号需要在__init__外，即类属性（可在类的所有实例之间共享的变量）
    sendmsg = pyqtSignal(object)  #姑且认为object代表任何对象
    #多参数型号例子：sendmsg = pyqtSignal(object,int,str,int)#4参数
    #比如pyqtSignal([int,str],[str])这类重载方式（关联上要显式signal[str].connect），可以看下方视频学习
    #https://www.bilibili.com/video/BV154411n79k?p=107
    printMes = pyqtSignal(str)
    def __init__(self,ab):
        super(MySignal, self).__init__()
        self.a=ab
        self.printMes.connect(self.prinT)
        self.printMes.emit("你好")#信号通过emit触发
    def prinT(self,mes):
        print("PrinT:"+mes)
    def run(self):
        self.sendmsg.emit(self.a+"Hello")#信号通过emit触发

class MySlot(QObject):
    def __init__(self,_prefix):
        super(MySlot, self).__init__()
        self.prefix=_prefix

    def get(self,meg):
        print("GET:"+self.prefix+meg)

if __name__=="__main__":
    sender=MySignal("ab")
    receiver=MySlot("Frozen:")
    sender.sendmsg.connect(receiver.get)

    sender.run()