"""
CircuitPython driver for PyCubed satellite board

PyCubed Mini mainboard-v02 for Pocketqube Mission

* Author(s): Max Holliday

"""

import sdcardio
import pycubed_rfm9x
import board
import microcontroller
import busio
import time
import digitalio
import analogio
import storage
import sys
import pulseio
import neopixel
import bmx160
import drv8830
from os import listdir, stat, statvfs, mkdir
from bitflags import bitFlag, multiBitFlag
from micropython import const
import adafruit_tsl2561

'''
TODO: implement backup import
------------------------------
imports = ['sys', 'os', 'miconctroller']
modules = []
for x in imports:
    try:
        modules.append(__import__(x))
        print("Successfully imported ", x)
    except ImportError:
        print("Error importing ", x)
'''

# NVM register numbers
# TODO: confirm registers start in MRAM partition & update board build file
_FLAG = const(20)
_DWNLINK = const(4)
_DCOUNT = const(3)
_RSTERRS = const(2)
_BOOTCNT = const(0)
_GSRSP = const(10)

class Satellite:
    # Define NVM flags
    f_deploy   = bitFlag(register=_FLAG, bit=1)
    f_mdeploy  = bitFlag(register=_FLAG, bit=2)
    f_burn1    = bitFlag(register=_FLAG, bit=3)
    f_burn2    = bitFlag(register=_FLAG, bit=4)

    # Define NVM counters
    c_boot       = multiBitFlag(register=_BOOTCNT, lowest_bit=0, num_bits=8)
    c_state_err  = multiBitFlag(register=_RSTERRS, lowest_bit=4, num_bits=4)
    c_vbus_rst   = multiBitFlag(register=_RSTERRS, lowest_bit=0, num_bits=4)
    c_deploy     = multiBitFlag(register=_DCOUNT,  lowest_bit=0, num_bits=8)
    c_downlink   = multiBitFlag(register=_DWNLINK, lowest_bit=0, num_bits=8)
    c_gs_resp    = multiBitFlag(register=_GSRSP,   lowest_bit=0, num_bits=8)

    UHF_FREQ = 433.0

    def __init__(self):
        """
        Big init routine as the whole board is brought up.
        """
        self._stat = {}
        self.BOOTTIME = const(self.timeon)
        self.hardware = {
            'IMU':    False,
            'Radio':  False,
            'SDcard': False,
            'GPS':    False,
            'WDT':    False,
            'Sun':    False,
            'Coils':  False
        }
        self.micro = microcontroller

        self.data_cache = {}
        self.filenumbers = {}
        self.vlowbatt = 3.5
        self.debug = True

        # Define battery voltage
        self._vbatt = analogio.AnalogIn(board.BATTERY)

        # Define SPI,I2C,UART
        self.i2c1  = busio.I2C(board.SCL1, board.SDA1)
        self.i2c2  = busio.I2C(board.SCL2, board.SDA2)
        self.i2c3  = busio.I2C(board.SCL3, board.SDA3)
        # self.spi   = busio.SPI(board.SCK,MOSI=board.MOSI,MISO=board.MISO)
        self.spi   = board.SPI()

        # Define sdcard
        self.filename = "/sd/default.txt"
        self.logfile = "/sd/logs/log000.txt"

        # Define radio
        self._rf_cs = digitalio.DigitalInOut(board.RF_CS)
        self._rf_rst = digitalio.DigitalInOut(board.RF_RST)
        self.radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
        self.radio_DIO0.switch_to_input()
        self.radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
        self.radio_DIO1.switch_to_input()
        self._rf_cs.switch_to_output(value=True)
        self._rf_rst.switch_to_output(value=True)

        # Initialize Neopixel
        try:
            self.neopixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            self.neopixel[0] = (0, 0, 0)
            self.hardware['Neopixel'] = True
        except Exception as e:
            print('[WARNING][Neopixel]', e)

        # Initialize sdcard
        try:
            self._sd   = sdcardio.SDCard(self.spi, board.CS_SD, baudrate=4000000)
            self._vfs = storage.VfsFat(self._sd)
            storage.mount(self._vfs, "/sd")
            sys.path.append("/sd")
            self.hardware['SDcard'] = True
            # self.new_Log() # create new log file
        except Exception as e:
            print('[ERROR][SD Card]', e)

        # Initialize radio #1 - UHF
        try:
            self.radio = pycubed_rfm9x.RFM9x(self.spi, self._rf_cs, self._rf_rst, self.UHF_FREQ, rfm95pw=True)
            self.radio.dio0 = self.radio_DIO0
            self.radio.sleep()
            self.hardware['Radio'] = True
        except Exception as e:
            print('[ERROR][RADIO]', e)

        # Initialize IMU
        try:
            self.IMU = bmx160.BMX160_I2C(self.i2c1, address=0x68)
            self.hardware['IMU'] = True
        except Exception as e:
            print(f'[ERROR][IMU] {e}\n\tMaybe try address=0x68?')

        # Initialize Sun Sensors
        try:
            sun_yn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x29)  # -Y
            sun_zn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x39)  # -Z
            sun_xn = adafruit_tsl2561.TSL2561(self.i2c1, address=0x49)  # -X

            sun_yp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x29)  # +Y
            sun_zp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x39)  # +Z
            sun_xp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x49)  # +X
            sun_sensors = [sun_zn, sun_yn, sun_xn, sun_yp, sun_xp]
            for i in sun_sensors:
                i.enabled = False
            self.hardware['Sun'] = True
        except Exception as e:
            print('[ERROR][Sun Sensors]', e)

        # Initialize H-Bridges
        try:
            drv_x = drv8830.DRV8830(self.i2c3, 0x68)  # U6
            drv_y = drv8830.DRV8830(self.i2c3, 0x60)  # U8
            drv_z = drv8830.DRV8830(self.i2c3, 0x62)  # U4
            coils = [drv_x, drv_y, drv_z]
            for driver in coils:
                driver.mode = drv8830.COAST
                driver.vout = 0
            self.hardware['Coils'] = True
        except Exception as e:
            print('[ERROR][H-Bridges]', e)

    def reinit(self, dev):
        dev = dev.lower()
        if dev == 'radio':
            self.radio2.__init__(self.spi, self._rf_cs, self._rf_rst, self.UHF_FREQ)
        elif dev == 'sd':
            self._sd.__init__(self.spi, self._sdcs, baudrate=1000000)
        elif dev == 'imu':
            self.IMU.__init__(self.i2c1)
        else:
            print('Invalid Device? ->', dev)

    @property
    def acceleration(self):
        return self.IMU.accel

    @property
    def magnetic(self):
        return self.IMU.mag

    @property
    def gyro(self):
        return self.IMU.gyro

    @property
    def temperature(self):
        return self.IMU.temperature  # Celsius

    @property
    def temperature_cpu(self):
        return microcontroller.cpu.temperature  # Celsius

    @property
    def RGB(self):
        return self.neopixel[0]

    @RGB.setter
    def RGB(self, value):
        if self.hardware['Neopixel']:
            try:
                self.neopixel[0] = value
            except Exception as e:
                print('[WARNING]', e)

    @property
    def battery_voltage(self):
        vbat = 0
        for _ in range(50):
            vbat += self._vbatt.value * 3.3 / 65536
        _voltage = (vbat / 50) * (100 + 100) / 100  # 100k/100k voltage divider
        return _voltage  # volts

    @property
    def fuel_gauge(self):
        # report battery voltage as % full
        return 100 * self.battery_voltage / 8.4

    @property
    def reset_boot_count(self):
        microcontroller.nvm[0] = 0

    @property
    def status(self):
        '''
        Returns dict
            - NVM registers(boot count, flags, counters)
            - Time (seconds) since boot/hard reset
            - Battery voltage as % of full
        TODO
            -
        '''
        self._stat.update({
            'boot-time': self.BOOTTIME,
            'boot-count': self.c_boot,
            'time-on': self.timeon,
            'fuel-gauge': self.fuel_gauge,
            'flags': {
                'deploy': self.f_deploy,
                'mid-deploy': self.f_mdeploy,
                'burn1': self.f_burn1,
                'burn2': self.f_burn2
            }, 'counters': {
                'state-errors': self.c_state_err,
                'vbus-resets': self.c_vbus_rst,
                'deploy': self.c_deploy,
                'downlink': self.c_downlink,
            },
        })
        self._stat.update({
            'raw': bytes([self.micro.nvm[_BOOTCNT],
                          self.micro.nvm[_FLAG],
                          self.micro.nvm[_RSTERRS],
                          self.micro.nvm[_DWNLINK],
                          self.micro.nvm[_DCOUNT]]) +
            self.BOOTTIME.to_bytes(3, 'big') +
            self._stat['time-on'].to_bytes(4, 'big') +
            int(self._stat['fuel-gauge']).to_bytes(1, 'big')
        })
        return self._stat

    @property
    def timeon(self):
        return int(time.monotonic())

    def crc(self, data):
        crc = 0
        for byte in data:
            crc ^= byte
        return crc

    def new_file(self, substring, binary=False):
        '''
        substring something like '/data/DATA_'
        directory is created on the SD!
        int padded with zeros will be appended to the last found file
        '''
        if self.hardware['SDcard']:
            n = 0
            _folder = substring[:substring.rfind('/') + 1]
            _file = substring[substring.rfind('/') + 1:]
            print('Creating new file in directory: /sd{} with file prefix: {}'.format(_folder, _file))
            if _folder.strip('/') not in listdir('/sd/'):
                print('Directory /sd{} not found. Creating...'.format(_folder))
                mkdir('/sd' + _folder)
                self.filename = '/sd' + _folder + _file + '000.txt'
            else:
                for f in listdir('/sd/' + _folder):
                    if _file in f:
                        for i in f.rsplit(_file):
                            if '.txt' in i and len(i) == 7:
                                c = i[-7:-4]
                                try:
                                    if int(c) > n:
                                        n = int(c)
                                except ValueError:
                                    continue
                                if int(i.rstrip('.txt')) > n:
                                    n = int(i.rstrip('.txt'))
                                    break
                self.filename = '/sd' + _folder + _file + "{:03}".format(n + 1) + ".txt"
            b = "a"
            if binary:
                b = "ab"
            with open(self.filename, b) as f:
                f.tell()
            print('New self.filename:', self.filename)
            return self.filename

    @property
    def storage_stats(self):
        _sd = 0
        if self.hardware['SDcard']:
            _sd = statvfs('/sd/')
            _sd = int(100 * _sd[3] / _sd[2])
        _fs = statvfs('/')
        _fs = int(100 * _fs[3] / _fs[2])
        return (_fs, _sd)

    def log(self, msg):
        if stat(self.logfile)[6] > 1E8:  # 100MB
            self.new_Log()
        if self.hardware['SDcard']:
            with open(self.logfile, "a+") as file:
                file.write('{:.1f},{}\r\n'.format(time.monotonic(), msg))

    def new_Log(self):
        if self.hardware['SDcard']:
            n = 0
            for f in listdir('/sd/logs/'):
                if int(f[3:-4]) > n:
                    n = int(f[3:-4])
            self.logfile = "/sd/logs/log" + "{:03}".format(n + 1) + ".txt"
            with open(self.logfile, "a") as logfile:
                logfile.write('# Created: {:.0f}\r\n# Status: {}\r\n'.format(time.monotonic(), self.status))
            print('New log file:', self.logfile)

    def print_file(self, filedir=None):
        if filedir is None:
            filedir = self.logfile
        print('--- Printing File: {} ---'.format(filedir))
        with open(filedir, "r") as file:
            for line in file:
                print(line.strip())

    def send_file(self, c_size, send_buffer, filename):
        num_packets = int(stat(filename)[6] / c_size)
        with open(filename, "rb") as f:
            for i in range(num_packets + 1):
                f.seek(i * c_size)
                f.readinto(send_buffer)
                yield bytes([i, 0x45, num_packets])

    def save(self, dataset, savefile=None):
        '''
        Dataset should be a list of lists. Each "line" is a list.
            save(([line1],[line2]))
        To save a string, just make it an item in a list:
            save(['This is my string'])
        '''
        if savefile is None:
            savefile = self.filename
        try:
            with open(savefile, "a") as file:
                for item in dataset:
                    if isinstance(item, (list, tuple)):
                        for i in item:
                            try:
                                if isinstance(i, float):
                                    file.write('{:.9G},'.format(i))
                                else:
                                    file.write('{G},'.format(i))
                            except:
                                file.write('{},'.format(i))
                    else:
                        file.write('{},'.format(item))
                    file.write('\n')
        except Exception as e:
            print('[ERROR] SD Save:', e)
            self.RGB = (255, 0, 0)
            return False

    def fifo(self, data, item):
        '''
        First-in first-out buffer
        buffer must be a list, size will not change
        preallocation example: data=[bytes([0]*66)]*30
        '''
        del data[0]
        data.append(item)

    def burn(self, burn_num, dutycycle=0, freq=1000, duration=1):
        # BURN1=-Y,BURN2=+Y,dutycycle ~0.13%
        dtycycl = int((dutycycle / 100) * (0xFFFF))
        print('----- BURN WIRE CONFIGURATION -----')
        print(f'\tFrequency of: {freq}Hz')
        print(f'\tDuty cycle of: {100 * dtycycl / 0xFFFF}% (int:{dtycycl})')
        print(f'\tDuration of {duration}sec')
        if '1' in burn_num:
            burnwire = pulseio.PWMOut(board.BURN1, frequency=freq, duty_cycle=0)
        elif '2' in burn_num:
            burnwire = pulseio.PWMOut(board.BURN2, frequency=freq, duty_cycle=0)
        else:
            return False
        self._relayA.drive_mode = digitalio.DriveMode.PUSH_PULL
        self._relayA.value = 1
        self.RGB = (255, 0, 0)
        time.sleep(0.5)
        burnwire.duty_cycle = dtycycl
        time.sleep(duration)
        self._relayA.value = 0
        burnwire.duty_cycle = 0
        self.RGB = (0, 0, 0)
        self._deployA = True
        burnwire.deinit()
        self._relayA.drive_mode = digitalio.DriveMode.OPEN_DRAIN
        return self._deployA


pocketqube = Satellite()
