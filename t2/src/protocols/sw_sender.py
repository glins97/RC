from .base import ProtocolBase
from time import time

class SWSender(ProtocolBase):
    def __init__(self, *args, **kwargs):
        self.state = 'wait_0'
        self.sequence_number = 0
        self.sender = None
        self.sent = True
        self.last_receive = time()

    def process_state(self):
        if not self.sent:
            pkg = ['pkg', self.sender._get_pkg(), self.sequence_number]
            self.sender._send(pkg)
            self.sent = True

    # response is a tuple of type and seq, 
    # such as ('ack', 1) or ('timeout', 0)
    def process_response(self, response):
        # print("SWSender received", response)
        self.last_receive = time()
        done = False
        
        t, seq = response
        if self.state == 'wait_0':
            if t == "ack" and seq == 0:
                done = True
                self.sent = False
                self.sender.msg_index += 1
                self.sequence_number = 1
                self.state = "wait_1"

            if t == "ack" and seq == 1:
                self.sent = False
                self.sequence_number = 0
    
        if self.state == 'wait_1':
            if t == "ack" and seq == 1:
                done = True
                self.sent = False
                self.sender.msg_index += 1
                self.sequence_number = 0
                self.state = "wait_0"

            if t == "ack" and seq == 0:
                self.sent = False
                self.sequence_number = 1

        if not done:
            input("Nothing done on sender at '{}' with response '{}'".format(self.state, response))
