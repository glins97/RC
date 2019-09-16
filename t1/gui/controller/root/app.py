#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config
from .root import T1Root
from src.client import Client

class T1(App):
	def build(self):
		Config.set('graphics', 'width', '690')
		Config.set('graphics', 'height', '340')

		self.root = T1Root()
		self.client = Client('nombregag@gmail.com', 'mmw835601')
		
		self.root.app = self
		self.client.app = self
		return self.root
