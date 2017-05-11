#!usr/bin/python
import math, sys, cmath
import numpy as np
import pylab as py
import multiprocessing
import time
import sys

np.set_printoptions(threshold=np.nan) # allows for printing entire np arrays

path = "./"
jules = False
f_str = "z**2"
esc_radius = 420.0
bloc_n = 10
spongebob = 'the krusty krab is unfair, mr krabs is in there, standing at concession, plotting his oppression!!'

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
            val = int(spongebob)
        break
    except ValueError:
        print("Invalid response, please try again.")

init = -1
while True:
    try:
        init_r = float(raw_input("Input real component of seed: "))
        init_c = float(raw_input("Input complex component of seed: "))
        init = complex(init_r,init_c)
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
            iter_m = int(spongebob)
        break
    except ValueError:
        print("Invalid input, please try again.")

res_xy = -1
print('Please choose from one of the following resolutions:\n'
        '(1) 10x10\n'
        '(2) 100x100\n'
        '(3) 500x500\n'
        '(4) 1000x1000\n'
        '(5) 5000x5000\n'
        '(6) 10000x10000\n'
        '(7) 25000x25000')
while True:
    try:
        temp = int(raw_input("Choose a number corresponding with your intended option (1-7): "))
        if temp == 7:
            res_xy = 25000
        elif temp == 6:
            res_xy = 10000
        elif temp == 5:
            res_xy = 5000
        elif temp == 4:
            res_xy = 1000
        elif temp == 3:
            res_xy = 500
        elif temp == 2:
            res_xy = 100
        elif temp == 1:
            res_xy = 10
        else:
            val = int(spongebob)
        break
    except ValueError:
        print("Invalid input, please try again.")

info = multiprocessing.get_logger().info # return_arr resxy thing was here may come back?

# color scheme prompt?

# takes array input, performs operations based on chosen function, returns array
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
        temp = np.zeros(z.shape, dtype = complex)
        temp[temp==0] = 1 # TODO: may be able to just use (1-z)
        np.subtract(temp,z,temp)
        np.multiply(z,temp,z)
        return z

def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))

def unblockshaped(arr, h, w):
    """
    Return an array of shape (h, w) where
    h * w = arr.size

    If arr is of shape (n, nrows, ncols), n sublocks of shape (nrows, ncols),
    then the returned array preserves the "physical" layout of the sublocks.
    """
    n, nrows, ncols = arr.shape
    return (arr.reshape(h//nrows, -1, nrows, ncols)
               .swapaxes(1,2)
               .reshape(h, w))

# handle parallel processes
def proc_handler(fn_str, f_name, seed, juul, iter_max, blocs, arr):
    pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count()*2))
    data = []

    i = 0
    for bloc in blocs:
        data.append((i, bloc, fn_str, f_name, seed, juul, iter_max))
        i += 1

    results = pool.map(proc, data)

    del bloc, data # save some memory

    for result in results:
        arr[result[1]] = result[0]

    return arr

def proc((procnum, c, fn_str, f_name, seed, juul, iter_max)):

    res = c.shape

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make grid

    m_arr = np.zeros(c.shape, dtype = int) # initialize mandelbrot array

    # flatten out np arrays
    gx.shape = res[0]*res[1]
    gy.shape = res[0]*res[1]
    c.shape = res[0]*res[1]

    zinit = np.zeros(c.shape, dtype = complex)
    zinit[zinit==0] = seed

    z = geom(fn_str, zinit, c) # initial iteration

    del zinit # save some memory

    for i in xrange(iter_max):
        if not len(z): break
        z = geom(fn_str, z, c)
        rem = abs(z) > esc_radius # escaped points condition
        m_arr[gx[rem], gy[rem]] = i+1 # record iteration count for escaped points
        rem = -rem # prisoner (non-escaped) points condition
        z = z[rem]
        gx, gy = gx[rem], gy[rem]
        c = c[rem]

    del gx, gy, c # save some memory

    m_arr[m_arr==0] = iter_max

    result = (m_arr, procnum)

    del m_arr # save some memory

    return result

def mandel(fn_str, f_name, seed = 0, juul = 0, res = (4000,4000), xrng = (-2.2,0.8), yrng = (-1.5, 1.5), iter_max = 100):

    print "Initializing arrays..."

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make grid
    x = np.linspace(xrng[0], xrng[1], res[0])[gx]
    y = np.linspace(yrng[0], yrng[1], res[1])[gy]
    c = x+complex(0,1)*y # make complex grid

    print "Clearing memory..."

    del x, y, gx, gy # save some memory

    res_x = int(float(res[0]) / bloc_n)
    res_y = int(float(res[1]) / bloc_n)

    blocs = blockshaped(c, res_x, res_y)

    del c # save some memory

    return_arr = np.zeros(blocs.shape, dtype = int)

    print "Running..."
    start = time.time()

    # quantize R (x) and i (y) axes and create different boxes, calculating those in parallel, then recombining the arrays and generating the image
    proc_handler(fn_str, f_name, seed, juul, iter_max, blocs, return_arr)

    del blocs # save some memory

    m_arr = unblockshaped(return_arr, res[0], res[1])

    print 'Time taken:', time.time()-start
    print "Generating PNG..."

    img = py.imshow(m_arr.T, origin='lower left', cmap = 'jet')
    img.write_png(f_name, noscale=True)

    m_arr = None

if __name__ == '__main__':
    mandel(f_str, "mandel_render.png", seed = init, res = (res_xy,res_xy), xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = iter_m)

'''

medium/long term:
- while figuring out multithreading/processing and optimizing speed, work on 3d modeling of various Mandelbrot/Julia sets
- rotate (maybe zoom? given software/lib) on models, reveal 2d slices based on angle/start or something else, display on separate screen
- save 3d objects for later use and inspection instead of having to make a new one every time

short term:
- consider using imap and tweaking chunksize arg to optimize performance
- start using PyOpenGL to do 3D modeling and even to improve fractal rendering

'''
