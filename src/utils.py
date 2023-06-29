"""Utils to help with: file/dir readings."""
import cv2
import os


def isFileEnding(path, file_endings):
    """
    Return true if this file ends in one of the file endings.

    Parameters:
        - path: The file path to check
        - file_endings: A list of file endings
    """
    return any(path.endswith(end) for end in file_endings)


def readPathForFiles(path, file_endings):
    """
    Read a file or a directory and returns matching files.

    Current Implementations:
       - Directory: Read out the files, and do the actions
                    described below. If no action is described
                    this returns nothing
       - tif/tiff: Read a stacked image or single image
                    with openCV
    """
    size = (100, 100)
    flag = cv2.IMREAD_GRAYSCALE
    if os.path.isdir(path):
        images = _getImagesFromDir(path, file_endings,
                                   size, flag)
    else:
        # do a check for the file ending
        is_tif = isFileEnding(path, [".tif", ".tiff"])
        if is_tif:
            images = _getImagesFromFile(path, size, flag)

    return images


def _getImagesFromDir(folder, file_endings, size, flag):
    """
    Load images from a directory with specified file endings.

    Parameters:
    - folder (str): Path to the directory containing the images.
    - file_endings (list): List of file endings (e.g., [".tif", ".tiff"])
    to filter the images.
    - size (tuple): Size to resize the loaded images to.
    - flag (int): Flag indicating the color mode for reading the images.

    Returns:
    - list: List of loaded and resized images from the directory.
    """
    files = os.listdir(folder)
    images = []
    for file in files:
        is_tif = isFileEnding(file, [".tif", ".tiff"])
        if is_tif:
            img = cv2.imread(os.path.join(folder, file), flag)
            img = cv2.resize(img, size)
            images.append(img)
    return images


def _getImagesFromFile(path, size, flag):
    """
    Load images from a single, stacked tiff file and put them in an array.

    Parameters:
    - path (str): Path to the image file.
    - size (tuple): Size to resize the loaded images to.
    - flag (int): Flag indicating the color mode for reading the images.

    Returns:
    - list: List of loaded and resized images from the file.
    """
    images = []
    read, loaded = cv2.imreadmulti(path, flags=flag)
    if not read:
        # TODO make this an error type
        print("Couldn't Read File")
        exit(1)
    for img in loaded:
        # change here for more or less resolution
        img = cv2.resize(img, size)
        images.append(img)
    return images
