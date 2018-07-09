#!/usr/bin/python

''' 2D RENDERING OF MSETS '''

import math, cmath, progressbar
import numpy as np
import seaborn as sns
import time, os, sys, argparse
from calc import *

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap

np.set_printoptions(threshold=np.nan) # allows for printing entire np arrays

path = "./"
jules = True
esc_radius = 420.0
spongebob = 'the krusty krab is unfair, mr krabs is in there, standing at concession, plotting his oppression!!'

parser = argparse.ArgumentParser()
parser.add_argument("--x0", type=float, help='window x0', required=False)
parser.add_argument("--x1", type=float, help='window x1', required=False)
parser.add_argument("--y0", type=float, help='window y0', required=False)
parser.add_argument("--y1", type=float, help='window y1', required=False)
parser.add_argument("--xres", type=int, help='window x resolution', required=False)
parser.add_argument("-f", "--frames", type=int, help='number of frames to generate', required=False)
parser.add_argument("--func", type=str, help='the function defining the IFS', required=False)
parser.add_argument("--type", type=str, help='m (mandelbrot) or j (julia)', required=False)
parser.add_argument("-r", type=float, help='real component of the seed', required=False)
parser.add_argument("-c", type=float, help='complex component of the seed', required=False)

# parser.add_argument("-t", "--testing", action='store_true', help='a testing flag for visualization')
args = parser.parse_args()

# prompt user for different options (function, seed, resolution, max iterations, etc.)

f_str = args.func
if args.func is None:
    print('Please choose from one of the following functions:\n'
            '(1) f(z) = z**2 + c\n'
            '(2) f(z) = e**z + c\n'
            '(3) f(z) = sin(z) + c\n'
            '(4) f(z) = cos(z) + c\n'
            '(5) f(z) = c*sin(z)\n'
            '(6) f(z) = c*cos(z)\n'
            '(7) f(z) = c*z*(1-z)\n'
            '(8) f(z) = null_eqn')
    while True:
        try:
            temp = int(input("Choose a number corresponding with your intended option (1-8): "))
            if temp == 8:
                f_str = "null"
                esc_radius = 420.0 # create eqn
            elif temp == 7:
                f_str = "log_c"
                esc_radius = 50.0
            elif temp == 6:
                f_str = "ccos"
                esc_radius = 10.0 * math.pi
            elif temp == 5:
                f_str = "csin"
                esc_radius = 10.0 * math.pi
            elif temp == 4:
                f_str = "cos"
                esc_radius = 10.0 * math.pi
            elif temp == 3:
                f_str = "sin"
                esc_radius = 10.0 * math.pi
            elif temp == 2:
                f_str = "e**z"
                esc_radius = 50.0
            elif temp == 1:
                f_str = "z**2"
                esc_radius = 2.0
            else:
                f_str = int(spongebob)
            break
        except ValueError:
            print("Invalid response, please try again.")

if f_str == "null":
    while True:
        try:
            temp = float(input("Specify an escape radius: "))
            if temp > 0:
                esc_radius = temp
                break
            else:
                temp = int(spongebob)
        except:
            print("Invalid input, please try again.")

while True:
    try:
        temp = input("Would you like to plot a Mandelbrot or Julia set? [m/j]: ")
        if temp == 'm':
            jules = False
            break
        elif temp == 'j':
            jules = True
            break
        else:
            jules = int(spongebob)
    except ValueError:
        print("Invalid input, please try again.")

init_r = args.r
init_c = args.c
if args.r is None or args.c is None:
    while True:
        try:
            init_r = float(input("Input real component of seed: "))
            init_c = float(input("Input complex component of seed: "))
            break
        except ValueError:
            print("Invalid input, please try again.")

x_0 = args.x0
x_1 = args.x1
y_0 = args.y0
y_1 = args.y1
if args.x0 is None or args.x1 is None or args.y0 is None or args.y1 is None:
    while True:
        try:
            x_0 = float(input("Input xmin: "))
            x_1 = float(input("Input xmax: "))
            y_0 = float(input("Input ymin: "))
            y_1 = float(input("Input ymax: "))
            break
        except ValueError:
            print("Invalid input, please try again.")
x_range = x_1 - x_0
y_range = y_1 - y_0

frames = args.frames
if args.frames is None:
    while True:
        try:
            frames = int(input("Input number of frames: "))
            if iter_m < 1:
                frames = int(spongebob)
            break
        except ValueError:
            print("Invalid input, please try again.")

res_x = args.xres
if args.xres is None:
    while True:
        try:
            temp = int(input("What do you want the x resolution to be?: "))
            if temp > 0:
                res_x = temp
                break
            else:
                res_x = int(spongebob)
        except ValueError:
            print("Invalid input, please try again.")
res_y = int(res_x * float(y_range) / float(x_range))

if __name__ == '__main__':
    my_cmap = ListedColormap(sns.color_palette("cubehelix", 8))
    base = 1

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    fig.set_tight_layout(True)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    print("Entering GIF creation")
    print("Generating data")

    bar = progressbar.ProgressBar(maxval=frames, \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' ', progressbar.ETA()])
    bar.start()

    all_data = [mandel(0, f_str, seed = np.complex128(init_r+init_c*1j),
        res = (res_x,res_y), xrng = (x_0,x_1), yrng = (y_0,y_1),
        iter_max = base, julia = jules, esc_radius = esc_radius)]
    for i in range(1, frames+1):
        # TODO: every once in a while, find brightest set of pixels in image (max pooling) and zoom in there

        data = mandel(i, f_str, seed = np.complex128(init_r+init_c*1j), res = (res_x,res_y),
            xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = base+i,
            julia = jules, esc_radius = esc_radius)

        # while avg value in data is below some threshold, recalculate with lower iter_max

        all_data.append(mandel(i, f_str, seed = np.complex128(init_r+init_c*1j), res = (res_x,res_y),
            xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = base+i,
            julia = jules, esc_radius = esc_radius))

        bar.update(i-1)

    print("Saving GIF...")

    bar.update(0)

    def update_image(i, b = bar):
        """Returns updated ax"""
        ax.imshow(all_data[i], cmap=my_cmap)
        b.update(i)
        return ax
    ani = animation.FuncAnimation(fig, lambda x: update_image(x), \
            frames=np.arange(0, frames), interval=1)

    bar.finish()

    ani.save("mandelbrot.gif", writer='imagemagick', dpi=100, fps=30)

    print('Done!')
