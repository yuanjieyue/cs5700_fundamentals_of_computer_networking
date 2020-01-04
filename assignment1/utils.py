# a helper module that defines the function of parse and format.
# Auther: Yuanjie Yuanjie
# Date: 09/25/19

import struct

bufsize = 16

def read_n_bytes(conn, n):
    data = bytearray()
    while len(data) < n:
        remain_bytes = n - len(data)
        read_len = min(bufsize, remain_bytes)
        data += conn.recv(read_len)
    return data

def read_expressions(conn):
    exprs = []
    (exprs_num,) = struct.unpack('!h', read_n_bytes(conn, 2))
    for i in range(exprs_num):
        (expr_len,) = struct.unpack('!h', read_n_bytes(conn, 2))
        expr = read_n_bytes(conn, expr_len)
        exprs.append(expr)
    return exprs

def write_expressions(conn, exprs):
    conn.sendall(struct.pack('!h', len(exprs)))
    for expr in exprs:
        conn.sendall(struct.pack('!h', len(expr)))
        conn.sendall(expr)
