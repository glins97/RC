import time

# Classe SRSender
# --------------
# É responsável por fazer o papel do sender no protocolo Selective Repeat
class SRSender(object):
    def __init__(self, sender, win_size=1, seq_size=2, timeout=0, *args, **kwargs):
        self.sender = sender
        self.win_size = win_size
        self.seq_size = seq_size
        self.timeout = timeout
        
        self.win_index = 0
        self.sends = {item: -1 for item in range(self.seq_size)}
        self.acks = {item: -1 for item in range(self.seq_size)}
        self.resend_seq = -1


    def get_pkg_by_seq(self, seq):
        self.sends[seq] = time.time()
        for item in range(self.seq_size):
            item_index = item + self.win_index
            if seq == (item_index) % self.seq_size:
                return [
                    ['pkg', self.sender.message[item_index], seq],
                    self.sends[seq]
                ]

    # Pede um pacote ao protocolo, retornando o byte a ser transmitido e o marcador de tempo atual;
    # Retorno None indica que não há pacotes a serem transmitidos;
    def get_pkg(self):
        if self.resend_seq != -1:
            tmp = self.get_pkg_by_seq(self.resend_seq)
            self.resend_seq = -1
            return tmp

        for item in range(self.win_size):
            item_index = item + self.win_index
            seq = item_index % self.seq_size

            # Verifica se já foi enviado um pacote com a seq atual;
            # -1 é o marcador que indica que a sequencia ainda não foi enviada;
            if item_index >= self.sender.message_size:
                return ['STATUS_DONE', 0]

            if self.sends[seq] == -1:
                self.sends[seq] = time.time()
                return [
                    ['pkg', self.sender.message[item_index], seq],
                    self.sends[seq]
                ]

        return [None, 0]

    # A partir dos acks já recebidos, move a janela para frente;
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

    # Response é uma tupla de (tipo_do_pacote, seq_id) 
    # Como ('ack', 1) ou ('ERR', 0)
    def process_response(self, response):
        # print("Sender::process_response", response)

        current_window = [(self.win_index + index) % self.seq_size for index in range(self.win_size)]
        t, seq = response
        if t == 'ack':
            if seq not in current_window:
                return
            self.acks[seq] = time.time()
            self.sender.rtts.append(self.acks[seq] - self.sends[seq])
            self.update_window()
            
