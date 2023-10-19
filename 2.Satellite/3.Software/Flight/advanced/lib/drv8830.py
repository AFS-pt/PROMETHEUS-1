from micropython import const

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bits import ROBits, RWBits
from adafruit_register.i2c_bit import ROBit, RWBit

'''
DRV8830 doesn't respond to general call address
General addresses range from 0x60 -> 0x68 depending on A1/A0 pins

if 0xC9 is read, and 0xC8 is write, then general address is 0x64
    0b0110 + (column 3 in Table 5)
'''
_DRV8830_ADDR = const(0x64)
_DRV8830_REG_CONTROL = const(0x00)
_DRV8830_REG_FAULT   = const(0x01)

'''
Bridge Control Logic
IN1 IN2 OUT1 OUT2 FUNC
 0   0   Z    Z   Coast (low-power/shutdown)
 0   1   L    H   Reverse
 1   0   H    L   Forward
 1   1   H    H   Brake
'''
COAST   = const(0b00)
REVERSE = const(0b01)
FORWARD = const(0b10)
BRAKE   = const(0b11)


class DRV8830(object):
    modes={
        0:'COAST', # low-power/shutdown
        1:'REVERSE',
        2:'FORWARD',
        3:'BRAKE',
    }

    _BUFFER = bytearray(2)
    # RWBits(num_bits, register_address, lowest_bit, register_width=1, lsb_first=True)
    _drive_control = RWBits(2,_DRV8830_REG_CONTROL,0,lsb_first=False)
    _drive_vset    = RWBits(6,_DRV8830_REG_CONTROL,2,lsb_first=False)
    clear_fault   = RWBit(_DRV8830_REG_FAULT,7,lsb_first=False)
    ilim          = ROBit(_DRV8830_REG_FAULT,4,lsb_first=False)
    ots           = ROBit(_DRV8830_REG_FAULT,3,lsb_first=False)
    uvlo          = ROBit(_DRV8830_REG_FAULT,2,lsb_first=False)
    ocp           = ROBit(_DRV8830_REG_FAULT,1,lsb_first=False)
    fault         = ROBit(_DRV8830_REG_FAULT,0,lsb_first=False)

    def __init__(self, i2c, address=_DRV8830_ADDR):
        assert 0x68>=_DRV8830_ADDR>=0x60, "Address must be 0x60 -> 0x64"
        self.i2c_device = I2CDevice(i2c, address, probe=False)
        self._drive_vset=0x00
        self._drive_control = COAST
        self.Mode=self.modes[COAST]
        self.Vout=0

    @property
    def mode(self):
        return self.Mode
    @mode.setter
    def mode(self,_mode):
        assert _mode in (COAST,REVERSE,FORWARD,BRAKE), "Invalid mode"
        self._drive_control = _mode
        self.Mode=self.modes[_mode]

    @property
    def vout(self):
        return self.Vout
    vout.setter
    def vout(self,vset):
        '''
        Tabulated output voltages: see Table 1.
        If Vout > VDD, duty cycle goes to 100% and
        voltage regulator is disabled (conventional h-bridge).
        '''
        assert 0x3F>=vset>=0x06, "Invalid output voltage"
        self._drive_vset=vset
        self.Vout=vset
