import time
try:
    from ulab.numpy import zeros, median
except ImportError:
    from numpy import zeros, median
from lib.pycubed import cubesat

def sensor_rate_test(sensor):
    trials = 100
    dt_list = zeros(trials)
    for i in range(trials):
        start_time = time.monotonic_ns()
        _ = sensor
        _ = sensor
        end_time = time.monotonic_ns()
        dt_list[i] = end_time - start_time
    worst_case = max(dt_list)
    best_case = min(dt_list)
    med_case = median(dt_list)
    return (f"worst case: {worst_case}, best case: {best_case}, median: {med_case}", True)

async def run(result_dict):
    """
    checks how fast the satellite can make two successive calls to a sensor
    to get its data.
    """
    print("Testing sensor rates...\n")
    sensors = [
        (cubesat.sun_xn.lux, "SUN_X-"),
        (cubesat.sun_xp.lux, "SUN_X+"),
        (cubesat.sun_yn.lux, "SUN_Y-"),
        (cubesat.sun_yp.lux, "SUN_Y+"),
        (cubesat.sun_zn.lux, "SUN_Z-"),
        (cubesat.sun_zp.lux, "SUN_Z+"),
        (cubesat.imu.accel, "IMU_ACCEL"),
        (cubesat.imu.gyro, "IMU_GYRO"),
        (cubesat.imu.mag, "IMU_MAG"),
    ]
    for (sensor, name) in sensors:
        result_dict[f"{name}_rate_test"] = sensor_rate_test(sensor)

    print("Done testing Sensor rates\n")
