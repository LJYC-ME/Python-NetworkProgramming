'''处理文件的相关方法'''
import chardet
def create_testFile(filePath,size):
    '''创建一个特定大小的测试文件'''
    with open(filePath,'w',encoding="UTF-8") as file:
        file.write("x"*size)

def get_encoding(filePath):
    '''给出文件路径获取文件的编码方式'''
    tmp = None
    with open(filePath,'rb') as file:
        tmp = chardet.detect(file.read(5))
    return tmp['encoding']

if __name__ == "__main__":
    create_testFile(r'C:\Users\26692\Desktop\樱绮纪行2021[↓]\课程\网络编程\实验A3-FTP\server\home\Frozen/10MB.txt',10*1024*1024)