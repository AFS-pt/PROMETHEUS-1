from radio_utils import PACKET_DATA_LEN

class Message:
    """The most basic message type.
    Other message types should inherit from this class.
    Truncates the message to fit within the payload limit.

    :param priority: The priority of the message (higher is better)
    :type priority: int
    :param str: The message to send
    :type str: str | bytes | bytearray
    """

    def __init__(self, priority, str, with_ack=False, header=0x00):
        self.priority = priority
        self.header = header
        self.with_ack = with_ack
        if isinstance(str, bytes) or isinstance(str, bytearray):
            self.str = str
        else:
            self.str = bytes(str, 'ascii')

    def packet(self):
        """Returns the byte representation of the message, and if it should be sent with or without ack."""
        str = self.str[:PACKET_DATA_LEN]
        pkt = bytearray(len(str) + 1)
        pkt[0] = self.header
        pkt[1:] = str
        return pkt, self.with_ack

    def done(self):
        """Returns true if the message is done sending."""
        return True

    def ack(self):
        """Called when the message is acknowledged."""
        pass

    def no_ack(self):
        """Called when the message fails to be acknowledged."""
        pass

    def __lt__(self, other):
        return self.priority < other.priority

    def __le__(self, other):
        return self.priority <= other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __ge__(self, other):
        return self.priority >= other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __repr__(self) -> str:
        return str(self.str[:20] + b"..." if len(self.str) > 23 else self.str)
