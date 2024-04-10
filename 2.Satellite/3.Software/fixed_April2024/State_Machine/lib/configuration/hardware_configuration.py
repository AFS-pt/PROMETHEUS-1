
# PROMETHEUS-1 AFS

from ulab.numpy import array

HARDWARE_VERSION = "B3/01"      # April 2023
# HARDWARE_VERSION = "B2/01"    # new flight boards (Dec 2022)
# HARDWARE_VERSION = "B1/02"    # Oct 2022
# HARDWARE_VERSION = "B1/01"    # Aug 2022

SUN_TYPE_TSL2561 = 1
SUN_TYPE_OPT3001 = 2

IMU_TYPE_BMX160 = 1
IMU_TYPE_BNO08X = 2

if HARDWARE_VERSION == "B3/01":

    SUN_TYPE = SUN_TYPE_OPT3001
    IMU_TYPE = IMU_TYPE_BNO08X

    SUN_XN_I2C = 3
    SUN_XN_ADDRESS = 0x44

    SUN_YN_I2C = 1
    SUN_YN_ADDRESS = 0x44

    SUN_ZN_I2C = 2
    SUN_ZN_ADDRESS = 0x44

    SUN_XP_I2C = 3
    SUN_XP_ADDRESS = 0x45

    SUN_YP_I2C = 1
    SUN_YP_ADDRESS = 0x45

    SUN_ZP_I2C = 2
    SUN_ZP_ADDRESS = 0x45

    COIL_X_I2C = 1
    COIL_X_ADDRESS = 0x60

    COIL_Y_I2C = 1
    COIL_Y_ADDRESS = 0x61

    COIL_Z_I2C = 1
    COIL_Z_ADDRESS = 0x64

    CURRENT_I2C = 1
    CURRENT_ADDRESS = 0x40

    RTC_I2C = 1

    """
    IMU no longer I2C device
    IMU_I2C = 1
    IMU_ADDRESS = 0x69
    """

    R_IMU2BODY = array([[0., -1., 0.], [0., 0., 1.], [-1., 0., 0.]])

elif HARDWARE_VERSION == "B2/01":

    SUN_TYPE = SUN_TYPE_TSL2561
    IMU_TYPE = IMU_TYPE_BMX160

    SUN_XN_I2C = 3
    SUN_XN_ADDRESS = 0x29

    SUN_YN_I2C = 1
    SUN_YN_ADDRESS = 0x29

    SUN_ZN_I2C = 2
    SUN_ZN_ADDRESS = 0x29

    SUN_XP_I2C = 3
    SUN_XP_ADDRESS = 0x49

    SUN_YP_I2C = 1
    SUN_YP_ADDRESS = 0x49

    SUN_ZP_I2C = 2
    SUN_ZP_ADDRESS = 0x49

    COIL_X_I2C = 1
    COIL_X_ADDRESS = 0x60

    COIL_Y_I2C = 1
    COIL_Y_ADDRESS = 0x62

    COIL_Z_I2C = 1
    COIL_Z_ADDRESS = 0x68

    RTC_I2C = 2

    IMU_I2C = 1
    IMU_ADDRESS = 0x69

    R_IMU2BODY = array([[0., -1., 0.], [0., 0., 1.], [-1., 0., 0.]])

elif HARDWARE_VERSION == "B1/02":

    SUN_TYPE = SUN_TYPE_TSL2561
    IMU_TYPE = IMU_TYPE_BMX160

    SUN_XN_I2C = 3
    SUN_XN_ADDRESS = 0x29

    SUN_YN_I2C = 1
    SUN_YN_ADDRESS = 0x29

    SUN_ZN_I2C = 2
    SUN_ZN_ADDRESS = 0x29

    SUN_XP_I2C = 3
    SUN_XP_ADDRESS = 0x49

    SUN_YP_I2C = 1
    SUN_YP_ADDRESS = 0x49

    SUN_ZP_I2C = 2
    SUN_ZP_ADDRESS = 0x49

    COIL_X_I2C = 1
    COIL_X_ADDRESS = 0x60

    COIL_Y_I2C = 1
    COIL_Y_ADDRESS = 0x62

    COIL_Z_I2C = 1
    COIL_Z_ADDRESS = 0x69

    RTC_I2C = 2

    IMU_I2C = 1
    IMU_ADDRESS = 0x68

    R_IMU2BODY = array([[-1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])

elif HARDWARE_VERSION == "B1/01":

    SUN_TYPE = SUN_TYPE_TSL2561
    IMU_TYPE = IMU_TYPE_BMX160

    SUN_XN_I2C = 2
    SUN_XN_ADDRESS = 0x49

    SUN_YN_I2C = 3
    SUN_YN_ADDRESS = 0x29

    SUN_ZN_I2C = 3
    SUN_ZN_ADDRESS = 0x39

    SUN_XP_I2C = 2
    SUN_XP_ADDRESS = 0x29

    SUN_YP_I2C = 3
    SUN_YP_ADDRESS = 0x49

    SUN_ZP_I2C = 2
    SUN_ZP_ADDRESS = 0x39

    COIL_X_I2C = 1
    COIL_X_ADDRESS = 0xC4 >> 1

    COIL_Y_I2C = 1
    COIL_Y_ADDRESS = 0xC0 >> 1

    COIL_Z_I2C = 1
    COIL_Z_ADDRESS = 0xD0 >> 1

    RTC_I2C = 2

    IMU_I2C = 1
    IMU_ADDRESS = 0x69

    R_IMU2BODY = array([[-1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])

else:
    raise ValueError(f"Invalid hardware version {HARDWARE_VERSION}")