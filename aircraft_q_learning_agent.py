from itertools import count
from tracemalloc import stop
import pygame as pg
import os
import random
from sqlalchemy import false, true
import time
import sys
import pickle

# --- Q-Learning 相關類別與函式 ---
class QLearningAgent:
    def __init__(self, actions):
        self.actions = actions
        self.lr = 0.1        # 學習率
        self.gamma = 0.9     # 折扣因子
        self.epsilon = 0.5   # 初始探索機率 (提高以增加初期嘗試)
        self.epsilon_min = 0.01 # 最小探索機率
        self.epsilon_decay = 0.995 # 衰減率
        self.q_table = {}    # Q-Table

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        # Epsilon-Greedy 策略
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        
        q_values = [self.get_q(state, a) for a in self.actions]
        max_q = max(q_values)
        # 若有多個最大值，隨機選擇其中一個
        best_actions = [self.actions[i] for i, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        q_predict = self.get_q(state, action)
        q_target = reward + self.gamma * max([self.get_q(next_state, a) for a in self.actions])
        self.q_table[(state, action)] = q_predict + self.lr * (q_target - q_predict)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_q_table(self, filename='q_table_v2.pkl'):
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)
        print("Q-Table saved.")

    def load_q_table(self, filename='q_table_v2.pkl'):
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Q-Table loaded. Size: {len(self.q_table)}")

    def debug_q_table(self):
        print("\n=== Q-Table Visualization ===")
        # 整理 Q-Table，將 (state, action) -> value 轉為 state -> {action: value}
        state_actions = {}
        for (state, action), q_val in self.q_table.items():
            if state not in state_actions:
                state_actions[state] = {}
            state_actions[state][action] = q_val

        action_map = {0: "STOP", 1: "LEFT", 2: "RIGHT", 3: "UP", 4: "DOWN", 5: "FIRE"}
        sorted_states = sorted(state_actions.keys())
        
        for state in sorted_states:
            enemy, danger, pos = state
            # 將數字狀態轉為可讀文字
            e_str = ["Align", "Left", "Right"][enemy]
            d_str = ["Safe", "L-Danger", "C-Danger", "R-Danger"][danger]
            p_str = ["Left", "Center", "Right"][pos]
            
            print(f"State [Enemy:{e_str:5} | Danger:{d_str:8} | Pos:{p_str:6}]:")
            best_act = max(state_actions[state], key=state_actions[state].get)
            for action in sorted(state_actions[state].keys()):
                act_name = action_map.get(action, str(action))
                q = state_actions[state][action]
                marker = " <--- BEST" if action == best_act else ""
                print(f"  {act_name:<5}: {q:8.2f}{marker}")
        print("=============================\n")

def get_rl_state(player_rect, enemies_rect, bullets_rect):
    # 將遊戲狀態簡化 (Discretization)
    px, py = player_rect.centerx, player_rect.centery
    
    # 1. 最近敵人的相對位置 (0:無/對齊, 1:左, 2:右)
    nearest_enemy_state = 0
    min_dist = 9999
    target_enemy = None
    
    for en in enemies_rect:
        dist = ((en.centerx - px)**2 + (en.centery - py)**2)**0.5
        if dist < min_dist:
            min_dist = dist
            target_enemy = en
            
    if target_enemy:
        dx = target_enemy.centerx - px
        if abs(dx) < 40: nearest_enemy_state = 0 # 大致對齊
        elif dx < 0: nearest_enemy_state = 1     # 在左邊
        else: nearest_enemy_state = 2            # 在右邊

    # 2. 是否有子彈逼近 (0:安全, 1:左邊有子彈, 2:中間有子彈, 3:右邊有子彈)
    danger_state = 0
    closest_bullet_dist = 9999
    closest_bullet = None

    # 檢查是否有子彈在玩家上方且距離很近
    for row in bullets_rect:
        for b in row:
            if b.centerx != -1: # 子彈存在
                # 偵測範圍：X軸距離 < 60 (稍微比飛機寬度大一點), Y軸距離 < 300 (上方)
                if abs(b.centerx - px) < 60 and 0 < (py - b.centery) < 300:
                    dist = py - b.centery
                    if dist < closest_bullet_dist:
                        closest_bullet_dist = dist
                        closest_bullet = b
    
    if closest_bullet:
        dx = closest_bullet.centerx - px
        if dx < -10:   # 子彈在左側 (需要往右閃)
            danger_state = 1
        elif dx > 10:  # 子彈在右側 (需要往左閃)
            danger_state = 3
        else:          # 子彈在正上方 (需要左右閃)
            danger_state = 2
        
    # 3. 自身位置 (0:左, 1:中, 2:右) - 避免卡牆角
    pos_state = 0
    if px < width / 3: pos_state = 0
    elif px < width * 2 / 3: pos_state = 1
    else: pos_state = 2
    
    return (nearest_enemy_state, danger_state, pos_state)
# -------------------------------

#全域變數
clock=pg.time.Clock()
#子彈移動速度
speed=[random.randint(-5,5),5,-4,3]
deadline=710
id=None
ENEMY_COUNT = 5 # 恢復為 5 架敵機
life=0
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
for i in range(5):
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
for i in range(ENEMY_COUNT):
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
    if object.left < 0:
        object.left = 0
    elif object.right > width:
        object.right = width
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

    #偵測關閉事件
def restart_game(a, ai_mode=False):
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
    ai_timer = 0
    while a:
        if not pg.mixer.music.get_busy():
            pg.mixer.music.load(ch+'lo-fi_fall.mp3')
            pg.mixer.music.play(-1)
        clock.tick(30)
        
        #pygame 事件處理
        if ai_mode:
            ai_timer += 1
            if ai_timer > 30: # 等待約 1 秒後自動點擊 Start
                play_sound(ch + "button05.mp3")
                pg.mixer.music.stop()
                return 0

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
                    return 0
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


def main_ui():
    start_png=pg.image.load(ch+'START.png')
    start=pg.transform.scale(start_png,(400,200))
    start_rect=start.get_rect()
    start_rect.center=width/2,height/2+150
    
    pra_png=pg.image.load(ch+'practise.png')
    pra_p=pg.transform.scale(pra_png,(400,200))
    pra_png2=pg.image.load(ch+'practise2.png')
    pra_p2=pg.transform.scale(pra_png2,(400,200))
    print_pra=pra_p

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
            if event.type==pg.MOUSEMOTION:
                x,y=pg.mouse.get_pos()
                if y>=start_rect.top and y<=start_rect.bottom and x>=start_rect.left and x<=start_rect.right:
                    if print_pra==pra_p:
                        play_sound(ch + "button.mp3")
                    print_pra=pra_p2
                else:
                    print_pra=pra_p

        # Updates
        screen.blit(change_background,change_back_rect)
        screen.blit(totaltext, total_rect)
        screen.blit(print_pra, start_rect)
        pg.display.flip()
par=False
while True:
    switch=main_ui()
    if switch==2:
        par=True

    # 初始化 RL Agent (移到迴圈外，確保 Q-Table 在重置遊戲後能保留)
    rl_agent = QLearningAgent(actions=[0, 1, 2, 3, 4, 5])
    rl_agent.load_q_table() # 嘗試讀取已存在的 Q-Table
    episode_count = 0
    score_history = [] # 用來記錄最近的分數

    try:
        while par: 
            episode_count += 1
            
            #字串字體和大小
            font=pg.font.SysFont("微軟正黑體",36)
            font2 = pg.font.SysFont("Microsoft Jhenghei",60)
            #倒數計時
            COUNT=pg.USEREVENT+1
            pg.time.set_timer(COUNT,1000)
            runtime=60
            life=3 # 降低血量，讓死亡懲罰來得更快，強迫 AI 學會閃躲
            bnbnoin=True
            boss_bnbnoin=[True,True,True,True,True,True,True,True,True,True]
            bnbspeed=[0,0]
            debomb_num=100
            mo=[-2,2]
            number=0
            eneSpeed=mo[random.randint(0,1)]
            logic_x,logic_dex,logic_y,logic_dey=false,false,false,false
            

            for i in range(5):
                bul_rect[i].center=width,height
                enbul_rect[i].center=-1,-1
            bul_num=-1
            enbul_num=-1
            operation=True#game start
            fps=60

            prev_life = life
            prev_score = number
            current_state = get_rl_state(airplane_rect, bossairplane_rect, bossbul_rect)
            shoot_delay = 0
            
            # 初始化 Frame Skipping 變數
            action = rl_agent.choose_action(current_state) # 先決定第一個動作
            accumulated_reward = 0 # 累積這幾幀的獎勵
            frame_counter = 0      # 計數器

            while operation:
                if not pg.mixer.music.get_busy():
                        pg.mixer.music.load(ch+'CleytonRX - Battle RPG Theme.mp3')
                        pg.mixer.music.play(-1)
                clock.tick(fps)#fps
                lifetext=font.render(f"life:{life}",True,(0,0,0))
                life_rect=lifetext.get_rect()
                life_rect.top=airplane_rect.bottom
                life_rect.centerx=airplane_rect.centerx
                
                if shoot_delay > 0:
                    shoot_delay -= 1

                # --- RL Agent 決定動作 (移除原本每幀決策的邏輯) ---
                # action = rl_agent.choose_action(current_state) 
                
                # 重置移動旗標
                logic_dex, logic_x, logic_dey, logic_y = False, False, False, False
                
                if action == 1: logic_dex = True   # 左
                elif action == 2: logic_x = True   # 右
                elif action == 3: logic_dey = True # 上
                elif action == 4: logic_y = True   # 下
                elif action == 5:                  # 射擊
                    if shoot_delay <= 0:
                        bul_num_after=bul_num
                        bul_num=(bul_num+1)%5
                        if bul_rect[bul_num].centerx==width:
                            bul_rect[bul_num].center=airplane_rect.center
                            play_sound(ch + "attack1.mp3")
                            shoot_delay = 40
                        else:
                            bul_num=bul_num_after
                # -----------------------

                #偵測使用者觸發的事件
                for event in pg.event.get():
                    if event.type==pg.QUIT:
                        rl_agent.save_q_table() # 離開前存檔
                        rl_agent.debug_q_table() # 印出學習成果
                        pg.quit()
                        sys.exit()
                    if event.type==COUNT:
                        fps+=1
                        number+=1
                    # 移除滑鼠與鍵盤控制，改由上方 RL Agent 控制
                    # if event.type==pg.MOUSEMOTION: ...
                    # if event.type==pg.KEYDOWN: ...
                    # if event.type==pg.KEYUP: ...
                    
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_p: # 按 P 鍵印出 Q-Table
                            rl_agent.debug_q_table()
                    
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

                vector(airplane_rect,logic_dex,logic_x,logic_dey,logic_y)

                for j in range(ENEMY_COUNT):
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
                    for j in range(ENEMY_COUNT):
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
                for i in range(5):
                    for j in range(ENEMY_COUNT):
                        if rebound0(airplane_rect.top,airplane_rect.bottom,airplane_rect.left,airplane_rect.right,bossbul_rect[i][j].top,bossbul_rect[i][j].bottom,bossbul_rect[i][j].left,bossbul_rect[i][j].right):
                                if bossbul_rect[i][j].centerx>0:
                                    play_sound(ch + "burst01.mp3")
                                    bossbul_rect[i][j].center=-1,-1
                                    life-=5
                
                # --- RL 學習步驟 (Frame Skipping) ---
                reward = 1 # 存活獎勵
                
                if life < prev_life:
                    reward -= 200 # 受傷懲罰 (大幅增加，讓 AI 優先考慮閃躲)
                if number > prev_score:
                    reward += 10 # 提高擊殺獎勵，鼓勵進攻
                
                accumulated_reward += reward
                frame_counter += 1
                
                # 每 4 幀進行一次學習與決策
                if frame_counter % 4 == 0:
                    next_state = get_rl_state(airplane_rect, bossairplane_rect, bossbul_rect)
                    rl_agent.learn(current_state, action, accumulated_reward, next_state)
                    
                    current_state = next_state
                    action = rl_agent.choose_action(current_state)
                    accumulated_reward = 0 # 重置累積獎勵
                
                prev_life = life
                prev_score = number
                # ------------------
                
                if life <=0:
                    pg.mixer.music.stop()
                    rl_agent.save_q_table() # 死亡時存檔
                    rl_agent.decay_epsilon() # 降低探索率
                    
                    # 計算最近 50 場的平均分數
                    score_history.append(number)
                    avg_score = sum(score_history[-50:]) / len(score_history[-50:])
                    print(f"Episode: {episode_count} | Score: {number} | Avg: {avg_score:.1f} | Epsilon: {rl_agent.epsilon:.3f} | Q-Table Size: {len(rl_agent.q_table)}")
                    
                    # 死亡時強制學習最後一次經驗 (避免因為沒滿 4 幀而遺漏死亡懲罰)
                    if frame_counter % 4 != 0:
                        next_state = get_rl_state(airplane_rect, bossairplane_rect, bossbul_rect)
                        rl_agent.learn(current_state, action, accumulated_reward, next_state)

                    game_over()
                    a=True
                    control_choose=restart_game(a, ai_mode=True)
                    if control_choose==1: 
                        par=False
                    break
                    

                #敵機左右移動
                for i in range(ENEMY_COUNT):
                    bossairplane_rect[i]=bossairplane_rect[i].move(bossSpeed[i],0)
                    if bossairplane_rect[i].centerx>=pause_rect.centerx:
                        bossairplane_rect[i].centerx=pause_rect.centerx
                        bossSpeed[i]=-2
                    elif bossairplane_rect[i].left<=0:
                        bossairplane_rect[i].left=1
                        bossSpeed[i]=2
                #圖片更新
                screen.blit(background,back_rect)
                for i in range(ENEMY_COUNT):
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
    except KeyboardInterrupt:
        print("\nTraining interrupted by user (Ctrl+C). Saving Q-Table...")
        rl_agent.save_q_table()
        pg.quit()
        sys.exit()
