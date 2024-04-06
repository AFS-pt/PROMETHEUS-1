# Raspberry Pi Ground Station

A small modular radio to chat with satellites.


## Features

- LoRa 433 MHz communication (TX and RX), with up to +30dBm output power;
- Compatible with Raspberry Pi (40-pin header);
- Programmed with CircuitPython.

For more details on the RFM98 radio module, check the [short](https://www.hoperf.com/uploads/RFM98PW_RFM95PWRFTransmitterandReceiverModuleDatasheetREV1.1_1695351516.pdf) and [detailed](https://cdn.sparkfun.com/assets/learn_tutorials/8/0/4/RFM95_96_97_98W.pdf) datasheets.


## Hardware

### Version comparison

A few issues from RPiGS v2 were discovered during testing, which led to a new, optimized v2.1. These issues are detailed below.

1. [RESET pin of RFM9x LoRa module should not have a pull-up resistor](https://github.com/adafruit/Adafruit_CircuitPython_RFM9x/pull/47):
    - v2.1: Resistor removed from schematic and PCB layout;
    - v2: Resistor is present on both, but do not phisically assemble it.

2. [Raspberry Pi pins CE0 and CE1 should not be used for GPIO purposes](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/spi-sensors-devices):
    - v2.1: RESET and CS pins rerouted;
    - v2: CS pin is connected to CE0, but this line can be rearranged to another pin (such as D6).

3. Hat board power supply cannot power Raspberry Pi startup:
    - v2.1: power supply and circuit removed to reduce space and costs, LoRa module powered by Raspberry;
    - v2: LoRa module can be powered by either Raspberry or by external power source.


## Software

### Instructions

Before using the RPiGS, make sure you have all the requirements, such as SPI enabled and CircuitPython installed. Please follow [this tutorial](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi) before running the software.

Also, check the repositories from this was forked from:

- RPiGS single modem HW: https://github.com/cmu-spacecraft-design-build-fly-2023/Ops-Groundstation
- RPiGS dual modem HW: https://github.com/PyCubed-Mini/RPIGS/tree/main/rpi_dual_rfm98_hat
- RPiGS TX+RX LoRa/FSK SW: https://github.com/PyCubed-Mini/basic_groundstation

