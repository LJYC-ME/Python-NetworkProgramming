from PyQt5.QtWidgets import *
from PyQt5.QtCore import *#QThread AND Signals Slots
import UI_ChatRoom#聊天室UI
from Client_Login import *#登录模块
from socket import *
from ChatRoom_DataStruct import *
from ChatRoom_Client_Receiver import *
import sys

ServerBook = {"local":("127.0.0.1",5122),"online":("服务器公网IP","服务端口号")}
ServerSwitch = "local"

class ChatRoom_Client(QWidget):
    #Instructor
    def __init__(self,clientAddr=None):
        super(ChatRoom_Client, self).__init__()
        # UI
        self.ui=UI_ChatRoom.Ui_Form()
        self.ui.setupUi(self)#以当前Widget来使用UI
        self.init_UI()#初始化UI配置
        # Datas
        self.ChatRoomServer = ServerBook[ServerSwitch]  # 对应服务端地址
        self.UID=None#用户的账号
        self.swichPriChat = False #是否开启私聊
        self.friends = None #私聊对象列表
        # Socket
        self.client = socket(AF_INET,SOCK_DGRAM)#IPv4 UDP
        self.client.setblocking(False)#不阻塞
        if clientAddr:#若需要显式绑定（暂不校验正确性）
            self.client.bind(clientAddr)
        # Threads
        self.receiver = None
        self.Thread_Receiver()#接受来自Server的消息（包括登录等操作）
        # Qt Connections
        self.ui.pushButton_SendMessage.clicked.connect(self.slot_PushButton_sendMes)
        self.ui.checkBox_PriChat.clicked.connect(self.slot_CheckBox_PriChat)
        # User Login
        self.login()
        # Start
        self.sockname = self.client.getsockname()
        self.show()

    # Methods
    def slot_CheckBox_PriChat(self):
        self.swichPriChat = self.ui.checkBox_PriChat.isChecked()

    def login(self):
        dialog_login = ChatRoom_Client_login(self)
        if dialog_login.exec_()==QDialog.Accepted:
            #print("Login OK")
            pass
        else:
            #print("Login Fail")
            sys.exit(-1)
    def init_UI(self):
        # 设置UI初始配置
        self.setWindowTitle("小小聊天室 Ver1.0 Designed By Frozen")
        self.window().setFixedSize(self.window().width(), self.window().height())
        self.window().setWindowOpacity(0.8)
        self.setWindowIcon(QIcon("./images/chatroom.ico"))
        # 居中
        screen = QDesktopWidget().screenGeometry()
        windowSize = self.window().geometry()
        centerLeft = (screen.width() - windowSize.width()) / 2
        centerTop = (screen.height() - windowSize.height()) / 2
        self.window().move(centerLeft, centerTop)
    def keyPressEvent(self, QKeyEvent):
        key = QKeyEvent.key()
        #print(key)
        if key == Qt.Key_Escape:
            app.quit()
        elif key == 16777220:#Qt.Key_Enter-1
            self.slot_PushButton_sendMes()
            pos = self.ui.textBrowser_Screen.textCursor().End
            self.ui.textBrowser_Screen.moveCursor(pos)

    def Thread_Receiver(self):
        self.receiver = ChatRoom_Client_Receiver(self.client, self.ChatRoomServer)
        self.receiver.signal_recvMes.connect(self.slot_TextBrowser_recvMes)
        self.receiver.start()  # 开启接受信息
    def CLI(self,mes):
        if mes[0]=='$':
            cmd=mes[1:]
            if cmd =='clear':
                self.ui.textBrowser_Screen.clear()
                return True#表示解析成功
        return False
    # Signals
    #signal_PushButton_sendMes = pyqtSignal(object)
    # Slots
    def slot_PushButton_sendMes(self):
        mes = self.ui.lineEdit_UserInput.text()
        self.ui.lineEdit_UserInput.clear()
        if mes != "":
            if not self.CLI(mes):#进入命令解析模式，如果不是命令则发送
                if self.swichPriChat:
                    self.friends = self.ui.lineEdit_PriChat.text()
                    print(self.friends)
                    mes = Message(mes,type=TypeMessage.PrivateChat.value,attach=self.friends)
                    self.ui.textBrowser_Screen.insertPlainText(
                        "{}--->{} ({})\n{}\n".format("我",self.friends.split(';'), mes.content["Time"], mes.content["Content"]))
                else:#公聊模式
                    mes = Message(mes)
                    self.ui.textBrowser_Screen.insertPlainText("{} ({})\n{}\n".format("我", mes.content["Time"], mes.content["Content"]))
                self.client.sendto(mes.wrap().encode("UTF-8"),self.ChatRoomServer)
                print("Send OK")

    def slot_TextBrowser_recvMes(self,mes):
        #print(mes)
        self.ui.textBrowser_Screen.insertPlainText(mes)#确保decode
        pos = self.ui.textBrowser_Screen.textCursor().End
        self.ui.textBrowser_Screen.moveCursor(pos)

if __name__=="__main__":
    app = QApplication(sys.argv)
    chat = ChatRoom_Client()
    app.exec_()
    mes_exit = Message(chat.UID,TypeMessage.Exit.value).wrap()
    chat.client.sendto(mes_exit.encode("UTF-8"),chat.ChatRoomServer)#告知退出
    sys.exit()