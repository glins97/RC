import time

class SWSender(object):
    def __init__(self, sender, *args, **kwargs):
        self.sender = sender
        self.previous_state = ''
        self.state = ''
        self.message_index = 0
        self.sequence_number = 0

    def set_state(self, state):
        self.previous_state = self.state
        self.state = state

    def get_pkg(self):
        r = None
        if self.message_index == self.sender.message_size:
            r = "STATUS_DONE"
        elif self.state == 'send_0' and self.sequence_number == 0:
            self.set_state('wait_0')
            r = ['pkg', self.sender.message[self.message_index], 0]
        elif self.state == 'send_1' and self.sequence_number == 1:
            self.set_state('wait_1')
            r = ['pkg', self.sender.message[self.message_index], 1]
        return r

    # response is a tuple of type and seq, 
    # such as ('ack', 1) or ('timeout', 0)
    def process_response(self, response):
        # print("SWSender received", response, self.state)
        t, seq = response

        if t == "ERR": self.set_state(self.previous_state)
        if self.state == 'wait_0':
            if t == "ack" and seq == 0:
                self.sender.rtts.append(time.time() - self.sender.sends[self.sequence_number])
                self.message_index += 1
                self.sequence_number = 1
                self.set_state("send_1")

            if t == "ack" and seq == 1:
                self.sequence_number = 0
    
        if self.state == 'wait_1':
            if t == "ack" and seq == 1:
                self.sender.rtts.append(time.time() - self.sender.sends[self.sequence_number])
                self.message_index += 1
                self.sequence_number = 0
                self.set_state("send_0")

            if t == "ack" and seq == 0:
                self.sequence_number = 1

