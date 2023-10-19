# Transmit "Hello World" beacon

from Tasks.log import LogTask as Task
from pycubed import cubesat
import files
import logs
import time

class task(Task):
    name = 'beacon'
    color = 'teal'

    async def main_task(self):
        """
        Pushes a beacon packet onto the transmission queue.
        """
        if not cubesat.sdcard:
            return

        try:
            self.write_telemetry()
        except Exception:
            boot = cubesat.c_boot
            files.mkdirp(f'/sd/logs/telemetry/{boot:05}')
            self.write_telemetry()

    def write_telemetry(self):
        if cubesat.rtc:
            t = cubesat.rtc.datetime
        else:
            t = time.localtime()
        hour_stamp = f'{t.tm_year:04}.{t.tm_mon:02}.{t.tm_mday:02}.{t.tm_hour:02}'
        boot = cubesat.c_boot
        current_file = f"/sd/logs/telemetry/{boot:05}/{hour_stamp}"
        telemetry_packet = logs.telemetry_packet(t)
        file = open(current_file, "ab+")
        file.write(telemetry_packet)
        file.close()
