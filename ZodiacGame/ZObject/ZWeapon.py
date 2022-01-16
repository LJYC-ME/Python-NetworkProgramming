import pygame
import numpy as np
from pygame.sprite import Sprite
import os
from ZGameSettings import GAME_SETTING

class Weapon(Sprite):
    def __init__(self,owner):
        self.image_bullet = pygame.image.load(os.path.abspath("./images/charactors/zidan.png"))
        self.attack = 1
        self.speed = 1
        self.owner = owner
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_speed = 10.0
    def shoot_bullets(self):
        bullet = Bullet(self)
        return bullet
class Bullet(Sprite):
    """一个对发射子弹管理的类"""

    def __init__(self,weapon):
        """在角色所处位置创建一个子弹对象"""
        super(Bullet,self).__init__()
        self.image = weapon.image_bullet#已经载入
        self.rect = pygame.Rect(0,0,weapon.bullet_width,weapon.bullet_height)
        self.rect.centerx=weapon.owner.realleft
        self.rect.centery=weapon.owner.realtop
        self.rect.top = weapon.owner.rect.top
        self.direction = np.array([float(0),float(0)])
        #子弹的发射方向（下左右上0123）
        #print(weapon.owner.attribution['direction'])
        if weapon.owner.attribution['direction'] == 0:
            self.direction[1] = 1.0
        elif weapon.owner.attribution['direction'] == 1:
            self.direction[0] = -1.0
        elif weapon.owner.attribution['direction'] == 2:
            self.direction[0] = 1.0
        elif weapon.owner.attribution['direction'] == 3:
            self.direction[1] = -1.0
        #self.x = float(self.rect.x)
        self.posion = np.array([float(self.rect.x),float(self.rect.y)])
        self.speed_factor = weapon.bullet_speed

    def update(self):
        """移动子弹"""
        #更新表示子弹的位置的小数值
        self.posion += self.direction*self.speed_factor
        #更新表示子弹rect的位置
        self.rect.x = self.posion[0]
        self.rect.y = self.posion[1]
        #self.image = self.image.subsurface(self.frame_rect) #生成子表面

    def obliviate(self,BIN):
        boundary = GAME_SETTING.screen_size #下面有个小运算可能会有效率损失，但是为了子弹的边缘发射，暂时这样设置
        if self.rect.x > boundary[0]+1 or self.rect.x < -1 or self.rect.y > boundary[1]+1 or self.rect.y < -1:
            BIN.put(self)