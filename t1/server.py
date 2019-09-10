import socket
from threading import Thread
from config import Config
from utils import notify
import re

class Server(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_connections = {}
        self.awaiting_connection = True
        self.end = False
        self.mailing_list = [
            'nombregag@gmail.com',
            'gabriel.lins97@gmail.com',
            '',
        ]

    def start(self):
        try:
            self.socket.bind((Config.SERVER.SERVER_IP, Config.SERVER.SERVER_PORT))
            notify(Config.NOTIFICATION_TYPES.SUCCESS, Config.MESSAGES.SOCKET_BINDED)
        except:
            notify(Config.NOTIFICATION_TYPES.ERROR, Config.MESSAGES.SOCKET_BIND_FAILED)
            try:
                notify(Config.NOTIFICATION_TYPES.WARNING, Config.MESSAGES.FIX_ATTEMPT)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((Config.SERVER.SERVER_IP, Config.SERVER.SERVER_PORT))
                s.close()
                
                self.socket.bind((Config.SERVER.SERVER_IP, Config.SERVER.SERVER_PORT))
                notify(Config.NOTIFICATION_TYPES.SUCCESS, Config.MESSAGES.SOCKET_BINDED)
            except:
                notify(Config.NOTIFICATION_TYPES.ERROR, Config.MESSAGES.FIX_ATTEMPT_FAILED)
                notify(Config.NOTIFICATION_TYPES.ERROR, Config.MESSAGES.SERVER_STALLED)
                return 

        self.socket.listen(10)
        Thread(target=self.handle_clients, args=tuple()).start()
        
        command = input()
        while command != "quit":
            print('"{}" command not found.'.format(command))
            command = input()
        
        self.stop()
    
    def stop(self):
        for conn in self.active_connections:
            conn.close()
        self.socket.close()

    def _do_helo(self, addr, *args):
        if (args):
            self.active_connections[addr]['uid'] = args[0]
            self.active_connections[addr]['protocol'] = 'helo'
            return b'200 OK'
        return b'400 not enough parameters'    

    def _do_verify(self, *args):
        found = False
        if not args:
            found = True
        for arg in args:
            print('tesint ', arg)
            if (arg in self.mailing_list):
                found = True
        if found:
            return b'200 OK'
        return b'500 NOT FOUND'    

    def _do_rset(self, addr):
        if addr not in self.active_connections:
            return b'500 NOT FOUND'
        
        try:
            self.active_connections[addr] = {
                'Connection': self.active_connections[addr]['Connection']
            }
            return b'200 OK'
        except:
            return b'500 Error'

    def _do_noop(self):
        return b'200 OK'

    def _do_ehlo(self, addr, *args):
        if (args):
            self.active_connections[addr]['uid'] = args[0]
            self.active_connections[addr]['protocol'] = 'ehlo'
            return b'200 OK'
        return b'400 not enough parameters'    

    def _do_help(self):
        return b'200 OK;\nHELO\nVRFY\nRSET\nNOOP\nSTARTTLS\nAUTH\nQUIT\r\n'

    def _do_start_tls(self, addr):
        if 'protocol' not in self.active_connections[addr]:
            return b'400 please specify comms protocol'
        if  self.active_connections[addr]['protocol'] != 'ehlo':
            return b'400 wrong protocol specified'
        return b'500 NOT YET IMPLEMENTED'

    def _do_auth_username(self, addr):
        self.active_connections[addr]['flow'] = 'username'
        return b'300 Username:'

    def _do_auth_passwd(self, addr):    
        self.active_connections[addr]['flow'] = 'passwd'
        return b'300 Password:'

    def _do_auth_result(self, addr):    
        del self.active_connections[addr]['flow']
        self.active_connections[addr]['authed'] = True
        return b'200 OK:'

    def _do_mail_from(self, addr, *args):
        self.active_connections[addr]['mail_from'] = re.search('<(.+?)>', str(args[0]), re.DOTALL).group(1)
        self.active_connections[addr]['mail_recpts'] = []
        return b'200 OK'
    
    def _do_mail_recpt(self, addr, *args):
        self.active_connections[addr]['mail_recpts'].append(re.search('<(.+?)>', str(args[0]), re.DOTALL).group(1))
        return b'200 OK'
    
    def _do_mail_data(self, addr):
        self.active_connections[addr]['mail_data'] = b'' 
        self.active_connections[addr]['flow'] = 'data' 
        return b'200 OK'

    def _do_mail_data_process(self, addr, raw):
        if raw != b'\r\n.\r\n' and raw != b'.\r\n':
            self.active_connections[addr]['mail_data'] += raw
            return None
        else:
            print('MAIL FINISH')
            del self.active_connections[addr]['flow']
            return b'200 OK'

    def _do_quit(self, addr):
        print(self.active_connections[addr])
        del self.active_connections[addr]
        return b'200 OK'

    def evaluate(self, addr, raw):
        if raw == b'': return b''

        if 'flow' in self.active_connections[addr]:
            status = self.active_connections[addr]['flow']
            if status == 'username':
                return self._do_auth_passwd(addr)
            elif status == 'passwd':
                return self._do_auth_result(addr)
            elif status == 'data':
                return self._do_mail_data_process(addr, raw)

        reply = b'400 Unidentified char sequence\r\n'
        
        data = raw.split()
        command = data[0]
        args = data[1:]

        if command == b'HELO':
            return self._do_helo(addr, *args)

        if command == b'VRFY':
            reply = self._do_verify(*args)

        if command == b'RSET':
            reply = self._do_rset(addr)
        
        if command == b'NOOP':
            reply = self._do_noop()

        if command == b'EHLO':
            reply = self._do_ehlo(addr, *args)
        
        if command == b'HELP':
            reply = self._do_help()

        if command == b'STARTTLS':
            reply = self._do_start_tls(addr)
        
        if command == b'AUTH':
            reply = self._do_auth_username(addr)

        if command == b"QUIT":
            reply = self._do_quit(addr)

        if command == b"MAIL":
            reply = self._do_mail_from(addr, *args)
        
        if command == b"RCPT":
            reply = self._do_mail_recpt(addr, *args)

        if command == b"DATA":
            reply = self._do_mail_data(addr, *args)

        return reply

    def handle_clients(self):
        while (self.active_connections or self.awaiting_connection) and not self.end:
            try:
                conn, addr = self.socket.accept()
                notify(Config.NOTIFICATION_TYPES.SUCCESS, Config.MESSAGES.CLIENT_CONNECTED)
            except:
                notify(Config.NOTIFICATION_TYPES.ERROR, Config.MESSAGES.CLIENT_CONNECTION_FAILED)

            try:
                Thread(target=self.handle_client, args=(conn, addr)).start()
                notify(Config.NOTIFICATION_TYPES.SUCCESS, Config.MESSAGES.CLIENT_HANDLER_STARTED)
            except:
                notify(Config.NOTIFICATION_TYPES.ERROR, Config.MESSAGES.CLIENT_HANDLER_START_FAILED)

    def handle_client(self, conn, addr):
        self.awaiting_connection = False
        self.active_connections[addr] = {'Connection': conn}
        conn.send(b'200 OK\r\n')
        
        while addr in self.active_connections:
            data = conn.recv(1024)
            reply = self.evaluate(addr, data)
            if reply:
                conn.send(reply)

        conn.close()

if __name__ == '__main__':
    s = Server()
    s.start()