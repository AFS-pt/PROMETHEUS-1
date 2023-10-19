import unittest
import sys
from numpy import array, cos, sin, pi, testing
from numpy.linalg import norm
from datetime import datetime as dt, timezone

sys.path.insert(0, './state_machine/applications/flight')

import lib.frames as frames

EARTH_RADIUS = 6371  # Earth radius (km)
LEO = 2000  # Low Earth Orbit Altitude Limit (km)

def sphere(p):
    (r, theta, phi) = p
    return array([r * cos(phi) * sin(theta), r * sin(phi) * sin(theta), r * cos(theta)])

def assert_matrices_close(A, B, limit=40):
    """Assert that the matrices are close enough to be considered equal.
    This is quantified by ||Ax - Bx|| <= limit where limit=40km by default.
    With 20 randomly preselected x vectors.
    """
    random_r = [0.8024612835524245, 0.7799976069168522, 0.2755708484874475, 0.7330229027509386, 0.25907330462717226,
                0.5463115713496455, 0.44071908096464074, 0.6813197448495494, 0.6643272512636399, 0.17347325364175925,
                0.8755423550584049, 0.4144062746589813, 0.574574071973453, 0.5450505615416308, 0.898767242216612,
                0.8929993117314708, 0.13563822268349823, 0.30579939151778357, 0.22185382634541484, 0.7369055233784879]
    random_theta = [0.5101178853945276, 0.335573508966745, 0.7898993563976668, 0.4379619702634009, 0.3317991172264475,
                    0.05409153128430766, 0.2089447958278125, 0.16700392301892353, 0.4026595634137289, 0.804533000884362,
                    0.5775769675013817, 0.4915534196831799, 0.3488173952232939, 0.41138992770355287, 0.2074700298578479,
                    0.9443597528619022, 0.4369826508351583, 0.9187908118163634, 0.13584368379659217, 0.8920158527647813]
    random_phi = [0.9331083038111837, 0.171456982916933, 0.9973850770496011, 0.09646857671696607, 0.914755982365568,
                  0.989740039777413, 0.34836908993688587, 0.9804857522697122, 0.16912940409029054, 0.8737226962320032,
                  0.48253924423095496, 0.8906909282328218, 0.5755947594709588, 0.6020846507401795, 0.1756451335479995,
                  0.28715487506952453, 0.04206276596303382, 0.4749591026605633, 0.599812282465087, 0.8555165321413011]
    # generate random vectors

    def scale(r, theta, phi):
        return (r / 2 + 0.5) * (EARTH_RADIUS + LEO), theta * 2 * pi, phi * 2 * pi

    rx = [sphere(scale(random_r[i], random_theta[i], random_phi[i])) for i in range(20)]

    maxdif = 0.0
    for x in rx:
        dist = norm(A @ x - B @ x)
        maxdif = max(maxdif, dist)
        assert dist <= limit, f"Matrices are not close enough.\n||Ax - Bx|| = {int(dist)}km\nA={A}\nB={B}"
    print(f"max(||Ax - Bx||) = {int(maxdif)}km")


class TestECIToECF(unittest.TestCase):

    def test_similar_to_SD(self):
        """Test that our ECI to ECF transformation is similar enough to the Satellite Dynamics implementation.
        Note that for these test cases the max error was 27km."""

        t = dt(2000, 1, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.170822,    0.985302,     2.31292e-5],
                   [-0.985302,   -0.170822,    -3.32888e-5],
                   [-2.88486e-5, -2.84757e-5,   1.0]])
        assert_matrices_close(A, frames.eci_to_ecef(t))

        t = dt(2023, 3, 5, tzinfo=timezone.utc).timestamp()
        A = array([[-0.952589,    0.304254,   0.00202102],
                   [-0.304253,   -0.952591,   0.000667447],
                   [0.00212828,  2.09018e-5, 0.999998]])
        assert_matrices_close(A, frames.eci_to_ecef(t))

        t = dt(2023, 4, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.98863,     -0.15035,     0.00221924],
                   [0.15035,      -0.988633,   -0.000306172],
                   [0.00224005,    3.0972e-5,   0.999997]])
        assert_matrices_close(A, frames.eci_to_ecef(t))

        t = dt(2023, 8, 24, tzinfo=timezone.utc).timestamp()
        A = array([[0.881403,   -0.47236,   -0.0019064],
                   [0.472359,    0.881406,  -0.00105366],
                   [0.00217802,  2.8192e-5,  0.999998]])
        assert_matrices_close(A, frames.eci_to_ecef(t))

    def test_almost_no_change(self):
        """Makes sure that changes to the implementation had no effect on results.
        Tests this by making sure there are minimal (floating point precission error) level changes on 12 dates"""
        t = dt(2021, 1, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.1839457605221258, 0.9829363952901209, 0.0],
                   [-0.9829363952901209, -0.1839457605221258, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 2, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.6580806377921898, 0.7529474577704772, 0.0],
                   [-0.7529474577704772, -0.6580806377921898, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 3, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.9320129243938287, 0.3624250388188755, 0.0],
                   [-0.3624250388188755, -0.9320129243938287, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 4, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.9868422306700495, -0.16168615205440712, 0.0],
                   [0.16168615205440712, -0.9868422306700495, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 5, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.7785373536811516, -0.6275982703315469, 0.0],
                   [0.6275982703315469, -0.7785373536811516, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 6, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.3513983831437039, -0.9362260284375726, 0.0],
                   [0.9362260284375726, -0.3513983831437039, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 7, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.15635686230392626, -0.9877006285360311, 0.0],
                   [0.9877006285360311, 0.15635686230392626, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 8, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.6367443390207271, -0.7710749942288736, 0.0],
                   [0.7710749942288736, 0.6367443390207271, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 9, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.9403086811984223, -0.34032276453814236, 0.0],
                   [0.34032276453814236, 0.9403086811984223, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 10, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.9857861928327254, 0.1680047083279533, 0.0],
                   [-0.1680047083279533, 0.9857861928327254, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 11, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.7635051952063154, 0.6458016854212802, 0.0],
                   [-0.6458016854212802, 0.7635051952063154, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2021, 12, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.3453935542734844, 0.9384579333493481, 0.0],
                   [-0.9384579333493481, 0.3453935542734844, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 1, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.17962914501591593, 0.9837344002630237, 0.0],
                   [-0.9837344002630237, -0.17962914501591593, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 2, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.6547690475062801, 0.755829011369449, 0.0],
                   [-0.755829011369449, -0.6547690475062801, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 3, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.9304129898262267, 0.36651284883701135, 0.0],
                   [-0.36651284883701135, -0.9304129898262267, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 4, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.9875424839359093, -0.15735260538578436, 0.0],
                   [0.15735260538578436, -0.9875424839359093, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 5, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.7812848508065111, -0.6241746405456149, 0.0],
                   [0.6241746405456149, -0.7812848508065111, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 6, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.35550479386916095, -0.9346744575177206, 0.0],
                   [0.9346744575177206, -0.35550479386916095, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 7, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.15201959883257268, -0.988377479291583, 0.0],
                   [0.988377479291583, 0.15201959883257268, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 8, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.6333533789908415, -0.7738627121918225, 0.0],
                   [0.7738627121918225, 0.6333533789908415, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 9, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.9388056901181695, -0.34444720379435156, 0.0],
                   [0.34444720379435156, 0.9388056901181695, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 10, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.9865141931440005, 0.16367573652023631, 0.0],
                   [-0.16367573652023631, 0.9865141931440005, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 11, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.7663327455735337, 0.6424438676349317, 0.0],
                   [-0.6424438676349317, 0.7663327455735337, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))
        t = dt(2022, 12, 1, tzinfo=timezone.utc).timestamp()
        A = array([[0.3495098203557688, 0.9369327006113504, 0.0],
                   [-0.9369327006113504, 0.3495098203557688, 0.0],
                   [0.0, 0.0, 1.0]])
        testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))

class TestECEFtoGEOC(unittest.TestCase):

    def test_equal_to_SD(self):
        """Checks that the results are almost equal to SatelliteDynamic's sECEFtoGEOC"""
        testing.assert_array_almost_equal(
            frames.convert_ecef_to_geoc(array([1, 2, 3])),
            array([1.1071487177940904, 0.9302740141154721, -6.374395342613226e3])
        )
        testing.assert_array_almost_equal(
            frames.convert_ecef_to_geoc(array([9000, 7000, 8000])),
            array([0.6610431688506868, 0.6118300867286255, 7.550251277184119e3])
        )

class TestNEDtoECEF(unittest.TestCase):

    def test_equal_to_GN(self):
        """Checks that the results are almost equal to GravNav's ecef_Q_ned_mat.
        Source: https://github.com/RoboticExplorationLab/GravNav/blob/main/simple_sim/mag_field.jl#L257"""
        testing.assert_array_almost_equal(
            frames.ned_to_ecef(12, 123),
            array([[0.388091,  0.536573,  0.749316],
                   [-0.246772, 0.843854, -0.47646],
                   [-0.887969, 0.0,       0.459903]])
        )
        testing.assert_array_almost_equal(
            frames.ned_to_ecef(0.23, -0.76),
            array([[0.67078,  -0.227978, -0.705748],
                   [0.157059,  0.973666, -0.165246],
                   [0.724836,  0.0,       0.688921]])
        )

def np_arr_to_py(arr):
    """Converts a numpy array to a python command creating the array"""
    def format_row(row):
        return f"[{', '.join(map(str, row))}]"
    spliter = ',\n'
    return f"array([{spliter.join([format_row(row) for row in arr])}])"


def generate_no_change_tests_ECI_to_ECEF():
    """Generates a bunch of tests to make sure no changes have been made for the ECEF to ECI conversion."""
    for year in range(2021, 2023):
        for month in range(1, 13):
            t = dt(year, month, 1, tzinfo=timezone.utc).timestamp()
            res = frames.eci_to_ecef(t)
            print(f't = dt({year}, {month}, 1, tzinfo=timezone.utc).timestamp()')
            print(f'A = {np_arr_to_py(res)}')
            print('testing.assert_array_almost_equal(A, frames.eci_to_ecef(t))')
