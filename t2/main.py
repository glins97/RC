#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gui.controller.root.app import T2

T2().run()

# from src import simulator, receiver, sender

# m = simulator.Simulator(
#     '10k',       # Message size
#     0,          # Error probability
#     125000000,  # 125MBps
#     15,         # Prop delay, half of rtt
#     0           # timeout -> not yet implemented
# )

# # m.load("STOP_AND_WAIT")
# m.load("SELECTIVE_REPEAT", 200, 400, 0)
# m.run()