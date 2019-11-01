from .protocols.stop_and_wait.sender import SWSender
from .protocols.selective_receive.sender import SRSender
import time

class Sender(object):
    def __init__(self, protocol, *args, **kwargs):
        self.message = []
        self.message_size = 0
        self.recv = []
        self.rtts = []
        self.protocol = self.load_protocol(protocol, *args, **kwargs)
        
    def load_protocol(self, name, *args, **kwargs):
        protocol = None
        if name == "STOP_AND_WAIT":
            protocol = SWSender(self)
            protocol.state = 'send_0' 
            
        if name == "SELECTIVE_REPEAT":
            protocol = SRSender(self, *args, **kwargs)

        return protocol

    def process(self, *args, **kwargs):
        start_ = time.time()
        OFFSET = 0 # us
        OFFSET = OFFSET / 1000000
        for obj in self.recv:
            pkg, t = obj
            if start_ - t > -OFFSET:
                self.recv.remove(obj)
                self.protocol.process_response(pkg, *args, **kwargs)

    def receive(self, pkg, time, *args, **kwargs):
        if pkg != None:
            self.recv.append([pkg, time])

    def request_pkg(self, *args, **kwargs):
        return self.protocol.get_pkg(*args, **kwargs)