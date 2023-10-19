import unittest
import sys
from testutils import assert_vector_similar, timestamp

sys.path.insert(0, './state_machine/applications/flight')

from lib.sun_position import approx_sun_position_ECI

class TestSunPosition(unittest.TestCase):

    def test_similar_to_SD(self):
        """Makes sure that the approx sun position vector is similar to the one from SatelliteDynamics.jl"""
        def similar(a, b):
            return assert_vector_similar(a, b, self.assertLessEqual, a_tolerance=1e7, angle_tolerance=2.0, units="km")
        tests = [
            {
                "time": timestamp(2019, 1, 1),
                "ref": [2.6679700934589096e7,
                        -1.3272442953501581e8,
                        -5.754308262033136e7]
            },
            {
                "time": timestamp(2019, 2, 13),
                "ref": [1.197370522199926e8,
                        -7.934173862461329e7,
                        -3.439885360149433e7]
            },
            {
                "time": timestamp(2020, 6, 15),
                "ref": [1.960107513186583e7,
                        1.3823368342943707e8,
                        5.993163650700999e7]
            },
            {
                "time": timestamp(2020, 4, 24),
                "ref": [1.2412537238980664e8,
                        7.804714079734519e7,
                        3.3837576751440614e7]
            },
            {
                "time": timestamp(2021, 3, 24),
                "ref": [1.4884395998626718e8,
                        8.856822633267123e6,
                        3.8399025584453815e6],
            },
            {
                "time": timestamp(2021, 5, 3),
                "ref": [1.1044761854947732e8,
                        9.422268016972692e7,
                        4.08505313506376e7]
            },
            {
                "time": timestamp(2022, 9, 15),
                "ref": [-1.4907043129178947e8,
                        1.861415189527427e7,
                        8.070222521729351e6]
            },
            {
                "time": timestamp(2022, 10, 7),
                "ref": [-1.4519107854048443e8,
                        -3.27636752741187e7,
                        -1.4204791686423695e7]
            },
            {
                "time": timestamp(2023, 2, 28),
                "ref": [1.385616842261845e8,
                        -4.8189529591819145e7,
                        -2.0892718035795942e7]
            },
            {
                "time": timestamp(2023, 11, 27),
                "ref": [-6.3401990461179e7,
                        -1.2231337391533968e8,
                        -5.302933759398837e7]
            },
        ]
        sum_angle = 0.0
        sum_dif = 0.0
        for test in tests:
            angle, dif = similar(approx_sun_position_ECI(test["time"]), test["ref"])
            sum_angle += angle
            sum_dif += dif
        print("Average angle error:", sum_angle / len(tests))
        print(f"Average absolute error {sum_dif / len(tests)/1e6} million km")
