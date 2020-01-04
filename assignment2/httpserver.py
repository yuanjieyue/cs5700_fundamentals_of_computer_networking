# HTTP Server
# Author: Yuanjie Yue
# Date: 10/03/19

import socket
import threading
import utils

# get local hostname and ip address
host_ip = '127.0.0.1'
# host_name = socket.getfqdn()
# host_ip = socket.gethostbyname(host_name)
host_port = 8181
print(f'Host is {host_ip}, Port is {host_port}')

# create a new socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket with host ip and port
s.bind((host_ip, host_port))

# socket keep listening
s.listen() 
print('Server started. Waiting for connection...')

def handler(conn, addr):
    (data, req) = utils.read_data(conn)
    print('Server recv', len(data), 'data from', addr)
    print('Server received: ', data)
    resp = utils.generate_response(req)
    utils.write_data(conn, resp)
    print('Server send: ', resp)
    conn.close() 
    print('Server finished talking with', addr)
    print('----------------------------------------------')

# main thread
while True:
    conn, addr = s.accept()
    print('----------------------------------------------')
    print('Server connected by', addr)
    threading.Thread(target=handler, args=(conn, addr)).start()
