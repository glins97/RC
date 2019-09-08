from config import Config
import inspect

def notify(mtype, message='', use_caller=True, caller='', *args, **kwargs):
    s = '{} {}'.format(mtype, message)
    if use_caller:
        if not caller:
            caller = inspect.stack()[1].function.upper()
        s = '{}::'.format(caller) + s
    print(s)
