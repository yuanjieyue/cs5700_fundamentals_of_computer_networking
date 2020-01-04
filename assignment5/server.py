# Server
# Author: Yuanjie Yuanjie
# Date: 11/20/19

import socket
import struct
import time
import snake
import config 
import util

name_dict = {} # key -> game_id, value -> two nick_names
port_dict = {} # key -> game_id, value -> port_number
ip_dict = {} # key -> game_id, value -> two client ip addrs
socket_dict = {} # key -> game_id, value -> socket bind to the (host, port_number)
seq_dict = {} # key -> game_id, value -> seq num
game_info_dict = {} # key -> game_id, value -> game info

# Create the Game Server
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_host = config.UDP_IP
udp_port = config.UDP_PORT
print('host:', udp_host, 'port', udp_port)

# Bind to address and ip
udp_socket.bind((udp_host, udp_port))
print("UDP server starts...")

while True:
    try:
        # get msg sent to server
        msg, addr = util.udp_read_data(udp_socket)
    except socket.timeout:
        # broadcast game_info messages to all their relevant clients connected.
        for game_id, names in name_dict.items():
            # only send msg to those client already paired and are playing the game.
            if len(names) == 2:
                client_socket = socket_dict[game_id]
                game_info = game_info_dict[game_id]
                a_name, b_name = names[0], names[1]
                a_snake, b_snake = game_info[0], game_info[1]

                game_info_msg = b''
                a_snake_game_status = util.update_game_info(game_info, name_dict, game_id, a_name, a_snake.direction)
                if a_snake_game_status == config.TIE or a_snake_game_status == config.LOSE:
                    game_info_msg = util.generate_game_over_msg(a_snake_game_status, names, a_name)
                else: 
                    b_snake_game_status = util.update_game_info(game_info, name_dict, game_id, b_name, b_snake.direction)
                    if b_snake_game_status == config.TIE or b_snake_game_status == config.LOSE:
                        game_info_msg = util.generate_game_over_msg(b_snake_game_status, names, b_name)
                    else:
                        game_info = game_info_dict[game_id]
                        a_snake, b_snake, apple = game_info[0], game_info[1], game_info[2]
                        game_info_msg = util.generate_info_msg(seq_dict[game_id], a_snake.body, b_snake.body, apple)
                for ip in ip_dict[game_id]:
                    udp_addr = (udp_host, ip[1])
                    print('UDP Server send:', game_info_msg, 'to', udp_addr)
                    util.udp_write_data(udp_socket, game_info_msg, udp_addr) 
        continue
    except socket.error:
        print("Error! {}".format(socket.error))
        exit()
    if msg:
        print('UDP server recv', msg, 'from', addr)
        offset = 0
        msg_type = struct.unpack_from('!B', msg, offset)[0]

        # 1. Create game msg
        if msg_type == config.CREATE_GAME_MSG:
            msg_type, game_id, nick_name, port_number = util.parse_client_msg(msg)
            # initialize all the info under provided game id 
            name_dict[game_id] = []
            name_dict[game_id].append(nick_name)
            port_dict[game_id] = port_number
            ip_dict[game_id] = []
            ip_dict[game_id].append(addr)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.bind((udp_host, port_number))
            socket_dict[game_id] = client_socket  
            # broadcast 'Wait for 2nd player msg'
            wait_2nd_user_msg = struct.pack('!B', config.WAIT_2ND_USER_MSG)
            for ip in ip_dict[game_id]:
                udp_addr = (udp_host, ip[1])
                print('UDP Server send', wait_2nd_user_msg, 'to', udp_addr)
                util.udp_write_data(client_socket, wait_2nd_user_msg, udp_addr)
        # 2. Join game msg
        elif msg_type == config.JOIN_GAME_MSG:
            msg_type, game_id, nick_name, port_number = util.parse_client_msg(msg)
            # update the info under game id
            name_dict[game_id].append(nick_name)
            ip_dict[game_id].append(addr)
            client_socket = socket_dict[game_id]
            seq_dict[game_id] = 1
            #  broadcast 'Wait game start msg'
            wait_game_start_msg = struct.pack('!B', config.WAIT_GAME_START_MSG)
            for ip in ip_dict[game_id]:
                udp_addr = (udp_host, ip[1])
                print('UDP Server send', wait_game_start_msg, 'to', udp_addr)
                util.udp_write_data(client_socket, wait_game_start_msg, udp_addr)

            # leave a time window for client to prepare for the game start.
            time.sleep(1)
            # generate initial two snakes and an apple
            a_snake_start_pos = util.generate_random_pos(config.WIDTH, config.HEIGHT)
            b_snake_start_pos = util.generate_random_pos(config.WIDTH, config.HEIGHT)
            while b_snake_start_pos == a_snake_start_pos: 
                b_snake_start_pos = util.generate_random_pos(config.WIDTH, config.HEIGHT)
            apple = util.generate_random_pos(config.WIDTH, config.HEIGHT)
            while apple == a_snake_start_pos or apple == b_snake_start_pos: 
                apple = util.generate_random_pos(config.WIDTH, config.HEIGHT)

            # create two snake instance
            a_snake = snake.Snake(a_snake_start_pos, config.HEIGHT, config.WIDTH)
            b_snake = snake.Snake(b_snake_start_pos, config.HEIGHT, config.WIDTH)
            game_info_dict[game_id] = [a_snake, b_snake, apple]
            # prepare the info message and broadcast the game info msg

            init_game_info_msg = util.generate_info_msg(seq_dict[game_id], a_snake.body, b_snake.body, apple)
            # seq_dict[game_id] += 1
            for ip in ip_dict[game_id]:
                udp_addr = (udp_host, ip[1])
                print('UDP Server send:', init_game_info_msg, 'to', udp_addr)
                util.udp_write_data(client_socket, init_game_info_msg, udp_addr)
                
            # set up the time out for the socket right after game start    
            udp_socket.settimeout(config.SOCKET_TIME_OUT)            
        elif msg_type == config.CHANGE_DIR_MSG:
            msg_type, game_id, nick_name, direction = util.parse_client_msg(msg)
            client_socket = socket_dict[game_id]
            # update the game info by moving the snake to given direction.
            game_status = util.update_game_info(game_info_dict[game_id], name_dict, game_id, nick_name, direction)
            game_info_msg = b''
            # current moving lead to a game over, then either it's a tie of current player lose.
            if game_status == config.LOSE or game_status == config.TIE:
                game_info_msg = util.generate_game_over_msg(game_status, name_dict[game_id], nick_name)
            # game continues
            elif game_status == config.CONTINUE:
                game_info = game_info_dict[game_id]
                a_snake, b_snake, apple = game_info[0], game_info[1], game_info[2]
                game_info_msg = util.generate_info_msg(seq_dict[game_id], a_snake.body, b_snake.body, apple)
                # seq_dict[game_id] += 1
            # broadcast game info msg to clients
            for ip in ip_dict[game_id]:
                udp_addr = (udp_host, ip[1])
                print('UDP Server send:', game_info_msg, 'to', udp_addr)
                util.udp_write_data(udp_socket, game_info_msg, udp_addr)
        # set up a time interval between two msg broadcasting
        time.sleep(config.TIME_INTERVAL)
