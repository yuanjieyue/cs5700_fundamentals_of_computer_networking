# Config
# Author: Yuanjie Yuanjie
# Date: 11/20/19

# Local host
UDP_IP = '127.0.0.1'
UDP_PORT = 1234
MAX_BUFFER_SIZE = 1024

# Message Type
CREATE_GAME_MSG = 1
JOIN_GAME_MSG = 2
CHANGE_DIR_MSG = 3

WAIT_2ND_USER_MSG = 4
WAIT_GAME_START_MSG = 5
GAME_OVER_MSG = 6
GAME_INFO_MSG = 7

# Game Window Size
WIDTH = 32
HEIGHT = 32

# Direction
UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4

# Game Status
LOSE = 1
TIE = 2
CONTINUE = 3

# Color
WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
ORANGE = 255, 165, 0

# Snake app status
CREATE = 1
READY = 2
START = 3
OVER = 4

# Udp socket time out
SOCKET_TIME_OUT = 0.13
TIME_INTERVAL = 0.1