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

    # write points
    point_count = 0
    for point in arr:
        # progress check
        point_count += 1
        if point_count % 10000 == 0:
            print("Point: " + str(point_count) + " of " + str(len(arr)))

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


def tiff_to_ply(path, output_name, dir=True):
    # tweakables
    slice_thickness = .2  # distance between slices
    xy_scale = 1  # rescale of xy distance

    # load images
    if dir:
        images = get_images_from_dir(path, [".tif", ".tiff"])
    else:
        print("reading tif with multiple images not available")
        exit(1)
    # keep a blank mask
    blank_mask = np.zeros_like(images[0], np.uint8)

    # create masks
    masks = []
    masks.append(blank_mask)
    for image in images:
        # mask
        mask = cv2.inRange(image, 0, 100)

        cv2.waitKey(1)
        masks.append(mask)
    masks.append(blank_mask)

    # go through and get points
    depth = 0
    points = []
    for index in range(1, len(masks)-1):
        # progress check
        # print("Index: " + str(index) + " of " + str(len(masks)))

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
        contours, _ = cv2.findContours(curr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
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


def get_images_from_dir(folder, file_endings):
    files = os.listdir(folder)
    images = []
    is_file = True
    for file in files:
        is_file = any(file.endswith(end) for end in file_endings)

        if is_file:
            img = cv2.imread(os.path.join(folder, file), cv2.IMREAD_GRAYSCALE)
            # change here for more or less resolution
            img = cv2.resize(img, (100, 100))
            images.append(img)
    return images