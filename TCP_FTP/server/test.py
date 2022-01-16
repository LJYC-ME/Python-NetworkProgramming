from ctypes import sizeof
import os
import  users
import protocol
import json

class test:
    def __init__(self) -> None:
        if hasattr(self,'say'):
            getattr(self,'say')()
        pass

    def say(self):
        print("hi")

def abc(a,b=1,**c):
    print(a)
    print(b)
    print(c)

def said(a,*para):
    if not para:
        print("??")
    print(a)
    for p in para:
        print(p)

import chardet
def get_encoding(file):
    tmp = chardet.detect(file.read(2))
    return tmp['encoding']
import time
if __name__ == "__main__":
    st = '*'
    for i in range(10):
        print(st,end='',flush=True)
        time.sleep(0.3)

    a = "a b"
    di = {'1':123,'2':333}
    di = json.dumps(di).encode("UTF-8")
    print(di.decode("ascii"))
    a = json.loads(di)
    print(a)
    b= input()
    print(a)
    print(a.split(' ')[1])
    with open(r'C:\Users\26692\Desktop\樱绮纪行2021[↓]\课程\网络编程\实验A3-FTP\server\home\Frozen\主要函数.docx','rb') as f:
        print(get_encoding(f))
    path = os.path.abspath(os.path.curdir)+'/server'
    print(path)
    for file in os.listdir(path):
        
        if os.path.isfile(os.path.join(path,file)):
            print(file.ljust(30),end='')
            siz = os.path.getsize(os.path.join(path,file))
            print(str(siz)+' KB')
