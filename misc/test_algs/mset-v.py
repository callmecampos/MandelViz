from numpy import *

def mandel(resx, resy, itermax, xmin, xmax, ymin, ymax):
    ix, iy = mgrid[0:resx, 0:resy]
    x = linspace(xmin, xmax, resx)[ix]
    y = linspace(ymin, ymax, resy)[iy]
    c = x+complex(0,1)*y
    del x, y
    img = zeros(c.shape, dtype=int)
    ix.shape = resx*resy
    iy.shape = resx*resy
    c.shape = resx*resy
    z = copy(c)
    for i in xrange(itermax):
        if not len(z): break
        multiply(z, z, z)
        add(z, c, z)
        rem = abs(z) > 2.0
        img[ix[rem], iy[rem]] = i+1
        rem = -rem
        z = z[rem]
        ix, iy = ix[rem], iy[rem]
        c = c[rem]
    return img

if __name__=='__main__':
    from pylab import *
    import time
    start = time.time()
    I = mandel(1000, 1000, 100, -2, .5, -1.25, 1.25)
    print 'Time taken:', time.time()-start
    I[I==0] = 101
    img = imshow(I.T, origin='lower left')
    img.write_png('mandel.png', noscale=True)
    show()
