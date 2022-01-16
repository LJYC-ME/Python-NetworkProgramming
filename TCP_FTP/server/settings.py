'''Server的配置文件'''
import os
SERVER_ROOT = os.path.dirname(os.path.abspath(__file__))#server的根目录

HOST_IP = "127.0.0.1"
HOST_PORT = 9968

MAX_LISTENING = 5 #最大挂起连接数
PORT_REUSE = True #是否端口复用
METRIC_SIZE_FILE = 4194304 #大文件阈值4MB

if __name__ == "__main__":
    print(os.path.join(SERVER_ROOT,'123'))#SERVER_ROOT)