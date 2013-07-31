# -*- coding: utf-8 -*-
import pygame
import random
import threading
import sys
import copy

from pygame.locals import *

###############################################################################
# 定义一些宏观变量
EnglishWordS="abcdefghijklmnopqrstuvwxyz"
EnglishWordL="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ScreenSize=(740,560) #画面像素
ScreenBackgroundColor=(255,255,255) #大背景为白色
FontBackgroundColor=(255,255,255) #信息WorldInfo and ClanInfo的背景为灰色
SmallGap=5 #屏幕规划，模块之间的间隔
BigGap=10 #屏幕规划，周边空格
FPS=30 #刷新率
RunState=1 #控制进程是否退出，1为运行，0为退出
Pause=0 #是否暂停
ClanInfo=[] #用来存放部落信息的list
ClanInfoLock=threading.Lock()
ClanInfoStartx=ScreenSize[0] #定义ClanInfo开始滚动的其实位置x
ClanInfoy=20 #定义ClanInfo开始滚动的其实位置y
ClanInfoHeight=35 #定义ClanInfo的高度
ClanInfoPosition=Rect(0,BigGap,ScreenSize[0],ClanInfoHeight) #ClanInfo所占用的矩形
GridPosition=[BigGap,BigGap+ClanInfoHeight+BigGap,BigGap+500+SmallGap,ScreenSize[1]] #Grid左上角(0,0)和右下角所在位置的 list 为后面画线画方格做准备
GridLineColor=(0,0,0) #Grid线为白色
WorldInfo=[] #用来存放世界信息的list
WorldInfoLock=threading.Lock()
WorldInfox=520 #WorldInfo开始坐标x
WorldInfoStarty=550 #WorldInfo开始坐标y
WorldInfoWide=220 #定义WorldInfo的宽度
WorldInfoPosition=Rect(GridPosition[2]+SmallGap,BigGap+ClanInfoHeight+BigGap\
    ,WorldInfoWide,GridPosition[3]-GridPosition[1]) #WorldInfo所占用的矩形
CellSize=10 #每个格子的长宽（正方形）
NumL=int((GridPosition[2]-GridPosition[0])/CellSize) #每行多少个格子
NumW=int((GridPosition[3]-GridPosition[1])/CellSize) #每列多少个格子
ColorExist=[] #存放已经存在的Color
ColorExistLock=threading.Lock() #ColorExist的锁
#
ClanToGenerate=[] #存放要产生的新部落的位置
ClanToGenerateLock=threading.Lock() #ClanToGenerate的锁
MemberToQuit=[] #存放因新部落产生而需要剔除出MemberList的成员
MemberToQuitLock=threading.Lock() #管理MemberToQuit的锁
#
#产生map
Grid=[]
for n in range(NumW+2):
    Grid.append([None]*(NumL+2))
Grid[0]=['W']*(NumL+2)
Grid[NumW+2-1]=['W']*(NumL+2)
for n in range(NumW+2):
    Grid[n][0]='W'
    Grid[n][NumL+2-1]='W'
GridLock=threading.Lock() #map的锁
#周边检查坐标变化
AddX=[-1,0,1,1,1,0,-1,-1]
AddY=[1,1,1,0,-1,-1,-1,0]
##############################################################################

##############################################################################
#部落 类
class Clan(threading.Thread):
    def __init__(self,name=None,Position=None,Color=None,DeadAge=None,Speed=None):
        threading.Thread.__init__(self)
        #初始化进程名字
        if name==None:
            self.name=EnglishWordL[random.randint(0,25)]
            namelength=random.randint(2,5)
            for n in range(namelength):
                self.name=self.name+EnglishWordS[random.randint(0,25)]
        else:
            self.name=name
        #初始化速度
        if Speed==None:
            Speed=random.randint(1,3)
        if Speed==1:
            self.Speed=30/3
        elif Speed==2:
            self.Speed=30/4
        else:
            self.Speed=30/5
        #初始化部落成员名单（存放所有人的位置）
        self.MemberList=[]
        #初始化部落的DeadAge
        if DeadAge==None:
            self.DeadAge=random.randint(1000,2000)
            if random.random<=0.1:
                self.DeadAge=random.randint(6000,10000)
        else:
            self.DeadAge=DeadAge
        #初始化部落的颜色
        if Color==None:
            self.Color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
            #验证Color是否已经存在
            ColorHasExist=1
            while ColorHasExist:
                ColorExistLock.acquire()
                try:
                    ColorExist.index(self.Color)
                except:
                    ColorHasExist=0
                    ColorExist.append(self.Color)
                    ColorExistLock.release()
                else:
                    ColorHasExist=1
                    ColorExistLock.release()
                    self.Color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        else:
            self.Color=Color
        #初始化部落位置
        if Position==None:
            #产生20个部落成员[color=self.color,state=0,year=random,sex=random,child=0]
            for n in range(20):
                Position=[random.randint(0,NumL-1),random.randint(0,NumW-1)]
                PositionHasExist=1
                Turn=0
                while PositionHasExist:
                    Turn+=1
                    GridLock.acquire()
                    if Grid[Position[1]+1][Position[0]+1]==None:
                        PositionHasExist=0
                        if random.random()<0.5:
                            Member=[self.Color,0,random.randint(0,self.DeadAge),1,0]#男
                        else:
                            Member=[self.Color,0,random.randint(0,self.DeadAge),0,0]#女
                        self.GetPosition(None,Position,Member)
                        GridLock.release()
                    else:
                        Position=[random.randint(0,NumL-1),random.randint(0,NumW-1)]
                        PositionHasExist=1
                        GridLock.release()
                    if Turn>NumW*NumL:
                        PositionHasExist=0
        else:
            for NewPosition in Position:
                if random.random()<0.5:
                    Member=[self.Color,0,random.randint(0,self.DeadAge),1,0]#男
                else:
                    Member=[self.Color,0,random.randint(0,self.DeadAge),0,0]#女
                GridLock.acquire()
                self.GetPosition(None,NewPosition,Member)
                GridLock.release()
        #生成ClanInfo
        self.RefreshClanInfo(1)
        #生成WorldInfo
        self.AddWorldInfo("Clan "+self.name+" is established!")

    #线程运行函数
    def run(self):
        while 1:
            if RunState==0:
                return
            if Pause==0:
                #成员退出
                self.QuitMember()
                #检查Clan是否存活
                self.ClanExist()
                #刷新ClanInfo
                self.RefreshClanInfo(0)
                #通过逐一检查Memberlist来控制部落中每一个人
                for PersonSite in self.MemberList:
                    GridLock.acquire()
                    Person=Grid[PersonSite[1]+1][PersonSite[0]+1]
                    GridLock.release()
                    try:
                        PersonState=Person[1]
                    except:
                        print PersonSite
                        global Pause
                        Pause=1
                    PersonAge=Person[2]
                    PersonSex=Person[3]
                    PersonChilde=Person[4]
                    #根据PersonState判断行动指标
                    GridLock.acquire()
                    Friend=[]
                    Foe=[]
                    NoPerson=[]
                    for n in range(len(AddX)):
                        Other=Grid[PersonSite[1]+1+AddY[n]][PersonSite[0]+1+AddX[n]]
                        if Other==None:
                            NoPerson.append([PersonSite[0]+AddX[n],PersonSite[1]+AddY[n]])
                        elif Other=="W":
                            pass
                        elif Other[0]==self.Color:
                            Friend.append([PersonSite[0]+AddX[n],PersonSite[1]+AddY[n]])
                        else:
                            Foe.append([PersonSite[0]+AddX[n],PersonSite[1]+AddY[n]])
                    if PersonState==0:#和平状态
                        if Friend==[] and Foe==[]:#和平状态，周围空无一人，就走动
                            PersonNewSite=random.choice(NoPerson)
                            self.GetPosition(PersonSite,PersonNewSite,[self.Color,PersonState,PersonAge,PersonSex,PersonChilde])
                            PersonSite=copy.deepcopy(PersonNewSite)
                        elif Foe!=[]:#和平状态，周围有敌人
                            NewFriend=[]
                            for FoePosition in Foe:#检测有没有10%几率产生朋友
                                if random.random()<0.9:
                                    NewFriend.append(FoePosition)
                            if NewFriend==[]:#没有朋友
                                PersonState+=1
                                self.AddWorldInfo("("+str(PersonSite[0])+","+str(PersonSite[1])+") is in the war")
                            else:#有朋友
                                if random.random()<0.05:#产生新部落
                                    self.MemberList.remove(PersonSite)
                                    NewClanMember=[]
                                    for NewFriendPosition in NewFriend:
                                        MemberToQuitLock.acquire()
                                        MemberToQuit.append([Grid[NewFriendPosition[1]+1][NewFriendPosition[0]+1][0],[NewFriendPosition]])
                                        MemberToQuitLock.release()
                                        NewClanMember.append(NewFriendPosition)
                                    NewClanMember.append(PersonSite)
                                    ClanToGenerateLock.acquire()
                                    ClanToGenerate.append(NewClanMember)
                                    ClanToGenerateLock.release()
                                else:#不产生新部落的话，就将朋友变到自己门下
                                    for NewFriendPosition in NewFriend:
                                        MemberToQuitLock.acquire()
                                        MemberToQuit.append([Grid[NewFriendPosition[1]+1][NewFriendPosition[0]+1][0],[NewFriendPosition]])
                                        MemberToQuitLock.release()
                                        self.AddWorldInfo("("+str(NewFriendPosition[0])+","+str(NewFriendPosition[1])+") renegades")
                                        self.MemberList.append(NewFriendPosition)
                                        Grid[NewFriendPosition[1]+1][NewFriendPosition[0]+1][0]=self.Color
                        else:#和平状态，周围只有朋友
                            pass
                    if PersonState!=0:#战争状态
                        pass
                    GridLock.release()
                    #判断是否该死
                    if PersonAge>=self.DeadAge:
                        if random.random>=0.1:
                            GridLock.acquire()
                            self.PersonDead(PersonSite,PersonState)
                            GridLock.release()
                        else:
                            #不该死，年龄+1，信息重新写入
                            PersonAge+=1
                            GridLock.acquire()
                            Grid[PersonSite[1]+1][PersonSite[0]+1]=[self.Color,PersonState,PersonAge,PersonSex,PersonChilde]
                            GridLock.release()
                    else:
                        #不该死，年龄+1，信息重新写入
                        PersonAge+=1
                        GridLock.acquire()
                        Grid[PersonSite[1]+1][PersonSite[0]+1]=[self.Color,PersonState,PersonAge,PersonSex,PersonChilde]
                        GridLock.release()
            #等待下一次循环
            pygame.time.wait(1000/self.Speed)

    #人员死亡
    #此地清零，名单除名
    # 如果state是0 pass，如果非1，则检查周边，如果发现颜色不一样，state减少1（最小为0)
    def PersonDead(self,PersonSite,PersonState):
        #此地清零，名单除名
        Grid[PersonSite[1]+1][PersonSite[0]+1]=None
        self.MemberList.remove(PersonSite)
        # 如果state是0 pass，如果非1，则检查周边，如果发现颜色不一样，state减少1（最小为0)
        if PersonState!=0:
            for n in range(len(AddX)):
                Other=Grid[PersonSite[1]+1+AddY[n]][PersonSite[0]+1+AddX[n]]
                if Other=='W' or Other==None:
                    pass
                else:
                    OtherColor=Other[0]
                    if OtherColor!=self.Color:
                        Other[1]-=1
                        if Other[1]<0:
                            Other[1]=0

    #得到位置函数
    #如果OldPosition==None，在NewPosition添加Member，并将其加入MemberList
    #如果OldPosition!=None，将OldPosition清为None，将NewPosition添加为Member，并相应改变MmberList
    def GetPosition(self,OldPosition,NewPosition,Member):
        if OldPosition==None:
            self.MemberList.append(NewPosition)
        else:
            Grid[OldPosition[1]+1][OldPosition[0]+1]=None
            MemberListPosition=self.MemberList.index(OldPosition)
            self.MemberList[MemberListPosition]=NewPosition
        Grid[NewPosition[1]+1][NewPosition[0]+1]=Member

    #检查次部落是否还有人
    #有人 pass，没有人，在ColorExist里面删除Color，在ClanInfo里面删除信息，在WorldInfo添加信息
    def ClanExist(self):
        if self.MemberList==[]:
            #在ColorExist里面删除Color
            ColorExistLock.acquire()
            ColorExist.remove(self.Color)
            ColorExistLock.release()
            #在ClanInfo里面删除信息
            ClanInfoLock.acquire()
            for ClanInformation in ClanInfo:
                if ClanInformation[0].find(self.name)!=-1:
                    break
            ClanInfo.remove(ClanInformation)
            ClanInfoLock.release()
            self.AddWorldInfo("Clan "+self.name+" is over!")
            sys.exit()

    #更新ClanInfo
    #如果是新部落成立，那么ClanInfo加入新信息
    #如果没有，刷新ClanInfo的人数
    def RefreshClanInfo(self,new):
        if new==1:
            ClanInfoLock.acquire()
            ClanInfo.append(["Clan "+self.name+": "+str(len(self.MemberList))+" members",self.Color])
            ClanInfoLock.release()
        else:
            ClanInfoLock.acquire()
            for n in range(len(ClanInfo)):
                if ClanInfo[n][1]!=self.Color:
                    pass
                else:
                    ClanInfo[n]=(["Clan "+self.name+": "+str(len(self.MemberList))+" members",self.Color])
                    break
            ClanInfoLock.release()

    #向WorldInfo添加AddString
    def AddWorldInfo(self,AddString):
        WorldInfoLock.acquire()
        WorldInfo.append([AddString,self.Color])
        WorldInfoLock.release()

    #查看是否有Member因为新的部落成立而退出
    def QuitMember(self):
        MemberToQuitLock.acquire()
        for MemberQuit in MemberToQuit:
            if MemberQuit[0]==self.Color:
                for MemberQuitPosition in MemberQuit[1]:
                    try:
                        self.MemberList.remove(MemberQuitPosition)
                    except:
                        pass
                MemberToQuit.remove(MemberQuit)
        MemberToQuitLock.release()
##############################################################################

##############################################################################
# 一个用来管理 Pygame 事件的函数
def HandleEvents():
    global Pause
    global RunState
    for event in pygame.event.get():
        # 点击窗口上的“关闭”或是按"esc"退出
        # s:pause
        # b:begin
        if event.type == QUIT or (event.type==KEYDOWN and event.key==K_ESCAPE):
            RunState=0
            pygame.quit()
            sys.exit()
        elif event.type==KEYDOWN and event.key==K_s:
            Pause=1
        elif event.type==KEYDOWN and event.key==K_b:
            Pause=0
##############################################################################

##############################################################################
# 一个函数，用来绘制屏幕
def DrawScreen():
    #屏幕填充为白色
    Surface.fill(ScreenBackgroundColor)
    #部落信息填充为灰色
    pygame.draw.rect(Surface,FontBackgroundColor,ClanInfoPosition)
    #实时状况填充为灰色
    pygame.draw.rect(Surface,FontBackgroundColor,WorldInfoPosition)
    #绘制方格
    for y in range(GridPosition[1],GridPosition[1]+CellSize*NumW+1,CellSize):
        pygame.draw.line(Surface,GridLineColor,(GridPosition[0],y),(GridPosition[0]+CellSize*NumW,y))
    for x in range(GridPosition[0],GridPosition[0]+CellSize*NumL+1,CellSize):
        pygame.draw.line(Surface,GridLineColor,(x,GridPosition[1]),(x,GridPosition[1]+CellSize*NumL))
    #画出map
    GridLock.acquire()
    for x in range(NumL):
        for y in range(NumW):
            if Grid[y+1][x+1]==None:
                pass
            else:
                GridColor=Grid[y+1][x+1][0]
                pygame.draw.rect(Surface,GridColor,Rect(GridPosition[0]+x*CellSize+1\
                    ,GridPosition[1]+y*CellSize+1\
                    ,CellSize-2,CellSize-2))
    GridLock.release()
##############################################################################


##############################################################################
# 主函数
def Main():
    global Surface, font, ClanToGenerate

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
    ClanInfoLock.acquire()
    ClanInfoText=copy.deepcopy(ClanInfo)
    ClanInfoLock.release()

    Clan().start()
    Clan().start()
    Clan().start()

    while True:
        #执行事件
        HandleEvents()
        #ClanToGenerate
        if ClanToGenerate!=[]:
            ClanToGenerateLock.acquire()
            for NewClanPosition in ClanToGenerate:
                Clan(Position=NewClanPosition).start()
            ClanToGenerate=[]
            ClanToGenerateLock.release()
        #刷新屏幕
        DrawScreen()
        #######################################################
        #刷新ClanInfo
        ClanInfoLock.acquire()
        if ClanInfoText==[]:
            #ClanInfo第一次显示头一个字的位置
            ClanInfofirstx=ClanInfoStartx
            #ClanInfo第一次要显示的字
            ClanInfoText=copy.deepcopy(ClanInfo)
        else:
            ClanInfox=ClanInfofirstx
            for i in range(len(ClanInfoText)):
                TextToDisplay=font.render(ClanInfoText[i][0],True,ClanInfoText[i][1])
                Surface.blit(TextToDisplay,(ClanInfox,ClanInfoy))
                if i==len(ClanInfoText)-1:
                    ClanInfox=ClanInfox+fontWide*len(ClanInfoText[i][0])
                else:
                    ClanInfox=ClanInfox+fontWide*len(ClanInfoText[i][0])+10
            if ClanInfox<0:
                ClanInfofirstx=ClanInfoStartx
                ClanInfoText=copy.deepcopy(ClanInfo)
            else:
                ClanInfofirstx-=3
        ClanInfoLock.release()
        ######################################################
        #刷新WorldInfo的信息
        #WorldInfo显示头一个字的位置
        WorldInfoy=WorldInfoStarty-fontHeight
        #WorldInfo要显示的字
        WorldInfoLock.acquire()
        WorldInfoText=WorldInfo
        WorldInfoText=WorldInfoText[-(500-fontHeight)/fontHeight:]
        for text in reversed(WorldInfoText):
            Surface.blit(font.render(text[0],True,text[1]),(WorldInfox,WorldInfoy))
            WorldInfoy-=fontHeight
        WorldInfoLock.release()
        #######################################################

        pygame.display.update()
        FPSClock.tick(FPS)
####################################################################################

if __name__=="__main__":
    Main()
