# Usage

Most all tutorials and quick start materials from https://pycubed.org/resources pertain to PyCubed Mini as well. When in doubt, look there for questions first. 

## 📅 2022-02-16
Updating from older CircuitPython firmware to 7.2. Put into bootloader mode, copy CURRENT.UF2 from `PYCUBEDBOOT` drive to your computer as a backup. Then update the bootloader by copying [update_bootloader.uf2](https://github.com/spacecraft-design-lab-2019/avionics-motherboard/blob/zac-updates/firmware/pycubedminiv02/update_bootloader.uf2) to the `PYCUBEDBOOT` drive. Board will unmount. BE PATIENT. It will eventually remount to your computer in bootloader mode again. Then copy over [firmware.uf2](https://github.com/spacecraft-design-lab-2019/avionics-motherboard/blob/zac-updates/firmware/pycubedminiv02/firmware.uf2). Details instructions [here](https://pycubed.org/Updating-PyCubed-cbc8b47a677549ed98fc5b23b5a04fac), just note PyCubed Mini it's available from https://circuitpython.org/downloads?q=pycubed yet. 

Once updated, your pycubedmini.py library will not work.
- See [flight-software max-fsw branch](https://github.com/spacecraft-design-lab-2019/flight-software/tree/max-fsw/board-side) for updated syntax. Copy entire lib directory from that repo and replace the lib directory on your board.
