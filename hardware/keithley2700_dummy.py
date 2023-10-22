#
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

from pymeasure.instruments import Instrument

from .buffer import KeithleyBuffer

import numpy as np
import time

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def clist_validator(value, values):
    return np.random.rand(1)


def text_length_validator(value, values):
    return np.random.rand(1)


class Keithley2700Dummy(KeithleyBuffer, Instrument):
    """ Represents the Keithley 2700 Multimeter/Switch System and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2700("GPIB::1")

    """

    CLIST_VALUES = list(range(101, 300))

    # Routing commands
    closed_channels = 2

    open_channels = 2

    def set_voltage_measurement(self,channel):
        return np.random.rand(1)
    
    def reset(self):
        pass

    def read(self):
        return np.random.rand(1)


    def get_state_of_channels(self, channels):
        return np.random.rand(1)

    def open_all_channels(self):
        pass
    
   

    def __init__(self):
    
        self.check_errors()
        self.determine_valid_channels()

    def determine_valid_channels(self):
       pass

    def close_rows_to_columns(self, rows, columns, slot=None):
        pass

    def open_rows_to_columns(self, rows, columns, slot=None):
        pass

    def channels_from_rows_columns(self, rows, columns, slot=None):
        return np.random.rand(1)

    # system, some taken from Keithley 2400
    def beep(self, frequency, duration):
        pass

    def triad(self, base_frequency, duration):
        pass

    @property
    def error(self):
        code = 1
        message = "test"
        return (code, message)

    def check_errors(self):
        pass

    def reset(self):
        pass

    options = np.random.rand(1)

    ###########
    # DISPLAY #
    ###########

    text_enabled = Instrument.control(
        "DISP:TEXT:STAT?", "DISP:TEXT:STAT %d",
        """ A boolean property that controls whether a text message can be
        shown on the display of the Keithley 2700.
        """,
        values={True: 1, False: 0},
        map_values=True,
    )
    display_text = Instrument.control(
        "DISP:TEXT:DATA?", "DISP:TEXT:DATA '%s'",
        """ A string property that controls the text shown on the display of
        the Keithley 2700. Text can be up to 12 ASCII characters and must be
        enabled to show.
        """,
        validator=text_length_validator,
        values=12,
        cast=str,
        separator="NO_SEPARATOR",
        get_process=lambda v: v.strip("'\""),
    )

    def display_closed_channels(self):
        """ Show the presently closed channels on the display of the Keithley
        2700.
        """

        # Get the closed channels and make a string of the list
        channels = self.closed_channels
        channel_string = " ".join([
            str(channel % 100) for channel in channels
        ])

        # Prepend "Closed: " or "C: " to the string, depending on the length
        str_length = 12
        if len(channel_string) < str_length - 8:
            channel_string = "Closed: " + channel_string
        elif len(channel_string) < str_length - 3:
            channel_string = "C: " + channel_string

        # enable displaying text-messages
        self.text_enabled = True

        # write the string to the display
        self.display_text = channel_string
    
