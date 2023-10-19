# Blink the RGB LED

from Tasks.log import LogTask as Task
from pycubed import cubesat
from state_machine import state_machine

MAX_BLINKS = None  # set to integer value to limit number of blinks per boot

class task(Task):
    name = 'blink'
    color = 'pink'

    rgb_on = False

    state_colors = [(0, 50, 50), (50, 0, 50), (0, 0, 10)]
    unknown_state_color = (30, 30, 30)
    blink_count = 0

    async def main_task(self):
        """
        Blinks the LED a color corresponding to the state machine state
        """
        if not cubesat.neopixel:
            self.debug('No neopixel attached, skipping blink task')
            return
        if self.rgb_on or (MAX_BLINKS is not None and self.blink_count > MAX_BLINKS):
            cubesat.RGB = (0, 0, 0)
            self.rgb_on = False
        else:
            state_index = state_machine.states.index(state_machine.state)
            if state_index < len(self.state_colors):
                cubesat.RGB = self.state_colors[state_index]
            else:
                cubesat.RGB = self.unknown_state_color
            self.rgb_on = True
            self.blink_count += 1
            if self.blink_count < 0:
                self.blink_count = 0
