import time
from threading import Thread

class Receiver(object):
    def __init__(self, protocol, *args, **kwargs):
        self.sender = None
        self.protocol = protocol
        self.protocol.receiver = self
        self.msg = []
        self.throughput = 1000
        
    def _send(self, *args, **kwargs):
        self.sender._receive(*args, **kwargs)

    def _receive(self, *args, **kwargs):
        self.protocol.process_response(*args, **kwargs)