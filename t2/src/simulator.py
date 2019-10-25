import numpy
import time
from .sender import Sender
from .receiver import Receiver
from random import uniform

class Simulator(object):
    # distance => propagation delay, in ms
    # timeout => ms
    # throughtput => bits/second
    # error_p => probability of error with range [0, 1] 
    def __init__(self, error_p, throughput, distance, timeout, *args, **kwargs):
        self.error_p = error_p
        self.throughput = throughput/8
        self.distance = distance/1000
        self.timeout = timeout
        
        self.sender = None
        self.receiver = None

        self.data = {
            'rtts': [],
        }
        
    def run(self):
        if self.sender == None:
            print("Simulator has no sender. Please call method 'load' before running.")
            return

        if self.receiver == None:
            print("Simulator has no receiver. Please call method 'load' before running.")
            return

        self.data['transmission_start'] = time.time()
        transmission_delay = len(self.sender.message)/self.throughput
        while True:
            sender_pkg = self.sender.request_pkg()
            if sender_pkg == 'STATUS_DONE': break
            
            # Errors & Delays =====================
            if uniform(0, 1) < self.error_p: # Error
                sender_pkg[0] = "ERR"
            time.sleep(transmission_delay) # Transmission delay
            rtt_start = time.time()
            time.sleep(self.distance) # Propagation delay
            # =====================================

            self.receiver.receive(sender_pkg)
            receiver_pkg = self.receiver.request_pkg()

            # Errors & Delays =====================        
            time.sleep(self.distance) # Propagation delay
            rtt_end = time.time()
            self.data['rtts'].append(rtt_end - rtt_start)
            if uniform(0, 1) < self.error_p: # Error
                sender_pkg[0] = "ERR"
            # =====================================
            self.sender.receive(receiver_pkg)

        self.data['transmission_end'] = time.time()
        self.evaluate()

    def load(self, protocol):
        self.sender = Sender(protocol)
        self.sender.message = self.generate_message('1k')
        self.sender.message_size = len(self.sender.message)
        self.receiver = Receiver(protocol)
        return self

    def evaluate(self):
        diff = numpy.sum(self.sender.message != self.receiver.message)
        if diff == 0:
            print("[SUCCESS] No transmission errors!")
        else:
            print("[ERROR] There were {} wrong packages.".format(diff))

        transmission_delay = len(self.sender.message)/self.throughput
        message_size = len(self.sender.message)
        average_rtt = numpy.average(self.data['rtts'])
        transmission_time = self.data['transmission_end'] - self.data['transmission_start']  
        
        print('Total transmissino time: {:.4f}s'.format(transmission_time))
        print('Message size: {}kb'.format(int(8 * message_size/1000)))
        print('------------------------')
        print('Average rtt: {:.4f}ms'.format(1000 * average_rtt))
        print("Transmision delay: {}ms".format(transmission_delay * 1000))
        print('Utilization: {:.4f}%'.format(100 * transmission_delay / (average_rtt + transmission_delay)))

    # in bytes
    def generate_message(self, size):
        return numpy.random.randint(0, 255, self.convert_size(size))
        
    def convert_size(self, size):
        multiplier = 1
        size = size.lower().replace('m', 'kk')
        size = size.lower().replace('g', 'kkk')
        size = size.lower().replace('t', 'kkkk')
        while 'k' in size.lower():
            index = size.index('k')
            multiplier = multiplier * 1000
            size = size[:index] + size[index+1:]

        return int(size) * multiplier
