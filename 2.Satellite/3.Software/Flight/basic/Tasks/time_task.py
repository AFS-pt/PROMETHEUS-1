# print the time in seconds since boot every 20 seconds

from Tasks.template_task import Task
import time

class task(Task):
    priority = 4
    frequency = 1/20 # once every 20s
    name='time'
    color = 'white'

    async def main_task(self):
        t_since_boot = time.monotonic() - self.cubesat.BOOTTIME
        self.debug('{:.3f}s since boot'.format(t_since_boot))


