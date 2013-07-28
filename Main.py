# -*- coding: utf-8 -*-
import pygame
import random
import threading
import sys
import copy

from pygame.locals import *

###############################################################################
# 定义一些宏观变量
ScreenSize=(740,560) #画面像素
FPS=30 #刷新率
CellSize=10 #每个格子的长宽（正方形）
NumL=50 #每行多少个格子
NumW=50 #没列多少个格子
RunState=1 #控制进程是否退出，1为运行，0为退出
ClanInfo=[] #用来存放部落信息的list
ClanInfoStartx=ScreenSize[0] #定义ClanInfo开始滚动的其实位置x
ClanInfoy=20 #定义ClanInfo开始滚动的其实位置y
WorldInfo=[] #用来存放世界信息的list
WorldInfox=520 #WorldInfo开始坐标x
WorldInfoStarty=550 #WorldInfo开始坐标y
##############################################################################

##############################################################################
# 一个用来管理 Pygame 事件的函数
def HandleEvents():
    for event in pygame.event.get():
        # 点击窗口上的“关闭”或是按"esc"退出
        if event.type == QUIT or (event.type==KEYDOWN and event.key==K_ESCAPE):
            RunState=0
            pygame.quit()
            sys.exit()
##############################################################################

##############################################################################
# 一个函数，用来绘制屏幕
def DrawScreen():
    #屏幕填充为白色
    Surface.fill((255,255,255))
    #部落信息填充为灰色
    pygame.draw.rect(Surface,(128, 128, 128),Rect(0,10,ScreenSize[0],35))
    #实时状况填充为灰色
    pygame.draw.rect(Surface,(128,128,128),Rect(515,50,220,500))
    #绘制方格
    for y in range(50,551,10):
        pygame.draw.line(Surface,(0,0,0),(10,y),(510,y))
    for x in range(10,511,10):
        pygame.draw.line(Surface,(0,0,0),(x,50),(x,550))
##############################################################################


##############################################################################
# 主函数
def Main():
    global Surface, font

    #pygame的初始化
    pygame.init()
    FPSClock=pygame.time.Clock()
    Surface=pygame.display.set_mode(ScreenSize,0,32)
    font=pygame.font.SysFont("menlo",20)
    fontWide=7 #定义字体宽度
    fontHeight=font.get_linesize() #定义字体高度
    pygame.display.set_caption('The War of Clans')

    #ClanInfo第一次显示头一个字的位置
    ClanInfofirstx=ClanInfoStartx
    #ClanInfo第一次要显示的字
    ClanInfoText=copy.deepcopy(ClanInfo)

    while True:
        #执行事件
        HandleEvents()
        #刷新屏幕
        DrawScreen()
        #######################################################
        #刷新ClanInfo
        if ClanInfoText==[]:
            #ClanInfo第一次显示头一个字的位置
            ClanInfofirstx=ClanInfoStartx
            #ClanInfo第一次要显示的字
            ClanInfoText=copy.deepcopy(ClanInfo)
        else:
            ClanInfox=ClanInfofirstx
            for i in range(len(ClanInfoText)):
                TextToDisplay=font.render(ClanInfoText[i],True,(0,0,0))
                Surface.blit(TextToDisplay,(ClanInfox,ClanInfoy))
                if i==len(ClanInfoText)-1:
                    ClanInfox=ClanInfox+fontWide*len(ClanInfoText[i])
                else:
                    ClanInfox=ClanInfox+fontWide*len(ClanInfoText[i])+10
            if ClanInfox<0:
                ClanInfofirstx=ClanInfoStartx
                ClanInfoText=copy.deepcopy(ClanInfo)
            else:
                ClanInfofirstx-=3
        ######################################################
        #刷新WorldInfo的信息
        #WorldInfo显示头一个字的位置
        WorldInfoy=WorldInfoStarty-fontHeight
        #WorldInfo要显示的字
        WorldInfoText=WorldInfo
        WorldInfoText=WorldInfoText[-(500-fontHeight)/fontHeight:]
        for text in reversed(WorldInfoText):
            Surface.blit(font.render(text,True,(0,0,0)),(WorldInfox,WorldInfoy))
            WorldInfoy-=fontHeight
        #######################################################

        pygame.display.update()
        FPSClock.tick(FPS)
####################################################################################

if __name__=="__main__":
    Main()
