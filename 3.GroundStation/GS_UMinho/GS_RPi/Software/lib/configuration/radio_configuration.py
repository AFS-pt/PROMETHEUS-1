"""
Defines the default settings used to configure the RFM9x satellite
"""

CHECKSUM = True
TX_POWER = 23  # dB
BITRATE = 1200  # bits per second
FREQUENCY = 433.0  # MHz
FREQUENCY_DEVIATION = 10000  # Hz
RX_BANDWIDTH = 25.0  # KHz
PREAMBLE_LENGTH = 16  # bytes
ACK_DELAY = 0.1  # seconds
ACK_WAIT = 1  # seconds
RECEIVE_TIMEOUT = 0.5  # seconds

SATELLITE_ID = 0xAB
GROUNDSTATION_ID = 0xBA
