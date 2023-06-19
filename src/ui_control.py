"""Use taichi and tkinter to create a controllable visualizing window."""
import tkinter as tk
from concurrent import futures
from visualizers.taichi import ParticleVisualizer


# make the proper things private in the Particlevisualizer class
def renderUI(points):
    """
    Create 2 windows to render and manipulate the point cloud.

    This function contains the render loop

    Parameters:
        - Points (taichi.Vector.field): the points to render

    Create the tk window in this file
    Returns:
        - None
    """
    # tk must be instantiated first
    window = _createWindow("Controller", 0.2, 0.2)
    visualizer = ParticleVisualizer("Visualize", points)

    move_dist = 5

    tk.Button(window, text="Move Back",
              command=lambda:
              (executor.submit(visualizer.moveBackwardDist, move_dist),
               executor.submit(visualizer.render()))
              ).grid(row=0, column=0)

    tk.Button(window, text="Move Forward",
              command=lambda:
              (executor.submit(visualizer.moveForwardDist, move_dist),
               executor.submit(visualizer.render()))
              ).grid(row=0, column=1)

    camera_scale = tk.Scale(window, from_=0, to=100, orient=tk.HORIZONTAL)
    prev_scale = camera_scale.get()
    camera_scale.grid(row=1, column=0)
    was_change = True
    # TODO causes issues when tk window is closed first
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        while visualizer.window.running and _tk_window_active(window):
            new_scale = camera_scale.get()
            # render the tkinter window
            window.update()
            # render the visualizer window
            # only if there were changes than update the taichi window
            if prev_scale != new_scale:
                prev_scale = new_scale
                was_change = True

            if was_change:
                # go through one render loop
                executor.submit(visualizer.moveBackwardDist(1))
                executor.submit(visualizer.render())
                was_change = False
    if _tk_window_active(window):
        window.destroy()
    visualizer.window.destroy()


# checks if a tk window is active
def _tk_window_active(window):
    try:
        window.state()
        return True
    except tk.TclError:
        return False


def _createWindow(name, x_scale, y_scale):
    """
    Create a tk window to control the taichi visualizer.

    Parameters:
        - name (str): Name of the window
        - x_scale (float): Percent of width of screen to take up
        - y_scale (float): Percent of height of screen to take up

    Returns
        - Window (tkinter.Tk): Top level widget
    """
    window = tk.Tk()
    window.title(name)
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # Calculate desired width and height
    desired_width = int(screen_width * x_scale)
    desired_height = int(screen_height * y_scale)
    # Set the window size
    window.geometry(f"{desired_width}x{desired_height}")

    return window
