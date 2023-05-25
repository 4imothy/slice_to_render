import os
import cv2
import numpy as np

# creates a point cloud file (.ply) from numpy array
def createPointCloud(filename, arr):
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


# extracts points from mask and adds to list
def addPoints(mask, points_list, depth):
    mask_points = np.where(mask == 255)
    for ind in range(len(mask_points[0])):
        # get point
        x = mask_points[1][ind]
        y = mask_points[0][ind]
        point = [x, y, depth]
        points_list.append(point)


def tiff_to_ply(path, output_name):
    # tweakables
    slice_thickness = 0.2  # distance between slices
    xy_scale = 1  # rescale of xy distance

    # load images
    size = (100, 100)
    flag = cv2.IMREAD_GRAYSCALE
    if os.path.isdir(path):
        images = get_images_from_dir(path, [".tif", ".tiff"], size, flag)
    else:
        images = get_images_from_file(path, size, flag)

    images1 = get_images_from_file("slices/mri.tif", size, flag)
    images2 = get_images_from_dir("slices/mri", [".tif", ".tiff"], size, flag)

    for i, elem in enumerate(images1):
        if not any(np.array_equal(elem, x) for x in images2):
            print("No matching element in images2 for element", i, "in images1")
        
    for i, elem in enumerate(images2):
        if not any(np.array_equal(elem, x) for x in images1):
            print("No matching element in images1 for element", i, "in images2")

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
        addPoints(prev_mask, points, depth)

        # # do a slice on after
        next_mask = np.zeros_like(curr)
        next_mask[after == 0] = curr[after == 0]
        addPoints(next_mask, points, depth)

        # get contour points (_, contours) in OpenCV 2.* or 4.*
        contours = cv2.findContours(curr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
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
    return createPointCloud(output_name, points)
    

def get_images_from_dir(folder, file_endings, size, flag):
    files = os.listdir(folder)
    images = []
    for file in files:
        is_tif = any(file.endswith(end) for end in file_endings)
        if is_tif:
            img = cv2.imread(os.path.join(folder, file), flag)
            img = cv2.resize(img, size)
            images.append(img)
    return images


def get_images_from_file(path, size, flag):
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
