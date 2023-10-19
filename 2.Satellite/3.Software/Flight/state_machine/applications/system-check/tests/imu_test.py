"""
Tests that the IMU sensors exist and are returning reasonable values.
Attempts to ensure the driver gives results in the satellite reference frame.
"""

from lib.pycubed import cubesat
from print_utils import bold, normal
import time
from test_utils import expect, less_in_magnitude, greater_in_magnitude, vec_approx_equal_generator
from test_utils import vec_different_generator, between
try:
    from ulab import numpy
except ImportError:
    import numpy


wait_time = 3
norm = numpy.linalg.norm
ACCEL_THRESHOLD = 1.5


async def magnet_imu_test(result_dict):
    """
    Check that the magnetometer reading increased as the magnet was
    moved closer
    """
    input(f"Slowly move the magnet closer to the cubesat for {wait_time} seconds:")

    mag_initial = cubesat.magnetic
    time.sleep(wait_time)
    mag_final = cubesat.magnetic

    different_by_10 = vec_different_generator(10)

    result_dict["IMU_MagMagnet"] = expect(mag_initial, different_by_10, mag_final)

def update_result_dict_from_list(result_dict, result_list, all_passed_key, all_passed_str):
    """
    If all tests passed, update result dictionary with all_passed_key and all_passed_str
    Otherwise update result dictionary with all tests in result_list
    """
    all_passed = True
    for (key, (msg, passed)) in result_list:
        if not passed:
            all_passed = False
            break
    if all_passed:
        result_dict[all_passed_key] = (all_passed_str, True)
    else:
        for (key, (msg, passed)) in result_list:
            result_dict[key] = (msg, passed)

async def run(result_dict):
    """
    If initialized correctly, run tests and update result dictionary
    If not initialized, update result dictionary.
    Tests include:
    - Check gyro reading is near 0 when stationary
    - Check accelerometer reads g correctly in all 3 directions
    - Check gyro reading is more than 1 when rotated
    - Check magnetometer readings increase as a magnet is moved closer
    - Check the temperature is within a reasonable range
    """

    if not cubesat.imu:
        result_dict["IMU"] = ("Not detected", False)
        return
    else:
        result_dict["IMU"] = ("Detected", True)

    # accelerometer tests
    directions = [
        ("X", numpy.array([9.8, 0, 0])),
        ("Y", numpy.array([0, 9.8, 0])),
        ("Z", numpy.array([0, 0, 9.8])),
    ]
    accel_results = []
    approx_equal = vec_approx_equal_generator(ACCEL_THRESHOLD)
    for (axis, expected) in directions:
        input(f"Place the cubesat with the {bold}+{axis}{normal} board facing up and press enter: ")
        res = expect(cubesat.acceleration, approx_equal, expected)
        accel_results.append((f"IMU_Accel_{axis}", res))
    update_result_dict_from_list(result_dict, accel_results, "IMU_Accel", "Success")

    # gyro tests
    gyro_results = []
    input("Place the cubesat on a flat surface and press enter: ")
    gyro_results.append(
        ("IMU_Gyro_Stationary", expect(cubesat.gyro, less_in_magnitude, 1))
    )
    input("Move the cubesat around for a few seconds after pressing enter: ")
    time.sleep(1.0)
    gyro_results.append(
        ("IMU_Gyro_Moving", expect(cubesat.gyro, greater_in_magnitude, 1))
    )
    update_result_dict_from_list(result_dict, gyro_results, "IMU_Gyro", "Success")

    # magnetometer test
    await magnet_imu_test(result_dict)

    # temperature test
    result_dict["IMU_Temp"] = expect(cubesat.temperature_imu, between, (20, 80))
