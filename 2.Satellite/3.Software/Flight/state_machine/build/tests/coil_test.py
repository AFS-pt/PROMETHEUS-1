import time
from lib.pycubed import cubesat
try:
    import ulab.numpy as numpy
except ImportError:
    import numpy

# voltage level constants; set between -1 and 1
v1 = 0.25
v2 = 0.5
v3 = 0.75

# find projected voltage: vlevel * max voltage
projected_v1 = v1 * 5.06
projected_v2 = v2 * 5.06
projected_v3 = v3 * 5.06

# alias norm
norm = numpy.linalg.norm


def test_voltage_levels(coil_index):
    """
    Ask the user to type y/any key to start/cancel the test
    If y, collect IMU magnetometer data for different voltage levels,
    and return if the magnetometer readings are increasing as voltage
    levels are increasing.
    If any other key, return  None
    """

    # wait times
    driver_time = 1

    # set up the test
    print(f"""Testing Coil Driver {coil_index} for the following voltage
levels: {0.0} V, {projected_v1} V, {projected_v2} V, {projected_v3} V.""")

    # conduct the test
    start_test = input("Type Y to start the test, any key to cancel: ")
    if start_test.lower() != "y":
        return None, None

    # test at 0V to get a starter reading
    cubesat.coildriver_vout(coil_index, 0)
    mag_reading0 = cubesat.magnetic

    # test each voltage level
    cubesat.coildriver_vout(coil_index, projected_v1)
    time.sleep(driver_time)
    mag_reading1 = cubesat.magnetic

    cubesat.coildriver_vout(coil_index, projected_v2)
    time.sleep(driver_time)
    mag_reading2 = cubesat.magnetic

    cubesat.coildriver_vout(coil_index, projected_v3)
    time.sleep(driver_time)
    mag_reading3 = cubesat.magnetic

    cubesat.coildriver_vout(coil_index, 0)

    # calculate total magnetic reading, subtracting the 0V starter reading
    print("Data Collection Complete")
    mag_total1 = norm(numpy.array(mag_reading1) - numpy.array(mag_reading0))
    mag_total2 = norm(numpy.array(mag_reading2) - numpy.array(mag_reading0))
    mag_total3 = norm(numpy.array(mag_reading3) - numpy.array(mag_reading0))

    # if magnetometer readings are increasing over time, return true
    mag3_greater_mag2 = (mag_total3 - mag_total2) >= 10  # µT
    mag2_greater_mag1 = (mag_total2 - mag_total1) >= 10  # µT
    result_val_bool = mag3_greater_mag2 and mag2_greater_mag1

    # store the voltage levels tested and mag readings in a string
    mag_reading_string = f"""Coil Driver {coil_index} (voltage level, mag reading):
({0.0} V, {norm(mag_reading0)} µT), ({projected_v1} V, {norm(mag_reading1)} uT),
({projected_v2} V, {norm(mag_reading2)} uT), ({projected_v3} V, {norm(mag_reading3)} uT)"""

    # if the test failed, print that the test failed, as well as the readings
    if not result_val_bool:
        print(f"""Magnetometer results should have been increasing but were not.
{mag_reading_string}""")
    # if the test passed, print the readings
    else:
        print(mag_reading_string)

    # return pass/fail and the readings in string form
    return result_val_bool, mag_reading_string


def coil_test(result_dict, coil_index):
    """
    Get boolean result of test_voltage_levels, which tells us
    if magnetometer readings are increasing correctly
    If result is None, update the result dictionary that the test was not run
    Else, process user inputted test results and update the result dictionary
    """

    # set string constant
    result_key = f"CoilDriver{coil_index}"

    # get user test result values, process and print results
    result, mag_reading_string = test_voltage_levels(coil_index)

    # user cancelled the test, update result dictionary
    if result is None and mag_reading_string is None:
        result_dict[result_key] = (f"{result_key} not tested.", None)
        return result_dict

    # user proceeded with test, update result dictionary
    result_dict[result_key] = (mag_reading_string, result)
    return result_dict


async def run(result_dict):
    """
    Check coil driver X, Y, and Z
    If initialized correctly, run test and update result dictionary
    through coil_test
    If not initialized, update result dictionary
    """

    # if no Coil X detected, update result dictionary
    if not cubesat.drv_x:
        result_dict["CoilDriverX"] = ("No Coil Driver X detected", None)
    else:  # Coil X detected, run tests
        print("Starting Coil Driver X test...")
        coil_test(result_dict, 'X')
        print("Coil Driver X Test complete.\n")

    # if no Coil Y detected, update result dictionary
    if not cubesat.drv_y:
        result_dict["CoilDriverY"] = ("No Coil Driver Y detected", None)
    else:  # Coil Y detected, run tests
        print("Starting Coil Driver Y test...")
        coil_test(result_dict, 'Y')
        print("Coil Driver Y Test complete.\n")

    # if no Coil Z detected, update result dictionary
    if not cubesat.drv_z:
        result_dict["CoilDriverZ"] = ("No Coil Driver Z detected", None)
    else:  # Coil Z detected, run tests
        print("Starting Coil Driver Z test...")
        coil_test(result_dict, 'Z')
        print("Coil Driver Z Test complete.\n")

    return result_dict
