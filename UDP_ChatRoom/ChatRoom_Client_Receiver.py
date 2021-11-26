from PyQt5.QtCore import *#QThread AND Signals Slots
from ChatRoom_DataStruct import *
import sys

class ChatRoom_Client_Receiver(QThread):
    # Signals
    signal_recvMes = pyqtSignal(str)#收到普通消息
    signal_recvRes = pyqtSignal(int)#收到服务端的回复，将状态码发送
    signal_recvErr= pyqtSignal(int)  # 收到服务端的报错，将错误码发送

    def __init__(self, ClientSocket, serverAddr):
        super(ChatRoom_Client_Receiver,self).__init__()
        self.client = ClientSocket
        self.client.connect(serverAddr) #Client必须建立连接，否则无法接受

    def run(self):
        while True:
            try:
                datagram, sender = self.client.recvfrom(2048)
                if datagram:  # 如果消息不为空
                    mes = json.loads(datagram.decode('UTF-8'))#将json字符串转换为字典
                    #print(mes)
                    if TypeMessage.isMessage(mes["Type"]):#Message
                        self.signal_recvMes.emit(mes["Content"] + "\n")
                    elif TypeMessage.isResponse(mes["Type"]):#Response
                        self.signal_recvRes.emit(int(mes["Content"]))
                    elif TypeMessage.isError(mes["Type"]):#Error
                        self.signal_recvErr.emit(int(mes["Content"]))
            except BlockingIOError:
                pass