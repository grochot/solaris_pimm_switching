

import logging




import numpy as np
import time
import pyvisa





class Keithley2700:
    def __init__(self, adapter):
        rm= pyvisa.ResourceManager()
        self.instrument = rm.open_resource(adapter)
        
    def set_home_reading_screen(self):
        self.instrument.write("DISP:CLE")
        self.instrument.write("DISP:SCR:HOME_LARG")

    def set_watching_channels(self, channel): 
        pass
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
        self.open_all_channels()
        self.instrument.write("ROUT:MULT:CLOS (@117,118,119,120,121,122,123,124)")
        print("All channels are closed to mass")

    def pulse_level(self, level):
        self.instrument.write("DIOD:BIAS:LEVel %s"%level)
    
    def set_resistance(self): 
        self.instrument.write("SENS:FUNC 'RES'")
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

    def close_rows_to_columns(self,row, column):
        self.number = str(str(100 + (row-1)*8 + column))
        self.instrument.write("ROUT:MULT:CLOS (@%s)"%self.number)
        time.sleep(0.2)
        return self.number


##### TEST #######

#k = Keithley2700("GPIB0::18::INSTR")
# k.open_all_channels()
# # from time import sleep
# k.closed_channels("125")
# k.closed_channels("138")
# k.closed_channels("103")
# # k.closed_channels("111")
# # k.closed_channels("116")
# k.closed_channels("108")
# k.closed_channels("150")
# # k.closed_channels("149")
# # k.closed_channels("127")
# # k.closed_channels("140")
# # k.set_averaging(10)
# k.set_resistance()
# k.set_averaging(3)
# time.sleep(2)
# print(k.read())

#print(k.close_rows_to_columns(5,6))

# # def close_rows_to_columns(row, column):
# #     number = str(100 + (row-1)*8 + column)
# #     return number

# # print(close_rows_to_columns(3,8))