
class SWReceiver(object):
    def __init__(self, receiver, *args, **kwargs):
        self.receiver = receiver
        self.state = ''
        self.sequence_number = 0
        self.response = None

    def get_pkg(self):
        return self.response

    # response is a tuple of type and seq, 
    # such as ('ack', 1) or ('timeout', 0)
    def process(self, response):
        # print("SWReceiver received", response)
        t, value, seq = response
        if self.state == 'wait_0':
            if t == 'pkg' and seq == 0:
                done = True
                self.sequence_number = 0
                self.state = "wait_1"
                self.receiver.message.append(value)
                self.response = ['ack', self.sequence_number]
        
        if self.state == 'wait_1':
            if t == 'pkg' and seq == 1:
                done = True
                self.sequence_number = 1
                self.state = "wait_0"
                self.receiver.message.append(value)
                self.response = ['ack', self.sequence_number]

            