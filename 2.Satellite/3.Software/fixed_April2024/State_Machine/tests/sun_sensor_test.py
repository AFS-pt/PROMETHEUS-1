from lib.pycubed import cubesat
from print_utils import bold, normal
import time

def test_sun_sensor(sensor, sensor_name, sensors):
    """
    Tests if a sun sensor is:
        - Detected
        - Driver sensor coresponds to the correct physical sensor
    """
    if sensor is None:
        return ("not detected", False)
    input(f'Place the {bold}{sensor_name}{normal} board face down on the table, then press enter: ')
    min_lux = sensor.lux
    for i in range(len(sensors)):
        (other, other_name) = sensors[i]
        if other is None:
            continue
        lux = other.lux
        if lux < min_lux and other != sensor:
            return (f"{sensor_name} should read the lowest lux, but {other_name} read lower ({min_lux} > {lux})", False)
    return ("success", True)

"""AFS
def consistency_test():
    trials = 100
    entries = [0] * trials
    totals = [0, 0, 0]
    for i in range(trials):
        sv = cubesat.sun_vector
        entries[i] = sv
        totals[0] += sv[0]
        totals[1] += sv[1]
        totals[2] += sv[2]
        time.sleep(0.1)
    avg_v = [totals[0] / trials, totals[1] / trials, totals[2] / trials]
    x_outliers = 0
    y_outliers = 0
    z_outliers = 0
    for i in range(trials):
        if not (avg_v[0] - 5 <= entries[i][0] <= avg_v[0] + 5):
            x_outliers += 1
        if not (avg_v[1] - 5 <= entries[i][1] <= avg_v[1] + 5):
            y_outliers += 1
        if not (avg_v[2] - 5 <= entries[i][2] <= avg_v[2] + 5):
            z_outliers += 1
    outlier_sum = x_outliers + y_outliers + z_outliers
    if outlier_sum > (trials * 3) / 10:
        # greater than 10% outliers
        return (f"too many outliers: (x: {x_outliers}, y: {y_outliers}, z: {z_outliers})", False)
    return ("passed sun sensor consistency test", True)

"""



async def run(result_dict):
    """
    Check all that all sun sensors exists, and are properly configured
    """
    print("Testing Sun Sensors\n")
#AFS    result_dict["sun_vector_consistency"] = consistency_test()
    sensors = [
        (cubesat.sun_xn, "X-"),
        (cubesat.sun_xp, "X+"),
        (cubesat.sun_yn, "Y-"),
        (cubesat.sun_yp, "Y+"),
        (cubesat.sun_zn, "Z-"),
        (cubesat.sun_zp, "Z+"),
    ]
    for (sensor, sensor_name) in sensors:
        (str, success) = test_sun_sensor(sensor, sensor_name, sensors)
        result_dict[f'Sun Sensor {sensor_name}'] = (str, success)
        if not success:
            print(f'Sun Sensor {sensor_name} failed: {str}')

    print("Done Testing Sun Sensors\n")
