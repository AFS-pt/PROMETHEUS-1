"""
A collection of functions for getting and validating inputs
"""

# print formatters
bold = '\033[1m'
normal = '\033[0m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'


def get_input_discrete(prompt_str, choice_values):
    print(prompt_str)
    choice = None

    choice_values_str = "("
    for i, _ in enumerate(choice_values):
        choice_values_str += f"{choice_values[i]}"
        if i < len(choice_values) - 1:
            choice_values_str += ", "
    choice_values_str += ")"

    choice_values = [cv.lower() for cv in choice_values]

    while choice not in choice_values:
        choice = input(f"{choice_values_str} ~> ").lower()
    return choice


def set_param_from_input_discrete(param, prompt_str, choice_values, allow_default=False, type=int):

    # add "enter" as a choice
    choice_values = [""] + choice_values if allow_default else choice_values
    prompt_str = prompt_str + \
        " (enter to skip):" if allow_default else prompt_str

    choice = get_input_discrete(prompt_str, choice_values)

    if choice == "":
        return param
    else:
        return type(choice)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_input_range(prompt_str, choice_range, allow_default=True):
    print(prompt_str)
    choice = None

    choice_range_str = f"({choice_range[0]} - {choice_range[1]})"

    while True:
        choice = input(f"{choice_range_str} ~> ").lower()
        if choice == "" and allow_default:
            break

        if not is_number(choice):
            continue

        if float(choice) >= choice_range[0] and float(choice) <= choice_range[1]:
            break
    return choice


def set_param_from_input_range(param, prompt_str, choice_range, allow_default=False):

    # add "enter" as a choice
    prompt_str = prompt_str + \
        " (enter to skip):" if allow_default else prompt_str

    choice = get_input_range(prompt_str, choice_range)

    if choice == "":
        return param
    else:
        return float(choice)


def manually_configure_radio(radio):
    radio.ack_delay = set_param_from_input_range(radio.ack_delay, f"Acknowledge delay (currently {radio.ack_delay} s)",
                                                 [0.0, 10.0], allow_default=True)
    radio.ack_wait = set_param_from_input_range(radio.ack_wait, f"Acknowledge RX Timeout (currently {radio.ack_wait} s)",
                                                [0.0, 100.0], allow_default=True)
    radio.receive_timeout = set_param_from_input_range(radio.receive_timeout, f"Receiver timeout (currently {radio.receive_timeout} s)",
                                                       [0.0, 100.0], allow_default=True)
    if not radio.separate_rx:
        manually_configure_rfm9x(radio.tx_device)
    else:
        print(f"\n{yellow}{bold}TX Device Configuration:{normal}")
        manually_configure_rfm9x(radio.tx_device)
        print(f"\n{yellow}{bold}RX Device Configuration:{normal}")
        manually_configure_rfm9x(radio.rx_device)


def manually_configure_rfm9x(device):
    device.frequency_mhz = set_param_from_input_range(device.frequency_mhz, f"Frequency (currently {device.frequency_mhz} MHz)",
                                                      [240.0, 960.0], allow_default=True)
    device.tx_power = set_param_from_input_discrete(device.tx_power, f"Power (currently {device.tx_power} dB)",
                                                    [f"{i}" for i in range(5, 24)], allow_default=True)
    device.coding_rate = set_param_from_input_discrete(device.coding_rate,
                                                       f"coding_rate currently {device.coding_rate}",
                                                       [f"{i}" for i in range(5, 9)],
                                                       allow_default=True)
    device.spreading_factor = set_param_from_input_discrete(device.spreading_factor,
                                                            f"current spreading factor {device.spreading_factor}",
                                                            [f"{i}" for i in range(6, 13)],
                                                            allow_default=True)
    device.signal_bandwidth = set_param_from_input_discrete(device.signal_bandwidth,
                                                            f"signal bandwidth currently {device.signal_bandwidth}",
                                                            ["7800", "10400", "15600", "20800", "31250", "41700", "62500", "125000", "250000"],
                                                            allow_default=True)
    # device.bitrate = set_param_from_input_range(device.bitrate, f"Bitrate (currently {device.bitrate} bps)",
    #                                             [500, 300000], allow_default=True)
    # device.frequency_deviation = set_param_from_input_range(device.frequency_deviation, f"Frequency deviation (currently {device.frequency_deviation})",
    #                                                         [600, 200000], allow_default=True)
    # device.rx_bandwidth = set_param_from_input_discrete(device.rx_bandwidth, f"Receiver filter bandwidth (single-sided, currently {device.rx_bandwidth})",
    #                                                     [f"{device._bw_bins_kHz[i]}" for i in range(len(device._bw_bins_kHz))], allow_default=True, type=float)
    device.lna_gain = set_param_from_input_discrete(device.lna_gain, f"LNA Gain - [max = 1, min = 6] (currently {device.lna_gain})",
                                                    [f"{i}" for i in range(1, 7)], allow_default=True)
    device.preamble_length = set_param_from_input_range(device.preamble_length, f"Preamble length (currently {device.preamble_length})",
                                                        [3, 2**16], allow_default=True)
    # device.afc_enable = set_param_from_input_discrete(device.afc_enable, f"Enable automatic frequency calibration (AFC) (currently {device.afc_enable})",
    #                                                   ["0", "1"], allow_default=True)


def print_rfm9x_configuration(device):
    print(f"\tFrequency = {device.frequency_mhz} MHz")
    print(f"\tPower = {device.tx_power} dBm")
    print(f"\tcoding reate = {device.coding_rate}")
    print(f"\tsignal bandwidth = {device.signal_bandwidth}")
    print(f"\tspreading factor = {device.spreading_factor}")
    # print(f"\tBitrate = {device.bitrate} Hz")
    # print(f"\tFrequency Deviation = {device.frequency_deviation}")
    # print(f"\tRX filter bandwidth = {device.rx_bandwidth}")
    # print(f"\tLNA Gain [max = 1, min = 6] = {device.lna_gain}")
    print(f"\tPreamble Length = {device.preamble_length}")
    # print(f"\tAFC enabled = {device.afc_enable}")


def print_radio_configuration(radio):
    print(f"{yellow}{bold}Radio Configuration:{normal}")
    print(f"\tNode addr = {radio.node}\tDest addr = {radio.destination}")
    print(f"\tAcknowledge delay = {radio.ack_delay} s")
    print(f"\tAcknowledge wait = {radio.ack_wait} s")
    print(f"\tReceive timeout = {radio.receive_timeout} s")
    if not radio.separate_rx:
        print_rfm9x_configuration(radio.tx_device)
    else:
        print(f"\t{yellow}{bold}TX Device Configuration:{normal}")
        print_rfm9x_configuration(radio.tx_device)
        print(f"\t{yellow}{bold}RX Device Configuration:{normal}")
        print_rfm9x_configuration(radio.rx_device)
