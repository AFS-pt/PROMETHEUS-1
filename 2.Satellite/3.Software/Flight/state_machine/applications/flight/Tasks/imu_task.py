from Tasks.log import LogTask as Task
from pycubed import cubesat


class task(Task):
    name = 'imu'
    color = 'green'
    data_file = None

    async def main_task(self):
        """
        Prints the IMU data to the console.
        """
        if not cubesat.imu:
            return
        # take IMU readings
        readings = {
            'accel': cubesat.acceleration,
            'mag':   cubesat.magnetic,
            'gyro':  cubesat.gyro,
        }

        # store them in our cubesat data_cache object
        cubesat.data_cache.update({'imu': readings})

        # print the readings with some fancy formatting
        self.debug('IMU readings (x,y,z)')
        for imu_type in cubesat.data_cache['imu']:
            self.debug(f'{imu_type:>5} {cubesat.data_cache["imu"][imu_type]}', 2)
