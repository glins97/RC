from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.label import Label

Builder.load_file('gui/view/screens/report.kv')
class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen,self).__init__(**kwargs)

    def add_report(self, message): 
        self.ids.grid.add_widget(Label(text=message, size_hint=(1, None), height=30))
