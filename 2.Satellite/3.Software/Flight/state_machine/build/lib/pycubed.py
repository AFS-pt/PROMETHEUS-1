"""
CircuitPython driver for PyCubed-Mini
"""

import sdcardio
import pycubed_rfm9x_fsk
import board
import microcontroller
import busio
import digitalio
import analogio
import storage
import sys
import neopixel
import pwmio
import bmx160
import drv8830
import opt3001
from adafruit_pcf8523 import PCF8523
from bitflags import bitFlag, multiByte
import configuration.hardware_configuration as hw_config
import configuration.radio_configuration as rf_config
import adafruit_tsl2561
import adafruit_ina219
import time
import tasko
from ulab.numpy import array, dot
import supervisor

class device:
    """
    Based on the code from: https://docs.python.org/3/howto/descriptor.html#properties
    Attempts to return the appropriate hardware device.
    If this fails, it will attempt to reinitialize the hardware.
    If this fails again, it will raise an exception.
    """

    def __init__(self, fget=None):
        self.fget = fget
        self._device = None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError(f'unreadable attribute {self._name}')

        if self._device is not None:
            return self._device
        else:
            self._device = self.fget(instance)
            return self._device


"""
Define constants, Satellite attributes and Satellite Class
"""
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

    instance = None
    data_cache = {}

    # Satellite attributes
    LOW_VOLTAGE = 3.6  # needs to be higher than harvester IC VBAT_OK ON threshold
    # Max operating temp on specsheet for ATSAMD51J19A (Celsius)
    HIGH_TEMP = 125
    # Min operating temp on specsheet for ATSAMD51J19A (Celsius)
    LOW_TEMP = -40

    def __new__(cls):
        """
        Override the built-in __new__ function
        Ensure only one instance of this class can be made per process
        """
        if not cls.instance:
            cls.instance = object.__new__(cls)
            cls.instance = super(_Satellite, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """ Big init routine as the whole board is brought up. """
        self.BOOTTIME = int(time.monotonic())  # get monotonic time at initialization
        self.micro = microcontroller
        self.c_boot += 1  # increment boot count (can only do this after self.micro is set up)
        self.micro.on_next_reset(self.micro.RunMode.NORMAL)  # make sure it always resets in normal mode
        self._vbatt = analogio.AnalogIn(board.BATTERY)  # Battery voltage

        # To force initialization of hardware
        self.i2c1
        self.i2c2
        self.i2c3
        self.spi
        self.sdcard
        self.vfs
        self.neopixel
        self.imu
        self.rtc
        self.radio
        self.sun_xn
        self.sun_yn
        self.sun_zn
        self.sun_xp
        self.sun_yp
        self.sun_zp
        self.current_sensor
        self.drv_x
        self.drv_y
        self.drv_z
        self.burnwire1

    @device
    def i2c1(self):
        """ Initialize I2C1 bus """
        try:
            return busio.I2C(board.SCL1, board.SDA1)
        except Exception as e:
            print("[ERROR][Initializing I2C1]", e)

    @device
    def i2c2(self):
        """ Initialize I2C2 bus """
        try:
            return busio.I2C(board.SCL2, board.SDA2)
        except Exception as e:
            print("[ERROR][Initializing I2C2]", e)

    @device
    def i2c3(self):
        """ Initialize I2C3 bus """
        try:
            return busio.I2C(board.SCL3, board.SDA3)
        except Exception as e:
            print("[ERROR][Initializing I2C3]", e)

    def i2c(self, index):
        if index == 1:
            return self.i2c1
        if index == 2:
            return self.i2c2
        if index == 3:
            return self.i2c3

        raise ValueError("Invalid I2C Index")

    @device
    def spi(self):
        """ Initialize SPI bus """
        try:
            return busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        except Exception as e:
            print("[ERROR][Initializing SPI]", e)

    @device
    def sdcard(self):
        """ Define SD Parameters and initialize SD Card """
        try:
            return sdcardio.SDCard(self.spi, board.SD_CS, baudrate=4000000)
        except Exception as e:
            print('[ERROR][Initializing SD Card]', e)

    @device
    def vfs(self):
        try:
            vfs = storage.VfsFat(self.sdcard)
            storage.mount(vfs, "/sd")
            sys.path.append("/sd")
            return vfs
        except Exception as e:
            print('[ERROR][Initializing VFS]', e)

    @device
    def neopixel(self):
        """ Define neopixel parameters and initialize """
        try:
            led = neopixel.NeoPixel(
                board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            led[0] = (0, 0, 0)
            return led
        except Exception as e:
            print('[ERROR][Initializing Neopixel]', e)

    @device
    def imu(self):
        """ Define IMU parameters and initialize """
        try:
            if hw_config.IMU_TYPE == hw_config.IMU_TYPE_BMX160:
                return bmx160.BMX160_I2C(
                    self.i2c(hw_config.IMU_I2C),
                    address=hw_config.IMU_ADDRESS)
            elif hw_config.IMU_TYPE == hw_config.IMU_TYPE_BNO08X:
                return None
        except Exception as e:
            print(f'[ERROR][Initializing IMU] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def radio(self):
        """ Define radio parameters and initialize UHF radio """
        try:
            self._rf_cs = digitalio.DigitalInOut(board.RF_CS)
            self._rf_rst = digitalio.DigitalInOut(board.RF_RST)
            self.radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
            self.radio_DIO0.switch_to_input()
            self.radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
            self.radio_DIO1.switch_to_input()
            self._rf_cs.switch_to_output(value=True)
            self._rf_rst.switch_to_output(value=True)
        except Exception as e:
            print('[ERROR][Initializing Radio]', e)

        try:
            radio = pycubed_rfm9x_fsk.RFM9x(
                self.spi,
                self._rf_cs,
                self._rf_rst,
                rf_config.FREQUENCY,
                checksum=rf_config.CHECKSUM)

            radio.dio0 = self.radio_DIO0

            radio.tx_power = rf_config.TX_POWER
            radio.bitrate = rf_config.BITRATE
            radio.frequency_deviation = rf_config.FREQUENCY_DEVIATION
            radio.rx_bandwidth = rf_config.RX_BANDWIDTH
            radio.preamble_length = rf_config.PREAMBLE_LENGTH
            radio.ack_delay = rf_config.ACK_DELAY
            radio.ack_wait = rf_config.ACK_WAIT
            radio.ack_retries = rf_config.ACK_RETRIES
            radio.receive_timeout = rf_config.RECEIVE_TIMEOUT
            radio.node = rf_config.SATELLITE_ID
            radio.destination = rf_config.GROUNDSTATION_ID

            radio.sleep()
            return radio
        except Exception as e:
            print('[ERROR][Initializing RADIO]', e)

    @device
    def sun_yn(self):
        """ Initialize the -Y sun sensor """
        try:
            if hw_config.SUN_TYPE == hw_config.SUN_TYPE_TSL2561:
                return adafruit_tsl2561.TSL2561(
                    self.i2c(hw_config.SUN_YN_I2C),
                    address=hw_config.SUN_YN_ADDRESS)
            elif hw_config.SUN_TYPE == hw_config.SUN_TYPE_OPT3001:
                return opt3001.OPT3001(
                    self.i2c(hw_config.SUN_YN_I2C),
                    address=hw_config.SUN_YN_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Sun Sensor -Y] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def sun_zn(self):
        """ Initialize the -Z sun sensor """
        try:
            if hw_config.SUN_TYPE == hw_config.SUN_TYPE_TSL2561:
                return adafruit_tsl2561.TSL2561(
                    self.i2c(hw_config.SUN_ZN_I2C),
                    address=hw_config.SUN_ZN_ADDRESS)
            elif hw_config.SUN_TYPE == hw_config.SUN_TYPE_OPT3001:
                return opt3001.OPT3001(
                    self.i2c(hw_config.SUN_ZN_I2C),
                    address=hw_config.SUN_ZN_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Sun Sensor -Z] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def sun_xn(self):
        """ Initialize the -X sun sensor """
        try:
            if hw_config.SUN_TYPE == hw_config.SUN_TYPE_TSL2561:
                return adafruit_tsl2561.TSL2561(
                    self.i2c(hw_config.SUN_XN_I2C),
                    address=hw_config.SUN_XN_ADDRESS)
            elif hw_config.SUN_TYPE == hw_config.SUN_TYPE_OPT3001:
                return opt3001.OPT3001(
                    self.i2c(hw_config.SUN_XN_I2C),
                    address=hw_config.SUN_XN_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Sun Sensor -X] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def sun_yp(self):
        """ Initialize the +Y sun sensor """
        try:
            if hw_config.SUN_TYPE == hw_config.SUN_TYPE_TSL2561:
                return adafruit_tsl2561.TSL2561(
                    self.i2c(hw_config.SUN_YP_I2C),
                    address=hw_config.SUN_YP_ADDRESS)
            elif hw_config.SUN_TYPE == hw_config.SUN_TYPE_OPT3001:
                return opt3001.OPT3001(
                    self.i2c(hw_config.SUN_YP_I2C),
                    address=hw_config.SUN_YP_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Sun Sensor +Y] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def sun_zp(self):
        """ Initialize the +Z sun sensor """
        try:
            if hw_config.SUN_TYPE == hw_config.SUN_TYPE_TSL2561:
                return adafruit_tsl2561.TSL2561(
                    self.i2c(hw_config.SUN_ZP_I2C),
                    address=hw_config.SUN_ZP_ADDRESS)
            elif hw_config.SUN_TYPE == hw_config.SUN_TYPE_OPT3001:
                return opt3001.OPT3001(
                    self.i2c(hw_config.SUN_ZP_I2C),
                    address=hw_config.SUN_ZP_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Sun Sensor +Z] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def sun_xp(self):
        """ Initialize the +X sun sensor """
        try:
            if hw_config.SUN_TYPE == hw_config.SUN_TYPE_TSL2561:
                return adafruit_tsl2561.TSL2561(
                    self.i2c(hw_config.SUN_XP_I2C),
                    address=hw_config.SUN_XP_ADDRESS)
            elif hw_config.SUN_TYPE == hw_config.SUN_TYPE_OPT3001:
                return opt3001.OPT3001(
                    self.i2c(hw_config.SUN_XP_I2C),
                    address=hw_config.SUN_XP_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Sun Sensor +X] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def drv_x(self):
        """ Initialize Coil Driver X """
        try:
            return drv8830.DRV8830(
                self.i2c(hw_config.COIL_X_I2C),
                hw_config.COIL_X_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Coil X H-Bridge] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def drv_y(self):
        """ Initialize Coil Driver Y """
        try:
            return drv8830.DRV8830(
                self.i2c(hw_config.COIL_Y_I2C),
                hw_config.COIL_Y_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Coil Y H-Bridge] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def drv_z(self):
        """ Initialize Coil Driver Z """
        try:
            return drv8830.DRV8830(
                self.i2c(hw_config.COIL_Z_I2C),
                hw_config.COIL_Z_ADDRESS)
        except Exception as e:
            print(f'[ERROR][Initializing Coil Z H-Bridge] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def burnwire1(self):
        """ Initialize Burnwire1 on PA19 """
        # TODO: update firmware so we can use board.BURN1
        try:
            # changed pinout from BURN1 to PA19 (BURN1 did not support PWMOut)
            return pwmio.PWMOut(
                microcontroller.pin.PA19, frequency=1000, duty_cycle=0)
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC1]', e)

    @device
    def rtc(self):
        """ Initialize Real Time Clock """
        try:
            rtc = PCF8523(self.i2c(hw_config.RTC_I2C))
            rtc.high_capacitance = False
            if rtc.lost_power:
                restore_time = time.struct_time((2000, 0, 0, 0, 0, 0, 0, -1, -1))
                print(f"RTC lost power, RTC time = {rtc.datetime}, restoring to {restore_time}")
                rtc.datetime = restore_time
                self.f_datetime_valid = False
            return rtc
        except Exception as e:
            print(f'[ERROR][Initializing RTC] {e}, ' +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    @device
    def current_sensor(self):
        try:
            sensor = adafruit_ina219.INA219(
                self.i2c(hw_config.CURRENT_I2C),
                addr=hw_config.CURRENT_ADDRESS)
            """ Calibrate the current sensor for __V and ___mA """
            sensor.set_py4_calibration()
            return sensor
        except Exception as e:
            print(f"[ERROR][INITIALIZING CURRENT] {e}, " +
                  f'is HARDWARE_VERSION = {hw_config.HARDWARE_VERSION} correct?')

    def imuToBodyFrame(self, vec):
        return dot(hw_config.R_IMU2BODY, array(vec))

    @property
    def acceleration(self):
        """ return the accelerometer reading from the IMU in m/s^2 """
        return self.imuToBodyFrame(self.imu.accel) if self.imu else None

    @property
    def magnetic(self):
        """ return the magnetometer reading from the IMU in µT """
        return self.imuToBodyFrame(self.imu.mag) if self.imu else None

    @property
    def gyro(self):
        """ return the gyroscope reading from the IMU in deg/s """
        return self.imuToBodyFrame(self.imu.gyro) if self.imu else None

    @property
    def temperature_imu(self):
        """ return the thermometer reading from the IMU in celsius """
        return self.imu.temperature if self.imu else None

    @property
    def temperature_cpu(self):
        """ return the temperature reading from the CPU in celsius """
        return self.micro.cpu.temperature if self.micro else None

    def coildriver_vout(self, driver_index, projected_voltage):
        """ Set a given voltage for a given coil driver """
        if driver_index == "X" or driver_index == "U7":
            self.drv_x.throttle_volts = projected_voltage
        elif driver_index == "Y" or driver_index == "U8":
            self.drv_y.throttle_volts = projected_voltage
        elif driver_index == "Z" or driver_index == "U9":
            self.drv_z.throttle_volts = projected_voltage
        else:
            print(driver_index, "is not a defined coil driver")

    @property
    def battery_voltage(self):
        """
        Return the battery voltage
        _cubesat._vbatt.value converts the analog value of the
        board.BATTERY pin to a digital one. We read this value 50
        times and then later average it to get as close as possible
        to a reliable battery voltage value
        """

        # Handle an issue with the hardware where the 3V3 bus is
        # 3.0 volts when the solar harvester chips regulate the power,
        # and is 3.3 volts when the USB is powering the board.
        # This will not use the right reference voltage when a data-only
        # USB cable is connected, but it should work for regular
        # USB cables and when nothing is connected to the satellite.
        if supervisor.runtime.usb_connected:
            vref = 3.3
        else:
            vref = 3.05

        # initialize vbat
        vbat = 0

        # get the battery value 50 times
        for _ in range(50):
            # 65536 = 2^16, number of increments we can have to voltage
            vbat += self._vbatt.value * vref / 65536

        # vbat / 50 = average of all battery voltage values read
        # 100k/100k voltage divider
        voltage = (vbat / 50) * (100 + 100) / 100

        # volts
        return voltage

    @property
    def sun_vector(self):
        """Returns the sun pointing vector in the body frame"""
        return array(
            [self.sun_xp.lux - self.sun_xn.lux,
                self.sun_yp.lux - self.sun_yn.lux,
                self.sun_zp.lux - self.sun_zn.lux])

    async def burn(self, dutycycle=0.0031, duration=3):
        """
        Activates the burnwire for a given duration and dutycycle.

        :param dutycycle: The dutycycle of the burnwire, between 0 and 1
        :type dutycycle: float
        :param duration: The duration of the burn, in seconds
        :type duration: float

        :return: True if the burn was successful, False otherwise
        :rtype: bool
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

            self.f_burn = True
            return True
            # burnwire.deinit()  # deinitialize burnwire
        except Exception as e:
            print('[ERROR][Burning]', e)
            return False

    @property
    def RGB(self):
        return self.neopixel[0]

    @property
    def battery_current(self):
        """ return the current_sensor current reading in milliamps """
        return self.current_sensor.current if self.current_sensor else None

    @RGB.setter
    def RGB(self, v):
        self.neopixel[0] = v

    def timeon(self):
        """ return the time on a monotonic clock """
        return int(time.monotonic()) - self.BOOTTIME

    def clear_nvm(self):
        """Clear all non-volatile memory"""
        # Clearing all of NVM takes a long time, so only clear the first 1K
        size = min(len(microcontroller.nvm), 1024)
        for i in range(0, size):
            if microcontroller.nvm[i] != 0:
                microcontroller.nvm[i] = 0

    def enable_low_power(self):
        """ set all devices into lowest available power modes """
        self.burn(0.0, 0)

        if self.drv_x:
            self.drv_x.throttle_volts = None
        if self.drv_y:
            self.drv_y.throttle_volts = None
        if self.drv_z:
            self.drv_z.throttle_volts = None

        if self.imu:
            self.imu.accel_powermode = bmx160.BMX160_ACCEL_SUSPEND_MODE
            self.imu.gyro_powermode = bmx160.BMX160_GYRO_SUSPEND_MODE
            self.imu.mag_powermode = bmx160.BMX160_MAG_SUSPEND_MODE

        if self.radio:
            self.radio.sleep()

        self.RGB = (0, 0, 0)

        if self.sun_xn:
            self.sun_xn.enabled = False
        if self.sun_yn:
            self.sun_yn.enabled = False
        if self.sun_zn:
            self.sun_zn.enabled = False
        if self.sun_xp:
            self.sun_xp.enabled = False
        if self.sun_yp:
            self.sun_yp.enabled = False
        if self.sun_zp:
            self.sun_zp.enabled = False

    def disable_low_power(self):
        """ set all devices into normal power modes """
        # error occurs if gyro goes into normal mode before mag/accel
        if self.imu:
            self.imu.accel_powermode = bmx160.BMX160_ACCEL_NORMAL_MODE
            self.imu.mag_powermode = bmx160.BMX160_MAG_NORMAL_MODE
            self.imu.gyro_powermode = bmx160.BMX160_GYRO_NORMAL_MODE

        if self.radio:
            self.radio.idle()

        if self.sun_xn:
            self.sun_xn.enabled = True
        if self.sun_yn:
            self.sun_yn.enabled = True
        if self.sun_zn:
            self.sun_zn.enabled = True
        if self.sun_xp:
            self.sun_xp.enabled = True
        if self.sun_yp:
            self.sun_yp.enabled = True
        if self.sun_zp:
            self.sun_zp.enabled = True


# initialize Satellite as cubesat
cubesat = _Satellite()
