# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_rfm9x`
====================================================

CircuitPython module for the RFM95/6/7/8 LoRa 433/915mhz radio modules.  This is
adapted from the Radiohead library RF95 code from:
http: www.airspayce.com/mikem/arduino/RadioHead/

* Author(s): Tony DiCola, Jerry Needell

====================================================
Modified to use FSK in 2022 by Jacob Willis
"""
import time
import adafruit_bus_device.spi_device as spidev
from micropython import const

HAS_SUPERVISOR = False

try:
    import supervisor
    if hasattr(supervisor, "ticks_ms"):
        HAS_SUPERVISOR = True
except ImportError:
    pass


class Constants:
    # Internal constants:
    # Register names

    # FIFO
    _RH_RF95_REG_00_FIFO = const(0x00)
    # Registers for common settings
    _RH_RF95_REG_01_OP_MODE = const(0x01)
    _RH_RF95_REG_02_BITRATE_MSB = const(0x02)
    _RH_RF95_REG_03_BITRATE_LSB = const(0x03)
    _RH_RF95_REG_04_FREQ_DEVIATION_MSB = const(0x04)
    _RH_RF95_REG_05_FREQ_DEVIATION_LSB = const(0x05)
    _RH_RF95_REG_06_FRF_MSB = const(0x06)
    _RH_RF95_REG_07_FRF_MID = const(0x07)
    _RH_RF95_REG_08_FRF_LSB = const(0x08)
    # Registers for the transmitter
    _RH_RF95_REG_09_PA_CONFIG = const(0x09)
    _RH_RF95_REG_0A_PA_RAMP = const(0x0A)
    _RH_RF95_REG_0B_OCP = const(0x0B)
    # Registers for the receiver
    _RH_RF95_REG_0C_LNA = const(0x0C)
    _RH_RF95_REG_0D_RX_CONFIG = const(0x0D)
    _RH_RF95_REG_0E_RSSI_CONFIG = const(0x0E)
    _RH_RF95_REG_0F_RSSI_COLLISION = const(0x0F)
    _RH_RF95_REG_10_RSSI_THRESH = const(0x10)
    _RH_RF95_REG_11_RSSI_VALUE = const(0x11)
    _RH_RF95_REG_12_RX_BW = const(0x12)
    _RH_RF95_REG_13_AFC_BW = const(0x13)
    _RH_RF95_REG_14_OOK_PEAK = const(0x14)
    _RH_RF95_REG_15_OOK_FIX = const(0x15)
    _RH_RF95_REG_16_OOK_AVG = const(0x16)
    # 0x17 to 0x19 - Reserved
    _RH_RF95_REG_1A_AFC_FEI = const(0x1A)
    _RH_RF95_REG_1B_AFC_MSB = const(0x1B)
    _RH_RF95_REG_1C_AFC_LSB = const(0x1C)
    _RH_RF95_REG_1D_FEI_MSB = const(0x1D)
    _RH_RF95_REG_1E_FEI_LSB = const(0x1E)
    _RH_RF95_REG_1F_PREAMBLE_DETECT = const(0x1F)
    _RH_RF95_REG_20_RX_TIMEOUT1 = const(0x20)
    _RH_RF95_REG_21_RX_TIMEOUT2 = const(0x21)
    _RH_RF95_REG_22_RX_TIMEOUT3 = const(0x22)
    _RH_RF95_REG_23_RX_DELAY = const(0x23)
    # Registers for RC oscillator
    _RH_RF95_REG_24_OSC = const(0x24)
    # Registers for packet handling
    _RH_RF95_REG_25_PREAMBLE_MSB = const(0x25)
    _RH_RF95_REG_26_PREAMBLE_LSB = const(0x26)
    _RH_RF95_REG_27_SYNC_CONFIG = const(0x27)
    _RH_RF95_REG_28_SYNC_VALUE_1 = const(0x28)  # Most significant byte
    _RH_RF95_REG_29_SYNC_VALUE_2 = const(0x29)
    _RH_RF95_REG_2A_SYNC_VALUE_3 = const(0x2A)
    _RH_RF95_REG_2B_SYNC_VALUE_4 = const(0x2B)
    _RH_RF95_REG_2C_SYNC_VALUE_5 = const(0x2C)
    _RH_RF95_REG_2D_SYNC_VALUE_6 = const(0x2D)
    _RH_RF95_REG_2E_SYNC_VALUE_7 = const(0x2E)
    _RH_RF95_REG_2F_SYNC_VALUE_8 = const(0x2F)
    _RH_RF95_REG_30_PKT_CONFIG_1 = const(0x30)
    _RH_RF95_REG_31_PKT_CONFIG_2 = const(0x31)
    _RH_RF95_REG_32_PAYLOAD_LEN = const(0x32)
    _RH_RF95_REG_33_NODE_ADDRESS = const(0x33)
    _RH_RF95_REG_34_BROADCAST_ADDRESS = const(0x34)
    _RH_RF95_REG_35_FIFO_THRESH = const(0x35)
    # Sequencer registers
    _RH_RF95_REG_36_SEQ_CONFIG_1 = const(0x36)
    _RH_RF95_REG_37_SEQ_CONFIG_2 = const(0x37)
    _RH_RF95_REG_38_TIMER_RESOLUTION = const(0x38)
    _RH_RF95_REG_39_TIMER1_COEF = const(0x39)
    _RH_RF95_REG_3A_TIMER2_COEF = const(0x3A)
    # Service registers
    _RH_RF95_REG_3B_IMAGE_CAL = const(0x3B)
    _RH_RF95_REG_3C_TEMP = const(0x3C)
    _RH_RF95_REG_3D_LOW_BATT = const(0x3C)
    # Status registers
    _RH_RF95_REG_3E_IRQ_FLAGS_1 = const(0x3D)
    _RH_RF95_REG_3F_IRQ_FLAGS_2 = const(0x3F)
    # IO control registers
    _RH_RF95_REG_40_DIO_MAPPING1 = const(0x40)
    _RH_RF95_REG_41_DIO_MAPPING2 = const(0x41)
    _RH_RF95_REG_42_VERSION = const(0x42)
    # Additional registers
    _RH_RF95_REG_44_PLL_HOP = const(0x44)
    _RH_RF95_REG_4B_TCXO = const(0x4B)
    _RH_RF95_REG_4D_PA_DAC = const(0x4D)
    _RH_RF95_REG_5B_FORMER_TEMP = const(0x5B)
    _RH_RF95_REG_5D_BITRATE_FRAC = const(0x5D)
    # Band-specific additional registers
    _RH_RF95_REG_61_AGC_REF = const(0x61)
    _RH_RF95_REG_62_AGC_THRESH1 = const(0x62)
    _RH_RF95_REG_63_AGC_THRESH2 = const(0x63)
    _RH_RF95_REG_64_AGC_THRESH3 = const(0x64)
    _RH_RF95_REG_70_PLL = const(0x70)

    # PA DAC register options
    _RH_RF95_PA_DAC_DISABLE = const(0x04)
    _RH_RF95_PA_DAC_ENABLE = const(0x07)

    # The crystal oscillator frequency of the module
    _RH_RF95_FXOSC = 32000000.0

    # The Frequency Synthesizer step = RH_RF95_FXOSC / 2^^19
    _RH_RF95_FSTEP = _RH_RF95_FXOSC / 524288

    # RadioHead specific compatibility constants.
    _RH_BROADCAST_ADDRESS = const(0xFF)

    # The acknowledgement bit in the FLAGS
    # The top 4 bits of the flags are reserved for RadioHead. The lower 4 bits are reserved
    # for application layer use.
    _RH_FLAGS_ACK = const(0x80)
    _RH_FLAGS_RETRY = const(0x40)

    # User facing constants:
    SLEEP_MODE = 0b000
    STANDBY_MODE = 0b001
    FS_TX_MODE = 0b010
    TX_MODE = 0b011
    FS_RX_MODE = 0b100
    RX_MODE = 0b101
    # supervisor.ticks_ms() contants
    _TICKS_PERIOD = const(1 << 29)
    _TICKS_MAX = const(_TICKS_PERIOD - 1)
    _TICKS_HALFPERIOD = const(_TICKS_PERIOD // 2)

    _MAX_FIFO_LENGTH = 66

# Disable the too many instance members warning.  Pylint has no knowledge
# of the context and is merely guessing at the proper amount of members.  This
# is a complex chip which requires exposing many attributes and state.  Disable
# the warning to work around the error.
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements


def ticks_diff(ticks1, ticks2):
    """Compute the signed difference between two ticks values
    assuming that they are within 2**28 ticks
    """
    diff = (ticks1 - ticks2) & Constants._TICKS_MAX
    diff = ((diff + Constants._TICKS_HALFPERIOD) & Constants._TICKS_MAX) - Constants._TICKS_HALFPERIOD
    return diff


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


class RFM9x:
    """Interface to a RFM95/6/7/8 radio module.  Allows sending and
    receiving bytes of data in FSK mode at a supported board frequency
    (433/915mhz).

    You must specify the following parameters:
    - spi: The SPI bus connected to the radio.
    - cs: The CS pin DigitalInOut connected to the radio.
    - reset: The reset/RST pin DigialInOut connected to the radio.
    - frequency: The frequency (in mhz) of the radio module (433/915mhz typically).

    You can optionally specify:
    - preamble_length: The length in bytes of the packet preamble (default 8).
    - high_power: Boolean to indicate a high power board (RFM95, etc.).  Default
    is True for high power.
    - baudrate: Baud rate of the SPI connection, default is 10mhz but you might
    choose to lower to 1mhz if using long wires or a breadboard.
    - agc: Boolean to Enable/Disable Automatic Gain Control - Default=False (AGC off)
    - checksum: Boolean to Enable/Disable appending a two byte checksum - Default=True (checksum Enabled)
    Remember this library makes a best effort at receiving packets with pure
    Python code.  Trying to receive packets too quickly will result in lost data
    so limit yourself to simple scenarios of sending and receiving single
    packets at a time.

    Also note this library tries to be compatible with raw RadioHead Arduino
    library communication. This means the library sets up the radio modulation
    to match RadioHead's defaults and assumes that each packet contains a
    4 byte header compatible with RadioHead's implementation.
    Advanced RadioHead features like address/node specific packets
    or "reliable datagram" delivery are supported however due to the
    limitations noted, "reliable datagram" is still subject to missed packets but with it,
    sender is notified if a packet has potentially been missed.
    """

    # Global buffer for SPI commands
    _BUFFER = bytearray(4)

    class _RegisterBits:
        # Class to simplify access to the many configuration bits avaialable
        # on the chip's registers.  This is a subclass here instead of using
        # a higher level module to increase the efficiency of memory usage
        # (all of the instances of this bit class will share the same buffer
        # used by the parent RFM69 class instance vs. each having their own
        # buffer and taking too much memory).

        # Quirk of pylint that it requires public methods for a class.  This
        # is a decorator class in Python and by design it has no public methods.
        # Instead it uses dunder accessors like get and set below.  For some
        # reason pylint can't figure this out so disable the check.
        # pylint: disable=too-few-public-methods

        # Again pylint fails to see the true intent of this code and warns
        # against private access by calling the write and read functions below.
        # This is by design as this is an internally used class.  Disable the
        # check from pylint.
        # pylint: disable=protected-access

        def __init__(self, address, *, offset=0, bits=1):
            assert 0 <= offset <= 7
            assert 1 <= bits <= 8
            assert (offset + bits) <= 8
            self._address = address
            self._mask = 0
            for _ in range(bits):
                self._mask <<= 1
                self._mask |= 1
            self._mask <<= offset
            self._offset = offset

        def __get__(self, obj, objtype):
            reg_value = obj._read_u8(self._address)
            return (reg_value & self._mask) >> self._offset

        def __set__(self, obj, val):
            reg_value = obj._read_u8(self._address)
            reg_value &= ~self._mask
            reg_value |= (val & 0xFF) << self._offset
            obj._write_u8(self._address, reg_value)

    operation_mode = _RegisterBits(Constants._RH_RF95_REG_01_OP_MODE, offset=0, bits=3)

    low_frequency_mode = _RegisterBits(
        Constants._RH_RF95_REG_01_OP_MODE, offset=3, bits=1)

    modulation_type = _RegisterBits(Constants._RH_RF95_REG_01_OP_MODE, offset=5, bits=2)

    # Long range mode (LoRa or FSK) can only be set in sleep mode!
    long_range_mode = _RegisterBits(Constants._RH_RF95_REG_01_OP_MODE, offset=7, bits=1)

    output_power = _RegisterBits(Constants._RH_RF95_REG_09_PA_CONFIG, offset=0, bits=4)

    max_power = _RegisterBits(Constants._RH_RF95_REG_09_PA_CONFIG, offset=4, bits=3)

    pa_select = _RegisterBits(Constants._RH_RF95_REG_09_PA_CONFIG, offset=7, bits=1)

    pa_dac = _RegisterBits(Constants._RH_RF95_REG_4D_PA_DAC, offset=0, bits=3)

    dio0_mapping = _RegisterBits(Constants._RH_RF95_REG_40_DIO_MAPPING1, offset=6, bits=2)

    lna_boost_hf = _RegisterBits(Constants._RH_RF95_REG_0C_LNA, offset=0, bits=2)

    lna_gain = _RegisterBits(Constants._RH_RF95_REG_0C_LNA, offset=5, bits=3)

    afc_enable = _RegisterBits(Constants._RH_RF95_REG_0D_RX_CONFIG, offset=4, bits=1)

    tx_start_condition = _RegisterBits(Constants._RH_RF95_REG_35_FIFO_THRESH, offset=7, bits=1)
    fifo_threshold = _RegisterBits(Constants._RH_RF95_REG_35_FIFO_THRESH, offset=0, bits=6)

    modulation_shaping = _RegisterBits(
        Constants._RH_RF95_REG_0A_PA_RAMP, offset=6, bits=2)

    packet_format = _RegisterBits(Constants._RH_RF95_REG_30_PKT_CONFIG_1, offset=7, bits=1)
    dc_free = _RegisterBits(Constants._RH_RF95_REG_30_PKT_CONFIG_1, offset=5, bits=2)
    crc_on = _RegisterBits(Constants._RH_RF95_REG_30_PKT_CONFIG_1, offset=4, bits=1)
    crc_auto_clear = _RegisterBits(Constants._RH_RF95_REG_30_PKT_CONFIG_1, offset=3, bits=1)
    address_filtering = _RegisterBits(Constants._RH_RF95_REG_30_PKT_CONFIG_1, offset=1, bits=2)
    crc_whitening = _RegisterBits(Constants._RH_RF95_REG_30_PKT_CONFIG_1, offset=0, bits=1)
    data_mode = _RegisterBits(Constants._RH_RF95_REG_31_PKT_CONFIG_2, offset=6, bits=1)

    _bw_mantissa = _RegisterBits(Constants._RH_RF95_REG_12_RX_BW, offset=3, bits=2)
    _bw_exponent = _RegisterBits(Constants._RH_RF95_REG_12_RX_BW, offset=0, bits=3)
    _bw_bins_kHz = (2.5, 3.1, 3.9, 5.2, 6.3, 7.8, 10.4, 12.5, 15.6, 20.8,
                    25.0, 31.3, 41.7, 50.0, 62.5, 83.3, 100.0, 125.0, 166.7, 200.0, 250.0)
    _bw_mant_bins = (2, 1, 0, 2, 1, 0, 2, 1, 0, 2,
                     1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0)
    _bw_exp_bins = (7, 7, 7, 6, 6, 6, 5, 5, 5, 4,
                    4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1)

    def __init__(
        self,
        spi,
        cs,
        reset,
        frequency,
        preamble_length=8,
        high_power=True,
        bitrate=1200,
        frequency_deviation=5000,
        spi_baudrate=5000000,
    ):
        self.high_power = high_power
        # Device support SPI mode 0 (polarity & phase = 0) up to a max of 10mhz.
        # Set Default Baudrate to 5MHz to avoid problems
        self._device = spidev.SPIDevice(
            spi, cs, baudrate=spi_baudrate, polarity=0, phase=0)
        # Setup reset as a digital output - initially High
        # This line is pulled low as an output quickly to trigger a reset.
        self._reset = reset
        # initialize Reset High
        self._reset.switch_to_output(value=True)
        self.reset()
        # No device type check!  Catch an error from the very first request and
        # throw a nicer message to indicate possible wiring problems.
        version = self._read_u8(Constants._RH_RF95_REG_42_VERSION)
        if version != 18:
            raise RuntimeError(
                "Failed to find rfm9x with expected version -- check wiring"
            )

        # Set sleep mode, wait 10s and confirm in sleep mode (basic device check).
        # Also set long range mode to false (FSK mode) as it can only be done in sleep.
        self.sleep()
        time.sleep(0.01)
        self.long_range_mode = False  # choose FSK instead of LoRA
        if self.operation_mode != Constants.SLEEP_MODE or self.long_range_mode:
            raise RuntimeError(
                "Failed to configure radio for FSK mode, check wiring!")
        # clear default setting for access to LF registers if frequency > 525MHz
        if frequency > 525:
            self.low_frequency_mode = 0
        else:
            self.low_frequency_mode = 1

        self.idle()

        # Set modulation type to FSK
        self.modulation_type = 0x00
        # Gaussian filter, BT = 0.5
        self.modulation_shaping = 0b10
        self.frequency_deviation = frequency_deviation
        self.bitrate = bitrate
        self.frequency_mhz = frequency
        self.preamble_length = preamble_length

        self.packet_format = 0b1  # variable length packets
        self.dc_free = 0b01  # Manchester coding
        self.crc_on = 0b0  # turn off CRC  - it doesn't work
        self.crc_auto_clear = 0b1  # FIFO not cleared for packets that fail CRC
        self.crc_whitening = 0b0  # use CCITT CRC - IBM not supported (see errata)
        self.address_filtering = 0b00  # no address filtering - handled in software
        self.data_mode = 0b1  # packet mode

        self.tx_start_condition = 0b1  # start transmitting when first byte enters FIFO

        self.tx_power = 13  # 13 dBm is a safe value any module support

    # pylint: disable=no-member
    # Reconsider pylint: disable when this can be tested
    def _read_into(self, address, buf, length=None):
        # Read a number of bytes from the specified address into the provided
        # buffer.  If length is not specified (the default) the entire buffer
        # will be filled.
        if length is None:
            length = len(buf)
        with self._device as device:
            self._BUFFER[0] = address & 0x7F  # Strip out top bit to set 0
            # value (read).
            device.write(self._BUFFER, end=1)
            device.readinto(buf, end=length)

    def _read_until_flag(self, address, buf, flag):
        # read bytes from the given address until flag is true
        idx = 0
        while not flag():
            buf[idx] = self._read_u8(address)
            idx += 1
            if idx > len(buf):
                raise RuntimeError(f"Overflow reading into buffer of length {len(buf)}")
        return idx

    def _read_u8(self, address):
        # Read a single byte from the provided address and return it.
        self._read_into(address, self._BUFFER, length=1)
        return self._BUFFER[0]

    def _write_from(self, address, buf, length=None):
        # Write a number of bytes to the provided address and taken from the
        # provided buffer.  If no length is specified (the default) the entire
        # buffer is written.
        if length is None:
            length = len(buf)
        with self._device as device:
            self._BUFFER[0] = (address | 0x80) & 0xFF  # Set top bit to 1 to
            # indicate a write.
            device.write(self._BUFFER, end=1)
            device.write(buf, end=length)

    def _write_u8(self, address, val):
        # Write a byte register to the chip.  Specify the 7-bit address and the
        # 8-bit value to write to that address.
        with self._device as device:
            self._BUFFER[0] = (address | 0x80) & 0xFF  # Set top bit to 1 to
            # indicate a write.
            self._BUFFER[1] = val & 0xFF
            device.write(self._BUFFER, end=2)

    def reset(self):
        """Perform a reset of the chip."""
        # See section 7.2.2 of the datasheet for reset description.
        self._reset.value = False  # Set Reset Low
        time.sleep(0.0001)  # 100 us
        self._reset.value = True  # set Reset High
        time.sleep(0.005)  # 5 ms

    def idle(self):
        """Enter idle standby mode."""
        self.operation_mode = Constants.STANDBY_MODE

    def sleep(self):
        """Enter sleep mode."""
        self.operation_mode = Constants.SLEEP_MODE

    def listen(self):
        """Listen for packets to be received by the chip.  Use: py: func: `receive`
        to listen, wait and retrieve packets as they're available.
        """
        self.operation_mode = Constants.RX_MODE
        self.dio0_mapping = 0b00  # Interrupt on rx done.

    def transmit(self):
        """Transmit a packet which is queued in the FIFO.  This is a low level
        function for entering transmit mode and more.  For generating and
        transmitting a packet of data use: py: func: `send` instead.
        """
        self.operation_mode = Constants.TX_MODE
        self.dio0_mapping = 0b00  # Interrupt on tx done.

    @property
    def preamble_length(self):
        """The length of the preamble for sent packets, an unsigned
        16-bit value. Default is 0x0003.
        """
        msb = self._read_u8(Constants._RH_RF95_REG_25_PREAMBLE_MSB)
        lsb = self._read_u8(Constants._RH_RF95_REG_26_PREAMBLE_LSB)
        return ((msb << 8) | lsb) & 0xFFFF

    @preamble_length.setter
    def preamble_length(self, val):
        val = int(val)
        assert 0 <= val <= 65535
        self._write_u8(Constants._RH_RF95_REG_25_PREAMBLE_MSB, (val >> 8) & 0xFF)
        self._write_u8(Constants._RH_RF95_REG_26_PREAMBLE_LSB, val & 0xFF)

    @property
    def frequency_mhz(self):
        """The frequency of the radio in Megahertz. Only the allowed values for
        your radio must be specified(i.e. 433 vs. 915 mhz)!
        """
        msb = self._read_u8(Constants._RH_RF95_REG_06_FRF_MSB)
        mid = self._read_u8(Constants._RH_RF95_REG_07_FRF_MID)
        lsb = self._read_u8(Constants._RH_RF95_REG_08_FRF_LSB)
        frf = ((msb << 16) | (mid << 8) | lsb) & 0xFFFFFF
        frequency = (frf * Constants._RH_RF95_FSTEP) / 1000000.0
        return frequency

    @frequency_mhz.setter
    def frequency_mhz(self, val):
        if val < 240 or val > 960:
            raise RuntimeError("frequency_mhz must be between 240 and 960")
        # Calculate FRF register 24-bit value.
        frf = int((val * 1000000.0) / Constants._RH_RF95_FSTEP) & 0xFFFFFF
        # Extract byte values and update registers.
        msb = frf >> 16
        mid = (frf >> 8) & 0xFF
        lsb = frf & 0xFF
        self._write_u8(Constants._RH_RF95_REG_06_FRF_MSB, msb)
        self._write_u8(Constants._RH_RF95_REG_07_FRF_MID, mid)
        self._write_u8(Constants._RH_RF95_REG_08_FRF_LSB, lsb)

    @property
    def bitrate(self):
        msb = self._read_u8(Constants._RH_RF95_REG_02_BITRATE_MSB)
        lsb = self._read_u8(Constants._RH_RF95_REG_03_BITRATE_LSB)
        frac = self._read_u8(Constants._RH_RF95_REG_5D_BITRATE_FRAC) & 0x0F

        int_part = ((msb << 8) | lsb) & 0xFFFF

        br = Constants._RH_RF95_FXOSC / (int_part + (frac / 16))

        return br

    @bitrate.setter
    def bitrate(self, val):
        br = Constants._RH_RF95_FXOSC / val
        int_part = int(br)
        frac_part = int(16 * (br % 1)) & 0x0F

        msb = (int_part >> 8) & 0xFF
        lsb = int_part & 0xFF

        self._write_u8(Constants._RH_RF95_REG_02_BITRATE_MSB, msb)
        self._write_u8(Constants._RH_RF95_REG_03_BITRATE_LSB, lsb)
        self._write_u8(Constants._RH_RF95_REG_5D_BITRATE_FRAC, frac_part)

    @property
    def frequency_deviation(self):
        msb = self._read_u8(Constants._RH_RF95_REG_04_FREQ_DEVIATION_MSB) & 0x3F
        lsb = self._read_u8(Constants._RH_RF95_REG_05_FREQ_DEVIATION_LSB)

        fd = (((msb << 8) | lsb) & 0xFFFF) * Constants._RH_RF95_FSTEP

        return fd

    @frequency_deviation.setter
    def frequency_deviation(self, val):
        val = int(val / Constants._RH_RF95_FSTEP)
        msb = (val >> 8) & 0x3F
        lsb = val & 0xFF

        self._write_u8(Constants._RH_RF95_REG_04_FREQ_DEVIATION_MSB, msb)
        self._write_u8(Constants._RH_RF95_REG_05_FREQ_DEVIATION_LSB, lsb)

    @property
    def frequency_error(self):
        """
        The frequency error
        """
        msb = self._read_u8(Constants._RH_RF95_REG_1D_FEI_MSB)
        lsb = self._read_u8(Constants._RH_RF95_REG_1E_FEI_LSB)

        fei_value = twos_comp(
            ((msb << 8) | lsb) & 0xFFFF, 16)
        f_error = fei_value * Constants._RH_RF95_FSTEP
        return f_error

    @property
    def afc_value(self):
        """
        The automatic frequency correction value
        """
        msb = self._read_u8(Constants._RH_RF95_REG_1B_AFC_MSB)
        lsb = self._read_u8(Constants._RH_RF95_REG_1C_AFC_LSB)

        afc = twos_comp(
            ((msb << 8) | lsb) & 0xFFFF,
            16
        )

        return afc

    @property
    def tx_power(self):
        """The transmit power in dBm. Can be set to a value from 5 to 23 for
        high power devices(RFM95/96/97/98, high_power=True) or -1 to 14 for low
        power devices. Only integer power levels are actually set(i.e. 12.5
        will result in a value of 12 dBm).
        The actual maximum setting for high_power = True is 20dBm but for values > 20
        the PA_BOOST will be enabled resulting in an additional gain of 3dBm.
        The actual setting is reduced by 3dBm.
        """
        if self.high_power:
            if self.pa_dac & 0x07 == Constants._RH_RF95_PA_DAC_ENABLE:
                return self.output_power + 5 + 3
            else:
                return self.output_power + 5

        return self.output_power - 1

    @tx_power.setter
    def tx_power(self, val):
        val = int(val)
        if self.high_power:
            if val < 5 or val > 23:
                raise RuntimeError("tx_power must be between 5 and 23")
            # Enable power amp DAC if power is above 20 dB.
            # Lower setting by 3db when PA_BOOST enabled - see Data Sheet  Section 6.4
            if val > 20:
                self.pa_dac = Constants._RH_RF95_PA_DAC_ENABLE
                val -= 3
            else:
                self.pa_dac = Constants._RH_RF95_PA_DAC_DISABLE
            self.pa_select = True
            self.output_power = (val - 5) & 0x0F
        else:
            assert -1 <= val <= 14
            self.pa_select = False
            self.max_power = 0b111  # Allow max power output.
            self.output_power = (val + 1) & 0x0F

    @property
    def rssi(self):
        """The received strength indicator (in dBm) of the last received message."""
        # Read RSSI register and convert to value using formula in datasheet.
        raw_rssi = self._read_u8(Constants._RH_RF95_REG_11_RSSI_VALUE)
        return -raw_rssi / 2

    @property
    def rx_bandwidth(self):
        """
        The receiver filter bandwidth in kHz.
        """
        # Defined using a mantissa and exponent(see table 40, pg 88 in Semtech Docs)
        mant_binary = self._bw_mantissa
        exp = self._bw_exponent

        if mant_binary == 0b10:
            mant = 24
        elif mant_binary == 0b01:
            mant = 20
        elif mant_binary == 0b00:
            mant = 16
        else:
            raise ValueError(f"RX bandwidth mantissa {mant_binary} invalid")

        rxbw = Constants._RH_RF95_FXOSC / (mant * (2**(exp + 2)))
        return rxbw / 1000

    @rx_bandwidth.setter
    def rx_bandwidth(self, val):
        try:
            idx = self._bw_bins_kHz.index(val)
        except ValueError:
            raise ValueError(
                f"Invalid receive bandwidth {val}, must be one of {self._bw_bins_kHz}")

        self._bw_mantissa = self._bw_mant_bins[idx]
        self._bw_exponent = self._bw_exp_bins[idx]

    def tx_done(self):
        """Transmit status"""
        return (self._read_u8(Constants._RH_RF95_REG_3F_IRQ_FLAGS_2) & 0b1000) >> 3

    def rx_done(self):
        """Receive status"""
        return (self._read_u8(Constants._RH_RF95_REG_3F_IRQ_FLAGS_2) & 0b0100) >> 2

    def crc_ok(self):
        """crc status"""
        return (self._read_u8(Constants._RH_RF95_REG_3F_IRQ_FLAGS_2) & 0b0010) >> 1

    def fifo_empty(self):
        """True when FIFO is empty"""
        return (self._read_u8(Constants._RH_RF95_REG_3F_IRQ_FLAGS_2) & (0b1 << 6)) >> 6

    def write_payload(self, payload):
        self._write_from(Constants._RH_RF95_REG_00_FIFO, payload)

    def check_data(self, data):
        assert 0 < len(data) <= 57

    def get_packet(self):
        packet = bytearray(Constants._MAX_FIFO_LENGTH)
        packet_length = self._read_until_flag(Constants._RH_RF95_REG_00_FIFO,
                                              packet,
                                              self.fifo_empty)
        return packet[:packet_length]
