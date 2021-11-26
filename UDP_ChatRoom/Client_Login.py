from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from socket import *
import UI_ChatRoomLogin #登陆界面UI
import sys
import time
from ChatRoom_DataStruct import *
from ChatRoom_Client_Receiver import *
from Client_Register import *

class ChatRoom_Client_login(QDialog):
    ''''用户登录'''
    #instructor
    def __init__(self,clientSocket):#需要将客户端拿来
        super(ChatRoom_Client_login, self).__init__()
        #Status
        #self.status_login = False
        # Receiver Thread
        self.clientSocket = clientSocket
        # UI
        self.ui=UI_ChatRoomLogin.Ui_Form()
        self.ui.setupUi(self)
        self.init_UI()
        self.show()
        #Connect
        self.ui.pushButton_Login.clicked.connect(self.on_PushButton_Login)
        self.ui.pushButton_Register.clicked.connect(self.on_PushButton_Register)
    def init_UI(self):
        #组件初始化
        self.ui.label_FeedBack.clear()
        self.window().setFixedSize(self.window().width(), self.window().height())
        self.setWindowIcon(QIcon("./images/chatroom.ico"))
        self.ui.lineEdit_UserID.setPlaceholderText("Your User ID")
        self.ui.lineEdit_Password.setPlaceholderText("Your Password")
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
    def on_PushButton_Login(self):
        uid = self.ui.lineEdit_UserID.text()
        password = self.ui.lineEdit_Password.text()
        #Local Validation
        if uid is "" or password is "":
            self.prompt("账号或用户名为空",0)
            #self.reject()
        else:
            #Online Validation
            self.clientSocket.receiver.signal_recvRes.connect(self.logining)
            mes = Message((uid,password),TypeMessage.Login.value)
            self.clientSocket.client.sendto(mes.wrap().encode("UTF-8"), self.clientSocket.ChatRoomServer)
            self.prompt("登录中",0.5)
    def on_PushButton_Register(self):
            dialog_register = ChatRoom_Client_Register(self.clientSocket)
            if dialog_register.exec_() == QDialog.Accepted:
                self.prompt("注册成功",0)
            else:
                self.prompt("注册失败", 0)
    def logining(self,num):
        if int(num) is TypeMessage.OK.value:
            self.clientSocket.UID = self.ui.lineEdit_UserID.text()
            self.prompt("登陆成功",0.5)
            self.clientSocket.receiver.signal_recvRes.disconnect(self.logining)  # 断开信号
            self.accept()  # 登录成功
        else:
            self.prompt("登录失败", 0.5)

if __name__=="__main__":
    app = QApplication(sys.argv)
    chat = ChatRoom_Client_login(123)
    chat.show()
    sys.exit(app.exec_())