# Simple circuitpython receiver to verify radio hardware
import board
import busio
import digitalio
import time
import struct
import lib.bmx160 as bmx160
import lib.adafruit_rfm9x as adafruit_rfm9x
try:
    from ulab.numpy import array, nan
except ImportError:
    from numpy import array, nan


# I2C and IMU init

i2c1 = busio.I2C(board.SCL1,board.SDA1)
IMU = bmx160.BMX160_I2C(i2c1,address=0x69)


# Payload packet definition

# 10 float32:
# acc[3] + gyro[3] + mag[3] + temp
payload_format = 'f' * 10

def payload_packet():
    #Creates a beacon packet containing the: state index byte,
    #f_datetime_valid, f_contact and f_burn flags,
    #state_error_count, boot count, battery voltage,
    #CPU temperature, IMU temperature, gyro reading, mag reading,
    #radio signal strength (RSSI), radio frequency error (FEI).

    #This data is packed into a c struct using `struct.pack`.

    acc = IMU.accel if IMU else array([nan, nan, nan])
    gyro = IMU.gyro if IMU else array([nan, nan, nan])
    mag = IMU.mag if IMU else array([nan, nan, nan])
    imu_temp = IMU.temperature if IMU else nan

    return struct.pack(payload_format,
                       acc[0], acc[1], acc[2],
                       gyro[0], gyro[1], gyro[2],
                       mag[0], mag[1], mag[2],
                       imu_temp)

def tinygs_packet():
    return bytearray(payload_packet())


# LoRa Range Test code


# print formatters
bold = '\033[1m'
normal = '\033[0m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'

# test messages
msg_1 = f"{bold}{yellow}111:{normal} A satellite or artificial satellite is an object intentionally placed into orbit in outer space."
msg_2 = f"{bold}{blue}222:{normal} Except for passive satellites, most satellites have an electricity generation system for equipment on board, such as solar panels or radioisotope thermoelectric generators (RTGs)."
msg_3 = f"{bold}{yellow}333:{normal} Most satellites also have a method of communication to ground stations, called transponders."
msg_4 = f"{bold}{blue}444:{normal} Many satellites use a standardized bus to save cost and work, the most popular of which is small CubeSats."
msg_5 = f"{bold}{yellow}555:{normal} Similar satellites can work together as a group, forming constellations."
msg_6 = f"{bold}{blue}666:{normal} Because of the high launch cost to space, satellites are designed to be as lightweight and robust as possible."
msg_7 = f"{bold}{yellow}777:{normal} Most communication satellites are radio relay stations in orbit and carry dozens of transponders, each with a bandwidth of tens of megahertz."

messages = [msg_1, msg_2, msg_3, msg_4, msg_5, msg_6, msg_7]


def get_input_discrete(prompt_str, choice_values):
    print(prompt_str)
    choice = None

    choice_values_str = "("
    for i, _ in enumerate(choice_values):
        choice_values_str += f"{choice_values[i]}"
        if i < len(choice_values) - 1:
            choice_values_str += ", "
    choice_values_str += ")"

    while choice not in choice_values:
        choice = input(f"{choice_values_str} ~> ").lower()
    return choice


def set_param_from_input_discrete(param, prompt_str, choice_values, allow_default=False):

    # add "enter" as a choice
    choice_values = [""] + choice_values if allow_default else choice_values
    prompt_str = prompt_str + \
        " (enter to skip):" if allow_default else prompt_str

    choice = get_input_discrete(prompt_str, choice_values)

    if choice == "":
        return param
    else:
        return int(choice)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_input_range(prompt_str, choice_range):
    print(prompt_str)
    choice = None

    choice_range_str = f"({choice_range[0]} - {choice_range[1]})"

    while True:
        choice = input(f"{choice_range_str} ~> ").lower()
        if choice == "":
            break

        if not is_number(choice):
            continue

        if float(choice) > choice_range[0] and float(choice) < choice_range[1]:
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


print(f"\n{bold}{yellow}Radio Range Test{normal}(with TinyGS example packet)\n")

# pocketqube
CS = digitalio.DigitalInOut(board.RF_CS)
RESET = digitalio.DigitalInOut(board.RF_RST)
CS.switch_to_output(value=True)
RESET.switch_to_output(value=True)

radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
radio_DIO0.switch_to_input()
radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
radio_DIO1.switch_to_input()

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)


# Initialze RFM radio
RADIO_FREQ_MHZ = 433.0
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, crc=False)
rfm9x.dio0 = radio_DIO0

# RFM radio configuration

# power - default is 13 dB, can go up to 23
param_str = get_input_discrete(
    f"Change radio parameters? {bold}(y/n){normal}", ["y", "n"])

# start by setting the defaults
rfm9x.frequency_mhz = 433.0
rfm9x.tx_power = 23
rfm9x.signal_bandwidth = rfm9x.bw_bins[7]
rfm9x.spreading_factor = 7
rfm9x.coding_rate = 5
timeout = rfm9x.receive_timeout
rfm9x.preamble_length = 16

if param_str == "y":
    rfm9x.frequency_mhz = set_param_from_input_range(rfm9x.frequency_mhz, f"Frequency (currently {rfm9x.frequency_mhz} MHz)",
                                                     [240.0, 960.0], allow_default=True)
    rfm9x.tx_power = set_param_from_input_discrete(rfm9x.tx_power, f"Power (currently {rfm9x.tx_power} dB)",
                                                   [f"{i}" for i in range(5, 24)], allow_default=True)
    rfm9x.signal_bandwidth = set_param_from_input_discrete(rfm9x.signal_bandwidth, f"Bandwidth (currently {rfm9x.signal_bandwidth} Hz)",
                                                           [f"{rfm9x.bw_bins[i]}" for i in range(len(rfm9x.bw_bins))], allow_default=True)
    rfm9x.spreading_factor = set_param_from_input_discrete(rfm9x.spreading_factor, f"Spreading Factor (currently {rfm9x.spreading_factor})",
                                                           [f"{i}" for i in range(7, 13)], allow_default=True)
    rfm9x.coding_rate = set_param_from_input_discrete(rfm9x.coding_rate, f"Coding Rate (currently {rfm9x.coding_rate})",
                                                      [f"{i}" for i in range(5, 9)], allow_default=True)
    rfm9x.low_datarate_optimize = set_param_from_input_discrete(rfm9x.low_datarate_optimize, f"Low Datarate Optimization (currently {rfm9x.low_datarate_optimize})",
                                                                ["0", "1"], allow_default=True)
    rfm9x.lna_gain = set_param_from_input_discrete(rfm9x.lna_gain, f"LNA Gain - [max = 1, min = 6] (currently {rfm9x.lna_gain})",
                                                   [f"{i}" for i in range(1, 7)], allow_default=True)
    timeout = set_param_from_input_range(timeout, f"Timeout (currently {timeout} s)",
                                         [0.0, 1000.0], allow_default=True)
    rfm9x.preamble_length = set_param_from_input_range(rfm9x.preamble_length, f"Preamble length (currently {rfm9x.preamble_length})",
                                                       [6, 65535], allow_default=True)

print(f"{yellow}{bold}Radio Parameters:{normal}")
print(f"\tFrequency = {rfm9x.frequency_mhz} MHz")
print(f"\tPower = {rfm9x.tx_power} dBm")
print(f"\tBandwidth = {rfm9x.signal_bandwidth} Hz")
print(f"\tSpreading Factor = {rfm9x.spreading_factor}")
print(f"\tCoding Rate = {rfm9x.coding_rate}")
print(f"\tLow Datarate Optimization = {rfm9x.low_datarate_optimize}")
# print(f"\tLNA Gain [max = 1, min = 6] = {rfm9x.lna_gain}")
print(f"\tTimeout = {timeout} s")
print(f"\tPreamble Length = {rfm9x.preamble_length} s")

mode_str = get_input_discrete(
    f"Operate in {bold}(r){normal}ecieve or {bold}(t){normal}ransmit mode?",
    ["r", "t"])

ack_str = get_input_discrete(
    f"Acknowledge? {bold}(y/n){normal}", ["y", "n"])

ack = (ack_str == "y")

if mode_str == "r":
    print(f"{bold}Receive{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")
    rfm9x.node = 0xAB  # our ID
    rfm9x.destination = 0xBA  # target's ID

    print(f"\n{yellow}Receiving...{normal}")
    while True:
        msg = rfm9x.receive(with_ack=ack, debug=True, timeout=timeout)
        if msg is not None:
            print(f"(RSSI: {rfm9x.last_rssi} | SNR: {rfm9x.last_snr} | FEI: {rfm9x.frequency_error})\t" +
                  msg.decode("utf-8", errors="backslashreplace"))

else:
    print(f"{bold}Transmit{normal} mode selected, {'with acknowledge' if ack else 'no acknowledge'}")
    rfm9x.node = 0xBA  # our ID
    rfm9x.destination = 0xAB  # target's ID

    pck_str = get_input_discrete(
        f"TinyGS or text packet? {bold}(tgs/txt){normal}", ["tgs", "txt"])

    i = 1

    if ack_str == "y":
        while True:
            if pck_str == "tgs":
                packet = tinygs_packet()
            else:
                packet = bytes(messages[0], "utf-8")
    
            print(packet)
            print(struct.unpack(payload_format, packet))

            if rfm9x.send_with_ack(packet):
                print(
                    f"Message {bold}{i}{normal}: {green}Acknowledged{normal}")
            else:
                print(
                    f"Message {bold}{i}{normal}: {red}No acknowledge{normal}")
            i += 1
            time.sleep(5)
    else:
        while True:
            if pck_str == "tgs":
                packet = tinygs_packet()
            else:
                packet = bytes(messages[0], "utf-8")

            print(packet)
            print(struct.unpack(payload_format, packet))

            rfm9x.send(packet)
            
            print(f"Message {bold}{i}{normal}: Sent")
            i += 1
            time.sleep(5)