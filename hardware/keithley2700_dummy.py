

import logging



import random
import numpy as np
import time
import pyvisa





class Keithley2700Dummy:
    def __init__(self):
        pass
        
   
    def closed_channels(self, channel):
        pass
    def open_all_channels(self):
        pass
    def open_channels(self, channel):
        pass

    def read(self):
        read = 1
        return read

    
    def opt(self):
        opt = 1
        return opt

    def pulse(self,time, channels):
        pass
    def set_diode(self): 
        pass
    def set_resistance(self): 
        pass
    def resistance(self):
        res = random.randint(1, 1000)
        return res
    def prepare_channels_source(self, channel=1):
        channel = channel[4:5]
        channel = str(100 + int(channel))
        return channel
    def prepare_channels_sense(self, channel=1):
        channel = channel[4:5]
        channel = str(108 + int(channel))
        return channel
    def close_to_mass(self):
        pass

    def pulse_level(self, level):
        pass

    #