import time 

# Classe SWReceiver
# --------------
# É responsável por fazer o papel do receiver no protocolo Stop and Wait
class SWReceiver(object):
    def __init__(self, receiver, *args, **kwargs):
        self.receiver = receiver
        self.sequence_number = 0
        self.response = None

    
    # Pede um pacote ao protocolo, retornando o byte a ser transmitido e o marcador de tempo atual;
    # Retorno None indica que não há pacotes a serem transmitidos;
    def get_pkg(self):
        r = self.response
        self.response = None
        return [r, time.time()]

    # Response é uma tupla de (tipo_do_pacote, valor, seq_id) 
    # Como ('ack', BYTE, 1) ou ('ERR', 0, 0)
    def process_response(self, response):
        # print("SWReceiver received", response, time.time())
        t, value, seq = response

        self.response = ['ack', seq]
        if self.sequence_number == seq:
            self.receiver.message.append(value)
            self.sequence_number = not seq
        else:
            self.receiver.message[-1] = value
