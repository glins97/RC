#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from kivy.uix.relativelayout import RelativeLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.properties import StringProperty

Builder.load_file('gui/view/root/root.kv')
class T2Root(RelativeLayout):
    total_transmission_time = StringProperty('')
    average_rtt = StringProperty('')
    transmission_delay = StringProperty('')
    utilization = StringProperty('')
    
    def run_simulator(self):
        app = App.get_running_app()
        total_transmission_time, average_rtt, transmission_delay, utilization = app.simulator.run()
        self.total_transmission_time = '{:.4f}s'.format(total_transmission_time)
        self.average_rtt = '{:.4f}ms'.format(average_rtt)
        self.transmission_delay = '{:.4f}ms'.format(transmission_delay)
        self.utilization = '{:.4f}%'.format(utilization)