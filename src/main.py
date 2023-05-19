import taichi as ti
from conversions.ply_to_mesh import read_ply
from renders.particle_render import ParticleVisualizer
from conversions.tiff_to_ply import tiff_to_ply

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


def begin_render(points):
    # particles_pos = ti.Vector.field(3, dtype=ti.f32, shape=(50493))
    p_viewer = ParticleVisualizer("Visualize", points)
    while p_viewer.window.running:
        p_viewer.render() 


if __name__ == "__main__":
    # source = "slices/mri.tif"
    # source = "slices/mri"
    source = "slices/EmbryoCE/focal1.tif"
    output = "mri.ply"
    # tiff_to_ply("slices/mri", "mri_from_dir.ply")
    tiff_to_ply(source, output)
    # tiff_to_ply("slices/EmbryoCE/focal1.tif", "embreyoce.ply")
    points = read_ply(output)
    begin_render(points)
