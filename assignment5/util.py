# Util
# Author: Yuanjie Yuanjie
# Date: 11/20/19
import struct
import config
import random

# Udp socket read data
def udp_read_data(socket):
    return socket.recvfrom(config.MAX_BUFFER_SIZE)

# Udp socket send data to the given addreass
def udp_write_data(socket, data, addr):
    return socket.sendto(data, addr)

# Parse the msg from clients
def parse_client_msg(msg):
    offset = 0
    msg_type = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    len_game_id = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    len_nick_name = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    game_id = msg[offset : offset + len_game_id].decode()
    offset += len_game_id
    nick_name = msg[offset : offset + len_nick_name].decode()
    offset += len_nick_name
    port_or_dir = b''
    if msg_type == config.CREATE_GAME_MSG or msg_type == config.JOIN_GAME_MSG:
        port_or_dir = struct.unpack_from('!h', msg, offset)[0]
    elif msg_type == config.CHANGE_DIR_MSG:
        port_or_dir = int(struct.unpack_from('!B', msg, offset)[0])
    return msg_type, game_id, nick_name, port_or_dir

# Generate random col and row num of a position
def generate_random_pos(width, height):
    col = random.randrange(width)
    row = random.randrange(height)
    return col, row    

# Generate game information msg based on the params provided.
def generate_info_msg(seq_num, a_snake_positions, b_snake_positions, apple_pos):
    msg = bytearray()
    msg += struct.pack('!B', config.GAME_INFO_MSG)
    msg += struct.pack('!B', seq_num)
    msg += struct.pack('!B', apple_pos[1])
    msg += struct.pack('!B', apple_pos[0])
    print('--> apple is: ', 'col -', apple_pos[0], ', row -', apple_pos[1])
    a_snake_binaries = convert_positions_to_binary(a_snake_positions)
    b_snake_binaries = convert_positions_to_binary(b_snake_positions)
    print('--> a snake is:\n')
    print_game_board(a_snake_binaries)
    print('--> b snake is:\n')
    print_game_board(b_snake_binaries)
    a_snake = concate_binaries(a_snake_binaries)
    b_snake = concate_binaries(b_snake_binaries)
    msg += a_snake
    msg += b_snake
    return bytes(msg)

# Convert the tuple positions to an 32 bits integer.
def convert_positions_to_binary(positions):
    binaries = [0 for i in range(config.WIDTH)]
    for col, row in positions:
        bit_mask = 1 << (31 - col)
        binaries[row] = binaries[row] | bit_mask
    return binaries

# Concate the all the numbers in the given binaries as bytes
def concate_binaries(binaries):
    data = bytearray()
    for binary in binaries:
        data += struct.pack('!I', binary)
    return bytes(data)

# Print all the integer in the binaries in binary format. 
def print_game_board(binaries):
    for i in binaries:
        print('{:032b}'.format(i))

# Update the game information based on the params provided.
def update_game_info(game_info, name_dict, game_id, nick_name, direction):
    # get the relative snake, and update the snake according to the direction
    names = name_dict[game_id]
    name_index = 0 if names[0] == nick_name else 1
    current_snake = game_info[name_index]
    opponent_snake = game_info[1 - name_index]
    apple = game_info[2]
    current_snake.direction = direction
    # Move the current snake to the given direction
    game_status = current_snake.move(opponent_snake, apple, direction)
    # Generate random positions for the apple when it is eaten by the current snake.
    if current_snake.head() == game_info[2]:
        while game_info[2] in current_snake.body or game_info[2] in opponent_snake.body:
            game_info[2] = generate_random_pos(config.WIDTH, config.HEIGHT)
    return game_status

# Generate game over msg based on the given game status
def generate_game_over_msg(game_status, names, nick_name):
    # it's a tie or nick name is the loser
    msg = bytearray()
    msg += struct.pack('!B', config.GAME_OVER_MSG)
    winner_name = ''
    if game_status == config.LOSE:
        msg += struct.pack('!B', config.LOSE)
        winner_name = names[1] if names[0] == nick_name else names[0]
        msg += struct.pack('!B', len(winner_name))
    elif game_status == config.TIE:
        msg += struct.pack('!B', config.TIE)
        msg += struct.pack('!B', 0)
    msg += winner_name.encode()
    return bytes(msg)

# Generate the prefix for all client msg 
def generate_client_msg_prefix(type, game_id, nick_name):
    msg = bytearray()
    msg += struct.pack('!B', type)
    msg += struct.pack('!B', len(game_id))
    msg += struct.pack('!B', len(nick_name))
    msg += game_id.encode()
    msg += nick_name.encode()
    return bytes(msg)

# Generate create or join msg of the clients
def generate_create_or_join_msg(type, game_id, nick_name, port_number):
    msg = generate_client_msg_prefix(type, game_id, nick_name)
    msg += struct.pack('!h', port_number)
    return msg

# Generate change direction msg
def generate_change_dir_msg(type, game_id, nick_name, dir):
    msg = generate_client_msg_prefix(type, game_id, nick_name)
    msg += struct.pack('!B', dir)
    return msg

# Read game over msg from the msg sent from the server
def read_game_over_msg(msg):
    offset = 0
    msg_type = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    result = struct.unpack_from('!B', msg, offset)[0]
    offset += 1
    name_len = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    winner_name = msg[offset : offset + name_len].decode()
    return msg_type, result, winner_name

# Read game information msg
def read_game_info_msg(msg):
    offset = 0
    msg_type = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    seq_num = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    apple_row = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    apple_col = int(struct.unpack_from('!B', msg, offset)[0])
    offset += 1
    a_snake, b_snake = [],[]
    for i in range(config.WIDTH):
        bitmap = struct.unpack_from('!I', msg, offset)[0]
        a_snake.append(bitmap)
        offset += 4
    for i in range(config.WIDTH):
        bitmap = struct.unpack_from('!I', msg, offset)[0]
        b_snake.append(bitmap)
        offset += 4
    print('--> a snake is:\n')
    print_game_board(a_snake)
    print('--> b snake is:\n')
    print_game_board(b_snake)
    return msg_type, seq_num, apple_row, apple_col, a_snake, b_snake

# Parse the given integer format of snake into positions
def parse_snake_pos(snake):
    positions = []
    rows = len(snake)
    for r in range(rows):
        row = snake[r]
        # row is an integer, find out all the indices of set bit
        for c in range(32):
            mask = 1 << (31 - c)
            if row & mask:
                pos = (c, r)
                positions.append(pos)
    return positions


