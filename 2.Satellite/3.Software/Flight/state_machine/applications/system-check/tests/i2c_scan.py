from lib.pycubed import cubesat


async def run(result_dict):
    """
    For each i2c device, print addresses of connected devices
    """
    print("Starting I2C Scan...")
    while not cubesat.i2c1.try_lock():
        pass
    print("Addresses of Devices Connected to I2C1:",
          [hex(x) for x in cubesat.i2c1.scan()])
    cubesat.i2c1.unlock()

    while not cubesat.i2c2.try_lock():
        pass
    print("Addresses of Devices Connected to I2C2:",
          [hex(x) for x in cubesat.i2c2.scan()])
    cubesat.i2c2.unlock()

    while not cubesat.i2c3.try_lock():
        pass
    print("Addresses of Devices Connected to I2C3:",
          [hex(x) for x in cubesat.i2c3.scan()])
    cubesat.i2c3.unlock()

    print("I2C Scan Complete.\n")
