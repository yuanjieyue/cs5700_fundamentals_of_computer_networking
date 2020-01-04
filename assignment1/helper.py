# a helper module that defines the function of parse and format.
# Auther: Yuanjie Yuanjie
# Date: 09/25/19

import struct

def parse(data):
    '''
    Parse the bytes data into a list of expressions strings, using Big Endian.
    Params:
    data (bytes) : the data in bytes.
    Return: 
    (list): expressions in string format as a list.
    '''
    expressions = []
    offset = 0
    # get first 2 bytes
    expressionsNum = int(struct.unpack_from('!h', data, offset)[0])
    offset += 2
    for i in range(expressionsNum):
        # read next 2 bytes and get current expression length
        curr_expression_len = int(struct.unpack_from('!h', data, offset)[0])
        offset += 2
        # read the next length of bytes
        curr_expression = struct.unpack_from('!' + str(curr_expression_len) + 's', data, offset)[0]
        offset += curr_expression_len
        expressions.append(curr_expression.decode('utf8'))
    # return the result
    return expressions

def format(messages):
    ''' 
    Format a message by packing all the messages in the given list into bytes,
    using Big Endian.
    Params:
    evaluatioins (list) : a list of messages as strings
    Return:
    (str) : a better formatted message as bytes.
    '''
    messages_len = len(messages)
    offset = 0
    result_len = 2 + messages_len * 2 + bytes_list_length(messages)
    result = bytearray(result_len)
    # pack the num of evaluations into the response
    struct.pack_into('!h', result, offset, messages_len)
    offset += 2
    for message in messages:
        curr_message_len = len(message)
        # pack the current evaluation length into the response
        struct.pack_into('!h', result, offset, curr_message_len)
        offset += 2
        struct.pack_into('!' + str(curr_message_len) + 's', result, offset, message)
        offset += curr_message_len
    return result

def bytes_list_length(bytes_list):
    '''
    Get the total byte length of the given list of bytes.
    Params:
    bytes_list (list) : a list of bytes
    Return:
    (int) : the total length
    '''
    res = 0
    for item in bytes_list:
        res += len(item)
    return res
