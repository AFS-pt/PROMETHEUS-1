import struct
import os
try:
    from ulab.numpy import array, nan
except ImportError:
    from numpy import array, nan
from pycubed import cubesat
from state_machine import state_machine

# 3 uint8 + 1 uint16 + 11 float32
# = 49 bytes of data
# = 52 byte c struct (1 extra to align chars, 2 extra to align short)
beacon_format = 3 * 'B' + 'H' + 'f' * 11

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

    return {"state_index": state_byte,
            "datetime_valid_flag": bool(flags & (0b1 << 2)),
            "contact_flag": bool(flags & (0b1 << 1)),
            "burn_flag": bool(flags & (0b1 << 0)),
            "software_error_count": software_error,
            "boot_count": boot_count,
            "battery_voltage": vbatt,
            "cpu_temperature_C": cpu_temp,
            "imu_temperature_C": imu_temp,
            "gyro": gyro,
            "mag": mag,
            "RSSI_dB": rssi,
            "FEI_Hz": fei,
            }
