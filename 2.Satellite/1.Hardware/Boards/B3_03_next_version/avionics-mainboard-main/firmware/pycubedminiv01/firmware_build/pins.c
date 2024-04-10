#include "shared-bindings/board/__init__.h"
#include "boards/board.h"

STATIC const mp_rom_map_elem_t board_global_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_SCK),     MP_ROM_PTR(&pin_PA09)  },
    { MP_ROM_QSTR(MP_QSTR_MOSI),    MP_ROM_PTR(&pin_PA08)  },
    { MP_ROM_QSTR(MP_QSTR_MISO),    MP_ROM_PTR(&pin_PA10)  },

    { MP_ROM_QSTR(MP_QSTR_DAC0),   	MP_ROM_PTR(&pin_PA02)  },
   
    { MP_ROM_QSTR(MP_QSTR_SDA1),     MP_ROM_PTR(&pin_PA00)  },
    { MP_ROM_QSTR(MP_QSTR_SCL1),     MP_ROM_PTR(&pin_PA01)  },
    { MP_ROM_QSTR(MP_QSTR_SDA2),     MP_ROM_PTR(&pin_PA17)  },
    { MP_ROM_QSTR(MP_QSTR_SCL2),     MP_ROM_PTR(&pin_PA16)  },

    { MP_ROM_QSTR(MP_QSTR_RF2_IO1),     MP_ROM_PTR(&pin_PA02)  },
    { MP_ROM_QSTR(MP_QSTR_RF1_CS),     MP_ROM_PTR(&pin_PA04)  },
    { MP_ROM_QSTR(MP_QSTR_RF1_BUSY),     MP_ROM_PTR(&pin_PA06)  },
    { MP_ROM_QSTR(MP_QSTR_RF1_IO1),     MP_ROM_PTR(&pin_PA07)  },
    { MP_ROM_QSTR(MP_QSTR_EN_CAM),     MP_ROM_PTR(&pin_PA11)  },
    { MP_ROM_QSTR(MP_QSTR_MINZ_2),     MP_ROM_PTR(&pin_PA12)  },
    { MP_ROM_QSTR(MP_QSTR_MINX_2),     MP_ROM_PTR(&pin_PA13)  },
    { MP_ROM_QSTR(MP_QSTR_MINX_1),     MP_ROM_PTR(&pin_PA14)  },
    { MP_ROM_QSTR(MP_QSTR_MINY_1),     MP_ROM_PTR(&pin_PA15)  },
    { MP_ROM_QSTR(MP_QSTR_M_EN),     MP_ROM_PTR(&pin_PA19)  },
    { MP_ROM_QSTR(MP_QSTR_BURN1),     MP_ROM_PTR(&pin_PA22)  },
    { MP_ROM_QSTR(MP_QSTR_BURN2),     MP_ROM_PTR(&pin_PA20)  },
    { MP_ROM_QSTR(MP_QSTR_M_FAULT),     MP_ROM_PTR(&pin_PA21)  },
    { MP_ROM_QSTR(MP_QSTR_MINY_2),     MP_ROM_PTR(&pin_PA23)  },
    { MP_ROM_QSTR(MP_QSTR_RF2_BUSY),     MP_ROM_PTR(&pin_PA27)  },
    { MP_ROM_QSTR(MP_QSTR_CS_SD),     MP_ROM_PTR(&pin_PB02)  },
    { MP_ROM_QSTR(MP_QSTR_RF2_CS),     MP_ROM_PTR(&pin_PB03)  },
    { MP_ROM_QSTR(MP_QSTR_RF2_RST),     MP_ROM_PTR(&pin_PB08)  },
    { MP_ROM_QSTR(MP_QSTR_RF1_RST),     MP_ROM_PTR(&pin_PB09)  },
    { MP_ROM_QSTR(MP_QSTR_CS_CAM),     MP_ROM_PTR(&pin_PB10)  },
    { MP_ROM_QSTR(MP_QSTR_MINZ_1),     MP_ROM_PTR(&pin_PB11)  },
    { MP_ROM_QSTR(MP_QSTR_WDT_WDI),     MP_ROM_PTR(&pin_PB23)  },
    { MP_ROM_QSTR(MP_QSTR_ADC_CS),     MP_ROM_PTR(&pin_PA18)  },

    { MP_ROM_QSTR(MP_QSTR_NEOPIXEL),MP_ROM_PTR(&pin_PB22)  },
    { MP_ROM_QSTR(MP_QSTR_BATTERY), MP_ROM_PTR(&pin_PA05) },
    { MP_ROM_QSTR(MP_QSTR_UART),    MP_ROM_PTR(&board_uart_obj) },
    { MP_ROM_QSTR(MP_QSTR_I2C),     MP_ROM_PTR(&board_i2c_obj)  },
    { MP_ROM_QSTR(MP_QSTR_SPI),     MP_ROM_PTR(&board_spi_obj)  },
};
MP_DEFINE_CONST_DICT(board_module_globals, board_global_dict_table);