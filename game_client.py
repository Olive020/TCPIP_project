from itertools import count
from tracemalloc import stop
import pygame as pg
import os
import random
import socket
import json
import threading
from sqlalchemy import false, true
import time
import sys

#全域變數
clock=pg.time.Clock()
#子彈移動速度
speed=[random.randint(-5,5),5,-6,5]
deadline=710
id=None
life=0
score=0
ui_input='input server address'
MAX_BYTES = 65535
#初始化
pg.init()
pg.mixer.init()
pg.mixer.music.set_volume(1.0)
pg.display.set_caption('飛機遊戲')
os.environ['SDL_VIDEO_WINDOW_POS']="%d,%d"%(0,32)#視窗
width,height=1280,720
screen=pg.display.set_mode((width,height))#視窗大小

#載入圖片
path1=os.path.abspath('.')
ch=path1+'\\picture\\'
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
enbul_num_after=enbul_num



bossbul=[]
bossbul_rect=[]
bossbul_num=[]
bossSpeed=[]
boss_mo=[-2,2]
bossairplane=[]
bossairplane_rect=[]
boss_bombold_rect=[]
boss_bombold_num=[]
enairplane_rect=enairplane.get_rect()
enairplane_rect.bottomleft=random.randint(enairplane_rect.width,width-enairplane_rect.width),80
for i in range(10):
    bossbul.append([])
    boss_bombold_num.append(0)
    boss_bombold_rect.append(bombold_rect)
    boss_bombold_rect[i].center=-1,-1
    bossbul_rect.append([])
    bossbul_num.append(-1)
    bossSpeed.append(boss_mo[random.randint(0,1)])
    bossairplane.append(pg.transform.scale(pg.image.load(ch+"enairplane.png").convert_alpha(),(80,90)))
    bossairplane_rect.append(bossairplane[i].get_rect())
    bossairplane_rect[i].bottomleft=random.randint(enairplane_rect.width,width-enairplane_rect.width),80
    for j in range(10):
        bossbul[i].append(pg.transform.scale(pg.image.load(ch+"enbullet.png").convert_alpha(),(15,40)))
        bossbul_rect[i].append(bossbul[i][j].get_rect())
        bossbul_rect[i][j].center=-1,-1

  
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
                sys.exit()
            if event.type==pg.MOUSEMOTION:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    if start_print==start:
                        play_sound(ch + "button.mp3")
                    start_print=start2
                else:
                    start_print=start
                if y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    if main_print==main:
                        play_sound(ch + "button.mp3")
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
    if object.left<0:
        object.left=0
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
                sys.exit()
        scoretext.set_alpha(i)
        time.sleep(0.05078125)
        screen.blit(scoretext,score_rect)
        pg.display.update()
        i+=1
def addres_error():
    scoretext = font2.render("此伺服器不存在",True,(255,0,0))
    score_rect=scoretext.get_rect()
    score_rect.center=width/2,height/2
    i=0
    while i<256:
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        scoretext.set_alpha(i)
        time.sleep(0.02078125)
        screen.blit(scoretext,score_rect)
        pg.display.update()
        i+=1    

def standby():
    scoretext=[]
    scoretext.append(font2.render("等待配對中",True,(255,0,0)))
    scoretext.append(font2.render("等待配對中.",True,(255,0,0)))
    scoretext.append(font2.render("等待配對中. .",True,(255,0,0)))
    scoretext.append(font2.render("等待配對中. . .",True,(255,0,0)))
    
    score_rect=scoretext[0].get_rect()
    score_rect.center=width/2,height/2
    i=0
    run=0
    global is_entered,background,back_rect
    while not is_entered:
        clock.tick(60)
        if not pg.mixer.music.get_busy():
                pg.mixer.music.load(ch+'Clouds.Wav')
                pg.mixer.music.play(-1)
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:
                # pg.quit()
                # sys.exit()
                pass
        screen.blit(background,back_rect)
        screen.blit(scoretext[i],score_rect)
        pg.display.update()
        if run==40:
            run=0
            i=(i+1)%4
        run+=1
         
    pg.mixer.music.stop() 

    #偵測關閉事件
def restart_game(a):
    global number
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

    scoretext = font2.render("是否繼續遊玩",True,(0,255,0))
    score_rect=scoretext.get_rect()
    score_rect.center=width/2,height/4
  
    numbertext = font2.render(f"score:{number}",True,(100,200,0))
    number_rect=numbertext.get_rect()
    number_rect.center=width/2,height/4-100
    while a:
        if not pg.mixer.music.get_busy():
            pg.mixer.music.load(ch+'lo-fi_fall.mp3')
            pg.mixer.music.play(-1)
        clock.tick(30)
        
        #pygame 事件處理
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type==pg.MOUSEMOTION:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    if start_print==start:
                        play_sound(ch + "button.mp3")
                    start_print=start2
                else:
                    start_print=start
                if y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    if main_print==main:
                        play_sound(ch + "button.mp3")
                    main_print=main2
                else:
                    main_print=main
                if y>=exit_rect.top and y<=exit_rect.bottom and x>=exit_rect.left and x<=exit_rect.right:
                    if exit_print==exit:
                        play_sound(ch + "button.mp3")
                    exit_print=exit2
                else:
                    exit_print=exit
            if event.type == pg.MOUSEBUTTONDOWN:
                x,y = pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    play_sound(ch + "button05.mp3")
                    pg.mixer.music.stop()
                elif y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    play_sound(ch + "button05.mp3")
                    pg.mixer.music.stop()
                    return 1
                elif y>=exit_rect.top and y<=exit_rect.bottom and x>=exit_rect.left and x<=exit_rect.right:
                    play_sound(ch + "button05.mp3")
                    pg.quit()
                    sys.exit()
        screen.blit(background,back_rect)
        screen.blit(start_print,start_rect)
        screen.blit(main_print,main_rect)
        screen.blit(exit_print,exit_rect)
        screen.blit(scoretext,score_rect)
        screen.blit(numbertext,number_rect)
        pg.display.update()


# 連線時遊戲結束
def link_restart(a,str1):

    main_png=pg.image.load(ch+'MAIN.png')
    main=pg.transform.scale(main_png,(400,200))
    main2_png=pg.image.load(ch+'MAIN2.png')
    main2=pg.transform.scale(main2_png,(400,200))
    main_print=main
    main_rect=main.get_rect()
    main_rect.center=width/4,height/2+150

    exit_png=pg.image.load(ch+'EXIT.png')
    exit=pg.transform.scale(exit_png,(400,200))
    exit2_png=pg.image.load(ch+'EXIT2.png')
    exit2=pg.transform.scale(exit2_png,(400,200))
    exit_print=exit
    exit_rect=exit.get_rect()
    exit_rect.center=width*3/4,height/2+150
    if str1=='LOSE':
        scoretext = font2.render(str1,True,(75,0,130))
    elif str1=='WIN':
        scoretext = font2.render(str1,True,(255,215,0))
    else:
        scoretext = font2.render(str1,True,(255,0,0))
    
    score_rect=scoretext.get_rect()
    score_rect.center=width/2,height/2
    i=0

    while i<256:
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:  
                play_sound(ch + "button05.mp3")
                pg.quit()
                end_message()
                sys.exit()
        scoretext.set_alpha(i)
        time.sleep(0.02953125)
        screen.blit(scoretext,score_rect)
        pg.display.update()
        i+=1    
    
    while a:
        clock.tick(30)
        scoretext = font2.render("是否繼續遊玩",True,(0,255,0))
        score_rect=scoretext.get_rect()
        score_rect.center=width/2,height/4
        #pygame 事件處理
        for event in pg.event.get():
            #正常關閉
            if event.type == pg.QUIT:
                play_sound(ch + "button05.mp3")
                pg.quit()
                end_message()
                sys.exit()
            if event.type==pg.MOUSEMOTION:
                x,y=pg.mouse.get_pos()
                if y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    if main_print==main:
                        play_sound(ch + "button.mp3")
                    main_print=main2
                else:
                    main_print=main
                if y>=exit_rect.top and y<=exit_rect.bottom and x>=exit_rect.left and x<=exit_rect.right:
                    if exit_print==exit:
                        play_sound(ch + "button.mp3")
                    exit_print=exit2
                else:
                    exit_print=exit
            if event.type == pg.MOUSEBUTTONDOWN:
                x,y = pg.mouse.get_pos()

                if y>=main_rect.top and y<=main_rect.bottom and x>=main_rect.left and x<=main_rect.right:
                    play_sound(ch + "button05.mp3")
                    pg.mixer.music.stop()
                    end_message()
                    return 1
                elif y>=exit_rect.top and y<=exit_rect.bottom and x>=exit_rect.left and x<=exit_rect.right:
                    play_sound(ch + "button05.mp3")
                    pg.quit()
                    end_message()
                    sys.exit()
        screen.blit(background,back_rect)
        screen.blit(main_print,main_rect)
        screen.blit(exit_print,exit_rect)
        screen.blit(scoretext,score_rect)
        pg.display.update()




def main_ui():
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
                    if print_pra==pra_p:
                        play_sound(ch + "button.mp3")
                    print_pra=pra_p2
                else:
                    print_pra=pra_p
                if y>=start2_rect.top and y<=start2_rect.bottom and x>=start2_rect.left and x<=start2_rect.right:
                    if print_game==game_p:
                        play_sound(ch + "button.mp3")
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
send_message_logic=False
stop_t=False
# 執行緒send_message()：取得使用者的x,y座標及是否開火，傳送到Server​
def send_message():
    global life,send_message_logic,stop_t
    while True:
        # 建立Message Request訊息的dict物件
        msgdict = {
            "type": 3,
            "nickname": nickname,
            "Xcoordinate": airplane_rect.centerx,
            "Ycoordinate": airplane_rect.centery,
            "life":life
        }
        # 轉成JSON字串，再轉成bytes
        msgdata = json.dumps(msgdict).encode('utf-8')
        print(msgdata)
        # print(msgdata)
        # 將Enter Request送到Server
        sock.sendto(msgdata, server_addr)
        if stop_t:
            break
    print('send_message已關閉')
win=False

# 執行緒recv_message()：接收來自Server傳來的訊息，
# 依據訊息中的type欄位所代表的訊息型態作對應的處理    
recv_message_logic=False
def recv_message():
    global is_entered,enbul_num,enairplane_rect,enbul_rect,win,enlife,enter,recv_message_logic,stop_t,win,life,enlife
    print('執行緒recv_message開始')
    while True:
        
        # 接收來自Server傳來的訊息
        try:
            data, address = sock.recvfrom(MAX_BYTES)
        except ConnectionResetError:
            is_entered = True
            enter=True
        msgdict = json.loads(data.decode('utf-8'))
        # 依照type欄位的值做對應的動作
        # 接收來自Ser
        if msgdict['type']==7:
            play_sound(ch + "attack1.mp3")
            enbul_num=(enbul_num+1)%10
            enbul_rect[enbul_num].center=width-msgdict['Xcoordinate'],height-msgdict['Ycoordinate']
        elif msgdict['type'] == 5:
            enlife=msgdict['life']
            enairplane_rect.center=width-msgdict['Xcoordinate'],height-msgdict['Ycoordinate']
        elif msgdict['type'] == 2:
            is_entered = True
        
        ## Message Response(4)：這是之前Message Request的回應訊息
        # elif msgdict['type'] == 4:
        #     # 不需做任何處理
        #     print('Get Message Response from server.') # 除錯用
        #     pass 
        ## Message Transfer(5)：這是其他Client所發布的訊息
        elif msgdict['type']==9:
            win=True
        if stop_t or win or life==0 :
            break
        
    print('recv_message已關閉')


def end_message():
    global end,stop_t,thread_recv_message,thread_send_message
    stop_t=True
    if end:
        thread_recv_message.join()
        thread_send_message.join()
        end=False
    


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
        life=20
        bnbnoin=True
        boss_bnbnoin=[True,True,True,True,True,True,True,True,True,True]
        bnbspeed=[0,0]
        debomb_num=100
        mo=[-2,2]
        number=0
        eneSpeed=mo[random.randint(0,1)]
        logic_x,logic_dex,logic_y,logic_dey=false,false,false,false
        

        for i in range(10):
            bul_rect[i].center=width,height
            enbul_rect[i].center=-1,-1
        bul_num=-1
        enbul_num=-1
        operation=True#game start
        fps=60
        while operation:
            if not pg.mixer.music.get_busy():
                    pg.mixer.music.load(ch+'CleytonRX - Battle RPG Theme.mp3')
                    pg.mixer.music.play(-1)
            clock.tick(fps)#fps
            lifetext=font.render(f"life:{life}",True,(0,0,0))
            life_rect=lifetext.get_rect()
            life_rect.top=airplane_rect.bottom
            life_rect.centerx=airplane_rect.centerx

            #偵測使用者觸發的事件
            for event in pg.event.get():
                if event.type==pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type==COUNT:
                    fps+=1
                    number+=1
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

            for j in range(10):
                logic=random.randint(0,50)
                if logic==1:#敵人子彈發射
                    bossbul_num[j]=(enbul_num+1)%5
                    if bossbul_rect[j][bossbul_num[j]].centerx==-1:
                        play_sound(ch + "attack1.mp3")
                        bossbul_rect[j][bossbul_num[j]].center=bossairplane_rect[j].center
                for i in range(10):
                    bossbul_rect[j][i]=bossbul_rect[j][i].move(0,speed[3])#子彈移動
                    if bossbul_rect[j][i].top>=height:#是否到達視窗底部
                        bossbul_rect[j][i].center=-1,-1
                if bul_rect[j].centerx!=width:#是否是射出的子彈
                    bul_rect[j]=bul_rect[j].move(0,speed[2])
                if bul_rect[j].top<=0:#將子彈重置
                    bul_rect[j].center=width,height



            
            #碰撞判定
            for i in range(5):
                for j in range(10):
                    for k in range(10):
                        if rebound0(bul_rect[i].top,bul_rect[i].bottom,bul_rect[i].left,bul_rect[i].right,bossbul_rect[j][k].top,bossbul_rect[j][k].bottom,bossbul_rect[j][k].left,bossbul_rect[j][k].right):
                            play_sound(ch + "bomb.mp3")
                            bul_rect[i].center=width,height
                            bossbul_rect[j][k].center=-1,-1
                        
                        if rebound0(bul_rect[i].top,bul_rect[i].bottom,bul_rect[i].left,bul_rect[i].right,bossairplane_rect[j].top,bossairplane_rect[j].bottom,bossairplane_rect[j].left,bossairplane_rect[j].right): 
                            play_sound(ch + "damage1.mp3")
                            number+=1
                            boss_bombold_num[j]=30
                            boss_bombold_rect[j].center=bossairplane_rect[j].center
                            bossSpeed[j]=mo[random.randint(0,1)]
                            bossairplane_rect[j].bottomleft=random.randint(enairplane_rect.width,width-enairplane_rect.width),80
                            bul_rect[i].center=width,height
            for i in range(10):
                for j in range(10):
                    if rebound0(airplane_rect.top,airplane_rect.bottom,airplane_rect.left,airplane_rect.right,bossbul_rect[i][j].top,bossbul_rect[i][j].bottom,bossbul_rect[i][j].left,bossbul_rect[i][j].right):
                            if bossbul_rect[i][j].centerx>0:
                                play_sound(ch + "burst01.mp3")
                                bossbul_rect[i][j].center=-1,-1
                                life-=1
            
            if life <=0:
                pg.mixer.music.stop()
                game_over()
                a=True
                control_choose=restart_game(a)
                life=20
                score=0
                fps=60
                if control_choose==1: 
                    par=False
                    break
                

            #敵機左右移動
            for i in range(10):
                bossairplane_rect[i]=bossairplane_rect[i].move(bossSpeed[i],0)
                if bossairplane_rect[i].centerx>=pause_rect.centerx:
                    bossairplane_rect[i].centerx=pause_rect.centerx
                    bossSpeed[i]=-2
                elif bossairplane_rect[i].left<=0:
                    bossairplane_rect[i].left=1
                    bossSpeed[i]=2
            #圖片更新
            screen.blit(background,back_rect)
            for i in range(10):
                if bul_rect[i].centerx>=0:
                    screen.blit(bul[i],bul_rect[i])
                if boss_bombold_num[i]>0:
                    screen.blit(bombold,boss_bombold_rect[i])
                    boss_bombold_num[i]-=1
                screen.blit(bossairplane[i],bossairplane_rect[i])
                for j in range(10):
                    if bossbul_rect[i][j].centerx>=0:
                        screen.blit(bossbul[i][j],bossbul_rect[i][j])

            screen.blit(airplane,airplane_rect)
            screen.blit(lifetext,life_rect)
            screen.blit(pausebtn,pause_rect)
            pg.display.update()

                
            
    restart=True
    while game_start: 
        #字串字體和大小
        font=pg.font.SysFont("微軟正黑體",36)
        font2 = pg.font.SysFont("Microsoft Jhenghei",60)
        #倒數計時
        COUNT=pg.USEREVENT+1
        pg.time.set_timer(COUNT,1000)
        runtime=60
        enlife=0
        life=30
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
        yn_onfire=False
        win=False
        end=False
        
        if restart:
            restart=False
            stop_t=False
            # 建立一個UDP socket
            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            while True:
                if not pg.mixer.music.get_busy():
                    pg.mixer.music.load(ch+'For the king.ogg')
                    pg.mixer.music.play(-1)
                server_addr = (ui('input server address'),6000)
                nickname=ui('Input your name')
                pg.mixer.music.stop()
                
                # 準備Enter Request訊息的dict物件
                msgdict = {
                    "type": 1,
                    "nickname": nickname
                }
                data = json.dumps(msgdict).encode('utf-8')
                try:
                    sock.sendto(data, server_addr)
                except Exception as e:
                    addres_error()
                    continue
                break
                
            for event in pg.event.get():
                    if event.type==pg.QUIT :
                        pg.quit()
                        sys.exit()
            screen.blit(background,back_rect)
            pg.display.update()
            # 等待並接收Server傳回來的訊息，若為Enter Response則繼續下一步，否則繼續等待
            is_entered = False
            enter=False
            # 建立threads：send_message與recv_message
            thread_send_message = threading.Thread(target=send_message)
            thread_recv_message = threading.Thread(target=recv_message)
            thread_recv_message.start()
            
            
            
        is_entered = False
        enter=False
        standby()#等待連線
        if enter:
            game_start=False
            addres_error()
            thread_recv_message.join()
            continue

        
        
        thread_send_message.start()
  
        

        while operation:
            if not pg.mixer.music.get_busy():
                    pg.mixer.music.load(ch+'Endless Pain of Nightmares.WAV')
                    pg.mixer.music.play(-1)
            clock.tick(60)#fps

            lifetext=font.render(f"life:{life}",True,(0,0,0))
            life_rect=lifetext.get_rect()
            life_rect.top=airplane_rect.bottom
            life_rect.centerx=airplane_rect.centerx
            enlifetext=font.render(f"life:{enlife}",True,(0,0,0))
            enlife_rect=enlifetext.get_rect()
            enlife_rect.top=enairplane_rect.bottom
            enlife_rect.centerx=enairplane_rect.centerx
            #偵測使用者觸發的事件
            for event in pg.event.get():
                if event.type==COUNT:#每秒會接收到
                    runtime-=1
                if event.type==pg.QUIT :#退出
                    life=0
                if event.type==pg.MOUSEMOTION:#讀取滑鼠座標
                    x,y=pg.mouse.get_pos()
                    if y<450:
                        y=450
                    elif y>600:
                        y=600
                    airplane_rect.center=x,y
                    if airplane_rect.left<0:
                        airplane_rect.left=0
                    
                if event.type==pg.KEYDOWN :#讀取按鍵事件
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
                            msgdict = {
                            "type": 6,
                            "nickname": nickname,
                            "Xcoordinate": airplane_rect.centerx,
                            "Ycoordinate": airplane_rect.centery,
                            }
                            # 轉成JSON字串，再轉成bytes
                            msgdata = json.dumps(msgdict).encode('utf-8')
                            # 將Enter Request送到Server
                            sock.sendto(msgdata, server_addr)
                        else:
                            bul_num=bul_num_after
                if event.type==pg.KEYUP:#讀取按鍵放下事件
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
                    #我方子彈發射
                    bul_num_after=bul_num
                    bul_num=(bul_num+1)%5
                    if bul_rect[bul_num].centerx==width:#判斷子彈是否能發射
                        play_sound(ch + "attack1.mp3")
                        bul_rect[bul_num].center=airplane_rect.center
                        msgdict = {
                            "type": 6,
                            "nickname": nickname,
                            "Xcoordinate": airplane_rect.centerx,
                            "Ycoordinate": airplane_rect.centery,
                            }
                        # 轉成JSON字串，再轉成bytes
                        msgdata = json.dumps(msgdict).encode('utf-8')
                        # 將Enter Request送到Server
                        sock.sendto(msgdata, server_addr)
                    else:
                        bul_num=bul_num_after
            vector(airplane_rect,logic_dex,logic_x,logic_dey,logic_y)

            for i in range(10):
                enbul_rect[i]=enbul_rect[i].move(0,speed[3])#子彈移動
                if enbul_rect[i].top>=height:#是否到達視窗底部
                    enbul_rect[i].center=-1,-1
                if bul_rect[i].centerx!=width:#是否是射出的子彈
                    bul_rect[i]=bul_rect[i].move(0,speed[2])
                if bul_rect[i].top<=0:#將子彈重置
                    bul_rect[i].center=width,height
                #碰撞判定
                if rebound0(airplane_rect.top,airplane_rect.bottom,airplane_rect.left,airplane_rect.right,enbul_rect[i].top,enbul_rect[i].bottom,enbul_rect[i].left,enbul_rect[i].right):
                    if enbul_rect[i].centerx>0:
                        play_sound(ch + "burst01.mp3")
                        enbul_rect[i].center=-1,-1
                        life-=1



            #碰撞判定
            for i in range(5):
                
                if rebound0(bul_rect[i].top,bul_rect[i].bottom,bul_rect[i].left,bul_rect[i].right,enairplane_rect.top,enairplane_rect.bottom,enairplane_rect.left,enairplane_rect.right): 
                    bnbnoin=True
                    debomb_num=0
                    bombold_rect.center=enairplane_rect.center
                    bul_rect[i].center=width,height
                if  bnbnoin:
                    bnbspeed[1]=random.randint(2,5)
                    bnbnoin=False
                for j in range(10):
                    if rebound0(bul_rect[i].top,bul_rect[i].bottom,bul_rect[i].left,bul_rect[i].right,enbul_rect[j].top,enbul_rect[j].bottom,enbul_rect[j].left,enbul_rect[j].right):
                        play_sound(ch + "bomb.mp3")
                        bul_rect[i].center=width,height
                        enbul_rect[j].center=-1,-1


            if win or enlife==0:#win
                life=10
                score=0
                pg.mixer.music.stop()
                if not pg.mixer.music.get_busy():
                    pg.mixer.music.load(ch+'Middle_age_RPG_Theme_1.ogg')
                    pg.mixer.music.play(-1)
                control_choose=link_restart(True,'WIN')
                pg.mixer.music.stop()
                if control_choose==1: 
                    game_start=False
                    end_message()
                break
            
            elif life <=0:#lose
                pg.mixer.music.stop()
                if not pg.mixer.music.get_busy():
                    pg.mixer.music.load(ch+'Game Over.ogg')
                    pg.mixer.music.play(-1)
                msgdict = {
                "type": 8,
                "nickname": nickname,
                }
                # 轉成JSON字串，再轉成bytes
                msgdata = json.dumps(msgdict).encode('utf-8')
                # 將Enter Request送到Server
                sock.sendto(msgdata, server_addr)
                control_choose=link_restart(True,'LOSE')
                pg.mixer.music.stop()
                life=30
                score=0
                if control_choose==1: 
                    game_start=False
                break
    
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
                if enbul_rect[i+5].centerx>=0:
                    screen.blit(enbul[i+5],enbul_rect[i+5])
            screen.blit(airplane,airplane_rect)
            screen.blit(lifetext,life_rect)
            screen.blit(enlifetext,enlife_rect)
            pg.display.update()
        

