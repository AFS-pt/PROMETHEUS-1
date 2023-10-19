from Tasks.log import LogTask as Task
from lib.control import bcross
from pycubed import cubesat
import time
try:
    from ulab.numpy import array
except ImportError:
    from numpy import array


def toStr(arr):
    return f'[{", ".join(map(str, arr))}]'

class task(Task):
    name = 'detumble'
    color = 'pink'

    rgb_on = False
    last = None
    r_eci = array([6871, -6571, -7071])

    async def main_task(self):
        """
        Guidance, navigation and control task.

        Uses the b-cross control law to detumble the satelite.
        """

        # compute control
        m = bcross(cubesat.magnetic, cubesat.gyro)

        # replace with calls to pycubed lib once it is ready
        if hasattr(cubesat, 'sim') and cubesat.sim:  # detects if we are hooked up to simulator
            print(f">>>m{toStr(m)}")
            print(f">>>t{time.monotonic_ns()}")

        self.last = time.monotonic()
