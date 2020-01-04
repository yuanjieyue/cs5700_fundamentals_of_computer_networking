# Server
# Auther: Yuanjie Yuanjie
# Date: 09/25/19

import socket
import threading
import time
import helper
import utils

host_name = socket.getfqdn()
print('hostname is', host_name)

host_ip = socket.gethostbyname(host_name)
print('host IP address is', host_ip)

host_port = 8181

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host_ip, host_port))
s.listen()
print('Server started. Waiting for connection...')

def now():
    '''
    Return current time.
    '''
    return time.ctime(time.time())

# set up the buffer size to be 16bytes
bufsize = 16

def handler(conn, addr):
    exprs = utils.read_expressions(conn)
    print('Server received', len(exprs), 'expressions from', addr)
    resp = []
    for expr in exprs:
        print('expression', expr)
        resp.append(str(eval(expr)).encode('utf8'))
    utils.write_expressions(conn, resp)
    conn.close()

def handler1(conn, addr):
    '''
    Handles a client at the given 'addr' with given socket 'conn'
    Params:
    conn (socket) : a socket object
    addr: a ip address
    '''
    data = b''
    while True:
        curr_data = conn.recv(bufsize) 
        data = data + curr_data
        # simulating long running program
        # time.sleep(2)  
        if len(curr_data) < bufsize: 
            break
    print('Server received request:', data, 'from', addr)
    # parse the data from the client as expressions
    expressions = helper.parse(data)
    print('Parsed expressions are: ', expressions)
    # get all the evaluations of the expressions
    evaluations = evaluate_expressions(expressions)
    # format the evaluations following the Response Format
    response = helper.format(evaluations)
    # send the organized the response to the client
    conn.sendall(response)
    print ('Server sent response:', response, 'to', addr)
    conn.close()

def evaluate_expressions(expressions):
    '''
    Evaluate the expressions in the given list.
    Params:
    expressions (list) : a list of expressions string.
    Return:
    (list) : a list of evaluations bytes.
    '''
    return [evaluate_expression(expression).encode('utf8') for expression in expressions]

def evaluate_expression(expression):
    '''
    Evaluate an expression.
    Params:
    expression (str) : an expression that contains '+' '-'
    Return:
    (str) : the evaluation as a string.
    '''
    # return str(eval(expression))
    
    items = list(expression.strip())
    i, nums = 0, len(items)
    val, sign, curr_val = 0, 1, 0
    while i < nums:
        curr = items[i]
        if curr.isdigit():
            curr_val = curr_val * 10 + int(curr)
        if curr in '+-' or i == nums - 1:
            val += sign * curr_val
            sign = 1 if curr == '+' else -1
            curr_val = 0
        i += 1
    return str(val)

# main thread
while True:
    conn, addr = s.accept()
    print('Server connected by', addr, 'at', now())
    threading.Thread(target=handler, args=(conn, addr)).start()

