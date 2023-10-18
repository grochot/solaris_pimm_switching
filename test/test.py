from hardware.keithley2636 import Keithley2600

k = Keithley2600('TCPIP0::192.168.2.121::INSTR')


k.voltage_sweep_single_smu(smu=k.smua, smu_sweeplist=range(0, 61),t_int=0.1, delay=-1, pulsed=False)