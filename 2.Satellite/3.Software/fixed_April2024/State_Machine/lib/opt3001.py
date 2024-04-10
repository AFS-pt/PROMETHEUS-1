"""
CircuitPython driver for the OPT3001 ambient light sensor
M. Holliday
T. Damiani
"""

from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bits import RWBits
from adafruit_register.i2c_bit import ROBit, RWBit

RESULT = const(0x00)
CONFIGURATION = const(0x01)

class OPT3001:
    """OPT3001 Sun Sensor Driver"""

    # RWBits(num_bits, register_address, lowest_bit, register_width=1, lsb_first=True)

    # See Table 10 in datasheet for Configuration Register settings
    mode         = RWBits(2, CONFIGURATION, 9, register_width=2, lsb_first=False)
    range_number = RWBits(4, CONFIGURATION, 12, register_width=2, lsb_first=False)
    conv_800ms   = RWBit(CONFIGURATION, 11, register_width=2, lsb_first=False)
    rdy   = ROBit(CONFIGURATION, 7, register_width=2, lsb_first=False)

    def __init__(self, i2c_bus, address=0x44):
        """Initialize and Configure the Light Sensor Driver"""
        self.i2c_device = I2CDevice(i2c_bus, address)
        # Initialize a fixed buffer to read and write from
        self.buf = bytearray(2)

        self.read_u16(0x7F)  # DEVICE_ID
        if b'0\x01' not in self.buf:
            print(f'device id: {self.buf}')
            raise Exception("ERROR: Could not read correct device ID from bus provided")

        self.read_u16(0x7E)  # MANUFACTURER_ID
        if b'TI' not in self.buf:
            print(f'manufacturer id: {self.buf}')
            raise Exception("ERROR: Could not read correct manufacturer ID from bus provided")

        # CONFIGURE
        self.range_number = 0b1100  # automatic lux range
        self.conv_800ms   = False   # 100ms conversion time
        self.mode = 0b11           # continuous conversions

    def read_u16(self, addr):
        self.buf[0] = addr
        with self.i2c_device as i2c:
            i2c.write_then_readinto(self.buf, self.buf, out_end=1, in_start=0)

    @property
    def lux(self):
        """LUX value of sun-sensor"""
        # read and process the lux measurement
        self.read_u16(RESULT)

        exponent = (self.buf[0] >> 4) & ((1 << 4) - 1)  # E[3:0]
        fractional_result = (self.buf[0]) & ((1 << 4) - 1)  # R[11:8]
        fractional_result = fractional_result << 8  # pad in order to add the rest of the mantissa
        fractional_result += self.buf[1]  # R[7:0]

        # Formulas used below are from opt3001 datasheet
        lsb_size = 0.01 * (2 ** exponent)
        lux = lsb_size * fractional_result

        return lux
