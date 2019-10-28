import time 

class SRReceiver(object):
    def __init__(self, receiver, win_size, seq_size, timeout, *args, **kwargs):
        self.receiver = receiver
        self.win_size = win_size
        self.seq_size = seq_size
        self.timeout = timeout

        self.responses = []
        self.seq_index = 0
        self.win_index = 0
        self.pkts = {}
        self.pkt_keys = [item for item in range(seq_size)]
        self.reset()

    def reset(self):
        self.pkts = {item:-1 for item in range(self.seq_size)}

    def append(self):
        for index in self.pkt_keys:
            self.receiver.message.append(self.pkts[index])

    def get_pkg(self):
        for item in self.responses:
            self.responses.remove(item)
            return [
                item,
                time.time()
            ]

        return [None, 0]

    def update_window(self):
        for item in self.pkt_keys[self.win_index:]:
            if self.pkts[item] == -1:
                return
            if self.win_index + self.win_size != self.seq_size:
                self.win_index = item

        self.append()
        self.reset()

    def process_response(self, response):
        # print("Receiver::process_response", response)
        t, value, seq = response

        if t == 'pkg':
            self.pkts[seq] = value
            self.responses.append(['ack', seq])
            self.update_window()
