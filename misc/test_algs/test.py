c = -2.5

def mtest(c, z = 0):
    for n in xrange(101):
        z = z**2 + c
        if abs(z) > 2:
            print(z)
            return False
    print(z)
    return True

while c <= 1.0:
    res = mtest(c)
    print(res, c)
    c += 0.1
print("Done")
