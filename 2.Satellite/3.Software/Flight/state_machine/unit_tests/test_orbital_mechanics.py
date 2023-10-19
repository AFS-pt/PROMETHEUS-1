import unittest
import sys
import math
from numpy import array, testing
from numpy.linalg import norm

sys.path.insert(0, './state_machine/applications/flight')

from lib.orbital_mechanics import rk4, propogate, d_state, MEAN_RADIUS

class TestRK4(unittest.TestCase):

    def test_basic_difeqs(self):
        self.assertAlmostEqual(rk4(0, 0.1, math.exp), 0.105360515657833149)
        self.assertAlmostEqual(rk4(1, 0.1, lambda x: 3 * x), 1.349859, places=4)

    def test_orbit_doesnt_crash(self):
        """Tests if this probably stable orbit doesn't crash into the earth"""
        x = array([0, 0, 10000.0, 5, -5, 0])
        for _ in range(20):
            x = propogate(x, 60 * 60 * 24, integration_step=60)
            self.assertGreaterEqual(norm(x[0:3]), MEAN_RADIUS)

class TestDState(unittest.TestCase):

    def test_no_changes(self):
        testing.assert_almost_equal(
            d_state(array([7e7, 8e7, -7e7, 3e3, 5e3, 1e3])),
            [3.00000000e+03, 5.00000000e+03, 1.00000000e+03, -1.35320407e-11, -1.54651893e-11, 1.35320407e-11]
        )
        testing.assert_almost_equal(
            d_state(array([-9e7, -7e7, 8e7, 4e3, 4e3, 2e3])),
            [4.00000000e+03, 4.00000000e+03, 2.00000000e+03, 1.32763193e-11, 1.03260262e-11, -1.18011728e-11]
        )


x = TestDState()
x.test_no_changes()
