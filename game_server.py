from cmath import log
import socket
import threading
import json
import time
MAX_BYTES = 65535
my_port = 6000
client_list = [] # 存放每個Client資訊的清單
def recv_message():
    global client_list
    # 接收來自Client的訊息，取得訊息內容(data)與地址資訊(address)
    data, address = sock.recvfrom(MAX_BYTES)
    text = data.decode('utf-8')
    # print('The client at {} says {!r}'.format(address, text))
    # 將訊息內容由JSON字串轉成dict物件
    message= json.loads(text)
    if message['type'] == 3:
            # 建立一個Message Response (4) 訊息，送回給來源Client
            msgdict = {
                "type": 4
            }
            data = json.dumps(msgdict).encode('utf-8')
            sock.sendto(data, address)
            
            # 建立一個Message Transfer (5)訊息
            msgdict = {
                "type": 5,
                "nickname": message['nickname'], # 來源Client的綽號
                "Xcoordinate": message['Xcoordinate'],    # 來源Client的x座標
                "Ycoordinate": message['Ycoordinate'],    # 來源Client的y座標
                "life":message['life']
            }
            data = json.dumps(msgdict).encode('utf-8')
            # 針對每一個在client_list中的每一個Client，
            # 轉送Message Transfer訊息給他們 (來源Client除外)
                
            for client in client_list:
                if client['address']==address:
                    client['end']=client['start']=time.perf_counter()
                if client['address'] != address:
                    sock.sendto(data, client['address']) 
def outtime():
    if end_time:
        for client in client_list:
            client['end']=time.perf_counter()
            if (client['end']-client['start'])>1:
                msgdict = {
                    "type": 9,
                    "nickname": message['nickname'], # 來源Client的綽號
                }
                data = json.dumps(msgdict).encode('utf-8')
                # 針對每一個在client_list中的每一個Client，
                # 轉送Message Transfer訊息給他們 (來源Client除外)
                for client in client_list:
                    if client['address'] != address:
                        sock.sendto(data, client['address']) 
                    else:
                        client_list.pop(client)

# 創建一個socket，並bind在指定的address
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
thread_outtime = threading.Thread(target=outtime)
# thread_recv_message = threading.Thread(target=recv_message)
sock.bind(('0.0.0.0',my_port))
print('Listening at {}'.format(sock.getsockname()))
people_num=0
while True:
    while True:
        # 接收來自Client的訊息，取得訊息內容(data)與地址資訊(address)
        data, address = sock.recvfrom(MAX_BYTES)
        text = data.decode('utf-8')
        print('The client at {} says {!r}'.format(address, text))
        # 將訊息內容由JSON字串轉成dict物件
        message= json.loads(text)
        if message['type'] == 1:
            # 新建一個Client的dict物件來存放它的資訊
            new_client = {
                'nickname': message['nickname'],
                'address': address,
                'start': time.perf_counter(),
                'end':time.perf_counter()
            }
            print('Enter Request：', new_client) # 除錯用
            # 將新Client的dict物件加入list中
            client_list.append(new_client)
            
        if len(client_list)==2:
            # 送回Request Response訊息
            msgdict = {
                "type": 2
            }
            data = json.dumps(msgdict).encode('utf-8')
            for client in client_list:
                sock.sendto(data, client['address'])
                print('Send back Enter Response to', address) # 除錯用
            break
    req=0
    client_num=len(client_list)
    game_start=True
    end_time=False
    thread_outtime.start()
    # thread_recv_message.start()
    # 處理來自Client訊息的無窮迴圈
    while(game_start):
        
        # 接收來自Client的訊息，取得訊息內容(data)與地址資訊(address)
            
        try:
            data, address = sock.recvfrom(MAX_BYTES)
        except ConnectionResetError:
            msgdict = {
                "type": 9,
                "nickname": message['nickname'], # 來源Client的綽號
            }
            data = json.dumps(msgdict).encode('utf-8')
            # 針對每一個在client_list中的每一個Client，
            # 轉送Message Transfer訊息給他們 (來源Client除外)
            for client in client_list:
                if client['address'] != address:
                    sock.sendto(data, client['address']) 
        text = data.decode('utf-8')
        message= json.loads(text)
        # 依照type欄位的值做對應的動作
        
        ## Message Request (3)：有一個Client送來聊天訊息
        if message['type'] == 3:
            # 建立一個Message Response (4) 訊息，送回給來源Client
            msgdict = {
                "type": 4
            }
            data = json.dumps(msgdict).encode('utf-8')
            sock.sendto(data, address)
            
            # 建立一個Message Transfer (5)訊息
            msgdict = {
                "type": 5,
                "nickname": message['nickname'], # 來源Client的綽號
                "Xcoordinate": message['Xcoordinate'],    # 來源Client的x座標
                "Ycoordinate": message['Ycoordinate'],    # 來源Client的y座標
                "life":message['life']
            }
            data = json.dumps(msgdict).encode('utf-8')
            # 針對每一個在client_list中的每一個Client，
            # 轉送Message Transfer訊息給他們 (來源Client除外)
                
            for client in client_list:
                if client['address']==address:
                    client['end']=client['start']=time.perf_counter()
                if client['address'] != address:
                    sock.sendto(data, client['address']) 
        
        if message['type']==6:
            msgdict = {
                "type": 7,
                "nickname": message['nickname'], # 來源Client的綽號
                "Xcoordinate": message['Xcoordinate'],    # 來源Client的x座標
                "Ycoordinate": message['Ycoordinate'],    # 來源Client的y座標
            }
            data = json.dumps(msgdict).encode('utf-8')
            # 針對每一個在client_list中的每一個Client，
            # 轉送Message Transfer訊息給他們 (來源Client除外)
            for client in client_list:
                if client['address'] != address:
                    sock.sendto(data, client['address']) 
        elif message['type']==8:  #結束
            msgdict = {
                "type": 9,
                "nickname": message['nickname'], # 來源Client的綽號
            }
            data = json.dumps(msgdict).encode('utf-8')
            # 針對每一個在client_list中的每一個Client，
            # 轉送Message Transfer訊息給他們 (來源Client除外)
            for client in client_list:
                if client['address'] != address:
                    sock.sendto(data, client['address']) 
            end_time=True
        elif message['type']==10:#退出
            for client in client_list:
                if client['address'] == address:
                    if not client['re']:
                        client_list.pop(client)
                    req+=1
            if req==client_num:
                break
    thread_outtime.join()
    # thread_recv_message.join()
                

