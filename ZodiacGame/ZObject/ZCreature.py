from pygame.rect import Rect
import pygame
from pygame.sprite import Sprite
#from ZGameSettings import *
import ZObject.ZControl as ZControl
from ZObject.ZAttribution import *
import ZObject.ZWeapon as ZWeapon
import ZGame

class ZCreature(Sprite):
    '''默认情况下一个游戏最基本生物单位应具备的属性和方法，建议以此作为基类通过继承派生新的生物'''
    cnt_Creatures = 0
    def __init__(self,_attribution):
        """初始化对象"""
        super().__init__()
        ZCreature.cnt_Creatures += 1
        self.ID = ZCreature.cnt_Creatures
        self.attribution = _attribution.visit().copy()

        #如下为sprite属性
        self.mast_image = None
        self.last_time =0
        self.last_frame = 0
        self.realleft = None
        self.realright = None
        self.realtop = None
        self.realbottom = None
        #对象图形以及其外接矩形
        self.changeDir = None
        self.mast_image = pygame.image.load(os.path.abspath(self.attribution['image_path']))
        self.image = pygame.image.load(os.path.abspath(self.attribution['image_path']))
        self.rect = self.mast_image.get_rect()
        self.rect = Rect(0,0,64,64)
        #对象矩形的二维坐标
        self.rect.centerx = self.attribution['centerx']
        self.rect.centery = self.attribution['centery']
        #对象的center坐标属性
        self.centerx = float(self.attribution['centerx'])
        self.centery = float(self.attribution['centery'])
        #精灵图的行列数
        #移动标志如下:
        #如：self.attribution['moving_right'] = False
        #初始方向
        #如：self.attribution['direction'] = np.array([0,-1]) 二维向量向上
        self.load()#加载精灵图
    
    def getAttr(self):
        '''返回对象的属性拷贝'''
        return self.attribution.copy()

    def move(self,x,y):
        self.attribution['centerx'] = x
        self.attribution['centery'] = y

    def updateAttr(self,attr):
        '''用字典更新属性'''
        self.attribution.update(attr)
        #print(self.attribution)

    def load(self):
        """加载精灵图，初始化帧块各类数据"""
        self.rect = self.mast_image.get_rect() #获取精灵图矩形参数
        self.frame_rect = self.rect.copy() #声明frame_rect框架参数
        self.rect.x,self.rect.y = self.centerx,self.centery  #动画初始绘制坐标(接口)
        self.frame_rect.width = self.frame_rect.width // self.attribution['Columns']
        self.frame_rect.height = self.frame_rect.height // self.attribution['Rows']
        self.attribution['frame'] = 0
        self.last_frame = (self.rect.width // self.frame_rect.width) * (self.rect.height // self.frame_rect.height) - 1
        self.attribution['old_frame'] = 1
        self.last_time = 0

    def update(self):
        self.image = self.mast_image.subsurface(self.frame_rect) #生成子表面
        if self.action():#如果对象有移动
            if self.changeDir:
                self.changeDir = False
                self.attribution['first_frame'] = self.attribution['direction'] * self.attribution['Columns']
                self.attribution['frame'] = self.attribution['first_frame']
                self.last_frame = self.attribution['first_frame'] + self.attribution['Columns'] - 1
        
        #任意对象
        self.current_time = pygame.time.get_ticks()
        rate = 180
        if self.current_time >= self.last_time + rate:
            self.attribution['frame'] += 1
            if self.attribution['frame'] > self.last_frame:
                self.attribution['frame'] = self.attribution['first_frame']
            self.last_time = self.current_time

        if self.attribution['old_frame'] != self.attribution['frame']:
            self.frame_rect.x = (self.attribution['frame'] % self.attribution['Columns']) * self.frame_rect.width
            self.frame_rect.y = (self.attribution['frame'] // self.attribution['Columns']) * self.frame_rect.height
            self.attribution['old_frame'] = self.attribution['frame']  
        
    def __del__(self):
        pass

    def level_up(self,num = 1):
        """对象升级"""
        self.attribution["LV"]+=num

    def action(self):
        """对象的行为"""
        #移动
        isMoved = False#本次是否移动
        window_size = GAME_SETTING.screen_size
        if self.attribution['moving_right'] and (self.rect.right - (self.attribution['Columns']-1) *self.frame_rect.width) < window_size[0]:
            self.rect.x += self.attribution["speed"]
            isMoved = True
            
        if self.attribution['moving_left'] and self.rect.left > 0:
            self.rect.x -= self.attribution["speed"]
            isMoved = True
            
        if self.attribution['moving_up'] and self.rect.top > 0:
            self.rect.y -= self.attribution["speed"]
            isMoved = True

        if self.attribution['moving_down'] and (self.rect.bottom - (self.attribution['Rows'] -1) * self.frame_rect.height) < window_size[1]:
            self.rect.y += self.attribution["speed"]
            isMoved = True

        oldDir = self.attribution['direction']
        if isMoved:#如果有行动才更新朝向
            if self.attribution['moving_up'] :self.attribution['direction'] = 3
            elif self.attribution['moving_down'] :self.attribution['direction'] = 0
            if self.attribution['moving_left'] :self.attribution['direction'] = 1
            elif self.attribution['moving_right'] :self.attribution['direction'] = 2 
        if oldDir != self.attribution['direction']:self.changeDir = True#告知修改了走向
        self.realright=self.rect.right - (self.attribution['Columns']-1) *self.frame_rect.width
        self.realbottom=self.rect.bottom - (self.attribution['Rows'] -1) * self.frame_rect.height
        self.realleft=self.rect.left
        self.realtop=self.rect.top
        return isMoved#返回是否移动

class Player(ZCreature):
    def __init__(self,_attribution):
        super().__init__(_attribution)
        self.weapon = ZWeapon.Weapon(self)

    def attack(self,trigger):
        if trigger.type == pygame.KEYDOWN:
            if trigger.key == pygame.K_SPACE:
                ZGame.GAME.self_bullets.add(self.weapon.shoot_bullets())

    def control(self):
        res = None
        for trigger in pygame.event.get():
            ZControl.check_WSAD_events(trigger,self)
            self.attack(trigger)
            res = ZControl.check_Exit_events(trigger)
        return res