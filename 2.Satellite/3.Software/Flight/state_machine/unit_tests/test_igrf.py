import unittest
import sys
import numpy as np
from testutils import timestamp, assert_vector_similar

sys.path.insert(0, './state_machine/applications/flight')

from lib.IGRF import igrf, igrf_eci

EARTH_RADIUS = 6.378136300e3  # km


class IGRF(unittest.TestCase):

    def test_matches_IGRF13(self):
        # test data generated from https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html
        # using pyIGRF.py
        # Note that we use geocentric coordinates
        # We are comparing the results with the IGRF13 results
        def similar(a, b):
            return assert_vector_similar(a, b, self.assertLessEqual, a_tolerance=3000, angle_tolerance=5.0, units="nT")
        t = timestamp(2020, 4, 19, 15)  # time is about 2020.3
        similar(
            igrf(t, 34.567, 45.678, 6697.043115),
            [24354.4, 1908.4, 32051.6]
        )

        t = timestamp(2023, 1, 1)
        similar(
            igrf(t, -12, 37, 6700),
            [20274.2, -1994.6, -18852.8]
        )

        t = timestamp(2022, 7, 2, 22)
        similar(
            igrf(t, 25, 35, EARTH_RADIUS + 400),  # about the ISS altitude
            [28295.864360612726, 1850.2071187341612, 21436.550334577572]
        )

        t = timestamp(2023, 1, 1)
        similar(
            igrf(t, -79, 48, EARTH_RADIUS + 700),
            [4650.9, -10831.9, -34896.3]
        )

    def test_no_changes(self):
        """Test that our changes to the IGRF model do not change the results."""
        equal = np.testing.assert_array_almost_equal

        t = timestamp(2020, 4, 19, 15)
        equal(
            igrf(t, 34.567, 45.678, 6697.043115),
            [24694.17511877, 2125.5475454, 32160.37154219],
            decimal=1
        )

        t = timestamp(2021, 7, 28, 2)
        equal(
            igrf(t, -12, 127, 6873),
            [28092.523258, 1432.59565072, -22804.66673182],
            decimal=1
        )

class IGRF_ECI(unittest.TestCase):

    def test_close_GN(self):
        """Test that our IGRF in ECI coordinates is close to the results from GravNav.
        Source: https://github.com/RoboticExplorationLab/GravNav/blob/main/simple_sim/mag_field.jl#L6"""
        def similar(a, b):
            return assert_vector_similar(a, b, self.assertLessEqual, a_tolerance=30, angle_tolerance=1.0, units="nT")
        t = timestamp(2020, 9, 15)
        similar(
            igrf_eci(t, [7000, 7500, 9300]),
            [-2958.36063183389, -3285.782343814322, -751.7865862535493]
        )

        t = timestamp(2021, 4, 1)
        similar(
            igrf_eci(t, [7654, -12345, 5678]),
            [-963.4031953585253, 1522.7638883411967, 1657.0123037449737]
        )

        t = timestamp(2020, 8, 13)
        similar(
            igrf_eci(t, [8763, -7421, -9213]),
            [1978.9330574152757, -2226.2182265227348, -306.67003898572216]
        )
