import taichi as ti
import os
from conversions.ply_to_mesh import read_ply
from renders.particle_render import ParticleVisualizer
# from definitions import ROOT_DIR
from conversions.tiff_to_ply import tiff_to_ply

import argparse

# Create an argument parser
parser = argparse.ArgumentParser()

# mode render
parser.add_argument('-r', '--render', action='store_true', help='use render mode')
# mode render
parser.add_argument('-c', '--convert', action='store_true', help='use convert mode')
# slices to create file from
parser.add_argument('-s', '--slices', type=str, help='path to folder of slices')
# output file, only valid if slices was given
parser.add_argument('-o', '--output', type=str, help='output file of the slices')
# file to render
parser.add_argument('-i', '--input', type=str, help='path to input file')


def parse_args():
    args = parser.parse_args()
    convert = args.convert
    render = args.render
    slices = args.slices
    output = args.output
    input = args.input
    if convert and (not slices or not output):
        exit("If converting, need a directory if tiffs and an output")
    if not convert and not render:
        exit("Must either render or convert") 
    if slices and not os.path.exists(os.path.expanduser(slices)):
        exit(f"Path to slices: {slices} doesn't exist")
        if os.path.isfile(slices):
            exit(f"Path to slices: {slices} is a file, need directory")
    if slices and not output:
        exit("If you give a directory of slices you need to give an output file to create")
    if not input and not output and render:
        exit("No file to render, will eiter render input file or output if no input given")
    if input and not output and not os.path.exists(os.path.expanduser(input)):
        exit(f"Path to input: {input} doesn't exist")
        if os.path.isdir(input):
            exit(f"Path to input: {input} is a directory, need a file")
    # if render and no output and no input

    if convert:
        filename = tiff_to_ply(os.path.expanduser(slices), output)
    if render:
        if input:
            filename = input

        begin_render(os.path.expanduser(filename))


def begin_render(file):
    arch = ti.vulkan if ti._lib.core.with_vulkan() else (ti.cuda if ti._lib.core.with_cuda() else ti.cpu())
    # cuda not working on mac, check with other systems
    if ti._lib.core.with_metal():
        arch = ti.cpu
    ti.init(arch=arch)

    # particles_pos = ti.Vector.field(3, dtype=ti.f32, shape=(50493))
    particles_pos = read_ply(file)
    p_viewer = ParticleVisualizer("Visualize", particles_pos)
    while p_viewer.window.running:
        p_viewer.render() 


if __name__ == "__main__":
    parse_args()
