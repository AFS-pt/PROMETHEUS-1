from lib.template_task import Task
from state_machine import state_machine


class task(Task):
    name = 'transition'
    color = 'blue'

    async def main_task(self):
        if state_machine.state == 'Normal':
            self.debug('Switching to Special mode')
            state_machine.switch_to('Special')
        else:
            self.debug('Switching to Normal mode')
            state_machine.switch_to('Normal')
