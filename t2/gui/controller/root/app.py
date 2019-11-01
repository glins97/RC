#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
from .root import T2Root
from src.simulator import Simulator

class T2(App):
	def build(self):
		Config.set('graphics', 'width', '380')
		Config.set('graphics', 'height', '500')

		self.root = T2Root()
		self.simulator = Simulator(0, 0, 0, 0, 0)
		self.root.app = self
		return self.root
