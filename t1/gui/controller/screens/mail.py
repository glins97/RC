from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.label import Label

Builder.load_file('gui/view/screens/mail.kv')
class MailScreen(Screen):
    def __init__(self, **kwargs):
        super(MailScreen,self).__init__(**kwargs)

