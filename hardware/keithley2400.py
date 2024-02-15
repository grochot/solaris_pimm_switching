
import logging
import time

import numpy as np

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from pymeasure.instruments.keithley.buffer import KeithleyBuffer


class Keithley2400(Instrument):
    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "Keithley 2400",
            includeSCPI=True,
            **kwargs
        )
    source_mode = Instrument.control(
        ":SOUR:FUNC?", ":SOUR:FUNC %s",
        """ A string property that controls the source mode, which can
        take the values 'current' or 'voltage'. The convenience methods
        :meth:`~.Keithley2400.apply_current` and :meth:`~.Keithley2400.apply_voltage`
        can also be used. """,
        validator=strict_discrete_set,
        values={'CURR': 'CURR', 'VOLT': 'VOLT'},
        map_values=True
)

    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ A floating point property that controls the measurement voltage
        range in Volts, which can take values from -210 to 210 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-210, 210]
    )

    compliance_current = Instrument.control(
        ":SENS:CURR:PROT?", ":SENS:CURR:PROT %g",
        """ A floating point property that controls the compliance current
        in Amps. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )
        
    def enable_source(self):
        self.write("OUTPUT ON")

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -1.05 A to 1.05 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
       
        self.write(":SENS:FUNC 'CURR';"
                    ":SENS:CURR:NPLC %f;:FORM:ELEM CURR;" % nplc)
        if auto_range:
            self.write(":SENS:CURR:RANG:AUTO 1;")
        else:
            self.current_range = current
        self.check_errors()
        
    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ A floating point property that controls the measurement current
        range in Amps, which can take values between -1.05 and +1.05 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )

    compliance_voltage = Instrument.control(
        ":SENS:VOLT:PROT?", ":SENS:VOLT:PROT %g",
        """ A floating point property that controls the compliance voltage
        in Volts. """,
        validator=truncated_range,
        values=[-210, 210]
    )
    

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param voltage: Upper limit of voltage in Volts, from -210 V to 210 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        self.write(":SENS:FUNC 'VOLT';"
                    ":SENS:VOLT:NPLC %f;:FORM:ELEM VOLT;" % nplc)
        if auto_range:
            self.write(":SENS:VOLT:RANG:AUTO 1;")
        else:
            self.voltage_range = voltage
        self.check_errors()
   
    def shutdown(self):
        self.write("OUTPUT OFF")

    def config_average(self, average):
        # self.write(":SENSe:AVERage:TCONtrol REP")
        # self.write(":SENSe:AVERage:COUNt {}".format(average))
        self.write(":TRIG:COUN {}".format(average))

    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT:LEV %g",
        """ A floating point property that controls the source voltage
        in Volts. """
    )
    
    source_current = Instrument.control(
        ":SOUR:CURR?", ":SOUR:CURR:LEV %g",
        """ A floating point property that controls the source current
        in Amps. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )
    
    current = Instrument.measurement(
        ":READ?",
        """ Reads the current in Amps, if configured for this reading.
        """
    )
   
    voltage = Instrument.measurement(
        ":READ?",
        """ Reads the voltage in Volt, if configured for this reading.
        """
    )
    filter_type = Instrument.control(
        ":SENS:AVER:TCON?", ":SENS:AVER:TCON %s",
        """ A String property that controls the filter's type.
        REP : Repeating filter
        MOV : Moving filter""",
        validator=strict_discrete_set,
        values=['REP', 'MOV'],
        map_values=False)

    filter_count = Instrument.control(
        ":SENS:AVER:COUNT?", ":SENS:AVER:COUNT %d",
        """ A integer property that controls the number of readings that are
        acquired and stored in the filter buffer for the averaging""",
        validator=truncated_range,
        values=[1, 100],
        cast=int)
    
    means = Instrument.measurement(
        ":CALC3:DATA?;",
        """ Reads the calculated means (averages) for voltage,
        current, and resistance from the buffer data  as a list. """
    )
    measure_concurent_functions = Instrument.control(
        ":SENS:FUNC:CONC?", ":SENS:FUNC:CONC %d",
        """ A boolean property that enables or disables the ability to measure
        more than one function simultaneously. When disabled, volts function
        is enabled. Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    def pulse(self,length, delay):
        self.enable_source()
        time.sleep(length)
        self.shutdown()
        time.sleep(delay)

    def opc(self): 
        kk = self.ask("*OPC?")
        return kk
    def reset(self):
        self.write('*RST')

    def beeper(self, state):
        self.write(":SYSTem:BEEPer:STATe {}".format(str(state)))

# k = Keithley2400("GPIB0::24::INSTR")
# k.beeper(0)
# k.enable_source()