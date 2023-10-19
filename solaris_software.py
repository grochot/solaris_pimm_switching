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
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from hardware.keithley2636 import Keithley2600

class RandomProcedure(Procedure):

    keithley_address = Parameter("Keithley address", default="GPIB::1::INSTR") 
    pulse_voltage = FloatParameter("Pulse voltage", units="V", default=0.1)
    pulse_time = FloatParameter("Pulse time", units="s", default=0.1)
    pulse_range = IntegerParameter("Pulse range", default=1)
    

    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Resistance (Ohm)']

    def startup(self):
        #Prepare keithley 
        self.keithley = Keithley2600(self.keithley_address)
        self.keithley.ChA.single_pulse_prepare(self.pulse_voltage, self.pulse_time, self.pulse_range) 



    def execute(self):
        log.info("Starting the loop of %d iterations" % self.iterations)
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                'Random Number 1': random.random(),
                'Random Number 2': random.random(),
                'Random Number 3': random.random()
            }
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            self.emit('progress', 100 * i / self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break


class MainWindow(ManagedDockWindow):

    def __init__(self):
        super().__init__(
            procedure_class=RandomProcedure,
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis=['Iteration', 'Random Number 1'],
            y_axis=['Random Number 1','Random Number 2', 'Random Number 3']
        )
        self.setWindowTitle('GUI Example')

    def queue(self):
        filename = tempfile.mktemp()

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())