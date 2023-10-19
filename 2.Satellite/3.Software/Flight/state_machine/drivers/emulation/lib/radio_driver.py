import asyncio
import queue
import random

class _Packet:
    """A packet with a bytearray ofdata and probability of sucessful reception"""

    def __init__(self, data, probability=1.0):
        self.data = data
        self.probability = probability

    def observe(self):
        """If the packet is sucessfully received, return the data, otherwise return None"""
        if random.random() < self.probability:
            return self.data
        else:
            return None

class Radio:
    def __init__(self):
        self.node = 0
        self.listening = False

        self._rx_queue = queue.LifoQueue()
        self._rx_time_bias = 0.5
        self._rx_time_dev = 0.3
        self._last_rssi = -147.0
        self._frequency_error = 123.45

    def listen(self):
        self.listening = True

    async def receive(self, *, keep_listening=True, with_header=False, with_ack=False, timeout=None, debug=False):
        rx_time = self._rx_time_bias + (random.random() - 0.5) * self._rx_time_dev
        await asyncio.sleep(rx_time)
        if self._rx_queue.empty():
            return None
        return self._rx_queue.get().observe()

    @property
    def last_rssi(self):
        return self._last_rssi

    @property
    def frequency_error(self):
        return self._frequency_error

    def sleep(self):
        self.listening = False

    async def send(self, packet, destination=0x00, keep_listening=True):
        return None

    async def send_with_ack(self, packet, keep_listening=True):
        return True

    def fifo_empty(self):
        return True

    def _push_rx_queue(self, packet):
        """Debug function to push a packet into the rx queue (lifo)"""
        self._rx_queue.put(packet)
