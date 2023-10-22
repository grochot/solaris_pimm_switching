import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import tempfile
import random
from time import sleep
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter, ListParameter, BooleanParameter, unique_filename
from hardware.keithley2636 import Keithley2600
from hardware.keithley2700 import Keithley2700
from logic.vector import Vector

class RandomProcedure(Procedure):
    #addressess of the instruments
    keithley_address = Parameter("Keithley address", default="GPIB::26::INSTR") 
    multimeter_address = Parameter("Multimeter address", default="GPIB::18::INSTR")
    sample = Parameter("Sample", default="Sample")

    #pulse parameters
    pulse_voltage = FloatParameter("Pulse voltage", units="V", default=0.1)
    pulse_time = FloatParameter("Pulse time", units="s", default=0.1)
    pulse_delay = FloatParameter("Pulse delay", units="s", default=0.1)
    pulse_range = IntegerParameter("Pulse range", default=1)
    number_of_pulses = IntegerParameter("Number of pulses", default=1)

    #masurement parameters
    bias_voltage = FloatParameter("Bias voltage", units="V", default=0.1)
    compliance= FloatParameter("Compliance", default=0.1)
    nplc= FloatParameter("NPLC", default=0.1)
    range= FloatParameter("Range", default=0.1)
    vector_param = Parameter("Vector")


    #switch parameters
    probe_1 = ListParameter("Probe 1", choices=["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col6", "Col 7", "Col 8"])
    probe_2 = ListParameter("Probe 2", choices=["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col6", "Col 7", "Col 8"])
    probe_3 = ListParameter("Probe 3", choices=["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col6", "Col 7", "Col 8"])
    probe_4 = ListParameter("Probe 4", choices=["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col6", "Col 7", "Col 8"])
    switch_source_plus= ListParameter("Switch source +", choices=["Row 1", "Row 2", "Row 3", "Row 4", "Row 5", "Row 6"])
    switch_source_minus= ListParameter("Switch source -", choices=["Row 1", "Row 2", "Row 3", "Row 4", "Row 5", "Row 6"])
    mode_source = ListParameter("Mode", choices=["1->2", "1->3", "1->4", "2->3", "2->4", "3->4", "1->2, 4->3", "1->4, 2->3"])
    mode_multimeter = ListParameter("Mode", choices=[" 1->3", "2->4"])
    step_by_step = BooleanParameter("Step by step", default=False)
    

    DATA_COLUMNS = ['Pulse Voltage (V)', 'Current (A)', 'Sense voltage (V)', 'Resistance (ohm)']

    def startup(self):
        self.vector_obj = Vector()
        self.vector = self.vector_obj.generate_vector(self.vector_param)
        try:
            #Prepare keithley 
            self.keithley = Keithley2600(self.keithley_address)
            self.keithley.ChA.single_pulse_prepare(self.pulse_voltage, self.pulse_time, self.pulse_range) 

            #Prepare multimeter
            self.multimeter = Keithley2700(self.multimeter_address)
            log.info("Intruments connected")
        except:
            log.error("Could not connect to the instruments")
        
    
    def execute(self):
        for i in self.vector:
            log.info("Close sourcemeter channel to probe")
            match self.mode_source:
                case "1->2":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_2[4:5]))
                case "1->3":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "1->4":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "2->3":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "2->4":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "3->4":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_3[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "1->2, 4->3":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_4[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "1->4, 2->3":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
            sleep(1)
            log.info("Run voltage pulses")
            self.keithley.ChB.pulse_script_v(0, i, self.pulse_time, self.pulse_delay, self.number_of_pulses, self.compliance )
            sleep(1)
            log.info("End of pulses")
            self.multimeter.open_all_channels()
            log.info("Close channels to measure")
            match self.mode_multimeter:
                case "1->3":
                    self.multimeter.close_rows_to_columns(int(1,int(self.probe_1[4:5])))
                    self.multimeter.close_rows_to_columns(int(1,int(self.probe_3[4:5])))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                    self.multimeter.set_voltage_measurement([self.multimeter.channels_from_rows_columns(int(1,int(self.probe_1[4:5]))), self.multimeter.channels_from_rows_columns(int(1,int(self.probe_3[4:5])))])
                case "2->4":
                    self.multimeter.close_rows_to_columns(int(1,int(self.probe_2[4:5])))
                    self.multimeter.close_rows_to_columns(int(1,int(self.probe_4[4:5])))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                    self.multimeter.set_voltage_measurement([self.multimeter.channels_from_rows_columns(int(1,int(self.probe_2[4:5]))), self.multimeter.channels_from_rows_columns(int(1,int(self.probe_4[4:5])))])

            log.info("Measure resistance")
            self.keithley.ChB.measure_current(self.nplc, self.range,1)
            self.keithley.ChB.source_mode = "voltage"
            self.keithley.ChB.source_voltage = self.bias_voltage
            self.keithley.ChB.source_output = True
            sleep(0.4)
            self.current_sense = self.keithley.ChB.current    
            self.voltage_sense = self.multimeter.read()
            self.keithley.ChB.shutdown()
            self.multimeter.open_all_channels()

    
            data = {
                'Pulse Voltage (V)': self.pulse_voltage,
                'Current (A)': self.current_sense,
                'Sense voltage (V)': self.voltage_sense,
                'Resistance (Ohm)': self.voltage_sense/self.current_sense
                }
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            self.emit('progress', 100 * i / self.iterations)
            if self.step_by_step == True:
                answer = input("Next step (y/n)?")
                while answer != "y" and answer != "n":
                    if answer == "n":
                        log.info("Loop break")
                        self.should_stop|()
                    elif answer == "y":
                        continue
                    else:
                        answer = input("Next step (y/n)?")
            
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break
    
    def shutdown(self):
        log.info("Finished")
        self.keithley.ChB.shutdown()       
            

class MainWindow(ManagedDockWindow):

    def __init__(self):
        super().__init__(
            procedure_class=RandomProcedure,
            inputs=['sample', 'pulse_voltage', 'pulse_time', 'pulse_range', 'pulse_delay', 'number_of_pulses', 'bias_voltage', 'compliance', 'nplc', 'range', 'vector_param', 'probe_1', 'probe_2', 'probe_3', 'probe_4', 'switch_source_plus', 'switch_source_minus', 'mode_source', 'mode_multimeter', 'step_by_step'],
            displays=['sample'],
            x_axis=['Pulse Voltage (V)', 'Current (A)'],
            y_axis=['Pulse Voltage (V)', 'Resistance (ohm)'],
            directory_input=True,
            inputs_in_scrollarea=True,
        )
        self.setWindowTitle('Solaris Measurement')
        self.directory = r'C:/Path/'

    def queue(self):
        directory = self.directory                               # Added line
                         # Modified line

        procedure = self.make_procedure()
        name_of_file = procedure.sample
        filename = unique_filename(directory, prefix="{}_".format(name_of_file)) 
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())