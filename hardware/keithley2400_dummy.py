
import logging
import time

import numpy as np

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from pymeasure.instruments.keithley.buffer import KeithleyBuffer


class Keithley2400Dummy():
    def __init__(self, resourceName, **kwargs):
        pass
    source_mode = 1

    voltage_range = 1

    compliance_current = 1
        
    def enable_source(self):
        pass

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        pass
        
    current_range = 1
    compliance_voltage = 1

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        pass
   
    def shutdown(self):
        pass

    def config_average(self, average):
        pass
    source_voltage = 1
    
    source_current = 1
    
    current = 1
   
    voltage = 1
    
    filter_type = 1

    filter_count = 1
    
    means = 1
    measure_concurent_functions = 1

    def pulse(self,length, delay):
        pass

    def opc(self): 
        pass
    def reset(self):
        pass
    def beeper(self, state):
        pass


