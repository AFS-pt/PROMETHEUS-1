from lib.pycubed import cubesat


def get_user_input():
    """
    Ask the user to type y/any key to start/cancel the test
    If y, return user inputs for voltage level and duration
    If any other key, return  None
    """

    # conduct the test
    print("Initializing burnwire test...")
    print("You can test using a multimeter or fishing line.")
    print("""If using a multimeter, please read the voltage between the ground pin
(GND) and burnwire pin on the -Z solar board.""")

    dutycycle = float(input("At what duty cycle do you want to run the burnwire[0,1]: "))
    duration = float(input("How many seconds to run the burnwire: "))

    start_test = input("Type Y to start the test, any key to cancel: ")
    if start_test.lower() != "y":
        return None, None

    return dutycycle, duration


async def burnwire_test(result_dict):
    """
    Retrieve burnwire and voltage level from get_user_input() and run the test
    If None, update the result dictionary that the test was not run
    Else, process user inputted test results and update the result dictionary
    """

    dutycycle, duration = get_user_input()

    if dutycycle is None or duration is None:
        result_dict["Burnwire"] = ("Test was not run.", None)
        return result_dict

    await cubesat.burn(dutycycle, duration)

    success_input = input("Did the test work as expected? (Y/N): ")
    success = False
    if success_input.lower() == "y":
        success = True

    # process results
    result_val_string = f"Tested burnwire at dutycle {dutycycle} for {duration} seconds."
    result_dict["Burnwire"] = (result_val_string, success)
    return result_dict


async def run(result_dict):
    """
    Check burnwire 1 and 2
    If initialized correctly, run test and update result dictionary
    through burnwire_test
    If not initialized, update result dictionary
    """

    # if no Burn Wire 1 detected, update result dictionary
    if not cubesat.burnwire1:
        result_dict["Burnwire1"] = ("No burnwire 1 detected", None)
    else:  # Burn Wire 1 detected, run tests
        print("Starting Burnwire1 test...")
        await burnwire_test(result_dict)
        print("Burnwire1 Test complete.\n")

    return result_dict
