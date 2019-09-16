class ConfigBase(object):
    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

class Config(object):
    SERVER = ConfigBase(
        SERVER_IP = "smtp.gmail.com",
        SERVER_PORT = 587,
        BUFFER_SIZE = 1024,
        IS_DEV_MODE = True,
    )

    RESPONSES = ConfigBase(
        INFORMATION = 'INFORMATION', 
        SUCCESSFUL = 'SUCCESS',
        REDIRECT = 'REDIRECT',
        CLIENT_ERROR = 'CLIENT_ERROR',
        SERVER_ERROR = 'SERVER_ERROR',
    )

    CONNECTION_TYPES = ConfigBase(
        ESMTP = "ESMTP",
        SMTP = "SMTP",
    )

    NOTIFICATION_TYPES = ConfigBase(
        ERROR = "[ERROR]",
        DEBUG = "[DEBUG]",
        WARNING = "[WARNING]",
        SUCCESS = "[SUCCESS]",
    )

    MESSAGES = ConfigBase(
        FIX_ATTEMPT = 'ATTEMPTING TO FIX ISSUES',
        FIX_ATTEMPT_FAILED = 'FIX ATTEMPT HAS FAILED',
        WRONG_PROTOCOL = 'WRONG PROTOCOL',
        ESMTP_NOT_SPECIFIED = 'EXTENDED SMTP HAS NOT BEEN SPECIFIED',
        TLS_NOT_STARTED = 'TLS HAS NOT BEEN NOT STARTED',
        START_TLS_FAILED = 'START TLS HAS FAILED TO START',
        AUTH_FAILED = 'AUTH HAS FAILED',
        SOCKET_BINDED = 'SOCKET HAS BINDED WITH LOCALHOST',
        SOCKET_BIND_FAILED = 'SOCKET FAILED TO BIND WITH LOCALHOST',
        SERVER_STALLED = 'SERVER HAS STALLED',
        CLIENT_CONNECTED = 'CONNECTED WITH CLIENT',
        CLIENT_CONNECTION_FAILED = 'FAILED TO CONNECT WITH CLIENT',
        CLIENT_HANDLER_STARTED = 'CLIENT HANDLER HAS STARTED',
        CLIENT_HANDLER_START_FAILED = 'CLIENT HANDLER HAS FAILED TO STARTED',
    )