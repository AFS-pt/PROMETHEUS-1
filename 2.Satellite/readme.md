[//]: # (# Introduction)
[//]: # (## What is a PocketQube/PyCubed-Mini and its context)
[//]: # (Get some info from paper introduction)

# Guide description

During two weeks on June 2023, a couple of stacks were successfully build at University of Minho, in which this guide is based. It provides a detailed step-by-step guide to correctly assemble and system check a PyCubed-Mini framework satellite of a PocketQube size. We also give some tips and useful notes for the process, learnt from this and previous builds at Carnergie Mellon University, where it was originally created and developed through multiple revisions.

During the development of a space mission, there are usually two separate units to build: an Engineering Unit and a Flight Unit. As the names sound, one is meant to validade all the hardware, firmware and software needed, while the other replicates it for a launch, ensuring extra safe and clean procedures, as required by launch companies.

This guide will be initially divided by each unit type, then mentioning the required parts to assemble each stack, describing the purpose and available options for fullfilling each one of the elements required. After, there will be some single testing of that parts, followed by the final assembly steps, for completing the stack, and final checking procedures.

This guide follows a sort of chronological order to facilitate its following, yet advised to fully read it first to avoid mistakes during the procedure.

![Satellite](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i01.satellite.JPG?raw=true)

<br /> 

# Engineering Unit

<br /> 

## Hardware

<br /> 

### Printed Circuit Boards (PCBs)

The PCBs are the fundamental hardware of the PyCubed-Mini, as they are precisely designed to hold its required components, as well as their connections, being that external, with USB-C connectors to easily interface with a computer or internal ones: between components in the same board, through the middle of it; or between board with stack connectors, with data and power lines.

The satellite is composed of eleven PCBs in total: five horizontally stacked inside, one on top of the other; and six covering each outside face of the cube. The KiCad schematics and board designs, as well as the gerber files for each are released in [Boards](/2.Satellite/Hardware/Boards). The recommended manufacturing option is to print the boards and solder the components at specialized companies, since there are multiple components in each board, some of them with different maximum temperature, in very reduced size or in need of a reflow oven.

This section will only mention the primary components and their references, discarding stack connectors and power regulation (present in all), reset and boot switches and status LEDs (present in some).

<br /> 

#### Inside boards

The first group is divided in main board, camera board and battery boards.

<br /> 

##### Main board

The main board contains the ATSAMD51J19A main microcontroller and MAX706 external watchdog timer, BNO085 IMU sensor and magnetorquer drivers, PCF8523 Real Time Clock, RFM98 radio module for 433 MHz LoRa communication, a USB-C connector for side power, flashing and communicating and SD Card connector for data logging.

![Main board](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i02.mainboard.png?raw=true)

<br /> 

##### Camera board

The camera board, as the name tells, holds the OV5640 camera, the STM32H743VI camera microcontroller, an SD Card connector for image savings, and a USB-C connector, for the same reasons as the main board. The camera ribbon cable is placed on the desired connector and should be fixed in the center square with tiny quantities of epoxy.

![Camera board](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i03.cameraboard.png?raw=true)

<br /> 

##### Battery boards

Two LP603443 batteries present in the satellite are placed between the three battery boards, wired in parallel for improved capacity, each with 3.7 V and 3.15 Wh. The circuitry is capable of sensing the current drawn and measuring its voltage.

![Battery boards](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i04.batteryboards.png?raw=true)

<br /> 

#### Outside boards

In all six solar boards (Figure 7), there are 14-turn coils serving as magnetorquers, 42 solar cells (KXOB25-05X3F) spread by the available space, energy harvesting systems, as well as OPT3001 sunlight sensors. There is also the antenna and burn wires, for its deployment, in one of the faces. Also, at the bottom one, there are two position switches that cut the battery power when pressed, preventing power draining during testing and storing. It has also a hole in the center, enabling the camera to take visible pictures.

![Solar boards](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i05.solarboards.png?raw=true)

In all solar boards, there is a 0 Ω resistor that is responsible for defining the correct I2C bus assignment. For negative axis boards, this SMD type wire pulls the I2C line to ground, while in positive boards, it should pull to power. 

![I2C](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i06.i2c.png?raw=true)

You can also check some important voltage potential values, such as (B)attery, (G)roud, (S)olar panels and (3).3 V, in the holes near the board edges.

<br /> 

##### +X, -X, +Y boards

These boards are equal, composed of eight solar cells each. 

##### -Y board

This board, besides the eight solar cells, holds two position switches that cut the battery power when pressed, preventing power draining during testing and storing. It has also a hole in the center, enabling the camera to take pictures.

##### +Z board

This board holds the two holes needed for the USB-C connectors in main and camera boards, besides the six solar cells.

##### -Z board

This board, besides the four solar cells, holds the antenna, which is holded in place with fishing line tied to each burn wire.

### Antenna

[//]: # (## Explain how and why is it possible to make an antenna with tape measure)

<br />

#### Antenna strips

As mentioned before, the satellite antenna, composed of two tape measure strips, is soldered to the defined Z- board pads. The metallic tape measure required for the process must be of approximately 1 cm in width, be almost planar and if possible, made of a easy-soldable material. The tape reference used for the assembly was DEXTER 8MM.

<br />

#### Fishing line

The fishing line used for passing through the tape measure strip hole and the burn wire must be multithreaded, as each thread is smaller, they are melted easier when current passes through the burn wire. The line reference used for the assembly was CAPERLAM 4X 0.16 mm.

<br />

#### Burn wire

The burn wire is made of nickel and chrome alloy of size AWG30.

[//]: # (The burn wire reference is?)

<br />

### Rails

Rails are the structural supports of the stack. There are two pieces in each stack, on the top and on the bottom, in which they hold inserts, sorted by the 3 axis. They provide the screwthreads needed for securing each external panels, as well as the upper and lower internal ones.

They are usually build from 3D-printed polylactic acid (PLA), since it is a cheap, simple and effective solution for granting the required rigidity for a testing unit.

Also made from PLA, two small brackets are needed for adjusting the antenna strips angle, holded in place with two M2 screws and nuts of nylon.

The 3D models of each rail and brackets are released in [Mechanical Structure](/2.Satellite/Hardware/Mechanical_Structure).

<br /> 

### Standoffs, heat inserts and screws

There are three major types of mechanical parts required for the satellite, mentioned in the subtitle. They are recommended to be made of brass, since it has low density, or alluminum alternatively for the same reason.

<br /> 

#### Standoffs

First, the standoffs separate each inside board with the adequate space between them. There were two sizes used: 6 mm and 4 mm in length, with eight M3 units needed for each size.

<br /> 

#### Heat inserts

Then, the heat inserts, as referred before, provide the screwthreads needed for securing the external boards to the internal stack. There are needed 24 units in total: 4 units of M3, for attaching the -Y board to the stack; and 20 units of M2, for attaching X, +Y and Z boards.

<br /> 

#### Screws

Finally, the screws fix the boards mentioned above, therefore, it is needed: 4 units of M3 (4 mm) for screwing -Y board to the -Y rail; 4 units of M3 (6 mm) screws for +Y rail to the stack; and 20 units of M2 (5 mm) screws for X, +Y and Z boards.

<br /> 

### Mounting base

The mounting base is 3D-printed from PLA to provide a stable and safe piece to the satellite be placed on. Also it helps to place it on a flat surface and to hold it without pressing any components. The sliding required to insert the satellite facilitates the trigger of the switch mechanism stated previously.

The 3D model is released in [Fixtures](/2.Satellite/Hardware/Fixtures).

![Mounted satellite](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i07.mounted.png?raw=true)

<br /> 

## Firmware

[//]: # (Explain UF2 bootloader and CircuitPython context)

Preferably, you should skip building both the SAMD UF2 bootloader and CircuitPython files, as they are already released on [Firmware](/2.Satellite/Firmware), and skip to [Flashing SAMD UF2 bootloader](#flashing-samd-uf2-bootloader). However, some important references are given if you want to learn the required steps to build the [SAMD UF2 bootloader](https://github.com/PyCubed-Mini/uf2-samdx1) or [CircuitPython](https://github.com/PyCubed-Mini/circuitpython) yourself.

<br />

### Flashing SAMD UF2 bootloader on mainboard

Based on [RExLab tutorial](https://github.com/PyCubed-Mini/avionics-mainboard/wiki/Flashing-UF2-Bootloader-on-the-ATSAMD51):

> The following procedure needs to be performed only once (barring any bricking / updating the bootloader) on a newly assembled mainboard with an unprogrammed MCU - in our case, the ATSAMD51J19A.
>
> <br /> 
>
> #### What you need
>
> - ATSAMD51 board (such as the PyCubed-Mini mainboard);
> 
> - Windows PC with atleast 2 free USB ports;
> 
> - SEGGER J-Link (we use the EDU Mini model);
> 
> - 2x5 pin 1.27mm pitch ribbon cable;
> 
> - USB-C and micro-USB cables, both with power and data lines;
>
> - SAMD bootloader binary file.
>
> <br /> 
>
> #### Step 1: Set up your PC
> 
> - Visit [Microchip Studio download page](https://www.microchip.com/en-us/tools-resources/develop/microchip-studio#Downloads), scroll down, and download the Web installer version of Microchip Studio. (The offline installer should also work, however I have had issues with antivirus software blocking it);
> 
> - Accept the Terms and Conditions, and deselect the "Send anonymous data" box. On the next page, select the architectures you'd like to install - we will only be using SAM boards. Finally, deselect "Advanced Software Framework and Example Projects" as these are not necessary. The rest of the installation should be fairly straightforward;
>
> - If asked to install the XC8 compiler, simply hit "OK" without installing - it is not necessary for this guide;
>
> - Microchip Studio should now be set up and open;
>
> - Next, visit [SEGGER J-Link download page](https://www.segger.com/downloads/jlink/), and download the latest Windows version of the J-Link software. The install process for this is fairly straightforward. The default settings should work fine;
>
> - A new SEGGER J-Link DLL Updater window will open asking to update Atmel Studio to the latest SEGGER software version. Make sure the check mark is selected and click "OK";
> 
> - Your computer is now ready for flashing the bootloader.

<br /> 

#### Step 2: Flash the bootloader

- Plug one end of the ribbon cable on 2x5 connector of the main board. Make sure pin 1 of the ribbon cable (red wire) is matching pin 1 of the board connector (longer silkscreen mark); 
  
- Plug the other end on the J-Link. Make sure pin 1 of the ribbon cable is matching pin 1 of the connector (white dot);

- Plug the J-Link on your PC with the micro-USB cable;

- Plug the the main board on your PC with the USB-C cable;

![Pin 1](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i08.pin1.png?raw=true)

Based on [AdaFruit tutorial](https://learn.adafruit.com/how-to-program-samd-bootloaders/programming-the-bootloader-with-atmel-studio#verify-connection-in-atmel-studio-3016767):

> - Next, open Atmel Studio. From the toolbar, select "Tools" -> "Device Programming";
> 
> - The device programming window will open. Then, select "Tool" -> "J-Link";
>
> - If you're using a J-Link EDU, accept the terms of use that will pop up after selecting the J-Link interface;
>
> - After that, select the Device (the type of chip you're programming): ATSAMD51J19A and click "Read" in the top navigation bar. The empty fields for Device Signature and Target Voltage should populate;
> 
> *NOTE: Make sure these values appear before proceeding! If the board or your wiring is not detected, Atmel Studio will throw an error that it could not connect to the board. Check your wiring and try to connect again.*
>
> - On the sidebar, click Memories. On Flash, select the bootloader binary file that you either built or downloaded, and mark "Erase Flash before programming";
>
> - Click "Program", then "Verify";
>
> *NOTE: After clicking, the serial should output "OK" for each action, and there should be a new USB volume mounted on your machine.*

<br /> 

### Flashing CircuitPython on mainboard

#### What you need

- PyCubed-Mini mainboard;

- PC with 1 free USB port;

- USB-C cable with power and data lines;

- CircuitPython UF2 file.

<br /> 

#### Step 1: Connect the board

- If you installed the bootloader right before, nothing should be made in this step;
  
- Otherwise, you should plug the board with the USB-C cable and the device should appear on your machine.

<br /> 

#### Step 2: Flash CircuitPython

Based on [AdaFruit tutorial](https://learn.adafruit.com/how-to-program-samd-bootloaders/installing-circuitpython):

> - Drag and drop the CircuitPython UF2 file that you either built or downloaded to the `pycubedminiBOOT` volume;
>
> - The volume should briefly disappear, and reappear as CIRCUITPY;
>
> - Your board is now running CircuitPython!

<br /> 

### "Camera board firmware"

[//]: # (some issues with the cameraboard)

<br /> 

## Software

After installing the firmware on the main and camera boards, some [Unitary testing](#unitary-testing) could be made to validate if everything is working as supposed, in an initial stage, or upload the code to run during launch and flight. To do so, some software applications must be built, in order to run files in our board(s). 

There are some already built and useful unitary testing scripts released in [Tests](/2.Satellite/Software/Tests), which will be mentioned in the next chapter. However, the Python software files for flight and system check are released in [Flight](/2.Satellite/Software/Flight), which require a build first, detailed right below. 

Based on [RExLab tutorial](https://pocketqube.readthedocs.io/en/latest/building.html):

> The frame folder contains the main.py (entry point for our software) and a custom state machine implementation.
>
> The drivers folder contains libaries allowing one to interface with the target hardware. We currently have the example emulator, pycubedmini driver and pycubedmini emulation.
>
> The applications folder contains the programs that utilize the drivers to achieve the specific mission objective. It contains the state machine configuration and tasks such as detumbling, beacon transmisions, logging and power management.

<br /> 

### Build an application

#### What you need

- Bash console;
  
- Flight software;  
  
> - python3
>
> - numpy
> 
> - ImageMagick
> 
> - graphviz
>
> *NOTE: Numpy is used for running the emulated sattelite and is therefore not required for building. ImageMagick and graphviz are used to create a state machine diagram along with your built files.*


<br /> 

#### Step 1: Run the script

> To build the flight software you run:
> 
> ```bash
> $ sh build.sh {driver} {application}
> ```
>
> The {driver} is the part of the software that interfaces with the hardware (or emulates it).
> 
> The {application} is what the software attempts to achieve the mission objective (by utilizing the driver to communicate with the hardware).
> 
> This allows us to easily test and develop flight software localy by emulating the hardware.

For example, for building system-check app, you should run:
```bash
user@machine ~/Software/Flight/state_machine
$ sh build.sh drivers/pycubedmini/ applications/system-check/
```

The build should appear at `~/Software/Flight/state_machine/build/` directory.

<br /> 

### Flash an application

This step is simple, as it only requires to drag the files and folders generated at the build directory and drop them inside satellite USB mounted volume.

<br /> 

## Unitary testing

By unitary testing, we refer to simple tests that can and should be made before assembling an entire unit. These can detect some errors or damages when testing individuals systems, for example, on communication or board detections. In this chapter, there are some detailed steps and expected results to be achieved during this type of testing.

<br /> 

### Mainboard payload

Based on system check app, which allows to test almost all systems, the same app can be used to validate some of the mainboard components and its connections, such as IMU readings or SD card detection.

<br /> 

#### What you need

- Mu Editor

- Flight software;

- Mainboard;

- USB-C cable, with power and data lines;

<br /> 

#### Step 1: Install Mu Editor

Based on [AdaFruit tutorial](https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor):

> Mu is a simple code editor that works with the Adafruit CircuitPython boards. It's written in Python and works on Windows, MacOS, Linux and Raspberry Pi. The serial console is built right in so you get immediate feedback from your board's serial output!
>
> - Download Mu from its [official website](https://codewith.mu);
>
> - Click the Download link for downloads and installation instructions;
>
> *NOTE: Click 'Start Here' to find other useful information, including extensive tutorials and how-to's.*
>
> - The first time you start Mu, you will be prompted to select your 'mode' - in our case, CircuitPython;
>
> *NOTE: Mu attempts to auto-detect your board on startup, so if you do not have a CircuitPython board plugged in with a CIRCUITPY drive available, Mu will inform you where it will store any code you save until you plug in a board.*
>
> - You can now explore Mu: you can use the text editor to edit the files (or use one at your preference) and interface with the main board with the serial console.

*TIP: in serial console, while the mainboard is plugged to your machine, use CTRL+C to stop the current program running on the board and CTRL+D to start the one on the volume. If the 'resource is busy' alert pops up, reconnect the board.*

<br /> 

#### Step 2: Test the mainboard

- Build (following the [steps](#build-an-application) above) and copy the system check files to the CIRCUITPY board;

- Open Mu Editor serial console and start running the program (CTRL+D);

- Follow the serial prompt, typing the code word for each specific test to be run.

You have 8 tests in total available in this application, however only 3 can help you to validade in this phase (IMU, NVM, SD).

Later in the guide, in [System check](#system-check) chapter, there is a detailed overview of this application, with the description of each test and expected result.

<br /> 

### LoRa communication

Another test that can be performed is the correct sending or receiving of LoRa packets. This can only be achieved while main board and antenna (-Z) board are connected, which is extremely important, since the absence of an antenna (load) may damage the trasmitter due to wave (power) reflection implying voltage and current overloads [[1]](https://electronics.stackexchange.com/questions/335912/can-i-break-a-radio-tranceiving-device-by-operating-it-with-no-antenna-connected).

The test software is released in [Tests](/2.Satellite/Software/Tests/), and is already built. To fully test, a second device is needed to check if the satellite is either able to successfully send of receive the packets. It can be another satellite (with both using the same test files) or a groundstation, composed of a ESP-32 or Raspberry Pi microcontroller with a compatible LoRa chip.

During testing phase, we had all the options stated: [LILYGO® TTGO T-Beam v1.1](https://meshtastic.org/docs/hardware/devices/tbeam/), a ESP-32 based groundstation; and RExLab custom groundstation, RPi based; and another twin satellite. We will cover the first case since it can be more easily replicated, either with a similar designed board or just with a simple ESP-32/Arduino connected to a LoRa IC.

[//]: # (Explicar parâmetros LoRa? bandwitdth, gain, ...)

<br />  

#### What you need

- Mu Editor and Arduino IDE;

- Lora Radio Range Test files;

- Main and -Z board;

- u.FL male to u.FL male cable;

- USB-C cable, with power and data lines;

- Another LoRa device for validation;

<br /> 

#### Step 1: Configure the groundstation for sending

- After installing Arduino IDE, install the ESP32 board drivers (follow this [tutorial](https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/)). In our case, the board reference changes to 'TTGO LoRa32-OLED' and the COM port may be defined to another instance;

- Install the libraries needed for peripherals, such as the OLED and LoRa chip (follow this [tutorial](https://randomnerdtutorials.com/ttgo-lora32-sx1276-arduino-ide/));

- Create a project with the sender sketch from the last tutorial, compile, run and open Serial Viewer, configured with the correct parameters. Again, in our case, change the board pins (MISO, SDA, ...) to the correct board [pinout](https://meshtastic.org/assets/images/t-beam_v1.1_pinmap-7c3402af077cdf2a5f90645561e049dc.webp) and frequency (433 MHz);

- The OLED should display the init prompt and the board starting to send packets.

<br /> 

#### Step 2: Set the satellite for receiving

- Connect the main and -Z boards with the u.FL cable;

- Like the previous unitary test, copy the files to the mainboard, open Mu Editor serial console and start running the program (CTRL+D);

- Follow the serial prompt, selecting the satellite option, followed by the radio parameters change (the default options should be fine);

- Finally, you should set the receiving mode with acknowledge;

- In a few seconds, it should print the received LoRa packet info, such as the RSSI and the message;

<p align="middle">
  <img src="https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i09.testsetup.jpg" width="500" />
  <img src="https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i10.serialviewer.png" width="500" />
</p>

<br /> 

#### Step 3: Invert the communication direction

To make the groundstation for Rx mode, you can simply use the receiver sketch instead of the sender one, also released in the previous [tutorial website](https://randomnerdtutorials.com/ttgo-lora32-sx1276-arduino-ide/) and switch the satellite to Tx mode on prompt.

<br /> 

### Camera detection

After the camera installation on the board, it is possible to transmit live video to a computer through USB, checking the correct functioning of the components and the firmware.

<br /> 

#### What you need

- OpenMV IDE;

- Camera board;

- USB-C cable, with power and data lines;

<br /> 

#### Step 1: Test the camera

- After installing OpenMV IDE, connect the camera board with the USB-C cable to your computer and open the IDE;

- On the top navigation bar, click in "File", "Examples", "HelloWorld" and "helloworld.py";

- If the board was detected, on the bottom left corner, click in the image buttons "Connect" and then "Start". If not, a brief troubleshooting should appear to unbrick your board;

- After this, you should get live feed from your camera at the top right corner;

![Open MV](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i11.openmv.png?raw=true)

<br /> 

## Assembly

This chapter states the final assembly of the unit once all the parts required and detailed above are gathered. In order to provide help for those who skipped to this chapter, or just to take extra precaution before this steps, the components and tools needed specifically for each subchapter are detailed at the start of each one. Nevertheless, a prior reading should prepare you for a better and continuous assembly process.

There are also some guidance videos that can help to visualize most of the steps taken, as well as some useful explanations given during the procedures. They are complementary, as all information is available in text.

<br /> 

### Creating an antenna

This chapter will describe how to create an antenna, detailing the tape strips, burnwire and brackets placement, along with the antenna tuning.

<br /> 

#### What you need

- [Tape measure and burn wire](#antenna);

- [Brackets, nylon screws and nuts](#rails);

- 3M DP2216 epoxy or similar, with apply gun;

- Cardboard/PVC tube, with around 1 meter;

- Velcro tape with adhesive;

- u.FL male cable;

- Dremel tool;

- Soldering iron and solder;

- Cutting and drilling pliers;

- Sandpaper;


<br /> 

#### Step 1: Prepare and place the tape

- Grab the referenced tape measure, get it out of the rolling box and cut at least two strips of around 20 cm each, making sure they are the same size;

- With a Dremel tool, remove around 3 cm from one of the sides of each strip to create an electrically conductive and solderable region;

*TIP: be extremely precise in removing all the paint around the edge to improve solderability.*

- At the recently scraped region, from about 1 cm of the tip, bend the strip 90 degrees to form a crease;

- Solder the creased tips of two strips to the antenna pads on the -Z board.

*NOTE: the soldering step must happen right after the scraping and bending due to oxidation issues on the strip.*

<br /> 

#### Step 2: Prepare and place the burn wire

- Cut at least two burn wire pieces of aroung 3 cm each;

- Pass them through the specified holes, keeping the center of the wire, and the majority of its length, on the same side of the antenna strips;

- On the other side, bent the necessary to keep it in place, solder both contact points and cut the excedent wire.

<br /> 

#### Step 3: Attach the antenna brackets

- After printing the brackets, place each between the antenna and the board, with the inclination touching the strip and its openings matching the board holes;

- Place a M2 nylon screw from the top through the bracket opening and the board hole, securing it with a corresponding nylon nut on the bottom side;

<br /> 

#### Step 4: Tune the antenna

- Grab a 1 m cardboard/PVC tube and place the antenna board on one end and the VNA on the other, with velcro tape with adhesive, and connect the two (an adapter from u.FL to SMA connectors may be needed);

*NOTE: the tube creates a safe distance between the parts, in terms of eletromagnetic interference*

- With the VNA, measure the initial frequency, resistance and reactance of the antenna. The desired values are around 433 MHz, 50 Ω and 0 Ω, respectively.

- Disconnect the antenna from the VNA;

- For tuning the frequency, since it has an initial value below the desired, cut around 5 mm in each strip;

- Connect the antenna again and check the frequency;

*TIP: each 5 mm cut should decrease in aroung 10 MHz, however it is still recommended to cut that size at a time and remeasure*

- Repeat the last three points until the value is close to the desired, then reducing the cutting size to only 1 mm (or less);

- For tuning the reactance, adjust the position of the brackets by sliding them. Overall, widing the antenna will increase its reactance, narrowing will decrease it;

<br /> 

#### Step 5: Final procedures

- Make sure you achieved the desired antenna parameters before proceeding;

- Make a 1 mm in diameter hole on the center of the outter edge (about 3 mm from the tip) of the antenna strips with a hole punch pliers, and sand it;

- Apply a good amount of epoxy on the sides of the brackets to fix it in position. Make sure the epoxy does not escape the board surface, neither touches the antenna strip or the nylon screw;

- Leave the board in a safe place to dry for about a day, and later remove the nylon pieces.

<br /> 

#### Video guide

Press on the image to be redirected to view the video guide on YouTube.

[![Creating an antenna](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/v01.antenna.jpg?raw=true)](https://youtu.be/2rDQudzhBSQ)

<br /> 

### Placing inserts on rails

This chapter will describe how to correctly place the heat inserts into the rails.

<br /> 

#### What you need

- [Inserts](#heat-inserts);

- [Rails](#rails);

- M2 and M3 drilling machine;

- Soldering iron;

- Sandpaper:

<br />

#### Step 1: Place the inserts

- Mount and tightly secure the M3 drill;

- Grab the printed rails and fix them on a vise;

- Drill the four M3 holes on the corners of the -Y board to remove imperfections;

*TIP: with the drill not rotating, align it with hole and then run it.*

![Insert holes](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i12.insertholes.png?raw=true)

- Repeat the above with a M2 drill in the remaining holes of both boards;

- Turn on the soldering iron at 275 ºC (slighty above the polymer melting point) and let it heat;

- Select the right insert for each hole and figure out its orientation;

*TIP: check the figure to find out the correct orientation.*

![Insert orientation](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i13.insertorientation.png?raw=true)

- From the outside perspective of the satellite, place each insert on top of the hole and push it down the rail with the iron, until the insert is totally inside;

*TIP: make sure it goes down slowly and straight as the plastic melts.*

<br /> 

#### Step 2: Final procedures

- Sand the remaining material off the hole margins and interiors;

- Check if the standoffs and screw can be easily fixed;

- Check if the camera board can be placed on -Y rail and, if needed, sand the side wall to allow it;

<br />

#### Video guide

Press on the image to be redirected to view the video guide on YouTube.

[![Placing inserts on rails](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/v02.inserts.jpg?raw=true)](https://youtu.be/tuawUfmNegQ)

<br />

### Assemblying the satellite

This chapter will describe the steps required to place the rails, inside and outside boards on the correct order and position on order to assemble the PocketQube. It is recommended to open the CAD assembly file, released in [Mechanical Structure](/2.Satellite/Hardware/Mechanical_Structure), to help visualize it.

<br />

#### What you need

[//]: # (explain cam placement on board)

- [PCBs](#printed-circuit-boards-pcbs), with the [antenna](#creating-an-antenna) and the camera on place;

- [Rails](#rails) with the [inserts](#placing-inserts-on-rails) on place;

- [Standoffs and screws](#standoffs-heat-inserts-and-screws);

- [Fishing line](#fishing-line);

- 2x LP603443 batteries;


- u.FL male to u.FL male cable;

- Kapton adhesive tape;

- Precision toolkit;

<br />

#### Step 1: Place the inside boards and rails

- Start by putting the camera board inside the -Y rail, with the camera pointing towards the inside of the rail;

- Place four M3 (8 mm) standoffs in each corner and screw them;

*TIP: making a cross pattern, screw the standoffs only a couple of times each until they give a lot of resistance*

- Plug the main board onto the camera board by its vertical connectors and make sure it aligns in the corners;

- Again, place four M3 (8 mm) standoffs in each corner and screw them;

- Plug the bottom battery board onto the stack, add four M3 (6 mm) standoffs in each corner and screw them;

- Solder both batteries to the corresponding polarity pads in each face of the middle battery board;

- Fix the batteries and its wires to the board with Kapton adhesive tape;

- Plug the finished middle battery board on top of the current satellite stack;

- Place four M3 (6 mm) standoffs in each corner and screw them;

- Plug the top battery board onto the middle one;

- Place the +Y rail on top of the stack and make sure its inserts match the silk note circles positions in the battery board;

- Screw the rail and board in place with 4 units of M3 (6 mm) screws;

<br />

#### Step 2: Add the outside boards

- Carefully connect the u.FL to u.FL antenna cable to the main board connector and leave the other end outside the stack;

- Place -X solar board in its designed face, with solar cells outwards and making sure the placement of the side connector between the board and the stack is correct;

- Screw the board in place with 4x M2 (5 mm) screws, following the same screwing technique as before;

- Repeat the previous points with the +Y and +Z boards;

- Place and screw the -Y board to the -Y rail with 4x M3 (4 mm) screws;

- After that, connect the remaining end of the u.FL cable to the -Z board connector and place the board. Managing the cable through the +X side, certify that it passes through the inside board's hollow space present in the -Z side;

[//]: # (add hole image?)

- When completed, screw the board with 4x M2 (5 mm) units;

- Finally, close the satellite with the +X board and screw it with 4x M2 (5 mm) screws;

<br /> 

#### Step 3: Tie the antenna

- Tightly wrap the antenna strips around the satellite and temporarily fix them with adhesive tape;

- Cut two pieces of fishing line with around 20 cm long;

*TIP: this length is more than enough but it makes the tying easier.*

- Pass the line through the first antenna tip hole and the first burn wire, tie it with a square knot and cut the surplus;

- Repeat the previous point on the other antenna strip;

<br />

#### Video guide

Press on the image to be redirected to view the video guide on YouTube.

[![Assemblying the satellite](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/v03.assembly.jpg?raw=true)](https://youtu.be/qyBwiglurZg)

<br /> 

### Charging the batteries

[//]: # (cable reference)

After finishing the assembly, you can charge the satellite via the connector on the back side of the -Y board. For that, plug a <reference> cable and provide around 3.7 V, with a maximum current of 850 mAh until the current drops to the recommended cut-off value.

*NOTE: These voltage and current values were retrieved from the batteries' datasheet. Always check it to make sure you execute the standard charging procedure correctly!*

<br /> 

## System check

This chapter describes the software application used for testing and validating the satellite's payload and core functioning. As it was expressed previously in chapter [Unitary testing: Mainboard payload](#mainboard-payload), the same code is used to now verify all eight tasks available. Also, if the unitary testing was performed, a detailed console log with its performance was noticeable, where some success criteria needed to be achieved in each trial to pass.

- SD card test: It displays if the SD card is detected or not;

- IMU test: Detects if IMU is functional and retrieve some accelerometer, gyroscope and magnetometer readings;

- Sun sensor test: Shows if all six sun sensors are functional and display some light intensity measurements;

- Coil driver test: Runs the drivers with three different voltage inputs, generating proportional magnetic fields with the driving current;

- Burn wire test: Applies a PWM signal (default duty-cycle is 0.3% for 3 secs) to the burn wire to validate the deploy mechanism;

- I2C test: Scans all integrated circuits and solar boards connected to the multiple I2C buses;

- NVM reset and test: Defaults the NVM counter and checks if its operation is right (requires the SD card);

- Current sensor test: Measures the current over a short period of time and looks for spikes or other anomalies that can translate in bad power supply;

<br /> 

# Flight Unit

This chapter explains only the different steps and precautions required during the flight unit manufacture, assembly and testing.

<br /> 

## Vibration testing and bake-out process

After the assembly, the satellite hardware must pass through vibration testing to certify that it can handle the launch. The vibration profile to test for is usually given by the launcher company and is specific for form factors or weight and the type of vibration. While all the tests are required for certification, usually the most important vibration test is the sinusoidal with frequencies up to 100 Hz, due to the predominance on launch. Consulting SpaceX Rideshare Payload User's Guide, the structure should handle at least 1.5 g. 

A vibe fixture was developed to couple the satellite with the vibration table, released on [Fixtures](/2.Satellite/Hardware/Fixtures). It is not recommended to use 3D-printed PLA as tends to damp higher frequencies and instead, consider alluminum for the case.

At last, the satellite goes through a bake-out process to accelerate outgassing, thus preventing contamination of the launcher pod and payload.

<br /> 

## Day in the life testing

Another important test is made to evaluate long-period satellite functioning. The test is performed by leaving the satellite running outdoors for an entire day, if possible being hit by the sun, to charge with the solar cells, and protected by the rain, to prevent damage. By the end of the test, the satellite should be running as it was left, and the batteries voltage be higher than previously.

<br /> 

## Assembly precautions

Before the procedure, drop and scrub the boards and its components with isopropyl alcohol (IPA). In this assembly procedure, more than required in engineering satellite units, the use of nitrile gloves and anti-static mat and wrist strap is very important. Although it is not mandatory, the assembly should be made in an ISO cleanliness certified room, if possible. Also, satellite transportation should be made inside an EMF protection bag, in a Nanuk case.

<br /> 

## Loctite usage

On flight unit, Loctite 222 is used in all screw surfaces. Just a few drops are enough to provide additional strength and prevent unscrewing.

[//]: # (vid dropping loctite?)

<br /> 

## Windform rails

Instead of PLA rails, a carbon-fiber-reinforced polyamide material called [Windform XT 2.0](https://www.windform.com/sls-materials/windform-xt-2-0/) was used for the rails. It provides improved specific strength and NASA outgassing certification.

![Rails](https://github.com/AFS-pt/PROMETHEUS-1_dev/blob/main/2.Satellite/images/i14.rails.png?raw=true)

<br /> 

[//]: # (# Conclusion)

# Credits

[//]: # (Créditos a laboratórios Colab, GEPE, oficinas DEI e DEM, RExLab e GitHub Pycubed-Mini)