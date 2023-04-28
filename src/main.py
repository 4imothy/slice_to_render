import taichi as ti
import os
from conversions.ply_to_mesh import read_ply
from renders.particle_render import ParticleVisualizer
from conversions.tiff_to_ply import tiff_to_ply


def begin_render(file):
    if ti._lib.core.with_vulkan():
        arch = ti.vulkan
    elif ti._lib.core.with_cuda():
        arch = ti.cuda
    else:
        arch = ti.cpu()

    # cuda not working on mac, check with other systems
    if ti._lib.core.with_metal():
        arch = ti.cpu
    ti.init(arch=arch)

    # particles_pos = ti.Vector.field(3, dtype=ti.f32, shape=(50493))
    particles_pos = read_ply(file)
    p_viewer = ParticleVisualizer("Visualize", particles_pos)
    while p_viewer.window.running:
        p_viewer.render() 


if __name__ == "__main__":
    # tiff_to_ply("slices/mri", "mri.ply", dir=True)
    begin_render("mri.ply")
    # tiff_to_ply("slices/mri.tif", "mri_single.ply", dir=False)
    begin_render("mri_single.ply")
    # tiff_to_ply("slices/EmbryoCE/focal1.tif", "embreyoce.ply", dir=False)
    # begin_render("embreyoce.ply")
