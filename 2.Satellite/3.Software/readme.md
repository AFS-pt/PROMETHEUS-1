# Software Testing

## Description

The mainboard (red) has all the main components present in the satellite, such as the microcontroller (ATSAMD51J19A), LoRa chip (RFM98), as well as some power and data management. The Z- Board (blue) is one of the edges of the PocketQube, designed to interface four solarpanels and the antenna.

RExLab Team shared some useful [documentation](https://pocketqube.readthedocs.io/en/latest/index.html) about the uC software implementation and a detailed CAD model of the satellite. Nevertheless, their Github repos contain most of the important info and code (https://github.com/PyCubed-Mini: /fight_software, /avionics-..., /Tests).

The uC is programmed in CircuitPython, which can be coded using Mu Editor. The code that arrived inside the board is inside "Software on board" folder.

<p align="middle">
  <img src="https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/Software/Figures/sat_boards_front.jpg" width="500" />
  <img src="https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/Software/Figures/sat_boards_back.jpg" width="500" />
</p>

<br>

## First steps

1. Install Mu Editor from [Adafruit website](https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor);

2. Connect an USB cable between your computer and the board;

3. Make sure that the switch below board USB-C port in turned on (right position);

4. Double-tap the button (there is only one);

5. If a USB unit isn't detected, there might be two issues:
    - Double-tap timing is wrong (keep trying);
	- USB-C connection (flip the USB-C cable at board connector);

6. Paste the code and libraries you want to run on the uC inside the USB unit;
    - See below the code used for testing LoRa packets transmission from satellite board to ground station [LILYGO® TTGO T-Beam v1.1](https://meshtastic.org/docs/hardware/devices/tbeam/);
    
7. In Mu Editor, open file from folder (main.py, for example) and open Serial Viewer;

8. Saving file edits should recompile the program, execute your code and show prints in serial data. If not, try Ctrl+D in Serial Viewer;

<br>

## Transmission from satellite board to ground station (LILYGO® TTGO T-Beam v1.1)

First, the steps needed for the ground station (receiver):

1. Install Arduino IDE;

2. Install the ESP32 board drivers (follow this [tutorial](https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/));
    - In our case, the board reference changes to 'TTGO LoRa32-OLED' and the COM port may be defined to another instance;

3. Install the libraries needed for peripherals, such as the OLED and LoRa chip (follow this [tutorial](https://randomnerdtutorials.com/ttgo-lora32-sx1276-arduino-ide/));

4. Create a project with the sender sketch from the last tutorial, compile, run and open Serial Viewer, configured with the correct parameters;
    - Again, in our case, change the board pins (MISO, SDA, ...) to the correct ones and frequency (433MHz);

5. The OLED should display the init prompt and starting to send packets;

Then, the steps needed for the mainboard (transmitter):

6. Download the Tests repo from PyCubed-Mini, more specifically the [LoRa Radio Range Test](https://github.com/PyCubed-Mini/Tests/tree/main/lora_radio_range_test) and do step 6 from last chapter;
    - This repo is really helpful since it has implemented easy and reliable testing routines to major components, such as the LoRa chip;
    - In our case, some modifications were necessary, such as the node address, receiving settings and string printing;

7. In the Seriel Viewer, it should prompt a interactive menu of the testing routine;

8. Select the satellite option, following the radio parameters change;
    - In our case, the default options were fine;

9. Finally, you should set the receiving mode with acknowledge;

10. In a few seconds, it should print the received LoRa packet info, such as the RSSI and the message;
    - As it is, the first four chars are not being printed as we hoped so;

<p align="middle">
  <img src="https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/Software/Figures/transmission_test_setup.jpg" width="500" />
  <img src="https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/Software/Figures/transmission_serial_viewer.png" width="500" />
</p>

<br>

## Transmission from ground station to satellite board

Not started but should be similar, since the satellite transmitting code could be functional in our case and the ground station receiving code could be like the one showed in the previous mentioned tutorial.

<br>

## Credits

We shared our files used, with our needed changes implemented, however we give all the credits to the rightful creators.
