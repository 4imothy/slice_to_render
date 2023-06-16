"""Read a mesh file and return a mesh or a ti.Vector.field of points."""

import numpy as np
from plyfile import PlyData
from main import ti


def read_ply(fn):
    """Take a file name and returns a taichi.Vector.field point cloud."""
    @ti.kernel
    def create_point_vert(x: ti.types.ndarray(),
                          y: ti.types.ndarray(),
                          z: ti.types.ndarray(),
                          length: ti.i32):
        for i in range(length):
            points[i] = ti.Vector([x[i], y[i], z[i]])

    plydata = PlyData.read(fn)
    # perform a check here if it has faces
    vertices = plydata['vertex']
    x = np.array(vertices['x'])
    y = np.array(vertices['y'])
    z = np.array(vertices['z'])
    number_vert = len(x)
    points = ti.Vector.field(3, dtype=ti.f32, shape=(number_vert,))
    # points = ti.Vector.field(3, dtype=ti.f32, shape=(number_vert, ))
    # points = ti.Matrix.field(n=3, m=number_vert, dtype=ti.f32)
    create_point_vert(x, y, z, number_vert)

    return points
