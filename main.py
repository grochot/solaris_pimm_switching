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
from hardware.keithley2636_dummy import Keithley2600Dummy
from hardware.keithley2700 import Keithley2700
from hardware.keithley2700_dummy import Keithley2700Dummy
from hardware.keithley2400 import Keithley2400
from hardware.keithley2400_dummy import Keithley2400Dummy   
from logic.vector import Vector

from logic.save_parameters import SaveParameters

class SolarisMesurement(Procedure):
    parameters = {}
    save_parameter = SaveParameters()
    parameters_from_file = save_parameter.ReadFile()
    used_parameters_list=['sample','keithley_address', 'multimeter_address', 'sourcemeter_device' , 'pulse_time', 'pulse_delay', 'number_of_pulses', 'average', 'bias_voltage', 'compliance', 'nplc', 'vector_param', 'probe_1', 'probe_2', 'probe_3', 'probe_4', 'switch_source_plus', 'switch_source_minus', 'mode_source', 'mode_multimeter']
    
    #addressess of the instruments
    keithley_address = Parameter("Keithley address", default = parameters_from_file["keithley_address"]) 
    multimeter_address = Parameter("Multimeter address", default = parameters_from_file["multimeter_address"])
    sourcemeter_device = ListParameter("Sourcemeter device", choices=["Keithley 2600", "Keithley 2400", "none"], default = parameters_from_file["sourcemeter_device"])
    sample = Parameter("Sample", default = parameters_from_file["sample"])

    #pulse parameters
    pulse_time = FloatParameter("Pulse time", units="s", default = parameters_from_file["pulse_time"])
    pulse_delay = FloatParameter("Pulse delay", units="s", default = parameters_from_file["pulse_delay"])
    number_of_pulses = IntegerParameter("Number of pulses",default = parameters_from_file["number_of_pulses"])

    #masurement parameters
    bias_voltage = FloatParameter("Bias voltage", units="V", default = parameters_from_file["bias_voltage"])
    compliance= FloatParameter("Compliance", default = parameters_from_file["compliance"])
    nplc= FloatParameter("NPLC", default = parameters_from_file["nplc"])
    vector_param = Parameter("Pulse amplitude vector [start, step, stop]", default = parameters_from_file["vector_param"])
    average = IntegerParameter("Average", default = parameters_from_file["average"])


    #switch parameters
    probe_1 = ListParameter("A", choices=["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 7", "Col 8"], default = parameters_from_file["probe_1"])
    probe_2 = ListParameter("B", choices=["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 7", "Col 8"], default = parameters_from_file["probe_2"])
    probe_3 = ListParameter("C", choices=["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 7", "Col 8"], default = parameters_from_file["probe_2"])
    probe_4 = ListParameter("D", choices=[ "Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 7", "Col 8"], default = parameters_from_file["probe_2"])
    switch_source_plus= ListParameter("Switch source +", choices=["Row 1", "Row 2", "Row 3", "Row 4", "Row 5", "Row 6"], default = parameters_from_file["switch_source_plus"])
    switch_source_minus= ListParameter("Switch source -", choices=["Row 1", "Row 2", "Row 3", "Row 4", "Row 5", "Row 6"], default = parameters_from_file["switch_source_minus"])
    mode_source = ListParameter("Mode source", choices=["A->B", "A->C", "A->D", "B->C", "B->D", "C->D", "A,B->C,D", "A,D,->B,C"], default = parameters_from_file["mode_source"])
    mode_multimeter = ListParameter("Mode multimeter", choices=["A->C", "B->D", "A->B", "C->D"], default = parameters_from_file["mode_multimeter"])
    

    DATA_COLUMNS = ['Pulse Voltage (V)', 'Current (A)', 'Sense voltage (V)', 'Resistance (ohm)']

    def startup(self):
        for i in self.used_parameters_list:
            self.param = eval("self."+i)
            self.parameters[i] = self.param
        
        self.save_parameter.WriteFile(self.parameters)
        self.vector_obj = Vector()
        self.vector = self.vector_obj.generate_vector(self.vector_param)
        try:
            #Prepare keithley 
            if self.sourcemeter_device == "Keithley 2600":
                self.keithley = Keithley2600(self.keithley_address)
                #self.keithley.ChA.single_pulse_prepare(self.pulse_voltage, self.pulse_time, self.pulse_range)
                self.keithley.ChB.compliance_current = self.compliance
            else: 
                self.keithley = Keithley2400(self.keithley_address)
                self.keithley.source_mode("Voltage")
                self.keithley.source_voltage_range(20)
                self.keithley.compliance_current(self.compliance)
                self.keithley.voltage_nplc(self.nplc)
                self.keithley.measure_current()
                
            log.info("Sourcemeter connected")
        except Exception as e:
            print(e)
            self.keithley = Keithley2600Dummy()
            log.warning("Could not connect to the sourcemeter. Use dummy.")
            
        #Prepare multimeter
        try:
            self.multimeter = Keithley2700(self.multimeter_address)
            self.multimeter.open_all_channels()
            self.multimeter.set_voltage()
            self.multimeter.set_averaging(self.average)
            log.info("Multimeter connected")
            
        except:
            self.multimeter = Keithley2700Dummy()
            log.warning("Could not connect to the multimeter. Use dummy.")
    
    
    def execute(self):
        licznik = 0
        for i in self.vector:
            log.info("Close sourcemeter channel to probe")
            match self.mode_source:
                case "A->B":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_2[4:5]))
                case "A->C":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "A->D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "B->C":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "B->D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "C->D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_3[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "A,B->C,D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_4[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "A,D,->B,C":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
            sleep(1)
            log.info("Run voltage pulses")
            if self.sourcemeter_device == "Keithley 2600":
                self.keithley.ChB.pulse_script_v(0, i, self.pulse_time, self.pulse_delay, self.number_of_pulses, self.compliance )
                sleep(1)
            else: 
                self.keithley.pulse(self.pulse_time, i)
            log.info("End of pulses")
            sleep(0.5)
            self.multimeter.open_all_channels()
            self.multimeter.closed_channels("150")
            #self.multimeter.closed_channels("150")
            log.info("Close channels to measure")
            sleep(0.5)
            match self.mode_source:
                case "A->B":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_2[4:5]))
                case "A->C":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "A->D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "B->C":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "B->D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "C->D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_3[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                case "A,B->C,D":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_4[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
                case "A,D,->B,C":
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_4[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_minus[4:5]), int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(int(self.switch_source_plus[4:5]), int(self.probe_3[4:5]))
            sleep(1)
            match self.mode_multimeter:
                case "A->C":
                    self.multimeter.close_rows_to_columns(1,int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(1,int(self.probe_3[4:5]))
                    
                case "B->D":
                    self.multimeter.close_rows_to_columns(1,int(self.probe_2[4:5]))
                    self.multimeter.close_rows_to_columns(1,int(self.probe_4[4:5]))
                  
                case "A->B":
                    self.multimeter.close_rows_to_columns(1,int(self.probe_1[4:5]))
                    self.multimeter.close_rows_to_columns(1,int(self.probe_2[4:5]))
                   
                case "C->D":
                    self.multimeter.close_rows_to_columns(1,int(self.probe_3[4:5]))
                    self.multimeter.close_rows_to_columns(1,int(self.probe_4[4:5]))
                   
            sleep(0.5)
            log.info("Measure resistance")
            if self.sourcemeter_device == "Keithley 2600":
                self.keithley.ChB.measure_current(self.nplc,3,1)
                self.keithley.ChB.source_mode = "voltage"
                self.keithley.ChB.source_voltage = self.bias_voltage
                self.keithley.ChB.source_output = 'ON'
                sleep(0.4)
                self.current_sense = self.keithley.ChB.current   
                print(self.current_sense) 
            else:  
                self.keithley.source_voltage(self.bias_voltage)
                sleep(0.3)
                self.keithley.enable_source()
                sleep(0.3)
                self.current_sense = self.keithley.current()
                
            sleep(0.8)
            self.voltage_sense = self.multimeter.read()
            sleep(0.3)
            if self.sourcemeter_device == "Keithley 2600":
                self.keithley.ChB.shutdown()
            else:
                self.keithley.shutdown()
            
            self.multimeter.open_all_channels()
        

    
            data = {
                'Pulse Voltage (V)': float(i),
                'Current (A)': float(self.current_sense[0]),
                'Sense voltage (V)': float(self.voltage_sense),
                'Resistance (ohm)': float(self.voltage_sense)/float(self.current_sense[0])
                }
            self.emit('results', data)
            log.info("Step {} of {}".format(licznik, len(self.vector)))
            self.emit('progress', 100 * licznik / len(self.vector))
            
            licznik = licznik + 1
                    
            
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break

        #shutdown instruments 
        self.keithley.ChB.shutdown()   

    
    def shutdown(self):
        log.info("Finished")
        # self.keithley.ChB.shutdown()       
            

class MainWindow(ManagedDockWindow):

    def __init__(self):
        super().__init__(
            procedure_class=SolarisMesurement,
            inputs=['sample','keithley_address', 'multimeter_address', 'sourcemeter_device' , 'pulse_time', 'pulse_delay', 'number_of_pulses', 'average', 'bias_voltage', 'compliance', 'nplc', 'vector_param', 'probe_1', 'probe_2', 'probe_3', 'probe_4', 'switch_source_plus', 'switch_source_minus', 'mode_source', 'mode_multimeter'],
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