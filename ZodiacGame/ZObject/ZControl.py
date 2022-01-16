"""author LY"""
from os import environ
import sys
import pygame
from pygame.event import event_name
import ZGame

def check_WSAD_events(event,creature):
    """响应按键上下左右模块"""
    #配合for event in pygame.event.get(): 食用
    #如：if event.type == pygame.KEYDOWN:
    #       check_WSAD_events(event,ai_settings)
    if event.type == pygame.KEYDOWN:
        #print(event.key)
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        #向右移动
            creature.attribution['moving_right'] = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        # 向左移动
            creature.attribution['moving_left']= True
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
        # 向上移动
            creature.attribution['moving_up']= True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        # 向下移动
            creature.attribution['moving_down']= True  
    #elif event.type == pygame.QUIT:
     #   ZGame.Running = False
        
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            creature.attribution['moving_right'] = False
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            creature.attribution['moving_left'] = False
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            creature.attribution['moving_up'] = False
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            creature.attribution['moving_down'] = False

def check_Exit_events(event):
    '''退出事件'''
    if event.type == pygame.QUIT:
        ZGame.GAME.Running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            ZGame.GAME.Running = False