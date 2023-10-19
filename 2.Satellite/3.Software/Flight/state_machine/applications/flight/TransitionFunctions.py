def announcer(source, destination, cubesat):
    print(f'We are transitioning from {source} -> {destination}!!!')
    print(f'We also have access to the cubesat object: {cubesat}')


def low_power_on(source, destination, cubesat):
    print('Turning off power hungry devices')
    cubesat.enable_low_power()


def low_power_off(source, destination, cubesat):
    print('Setting devices back to normal power modes')
    cubesat.disable_low_power()
