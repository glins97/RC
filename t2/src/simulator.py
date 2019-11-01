import numpy
import time
from .sender import Sender
from .receiver import Receiver
from random import uniform
import sys

class Simulator(object):
    # message_size => @string size in bytes
    # distance => propagation delay, in ms
    # timeout => ms
    # throughtput => bytes/second
    # error_p => probability of error with range [0, 1] 
    def __init__(self, message_size, error_p, throughput, distance, timeout, *args, **kwargs):
        self.message_size = message_size
        self.error_p = error_p
        self.throughput = throughput
        self.distance = distance/1000
        self.timeout = timeout
        
        self.sender = None
        self.receiver = None

        self.data = {}
        
    def run(self):
        if self.sender == None:
            print("Simulator has no sender. Please call method 'load' before running.")
            return

        if self.receiver == None:
            print("Simulator has no receiver. Please call method 'load' before running.")
            return

        self.sender.message = self.generate_message(self.message_size)
        self.sender.message_size = len(self.sender.message)

        transmission_delay = len(self.sender.message)/self.throughput
        self.data['transmission_start'] = time.time()
        i = 0
        while True:
            self.sender.process()
            self.receiver.process()

            sys.stdout.write("Transmission: " + str(i * 100 / self.sender.message_size) + "%" + "\r")
            sender_pkg, sender_time = self.sender.request_pkg()
            receiver_pkg, receiver_time = self.receiver.request_pkg()
            
            if i == self.sender.message_size: break
            if sender_pkg != None and sender_pkg != 'STATUS_DONE':
                if uniform(0, 1) < self.error_p: # Error
                    sender_pkg[0] = "ERR"
                self.receiver.receive(sender_pkg, sender_time + transmission_delay + self.distance)
            
            if receiver_pkg != None:
                i += 1
                if uniform(0, 1) < self.error_p: # Error
                    receiver_pkg[0] = "ERR"
                self.sender.receive(receiver_pkg, receiver_time + self.distance)
        self.data['transmission_end'] = time.time()
        self.data['rtts'] = self.sender.rtts[:]
        return self.evaluate()

    def load(self, protocol, *args, **kwargs):
        self.sender = Sender(protocol, *args, **kwargs)
        self.receiver = Receiver(protocol, *args, **kwargs)
        return self

    def evaluate(self):
        diff = numpy.sum(self.sender.message != self.receiver.message)
        if diff == 0:
            print("[SUCCESS] No transmission errors!")
        else:
            print("[ERROR] There were {} wrong packages.".format(diff))
            for i in range(len(self.receiver.message)):
                print('{}x{}'.format(self.sender.message[i], self.receiver.message[i]), end=" ")
        transmission_delay = len(self.sender.message)/self.throughput
        message_size = len(self.sender.message)
        average_rtt = numpy.mean(self.data['rtts'])
        transmission_time = self.data['transmission_end'] - self.data['transmission_start']  

        print('Total transmissino time: {:.4f}s'.format(transmission_time))
        print('Message size: {:.1f}KB'.format(message_size/1000))
        print('------------------------')
        print('Average rtt: {:.4f}ms'.format(1000 * average_rtt))
        print("Transmision delay: {}ms".format(transmission_delay * 1000))
        print('Utilization: {:.4f}%'.format(1000 * 100 * message_size / transmission_time / self.throughput))
        return [transmission_time, 1000 * average_rtt, transmission_delay * 1000, 1000 * 100 * message_size / transmission_time / self.throughput]
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
