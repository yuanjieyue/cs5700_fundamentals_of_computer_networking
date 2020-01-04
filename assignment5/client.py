# Client
# Author: Yuanjie Yuanjie
# Date: 11/20/19

import socket
import struct
import config
import util
import sys
import snake
import pygame

args_len = len(sys.argv) - 1
if args_len != 4:
    print('Wrong number of parameters!')
else:   
    create_or_join = sys.argv[1]
    game_id = sys.argv[2]
    nick_name = sys.argv[3]
    port_number = int(sys.argv[4])
    print(create_or_join, game_id, nick_name, port_number)

msg = b''
if create_or_join == 'create':
    msg = util.generate_create_or_join_msg(config.CREATE_GAME_MSG, game_id, nick_name, port_number)
elif create_or_join == 'join':
    msg = util.generate_create_or_join_msg(config.JOIN_GAME_MSG, game_id, nick_name, port_number)
# create a udp socket
try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print("Oops, something went wrong connecting the socket")
    exit()

udp_host = config.UDP_IP
udp_port = config.UDP_PORT
print('host', udp_host, 'port', udp_port)
print('UDP client send:', msg)
util.udp_write_data(udp_socket, msg, (udp_host, udp_port))

clock = pygame.time.Clock()
FPS = 10  # frames-per-second
game = None
while True:
    # keep trying to recv msg from the server
    try:
        recv_msg, addr = util.udp_read_data(udp_socket)  
    except socket.error:
        print("Error! {}".format(socket.error))
        exit()

    if recv_msg: 
        # print('UDP client recv', recv_msg, 'from', addr)
        msg_type = struct.unpack_from('!B', recv_msg, 0)[0]
        print('msg type is', msg_type)
     
        # 1. Wait for 2nd player msg
        if msg_type == config.WAIT_2ND_USER_MSG:
            # create new snake game and display 'wait for opponent' msg
            print('Init game')
            pygame.init()
            game = snake.SnakeApp()
            game._draw_msg('Wait for opponent')
        # 2. Wait game start msg
        elif msg_type == config.WAIT_GAME_START_MSG:
            # Optional: create new snake game if current client is 'join'
            # update game status to be 'Ready'
            if create_or_join == 'join':
                print('Init game')
                pygame.init()
                game = snake.SnakeApp()
            game._update_game_status(config.READY)
        # 3. Game over msg
        elif msg_type == config.GAME_OVER_MSG:
            print('Game over')
            msg_type, result, winner_name = util.read_game_over_msg(recv_msg)
            game._update_game_status(config.OVER)
            # check up if it's a tie or get the winner name.
            result_msg = 'GAME OVER! '
            if result == config.TIE:
                result_msg += 'It is a tie'
            else: 
                result_msg += 'Winner is '
                result_msg += winner_name
            game._draw_msg(result_msg)
        # 4. Game info msg
        elif msg_type == config.GAME_INFO_MSG and game.game_status != config.OVER:
            print('game running...')
            msg_type, seq_num, apple_row, apple_col, a_snake, b_snake = util.read_game_info_msg(recv_msg)
            a_snake_pos = util.parse_snake_pos(a_snake)
            b_snake_pos = util.parse_snake_pos(b_snake)
            print('--> a snake positions: ', a_snake_pos)
            print('--> b snake positions: ', b_snake_pos)
            print('--> apple positions: ', apple_col, apple_row)
            game._update_game_status(config.START)
            if create_or_join == 'create':
                game._update_snakes_and_apple(a_snake_pos, b_snake_pos, (apple_col, apple_row))
            else:
                game._update_snakes_and_apple(b_snake_pos, a_snake_pos, (apple_col, apple_row))
            
            # get change direction movement 
            print('Get key movement')      
            keys = pygame.key.get_pressed()
            direction = 0
            if keys[pygame.K_RIGHT]: 
                print('RIGHT pressed!')
                direction = config.RIGHT
            if keys[pygame.K_LEFT]: 
                print('LEFT pressed!')
                direction = config.LEFT
            if keys[pygame.K_UP]: 
                print('UP pressed!')
                direction = config.UP
            if keys[pygame.K_DOWN]:
                print('DOWN pressed!') 
                direction = config.DOWN
            if direction:
                send_msg = util.generate_change_dir_msg(config.CHANGE_DIR_MSG, game_id, nick_name, direction)
                print('UDP client send:', send_msg)
                util.udp_write_data(udp_socket, send_msg, addr)
            else:
                print('No key pressed!')
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()   
    game.run_once()
udp_socket.close()