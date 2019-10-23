import sys
import numpy
import time
from threading import Thread

class Sender(object):
    def __init__(self, receiver, protocol, *args, **kwargs):
        self.timeout = 0
        self.throughput = 1000
        self.error_probability = 0
        self.distance = 0

        self.protocol = protocol
        self.protocol.sender = self
        self.msg = []
        self.msg_index = 0

        self.gen_packet('1m')
        self.receiver = receiver
        self.receiver.sender = self

    def gen_packet(self, size):
        multiplier = 1

        size = size.lower().replace('m', 'kk')
        size = size.lower().replace('g', 'kkk')
        size = size.lower().replace('t', 'kkkk')
        while 'k' in size.lower():
            index = size.index('k')
            multiplier = multiplier * 1000
            size = size[:index] + size[index+1:]

        self.msg = list(numpy.random.randint(0, 255, int(size) * multiplier))

    def _send(self, *args, **kwargs):
        self.receiver._receive(*args, **kwargs)

    def _receive(self, *args, **kwargs):
        self.protocol.process_response(*args, **kwargs)

    def _get_pkg(self):
        return self.msg[self.msg_index]