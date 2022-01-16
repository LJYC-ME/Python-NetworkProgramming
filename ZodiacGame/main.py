from ZGame import GAME
from ZObject.ZCreature import *

if __name__ == "__main__":
    player = Player(ATTR_Brave)
    GAME.ME = player #绑定玩家操作对象
    GAME.Online =  True#联机模式启动
    GAME.addCreature(ATTR_Brave,GAME.players)
    GAME.start() 