'''游戏内部生物的属性'''

import numpy as np
from ZGameSettings import *
from ZGame import *
import os

class ZAttribution():
    def __init__(self,generDic=None) :
        self.attr = dict()
        if generDic:
            self.attr.update(generDic)
        else:
            self.attr["Name"] = ""
            self.attr["LV"] = 1
            self.attr["image_path"] = './images/charactors/勇者64x64.png'
            #print(self.attr["image_path"])
            #动作属性 
            #self.attr['direction'] = np.array([0,-1])#朝向（需要更新）
            self.attr['direction'] = 0
            #移动方向   
            self.attr['moving_right'] = False
            self.attr['moving_up'] = False
            self.attr['moving_left'] = False
            self.attr['moving_down'] = False
            #精灵图数据
            self.attr['frame'] = 0
            self.attr['first_frame'] = 0
            self.attr['old_frame'] = -1
            self.attr['frame_width'] = 1
            self.attr['frame_height'] = 1
            self.attr['Columns'] = 1
            self.attr['Rows'] = 1
            self.attr["Rows"] = 4
            self.attr["Columns"] = 3
            #初始二维坐标
            #self.screen_rect = ZGame.GameWindow.get_rect()
            self.attr['centerx'] = GAME_SETTING.screen_width/2.0#self.screen_rect.centerx
            self.attr['centery'] = GAME_SETTING.screen_height/2.0#self.screen_rect.centery
            self.attr['rect_x'] = None
            self.attr['rect_y'] = None
            #速度
            self.attr["speed"] = 5.0
    
    def visit(self):
        return self.attr

class Attr_Brave(ZAttribution):
    '''勇者的默认属性'''
    def __init__(self, generDic=None):
        super().__init__(generDic=generDic)

ATTR_Normal = ZAttribution()
ATTR_Brave = ZAttribution()#暂时不用Attr_Brave