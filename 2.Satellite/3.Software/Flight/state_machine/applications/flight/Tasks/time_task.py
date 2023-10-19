# print the time in seconds since boot every 20 seconds

from Tasks.log import LogTask as Task
from pycubed import cubesat
import time
import gc


class task(Task):
    name = 'time'
    color = 'white'

    async def main_task(self):
        t_since_boot = time.monotonic() - cubesat.BOOTTIME
        self.debug('{:.3f}s since boot'.format(t_since_boot))
        gc.collect()
        try:
            self.debug(f"{gc.mem_free()} free bytes in memory")
        except Exception as e:
            self.debug(f"Couldn't get free memory: {e}")
