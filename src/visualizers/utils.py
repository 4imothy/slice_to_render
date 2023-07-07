"""
Utility functions for rendering particles.

Exported functions: vecToEulor, eulerToVec
"""
from math import acos, asin, cos, sin
from taichi.lang.matrix import Vector


def vecToEuler(v, eps: float = 1e-6):
    """
    Convert a 3D vector to Euler angles.

    Parameters:
        v (Vector): The input 3D vector.
        eps (float, optional): A small value used for float comparison.
        Defaults to 1e-6.

    Returns:
        tuple: A tuple containing the yaw and pitch angles in radians.
    """
    v = v.normalized()
    pitch = asin(v[1])

    sin_yaw = v[0] / cos(pitch)
    cos_yaw = v[2] / cos(pitch)

    if abs(sin_yaw) < eps:
        yaw = 0
    else:
        # fix math domain error due to float precision loss
        cos_yaw = max(min(cos_yaw, 1.0), -1.0)
        yaw = acos(cos_yaw)
        if sin_yaw < 0:
            yaw = -yaw

    return yaw, pitch


def eulerToVec(yaw, pitch):
    """
    Convert Euler angles to a 3D vector.

    Parameters:
        yaw (float): The yaw angle in radians.
        pitch (float): The pitch angle in radians.

    Returns:
        Vector: The resulting 3D vector.
    """
    v = Vector([0.0, 0.0, 0.0])
    v[0] = sin(yaw) * cos(pitch)
    v[1] = sin(pitch)
    v[2] = cos(yaw) * cos(pitch)
    return v
