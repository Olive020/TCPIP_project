from itertools import count
import pygame as pg
import os
import random
import socket
import json
import threading
from sqlalchemy import false, true
import time
#全域變數
clock=pg.time.Clock()
speed=[random.randint(-5,5),5,-6,5]
deadline=710
id=None
life=0
score=0
ui_input='input server address'
MAX_BYTES = 65535
pg.init()#初始化
pg.mixer.init
pg.mixer.music.set_volume(1.0)
pg.display.set_caption('飛機遊戲')

os.environ['SDL_VIDEO_WINDOW_POS']="%d,%d"%(0,32)#視窗
width,height=1280,720
screen=pg.display.set_mode((width,height))#視窗大小

#載入圖片
path1=os.path.abspath('.')
ch=path1+'\\TCPIP_project\\picture\\'
ui_background_jpg=pg.image.load(ch+'ui.png')
background_jpg=pg.image.load(ch+'background.jpg')
airplane_jpg=pg.image.load(ch+"airplane2.png").convert_alpha()
ball=pg.image.load(ch+"ball.png").convert_alpha()
enairplane_jpg=pg.image.load(ch+"enairplane.png").convert_alpha()
pausebtn=pg.image.load(ch+"pause.png").convert_alpha()
startbtn=pg.image.load(ch+"START.png").convert_alpha()
bomboldbig=pg.image.load(ch+"bombold.png").convert_alpha()

#改變圖片大小
ui_background=pg.transform.scale(ui_background_jpg,(width,height))
startbtn=pg.transform.scale(startbtn,(200,100))
airplane=pg.transform.scale(airplane_jpg,(80,90))
background=pg.transform.scale(background_jpg,(width,height))
enairplane=pg.transform.scale(enairplane_jpg,(80,90))
bombold=pg.transform.scale(bomboldbig,(90,100))


#獲得圖片的矩形資料以及設定初始座標
back_rect=background.get_rect()
ui_back_rect=ui_background.get_rect()
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
    bul.append(pg.transform.scale(pg.image.load(ch+"bullet.png").convert_alpha(),(15,40)))
    bul_rect.append(bul[i].get_rect())
    bul_rect[i].center=width,height
    enbul.append(pg.transform.scale(pg.image.load(ch+"enbullet.png").convert_alpha(),(15,40)))
    enbul_rect.append(enbul[i].get_rect())
    enbul_rect[i].center=-1,-1
bul_num=-1
enbul_num=-1

  
# 播放音效
def play_sound(path):
    ouch = pg.mixer.Sound(path)
    pg.mixer.Sound.set_volume(ouch,0.3)
    pg.mixer.Sound.play(ouch)

#碰撞判定
def rebound0(atop,abot,al,ar,btop,bbot,bl,br):#a:子彈  b:敵機
    if atop<=bbot and abot>=btop and al<=br and ar>=bl:
        return True
    else:
        return False
    #暫停
def pause(a):
    scoretext = font2.render("暫停中",True,(0,200,0))
    score_rect=scoretext.get_rect()
    score_rect.center=width/2,height/4
    start_png=pg.image.load(ch+'START.png')
    start=pg.transform.scale(start_png,(400,200))
    start2_png=pg.image.load(ch+'START2.png')
    start2=pg.transform.scale(start2_png,(400,200))
    start_rect=start.get_rect()
    start_rect.center=width/4,height/2+150
    start_print=start
    main_png=pg.image.load(ch+'MAIN.png')
    main=pg.transform.scale(main_png,(400,200))
    main2_png=pg.image.load(ch+'MAIN2.png')
    main2=pg.transform.scale(main2_png,(400,200))
    main_print=main
    main_rect=main.get_rect()
    main_rect.center=width*3/4,height/2+150
    while a:
        clock.tick(30)
        for event in pg.event.get():
            if event.type==pg.QUIT:
                pg.quit()
            if event.type==pg.MOUSEMOTION:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    start_print=start2
                else:
                    start_print=start
                if y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    main_print=main2
                else:
                    main_print=main
            if event.type==pg.MOUSEBUTTONDOWN:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right :
                    play_sound(ch + "button05.mp3")
                    return 1
                if y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right :
                    play_sound(ch + "button05.mp3")
                    return 0
        screen.blit(background,back_rect)
        screen.blit(lifetext,life_rect)
        screen.blit(airplane,airplane_rect)
        screen.blit(start_print,start_rect)
        screen.blit(main_print,main_rect)
        screen.blit(scoretext,score_rect)
        pg.display.update()
        
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
    if object.centerx<0:
        object.centerx=0
    elif object.centery>=1280:
        object.centerx=1280
    if object.centery<450:
        object.centery=450
    elif object.centery>600:
        object.centery=600

def game_over():
    scoretext = font2.render("GAME OVER",True,(255,0,0))
    score_rect=scoretext.get_rect()
    score_rect.center=width/2,height/4
    if not pg.mixer.music.get_busy():
        pg.mixer.music.load(ch+'No Hope.mp3')
        pg.mixer.music.play()
    i=0
    while i<256:
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:
                pg.quit()
        scoretext.set_alpha(i)
        time.sleep(0.05078125)
        screen.blit(scoretext,score_rect)
        pg.display.update()
        i+=1
    
    #偵測關閉事件
def restart(a):
    start_png=pg.image.load(ch+'START.png')
    start=pg.transform.scale(start_png,(400,200))
    start2_png=pg.image.load(ch+'START2.png')
    start2=pg.transform.scale(start2_png,(400,200))
    start_rect=start.get_rect()
    start_rect.center=width/4-100,height/2+150
    start_print=start
    main_png=pg.image.load(ch+'MAIN.png')
    main=pg.transform.scale(main_png,(400,200))
    main2_png=pg.image.load(ch+'MAIN2.png')
    main2=pg.transform.scale(main2_png,(400,200))
    main_print=main
    main_rect=main.get_rect()
    main_rect.center=width/2,height/2+150
    exit_png=pg.image.load(ch+'EXIT.png')
    exit=pg.transform.scale(exit_png,(400,200))
    exit2_png=pg.image.load(ch+'EXIT2.png')
    exit2=pg.transform.scale(exit2_png,(400,200))
    exit_print=exit
    exit_rect=exit.get_rect()
    exit_rect.center=width*3/4+100,height/2+150
    while a:
        # if not pg.mixer.music.get_busy():
        #     pg.mixer.music.load(ch+'')
        #     pg.mixer.music.play()
        clock.tick(30)
        scoretext = font2.render("是否繼續遊玩",True,(0,255,0))
        score_rect=scoretext.get_rect()
        score_rect.center=width/2,height/4
        #pygame 事件處理
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:
                pg.quit()
            if event.type==pg.MOUSEMOTION:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    start_print=start2
                else:
                    start_print=start
                if y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    main_print=main2
                else:
                    main_print=main
                if y>=exit_rect.top and y<=exit_rect.bottom and x>=exit_rect.left and x<=exit_rect.right:
                    exit_print=exit2
                else:
                    exit_print=exit
            if event.type == pg.MOUSEBUTTONDOWN:
                x,y = pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    play_sound(ch + "button05.mp3")
                    a=False 
                    pg.mixer.music.stop()
                elif y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    play_sound(ch + "button05.mp3")
                    pg.mixer.music.stop()
                    return 1
                elif y>=exit_rect.top and y<=exit_rect.bottom and x>=exit_rect.left and x<=exit_rect.right:
                    play_sound(ch + "button05.mp3")
                    pg.quit()
        screen.blit(background,back_rect)
        screen.blit(start_print,start_rect)
        screen.blit(main_print,main_rect)
        screen.blit(exit_print,exit_rect)
        screen.blit(scoretext,score_rect)
        pg.display.update()

def main_ui():
    # Settings
    path1=os.path.abspath('.')
    ch=path1+'\\TCPIP_project\\picture\\'
    start_png=pg.image.load(ch+'START.png')
    start=pg.transform.scale(start_png,(400,200))
    start_rect=start.get_rect()
    start_rect.center=width/4,height/2+150
    start2_rect=start.get_rect()
    start2_rect.center=width/4+600,height/2+150
    
    pra_png=pg.image.load(ch+'practise.png')
    pra_p=pg.transform.scale(pra_png,(400,200))
    pra_png2=pg.image.load(ch+'practise2.png')
    pra_p2=pg.transform.scale(pra_png2,(400,200))
    print_pra=pra_p

    game_png=pg.image.load(ch+'game_start.png')
    game_p=pg.transform.scale(game_png,(400,200))
    game_png2=pg.image.load(ch+'game_start2.png')
    game_p2=pg.transform.scale(game_png2,(400,200))
    print_game=game_p

    change_background_jpg=pg.image.load(ch+'background.jpg')
    change_background=pg.transform.scale(change_background_jpg,(width,height))
    change_back_rect=change_background.get_rect()
    font=pg.font.SysFont("Microsoft Jhenghei",60)
    totaltext=font.render(f"飛機遊戲",True,(255,255,255))
    total_rect=totaltext.get_rect()
    total_rect.center=width/2,height/4
    
    running = True

    # Font
    font = pg.font.SysFont("微軟正黑體",50)
    # Run
    while running:
        if not pg.mixer.music.get_busy():
            pg.mixer.music.load(ch+'Space Sprinkles.mp3')
            pg.mixer.music.play(-1)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right :
                    play_sound(ch + "button05.mp3")
                    pg.mixer.music.stop()
                    return 2
                if y>=start2_rect.top and y<=start2_rect.bottom and x>=start2_rect.left and x<=start2_rect.right :
                    play_sound(ch + "button05.mp3")
                    pg.mixer.music.stop()
                    return 1
            if event.type==pg.MOUSEMOTION:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    print_pra=pra_p2
                else:
                    print_pra=pra_p
                if y>=start2_rect.top and y<=start2_rect.bottom and x>=start2_rect.left and x<=start2_rect.right:
                    print_game=game_p2
                else:
                    print_game=game_p

        # Updates
        screen.blit(change_background,change_back_rect)
        screen.blit(totaltext, total_rect)
        screen.blit(print_pra, start_rect)
        screen.blit(print_game, start2_rect)
        pg.display.flip()
#連線介面
def ui(ui_input):
    # Settings
    color_background = (0, 0, 0)
    color_inactive = (0, 0, 255)
    color_active = (0, 200, 255)
    color = color_inactive
    text = ""
    active = False
    running = True

    # Font
    font = pg.font.SysFont("微軟正黑體",50)

    # Input box
    input_box = pg.Rect(100, 100, 140, 32)
    # Run
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True  
                else: 
                    active=False

                if active:
                    color=color_active  
                else: 
                    color=color_inactive

            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        play_sound(ch + "button05.mp3")
                        return text
                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        # Input box
        text_surface = font.render(text, True, color)
        text_addr=font.render(ui_input, True, color_inactive)
        input_box_width = max(200, text_surface.get_width()+10)
        input_box.w = input_box_width
        input_box.center = (width/2, height/2+80)

        # Updates
        screen.blit(ui_background,ui_back_rect)
        screen.blit(text_surface, (input_box.x+5, input_box.y))
        screen.blit(text_addr, (input_box.x-60, input_box.y-40))
        pg.draw.rect(screen, color, input_box, 3)
        pg.display.flip()
par=False
game_start=False
while True:
    switch=main_ui()
    if switch==2:
        par=True
    elif switch==1:
        game_start=True
    while par: 
        
        #字串字體和大小
        font=pg.font.SysFont("微軟正黑體",36)
        font2 = pg.font.SysFont("Microsoft Jhenghei",60)
        #倒數計時
        COUNT=pg.USEREVENT+1
        pg.time.set_timer(COUNT,1000)
        runtime=60
        life=10
        bnbnoin=True
        bnbspeed=[0,0]
        debomb_num=100
        mo=[-2,2]
        eneSpeed=mo[random.randint(0,1)]
        logic_x,logic_dex,logic_y,logic_dey=false,false,false,false
        scoretext = font2.render(f"score:{score}",True,(0,0,0))
        score_rect=scoretext.get_rect()
        score_rect.center=width/2,height/2
        operation=True#game start
        while operation:
            if not pg.mixer.music.get_busy():
                    pg.mixer.music.load(ch+'Endless Pain of Nightmares.WAV')
                    pg.mixer.music.play(-1)
            clock.tick(60)#fps
            lifetext=font.render(f"life:{life}",True,(0,0,0))
            life_rect=lifetext.get_rect()
            life_rect.top=airplane_rect.bottom
            life_rect.centerx=airplane_rect.centerx

            #偵測使用者觸發的事件
            for event in pg.event.get():
                if event.type==pg.QUIT:
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
                            play_sound(ch + "attack1.mp3")
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
                        play_sound(ch + "button05.mp3")
                        a=True
                        pause_b=pause(a)
                        if pause_b==0:
                            operation=False
                            par=False
                            pg.mixer.music.stop()
                    #我方子彈發射
                    bul_num_after=bul_num
                    bul_num=(bul_num+1)%5
                    if bul_rect[bul_num].centerx==width:
                        play_sound(ch + "attack1.mp3")
                        bul_rect[bul_num].center=airplane_rect.center
                    else:
                        bul_num=bul_num_after
            vector(airplane_rect,logic_dex,logic_x,logic_dey,logic_y)
            logic=random.randint(0,50)
            if logic==1:#敵人子彈發射
                enbul_num=(enbul_num+1)%5
                if enbul_rect[enbul_num].centerx==-1:
                    play_sound(ch + "attack1.mp3")
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
                pg.mixer.music.stop()
                game_over()
                control_choose=restart(True)
                life=10
                score=0
                if control_choose==1: 
                    par=False
                    break
                

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
                play_sound(ch + "damage1.mp3")
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
    while game_start: 
        server_addr = (ui('input server address'),6000)
        nickname=ui('Input your name')
        # 建立一個UDP socket
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #字串字體和大小
        font=pg.font.SysFont("微軟正黑體",36)
        font2 = pg.font.SysFont("Microsoft Jhenghei",60)
        #倒數計時
        COUNT=pg.USEREVENT+1
        pg.time.set_timer(COUNT,1000)
        runtime=60

        life=10
        bnbnoin=True
        bnbspeed=[0,0]
        debomb_num=100
        mo=[-2,2]
        eneSpeed=mo[random.randint(0,1)]
        logic_x,logic_dex,logic_y,logic_dey=false,false,false,false
        scoretext = font2.render(f"score:{score}",True,(0,0,0))
        score_rect=scoretext.get_rect()
        score_rect.center=width/2,height/2
        operation=True
        while operation:
            if not pg.mixer.music.get_busy():
                    pg.mixer.music.load(ch+'Endless Pain of Nightmares.WAV')
                    pg.mixer.music.play(-1)
            clock.tick(60)#fps
            lifetext=font.render(f"life:{life}",True,(0,0,0))
            life_rect=lifetext.get_rect()
            life_rect.top=airplane_rect.bottom
            life_rect.centerx=airplane_rect.centerx

            #偵測使用者觸發的事件
            for event in pg.event.get():
                if event.type==COUNT:
                    runtime-=1
                if event.type==pg.QUIT :
                    pg.quit()
                if event.type==pg.MOUSEMOTION:
                    x,y=pg.mouse.get_pos()
                    if y<450:
                        y=450
                    elif y>600:
                        y=600
                    airplane_rect.center=x,y
                    #######################################################################
                    #######################################################################
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
                            play_sound(ch + "attack1.mp3")
                            #############################################################
                            pass
                            #############################################################
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
                        pause_b=pause(a)
                        if pause_b==0:
                            operation=False
                            game_start=False
                            pg.mixer.music.stop()
                    #我方子彈發射
                    bul_num_after=bul_num
                    bul_num=(bul_num+1)%5
                    if bul_rect[bul_num].centerx==width:
                        play_sound(ch + "attack1.mp3")
                        bul_rect[bul_num].center=airplane_rect.center
                        ############################################################
                        pass
                        ############################################################
                    else:
                        bul_num=bul_num_after
            vector(airplane_rect,logic_dex,logic_x,logic_dey,logic_y)
            ############################################################################################
            # if logic==1:#敵人子彈發射
            #     enbul_num=(enbul_num+1)%5
            #     if enbul_rect[enbul_num].centerx==-1:
            #         enbul_rect[enbul_num].center=enairplane_rect.center
            ############################################################################################
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
                    bul_rect[i].center=width,height
                if  bnbnoin:
                    bnbspeed[1]=random.randint(2,5)
                    bnbnoin=False


        
            if life <=0:
                ######################################################################
                #####################################################################
                pg.mixer.music.stop()
                control_choose=restart(True)
                life=10
                score=0
                if control_choose==1: 
                    game_start=False
                    break
            #############################################################################
            #敵機移動
            ###############################################################################
                
            #圖片更新
            screen.blit(background,back_rect)
            screen.blit(enairplane,enairplane_rect)
            if debomb_num<30:
                play_sound(ch + "damage1.mp3")
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

