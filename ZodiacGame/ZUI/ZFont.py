'''游戏内字体设置'''
from ZUI.ZColor import Color
import pygame
import pygame.freetype
import os

#字体


class ZFont():
    def __init__(self,_color=Color.white,_size=36,_path = './fonts/28DaysLater.ttf'):
        self.color = _color
        self.size = _size
        self.path=os.path.abspath(_path)
        self.object = None 

    def show(self,content,position,window,size=None):
        '''显示字体'''
        if not self.object:#第一次show需要单独预加载self.object（因为在pygame.init之前是不能加载字体的）
            self.object = pygame.freetype.Font(self.path)
        if size:
            font_size = size
        else:
            font_size = self.size
        self.object.render_to(window,position,content,fgcolor=self.color,size=font_size)

    def prompt(self):
        '''聊天框提示（理论上不应该继承在这里，应该写在ZGame，这里只是记录下想法）'''
        pass
