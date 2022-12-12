from itertools import count
import pygame as pg
import os
import random
import socket
import json
import threading
from sqlalchemy import false, true
#全域變數
clock=pg.time.Clock()
speed=[random.randint(-5,5),5,-6,5]
deadline=710
id=None
life=10
score=0

pg.init()#初始化
pg.display.set_caption('飛機遊戲')

os.environ['SDL_VIDEO_WINDOW_POS']="%d,%d"%(0,32)#視窗
width,height=1280,720
screen=pg.display.set_mode((width,height))#視窗大小

#載入圖片
path1=os.path.abspath('.')
ch=path1+'\\TCPIP_project\\picture\\'
background_jpg=pg.image.load(ch+'background.jpg')
airplane_jpg=pg.image.load(ch+"airplane.png").convert_alpha()
ball=pg.image.load(ch+"ball.png").convert_alpha()
enairplane_jpg=pg.image.load(ch+"enairplane.png").convert_alpha()
pausebtn=pg.image.load(ch+"pause.png").convert_alpha()
startbtn=pg.image.load(ch+"START.png").convert_alpha()
bomboldbig=pg.image.load(ch+"bombold.png").convert_alpha()

#改變圖片大小
airplane=pg.transform.scale(airplane_jpg,(80,90))
background=pg.transform.scale(background_jpg,(width,height))
enairplane=pg.transform.scale(enairplane_jpg,(70,80))
bombold=pg.transform.scale(bomboldbig,(90,100))


#獲得圖片的矩形資料以及設定初始座標
back_rect=background.get_rect()

airplane_rect=airplane.get_rect()
airplane_rect.center=width/2,600

ball_rect=ball.get_rect()#暫時是子彈
enairplane_rect=enairplane.get_rect()
enairplane_rect.bottomleft=random.randint(enairplane_rect.width,width-enairplane_rect.width),80

bombold_rect=bombold.get_rect()#爆炸特效

pause_rect=pausebtn.get_rect()
pause_rect.topright=width,0

start_rect=startbtn.get_rect()
start_rect.center=width/2,height/2+150


#設定我方子彈和敵方子彈
bul=[]
bul_rect=[]
enbul=[]
enbul_rect=[]
for i in range(10):
    bul.append(pg.transform.scale(pg.image.load(ch+"ball.png").convert_alpha(),(15,15)))
    bul_rect.append(bul[i].get_rect())
    bul_rect[i].center=width,height
    enbul.append(pg.transform.scale(pg.image.load(ch+"ball.png").convert_alpha(),(15,15)))
    enbul_rect.append(enbul[i].get_rect())
    enbul_rect[i].center=-1,-1
bul_num=-1
enbul_num=-1

    






#碰撞判定
def rebound0(atop,abot,al,ar,btop,bbot,bl,br):#a:子彈  b:敵機
    if atop<=bbot and abot>=btop and al<=br and ar>=bl:
        return True
    else:
        return False
#暫停
def pause(a):
    while a:
        clock.tick(30)
        scoretext = font2.render(f"score:{score}",True,(150,100,100))
        score_rect=scoretext.get_rect()
        score_rect.center=width/2,height/2

        screen.blit(background,back_rect)
        screen.blit(lifetext,life_rect)
        screen.blit(airplane,airplane_rect)
        screen.blit(startbtn,start_rect)
        screen.blit(scoretext,score_rect)
        pg.display.update()
        for event in pg.event.get():
            if event.type==pg.QUIT:
                operation=False
                pg.quit()
            if event.type==pg.MOUSEBUTTONDOWN:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right :
                    a=False
#飛機移動
def vector(object,dex,x,dey,y):
    if dex==True:
        object.centerx-=3
    if x==True:
        object.centerx+=3
    if dey==True:
        object.centery-=3
    if y==True:
        object.centery+=3





#偵測關閉事件
def restart(a):
    while a:
        clock.tick(30)
        scoretext = font2.render(f"score:{score}",True,(0,0,0))
        score_rect=scoretext.get_rect()
        score_rect.center=width/2,height/2
        #pygame 事件處理
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                x,y = pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    a=False
        screen.blit(background,back_rect)
        screen.blit(startbtn,start_rect)
        screen.blit(scoretext,score_rect)
        pg.display.update()
#字串字體和大小
font=pg.font.SysFont("微軟正黑體",36)
font2 = pg.font.SysFont("微軟正黑體",60)
#倒數計時
COUNT=pg.USEREVENT+1
pg.time.set_timer(COUNT,1000)
runtime=60

bnbnoin=True
bnbspeed=[0,0]
operation=True#game start
debomb_num=100
mo=[-2,2]
eneSpeed=mo[random.randint(0,1)]
logic_x,logic_dex,logic_y,logic_dey=false,false,false,false

while operation:
    clock.tick(60)#fps
    lifetext=font.render(f"life:{life}",True,(0,0,0))
    life_rect=lifetext.get_rect()
    life_rect.top=airplane_rect.bottom
    life_rect.centerx=airplane_rect.centerx

    #偵測使用者觸發的事件
    for event in pg.event.get():
        if event.type==COUNT:
            runtime-=1
        if event.type==pg.QUIT or runtime==0:
            pg.quit()
        if event.type==pg.MOUSEMOTION:
            x,y=pg.mouse.get_pos()
            if y<450:
                y=450
            elif y>600:
                y=600
            airplane_rect.center=x,y
        if event.type==pg.KEYDOWN :
            if event.key==pg.K_a or event.key==pg.K_LEFT:
                logic_dex=True
            elif event.key==pg.K_d or event.key==pg.K_RIGHT:
                logic_x=True
            elif event.key==pg.K_w or event.key==pg.K_UP:
                logic_dey=True
            elif event.key==pg.K_s or event.key==pg.K_DOWN:
                logic_y=True
            if event.key==pg.K_SPACE:
                bul_num_after=bul_num
                bul_num=(bul_num+1)%5
                if bul_rect[bul_num].centerx==width:
                    bul_rect[bul_num].center=airplane_rect.center
                else:
                    bul_num=bul_num_after
        if event.type==pg.KEYUP:
            if event.key==pg.K_a or event.key==pg.K_LEFT:
                logic_dex=False
            if event.key==pg.K_d or event.key==pg.K_RIGHT:
                logic_x=False
            if event.key==pg.K_w or event.key==pg.K_UP:
                logic_dey=False
            if event.key==pg.K_s or event.key==pg.K_DOWN:
                logic_y=False
        if event.type==pg.MOUSEBUTTONDOWN:
            x,y=pg.mouse.get_pos()
            if y>=pause_rect.top and y<=pause_rect.bottom and x>=pause_rect.left and x<=pause_rect.right :
                a=True
                pause(a)
            #我方子彈發射
            bul_num_after=bul_num
            bul_num=(bul_num+1)%5
            if bul_rect[bul_num].centerx==width:
                bul_rect[bul_num].center=airplane_rect.center
            else:
                bul_num=bul_num_after
    vector(airplane_rect,logic_dex,logic_x,logic_dey,logic_y)
    logic=random.randint(0,100)
    if logic==1:#敵人子彈發射
        enbul_num=(enbul_num+1)%5
        if enbul_rect[enbul_num].centerx==-1:
            enbul_rect[enbul_num].center=enairplane_rect.center
    for i in range(5):
        enbul_rect[i]=enbul_rect[i].move(0,speed[3])#子彈移動
        if enbul_rect[i].top>=height:#是否到達視窗底部
            enbul_rect[i].center=-1,-1
        if bul_rect[i].centerx!=width:#是否是射出的子彈
            bul_rect[i]=bul_rect[i].move(0,speed[2])
        if bul_rect[i].top<=0:#將子彈重置
            bul_rect[i].center=width,height



    #碰撞判定
    for i in range(5):
        for j in range(5):
            if rebound0(bul_rect[i].top,bul_rect[i].bottom,bul_rect[i].left,bul_rect[i].right,enbul_rect[j].top,enbul_rect[j].bottom,enbul_rect[j].left,enbul_rect[j].right):
                bul_rect[i].center=width,height
                enbul_rect[j].center=-1,-1
        if rebound0(airplane_rect.top,airplane_rect.bottom,airplane_rect.left,airplane_rect.right,enbul_rect[i].top,enbul_rect[i].bottom,enbul_rect[i].left,enbul_rect[i].right):
            enbul_rect[i].center=-1,-1
            life-=1
        if rebound0(bul_rect[i].top,bul_rect[i].bottom,bul_rect[i].left,bul_rect[i].right,enairplane_rect.top,enairplane_rect.bottom,enairplane_rect.left,enairplane_rect.right): 
            bnbnoin=True
            debomb_num=0
            bombold_rect.center=enairplane_rect.center
            eneSpeed=mo[random.randint(0,1)]
            enairplane_rect.bottomleft=random.randint(enairplane_rect.width,width-enairplane_rect.width),80
            bul_rect[i].center=width,height
        if  bnbnoin:
            bnbspeed[1]=random.randint(2,5)
            bnbnoin=False


   
    if life <=0:
        restart(True)
        score=0
        life=10
    #敵機左右移動
    enairplane_rect=enairplane_rect.move(eneSpeed,0)
    if enairplane_rect.centerx>=pause_rect.centerx:
        enairplane_rect.centerx=pause_rect.centerx
        eneSpeed=-2
    elif enairplane_rect.left<=0:
        enairplane_rect.left=1
        eneSpeed=2

        
    #圖片更新
    screen.blit(background,back_rect)
    screen.blit(enairplane,enairplane_rect)
    if debomb_num<30:
        screen.blit(bombold,bombold_rect)
        debomb_num+=1

    for i in range(5):
        if bul_rect[i].centerx>=0:
            screen.blit(bul[i],bul_rect[i])
        if enbul_rect[i].centerx>=0:
            screen.blit(enbul[i],enbul_rect[i])
    if((ball_rect.centerx<0)):
        screen.blit(ball,ball_rect)
    screen.blit(airplane,airplane_rect)
    screen.blit(lifetext,life_rect)
    screen.blit(pausebtn,pause_rect)
    pg.display.update()