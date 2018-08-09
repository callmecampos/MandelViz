import multiprocessing, time
import math, cmath
import numpy as np
import seaborn as sns

pbar = False
try:
    import progressbar
    pbar = True
except:
    pass

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap

def getMaxInImage(a):
    return np.unravel_index(a.argmax(), a.shape)

def pixToCoor(pixCoors, x_res, y_res, x_range, y_range, x_0, y_0):
    return (pixCoors[0] / float(x_res)) * x_range + x_0, (pixCoors[1] / float(y_res))  * y_range + y_0

# takes array input, performs operations based on chosen function, returns array
def geom(func_str, z, c, n=2):
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
    elif func_str == "csin":
        np.sin(z, z)
        np.multiply(z, c, z)
        return z
    elif func_str == "cos":
        np.cos(z,z)
        np.add(z, c, z)
        return z
    elif func_str == "ccos":
        np.cos(z, z)
        np.multiply(z, c, z)
        return z
    elif func_str == "log_c":
        np.multiply(z, c, z)
        temp = np.zeros(z.shape, dtype = np.complex128)
        temp[temp==0] = 1 # NOTE: may be able to just use (1-z)
        np.subtract(temp,z,temp)
        np.multiply(z,temp,z)
        return z
    elif func_str == "null":
        np.sinc(z,z)
        np.multiply(z,z,z)
        # np.add(z,c,z)
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
def proc_handler(fn_str, seed, juul, iter_max, blocs, arr, jules, esc_radius):
    pool = multiprocessing.Pool(processes=(multiprocessing.cpu_count()*2))
    data = []

    i = 0
    for bloc in blocs:
        data.append((i, bloc, fn_str, seed, iter_max, esc_radius))
        i += 1

    if jules == False:
        results = pool.map(procm, data)
    else:
        results = pool.map(procj, data)

    pool.close()

    del bloc, data # save some memory

    for result in results:
        arr[result[1]] = result[0]

    return arr

def procm(args):
    procnum, c, fn_str, seed, iter_max, esc_radius = args

    res = c.shape

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make grid

    m_arr = np.zeros(c.shape, dtype = int) # initialize mandelbrot array

    # flatten out np arrays
    gx.shape = res[0]*res[1]
    gy.shape = res[0]*res[1]
    c.shape = res[0]*res[1]

    zinit = np.zeros(c.shape, dtype = np.complex128)
    zinit[zinit==0] = seed

    z = geom(fn_str, zinit, c) # initial iteration

    del zinit # save some memory

    for i in range(iter_max):
        if not len(z): break
        z = geom(fn_str, z, c)
        rem = abs(z) > esc_radius # escaped points condition
        m_arr[gx[rem], gy[rem]] = i+1 # record iteration count for escaped points
        rem = ~rem # prisoner (non-escaped) points condition
        z = z[rem]
        gx, gy = gx[rem], gy[rem]
        c = c[rem]

    del gx, gy, c # save some memory

    m_arr[m_arr==0] = iter_max
    # m_arr[m_arr!=iter_max] = 0
    result = (m_arr, procnum)

    del m_arr # save some memory

    return result

def procj(args):

    procnum, c, fn_str, seed, iter_max, esc_radius = args

    res = c.shape

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make grid

    m_arr = np.zeros(c.shape, dtype = int) # initialize mandelbrot array

    # flatten out np arrays
    gx.shape = res[0]*res[1]
    gy.shape = res[0]*res[1]
    c.shape = res[0]*res[1]

    zinit = np.zeros(c.shape, dtype = np.complex128)
    zinit[zinit==0] = seed

    z = geom(fn_str, c, zinit) # initial iteration

    del c # save some memory

    for i in range(iter_max):
        if not len(z): break
        z = geom(fn_str, z, zinit)
        rem = abs(z) > esc_radius # escaped points condition
        m_arr[gx[rem], gy[rem]] = i+1 # record iteration count for escaped points
        rem = ~rem # prisoner (non-escaped) points condition
        z = z[rem]
        gx, gy = gx[rem], gy[rem]
        zinit = zinit[rem]

    del gx, gy, zinit # save some memory

    m_arr[m_arr==0] = iter_max

    result = (m_arr, procnum)

    del m_arr # save some memory

    return result

def mandel(i, fn_str, julia = False, seed = 0, juul = 0, res = (4000,4000),
            xrng = (-2.2,0.8), yrng = (-1.5, 1.5), iter_max = 100,
            num_blocs = 10, esc_radius = 2):

    # print('Running instance ' + str(i))

    # print("Initializing arrays...")

    gx, gy = np.mgrid[0:res[0], 0:res[1]] # make grid
    x = np.linspace(xrng[0], xrng[1], res[0])[gx]
    y = np.linspace(yrng[0], yrng[1], res[1])[gy]
    c = x+np.complex128(0+1j)*y # make complex grid

    # print("Clearing memory...")

    del x, y, gx, gy # save some memory

    res_x = int(float(res[0]) / num_blocs)
    res_y = int(float(res[1]) / num_blocs)

    blocs = blockshaped(c, res_x, res_y)

    del c # save some memory

    return_arr = np.zeros(blocs.shape, dtype = int)

    # print("Running...")
    start = time.time()

    # quantize R (x) and i (y) axes and create different boxes
    # calculate those in parallel
    # then recombining the arrays and generating the image
    proc_handler(fn_str, seed, juul, iter_max, blocs, return_arr, julia, esc_radius)

    del blocs # save some memory

    m_arr = unblockshaped(return_arr, res[0], res[1])

    # print('Time taken: ' + str(time.time()-start))

    return m_arr.T

ix, iy = 0, 0
images = []
def zoom(x_0, x_1, y_0, y_1, res_x, res_y, scale, frames, jules, esc_radius, f_str, _ix, _iy, init_r, init_c):
    my_cmap = ListedColormap(sns.color_palette("cubehelix", 8))
    base, p = 250, 10

    def click_figure(depth, x_0 = x_0, x_1 = x_1, y_0 = y_0, y_1 = y_1, _ix = _ix, _iy = _iy, \
                    init_r = init_r, init_c = init_c, base = base, p = p, my_cmap = my_cmap):
        global ix
        global iy
        global images

        ix = _ix
        iy = _iy

        x_range = x_1 - x_0
        y_range = y_1 - y_0

        f = plt.figure()
        ax = f.add_subplot(1,1,1)

        f.set_tight_layout(True)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        ax.imshow(mandel(0, f_str, seed = np.complex128(init_r+init_c*1j), res = (res_x,res_y),
            xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = base+int(math.log10(((float(y_range)/x_range)))**p),
            julia = jules, esc_radius = esc_radius), cmap=my_cmap)

        def on_click(event):
            global ix
            global iy
            ix, iy = pixToCoor((event.xdata, event.ydata), res_x, res_y, x_range, y_range, x_0, y_0)

            print("Zooming on (real: " + str(ix) + ", complex: " + str(iy) + ")")
            plt.close(f)

        cid = f.canvas.mpl_connect('button_press_event', on_click)

        plt.show(f)

        bar = progressbar.ProgressBar(maxval=depth, \
                    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage(), ' ', progressbar.ETA()])
        bar.start()

        center = (float(ix), float(iy))

        images = []
        for i in range(1, depth+1):
            x_range = x_range / float(scale)
            y_range = x_range / float(scale)
            x_0, x_1 = center[0] - (x_range / 2.0), center[0] + (x_range / 2.0)
            y_0, y_1 = center[1] - (y_range / 2.0), center[1] + (y_range / 2.0)

            # TODO: every once in a while, find brightest set of pixels in image (max pooling) and zoom in there

            data = mandel(i, f_str, seed = np.complex128(init_r+init_c*1j), res = (res_x,res_y),
                xrng = (x_0,x_1), yrng = (y_0,y_1), iter_max = base,#+int(math.log10(((4.0/float(y_range))))**p),
                julia = jules, esc_radius = esc_radius)

            images.append(data)
            bar.update(i)

        bar.finish()

        input("Calculated zoom, hit any key to render.")

        print("Rendering...")

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

        fig.set_tight_layout(True)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        im = ax.imshow(images[0], cmap=my_cmap)
        def update_image(i):
            """Returns updated ax"""
            im.set_data(images[i])
            fig.canvas.draw()
            return ax

        ani = animation.FuncAnimation(fig, lambda x: update_image(x), \
                frames=np.arange(0, depth), interval=10, repeat=False)

        plt.show(fig)

    click_figure(frames, x_0 = x_0, x_1 = x_1, y_0 = y_0, y_1 = y_1, _ix = _ix, _iy = _iy, \
                init_r = init_r, init_c = init_c, base = base, p = p, my_cmap = my_cmap)
