'''各种实用性组件'''
import time
import sys

def processBar(totalNum,sign='='):
    '''[生成器] 传入总值并通过使用send方法传入当前数值生成进度条'''
    current_process = 0 #当前进度
    last_process = 0 #上一次调用进度
    while True:
        curNum = yield current_process
        current_process = int(curNum / totalNum * 100) 
        if current_process > last_process:
            print("\r|{}[{}%]|".format( (str(sign*round(current_process/2))).ljust(50) , current_process),flush=True,end='')
            last_process = current_process

if __name__ == "__main__":
    prcBar = processBar(100)
    prcBar.__next__()
    for i in range(101):
        time.sleep(0.05)
        prcBar.send(i)
