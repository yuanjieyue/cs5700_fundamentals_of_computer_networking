# Utils
# Author: Yuanjie Yue
# Date: 10/16/2019

from datetime import datetime
import config
import socket
import struct

MAX_BUFF_SIZE = 16

def now():
    '''
    Return the datetime object represent the current date and time.
    '''
    return datetime.now()

def get_time():
    '''
    Get the current time in a better format.
    Return
    (str): the current time
    '''
    return now().strftime("%d/%m/%Y %H:%M:%S")

def io_read_n_bytes(io, n):
    '''
    Read n bytes of data from io stream 
    Param
    io: the io stream
    n: number of bytes to read
    Return
    (bytes) the bytes data
    '''
    data = bytearray()
    while len(data) < n:
        remain_len = n - len(data)
        buff_size = min(MAX_BUFF_SIZE, remain_len)
        data += io.read(buff_size)
    return bytes(data)

def socket_read_n_bytes(conn, n):
    '''
    Read n bytes of data from socket
    Param
    conn: the socket
    n: number of bytes to read
    Return
    (bytes) the bytes data
    '''
    data = bytearray()
    while len(data) < n:
        remain_len = n - len(data)
        buff_size = min(MAX_BUFF_SIZE, remain_len)
        data += conn.recv(buff_size)
    return bytes(data)

def get_evaluation(expression):
    '''
    Evaluate the given expression
    Param
    expression: math expression
    Return
    (str): evaluation result
    '''
    if not expression:
        return ''
    items = list(expression.strip())
    i, nums = 0, len(items)
    val, sign, curr_val = 0, 1, 0
    while i < nums:
        curr = items[i]
        if not curr.isdigit() and curr not in '+-':
            return ''
        if curr.isdigit():
            curr_val = curr_val * 10 + int(curr)
        if curr in '+-' or i == nums - 1:
            val += sign * curr_val
            sign = 1 if curr == '+' else -1
            curr_val = 0
        i += 1
    return str(val)

def connect_server(server, port, req):
    '''
    Connect to the server at given port
    Param
    server: server name
    port: port number
    req: req to be evaluated
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = socket.gethostbyname(server)
    s.connect((server_ip, port))
    print('client send:', req)
    write_expression(s, req)
    result = read_expression(s)
    print('client recv:', result)
    return result

def read_expression(conn):
    '''
    Read expression from socket connection
    Param
    conn: socket 
    Return:
    (bytes): the expression
    '''
    l = struct.unpack('!h', socket_read_n_bytes(conn, 2))[0]
    return socket_read_n_bytes(conn, l)

def write_expression(conn, expr):
    '''
    Write expression to socket connection
    Param
    conn: socket 
    expr: expr to write to the socket
    '''
    conn.sendall(struct.pack('!h', len(expr)))
    conn.sendall(expr)

def update_api_count(cache, key):
    '''
    Update the api count of the server.
    Param
    cache: memory cache
    api: the api to be updated
    '''
    val = cache.get(key, default=b'').decode()
    if val:
        val += ',' 
    val += get_time()
    cache.set(key, val)

def update_last_ten_expressions(cache, key, expr):
    '''
    Update the last ten expressions.
    Param
    cache: memory cache
    key: the key of the last ten expressions
    expr: the latest expr
    '''
    val = cache.get(key, default=b'').decode()
    if not val:
        val += expr
    else: 
        exprs = val.split(',')
        exprs.append(expr)
        if len(exprs) > 10:
            exprs.pop(0)
        val = ','.join(exprs)
    cache.set(key, val)

def get_status(cache):
    '''
    Get the status of the http server
    Return
    (str): an html page shows the status of the server
    '''
    status = '<!DOCTYPE html>'
    head = get_head()
    body = get_body(cache)
    status += wrap_with_tag(head + body, 'html')
    return status

def get_head():
    '''
    Get the header for the status html page
    '''
    return wrap_with_tag(wrap_with_tag('HttpServer Status', 'title'), 'head')

def get_body(cache):
    '''
    Get the body for the status html page
    '''
    api_count_info = get_api_count(cache)
    expressions_info = get_last_ten_expressions(cache)
    return wrap_with_tag(api_count_info + expressions_info, 'body')

def get_api_count(cache):
    '''
    Get all the api count info
    Param
    cache: memory cache
    Return
    (str): the api count part of the status html page
    '''
    ans = wrap_with_tag('API count information', 'h1')
    lis = ''
    lis += get_single_api_count(cache, '/api/gettime')
    lis += get_single_api_count(cache, '/api/evalexpression')
    ans += lis
    return ans

def get_single_api_count(cache, api):
    '''
    Get a api count info
    Param
    cache: memory cache
    api: name of api
    Return
    (str): single api info part on the html page
    '''
    ans = wrap_with_tag(api, 'h3')
    curr_time = now()
    val = cache.get(api, default=b'').decode()
    time_tags = []
    if val:
        time_tags = val.split(',')
    nums = get_num(time_tags, curr_time)
    items = ['last minute', 'last hour', 'last 24 hours', 'lifetime']
    lis = ''
    for i in range(len(nums)):
        lis += wrap_with_tag(items[i] + ': ' + str(nums[i]), 'li')  
    ans += wrap_with_tag(lis, 'ul')
    return ans

def get_num(time_tags, curr_time):
    '''
    Get the number of datetimes between each specified duration.
    Param
    time_tags: list of datetime in string format
    curr_time: current datetime
    Return
    (tuple): number for each specified duration 
    '''
    last_min, last_hour, last_24_hours, lifetime = 0, 0, 0, 0
    for time in time_tags:
        time = datetime.strptime(time, '%d/%m/%Y %H:%M:%S')
        duration_in_seconds = (curr_time - time).total_seconds()
        if duration_in_seconds < 60:
            last_min += 1
        if duration_in_seconds < 60 * 60:
            last_hour += 1
        if duration_in_seconds < 24 * 60 * 60:
            last_24_hours += 1
        lifetime += 1
    return (last_min, last_hour, last_24_hours, lifetime)

def get_last_ten_expressions(cache):
    '''
    Get the last ten expressions
    Param:
    cache: the memory cache instance
    Return
    (str): last ten expressions info for the status html page
    '''
    ans = wrap_with_tag('Last 10 expressions', 'h1')
    lis = ''
    val = cache.get('last_ten_exprs', default=b'')
    last_ten_expressions = []
    if val:
        last_ten_expressions = val.decode().split(',')
    for expression in last_ten_expressions[::-1]:
        lis += wrap_with_tag(expression, 'li')
    ans += wrap_with_tag(lis, 'ul')
    return ans

def wrap_with_tag(content, tag):
    '''
    Wrap given content with given tag following html rules
    Param
    content: content to be wrapped
    tag: tag used to wrap the content
    '''
    ans = '<'
    ans += tag
    ans += '>'
    ans += content
    ans += '</'
    ans += tag
    ans += '>'
    return ans






