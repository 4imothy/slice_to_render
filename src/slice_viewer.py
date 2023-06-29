"""Use openCV to view slices and tkinter to create widgets to control the window."""
import cv2
import tkinter as tk
from PIL import Image, ImageTk


def view_slices(images):
    """
    Display the OpenCV images in a window using Tkinter.

    Parameters:
    - images: list of images
    """
    window = tk.Tk()
    window.title("Image Viewer")

    # Create a label to display the image
    image_label = tk.Label(window)
    image_label.pack()

    # Function to update the displayed image
    def update_image(index):
        cv2image = cv2.cvtColor(images[index], cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv2image)
        tk_image = ImageTk.PhotoImage(image=pil_image)
        image_label.config(image=tk_image)
        image_label.image = tk_image

    # Initial image index
    current_index = 0
    update_image(current_index)

    # Function to handle keypress events
    def handle_keypress(event):
        nonlocal current_index
        if event.keysym == "Right":
            current_index = (current_index + 1) % len(images)
            update_image(current_index)
        elif event.keysym == "Left":
            current_index = (current_index - 1) % len(images)
            update_image(current_index)

    # Bind keypress events to the window
    window.bind("<KeyPress>", handle_keypress)
    window.focus_set()

    # Function to handle button click events
    def next_image():
        nonlocal current_index
        current_index = (current_index + 1) % len(images)
        update_image(current_index)
        _updateLabel(index_label, current_index)

    def prev_image():
        nonlocal current_index
        current_index = (current_index - 1) % len(images)
        update_image(current_index)
        _updateLabel(index_label, current_index)

    # Create buttons for navigation
    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)
    prev_button = tk.Button(button_frame, text="Previous", command=prev_image)
    prev_button.pack(side=tk.LEFT)
    next_button = tk.Button(button_frame, text="Next", command=next_image)
    next_button.pack(side=tk.LEFT)

    # Create label to display current index
    index_label = tk.Label(window)
    _updateLabel(index_label, current_index)
    index_label.pack()

    # Start the Tkinter main loop
    window.mainloop()

def _updateLabel(label, current_index):
    label.config(text=f"Index: {current_index + 1}")
