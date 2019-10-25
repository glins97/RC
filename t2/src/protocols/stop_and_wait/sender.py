
class SWSender(object):
    def __init__(self, sender, *args, **kwargs):
        self.sender = sender
        self.state = ''
        self.message_index = 0
        self.sequence_number = 0

    def get_pkg(self):
        if self.message_index == self.sender.message_size:
            return "STATUS_DONE"
        return ['pkg', self.sender.message[self.message_index], self.sequence_number]

    # response is a tuple of type and seq, 
    # such as ('ack', 1) or ('timeout', 0)
    def process(self, response):
        # print("SWSender received", response)
        t, seq = response
        if self.state == 'wait_0':
            if t == "ack" and seq == 0:
                self.message_index += 1
                self.sequence_number = 1
                self.state = "wait_1"

            if t == "ack" and seq == 1:
                self.sequence_number = 0
    
        if self.state == 'wait_1':
            if t == "ack" and seq == 1:
                self.message_index += 1
                self.sequence_number = 0
                self.state = "wait_0"

            if t == "ack" and seq == 0:
                self.sequence_number = 1

