from .protocols.stop_and_wait.receiver import SWReceiver
from .protocols.selective_receive.receiver import SRReceiver
import time

class Receiver(object):
    def __init__(self, protocol, *args, **kwargs):
        self.protocol = self.load_protocol(protocol, *args, **kwargs)
        self.message = []
        self.recv = []

    def load_protocol(self, name, *args, **kwargs):
        protocol = None
        if name == "STOP_AND_WAIT":
            protocol = SWReceiver(self)
            protocol.state = 'wait_0' 
            
        if name == "SELECTIVE_REPEAT":
            protocol = SRReceiver(self, *args, **kwargs)

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