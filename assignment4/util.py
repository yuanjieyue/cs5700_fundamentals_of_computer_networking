import dummy
import gbn
import sw
import threading
import struct


def get_transport_layer_by_name(name, local_port, remote_port, msg_handler):
    assert name == 'dummy' or name == 'sw' or name == 'gbn'
    if name == 'dummy':
        return dummy.DummyTransportLayer(local_port, remote_port, msg_handler)
    if name == 'sw':
        return sw.StopAndWait(local_port, remote_port, msg_handler)
    if name == 'gbn':
        return gbn.GoBackN(local_port, remote_port, msg_handler)

def parse_packet(packet): 
    '''
    Parse the given packet
    Param
    packet: a packet following format:
            2 bytes data type + 2 bytes seq num + 2 bytes check sum + payload
    Return
    (tuple): data type, sequence num, check sum and payload
    '''
    data_type = struct.unpack_from('!h', packet, offset=0)[0]
    seq_num = struct.unpack_from('!h', packet, offset=2)[0]
    check_sum = struct.unpack_from('!H', packet, offset=4)[0]
    payload = packet[6:]
    return data_type, seq_num, check_sum, payload

def make_packet(data_type, seq_num, payload):
    '''
    Make a packet with the given data
    Param
    data_type: data type for the packet header, given as int
    seq_num: sequence number for the packet header, given as int
    payload: payload of the packet, given as bytes
    Return
    bytes: a packet following format:
            2 bytes data type + 2 bytes seq num + 2 bytes check sum + payload
    '''
    packet = bytearray(6)
    struct.pack_into('!h', packet, 0, data_type)
    struct.pack_into('!h', packet, 2, seq_num)
    check_sum = calculate_check_sum(data_type, seq_num, payload)
    struct.pack_into('!H', packet, 4, check_sum)
    # deal with scenario that the packet is longer the MAX_MESSAGE_SIZE
    packet = bytes(packet) + payload
    return packet

def calculate_check_sum(data_type, seq_num, payload):
    '''
    Calculate check sum of the given three items
    Param
    data_type: data type given as int
    seq_num: sequence num given as int
    payload: payload given as bytes
    Return
    (int): the check sum 
    '''
    check_sum = ones_comp_add_16bit(data_type, seq_num)
    msg = payload.decode('utf-8', 'ignore')
    for i in range(0, len(msg), 2):
        if i + 1 >= len(msg):
            check_sum = ones_comp_add_16bit(check_sum, ord(msg[i]))
        else:
            partial_check_sum = ord(msg[i]) + (ord(msg[i+1]) << 8)
            check_sum = ones_comp_add_16bit(check_sum, partial_check_sum)
    return ~check_sum & 0xffff

def ones_comp_add_16bit(a,  b):
    ''' 
    A ones composite add for 16 bit numbers
    Param
    a: the first int operand
    b: the second int operand
    Return
    (int): ones composite sum of given operands
    '''
    mod = 1 << 16
    res = a + b
    if res < mod: 
      return res
    else:
      return (res + 1) % mod

class Timer:
    '''
    A Timer class that wraps up a threading timer, which is thread safe
    '''
    def __init__(self, interval, handler):
        self.interval = interval
        self.handler = handler
        self.lock = threading.Lock()
        self.timer = None

    def start(self):
        '''
        create a new threading timer and start it
        '''
        self.timer = threading.Timer(self.interval, self.time_out_handler)
        self.timer.start()

    def time_out_handler(self):
        '''
        run the handler
        '''
        with self.lock:
            self.handler()
            # recall the handler when timeout, which will keep the timer running
            # until manually terminate.
            self.start()

    def stop(self):
        '''
        stop the timer
        '''
        with self.lock:
            if self.timer:
                self.timer.cancel()


