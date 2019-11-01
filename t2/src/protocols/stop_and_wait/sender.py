import time

# Classe SWSender
# --------------
# É responsável por fazer o papel do sender no protocolo Stop and Wait
class SWSender(object):
    def __init__(self, sender, *args, **kwargs):
        self.sender = sender
        self.previous_state = ''
        self.state = ''
        self.message_index = 0
        self.sequence_number = 0
        self.sends = {0: -1, 1:-1}

    # Observer pattern no estado do protocolo;
    # Permite que qualquer alteração ao state, salve o state atual
    #   no atributo previous_state;
    def set_state(self, state):
        self.previous_state = self.state
        self.state = state

    # Pede um pacote ao protocolo, retornando o byte a ser transmitido e o marcador de tempo atual;
    # Retorno None indica que não há pacotes a serem transmitidos;
    def get_pkg(self):
        r = None
        t = time.time()

        # Verifica se já foi enviado um pacote com a seq atual;
        #  -1 é o marcador que indica que a sequencia ainda não foi enviada;
        if self.sends[self.sequence_number] == -1:
            self.sends[self.sequence_number] = t # Salva o tempo de envio do pacote 

        if self.message_index == self.sender.message_size:
            r = "STATUS_DONE"
        elif self.state == 'send_0' and self.sequence_number == 0:
            self.set_state('wait_0')
            r = ['pkg', self.sender.message[self.message_index], 0]
        elif self.state == 'send_1' and self.sequence_number == 1:
            self.set_state('wait_1')
            r = ['pkg', self.sender.message[self.message_index], 1]
        
        # Retorna o objeto resposta (r), e o tempo de envio do mesmo (t)
        return [r, t]

    # Response é uma tupla de (tipo_do_pacote, seq_id) 
    # Como ('ack', 1) ou ('ERR', 0)
    def process_response(self, response):
        # print("SWSender received", response, self.state)
        t, seq = response

        if t == "ERR": self.set_state(self.previous_state)
        if self.state == 'wait_0':
            if t == "ack" and seq == 0:
                self.sender.rtts.append(time.time() - self.sends[seq])
                self.message_index += 1
                self.sequence_number = 1
                self.set_state("send_1")

            if t == "ack" and seq == 1:
                self.sequence_number = 0
    
        if self.state == 'wait_1':
            if t == "ack" and seq == 1:
                self.sender.rtts.append(time.time() - self.sends[seq])
                self.message_index += 1
                self.sequence_number = 0
                self.set_state("send_0")
                self.sends = {0: -1, 1:-1}

            if t == "ack" and seq == 0:
                self.sequence_number = 1

