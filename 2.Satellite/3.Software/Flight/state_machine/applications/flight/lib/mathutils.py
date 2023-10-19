try:
    from ulab.numpy import array, ndarray, zeros, eye as I, dot as matmul  # noqa: E741 (I is not ambiguous)
except Exception:
    from numpy import array, ndarray, zeros, eye as I, matmul  # noqa: E741 (I is not ambiguous)

def block(S):
    """Returns a block matrix from a list of lists of matrices
    For example:

    .. code-block:: python

        A = eye(2)
        B = zeros((2, 3))
        C = ones((4, 2))
        D = ones((4, 3)) * 4
        block([[A, B],
               [C, D]])
        array([[1., 0., 0., 0., 0.],
               [0., 1., 0., 0., 0.],
               [1., 1., 4., 4., 4.],
               [1., 1., 4., 4., 4.],
               [1., 1., 4., 4., 4.],
               [1., 1., 4., 4., 4.]])"""
    w = sum([len(m[0]) for m in S[0]])
    h = sum([len(row[0]) for row in S])
    M = zeros((h, w))
    i = 0
    j = 0
    for row in S:
        di = len(row[0])
        for matrix in row:
            dj = len(matrix[0])
            M[i:i + di, j:j + dj] = matrix
            j += dj
        i += di
        j = 0
    return M


def hat(v):
    """Converts v to a matrix such that hat(v)w = cross(v, w)

    :param v: vector
    :type v: numpy.ndarray
    :return: 3x3 numpy array
    """
    if not isinstance(v, ndarray):
        v = array(v)
    return array([
        [0,      -v[2],   v[1]],
        [v[2],    0,     -v[0]],
        [-v[1],   v[0],   0]])

def quaternion_to_left_matrix(q):
    """Converts a scalar-first unit quaternion into the left-side matrix for quaternion multiplication"""
    if not isinstance(q, ndarray):
        q = array([q])
    qs, qv = q[0], array(q[1:4])

    dr = qs * I(3) + hat(qv)
    qv = array([qv])

    M = block(
        [[array([[qs]]),   -qv],
         [qv.transpose(),   dr]])

    return M

def quaternion_to_rotation_matrix(q):
    """Converts a scalar-first unit quaternion into the rotation matrix Qv = qvq+"""
    if not isinstance(q, ndarray):
        q = array([q])
    qs, qv = q[0], array(q[1:4]).transpose()

    return I(3) + 2 * matmul(hat(qv), (qs * I(3) + hat(qv)))

def quaternion_mul(q1, q2):
    """Multiplies a scalar-first unit quaternion by another scalar-first unit quaternion"""
    return matmul(quaternion_to_left_matrix(q1), q2)
