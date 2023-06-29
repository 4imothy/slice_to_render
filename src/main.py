"""Entry point for renderer."""
import taichi as ti
from conversions.tiff_to_ply import tiffToPly
from visualizers.taichi import render
from ui_control import renderUI
from slice_viewer import view_slices
from utils import readPathForFiles


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

render_with_control_ui = True
render_with_keyboard_controls = False
render_slices = False

# source = "slices/EmbryoCE/focal1.tif"
# source = "slices/mri.tif"
# Make it work for single images, not a priority really
# source = "slices/mri/mri_1.tiff"
source = "slices/mri"
  
if __name__ == "__main__":
    images = readPathForFiles(source, [".tif", ".tiff"])
    output = "mri.ply"
    if render_slices:
        view_slices(images)
        exit()
        
    tiffToPly(images, output)
    # has to be imported here as ti is ready to be imported here
    from conversions.ply_to_cloud import readPly

    points = readPly(output)
    # this function contains the draw loop
    # and creation of the visualizer
    # Create a new Tkinter window
    if render_with_keyboard_controls:
        render(points)
        exit()
    if render_with_control_ui:
        renderUI(points)
        exit()
