import socket
from threading import Thread
from config import Config
from utils import notify

class Server(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_connections = []
        self.awaiting_connection = True
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
        self.close()

    def handle_clients(self):
        while (self.active_connections or self.awaiting_connection) and not self.end:
            try:
                conn, addr = self.socket.accept()
                notify(Config.NOTIFICATION_TYPES.SUCCESS, Config.MESSAGES.CLIENT_CONNECTED)
            except:
                notify(Config.NOTIFICATION_TYPES.ERROR, Config.MESSAGES.CLIENT_CONNECTION_FAILED)

            try:
                Thread(target=self.handle_client, args=(conn,)).start()
                notify(Config.NOTIFICATION_TYPES.SUCCESS, Config.MESSAGES.CLIENT_HANDLER_STARTED)
            except:
                notify(Config.NOTIFICATION_TYPES.ERROR, Config.MESSAGES.CLIENT_HANDLER_START_FAILED)

    def handle_client(self, conn):
        self.awaiting_connection = False
        self.active_connections.append(conn)
        conn.send(b'Welcome to the server. Type something and hit enter\r\n')
        
        while True:
            data = conn.recv(1024)
            reply = b'OK...' + data
            if not data or data == b"QUIT\r\n": 
                break
            conn.send(reply)

        self.active_connections.remove(conn)
        conn.close()

s = Server()
s.start()