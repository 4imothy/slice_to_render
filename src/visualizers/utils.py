from math import acos, asin, cos, sin
from taichi.lang.matrix import Vector


def vec_to_euler(v, eps: float = 1e-6):
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


def euler_to_vec(yaw, pitch):
    v = Vector([0.0, 0.0, 0.0])
    v[0] = sin(yaw) * cos(pitch)
    v[1] = sin(pitch)
    v[2] = cos(yaw) * cos(pitch)
    return v
