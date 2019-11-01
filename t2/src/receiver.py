from .protocols.stop_and_wait.receiver import SWReceiver
from .protocols.selective_receive.receiver import SRReceiver
import time

# Classe Receiver
# --------------
# Utilizado no Simulator para executar o papel do host que recebe a mensagem;
# 
# Inicialização do sender requer uma string identificadora do protocolo a ser utilizado,
#   como "STOP_AND_WAIT" ou "SELECTIVE_REPEAT". A partir da string, o protocolo correto é carregado;
# 
# Assim, é possível mudar o protocolo de recebimento a qualquer instante, e uma mesma classe é capaz de 
#   utilizar uma quantidade não-limitada de protocolos. Ainda, a adição de novos protocolos não 
#   implica na modificação do código atual, facilitando a expansão e correção do sistema;
class Receiver(object):
    def __init__(self, protocol, *args, **kwargs):
        self.protocol = self.load_protocol(protocol, *args, **kwargs)
        self.message = []
        self.recv = []

    # Carrega o protocolo especificado, bem como configurações adicionais contidas em *args e **kwargs
    def load_protocol(self, name, *args, **kwargs):
        protocol = None
        if name == "STOP_AND_WAIT":
            protocol = SWReceiver(self)
            protocol.state = 'wait_0' 
            
        if name == "SELECTIVE_REPEAT":
            protocol = SRReceiver(self, *args, **kwargs)

        return protocol

    # Processa os pacotes recebidos até então, verificando se o protocolo já pode interpretar os dados recebidos;
    def process(self, *args, **kwargs):
        start_ = time.time()

        # OFFSET é uma breve janela de tempo que permite o processamento de protocolos que seriam processados em breve;
        #   OFFSET é responsável por balancear o tempo de processamento com o rtt, evitando que lentidões eventuais afetem
        #   o resultado obtido, diminuindo o erro do sistema
        OFFSET = 5 # us
        OFFSET = OFFSET / 1000000
        for obj in self.recv:
            pkg, t = obj
            if start_ - t > -OFFSET:
                # Processa o pacote e o remove da lista de processamento
                self.protocol.process_response(pkg, *args, **kwargs)
                self.recv.remove(obj) 

    # Coloca o pacote na fila de processamento
    def receive(self, pkg, time, *args, **kwargs):
        if pkg != None:
            self.recv.append([pkg, time])

    # Verifica se o protocolo permite o envio de um pacote
    def request_pkg(self, *args, **kwargs):
        return self.protocol.get_pkg(*args, **kwargs)