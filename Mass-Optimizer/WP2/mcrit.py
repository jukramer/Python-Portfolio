from math import sqrt, cos, pi
from parameters import *
import numpy as np

cps = np.loadtxt('WP2/tmp.txt')
cp_min = np.min(cps)
print(cp_min)

V = V_CRUISE
err = 1
while abs(err)>1e-5:
    V += err
    cp = cp_min/sqrt(1-(V/a_CRUISE)**2)
    v = sqrt(1-cp) * V
    v *= cos(14.822*pi/180)
    M = v/a_CRUISE
    err = 1-M

print(V, V/a_CRUISE)
