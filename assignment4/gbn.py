import udt
import config
import util
import struct

# Go-Back-N reliable transport protocol.
class GoBackN:
    # "msg_handler" is used to deliver messages to application layer
    # when it's ready.
    # base stands for the starting of a new window
    # next_seq_num stands for the seq # of the next packet
    # last_packets holds the packets sent
    # expect_seq_num is for receiver
    def __init__(self, local_port, remote_port, msg_handler):
        self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
        self.msg_handler = msg_handler
        self.base = 0
        self.next_seq_num = 0
        self.expect_seq_num = 0
        self.last_packets = []
        self.timer = util.Timer(config.TIMEOUT_MSEC / 1000, self.timer_handler)

    # handler that resends the packets between base and next_seq_num, they
    # were sent while not acked yet.
    def timer_handler(self):
        for i in range(self.base, self.next_seq_num):
            self.network_layer.send(self.last_packets[i])

    # "send" is called by application. Return true on success, false otherwise.
    def send(self, msg):
        # TODO: impl protocol to send packet from application layer.
        # call self.network_layer.send() to send to network layer.
        # send the msg when the seq num is inside of the window
        if self.next_seq_num < self.base + config.WINDOW_SIZE:
            snd_pkt = util.make_packet(config.MSG_TYPE_DATA, self.next_seq_num, msg)
            self.last_packets.append(snd_pkt)
            self.network_layer.send(snd_pkt)
            # start the timer for the oldest in-flight pkt
            if self.base == self.next_seq_num:
                self.timer.start()
            self.next_seq_num += 1
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
            # 1. send ACK for correctly-received pkt with highest in-order seq #
            if cal_check_sum == rcv_check_sum and self.expect_seq_num == rcv_seq_num:
                self.msg_handler(payload)
                snd_pkt = util.make_packet(config.MSG_TYPE_ACK, rcv_seq_num, b'')
                self.network_layer.send(snd_pkt)
                self.expect_seq_num += 1
            # 2. for out-of-order pkt, discard it and resend the ACK pkt with highest in-order seq #
            else:
                snd_pkt = util.make_packet(config.MSG_TYPE_ACK, self.expect_seq_num - 1, b'')
                self.network_layer.send(snd_pkt)
        # Case for Sender
        elif rcv_data_type == config.MSG_TYPE_ACK:
            # if recving packet of the correct ACK, update the base
            if rcv_check_sum == cal_check_sum:
                self.base = rcv_seq_num + 1
                # if current window is over, stop the timer.
                if self.base == self.next_seq_num:
                    self.timer.stop()
                else:
                    self.timer.start()

    # Cleanup resources.
    def shutdown(self):
        # TODO: cleanup anything else you may have when implementing this
        # class.
        self.network_layer.shutdown()
