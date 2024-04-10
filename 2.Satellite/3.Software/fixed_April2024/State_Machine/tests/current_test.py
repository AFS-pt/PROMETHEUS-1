from lib.pycubed import cubesat
import time

def current_test():
    """
    Tests if the current sensor:
        - returns consistent values
        - (possible for future) has a reasonable average value
                - need to know how many mA the satellite should be running at on idle.
    """
    measurements = 100
    vals = [0] * measurements
    outlier_count = 0

    # threshold in mA, such that a measurement counts as an outlier
    outlier_threshold = 2
    for i in range(measurements):
        vals[i] = cubesat.battery_current
        time.sleep(0.05)
    sum = 0
    for val in vals:
        sum += val
    avg = sum / measurements
    for val in vals:
        if not ((avg - outlier_threshold) <= val <= (avg + outlier_threshold)):
            outlier_count += 1

    # if greater than 10% of the data points are far away from the average
    # the sensor is giving strange and possibly inaccurate readings.
    if (outlier_count >= measurements / 10):
        return (f"current was inconsistent: {outlier_count} outliers", False)

    return (f"passed current test, average {avg} mA", True)


async def run(result_dict):
    """
    basic current sensor test to verify that the hardware is connected
    and returning reasonable values
    """
    if cubesat.current_sensor:
        print("running current tests, will take ~5 seconds ...")
        result_dict["Basic_Current_test"] = current_test()
        print("done running current test!")
    else:
        result_dict["Basic_Current_test"] = (
            "cannot test current sensor; no current sensor detected", None)
