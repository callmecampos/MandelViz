#!usr/bin/python
from PIL import Image, ImageDraw
import math, colorsys, cmath
import imageio
import threading

iter_max = 100
dilate = float(iter_max)
path = "./"
jules = True
f_str = "z**2"
esc_radius = 420

val = -1
print('Please choose from one of the following functions:\n'
        '(1) f(z) = z**2 + c\n'
        '(2) f(z) = e**z + c\n'
        '(3) f(z) = sin(z) + c\n'
        '(4) f(z) = cos(z) + c\n'
        '(5) f(z) = c*z*(1-z)\n'
        '(6) f(z) = null\n'
        '(7) Create your own equation')
while True:
    try:
        temp = int(raw_input("Choose a number corresponding with your intended option (1-6): "))
        if temp == 7:
            f_str = "null"
            esc_radius = -1
        elif temp == 6:
            f_str = "fun"
            esc_radius = 69
        elif temp == 5:
            f_str = "log"
            esc_radius = 50
        elif temp == 4:
            f_str = "cos"
            esc_radius = 10 * math.pi
        elif temp == 3:
            f_str = "sin"
            esc_radius = 10 * math.pi
        elif temp == 2:
            f_str = "e**z"
            esc_radius = 50
        elif temp == 1:
            val = "z**2"
            esc_radius = 2
        else:
            val = int('krusty krab is unfair, mr krabs is in there, standing at concession, plotting his oppression')
        break
    except ValueError:
        print("Invalid response, please try again.")

def iterate(func_str, num, c):
    if func_str == "z**2":
        return num**2 + c
    elif func_str == "e**z":
        return num**cpow + c
    elif func_str == "sin":
        return math.sin(num) + c
    elif func_str == "cos":
        return math.cos(num) + c
    elif func_str == "log":
        return c*num*(1-num)

def geom(fn_str, f_name, seed = 0, juul = 0, box = [-2.2,0.8,-1.5,1.5]): # calculate center and box from dim and origin
    res = (1000, 1000)
    scale_x = 1.0/((res[1])/(box[1]-box[0]))
    scale_y = 1.0/((res[1])/(box[3]-box[2]))
    origin = (1.5,1.5) # (-1 * box[0], box[3]) # Mandelbrot
    color_max = 50

    img = Image.new("RGB", res)
    board = ImageDraw.Draw(img)

    # calculate color scheme
    palette = [0] * color_max
    for i in xrange(color_max):
        f = 1-abs((float(i+1)/color_max-1)**15)
        r, g, b = colorsys.hsv_to_rgb(.5+f/3, 1-f/3, f)
        palette[i] = (int(r*255), int(g*255), int(b*255))

    # calculate sequence for the point c with start value z
    def mandelbrot(c, z = 0):
        for n in xrange(iter_max + 1):
            z = iterate(fn_str, z, c)
            if abs(z) > (esc_radius):
                return n
        return None

    mandel_arr = []

    for y in xrange(res[1]):
        for x in xrange(res[0]):
            c = complex(x * scale_x - origin[0], y * scale_y - origin[1])

            if jules != True:
                n = mandelbrot(c, seed) # Mandelbrot (compare to iterative)
            else:
                n = mandelbrot(juul, c) # Julia

            col = palette[int(0)]
            if n is None:
                col = (0,0,0)
            elif n > 2:
                v = n / dilate
                col = palette[int(v * (color_max-1))]
            else:
                col = (69, 69, 69)

            mandel_arr.append((x,y,col))

    for p in mandel_arr:
        (x, y, col) = p
        board.point((x, y), fill = col)

    del board

    filename = str(f_name) + ".png"

    img.save(path + filename)

geom(f_str, "0_static", juul = complex(-1.25066, 0.02012))

'''

- maintain list of scales, domains, ranges, escape radii, suggested iteration limits, etc.

'''
