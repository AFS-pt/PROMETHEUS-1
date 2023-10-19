import struct
import os
try:
    from ulab.numpy import array, nan
except ImportError:
    from numpy import array, nan
from pycubed import cubesat
from state_machine import state_machine
from collections import namedtuple

# 3 uint8 + 1 uint16 + 11 float32
# = 49 bytes of data
# = 52 byte c struct (1 extra to align chars, 2 extra to align short)
beacon_format = 3 * 'B' + 'H' + 'f' * 11

# Defines what the unpack_beacon will return
beacon_tuple = namedtuple("beacon_tuple", ("state_index", "datetime_valid_flag", "contact_flag",
                                           "burn_flag", "software_error_count", "boot_count",
                                           "battery_voltage", "cpu_temperature_C", "imu_temperature_C",
                                           "gyro", "mag", "RSSI_dB", "FEI_Hz"))

# 6 float32
# = 24 bytes of data
system_format = 6 * 'f'

# defines what the system_unpack will return
system_tuple = namedtuple("system_tuple", ("lux_xp", "lux_yp", "lux_zp",
                                           "lux_xn", "lux_yn", "lux_zn"))
# 2 unint8
# = 4 bytes
time_format = 2 * 'H'

# defines what the time_unpack will return
time_tuple = namedtuple("time_tuple", ("tm_min", "tm_sec"))

telemetry_tuple = namedtuple("telemetry_tuple", ("time", "beacon", "system"))

def beacon_packet():
    """Creates a beacon packet containing the: state index byte,
    f_datetime_valid, f_contact and f_burn flags,
    state_error_count, boot count, battery voltage,
    CPU temperature, IMU temperature, gyro reading, mag reading,
    radio signal strength (RSSI), radio frequency error (FEI).

    This data is packed into a c struct using `struct.pack`.
    """
    state_byte = state_machine.states.index(state_machine.state)
    flags = ((cubesat.f_datetime_valid << 2) |
             (cubesat.f_contact << 1) |
             (cubesat.f_burn)) & 0xFF
    software_error = cubesat.c_software_error
    boot_count = cubesat.c_boot
    vbatt = cubesat.battery_voltage
    cpu_temp = cubesat.temperature_cpu if cubesat.micro else nan
    imu_temp = cubesat.temperature_imu if cubesat.imu else nan
    gyro = cubesat.gyro if cubesat.imu else array([nan, nan, nan])
    mag = cubesat.magnetic if cubesat.imu else array([nan, nan, nan])
    rssi = cubesat.radio.last_rssi if cubesat.radio else nan
    fei = cubesat.radio.frequency_error if cubesat.radio else nan
    return struct.pack(beacon_format,
                       state_byte, flags, software_error, boot_count,
                       vbatt, cpu_temp, imu_temp,
                       gyro[0], gyro[1], gyro[2],
                       mag[0], mag[1], mag[2],
                       rssi, fei)

def system_packet():
    """Function for logging system data, packs this data into a
    c struct.

    includes the: lux values from each sun sensor
    """
    lux_xp = cubesat.sun_xp.lux if cubesat.sun_xp and cubesat.sun_xp.lux is not None else nan
    lux_yp = cubesat.sun_yp.lux if cubesat.sun_yp and cubesat.sun_yp.lux is not None else nan
    lux_zp = cubesat.sun_zp.lux if cubesat.sun_zp and cubesat.sun_zp.lux is not None else nan
    lux_xn = cubesat.sun_xn.lux if cubesat.sun_xn and cubesat.sun_xn.lux is not None else nan
    lux_yn = cubesat.sun_yn.lux if cubesat.sun_yn and cubesat.sun_yn.lux is not None else nan
    lux_zn = cubesat.sun_zn.lux if cubesat.sun_zn and cubesat.sun_zn.lux is not None else nan
    return struct.pack(system_format,
                       lux_xp, lux_yp, lux_zp,
                       lux_xn, lux_yn, lux_zn)

def time_packet(t):
    """returns a struct containing only the minutes and seconds, which are
    all that is necessary given the file name will contain the year, month
    day, hour"""

    (tm_year, tm_month, tm_day,
     tm_hour, tm_min, tm_sec,
     tm_wday, tm_yday, tm_isdst) = t
    return struct.pack(time_format,
                       tm_min, tm_sec)

def telemetry_packet(t):
    return bytearray(time_packet(t)) + bytearray(beacon_packet()) + bytearray(system_packet())

def human_time_stamp(t):
    """Returns a human readable time stamp in the format: 'boot_year.month.day_hour:min'
    Gets the time from the RTC.

    :param t: The time to format
    :type t: time.struct_time"""
    boot = cubesat.c_boot
    return f'{boot:05}_{t.tm_year:04}.{t.tm_mon:02}.{t.tm_mday:02}_{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}'

def try_mkdir(path):
    """Tries to make a directory at the given path.
    If the directory already exists it does nothing."""
    try:
        os.mkdir(path)
    except Exception:
        pass

def unpack_beacon(bytes):
    """Unpacks the fields from the beacon packet packed by `beacon_packet`
    """
    (state_byte, flags, software_error, boot_count,
     vbatt, cpu_temp, imu_temp,
     gyro0, gyro1, gyro2,
     mag0, mag1, mag2,
     rssi, fei) = struct.unpack(beacon_format, bytes)

    gyro = array([gyro0, gyro1, gyro2])
    mag = array([mag0, mag1, mag2])

    return beacon_tuple(state_byte, bool(flags & (0b1 << 2)), bool(flags & (0b1 << 1)),
                        bool(flags & (0b1 << 0)), software_error,
                        boot_count, vbatt, cpu_temp,
                        imu_temp, gyro, mag,
                        rssi, fei)


def unpack_system(bytes):
    (lux_xp, lux_yp, lux_zp,
     lux_xn, lux_yn, lux_zn) = struct.unpack(system_format, bytes)
    return system_tuple(lux_xp, lux_yp, lux_zp,
                        lux_xn, lux_yn, lux_zn)

def unpack_time(bytes):
    (tm_min, tm_sec) = struct.unpack(time_format, bytes)
    return time_tuple(tm_min, tm_sec)

def unpack_telemetry(bytes):
    """returns the contents of the telemetry file as a named tuple of named tuples
    For example: you could access the gyro values via unpack_telemetry().beacon.gyro"""
    time_buffer = struct.calcsize(time_format)
    beacon_buffer = struct.calcsize(beacon_format)
    system_buffer = struct.calcsize(system_format)
    t = unpack_time(bytes[0:time_buffer])
    beacon = unpack_beacon(bytes[time_buffer:time_buffer + beacon_buffer])
    system = unpack_system(bytes[time_buffer + beacon_buffer:time_buffer + beacon_buffer + system_buffer])
    return telemetry_tuple(t, beacon, system)
