from .message import Message
from . import headers
from . import PACKET_DATA_LEN

class MemoryBufferedMessage(Message):
    """Transmits the message PACKET_DATA_LEN bytes at a time.
    Sets special headers for the first packet, middle packets, and last packet.

    :param str: The message to send
    :type str: str | bytes | bytearray
    """

    packet_len = PACKET_DATA_LEN

    def __init__(self, str):
        priority = 2  # fixed so MemoryBufferedMessage packets don't interleave
        super().__init__(priority, str)
        self.cursor = 0

    def packet(self):
        payload = self.str[self.cursor:self.cursor + self.packet_len]
        pkt = bytearray(len(payload) + 1)
        if len(self.str) <= self.cursor + self.packet_len:  # last packet
            pkt[0] = headers.MEMORY_BUFFERED_END
        elif self.cursor == 0:
            pkt[0] = headers.MEMORY_BUFFERED_START
        else:
            pkt[0] = headers.MEMORY_BUFFERED_MID

        pkt[1:] = payload
        return pkt, True

    def done(self):
        return len(self.str) <= self.cursor

    def ack(self):
        self.cursor += self.packet_len
