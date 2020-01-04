# Client
# Auther: Yuanjie Yuanjie
# Date: 09/25/19

import socket
import time
import helper

server_name = socket.getfqdn() 
print('Hostname: ', server_name) 
server_port = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((server_name, server_port)) 
print('Connected to server ', server_name)

# get the request from user inputs      
messages = []
expressionsNum = int(input('How many expressions would you like to calculate? '))
for i in range(expressionsNum):
    currentExpression = input('Type in an expression: ')
    # convert the string to bytes
    messages.append(currentExpression.encode('utf8'))

# format the messages and make it follow the Request Format
request = helper.format(messages)
print('Client sent request:', request)
s.sendall(request) 

# read response from server
bufsize = 16
data = b''
while True:
    curr_data = s.recv(bufsize)
    data = data + curr_data
    if len(curr_data) < bufsize: 
        break
# parse the received messages with the Response Format
print('Client received response: ', data)
response = helper.parse(data)
print('Parsed results are: ', response)

# Close socket to send EOF to server. 
s.close()
