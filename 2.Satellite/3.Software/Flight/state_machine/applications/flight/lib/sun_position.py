# Based on: https://github.com/spacecraft-design-lab-2019/flight-software/blob/master/sun-position/sun_position.py
try:
    from ulab.numpy import array, degrees, radians, cos, sin
except ImportError:
    from numpy import array, degrees, radians, cos, sin

def unix_time_to_julian_day(unix_time):
    """Takes in a unix timestamp and returns the julian day"""
    return unix_time / 86400 + 2440587.5

def approx_sun_position_ECI(utime):
    """
    Formula taken from "Satellite Orbits: Models, Methods and Applications" by Motenbruck and Gill
    See section 3.3.2 on page 70 for the formula
    Modified to take unix time as input.

    Args:
        - utime: unix timestamp

    Returns:
        - sun pointing in Earth Centered Intertial (ECI) frame (km)
    """
    JD = unix_time_to_julian_day(utime)
    OplusW = 282.94  # Ω + ω
    T = (JD - 2451545.0) / 36525

    M = radians(357.5256 + 35999.049 * T)

    long = radians(OplusW + degrees(M) + (6892 / 3600) * sin(M) + (72 / 3600) * sin(2 * M))
    r_mag = (149.619 - 2.499 * cos(M) - 0.021 * cos(2 * M)) * 10**6

    epsilon = radians(23.43929111)
    r_vec = array([r_mag * cos(long),
                   r_mag * sin(long) * cos(epsilon),
                   r_mag * sin(long) * sin(epsilon)])

    return r_vec
