"""Multiplicative Extended Kalman Filter
Based on Zac Manchester's Formulation
Writen by Aleksei Seletskiy

A Multiplicative Extended Kalman filter (MEKF) is a variant of an Extended Kalman Filter (EKF).
The important features of this MEKF are:
- We eliminate rigibody dynamics by assuming we have a near perfect gyro (after the bias β is removed).
- We assume our gyro sample is rate is high enough that ω is essentialy constant over a sample period.
- Thus we treat ω (angular velocity) as a the control.
- We are running an EKF with a local axis-angle error vector, but the global state is stored using a quaternion.
- The gyro bias (β) is estimated.
"""
try:
    from ulab.numpy import dot as matmul, eye as I, zeros, array, linalg, concatenate as concat  # noqa: E741
except Exception:
    from numpy import linalg, matmul, eye as I, zeros, array, concatenate as concat  # noqa: E741
from lib.mathutils import quaternion_mul, quaternion_to_left_matrix, hat, block, quaternion_to_rotation_matrix
from math import cos, sin

q = array([0., 0., 0., 0.])  # Quaternion attitude vector
β = array([0., 0., 0.])  # Gyro bias vector
P = I(6)  # Covariance matrix


def propagate_state(q, β, ω, δt):
    """State propogation function.
    Substracts out the gyro bias from the gyro reading,
    then propogates the state forward by the time step.

    :param q: Quaternion attitude vector
    :type q: numpy.array
    :param β: Gyro bias axis-angle vector
    :type β: numpy.array
    :param ω: Measured angular velocity
    :type ω: numpy.array
    :param δt: Time step
    :type δt: float
    :return: New quaternion attitude vector
    """
    θ = linalg.norm(ω - β) * δt
    if linalg.norm(ω - β) == 0:
        return q
    r = (ω - β) / linalg.norm(ω - β)
    return quaternion_mul(q, concat([[cos(θ / 2)], r * sin(θ / 2)]))

def step(
    ω,
    δt,
    nr_mag,
    nr_sun,
    br_mag,
    br_sun
):
    """Updates the state of the MEKF by one itteration of sensor readings.

    :param ω: Gyroscope reading
    :param δt: Time step
    :param nr_mag: Inertial frame magnetic field vector
    :param nr_sun: Inertial frame sun pointing vector
    :param br_mag: Measured body frame magnetic field vector
    :param br_sun: Measured body frame sun pointing vector
    """
    global q
    global β
    global P

    W = I(6) * 1e-6
    V = I(6) * 1e-6

    # Predict
    q_p = propagate_state(q, β, ω, δt)  # β remains constant

    # The following is equivalent to:
    # R = exp(-hat(ω-β) * δt)
    v = - (ω - β)
    mag = linalg.norm(v)
    v̂= hat(v / mag)
    R = I(3) + (v̂) * sin(mag * δt) + matmul(v̂, v̂) * (1 - cos(mag * δt))

    A = block([
        [R,              (-δt * I(3))],
        [zeros((3, 3)),  I(3)]])
    P_p = matmul(A, matmul(P, A.transpose())) + W

    # Innovation
    Q = quaternion_to_rotation_matrix(q_p).transpose()
    body_measurements = concat([br_mag, br_sun])
    inertial_measurements = concat([nr_mag, nr_sun])
    inertial_to_body = block([[Q,              zeros((3, 3))],
                             [zeros((3, 3)),  Q]])
    Z = body_measurements - matmul(inertial_to_body, inertial_measurements)
    C = block([[hat(ᵇr_mag), zeros((3, 3))],
              [hat(ᵇr_sun), zeros((3, 3))]])
    S = matmul(C, matmul(P_p, C.transpose())) + V  # CP_PC' + V

    # Kalman Gain
    L = matmul(P_p, matmul(C.transpose(), linalg.inv(S)))  # P_pC'S^-1

    # Update
    δx = matmul(L, Z)
    ϕ = δx[0:3]
    δβ = δx[3:]
    θ = linalg.norm(ϕ)
    r = ϕ / θ
    q_u = matmul(quaternion_to_left_matrix(q_p), concat([[cos(θ / 2)], r * sin(θ / 2)]))
    β_u = β + δβ
    e1 = (I(6) - matmul(L, C))                # I(6) - LC
    e2 = (I(6) - matmul(L, C)).transpose()    # (I(6) - LC)'
    e3 = matmul(e1, matmul(P_p, e2))          # e1 * P_p * e2
    e4 = matmul(L, matmul(V, L.transpose()))  # LVL'
    P_u = e3 + e4
    # Pᵤ = (I(6) - LC) * Pₚ * (I(6) - LC)' + LVL'

    q = q_u
    β = β_u
    P = P_u
