# SPDX-FileCopyrightText: Copyright (c) 2022 JG for Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`cedargrove_drv8830`
================================================================================
A CircuitPython driver class for the DRV8830 motor controller.
* Author(s): JG
Implementation Notes
--------------------
**Hardware:**
.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"
**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies
  based on the library's use of either.
# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bits import RWBits
from adafruit_register.i2c_bit import RWBit
from adafruit_register.i2c_bit import ROBit

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/CedarGroveStudios/Cedargrove_CircuitPython_DRV8830.git"


# DEVICE REGISTER MAP
_CONTROL = 0x00  # Control Register      -W
_FAULT = 0x01  # Fault Status Register R-

# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
class VoltageAdapter:
    """Output voltage calculator. Datasheet formula modified to match the
    datasheet's voltage table. The algorithm was inspired by Pimironi's original
    VoltageAdapter class code, Copyright (c) 2018 Pimoroni Ltd.
    (https://github.com/pimoroni/drv8830-python)."""

    def index_to_voltage(self, index):
        """Convert an index value to nearest voltage value."""
        index = min(max(index, 0), 0x3F)
        if index <= 5:
            return 0.0
        offset = 0.01 if index >= 16 else 0
        offset += 0.01 if index >= 48 else 0
        return round(offset + (index * 0.08), 2)

    def voltage_to_index(self, volts):
        """Convert a voltage to nearest index value."""
        volts = min(max(volts, 0.0), 5.06)
        if volts < 0.48:
            return 0
        offset = 0.01 if volts >= 1.29 else 0
        offset -= 0.01 if volts >= 3.86 else 0
        return int(offset + volts / 0.08)


# pylint: disable=too-few-public-methods
class BridgeControl:
    """H-bridge control states and descriptors. Bit order: IN2 IN1"""

    STANDBY = 0b00  # Standby/Coast function (Hi-Z)
    COAST = 0b00  # Standby/Coast function (Hi-Z)
    FORWARD = 0b01  # Forward function
    REVERSE = 0b10  # Reverse function
    BRAKE = 0b11  # Brake function

    DESCRIPTOR = ["STANDBY/COAST", "FORWARD", "REVERSE", "BRAKE"]


class Faults:
    """Fault Register Flag Descriptors
    FAULT  Any fault condition
    OCP    Overcurrent event;
           device disabled, clear fault to reactivate
    UVLO   Undervoltage lockout; device disabled,
           resumes with voltage restoration
    OTS    Overtemperature condition;
           device disabled, resumes with lower temperature
    ILIMIT Extended current limit event;
           device disabled, clear fault to reactivate
    """

    DESCRIPTOR = ["FAULT", "OCP", "UVLO", "OTS", "ILIMIT"]


class DRV8830(object):
    """DC motor driver with I2C interface. Using an internal PWM scheme, the
    DRV8830 produces a regulated output voltage from a normalized input value
    (-1.0 to +1.0) or voltage input value (-5.06 to +5.06 volts).
    :param i2c_bus: The microcontroller I2C interface bus pins.
    :param address: The I2C address of the DRV8830 motor controller."""

    def __init__(self, i2c_bus, address=0x60):
        """Instantiate DRV8830. Set output voltage to 0.0, place into STANDBY
        mode, and reset all fault status flags."""
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._vset = 0x00
        self._in_x = BridgeControl.STANDBY
        # Clear all fault status flags
        self._clear = True

    # DEFINE I2C DEVICE BITS, NYBBLES, BYTES, AND REGISTERS
    _in_x = RWBits(2, _CONTROL, 0, 1, False)  # Output state; IN2, IN1
    _vset = RWBits(6, _CONTROL, 2, 1, False)  # DAC output voltage (raw)
    _fault = ROBit(_FAULT, 0, 1, False)  # Any fault condition
    _ocp = ROBit(_FAULT, 1, 1, False)  # Overcurrent event
    _uvlo = ROBit(_FAULT, 2, 1, False)  # Undervoltage lockout
    _ots = ROBit(_FAULT, 3, 1, False)  # Overtemperature condition
    _ilimit = ROBit(_FAULT, 4, 1, False)  # Extended current limit event
    _clear = RWBit(_FAULT, 7, 1, False)  # Clears fault status flag bits

    @property
    def throttle(self):
        """Current motor speed, ranging from -1.0 (full speed reverse) to
        +1.0 (full speed forward), or ``None`` (controller off). If ``None``,
        the H-bridge is set to high-impedance (coasting). If ``0.0``, the
        H-bridge is set to cause braking."""
        if self.bridge_control[0] == BridgeControl.COAST:
            return None
        if self.bridge_control[0] == BridgeControl.BRAKE:
            return 0.0
        if self.bridge_control[0] == BridgeControl.REVERSE:
            return -1 * round(self._vset / 0x3F, 3)
        return round(self._vset / 0x3F, 3)

    @throttle.setter
    def throttle(self, new_throttle):
        if new_throttle is None:
            self._vset = 0
            self._in_x = BridgeControl.COAST
            return
        # Constrain throttle value
        self._throttle_normalized = min(max(new_throttle, -1.0), +1.0)
        if new_throttle < 0:
            self._vset = int(abs(new_throttle * 0x3F))
            self._in_x = BridgeControl.REVERSE
        elif new_throttle > 0:
            self._vset = int(new_throttle * 0x3F)
            self._in_x = BridgeControl.FORWARD
        else:
            self._vset = 0
            self._in_x = BridgeControl.BRAKE
        return

    @property
    def throttle_volts(self):
        """Current motor speed, ranging from -5.06 volts (full speed reverse) to
        +5.06 volts (full speed forward), or ``None`` (controller off). If ``None``,
        the H-bridge is set to high-impedance (coasting). If ``0.0``, the
        H-bridge is set to cause braking."""
        if self.bridge_control[0] == BridgeControl.COAST:
            return None
        if self.bridge_control[0] == BridgeControl.BRAKE:
            return 0.0
        if self.bridge_control[0] == BridgeControl.REVERSE:
            return -1 * VoltageAdapter.index_to_voltage(self, self._vset)
        return VoltageAdapter.index_to_voltage(self, self._vset)

    @throttle_volts.setter
    def throttle_volts(self, new_throttle_volts):
        if new_throttle_volts is None:
            self._vset = 0
            self._in_x = BridgeControl.COAST
            return
        # Constrain throttle voltage value
        new_throttle_volts = min(max(new_throttle_volts, -5.1), +5.1)
        if new_throttle_volts < 0:
            self._vset = VoltageAdapter.voltage_to_index(self, abs(new_throttle_volts))
            self._in_x = BridgeControl.REVERSE
        elif new_throttle_volts > 0:
            self._vset = VoltageAdapter.voltage_to_index(self, new_throttle_volts)
            self._in_x = BridgeControl.FORWARD
        else:
            self._vset = 0
            self._in_x = BridgeControl.BRAKE
        return

    @property
    def throttle_raw(self):
        """Current motor speed, 6-bit VSET byte value, ranging from -63 (full speed reverse) to
        63 (full speed forward), or ``None`` (controller off). If ``None``,
        the H-bridge is set to high-impedance (coasting). If ``0``, the
        H-bridge is set to cause braking."""
        if self.bridge_control[0] == BridgeControl.COAST:
            return None
        if self.bridge_control[0] == BridgeControl.BRAKE:
            return 0
        if self.bridge_control[0] == BridgeControl.REVERSE:
            return -1 * self._vset
        return self._vset

    @throttle_raw.setter
    def throttle_raw(self, new_throttle_raw):
        if new_throttle_raw is None:
            self._vset = 0
            self._in_x = BridgeControl.COAST
            return
        # Constrain raw throttle value
        new_throttle_raw = min(max(new_throttle_raw, -63), 63)
        if new_throttle_raw < 0:
            self._vset = new_throttle_raw
            self._in_x = BridgeControl.REVERSE
        elif new_throttle_raw > 0:
            self._vset = new_throttle_raw
            self._in_x = BridgeControl.FORWARD
        else:
            self._vset = 0
            self._in_x = BridgeControl.BRAKE
        return

    @property
    def bridge_control(self):
        """Motor driver bridge status. Returns the 2-bit bridge control integer
        value and corresponding description string."""
        return self._in_x, BridgeControl.DESCRIPTOR[self._in_x]

    @property
    def fault(self):
        """Motor driver fault register status. Returns state of FAULT flag and
        a list of activated fault flag descriptors. FAULT flag is ``True`` if
        one or more fault register flags are ``True``."""
        faults = []
        if self._fault:
            faults.append(Faults.DESCRIPTOR[0])
            if self._ocp:
                faults.append(Faults.DESCRIPTOR[1])
            if self._uvlo:
                faults.append(Faults.DESCRIPTOR[2])
            if self._ots:
                faults.append(Faults.DESCRIPTOR[3])
            if self._ilimit:
                faults.append(Faults.DESCRIPTOR[4])
        return self._fault, faults

    def clear_faults(self):
        """Clears all fault conditions."""
        self._clear = True  # Clear all fault status flags

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._vset = 0
        self._in_x = BridgeControl.STANDBY
