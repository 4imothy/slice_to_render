# Read a mesh file and return a mesh or a ti.Vector.field of points
# return whether the return is points or mesh so that the renderer
# can call scene.particles or scene.mesh respectively

import taichi as ti
from plyfile import PlyData

def read_ply(fn):
    plydata = PlyData.read(fn)
    # perform a check here if it has faces
    vertices = plydata['vertex']
    x = vertices['x']
    y = vertices['y']
    z = vertices['z']
    points = create_point_vert(x, y, z)
    # make the 50493 a variable read from the file
    return points


def create_point_vert(x, y, z):
    vec = ti.Vector.field(3, dtype=ti.f32, shape=(len(x), ))
    for i in range(len(x)):
        vec[i] = ti.Vector([x[i], y[i], z[i]])

    return vec
