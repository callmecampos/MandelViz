#!usr/bin/python
from PIL import Image, ImageDraw
import math, sys, cmath
import numpy as np
import pylab as py
import imageio
import time

np.set_printoptions(threshold=np.nan) # allows for printing entire np arrays

path = "./"
jules = False
f_str = "z**2"
esc_radius = 420.0

# prompt user for different options (function, seed, resolution, max iterations, etc.)

val = -1
print('Please choose from one of the following functions:\n'
        '(1) f(z) = z**2 + c\n'
        '(2) f(z) = e**z + c\n'
        '(3) f(z) = sin(z) + c\n'
        '(4) f(z) = cos(z) + c\n'
        '(5) f(z) = c*z*(1-z)\n'
        '(6) Create your own equation')
while True:
    try:
        temp = int(raw_input("Choose a number corresponding with your intended option (1-6): "))
        if temp == 6:
            f_str = "null"
            esc_radius = 69.0
        elif temp == 5:
            f_str = "log"
            esc_radius = 50.0
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
            val = "z**2"
            esc_radius = 2.0
        else:
            val = int('the krusty krab is unfair, mr krabs is in there, standing at concession, plotting his oppression')
        break
    except ValueError:
        print("Invalid response, please try again.")

init = -1
while True:
    try:
        init = float(raw_input("Input seed: "))
        break
    except ValueError:
        print("Invalid input, please try again.")

x_0 = -1
x_1 = -1
y_0 = -1
y_1 = -1
while True:
    try:
        x_0 = float(raw_input("Input xmin: "))
        x_1 = float(raw_input("Input xmax: "))
        y_0 = float(raw_input("Input ymin: "))
        y_1 = float(raw_input("Input ymax: "))
        break
    except ValueError:
        print("Invalid input, please try again.")

iter_m = -1
while True:
    try:
        iter_m = int(raw_input("Input max iterations: "))
        if iter_m < 1:
            iter_m = int('the krusty krab is unfair, mr krabs is in there, standing at concession, plotting his oppression')
        break
    except ValueError:
        print("Invalid input, please try again.")

res_xy = -1
while True:
    try:
        res_xy = int(raw_input("Input the number of pixels to render on an axis: "))
        if res_xy < 1:
            res_xy = int('the krusty krab is unfair, mr krabs is in there, standing at concession, plotting his oppression')
        break
    except ValueError:
        print("Invalid input, please try again.")

# color scheme?

def geom(func_str, z, c):
    if func_str == "z**2":
        np.multiply(z, z, z)
        np.add(z, c, z)
        return z
    elif func_str == "e**z":
        np.exp(z,z)
        np.add(z, c, z)
        return z
    elif func_str == "sin":
        np.sin(z,z)
        np.add(z, c, z)
        return z
    elif func_str == "cos":
        np.cos(z,z)
        np.add(z, c, z)
        return z
    elif func_str == "log":
        np.multiply(z, c, z)
        temp = np.zeros(z.shape, dtype = int)
        temp[temp==0] = 1
        np.subtract(temp,z,temp)
        np.multiply(z,temp,z)
        return z

# TODO: quantize R (x) and i (y) axes and create different boxes, calculating those, then combining the arrays and generating the image
def mandel(fn_str, f_name, seed = 0, juul = 0, res = (4000,4000), xrng = (-2.2,0.8), yrng = (-1.5, 1.5), iter_max = 100):

    print "Initializing arrays..."

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make grid
    x = np.linspace(xrng[0], xrng[1], res[0])[gx]
    y = np.linspace(yrng[0], yrng[1], res[1])[gy]
    c = x+complex(0,1)*y # make complex grid

    print "Clearing memory..."

    del x, y # save some memory

    m_arr = np.zeros(c.shape, dtype = int) # initialize mandelbrot array

    # flatten out np arrays
    gx.shape = res[0]*res[1]
    gy.shape = res[0]*res[1]
    c.shape = res[0]*res[1]

    zinit = np.zeros(c.shape, dtype = complex)
    zinit[zinit==0] = seed

    z = geom(fn_str, zinit, c) # initial iteration

    print "Running..."
    start = time.time()

    for i in xrange(iter_max):
        if not len(z): break
        z = geom(fn_str, z, c)
        rem = abs(z) > esc_radius # escaped points condition
        m_arr[gx[rem], gy[rem]] = i+1 # record iteration count for escaped points
        rem = -rem # prisoner (non-escaped) points condition
        z = z[rem]
        gx, gy = gx[rem], gy[rem]
        c = c[rem]

    print 'Time taken:', time.time()-start
    print "Generating PNG..."

    m_arr[m_arr==0] = iter_max

    img = py.imshow(m_arr.T, origin='lower left', cmap = 'binary')
    img.write_png(f_name, noscale=True)

mandel(f_str, "mandel_render.png", res = (res_xy,res_xy), xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = iter_m)

'''

- maintain list of scales, domains, ranges, escape radii, suggested iteration limits, etc.

'''
