import time 

class SWReceiver(object):
    def __init__(self, receiver, *args, **kwargs):
        self.receiver = receiver
        self.sequence_number = 0
        self.response = None

    def get_pkg(self):
        r = self.response
        self.response = None
        return [r, time.time()]

    # response is a tuple of type and seq, 
    # such as ('ack', 1) or ('timeout', 0)
    def process_response(self, response):
        # print("SWReceiver received", response, time.time())
        t, value, seq = response

        self.response = ['ack', seq]
        if self.sequence_number == seq:
            self.receiver.message.append(value)
            self.sequence_number = not seq
        else:
            self.receiver.message[-1] = value
