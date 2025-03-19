# Raspberry Pi Ground Station

A small modular radio to chat with satellites.


## Features

- LoRa UHF communication (TX and RX);
- Compatible with Raspberry Pi (40-pin header);
- Programmed with CircuitPython;
- Independent power supply to increase performance;
- Dedicated to PROMETHEUS-1 satellite.

For more details on the RFM98 radio module, check the [short](https://www.hoperf.com/uploads/RFM98PW_RFM95PWRFTransmitterandReceiverModuleDatasheetREV1.1_1695351516.pdf) and [detailed](https://cdn.sparkfun.com/assets/learn_tutorials/8/0/4/RFM95_96_97_98W.pdf) datasheets.


## Hardware

### Issues

A few issues from RPiGS v2 were discovered during testing, which could be fixed in a new iteration (v2.1). These issues are detailed below:

1. [RESET pin of RFM9x radio should not have a pull-up resistor](https://github.com/adafruit/Adafruit_CircuitPython_RFM9x/pull/47):
    - v2: Resistor is present on both, but do not phisically assemble it.
    - v2.1: Resistor should be removed;

2. [Raspberry Pi pins CE0 and CE1 should not be used for GPIO purposes](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/spi-sensors-devices):
    - v2: CS pin is connected to CE0, but this line can be rearranged to another pin (such as D6) via software.
    - v2.1: RESET and CS pins from radio should be rerouted to other free GPIO pins;

3. Hat board power supply cannot power Raspberry Pi startup due to high initial current:
    - v2: radio and Raspberry can be powered by either Raspberry power module or by external power source.
    - v2.1: Raspberry should be only powered by its own power module, radio could be powered by either Raspberry power module or by external power source (probably increase transmission power).


## Software

### Instructions

#### Dependencies

Before using the RPiGS, make sure you have all the requirements, such as SPI enabled and CircuitPython installed. 

Based on [Adafruit tutorial](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi):

> Run these commands to enable the various interfaces such as I2C and SPI:
> ```bash
> user@machine ~
> $ sudo raspi-config nonint do_i2c 0
> $ sudo raspi-config nonint do_spi 0
> $ sudo raspi-config nonint do_serial_hw 0
> $ sudo raspi-config nonint do_ssh 0
> $ sudo raspi-config nonint do_camera 0
> $ sudo raspi-config nonint disable_raspi_config_at_boot 0
> ```
> 
> Then, install Blinka package and its dependencies with:
> ```bash
> user@machine ~
> $ sudo apt-get install -y i2c-tools libgpiod-dev python3-libgpiod
> $ sudo pip3 install --upgrade adafruit-blinka
> ```

Note that `--break-system-dependencies` might be needed. If it is undesirable please visit the original tutorial and install the package with a virtual environment.

> In Raspberry Pi model 5, RPi.GPIO is installed which causes issues. Just remove it with the following command:
> ```bash
> user@machine ~
> $ sudo pip3 uninstall -y RPi.GPIO
> ```
> 
> This script will automatically enable I2C and SPI. You can run the following command to verify:
> ```bash
> user@machine ~
> $ ls /dev/i2c* /dev/spi*
> ```
> 
> You should see the response:
> ```bash
> /dev/i2c-1 /dev/spidev0.0 /dev/spidev0.1
> ```

The following commands should also be executed if the hardware version is v2, as described in the issue #2 above.

> CE0 and CE1 can be reassigned via software with the commands:
> ```bash
> user@machine ~
> $ cd ~
> $ sudo pip3 install --upgrade adafruit-python-shell click
> $ wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/raspi-spi-reassign.py
> $ sudo -E env PATH=$PATH python3 raspi-spi-reassign.py --ce0=5 --ce1=6
> ```
> 
> After this, the package should be properly installed. You can verify it with the following code:
> 
> ```python
> import board
> import digitalio
> import busio
> 
> print("Hello, blinka!")
> 
> # Try to create a Digital input
> pin = digitalio.DigitalInOut(board.D4)
> print("Digital IO ok!")
> 
> # Try to create an I2C device
> i2c = busio.I2C(board.SCL, board.SDA)
> print("I2C ok!")
> 
> # Try to create an SPI device
> spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
> print("SPI ok!")
> 
> print("done!")
> ```

#### Code

To run the ground station software, use the following command:
```bash
user@machine ~/PROMETHEUS-1/3.GroundStation/GS_UMinho/GS_RPi/Software/
$ python gs_shell.py
```

After this a prompt menu should appear, where you should select the option below to work with RPi_GS v2.
```bash
(o) RPiGS TX and RX (single radio)
```

Next, you can modify the radio parameters via prompt, but mind that these are the defined settings for PROMETHEUS-1. 

After this, you'll reach the ground station menu where you can request beacons, images, send commands, etc.

### References

Check the repositories from this was forked from:

- RPiGS single modem HW: https://github.com/cmu-spacecraft-design-build-fly-2023/Ops-Groundstation
- RPiGS dual modem HW: https://github.com/PyCubed-Mini/RPIGS/tree/main/rpi_dual_rfm98_hat
- RPiGS TX+RX LoRa/FSK SW: https://github.com/PyCubed-Mini/basic_groundstation/tree/image_radio_modes


