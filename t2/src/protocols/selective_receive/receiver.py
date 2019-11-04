import time 

# Classe SRReceiver
# --------------
# É responsável por fazer o papel do receiver no protocolo Selective Repeat
class SRReceiver(object):
    def __init__(self, receiver, win_size=1, seq_size=2, timeout=0, *args, **kwargs):
        self.receiver = receiver
        self.win_size = win_size
        self.seq_size = seq_size
        self.timeout = timeout

        self.responses = []
        self.win_index = 0
        self.recvs = {item:-1 for item in range(self.seq_size)}
        self.pkts = {item:None for item in range(self.seq_size)}

    # Pede um pacote ao protocolo, retornando o byte a ser transmitido e o marcador de tempo atual;
    # Retorno None indica que não há pacotes a serem transmitidos;
    def get_pkg(self):
        for item in self.responses:
            self.responses.remove(item)
            return [
                item,
                time.time()
            ]

        return [None, 0]

    # A partir dos acks já recebidos, move a janela para frente;
    def update_window(self):
        shift_ammount = 0
        for index in range(self.win_size):
            seq = (self.win_index + index) % self.seq_size
            if self.recvs[seq] != -1:
                self.receiver.message.append(self.pkts[seq])
                self.receiver.message_size += 1
                self.recvs[seq] = -1
                self.pkts[seq] = None
                shift_ammount += 1
            else:
                break

        self.win_index += shift_ammount
        

    # Response é uma tupla de (tipo_do_pacote, valor, seq_id) 
    # Como ('ack', BYTE, 1) ou ('ERR', 0, 0)
    def process_response(self, response):
        # print("Receiver::process_response", response)
        t, value, seq = response

        current_window = [(self.win_index + index) % self.seq_size for index in range(self.win_size-1)]
        if t == 'pkg':
            self.responses.append(['ack', seq])
            if seq not in current_window:
                return
            self.recvs[seq] = time.time()
            self.pkts[seq] = value
            self.update_window()
