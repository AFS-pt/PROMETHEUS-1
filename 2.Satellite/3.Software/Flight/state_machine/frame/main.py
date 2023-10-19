import sys
if '/lib' not in sys.path:
    sys.path.insert(0, './lib')

import traceback
from pycubed import cubesat
from state_machine import state_machine
from config import initial


print('Running...')
try:
    # should run forever
    state_machine.start(initial)
except Exception as e:
    formated_exception = traceback.format_exception(e, e, e.__traceback__)
    for line in formated_exception:
        print(line, end='')

    try:
        # increment our NVM error counter
        cubesat.c_state_err += 1
    except Exception:
        pass

# we shouldn't be here!
print('Engaging fail safe: hard reset')
# from time import sleep
# sleep(10)
# cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
# cubesat.micro.reset()
