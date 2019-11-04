import numpy
import time
from .sender import Sender
from .receiver import Receiver
from random import uniform
import sys

# Classe Simulator
# --------------
# Utilizado na interface gráfica para criar e executar simulações
#   de transmissão de maneira controlada
# 
# Entradas:
#   1. Tamanho da mensage, em bytes
#   2. Probabilidade de erro, com intervalo [0, 1)
#   3. Vazão/velocidade do link a ser simulado
#   4. Tempo de propagação do meio, abstração da distância entre sender e receiver
#   5. *args e **kwargs são parâmetros adicionais que serão carregados para o protocolo escolhido

class Simulator(object):
    # message_size => @string size in bytes
    # distance => propagation delay, in ms
    # timeout => ms
    # throughtput => bytes/second
    # error_p => probability of error with range [0, 1] 
    def __init__(self, message_size, error_p, throughput, distance,*args, **kwargs):
        self.message_size = message_size
        self.error_p = error_p
        self.throughput = throughput
        self.distance = distance/1000
        
        self.sender = None
        self.receiver = None

        self.data = {}
        
    # Inicia a simulação de transmissão;
    # Retorna os dados coletados da transmissão do pacote, como rtt médio, tempo total de transmissão e utilização do link;
    # ----
    # Funcionamento:
    #   Sender e receiver são requisitados pacotes à todo instante, mas só retornam quando o protocolo permitir;
    #   Para simular o tempo de envio de cada pacote sem utilizar métodos que temporariamente congelem a execução do programa,
    #       cada pacote enviado é colocado em uma fila de processamento até que o tempo de envio tenha decorrido; tal escolha
    #       permite a implementação de protocolos como o selective repeat com esforço mínimo 
    def run(self):
        # Verifica a validez do sender
        if self.sender == None:
            print("Simulator has no sender. Please call method 'load' before running.")
            return

        # Verifica a validez do receiver
        if self.receiver == None:
            print("Simulator has no receiver. Please call method 'load' before running.")
            return

        # Gera mensagem aleatória composta por números de 0 a 255 para simular 1 byte
        self.sender.message = self.generate_message(self.message_size)
        self.sender.message_size = len(self.sender.message)
        self.receiver.message = []
        self.receiver.message_size = 0
        transmission_delay = len(self.sender.message)/self.throughput
        
        self.data['transmission_start'] = time.time()
        while True: # Execução ocorrerá até o sender explicitamente requisite o fim da mesma

            # Sender e receiver ambos processam os pacotes recebidos, avaliando 
            # se seus protocolos já podem registrar o recebimento dos mesmos
            self.sender.process()
            self.receiver.process()

            # Feedback do estado atual da transmissão no console
            sys.stdout.write("Transmission: " + str(self.receiver.message_size * 100 / self.sender.message_size) + "%" + "\r")
            
            # Requisição de pacotes para o sender e receiver
            sender_pkg, sender_time = self.sender.request_pkg()
            receiver_pkg, receiver_time = self.receiver.request_pkg()
            
            # Se 'total_acks' for igual ao tamanho da mensagem a ser transmitida, encerra a transmissão;
            if self.receiver.message_size == self.sender.message_size: break

            # Se houver um pacote a ser mandado pelo sender, receiver recebe o pacote e o guarda na fila
            # de processamento, indicando que o mesmo deve ser interpretado pelo protocolo em X milisegundos a partir do momento de envio, 
            # com X = tempo de transmissão + tempo de propagação (self.distance)
            err = 0
            if sender_pkg != None and sender_pkg != 'STATUS_DONE':
                if uniform(0, 1) < self.error_p: # Error
                    err = 60
                self.receiver.receive(sender_pkg, sender_time + transmission_delay + self.distance + err)
            
            # Se houver um pacote a ser enviado pelo receiver, ...
            if receiver_pkg != None:
                if uniform(0, 1) < self.error_p: # Error
                    err = 60
                self.sender.receive(receiver_pkg, receiver_time + self.distance + err)

        # Calcula dados referentes à transmissão
        self.data['transmission_end'] = time.time()
        self.data['rtts'] = self.sender.rtts[:]

        # Retorna análise dos resultados obtidos, na forma de 
        # 1. Tempo total de transmissão;
        # 2. RTT médio;
        # 3. Delay de transmissão;
        # 4. Utilização do link
        return self.evaluate()

    # Carrega as configurações de inicialização contidas em *args e **kwargs para os protocolos;
    # Essa semântica permite que eu possa inicializar o simulador com quaisquer quantidade de parâmetros,
    #   e todos que não forem utilizados no Simulator serão utilizados aqui
    def load(self, protocol, *args, **kwargs):
        self.sender = Sender(protocol, *args, **kwargs)
        self.receiver = Receiver(protocol, *args, **kwargs)
        return self

    # Dadas informações de transmissão, faz a análise dos resultados obtidos
    def evaluate(self):
        # Se houver diferença entre a mensagem enviada e recebida, mostrar byte a byte a comparação entre mensagens
        diff = numpy.sum(self.sender.message != self.receiver.message)
        if diff == 0:
            print("[SUCCESS] No transmission errors!")
        else:
            print("[ERROR] There were {} wrong packages.".format(diff))
            print(self.sender.message)
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

    # Gera números inteiros aleatórios entre o intervalo [0, 255] para simular 
    # atomicamente o envio de bytes
    def generate_message(self, size):
        return numpy.random.randint(0, 255, self.convert_size(size))

    # Converte a entrada em representação com multiplicadores para entrada com valor bruto
    # Eg: 1M = 1000000
    # Facilitia a simulação rápida de pacotes de diversos tamanhos        
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
