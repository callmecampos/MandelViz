#!/usr/bin/python

''' 3D RENDERING OF MSETS '''

import math, sys, cmath
import numpy as np
sys.path.insert(0, '/Users/felipe_campos/anaconda/lib/python2.7/site-packages')
import mayavi as my
from mayavi import mlab
from progressbar import ProgressBar
sys.path.remove('/Users/felipe_campos/anaconda/lib/python2.7/site-packages')
import multiprocessing
import time

pbar = ProgressBar()

np.set_printoptions(threshold=np.nan) # allows for printing entire np arrays

dim = 3

iso = True
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

while True:
    try:
        temp = raw_input("Would you like to plot a Mandelbrot or Julia set? [m/j]: ")
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

x_0 = x_1 = y_0 = y_1 = z_0 = z_c0 = z_1 = z_c1 = -1
while True:
    try:
        x_0 = float(raw_input("Input xmin: "))
        x_1 = float(raw_input("Input xmax: "))
        y_0 = float(raw_input("Input ymin: "))
        y_1 = float(raw_input("Input ymax: "))
        z_0 = float(raw_input("Input real zmin: "))
        z_c0 = float(raw_input("Input complex zmin: "))
        z_1 = float(raw_input("Input real zmax: "))
        z_c1 = float(raw_input("Input complex zmax: "))
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

res_x = -1
while True:
    try:
        temp = int(raw_input("Input a positive integer indicating the resolution of the x-axis: "))
        if temp > 0:
            res_x = int(temp)
            break
        else:
            res_x = int(spongebob)
    except ValueError:
        print("Invalid input, please try again.")

res_y = -1
while True:
    try:
        temp = int(raw_input("Input a positive integer indicating the resolution of the y-axis: "))
        if temp > 0:
            res_y = int(temp)
            break
        else:
            res_y = int(spongebob)
    except ValueError:
        print("Invalid input, please try again.")

res_z = -1
while True:
    try:
        temp = int(raw_input("Input a positive integer indicating the resolution of the z-axis: "))
        if temp > 0:
            res_z = int(temp)
            break
        else:
            res_z = int(spongebob)
    except ValueError:
        print("Invalid input, please try again.")

while True:
    try:
        temp = raw_input("Plot iso-surface or voxel object? [i/v]: ")
        if temp == 'i':
            iso = True
            break
        elif temp == 'v':
            iso = False
            break
        else:
            iso = int(spongebob)
    except ValueError:
        print("Invalid input, please try again.")

# TODO: make a dictionary, dumbass ^^

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
def proc_handler(fn_str, seed, juul, iter_max, blocs, arr):
    pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count()*2))
    data = []

    '''if jules == True: seed = juul'''

    i = 0
    for bloc in blocs:
        data.append((i, bloc, fn_str, seed, iter_max))
        i += 1

    if jules == False:
        results = pool.map(procm, data)
    else:
        results = pool.map(procj, data)

    pool.close()
    pool.join()

    del bloc, data # save some memory

    for result in results:
        arr[result[1]] = result[0]

    return arr

def procm((procnum, c, fn_str, seed, iter_max)):

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

def procj((procnum, c, fn_str, seed, iter_max)):

    res = c.shape

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make grid

    m_arr = np.zeros(c.shape, dtype = int) # initialize mandelbrot array

    # flatten out np arrays
    gx.shape = res[0]*res[1]
    gy.shape = res[0]*res[1]
    c.shape = res[0]*res[1]

    zinit = np.zeros(c.shape, dtype = complex)
    zinit[zinit==0] = seed

    z = geom(fn_str, c, zinit) # initial iteration

    del c # save some memory

    for i in xrange(iter_max):
        if not len(z): break
        z = geom(fn_str, z, zinit)
        rem = abs(z) > esc_radius # escaped points condition
        m_arr[gx[rem], gy[rem]] = i+1 # record iteration count for escaped points
        rem = -rem # prisoner (non-escaped) points condition
        z = z[rem]
        gx, gy = gx[rem], gy[rem]
        zinit = zinit[rem]

    del gx, gy, zinit # save some memory

    m_arr[m_arr==0] = iter_max

    result = (m_arr, procnum)

    del m_arr # save some memory

    return result

def mandel(fn_str, seed = 0, juul = 0, res = (4000,4000), xrng = (-2.2,0.8), yrng = (-1.5, 1.5), iter_max = 100):

    #print "Initializing arrays..."

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make 2d grid
    x = np.linspace(xrng[0], xrng[1], res[0])[gx]
    y = np.linspace(yrng[0], yrng[1], res[1])[gy]
    c = x+complex(0,1)*y # make complex grid

    #print "Clearing memory..."

    del x, y, gx, gy # save some memory

    res_x = int(float(res[0]) / bloc_n)
    res_y = int(float(res[1]) / bloc_n)

    blocs = blockshaped(c, res_x, res_y)

    del c # save some memory

    return_arr = np.zeros(blocs.shape, dtype = int)

    #print "Running..."
    #start = time.time()

    # quantize R (x) and i (y) axes and create different boxes, calculating those in parallel, then recombining the arrays and generating the image
    proc_handler(fn_str, seed, juul, iter_max, blocs, return_arr)

    del blocs # save some memory

    m_arr = unblockshaped(return_arr, res[0], res[1])

    #print 'Time taken:', time.time()-start
    #print "Generating section..."

    return m_arr

if __name__ == '__main__':

    result = mandel(f_str, seed = complex(z_0, 0), res = (res_x,res_y), xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = iter_m)

    if dim == 3:
        step_z = (z_1 - z_0) / float(res_z)
        seed = np.linspace(z_0 + step_z, z_1, num=res_z)

        for seed_i in pbar(seed):
            res = mandel(f_str, seed = complex(seed_i, 0), res = (res_x,res_y), xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = iter_m)
            result = np.dstack((result, res))

        if iso == True:
            mlab.contour3d(result)
        else:
            mlab.pipeline.volume(mlab.pipeline.scalar_field(result))
    else:
        mlab.surf(result)

    mlab.show()

'''

medium/long term:
- rotate (maybe zoom? given software/lib) on models, reveal 2d slices based on angle/start or something else, display on separate screen
- save 3d objects for later use and inspection instead of having to make a new one every time
- maybe use 3d nparrays instead of layers

short term:
- consider using imap and tweaking chunksize arg to optimize mp performance
- display image of Mandelbrot set for specific function when choosing Julia set (especially for animation) --> take user input on image

'''
