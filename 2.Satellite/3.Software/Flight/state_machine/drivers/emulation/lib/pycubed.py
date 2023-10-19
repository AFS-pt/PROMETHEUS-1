import time
import tasko

import lib.reader as reader
from lib.bitflags import bitFlag, multiByte, nvm
from lib.radio_driver import Radio
from lib.sd import SD
import random
try:
    from ulab.numpy import array
except ImportError:
    from numpy import array

class Burnwire:
    def __init__(self):
        pass

    def duty_cycle(self, duty_cycle):
        assert 0 <= duty_cycle <= 0xffff


"""
Define HardwareInitException
"""
class HardwareInitException(Exception):
    pass

class rtc_device:
    def __init__(self, date_input):
        self.datetime = date_input

    def update_time(self, date_input):
        self.datetime = date_input

class sun_sensor:
    def __init__(self, lux):
        self.lux = lux

class _Satellite:
    # Define NVM flags
    f_contact = bitFlag(register=0, bit=1)
    f_burn = bitFlag(register=0, bit=2)
    f_datetime_valid = bitFlag(register=0, bit=3)

    # Define NVM counters
    c_boot = multiByte(num_bytes=2, lowest_register=1)
    c_software_error = multiByte(num_bytes=1, lowest_register=3)
    c_downlink = multiByte(num_bytes=4, lowest_register=4)
    c_uplink = multiByte(num_bytes=4, lowest_register=8)

    tasko = None
    _RGB = (0, 0, 0)
    vlowbatt = 4.0
    BOOTTIME = time.monotonic()
    data_cache = {}

    # Max opperating temp on specsheet for ATSAMD51J19A (Celsius)
    HIGH_TEMP = 125
    # Min opperating temp on specsheet for ATSAMD51J19A (Celsius)
    LOW_TEMP = -40
    # Low battery voltage threshold
    LOW_VOLTAGE = 4.0

    def __init__(self):
        self.f_contact = True
        self.task = None
        self.scheduled_tasks = {}

        self.radio = Radio()
        self.burnwire1 = Burnwire()

        self.data_cache = {}

        # magnetometer and accelerometer chosen to be arbitrary non zero, non parallel values
        # to provide more interesting output from the b-cross controller.
        self._accel = array([1.0, 2.0, 3.0])
        self._mag = array([4.0, 3.0, 1.0])
        self._gyro = array([0.0, 0.0, 0.0])
        self._torque = [0, 0, 0]
        self._cpu_temp = 30
        self._imu_temperature = 20
        self._luxp = array([3.0, 1.0, 2.0])
        self._luxn = array([2.0, 4.0, 7.0])

        # debug utilities
        self.sim = False
        self.randomize_voltage = False
        self.sdcard = SD()
        self.vfs = None

    @property
    def acceleration(self):
        """ return the accelerometer reading from the IMU """
        reader.read(self)
        return self._accel

    @property
    def magnetic(self):
        """ return the magnetometer reading from the IMU """
        reader.read(self)
        return self._mag

    @property
    def gyro(self):
        """ return the gyroscope reading from the IMU """
        reader.read(self)
        return self._gyro

    @property
    def temperature_imu(self):
        """ return the thermometer reading from the IMU """
        reader.read(self)
        return self._imu_temperature

    @property
    def temperature_cpu(self):
        """ return the temperature reading from the CPU in celsius """
        return self._cpu_temp

    @property
    def RGB(self):
        return self._RGB

    @RGB.setter
    def RGB(self, v):
        self._RGB = v

    @property
    def battery_voltage(self):
        reader.read(self)
        random_offset = - 0.5 + random.random() if self.randomize_voltage else 0
        return self.LOW_VOLTAGE + 0.01 + random_offset

    def log(self, str):
        """Logs to sd card"""
        str = (str[:20] + '...') if len(str) > 23 else str
        print(f'log not implemented, tried to log: {str}')

    @property
    def imu(self):
        return True

    @property
    def sun_vector(self):
        """returns the sun pointing vector in the body frame"""
        return array([self._luxp[0] - self._luxn[0],
                      self._luxp[1] - self._luxn[1],
                      self._luxp[2] - self._luxn[2]])

    @property
    def micro(self):
        return True

    @property
    def neopixel(self):
        return True

    @property
    def rtc(self):
        return rtc_device(time.localtime())

    @property
    def sun_yn(self):
        return sun_sensor(self._luxn[1])

    @property
    def sun_zn(self):
        return sun_sensor(self._luxn[2])

    @property
    def sun_xn(self):
        return sun_sensor(self._luxn[0])

    @property
    def sun_yp(self):
        return sun_sensor(self._luxp[1])

    @property
    def sun_zp(self):
        return sun_sensor(self._luxp[2])

    @property
    def sun_xp(self):
        return sun_sensor(self._luxp[0])

    async def burn(self, dutycycle=0.5, duration=1):
        """
        Activates the burnwire for a given duration and dutycycle.
        """
        try:
            burnwire = self.burnwire1
            self.RGB = (255, 0, 0)

            # set the burnwire's dutycycle; begins the burn
            burnwire.duty_cycle = int(dutycycle * (0xFFFF))
            await tasko.sleep(duration)  # wait for given duration

            # set burnwire's dutycycle back to 0; ends the burn
            burnwire.duty_cycle = 0
            self.RGB = (0, 0, 0)

            self._deployA = True  # sets deployment variable to true
            return True
        except Exception as e:
            print('[ERROR][Burning]', e)
            return False

    def clear_nvm(self):
        """ clear all non volatile memory """
        for i in range(len(nvm)):
            nvm[i] = 0

    def enable_low_power(self):
        """ set all devices into lowest available power modes """
        pass

    def disable_low_power(self):
        """ set all devices into normal power modes """
        pass


cubesat = _Satellite()
