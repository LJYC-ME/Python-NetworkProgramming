'''游戏核心模块'''

import pygame
from queue import Queue
from pygame.sprite import Group
from ZGameSettings import *
from ZNet import ZClient
from ZObject.ZCreature import ZCreature
from ZUI.ZFont import ZFont
import os
import threading
import sys

class ZGame():
    '''提供访问全局变量的接口'''
    #游戏对象
    Player = None #玩家实例的访问
    Window = None #游戏窗口
    Map = None #游戏地图（暂时没多地图模式）
    #游戏字体   
    Font_default = ZFont() #默认字体
    Font_title = ZFont(_size = 100) #标题字体
    #以下是游戏的状态
    Running = False #游戏循环
    Online = False #联机模式
    #以下是对象池(如果可以通过dict改变对象，那使用dict)
    ME = None #玩家本身的对象（因为暂不确定是否可以在Group中访问）
    players = Group()
    self_bullets = Group()
    other_bullets = Group()
    #对象回收池
    BIN_players = Queue()
    BIN_self_bullets = Queue()
    BIN_other_bullets = Queue()
    #联机模式Socket
    Login = False #是否登录成功
    Client = None
    PlayerManager = {} #玩家Name:player实体的映射

    def __init__(self):
        pygame.init()
        #global GameWindow
        ZGame.Window = pygame.display.set_mode(GAME_SETTING.screen_size)#屏幕尺寸
        pygame.display.set_caption(GAME_SETTING.game_caption)#游戏标题
        self.clock = pygame.time.Clock()#控制FPS
        pygame.display.set_icon(pygame.image.load(GAME_SETTING.ui_icon))#ICON

    def start(self):
        '''启动游戏'''
        GAME.Running = True
        if GAME.ME:#载入玩家
            GAME.players.add(GAME.ME)
        if GAME_SETTING.screen_background:#载入地图
            GAME.Map = pygame.image.load(GAME_SETTING.screen_background)
        if GAME.Online:
            #GAME.Client = ZClient.Client('127.0.0.1',19219)#创建Client（Server单独开启）
            GAME.Client = ZClient.Client('47.97.202.110',19219)#创建Client（Server单独开启）
            #thread_client = multiprocessing.Process(target=GAME.Client.start)
            thread_client = threading.Thread(target=GAME.Client.start)
            thread_client.setDaemon(True)
            thread_client.start()
            while not GAME.Login:
                self.prompt_authors()
                self.prompt('Hello Please Sign In',font=GAME.Font_title)
        sys.exit(self.GameLoop())#进入游戏循环
    
    def GameLoop(self):
        '''游戏主循环'''
        while GAME.Running:
            #FPS
            self.clock.tick(GAME_SETTING.MAX_FPS)
            #玩家控制
            self.control()
            #状态迁移
            self.stateUpdate()
            #垃圾回收
            self.garbageCollection()
            #绘制事件
            self.render()

    def __del__(self):
        if self.Online:
            self.Client.exit()

    def addCreature(self,attribution,group):
        '''根据属性创建并向一个指定的Group添加一个实例'''
        summon = ZCreature(attribution)
        group.add(summon)
        return summon

    def prompt(self,content,position=GAME_SETTING.area_prompt,font=None):
        '''游戏内的文字提示（默认在左下角附近位置）'''
        if not font:#采用默认字体
            shower = GAME.Font_default
        else:
            shower = font
        shower.show(content,position,GAME.Window)
        pygame.display.update()

    def prompt_authors(self):
        '''展示游戏作者信息'''
        GAME.Font_title.show('Authors',position=(100,100),window=GAME.Window)
        GAME.Font_title.show('Frozen',position=(100,210),window=GAME.Window,size=50)
        GAME.Font_title.show('IzumiSagiri',position=(100,270),window=GAME.Window,size=50)
        GAME.Font_title.show('Jerry',position=(100,330),window=GAME.Window,size=50)
        GAME.Font_title.show('TroubleMaker',position=(100,390),window=GAME.Window,size=50)

    def stateUpdate(self):
        '''对象池对象状态迁移'''
        #更新状态
        GAME.players.update()
        GAME.self_bullets.update()
        for each in GAME.self_bullets:
            each.obliviate(GAME.BIN_self_bullets)
        GAME.other_bullets.update()
        #碰撞检测
        res = pygame.sprite.groupcollide(GAME.self_bullets,GAME.players,False,False,collided=None) #自己的子弹与玩家的碰撞
        if res:
            for myBullet,list_player in res.items():
                for player in list_player:
                    if player != GAME.ME:#这里可以做一个bullet times-1（后期可以做子弹穿透、弹射等效果）
                        #print("命中敌人")#因为是自己的子弹所以向所有人广播伤害信息（who hp-$damage）
                        GAME.BIN_self_bullets.put(myBullet)
                        #print("命中自己")
        res = pygame.sprite.groupcollide(GAME.other_bullets,GAME.players,False,False,collided=None) #自己的子弹与玩家的碰撞
        if res:
            for myBullet,list_player in res.items():
                for player in list_player:
                    #print("命中敌人")#因为是自己的子弹所以向所有人广播伤害信息（who hp-$damage）
                    GAME.BIN_self_bullets.put(myBullet)
                    #print("命中自己")
        if GAME.Online: #联机态需要同步玩家状态
            GAME.Client.syn()

    def garbageCollection(self):
        '''对象池垃圾回收'''
        while not GAME.BIN_players.empty():
            GAME.players.remove(GAME.BIN_players.get())
        while not GAME.BIN_self_bullets.empty():
            GAME.self_bullets.remove(GAME.BIN_self_bullets.get())
        while not GAME.BIN_other_bullets.empty():
            GAME.other_bullets.remove(GAME.BIN_other_bullets.get())

    def render(self):
        '''渲染事件'''
        if GAME.Map == None:#地图绘制
            GAME.Window.fill(GAME_SETTING.screen_backgroundColor)
        else:
            GAME.Window.blit(GAME.Map,(0,0))
        GAME.players.draw(ZGame.Window)
        GAME.self_bullets.draw(ZGame.Window)
        GAME.other_bullets.draw(ZGame.Window)
        #Flush
        pygame.display.update()

    def control(self):
        '''玩家操控事件'''
        if GAME.ME != None:
            GAME.ME.control()

GAME = ZGame()#Singleton
