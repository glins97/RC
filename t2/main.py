from src import simulator, receiver, sender

m = simulator.Simulator(0.05, # Error probability
                        1000000000, # 1Gbps or 125MBps
                        1, # Prop delay, half of rtt
                        0) # timeout -> not yet implemented
m.load("STOP_AND_WAIT")
m.run('1k')