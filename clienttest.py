from matplotlib.pyplot import text
import pygame
import os
import threading
import socket
import json

ch='TCPIP_project/picture/'
width = 1280
height = 720
pygame.init()
pygame.display.set_caption("飛機遊戲")
os.environ['SDL_VIDEO_WINDOW_POS']="%d,%d"%(0,32)#視窗
screen = pygame.display.set_mode((width, height))
ui_background_jpg=pygame.image.load(ch+'ui.png')
ui_background=pygame.transform.scale(ui_background_jpg,(width,height))
ui_back_rect=ui_background.get_rect()
ui_input='input server address'
MAX_BYTES = 65535
def ui():
    # Settings
    color_background = (0, 0, 0)
    color_inactive = (0, 0, 255)
    color_active = (0, 200, 255)
    color = color_inactive
    text = ""
    active = False
    running = True

    # Font
    font = pygame.font.SysFont("微軟正黑體",50)

    # Input box
    input_box = pygame.Rect(100, 100, 140, 32)
    ui_addr='Input server address'
    # Run
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True  
                else: 
                    active=False

                if active:
                    color=color_active  
                else: 
                    color=color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
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
        pygame.draw.rect(screen, color, input_box, 3)
        pygame.display.flip()

server_addr = (ui(),6000)
print(server_addr)
ui_input='Input your name'
nickname=ui()
# 建立一個UDP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# 準備Enter Request訊息的dict物件
msgdict = {
    "type": 1,
    "nickname": nickname
}
data = json.dumps(msgdict).encode('utf-8')
sock.sendto(data, server_addr)


# 等待並接收Server傳回來的訊息，若為Enter Response則繼續下一步，否則繼續等待
is_entered = False
while not is_entered:
    data, address = sock.recvfrom(MAX_BYTES)
    msgdict = json.loads(data.decode('utf-8'))
    if msgdict['type'] == 2:
        is_entered = True
        screen.blit('成功進入伺服器!!!', (width/2,height/2))

print('程式結束')


