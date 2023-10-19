try:
    from ulab.numpy import eye as identity, array, linalg, cross, dot as matmul, isfinite, all
except Exception:
    from numpy import identity, array, linalg, cross, matmul, isfinite, all

def bcross(b, ω, k=7e-4):
    b = (array(b))
    ω = (array(ω))
    b_hat = b / linalg.norm(b)
    bbt = matmul(array([b_hat]).transpose(), array([b_hat]))
    M = - k * matmul(identity(3) - bbt, ω)
    # control
    m = (1 / linalg.norm(b)) * cross(b_hat, M)
    if all(isfinite(m)):
        return m
    return [0, 0, 0]
