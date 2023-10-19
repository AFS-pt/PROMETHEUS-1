# print the time in seconds since boot every 20 seconds

from lib.template_task import Task
from lib.pycubed import cubesat
import time


class task(Task):
    name = 'time'
    color = 'green'

    async def main_task(self):
        # Tasks also can import libraries like any other python file
        # So we can use this to show the uptime
        t_since_boot = time.monotonic() - cubesat.BOOTTIME
        self.debug(f'{t_since_boot:.3f}s since boot')
