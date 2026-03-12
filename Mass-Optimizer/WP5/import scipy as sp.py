import numpy as np
import scipy as sp

class test:
    def __init__(self):
        pass
    
    def optim(self, x):
        return foo(x)
    
abx = test()

def foo(x):
    x, y, z, a, b, c = x
    return (x-1)**2 + (y-1)**2 + z**2 + a**2 + b**2 + c**4

res = sp.optimize.minimize(abx.optim, np.array([2,2,2,2,2,2]), method='Nelder-Mead', tol=1e-12)
print(res.x)