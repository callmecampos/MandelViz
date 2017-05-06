#!usr/bin/python
from PIL import Image, ImageDraw
import math, colorsys, cmath
import imageio
import os

iter_max = 100
dilate = 150.0
path = "./"
jules = False
esc_radius = 2

def geom(f_str, seed = 0, juul = 0): # include ftype in future version
    dim = (1000, 1000) # calculate domain and range for different msets and convert to scale operator
    scale = 1.0/(dim[0]/3)
    origin = (1.5,1.5) # Mandelbrot
    color_max = 50

    img = Image.new("RGB", dim)
    board = ImageDraw.Draw(img)

    # calculate color scheme
    palette = [0] * color_max
    for i in xrange(color_max):
        f = 1-abs((float(i)/color_max-1)**15)
        r, g, b = colorsys.hsv_to_rgb(.5+f/3, 1-f/3, f)
        palette[i] = (int(r*255), int(g*255), int(b*255))

    # calculate sequence for the point c with start value z
    def mandelbrot(c, z = 0):
        for n in xrange(iter_max + 1):
            z = cexp(z, complex(1.6,0.9)) + c
            if abs(z) > esc_radius:
                return n
        return None

    def mandelbrot_rec(n, c):
        if n == 0:
            return c
        else:
            z = mandelbrot_rec(n-1, c)
            return z**2 + c

    def mrec(n, c, z = 0):
        z_f = -1
        nan_b = False
        try:
            z_f = mandelbrot_rec(iter_max, c)
        except OverflowError:
            nan_b = True
        if str(z_f) != "(nan+nanj)" and nan_b == False:
            if abs(z_f) > 2:
                return 1 # look into distance from 2 as way to determine n
            else:
                return None
        else:
            return 1

    print("Working...")

    for y in xrange(dim[1]):
        for x in xrange(dim[0]):
            c = complex(x * scale - origin[0], y * scale - origin[1])

            if jules != True:
                n = mrec(iter_max, c, seed) # Mandelbrot (compare to iterative)
            else:
                n = mandelbrot(juul, c) # Julia

            if n is None:
                v = 1
                # print(c)
            else:
                v = n / dilate

            board.point((x, y), fill = palette[int(v * (color_max-1))])

    del board

    filename = str(f_str) + ".png"

    img.save(path + filename)

    print("Done.")

geom("0_static")

'''

- maintain list of scales, domains, ranges, escape radii, suggested iteration limits, etc.

'''
