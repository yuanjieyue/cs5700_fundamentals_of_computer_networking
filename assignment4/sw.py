import udt
import struct
import config
import time
import util

debug = False
def debug_print(message):
    if debug:
        print(message)

# Stop-And-Wait reliable transport protocol.
class StopAndWait:
    # "msg_handler" is used to deliver messages to application layer
    # when it's ready.

    # seq_num and last_seq_num help Sender side check the right sequence.
    # expect_seq_num helps Receiver side check the seq num coming from the Sender.
    def __init__(self, local_port, remote_port, msg_handler):
        self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
        self.msg_handler = msg_handler
        self.seq_num = 0
        self.last_seq_num = -1
        self.expect_seq_num = 0
        self.last_packet = b''
        self.timer = util.Timer(config.TIMEOUT_MSEC / 1000, self.timer_handler)

    # handler that sends the last packet when time out
    def timer_handler(self):
        self.network_layer.send(self.last_packet)

    # "send" is called by application. Return true on success, false otherwise.
    def send(self, msg):
        # TODO: impl protocol to send packet from application layer.
        # call self.network_layer.send() to send to network layer.
        # if current sequence status is correct, send the msg
        if self.seq_num == self.last_seq_num + 1:
            self.print_seqs(self.seq_num, self.last_seq_num, self.expect_seq_num)
            self.print_pkt_infos(config.MSG_TYPE_DATA, self.seq_num, msg)
            snd_pkt = util.make_packet(config.MSG_TYPE_DATA, self.seq_num, msg)
            self.last_packet = snd_pkt
            debug_print('++++ snd pkt is {}'.format(snd_pkt))
            self.network_layer.send(snd_pkt)
            self.incr_seq('seq')
            self.timer.start()
            return True
        else:
            return False

    # "handler" to be called by network layer when packet is ready.
    def handle_arrival_msg(self):
        # TODO: impl protocol to handle arrived packet from network layer.
        # call self.msg_handler() to deliver to application layer.
        rcv_pkt = self.network_layer.recv()
        rcv_data_type, rcv_seq_num, rcv_check_sum, payload = util.parse_packet(rcv_pkt)     
        cal_check_sum = util.calculate_check_sum(rcv_data_type, rcv_seq_num, payload)
        # Case for Receiver
        if rcv_data_type == config.MSG_TYPE_DATA:
            # 1. if not corrupt and of right sequence, handle it and send a right ACK back
            if cal_check_sum == rcv_check_sum and self.expect_seq_num == rcv_seq_num:
                self.print_seqs(self.seq_num, self.last_seq_num, self.expect_seq_num)
                self.print_pkt_infos(rcv_data_type, rcv_seq_num, payload)
                self.msg_handler(payload)
                snd_pkt = util.make_packet(config.MSG_TYPE_ACK, rcv_seq_num, b'')
                debug_print('++++ snd pkt is {}'.format(snd_pkt))
                self.network_layer.send(snd_pkt)
                self.incr_seq('expect_seq')
            # 2. if of wrong sequence send ACK of most recent seq num
            #    thus the Sender will retransmit the last packet    
            else:
                snd_pkt = util.make_packet(config.MSG_TYPE_ACK, self.expect_seq_num - 1, b'')
                self.network_layer.send(snd_pkt)
        # Case for Sender
        elif rcv_data_type == config.MSG_TYPE_ACK:
            # if not corrupt and of right sequence, means last packet was well received
            # stop timer and move on to be ready for the next packet
            if cal_check_sum == rcv_check_sum and self.last_seq_num == rcv_seq_num - 1:
                self.timer.stop()
                self.incr_seq('last_seq')

    # Cleanup resources.
    def shutdown(self):
        # TODO: cleanup anything else you may have when implementing this
        # class.
        self.network_layer.shutdown()
  
    # help increase the seq numbers.
    def incr_seq(self, name):
        if name == 'seq':
            self.seq_num += 1
        elif name == 'last_seq':
            self.last_seq_num += 1
        elif name == 'expect_seq':
            self.expect_seq_num += 1

    # helper function to print the three sequence numbers  
    def print_seqs(self, seq_num, last_seq_num, expect_seq_num):
        debug_print('++++++++++++++++++++++++++++++++++++++++++')
        debug_print('++ seq num is {}'.format(seq_num))
        debug_print('++ last seq num is {}'.format(last_seq_num))
        debug_print('++ expect seq num is {}'.format(expect_seq_num))
        debug_print('++++++++++++++++++++++++++++++++++++++++++')

    # helper function to print the detailed info of in a packet
    def print_pkt_infos(self, data_type, seq_num, payload):
        debug_print('++++++++++++++++++++++++++++++++++++++++++')
        debug_print('++ rcv data type {}'.format(data_type))
        debug_print('++ rcv seq num {}'.format(seq_num))
        debug_print('++ payload is {}'.format(payload))
        debug_print('++++++++++++++++++++++++++++++++++++++++++')