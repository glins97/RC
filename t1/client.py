from socket import *
from base64 import b64encode
import ssl
import inspect

from config import Config
from utils import *

class Client(object):
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.username = ''
        self.password = ''
        self.connection_type = Config.CONNECTION_TYPES.SMTP
        self.tls_started = False

    def encode(self, s, base64=False):
        res = s.encode()
        if base64:
            res = b64encode(res)
        return res + b'\r\n'

    def send(self, s, encoded=False, **kwargs):
        if not encoded:
            s = self.encode(s, **kwargs)
        self.socket.send(s)

    def receive_response(self):
        recv = self.socket.recv(Config.SERVER.BUFFER_SIZE)
        recv = recv.decode()

        status_desc = Config.RESPONSES.CLIENT_ERROR
        status_code = 400

        caller = inspect.stack()[1].function.upper()
        if Config.SERVER.IS_DEV_MODE:
            formating = '\n-------------------\n'
            deb_n(recv.replace('\r\n', '\n\t').strip())
        
        descs = {
            1: Config.RESPONSES.INFORMATION, # 1xx
            2: Config.RESPONSES.SUCCESSFUL,
            3: Config.RESPONSES.REDIRECT,
            4: Config.RESPONSES.CLIENT_ERROR,
            5: Config.RESPONSES.SERVER_ERROR
        }
        try:
            status_desc = descs[int(recv[0])]
            status_code = int(recv[:3])
        except:
            notify(Config.NOTIFICATION_TYPES.ERROR, repr(recv), caller=caller)

        if status_desc == Config.RESPONSES.SUCCESSFUL: 
            notify('[{}]'.format(status_desc), caller=caller)
        else:
            notify('[{}]'.format(status_desc), recv.strip(), caller=caller)

        return (status_code, status_desc, recv)

    def connect(self):
        self.socket.connect((Config.SERVER.SERVER_IP, Config.SERVER.SERVER_PORT))
        self.receive_response()

    def reset(self):
        self.send('RSET')
        self.receive_response()

    def verify(self):
        self.send('VRFY')
        self.receive_response()

    def noop(self):
        self.send('NOOP')
        self.receive_response()

    def quit(self):
        self.send('QUIT')
        self.receive_response()
        self.socket.close()

    def helo(self):
        self.send("HELO {}".format(self.username.strip('@')[0]))
        _, status_desc, _ = self.receive_response()
        if status_desc == Config.RESPONSES.SUCCESSFUL:
            self.connection_type = Config.CONNECTION_TYPES.SMTP
        
    def ehlo(self):
        self.send("HELO {}".format(self.username.strip('@')[0]))
        _, status_desc, _ = self.receive_response()
        if status_desc == Config.RESPONSES.SUCCESSFUL:
            self.connection_type = Config.CONNECTION_TYPES.ESMTP

    def help(self):
        if self.connection_type != Config.CONNECTION_TYPES.ESMTP:
            notify(Config.NOTIFICATION_TYPES.ERROR,
                Config.MESSAGES.WRONG_PROTOCOL)
            return
        self.send("HELP")
        self.receive_response()

    def start_tls(self):
        if self.connection_type != Config.CONNECTION_TYPES.ESMTP:
            notify(Config.NOTIFICATION_TYPES.ERROR,
                Config.MESSAGES.WRONG_PROTOCOL)
            return

        self.send("STARTTLS")
        _, status_desc, _ = self.receive_response()
        self.socket = ssl.wrap_socket(self.socket, ssl_version=ssl.PROTOCOL_TLSv1)
        if status_desc == Config.RESPONSES.SUCCESSFUL:
            self.tls_started = True

    def auth(self):
        if self.connection_type != Config.CONNECTION_TYPES.ESMTP:
            notify(Config.NOTIFICATION_TYPES.ERROR,
                Config.MESSAGES.WRONG_PROTOCOL)
            return

        if not self.tls_started:
            notify(Config.NOTIFICATION_TYPES.ERROR,
                Config.MESSAGES.TLS_NOT_STARTED)
            return
            
        self.send("AUTH LOGIN")
        self.receive_response()

        self.send(self.username, encoded=False, base64=True)
        self.receive_response()

        self.send(self.password, encoded=False, base64=True)
        self.receive_response()

    def mail(self, message, recipient):
        pass

c = Client()
c.username = 'nombregag@gmail.com'
c.password = 'qazxsaq5601'

c.connect()
c.helo()
c.reset()
c.verify()
c.noop()
c.ehlo()
c.help()
c.start_tls()
c.auth()