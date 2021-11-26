from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import UI_ChatRoomRegister #登陆界面UI
import sys
import time
from ChatRoom_DataStruct import *

class ChatRoom_Client_Register(QDialog):
    ''''用户注册'''
    #instructor
    def __init__(self,clientSocket):
        super(ChatRoom_Client_Register, self).__init__()
        # Client
        self.clientSocket = clientSocket
        # UI
        self.ui=UI_ChatRoomRegister.Ui_Form()
        self.ui.setupUi(self)
        self.init_UI()
        self.show()
        #Connect
        self.ui.pushButton_Register.clicked.connect(self.on_PushButton_Register)
    def init_UI(self):
        #组件初始化
        self.ui.label_FeedBack.clear()
        self.window().setFixedSize(self.window().width(), self.window().height())
        self.setWindowIcon(QIcon("./images/chatroom.ico"))
        # 居中
        screen = QDesktopWidget().screenGeometry()
        windowSize = self.window().geometry()
        centerLeft = (screen.width() - windowSize.width()) / 2
        centerTop = (screen.height() - windowSize.height()) / 2
        self.window().move(centerLeft, centerTop)
    def prompt(self,feedback,timewait=1):
        self.ui.label_FeedBack.setText(feedback)
        self.ui.label_FeedBack.repaint()
        time.sleep(timewait)
    def on_PushButton_Register(self):
        nickname=self.ui.lineEdit_UserNickName.text()
        uid = self.ui.lineEdit_UserID.text()
        password = self.ui.lineEdit_Password.text()
        if nickname is '' or uid is '' or password is '':
            #Local Validation
            self.prompt("请确保所有信息填写完整")
        else:
            #Online Validation
            self.clientSocket.receiver.signal_recvRes.connect(self.registering)
            mes = Message((nickname,uid,password),TypeMessage.Register.value)
            self.clientSocket.client.sendto(mes.wrap().encode("UTF-8"),self.clientSocket.ChatRoomServer)
    def registering(self,num):
        if int(num) is TypeMessage.OK.value:
            self.clientSocket.receiver.signal_recvRes.disconnect(self.registering)  # 断开信号
            self.accept()  # 注册成功
        else:
            self.prompt("注册失败")
            self.prompt = QMessageBox.about(self,'注册失败','该用户可能已经注册或您的注册信息有误')
            self.reject() # 注册失败

if __name__=="__main__":
    app = QApplication(sys.argv)
    chat = ChatRoom_Client_Register()
    chat.show()
    sys.exit(app.exec_())