import taichi as ti
from visualizers.particle_render import ParticleVisualizer
from conversions.tiff_to_ply import tiff_to_ply

if ti._lib.core.with_vulkan():
    arch = ti.vulkan
elif ti._lib.core.with_cuda():
    arch = ti.cuda
else:
    arch = ti.cpu

# NOTE: cuda not working on mac, check with other systems
if ti._lib.core.with_metal():
    arch = ti.cpu
ti.init(arch=arch)


def render(points):
    p_viewer = ParticleVisualizer("Visualize", points)
    while p_viewer.window.running:
        p_viewer.render()


if __name__ == "__main__":
    # source = "slices/mri.tif"
    # source = "slices/mri"
    source = "slices/EmbryoCE/focal1.tif"
    output = "mri.ply"
    tiff_to_ply(source, output)
    # has to be imported here as ti is ready to be imported here
    from conversions.ply_to_mesh import read_ply
    points = read_ply(output)
    render(points)
