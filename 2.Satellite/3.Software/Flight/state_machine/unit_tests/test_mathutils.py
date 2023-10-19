import unittest
import sys
from numpy import testing, array, zeros, eye, ones

sys.path.insert(0, './state_machine/applications/flight')

from lib.mathutils import hat, quaternion_to_left_matrix, block, quaternion_to_rotation_matrix, quaternion_mul

class HatTests(unittest.TestCase):

    def test(self):
        testing.assert_equal(
            array(
                [[0,  -3,  2],
                 [3, 0,  -1],
                 [-2,  1, 0]]),
            hat([1, 2, 3])
        )
        testing.assert_equal(
            array(
                [[0.0,  -0.6, 0.4],
                 [0.6,  0.0,  -0.3],
                 [-0.4, 0.3,  0.0]]),
            hat([0.3, 0.4, 0.6])
        )
        testing.assert_equal(
            array([[0.0, 0.3982060297895143, 0.2543322132742208],
                   [-0.3982060297895143, 0.0, -0.7083212680159963],
                   [-0.2543322132742208, 0.7083212680159963, 0.0]]),
            hat(array([0.7083212680159963, 0.2543322132742208, -0.3982060297895143]))
        )

class BlockTests(unittest.TestCase):

    def test(self):
        a = array([[1, 1]])
        b = array([[2]])
        c = array(
            [[3, 3],
             [3, 3],
             [3, 3]])
        d = array(
            [[4],
             [4],
             [4]])
        testing.assert_equal(
            block([[a, b], [c, d]]),
            array([[1, 1, 2],
                   [3, 3, 4],
                   [3, 3, 4],
                   [3, 3, 4]])
        )
        a = zeros((2, 3))
        b = eye(2) * 2
        c = eye(3) * 5
        d = ones((3, 2))
        testing.assert_equal(
            block([[a, b], [c, d]]),
            array([[0, 0, 0, 2, 0],
                   [0, 0, 0, 0, 2],
                   [5, 0, 0, 1, 1],
                   [0, 5, 0, 1, 1],
                   [0, 0, 5, 1, 1]])
        )

class QuaternionToLeftTests(unittest.TestCase):

    def test(self):
        q = array([0.692, -0.332,  0.499,  0.403])
        testing.assert_almost_equal(
            array(
                [[0.692,   0.332,  -0.499,  -0.403],
                 [-0.332,  0.692,  -0.403,   0.499],
                 [0.499,   0.403,   0.692,   0.332],
                 [0.403,  -0.499,  -0.332,   0.692]]),
            quaternion_to_left_matrix(q)
        )
        q = array([0.5, 0.5, 0.5, 0.5])
        testing.assert_equal(
            array(
                [[0.5,  -0.5,  -0.5,  -0.5],
                 [0.5,   0.5,  -0.5,   0.5],
                 [0.5,   0.5,   0.5,  -0.5],
                 [0.5,  -0.5,   0.5,   0.5]]),
            quaternion_to_left_matrix(q)
        )
        q = array([-0.5244311817641283, 0.7083212680159963, 0.2543322132742208, -0.3982060297895143])
        testing.assert_almost_equal(
            array([[-0.524431, -0.708321, -0.254332, 0.398206],
                   [0.708321, -0.524431, 0.398206, 0.254332],
                   [0.254332, -0.398206, -0.524431, -0.708321],
                   [-0.398206, -0.254332, 0.708321, -0.524431]]),
            quaternion_to_left_matrix(q),
            decimal=6
        )

class QuaternionToRotationMatrixTest(unittest.TestCase):

    def test(self):
        # Using: https://www.andre-gaschler.com/rotationconverter/ to generate test cases
        # Test cases switched to scalar first (rather than the converter's scalar last)
        q1 = array([0.6804138, 0.4082483, 0.5443311, 0.2721655])
        testing.assert_almost_equal(
            array([[0.2592593,  0.0740741,  0.9629630],
                   [0.8148148,  0.5185185, -0.2592593],
                   [-0.5185185,  0.8518519,  0.0740741]]),
            quaternion_to_rotation_matrix(q1)
        )
        q2 = array([0.1601282, 0.3202563, 0.8006408, 0.4803845])
        testing.assert_almost_equal(
            array([[-0.7435898,  0.3589744,  0.5641026],
                   [0.6666667,  0.3333333,  0.6666667],
                   [0.0512821,  0.8717949, -0.4871795]]),
            quaternion_to_rotation_matrix(q2)
        )
        # identity
        qi = array([1, 0, 0, 0])
        testing.assert_almost_equal(
            eye(3),
            quaternion_to_rotation_matrix(qi)
        )


class QuaternionMultiplicationTest(unittest.TestCase):

    def test(self):
        q1 = array([0.6804138, 0.4082483, 0.5443311, 0.2721655])
        q2 = array([0.1601282, 0.3202563, 0.8006408, 0.4803845])
        testing.assert_almost_equal(
            array([-0.58835, 0.32686, 0.52298, 0.52298]),
            quaternion_mul(q1, q2),
            decimal=5
        )
