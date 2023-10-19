from Tasks.log import LogTask as Task
from pycubed import cubesat
from state_machine import state_machine


class task(Task):
    name = 'safety'
    color = 'orange'

    timeout = 60 * 60  # 60 min

    def debug_status(self, vbatt, temp):
        self.debug(f'Voltage: {vbatt:.2f}V | Temp: {temp:.2f}°C', log=True)

    def safe_mode(self, vbatt, temp):
        # Needs to be done here, and not in transition function due to #306
        cubesat.enable_low_power()
        # margins added to prevent jittering between states
        if vbatt < cubesat.LOW_VOLTAGE + 0.1:
            self.debug(f'Voltage too low ({vbatt:.2f}V < {cubesat.LOW_VOLTAGE + 0.1:.2f}V)', log=True)
        elif temp >= cubesat.HIGH_TEMP - 1:
            self.debug(f'Temp too high ({temp:.2f}°C >= {cubesat.HIGH_TEMP - 1:.2f}°C)', log=True)
        else:
            self.debug_status(vbatt, temp)
            self.debug(
                f'Safe operating conditions reached, switching back to {state_machine.previous_state} mode', log=True)
            state_machine.switch_to(state_machine.previous_state)

    def other_modes(self, vbatt, temp):
        if vbatt < cubesat.LOW_VOLTAGE:
            self.debug(f'Voltage too low ({vbatt:.2f}V < {cubesat.LOW_VOLTAGE:.2f}V) switch to safe mode', log=True)
            state_machine.switch_to('Safe')
        elif temp > cubesat.HIGH_TEMP:
            self.debug(f'Temp too high ({temp:.2f}°C > {cubesat.HIGH_TEMP:.2f}°C) switching to safe mode', log=True)
            state_machine.switch_to('Safe')
        else:
            self.debug_status(vbatt, temp)

    async def main_task(self):
        """
        If the voltage is too low or the temp is to high, switch to safe mode.
        If the voltage is high enough and the temp is low enough, switch to normal mode.
        """
        vbatt = cubesat.battery_voltage
        temp = cubesat.temperature_cpu
        if state_machine.state == 'Safe':
            self.safe_mode(vbatt, temp)
        else:
            self.other_modes(vbatt, temp)
