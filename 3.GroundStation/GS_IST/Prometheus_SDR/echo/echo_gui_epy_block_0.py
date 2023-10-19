"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr

import pmt
import time

textboxValue = ""

class my_sync_block(gr.sync_block):
    """
    reads input from a message port
    outputs text
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name = "Echo Silencer",
            in_sig = None,
            out_sig = [np.float32])
        self.message_port_register_in(pmt.intern('msg_in'))
        self.message_port_register_out(pmt.intern('enable'))
        self.set_msg_handler(pmt.intern('msg_in'), self.handle_msg)

    def handle_msg(self, msg):
        global textboxValue

        textboxValue = pmt.symbol_to_string (msg)
        # print (textboxValue)
    
    def work(self, input_items, output_items):
        global textboxValue

        # get length of string
        _len = len(textboxValue)
        if (_len > 0):
            # terminate with LF
            textboxValue += "\n"
            _len += 1
            # store elements in output array
            for x in range(_len):
                output_items[0][x] = ord(textboxValue[x])
            textboxValue = ""
            self.message_port_pub(pmt.intern('enable'), pmt.to_pmt(False))

            time.sleep(2)
            self.message_port_pub(pmt.intern('enable'), pmt.to_pmt(True))

            return (_len)
        else:
            return (0)