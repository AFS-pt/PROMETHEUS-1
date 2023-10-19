import unittest
import sys

sys.path.insert(0, 'state_machine/applications/flight/lib')

from radio_utils import transmission_queue as tq  # noqa: E402

class Test(unittest.TestCase):

    def test(self):
        for i in range(tq.limit):
            tq.push(i)
        self.assertRaises(Exception, tq.push, 101)
        self.assertEqual(tq.limit - 1, tq.pop())
        self.assertEqual(99, len(tq.queue))
        tq.clear()
