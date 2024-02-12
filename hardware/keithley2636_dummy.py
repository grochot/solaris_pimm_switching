# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
import time
import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2600Dummy(Instrument):
    """Represents the Keithley 2600 series (channel A and B) SourceMeter"""

    def __init__(self):
        self.ChA = Channel(self, 'a')
        self.ChB = Channel(self, 'b')

    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        code = "test"
        message = "test"
        return (code, message)

    def check_errors(self):
       pass


class Channel:

    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel

    def ask(self, cmd):
        return np.random.rand(1)
    
    def askall(self, cmd):
        return np.random.rand(1)

    def write(self, cmd):
        pass
    
    def writeall(self, cmd):
        pass

    def values(self, cmd, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return np.random.rand(1)

    def binary_values(self, cmd, header_bytes=0, dtype=np.float32):
        return np.random.rand(1)

    def check_errors(self):
        return np.random.rand(1)

    source_output = 2

    source_mode = 2

    measure_nplc = 2

    ###############
    # Current (A) #
    ###############
    current = np.random.rand(1)

    source_current = 2

    compliance_current = 2

    source_current_range = 2

    current_range = 2

    ###############
    # Voltage (V) #
    ###############
    voltage = np.random.rand(1)

    source_voltage = 2

    compliance_voltage = 2

    source_voltage_range = 2

    voltage_range = 2

    ####################
    # Resistance (Ohm) #
    ####################
    resistance = np.random.rand(1)

    wires_mode = 2

    #######################
    # Measurement Methods #
    #######################

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        pass

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        pass
    
    def single_pulse_prepare(self, voltage, time, range):
        pass
        
    def single_pulse_run(self):
        pass

    def pulse_script_v(self, bias, level, ton, toff, points, limiti): 
        pass 
    
    def pulse_script_i(self): 
        pass
    def pulse_script_read_i(self):
        pass
    
    def pulse_script_read_v(self):
        pass

    def config_pulse_v(self):
        pass
    def config_pulse_i(self):
        pass

    def start_pulse(self):
        pass
    
    def reset_buffer(self):
        pass

    def reset_smu(self):
        pass

    def auto_range_source(self, ss):
       pass

    def apply_current(self, current_range=None, compliance_voltage=0.1):
       pass
    def apply_voltage(self, voltage_range=None, compliance_current=0.1):
       pass

    def ramp_to_voltage(self, target_voltage, steps=30, pause=0.1):
        pass

    def ramp_to_current(self, target_current, steps=30, pause=0.1):
       pass

    def shutdown(self):
       pass