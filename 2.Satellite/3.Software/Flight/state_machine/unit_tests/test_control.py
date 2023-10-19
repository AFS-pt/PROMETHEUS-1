import unittest
import sys
from numpy import testing

sys.path.insert(0, './state_machine/drivers/emulation')
sys.path.insert(0, './state_machine/applications/flight')
sys.path.insert(0, './state_machine/frame')

from lib.control import bcross


class BCrossTest(unittest.TestCase):

    def test(self):
        b = [0, 2, 3]
        ω = [0.5, 1, -2]
        print(bcross(b, ω))
        # calculated from julia simulator with k = 7e-4
        testing.assert_array_almost_equal(
            bcross([4, 5, -6], [1, 2, 3]),
            [-0.00024545454545454545,
             0.00016363636363636366,
             -2.7272727272727266e-5]
        )
        testing.assert_array_almost_equal(
            bcross([0.03, 1.3, -2.05], [0.3, -0.7, 0.5]),
            [9.323989547629548e-5,
             7.482947025486136e-5,
             4.881732107102861e-5]
        )
        testing.assert_array_almost_equal(
            bcross([0.98, 0.23, 0.73], [0.92, -0.124, 0.21]),
            [-6.284697969214849e-5,
             -0.0002108782822403312,
             0.00015081102056655027]
        )
        testing.assert_array_almost_equal(
            bcross([0, 0, 0], [0, 0, 0]),
            [0, 0, 0]
        )
        testing.assert_array_almost_equal(
            bcross([1, 2, 3], [1, 2, 3]),
            [0, 0, 0]
        )
