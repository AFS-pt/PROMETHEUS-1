"""
Provides individual groundstation actions such as upload a file,
wait for packet, or send a command.
"""
import board
import busio
import digitalio
from lib import radiohead
from lib.configuration import radio_configuration as rf_config


def initialize_radio(tx_spi, tx_cs, tx_reset, rx_spi=None, rx_cs=None, rx_reset=None, rxtx_switch=None):
    rh = radiohead.Radiohead(rf_config.PROTOCOL,
                             tx_spi,
                             tx_cs,
                             tx_reset,
                             rx_spi,
                             rx_cs,
                             rx_reset,
                             rxtx_switch)

    rh.ack_delay = rf_config.ACK_DELAY
    rh.ack_wait = rf_config.ACK_WAIT
    rh.receive_timeout = rf_config.RECEIVE_TIMEOUT
    rh.node = rf_config.GROUNDSTATION_ID
    rh.destination = rf_config.SATELLITE_ID

    return rh

def satellite_spi_config():
    # pocketqube
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.RF_CS)
    reset = digitalio.DigitalInOut(board.RF_RST)
    cs.switch_to_output(value=True)
    reset.switch_to_output(value=True)

    radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
    radio_DIO0.switch_to_input()
    radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
    radio_DIO1.switch_to_input()

    return spi, cs, reset


def feather_spi_config():
    # feather
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.D5)
    reset = digitalio.DigitalInOut(board.D6)
    cs.switch_to_output(value=True)
    reset.switch_to_output(value=True)

    return spi, cs, reset


def pi_spi_config():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.ce1)
    reset = digitalio.DigitalInOut(board.d25)

    return spi, cs, reset


def rpigs_tx_spi_config():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.D7)
    reset = digitalio.DigitalInOut(board.D25)

    return spi, cs, reset


def rpigs_rx_spi_config():
    spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

    cs = digitalio.DigitalInOut(board.D16)
    reset = digitalio.DigitalInOut(board.D24)

    return spi, cs, reset


def rpigs_spi_config():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

    cs = digitalio.DigitalInOut(board.CE0)
    reset = digitalio.DigitalInOut(board.D12) #PWM0

    return spi, cs, reset
