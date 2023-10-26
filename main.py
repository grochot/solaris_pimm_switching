import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import tempfile
import random
from time import sleep
from pymeasure.display.windows import ManagedWindowBase
from pymeasure.display.widgets import TableWidget, LogWidget
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter, ListParameter, BooleanParameter, unique_filename

from hardware.keithley2700 import Keithley2700
from hardware.keithley2700_dummy import Keithley2700Dummy

from logic.vector import Vector

class SolarisMesurement(Procedure):
    #addressess of the instruments
   
    multimeter_address = Parameter("Multimeter address", default="GPIB::18::INSTR")
    sample = Parameter("Sample", default="Sample")
    mode = ListParameter("Mode", choices=["Pulse", "Mass", "Resistance"])

    #pulse parameters
    pulse_current = ListParameter("Pulse current", choices=["1e-05", "0.0001", "0.001", "0.01"])
    pulse_time = FloatParameter("Pulse time", units="s", default=0.1)

    #masurement parameters



    #switch parameters
    probe_1 = ListParameter("Probe 1", choices=["Col 1", "Col 2", "Col 3", "Col 4"])
    probe_2 = ListParameter("Probe 2", choices=["Col 1", "Col 2", "Col 3", "Col 4" ])
    probe_3 = ListParameter("Probe 3", choices=["Col 5", "Col 6", "Col 7", "Col 8"])
    probe_4 = ListParameter("Probe 4", choices=[ "Col 5", "Col 6", "Col 7", "Col 8"])
    mode_source = ListParameter("Pulse mode", choices=["1->2", "1->3", "1->4", "2->3", "2->4", "3->4", "1->2, 4->3", "1->4, 2->3"])
    mode_multimeter = ListParameter("Rxy mode", choices=[" 1->3", "2->4"])

    

    DATA_COLUMNS = ['Pulse Current (V)', 'Resistance (ohm)']

    def startup(self):
        #Prepare multimeter
            try:
                self.multimeter = Keithley2700(self.multimeter_address)
                if self.mode == "Pulse":
                    self.multimeter.open_all_channels()
                    sleep(0.5)
                    self.multimeter.closed_channels("149")
                    self.multimeter.closed_channels("150")
                    self.multimeter.pulse_level(self.pulse_current)
                    self.multimeter.set_diode()
                    log.info("Multimeter connected")
                elif self.mode == "Mass": 
                    self.multimeter.close_to_mass()
                elif self.mode == "Resistance":
                    self.multimeter.open_all_channels()
            except:
                self.multimeter = Keithley2700Dummy()
                log.error("Could not connect to the multimeter. Use dummy.")
    

    
    
    def execute(self):
        if self.mode == "Pulse":
            log.info("Close sourcemeter channel to probe")
            sleep(0.3)
            match self.mode_source:
                case "1->2":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_2))
                case "1->3":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_3))
                case "1->4":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_4))
                case "2->3":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_2))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_3))
                case "2->4":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_2))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_4))
                case "3->4":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_3))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_4))
                case "1->2, 4->3":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_2))
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_4))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_3))
                case "1->4, 2->3":
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_4))
                    self.multimeter.open_channels(self.multimeter.prepare_channels_source(self.probe_2))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_3))
            sleep(1)
            log.info("Run voltage pulses")
            match self.mode_source:
                case "1->2":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_1))
                case "1->3":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_1))
                case "1->4":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_1))
                case "2->3":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_2))
                case "2->4":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_2))
                case "3->4":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_3))
                case "1->2, 4->3":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_4))
                case "1->4, 2->3":
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.pulse(self.pulse_time, self.multimeter.prepare_channels_source(self.probe_2))
        
            log.info("End of pulses")
            sleep(1)
        if self.mode == "Pulse" or self.mode == "Resistance":
            self.multimeter.open_all_channels()
            sleep(1)
            self.multimeter.closed_channels("149")
            self.multimeter.closed_channels("150")
            sleep(1)
            self.multimeter.set_resistance()
            self.multimeter.set_averaging()
            sleep(1)
            log.info("Close channels to measure")
            match self.mode_multimeter:
                case "1->3":
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_sense(self.probe_1))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_sense(self.probe_3))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_2))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_4))
                    
                case "2->4":
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_sense(self.probe_2))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_sense(self.probe_4))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_1))
                    self.multimeter.closed_channels(self.multimeter.prepare_channels_source(self.probe_3))
                    

            log.info("Measure resistance")
            sleep(1)
            self.resistence = float(self.multimeter.read())
            #self.resistance = float(self.multimeter.resistance())
            
            sleep(1)
            
            #close all probes to mass
            self.multimeter.close_to_mass()
            sleep(1)
            
        


            data = {
                'Pulse Current (V)': float(self.pulse_current),
                'Resistance (ohm)': self.resistance
                }
            self.emit('results', data)
        
            #self.emit('progress', 100 * licznik / len(self.vector))
            # if self.step_by_step == True:
            #     answer = input("[{}%] Next step (y/n)?".format(100 * licznik / len(self.vector)))
            #     while answer != "y" and answer != "n":
            #         answer = input("Next step (y/n)?")
            #     if answer == "n":
            #         log.info("Loop break")
            #         self.should_stop()
            #         break
            #     elif answer == "y":
            #         licznik = licznik + 
            #         continue

            
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
        else: 
            pass
           

    def shutdown(self):
        log.info("Finished")     
            

class MainWindow(ManagedWindowBase):

    def __init__(self):
        widget_list = (TableWidget("Experiment Table",
                                    SolarisMesurement.DATA_COLUMNS,
                                    by_column=True,
                                    ),
                        LogWidget("Experiment Log"),
                        )
        super().__init__(
            procedure_class=SolarisMesurement,
            inputs=['sample', 'pulse_current','multimeter_address', 'pulse_time',  'probe_1', 'probe_2', 'probe_3', 'probe_4', 'mode_source', 'mode_multimeter'],
            displays=['sample'],
            directory_input=True,
            inputs_in_scrollarea=True,
            widget_list=widget_list
        )
        logging.getLogger().addHandler(widget_list[1].handler)
        log.setLevel(self.log_level)
        log.info("ManagedWindow connected to logging")
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