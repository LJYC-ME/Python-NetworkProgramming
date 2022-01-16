'''C/S间通信协议'''
import json
from json import encoder

suffix = '/eNd' #封帧
coder = "UTF-8" #编解码规则

STATE={
    100:'OK / Log request',
    101:'ERROR / Log request',
    200:'Get OK',
    201:'Get ERROR',
    202:'Get: Large File Start/Doing',#大文件传输协议——开始（C）/传输中（S）
    203:'Get: Large File Refuse/Done',#大文件传输协议——拒绝（C）/传输结束（S）
    999:'Exit request',
    1:'Normal Request',
    2:'Request ERROR',
}

def FTPMes(mes,state=1,**addition):
    '''构造一个经过编码（默认UTF-8）格式化的json数据包'''
    if state in STATE.keys():
        data = {}
        data['state']=state
        data['message']=mes
        if addition:
            data.update(addition)#其他功能的额外信息
    else:
        print("ERROR: state not exist in protocol.py!")
    return (json.dumps(data)+suffix).encode(coder)

def FTPMes_NoSuffix(mes,state=1,**addition):
    '''构造一个经过编码（默认UTF-8）格式化的json数据包，不封帧'''
    if state in STATE.keys():
        data = {}
        data['state']=state
        data['message']=mes
        if addition:
            data.update(addition)#其他功能的额外信息
    else:
        print("ERROR: state not exist in protocol.py!")
    return (json.dumps(data)).encode(coder)
