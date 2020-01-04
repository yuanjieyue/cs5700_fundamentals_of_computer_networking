# Utils
# Author: Yuanjie Yue
# Date: 10/03/2019

import struct
from datetime import datetime
from collections import defaultdict

MAX_BUFF_SIZE = 16

api_count = {}
api_count['/api/evalexpression'] = []
api_count['/api/gettime'] = []
last_ten_expressions = []

def now():
    '''
    Return the datetime object represent the current date and time.
    '''
    return datetime.now()

def read_n_bytes(conn, n):
    data = bytearray()
    while len(data) < n:
        remain_len = n - len(data)
        buff_size = min(MAX_BUFF_SIZE, remain_len)
        data += conn.recv(buff_size)
    return bytes(data)

def read_data(conn):
    '''
    Read bytes from socket and return it as string.
    Param
    conn: socket connection
    Return
    tuple: the read data and request parsed
    '''
    data = b''
    req = {}
    while b'\r\n\r\n' not in data:
        data += read_n_bytes(conn, 1)
    # get rid of the rear '\r\n\r\n'
    http_req_header = data[:-4].decode('utf8').split('\r\n')
    # get the first line
    http_req_line = http_req_header[0]
    http_req_line_parts = http_req_line.split(' ')
    http_req_line_parts_len = len(http_req_line_parts)
    if http_req_line_parts_len > 0 and len(http_req_line_parts[0]) > 0:
        req['Http-Method'] = http_req_line_parts[0]
        print('http method', req['Http-Method'])
    else:
        print('http method not provided!')
    if http_req_line_parts_len > 1 and len(http_req_line_parts[1]) > 0:
        req['Api'] = http_req_line_parts[1]
        print('api', req['Api'])
    else:
        print('api not provided!')
    if http_req_line_parts_len > 2 and len(http_req_line_parts[2]) > 0:
        req['Http-Version'] = http_req_line_parts[2]
        print('http version', req['Http-Version'])
    else:
        print('http version not provided!')

    http_header_lines = http_req_header[1:]
    http_header_lines_parts = dict([i.lower().split(': ') for i in http_header_lines])

    if 'content-length' in http_header_lines_parts:
        content_length = int(http_header_lines_parts['content-length'])
        print('Content-length is', content_length)
        content = read_n_bytes(conn, content_length)
        data += content
        req['Content'] = content.decode('utf8')
        print('Content is', req['Content'])
    return (data, req)

def write_data(conn, resp):
    '''
    Write the bytes data to the socket connection.
    Param
    conn: socket connection
    resp: response message to be sent 
    '''
    conn.sendall(resp)

def generate_response(req):
    '''
    Generate response bytes based on the given request.
    Param
    req: requset string
    Return
    (bytes): the relative response
    '''
    resp = {}
    resp['Status-Code'] = '200 OK'
    if 'Http-Method' not in req:
        resp['Status-Code'] = '405 Method Not Allowed'
    elif 'Api' not in req:
        resp['Status-Code'] = '404 Not Found'
    elif 'Http-Version' not in req or req['Http-Version'] not in ['HTTP/1.0', 'HTTP/1.1']:
        resp['Status-Code'] = '505 HTTP Version Not Supported'
    else:
        resp['Http-Version'] = req['Http-Version']
        resp['Content-Type'] = 'text/html'
        resp['Api'] = req['Api']
        if req['Http-Method'] == 'POST':
            if req['Api'] == '/api/evalexpression':
                evaluation = get_evaluation(req['Content'])
                if len(evaluation) > 0:
                    resp['Content'] = evaluation
                    resp['Content-Length'] = str(len(evaluation))
                    update_last_ten_expressions(req['Content'])
                    update_api_count(req['Api']) 
                else: 
                    resp['Status-Code'] = '400 Bad Request'
            else:
                resp['Status-Code'] = '404 Not Found'
        elif req['Http-Method'] == 'GET':
            if req['Api'] == '/api/gettime':
                curr_time = get_time()
                resp['Content'] = curr_time
                resp['Content-Length'] = str(len(curr_time))
                update_api_count(req['Api']) 
            elif req['Api'] == '/status' or req['Api'] == '/status.html':
                status = get_status()
                resp['Content'] = status
                resp['Content-Length'] = str(len(status))
            else:
                resp['Status-Code'] = '404 Not Found' 
        else:
            resp['Status-Code'] = '404 Not Found'
    return prepare_response(resp)

def prepare_response(resp):
    '''
    Prepare the response bytes based on the response dict
    Param
    resp: infos about the response in dict format
    Return
    (bytes): the http response
    '''
    ans = prepare_header(resp)
    if resp['Status-Code'] == '200 OK': 
        ans += 'Content-Type: text/html'
        ans += '\r\n'
        ans += 'Content-Length: '
        ans += resp['Content-Length']
        ans += '\r\n'
        ans += '\r\n'
        ans += resp['Content']
    else:
        ans += '\r\n'
    return ans.encode('utf8')

def prepare_header(resp):
    '''
    Prepare first line of http response header based on the given response dict.
    Param
    resp: infos about the response in dict format
    Return
    (str): the http response header
    '''
    header = ''
    if 'Http-Version' in resp:
        header += resp['Http-Version']
        header += ' '
    header += resp['Status-Code']
    header += '\r\n'
    return header

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

def get_time():
    '''
    Get the current time in a better format.
    Return
    (str): the current time
    '''
    return now().strftime("%d/%m/%Y %H:%M:%S")

def get_status():
    '''
    Get the status of the http server
    Return
    (str): an html page shows the status of the server
    '''
    status = '<!DOCTYPE html>'
    head = get_head()
    body = get_body()
    status += wrap_with_tag(head + body, 'html')
    return status

def update_last_ten_expressions(expression):
    '''
    Update the last ten expressions.
    Param
    expression: the last ten expressions
    '''
    if expression in last_ten_expressions:
        last_ten_expressions.remove(expression)
    last_ten_expressions.append(expression)
    if len(last_ten_expressions) > 10:
        last_ten_expressions.pop(0)

def update_api_count(api):
    '''
    Update the api count of the server.
    Param
    api: the api to be updated
    '''
    api_count[api].append(now())

def get_api_count(api_count):
    '''
    Get all the api count info
    Param
    api_count: api count info
    Return
    (str): the api count part of the status html page
    '''
    ans = wrap_with_tag('API count information', 'h1')
    lis = ''
    for key, value in api_count.items():
        lis += get_single_api_count(key, value)
    ans += lis
    return ans

def get_single_api_count(api, count):
    '''
    Get a api count info
    Param
    api: name of api
    count: list of datetime objects of the api that was called
    Return
    (str): single api info part on the html page
    '''
    ans = wrap_with_tag(api, 'h3')
    curr_time = now()
    nums = get_num(count, curr_time)
    items = ['last minute', 'last hour', 'last 24 hours', 'lifetime']
    lis = ''
    for i in range(len(nums)):
        lis += wrap_with_tag(items[i] + ': ' + str(nums[i]), 'li')  
    ans += wrap_with_tag(lis, 'ul')
    return ans

def get_num(list_datetime, now):
    '''
    Get the number of datetimes between each specified duration.
    Param
    list_datetime: list of datetime objects
    now: current datetime
    Return
    (tuple): number for each specified duration 
    '''
    last_min, last_hour, last_24_hours, lifetime = 0, 0, 0, 0
    for date in list_datetime:
        duration_in_seconds = (now - date).total_seconds()
        if duration_in_seconds < 60:
            last_min += 1
        if duration_in_seconds < 60 * 60:
            last_hour += 1
        if duration_in_seconds < 24 * 60 * 60:
            last_24_hours += 1
        lifetime += 1
    return (last_min, last_hour, last_24_hours, lifetime)

def get_last_ten_expressions(last_ten_expressions):
    '''
    Get the last ten expressions
    Param:
    last_ten_expressions: last ten expressions http server had evaluated
    Return
    (str): last ten expressions info for the status html page
    '''
    ans = wrap_with_tag('Last 10 expressions', 'h1')
    lis = ''
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

def get_head():
    '''
    Get the header for the status html page
    '''
    return wrap_with_tag(wrap_with_tag('HttpServer Status', 'title'), 'head')

def get_body():
    '''
    Get the body for the status html page
    '''
    api_count_info = get_api_count(api_count)
    expressions_info = get_last_ten_expressions(last_ten_expressions)
    return wrap_with_tag(api_count_info + expressions_info, 'body')


