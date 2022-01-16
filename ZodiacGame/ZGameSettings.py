"""存储游戏基本设置（游戏过程中不应该轻易变更的）"""
import os

class ZGameSettings():
    #游戏基本信息
    game_caption = "ZodiacGame"
    MAX_FPS = 60
    #UI
    ui_icon = os.path.abspath("./images/icon/Zodiac.png")
    #屏幕设置
    screen_zoom = 0.8
    screen_width = 1920#1680
    screen_height = 1080#960
    screen_size=(screen_width * screen_zoom,screen_height * screen_zoom)#建议通过该属性控制屏幕尺寸
    screen_backgroundColor = (255,255,255) #默认背景颜色
    screen_background = os.path.abspath('./images\maps/map_test/map_test.png')#理论上需要一个专门载入地图文件的模块
    #屏幕特殊区域划分
    area_prompt = (100,screen_height*(2.0/3.0)) #文字提示区域(宽也可以用screen_width/20.0)
    
    @staticmethod
    def update_screen_size(self):
        '''根据缩放比例更新当前屏幕尺寸'''
        ZGameSettings.screen_size=(ZGameSettings.screen_width * ZGameSettings.screen_zoom,ZGameSettings.screen_height * ZGameSettings.screen_zoom)

GAME_SETTING = ZGameSettings()#Singleton
