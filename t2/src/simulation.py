from sender import Sender
from receiver import Receiver
from protocols import SWSender, SWReceiver
import time
def main():
    sw_sender = SWSender()
    sw_receiver = SWReceiver()

    r = Receiver(sw_receiver)
    s = Sender(r, sw_sender)

    s.protocol.sent = False

    start = time.time()
    while len(r.msg) != len(s.msg):
        s.protocol.process_state()
        r.protocol.process_state()
    end = time.time()
    
    print(s.msg == r.msg)
    print('Tempo:', end - start)
    print('Vazão:', 8 * len(s.msg) / (end - start))

    start = time.time()
    count = 0
    while count < 1000000:
        count += 1
    end = time.time()
    print('CPU Tempo:', end - start)
    print('CPU Vazão:', count / (end - start))

if __name__ == "__main__":
    main()
