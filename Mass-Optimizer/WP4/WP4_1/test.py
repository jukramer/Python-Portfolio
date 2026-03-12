import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

xMin, xMax = (0, 10)
xValsOuter = np.arange(xMin, xMax, 1e-1)

def foo(x, f):
    xVals = np.arange(x, xMax, 1e-3)
    yVals = f(xVals)
    print(xVals.shape)
    print(yVals.shape)
    return sp.integrate.simpson(x=xVals, y=yVals)

fooVec = np.vectorize(foo)
yValsOuter = fooVec(xValsOuter, np.sin)

plt.plot(xValsOuter, yValsOuter)
plt.show()
