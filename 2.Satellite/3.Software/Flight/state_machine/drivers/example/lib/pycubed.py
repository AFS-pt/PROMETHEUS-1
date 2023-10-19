import time

class Satellite:

    def __init__(self):
        self.acceleration = (0.0, 0.0, 0.0)
        self.magnetic = (0.0, 0.0, 0.0)
        self.gyro = (0.0, 0.0, 0.0)
        self.temperature_imu = 20.0
        self.battery_voltage = 6.4
        self.vlowbatt = 4.0
        self.BOOTTIME = time.monotonic()


cubesat = Satellite()
