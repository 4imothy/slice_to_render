"""
Converts tiff imaages in a dir or stacked in a single file to a ply file.

Exported functions tiffToPly
Private functions begin with an _
"""
import os
import cv2
import numpy as np


def _createPlyFile(filename, arr):
    """
    Create a ply file and writes the arr of points to it.

    Parameters:
    - filename (str): Name of the file to write
    - arr (List[List[float]]): Points to write to the file

    Returns:
    - filename (str): Name of the created file.
    """
    # open file and write boilerplate header
    file = open(filename, 'w')
    file.write("ply\n")
    file.write("format ascii 1.0\n")

    # count number of vertices
    num_verts = arr.shape[0]
    file.write("element vertex " + str(num_verts) + "\n")
    file.write("property float32 x\n")
    file.write("property float32 y\n")
    file.write("property float32 z\n")
    file.write("end_header\n")

    for point in arr:
        # create file string
        out_str = ""
        for axis in point:
            out_str += str(axis) + " "
        out_str = out_str[:-1]  # dump the extra space
        out_str += "\n"
        file.write(out_str)
    file.close()
    return filename


def _addPoints_(mask, points_list, depth):
    """
    Add points from a mask to a list of points.

    Parameters:
    - mask (numpy.ndarray): The mask array containing points to be added.
    - points_list (list): The list to which the points will be appended.
    - depth (float or int): The depth value to assign to the points.

    Returns:
    None
    """
    mask_points = np.where(mask == 255)
    for ind in range(len(mask_points[0])):
        # get point
        x = mask_points[1][ind]
        y = mask_points[0][ind]
        point = [x, y, depth]
        points_list.append(point)


def tiffToPly(path, output_name):
    """
    Convert TIFF image(s) to a point cloud in PLY format.

    Parameters:
    - path (str): Path to the TIFF image(s) or directory
        containing TIFF images.
    - output_name (str): Name of the output PLY file.

    Returns:
    - str: Path to the created PLY file.
    """
    # tweakables
    slice_thickness = 0.2  # distance between slices
    xy_scale = 1  # rescale of xy distance

    # load images
    size = (100, 100)
    flag = cv2.IMREAD_GRAYSCALE
    if os.path.isdir(path):
        images = _getImagesFromDir(path, [".tif", ".tiff"], size, flag)
    else:
        images = _getImagesFromFile(path, size, flag)

    # create masks
    masks = []
    for image in images:
        mask = cv2.inRange(image, 0, image.shape[0])
        masks.append(mask)

    # go through and get points
    depth = 0
    points = []
    for index in range(1, len(masks) - 1):
        # get three masks
        prev = masks[index - 1]
        curr = masks[index]
        after = masks[index + 1]

        # do a slice on previous
        prev_mask = np.zeros_like(curr)
        prev_mask[prev == 0] = curr[prev == 0]
        _addPoints_(prev_mask, points, depth)

        # # do a slice on after
        next_mask = np.zeros_like(curr)
        next_mask[after == 0] = curr[after == 0]
        _addPoints_(next_mask, points, depth)

        # get contour points (_, contours) in OpenCV 2.* or 4.*
        contours = cv2.findContours(
            curr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
        for con in contours:
            for point in con:
                p = point[0]  # contours have an extra layer of brackets
                points.append([p[0], p[1], depth])

        # increment depth
        depth += slice_thickness

    # rescale x,y points
    for ind in range(len(points)):
        # unpack
        x, y, z = points[ind]

        # scale
        x *= xy_scale
        y *= xy_scale
        points[ind] = [x, y, z]

    # convert points to numpy and dump duplicates
    points = np.array(points).astype(np.float32)
    points = np.unique(points.reshape(-1, points.shape[-1]), axis=0)

    # save to point cloud file
    return _createPlyFile(output_name, points)


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
        is_tif = any(file.endswith(end) for end in file_endings)
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
