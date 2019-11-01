import time

class SRSender(object):
    def __init__(self, sender, win_size=1, seq_size=2, timeout=0, *args, **kwargs):
        self.sender = sender
        self.win_size = win_size
        self.seq_size = seq_size
        self.timeout = timeout
        
        self.win_index = 0
        self.sends = {}
        self.acks = {}
        self.reset()

        self.transfers = 0

    def reset(self):
        self.sends = {item: -1 for item in range(self.seq_size)}
        self.acks = {item: -1 for item in range(self.seq_size)}

    def get_pkg(self):
        for item in range(self.win_size):
            item_index = item + self.win_index
            seq = item_index % self.seq_size

            if item_index >= self.sender.message_size:
                return ['STATUS_DONE', 0]

            if self.sends[seq] == -1:
                self.sends[seq] = time.time()
                self.transfers += 1
                return [
                    ['pkg', self.sender.message[item_index], seq],
                    self.sends[seq]
                ]

        return [None, 0]

    def update_window(self):
        shift_ammount = 0
        for index in range(self.win_size):
            seq = (self.win_index + index) % self.seq_size
            if self.acks[seq] != -1:
                self.acks[seq] = -1
                self.sends[seq] = -1
                shift_ammount += 1
            else:
                break
        self.win_index += shift_ammount

    def process_response(self, response):
        # print("Sender::process_response", response)

        t, seq = response
        if t == 'ack':
            self.acks[seq] = time.time()
            self.sender.rtts.append(self.acks[seq] - self.sends[seq])
            self.update_window()
            
        # print(self.acks)
        # print(self.sends)
