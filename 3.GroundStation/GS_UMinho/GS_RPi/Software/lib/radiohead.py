import random
import time
import tasko
from lib.pycubed_rfm9x_lora import (Constants as LoRa_Constants,
                                    RFM9x as LoRa_RFM9x)
from lib.pycubed_rfm9x_fsk import (Constants as FSK_Constants,
                                   RFM9x as FSK_RFM9x)
from lib.configuration import radio_configuration as rf_config

HAS_SUPERVISOR = False

try:
    import supervisor

    if hasattr(supervisor, "ticks_ms"):
        HAS_SUPERVISOR = True
except ImportError:
    pass

try:
    from typing import Optional
    from circuitpython_typing import ReadableBuffer

except ImportError:
    pass


class Radiohead:

    def __init__(self,
                 protocol,
                 tx_spi,
                 tx_cs,
                 tx_reset,
                 rx_spi=None,
                 rx_cs=None,
                 rx_reset=None,
                 rxtx_switch=None,
                 checksum=True
                 ):
        self.protocol = protocol

        self.tx_device = self.initialize_radio(tx_spi,
                                               tx_cs,
                                               tx_reset)

        if rx_spi and rx_cs and rx_reset:
            self.rx_device = self.initialize_radio(rx_spi,
                                                   rx_cs,
                                                   rx_reset)
            self.separate_rx = True
        else:
            self.rx_device = self.tx_device
            self.separate_rx = False

        self.choose_constants()

        self.rxtx_switch = rxtx_switch

        self.ack_wait = 0.5
        """The delay time before attempting a retry after not receiving an ACK"""

        self.receive_timeout = 0.5
        """The amount of time to poll for a received packet.
           If no packet is received, the returned packet will be None
        """

        self.xmit_timeout = 2.0
        """The amount of time to wait for the HW to transmit the packet.
           This is mainly used to prevent a hang due to a HW issue
        """

        self.ack_retries = 5
        """The number of ACK retries before reporting a failure."""

        self.ack_delay = None
        """The delay time before attemting to send an ACK.
           If ACKs are being missed try setting this to .1 or .2.
        """

        # initialize sequence number counter for reliabe datagram mode
        self.sequence_number = 0

        # create seen Ids list
        self.seen_ids = bytearray(256)

        # initialize packet header
        # node address - default is broadcast
        self.node = self.constants._RH_BROADCAST_ADDRESS
        """The default address of this Node. (0-255).
           If not 255 (0xff) then only packets address to this node will be accepted.
           First byte of the RadioHead header.
        """

        # destination address - default is broadcast
        self.destination = self.constants._RH_BROADCAST_ADDRESS
        """The default destination address for packet transmissions. (0-255).
           If 255 (0xff) then any receiving node should accept the packet.
           Second byte of the RadioHead header.
        """

        # ID - contains seq count for reliable datagram mode
        self.identifier = 0
        """Automatically set to the sequence number when send_with_ack() used.
           Third byte of the RadioHead header.
        """

        # flags - identifies ack/reetry packet for reliable datagram mode
        self.flags = 0
        """Upper 4 bits reserved for use by Reliable Datagram Mode.
           Lower 4 bits may be used to pass information.
           Fourth byte of the RadioHead header.
        """

        self.checksum = checksum
        self.checksum_error_count = 0

        self.last_rssi = 0.0
        """The RSSI of the last received packet. Stored when the packet was received.
           The instantaneous RSSI value may not be accurate once the
           operating mode has been changed.
        """

        self.last_snr = 0.0
        """The SNR of the last received packet. Stored when the packet was received.
           The instantaneous SNR value may not be accurate once the
           operating mode has been changed.
        """

    def ticks_diff(self, ticks1, ticks2):
        """Compute the signed difference between two ticks values
        assuming that they are within 2**28 ticks
        """
        diff = (ticks1 - ticks2) & self.constants._TICKS_MAX
        diff = ((diff + self.constants._TICKS_HALFPERIOD) & self.constants._TICKS_MAX) - self.constants._TICKS_HALFPERIOD
        return diff

    def choose_constants(self):
        if self.protocol == "fsk":
            self.constants = FSK_Constants
        elif self.protocol == "lora":
            self.constants = LoRa_Constants

    def initialize_radio(self, spi, cs, reset):
        if self.protocol == "fsk":
            rfm_device = FSK_RFM9x(spi, cs, reset, rf_config.FREQUENCY)
            rfm_device.bitrate = rf_config.BITRATE
            rfm_device.frequency_deviation = rf_config.FREQUENCY_DEVIATION
            rfm_device.rx_bandwidth = rf_config.RX_BANDWIDTH

        elif self.protocol == "lora":
            rfm_device = LoRa_RFM9x(spi, cs, reset, rf_config.FREQUENCY)
            rfm_device.spreading_factor = rf_config.SPREADING_FACTOR
            rfm_device.coding_rate = rf_config.CODING_RATE
            rfm_device.signal_bandwidth = rf_config.SIGNAL_BANDWIDTH

        else:
            raise RuntimeError(f"unrecognized radio protocol: {self.protocol}")

        rfm_device.tx_power = rf_config.TX_POWER
        rfm_device.preamble_length = rf_config.PREAMBLE_LENGTH

        return rfm_device

    def listen(self):
        if self.separate_rx:
            self.tx_device.idle()
        self.rx_device.listen()
        if self.rxtx_switch:
            self.rxtx_switch.receive()

    def idle(self):
        self.tx_device.idle()
        if self.separate_rx:
            self.rx_device.idle()
        if self.rxtx_switch:
            self.rxtx_switch.idle()

    def transmit(self):
        if self.separate_rx:
            self.rx_device.idle()
        self.tx_device.transmit()
        if self.rxtx_switch:
            self.rxtx_switch.transmit()

    """
    ===========================================================================
    Main Functions
    ===========================================================================
    """

    async def send(
        self,
        data: ReadableBuffer,
        *,
        keep_listening: bool = False,
        destination: Optional[int] = None,
        node: Optional[int] = None,
        identifier: Optional[int] = None,
        flags: Optional[int] = None,
        debug: bool = False
    ) -> bool:
        """Send a string of data using the transmitter.
        (limited by chip's FIFO size and appended headers).
        This prepends a 1 byte length to be compatible with the RFM9X fsk packet handler,
        and 4 byte header to be compatible with the RadioHead library.
        The header defaults to using the initialized attributes:
        (destination, node, identifier, flags)
        It may be temporarily overidden via the kwargs - destination, node, identifier, flags.
        Values passed via kwargs do not alter the attribute settings.
        The keep_listening argument should be set to True if you want to start listening
        automatically after the packet is sent. The default setting is False.

        Returns: True if success or False if the send timed out.
        """
        self.tx_device.check_data(data)

        self.idle()  # Stop receiving to clear FIFO and keep it clear.
        if self.protocol == "lora":
            # tells device that FIFO should start at 0.
            # register is used different in fsk
            self.tx_device.write_fifo_start()

        # Combine header and data to form payload
        payload = bytearray(5)
        payload[0] = len(payload) + len(data) - 1  # first byte is length to meet semtech FSK requirements (pg 74)
        if destination is None:  # use attribute
            payload[1] = self.destination
        else:  # use kwarg
            payload[1] = destination
        if node is None:  # use attribute
            payload[2] = self.node
        else:  # use kwarg
            payload[2] = node
        if identifier is None:  # use attribute
            payload[3] = self.identifier
        else:  # use kwarg
            payload[3] = identifier
        if flags is None:  # use attribute
            payload[4] = self.flags
        else:  # use kwarg
            payload[4] = flags

        payload = payload + data

        if self.checksum:
            payload[0] += 2
            checksum = bsd_checksum(payload)
            payload = payload + checksum

        if debug:
            print(f"RFM9X: Sending {str(payload)}")

        # Write payload.
        self.tx_device.write_payload(payload)

        # Turn on transmit mode to send out the packet.
        self.transmit()
        # Wait for tx done interrupt with explicit polling (not ideal but
        # best that can be done right now without interrupts).
        timed_out = False
        if HAS_SUPERVISOR:
            start = supervisor.ticks_ms()
            while not timed_out and not self.tx_device.tx_done():
                if self.ticks_diff(supervisor.ticks_ms(), start) >= self.xmit_timeout * 1000:
                    timed_out = True
                else:
                    await tasko.sleep(0)
        else:
            start = time.monotonic()
            while not timed_out and not self.tx_device.tx_done():
                if time.monotonic() - start >= self.xmit_timeout:
                    timed_out = True
                else:
                    await tasko.sleep(0)
        # Done transmitting - change modes (interrupt automatically cleared on mode change)
        if keep_listening:
            self.listen()
        else:
            # Enter idle mode to stop receiving other packets.
            self.idle()
        if self.protocol == "lora":
            self.tx_device.reset_irq_flags()
        return not timed_out

    async def send_with_ack(self, data, debug=False):
        """Reliable Datagram mode:
        Send a packet with data and wait for an ACK response.
        The packet header is automatically generated.
        If enabled, the packet transmission will be retried on failure
        """
        if self.ack_retries:
            retries_remaining = self.ack_retries
        else:
            retries_remaining = 1
        got_ack = False
        self.sequence_number = (self.sequence_number + 1) & 0xFF
        while not got_ack and retries_remaining:
            self.identifier = self.sequence_number
            await self.send(data, keep_listening=True, debug=debug)
            # Don't look for ACK from Broadcast message
            if self.destination == self.constants._RH_BROADCAST_ADDRESS:
                got_ack = True
            else:
                # wait for a packet from our destination
                ack_packet = await self.receive(
                    timeout=self.ack_wait, with_header=True, debug=debug)
                if ack_packet is not None:
                    if ack_packet[4] & self.constants._RH_FLAGS_ACK:
                        # check the ID
                        if ack_packet[3] == self.identifier:
                            got_ack = True
                            break
                    if debug:
                        print(f"Invalid ACK packet {str(ack_packet)}")
            # pause before next retry -- random delay
            if not got_ack:
                # delay by random amount before next try
                await tasko.sleep(self.ack_wait * random.random())
                if debug:
                    print(f"No ACK, retrying send - retries remaining: {retries_remaining}")
            retries_remaining = retries_remaining - 1
            # set retry flag in packet header
            self.flags |= self.constants._RH_FLAGS_RETRY
        self.flags = 0  # clear flags
        return got_ack

    async def receive(
        self,
        *,
        keep_listening: bool = True,
        with_header: bool = False,
        with_ack: bool = False,
        timeout: Optional[float] = None,
        debug: bool = False,
    ) -> Optional[bytearray]:
        """Wait to receive a packet from the receiver. If a packet is found the payload bytes
        are returned, otherwise None is returned(which indicates the timeout elapsed with no
        reception).
        If keep_listening is True (the default) the chip will immediately enter listening mode
        after reception of a packet, otherwise it will fall back to idle mode and ignore any
        future reception.
        All packets must have a 4-byte header for compatibilty with the
        RadioHead library.
        The header consists of 4 bytes(To, From, ID, Flags). The default setting will  strip
        the header before returning the packet to the caller.
        If with_header is True then the 4 byte header will be returned with the packet.
        The payload then begins at packet[4].
        If with_ack is True, send an ACK after receipt(Reliable Datagram mode)
        """

        if timeout is None:
            timeout = self.receive_timeout

        # get starting time
        if HAS_SUPERVISOR:
            start = supervisor.ticks_ms()
        else:
            start = time.monotonic()

        packet = None
        # Make sure we are listening for packets (and not transmitting).
        self.listen()

        while True:
            # check for valid packets
            if self.rx_device.rx_done():
                # save last RSSI reading
                self.last_rssi = self.rx_device.rssi

                if self.protocol == "lora":
                    self.last_snr = self.rx_device.snr

                # Enter idle mode to stop receiving other packets.
                self.idle()
                # read packet
                packet = await self.process_packet(with_header=with_header, with_ack=with_ack, debug=debug)
                if packet is not None:
                    break  # packet valid - return it
                # packet invalid - continue listening
                self.listen()

            # check if we have timed out
            if ((HAS_SUPERVISOR and (self.constants.ticks_diff(supervisor.ticks_ms(), start) >= timeout * 1000)) or
                    (not HAS_SUPERVISOR and (time.monotonic() - start >= timeout))):
                # timed out
                if debug:
                    print("RFM9X: RX timed out")
                break

            await tasko.sleep(0)

        # Exit
        if keep_listening:
            self.listen()
        else:
            self.idle()

        return packet

    async def process_packet(self, with_header=False, with_ack=False, debug=False):

        # Read the data from the radio FIFO
        packet = self.rx_device.get_packet()
        packet_length = len(packet)

        # Reject if the received packet is too small to include the 1 byte length, the
        # 4 byte RadioHead header and at least one byte of data
        if packet_length < 6:
            if debug:
                print(f"RFM9X: Incomplete message (packet_length = {packet_length} < 6, packet = {str(packet)})")
            return None

        # Reject if the length recorded in the packet doesn't match the amount of data we got
        internal_packet_length = packet[0]
        if internal_packet_length != packet_length - 1:
            if debug:
                print(
                    f"RFM9X: Received packet length ({packet_length}) " +
                    f"does not match transmitted packet length ({internal_packet_length}), " +
                    f"packet = {str(packet)}")
            return None

        # Reject if the packet does not pass the checksum
        if self.checksum:
            if not bsd_checksum(packet[:-2]) == packet[-2:]:
                if debug:
                    print(
                        f"RFM9X: Checksum failed, packet = {str(packet)}, bsd_checksum(packet[:-2])" +
                        f" = {bsd_checksum(packet[:-2])}, packet[-2:] = {packet[-2:]}")
                self.checksum_error_count += 1
                return None
            else:
                # passed the checksum - remove it before continuing
                packet = packet[:-2]

        # Reject if the packet wasn't sent to my address
        if (self.node != self.constants._RH_BROADCAST_ADDRESS and
                packet[1] != self.constants._RH_BROADCAST_ADDRESS and
                packet[1] != self.node):
            if debug:
                print(
                    "RFM9X: Incorrect Address " +
                    f"(packet address = {packet[1]} != my address = {self.node}), " +
                    f"packet = {str(packet)}")
            return None

        # send ACK unless this was an ACK or a broadcast
        if (with_ack and
                ((packet[4] & self.constants._RH_FLAGS_ACK) == 0) and
                (packet[1] != self.constants._RH_BROADCAST_ADDRESS)):
            # delay before sending Ack to give receiver a chance to get ready
            if self.ack_delay is not None:
                await tasko.sleep(self.ack_delay)
            # send ACK packet to sender (data is b'!')
            if debug:
                print("RFM9X: Sending ACK")
            await self.send(
                b"!",
                destination=packet[2],
                node=packet[1],
                identifier=packet[3],
                flags=(packet[4] | self.constants._RH_FLAGS_ACK),
            )
            # reject this packet if its identifier was the most recent one from its source
            # TODO: Make sure identifiers are being changed for each packet
            if (self.seen_ids[packet[2]] == packet[3]) and (
                    packet[4] & self.constants._RH_FLAGS_RETRY):
                if debug:
                    print(f"RFM9X: dropping retried packet, packet = {str(packet)}")
                return None
            else:  # save the packet identifier for this source
                self.seen_ids[packet[2]] = packet[3]

        if (not with_header):  # skip the header if not wanted
            packet = packet[5:]

        if debug:
            print(f"RFM9X: Received {str(packet)}")

        return packet


def bsd_checksum(bytedata):
    """Very simple, not secure, but fast 2 byte checksum"""
    checksum = 0

    for b in bytedata:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += b
        checksum &= 0xffff
    return bytes([checksum >> 8, checksum & 0xff])
