"""Entry point for renderer."""
import taichi as ti
from visualizers.taichi import render
from conversions.tiff_to_ply import tiffToPly
from ui_control import renderUI


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


if __name__ == "__main__":
    # source = "slices/mri.tif"
    # source = "slices/mri"
    source = "slices/EmbryoCE/focal1.tif"
    output = "mri.ply"
    tiffToPly(source, output)
    # has to be imported here as ti is ready to be imported here
    from conversions.ply_to_cloud import readPly
    points = readPly(output)
    # this function contains the draw loop
    # and creation of the visualizer
    # Create a new Tkinter window
    renderUI(points)
    # render(points)
