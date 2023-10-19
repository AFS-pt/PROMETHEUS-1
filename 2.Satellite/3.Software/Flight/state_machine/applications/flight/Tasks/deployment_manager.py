"""
Manages deployment of the cubesat's antenna.

When contact is established with the groundstation
(f_contact is True, set by the radio task) the cubesat switches to normal mode.
If f_burn is false and the cubesat has been up for 5 minutes, the burnwire is activated.
Every 24 hours the cubesat activates the burn wire.
"""
from Tasks.log import LogTask as Task
from pycubed import cubesat
from state_machine import state_machine
import time


INITIAL_BURN_DELAY = 5 * 60
BURN_INTERVAL = 24 * 60 * 60

class deployment_manager(Task):
    name = 'deployment_manager'
    color = 'blue'

    rgb_on = False
    start_time = time.time()
    last_burn = float('inf')

    async def main_task(self):
        """
        Manages deployment by activating burnwires when appropriate,
        and switching to normal operations if contact is established.
        """
        if (cubesat.f_contact):
            self.debug('Contact with ground station has been already established, switching to Normal mode', log=True)
            state_machine.switch_to('Normal')
        elif self.should_burn():
            self.last_burn = time.time()
            self.debug(f'Starting burn, vbatt = {cubesat.battery_voltage}', log=True)
            if await cubesat.burn(duration=3, dutycycle=0.0031):
                cubesat.f_burn = True
                self.debug('Successfully burned', log=True)
            else:
                self.debug('Unsuccessful burn', log=True)
        else:
            vbatt = cubesat.battery_voltage
            if vbatt < cubesat.LOW_VOLTAGE:
                self.debug(f'Voltage too low ({vbatt:.2f}V < {cubesat.LOW_VOLTAGE:.2f}V) switch to safe mode', log=True)
                state_machine.switch_to('Safe')

    def should_burn(self):
        if (time.time() - self.start_time) >= INITIAL_BURN_DELAY and not cubesat.f_burn:  # first burn
            return True
        elif (time.time() - self.last_burn) >= BURN_INTERVAL:  # other burns
            return True
        return False
