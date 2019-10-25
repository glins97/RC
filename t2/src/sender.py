from .protocols.stop_and_wait.sender import SWSender

class Sender(object):
    def __init__(self, protocol, *args, **kwargs):
        self.protocol = self.load_protocol(protocol)
        self.message = []
        
    def load_protocol(self, name):
        protocol = None
        if name == "STOP_AND_WAIT":
            protocol = SWSender(self)
            protocol.state = 'wait_0' 
            
        if name == "GO_BACK_N":
            pass
        if name == "SELECTIVE_REPEAT":
            pass

        return protocol

    def receive(self, *args, **kwargs):
        self.protocol.process(*args, **kwargs)

    def request_pkg(self, *args, **kwargs):
        return self.protocol.get_pkg(*args, **kwargs)