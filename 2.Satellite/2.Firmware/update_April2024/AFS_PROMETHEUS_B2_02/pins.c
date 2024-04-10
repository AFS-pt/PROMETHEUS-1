#include "shared-bindings/board/__init__.h"
#include "supervisor/board.h"

STATIC const mp_rom_map_elem_t board_global_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_SCK),     MP_ROM_PTR(&pin_PA13)  },
    { MP_ROM_QSTR(MP_QSTR_MOSI),    MP_ROM_PTR(&pin_PA12)  },
    { MP_ROM_QSTR(MP_QSTR_MISO),    MP_ROM_PTR(&pin_PA14)  },

    { MP_ROM_QSTR(MP_QSTR_SDA1),     MP_ROM_PTR(&pin_PB12)  },
    { MP_ROM_QSTR(MP_QSTR_SCL1),     MP_ROM_PTR(&pin_PB13)  },
    { MP_ROM_QSTR(MP_QSTR_SDA2),     MP_ROM_PTR(&pin_PA17)  },
    { MP_ROM_QSTR(MP_QSTR_SCL2),     MP_ROM_PTR(&pin_PA16)  },
    { MP_ROM_QSTR(MP_QSTR_SDA3),     MP_ROM_PTR(&pin_PB31)  },
    { MP_ROM_QSTR(MP_QSTR_SCL3),     MP_ROM_PTR(&pin_PB30)  },

    { MP_ROM_QSTR(MP_QSTR_RF_IO0),     MP_ROM_PTR(&pin_PA05)  },
    { MP_ROM_QSTR(MP_QSTR_RF_IO1),     MP_ROM_PTR(&pin_PA04)  },
    { MP_ROM_QSTR(MP_QSTR_RF_RST),     MP_ROM_PTR(&pin_PA20)  },
    { MP_ROM_QSTR(MP_QSTR_RF_CS),      MP_ROM_PTR(&pin_PA22)  },

    { MP_ROM_QSTR(MP_QSTR_SD_CS),       MP_ROM_PTR(&pin_PB15)  },
    { MP_ROM_QSTR(MP_QSTR_IMU_INT),     MP_ROM_PTR(&pin_PB16)  },
    { MP_ROM_QSTR(MP_QSTR_M_FAULT),     MP_ROM_PTR(&pin_PB14)  },
    { MP_ROM_QSTR(MP_QSTR_BURN1),       MP_ROM_PTR(&pin_PA19)  },
    { MP_ROM_QSTR(MP_QSTR_BURN2),       MP_ROM_PTR(&pin_PA18)  },
    { MP_ROM_QSTR(MP_QSTR_CAM_CS),       MP_ROM_PTR(&pin_PB08)  },
    { MP_ROM_QSTR(MP_QSTR_CAM_EN),       MP_ROM_PTR(&pin_PB09)  },

    { MP_ROM_QSTR(MP_QSTR_WDT_WDI),  MP_ROM_PTR(&pin_PA23)  },

    { MP_ROM_QSTR(MP_QSTR_NEOPIXEL), MP_ROM_PTR(&pin_PA21)  },
    { MP_ROM_QSTR(MP_QSTR_BATTERY),  MP_ROM_PTR(&pin_PA06) },
    { MP_ROM_QSTR(MP_QSTR_I2C),      MP_ROM_PTR(&board_i2c_obj)  },
    { MP_ROM_QSTR(MP_QSTR_SPI),      MP_ROM_PTR(&board_spi_obj)  },
};
MP_DEFINE_CONST_DICT(board_module_globals, board_global_dict_table);


//UPDATED FROM PREVIOUS VERSION:
//   { MP_ROM_QSTR(MP_QSTR_CS_CAM),   MP_ROM_PTR(&pin_PB15)  },
//   { MP_ROM_QSTR(MP_QSTR_EN_CAM),   MP_ROM_PTR(&pin_PB16)  },

//DO NOT EXIST (REMOVED)
//    { MP_ROM_QSTR(MP_QSTR_M_EN),        MP_ROM_PTR(&pin_PB00)  },
