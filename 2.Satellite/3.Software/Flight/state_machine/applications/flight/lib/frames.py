try:
    import ulab.numpy as np
    from ulab.numpy import cos, sin, pi, arctan2, sqrt, array
except ImportError:
    import numpy as np
    from numpy import cos, sin, pi, arctan2, sqrt, array

J2000 = 946684800  # unix timestamp for the Julian date 2000-01-01
MJD_ZERO = 2400000.5  # Offset of Modified Julian Days representation with respect to Julian Days.
JD2000 = 2451545.0  # Reference epoch (J2000.0), Julian Date
MJD2000 = 51544.5  # MJD at J2000.0
PI2 = 6.283185307179586
EQUATORIAL_RADIUS = 6378.137  # Equatorial raduis of the Earth (km)

def mjd(utime):
    """Returns the Modified Julian Date (MJD) for a given unix timestamp."""
    return utime / 86400.0 + 40587

def rotZ(theta):
    """Returns the rotation matrix for a given angle around the z-axis.

    :param theta: Angle in radians.
    :type theta: float
    :returns: A 3x3 numpy array.
    """
    return array([[cos(theta),   sin(theta),  0],
                  [-sin(theta),  cos(theta),  0],
                  [0,            0,           1]])

def ERA(utime):
    """Returns the the ERA (Earth Rotation Angle) at a certain unix time stamp.
    Inspired by SOFA's iauEra00 function.

    :param utime: A unix timestamp
    :type utime: int
    :returns: The Earth Rotation Angle in radians.
    """
    # Days since J2000.0.
    d = mjd(utime)
    days = d - MJD2000
    # Fractional part of T (days).
    f = (d % 1.0)
    # Earth rotation angle at this UT1.
    theta = (PI2 * (f + 1.2790572732640 + 0.00273781191135448 * days)) % (2 * PI2)

    return theta

def earth_rotation(utime):
    """Computes rotation matrix based on the Earth Rotation Angle (ERA) at a certain unix time stamp."""
    # Compute Earth rotation angle
    era = ERA(utime)
    # Rotate Matrix and return
    R = rotZ(era)
    return R

def eci_to_ecef(utime):
    """Returns the rotation matrix from ECI (Earth Centered Inertial) to ECEF (Earth Centered Earth Fixed).
    Applies correction for Earth-rotation.
    Based on SatelliteDynamic's rECItoECEF.

    :param utime: A unix timestamp
    :type utime: int
    :returns: A 3x3 numpy array.
    """
    # we may choose to add bias_precession_nutation and polar motion in the future
    # rc2i = bias_precession_nutation(epc)
    R = earth_rotation(utime)
    # rpm  = polar_motion(epc)

    # return rpm @ r @ rc2i
    return R

def ecef_to_eci(utime):
    """Returns the rotation matrix from ECEF (Earth Centered Earth Fixed) to ECI (Earth Centered Inertial).

    :param utime: A unix timestamp
    :type utime: int
    :returns: A 3x3 numpy array.
    """
    return eci_to_ecef(utime).transpose()

def ned_to_ecef(lon, lat):
    """ Returns the rotation matrix for transforming coordinates in an earth-centered NED frame
    to coordinates in an ECEF frame.

    :param lon: Longitude in radians (geocentric).
    :type lon: float
    :param lat: Latitude in radians (geocentric).
    :param lat: float
    :returns: A 3x3 numpy array.
    """
    return array([[-sin(lat) * cos(lon),  -sin(lon), -cos(lat) * cos(lon)],
                  [-sin(lat) * sin(lon),   cos(lon), -cos(lat) * sin(lon)],
                  [cos(lat),               0.0,      -sin(lat)]])

def convert_ecef_to_geoc(ecef, degrees=False):
    """Converts from ECEF (Earth Centered Earth Fixed) to geocentric coordinates.

    :param ecef: ECEF coordinates in km.
    :type ecef: numpy.array
    :param degrees: If True, returns the coordinates in degrees.
    :type degrees: bool, optional
    :returns: A 3x1 numpy arary containing the geocentric coordinates long, lat, alt (radians, radians, km)
    """
    x, y, z = ecef
    lat = arctan2(z, sqrt(x * x + y * y))
    lon = arctan2(y, x)
    alt = sqrt(x * x + y * y + z * z) - EQUATORIAL_RADIUS

    # Convert output to degrees
    if degrees:
        lat = lat * 180.0 / pi
        lon = lon * 180.0 / pi

    return array([lon, lat, alt])
