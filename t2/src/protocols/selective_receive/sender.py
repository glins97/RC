import time

class SRSender(object):
    def __init__(self, sender, win_size, seq_size, timeout, *args, **kwargs):
        self.sender = sender
        self.win_size = win_size
        self.seq_size = seq_size
        self.timeout = timeout
        
        self.seq_index = 0
        self.win_index = 0
        self.sequence = {}
        self.sends = {}
        self.acks = {}
        self.ack_keys = [item for item in range(self.seq_size)]
        self.reset()

    def reset(self):
        self.sends = {item:-1 for item in range(self.seq_size)}
        self.acks = {item:-1 for item in range(self.seq_size)}

        if self.sender.message_size > 0:
            for i in range(self.seq_size):
                if self.seq_index + i < self.sender.message_size:
                    self.sequence[i] = self.sender.message[self.seq_index + i]
                else:
                    self.sequence[i] = None
        else:
            self.sequence = {}

    def get_pkg(self):
        if self.sequence == {}:
            self.reset()
            
        for item in range(self.win_size):
            item_index = item + self.win_index
            if item_index + self.seq_index >= self.sender.message_size:
                return ['STATUS_DONE', 0]

            # print(item_index)
            if self.sends[item_index] == -1:
                self.sends[item_index] = time.time()
                return [
                    ['pkg', self.sequence[item_index], item_index],
                    self.sends[item_index]
                ]
                
        return [None, 0]

    def update_window(self):
        for item in self.ack_keys[self.win_index:]:
            if self.acks[item] == -1:
                return
            if self.win_index + self.win_size != self.seq_size:
                self.win_index = item

        self.win_index = 0
        self.seq_index += self.seq_size
        self.reset()
        
    def process_response(self, response):
        # print("Sender::process_response", response)
        t, seq = response

        if t == 'ack':
            self.acks[seq] = time.time()
            self.sender.rtts.append(self.acks[seq] - self.sends[seq])
            self.update_window()
