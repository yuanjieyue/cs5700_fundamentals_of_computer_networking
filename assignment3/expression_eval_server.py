# Expression Eval Server
# Author: Yuanjie Yue
# Date: 10/16/2019

import socket
import threading
import utils
import config

server_ip = socket.gethostbyname(config.EXPRESSION_EVAL_SERVER)
# create a new socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket with host ip and port
s.bind((server_ip, config.EXPRESSION_EVAL_PORT))

# socket keep listening
s.listen() 
print('Expression_Eval_Server started. Waiting for connection...')

def handler(conn, addr):
    expr = utils.read_expression(conn)
    print('Server recv:', len(expr), 'bytes of data from', addr)
    print('Server recv:', expr)
    resp = utils.get_evaluation(expr.decode()).encode()
    utils.write_expression(conn, resp)
    print('Server send:', resp)
    conn.close() 
    print('Server finished talking with', addr)
    print('----------------------------------------------')

# main thread
while True:
    conn, addr = s.accept()
    print('----------------------------------------------')
    print('Server connected by:', addr)
    threading.Thread(target=handler, args=(conn, addr)).start()







