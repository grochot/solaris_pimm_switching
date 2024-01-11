

import logging




import numpy as np
import time
import pyvisa





class Keithley2700:
    def __init__(self, adapter):
        rm= pyvisa.ResourceManager()
        self.instrument = rm.open_resource(adapter)
        
   
    def closed_channels(self, channel):
        self.instrument.write("ROUT:MULT:CLOS (@%s)"%channel)
    def open_all_channels(self):
        self.instrument.write("ROUT:OPEN:ALL")
    def open_channels(self, channel):
        self.instrument.write("ROUT:MULT:OPEN (@%s)"%channel)

    def read(self):
        read = self.instrument.query("READ?")
        return read

    
    def opt(self):
        opt = self.instrument.query("*OPT?")
        return opt

    def pulse(self,time, channels):
        self.instrument.write("ROUT:MULT:CLOS (@%s)"%channels)
        time.sleep(time)
        self.instrument.write("ROUT:MULT:OPEN (@%s)"%channels)
    def set_diode(self): 
        self.instrument.write("SENS:FUNC 'DIOD'")
    def set_resistance(self): 
        self.instrument.write("SENS:FUNC 'FRES'")
    def resistance(self):
        res = self.instrument.query("MEAS:FRES?")
        return res
    def prepare_channels_source(self, channel):
        channel = channel[4:5]
        channel = str(100 + int(channel))
        return channel
    def prepare_channels_sense(self, channel):
        channel = channel[4:5]
        channel = str(108 + int(channel))
        return channel
    def close_to_mass(self):
        self.instrument.write("ROUT:MULT:CLOS (@141,142,143,144,145,146,147,148,149,150)")

    def pulse_level(self, level):
        self.instrument.write("DIOD:BIAS:LEVel %s"%level)
    
    def set_resistance(self): 
        self.instrument.write("SENS:FUNC 'FRES'")
        # time.sleep(0.5)
        # self.instrument.write("SENS:FRES:NPLC 1")
    def set_voltage(self):
        self.instrument.write("SENS:FUNC 'VOLT'")

    def set_averaging(self, aver):
        self.instrument.write("SENS:VOLT:AVER:COUNT {}".format(aver))
        time.sleep(0.3)
        self.instrument.write("SENS:VOLT:AVER:TCON REP")
        time.sleep(0.3)
        self.instrument.write("SENS:VOLT:AVER ON")

    def resistance(self):
        res = self.instrument.query("MEAS:FRES?")
        return res



k = Keithley2700("GPIB::18::INSTR")
from time import sleep
k.closed_channels("101")
k.set_averaging(10)
k.set_voltage()
# sleep(2)
print(k.read())