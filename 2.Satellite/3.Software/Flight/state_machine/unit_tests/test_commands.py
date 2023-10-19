import sys
from unittest import IsolatedAsyncioTestCase

sys.path.insert(0, './state_machine/drivers/emulation/lib')
sys.path.insert(0, './state_machine/drivers/emulation/')
sys.path.insert(0, './state_machine/applications/flight')
sys.path.insert(0, './state_machine/applications/flight/lib')
sys.path.insert(0, './state_machine/frame/')

import Tasks.radio as radio
import radio_utils.commands as cdh
from state_machine import state_machine
from testutils import send_cmd, CaptureDownlinks
from radio_utils import transmission_queue as tq
from radio_utils import message
from pycubed import cubesat
Message = message.Message

radio.ANTENNA_ATTACHED = True
state_machine.state = 'Debug'

cubesat.radio._rx_time_bias = 0.0
cubesat.radio._rx_time_dev = 0.0

class CommandTests(IsolatedAsyncioTestCase):

    async def test_query(self):
        await self.cmd_test(cdh.QUERY, b'5+5', '10')
        await self.cmd_test(cdh.QUERY, b'12*12', '144')

    async def test_tq_len(self):
        await self.cmd_test(cdh.TQ_SIZE, b'', '0')

    async def test_tq_clear(self):
        # clog tx queue
        await send_cmd(cdh.EXEC_PY, b"for _ in range(10):\n\ttq.push(Message(5, b'hello'))")

        # clear the tx queue
        for _ in range(radio.TX_SKIP):
            await send_cmd(cdh.CLEAR_TX_QUEUE, b'')

        await self.cmd_test(cdh.TQ_SIZE, b'', '0', tq_clear=False)

    async def cmd_test(self, cmd, args, expected, tq_clear=True):
        """Test that RX of a command with and without args works"""
        if tq_clear:
            tq.clear()
        old_downlink = cdh._downlink
        downlink = CaptureDownlinks(cdh._downlink)
        cdh._downlink = downlink.command

        await send_cmd(cmd, args)
        cdh._downlink = old_downlink
        self.assertEqual(downlink.result, expected)
        if tq_clear:
            tq.clear()
