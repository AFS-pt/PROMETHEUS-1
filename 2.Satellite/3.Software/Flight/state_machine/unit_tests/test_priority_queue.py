import unittest
import sys

sys.path.insert(0, 'state_machine/applications/flight/lib/radio_utils')

import priority_queue as pq  # noqa: E402
from message import Message as msg  # noqa: E402

# https://www.geeksforgeeks.org/how-to-check-if-a-given-array-represents-a-binary-heap/
def _isHeap(arr, i, n):

    # If (2 * i) + 1 >= n, then leaf node, so return true
    if i >= int((n - 1) / 2):
        return True

    # If an internal node and is greater
    # than its children, and same is
    # recursively true for the children
    if (arr[i] >= arr[2 * i + 1] and
       arr[i] >= arr[2 * i + 2] and
       _isHeap(arr, 2 * i + 1, n) and
       _isHeap(arr, 2 * i + 2, n)):
        return True

    return False

def isHeap(arr):
    return _isHeap(arr, 0, len(arr))

class Tests(unittest.TestCase):

    def test_heapify(self):
        h1 = [3, 8, 17, 4]
        self.assertTrue(isHeap(pq.heapify(h1)))
        self.assertTrue(isHeap(h1))
        h2 = [3, 8, 17, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16]
        self.assertTrue(isHeap(pq.heapify(h2)))
        self.assertTrue(isHeap(h2))
        h3 = [4, 3, -3, 0, -1, -2, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16]
        self.assertTrue(isHeap(pq.heapify(h3)))
        self.assertTrue(isHeap(h3))
        h4 = []
        self.assertTrue(isHeap(pq.heapify(h4)))
        self.assertTrue(isHeap(h4))
        h5 = [1, 0, -5, 7, 12, 8, -12]
        self.assertTrue(isHeap(pq.heapify(h5)))
        self.assertTrue(isHeap(h5))
        a = msg(3, 'hello')
        b = msg(3, 'hello')
        c = msg(3, 'hello')
        d = msg(3, 'hello')
        h6 = [a, c, d]
        self.assertTrue(isHeap(pq.heapify(h6)))
        self.assertTrue(isHeap(h6))
        h7 = [a, b, c, d]
        self.assertTrue(isHeap(pq.heapify(h7)))
        self.assertTrue(isHeap(h7))
        h8 = [d, a, b]
        self.assertTrue(isHeap(pq.heapify(h8)))
        self.assertTrue(isHeap(h8))
        h9 = [d]
        self.assertTrue(isHeap(pq.heapify(h9)))
        self.assertTrue(isHeap(h9))

    def test_push_and_pop(self):
        h = []
        pq.push(h, 3)
        self.assertEqual(3, h[0])
        pq.push(h, 8)
        self.assertEqual(8, h[0])
        pq.push(h, 0)
        self.assertEqual(pq.pop(h), 8)
        self.assertEqual(3, h[0])
        pq.push(h, 5)
        self.assertEqual(5, h[0])
        pq.push(h, 4)
        self.assertEqual(5, h[0])
        self.assertEqual(5, pq.pop(h))
        self.assertEqual(4, pq.pop(h))
        self.assertEqual(3, pq.pop(h))
        self.assertEqual(0, pq.pop(h))
