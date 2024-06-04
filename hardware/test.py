from keithley2636 import Keithley2600
from keithley2700 import Keithley2700
import pyvisa 

rm = pyvisa.ResourceManager()
print(rm.list_resources())

m = Keithley2700('GPIB0::18::INSTR')

print(m.get_state_of_channels(108))

#k.ChB.reset_smu()
#k.ChB.reset_buffer()

# k.ChB.single_pulse_prepare(1,10,4)  # dziala

# k.ChB.single_pulse_run() # działa

# k.ChB.config_pulse_v()

