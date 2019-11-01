import time 

class SRReceiver(object):
    def __init__(self, receiver, win_size=1, seq_size=2, timeout=0, *args, **kwargs):
        self.receiver = receiver
        self.win_size = win_size
        self.seq_size = seq_size
        self.timeout = timeout

        self.responses = []
        self.seq_index = 0
        self.win_index = 0
        self.recvs = {}
        self.pkts = {}
        self.pkt_keys = [item for item in range(seq_size)]
        self.reset()

    def reset(self):
        self.recvs = {item:-1 for item in range(self.seq_size)}
        self.pkts = {item:None for item in range(self.seq_size)}

    def get_pkg(self):
        for item in self.responses:
            self.responses.remove(item)
            return [
                item,
                time.time()
            ]

        return [None, 0]

    def update_window(self):
        shift_ammount = 0
        for index in range(self.win_size):
            seq = (self.win_index + index) % self.seq_size
            if self.recvs[seq] != -1:
                self.receiver.message.append(self.pkts[seq])
                self.recvs[seq] = -1
                self.pkts[seq] = None
                shift_ammount += 1
            else:
                break

        self.win_index += shift_ammount
        

    def process_response(self, response):
        # print("Receiver::process_response", response)
        t, value, seq = response

        if t == 'pkg':
            self.recvs[seq] = time.time()
            self.pkts[seq] = value
            self.responses.append(['ack', seq])
            self.update_window()
