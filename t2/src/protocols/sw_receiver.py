from .base import ProtocolBase
from time import time

class SWReceiver(ProtocolBase):
    def __init__(self, *args, **kwargs):
        self.receiver = None
        self.sequence_number = 0
        self.state = "wait_0"
        self.sent = True
        self.last_receive = time()

    def process_state(self):
        if not self.sent:
            pkg = ['ack', self.sequence_number]
            self.receiver._send(pkg)
            self.sent = True

    # response is a tuple of (type, value, seq)
    # such as ('ack', 0, 0), ('timeout', 0, 0)
    def process_response(self, response):
        # print("SWReceiver received", response)
        self.last_receive = time()
        done = False
        
        t, value, seq = response
        if self.state == 'wait_0':
            if t == 'pkg' and seq == 0:
                done = True
                self.sent = False
                self.sequence_number = 0
                self.state = "wait_1"
                self.receiver.msg.append(value)
        
        if self.state == 'wait_1':
            if t == 'pkg' and seq == 1:
                done = True
                self.sent = False
                self.sequence_number = 1
                self.state = "wait_0"
                self.receiver.msg.append(value)

        if not done:
            print(self.receiver.msg)
            input("Nothing done on receiver at '{}' with response '{}'".format(self.state, response))
            