"""Entry point for renderer."""
from conversions.tiff_to_ply import tiffToPly
from slice_viewer import view_slices
from utils import readPathForFiles
import tkinter as tk
from tkinter import filedialog


# defining the strings for each rendering method
render_with_control_ui_str = "Render Points with Control UI"
render_with_keyboard_controls_str = "Render Points with Keyboard Controls"
render_slices_str = "Render Slices"


def ti_init():
    import taichi as ti
    # initialize taichi and make the ti object global
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
    return ti

# implement GUI to select the file, launch at current project location
# source = "slices/EmbryoCE/focal1.tif"
# source = "slices/mri.tif"
# source = "slices/mri"
# Make it work for single images, not a priority really
# source = "slices/mri/mri_1.tiff"


def pickImageAndMethod(x_scale, y_scale):
    window = tk.Tk()
    window.title("SetUp")
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # Calculate desired width and height
    desired_width = int(screen_width * x_scale)
    desired_height = int(screen_height * y_scale)
    # Set the window size
    window.geometry(f"{desired_width}x{desired_height}")
    weight = 1
    for i in range(4):     
        window.grid_rowconfigure(i, weight=weight)
        window.grid_columnconfigure(i, weight=weight)

    source = None
    rendering_method = None
    selected_label = tk.Label(window)
    selected_label.grid(row=0, column=1)
    def getLabel(source, rendering_method):
        return f"Selected Path: {source}\nRendering Method: {rendering_method}"
    selected_label.configure(text=getLabel(source, rendering_method))

    def getImageFile():
        nonlocal source
        source = filedialog.askopenfilename()
        selected_label.configure(text=getLabel(source, rendering_method))
    def getImageDir():
        nonlocal source
        source = filedialog.askdirectory()
        selected_label.configure(text=getLabel(source, rendering_method))
    def renderWithControlUI():
        nonlocal rendering_method
        rendering_method = render_with_control_ui_str
        selected_label.configure(text=getLabel(source, rendering_method))
    def renderWithKeyboardControls():
        nonlocal rendering_method
        rendering_method = render_with_keyboard_controls_str
        selected_label.configure(text=getLabel(source, rendering_method))
    def renderSlices():
        nonlocal rendering_method
        rendering_method = render_slices_str
        selected_label.configure(text=getLabel(source, rendering_method))
    def returnSelections():
        window.destroy()

    select_image = tk.Button(window, text="Pick Image File", command=getImageFile)
    select_image.grid(row=2, column=1)
    dir_select = tk.Button(window, text="Pick Image Directory", command=getImageDir)
    dir_select.grid(row=2, column=0)
    render_control_ui = tk.Button(window, text="Render with Control UI", command=renderWithControlUI)
    render_control_ui.grid(row=1, column=0)
    render_keyboard_controls = tk.Button(window, text="Render with Keyboard Controls", command=renderWithKeyboardControls)
    render_keyboard_controls.grid(row=1, column=1)
    render_slices = tk.Button(window, text="Render Slices", command=renderSlices)
    render_slices.grid(row=1, column=2)
    start_button = tk.Button(window, text="Begin Rendering", command=returnSelections)
    start_button.grid(row=3, column=1)

    window.mainloop()

    return source, rendering_method

  
if __name__ == "__main__":
    source, render_method = pickImageAndMethod(0.4, 0.4)
    # source = "slices/mri.tif"
    # render_method = render_with_control_ui_str
    if source is None or render_method is None:
        print("Didn't select a rendering method or didn't select a target to view")
        exit()
    # returns grayscale 100 x 100 images
    size = (128 , 128)
    images = readPathForFiles(source, [".tif", ".tiff"], size)
    if images is None:
        print("Error: Did not select a supported image type.")
        exit()
    output = "mri.ply"
    if render_method == render_slices_str:
        view_slices(images)
        exit()
    global ti
    ti = ti_init() 
    tiffToPly(images, output)

    from conversions.ply_to_cloud import readPly
    points = readPly(output)
    # this function contains the draw loop
    # and creation of the visualizer
    # Create a new Tkinter window
    if render_method == render_with_keyboard_controls_str:
        from visualizers.taichi import render
        render(points)
        exit()
    if render_method == render_with_control_ui_str:
        from ui_control import renderUI
        renderUI(points)
        exit()
